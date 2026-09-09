# Deploying the judge-facing prototype

The server holds WebSocket sessions for the length of a call, so it needs a
long-running process. Serverless request timeouts will cut a live attack off
part way. Any container host works: Render, Railway, Fly.io, or a small VPS.

```bash
docker build -t voxrede .
docker run -p 8080:8080 -e ASSEMBLYAI_API_KEY=... voxrede
```

Set these in the host's environment, never in the image:

- `ASSEMBLYAI_API_KEY` (the only credential the project needs)
- `VOXREDE_MAX_RUNS` hourly cap on live attacks judges can trigger, default 12
- `VOXREDE_LIVE_SECONDS` length of one live attack, default 100

Each live attack opens two Voice Agent sessions for `VOXREDE_LIVE_SECONDS`, so
the hourly cap is also the spend cap: 12 runs of 100s is about 0.67 session
hours, roughly 3 US dollars per hour at 4.50 per session hour.

Judges never need an account or a key. The pre-run baseline and hardened
reports are baked into the image, so the page is useful even when the live
budget is exhausted.

## Static copy

`python static_build.py` writes a `static/` directory (overview plus the three
reports) that any static host will serve. The published pages listed in the
README are the same content, hosted already.
