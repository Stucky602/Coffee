# CIG v110 — diagram legibility in PM mode, tea leaf, robusta arc

## The big one: pale-background sweep (all SVG diagrams)
The SVG diagrams are authored for a DARK background (light bars, light text, gradient
fills tuned for dark). The `.diagram` card used `background: var(--panel)`, which is dark
in the neutral theme but goes CREAM in Proud Mary mode. On cream, the dark-theme diagram
content washed out and the data became hard to see.

Fix, one rule: in PM mode the diagram card is forced back to its dark surface
(`html[data-theme="pm"] .diagram { background:#1b140e; border-color:#3a2e24 }`, plus a
matching figcaption color and hover). Every SVG diagram now sits on the dark background it
was designed for, regardless of page theme. Verified across robusta, particle-size, and CVA
that the card computes to rgb(27,20,14) in PM mode.

## Robusta chart, two fixes
1. Bars were using the shared faint gradient (7-22% opacity), which barely reads even on a
   dark card, so the bars looked like floating tops. Gave the two bars dedicated solid
   gradients and brighter tans (#b39468 / #d8a94e). Pixel-verified the bar interiors now read
   as solid tan/gold top-to-bottom instead of fading into the background.
2. The green "+60% growth" arc was mis-anchored: control point pulled ~30px above the taller
   bar, so it spiked and read as a disconnected floating line. Re-drawn to span the GAP
   between the two bars, from the left bar's top-right to the right bar's top-left, with a
   gentle lift and the label tucked above the apex, clear of both value labels.

## Tea/coffee comparison image (teacoffee.png)
- Leaf was too big and its base overlapped the "TEA" label. Shrunk (LEN 104->92, WID 27->24)
  and raised 6px so it clears the label. Pixel-verified the row above the label is now clean
  background.
- Removed the stray semi-transparent "sheen" ellipse on the leaf's upper-left, which read as
  a weird smudge in a random spot (same class of issue as the earlier stray bean highlights).

## Verification
136 tests green (qa_v101 24, qa_locale 13, qa_devpanel 17, qa_pmmode 23, qa_pmtools 59).
Playwright + pixel-sampling confirmed bars/arc/leaf. Bumped APP_VERSION + CACHE_C to v110.
