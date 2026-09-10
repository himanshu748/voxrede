# Voxrede

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Hackathon judges evaluating whether Voxrede clearly demonstrates voice-agent red teaming. The developer uses the same evidence viewer to inspect recorded findings.

## Product Purpose

Make a declared policy, the test conversation, its observed finding, and a recorded follow-up easy to inspect. The user explicitly requested a designer-quality palette and a demonstration of how the project works.

## Capabilities and Constraints

The current evidence comes from two AssemblyAI Voice Agent sessions created from local configurations. Business tools are mocked. The current redesign is a passive archived-evidence viewer and does not initiate new tests. The page must distinguish a recorded transcript replay from audio playback and from a live call. A no-finding sample does not certify safety or a reliable fix.

## Evidence on Hand

`evidence/report_base.json`, `evidence/report_hardened.json`, and archived event logs support the guided authority-impersonation review. The baseline finding is at 51.887 seconds. The first baseline finding has no bundled audio. The complete reports remain accessible from the overview.

## Brand Commitments

Keep the name Voxrede, the project's factual claims, the guided review, and its archived evidence. The user rejected the previous palette and requested a replacement visual treatment. Implementation is code-first per the user's standing instructions.

## Product Principles

- Make the red-teaming mechanism understandable before asking a judge to inspect detail.
- Connect findings to their recorded evidence.
- Keep fixture, mock-tool, and sample limitations visible.
- Preserve keyboard access, reduced-motion behavior, and readable content without JavaScript.
