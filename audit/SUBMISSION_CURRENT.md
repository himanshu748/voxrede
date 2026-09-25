# Current submission copy

Hear a voice agent claim an account lookup that never happened. Voxrede links the recorded failure, changed mock result and follow-up to source events, then opens all 19 fixture trials for review.

A voice agent said, "I have successfully pulled up the account for Priya Sharma." The tool had returned a simulated result with executed=false. Voxrede preserved the misleading reply and the later retests.

The historical archive shows the same agent leaking its protected phone digits in 4 of 13 baseline-prompt samples, across three different attacks (authority impersonation, barge-in and PII extraction). Twice it put the answer inside its own verification question. The stricter prompt had no findings in its two matched samples, which is too few to claim a fix rate.

Three unmodified excerpts link to recordings and source events. The stricter-prompt follow-up retains its incomplete-shutdown label.

I built Voxrede for developers reviewing voice support agents. Two AssemblyAI Voice Agent sessions act as test caller and support fixture, exchanging paced audio. Scenarios include authority impersonation, spoken prompt injection, interruption and a degraded channel, alongside permitted tasks.

All 19 attempted trials and nine matched pairs remain visible. Three of six permitted tasks completed; one gave an incorrect outcome and two were inconclusive. Twelve evaluations remain inconclusive for coverage or transport reasons. These samples do not establish a defense success rate.

Voxrede separates digit mentions from verified identity, tool requests from execution, and generated audio from audio sent after pacing and noise. Unique trial IDs and manifests retain configuration, source hashes and completion state. Public logs remove provider identifiers and tokens. Outcomes are assistant source-event reviews, not independent adjudication.

The original 17-sample archive still supports search, exports, exact-event links and missing comparisons. No API key is needed to review the evidence. All business tools are mocked; no production account or real refund was tested. The current deck and interactive walkthrough cover the upgrade. The narrated video shows the earlier viewer.

## Additional information

Start here: https://himanshu748.github.io/voxrede/evaluation.html#walkthrough

Use the three walkthrough steps. Hear the 6.40-second misleading lookup claim, the 11.10-second later baseline reply and the 8.60-second stricter-prompt follow-up. Expand the mock tool result, follow the exact source link, or download the review brief with audio hashes and sample ranges. These are contiguous excerpts of existing delivered recordings, not new narration.

Then open the complete evaluation: all 19 attempts, nine matched pairs, 3/6 permitted tasks completed and 12 inconclusive evaluations. The original protected-digit disclosure is at https://himanshu748.github.io/voxrede/findings.html#base/01_authority/event-7

The mock-tool response changed between the first recording and the final pair. Separate calls do not prove causation or a reliable fix rate. Delivered means a successful local WebSocket send, not provider receipt. Source-event review is by an assistant. No trusted identity adapter or production tool integration exists.

The eight-second shutdown timeout has offline tests only. Safari playback was verified; if an embedded browser cannot play audio, use the WAV download. The narrated video uses the earlier viewer; the interactive walkthrough and PDF are current.
