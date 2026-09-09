"""Bridge two AssemblyAI Voice Agent sessions so one can call the other."""
import array, asyncio, base64, json, os, random, time, uuid, wave
from pathlib import Path

import websockets

WS_URL = "wss://agents.assemblyai.com/v1/ws"
SAMPLE_RATE = 24000
FRAME_MS = 50
FRAME_BYTES = SAMPLE_RATE * 2 * FRAME_MS // 1000
SILENCE = b"\x00" * FRAME_BYTES


def load_env(path=".env"):
    for line in Path(path).read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


class Side:
    """One voice agent session, with a real-time outbound audio pacer."""

    def __init__(self, name, config, log, noise=0.0):
        self.name = name
        self.config = config
        self.log = log
        self.noise = noise
        self.outbox = asyncio.Queue()
        self.peer = None
        self.ws = None
        self.ready = asyncio.Event()
        self.done = asyncio.Event()
        self.pending_audio = bytearray()

    def record(self, direction, payload):
        self.log.write(json.dumps({
            "t": round(time.time() - self.log.t0, 3),
            "side": self.name,
            "dir": direction,
            "event": payload,
        }) + "\n")
        self.log.flush()

    async def send(self, msg):
        if msg["type"] != "input.audio":
            self.record("send", msg)
        await self.ws.send(json.dumps(msg))

    async def run(self):
        key = os.environ["ASSEMBLYAI_API_KEY"]
        async with websockets.connect(
            WS_URL, additional_headers={"Authorization": f"Bearer {key}"},
            max_size=None,
        ) as ws:
            self.ws = ws
            await self.send({"type": "session.update", "session": self.config})
            pacer = asyncio.create_task(self.pace())
            try:
                await self.listen()
            finally:
                pacer.cancel()

    async def pace(self):
        """Emit one frame every FRAME_MS: peer speech if buffered, else silence.

        Continuous audio is required; the agent's turn detection measures
        silence, so gaps in the stream are not the same as silence in it.
        """
        await self.ready.wait()
        next_at = time.monotonic()
        while True:
            if len(self.pending_audio) >= FRAME_BYTES:
                frame = bytes(self.pending_audio[:FRAME_BYTES])
                del self.pending_audio[:FRAME_BYTES]
            else:
                frame = mix_noise(SILENCE, self.noise) if self.noise else SILENCE
            await self.send({
                "type": "input.audio",
                "audio": base64.b64encode(frame).decode(),
            })
            next_at += FRAME_MS / 1000
            await asyncio.sleep(max(0, next_at - time.monotonic()))

    def feed(self, pcm):
        if self.noise:
            pcm = mix_noise(pcm, self.noise)
        self.pending_audio.extend(pcm)

    async def listen(self):
        async for raw in self.ws:
            ev = json.loads(raw)
            kind = ev.get("type")
            if kind == "reply.audio":
                b64 = ev.get("data") or ev.get("audio") or ""
                if b64:
                    pcm = base64.b64decode(b64)
                    if self.peer:
                        self.peer.feed(pcm)
                    try:
                        self.log.add_audio(time.time() - self.log.t0, pcm)
                    except Exception:
                        pass
                continue
            if kind in ("transcript.user.delta", "transcript.agent.delta"):
                continue
            self.record("recv", ev)
            if kind == "session.ready":
                self.ready.set()
            elif kind == "transcript.agent":
                print(f"  [{self.name}] {ev.get('text','')}")
            elif kind == "tool.call":
                print(f"  [{self.name}] TOOL CALL {ev.get('name')} {ev.get('arguments')}")
                await self.send({
                    "type": "tool.result", "call_id": ev.get("call_id"),
                    "result": json.dumps({"status": "ok"}), "is_error": False,
                })
            elif kind == "session.error":
                print(f"  [{self.name}] ERROR {ev.get('code')}: {ev.get('message')}")
            elif kind in ("session.ended",):
                self.done.set()
                return


def mix_noise(pcm, level):
    """Add band-limited noise so the target hears a degraded line.

    Degrades what the target's ASR receives, which is the point of the test:
    a guardrail that only holds on a clean channel has not been tested.
    """
    samples = array.array("h")
    samples.frombytes(pcm)
    amp = int(3000 * level)
    prev = 0
    for i in range(len(samples)):
        prev = (prev + random.randint(-amp, amp)) // 2
        v = samples[i] + prev
        samples[i] = max(-32768, min(32767, v))
    return samples.tobytes()


class Log:
    def __init__(self, path):
        self.path = path
        self.f = open(path, "w")
        self.t0 = time.time()
        self.mix = bytearray()

    def add_audio(self, offset_s, pcm):
        """Write a chunk into the call mix at its arrival offset.

        Both sides land on one timeline, so the saved wav plays back as the
        conversation actually sounded, overlaps included.
        """
        start = int(offset_s * SAMPLE_RATE) * 2
        end = start + len(pcm)
        if len(self.mix) < end:
            self.mix.extend(b"\x00" * (end - len(self.mix)))
        a = array.array("h"); a.frombytes(bytes(self.mix[start:end]))
        b = array.array("h"); b.frombytes(pcm)
        for i in range(min(len(a), len(b))):
            v = a[i] + b[i]
            a[i] = max(-32768, min(32767, v))
        self.mix[start:end] = a.tobytes()

    def save_wav(self):
        if not self.mix:
            return None
        path = self.path.replace(".jsonl", ".wav")
        with wave.open(path, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SAMPLE_RATE)
            w.writeframes(bytes(self.mix))
        return path

    def write(self, s):
        self.f.write(s)

    def flush(self):
        self.f.flush()

    def close(self):
        self.f.close()


async def bridge(attacker_cfg, target_cfg, seconds, run_id=None, noise=0.0):
    run_id = run_id or uuid.uuid4().hex[:8]
    Path("runs").mkdir(exist_ok=True)
    log = Log(f"runs/{run_id}.jsonl")
    a = Side("attacker", attacker_cfg, log)
    t = Side("target", target_cfg, log, noise=noise)
    a.peer, t.peer = t, a
    tasks = [asyncio.create_task(a.run()), asyncio.create_task(t.run())]
    try:
        await asyncio.wait_for(asyncio.gather(*tasks), timeout=seconds)
    except asyncio.TimeoutError:
        # Closing without session.end leaves a billable 30s grace window.
        for side in (a, t):
            try:
                await asyncio.wait_for(side.send({"type": "session.end"}), 2)
            except Exception:
                pass
        await asyncio.sleep(0.5)
    except Exception as e:
        print(f"  bridge error: {type(e).__name__}: {e}")
    finally:
        for task in tasks:
            task.cancel()
        try:
            wav = log.save_wav()
            if wav:
                print(f"  audio: {wav}")
        except Exception as e:
            print(f"  wav save failed: {type(e).__name__}: {e}")
        log.close()
    return log.path
