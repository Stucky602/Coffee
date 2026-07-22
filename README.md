# Coffee: An Industry Guide

A self-contained coffee reference PWA. Live at **https://stucky602.github.io/Coffee/**

Everything at the root of this repo is the deployed site. GitHub Pages serves it directly.

---

## What's here

| Path | What it is |
|---|---|
| `index.html` | The entire app. One file, all data inlined. |
| `sw.js` | Service worker. Caches by version string for offline use. |
| `manifest.webmanifest` | PWA manifest (installable to a phone home screen). |
| `icon.svg` | App icon. |
| `img/` | Raster diagrams, QR codes, and the Proud Mary logos. |
| `fonts/` | Fraunces (display face). |
| `src/` | **Build source.** Not served. See below. |
| `docs/` | Version notes and architecture docs. Not served. |

`src/` and `docs/` are ignored by GitHub Pages. They live here so the project is
recoverable and versioned, not because the site needs them.

---

## Deploying an update

1. Replace `index.html`, `sw.js`, `manifest.webmanifest`, `icon.svg`, and anything
   changed under `img/`.
2. **Replace `index.html` AND `sw.js` together, always.**

That second point matters. The service worker caches by version string
(`coffee-guide-vNNN`). If you upload a new `index.html` but leave the old `sw.js`,
returning visitors keep getting the cached old build and will not see your changes.
`APP_VERSION` and `CACHE_C` in `build.py` are bumped together every ship for this reason.

---

## Rebuilding from source

```bash
cd src
python3 build.py          # writes index.html, sw.js, manifest, icon into src/
```

Then copy those outputs to the repo root.

Regenerating the raster diagrams (only needed if you change them):

```bash
python3 gen_extras.py     # writes into src/img_src/
python3 gen_defects.py
cp img_src/*.png img/
```

## Tests

```bash
cd src
node qa_v101.js      # core architecture
node qa_locale.js    # US / AU locale switching
node qa_devpanel.js  # demo panel plumbing
node qa_pmmode.js    # Proud Mary master switch
node qa_pmtools.js   # Proud Mary tools, catalog, and back-navigation
python3 check_catalog.py
```

All five suites should pass clean before shipping. Current total: 169 tests.

---

## Demo mode

Long-press the version number (or add `?dev=1`) to open the demo panel. The headline
control is a single **Proud Mary mode** switch: one flip applies the house theme, logo,
copy, and every built feature, and reskins the guide around Proud Mary's actual catalog
(tiers, current lots, cafes). Nothing is saved to the live site; it is session-only
apart from the theme itself.
