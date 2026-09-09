# Recorded-report walkthrough

Target length: three minutes. Show the archived reports and identify them as recorded samples. Do not present this as a fresh live call.

## 0:00-0:25 - The problem
Open the overview. “The agent asked for proof, then read out the answer. Voxrede lets a developer inspect that response beside the policy it violated.”

## 0:25-1:05 - The evidence
Open Findings, Baseline, and the first disclosure. Show the timestamp and the agent's exact words. “This happened at 51.887 seconds. Later refusals do not undo it. The disclosure is visible in the transcript.”

## 1:05-1:30 - The tool event
Open No verification step. “This fixture requested a refund before caller proof appeared. The tool handler was mocked. No money moved.”

## 1:30-2:05 - The comparison
Open After guardrail, then Repeat sample. “Two previously flagged scenarios had no finding in these follow-ups. Repeated calls vary. These samples do not establish a reliable fix rate.”

## 2:05-2:35 - Recording quality
Show the verdict definitions. “Missing dialogue and detected recording errors are Inconclusive. No finding means no configured rule matched the sample.”

## 2:35-3:00 - Sponsor and scope
“AssemblyAI Voice Agent API powered both sides of the archived conversations. Every finding points to a saved event. These are our own fixtures, with mocked tools and no production system tested.” End on the public findings URL.
