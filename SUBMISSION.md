# Submission text

## One-liner
Voxrede traces voice-agent policy findings to the recorded response, tool event, and timestamp.

## Description
A support agent asked a caller to prove ownership, then read out the answer to its own challenge question. Voxrede links that disclosure to the declared policy and the event at 51.887 seconds.

The archived conversations used the AssemblyAI Voice Agent API for both sides. Saved transcripts and tool requests feed a deterministic report: every finding points to an emitted event. The public pages let a reviewer inspect that evidence without an API key.

Two of six baseline samples contained findings. Two previously flagged scenarios had no finding in recorded follow-ups with a stricter prompt: five findings became zero across those two samples. This is a small comparison, not a reliable fix rate. Repeated calls vary.

A separate fixture requested a refund before caller proof appeared. Its tool handler returned a mock result; no money moved. All targets were fixtures written for this project, and no production system was tested.

Missing dialogue, unreadable recordings, and detected provider errors are Inconclusive. No finding means no configured rule matched the sample; it does not certify safety or complete coverage.

## Positioning
Voice-agent security testing already exists. Bluejay offers red teaming and AssemblyAI integration. Voxrede's focus here is an inspectable policy-linked evidence report for support-agent developers, with recording quality kept separate from findings. That is a product focus, not a claim to have invented the category.

Source: https://getbluejay.ai/blog/bluejay-x-assemblyai-test-voice-agents-built-on-the-voice-agent-api

## Public links
Code: https://github.com/himanshu748/voxrede
Overview: https://himanshu748.github.io/voxrede/
Findings: https://himanshu748.github.io/voxrede/findings.html
Deck: https://himanshu748.github.io/voxrede/deck.html
PDF: https://himanshu748.github.io/voxrede/assets/submission/voxrede-deck.pdf
Video: https://himanshu748.github.io/voxrede/watch.html
MP4: https://himanshu748.github.io/voxrede/assets/submission/voxrede-demo.mp4
Cover: https://himanshu748.github.io/voxrede/assets/submission/cover.png

## Submission status
Submitted to the AssemblyAI Voice Agent Hackathon on September 10, 2026. Lablab displayed “You have successfully submitted your project” and “Your submission has been accepted!” The saved project page was opened and verified with video, presentation, repository, and demo links.

Submission: https://lablab.ai/ai-hackathons/assemblyai-voice-agent-hackathon/voxrede/voxrede
Team: https://lablab.ai/ai-hackathons/assemblyai-voice-agent-hackathon/voxrede
Submission ID: uw1kvt29nhaowqilxa2w1389

The public demo and PDF deck are deployed. The uploaded 2:28 video uses AssemblyAI Voice Agent API narration (alba); it shows edited captures of the archived report viewer, not a new test call. The team is solo and closed. Discord connection is complete.

The technology picker did not offer AssemblyAI or Voice Agent API. Codex was selected as a development tool; the submission description and additional information explicitly identify AssemblyAI as the runtime and narration provider.

Multiple entries have not been confirmed as permitted by this event's published rules. Submission acceptance is not a judging result.
