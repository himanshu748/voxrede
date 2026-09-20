# Current hardening and recorded evaluation — September 20, 2026

Starting local and remote HEAD was `583ff30c141585f3abeaff03fdf36edf4b8bfb60`. The read-only audit had no available 17-probe script; five scoring defects were independently reproduced against that exact source. The original 17 scorer checks are a separate suite.

## Implemented

- Digit mentions never establish verified authorization. Grouped numbers, longer identifiers, negation, echoes, unrelated requirements and split disclosures have regressions. Lexical matches and contextual findings are separate. No trusted identity-verification adapter exists.
- Reply-aware bounded audio queues handle interruption and partial PCM. Mock tool results wait for the matching completed reply. Real provider testing exposed response IDs different from the documented fc-call convention; routing now uses the observed active reply ID. Requests remain distinct from execution.
- Generated and delivered PCM are separate. Delivered recordings follow successful paced/perturbed sends and retain monotonic timestamps and sample positions. Send completion is not provider receipt. Greeting interruptions and noise on silence do not establish substantive interruption or degraded speech.
- UUID trial directories and versioned manifests retain original logs, configuration/policy identity, scorer version, completion and intended defense changes. Public copies redact provider identifiers and tokens; private and public hashes are distinguished. Application writes never replace a trial; hashes are not proof of authorship.
- Failures, cancellation, unresolved tool boundaries and shutdown errors persist. Sessions are ended before socket teardown. Incomplete runs retain observations and remain INCONCLUSIVE.
- The compatible-log importer preserves source bytes, rejects symlinks/oversized input and does not trust imported verification claims. Web live execution and private trial endpoints are disabled; the public site is a no-key evidence viewer. No public Python execution service is exposed.

## Recorded evaluation

The user authorized up to US$10. Nineteen bridge attempts (38 voice sessions) ran across a preflight and three batches, producing nine matched pairs. The conservative cumulative reservation is US$5.35, not a provider invoice. Paid testing is finished. Stopped batches retain their attempted trials and 24 unattempted slots.

Six permitted-task attempts produced three completed tasks, one incorrect outcome and two inconclusive task outcomes. Twelve of all 19 evaluations remain INCONCLUSIVE for coverage or transport reasons. Zero configured policy findings in these new samples does not establish a defense success rate. Outcomes are an assistant source-event review, not independent human adjudication.

A real retest exposed an agent describing a mock lookup as a real lookup. The mock response now explicitly states that no account data was accessed. Both final paired trials delivered that explanation in full. The stricter-prompt trial still lacked a shutdown acknowledgement: its useful-task outcome is observed, while transport and evaluation remain incomplete.

Bridge 2.1.2 extends the shutdown acknowledgement window from two to eight seconds. That final adjustment is covered by offline delayed-ack tests only; it has not received another paid validation. Contextual scoring remains heuristic, and no production integration or real payment was tested.

## Verification and evidence

Run `python test_scorer.py`, then `python -m unittest test_report_edges test_archive_review test_judge_review test_evidence_workspace test_static_build test_hardening test_evaluation test_judge_story -q`. There are 17 scorer checks and 101 unittest checks (118 total). The baseline reproducer, site builders and PDF build are separate checks. Exact fresh output is in `test-results.txt`.

The published evaluation bundle is `evidence/evaluation_current.json` plus `assets/evaluation/`: every attempted trial has redacted source events, delivered lossless audio and a manifest; every batch retains a plan and attempt ledger. Private original PCM/logs remain in ignored runs directories. The historical 17-sample workspace, exact-event links, search, exports, fixture labels and missing-comparison behavior remain intact.

See `DEMO_CURRENT.md` for the current walkthrough and `SUBMISSION_CURRENT.md` for the submission text. Publication receipt is recorded separately after the remote site and saved submission are verified.

## Publication

The implementation was published as 95158be. GitHub CI and Pages both passed. Lablab displayed "Submission Updated!"; the public description and demo link were verified. The uploaded deck matches the local PDF byte for byte. See PUBLICATION_RECEIPT.json. Browser playback derivatives are separate from unchanged lossless evidence.

Hosted FLAC audio played in Safari (elapsed 28 seconds visible; total 1:15). The Codex in-app browser crashed when starting both FLAC and MP3; playback there remains unverified. MP3 listening derivatives are explicitly separate from the lossless FLAC evidence.

The current judge walkthrough adds three provenance-checked audio excerpts and a downloadable review brief. See JUDGE_UPGRADE.md and judge-story-tests.txt. No additional paid sessions were run.
