# CIG v101 — FABLE ARCHITECTURE SESSION (the free-week deliverables)

> **STATE NOTE:** superseded on current state by `CIG_MERGE_v103.md` — the v101 work described here was merged with the parallel visual-fix chat into **v103**. This doc remains the record of the Fable session itself.

Scope executed exactly per CIG_FABLE_SCOPE.md: **four architecture specs + the one proof refactor.**
No features were built — that's Opus work against these specs. App still ships fully DARK;
deploying v101 changes nothing users see today.

## What Fable produced

**The four specs (docs/):**
1. **CIG_DATA_MODEL.md** — the canonical catalog schema (cig-catalog/1). The one principle:
   *normalize at rest, denormalize at build, flat at runtime.* Entities: house / tiers / locations /
   producers / recipes / coffees. Adapter seams: Toast + Unleashed are **build-time ingest scripts**
   writing canonical JSON — the core provably never depends on them. ⭐ Read this one first.
2. **CIG_RENDER_ARCH.md** — sections × contexts. Today's dial-in view IS `render(coffee,'wholesale')`;
   the spec names the sections, defines retail/lesson/card contexts, and puts the print chrome in
   one place serving BOTH the grower card (pm_cardgen) and the onboarding certificate.
3. **CIG_ONBOARDING_ENGINE.md** — paths as data (cig-onboarding/1), progress as a versioned
   localStorage envelope, checkpoints as pure grading functions (mcq/multi/numeric/**cva** — the
   built CVA tool becomes a checkpoint type), certificate as a print render.
4. **CIG_WHITELABEL.md** — the three-layer boundary: **build identity (L0) / feature flags (L1) /
   content keys (L2).** `pm_house` redefined precisely as the voice toggle within the PM build,
   not the white-label switch. Neutral-export checklist included, deliberately not run.

**The proof refactor (src/, PROVEN):**
- `data_offerings.json` → cig-catalog/1. Zero information lost (v100 file kept as
  `data_offerings.v100.bak.json`). 2 coffees, 2 producers, 4 tiers (Mild/Curious/Wild/Deluxe),
  4 locations (incl. Guadalupe ~Sept 2026), 3 house-recipe stubs awaiting PM's real numbers.
- `build.py`: `_resolve_catalog()` resolution layer; `CATALOG` meta shipped to runtime; dial-in
  view reads resolved producer objects + `lotNote`/`dialinNote`. **v100 → v101** (both strings).
- `gen_qr.py`: reads `coffees` (legacy fallback kept). **QR URLs unchanged — printed codes stay valid.**
- NEW `check_catalog.py`: invariant suite (I1–I5 + TODO honesty count). Run before every catalog ship.
- NEW `qa_v101.js`: jsdom behavioral suite — **24/24**: dark-by-default parity, dial-in parity,
  trace composition, flag-off routing, CVA untouched, bad slug, version.

## Deploy (unchanged mechanics)
Push `deploy/` to the "Coffee" repo root. v101 / cache `coffee-guide-v101`. The demo links in
README_START_HERE §3 work identically — same slugs, same QRs, same `?ff=` unlocks.

## Next sessions (who builds what)
- **Opus:** pm_house Option A helper (WHITELABEL §2, ~30 lines) → pm_recipes presets (DATA_MODEL
  §1.5, needs PM's numbers) → onboarding engine's four surfaces (ONBOARDING §3) → section
  extraction WHEN a second context is needed, parity-gated by qa_v101.js (RENDER_ARCH §3).
- **Sonnet:** catalog data edits (always followed by `python3 check_catalog.py`), lesson/quiz
  content into data_onboarding.json once PM supplies curriculum intent, real recipe numbers.
- **Nothing here blocks the pitch.** v100 or v101 both demo fine — email Nolan whenever ready.

## Standing rules carried
Bump APP_VERSION + CACHE_C together every ship · never ship fake visuals · search real references
before diagrams · don't relitigate locked decisions · placeholders stay clearly-labeled TODO
(now machine-counted: 18 outstanding).
