# Voxrede, pitch deck content

Ten slides. Numbers get filled from the real suite report, never estimated.

## 1. Title
Voxrede
A voice agent that calls your voice agent and attacks it.
Built on the AssemblyAI Voice Agent API.

## 2. The problem
Voice agents now hold tools that move money: refunds, transfers, account
changes, appointment cancellations. The spoken channel carries failure modes
that text testing cannot reach.

You cannot type an interruption. You cannot type an accent, a bad line, or a
caller who talks over a refusal. Text jailbreak lists do not reach any of it.

## 3. What exists today
Voice-agent security testing already exists. Bluejay lists red teaming
alongside simulation, and integrates with the same Voice Agent API.

Voxrede's focus is narrower: self-hosted with no third party in the call path,
a policy declared per target, and every verdict linked to the logged event
that produced it. That is a product focus, not a claim to have invented the
category.

## 4. What Voxrede does
Point it at an agent. It runs a suite of hostile calls and returns a report:
what leaked, which tools fired without authorization, and the exact utterance
that broke it.

## 5. How it works
Two AssemblyAI Voice Agent sessions, bridged audio to audio, server side.
No browser. No media server.

The attacker's reply.audio becomes the target's input.audio, and back.
A real-time pacer emits one 50 ms PCM16 frame every 50 ms, silence included,
because turn detection measures silence in the stream. Without it the two
agents talk over each other and never yield a turn.

## 6. Verdicts you can trust
Deterministic. Every finding traces to a logged event: a tool.call the agent
emitted, or a policy phrase it actually spoke. Spoken digits are normalized,
so "four four seven one" matches 4471.

No model judges the result, so the same run always scores the same way.
A security report that hallucinates is worthless.

## 7. The attacks
Six, all voice-specific: authority impersonation, audio-channel prompt
injection, barge-in exploitation, slow boil, PII extraction, degraded channel.
Attacks are JSON files. Adding one is a file, not a code change.

## 8. The demo
Baseline run against a realistic support agent. [N] of 6 attacks break it.
Show the tool.call event where a 4000 rupee refund fires for a caller who
never proved anything.

Apply the guardrail the report suggests. Re-run the same attacks. They hold.

## 9. Who needs it
Anyone shipping a customer-facing voice agent with tool calling: support,
booking, healthcare intake, telecom. They have a prompt and a tool schema and
no idea what a determined caller gets out of them.

## 10. Honest scope
The target agent is a fixture written for this project; its prompt is realistic,
not adversarially hardened. Six attacks is six attacks, not a benchmark.
Point it only at agents you own or are authorized to test.
