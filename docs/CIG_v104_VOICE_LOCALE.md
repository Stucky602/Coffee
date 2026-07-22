# CIG v104 — PM voice pass, em-dash cleanup, US/AU locale toggle, dev-panel spec
### Builds on v103 (merged Fable architecture + visual fixes). All flags still dark.

## What shipped in v104 (user-visible)

### 1. US ⇄ AU locale toggle (the flag buttons) — BUILT, tested
Two flag buttons live in the brand card (top-left, beside "☕ CIG"). Tapping the Australian flag
re-locales the ENTIRE app — every rendered surface, including the technical Learn pages — into
Australian English. Tapping the US flag returns to American English. Choice persists per device
(localStorage `cig_locale_v1`); US is the default (home market is Portland/Austin).

**How it works (the architecture that matters):**
- A `loc(str)` transform holds a curated, ordered US→AU map: spelling (flavor→flavour, colour,
  litre, caramelise, etc. — plurals handled automatically), vocab (to-go→takeaway, parking lot→car
  park), and a few gentle PM-isms (heaps of, brekkie, mates) on narrow triggers.
- Applied via `localizeApp()`, a **text-node walk** run after every render. This localizes BOTH
  data-driven text AND hand-written template copy, while NEVER touching tag names, attributes,
  URLs, or numbers/units (they aren't localizable text nodes). US = pure no-op.
- **Numbers/units are provably safe:** "18 g", "1:2.3", "92–96°C", "200 litres" — the dial-in
  recipes and all measurements pass through untouched (verified in qa_locale.js).
- Write-once: the data files stay US; AU is generated live. No dual copies of 136 pages.

### 2. PM voice on the high-visibility surfaces
The hero, section cards, and lead copy were rewritten toward Proud Mary's actual voice (researched
from their site: warm, direct, confident, a little cheeky — "no guessing, just the shapes"; "the
good stuff, none of the padding"). Per Kevin's call, the **technical Learn content stays in clear
technical speech** — PM voice belongs on the brand/orientation surfaces, not on extraction theory.
(A deeper page-by-page voice pass on intros is a Sonnet follow-on if wanted.)

### 3. Em-dash cleanup
Mid-sentence "pause" em-dashes (the AI tell) were removed from display copy — 47 lines cleaned,
converted to periods or commas by context. **Kept where structurally right:** number ranges
(92–96°C), the "Coffee — An Industry Guide" brand lockup, diagram null-markers ('—'), and
architecture comments. Per Kevin's rule: kill in prose, keep where it earns its place.

## What was SPEC'd (not built) — for a later Sonnet session

### CIG_DEVPANEL_SPEC.md — the hidden demo panel (long-press the version number)
A **dev/demo instrument for Kevin**, not a public feature. Long-press `#verlabel` (or `?dev=1`)
opens a hidden panel with a toggle per CIG_FLAGS entry, flipping a session-only in-memory
`FF_OVERRIDE` that `ff()` reads at highest priority. Lets Kevin reveal the dormant PM layer live in
an interview (hand Nolan the phone, tap, PM layer blooms) without typing a URL. Hidden by design so
the honest dark-ship posture survives. Gets more dramatic once `pm_house` is built (re-skins the
whole app). ~60–90 lines, Sonnet-tier. Full wiring + tests in the spec.

## Verification (all green on v104)
- `qa_v101.js`: **24/24** — architecture intact (dial-in, flags, catalog, CVA) through all the
  voice/locale changes.
- `qa_locale.js`: **13/13** — flag buttons render + inject SVGs, US default, AU switch localizes
  home + technical pages, US restores, dial-in numbers survive AU.
- `check_catalog.py`: OK (18 TODOs).
- JS parses; `APP_VERSION v104` + cache `coffee-guide-v104` agree.

## New files
- `src/locale_engine.js` — the source of the locale transform (also injected into build.py).
- `src/qa_locale.js` — the locale test suite (run alongside qa_v101.js every ship).
- `docs/CIG_DEVPANEL_SPEC.md` — the hidden-panel build spec.

## Notes for next session
- Locale map is curated, not exhaustive. Adding a term = one line in `AU_RULES` (vocab or
  spelling block) in locale_engine.js, re-inject, rebuild. Spelling rules auto-handle plurals.
- If a term over-triggers (localizes something it shouldn't), tighten its `\b` guard or move it to
  a narrower phrase trigger. The `fall ` (→autumn) rule already uses a trailing space to avoid
  "fall apart".
- Deeper PM-voice on Learn-section intros (keeping the technical bodies as-is) is the natural next
  content pass — Sonnet work, page by page.
