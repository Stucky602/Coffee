# CIG v106 — full Proud Mary house mode + one-flip master switch

## The headline change: one switch does everything
Open the demo panel (long-press the version number, or `?dev=1`). The top control is now a
single **"Proud Mary mode"** switch. One tap:
- applies the full house theme (see below),
- swaps the CIG logo for Proud Mary's real wordmark,
- shows the hamsa emblem in the hero,
- flips the hero + footer copy to house voice,
- and turns on every built PM feature (the CVA cupping tool + the wholesale dial-in with
  producer stories) at once.

No more flipping 14 flags one at a time. The 14-flag view still exists, collapsed under an
"Advanced" disclosure, for dev testing — but the demo control is the single switch. Tap
"Reset to shipped state" and it all snaps back to the neutral dark app.

The theme persists per device (localStorage `cig_theme_v1`), and on reload the built features
re-enable automatically if PM mode was on — so a demo phone stays fully in PM mode between
sessions until you reset it.

## The re-skin is real now, not a tint
The earlier "PM theme" was a subtle brown recolor — wrong, and hard to see. This version uses
Proud Mary's **actual brand**, sampled pixel-by-pixel from their real hamsa-hand logo:
- powder blue `#7cc4dc`, butter cream `#f2eea6`, mint/seafoam `#27b388`, terracotta `#d08a52`,
  warm red `#c8503a`, black linework `#1a1a1a`.
- **PM runs LIGHT**: cream paper (`#f5f0df`), ink-black type — the opposite of the neutral dark
  app. Verified by pixel-sampling the rendered page: neutral background is `(22,14,8)` dark
  brown, PM background is `(246,241,225)` light cream. It's an unmissable transformation.

What changes on the flip: background, all text ink, the accent color (warm red), nav accents,
the heat bar (recolored to the brand spectrum blue→mint→cream→terra→red), card borders (bold
black PM outlines with offset shadows and a mint hover lift), the hero gradient, the section
headings, and the header logo. Every surface reads through CSS variables, so the swap is one
attribute (`data-theme="pm"` on `<html>`) touching the whole app.

## Real logo assets
Both of Proud Mary's real logos are now embedded as image files in `deploy/img/`:
- `pm-logo.png` — the horizontal "PROUD MARY" wordmark, shown in the header in place of "☕ CIG".
- `pm-emblem.png` — the full hamsa-hand-with-eye emblem, shown centered in the hero in PM mode.

Both are registered in `IMG_ASSETS`, copied into the build, and precached by the service worker
for offline use. Sourced from Proud Mary's own Shopify CDN (`logo-new_600x.png` and
`Proudmary-logo-header-simple_600x.png`), optimized to retina sizes.

## House copy
In PM mode the hero reads "The coffee, explained." with the lede "Everything behind the cup
you're about to make..." and the signature "Melbourne → Portland → Austin. Same standards, every
cup." The footer becomes "Proud Mary Coffee Roasters · Melbourne · Portland · Austin." Neutral
mode is untouched. This runs through the `pmOr(houseText, neutralText)` helper, so adding more
house copy later is a one-liner per string.

## Under the hood
- `pmModeOn()` — single source of truth (the theme is the master signal).
- `setPmMode(true/false)` — applies theme + toggles all `PM_BUILT_FEATURES` + updates footer.
- `togglePmMaster()` — the one-tap panel control.
- `PM_BUILT_FEATURES = ['cvatool','pm_dialin','pm_trace']` — the features that actually work
  today. When a reserved feature gets built, add it here and the master switch includes it.
- `updateFooter()` — house-aware footer copy.
- Everything is session-only (`FF_OVERRIDE`) except the theme (persisted deliberately). A normal
  visitor who never opens the panel sees the neutral dark app, unchanged.

## Verification — 77 tests green
- `qa_v101.js` 24/24 (architecture untouched)
- `qa_locale.js` 13/13 (US⇄AU untouched)
- `qa_devpanel.js` 17/17 (panel plumbing)
- `qa_pmmode.js` 23/23 (NEW — master switch on/off flips theme + all features + footer + hero
  copy + emblem together; persisted theme re-enables features on boot; dial-in reachable in PM
  mode without a URL flag; header wordmark slot present)
- `check_catalog.py` invariants pass
- Playwright computed-style + pixel checks confirm: cream background, near-black ink, warm-red
  accent, CIG text mark hidden, real PM wordmark shown (275px), hero emblem shown (126px), and
  the master switch UI flips theme on tap.

## What's NOT done / next
- Typography: still on Fraunces for display headings. A PM-specific display face (their wordmark
  is a bold slab) could push the house feel further — a good next step but not blocking.
- The deep methodology sentences that name-drop PM (Panama/Nicaragua) still read the same in both
  modes; routing those through `pm()` is a clean content pass when wanted.
- `og-card.png` still needs the Fraunces font to regenerate (unchanged, comes from the deploy
  folder). Not affected by this work.

## Deploy
Push `deploy/` contents to the repo root as before. The pm-logo.png and pm-emblem.png ride along
in `img/`. Bump was APP_VERSION + CACHE_C together to v106.
