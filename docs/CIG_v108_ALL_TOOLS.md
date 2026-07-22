# CIG v108 — every flag now has a demo

## What this adds
v107 built the first five hub tools. v108 fills in the remaining eight flags, so the master
switch now lights up a full toolkit. The hub has two sections: **Pick a tool** (the eight
Proud Mary tools) and **Explorer tools** (four general-purpose ones). 12 cards total.

### New Proud Mary tools
- **Partner portal** (`pm_wholesale`). A wholesale-facing landing that bundles the four tools a
  café partner actually needs — dial-in recipes, staff onboarding, QC cupping, house standards —
  in one place. A live version would gate behind a partner login and show that partner's lots.
- **Menu decoder** (`pm_menu`). A plain-English "what am I drinking" guide to every drink on the
  board (espresso through cold brew), with rough sizes. The café-facing till/QR tool.
- **Grower-story cards** (`pm_cardgen`). Pick a coffee, get a print-ready shelf/bag card — the
  story, tasting notes, specs, and producer line, with a Print button (print CSS hides the app
  chrome and prints just the card). Honestly suppresses any TODO-placeholder values rather than
  printing "TODO masl".

### New Explorer tools (general, not PM-specific)
- **Flavor face-off** (`radarcompare`). Two roast profiles overlaid on one radar, plus a per-axis
  delta table. (Note: the core Compare tab already overlays radars/curves; this is a focused,
  faster 2-up picker, and overlaps that tab by design.)
- **Roast playground** (`roastplay`). Drag sliders for total time, development ratio, and charge/
  drop temps; the roast curve and live readouts (development minutes, DTR, temp rise) update in
  real time. A feel-tool for how the levers interact — not a profiler.
- **Brew face-off** (`brewcompare`). Two brew methods side by side at the same water weight, so you
  can see how dose, grind, temp, and time differ. Reuses the real BREW_METHODS data.
- **Glossary** (`glossaryhub`). A dedicated, searchable page for all 43 glossary terms (they exist
  inline as popovers everywhere, but there was no standalone reference page).

## The one flag left alone
`pm_house` is not a feature — it's an alias of PM mode itself (the theme is the master signal via
`pmModeOn()`). It stays as the single "reserved" flag and renders disabled in the Advanced panel.
Every other flag now has a working demo.

## Honesty pass
The grower-story card and dial-in producer sections now filter out TODO-placeholder text
everywhere: TODO producer names, TODO altitudes, and the "TODO — PM producer story" stub all get
suppressed, replaced with an honest "Grower story to come — Proud Mary's to write." A pitch demo
should never print a literal "TODO" on a card.

## Architecture (unchanged pattern)
- Routing: added `radarcompare`, `roastplay`, `brewcompare`, `glossaryhub`, `pmmenu`, `pmcardgen`,
  `pmwholesale2` views; all map to the PM nav-tab highlight.
- Each tool guards on its own `ff()` flag and bounces to the hub if off, so the Advanced panel can
  still toggle any one individually; the master switch flips the whole set (`PM_BUILT_FEATURES` now
  lists all 13 built flags).
- Reused existing renderers: `radar()`, `roastCurve()`/`buildCurve()`, `BREW_METHODS`,
  `glossaryRows()`, `pmToolCard()`. No new data files needed.

## Verification — 130 tests green
- qa_v101 24 · qa_locale 13 · qa_devpanel 17 · qa_pmmode 23 · **qa_pmtools 53** (was 29; +24 for the
  new tools: render, per-flag guard-to-hub, hub-shows-12, master-enables-all-13, roastplay
  interactivity, cardgen TODO-suppression)
- check_catalog invariants pass
- Playwright end-to-end: all 12 hub cards present under the right two section headers; every tool
  renders and is interactive (radar overlay draws, roastplay curve+DTR update live, brewcompare
  shows two columns, cardgen renders a printable card with no TODO leakage).

## Still demo / next
- The two coffees' producer names and the house-recipe numbers remain PM's to supply (shown
  honestly as "to come" / "awaiting values"). 18 TODO markers tracked by check_catalog.
- Typography still on Fraunces; a PM slab display face is the natural next polish.

## Deploy
Push `deploy/` to the repo root. Bumped APP_VERSION + CACHE_C to v108 together.
