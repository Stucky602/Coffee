# CIG_DATA_MODEL — the canonical catalog schema (cig-catalog/1)
### Fable architecture artifact #1 · PROVEN in v101 · the spine every PM feature hangs off

**Status:** implemented and shipping (dark) as of v101. `data_offerings.json` IS this schema now;
`build.py` resolves it; `check_catalog.py` enforces it; `qa_v101.js` proves the runtime (24/24).
This doc is the contract for every future session that touches catalog data or builds a PM feature.

---

## 0. THE ONE PRINCIPLE

**Normalize at rest. Denormalize at build. Flat at runtime.**

- **At rest** (`data_offerings.json`): entities + id references. A producer is written ONCE and
  referenced by every lot they've ever grown. This is what makes the file Sonnet-editable (change a
  producer's story in one place) and adapter-ingestable (an Unleashed import emits records into
  known collections).
- **At build** (`build.py :: _resolve_catalog`): references become embedded objects. Each coffee's
  `producer: "la-salvaje"` string becomes the full producer object. This single function is the
  choke point where ALL joining happens — and therefore the seam where adapters plug in.
- **At runtime** (the shipped JS): `OFFERINGS` is a flat array of fully-resolved coffee records plus
  a small `CATALOG` meta object. The client does zero joins. Views stay dumb, fast, and testable.

Why this matters: every alternative loses something. Denormalized-at-rest (the old flat file) meant
producer stories duplicated per lot and no place for locations/tiers to live. Normalized-at-runtime
would push join logic into 400KB of client JS that five different views would each reimplement
slightly differently. The build step already exists — resolution is free there.

---

## 1. ENTITY REFERENCE

Top-level shape of `data_offerings.json`:

```
{ "schema": "cig-catalog/1", "_note": "...",
  "house": {...}, "tiers": [...], "locations": [...],
  "producers": [...], "recipes": [...], "coffees": [...] }
```

### 1.1 `coffees[]` — the center of the graph
| field | type | req | semantics |
|---|---|---|---|
| `slug` | string | ✓ | Stable URL identity. **Never changes once a QR is printed** — the slug IS the contract with physical bags. Kebab-case. |
| `name` | string | ✓ | Display name. |
| `origin` | string | ✓ | Country. |
| `variety`, `process`, `roast` | string | – | Identity line. |
| `notes` | string[] | – | Tasting-note chips. |
| `producer` | id → `producers[]` | – | Reference; resolved to the object at build. |
| `tier` | id → `tiers[]` | – | Reference; resolved at build. Drives the subscription CTA. |
| `lotNote` | string\|null | – | THIS lot's one-liner (COE placement, harvest note). Lot-specific; the producer's `story` is the durable family/farm narrative. The split exists so producers persist across seasons while lots turn over. |
| `channels` | subset of `["wholesale","retail","cafe"]` | – | Which render contexts may show this coffee (see CIG_RENDER_ARCH). Default: all. |
| `dialin` | `{espresso?, batch?, home?}` | – | Per-coffee starting points, embedded (owned by the lot, drifts per bag — never shared). Block shapes below. |
| `dialinNote` | string | – | The honest "every bag drifts 4–6s; re-dial" line. |
| `links` | `{shop?: url\|null}` | – | Outbound commerce links. Plain URLs only — see §3. |

`dialin.espresso`: `{dose_g, yield_g, time_s, ratio, temp, grinder}` ·
`dialin.batch`: `{ratio, grind, temp, time}` ·
`dialin.home`: `{method, dose_g, water_g, grind, temp, time}`.
All fields optional; the view renders only what's present (row() skips empties).

### 1.2 `producers[]` — the durable story entity
| field | type | semantics |
|---|---|---|
| `id` | string ✓ | Referenced by `coffee.producer`. |
| `name` | string | Family / producer name. |
| `farm` | string | Farm/estate name. |
| `region`, `altitude` | string | Farm attributes (they belong HERE, not on the coffee — a farm's altitude doesn't change per lot). |
| `story` | string | The grower-family narrative. **This one field feeds THREE surfaces:** the `pm_trace` screen block, the printed grower card (`pm_cardgen`), and onboarding story lessons. Write it once, render it everywhere — that's the point of the entity. |
| `originPage` | METHODOLOGY id\|null | Deep-link into the existing origin pages/maps (e.g. `origin_honduras`). Validated by check_catalog I5. Reuses the origin maps Kevin likes — never duplicates them. |

### 1.3 `tiers[]` — Mild / Curious / Wild / Deluxe
`{id, name, blurb, subscribeUrl}`. PM's real subscription taxonomy. A coffee references its tier;
the tier carries the CTA. Education→sales loop lives here and only here.

### 1.4 `locations[]` — the multi-location reality
`{id, name, address, lineup: {espresso:[slugs], filter:[slugs], retail:[slugs]}, note?}`.
The lineup lives ON the location because that's where the weekly edit happens ("what's on at
Guadalupe"). Slugs are validated (I3). Current entries: austin-slamar, austin-guadalupe (opening
~Sept 2026 — the consistency use case this schema exists for), portland-alberta,
melbourne-collingwood.

### 1.5 `recipes[]` — SHARED house presets (distinct from per-coffee dialin)
`{id, kind: pourover|batch|espresso, name, status, ...numbers}`. Two kinds of recipe exist and the
model keeps them apart deliberately: **per-coffee dial-in** is embedded in the coffee (it drifts
with the lot); **house presets** ("PM Café Pourover") are shared, referenced, and feed the brew
calculator under `ff('pm_recipes')`. Three stubs ship with all numbers `null` + status TODO —
the seam is proven, the numbers are PM's to supply. Build recipe for `pm_recipes` (Opus): map these
into `BREW_METHODS`-shaped rows in a `house:true` group, shown only under the flag.

