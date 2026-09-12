# Submission text

## One-liner
Voxrede traces voice-agent policy findings to the recorded response, tool event, and timestamp.

## Description
A support agent asked a caller to prove ownership, then read out the answer to its own challenge question. Voxrede links that disclosure to the declared policy and the event at 51.887 seconds.

The archived conversations used the AssemblyAI Voice Agent API for both sides. Saved transcripts and tool requests feed a deterministic report: every finding points to an emitted event. The public pages let a reviewer inspect that evidence without an API key.

The evidence workspace contains 17 recorded samples across six suites. Reviewers can search transcripts, filter by suite or outcome, and jump from a finding to its exact source event. Matching baseline and stricter-prompt recordings appear side by side; missing follow-ups stay explicitly missing. Shareable case links and source-file hashes make a specific result easier to review. The workspace also works on mobile, and all cases remain readable without JavaScript.

Two of six baseline samples contained findings. Two previously flagged scenarios had no finding in recorded follow-ups with a stricter prompt: five findings became zero across those two samples. This is a small comparison, not a reliable fix rate. Repeated calls vary.

A separate fixture requested a refund before caller proof appeared. Its tool handler returned a mock result; no money moved. All targets were fixtures written for this project, and no production system was tested.

Missing dialogue, unreadable recordings, and detected provider errors are Inconclusive. No finding means no configured rule matched the sample; it does not certify safety or complete coverage.

AssemblyAI also generated the walkthrough narration. The video introduces the recorded test using the earlier report layout; the live demo includes the expanded evidence workspace. Code is public under MIT.

## Short description
Voice-agent red teaming with searchable evidence. Inspect 17 archived samples, trace findings to source events, and compare matching follow-ups. Built with AssemblyAI using project-owned fixtures and mocked business tools.

## Judge walkthrough
Start with the guided review at https://himanshu748.github.io/voxrede/#review. The four steps explain the policy, test, evidence, and recorded follow-up.

Open https://himanshu748.github.io/voxrede/findings.html#base/01_authority/event-7 for the disclosure at 51.887 seconds. The evidence workspace links the quoted finding to its exact conversation event. Open the stricter-prompt recording from the comparison, then use the suite and outcome filters to inspect the other saved samples. Every displayed count describes archived recordings, not a new live run.

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
