# Submission text

## One-liner
Voxrede traces voice-agent policy findings to the recorded response, tool event, and timestamp.

## Description
A support agent asked a caller to prove ownership, then read out the answer to its own challenge question. Voxrede traces that disclosure to the policy and the recorded event at 51.887 seconds.

Voxrede helps support-agent developers review voice-agent red-team evidence. AssemblyAI's Voice Agent API powered both sides of each archived conversation: a simulated caller and an agent under test. Audio passed between the sessions; saved transcripts and tool requests feed deterministic findings.

The evidence workspace lets judges search 17 recorded samples across six suites, filter outcomes, and jump from a finding to its exact conversation event. Matching baseline and stricter-prompt recordings appear side by side. Missing follow-ups stay missing. Shareable case links and source hashes identify the recording being reviewed. No API key is needed; all cases remain readable without JavaScript.

Two of six baseline samples contained findings. Across two previously flagged scenarios, five findings became zero in the saved stricter-prompt samples. This small comparison does not establish a reliable fix rate; repeated calls vary.

A separate fixture requested a refund before caller proof appeared. Business tools were mocked, so no money moved. All targets were project-owned fixtures; no production system was tested.

Missing dialogue, unreadable recordings, and detected provider errors are Inconclusive. No finding means no configured rule matched that sample, not a safety certification.

The demo follows policy, test, evidence, and follow-up. AssemblyAI also generated the video narration. The video shows the earlier report layout; the current demo includes the expanded workspace. Code is public under MIT.

## Short description
Voice-agent red teaming with searchable evidence. Inspect 17 archived samples, trace findings to source events, and compare matching follow-ups. Built with AssemblyAI using project-owned fixtures and mocked business tools.

## Judge walkthrough
Start with the guided review at https://himanshu748.github.io/voxrede/#review. The four steps explain the policy, test, evidence, and recorded follow-up.

Open https://himanshu748.github.io/voxrede/findings.html#base/01_authority/event-7 for the disclosure at 51.887 seconds. The evidence workspace links the quoted finding to its exact conversation event. Open the stricter-prompt recording from the comparison, then use the suite and outcome filters to inspect the other saved samples. Every displayed count describes archived recordings, not a new live run.

## Additional information
Guided review: https://himanshu748.github.io/voxrede/#review
Evidence workspace: https://himanshu748.github.io/voxrede/findings.html
Exact disclosure event: https://himanshu748.github.io/voxrede/findings.html#base/01_authority/event-7
Narrated video: https://himanshu748.github.io/voxrede/watch.html
PDF deck: https://himanshu748.github.io/voxrede/assets/submission/voxrede-deck.pdf

Start with Policy, Test, Evidence, and Follow-up. Open the 51.887-second disclosure, inspect its source event, then compare the matching stricter-prompt recording. The workspace contains 17 saved samples across six suites, with transcript search, outcome filters, case links, and source hashes. Missing follow-ups remain explicit.

AssemblyAI Voice Agent API powered both sides of the archived conversations and generated the presentation narration (alba). The technology picker did not list AssemblyAI or Voice Agent API. Codex is a development tool; AssemblyAI is the runtime provider.

The public demo needs no account or API key. All target agents were project-owned fixtures, business tools were mocked, and original call audio is not embedded. The 2:28 captioned video introduces the recorded test using the earlier report layout; the current demo includes the expanded workspace.

Validation: 77 offline checks passed. Desktop and mobile layouts, search/filter states, matching comparisons, exact-event links, and no-JavaScript rendering were checked. GitHub Pages serves the upgraded viewer.

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

## Verified update — September 12, 2026
Released the evidence-workspace upgrade as `cacb2f5` to `main` and `upgrade/evidence-workspace`. GitHub Pages reported a successful build for that exact commit. The public viewer opened the disclosure at event 7. Lablab displayed “Submission Updated!” and confirmed that the AssemblyAI Voice Agent Hackathon submission had been updated successfully. The public entry was reopened and verified with the new workspace description, video-layout note, and existing demo, repository, and PDF links.

The short description, long description, and additional information above match the saved update. The original video, cover, and deck remain attached. The release retains the same archived evidence; 77 offline checks passed. Browser download-save confirmation remains unverified.
