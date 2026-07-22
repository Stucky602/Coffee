# Coffee: An Industry Guide

A self-contained coffee reference PWA. Live at **https://stucky602.github.io/Coffee/**

Everything at the root of this repo is the deployed site. GitHub Pages serves it directly.

| Path | What it is |
|---|---|
| `index.html` | The entire app. One file, all data inlined. |
| `sw.js` | Service worker. Caches by version string for offline use. |
| `manifest.webmanifest` | PWA manifest (installable to a phone home screen). |
| `icon.svg` | App icon. |
| `img/` | Raster diagrams, QR codes, and the Proud Mary logos. |
| `fonts/` | Fraunces (display face). |
| `src/` | Build source. Not served. |
| `docs/` | Version notes and architecture docs. Not served. |

## Deploying an update

**Replace `index.html` AND `sw.js` together, always.** The service worker caches by version
string (`coffee-guide-vNNN`). Ship a new `index.html` with a stale `sw.js` and returning
visitors keep the old cached build. `APP_VERSION` and `CACHE_C` in `build.py` are bumped
together every ship for exactly this reason.

## Rebuilding

```bash
cd src
python3 build.py     # writes index.html, sw.js, manifest, icon into src/
```

Then copy those outputs to the repo root.

## Tests

```bash
cd src
node qa_v101.js qa_locale.js qa_devpanel.js qa_pmmode.js qa_pmtools.js   # run individually
python3 check_catalog.py
```

All five suites should pass clean before shipping. Current total: 200 tests.

## Demo mode

Long-press the version number (or add `?dev=1`) to open the demo panel. The headline control
is a single **Proud Mary mode** switch: one flip applies the house theme, logo, and copy, and
reskins the guide around Proud Mary's actual catalog, tiers, and lots. In PM mode a **Bar
mode** toggle also appears for behind-the-counter use. Nothing is saved to the live site
apart from the theme and bar-mode preferences.
