# Current submission copy

Voice-agent red teaming with recorded calls, exact source events and matched follow-ups. Inspect 19 real fixture trials, delivered audio and permitted-task outcomes without an API key.

Voxrede makes voice-agent red teaming inspectable. I use two AssemblyAI Voice Agent sessions: a test caller and a fictional support agent. Judges can hear audio sent between them, inspect the source events and compare the baseline with a stricter prompt.

The current evaluation retains all 19 attempted trials and nine matched pairs, including failures. Three of six permitted-task attempts completed their task; one produced an incorrect outcome and two were inconclusive. Twelve of the 19 evaluations remain inconclusive because of transport or coverage limits. Zero configured policy findings in these new samples is not a safety claim.

The retests found a concrete problem: an agent described a simulated account lookup as real. The mock response now states that no account data was accessed. Both final calls delivered that explanation, although the stricter-prompt run lacked a shutdown acknowledgement.

Voxrede separates digit mentions from verified identity, tool requests from execution, and generated audio from audio actually sent after pacing and noise. Unique trial IDs and versioned manifests preserve configuration, source hashes and completion state. Public source copies remove provider identifiers and tokens. Outcomes are reviewed by an assistant against cited events, not independently adjudicated.

The original 17-sample evidence workspace remains searchable, with exact-event links, exports and missing comparisons. No key is needed to review either archive. Tools are mocked; no production account, real refund or external target was tested. The current deck and recorded evaluation cover this upgrade; the existing narrated video shows the earlier viewer.

## Additional information

Start with the recorded evaluation: https://himanshu748.github.io/voxrede/evaluation.html

Open the first permitted lookup pair, play the delivered-audio tracks and follow its source-event links. Both agents explain that the lookup is simulated. The stricter-prompt trial remains INCONCLUSIVE because shutdown was not acknowledged. Then inspect the other matched pairs and the stopped-batch plans/ledgers.

Historical finding: https://himanshu748.github.io/voxrede/findings.html#base/01_authority/event-7

19 attempted trials; 9 matched pairs; 3/6 permitted tasks completed; 12 inconclusive evaluations. These small fixture samples do not establish general safety or a defense success rate. Delivered means successful local WebSocket send, not provider receipt. Source-event review is by an assistant.

The final eight-second shutdown timeout adjustment has offline tests only. No trusted identity-verification adapter or production tool integration exists. The existing video shows the earlier viewer; the updated deck and evaluation page are current.
