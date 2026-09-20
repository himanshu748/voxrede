"""Paced fixture-to-fixture bridge. No production tools are executed."""
import asyncio, base64, hashlib, json, os, random, re, struct, time, uuid, wave
from collections import deque
from pathlib import Path
import websockets
from scorer import SCORER_VERSION

BRIDGE_VERSION = "2.1.2"

WS_URL = "wss://agents.assemblyai.com/v1/ws"
SAMPLE_RATE = 24000
END_ACK_TIMEOUT = 8
SEND_TIMEOUT = 5
FRAME_MS = 50
FRAME_BYTES = SAMPLE_RATE * 2 * FRAME_MS // 1000
SILENCE = bytes(FRAME_BYTES)


def load_env(path=".env"):
    if not Path(path).exists():
        return
    for line in Path(path).read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def mix_noise(pcm, level, rng=None):
    if len(pcm) % 2:
        raise ValueError("PCM16 requires complete samples")
    rng = rng or random
    samples = list(struct.unpack('<' + 'h' * (len(pcm)//2), pcm))
    prev = 0
    for i, sample in enumerate(samples):
        prev = (prev + rng.randint(-int(3000*level), int(3000*level))) // 2
        samples[i] = max(-32768, min(32767, sample + prev))
    return struct.pack('<' + 'h' * len(samples), *samples)


class AudioQueue:
    """Reply-aware bounded queue; odd bytes wait for the next chunk."""
    def __init__(self):
        self.chunks = deque()
        self.cancelled = set()

    def feed(self, pcm, reply_id):
        if reply_id in self.cancelled:
            return
        if sum(len(b) for _, b in self.chunks) + len(pcm) > SAMPLE_RATE * 2 * 30:
            raise ValueError("Audio queue exceeded 30 seconds")
        if self.chunks and self.chunks[-1][0] == reply_id:
            self.chunks[-1][1].extend(pcm)
        else:
            self.chunks.append((reply_id, bytearray(pcm)))

    def cancel(self, reply_id):
        self.cancelled.add(reply_id)
        removed = sum(len(b) for r, b in self.chunks if r == reply_id)
        self.chunks = deque((r, b) for r, b in self.chunks if r != reply_id)
        return removed

    def frame(self):
        if not self.chunks:
            return SILENCE, None, 0
        reply_id, data = self.chunks[0]
        n = min(len(data) // 2 * 2, FRAME_BYTES)
        frame = bytes(data[:n])
        del data[:n]
        if not data:
            self.chunks.popleft()
        return frame + bytes(FRAME_BYTES-n), reply_id, n // 2

    def finish(self, reply_id):
        # An odd tail at a reply boundary cannot form a PCM16 sample.
        if any(r == reply_id and len(b) % 2 for r, b in self.chunks):
            raise ValueError("Incomplete PCM16 sample at reply boundary")


class Log:
    def __init__(self, path):
        self.path = str(path)
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        self.f = os.fdopen(fd, "w")
        self.t0 = time.monotonic()
        self.audio = {}
        self.positions = {}

    def audio_chunk(self, side, stage, pcm, reply_id=None):
        key = (side, stage)
        if key not in self.audio:
            path = Path(self.path).with_suffix(f'.{side}.{stage}.pcm')
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            self.audio[key] = os.fdopen(fd, 'wb')
            self.positions[key] = 0
        start = self.positions[key]
        self.audio[key].write(pcm)
        self.audio[key].flush()
        self.positions[key] += len(pcm)
        return {"byte_start": start, "byte_count": len(pcm), "sample_start": start // 2, "intra_sample_byte": start % 2,
                "reply_id": reply_id, "stage": stage}

    def write(self, value):
        self.f.write(value)

    def flush(self):
        self.f.flush()

    def close(self):
        for f in self.audio.values():
            f.close()
        self.f.close()


class Side:
    def __init__(self, name, config, log, noise=0.0):
        self.name, self.config, self.log, self.noise = name, config, log, noise
        self.peer = self.ws = None
        self.ready, self.done = asyncio.Event(), asyncio.Event()
        self.queue = AudioQueue()
        self.reply_id = None
        self.pending_tools = {}
        self.stopping = False
        self.end_requested = False
        self.rng = random.Random(0)

    def record(self, direction, payload):
        # Resume tokens are credentials, not evidence.
        payload = {k: v for k, v in payload.items() if k not in ('resume_token', 'token')}
        self.log.write(json.dumps({"t": time.monotonic()-self.log.t0, "side": self.name,
                                   "dir": direction, "event": payload}) + '\n')
        self.log.flush()

    async def send(self, msg):
        await asyncio.wait_for(self.ws.send(json.dumps(msg)), SEND_TIMEOUT)
        if msg['type'] != 'input.audio':
            self.record('send', msg)

    async def request_end(self):
        self.stopping = True
        if self.ws and not self.done.is_set() and not self.end_requested:
            self.end_requested = True
            await asyncio.wait_for(self.send({'type': 'session.end'}), 2)

    async def run(self):
        try:
            async with websockets.connect(WS_URL, additional_headers={
                'Authorization': 'Bearer ' + os.environ['ASSEMBLYAI_API_KEY']},
                max_size=4*1024*1024, open_timeout=10, close_timeout=2) as ws:
                self.ws = ws
                pacer = None
                try:
                    await self.send({'type': 'session.update', 'session': self.config})
                    pacer = asyncio.create_task(self.pace())
                    listener = asyncio.create_task(self.listen())
                    finished, _ = await asyncio.wait([pacer, listener], return_when=asyncio.FIRST_COMPLETED)
                    for task in finished:
                        task.result()
                finally:
                    self.stopping = True
                    if not self.done.is_set():
                        try:
                            await self.request_end()
                            await asyncio.wait_for(self.done.wait(), END_ACK_TIMEOUT)
                        except Exception:
                            self.record('recv', {'type': 'transport.error', 'code': 'end_not_acknowledged'})
                    for task in (pacer, locals().get('listener')):
                        if task:
                            task.cancel()
                    await asyncio.gather(*(t for t in (pacer, locals().get('listener')) if t), return_exceptions=True)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            self.record('recv', {'type': 'transport.error', 'code': type(exc).__name__})
        finally:
            self.ws = None

    async def pace_once(self):
        frame, reply_id, speech_samples = self.queue.frame()
        clean = frame
        if self.noise:
            frame = mix_noise(frame, self.noise, self.rng)
        await self.send({'type': 'input.audio', 'audio': base64.b64encode(frame).decode()})
        meta = self.log.audio_chunk(self.name, 'delivered', frame, reply_id)
        self.record('send', {'type': 'audio.delivered', **meta, 'speech_samples': speech_samples,
                             'noise_level': self.noise, 'perturbed': frame != clean,
                             'delivery_scope': 'websocket_send_completed_not_provider_acknowledged'})

    async def pace(self):
        await self.ready.wait()
        while not self.stopping:
            started = time.monotonic()
            await self.pace_once()
            # Never burst frames to catch up after a scheduling stall.
            await asyncio.sleep(max(0, FRAME_MS/1000 - (time.monotonic()-started)))

    def feed(self, pcm, reply_id=None):
        self.queue.feed(pcm, reply_id)

    async def handle(self, ev):
        kind = ev.get('type')
        if kind == 'reply.audio':
            rid = ev.get('reply_id', self.reply_id)
            if rid is None:
                raise ValueError('Audio has no reply identity')
            pcm = base64.b64decode(ev.get('data', ''), validate=True)
            meta = self.log.audio_chunk(self.name, 'generated', pcm, rid)
            self.record('recv', {'type': 'audio.generated', **meta})
            if self.peer:
                self.peer.feed(pcm, rid)
            return
        self.record('recv', ev)
        if kind == 'session.ready':
            self.ready.set()
        elif kind == 'reply.started':
            self.reply_id = ev.get('reply_id')
        elif kind == 'tool.call':
            call_id = ev.get('call_id')
            if not isinstance(call_id, str) or not isinstance(ev.get('arguments'), dict):
                raise ValueError('Invalid tool request')
            # Only a mock result, never money movement or production execution.
            rid = ev.get('reply_id') or self.reply_id or 'fc-' + call_id
            self.pending_tools.setdefault(rid, []).append(call_id)
        elif kind == 'reply.done':
            rid = ev.get('reply_id', self.reply_id)
            pending = self.pending_tools.pop(rid, [])
            if ev.get('status') == 'completed' and not self.stopping:
                if self.peer:
                    self.peer.queue.finish(rid)
                for call_id in pending:
                    await self.send({'type': 'tool.result', 'call_id': call_id,
                                     'result': json.dumps({'status': 'simulated', 'executed': False, 'message': 'No real account lookup or payment was performed. This mock result provides no account data. Tell the caller that the operation is simulated.'}),
                                     'is_error': False})
            else:
                removed = self.peer.queue.cancel(rid) if self.peer else 0
                self.record('recv', {'type': 'audio.cancelled', 'reply_id': rid,
                                     'discarded_bytes': removed, 'discarded_tool_results': len(pending)})
            if rid == self.reply_id:
                self.reply_id = None
        elif kind == 'session.error':
            raise RuntimeError('Provider error')
        elif kind == 'session.ended':
            if any(self.pending_tools.values()):
                self.record('recv', {'type': 'transport.error', 'code': 'unresolved_tool_reply_boundary',
                                     'pending_count': sum(map(len, self.pending_tools.values()))})
            self.done.set()

    async def listen(self):
        async for raw in self.ws:
            await self.handle(json.loads(raw))
            if self.done.is_set():
                return
        if not self.done.is_set():
            raise ConnectionError('Socket closed without session.ended')


async def bridge(attacker_cfg, target_cfg, seconds, run_id=None, noise=0.0, *, approved=False, evidence_context=None):
    if not approved:
        raise PermissionError('Explicit provider-credit approval is required')
    if not 1 <= seconds <= 120 or not 0 <= noise <= 1:
        raise ValueError('Trial bounds exceeded')
    label = re.sub(r'[^a-zA-Z0-9_-]', '_', run_id or 'trial')[:80]
    trial_id = uuid.uuid4().hex
    folder = Path('runs') / trial_id
    folder.mkdir(parents=True, mode=0o700)
    os.chmod(folder, 0o700)
    log = Log(folder / 'events.jsonl')
    manifest = {'schema_version': 1, 'trial_id': trial_id, 'label': label,
                'state': 'attempted', 'scope': 'local_fixture_mock_tools',
                'scorer_version': SCORER_VERSION, 'bridge_version': BRIDGE_VERSION, 'evidence_context': evidence_context or {}, 'config': {'attacker': attacker_cfg, 'target': target_cfg},
                'conditions': {'seconds': seconds, 'noise': noise, 'noise_seed': 0},
                'audio_format': {'encoding': 'PCM16LE', 'sample_rate': SAMPLE_RATE, 'channels': 1}}
    def snapshot(name):
        path = folder / name
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w') as f:
            json.dump(manifest, f, indent=2)
    snapshot('manifest.attempt.json')
    a, t = Side('attacker', attacker_cfg, log), Side('target', target_cfg, log, noise)
    a.peer, t.peer = t, a
    tasks = [asyncio.create_task(a.run()), asyncio.create_task(t.run())]
    cancelled = False
    try:
        # wait does not cancel sockets at the deadline: request shutdown first.
        await asyncio.wait(tasks, timeout=seconds, return_when=asyncio.FIRST_COMPLETED)
    except asyncio.CancelledError:
        cancelled = True
        a.record('recv', {'type': 'run.cancelled', 'reason': 'operator_or_task_cancellation'})
        raise
    finally:
        for side in (a, t):
            side.stopping = True
            if side.ws and not side.done.is_set():
                try:
                    await side.request_end()
                except Exception:
                    side.record('recv', {'type': 'transport.error', 'code': 'end_send_failed'})
        await asyncio.wait(tasks, timeout=END_ACK_TIMEOUT + 2)
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        log.close()
        records = [json.loads(line) for line in Path(log.path).read_text().splitlines()]
        errors = [r for r in records if r['event']['type'] in ('session.error', 'transport.error')]
        manifest['state'] = 'cancelled' if cancelled else ('ended' if a.done.is_set() and t.done.is_set() and not errors else 'incomplete')
        manifest['error_count'] = len(errors)
        manifest['files'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in folder.iterdir() if p.is_file()}
        snapshot('manifest.final.json')
    return log.path
