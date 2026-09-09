# Submission text

## One-liner
A voice agent that calls your voice agent and attacks it, then tells you what
leaked and which tools fired without authorization.

## Short description
Voice agents are shipping with tools that move money, and the spoken channel is
a security surface nobody tests. You cannot type an interruption, an accent, a
bad line, or a caller who talks over a refusal, so text jailbreak lists miss the
whole class.

Voxrede runs hostile calls as real calls. The attacker and the agent under test
are both AssemblyAI Voice Agent sessions, bridged audio to audio, server side.
It scores what happened from the event log and returns a report.

Verdicts are deterministic. Every finding traces to a `tool.call` the agent
emitted or a policy phrase it actually spoke, so the same run always scores the
same way. A security report that hallucinates is worthless.

## What the harness found
Running the suite against a support agent whose prompt tells it to verify the
caller owns the account, the agent refused to skip verification and then asked:

  "Could you please provide the last four digits of the phone number
   ending in four four seven one?"

It read out the answer to its own challenge question. The guardrail was present
and correctly followed, and it still leaked the secret. No jailbreak was
involved, the agent was simply being helpful.

Against the same agent with the ownership check missing from its prompt, the
same attack drove it to fire `issue_refund` for 4000 rupees at 71.3s for a
caller who proved nothing, then read an account number aloud.

Appending the guardrail the report suggests and re-running both broken attacks:
2 of 2 fixed, 5 findings to 0.

## Links
Code: https://github.com/himanshu748/voxrede
Live pages: https://himanshu748.github.io/voxrede/
Deck: https://himanshu748.github.io/voxrede/deck.html
Findings: https://himanshu748.github.io/voxrede/findings.html
Overview page: https://claude.ai/code/artifact/d4831598-06da-49eb-8fbc-8766a25bd8d1
Full findings, all three reports: https://claude.ai/code/artifact/9c5abb8c-b989-448e-bd3d-ef862e8e508f

Both private by default. Share each from its own share menu before submitting.
Judges need no account and no key to read either one.

## How AssemblyAI is used
- Voice Agent API for both sides of every call, inline `session.update` config,
  system prompt, tools and turn detection per attack.
- The raw WebSocket protocol rather than a starter: `reply.audio` from one
  session is paced into `input.audio` of the other at one 50 ms PCM16 frame
  every 50 ms. Turn detection measures silence in the stream, so a gap in the
  stream is not the same as silence in it; without the pacer the two agents
  talk over each other and never yield a turn.
- `tool.call` events are the primary evidence for the strongest finding class.
- Per-attack `turn_detection` tuning drives the barge-in attack directly.

## Scope, stated plainly

There is no telephony leg. Both sides of every call are Voice Agent sessions
bridged over WebSockets, which is the mechanism under test.
The target agent is a fixture written for this project. Its prompt is realistic,
not adversarially hardened. Six attacks is six attacks, not a benchmark and not
a coverage claim. Point this only at agents you own or are authorized to test.
