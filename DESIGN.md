---
name: Voxrede
description: An editorial visual system for inspecting recorded voice-agent evidence.
colors:
  plum: "#2b2132"
  paper: "#f3f0e8"
  surface: "#eae6dc"
  raise: "#dfd9cd"
  line: "#cbc4b7"
  dim: "#665c67"
  faint: "#726673"
  citron: "#ddea8d"
  held: "#386047"
  held-bg: "#dbe7d8"
  disclosure: "#a13c28"
  disclosure-bg: "#f0ddd3"
  review-surface: "#352b3c"
  review-raise: "#44364c"
  review-line: "#594760"
  review-dim: "#c1b7c5"
  review-disclosure: "#ffac94"
  primary-hover: "#49374f"
  next-hover: "#eef4c7"
typography:
  display:
    fontFamily: "Manrope, sans-serif"
    fontSize: "clamp(48px, 6.8vw, 86px)"
    fontWeight: 600
    lineHeight: 1.01
    letterSpacing: "-.04em"
  headline:
    fontFamily: "Manrope, sans-serif"
    fontSize: "clamp(32px, 4.2vw, 56px)"
    fontWeight: 600
    lineHeight: 1.08
    letterSpacing: "-.035em"
  title:
    fontFamily: "Manrope, sans-serif"
    fontSize: "26px"
    fontWeight: 600
    lineHeight: 1.3
    letterSpacing: "-.025em"
  body:
    fontFamily: "Manrope, sans-serif"
    lineHeight: 1.65
  quote:
    fontFamily: "Instrument Serif, serif"
    fontSize: "27px"
    fontWeight: 400
    lineHeight: 1.3
  label:
    fontFamily: "Manrope, sans-serif"
    fontSize: "12px"
    fontWeight: 600
    lineHeight: 1.4
  source:
    fontFamily: "ui-monospace, monospace"
    fontSize: "10px"
    fontWeight: 400
    lineHeight: 1.6
rounded:
  replay: "4px"
  button: "5px"
  event: "6px"
  card: "7px"
  call: "8px"
  review: "12px"
spacing:
  control-gap: "12px"
  event-padding: "24px"
  review-grid-gap: "40px"
  page-inset: "48px"
  section: "90px"
components:
  button-primary:
    backgroundColor: "{colors.plum}"
    textColor: "{colors.paper}"
    rounded: "{rounded.button}"
    padding: "12px 17px"
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.plum}"
    rounded: "{rounded.button}"
    padding: "12px 17px"
  button-next:
    backgroundColor: "{colors.citron}"
    textColor: "{colors.plum}"
    rounded: "{rounded.replay}"
    padding: "8px 12px"
  button-next-hover:
    backgroundColor: "{colors.next-hover}"
  review-navigation:
    textColor: "{colors.review-dim}"
    typography: "{typography.label}"
    padding: "19px 0"
  event-card:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.event}"
    padding: "24px"
  status-label:
    textColor: "{colors.held}"
  review:
    backgroundColor: "{colors.plum}"
    textColor: "{colors.paper}"
    rounded: "{rounded.review}"
    padding: "30px 34px"
---

# Design System: Voxrede

## Overview

**Creative North Star: "Signal-routing studio"**

Voxrede uses a warm editorial page and a concentrated plum workspace to make recorded evidence readable. Manrope supplies direct labels and structure; italic Instrument Serif distinguishes speech and headline emphasis. The overall character is restrained, precise, and conversational.

Surfaces are flat and organized through tone, spacing, and fine rules. Color identifies review progress and observed outcomes. The local dark review surface is part of the light page, rather than a separate global theme.

**Key Characteristics:**
- Warm ivory page with a local plum review surface.
- Citron for the current review state and next-step control.
- Serif italic for speech; monospace for source identifiers.
- Fine borders, modest corners, and flat controls.

## Colors

Warm paper and muted plum support a small set of functional accents. Frontmatter values are normative and extracted from `design.css`.

### Primary

- **Deep Plum** (`plum`): primary page text, primary action fill, and the review container's ground.
- **Signal Citron** (`citron`): current review step, next-step button, source links inside the review, and text selection.

### Secondary

- **Disclosure Rust** (`disclosure`, `disclosure-bg`): recorded disclosure and tool-trigger treatments on ivory surfaces. The CSS aliases `leaked` and `fired` share these values.
- **Disclosure Coral** (`review-disclosure`): recorded disclosure emphasis inside the plum review.
- **Held Green** (`held`, `held-bg`): held-policy status and its pale background; always retain the textual status.

### Neutral

- **Warm Paper** (`paper`): page background and text on plum.
- **Linen / Raised Linen** (`surface`, `raise`): page containers and tonal separation.
- **Stone Rule** (`line`): page borders and dividers.
- **Muted Plum Text** (`dim`, `faint`): secondary page text.
- **Review Plum Layers** (`review-surface`, `review-raise`): local review surface and hover layer.
- **Review Rule / Muted Lilac** (`review-line`, `review-dim`): borders and supporting text on plum.
- `primary-hover` and `next-hover` are existing action hover fills, not additional status colors.

**The Local Surface Rule.** Keep the plum review palette scoped to its container; the surrounding page and archived reports remain ivory.

## Typography

**Display / Body Font:** Manrope, sans-serif. Self-hosted at weights 400, 600, and 800.

**Speech / Emphasis Font:** Instrument Serif, serif. Self-hosted at weight 400, italic only.

