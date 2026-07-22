# CIG_MERGE_v103 — the reunification (Fable architecture × visual fixes)
### Two parallel chats, one build. This doc is the top-of-stack state record as of v103.

**The situation:** Kevin ran two chats in parallel off v100. Chat A (Fable) did the architecture
work → **v101** (catalog schema cig-catalog/1, resolver, invariant suite, 4 specs). Chat B (visual)
did live-site diagram QA → **v102** (5 surgical diagram fixes + all raster diagrams regenerated at
2×). Neither contained the other's work. **v103 = both, merged, verified.**

## Merge direction (per Chat B's own handoff guide)
Fable v101 `src/` was the base — authoritative on architecture. Chat B's changes were folded IN.
Version continues past both lines: **v103** (`APP_VERSION` + `CACHE_C` together, as always).

## Exactly what was folded in from the visual chat
| fix | file | what |
|---|---|---|
| 1 — 2× raster output | `gen_extras.py` `finish()`, `gen_defects.py` (2 saves) | diagrams save at 2× device scale; text crisp on high-DPI. Every diagram PNG doubled in pixel dims. |
| 2 — green-metrics card | `gen_extras.py` `gen_greenmetrics` | short card values + auto-fit shrink loop, cw 180→182 |
| 3 — Fine Robusta | `build.py` `diaRobustaRise` (whole-function swap) | **math fix: "+60% growth" → "+15 pts of share"**, straight arrow between bar tops, taller driver cards (48→54), bmax 140/by 205 |
| 4 — Heat Transfer | `build.py` `diaHeat` (whole-function swap) | convection C-curves → clean single Q-curves rising from the bean mass; conduction arrow 3→3.5 |
| 5 — Roaster hybrid duct | `gen_extras.py` `gen_roasters` | clean external recirculation loop |

**Deliberately NOT taken from Chat B:** its `build.py` data layer (still flat v100 — superseded by
the resolver), its `data_offerings.json` (flat v100 — superseded by cig-catalog/1), its
`gen_qr.py` (pre-schema — the catalog-aware one stays). Its `CIG_MASTER_CONTINUITY.md` is kept as
project history but is v100-stale on state; THIS doc supersedes it on current state.

## Images: taken, not regenerated
The sandbox has no `img_src/` source assets, so regeneration wasn't possible here — and wasn't
needed: Chat B's `deploy/img/` already contains every diagram regenerated at 2× (verified:
greenmetrics 1520×540, roasters/cupping 1520×600 vs 760× base; og-card correctly UNCHANGED at
1200×630, matching the `og:image` meta; both QR PNGs unchanged, URLs still valid). v103 ships Chat
B's image set as-is. **On Kevin's machine, the next image change regenerates from source per the
standing recipe:** `python3 gen_extras.py && python3 gen_defects.py && python3 build.py`.

## Verification (all on the merged v103 artifact)
- **Residual-diff audit:** merged `build.py` vs Chat B's differs ONLY in the Fable hunks + version
  (66 lines, zero diagram terms) — proof the diagram merge is complete and nothing else leaked.
- `check_catalog.py`: OK (2 coffees, 2 producers, 4 tiers, 4 locations, 3 recipes, 18 TODOs).
- Architecture suite (`qa_v101.js`, version assertion now evergreen): **24/24** — dark-by-default,
  dial-in parity, trace composition, flag routing, CVA, bad slug.
- Diagram smoke (jsdom): `heat` page renders the new Q-curve arrows; `fine_robusta` page renders
  "+15 pts of share" and the old "+60% growth" is GONE.
- JS parses; sw cache `coffee-guide-v103` agrees with `APP_VERSION v103`.

## Still open (carried from Chat B)
Kevin's live-site visual pass continues — expect more diagram flags. The pattern: raster issues →
`gen_extras.py`/`gen_defects.py` (regenerate after), SVG issues → `build.py` `diaXxx()` functions.
~18 diagrams not yet eye-reviewed. No other known bugs.

## State after this merge
**v103, all flags dark, deploy-ready.** Contains: full Fable architecture (dormant) + all 5 visual
fixes + 2× diagrams (live-visible improvements — the ONLY user-visible change in v103 is sharper,
corrected diagrams). Next work: Opus/Sonnet tasks per README_FABLE_SESSION.md — nothing Fable-tier
remains.
