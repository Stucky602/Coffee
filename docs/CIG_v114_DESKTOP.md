# CIG v114 — desktop presentation

The app was built mobile-first and, on a wide monitor, read as a narrow column
stranded on the left with a large empty right half. Bar mode, a wet-hands
behind-the-counter feature, also floated over the corner of a desktop screen
where it makes no sense.

## What changed

**Wider measure on large screens.** `.wrap` grows from 1120px to 1240px at
1000px+, and to 1360px at 1500px+. Below 1000px nothing changes.

**PM hero becomes two columns.** The emblem sits in a 300px left column with the
headline, lede, heat bar, and signature stacked in the right column, vertically
centred. Previously the emblem was centred above left-aligned text that was
capped at a 15ch measure, which is what produced the lopsided look.

*Bug found while doing this:* the hero grid was applying to every direct child of
`.hero .wrap`, so the lede and signature were each being placed into their own
grid cell and squeezed to 300px. Fixed by wrapping the text in a `.herocopy`
container so the grid has exactly two children.

**Denser grids.** On desktop: hub 3 columns, origins and menu 4 (5 at 1500px+),
quality fields 3, origin lots 3, menu strip 6. The diagnostic list and visit
checklist go to 2 columns, and the freshness tool puts its controls and verdict
side by side.

**Bar mode is hidden at 1000px and up.** It remains on tablets at 900px, where
touch is still the input method.

**Neutral hero gets room too.** The headline measure goes from 15ch to 22ch and
the lede from 64ch to 70ch on wide screens.

**Toolkit bar and sub-row** align their contents to the same measure as the page
rather than spanning the raw viewport width.

## New test suite: `qa_responsive.py`

Media queries need a real browser, so this one is Playwright-based rather than
jsdom. 24 checks across 1800px, 900px, and 420px covering the wrap width, hero
layout, column counts, bar-mode visibility, neutral-mode isolation, and
horizontal overflow on every new view at phone width.

Run it with `python3 qa_responsive.py` from `src/`.

## Verification
- JS suites 200 (qa_v101 24, qa_locale 13, qa_devpanel 17, qa_pmmode 23, qa_pmtools 123)
- Responsive suite 24
- **Total 224**, no failures. No horizontal overflow at any tested width.

Bumped APP_VERSION + CACHE_C to v114 together.
