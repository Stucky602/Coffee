# Coffee — An Industry Guide

A working roasting reference for coffee professionals. Built as a self-contained, installable web app
for the roastery floor — no accounts, no network needed once loaded.

**Live:** https://stucky602.github.io/Coffee/

## What's in it

- **10 roast profiles** — Nordic through Italian, plus purpose-built Espresso and Omni. Each one breaks down
  the roast curve (charge, turning point, first crack, drop, total time, DTR in °F and °C), a phase-by-phase
  walkthrough, defects with cause and fix, and machine considerations.
- **Flavor radar** — every profile scored on a fixed six-axis scale (acidity, aroma, sweetness, body,
  bitterness, roast) so profiles are directly comparable at a glance.
- **Roast curve graph** — an idealized BT + RoR curve per profile, phase-shaded, with landmarks marked.
- **Compare view** — overlay up to four flavor radars.
- **Roasting knowledge** — 10 fundamentals pages: reading the curve, RoR, phases, cracks, DTR, chemistry,
  heat transfer, roaster types, defects, and profiling workflow.

Roasting-focused for now. Green sourcing, cupping/QC, and brewing are planned expansions.

## How it's built

Three source files compile to a single self-contained `index.html` plus PWA assets:

- `data_profiles.json` — the 10 profiles
- `data_methodology.json` — the 10 knowledge pages
- `build.py` — reads both, renders the HTML shell (radar + roast-curve SVG renderers, router), writes
  `index.html`, `sw.js`, `manifest.webmanifest`, and `icon.svg`

Edit a JSON, run `python3 build.py`, commit. No framework, no bundler.

## Deploy

GitHub Pages, deploy from `main` / root. Push the built files; the site serves `index.html` automatically.
Bump `APP_VERSION` and `CACHE_C` together in `build.py` when shipping so the service worker refreshes.

---

Temperatures are typical bean-temp ranges and vary by roaster. The phase relationships and ratios transfer
across machines better than absolute numbers do.