### 1.6 `house{}` — the identity block
`{id:"pm", name, footer, links:{site, academy, subscribe}}`. The ONLY place brand identity lives in
data. See CIG_WHITELABEL for how this interacts with build identity and the `pm_house` flag.

---

## 2. THE RELATIONSHIP GRAPH

```
                 tiers ──────────┐ (CTA)
                                 ▼
 producers ──story──▶  COFFEE (slug = printed-QR contract)
     │                   ▲   │
     │ originPage        │   └─ dialin (embedded, per-lot)
     ▼                   │
 METHODOLOGY        locations.lineup (slugs)      recipes (shared presets)
 origin pages                                      └─▶ brew calculator (ff:pm_recipes)
 (existing 136,
  never modified)
```

Curricula (CIG_ONBOARDING_ENGINE) live in their own file and reference METHODOLOGY page ids; a
lesson MAY reference a coffee slug for a practical checkpoint ("dial in today's espresso") — that
is the only coupling, and it's a string reference validated at build, never an import.

---

## 3. THE ADAPTER SEAMS — commerce-agnostic, by construction

**The constraint (Business Case R5.4 + R6.5, verbatim intent):** core is commerce-system-agnostic;
Toast (café POS) and Unleashed (wholesale ERP) are each optional adapters, never dependencies.

**The Fable-level realization:** because CIG is a static PWA on GitHub Pages, adapters are
**build-time ingest scripts, not runtime integrations.** This is not a limitation — it's the
design. A runtime integration would make the core depend on an API being up; a build-time adapter
makes the canonical JSON the interface, and the core provably cannot depend on what it never reads.

**Adapter contract:**
- An adapter is a standalone script (future `adapters/unleashed_ingest.py`, `adapters/toast_menu.py`)
  whose ONLY job is: fetch/read an external export → map to canonical records → merge into
  `data_offerings.json` → run `check_catalog.py`.
- **Merge rule — field ownership:** the adapter owns *commerce* fields it can know (slug↔SKU map,
  name, origin, availability → `locations[].lineup`, `links.shop`). It must NEVER overwrite
  *human-owned* fields: `dialin`, `dialinNote`, `producer.story`, `lotNote`, tasting `notes`.
  Those are PM's knowledge, not Unleashed's. An adapter that touches them is a bug.
- `build.py` never imports an adapter. Grep-testable: `grep -c "import adapters" build.py` == 0,
  forever.
- The Unleashed payoff, stated once (R6.4): partner orders a lot in Unleashed → next ingest+build,
  that lot's dial-in page exists automatically. Same slugs, same QRs, zero manual upkeep. Say this
  only if asked "how does it stay current."
- Toast is the same pattern pointed at the menu-decoder (`pm_menu`): Toast menu export → canonical
  drink/coffee records. Ordering (write-side Toast API) is OUT of core scope entirely — if PM ever
  wants it, it's a separate hosted app that *reads* this same catalog (R5.3: never lead with it).

---

## 4. INVARIANTS (enforced by `check_catalog.py` — run before EVERY catalog ship)

- **I1** `schema == "cig-catalog/1"`.
- **I2** Unique ids: coffee slugs, producer/tier/location/recipe ids.
- **I3** Every reference resolves: coffee→producer, coffee→tier, lineup slugs→coffees;
  channels ⊆ {wholesale, retail, cafe}; lineup roles ⊆ {espresso, filter, retail}.
- **I4** `dialin` blocks are objects under known keys only.
- **I5** `producer.originPage` exists in METHODOLOGY.
- **Honesty surface:** TODO markers are counted and reported every run (18 as of v101) — the
  standing "clearly-labeled placeholder" rule made mechanical. Never ships silently.

---

## 5. EVOLUTION RULES

1. **Adding a field:** optional fields are free — views render only what's present. Add, document
   here, extend check_catalog if it's a reference.
2. **Adding an entity collection:** add the key, add I2/I3 coverage, add to `_resolve_catalog` only
   if coffees reference it. Bump nothing — additive is compatible.
3. **Breaking change** (rename/re-shape): bump to `cig-catalog/2`, keep a legacy fallback in the
   resolver for one version (the `OFFERINGS` fallback in v101 is the worked example), migrate, drop.
4. **When to split files:** when any single collection exceeds ~50 records or two people/sessions
   edit different collections in the same week. Until then one file wins — the schema tag makes the
   later split a resolver-only change.
5. **Slugs are forever.** A printed QR is a contract. Retire a coffee by removing it from lineups,
   not by deleting its record, until every physical bag is gone; the not-found page is the last resort.

## 6. WHAT WAS PROVEN IN v101 (the receipt)
- Old flat file → this schema, zero information lost (v100 file kept as `data_offerings.v100.bak.json`).
- `build.py` resolver added; `CATALOG` meta shipped to runtime; view reads resolved objects.
- `gen_qr.py` reads `coffees` (legacy fallback kept); QR URLs unchanged — printed codes stay valid.
- jsdom suite `qa_v101.js`: 24/24 — dark-by-default parity, dial-in parity, trace composition
  (lotNote + story + producer line), flag-off routing, CVA untouched, bad-slug, version.

## 7. WHAT NOT TO DO
- Don't put farm attributes back on coffees. Don't share dial-in blocks between coffees.
- Don't let an adapter write human-owned fields. Don't make build.py import anything external.
- Don't add join logic to client JS — if a view needs a relationship, resolve it in `_resolve_catalog`.
- Don't edit catalog data without running `check_catalog.py`. It takes one second.