**Source Font:** ui-monospace, monospace.

The font files and OFL licenses live in `assets/fonts`. The serif's narrow, expressive forms contrast with the clear sans-serif interface. Body size varies by context; the shared body token intentionally records only the family and line height set in `design.css`.

### Hierarchy

- **Display:** main headline; use the display token with a narrow measure (15ch). Italic emphasis scales to 1.12em.
- **Headline:** section titles; use the headline token.
- **Title:** guided review detail headings; use the title token with a maximum measure of 24ch.
- **Body:** introductory text is 16px with 1.8 line height and a 43ch measure; review detail is 14px with paragraph line height 1.75.
- **Quote:** review speech uses the quote token in italic. Evidence quotations scale with `clamp(27px, 3.3vw, 44px)` and a 1.25 line height.
- **Label / Source:** controls use Manrope; source identifiers use the source token and wrap long hashes.

**The Speech Rule.** Use Instrument Serif in italic for quoted speech and deliberate headline emphasis; keep controls in Manrope.

## Layout

The desktop container has a 1280px maximum width with the page-inset token. Section spacing uses the section token. The introductory grid is 1.4fr / 1fr with a 50px gap; the review uses .94fr / 1.25fr with the review-grid-gap token. The signal diagram is separated from the detail by a fine vertical rule.

At 1000px and below, page insets become 32px, review padding becomes 26px, and the headline becomes 64px. At 700px and below, page insets become 22px, the headline becomes 57px, and the review stacks the diagram above the evidence. The diagram separator becomes horizontal; review padding becomes 22px 18px, section spacing becomes 52px, and the navigation height changes from 82px to 66px. Source identifiers remain available in detail even where compact diagram metadata is hidden.

The evidence workspace uses a wider container (1500px maximum): a narrow case index (300px, reducing to 255px at 1000px) sits beside the primary evidence document. At 700px and below, the index becomes a collapsible section above the document. It starts collapsed when JavaScript is active; without JavaScript, the index and every recorded case remain available.

## Elevation & Depth

The shared stylesheet defines no shadow tokens. Tonal layers, spacing, and one-pixel rules provide separation. Navigation has no backdrop blur. Primary buttons change fill on hover without lifting.

**The Flat Surface Rule.** Use tonal separation and fine borders for depth; the current visual system defines no shadow tokens.

## Shapes

Corners are modest and component-specific: buttons use the button radius, replay controls the replay radius, event cards the event radius, report cards the card radius, and transcript containers the call radius. The large review uses the review radius on desktop and the call radius on mobile. Recorded findings and highlighted transcript rows retain square geometry. Dividers are predominantly one pixel; the active review step uses a two-pixel underline.

## Components

### Buttons

Compact, flat controls. The primary page action uses plum on paper, while the next-step action uses citron on plum. The ghost action remains transparent with a fine border. Primary and ghost buttons use 12px Manrope at weight 600. Replay controls use 11px Manrope at weight 600 and 1.5 line height.

Page buttons transition background and color over .18s; replay buttons transition background over .16s. Keyboard focus is a two-pixel outline offset by five pixels. Disabled review controls use .5 opacity.

### Cards / Containers

Event cards use linen, a fine stone border, and the event-padding token. Archived report cards use linen and the card radius. The review container establishes its own paper text, muted lilac support text, plum layers, and review rules. Do not let root secondary text colors leak into this dark surface.

### Status Labels

Compact Manrope labels identify held, disclosed, and tool-trigger outcomes. Labels remain readable text; color supplements their meaning. They are status annotations rather than interactive filters.

### Navigation

The page navigation is an opaque ivory bar with a fine bottom rule and a Manrope wordmark at weight 800. Desktop links use 12px text; those links are hidden on mobile. Review navigation keeps Policy, Test, Evidence, and Follow-up visible, with citron text and an underline on the current step. The mobile review labels shrink to 10px and distribute across the width.

### Signal Review

The paired caller and target diagram routes a recorded conversation into inspectable evidence. Step changes highlight the associated diagram element. Only the test step animates the connector: a dashed path moves over 1.5s, linearly and continuously, only when reduced motion is not requested. This depicts the selected test step, not live telemetry. Transcript replay, audio availability, and source references retain their explicit labels. The signal review does not use input fields.

### Evidence Workspace

The searchable case index uses compact, labeled search and select controls with fine borders and modest corners. Suite and outcome filters retain a visible result count and reset action. The selected case uses plum with paper text; written verdicts remain distinct from selection state.

The ivory evidence document presents findings, the recorded comparison, then the transcript. Exact event anchors connect each finding to its matching source row and give that row a visible outline. Missing or incompatible comparison samples receive an explicit explanation; incomplete recordings keep their quality notice. Case links and evidence exports support sharing without changing the recorded material. Search, filters, sharing controls, and speaker selection progressively enhance the fully rendered archive.

## Do's and Don'ts

### Do:

- Do preserve the local review color overrides when moving a component into the plum surface.
- Do use the self-hosted font files and their supplied weights.
- Do retain visible keyboard focus, reduced-motion support, and readable no-JavaScript content.
- Do pair status color with readable labels and source-backed evidence.

### Don't:

- Don't turn the local plum surface into an app-wide dark theme.
- Don't imply a live call, audio playback, or safety certification through decorative status UI.
- Don't use citron and disclosure coral interchangeably.
- Don't replace the fine borders and flat hover states with ornamental elevation.
