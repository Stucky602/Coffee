# COFFEE — AN INDUSTRY GUIDE · HANDOFF 1

First-pass build. Roasting-scoped. Kevin directs architecture, Claude writes code (same pattern as CQV/LTB).

**Current version: v11** (v1–v9 as before; v10 = Phase E "Green Buying & QC" 6 pages + 3 origins → 45 pages
across 8 groups; v11 = information-architecture redesign — see below). Live at https://stucky602.github.io/Coffee/

**v11 IA redesign (navigation & organization):** With 45 knowledge pages, the old flat "Learn" wall of cards
didn't scale. Changes:
- **Nav renamed** "Roasting Knowledge" → "Learn" (the section now spans green buying → brewing, not just roasting).
- **Learn is now a searchable hub.** Default view = 8 collapsible group tiles (accent bar + one-line
  description + page count), click to expand cards in place. A search box filters across ALL 45 pages by
  title, sub, section text, and keypoints (flat results with group tags). Functions: `learnList`, `drawLearn`,
  `toggleHub`, `matchMeth`. State: `learnQuery`, `learnOpen`.
- **Groups reordered to follow the bean's journey:** Green Buying → Reading the Roast → Roast Science → In
  Practice → Origin → Cupping → Operations → Brewing. New `METH_GROUP_META` dict (in build.py, injected into
  JS) holds each group's description + accent for the hub tiles.
- **Meth detail pages now show sibling topics** ("More in {group}") at the bottom for lateral navigation
  within a section. Back button relabeled "← All topics".
- **Home page** "Learn the Craft" section now samples one topic from six different groups (`homeLearnSample`)
  instead of the first 6 by insertion order, and shows group tags.
- **methCard** gained a `showGroup` param — group tag shows only in search results / home / siblings (where
  context is lost), not inside grouped hub views. New CSS: `.mgrid` utility, `.hubgroup/.hubhead/.hubbar/etc`,
  `.siblings`.

## What this app is
A practitioner-in-the-trenches roasting reference for people **in the coffee industry**, starting with the
**roastery floor**. Same structural breadth ambition as the CQV Field Reference App, pointed at coffee.
Later expansions (in rough order): baristas → green buyer/QC → maybe hobbyist far down the line. Full arc is
**seed-to-cup**, but v1 is **roasting only**.

Working title: **Coffee — An Industry Guide** (brand mark "CIG").

## Decisions locked in planning (do not relitigate without Kevin)
- **Hero object = Roast Profiles.** 10 in the first pass. Everything else (origins, varietals, processing,
  brewing, cupping) is future expansion.
- **Flavor viz = radar**, six FIXED axes so profiles are comparable: Acidity, Aroma, Sweetness, Body,
  Bitterness, Roast. Scores are 1–5 and must stay correct *relative to each other* (light = high
  acidity/aroma, dark = high body/bitterness/roast). This is the thing most likely to break if edited
  carelessly — a dark roast scoring higher acidity than a light roast makes the whole chart look wrong.
- **Temps shown in both °F and °C.** Presented as typical bean-temp RANGES, not single true numbers
  (they're machine-specific). Lean on relationships/ratios (DTR, phase proportions) which transfer.
- **Citations = lightweight / optional**, not the CQV five-tier formal system. Coffee has no hard regs.
  Semi-authoritative bodies worth referencing later: SCA, CQI/Q-grader, ICO, roaster literature
  (Rao, Hoffmann, Rogers). Not built yet.
- **Tech = single self-contained HTML PWA**, GitHub Pages, ship by renaming to `index.html`. Same as CQV.
  Split into multiple files LATER, not now.
- **Model plan:** foundational pass built on **Opus**. Future maintenance passes (add profile #11, tweak a
  defect note, fix an axis) → **Sonnet** is fine, CQV-style surgical edits.

## The 16 profiles (by group, spectrum order)
- **Light:** Cinnamon, New England, Nordic, Blonde, City
- **Medium:** American, City+
- **Medium-Dark:** Full City, Full City+
- **Dark:** Vienna, Continental, French, Italian, Spanish
- **Purpose-Built:** Espresso, Omni

Spectrum runs Cinnamon (lightest, Agtron 95-85) → Spanish (darkest, carbonized edge, Agtron 25-20).
Blonde (v6) is honestly framed as the Starbucks-popularized marketing term that in practice lands near City.
The named Western roast spectrum is now complete — remaining industry terms (High Roast, Breakfast, Regular,
"espresso roast") are all captured as `aka` aliases, not separate profiles. All flavor scores set relative
to the original 10 anchors so radars stay comparable. Web-verified against current sources.

**Spectrum navigation (added v6):** `spectrumNav(id)` renders an "Along the Spectrum" block at the bottom of
each detail page linking to the lighter and darker neighbors. It walks the ordered PROFILES object EXCLUDING
group==='purpose' (Espresso/Omni aren't on the light-dark line, so they get no spectrum nav). End profiles
(Cinnamon lightest, Spanish darkest) show a dashed empty cell on the missing side. Because PROFILES is stored
in spectrum order, neighbors are just adjacent keys — if you reorder/insert profiles, keep the object in
spectrum order or this breaks.

**Synonym / "aka" system (added v5):** each profile can carry an `aka: [...]` array of alternate/regional
names (e.g. New England = Light City / Half City / Breakfast). Rendered on the detail page as muted pills
under the sub-title ("also called …"), and folded into `matchProf` search so typing "half city" or
"breakfast" or "new orleans" finds the right profile. Cards stay clean (no aka) — detail + search only.

## The 15 methodology / knowledge pages (by group)
- **Reading the Roast:** Reading the Roast Curve, Rate of Rise (RoR), Phases of a Roast, First & Second
  Crack, Development Time Ratio
- **Roast Science:** Roasting Chemistry, Heat Transfer, Roaster Types
- **In Practice:** Roast Defects, Sample Roasting & Profiling
- **Roasting by Origin (v7):** Roasting by Origin (overview), Ethiopia, Colombia, Brazil, Sumatra/Indonesia.
- **Cupping & Quality (v8, Phase B):** What Cupping Is, Cupping Mechanics, The Coffee Value Assessment,
  CVA Affective Scoring, The Legacy 2004 Protocol, The Flavor Wheel, The Roaster's QC Loop, Q Graders & the
  Evolved Q. Built CVA-first per the audit (the SCA replaced the 2004 protocol Nov 2024). All numbers
  source-verified against SCA standards docs + practitioner sources. KEY VERIFIED FACT for the future
  digital cupping tool: the CVA affective score formula is **Cup Score = 0.65625 × (sum of 8 section scores,
  each 1–9) + 52.75 − 2×(non-uniform cups) − 4×(defective cups)**. Confirmed against a published worked
  example (sections summing to 48 → 84.25). Sections: fragrance, aroma, flavor, aftertaste, acidity,
  sweetness, mouthfeel, overall.
- **Roastery Operations (v9, Phase C):** Warm-Up & Seasoning, Between-Batch Protocol, Batch Size & Capacity,
  Fire Safety, Roasting Decaf, Degassing/Storage/Packaging, Roast Logging & Software. Verified specifics:
  warm-up 30–90 min to thermal equilibrium; BBP charges on rising temp, ~60–90s to charge temp; batch
  50–85% capacity; decaf roasts faster/darker and lies about color, lower charge temp, rest 24–48h;
  degassing peaks 12–24h, one-way valves, rough rest windows dark 1–3d / medium 3–5d / espresso 7–12d.
- **Brewing & Barista (v9, Phase D):** Extraction Theory, Dialing In Espresso, Grind & Burrs, Brew Methods,
  Milk & Steaming, Water Chemistry. Verified: espresso 1:2 (18g→36g), 25–30s, 9 bar, 90–96°C; extraction
  yield 18–22%, espresso TDS 8–12%, filter TDS 1.15–1.35% at 1:16–1:17; sour=under (grind finer),
  bitter=over (coarser); milk sweet spot 60–65°C.
- **Green Buying & QC (v10, Phase E):** Buying Green Coffee, Green Grading & Defects, Density/Moisture/Water
  Activity, Processing Methods, Arabica vs Robusta, Country Grading Systems. Verified: SCA green grade 350g
  sample under 4000K/1200 Lux, specialty = 0 Cat-1 + ≤5 full Cat-2, equivalences (1 full black = 3 partial,
  5 broken = 1 full Cat-2), scale <350g by ×3.5 per 100g; moisture 10–12% (>12.5% mold risk, <9% flat),
  water activity <0.70 shelf-stable, screen size 64ths (18 ≈ 7.1mm); arabica ~1.2–1.5% caffeine / robusta
  ~2.2–2.7%; processing washed/natural/honey/anaerobic/wet-hulled; country grades (Ethiopia G1–G5, Kenya
  AA=size, Colombia Supremo/Excelso); EP ≤8 defects/300g; certifications ≠ specialty.
- **Origin expansion (v10, Phase E):** Kenya (SL28/SL34, blackcurrant, double-washed, dense/exothermic —
  roast light-medium), Guatemala (Antigua balanced/Huehuetenango bright, SHB, medium), Costa Rica (Tarrazú,
  honey-process home, SHB, clean/sweet, medium). Now 8 origin pages total.

The app now covers the complete seed-to-cup arc across 8 knowledge groups. No content phase remains; the
next work is the Tier 1 tools (Part 3 of the audit/agenda) — the reference-to-instrument jump.

**Citations/refs feature (v8, Phase A#3):** METHODOLOGY entries now support an optional `refs:[{label,link}]`
array, rendered as a "Sources" block at the bottom of the meth detail page via `refsBlock()`. All 23 meth
pages are seeded with verified sources. To add refs to a page, add the array to its data entry. (Profiles
schema does NOT yet have refs — that's an easy future add if wanted.)

**Curve °F/°C toggle (v8, Phase A#4):** `roastCurve(c,accent,w,h,units)` takes a units arg ('C'|'F') and
converts axis labels. Profile detail has a °C/°F toggle (`setCurveUnits(id,u)`) that re-renders the curve svg.

**Curve-compare overlay (v8, Phase A#5):** Compare view now has a Flavor Radar / Roast Curve mode toggle
(`setCmpMode`). Curve mode (`drawCmpCurve`) overlays the selected profiles' BT curves on a shared time+temp
axis with first-crack and drop dots — visually shows short-light vs long-dark. Reuses `buildCurve()`.

---

## ARCHITECTURE (how it's built)

Unlike the CQV app (hand-edited monolithic HTML), this uses a **Python build step** for clean/verifiable
data, mirroring the LTB `src/`-build discipline. Three source files → one self-contained `index.html`.

**Source files:**
- `data_profiles.json` — `{PROFILES:{id:{...}}}`. The 10 profile cards. Full schema below.
- `data_methodology.json` — `{GLOSSARY:[...], METHODOLOGY:{id:{...}}}`. The 10 knowledge pages PLUS the
  22-term newcomer glossary (added v4). GLOSSARY is a flat array of `{term, def}` in plain English — add a
  term by appending an object. build.py reads both keys out of this one file.
- `build.py` — reads both JSONs, injects as one `<script type="application/json">` blob, wraps in the
  HTML/CSS/JS shell (radar renderer + roast-curve renderer + router). Run `python3 build.py` → writes
  `index.html` AND the PWA assets: `sw.js`, `manifest.webmanifest`, `icon.svg`.

**Start Here tab (added v4):** `startHere()` view, first content tab after Overview. Built for total
newcomers (Kevin's own request — he didn't know what "drop" meant). Three parts: (1) plain-language intro to
what roasting is, (2) a 7-stop green-to-cup journey (green → charge → drying → Maillard → first crack →
development → drop) as a vertical stepper, (3) the single light-vs-dark trade-off framed as a two-sided
panel, (4) the full glossary with a live filter box. Journey steps are hardcoded in `startHere()`; glossary
comes from the GLOSSARY data array. All roasting facts were web-search-verified against current sources
(first crack ~196°C, second crack ~224°C, green 10-12% moisture, rest 12-24h, weight loss 15-20%).

**PWA (added v2):** `index.html` links `manifest.webmanifest` and registers `sw.js`. Service worker caches
the shell (cache-first, network fallback) so it installs to a phone home screen and works offline on the
roastery floor. `icon.svg` is a gradient coffee-bean mark (scales to any size). All four are regenerated by
build.py — never hand-edit sw.js/manifest, edit build.py.

**Roast-curve renderer (added v2):** `roastCurve(curve,accent,w,h)` in build.py's JS shell. Derives an
idealized BT + RoR curve entirely from each profile's EXISTING curve data (no new authoring) — parses the
total-time and DTR ranges to place first crack and drop, uses standard charge/turning-point/drying physics
for the rest. Phase-shaded (drying/Maillard/development), landmarks marked (TP, 1C, Drop), RoR overlaid as a
dashed secondary line. `buildCurve()` does the math, `roastCurve()` draws. The curve auto-shapes per profile:
Nordic is short with 1C≈Drop, Italian is long with a big development phase. Label collision handling: 1C label
drops below the line when development is short (`fcClose` threshold 0.13).

**Profile schema** (`data_profiles.json`):
```
id: {
  name, sub, level (Light|Medium|Medium-Dark|Dark|Purpose),
  group (light|medium|mediumdark|dark|purpose),
  agtron (string range), accent (hex — MUST be readable on #160e08 dark bg; darkest roasts use a
    warm-brown proxy ~#8a4a28..#b06a3e, NOT near-black, or the radar line vanishes),
  aka (optional array of alternate/regional names, e.g. ["Half City","Breakfast"] — shown as pills on
    detail page + searchable; omit or [] if none),
  oneLine, useFor,
  curve: {chargeC,chargeF, tpC,tpF, dryEndC,dryEndF, fcC,fcF, dropC,dropF, totalTime, dtr},
  flavor: {acidity,aroma,sweetness,body,bitterness,roast}  // each 1..5
  phases: [{h, body}, ...]      // typically 4: drying, Maillard, first crack, development
  defects: [{d, cause, avoid}, ...]
  machine: "..."                 // roaster-type considerations
}
```

**Methodology schema** (`data_methodology.json`):
```
id: {
  name, sub, group (read|science|practice), accent,
  sections: [{h, body}, ...],
  keypoints: ["...", ...]        // optional; renders as arrow list at bottom
}
```

**The radar renderer** lives in `build.py`'s JS shell: `radar(vals,size,accent,opts)`.
- Pure inline SVG, no library (keeps the app self-contained).
- `opts.small` = card thumbnail (no axis labels, no vertex dots).
- Compare view has its own multi-shape overlay drawer (`drawCmp()`), up to 4 profiles, fixed color list.
- Axes order is defined ONCE in `FLAVOR_AXES` (build.py). Change there, everything follows.

**Views / router:** `go(view,arg)` — `home`, `start`, `profiles`, `profile:<id>`, `compare`, `learn`,
`meth:<id>`.
Nav highlights map sub-views back to their top tab.

## VERIFICATION (do this every change, CQV discipline)
- jsdom smoke test: load index.html with `runScripts:'dangerously'`, call `go()` into each view, assert the
  SVG count / card count / detail h1. (scrollTo "not implemented" warnings from jsdom are harmless.)
- For radar sanity, export a light and a dark profile's SVG and eyeball: light must lean top-right
  (acidity/aroma), dark must lean left (bitterness/roast). If they're not visibly inverted, the flavor
  numbers are wrong.
- Chrome/puppeteer screenshotting was NOT available in this environment (chrome download incomplete);
  jsdom + cairosvg-on-SVG was the working path.

## VISUAL IDENTITY
Dark "cooling-roast" instrument-panel look, NOT the cream/terracotta AI default. Deep roasted-brown bg
(#160e08), warm heat-gradient accents (gold→ember, `--heat1..5`), mono utility face for all
numbers/temps/DTR so data reads like gauges. Each profile carries its own roast-color accent. The heatbar
under the hero is the signature element (the roast spectrum as a strip).

---

## BACKLOG / NEXT (not built yet)
Roasting-scope polish:
- Optional lightweight citation/refs strip per profile + per methodology page (SCA/CQI/Rao/Hoffmann).
- ~~Roast-curve line graph per profile~~ — DONE in v2.
- ~~PWA manifest + service worker for true offline~~ — DONE in v2.
- ~~Search/filter across profiles~~ — DONE in v3. Search box + level-filter chips + sort-by-flavor-axis on
  the Profiles view. Search matches name/sub/level/oneLine/useFor/agtron PLUS a synonym layer (`SYN` map in
  `matchProf`) so flavor words map to axes: bright/fruity/citrus→acidity, bold/rich→body, smoky/roasty→roast,
  etc. Sort options: roast spectrum (grouped) or by any single flavor axis descending. State held in
  `profQuery`/`profLevel`/`profSort` closures. To add synonyms, extend the SYN map.
- ~~More profiles (Cinnamon/blonde extreme-light, Continental, regional/traditional variants)~~ — DONE in
  v5 (now 15: added Cinnamon, New England, American, Continental, Spanish). Spectrum is essentially complete
  for named Western roast levels. Possible future niche adds: Blonde (Starbucks marketing term ≈ City),
  regional espresso variants — but these mostly duplicate existing levels, so aka is the better home.
- Curve enhancement idea: let the curve toggle °F/°C on the axis, and/or a "compare two curves" overlay
  (same idea as the radar compare but for the BT lines — visually shows short-light vs long-dark).

Future expansion axes (post-roasting, the seed-to-cup arc):
- **Green:** origins, varietals, processing (washed/natural/honey), grading, density/moisture.
- **Cupping/QC:** SCA cupping protocol, flavor wheel, defect cupping, Q-grader framework (green-buyer user).
- **Brewing/extraction:** espresso + filter methods, extraction theory (barista user).

## STANDING STYLE RULES (Kevin)
Direct, casual, humor-forward. No em-dashes in copy. No "not only X but also Y". No AI-speak filler.
Peer-level: confirm and proceed, don't narrate reasoning back.

---

# PROUD MARY COFFEE (PMC) — STRATEGIC CONTEXT & FUTURE DIRECTION
*(Logged for later. This app is being built with Proud Mary Coffee as the target user/recipient. Not generic.)*

## Who PMC is (verified)
A vertically-integrated, multi-entity, cross-continental specialty coffee group founded by Nolan Hirte
(2009, Melbourne). Sub-brands each serve a DIFFERENT market:
- **Proud Mary Coffee Roasters** — wholesale / B2B engine (roasting in Melbourne + Portland).
- **Proud Mary Cafe** — flagship all-day brunch + coffee experience (Melbourne, Portland, Austin TX).
- **Aunty Peg's** — dedicated brew bar / tasting room (nerdy, education-forward retail face).
- **Collingwood Coffee College** — an actual coffee SCHOOL. They already sell education.
Identity: direct trade, Cup of Excellence, B Corp certified, competition-winning geishas, coffee served in
flights/wine glasses. Founding ethos: "innovate, educate, collaborate." Known for unique/rare origins.

## The core reframe
This is not a reference app — it's the digital layer of a company that ALREADY sells coffee education
(Collingwood Coffee College). Frame everything as courseware / onboarding / branded credential, plus a
wholesale-quality tool. One content base serves all four entities and each reinforces the others — the app
is "shaped like their company."

## The four seams (where the app earns its keep)
1. **Wholesale (highest $ / clearest ROI — the beachhead):** Their coffee only tastes as good as the worst
   barista at the worst account. QR on each bag → per-coffee dial-in card (recipe + sour/bitter fix +
   provenance). Makes PMC's standard travel with the bag; deflects the weekly wholesale support call;
   optional wholesale-partner certification track. **START HERE — cheapest to prove, internal-facing.**
2. **Cafe floor:** Table-side QR → guest "tasting companion" (origin story + flavor wheel + processing
   explainer + the compare-radar for flights). Turns a passive $12 geisha into an interactive experience =
   PMC's whole brand. Staff-side: single source of truth so Melbourne/Portland/Austin tell the same story.
3. **Collingwood Coffee College:** App = textbook + homework. Training Mode (quiz from glossary/content) =
   assessment layer → branded digital certificate. Cross-country staff onboarding (roastery-ops pages are
   exactly what a new roaster needs, expensive to teach 1:1).
4. **Green / direct-trade story:** Phase E green content = technical spine of their direct-trade narrative.
   Add per-coffee traceability (producer, farm, altitude, process, relationship story) = tangible B Corp /
   direct-trade proof AND a wholesale closing tool.

## PMC-specific roadmap reprioritization (vs generic agenda)
1. Per-coffee dial-in cards + QR routing (content largely exists; it's a data + routing layer). **MOCKUP DONE**
   — see pm_dialin_card.png/.html. Barista-facing: scan confirm bar, PMC-branded hero, big recipe numbers,
   sour/bitter troubleshooting rows, provenance + B Corp badge, deeper links.
2. Co-brand / white-label skin (PMC red identity, not generic dark theme).
3. Table-side guest tasting-companion mode (flavor wheel + radar).
4. Training Mode + certificate (College courseware + wholesale training).
5. Roast tools (timer + log) for the actual Melbourne/Portland roasting teams.

## Honest caveats
- Wholesale QR depends on their bag/label workflow accommodating it.
- Cafe tasting-companion assumes guests scan (mixed industry evidence — pilot at one location, likely Austin).
- Certification angle needs Collingwood Coffee College to want a digital arm (a conversation, not an assumption).
- Safest highest-value beachhead = wholesale dial-in cards.

## Next mockups to build (future session)
- Filter/pour-over version of the dial-in card (they lead with filter flights).
- Guest-facing tasting-companion view (same coffee, story + flavor wheel instead of recipe).
- Those two + the espresso dial-in card = all three PMC markets from a single scan.

---

# v12 — UX/IA REFINEMENT PASS (Sessions 1 & 2 of Kevin's refinement list)

## Fixes (Session 1)
- **Radar label clipping FIXED** (Profiles + Compare). Root cause: right-anchored "Bitterness" label extended
  past the square viewBox edge. Fix: `radar()` now uses horizontal margin `M=48`, viewBox width `size+M*2`,
  cx shifted by M. Same fix applied to the manual compare radar (`drawCmp`). Radar also now `margin:0 auto`
  centered, and on mobile (<640px) it stacks full-width and centered under the profile text.
- **iOS notch / safe-area FIXED.** `header.top` gets `padding-top:env(safe-area-inset-top)`, `.top .wrap`
  gets left/right safe-area padding, and `.mobnav` sticky `top` offset by the inset. Content no longer hides
  under the iPhone status bar. (viewport already had `viewport-fit=cover`.)
- **Blue link text FIXED.** Was the browser default `:visited` color overriding `color:inherit`. Now
  `a,a:visited{color:inherit}` globally and `.refs a:visited` pinned to `--ink2`.
- **Overview page REBUILT.** Killed the vague "Built for practitioners, not the shelf" hero. New: a real
  `.lede` intro paragraph + a clean **section directory** (`.secdir`/`.secard`) — one card per main area
  (Profiles, Compare, Origins, Learn, Start Here) with an inline line-icon (`svgIcon()`), a one-line blurb,
  and a quick-link. Replaced the old "show 6 profiles + 6 meth cards" clutter.

## Structural (Session 2)
- **"Roasting by Origin" is now its own top-level TAB** (was a group inside Learn). New nav item "Origins"
  (desktop + mobile). New routes `origins` (list) and `origin` (detail) in the router; `origin` meth pages
  route to the Origins tab. Removed `origin` from `METH_GROUPS` (so the Learn hub + Learn search exclude it).
  Origin data still lives in METHODOLOGY with `group:"origin"`.
- **Origins tab built deep:**
  - `originList()` — a **world map** (`originMap()`, equirectangular `projXY()`) showing the Bean Belt band
    (Tropics of Cancer/Capricorn) with a tappable dot per origin, then origin cards grouped by continent
    (Africa / Central America / South America / Asia).
  - `originDetail()` — rich layout: continent eyebrow, name, blurb, flavor tags, a **roast-level ring**
    (`.odroast-ring`, color via `roastColor()`), a **facts strip** (Regions/Altitude/Varieties/Process/
    Harvest), the deep sections, key points, refs, and "More origins" siblings.
  - Origin intro page renders via `methLike()` and is linked from the bottom of the Origins list.
- **Origin data enriched** with structured fields: `country, continent, lat, lng, regions, altitude,
  varieties, process, harvest, roastLevel, flavorTags[], blurb`. Applied to all existing origins.
- **4 NEW origins added** (all in Proud Mary's actual lineup — verified from PMC's site/academy):
  - **Panama** (their signature — full Geisha story: Ethiopia→Panama, Best of Panama 2004, Boquete/Volcán/
    Renacimiento, roast as light as you dare). **El Salvador** (heirloom Bourbon preserved by history,
    birthplace of Pacamara). **Honduras** (rising heavyweight, 6 regions). **Nicaragua** (between Honduras
    & Costa Rica). Now **11 origin countries** total (was 7).

## Filesize note
index.html = ~233 KB (lean; SVG map + icons are vector, near-zero bytes). No raster bloat. Kevin's rule after
the LTB base64 incident: keep rasters external/SVG, never base64-embed photos.

## STILL TODO — Session 3 (Kevin's list, deferred)
1. **Profiles deep-dive** (Kevin's favorite part — keep the top half exactly as-is): add deeper
   **defects/pitfalls per roast level**, **machine considerations** per roast, and surface **which single
   origins suit which roast level** (cross-link Profiles <-> Origins; the roastLevel field on each origin now
   makes this data-driven).
2. **Learn content bulk-up** — far greater depth across all of it; real teaching not filler. Green defects
   especially need **actual defect photos/illustrations** (custom labelled SVGs per Kevin's approval, +
   public-domain where findable, watching filesize). Most Learn pages can be meaningfully deepened.
3. Consider diagrams/graphs on more Learn pages where they aid understanding.

---

# v13 — SESSION 3: CONTENT DEEPENING + DEFECT ILLUSTRATIONS

## Track 1 — Profiles deep-dive (Kevin's favorite section; top half untouched)
- **Defects deepened** from 2 → 3–4 per profile, level-appropriate (tipping/uneven on light roasts; oily-too-soon/
  muddled on medium-dark; uncontrolled second crack/smoke taint on dark; harsh-crema on espresso). Data in
  data_profiles.json `defects[]`.
- **Machine considerations roughly doubled** per profile — specific per roast band (responsive convection +
  small batches for light; drum thermal mass + airflow/smoke management for dark; repeatability + BBP for
  espresso). Data in `machine` string.
- **NEW: "Origins That Shine Here" section** on every profile detail — DATA-DRIVEN cross-link to the Origins
  tab. `roastBand()` maps level strings to 0–4; `originPairing(p)` matches origins whose `roastLevel` band is
  within ±1 of the profile (purpose profiles get espresso-appropriate origins). Verified sane: Nordic→
  Ethiopia/Panama/Colombia/Kenya; French→Brazil/Sumatra; Espresso→the sweet/chocolatey bases. Chips link to
  `origin` route. This is the profile↔origin merge Kevin asked for, and it stays automatic as origins are added.

## Track 2 — Learn bulk-up + defect illustrations
- **Defect bean illustrations** — `beanSVG(kind)` generates inline SVG coffee beans (ellipse + center crease +
  defect-specific signature) for: healthy, fullblack, partialblack, sour, broken, insect, quaker, shell,
  immature. Zero-byte (vector), offline, no licensing. `beanGallery(items)` renders a labelled figure grid.
  Pages can carry an optional `visuals:{title,note,beans:[{kind,label,cap}]}` field; methDetail renders it
  after the sections. **green_grading** now shows an 8-bean defect gallery.
- **Content deepened** on key pages (each got a substantial new section):
  - green_grading: + "Sorting in practice" (bench workflow) + the 8-bean visual gallery.
  - cracks: + "Reading the cracks by ear" (first = popcorn/196°C, second = Rice-Krispies/224°C, the gap).
  - chemistry: + "Where the flavors come from" (Maillard/caramelization/chlorogenic-acid breakdown).
  - defects: + "From the cup back to the curve" (cup-flaw → roast-cause diagnostic).

## Filesize
index.html = ~252 KB (was 233). +19 KB for all Session-3 content + SVG bean generator. Still lean; beans are
vector so they cost nothing. No base64 raster.

## To extend the defect illustrations later
- `beanSVG()` is the single place to add/adjust bean visuals. Add a `visuals` block to any page (e.g. the roast
  'defects' page could get roast-defect beans — scorched/tipped/baked color signatures) the same way
  green_grading does. Kevin can also drop real PMC photos in later if he hosts them.

## REMAINING / FUTURE (not blocking)
- Could add roast-defect bean visuals to the roast 'defects' page (scorched/tipped/oily surface signatures).
- Learn pages still have room to deepen further (ops, brew, cupping) if desired — the schema supports it.
- PMC track (logged earlier): filter dial-in card mockup, guest tasting-companion mockup, then tools.

---

# v14 — LEARN TAB DEEP-DIVE + CONCEPT DIAGRAM ENGINE

## New: concept-diagram engine (inline SVG, zero-byte, offline)
`diagram(kind)` + `diaWrap()` render teaching diagrams into `.diagram` figures. Ten diagrams built:
- `roastcurve` — annotated BT S-curve + declining RoR, phase bands, TP/dry-end/1C/drop markers, legend.
- `phasebar` — Drying/Maillard/Development timeline with temps + what happens.
- `dtr` — development-share bars for light/balanced/dark styles.
- `cracks` — 1st vs 2nd crack on a 150–240°C axis with drop zones.
- `heat` — drum cross-section showing conduction/convection/radiation.
- `extraction` — under/ideal/over yield band (18–22% ideal).
- `espresso` — 18g dose → 36g yield 1:2 ratio visual.
- `grind` — particle-size clusters across espresso/pour-over/drip/French press.
- `flavorwheel` — radial 9-category SCA wheel.
- `cva` — 8 sections → formula → 84.25 score build.

Pages opt in via a `diagram:"kind"` field; methDetail renders it after the FIRST section (anchors the
concept early). Attached to: curve, ror (both roastcurve), phases, dtr, cracks, heat, brew_extraction,
brew_espresso, brew_grind, flavor_wheel, cva_scoring. To add more: write a `diaX()` fn, add to `diagram()`
switch, set the page's `diagram` field. Palette pulled from `DIA{}` constant to match the app aesthetic.

## Content deepened (teaching-first)
The thin "Reading the Roast" pages roughly doubled and gained diagrams:
- curve 150→356 words (+ "shape > numbers", "using it live"), ror 159→361 (+ "crash and flick",
  "RoR as prediction"), phases 140→325 (+ "what goes wrong per phase", "proportions not times"),
  dtr 141→322 (+ "why higher isn't better", "measuring consistently").
- Also deepened: heat (+airflow as third control), roasters (+matching machine to style),
  flavor_wheel (+how to use it at the table), brew_water (+building/fixing your water).
- (Session-3 deepenings still in place: green_grading sorting + 8 defect beans, cracks-by-ear,
  chemistry flavor formation, defects cup-to-cause.)

## Filesize
index.html = ~278 KB (was 252). +26 KB for the diagram engine + deepened Learn content. All diagrams are
inline SVG (vector), so no raster bloat. Still well within a healthy single-file PWA.

## Learn tab status
Every "Reading the Roast" page now teaches with a diagram. Green has defect illustrations. Cupping has the
flavor wheel + CVA score diagram. Brewing has extraction/espresso/grind diagrams. Science has the heat
diagram. The tab is now genuinely instructional rather than reference-only.

## Still-open future (not blocking)
- Could add diagrams to more pages (processing methods cross-section, milk-steaming phases, brew-methods
  families, water hardness/alkalinity grid).
- Roast-defect bean visuals on the roast 'defects' page (scorched/tipped/oily) via the same beanSVG engine.
- PMC track: filter dial-in card + guest tasting-companion mockups, then tools.

---

# v15 — BLUE-HEADER FIX, PER-ORIGIN MAPS, LEARN WAVE 2

## Bug fix: blue headers everywhere
Root cause: `.secard-title`, `.beanfig`, `.opair-name`, `.odtxt h1`, origin cards all used `color:var(--ink1)`
but **--ink1 was never defined** — so on iOS `<button>` elements it fell back to system-blue. Fixed by
(a) defining `--ink1:#f0e6d8` (alias of --ink) and (b) adding `color:inherit` to the global `button{}` reset.
Verified no other undefined CSS vars remain.

## Maps reworked (Kevin: world map on detail was un-zoomable/pointless)
- **Removed** the un-zoomable world map (`originMap`/`projXY` deleted).
- **Origins list** now shows `beltStrip()` — a clean, compact "Bean Belt" context band (tropics + equator +
  scattered bean dots), not a fake interactive map.
- **Each origin detail page** now has `originRegionMap(m)` — a stylized country silhouette with that origin's
  actual growing regions plotted as labeled dots (e.g. Ethiopia shows Yirgacheffe/Guji/Sidamo/Harrar). Data
  in each origin's `regionMap:{note,shape(SVG path),regions:[[name,x,y]]}`. Far more useful than a world map:
  shows where in the country the coffee grows. All 11 origins have one.

## Learn tab — Wave 2 (going harder, then more)
Diagram engine extended from 10 → 15 diagrams; **16 Learn pages now carry a teaching diagram** (was 11):
- New diagrams: `processing` (washed/honey/natural fruit-retention), `milk` (stretch/texture temp track),
  `brewfamilies` (percolation/immersion/pressure), `water` (hardness×alkalinity target box), `roasters`
  (drum/fluid-bed/hybrid).
- **Roast-defect bean gallery** added to the roast `defects` page (well-developed/quaker/scorched/charred) —
  reuses the beanSVG engine; now 2 bean galleries total (green defects + roast defects).
- Content deepened further: green_processing (+processing as a lever), green_measure (+why buyers read all
  four numbers), cupping_mechanics (+why the protocol is rigid), ops_fire (+building a fire plan), ops_decaf
  (+reading decaf without visual cues).

## Filesize
index.html = ~297 KB (was 278). +19 KB for 5 new diagrams, per-origin maps, and deepened content. All vector.

## Learn tab diagram coverage (16 pages)
curve, ror, phases, dtr, cracks, heat, roasters, chemistry(no—text), green_grading(beans), green_processing,
green_measure(no), cupping_mechanics(no), flavor_wheel, cva_scoring, brew_extraction, brew_espresso,
brew_grind, brew_methods, brew_milk, brew_water, defects(beans). Nearly every visual-worthy page now teaches
with an image.

## Still open (future)
- A few pages remain text-only where a diagram wouldn't add much (green_species, green_grades, cupping_intro,
  cva_overview, legacy_protocol, qc_loop, q_grader, ops_* logistics, profiling). Could add if desired.
- PMC track: filter dial-in card + guest tasting-companion mockups, then tools (timer/log, cupping form).

---

# v16 — CONNECTIVE TISSUE + CULTURE CONTENT + FULL DEPTH PASS

## Navigation layer (the big adds)
- **Global search.** Magnifier button in the header opens a full-screen overlay (`openSearch`/`runGlobalSearch`)
  that searches across PROFILES + origins + Learn pages + GLOSSARY at once, grouped by type, with live results.
  Keyboard: "/" opens, Esc closes. This is the cross-app search the app was missing.
- **Inline glossary tooltips.** `buildGloss()` builds a term→def map from GLOSSARY plus an ALIASES layer (bare
  words like maillard, caramelization, mucilage, chlorogenic, endothermic, microlot, direct trade, c-price…).
  `linkTerms()` wraps the first occurrence of any known term per paragraph in a tappable `.termref`; `showTerm()`
  shows a `.termpop` popover. Applied to all section bodies (methDetail, originDetail, methLike). 38/41 Learn
  pages now have inline term links. NOTE: word-boundary regex built via `String.fromCharCode(92)+'b'` to dodge
  Python-raw-string/JS escaping hell (earlier `\\b` attempts double-escaped and silently failed).
- **Guided beginner path.** `PATH` = 10-step ordered spine (waves→green_intro→green_processing→curve→phases→
  cracks→dtr→chemistry→cupping_intro→brew_extraction). Rendered as a numbered clickable list on Start Here
  ("A path through the fundamentals"), and `pathNav()` shows a "step N of 10 · Next: X" nudge at the bottom of
  any page that's on the path.
- **Concept cross-linking.** 41 Learn pages got a curated `related:[ids]` field; `relatedBlock()` renders
  tappable `.relchip` links after keypoints. The content now feels connected instead of siloed.
- **Accessibility.** All diagrams/bean/region SVGs now carry `aria-label` (from caption/kind/country).

## New content group: "Coffee, the Bigger Picture" (culture)
Added as the FIRST Learn group (leads the hub). Four research-grounded pages:
- **waves** — first→fourth wave history (Trish Rothgeb origin of the term; commodity→experience→craft→science/
  home/community). Diagram: `waves` (rising timeline).
- **supply_chain** — cherry→cup chain, the C-price/commodity market, how specialty premiums work, Fair Trade
  vs direct trade. Diagram: `supplychain`.
- **sustainability** — environmental/economic/social; certifications (Fair Trade, Rainforest Alliance, Organic,
  Bird-Friendly) and their limits; certifications vs direct relationships; regenerative/climate frontier.
- **blending** — why blend (consistency, construction, cost), designing by roles, pre-blend vs post-blend
  roasting, single-origin vs blend. Diagram: `blend`.

## Diagram engine: 15 → 18
Added `waves`, `supplychain`, `blend`. Total 19 Learn pages now carry a diagram.

## FULL DEPTH PASS — every Learn page now ≥260 words
Deepened the final 13 thin pages (cupping_intro, ops_batchsize, ops_logging, profiling, q_grader, ops_warmup,
green_intro, legacy_protocol, roasters, qc_loop, cva_scoring, heat, brew_grind) with substantial new teaching
sections. **Result: 0 Learn pages under 260 words; median 356; ~14,700 words of Learn content across 41 pages.**

## Filesize
index.html = ~352 KB (was 297). +55 KB for global search, glossary layer, path, cross-links, 3 diagrams, the
culture group, and the full depth pass. All vector; no raster. Still a single self-contained file.

## Content coverage now (holes closed)
Waves/history ✓, trade & economics ✓, sustainability/certifications ✓, blending ✓ — all previously missing,
now covered. Remaining possible future content: varietals deep-dive (Bourbon/Typica/Geisha/SL28 etc. as its
own page), water recipe specifics, latte-art mechanics, decaf process types (Swiss Water/CO2/EA) as a
dedicated page. None are gaps so much as future depth.

## Still deferred (by Kevin's direction — "just building the base")
PMC track (dial-in cards, tasting companion, courseware) and any interactive tools (brew calculator, roast
timer, cupping form). Base is now very complete: 16 profiles, 41 Learn pages + 11 origins, 43 glossary terms,
19 concept diagrams, 2 bean galleries, 11 origin maps, global search, inline glossary, guided path, cross-links.

---

# v17 — SIX MAJOR CONTENT EXPANSIONS (grow, brew deep-dives, decaf, history, health, business)

Closed the "app starts at the green bean and stops at the roaster's door" gap. Learn now spans farm → cup →
business. 41 → 57 Learn pages; 18 → 29 diagrams; ~14,700 → ~20,600 words. Size ~423 KB.

## New group: "Growing & Origin" (grow) — the farm end
- **plant** — coffee is a fruit seed; cherry anatomy; where/how it grows (altitude, bean belt, ripening);
  the three species (Arabica/Robusta/Liberica). Diagram: `cherry` (cross-section).
- **varietals** — species vs variety; Typica & Bourbon founding lines; mutations/crosses (Caturra, Mundo Novo,
  Catuai, Pacamara, SL28/34); Geisha & the genetics case; rust-resistant hybrids (Timor Hybrid→Catimor/
  Sarchimor/Castillo/F1); "variety sets the ceiling but terroir+processing often matter more." Diagram:
  `vartree` (family tree).
- **harvest** — ripeness as top lever; selective vs strip picking; the labor reality.
- **threats** — leaf rust (la roya), borer beetle (broca), climate change as existential. 

## Brewing expanded from 6 → 12 pages
- **brew_pourover** — what it is, the universal bloom-and-pour method, V60 vs Chemex vs Kalita. Diagram: `pourover`.
- **brew_immersion** — steeping; French press (coarse, 4 min, decant); AeroPress (paper microfilter, forgiving,
  standard vs inverted).
- **brew_cold** — cold brew vs iced coffee (the key distinction), how to make cold brew, nitro & RTD. Diagram: `coldbrew`.
- **brew_pressure** — moka pot (not true espresso) & siphon/vac pot.
- **brew_troubleshoot** — the two dials (extraction vs strength); sour→under, bitter→over, weak→ratio. Diagram: `troubleshoot`.
- **brew_drinks** — espresso milk drinks as ratios (macchiato/cortado/flat white/cappuccino/latte/mocha) + latte
  art. Diagram: `milkdrinks` (ratio cups).

## Decaf processing (green group)
- **decaf_methods** — done to GREEN coffee; solvent (MC & EA/"sugarcane"), water (Swiss Water GCE trick,
  Mountain Water), supercritical CO2; ~97–99.9% removal; buying guidance. Diagram: `decaf`.

## History & Health (culture group)
- **history** — wild in Ethiopia; the Kaldi legend; Ethiopia→Yemen/Mocha→Europe→colonial spread; how the
  bean-belt map got drawn. Diagram: `coffeemap`.
- **health** — caffeine (adenosine, ~95mg/8oz, Arabica<Robusta); roast/brew caffeine myths; the moderate-intake
  research picture (association not advice); downsides & genetic variation. Diagram: `caffeine`.

## New group: "The Business of Coffee" (business)
- **biz_roastery** — low-margin volume-and-relationships business; green as top cost; wholesale vs retail vs
  DTC; consistency is the product.
- **biz_cafe** — a café sells labor & rent not beans; consistency under pressure; menu/waste/hospitality.
- **biz_menu** — single origin vs blend roles; how bags & drinks get priced (green premium + ~15–20% roast loss);
  freshness & seasonality keep the menu in motion.

## Navigation updates
- Guided PATH expanded 10 → 12 steps, now starting at history→plant→varietals (the farm end) through to
  brew_troubleshoot.
- 24 pages got new/updated `related` cross-links weaving the new content into the web (every Learn page now has
  related chips).
- Global search + inline glossary automatically cover all new pages (verified: geisha, cold brew, cappuccino,
  leaf rust, swiss water all return hits).
- 12 new diagrams total (cherry, vartree, pourover, coldbrew, troubleshoot, milkdrinks, decaf, coffeemap,
  caffeine + the 3 culture ones from v16).

## Learn now covers (gaps closed this round)
Farm/agronomy ✓ (plant, varietals, harvest, threats), individual brew methods & cold brew & troubleshooting &
milk drinks ✓, decaf processing ✓, coffee history/origin story ✓, caffeine & health ✓, business/economics of
roastery+café ✓. 

## Possible future (genuinely optional now)
Espresso-machine hardware deep-dive (pump/lever, boilers, PID, pressure profiling); a dedicated "how to taste"
sensory-training page; latte-art technique step-by-step; water-recipe specifics (mineral targets/recipes);
regional coffee-culture traditions (Italian espresso culture, Nordic, Turkish, Japanese kissaten). None are
gaps now — all are depth-on-depth. PMC track + interactive tools still deferred by direction.

---

# v18 — IMAGE FIXES + DEPTH-ON-DEPTH (5 more deep pages, 62 total)

## Image fixes (Kevin flagged: origin maps "blob with dots", graphs "off-center words")
- **Origin region maps COMPLETELY REDESIGNED.** Dropped the crude abstract country-silhouette `shape` blobs and
  the hand-placed colliding region dots. New `originRegionMap()` renders a clean, collision-free vertical
  "GROWING REGIONS" panel: a location-pin + country + altitude band header, then one row per region with a dot on
  a connecting spine, the region name, and a short flavor descriptor. Fixed row spacing (34px) means labels can
  NEVER overlap. New data: each origin's regionMap got `alt` (altitude band) + `regions2` ([name, descriptor]).
  Enriched all 11 origins (old `shape`/`regions` fields left in data but unused now). Verified 11/11 render.
- **Heat diagram text truncation FIXED.** The legend descriptions were cut mid-word at `.slice(0,42)`. Added a
  reusable `wrapTspans(text,x,startY,lineH,maxChars,attrs)` helper and rewrote the heat legend to wrap instead of
  truncate.
- **Font typo fixed:** one `font-family="ui-mono"` (invalid) → `ui-monospace`.
- **Flavor wheel labels:** added `dominant-baseline="central"` for cleaner vertical centering.
- NOTE: the `view` image tool returned blank ALL session (known issue), so diagrams were verified via cairosvg
  render + non-bg pixel counts + structural SVG inspection rather than by eye. The origin-map redesign and the
  truncation/typo fixes are structural (collision-free by construction), so they're solid. Remaining fine
  pixel-level polish on the ~95 middle-anchored diagram texts is unverifiable this session — flagged for a future
  pass when the image tool works. Kevin considers image polish SECONDARY to depth.

## Depth-on-depth: 5 new deep pages (57 → 62 Learn pages; ~20,600 → ~23,000 words; 29 → 33 diagrams)
- **brew_machine** (The Espresso Machine) — follow-the-water model; pump types (vibratory vs rotary, OPV);
  boilers (single / heat-exchanger / dual / thermoblock); PID (~1°F vs 5–10°F swing); E61 group; pressure
  profiling & pre-infusion. Diagram: `espmachine` (water-path).
- **tasting** (How to Taste) — taste (tongue: sweet/sour/bitter/salty/umami) vs flavor (nose, retronasal);
  assessing STRUCTURE first; building flavor memory; a practice routine. Diagram: `tastemap`.
- **brew_latteart** (Latte Art) — art as a symptom of good milk; sink-then-surface; heart/rosetta/tulip;
  failure diagnosis. Diagram: `latteart`.
- **brew_waterrecipe** (Water Recipes) — water is ~98% of the cup; hardness vs alkalinity; the SCA target zone
  (~150 mg/L TDS etc.); filter/blend/build-from-distilled; DIY two-concentrate recipes. Diagram: `waterrecipe`.
- **cultures_world** (Coffee Cultures Worldwide) — Italy (espresso culture ancestor), Nordics (light-roast 3rd-
  wave vanguard), Turkey/Middle East (ancient boiled cezve tradition), Japan kissaten + the 4th-wave global
  cross-pollination. No diagram (narrative page).

## Navigation
- 12 pages got new/updated `related` cross-links weaving the new pages in; all 62 Learn pages now have related chips.
- Global search + inline glossary auto-cover the new content (verified: dual boiler, retronasal, rosetta,
  bicarbonate, kissaten all return hits).
- 4 new diagrams (espmachine, tastemap, latteart, waterrecipe) → 33 total.
- Size ~456 KB.

## Diagram inventory (33): roastcurve, phasebar, dtr, cracks, heat, extraction, espresso, grind, flavorwheel,
cva, processing, milk, brewfamilies, water, roasters, waves, supplychain, blend, cherry, vartree, pourover,
coldbrew, troubleshoot, milkdrinks, decaf, coffeemap, caffeine, espmachine, tastemap, latteart, waterrecipe.
(Origin region maps are a separate `originRegionMap()` renderer, not in the `diagram()` dispatcher.)

## What's genuinely left (all depth-on-depth, no structural gaps)
Kevin will likely re-run "go deeper" again. Candidate next pages: grinder deep-dive (burr types: conical vs flat,
alignment, retention, stepped vs stepless); more sensory detail (aroma kit / Le Nez, specific acid types);
coffee competitions & barista championships; espresso puck prep (WDT, distribution, tamping, channeling); coffee
storage & staling chemistry (O2/CO2/moisture, valve bags) as its own page; a deeper per-origin content pass;
subscription/DTC business mechanics; sca/certification pathways. Also: a future diagram-visual-polish pass once
the image tool works (audit the ~95 middle-anchored texts by eye). PMC track + interactive tools still deferred.

---

# v19 — DEPTH-ON-DEPTH ROUND 2 (grinder, puck prep, storage, competitions)

62 → 66 Learn pages; ~23,000 → ~25,000 words; 33 → 36 diagrams; ~480 KB. All the "next candidates" from the
v18 handoff, built.

## New pages
- **brew_grinder** (The Grinder) — grinder > machine in priority; burr vs blade; conical vs flat (gravity/cooler/
  low-retention/forgiving/punchy vs centrifugal/hotter/unimodal-clarity/espresso-standard); alignment, retention
  (single-dose, purge), stepped vs stepless. Diagram: `grinder` (conical vs flat side-by-side).
- **brew_puckprep** (Espresso Puck Prep) — channeling as the enemy; WDT (0.3–0.4mm needles, John Weiss 2005, be
  gentle/fines migration); distribution & leveling (dry room-temp basket, circle while grinding, distributor,
  puck screen); tamp LEVEL not hard (~15–30 lb, straightness > force). Diagram: `puckprep` (dose→WDT→level→tamp).
- **ops_storage** (Storage & Staling) — stales from oxygen/moisture/heat/light; degassing & the freshness window
  (rest ~days–2 weeks, espresso wants more); one-way valve + foil/opaque packaging; buy whole bean & grind per
  brew, airtight opaque container, freezing in airtight portions works (don't thaw/refreeze), never loose in
  fridge. Diagram: `staling` (freshness curve: rise→plateau→slow decline).
- **competitions** (Competitions & Championships) — SCA/WCE as sport+R&D+marketing; WBC (~15 min espresso+milk+
  signature); Brewers Cup, Cup Tasters, Roasting, Latte Art, Coffee in Good Spirits, Cezve/Ibrik; Cup of
  Excellence (producer competition, auction, rewards quality at source). No diagram (narrative).

## Navigation
- 9 pages got new/updated `related` cross-links; ALL 66 Learn pages now have related chips (related=66/66).
- Search + glossary auto-cover new content (verified: conical, channeling, degassing valve, cup of excellence,
  stepless all return hits).
- 3 new diagrams (grinder, puckprep, staling) → 36 total.
- NOTE on inline glossary: 51/66 pages have termrefs. The 15 without (grinder, puck prep, machine, business,
  history, competitions, several brew pages) legitimately don't use exact glossary vocabulary — the linker
  correctly only fires on real matches. This is expected, not a bug.

## Brew section is now very deep (17 pages)
extraction, espresso, machine, grind, grinder, puckprep, methods, pourover, immersion, cold, pressure,
troubleshoot, milk, drinks, latteart, water, waterrecipe. Covers theory → hardware → prep → every method →
milk/art → water. 

## Diagram inventory (36): + grinder, puckprep, staling on top of v18's 33.

## Still available for future depth-on-depth (Kevin will likely re-run)
Aroma/sensory kit deep-dive (Le Nez du Café, specific organic acids: malic/citric/acetic/quinic); espresso
recipe theory (ratio/yield/time dialing, updosing, temperature); milk science deep-dive (proteins/fats/
lactose, alt-milks steaming); a per-origin deeper content expansion (each origin page could gain processing/
harvest-season/notable-farms detail); SCA education/certification pathways; coffee roasting business
deep-dives (green contracts, futures hedging, importers). Plus the standing diagram-visual-polish pass once the
`view` image tool works again (it was blank all of v18–v19; diagrams verified structurally). PMC track +
interactive tools still deferred by direction.

---

# v20 — DEPTH-ON-DEPTH ROUND 3 (organic acids, espresso dialing, milk science)

66 → 69 Learn pages; ~25,000 → ~26,400 words; 36 → 39 diagrams; ~500 KB.

## New pages
- **acids** (The Acids in Coffee) [cupping group] — acidity = a prized POSITIVE quality; the bright acids
  (citric/lemon-juicy, malic/green-apple-tart, phosphoric/sparkling-cola/East-African); the others (acetic/
  vinegar, lactic/creamy, quinic/hot-plate-sour from chlorogenic breakdown, chlorogenic/bitter); how roast
  (bright acids fall, others rise → light bright, dark flat) & brewing (acids extract first → under-extraction
  tastes sour) move acidity. Type of acid > total amount. Diagram: `acidmap` (acid → flavor + brightness bars).
- **brew_dialing** (Dialing In Espresso) [brew] — the 3 numbers (dose/yield/time); brew ratio (1:2 balanced,
  ristretto 1:1–1.5, lungo 1:3+); grind as master dial (finer=more extraction fixes sour, coarser fixes bitter);
  taste-not-clock, one-variable-at-a-time, ~3–5 shots/bag; secondary levers (dose, temp light-hot/dark-cool,
  pre-infusion); drift with age/humidity. Diagram: `dialring` (recipe ring + sour/bitter fixes).
- **brew_milkscience** (Milk Science) [brew] — proteins (foam)/fat (texture)/lactose (heat→sweeter); two phases
  STRETCH (aerate early, cold) then TEXTURE (spin→microfoam); microfoam goal; temp ~55–65°C, past ~70°C scalds/
  collapses; finish (tap+swirl); alt-milks & why 'barista' editions foam. Diagram: `milkstretch` (stretch→texture).

## Navigation
- 8 pages cross-linked; ALL 69 Learn pages have related chips (related=69/69).
- Search + glossary auto-cover new content (verified: citric, brew ratio, microfoam, phosphoric, ristretto).
- 3 new diagrams (acidmap, dialring, milkstretch) → 39 total.

## Brew section now 19 pages; cupping now 10 pages
Brew: extraction, espresso, dialing, machine, grind, grinder, puckprep, methods, pourover, immersion, cold,
pressure, troubleshoot, milk, milkscience, drinks, latteart, water, waterrecipe — a genuinely complete barista
curriculum from theory → hardware → prep → dialing → every method → milk science/art → water.
Cupping: intro, mechanics, tasting, acids, cva_overview, cva_scoring, legacy_protocol, flavor_wheel, qc_loop,
q_grader.

## Diagram inventory (39): + acidmap, dialring, milkstretch on top of v19's 36.

## Still available for future depth-on-depth (Kevin WILL re-run)
Per-origin content expansion (each of the 11 origin pages could gain processing/harvest-season/notable-region
detail — I did NOT get to this yet, it's the biggest remaining chunk); water chemistry deeper (scale/descaling,
espresso-machine water); roasting-defect deep-dive with more bean visuals; green contracts/futures/importers
business mechanics; SCA education & certification pathways; a "coffee equipment maintenance" page (backflushing,
descaling, grinder cleaning, burr replacement); tea-vs-coffee or cascara/coffee-cherry-products curiosity page;
sugar/carbohydrate & Maillard aroma-compound chemistry deep-dive. Plus the standing diagram-visual-polish pass
once the `view` image tool works (blank since v18; diagrams verified structurally via cairosvg pixel counts).
PMC track + interactive tools still deferred by direction.

---

# v21 — PER-ORIGIN DEEP EXPANSION (the big remaining chunk) + accent-insensitive search

The 11 origin pages were the thinnest content in the app (145–320 words, roast-focused only). Now each is a
proper origin monograph: ~420–585 words, 6 sections, rich keypoints. Total app content (Learn + origins) is now
~31,600 words. Size ~521 KB.

## Every origin got 3 new deep sections + rewritten richer keypoints
Kept the existing "what you're working with / how to roast it / target" roast sections; APPENDED story, terroir/
processing, and regions. Highlights:
- **Ethiopia** — birthplace/genetic diversity/heirloom; smallholders→washing stations (station = #1 variable);
  regions (Yirgacheffe/Sidama/Guji/Harrar/Limu/Jimma).
- **Kenya** — technical powerhouse; SL28/SL34 (Scott Labs 1930s); the double-wash; Nairobi auction + AA/AB/PB =
  SIZE not quality; Nyeri/Kirinyaga.
- **Colombia** — three Andean ranges → year-round harvest; washed tradition; Federación/Cenicafé/Castillo;
  Huila/Nariño/Tolima/Eje Cafetero.
- **Brazil** — world's largest, moves C-price; low-altitude mechanized; natural/pulped-natural home; espresso
  backbone; Cerrado/Sul de Minas/Mogiana/Bahia.
- **Sumatra** — Dutch/Java legacy; wet-hulling (giling basah) = the earthy/savory signature; Gayo/Lintong/
  Mandheling.
- **Guatemala** — volcanic, 8 Anacafé regions; Antigua/Huehuetenango/Atitlán/Cobán.
- **Costa Rica** — Arabica-only tradition; micro-mill revolution + honey process; Tarrazú/Central+West Valley.
- **Panama** — the Geisha revolution (2004 Best of Panama, La Esmeralda); Boquete/Volcán; experimental processing.
- **El Salvador** — preserved Bourbon genetics; Pacas & Pacamara; Apaneca-Ilamatepec.
- **Honduras** — Central America's largest, rising into specialty; IHCAFE; 6 regions incl. Marcala DO.
- **Nicaragua** — rising CoE performer; Maragogype/Pacamara; Nueva Segovia/Jinotega/Matagalpa.
Ethiopia & Kenya also got proper sourcing refs (the others retain existing refs).

## Accent-insensitive global search (bonus fix)
Origin content is full of accented names (Tarrazú, Nariño, Antigua, Cobán). Added NFD-normalize + diacritic-strip
to `runGlobalSearch` for BOTH query and haystack, so "tarrazu" finds "Tarrazú". Verified: tarrazu, antigua,
huehuetenango, cerrado all return hits now. General search quality improvement.

## State
- 69 Learn pages + 11 origins + intro; 39 diagrams; ~31,600 words total; ~521 KB.
- Regression ALL GREEN: all learn render, all origins deep (>1500 chars each), 39 diagrams, region panels intact,
  profile pairings intact, accent-search working.

## Still available for future depth-on-depth (Kevin WILL re-run)
- Even deeper origins: per-origin harvest-CALENDAR specifics, notable farms/producers, processing-innovation
  detail, or splitting mega-regions into sub-region notes.
- Coffee equipment MAINTENANCE page (backflushing, descaling, grinder/burr cleaning & replacement) — flagged
  earlier, still not built.
- Deeper roast-defect gallery with more bean visuals; sugar/carbohydrate & Maillard aroma-compound chemistry;
  green contracts/futures/importer mechanics; SCA education & certification pathways; a cascara / coffee-cherry-
  products curiosity page; tea-vs-coffee.
- STANDING: diagram visual-polish pass once the `view` image tool works (blank v18–v21; all diagrams verified
  structurally via cairosvg pixel counts + SVG inspection). The origin region-map redesign (v18) is collision-
  free by construction and confirmed good.
- PMC track + interactive tools still deferred by direction.

---

# v22 — 10 NEW ORIGINS (11 → 21), auto-wired into profile pairings

Added the major missing origins (Kevin flagged Hawaii & Vietnam). Each new origin uses the FULL schema
(sections, keypoints, refs, country/continent/lat/lng, regions, altitude, varieties, process, harvest,
roastLevel, flavorTags, blurb, regionMap with alt+regions2) so it auto-appears in profile "Origins That Shine
Here" pairings (which read roastLevel band ±1) AND on the Origins tab. Total content now ~34,700 words.

## New origins (each 266–349 words, 3 rich sections + keypoints + refs + region panel)
- **Hawaii (Kona)** [North America, Medium] — only US state growing coffee; the Kona belt terroir; smooth/low-acid/
  nutty; Kaʻū/Puna/Hāmākua/Maui; the '10% Kona blend' label trap.
- **Vietnam** [Asia, Dark] — world #2 producer / #1 Robusta; Đổi Mới boom; Central Highlands red basalt; bold/
  chocolatey/earthy; phin + condensed milk (cà phê sữa đá); rising specialty Robusta & Arabica.
- **Yemen** [Middle East, Medium–Dark] — where coffee cultivation & trade BEGAN (Mokha→'mocha'); ancient terraces/
  landraces ('Yemenia'); wild winey dried-fruit naturals; rare, war-affected.
- **Rwanda** [Africa, Light–Medium] — post-genocide specialty success; 1st African CoE host; Bourbon washed;
  clean/floral/red-fruit; the potato defect.
- **Burundi** [Africa, Light–Medium] — tiny landlocked neighbor; high washed Bourbon; elegant/juicy/floral;
  underrated value.
- **Tanzania** [Africa, Light–Medium] — Kilimanjaro + the famous PEABERRY; bright/berry/wine-like; north vs
  southern-highlands (Mbeya) vs Kigoma.
- **India** [Asia, Medium–Dark] — Baba Budan legend; shade-grown Western Ghats; the unique MONSOONED MALABAR
  process; low-acid/spice/chocolate; Arabica + Robusta.
- **Mexico** [North America, Medium] — biggest N. American producer; Chiapas/Oaxaca/Veracruz; mild/clean/
  chocolatey; major ORGANIC source; SHG grade.
- **Peru** [South America, Medium] — organic & fair-trade powerhouse; remote Andean smallholders/co-ops; mild/
  sweet/balanced; Cajamarca/Amazonas.
- **Papua New Guinea** [Oceania, Medium] — rugged Highlands 'garden' smallholders; JBM Typica seed stock; wild/
  fruity/full-bodied; isolation challenge.

## Wiring fixes
- **Origins tab continent order** expanded: was ['Africa','Central America','South America','Asia'] which
  silently dropped North America/Middle East/Oceania origins. Now
  ['Africa','Middle East','Central America','North America','South America','Asia','Oceania'] — all 21 show,
  grouped by region.
- Profile pairings auto-updated (data-driven via roastBand ±1): verified dark profiles (Italian/Vienna) now list
  Vietnam & India; light profiles (Nordic/Blonde) list Rwanda; Espresso lists Vietnam & Hawaii. NO code change
  needed — the pairing engine reads any origin with roastLevel+flavorTags.
- Search finds all new origins (kona, monsooned, peaberry, robusta, mokha, oaxaca verified) via the existing
  accent-insensitive search.

## State
- 69 Learn pages + 21 origins + intro; 39 diagrams; ~34,700 words; ~560 KB.
- Regression ALL GREEN: all learn render, all 21 origins deep (>1200 chars) with region panels, origins tab=21,
  pairings wired, search working.

## Roast-band distribution of origins (for pairing coverage)
Light: Ethiopia, Panama. Light–Medium: Colombia, Kenya, Rwanda, Burundi, Tanzania. Medium: Guatemala, Costa
Rica, El Salvador, Honduras, Nicaragua, Hawaii, Mexico, Peru, PNG. Medium–Dark: Brazil, Sumatra, Yemen, India.
Dark: Vietnam. (Good spread across all bands now — every profile gets sensible pairings.)

## Still available for future depth-on-depth (Kevin WILL re-run)
- MORE origins possible: Jamaica (Blue Mountain), Uganda, Indonesia beyond Sumatra (Java, Sulawesi/Toraja, Bali,
  Flores), Ecuador, Bolivia, DR Congo, Malawi, Zambia, Thailand, China (Yunnan).
- Even deeper existing origins: harvest-calendar specifics, notable farms/producers, sub-region splits.
- Non-origin: coffee equipment MAINTENANCE page (backflush/descale/burr) — STILL not built; roast-defect visual
  gallery expansion; Maillard/aroma-compound chemistry; SCA certification pathways; cascara/cherry products.
- STANDING: diagram visual-polish pass when `view` tool is reliable (flickered back in v22 — Vietnam region panel
  rendered correctly, confirming the v18 panel redesign looks good).
- PMC track + interactive tools still deferred by direction.

---

# v23 — 8 MORE ORIGINS (21 -> 29) + equipment maintenance page

Added the rest of Indonesia, the Caribbean, and more. 29 origins now; 70 Learn pages; 100 total methodology
pages; ~37,500 words; ~597 KB.

## New origins (each 264-311w, full schema, auto-wired into profile pairings by roast band)
- **Java** [Asia, Med-Dark] - where colonial coffee began, java=slang, Mocha-Java blend, Ijen Plateau washed
  estates, rust->Robusta history.
- **Sulawesi (Toraja)** [Asia, Med-Dark] - highland wet-hulled but cleaner than Sumatra; syrupy/savory/spice;
  Tana Toraja + Kalosi/Enrekang; prized in Japan.
- **Bali (Kintamani)** [Asia, Medium] - newer, clean/bright; Subak Abian Hindu farming system; citrus/nutty;
  the clean side of Indonesia.
- **Flores (Bajawa)** [Asia, Medium] - eastern volcanic gem, Portuguese heritage genetics; chocolate/floral;
  rising star.
- **Jamaica** [Caribbean, Medium] - Blue Mountain: famous/expensive, legally protected name, JBM Typica,
  barrels, prized-but-debated mild balance.
- **Uganda** [Africa, Medium] - Robusta NATIVE homeland; Mount Elgon (Bugisu) washed Arabica rising; huge
  exporter; wild eugenioides.
- **Ecuador** [S. America, Medium] - high Andes on the equator; the buzzy SIDRA variety; even Galapagos coffee;
  emerging specialty.
- **Bolivia** [S. America, Light-Med] - tiny/landlocked/very-high Yungas; Caranavi; clean/sweet/delicate/
  floral; coca competition; rare treasure.

## New Learn page
- **ops_maintenance** (Equipment Maintenance) [ops, 555w] - maintenance as a FLAVOR issue; backflushing (blind
  basket, water daily / detergent weekly, never vinegar, solenoid-only); descaling (scale = #1 killer, by water
  hardness, filtered water prevention, some machines technician-only); grinder (brush/pellets, no water, burr
  wear/replacement), gaskets, steam-wand hygiene. Diagram: maintenance (Daily/Weekly/Monthly/Periodic cadence).
  Cross-linked with brew_machine, brew_grinder, ops_storage, brew_water.

## Wiring fixes
- Added Caribbean to the origins-tab contOrder (Jamaica introduced it) -> was going to drop like the N.America/
  Middle East/Oceania bug last round. Order now: Africa, Middle East, Central America, Caribbean, North America,
  South America, Asia, Oceania. All 29 show, grouped.
- Profile pairings auto-updated (data-driven): verified dark profiles list Java/Sulawesi/Vietnam/India; medium
  (American/Full City) list Jamaica/Bali/Flores/Hawaii/etc; light list Bolivia/Rwanda. NOTE: "City" profile is a
  Light-Medium band so it lists lighter origins - Jamaica/Bali correctly appear under the true-Medium profiles.
- Search finds all new content (toraja, kintamani, blue mountain, bugisu, sidra, caranavi, backflush, descale).

## State
- 70 Learn pages + 29 origins + intro; 40 diagrams; ~37,500 words; ~597 KB.
- Regression ALL GREEN (the one test "fail" was a wrong assertion about City band, not a bug).

## Origin roast-band spread (29 total)
Light: Ethiopia, Panama. Light-Med: Colombia, Kenya, Rwanda, Burundi, Tanzania, Bolivia. Medium: Guatemala,
Costa Rica, El Salvador, Honduras, Nicaragua, Hawaii, Mexico, Peru, PNG, Bali, Flores, Jamaica, Uganda, Ecuador.
Med-Dark: Brazil, Sumatra, Yemen, India, Java, Sulawesi. Dark: Vietnam.

## Still available for future depth (Kevin WILL re-run)
- Even more origins: DR Congo, Malawi, Zambia, Thailand, China (Yunnan), Timor-Leste, Cuba, Dominican Republic,
  Haiti, Venezuela, Zimbabwe, Myanmar, Laos, Philippines, El Salvador done.
- Even deeper existing origins (harvest calendars, notable farms, sub-region splits).
- Non-origin: roast-defect visual gallery expansion; Maillard/aroma-compound chemistry deep-dive; SCA
  education/certification pathways; cascara/coffee-cherry products; tea-vs-coffee; a decaf deep-dive already
  exists (decaf_methods) but could expand.
- STANDING: diagram visual-polish pass - the view tool WORKED this session (maintenance + Vietnam panel both
  rendered correctly on screen), so a polish pass is now feasible if desired.
- PMC track + interactive tools still deferred by direction.

---

# v24 — 7 MORE ORIGINS (29 -> 36): emerging Africa + Asia

Deep-dive continuation. 36 origins now; ~39,500 words; 107 methodology pages; ~624 KB. Continent spread now:
Africa 10, Asia 10, Central America 6, South America 5, North America 2, Middle East 1, Caribbean 1, Oceania 1.

## New origins (each 265-311w, full schema, auto-wired into pairings)
- **DR Congo** [Africa, Light-Med] - Kivu, across Lake Kivu from Rwanda (same terroir); harrowing history
  (farmers smuggled coffee across the lake); SOPACDI revival, ~100 new washing stations; bright/red-fruit.
- **Malawi** [Africa, Light-Med] - tiny; the GEISHA surprise (some of the best outside Panama, introduced
  decades early); Misuku Hills; clean/tea-like/citrus; hidden gem.
- **Zambia** [Africa, Light-Med] - unusual ESTATE-driven model (vs smallholder norm); clean/bright/chocolate;
  bumpy history, rebuilding; good value.
- **Zimbabwe** [Africa, Medium] - once ranked with Africa best (~15,000t in 1999); collapsed via 2000s land
  reform (a lesson: quality needs institutions, not just terroir); Chipinge/Mutare quiet revival.
- **Thailand** [Asia, Medium] - northern Arabica from royal OPIUM-substitution projects (Royal Project, Doi
  Tung); clean/sweet; Doi Chaang/Doi Tung; fast-rising, big domestic culture.
- **China (Yunnan)** [Asia, Medium] - the "sleeping giant"; ~99% from Yunnan; French-missionary origin +
  Nestlé/Puer investment; Catimor-dominant, mild/chocolatey; rapid commodity->specialty climb.
- **Timor-Leste** [Asia, Medium] - birthplace of the TIMOR HYBRID (HdT, natural Arabica x Robusta -> foundation
  of Catimor/Sarchimor worldwide); organic-by-default; Ermera; sweet/chocolate/earthy; CCT co-op.

## Notes
- No continent-order bug this round (all Africa/Asia, already in contOrder). All 36 show on the tab, grouped.
- Profile pairings auto-updated: verified medium profiles list Thailand/China/Timor/Zimbabwe; light profiles
  list Congo/Malawi/Zambia. Data-driven, no code change.
- Search finds all (kivu, sopacdi, misuku, doi chaang, yunnan, timor hybrid, opium verified).
- Regression ALL GREEN.

## Origin roast-band spread (36 total)
Light: Ethiopia, Panama. Light-Med: Colombia, Kenya, Rwanda, Burundi, Tanzania, Bolivia, Congo, Malawi, Zambia.
Medium: Guatemala, Costa Rica, El Salvador, Honduras, Nicaragua, Hawaii, Mexico, Peru, PNG, Bali, Flores,
Jamaica, Uganda, Ecuador, Zimbabwe, Thailand, China, Timor. Med-Dark: Brazil, Sumatra, Yemen, India, Java,
Sulawesi. Dark: Vietnam.

## Still available (Kevin WILL re-run)
- Even more origins: Cuba, Dominican Republic, Haiti, Puerto Rico, Venezuela, Cote d Ivoire, Myanmar, Laos,
  Nepal, Philippines, Australia. (Getting into truly minor/rare territory now - could also PIVOT to non-origin.)
- Non-origin content still open: roast-defect visual gallery; Maillard/aroma-compound chemistry deep-dive; SCA
  education/certification pathways; cascara/coffee-cherry products; tea-vs-coffee; espresso-machine-types deep
  dive; water-chemistry-for-brewing deep dive.
- PENDING (agreed with Kevin): a DIAGRAM VISUAL-POLISH PASS - go through all 40 diagrams by eye now that the
  view tool is working, tighten spacing/contrast/labels. Kevin wants MORE content deep-dives first, THEN polish.
- PMC track + interactive tools still deferred by direction.

---

# v25 — NON-ORIGIN DEEP DIVES: aroma chemistry, SCA education, cascara, coffee vs tea

Pivoted from origins to remaining non-origin content (Kevin: "keep going on non origin content, depth upon
depth"). 74 Learn pages now; 44 diagrams; ~41,500 words total; 111 methodology pages; ~652 KB.

## New Learn pages (each 472-528w, full schema + diagram + cross-links)
- **aroma_chemistry** (Aroma Chemistry) [science, 513w] - green coffee has ~NO flavor; heat creates 800+ volatiles.
  Maillard (sugars+amino acids, ~140-160C, needs both, source of most volatiles + melanoidins); caramelization
  (sugars alone, ~160-170C); Strecker (amino acids -> aldehydes). Compound families -> smells (pyrazines nutty,
  furans sweet, aldehydes fruity/malty, ketones buttery, sulfur tiny-but-huge). Why roast level changes
  everything + the too-fast-pressure-suppresses-Maillard wrinkle. Diagram: aromachem.
- **biz_education** (Coffee Education & Certification) [business, 528w] - why certs exist (sommelier parallel);
  SCA Coffee Skills Program (Intro + 5 modules Barista/Brewing/Green/Roasting/Sensory x Foundation/Intermediate/
  Professional -> Skills Diploma); Q Grader (CQI, ~6 days, ~20 exams, Le Nez du Cafe, ~$1.5-2k, recalibration);
  wider landscape (Barista Hustle, WCE championships, Sustainability/Technicians programs, MSC). Diagram: scapath.
- **cascara** (The Coffee Cherry & Cascara) [green, 497w] - the bean is a seed inside a fruit; cascara (dried
  husk -> fruity tisane, qishr history, tastes like fruit not bean); other products (coffee flour, fruit
  extracts/supplements, syrups, beer); why it matters (pulp pollution, farmer income, whole-fruit mindset).
  Diagram: cherrybyproduct (cherry cross-section -> products).
- **tea_coffee** (Coffee vs Tea) [culture, 472w] - the two caffeinated giants; different plants (Coffea seed vs
  Camellia leaf; tea types = processing like roast); caffeine (tea more per dry gram BUT coffee more per cup
  ~95 vs 30-50mg; L-theanine); parallel crafts (terroir/processing/ritual/brewing); which & when. Diagram:
  teacoffee.

## Diagrams (44 total): + aromachem, scapath, cherrybyproduct, teacoffee

## Group counts now
culture 9, green 8, read 5, science 4, practice 2, cupping 10, ops 9, brew 19, grow 4, business 4.
Science section now has a proper chemistry pair (chemistry + aroma_chemistry). Business now 4 (biz_roastery,
biz_cafe, biz_menu, biz_education).

## Notes
- All 74 Learn pages cross-linked (related=74). 9 pages got new/updated related chips.
- Search + glossary auto-cover new content (maillard, pyrazine, q grader, cascara, l-theanine, strecker,
  sensory skills all verified). Regression ALL GREEN.
- aromachem diagram rendered & confirmed good on screen (view tool working).

## Still available for future depth (Kevin WILL re-run)
- Non-origin still open: espresso-machine-TYPES deep dive (lever/pump/HX/dual-boiler); water-chemistry-for-
  brewing deep dive (SCA water standard, GH/KH, recipes - some exists in brew_water/brew_waterrecipe but could
  go deeper); a coffee-history timeline expansion; green-coffee-buying/contracts/futures/C-price deep dive;
  decaf deep-dive expansion; grinder-burr-geometry deep dive; a roast-defect VISUAL gallery (needs bean SVGs).
- More origins if desired: Cuba, Dominican Republic, Haiti, Puerto Rico, Venezuela, Cote d Ivoire, Myanmar,
  Laos, Nepal, Philippines, Australia (minor/rare now).
- PENDING (agreed): DIAGRAM VISUAL-POLISH PASS through all 44 diagrams by eye. Kevin wants content deep-dives
  first, THEN the polish pass.
- PMC track + interactive tools still deferred by direction.

---

# v26 — NON-ORIGIN DEEP DIVES: espresso machine types + water chemistry

Continued non-origin depth. 76 Learn pages; 46 diagrams; ~42,800 words; 113 methodology pages; ~669 KB.

## New Learn pages (both in brew group, full schema + diagram + cross-links)
- **brew_machinetypes** (Espresso Machine Types) [brew, 647w] - how pressure is made (steam weak / LEVER Gaggia
  1948 first crema / PUMP Faema E61 1961 standard); single boiler (brew OR steam, PID = value); heat exchanger
  (thermosiphon brew pipe, cooling flush, E61) vs dual boiler (two boilers, direct temp, premium); PID (vs
  pressurestat, settable temp, key for light roasts) + pressure profiling/flow control (pre-infusion->full->
  taper, levers inherent). Caveat: PID sets boiler not cup; stability+grinder matter more than category.
  Diagram: machtypes (3 boiler configs side by side).
- **brew_waterchem** (Water Chemistry) [brew, 561w] - coffee is ~98% water (espresso ~90%); GH (General
  Hardness = Ca+Mg = EXTRACTS flavor, too little=flat) vs KH (alkalinity/bicarbonate = BUFFERS acidity, too
  much=dull, too little=sour); SCA water target (TDS ~150, Ca ~50-75, alkalinity ~40, pH ~7, ~0 chlorine);
  flavor-vs-scale tension (KH bicarbonate = what forms scale -> longevity wants soft); practical path (filtered
  in range, not distilled-alone/hard-tap, test hardness). Diagram: waterchem (GH/KH + SCA target).

## Diagrams (46 total): + machtypes, waterchem

## Brew section is now 21 pages
The most comprehensive section by far: extraction, espresso, dialing, machine, machinetypes, grind, grinder,
puckprep, methods, pourover, immersion, cold, pressure, troubleshoot, milk, milkscience, drinks, latteart,
water, waterchem, waterrecipe. A genuinely complete barista/espresso curriculum incl. hardware internals +
water science.

## Notes
- All 76 Learn pages cross-linked (related=76). Search finds all new content (dual boiler, heat exchanger,
  thermosiphon, general hardness, alkalinity, pid, pressure profiling verified). Regression ALL GREEN.
- machtypes diagram rendered & confirmed good on screen.

## Still available for future depth (Kevin WILL re-run)
- Non-origin still open: green-coffee-buying / C-price / futures / contracts deep dive; a coffee-history
  timeline expansion; decaf deep-dive expansion; a roast-defect VISUAL gallery (needs new bean SVGs);
  coffee-and-climate-change deep dive; the economics/ethics of pricing (living income, FOB vs C-price).
- More origins if desired: Cuba, Dominican Republic, Haiti, Puerto Rico, Venezuela, Cote d Ivoire, Myanmar,
  Laos, Nepal, Philippines, Australia (minor/rare).
- PENDING (agreed): DIAGRAM VISUAL-POLISH PASS through all 46 diagrams by eye. Kevin wants content deep-dives
  first, THEN polish.
- PMC track + interactive tools still deferred by direction.

---

# v27 — NON-ORIGIN DEEP DIVES: the C-market/coffee economics + climate change

Continued non-origin depth (the economics & climate gap). 78 Learn pages; 48 diagrams; ~43,900 words; 115
methodology pages; ~685 KB. Culture group now 11 pages.

## New Learn pages (both culture group, full schema + diagram + cross-links)
- **cmarket** (The C-Market & Coffee Prices) [culture, 607w] - what the C price is (green Arabica benchmark, ICE
  NY futures, C=Centrals, ~37,500lb lots, 20 countries/8 warehouses, Robusta separate/London); why it swings
  (supply/demand: weather/disease/harvest cycles/few dominant countries + SPECULATION by funds); differentials
  (C is a starting point -> differential -> FOB -> middlemen -> farmgate, farmer gets a small shrinking slice);
  the ethics (high C often does not help producers, below living income, drives Fairtrade/direct trade/living-
  income pricing). Grounded in current data: sank <$1 in 2018-19, exceeded $4 first time ever early 2025.
  Diagram: cmarket (price waterfall C->farmgate).
- **climate_coffee** (Coffee & Climate Change) [culture, 508w] - Arabica among most climate-vulnerable crops
  (narrow 18-22C band); what is already happening (low-elevation land unviable, erratic rain spiking prices,
  rust/borer spreading higher, extreme events; Arabica-suitable land could ~halve by 2050); adapting (resistant
  varieties/WCR/Timor-Hybrid lineage, forgotten species stenophylla/liberica, shade/agroforestry, higher
  ground); a JUSTICE issue (~12.5M smallholder families bear worst impacts, thin margins block adaptation ->
  links environmental + economic sustainability). Diagram: climatecoffee (threat vs adaptation).

## Diagrams (48 total): + cmarket, climatecoffee

## Notes
- These two pages tie together threads from across the app: supply_chain, sustainability, threats, varietals,
  green_species, the Timor-Hybrid origin, competitions. Cross-linked accordingly.
- All 78 Learn pages cross-linked (related=78). Search finds all new content (c price, differential, farmgate,
  futures, leaf rust, stenophylla, living income verified). Regression ALL GREEN.
- cmarket diagram rendered & confirmed good on screen.

## Content coverage is now very broad. Group counts:
culture 11, brew 21, cupping 10, ops 9, green 8, read 5, science 4, grow 4, business 4, practice 2 = 78 Learn
+ 36 origins + intro = 115 methodology pages, 48 diagrams, ~43,900 words.

## Still available for future depth (Kevin WILL re-run)
- Non-origin still open: a coffee-history TIMELINE expansion (history page exists but could become a rich dated
  timeline); decaf deep-dive expansion (decaf_methods exists); a roast-defect VISUAL gallery (needs new bean
  SVGs - the one genuinely visual-heavy addition left); coffee-varieties deep dive (varietals exists, could go
  much deeper w/ a variety family tree - vartree diagram already exists); instant/soluble coffee deep dive;
  the history of espresso/cafe culture deep dive.
- More origins if desired: Cuba, Dominican Republic, Haiti, Puerto Rico, Venezuela, Cote d Ivoire, Myanmar,
  Laos, Nepal, Philippines, Australia (minor/rare).
- PENDING (agreed): DIAGRAM VISUAL-POLISH PASS through all 48 diagrams by eye. Kevin wants content deep-dives
  first, THEN polish.
- PMC track + interactive tools still deferred by direction.

---

# v28 — NON-ORIGIN DEEP DIVES: coffee history timeline + the coffeehouse

Continued non-origin depth (the history gap). 80 Learn pages; 49 diagrams; ~45,000 words; 117 methodology pages;
~698 KB. Culture group now 13 pages (the app has crossed 80 Learn pages).

## New Learn pages (both culture, full schema + cross-links)
- **history_timeline** (A History of Coffee) [culture, 690w] - dated narrative: Ethiopia (wild Arabica, Kaldi
  legend, ceremony ~1400) -> Yemen (15th c Sufi drink, Mocha trade, 2-century monopoly) -> Ottoman coffeehouses
  (~1475 Constantinople, qahveh khaneh, 1511 Mecca ban) -> Europe (Venice ~1600, Pope Clement VIII, Oxford
  ~1650/London 1652 penny universities, Le Procope 1686, Bach Coffee Cantata 1732) -> colonial expansion (Dutch
  Java, de Clieu seedling to Martinique ~1720, Brazil ~1727, Haiti half the world, slave labor) -> modern (vacuum
  1900, instant 1901, decaf 1903, Gaggia 1948, 2nd/3rd wave). Diagram: historytimeline (9-event dated axis).
- **coffeehouse** (The Coffeehouse) [culture, 489w] - the original social network; penny universities (Royal
  Society/Enlightenment); crucible of commerce (Lloyd\047s coffeehouse -> Lloyd\047s of London insurance; Jonathan\047s/
  Garraway\047s -> London Stock Exchange); evolution (Viennese coffee house/UNESCO, Parisian cafe, Oldenburg\047s
  THIRD PLACE -> today\047s specialty cafe). No diagram (narrative).

## Diagrams (49 total): + historytimeline

## Notes
- These tie into the existing history page + waves + cultures_world + biz_cafe + many origin pages (Yemen/Mocha,
  Java, Brazil, Haiti, Martinique). Cross-linked accordingly. history + waves + cultures_world + biz_cafe got
  new related chips.
- All 80 Learn pages cross-linked (related=80). Search finds all new content (kaldi, penny universities, gabriel
  de clieu, lloyd, pope clement, qahveh, mocha verified). Regression ALL GREEN.
- NOTE for polish pass: the historytimeline diagram is a touch DENSE (9 events + 2-line labels on one axis) -
  legible & structurally sound but a good candidate to refine (maybe fewer events or a taller layout) during the
  agreed diagram visual-polish pass.

## Still available for future depth (Kevin WILL re-run)
- Non-origin still open: decaf deep-dive expansion (decaf_methods exists); a coffee-VARIETIES family-tree deep
  dive (varietals exists + vartree diagram exists, could go much deeper - Typica/Bourbon lineage, Geisha, SL,
  Catimor/Timor Hybrid family); instant/soluble coffee deep dive; the history of ESPRESSO specifically; a
  roast-defect VISUAL gallery (needs new bean SVGs - the one genuinely visual-heavy addition left).
- More origins if desired: Cuba, Dominican Republic, Haiti, Puerto Rico, Venezuela, Cote d Ivoire, Myanmar,
  Laos, Nepal, Philippines, Australia (minor/rare).
- PENDING (agreed): DIAGRAM VISUAL-POLISH PASS through all 49 diagrams by eye (incl. tightening historytimeline).
  Kevin wants content deep-dives first, THEN polish.
- PMC track + interactive tools still deferred by direction.

---

# v29 — NON-ORIGIN DEEP DIVES: the Arabica family tree + the coffee species

Continued non-origin depth (genetics/varieties). 82 Learn pages; 51 diagrams; ~46,150 words; 119 methodology
pages; ~714 KB. Grow group now 6 pages (plant, varietals, variety_tree, species_deep, harvest, threats).

## New Learn pages (both grow group, full schema + diagram + cross-links)
- **variety_tree** (The Arabica Family Tree) [grow, 573w] - two founders TYPICA (via Amsterdam, tall/sweet) &
  BOURBON (mutated on Bourbon/Reunion); Bourbon dwarf mutations (Caturra BR ~1937 first known, Pacas, Villa
  Sarchi, Yellow Bourbon, low-caff Laurina); great crosses (Mundo Novo=Bourbon x Typica -> Catuai w/ Caturra;
  Pacamara=Pacas x Maragogipe; Kenya SL28/SL34; Geisha Ethiopian landrace star ~2004); disease-resistant branch
  (Timor Hybrid=Arabica x Robusta -> Catimor x Caturra / Sarchimor x Villa Sarchi; Castillo, Cenicafe 1, IAPAR
  59, Obata, Ruiru 11, Batian; F1 hybrids like Centroamericano). Diagram: familytree.
- **species_deep** (Arabica, Robusta & the Rest) [grow, 519w] - 2 species run the world: Arabica (~60-70%, high/
  delicate/complex, ~1.2-1.5% caffeine) vs Robusta (~30-40%, hardy/bitter, ~2.2-2.7% caffeine); why Arabica
  tastes better + is fragile (allotetraploid natural eugenioides x canephora hybrid, self-pollinating, LOW
  diversity); forgotten species (Liberica/Barako, Excelsa, rediscovered Stenophylla = heat-tolerant Arabica-like
  climate hope); on-the-bag takeaways (specialty=~100% Arabica; espresso blends add Robusta for crema/body).
  Diagram: speciesmap.

## Diagrams (51 total): + familytree, speciesmap

## Bug caught during build (logged for future reference)
- diaSpeciesMap initially crashed the whole render loop: array had 4 elements [name,sci,color,list] but code
  read sp[4] for the list (should be sp[3]). Symptom was tricky: species_deep rendered fine ALONE, but iterating
  all diagrams threw \"Cannot read properties of undefined (reading forEach)\". Also note: jsdom floods stderr with
  harmless \"Not implemented: scrollTo\" warnings from back-button nav that can drown real output - filter stdout
  only, do NOT use beforeParse to stub scrollTo (breaks script init). Fixed, re-verified ALL GREEN.

## Notes
- Ties deeply into origin pages (Timor=Timor Hybrid birthplace, Panama/Malawi=Geisha, Kenya=SL28/SL34, Brazil=
  Caturra/Mundo Novo, El Salvador=Pacas/Pacamara) + climate_coffee (fragility) + threats + green_species. Cross-
  linked. varietals/green_species/plant/climate_coffee/threats got new related chips.
- All 82 Learn pages cross-linked (related=82). Search finds all (typica, bourbon, caturra, catimor, timor
  hybrid, geisha, stenophylla, liberica, canephora verified). Regression ALL GREEN.
- NOTE for polish pass: familytree is now the DENSEST diagram in the app (5 rows of boxes + many connecting
  lines). Legible & structurally correct but the #1 candidate to refine/simplify during the diagram polish pass,
  alongside historytimeline.

## Content coverage is now extremely broad. Grow group finally has real depth (was a known light spot).
Group counts: culture 13, brew 21, cupping 10, ops 9, green 8, grow 6, read 5, science 4, business 4, practice 2
= 82 Learn + 36 origins + intro = 119 methodology pages, 51 diagrams, ~46,150 words.

## Still available for future depth (Kevin WILL re-run)
- Non-origin still open: decaf deep-dive expansion (decaf_methods exists); instant/soluble coffee deep dive;
  the history of ESPRESSO specifically; roast-defect VISUAL gallery (needs new bean SVGs - the one genuinely
  visual-heavy addition left); a single-variety spotlight series (Geisha, SL28, Bourbon deep profiles).
- More origins if desired: Cuba, Dominican Republic, Haiti, Puerto Rico, Venezuela, Cote d Ivoire, Myanmar,
  Laos, Nepal, Philippines, Australia (minor/rare).
- PENDING (agreed): DIAGRAM VISUAL-POLISH PASS through all 51 diagrams by eye (esp. familytree + historytimeline,
  the two densest). Kevin wants content deep-dives first, THEN polish.
- PMC track + interactive tools still deferred by direction.

---

# v30 — NON-ORIGIN DEEP DIVES: how decaf is made + instant coffee

Continued non-origin depth. 84 Learn pages; 53 diagrams; ~47,300 words; 121 methodology pages; ~729 KB.

## New Learn pages (full schema + diagram + cross-links)
- **decaf_deep** (How Decaf Is Made) [green, 645w] - deeper than the existing decaf_methods overview. Shared
  challenge (remove ~97-99% caffeine, US legal 97%, leave flavor; all: steam/soak->extract->dry, the AGENT
  differs). SOLVENT methods (Roselius 1903 orig benzene; today MC=methylene chloride aggressive/medicinal rep,
  residue ~10ppm cap; EA=ethyl acetate gentler/sweeter, marketed natural/sugarcane from molasses BUT can be
  petroleum-synth). CLEAN methods: Swiss Water (caffeine-free green-coffee-extract soak so only caffeine
  diffuses out, charcoal filter/reuse, 99.9%/organic; Mountain Water same); CO2 (supercritical, top flavor
  retention, pricey equip). Why good decaf now exists (clean methods + better tech + specialty decaffeinating
  GOOD green not junk). Diagram: decafmethods.
- **instant_coffee** (Instant Coffee) [science, 521w] - the coffee most of the world drinks (huge global share,
  dominant UK/Asia/E.Europe/developing; brewed coffee w/ water removed; mostly Robusta). Two drying methods:
  SPRAY (older/cheap, mist into hot-air tower->powder, heat costs aroma) vs FREEZE (premium, freeze ~-40C then
  vacuum-sublimate->crystalline granules, cold preserves aroma). History (attempts 1800s, Nescafe 1938 for
  Brazil surplus, WWII rations spread it, mid-century 1st-wave golden age). Specialty instant REVIVAL (Swift
  Cup/Voila/Sudden, single-origin Arabica freeze-dried). Diagram: instantcoffee.

## Diagrams (53 total): + decafmethods, instantcoffee

## Notes
- Careful with diagram array indices this time (after v29 sp[4]-vs-sp[3] bug) - both new diagrams verified
  rendering via cairosvg+pixel-region analysis. NOTE: the view IMAGE tool returned empty again intermittently
  (as it did v18-21) but pixel counts confirm render; not blocking.
- decaf_deep ties to decaf_methods/green_processing/health; instant_coffee to waves/species_deep/history_
  timeline/roasters. Cross-linked. decaf_methods/roasters/waves/health got new related chips.
- All 84 Learn pages cross-linked (related=84). Search finds all (swiss water, ethyl acetate, supercritical,
  methylene chloride, freeze drying, nescafe, sublimate verified). Regression ALL GREEN.

## Group counts: culture 13, brew 21, cupping 10, green 9, ops 9, grow 6, read 5, science 5, business 4,
practice 2 = 84 Learn + 36 origins + intro = 121 methodology pages, 53 diagrams, ~47,300 words.

## Still available for future depth (Kevin WILL re-run)
- Non-origin still open: the history of ESPRESSO specifically (Bezzera/Gaggia/Faema/lever->pump->3rd wave
  machines - some of this is scattered across brew_machinetypes/history_timeline but no dedicated espresso-
  history page); single-variety SPOTLIGHT profiles (Geisha, SL28, Bourbon deep-dive pages); a roast-defect
  VISUAL gallery (needs new bean SVGs - the one genuinely visual-heavy addition left); coffee-grading/defect-
  classification deep dive (green_grading exists, could go deeper on SCA green grading + defect counts).
- More origins if desired: Cuba, Dominican Republic, Haiti, Puerto Rico, Venezuela, Cote d Ivoire, Myanmar,
  Laos, Nepal, Philippines, Australia (minor/rare).
- PENDING (agreed): DIAGRAM VISUAL-POLISH PASS through all 53 diagrams by eye (esp. familytree + historytimeline
  the two densest). Kevin wants content deep-dives first, THEN polish.
- PMC track + interactive tools still deferred by direction.

---

# v31 — NON-ORIGIN DEEP DIVES: the espresso machine history + Geisha variety spotlight

Continued non-origin depth. 86 Learn pages; 55 diagrams; ~48,500 words; 123 methodology pages; ~746 KB.
Introduces a new page TYPE: a single-variety SPOTLIGHT (Geisha) - a model for future variety/origin deep-dives.

## New Learn pages (full schema + diagram + cross-links)
- **esp_history** (The Espresso Machine) [culture, 583w] - consolidates the espresso-machine story that was
  scattered across brew_machinetypes + history_timeline into a dedicated narrative. The problem (SPEED); pioneers
  (Moriondo Turin 1884 first patent/bulk; Bezzera Milan 1901 portafilter+group cup-by-cup; Pavoni La Pavoni
  ~1905 first commercial espresso; steam limit ~1.5-2 bar = bitter); REVOLUTION (Gaggia spring-lever, Cremonesi
  late 1930s/patent 1938/production 1948, 8-10 bar -> first CREMA; pulling a shot); modern (Faema E61 Ernesto
  Valente 1961 motor pump 9 bar, E61 group still made; 3rd wave La Marzocco/Synesso/Slayer PID/pre-infusion/
  pressure profiling, Decent home). Diagram: esphistory (pressure-evolution timeline w/ bar values).
- **geisha_spotlight** (Spotlight: Geisha) [grow, 643w] - the variety that changed everything. Forgotten
  Ethiopian plant (Gori Gesha forest 1930s, collected ~1936 -> Tanzania -> CATIE Costa Rica 1950s accession
  T2722 -> Panama 1960s for LEAF RUST resistance, ignored for decades); the 2004 Best of Panama moment (Peterson
  family/Hacienda La Esmeralda isolate healthy high-altitude plants, win ~94 pts, ~$21/lb ~10x rate); why it
  tastes like that (linalool+geraniol -> jasmine/bergamot/tea, ONLY at 1700-2100m + ripe pick + careful process);
  the world most expensive coffee (2017 $601/lb, 2019 broke $1,000, 2020s >$2,000/lb green, BoP tens of thousands
  $/kg; scarcity + narrative). Diagram: geishastory (journey chain + flavor/price panels).

## Diagrams (55 total): + esphistory, geishastory

## Notes
- esp_history cross-links history_timeline/brew_machinetypes/brew_espresso/waves; geisha_spotlight cross-links
  variety_tree/species_deep/origin_panama/competitions/cmarket. Ties the Geisha thread across the whole app
  (Panama origin page, the family tree, the competitions page, the C-market/pricing page). history_timeline/
  brew_machinetypes/variety_tree/species_deep/competitions got new related chips.
- All 86 Learn pages cross-linked (related=86). Search finds all (moriondo, bezzera, gaggia, faema, crema,
  geisha, esmeralda, best of panama, linalool verified). Regression ALL GREEN. Diagrams verified via cairosvg+
  pixel-region analysis; geishastory also confirmed on-screen via view.

## The SPOTLIGHT format is reusable - future single-variety (SL28, Bourbon, Caturra) or single-farm/single-topic
deep-dives can follow this template (journey + why + significance + a story diagram).

## Group counts: culture 14, brew 21, cupping 10, ops 9, green 9, grow 7, read 5, science 5, business 4,
practice 2 = 86 Learn + 36 origins + intro = 123 methodology pages, 55 diagrams, ~48,500 words.

## Still available for future depth (Kevin WILL re-run)
- Non-origin still open: MORE variety spotlights (SL28/Kenyan story, Bourbon, Pacamara, Maragogype); a roast-
  defect VISUAL gallery (needs new bean SVGs - the one genuinely visual-heavy addition left); green-grading/
  defect-classification deep dive; the moka pot / home-brewing-history; coffee & the body / caffeine science
  deep dive (health + caffeine exist, could go deeper on metabolism/adenosine/half-life).
- More origins if desired: Cuba, Dominican Republic, Haiti, Puerto Rico, Venezuela, Cote d Ivoire, Myanmar,
  Laos, Nepal, Philippines, Australia (minor/rare).
- PENDING (agreed): DIAGRAM VISUAL-POLISH PASS through all 55 diagrams by eye (esp. familytree + historytimeline
  the two densest; also review the new esphistory timeline for density). Kevin wants content deep-dives first.
- PMC track + interactive tools still deferred by direction.

---

# v32 — BIG UPDATE: roast-defect gallery + 4 variety spotlights + NAVIGATION REORG + diagram polish

Multi-part release (Kevin: "roast defect visual gallery + spotlights on all mentioned + then polish + reorganize
navigation, it is cluttered"). 91 Learn pages; 60 diagrams; ~50,300 words (crossed 50k!); 128 methodology pages;
~774 KB.

## A) Roast-defect VISUAL gallery (the one genuinely visual-heavy addition)
- **defect_gallery** (Roast Defect Gallery) [practice, 601w] - the FIRST custom-illustration page. New diagram
  diaRoastDefects draws 9 custom coffee-bean SVGs in a 3x3 grid: a bean() helper draws an ellipse body +
  center-crease S-curve + defect overlays (scorch patches on faces, burnt tips, charred side/facing, missing
  chunk/chipping, oily sheen/overdeveloped). Cells: Healthy, Scorching, Tipping, Facing, Chipping,
  Underdeveloped, Overdeveloped, Baked, Quaker - each w/ bean + name + cause + cup note. Content: reading the
  bean (color alone never tells the whole story); heat-contact burns (location = which); development color;
  the ones you only taste (baked looks normal; quakers = pale unripe, the easy one to hand-pick). Diagram:
  roastdefects. VERIFIED on-screen - beans read clearly.

## B) Four variety SPOTLIGHTS (following the Geisha template from v31)
- **spot_sl28** (Spotlight: SL28) [grow, 319w] - Scott Labs 1930s Nairobi selection, Bourbon-related; the
  BLACKCURRANT signature of Kenyan coffee; paired w/ SL34; Kenya washing-station + AA/AB grading system.
- **spot_bourbon** (Spotlight: Bourbon) [grow, 315w] - named for Bourbon/Reunion island (Yemeni coffee mutated
  ~1700s); sweet/rounded/balanced; the most PRODUCTIVE parent (Caturra/Pacas/V.Sarchi/Mundo Novo/SL/Sarchimor).
- **spot_pacamara** (Spotlight: Pacamara) [grow, 287w] - deliberate El Salvador cross (ISIC 1958, Pacas x
  Maragogipe); enormous beans + wild/savory/complex cup; Cup of Excellence favorite; cult following.
- **spot_maragogipe** (Spotlight: Maragogipe) [grow, 276w] - the ELEPHANT BEAN (largest in coffee); Typica
  mutation Brazil ~1870; soft/mild cup but the giant-bean GENE -> parent of Pacamara.
- New reusable diaVarietyCard(name,color,parent,traits,flavor,legacy) generator -> spotsl28/spotbourbon/
  spotpacamara/spotmaragogipe cards (name header + 3 panels: traits/cup/legacy). SPOTLIGHT format now well-
  established for future single-variety pages.

## C) NAVIGATION REORGANIZATION (declutter - the app had 10 flat equal-weight groups + 36 origins)
- NEW: METH_CHAPTERS structure (in build.py + injected in DATA_JSON + JS destructuring) groups the 10 areas
  into 5 journey-based CHAPTERS:
    1. The World of Coffee (culture + grow) = 25 pages
    2. From Cherry to Green (green) = 9
    3. The Craft of Roasting (read + science + practice) = 13
    4. Tasting & Quality (cupping) = 10
    5. Brewing & Business (brew + ops + business) = 34
- drawLearn() hub-view REWRITTEN: renders chapters (section header w/ accent bar, name, desc, count) -> group
  tiles nested underneath -> click tile to expand into cards (existing toggleHub behavior preserved). Flat
  cross-group SEARCH still works unchanged (typing in the Learn search bar bypasses chapters).
- New CSS: .chaplist/.chapter/.chaphead/.chapnum/.chapname/.chapdesc/.chapcount. Verified 5 chapters render,
  all 10 tiles present, expand works, no orphan pages, all 91 pages still reachable.
- Updated culture + grow group descriptions to mention the new spotlights/pages.

## D) Diagram POLISH pass (the 3 densest, flagged over prior versions)
- **familytree**: 760x270 -> 820x340. Taller, more breathing room; founders (Typica/Bourbon) now bolder/
  emphasized (strong flag); disease branch + Timor Hybrid clearly connected at bottom; Geisha set apart. Was
  the densest diagram; now clean. VERIFIED on-screen.
- **historytimeline**: 760x250 -> 820x270. Labels split to 3 tidy lines (year/title/detail) instead of cramped
  2-line wrap; better above/below spacing. VERIFIED on-screen.
- **esphistory**: 760x250 -> 820x260. Removed a leftover noop line; year/name/detail/pressure now clean &
  spaced. VERIFIED on-screen.
- (Other 57 diagrams left as-is - they were already fine. Could do a lighter cosmetic sweep later if desired.)

## Notes
- All 91 Learn pages cross-linked (related=91). Search finds all new content. Regression ALL GREEN.
- diaVarietyCard + the bean() illustration helper are both REUSABLE for future pages.
- Chapters are DATA (METH_CHAPTERS) - adding/reordering chapters or moving a group between chapters is a one-
  line edit; the hub auto-renders from it.

## Group counts: culture 14, brew 21, grow 11, cupping 10, ops 9, green 9, read 5, science 5, business 4,
practice 3 = 91 Learn + 36 origins + intro = 128 methodology pages, 60 diagrams, ~50,300 words.

## Still available for future depth (Kevin WILL re-run)
- More spotlights: Caturra, Catuai, Typica, Mundo Novo, or a Robusta spotlight; single-origin deep spotlights.
- Non-origin still open: caffeine/metabolism science deep-dive (adenosine/half-life); moka-pot / home-brew-
  history; a deeper green-grading/defect-classification page; more roast-defect bean illustrations (green-bean
  defects: black beans, sour beans, insect damage, shells/ears - could extend the bean() helper).
- More origins: Cuba, Dominican Republic, Haiti, Puerto Rico, Venezuela, Cote d Ivoire, Myanmar, Laos, Nepal,
  Philippines, Australia (minor/rare).
- FURTHER polish: a lighter cosmetic sweep of the other ~57 diagrams if desired; the chapter accent colors and
  hub visual treatment could be iterated. Navigation could gain a chapter-level landing/hero if wanted.
- PMC track + interactive tools still deferred by direction.

---

# v33 — DIAGRAM RICHER-STYLING PASS: shared visual toolkit + upgraded diagrams

Folded richer styling into diagrams worth it (Kevin: "finish the polish + fold in richer styling for those you
deem worth it + check other stuff done before"). 128 methodology pages; 60 diagrams; ~776 KB (only +2KB - the
gradient/shadow filters are tiny vector defs).

## NEW: shared richer-styling SVG toolkit (in build.py, right after wrapTspans)
Reusable primitives so diagrams read as designed, not utilitarian:
- _hex2rgb / _rgba / _cid - color helpers (rgba + stable gradient id per color).
- diaDefs(colors) - injects ONCE per SVG: a soft drop-shadow filter (#dsh), a softer one (#dsoft), and one
  vertical linear-gradient per accent color (id = g<hexcolor>). Dedupes colors.
- diaCard(x,y,w,h,color,opt) - gradient-filled rounded card w/ soft depth. opt: {title,titleColor,titleSize,r,
  shadow:false,strong}. THE workhorse - replaces flat opacity rects everywhere.
- diaChip(cx,cy,label,color,w) - small pill.
- diaHeader(x,y,w,title,sub,color) - left-accent-bar section header inside a diagram.
- diaArrowMarker(color) - soft arrowhead marker (id darr); inject via <defs>.
These are the standard for ALL future diagrams - use diaCard/diaHeader/diaDefs instead of hand-rolled rects.

## Diagrams UPGRADED to the toolkit (11 + the 4-page spotlight card = 15 pages)
- diaVarietyCard (powers spot_sl28/bourbon/pacamara/maragogipe) - gradient header w/ accent bar + 3 gradient
  panels w/ divider + dot bullets.
- diaSpeciesMap - gradient species cards + depth; "vs" now a floating badge; gradient forgotten-species strip.
- diaAromaChem - glowing gradient center ring + gradient compound-family cards + connector dots.
- diaClimateCoffee - diaHeader bars for Threat/Adapting + gradient cards.
- diaCmarket - gradient waterfall cards + shared arrow marker + highlighted price card.
- diaMachTypes - gradient boiler cards w/ depth (strong).
- diaDecafMethods - glowing green-bean + gradient method cards + connector dots.
- diaInstantCoffee - gradient spray/freeze cards + shared arrows.
- diaWaterChem - diaHeader bars for GH/KH + gradient SCA-target card w/ spec dividers.
- diaScaPath - gradient cards throughout + shared arrow marker.
- diaTeaCoffee - gradient glowing circle badges + depth.
- diaCherryByproduct - depth on the concentric cherry + ring labels + gradient product cards.

## Notes
- File size barely moved (+2KB) - gradients/shadows are tiny vector <defs>, dedupe by color. Still one self-
  contained offline file, still infinitely sharp.
- All verified: regression ALL GREEN, all 15 upgraded diagrams confirmed carrying linearGradient defs + >500
  chars content. Rendered spot-checks (spotlight card, C-market, aroma, instant, water chem, species) all look
  markedly more "designed" - gradient depth, soft shadows, cleaner headers/arrows/badges.
- The v32 polish-pass diagrams (familytree, historytimeline, esphistory) were already restructured for density;
  left as-is (could get the gradient treatment too in a future pass if desired).

## Diagrams NOT yet given the gradient toolkit (~45 older ones - roastcurve, extraction, espresso, grind,
flavorwheel, cva, processing, milk, water, roasters, waves, supplychain, blend, cherry, vartree, pourover,
coldbrew, troubleshoot, milkdrinks, decaf, coffeemap, caffeine, espmachine, tastemap, latteart, waterrecipe,
grinder, puckprep, staling, acidmap, dialring, milkstretch, maintenance, cracks, heat, dtr, phasebar,
brewfamilies, geishastory, historytimeline, esphistory, familytree, roastdefects). Many are data/curve diagrams
that already look good (roastcurve, dtr, flavorwheel, cva) and do not need cards. The boxes-and-panels ones among
them (supplychain, blend, troubleshoot, coffeemap, tastemap, geishastory) are the next candidates if Kevin wants
the toolkit applied more broadly - straightforward diaCard swaps.

## Still available (Kevin WILL re-run)
- Apply the gradient toolkit to the remaining boxes-and-panels diagrams (supplychain, blend, troubleshoot,
  coffeemap, tastemap, geishastory, brewfamilies) - easy diaCard swaps, ~same pattern as this pass.
- CONTENT deep-dives still open: caffeine/metabolism science page (adenosine/CYP1A2/half-life - I already
  researched this: ~5hr half-life, CYP1A2 metabolizes ~95%, fast AA vs slow CC metabolizers, ADORA2A anxiety
  variant, adenosine antagonism; ready to build a caffeine_science page next); moka-pot/home-brew history;
  more variety/origin spotlights.
- More origins (minor/rare): Cuba, Dominican Republic, Haiti, Puerto Rico, Venezuela, Cote d Ivoire, Myanmar,
  Laos, Nepal, Philippines, Australia.
- PMC track + interactive tools still deferred by direction.

---

# v34 — Learn expand/collapse-all button + caffeine science page + more diagram polish

Three-part round (Kevin: "polish more + more deep-dive content + add collapse/expand-all to Learn top; polish
EVERY round like the content deep-dives"). 129 methodology pages; 61 diagrams; ~50,900 words; ~788 KB.

## A) Learn EXPAND/COLLAPSE-ALL button (Kevin: "it is basically begging for that")
- Changed learnOpen from a single id (null|gid) to a Set() \u2014 groups now open INDEPENDENTLY (before, opening one
  closed the others; multi-open is a nice side-benefit).
- toggleHub() now add/deletes from the Set. New: expandAllHubs(), collapseAllHubs(), allGroupIds().
- New .learntools toolbar at top of Learn hub view (hub mode only, NOT search mode): left = "N areas · N topics"
  count; right = a smart button that shows "Expand all" (chevron-down) when not all open, flips to "Collapse all"
  (chevron-up) when all are open. onclick swaps between expandAllHubs()/collapseAllHubs().
- New CSS: .learntools/.ltcount/.ltbtn (+hover). Verified: toolbar renders, expand->all 10 open + btn flips,
  close one->btn back to Expand, collapse->0, multi-open via individual toggles works.

## B) NEW CONTENT: caffeine science deep-dive
- **caffeine_science** (The Science of Caffeine) [science, 605w] \u2014 the pharmacology the health page never went deep
  on. What caffeine does (ADENOSINE builds sleep pressure \u2192 caffeine is same-shaped, plugs A1/A2A receptors as an
  ANTAGONIST, blocks the tired signal, doesn
'
t add energy \u2014 hides fatigue); kinetics (absorbed ~45min, peaks
  ~30min-2hr, ~5hr HALF-LIFE \u2192 200mg at 3pm = 100mg at 8pm; stop 8-10hr before bed); why people differ (CYP1A2
  metabolizes ~95%, fast vs slow metabolizers 2-3hr vs 9-12hr; ADORA2A gene \u2192 caffeine anxiety; smoking halves
  half-life, pregnancy/meds lengthen); tolerance/dependence (brain grows MORE receptors \u2192 tolerance + withdrawal
  headache peaks day 1-2 gone ~1wk; real dependence not harmful addiction; tolerance breaks + delaying 1st coffee
  ~90min help). Diagram: caffeinescience (receptor-blocking mechanism on left + ~5hr half-life decay curve with
  3pm/8pm/1am markers on right; uses the new gradient toolkit). Cross-links health/tea_coffee/decaf_deep/
  chemistry. Search verified: adenosine, cyp1a2, half-life, metabolizer, withdrawal.
- Grounded in NCBI StatPearls, Biology Insights, Fuel Your DNA (CYP1A2).

## C) MORE DIAGRAM POLISH (gradient toolkit applied to 4 more)
- diaGeishaStory \u2014 gradient journey cards + shared arrow + gradient flavor/price panels (diaCard titles).
- diaSupplyChain \u2014 gradient farmer\u2192you circles + shared arrow marker.
- diaBlend \u2014 gradient component nodes + depth on the blend cup.
- diaCaffeineScience \u2014 built NEW on the toolkit from the start (gradient receptor + gradient decay area).
- Reviewed diaTroubleshoot & diaBrewFamilies: intentionally LEFT as-is (already have a gradient spectrum bar /
  custom brew-method icons respectively; cards would clutter them). Good judgment call, not an omission.

## Running toolkit adoption (gradient diaCard/diaHeader/diaDefs/diaArrowMarker)
Now upgraded (~19 diagrams): varietycard(x4 spotlights), speciesmap, aromachem, climatecoffee, cmarket,
machtypes, decafmethods, instantcoffee, waterchem, scapath, teacoffee, cherrybyproduct, geishastory,
supplychain, blend, caffeinescience. Plus v32 density-restructured: familytree, historytimeline, esphistory.

## Diagrams still on the OLD flat style (candidates for future polish rounds)
roastcurve, phasebar, dtr, cracks, heat, extraction, espresso, grind, flavorwheel, cva, processing, milk, water,
roasters, waves, cherry, vartree, pourover, coldbrew, troubleshoot(kept), milkdrinks, decaf, coffeemap, caffeine,
espmachine, tastemap, latteart, waterrecipe, grinder, puckprep, staling, acidmap, dialring, milkstretch,
maintenance, brewfamilies(kept), roastdefects. Many (roastcurve, dtr, flavorwheel, cva, curves) are data/curve
diagrams that look good already and do NOT want cards. Panel-ish ones to hit next: coffeemap, tastemap, waves,
processing, milkdrinks, espmachine, waterrecipe, acidmap, dialring, maintenance, staling.

## Group counts: culture 14, brew 21, grow 11, cupping 10, ops 9, green 9, science 6, read 5, business 4,
practice 3 = 92 Learn + 36 origins + intro = 129 methodology pages, 61 diagrams, ~50,900 words.

## Still available (Kevin WILL re-run \u2014 EVERY round: polish + content)
- POLISH: keep applying the gradient toolkit to the panel-ish diagrams listed above (easy diaCard swaps).
- CONTENT: moka-pot / home-brew-history; a fermentation/processing-innovation deep dive (anaerobic, carbonic
  maceration, honey levels); more variety spotlights (Caturra, Catua\u00ed, Typica, Robusta); more origins (Cuba,
  Dominican Republic, Haiti, Venezuela, Myanmar, Philippines, Australia, etc.); a coffee-grading/defect-classing
  deep dive; the roast-defect bean gallery could extend to green-bean defects (reuse the bean() helper).
- PMC track + interactive tools still deferred by direction.

---

# v35 — Experimental-processing + moka-pot pages + diagram polish batch

Standing round (Kevin: "keep polishing and digging"). 131 methodology pages; 63 diagrams; ~52,300 words (crossed
52k); ~808 KB. Two new content deep-dives + 6 diagrams upgraded to the gradient toolkit.

## NEW CONTENT (2 pages)
- **processing_experimental** (Experimental Processing) [green, 672w] \u2014 fermentation as the flavor lever.
  ANAEROBIC (sealed, no O2, one-way valve \u2192 heavy/winey/fruity); CARBONIC MACERATION (whole cherries in CO2, from
  Beaujolais wine \u2192 juicy red fruit; Sasa Sestic 2015 WBC); LACTIC (favors lactic-acid bacteria, 80+ hrs \u2192
  velvety/yogurt-tang); THERMAL SHOCK; HONEY LEVELS (white\u2192yellow\u2192red\u2192BLACK = more mucilage/fermentation); yeast-
  inoculation, koji; CO-FERMENTATION debate (adding fruit/spice \u2014 advocates vs "just infused" critics). Buy well:
  trustworthy lots NAME method + fermentation time; best as pour-over. Diagram: fermentmethods (5 gradient method
  cards radiating from a central cherry node \u2014 richest diagram yet, ~117k px). Grounded in Royal Coffee, Buddha
  Beans, CoffeeGeek. Search verified: anaerobic/carbonic/lactic/fermentation/honey process.
- **moka_pot** (The Moka Pot) [culture, 667w] \u2014 how espresso came home. Before: coffee was PUBLIC (big cafe-only
  machines; home = gentler Napoletana flip pot / Milanese). 1933: Alfonso Bialetti (Piedmontese aluminium maker,
  design also credited Luigi De Ponti) \u2014 inspired by a lessiveuse washing machine; fit La Pavoni-style pressure
  into an octagonal Art Deco stovetop pot (now in MoMA). Not an instant hit (~10k/yr pre-WWII); son RENATO (POW
  camp \u2192 1945) = marketing genius: billboards/radio/TV, mascot "l
'
omino coi baffi" (caricature of his father),
  slogan "in casa un espresso come al bar" \u2192 4M pots/yr, ~90% of Italian homes (Renato\u2019s ashes are in a giant
  Moka). How it works: 3 chambers, steam pressure pushes water up (gurgle = done, never recirculates), BUT ~1-2
  bar vs espresso 9 bar \u2192 NOT espresso; between espresso & strong drip. Tips: hot water start, medium-fine, no
  tamp, pull at gurgle. Diagram: mokapot (3-chamber cross-section + steam-flow arrows + moka-vs-espresso pressure
  comparison). Grounded in Wikipedia, Sunday Baker, Imbibe. Search verified: bialetti/moka/napoletana.

## DIAGRAM POLISH (6 more to the gradient toolkit this round)
- diaWaves + diaTasteMap (done earlier in this session before the two content pages).
- diaDialRing \u2014 glowing recipe center + gradient sour/bitter fix cards.
- diaCoffeeMap \u2014 gradient node halos on the journey map + shared arrow marker.
- diaMaintenance \u2014 4 gradient cadence columns (daily/weekly/monthly/periodic).
- diaWaterRecipe \u2014 gradient hardness/buffer cards + glowing target + shared arrow.
- Plus the 2 NEW diagrams (fermentmethods, mokapot) built ON the toolkit from scratch.
- Reviewed & intentionally LEFT flat (already good / cards would clutter): acidmap (bar chart), staling (curve),
  milkdrinks (custom layered cups), troubleshoot (gradient spectrum bar), brewfamilies (custom brew icons).

## Running gradient-toolkit adoption (~27 diagrams now on the rich style)
varietycard(x4), speciesmap, aromachem, climatecoffee, cmarket, machtypes, decafmethods, instantcoffee,
waterchem, scapath, teacoffee, cherrybyproduct, geishastory, supplychain, blend, caffeinescience, waves,
tastemap, dialring, coffeemap, maintenance, waterrecipe, fermentmethods, mokapot. Plus v32 density-restructured:
familytree, historytimeline, esphistory.

## Diagrams STILL on the old flat style (future polish candidates)
roastcurve, phasebar, dtr, cracks, heat, extraction, espresso, grind, flavorwheel, cva, processing, milk, water,
roasters, cherry, vartree, pourover, coldbrew, decaf, caffeine(old one), espmachine, latteart, grinder, puckprep,
acidmap(kept), milkstretch, roastdefects. Many (roastcurve/dtr/flavorwheel/cva/curves) are data diagrams that
should stay flat. Panel-ish ones to hit next: processing (seed illustrations - add gradient depth, not cards),
espmachine, grinder, puckprep, milkstretch, cherry, vartree, decaf, water, roasters, extraction, espresso.

## Group counts: brew 21, culture 15, grow 11, cupping 10, ops 9, green 10, science 6, read 5, business 4,
practice 3 = 94 Learn + 36 origins + intro = 131 methodology pages, 63 diagrams, ~52,300 words.

## Still available (Kevin WILL re-run \u2014 EVERY round: polish + content)
- POLISH: the panel-ish flat diagrams above (easy diaCard swaps); give diaProcessing gradient depth on its seeds.
- CONTENT: more variety spotlights (Caturra, Catua\u00ed, Typica, Robusta, Mundo Novo); a green-grading/defect-
  classification deep dive; extend the roast-defect bean() gallery to GREEN-bean defects (black/sour/insect/
  shells \u2014 reuse the bean() helper); more origins (Cuba, Dominican Republic, Haiti, Venezuela, Myanmar, Laos,
  Nepal, Philippines, Australia); a coffee-grinder/burr deep-dive; latte-art progression page.
- PMC track + interactive tools still deferred by direction.

---

# v36 — Green-bean defect gallery (2nd custom-illustration diagram) + more diagram polish

Standing round (Kevin: "keep polishing and digging"). 131 methodology pages; 64 diagrams; ~52,300 words; ~812 KB.
A visual companion to the roast-defect gallery + 3 more diagrams onto the gradient toolkit.

## NEW: green-bean defect VISUAL gallery (the 2nd custom-illustration diagram)
- Built diaGreenDefects \u2014 a 3x3 grid of raw (green) coffee beans with defect-specific overlays, mirroring the
  roast-defect gallery pattern but with a NEW green-bean helper (gbean()) since raw beans are blue-green not brown.
  Cells (with SCA category tags in corner \u2014 red CAT 1 / gold CAT 2 / green healthy): Healthy, Full black (CAT 1),
  Full sour (CAT 1, reddish-brown), Partial black (CAT 2), Insect damage (CAT 2, borer holes), Broken/chipped
  (CAT 2, pale inner), Immature (CAT 2, pale/thin), Shell/ear (CAT 2, hollow shape), Floater/fungus (CAT 2).
  gbean() overlays: fullblack, partblack, sour, insect (boreholes), broken (cut w/ pale inner), shell (concave
  cut), floater (faded), fungus (yellowish blotches).
- ATTACHED to the EXISTING green_grading page (Green Grading & Defects) which had NO diagram \u2014 filled its missing
  visual. Cross-linked green_grading <-> defect_gallery (roast) as companion galleries. Verified: all 9 cells
  render (~1.7-3.9k px each), category tags present.
- NOTE: like diaRoastDefects, this is a custom-illustration diagram (solid fills + overlays, NOT gradient cards)
  so it intentionally does NOT use linearGradient \u2014 that is correct, not a regression.
- The gbean() helper is now REUSABLE for any future green-bean visual.

## DIAGRAM POLISH (3 more to the gradient toolkit)
- diaGrinder \u2014 gradient conical cone + flat burr discs w/ depth; shared arrow marker.
- diaEspMachine \u2014 gradient Source/Pump/Boiler/Group stage cards (strong) + shared arrow. Verified all 4 cards
  render (~3.5-5.4k px each).
- diaPuckPrep \u2014 gradient step-number badges (1-4) w/ soft depth.
- Reviewed & LEFT flat (correctly): diaWater (quadrant data chart \u2014 cards would ruin it).

## Running gradient-toolkit adoption (~30 diagrams on the rich style)
varietycard(x4), speciesmap, aromachem, climatecoffee, cmarket, machtypes, decafmethods, instantcoffee,
waterchem, scapath, teacoffee, cherrybyproduct, geishastory, supplychain, blend, caffeinescience, waves,
tastemap, dialring, coffeemap, maintenance, waterrecipe, fermentmethods, mokapot, grinder, espmachine, puckprep.
Plus v32 density-restructured: familytree, historytimeline, esphistory. Custom-illustration (solid fills, by
design): roastdefects, greendefects.

## Diagrams STILL on the old flat style (future polish candidates)
roastcurve, phasebar, dtr, cracks, heat, extraction, espresso, grind, flavorwheel, cva, processing, milk, water
(kept), roasters, cherry, vartree, pourover, coldbrew, decaf, caffeine(old), latteart, milkstretch. Many
(roastcurve/dtr/flavorwheel/cva/curves/water-quadrant) are DATA diagrams that should stay flat. Panel/illustration
ones to hit next: processing (seed illustrations \u2014 gradient depth not cards), cherry, vartree, decaf, roasters,
extraction, espresso, milk, milkstretch, latteart, pourover, coldbrew.

## Group counts unchanged: brew 21, culture 15, grow 11, cupping 10, green 10, ops 9, science 6, read 5,
business 4, practice 3 = 94 Learn + 36 origins + intro = 131 methodology pages, 64 diagrams, ~52,300 words.
ALL 64 diagram-bearing pages verified rendering. green_grading was the last diagram-less green page \u2014 now every
green page except the pure-text ones (green_intro, green_measure, green_species, green_grades) has a visual.

## Still available (Kevin WILL re-run \u2014 EVERY round: polish + content)
- POLISH: the flat panel/illustration diagrams above (diaCard swaps or gradient depth on illustrations).
- CONTENT: variety spotlights (Caturra, Catua\u00ed, Typica, Robusta, Mundo Novo); a coffee-grinder/burr deep-dive;
  latte-art progression page; a milk-science/steaming deep-dive; more origins (Cuba, Dominican Republic, Haiti,
  Venezuela, Myanmar, Laos, Nepal, Philippines, Australia); a roast-profiling/sample-roasting deep dive.
- PMC track + interactive tools still deferred by direction.

---

# v37 — Caturra & Catuai workhorse spotlight + sample-roasting loop diagram + processing polish

Standing round (Kevin: "keep polishing and digging"). 132 methodology pages; 66 diagrams; ~52,800 words; ~824 KB.

## NEW CONTENT: the WORKHORSE variety spotlight (fills a real gap)
- **spot_workhorse** (Spotlight: Caturra & Catuai) [grow, 544w] \u2014 the app spotlighted the EXOTIC varieties
  (Geisha/SL28/Pacamara/Maragogipe) but skipped the everyday backbone. This covers the two workhorses behind most
  Latin American coffee. CATURRA: natural dwarf Bourbon mutation, Minas Gerais Brazil ~1915-18 (Guarani "small");
  compact \u2192 dense planting + easy harvest (revolutionized farming); IAC-selected from 1937; bright citric/clean/
  light-med body; the WCR yield-reference baseline; rust-susceptible. CATUAI: Caturra x Mundo Novo (IAC 1949, rel.
  1972; "very good"); ~20% higher yield, ~2x density; cherries CLING to branches (wind/rain/mechanized harvest);
  red/yellow forms; balanced choc/nut, holds dark roasts, vibrant with honey/natural at altitude. Why they matter:
  bred for PRODUCTIVITY not fame \u2014 practicality that let good coffee scale; their rust weakness drives resistant-
  hybrid breeding (Catimor etc.); Caturra also parents Catimor & Maracaturra. Diagram: spotworkhorse (lineage
  chain Bourbon->Caturra->Catuai + two gradient detail cards). Grounded in World Coffee Research, JayArr.
  Cross-links variety_tree/spot_bourbon/species_deep/origin_brazil/green_processing. Search verified: caturra/
  catuai/workhorse/mundo novo. NOTE: the spotlight set now covers both the exotic AND the everyday varieties.

## POLISH + gap-fill
- diaProfiling \u2014 NEW diagram for the previously diagram-LESS profiling page (Sample Roasting & Profiling): a
  5-node iteration LOOP (Green -> Sample roast -> Cup -> Adjust one variable -> Repeat) on a dashed oval with
  gradient nodes + shared arrows, plus a "then scale to production" gradient card. Fixes a gap AND strengthens
  the thin practice group. The practice group is now: defects (text explainer, pairs w/ gallery \u2014 no diagram by
  design), defect_gallery (roastdefects), profiling (profiling).
- diaProcessing \u2014 added gradient DEPTH to the washed/honey/natural seed illustrations (gradient fills + soft
  shadow, NOT cards \u2014 as planned for illustration-style diagrams).
- Reviewed & LEFT as-is: diaRoasters (custom roaster-machine illustrations, already good).

## Running gradient-toolkit adoption (~32 diagrams on the rich style)
varietycard(x4), speciesmap, aromachem, climatecoffee, cmarket, machtypes, decafmethods, instantcoffee,
waterchem, scapath, teacoffee, cherrybyproduct, geishastory, supplychain, blend, caffeinescience, waves,
tastemap, dialring, coffeemap, maintenance, waterrecipe, fermentmethods, mokapot, grinder, espmachine, puckprep,
processing, spotworkhorse, profiling. Plus v32 density-restructured: familytree, historytimeline, esphistory.
Custom-illustration (solid fills, by design): roastdefects, greendefects.

## Diagrams STILL flat (future polish candidates)
roastcurve, phasebar, dtr, cracks, heat, extraction, espresso, grind, flavorwheel, cva, milk, water(kept),
roasters(kept), cherry, vartree, decaf, pourover, coldbrew, latteart, milkstretch, caffeine(old). Many
(roastcurve/dtr/flavorwheel/cva/curves/water-quadrant) are DATA diagrams that should stay flat. Panel/illustration
ones to hit next: cherry, vartree, decaf, extraction, espresso, milk, milkstretch, latteart, pourover, coldbrew.

## Group counts: brew 21, culture 15, grow 12, cupping 10, green 10, ops 9, science 6, read 5, business 4,
practice 3 = 95 Learn + 36 origins + intro = 132 methodology pages, 66 diagrams, ~52,800 words.

## Still available (Kevin WILL re-run \u2014 EVERY round: polish + content)
- POLISH: the flat panel/illustration diagrams above.
- CONTENT: more variety spotlights (Typica the other founder, Mundo Novo, Robusta as a spotlight); a milk-
  steaming/microfoam SCIENCE deep-dive (milk pages exist but could go deeper on proteins/fats/temperature);
  a latte-art progression page; more origins (Cuba, Dominican Republic, Haiti, Venezuela, Myanmar, Laos, Nepal,
  Philippines, Australia); a coffee-storage/freshness deep-dive; a grind-size/distribution deep-dive.
- PMC track + interactive tools still deferred by direction.

---

# v38 — Typica spotlight (completes the two founders) + cherry & decaf diagram polish

Standing round (Kevin: "keep polishing and digging"). 133 methodology pages; 67 diagrams; ~53,400 words; ~833 KB.

## NEW CONTENT: the Typica spotlight (closes a real asymmetry)
- **spot_typica** (Spotlight: Typica) [grow, 544w] \u2014 Bourbon was spotlighted but Typica, the OTHER founding
  variety, was not. This completes the two-founders pair. Typica = THE original cultivated Arabica, the root of
  nearly the whole family tree (Bourbon/Caturra/Geisha/SL28/Mundo Novo/Maragogipe all trace back). Tall (~5m),
  bronze-tipped leaves. THE GREAT JOURNEY (chain of single plants): Ethiopia \u2192 Yemen (15-16th c.) \u2192 India ~1700
  (Baba Budan) \u2192 Java ~1696-99 (these seeds BECAME Typica) \u2192 one plant to Amsterdam 1706 \u2192 France 1714 \u2192
  Caribbean/Americas early 1700s. Until the 1940s most Central/S-American coffee was Typica. Descendants: Jamaica
  Blue Mountain, Hawaiian Kona, Maragogipe (mutation); a.k.a. Criollo/Ar\u00e1bigo/Pluma Hidalgo/Sumatra. THE BARGAIN:
  clean/elegant/sweet/refined cup BUT ~20-30% lower yield than Bourbon, tall, rust-prone \u2192 a deliberate quality-
  over-yield choice for specialty. Diagram: spottypica (6-stop journey chain + 2 gradient cards: descendants /
  the bargain). Grounded in World Coffee Research, Perfect Daily Grind, Mirus. Cross-links variety_tree/
  spot_bourbon/species_deep. Search verified: typica/blue mountain/kona/criollo/baba budan.
- The variety-spotlight SET is now 7 and covers the full arc: the two FOUNDERS (Typica + Bourbon), the everyday
  WORKHORSES (Caturra & Catuai), and the EXOTICS (Geisha, SL28, Pacamara, Maragogipe). Good place to pause on
  spotlights \u2014 the story is complete; future variety content should be different in kind (e.g. Robusta deep-dive,
  hybrid/rust-resistance story) rather than another single-variety card.

## DIAGRAM POLISH (2 illustration diagrams given gradient depth)
- diaCherry \u2014 gradient fills + soft outer shadow + subtle top-light highlights on the fruit layers (volume on the
  concentric cross-section), gradient on the seeds. Illustration-style depth, NOT cards.
- diaDecaf \u2014 gradient method circles (Solvent/Swiss Water/CO2) with soft depth.

## Running gradient-toolkit adoption (~35 diagrams on the rich style)
varietycard(x4), speciesmap, aromachem, climatecoffee, cmarket, machtypes, decafmethods, instantcoffee,
waterchem, scapath, teacoffee, cherrybyproduct, geishastory, supplychain, blend, caffeinescience, waves,
tastemap, dialring, coffeemap, maintenance, waterrecipe, fermentmethods, mokapot, grinder, espmachine, puckprep,
processing, spotworkhorse, profiling, spottypica, cherry, decaf. Plus v32 density-restructured: familytree,
historytimeline, esphistory. Custom-illustration (solid fills, by design): roastdefects, greendefects.

## Diagrams STILL flat (future polish candidates)
roastcurve, phasebar, dtr, cracks, heat, extraction, espresso, grind, flavorwheel, cva, milk, water(kept),
roasters(kept), vartree, pourover, coldbrew, latteart, milkstretch, caffeine(old). Many (roastcurve/dtr/
flavorwheel/cva/curves/water-quadrant) are DATA diagrams that should stay flat. Panel/illustration ones to hit
next: vartree, extraction, espresso, milk, milkstretch, latteart, pourover, coldbrew.

## Group counts: brew 21, culture 15, grow 13, cupping 10, green 10, ops 9, science 6, read 5, business 4,
practice 3 = 96 Learn + 36 origins + intro = 133 methodology pages, 67 diagrams, ~53,400 words.

## Still available (Kevin WILL re-run \u2014 EVERY round: polish + content)
- POLISH: the flat panel/illustration diagrams above (vartree, extraction, espresso, milk, milkstretch, latteart,
  pourover, coldbrew).
- CONTENT (be deliberate \u2014 add where there is a REAL gap, not another spotlight): a Robusta deep-dive (as a
  serious species, not a footnote); a milk-steaming/microfoam SCIENCE deep-dive; a latte-art progression page;
  a coffee-storage/freshness deep-dive; a grind-size/distribution deep-dive; more origins (Cuba, Dominican
  Republic, Haiti, Venezuela, Myanmar, Laos, Nepal, Philippines, Australia).
- PMC track + interactive tools still deferred by direction.

---

# v39 — Fine Robusta deep-dive (content shifts OFF variety spotlights) + pourover/coldbrew polish

Standing round (Kevin: "keep polishing and digging"). 134 methodology pages; 68 diagrams; ~54,000 words; ~842 KB.
Deliberately moved the content dig AWAY from variety spotlights (that set is complete at 7) to something
different in kind \u2014 a species deep-dive with a live modern story.

## NEW CONTENT: The Rise of Fine Robusta (a genuinely new direction)
- **fine_robusta** (The Rise of Fine Robusta) [science, 585w] \u2014 distinct from the existing Arabica-vs-Robusta
  COMPARISON pages (species_deep, green_species). This is a forward-looking deep-dive on Robusta (Coffea
  canephora) as a species in its own right and its rehabilitation. From footnote to force: ~25% -> ~40% of world
  production in 30 yrs (a huge share of ALL demand growth; fastest-growing/youngest markets drink robusta). Why
  the industry flipped: (1) CLIMATE+COST \u2014 Arabica delicate & pricey (>$4/lb early 2025), robusta grows low/hot,
  rust-resistant, higher yield \u2192 climate insurance; premium roasters now blend up to ~30%. (2) QUALITY MOVEMENT \u2014
  Vietnam (the giant), Uganda, India, Brazil applying specialty processing. Fine-robusta flavor: the "bitter" rap
  came from badly-grown lots; done well = dark choc/nut/savory + heavy velvety body; built-in ~2.2-2.7% caffeine
  (~2x Arabica) + thick persistent CREMA (why Italian espresso blends lean on it). Frame as its OWN category, not
  a cheap substitute. Grading: SCA/Q were Arabica-only \u2014 now CQI Fine Robusta protocol + Q Robusta cert; WCR
  published a robusta-variety catalog & breeds for cup quality; possible shortages of tens of millions of bags by
  2040. Diagram: robustarise (25%->40% growth bars + climate/quality driver cards + fine-robusta reframe strip).
  Grounded in World Coffee Research, Perfect Daily Grind, Coffee Intelligence (all 2024-25 sources). Cross-links
  species_deep/green_species/climate_coffee/cmarket/blending. Search verified: robusta/canephora/fine robusta/
  crema/q robusta/vietnam.

## DIAGRAM POLISH (2 more illustration diagrams)
- diaPourover \u2014 gradient glowing step-number badges (1-4) with soft depth on the cone sequence.
- diaColdBrew \u2014 gradient hot/cold circle badges + shared arrow marker.

## Running gradient-toolkit adoption (~37 diagrams on the rich style)
Adds robustarise, pourover, coldbrew this round. Full list in prior changelogs. Plus v32 density-restructured:
familytree, historytimeline, esphistory. Custom-illustration (solid fills, by design): roastdefects, greendefects.

## Diagrams STILL flat (future polish candidates)
roastcurve, phasebar, dtr, cracks, heat, extraction, espresso, grind, flavorwheel, cva, milk, water(kept),
roasters(kept), vartree, latteart, milkstretch, caffeine(old). Many (roastcurve/dtr/flavorwheel/cva/curves/
water-quadrant) are DATA diagrams that should stay flat. Panel/illustration ones to hit next: vartree,
extraction, espresso, milk, milkstretch, latteart.

## Group counts: brew 21, culture 15, grow 13, cupping 10, green 10, ops 9, science 7, read 5, business 4,
practice 3 = 97 Learn + 36 origins + intro = 134 methodology pages, 68 diagrams, ~54,000 words.

## Still available (Kevin WILL re-run \u2014 EVERY round: polish + content)
- POLISH: vartree, extraction, espresso, milk, milkstretch, latteart (flat illustration/panel diagrams).
- CONTENT (keep it different in kind, real gaps only): a milk-steaming/microfoam SCIENCE deep-dive; a latte-art
  progression page; a coffee-storage/freshness deep-dive; a grind-size/distribution deep-dive; a water-for-coffee
  practical recipe deep-dive; more origins (Cuba, Dominican Republic, Haiti, Venezuela, Myanmar, Laos, Nepal,
  Philippines, Australia).
- PMC track + interactive tools still deferred by direction.

---

# v40 — Back-button scroll restore (UX fix) + grind particle-science deep-dive + no new flat polish debt

Standing round (Kevin: "keep polishing and deep diving; how far can we take this") + a specific UX request:
back button should return to the SAME SCROLL SPOT, not jump to top. 135 methodology pages; 69 diagrams;
~54,600 words; ~853 KB. Milestone: v40.

## UX FIX: back-button scroll-position memory (Kevin: "annoying to rescroll every time")
- Added a scrollMemo map + viewKey(state) helper in the router. go(view,arg,restore):
  * On EVERY navigation, saves the scroll position of the view being LEFT (scrollMemo[viewKey(prev)] = scrollY).
  * Forward nav (go) scrolls to top (y=0). BACK nav (goBack = go with restore=true) restores the saved position.
  * Uses double-requestAnimationFrame so restore happens AFTER layout (reliable on mobile); falls back to
    setTimeout if rAF is unavailable (defensive \u2014 also keeps the jsdom harness working).
- New goBack(view,arg) wrapper; the 4 sticky back buttons (All profiles / All origins / All topics / meth backView)
  now call goBack() instead of go(). Detail-page back \u2192 list now lands exactly where you were.
- Learn groups stay expanded on back (learnOpen is a persistent Set), so the restored scroll position still lines
  up with the same content. Verified end-to-end in jsdom: forward=top, back=exact prior Y (learn 900/1200,
  origins 800, profiles 650), groups still expanded, fresh forward still tops.
- NOTE for future: this is scroll memory within the SPA state, not browser history; the phone back-gesture still
  does browser back. If Kevin ever wants the hardware/gesture back to also restore, wire pushState + popstate to
  goBack \u2014 logged as a future option.

## NEW CONTENT: The Science of Particle Size (a genuinely new, deeper cut)
- **grind_science** (The Science of Particle Size) [science, 608w] \u2014 distinct from the equipment-focused
  brew_grind/brew_grinder pages; this is the PARTICLE-DISTRIBUTION science. Grind size is really a DISTRIBUTION
  (shape matters as much as the average median micron). FINES (~50\u00b5m dust, huge surface area \u2192 over-extract fast
  = bitter, clog espresso) vs BOULDERS (chunks water can\u2019t penetrate \u2192 under-extract = sour) \u2014 a wide spread has
  BOTH \u2192 why bad grind tastes bitter AND sour at once. UNIMODAL (flat burr, one tight peak, clarity) vs BIMODAL
  (conical, main peak + fines spike, body) \u2014 strong tendencies not laws; blade = chaotic worst case. What to do:
  a good BURR grinder is the highest-leverage buy; match spread to method (espresso fine+tight, pour-over slightly
  broader, French press coarse+uniform); keep burrs clean+ALIGNED; bitter+sour = fix the DISTRIBUTION not just the
  average. Diagram: particlesize (a real data-viz \u2014 overlaid unimodal vs bimodal gaussian curves with FINES /
  BOULDERS zones marked + over/under-extract consequences). Grounded in Mahlk\u00f6nig, Coffee ad Astra, Nature Sci
  Reports. Cross-links brew_grind/brew_grinder/brew_extraction/brew_dialing/brew_troubleshoot. Search verified:
  grind/fines/boulders/bimodal/distribution/unimodal.

## POLISH note
- No new diagram polish this round \u2014 the round budget went to the (larger) scroll-fix + a data-viz diagram built
  rich from scratch. Remaining flat diagrams to polish next: vartree, extraction, espresso, milk, milkstretch,
  latteart (all illustration/panel; the data/curve ones stay flat by design). Not a regression \u2014 just where the
  effort landed this round.

## Group counts: brew 21, culture 15, grow 13, cupping 10, green 10, science 8, read 5, business 4, practice 3
= 98 Learn + 36 origins + intro = 135 methodology pages, 69 diagrams, ~54,600 words.

## Still available (Kevin WILL re-run \u2014 EVERY round: polish + content)
- POLISH: vartree, extraction, espresso, milk, milkstretch, latteart (flat illustration/panel diagrams).
- CONTENT (different in kind, real gaps only): a coffee-storage/freshness-at-home deep-dive; a water-for-coffee
  practical recipe deep-dive; a latte-art progression page; the rust/leaf-disease + resistant-hybrid breeding
  story; more origins (Cuba, Dominican Republic, Haiti, Venezuela, Myanmar, Laos, Nepal, Philippines, Australia).
- OPTIONAL UX: wire browser history (pushState/popstate) so the phone back-gesture also restores scroll.
- PMC track + interactive tools still deferred by direction.

---

# v41 — Coffee Leaf Rust deep-dive (ties many threads) + proper diagram-polish pass (espresso, vartree)

Standing round (Kevin: "dig and polish :)" \u2014 explicitly wanted the polish turn I owed from v40). 136 methodology
pages; 70 diagrams; ~55,200 words; ~863 KB. Crossed 55k words / 70 diagrams.

## NEW CONTENT: Coffee Leaf Rust (finally explains a thread referenced app-wide)
- **leaf_rust** (Coffee Leaf Rust) [science, 656w] \u2014 rust is referenced all over the app (Typica rust-prone,
  Caturra/Catuai susceptible, Robusta resistant, climate spreading it) but never explained. This is the dedicated
  deep-dive, distinct from the survey-level "threats" page (which touches rust among pests+climate). The fungus
  Hemileia vastatrix ("la roya"): orange spores under leaves \u2192 early leaf drop \u2192 tree starves; obligate parasite,
  spreads wind/rain + on tools, germinates ~13\u201331\u00b0C (warming = new ground). 1869 CEYLON: first big epidemic \u2014
  devastated the island, planters gave up & replanted TEA \u2192 why Sri Lanka & the British Empire went coffee\u2192tea
  (starkest case of a disease redrawing a commodity map); spread to nearly every region 1869\u20131985 (Hawaii held to
  2020). 2012 THE BIG RUST: industry thought it was managed, then severe epidemic in C.America/Colombia/Peru/
  Ecuador, up to 35% yield loss, food-security impact; causes = warm/wet (climate) + post-2008-crash under-
  fertilizing + maybe new races. THE RED QUEEN: best weapon = genetic resistance; lucky break = H\u00edbrido de Timor
  (natural Arabica\u00d7Robusta w/ Robusta rust-resistance) \u2192 CIFC crossed w/ Caturra/Villa Sarchi \u2192 CATIMORS &
  SARCHIMORS; BUT fungus evolves new virulence races that break resistance \u2192 must re-breed forever (permanent arms
  race, worse w/ climate). Diagram: ruststory (history timeline 1861\u21921869\u21921985\u21922012 + fungus fact strip + a
  "breed resistance VS fungus evolves" two-card arms-race). Grounded in Talhinhas/Molecular Plant Pathology,
  McCook/Phytopathology (Big Rust & Red Queen), Wikipedia. Cross-links threats/climate_coffee/fine_robusta/
  variety_tree/spot_workhorse. Search verified: leaf rust/hemileia/la roya/ceylon/catimor/timor hybrid/red queen.
- This page now ties together the workhorse, Typica, Robusta, and climate pages into one coherent thread.

## DIAGRAM POLISH (the turn owed from v40 \u2014 3 diagrams)
- diaEspresso \u2014 gradient portafilter + cup shapes w/ soft depth, light text (was dark-on-flat), shared arrow.
- diaVarTree (used by the varietals page) \u2014 rebuilt the node() helper to use diaCard gradient fills + light text
  (was flat opacity fills w/ hard-to-read dark text). Big readability win on the family tree.
- diaRustStory \u2014 new, built rich on the toolkit from scratch.
- Left diaExtraction as-is (its 3-band spectrum bar already reads well; gradient depth optional later).
- NOTE: the variety_tree PAGE uses the separate familytree diagram (already density-done in v32); the varietals
  PAGE uses vartree \u2014 that is the one upgraded here. (Regression key gotcha logged.)

## Running gradient-toolkit adoption (~40 diagrams). Custom-illustration (solid, by design): roastdefects,
greendefects. Data/curve diagrams intentionally flat: roastcurve, dtr, flavorwheel, cva, phasebar, water-quadrant,
acidmap, staling, extraction(spectrum).

## Diagrams STILL flat & polish-able next: milk, milkstretch, latteart, milkdrinks(custom-ish), heat, cracks,
grind(bar). Most remaining flats are data/curve (leave) or already-custom. The illustration ones left are mainly
the milk/latte-art cluster.

## Group counts: brew 21, culture 15, grow 13, cupping 10, green 10, science 9, read 5, business 4, practice 3
= 99 Learn + 36 origins + intro = 136 methodology pages, 70 diagrams, ~55,200 words.

## Still available (Kevin WILL re-run \u2014 EVERY round: polish + content, ONLY if it still makes sense)
- POLISH: milk, milkstretch, latteart (the remaining illustration cluster).
- CONTENT (different in kind, real gaps only): coffee-storage/freshness-at-home; a latte-art progression page;
  the coffee-borer-beetle / other-pests companion to rust; more origins (Cuba, Dominican Republic, Haiti,
  Venezuela, Myanmar, Laos, Nepal, Philippines, Australia). Kevin flagged: only keep digging if it genuinely adds
  \u2014 avoid padding. We are near the point where new PAGES should be rarer & each must earn its place; polish +
  occasional high-value pages is the right cadence now.
- OPTIONAL UX: wire pushState/popstate so the phone back-GESTURE also restores scroll (in-app back already does).
- Bigger swings if wanted: the deferred interactive tools (brew calc, roast timer, cupping form) or the PMC track.

---

# v42 — BUGFIX: origin pin/label overlap (all 36 origins) + Coffee Berry Borer deep-dive + region-map polish

Standing round (Kevin: "push polish + depth until it is no longer worth it; then we move to apps") + a reported
bug (screenshot): the location PIN overlapped the "GROWING REGIONS" label on EVERY origin page. 137 methodology
pages; 71 diagrams; ~55,800 words; ~873 KB. Milestone: 100 Learn pages.

## BUGFIX: pin overlapping GROWING REGIONS label (originRegionMap, hit all 36 origins)
- Root cause: pin was at translate(22,20) and is 24px tall (y=20\u201344); the GROWING REGIONS label was at x=22,y=46
  \u2014 directly under/overlapping the pin bottom (pin spans x=21\u201339, label started x=22).
- Fix: pin nudged to translate(22,14) so it centers on the two-line name+label block; the GROWING REGIONS label
  moved to x=50 (indented to align UNDER the country name, past the pin). Verified with pixel analysis: 0 non-bg
  px under the pin at the label row (was overlapping), label text renders clean to the right. Fixes ALL 36 origins
  at once (shared function). Regression: region maps ok=36/36.

## POLISH: region-map header (every origin page)
- Added diaDefs([accent]) gradient + soft shadow on the pin + gradient halo on the region dots (subtle depth).
  Consistent with the toolkit; applies across all 36 origin pages.

## NEW CONTENT: The Coffee Berry Borer (companion to the rust page; connects to caffeine page)
- **coffee_borer** (The Coffee Berry Borer) [science, 606w] \u2014 the most destructive INSECT pest (rust = worst
  disease; deliberate pairing). Hypothenemus hampei / "la broca": tiny black beetle (female ~1.4\u20131.8mm), native
  Africa, now nearly everywhere; up to 80% yield loss, >$500M/yr, ~20M smallholder farms. Lives INSIDE the bean
  (female bores in at the tip, tunnels the seed, lays eggs, larvae eat from inside \u2192 the "insect damage" grading
  defect + mould entry) \u2192 sprays fail; control = trapping, sanitation (strip leftover cherries), biocontrol fungus
  Beauveria bassiana. THE MARVEL: caffeine is the plant\u2019s natural pesticide (toxic to almost all insects at bean
  levels) but the borer beats it via GUT BACTERIA (Pseudomonas) that break caffeine down & eat it (C+N); proven
  2015 by killing the microbes \u2192 beetle can\u2019t detox; borers from 7 countries share the caffeine-eating flora. Ties
  rust+borer as coffee\u2019s two great enemies, both worsened by climate. Diagram: borerstory (cherry cross-section w/
  beetle boring in + tunnel on the left; the caffeine\u2192gut-bacteria\u2192disarm 3-step on the right). Grounded in Nature
  Communications, PMC review, Wikipedia. Cross-links leaf_rust/threats/caffeine_science/climate_coffee/
  green_grading. Search verified: borer/broca/hypothenemus/gut bacteria/pseudomonas/beauveria.
- WHY this one earns its place (per Kevin\u2019s no-padding bar): it is a genuine gap (only survey-level before), it is
  the natural COMPANION to the v41 rust page (disease + pest = the two enemies), and it CONNECTS back to the
  caffeine-science page (caffeine as pesticide) \u2014 it makes the app cohere, not just grow.

## Milestone + honest scope read
- 100 Learn pages, 36 origins, 71 diagrams, ~55,800 words. The science group is now notably strong on the
  agronomy/threats/biology axis (rust, borer, caffeine, climate, fine-robusta, particle-size).
- Remaining GENUINE content gaps are now few: a latte-art progression page (skill, not yet covered as progression);
  possibly a water-quality-troubleshooting or a cupping-calibration practical. Most other ideas would overlap.
  We are close to the point where NEW pages should be rare; polish + the occasional real gap is the right cadence,
  and after that the higher-value move is the deferred INTERACTIVE TOOLS (brew calc, roast timer, cupping form) or
  the PMC track \u2014 i.e., turning great reference INTO applications, which is exactly Kevin\u2019s stated next phase.

## Still-flat diagrams to polish next: milk, milkstretch, latteart (the milk/latte cluster) + heat, cracks.

## Group counts: brew 21, culture 15, grow 13, cupping 10, green 10, science 10, read 5, business 4, practice 3
= 100 Learn + 36 origins + intro = 137 methodology pages, 71 diagrams, ~55,800 words.

---

# v43 — Country silhouettes in origin region-maps (Kevin request) + extraction-theory deep-expansion

Standing round (Kevin: "dig and polish") + a feature request: fill the empty lower-right of the origin region-map
banner with an outline of the actual country. 137 methodology pages; 71 diagrams; ~56,200 words; ~880 KB.

## FEATURE (Kevin request): country silhouette watermark in region-map cards
- Added COUNTRY_SIL map (build.py, just before originRegionMap): simplified, recognizable country-outline SVG
  paths normalized to a ~100x100 box. Rendered faintly (opacity 0.13, accent-colored, aria-hidden) anchored in the
  lower-right empty space of the region-map card, sized to fit the region-list band, behind the text.
- 31 of 36 origins have a silhouette. The 5 without are island/sub-regions where a country outline would be
  unrecognizable or wrong at this size (Java, Sulawesi, Bali, Flores, Hawaii) \u2014 those render NOTHING (graceful, no
  fake blob). Note the OLD unused rm.shape field was a generic 8-point placeholder blob (identical across
  countries) \u2014 NOT used; COUNTRY_SIL is the real thing.
- HONEST scope caveat: these are STYLIZED simplified silhouettes (recognizable proportions \u2014 Brazil bulk+taper,
  India subcontinent point, Vietnam thin S, etc.), not survey-accurate GeoJSON outlines. They read as "this
  country" as a subtle watermark, which is the intent. If Kevin ever wants geographically-accurate outlines,
  that would mean bundling real (even simplified) GeoJSON per country \u2014 bigger + heavier; logged as an option.
- Verified: 31/36 render the silhouette; all 36 region maps still render; no-silhouette origins (java) still fine.

## DIG: deep-expanded the Extraction Theory page (chose depth over a redundant new page)
- Considered a latte-art progression page \u2014 REJECTED as padding (brew_latteart already covers the moves +
  patterns + fixes). Per Kevin\u2019s no-padding bar, dug into a THIN FOUNDATIONAL page instead.
- **brew_extraction** (Extraction Theory): 269w \u2192 608w (the most fundamental brewing concept was one of the
  thinnest). Added 2 substantive sections + 2 keypoints: (1) "Why flavors come out in order" \u2014 the SOLUBILITY
  SEQUENCE: acids/salts dissolve first (sour), sugars/sweetness in the middle (the heart), bitter compounds +
  astringent polyphenols last (bitter) \u2192 explains WHY the 18\u201322% window works and why the same coffee tastes
  sour/sweet/bitter by how far you take it. (2) "Extraction vs strength: two different dials" \u2014 the #1 brewing
  confusion: extraction yield (how MUCH, quality axis, 4 levers) vs strength/TDS (how CONCENTRATED, preference
  axis, brew RATIO) \u2192 weak-but-bitter or strong-but-sour possible; the Brewing Control Chart grids the two. This
  strengthens a page that underpins grind/dialing/troubleshooting. Search verified: solubility, brewing control
  chart, strength, extraction yield.

## Scope read (unchanged from v42, reinforced)
- 100 Learn pages / 36 origins / 71 diagrams / ~56,200 words. Genuinely near the ceiling for NEW reference pages.
- This round deliberately chose polish (silhouettes) + DEEPENING an existing thin page over a new page \u2014 that is
  the right cadence now. Remaining honest moves: finish diagram polish (milk/milkstretch/latteart cluster), deepen
  a few more thin foundational pages if warranted, then TURN TO APPLICATIONS (interactive tools: brew-ratio calc,
  roast timer, cupping form) \u2014 Kevin\u2019s stated next phase, and where the real new value is once reference is this
  complete.

## Group counts unchanged: 100 Learn + 36 origins + intro = 137 methodology pages, 71 diagrams, ~56,200 words.

---

# v44 — Island silhouettes (all 36 origins now covered) + kanji-stroke-order latte-art diagram + advanced latte-art content

Standing round (Kevin: two specific requests + keep polishing/deepening). 137 methodology pages; ~56,400 words;
~889 KB. Silhouettes now on ALL 36 origins; latte-art page deepened + a new step-by-step pour diagram.

## REQUEST 1: silhouettes for the 5 island origins (Kevin: "try to put something there")
- Added simplified island silhouettes to COUNTRY_SIL for the 5 that lacked one \u2014 kept the SAME vector style as the
  country outlines (Kevin noted switching methods might look weird alongside the others; agreed, so same method).
  Java = long thin horizontal sliver; Sulawesi (Toraja) = the distinctive tall 4-armed/orchid shape; Bali
  (Kintamani) & Flores (Bajawa) = small elongated islands; Hawaii (Kona) = a multi-PATH island CHAIN (4 separate
  island blobs in one path). Keyed by full display name so the lookup (m.country||m.name) hits them.
- Result: silhouettes now render on 36/36 origins (verified). Island shapes confirmed via pixel proportions
  (Sulawesi tall/irregular, Hawaii wide chain, Java thin horizontal). Same faint 0.13-opacity accent watermark
  in the lower-right. Still STYLIZED (recognizable, not survey-accurate) \u2014 consistent caveat with the countries.

## REQUEST 2: latte-art advanced techniques + kanji-stroke-order diagram (Kevin\u2019s idea)
- **brew_latteart** deepened 473w \u2192 671w: added "Beyond the basics" section \u2014 STACKING (multi-pulse pours \u2192
  6-stack tulips, wave-hearts; needs clean flow start/stop), ROSETTA variations (wider/more leaves, inverted),
  ETCHING & free-pour hybrids (drag a tool/thin stream for swan antennae, cat whiskers), slow-pour & 3D foam \u2014
  framed as "extreme control of the SAME two moves (sink+surface)", still needs microfoam + crema. +1 keypoint.
- NEW diagram diaPourStroke (Kevin\u2019s kanji-stroke-order idea): each of the 3 foundational patterns (Heart,
  Rosetta, Tulip) shown as a ROW of 4 numbered movement STEPS, left\u2192right, like teaching kanji stroke order.
  Each step = a top-down cup with the milk pattern at THAT stage + directional pour ARROWS (white = pour path,
  dashed red = the cut/pull-through move) + a numbered badge + a short caption. Heart: pour high\u2192drop low disc\u2192
  fill\u2192cut through. Rosetta: base\u2192wiggle side-to-side\u2192leaves stack\u2192draw through. Tulip: push blob\u2192stop+push
  behind\u2192stack\u2192pull through. SWAPPED the latteart page from the old static "latteart" diagram to this "pourstroke"
  one (so diagram COUNT stays 71 \u2014 same page, better diagram; not a regression). Verified: all 3 rows + 4 step
  cols populated, evolving white milk patterns present, finished heart shape renders.

## Diagram-count note (for future regressions)
- Learn pages with a diagram = 71 (UNCHANGED) because pourstroke REPLACED latteart on the same page rather than
  filling a diagram-less page. diaPourStroke is the 66th hand-built diagram FUNCTION though. If a regression
  asserts a diagram-count floor, use >=71, not >=72.

## Scope read (reinforced; Kevin wants reference 100% DONE before apps)
- 100 Learn / 36 origins / 71 diagram-bearing pages / ~56,400 words. Both of this round\u2019s asks are done.
- Remaining polish-and-deepen candidates (the honest, non-padding list):
  * DIAGRAM POLISH: the milk cluster is the last flat illustration set \u2014 milk (brew_milk) + milkstretch
    (brew_milkscience). After that, remaining flats are data/curve diagrams that SHOULD stay flat.
  * DEEPEN thin foundational pages (shortest now, post-extraction-expansion): ops_bbp 260w, cracks 270w,
    spot_maragogipe 276w, green_species 277w, brew_methods 279w, cva_overview 283w, brew_espresso 284w,
    ops_degassing 285w, biz_cafe 286w, spot_pacamara 287w, harvest 293w. Deepen where it genuinely adds.
  * Then: TURN TO APPLICATIONS (brew-ratio calc, roast timer, cupping form) \u2014 Kevin\u2019s stated next phase.
- Kevin explicitly OK\u2019d stopping polish or deepening when it\u2019s at an appropriate point. Getting close: after the
  milk-diagram polish + a couple more thin-page deepenings, reference is defensibly "100% done".

## Group counts unchanged: 100 Learn + 36 origins + intro = 137 pages, 71 diagram-bearing, ~56,400 words.

---

# v45 — Milk diagram cluster polished (the last flat illustrations) + cracks page deepened + dup-section bugfix

Standing round (Kevin: "polish and deepen the remaining items"). 137 methodology pages; 71 diagram-bearing;
~56,500 words; ~891 KB. This finishes the diagram-polish pass \u2014 the milk cluster was the last flat set.

## POLISH: the milk diagram cluster (the LAST flat illustration diagrams)
- diaMilk (steaming temperature track) \u2014 gradient depth on the STRETCH/TEXTURE zone bands + soft shadow.
- diaMilkDrinks (the 5 drink cross-sections: macchiato\u2192latte) \u2014 gradient fills on espresso/milk layers + a subtle
  top-highlight on the foam + soft cup depth. Verified render (5 cups, ~16k px in the band).
- diaMilkStretch (the 2-phase stretch/texture pitchers) \u2014 gradient milk + soft pitcher depth + switched its two
  local ad-hoc arrow markers (ams/ams2) to the shared darr marker (kept the white spin-marker ams).
- With this, the gradient-toolkit adoption is effectively COMPLETE for illustration/panel diagrams. What remains
  flat is BY DESIGN: data/curve diagrams (roastcurve, dtr, ror, flavorwheel, cva, phasebar, water-quadrant,
  acidmap, staling, extraction-spectrum) which should stay flat, and the 2 custom-illustration galleries
  (roastdefects, greendefects). Diagram polish is DONE \u2014 no more flat illustrations worth converting.

## DEEPEN + BUGFIX: the First & Second Crack page
- Found & FIXED a duplicate section: cracks had BOTH "Reading them by ear" (short) and "Reading the cracks by
  ear" (fuller) \u2014 near-duplicates. Removed the shorter one.
- Deepened 270w \u2192 417w: added "What the cracks actually are" \u2014 the two cracks are physically DIFFERENT events.
  1st crack = steam+CO2 rupture, bean ~doubles in size, roughly coincides with the roast turning EXOTHERMIC (bean
  releases its own heat \u2192 can run away \u2192 ease heat after). 2nd crack = brittle cell walls fracture + oils pushed to
  the SURFACE (dark-roast sheen); past it you taste roast/carbon not coffee, and taken far enough the bean can
  literally catch fire. +3 keypoints. This is a load-bearing roasting page (feeds curve/RoR/phases/profiling).

## SCOPE READ \u2014 reference is now defensibly "100% done" (Kevin\u2019s bar to move to apps)
- 100 Learn / 36 origins (all w/ silhouettes) / 71 diagram-bearing pages / ~56,500 words.
- BOTH standing threads have reached their honest stopping point, and I said I\u2019d flag this:
  * DIAGRAM POLISH: DONE. Every illustration/panel diagram is on the gradient toolkit; the rest are data diagrams
    that should stay flat or the 2 intentional custom galleries. Converting more would make them WORSE.
  * DEEPENING: the worst thin spots + the one duplicate-section bug are handled. Remaining short pages (ops_bbp
    260w, brew_methods 279w, cva_overview 283w, brew_espresso 284w, the two shorter spotlights) are short because
    they are appropriately SCOPED \u2014 forcing them longer would be padding, which Kevin explicitly rejected. A
    couple could take a light pass later if a real gap surfaces, but none NEEDS it.
- RECOMMENDATION: the reference material is complete. The right next move is the APPLICATIONS phase Kevin named \u2014
  interactive tools built ON this reference: brew-ratio calculator, roast timer, cupping/CVA form, maybe a
  dial-in troubleshooter. That is where new value now lives. (Anthropic-API-in-artifacts is available if we want
  AI-assisted tools; otherwise pure-JS tools fit the self-contained-PWA architecture cleanly.)

## Group counts unchanged: 100 Learn + 36 origins + intro = 137 pages, 71 diagram-bearing, ~56,500 words.

---

# v46 — Diagram clipping/centering audit + fixes (Kevin: systematic check for cut-off/off-center content)

Kevin asked for one last polish pass specifically hunting mis-centered or CUT-OFF content in graphs/charts (he saw
a few while scanning, like the earlier pin bug). Built an automated overflow detector (parse each diagram\u2019s
viewBox, scan every coord + estimate text extents, then render to PNG and measure edge-band pixels). 137 pages;
71 diagram-bearing; ~56,500 words; ~891 KB.

## REAL BUGS FOUND + FIXED
- **profiling (Sample-Roasting loop) \u2014 the badge-number bug (worst one):** step numbers 1\u20135 rendered WAY off-screen
  (y="374","984","1964"...). Cause: `p[1].toFixed(0)+4` \u2014 .toFixed returns a STRING, so "37"+4 = "374" (string
  concat, not addition). Fixed to `(p[1]+4).toFixed(0)`. ALSO recentered the loop (cx 250\u2192264, rx 200\u2192178,
  cy 125\u2192128) so the outer node LABELS (Repeat/converge/target on the left, etc.) stop spilling past the left/top
  edges. Now all coords in-bounds.
- **espresso (1:2 ratio):** caption sat at y=150 = exact viewBox bottom \u2192 clipped. Bumped H 150\u2192172.
- **dtr (Development Time Ratio):** caption at y=168 with H=170 \u2192 descenders clipped. Bumped H 170\u2192188.
- **phasebar (roast phases):** the one-line caption (~118 chars @ fs12) overflowed the right edge by ~7px. Split
  into TWO lines. Now fits.

## CHECKED \u2014 NOT bugs (verified false positives from the text-width heuristic / cosmetic)
- water "Alkalinity" label flagged at x=-52: it is a ROTATED (-90\u00b0) axis label \u2014 correctly placed vertically.
- greendefects / robustarise RIGHT=12px: just the soft drop-shadow filter (dsoft) bleeding a few px past a card
  edge \u2014 no actual content cut off; looks intentional. Confirmed via markup scan (nothing past x=749).
- speciesmap / caffeinescience / particlesize / milk long captions: within frame; heuristic over-estimated width.

## FINAL SWEEP RESULT
- Automated edge-pixel scan across ALL 69 renderable diagrams: 69/69 OK, ZERO real edge clips (threshold set to
  ignore faint shadow bleed).
- Hard out-of-bounds coordinate scan (any x/y/cx/cy > bound+40 or < -40): NONE. All diagrams sit within frame.
- Full regression ALL GREEN (100 learn, 71 diagram-bearing, 36 origins + silhouettes, profiling y in-bounds).
- Reusable tooling note: the overflow detector (viewBox parse + text-extent estimate + cairosvg render +
  edge-band pixel count) is the way to re-audit if new diagrams are added. Text-extent heuristic over-flags long
  centered captions \u2014 always confirm with the render/pixel step before "fixing".

## Group counts unchanged: 100 Learn + 36 origins + intro = 137 pages, 71 diagram-bearing, ~56,500 words.
Reference remains DONE; this was a QA/polish pass. Next: applications phase (brew calc / roast timer / cupping).

---

# v47 — The "make it pop" pass: tasteful motion + depth (Kevin gave free rein to have fun)

Kevin explicitly said: have fun, add tweaks to make it pop, shaders/moving objects/whatever, "I am letting you
drive." Added life WITHOUT breaking the calm warm instrument-panel aesthetic. All motion is subtle, slow, and
guarded by prefers-reduced-motion. 137 pages; ~894 KB (only +3KB \u2014 all CSS, no assets).

## WHAT WAS ADDED (all CSS, self-contained, offline-safe)
- HERO HEAT HAZE: .hero::before renders 3 soft radial-gradient plumes (heat1/2/4 tints) blurred + slowly drifting
  (haze keyframe, 14s alternate) behind the title \u2014 like heat rising off a roaster. z-index below the text.
- SHIMMER TITLE: the "becomes flavor." gradient text now has a 4-stop heat gradient that slowly sweeps
  (shimmer, 9s) \u2014 a living ember glow, not a flashy rainbow.
- LIVING HEATBAR: the 5-band roast gradient bar under the hero got (a) a warm outer glow (box-shadow 18px
  heat1 .22) and (b) a bright heat-pulse that sweeps across it every 4.5s (heatsweep, screen blend-mode).
- ROAST-CURVE DRAWS ITSELF IN: the bean-temp line (.rc-bt) on every roast-profile page now animates via
  stroke-dashoffset (rcdraw, 1.6s) \u2014 the curve plots itself like a live roast. Signature touch on the app\u2019s
  hero visual.
- DIAGRAM REVEAL: every .diagram card fades+rises in (diareveal .5s) and gets a soft heat glow + border-warm on
  hover.
- VIEW FADE: #app fades+rises on every navigation (viewfade .34s) \u2014 page changes feel smooth, not jarring.
- STAGGERED CARD ENTRANCE: .grid (profiles) / .origrid (origins) / .secdir (home cards) children rise in with a
  small cascading delay (cardrise, nth-child delays .03\u2013.12s).
- RICHER HOVERS: secard / pcard / origcard hovers now lift -3px (was -2) with a warm glow shadow
  (rgba(201,163,78,.10)) \u2014 more tactile "pop" on the clickable cards.

## SAFETY / DISCIPLINE
- prefers-reduced-motion:reduce \u2192 a global guard zeroes ALL animation/transition durations. Anyone with that OS
  setting sees the app fully static. This is the responsible way to ship motion.
- Everything is pure CSS (no JS animation loop, no canvas, no libs) \u2192 stays self-contained, offline, tiny (+3KB),
  and GPU-cheap (transforms/opacity only). No layout thrash.
- Aesthetic held: warm/slow/low-opacity, matches the "cooling roast instrument panel" identity. Nothing blinks,
  bounces, or distracts from reading. Removed an early IntersectionObserver reveal idea (redundant w/ the CSS
  diareveal + risked flicker) \u2014 CSS-only is cleaner.
- Fixed an orphaned CSS fragment left from editing the .grad rule; CSS braces verified balanced (366/366),
  9 keyframes, full regression ALL GREEN (100 learn, 71 diagrams, 36 origins+silhouettes, scroll memory intact).

## DEPLOY NOTE: this touched the app SHELL (CSS) \u2192 HARD-refresh after deploy to load the new styles (the service
worker cache const bumped to v47 handles it, but a hard refresh guarantees it).

## Group counts unchanged: 100 Learn + 36 origins + intro = 137 pages, 71 diagram-bearing, ~56,500 words.
Reference DONE + now visually alive. Next: applications phase (brew calc / roast timer / cupping form).

---

# v48 — The personality pass: a "Proud Mary" voice (Kevin: warm/editorial/quietly-confident, NOT Guy Fieri)

Kevin\u2019s brief (his words): keep doing what you did but give it PERSONALITY \u2014 "we aren\u2019t going for Guy Fieri but
rather Proud Mary." = warm, design-led, quietly-confident, dry-witted maker\u2019s voice (like a well-designed coffee
bag), NOT loud/flashy. His promised LAST polish for a while. 137 pages; ~895 KB (+1KB, copy only).

## WHAT CHANGED (voice only \u2014 zero changes to factual reference content, which stays precise)
Personality was added ONLY in the first-impression / connective-tissue copy, deliberately NOT sprinkled everywhere
(that would dilute it). Touchpoints:
- HERO LEDE: rewritten warmer + confident \u2014 ends "Opinionated where it counts, honest about the rest, and
  blessedly free of fluff."
- NEW HERO SIGNATURE LINE (.herosig): a maker\u2019s-credo line under the heatbar \u2014 "Light to dark, seed to cup \u2014
  every step here has a reason, and we tell you what it is." Styled as a quiet mono caption w/ a heat-gradient
  accent bar (::before). New .herosig CSS.
- 5 HOME DIRECTORY CARD BLURBS: rewritten with warmth + dry wit (e.g. origins "the roast level that finally lets
  it sing"; profiles "the honest bit: exactly how it falls apart when you push it too far"; compare "let them
  argue it out"; learn "The good stuff, none of the padding"; start "Start here, no shame in it").
- SECTION LEADS: profiles "the whole spectrum, warts and all"; compare "let them argue it out. Up to four."
- EMPTY STATES: profiles "Nothing here matches that one\u2026 no harm done"; learn "Drew a blank on that one\u2026 or
  wander the chapters below."
- FOOTER: "Made for the people who take it seriously."
- LEFT ALONE (correctly): all factual page bodies/keypoints/refs; METH_GROUP_META descriptions (functional TOC
  text, not a place for cutesy voice); the Start-Here teaching lede (already had the confident "That\u2019s the whole
  craft \u2014 everything else is detail." closer).

## SAFETY / QA
- During the .herosig CSS add I briefly broke the .heatbar::after sweep rule (merged selectors) \u2014 caught + fixed;
  CSS braces verified balanced (368/368), heatsweep animation intact, 9 keyframes present.
- Full regression ALL GREEN (100 learn, 71 diagrams, 36 origins+silhouettes, scroll memory, all voice strings
  render). Motion layer (v47) + reduced-motion guard untouched.
- DEPLOY NOTE: touched the app SHELL (hero markup + CSS) \u2192 HARD-refresh after deploy. Cache const bumped v48.

## STATUS: reference DONE + polished + now it has a soul. This was the last polish pass for a while (Kevin\u2019s call).
## NEXT (when Kevin returns): the APPLICATIONS phase \u2014 interactive tools built ON the reference:
  brew-ratio calculator (ties to the deepened extraction page), roast timer w/ first-crack + DTR calc, cupping/CVA
  score form, dial-in troubleshooter. Pure-JS fits the self-contained-PWA architecture; Anthropic-API-in-artifacts
  available if AI-assisted tools are wanted. PMC commercial track still logged/held.

## Group counts unchanged: 100 Learn + 36 origins + intro = 137 pages, 71 diagram-bearing, ~56,500 words, ~895 KB.

---

# v49 — Country silhouettes REFINED (Kevin: they read as blobs, too small, barely fill the space)

Kevin\u2019s honest call: the origin region-map silhouettes needed work \u2014 too small, floating, blob-like. Decision
(agreed): REFINE, not remove (concept is good, fills the requested space) and not replace (raster/GeoJSON would
bloat the file + break the hand-drawn vector aesthetic \u2014 stays one self-contained offline file). Two root causes
fixed: crude paths + timid sizing. 137 pages; ~897 KB.

## FIX 1 \u2014 REDREW all 36 silhouette paths with real detail
- Old paths were 8\u201313 points (Rwanda/Burundi/El Salvador/Zimbabwe/Jamaica down at 8\u20139 = unavoidably blobby).
- New paths are 12\u201332 points capturing each country\u2019s DISTINCTIVE contour: Brazil\u2019s eastern bulge + southern
  taper, India\u2019s subcontinent point, Vietnam\u2019s thin S-curve w/ narrow waist, Peru\u2019s Andean stretch, Sulawesi\u2019s
  multi-armed orchid, etc. Verified by rendering each shape solid + checking fill%/aspect (Vietnam 9% fill /0.40
  aspect = correctly thin&tall; Brazil 39% = correctly bulky; Ethiopia/Rwanda wide-aspect = correct). Visual
  spot-checks (Brazil, Vietnam, Sulawesi, Ethiopia in-context) confirm they now read as PLACES, not blobs.
- All 36 render cleanly (solid-fill test, none broken/empty). Island set (Java/Sulawesi/Bali/Flores/Hawaii-chain)
  also redrawn; Hawaii stays a 4-island multi-path.

## FIX 2 \u2014 SIZING + PRESENCE in originRegionMap render
- Was: Math.min(H-padTop-8, 132) capped small, anchored fully inside bottom-right w/ 16px margin \u2192 floated.
- Now: Math.max(H-padTop+18, 150) fills the card height generously, and the shape BLEEDS off the lower-right
  corner (sx/sy pushed +14%/+12% past the edge) so it reads as an intentional design element anchored to the
  corner, not a sticker. Bumped opacity 0.13 \u2192 a 0.20\u21920.10 diagonal GRADIENT fade (silfade linear-gradient per
  accent) so it has more presence at the top-left of the shape and dissolves toward the corner.
- Text safety: silhouette lives in the RIGHT portion; GROWING REGIONS label + region names (left third) verified
  intact and unoverlapped. aria-hidden kept.

## Result: the region-map header now looks deliberate \u2014 a large, recognizable, softly-faded country shape filling
## the right side behind the growing-regions list. Big upgrade over the v42\u2013v48 blob.

## QA: full regression ALL GREEN (100 learn, 71 diagrams, 36 origins, 36/36 silhouettes, labels intact, gradient
present). DEPLOY NOTE: region-map component only (no shell/CSS-animation change) \u2014 normal refresh OK, though hard
refresh guarantees the new shapes.

## Group counts unchanged: 100 Learn + 36 origins + intro = 137 pages, 71 diagram-bearing, ~56,500 words, ~897 KB.
## Reference remains done+polished; this was a targeted visual-quality fix. Next: applications phase.

---

# v50 — Silhouettes converted to flowing BEZIER CURVES (Kevin: double the points, make them look like real curves)

Kevin asked to at least double the points and make the silhouettes read as actual CURVES, not angular polygons.
Solution: a build-time Catmull-Rom -> cubic-Bezier smoother. 137 pages; ~912 KB (+15KB for the curve data).

## APPROACH: curve-smoothing at build time (not hand-authoring hundreds of control points)
- The COUNTRY_SIL paths stay hand-authored as readable straight-line POLYGONS (they capture each country\u2019s
  proportions + distinctive features \u2014 the skeleton). build.py now runs a Catmull-Rom->cubic-Bezier converter
  (smooth_silhouette / _cr_to_bezier, tension 0.8) over EVERY path at build time, turning each straight segment
  into a flowing curve. So one source vertex -> one Bezier C command; the effective control-point count roughly
  DOUBLES and every corner becomes a smooth curve.
- Why this way: hand-placing Bezier handles for 36 coastlines would be error-prone and I can\u2019t eyeball true
  coastlines; smoothing the proportion-correct skeleton gives organic curves reliably + keeps the source EASY to
  edit (still simple polygons). tension 0.8 = clean curves, minimal overshoot (tested vs 1.0).
- Implementation: build.py smooths the COUNTRY_SIL block in the final `out` string via regex right before
  writing index.html; prints "Smoothed 36 country silhouettes into Bezier curves". Source stays straight-line;
  OUTPUT is all curves. Verified: 36/36 output paths contain C commands, all render cleanly (solid-fill test),
  in-context cards (Ethiopia, Colombia, India, Peru) confirmed as flowing coastline shapes.

## Result: the country outlines now read as real, curved map shapes \u2014 India tapers smoothly to its point, Peru\u2019s
## borders flow, Brazil\u2019s coast curves, Vietnam keeps its graceful S. Final step up from the v49 angular version.

## MAINTENANCE NOTE (important for future edits): to tweak a silhouette, edit its STRAIGHT-LINE path in
## COUNTRY_SIL (build.py ~line 1310). The build auto-smooths it. Do NOT hand-edit curves in index.html \u2014 they are
## generated. To change smoothing strength, adjust tension in smooth_silhouette (0.8 default; lower=tighter).

## QA: full regression ALL GREEN (100 learn, 71 diagrams, 36 origins, 36/36 curved silhouettes, labels intact).
## DEPLOY: region-map component only \u2014 normal refresh OK, hard refresh guarantees the curves.

## Group counts unchanged: 100 Learn + 36 origins + intro = 137 pages, 71 diagram-bearing, ~56,500 words, ~912 KB.

---

# v51 — Silhouette points DOUBLED again + TOPOGRAPHY (mountains + shorelines) per region (Kevin request)

Kevin: double the points again + add topography that makes sense for the region \u2014 color variants for mountains
and shorelines. 137 pages; ~936 KB (+23KB for the finer curves + topo layer).

## FIX 1 \u2014 doubled the coastline points again (finer curves)
- Added _subdivide() to the build smoother: inserts a midpoint between every vertex pair BEFORE the Catmull-Rom
  smoothing, doubling the anchor count. Bezier segments per country went ~11\u201331 \u2192 now 24\u201362 (avg 35). Coastlines
  are noticeably finer/rounder. Source polygons unchanged (still easy to edit); doubling happens at build time.

## FIX 2 \u2014 TOPOGRAPHY layer (new COUNTRY_TOPO data + clipped render)
- New COUNTRY_TOPO map (31 countries): per-country mtns:[[x,y]...] peak positions placed where the REAL ranges
  sit (Andes down Peru/Colombia/Ecuador west, Ethiopian highlands, East-African rift ranges, Sierra Madre,
  Annamite range in Vietnam, etc.) + coast:[[x,y]...] tracing the main shoreline. Coords in the same 0..100 box
  as the silhouette.
- Render (originRegionMap): base landmass (gradient fade) + a clipPath of the silhouette, and INSIDE it:
  * MOUNTAINS \u2014 little peak glyphs in a lighter elevation tint (#d8b566) with a sunlit left face (#f2e6bf) and a
    SNOW CAP (#fbf3dc) on the taller peaks; slight size variation for a ridgeline feel. Clipped to the landmass
    so nothing spills outside the coast.
  * SHORELINE \u2014 a soft lighter stroke (#e8d29a) tracing the coast points on coastal countries.
- Elevation/coast colors are deliberate lighter-gold variants of the warm palette (not new hues) so it stays on-
  aesthetic. Verified in-context: Peru shows snow-capped Andes + Pacific coast; Colombia/Ethiopia/etc. read as
  real terrain. All 36 render cleanly, mountains stay clipped inside the coast, region text unaffected.

## MAINTENANCE: silhouette shapes = straight-line polygons in COUNTRY_SIL (auto-smoothed+subdivided at build).
## Topography = COUNTRY_TOPO (mtns/coast point lists, same 0..100 space). Both easy to tweak by hand; rebuild
## re-smooths. 5 small islands intentionally have no mtns (would clutter).

## QA: full regression ALL GREEN (100 learn, 71 diagrams, 36 origins, 36 silhouettes w/ topo clip, labels intact).
## DEPLOY: region-map component only \u2014 normal refresh OK, hard refresh guarantees the new terrain.

## Group counts unchanged: 100 Learn + 36 origins + intro = 137 pages, 71 diagram-bearing, ~56,500 words, ~936 KB.

---

# v52 — Coffee-growing LIFE on the maps (Kevin: get creative, but remember people live there; respect that)

Kevin\u2019s note reframed the whole thing: these are not empty landscapes to look at \u2014 they are lived-in, worked lands
where people grow coffee. So the maps now carry human presence, not just terrain. 137 pages; ~938 KB.

## WHAT WAS ADDED (all clipped inside the landmass, layered on the v51 mountains/coast)
- COFFEE-GROWING SLOPES: soft cultivated-green patches (#8faf74, muted to fit the warm palette) nestled beside
  each mountain range \u2014 because coffee is grown on the slopes at altitude. Two-ring soft fill so they read as
  planted hillsides, not hard dots.
- SETTLEMENTS: small warm lights (#fff1cf core + #ffe7a8 glow) beside the ranges \u2014 towns where the growing
  communities live. Deliberately small/quiet: dots of habitation in the hills, not glaring markers.
- A COFFEE CHERRY + LEAF (#c65b3c cherry, #8faf74 leaf, soft highlight) nestled in the growing country \u2014 the
  crop these communities build a life around. The one clear signature element that says "this is a coffee land."
- Placement is geographic + honest: everything clusters where the real ranges/growing regions are (Ethiopian
  highlands, Kenyan central highlands, the Andes slopes, etc.), derived from the COUNTRY_TOPO mtn positions.

## INTENT (worth preserving): this change is about RESPECT \u2014 acknowledging that origin coffee is the work of real
## people in real places, not an abstract commodity or an empty map. The maps now quietly tell that story: land,
## mountains, cultivated slopes, a town light, a coffee cherry. A lived-in landscape.

## Verified via pixel-color + ASCII-grid composition checks (the view image tool was blank all session \u2014 infra,
not the art; pixel data confirms every element renders). Ethiopia + Kenya compositions confirmed balanced (life
clusters in the highlands, not cluttered) on both large and small countries. 31 countries carry life (the 5 tiny
islands stay clean). All 36 silhouettes render; region text unaffected; clipped inside coasts.

## MAINTENANCE: life elements are DERIVED from COUNTRY_TOPO.mtns (grow patch + settlement + cherry placed
## relative to peak positions) \u2014 no new per-country data to maintain; move a range and its life moves with it.
## Tune visibility via the fill-opacity values in the life block of originRegionMap.

## QA: full regression ALL GREEN (100 learn, 71 diagrams, 36 origins, 36 silhouettes, 31 w/ life, labels intact).
## DEPLOY: region-map component only \u2014 normal refresh OK, hard refresh guarantees the new detail.

## Group counts unchanged: 100 Learn + 36 origins + intro = 137 pages, 71 diagram-bearing, ~56,500 words, ~938 KB.

---

# v53 — Maps REDESIGNED: elegant engraved-map look (Kevin: the mountains/trees/cherries look terrible + too small)

Kevin\u2019s screenshot (Uganda) showed the v51\u2013v52 terrain reading as cluttered clip-art: cartoon triangle peaks,
green blobs, a red cherry, tiny lights \u2014 scattered objects fighting each other, floating in the middle-right with
empty space to the left. Honest cause: I OVERBUILT it (kept adding elements). Fix = restraint. 137 pages; ~936 KB.

## WHAT CHANGED \u2014 replaced the diorama with a considered map treatment
- REMOVED entirely: triangle mountains, snow caps, green growing-slope blobs, settlement lights, red coffee
  cherry + leaf, coastline stroke. All of it read as clip-art at watermark scale.
- NEW look (per country, all clipped to the shape):
  * Base landmass = the linear-gradient fade (kept).
  * ELEVATION = a soft RADIAL-gradient glow (userSpaceOnUse) centered on the highland CENTROID (mean of
    COUNTRY_TOPO.mtns), radius derived from how spread-out the ranges are. Reads as raised, shaded high ground
    \u2014 smooth tonal shading like an engraved relief map, NO discrete peaks. Colors: #e9cf94\u2192#d8b566 fading to
    transparent (warm-gold, on-palette).
  * ONE quiet marker for the growing heart: a small hollow ring + dot (#f0dca0) at the highland centroid.
    Replaces the loud red cherry. Understated.
  * A crisp thin OUTLINE on the whole silhouette (accent, 0.35 opacity, 0.8 width) \u2014 gives the engraved-map
    definition that makes it look intentional.
- BIGGER + better anchored: silSize (H-padTop)*1.18 (min 168, was ~150) and pushed further off the corner
  (0.20/0.18 bleed) so it FILLS the right side instead of floating with empty space beside it.

## RESULT: clean, elegant, restrained \u2014 a softly-shaded country shape with a crisp edge and a single quiet
## growing-heart mark. Verified via ASCII-composition render (view image tool blank again this session = infra):
## Uganda/Brazil now show smooth tonal gradients across the landmass, no scattered objects. Output got SMALLER
## (937\u2192936 KB) despite looking better \u2014 fewer shapes, cleaner code. Good refactor.
## Still derived from COUNTRY_TOPO.mtns (centroid+spread) \u2014 no new per-country data; the growing-life INTENT is
## kept (the ring marks the growing heart) but expressed with restraint instead of clutter.

## Lesson logged: at watermark scale, tonal SHADING > discrete objects. Don\u2019t add more elements; refine the few.

## QA: full regression ALL GREEN (100 learn, 71 diagrams, 36 origins, 36 elev+outline, no cherry/blob, labels ok).
## DEPLOY: region-map component only \u2014 normal refresh OK, hard refresh guarantees it.

## GitHub deploy (separate issue, ongoing): "Deployment failed, try again later" is a KNOWN GitHub-side Pages bug
## (build succeeds, only deploy step stalls on syncing_files; actions/deploy-pages issues #406/#418). Recommended
## Kevin switch Settings\u2192Pages\u2192Source to "Deploy from a branch" (main /root) \u2014 simpler + reliable for a static
## site, skips the failing Actions deploy job. Not a code/file problem (artifact builds fine at 604 KB).

## Group counts unchanged: 100 Learn + 36 origins + intro = 137 pages, 71 diagram-bearing, ~56,500 words, ~936 KB.

---

# v54 — Region-map card RELAYOUT (Kevin: move country name under the map, enlarge GROWING REGIONS to the left,
# label the glowing dot; fill the empty middle)

Kevin\u2019s layout direction on the Uganda card: (1) move the country NAME to the right, UNDER the map picture;
(2) make GROWING REGIONS bigger + moved LEFT, above the first dot; (3) the glowing dot needs a label \u2014 unclear
what it represents; (4) the map still hugged the corner leaving the middle empty. Reworked the whole card layout.
137 pages; ~936 KB.

## LAYOUT CHANGES (originRegionMap fully restructured into a LEFT list zone + RIGHT map zone)
- COUNTRY NAME: moved out of the top-left header \u2192 now centered UNDER the map in the right zone (18px, bold),
  with the ALTITUDE beneath it (mono, accent).
- GROWING REGIONS: was a small 10.5px single-line label \u2192 now a BIG two-line stacked mono header (15px,
  "GROWING" / "REGIONS") on the upper-LEFT with the location pin beside it, sitting above the first region dot.
  It reads as the real heading for the list now.
- THE GLOWING DOT IS NOW LABELLED: added a legend under the country name \u2014 a small ring-marker swatch + the
  words "coffee-growing heartland" \u2014 so its meaning is explicit. (It marks the highland centroid where the
  country\u2019s coffee is grown.)
- MAP CENTERED IN THE RIGHT ZONE: silhouette now centered at x=W*0.72 (was hugging the far corner) at 150px,
  filling the previously-empty middle-right instead of floating in the corner.
- CARD HEIGHT now = max(list height, right-zone height) so the map + name + altitude + legend stack always fits
  (card grew ~218\u2192242 for a 4-region origin). Left list (padTop 64) and right map zone are independent columns.

## Kept from v53: the elegant engraved-map treatment (soft radial elevation shading, crisp outline, restrained
## single marker) \u2014 this round was LAYOUT, not the map art itself.

## Verified via ASCII full-card composition (view image tool intermittent this session): Uganda + Ethiopia both
## show the big left GROWING REGIONS header + list, the centered shaded map filling the right, the growing-heart
## marker in the highlands, and name/altitude/legend stacked cleanly beneath. No overlap, empty middle gone.

## QA: full regression ALL GREEN (100 learn, 71 diagrams, 36 origins, 36 silhouettes, 36 GROWING-REGIONS headers,
## 31 heart-legends, country name + altitude present). DEPLOY: region-map component only \u2014 hard refresh to see it.

## Reminder (GitHub deploy still failing): switch Settings\u2192Pages\u2192Source to "Deploy from a branch" (main /root) \u2014
## the Actions deploy step is the known-buggy part; static-site branch deploy sidesteps it. Build/artifact are fine.

## Group counts unchanged: 100 Learn + 36 origins + intro = 137 pages, 71 diagram-bearing, ~56,500 words, ~936 KB.

---

# v55 — REAL country maps (Natural Earth) + glossary false-positive fix + particle-diagram collision fix

Kevin (with screenshots): the hand-drawn silhouettes look NOTHING like the real countries ("that is defffff not
Brazil"), all of them bad. Also: some glossary links are wrong (common words linked in their ordinary sense),
a graph has garbled overlapping text, and the latte-art diagram is weak. Directive: make the shapes look like the
ACTUAL countries FIRST (use real maps as reference); HOLD the regional dots for now; fix the other errors.

## FIX 1 (the big one) — REAL SILHOUETTES from Natural Earth
- ROOT CAUSE of every prior map complaint: I was hand-drawing shapes from memory. They were wrong at the bone;
  no amount of "more curves" fixes a wrong shape.
- NEW PIPELINE (gen_silhouettes.py, kept in /home/claude/coffee): downloads Natural Earth 50m admin-0 countries
  GeoJSON (public-domain cartographic data), extracts each of the 36 coffee origins by name, simplifies with
  shapely (adaptive tolerance: 0.06 for small countries, 0.35 for large), drops tiny outlying islands
  (area<12-20% of largest), normalizes into the 0..100 box (Y-flipped for SVG), emits straight-line paths.
  Islands handled specially: Sumatra/Java/Sulawesi/Flores/Bali extracted from Indonesia by centroid lon/lat;
  Hawaii = multi-island chain from USA. Output baked into COUNTRY_SIL in build.py (self-contained; geojson only
  needed at generation time). Verified by ASCII render: Brazil, Vietnam (S-curve), India (subcontinent point),
  Peru, Sulawesi (multi-armed), Italy (the BOOT) all read as the real countries. Point counts 10-136, real.
- SMOOTHING RE-TUNED for real data: smooth_silhouette now subdivide=False, tension=0.55 (was subdivide=True,
  0.8). Real outlines already carry detail; subdividing would round off real features (peninsulas, arms). The
  gentle Catmull-Rom pass just softens simplified segments into natural coastline curves.
- RENDER: bbox-fit each shape into a 158px box (silBBox helper), centered in the right zone; soft centered
  elevation glow (no misplaced markers); crisp outline; country name + altitude beneath. REGIONAL DOTS + the old
  COUNTRY_TOPO-based mountains/glow are HELD/removed per Kevin (the old topo coords were for the old fake shapes
  anyway). REGION_COLORS + silBBox + the dot-placement code remain staged for when we re-add dots on real maps.

## FIX 2 — glossary false-positive links (Images 2 & 3: "washed", "development" wrongly linked)
- linkTerms matched glossary terms even when the word was used in its ordinary English sense. Removed the bare
  ambiguous aliases (\x27washed\x27, \x27browning\x27) and added a STOP set (washed, development, body, clean, wild, natural,
  green, roast, crack, bright, dry, wet, hard, soft, drop, charge, slurp, airflow, chaff, process, honey) that is
  deleted from GLOSS_MAP so those never auto-link alone. Multiword terms (first crack, rate of rise, washed
  process, TDS) still link. Verified: "washed repeatedly"/"cherries development" now clean; "first crack" links.

## FIX 3 — particle-size distribution diagram (Image 1: garbled overlapping text)
- The legend (top-left, inside frame) collided with the FINES zone label + curves. Moved the legend ABOVE the
  frame (two entries at x+66/x+296, y=gy0-16), dropped FINES/BOULDERS labels lower into the chart body (gy0+44),
  shortened "bimodal (body, more fines)"->"(more body)". Verified: all text y-separated, no overlaps.

## STILL TODO (flagged, not yet done): the latte-art diagram (diaPourStroke) is weak — the heart reads as a
## spade, rosetta leaves are stacked ovals, tulip is lumpy. Needs a real redraw. Deferred to keep this batch
## focused on the maps (the priority) + correctness fixes. Also: re-add per-region dots on the REAL maps once
## Kevin confirms the shapes are right (staged: REGION_COLORS, silBBox, dot code preserved).

## QA: full regression ALL GREEN (100 learn, 71 diagrams, 36 real silhouettes, glossary fixes, diagram fix).
## DEPLOY: touched COUNTRY_SIL + smoother + glossary + one diagram; hard refresh. Cache v55.
## GitHub deploy still needs the Settings->Pages->"Deploy from a branch" switch to publish.

## Group counts unchanged: 100 Learn + 36 origins + intro = 137 pages, 71 diagram-bearing, ~56,500 words, ~937 KB.
## gen_silhouettes.py + real_silhouettes.json + ne50.geojson kept in /home/claude/coffee for regenerating shapes.

---

# v56 — Region dots BACK, placed at REAL lat/lon (cross-referenced with actual geography)

Kevin: add the region dots back, but cross-reference placement with real maps first. Done properly: dots are
placed at each region\u2019s REAL lon/lat, projected through the SAME transform as the silhouette (same Natural Earth
source), so they land in the right actual place inside the country. 137 pages; ~940 KB.

## HOW (the cross-reference, done right)
- region_coords.py: hand-built lon/lat table for all 124 point-locatable growing regions (10 generic entries
  like "(Robusta lowlands)","(Yunnan)" set to None -> no dot). Coordinates are real, verified against geography.
- gen_with_dots.py: for each origin, rebuilds the EXACT same polygon extraction + 0..100 normalization used to
  make the silhouette (gen_silhouettes.py logic), then projects each region\u2019s lon/lat through that identical
  transform. Guarantees dots sit in the same coordinate space as the shape. Output -> region_dots.json ->
  REGION_DOTS in build.py (aligned to regions2 order; null = no dot). All 124 dots fall inside the 0..100 box.
- VERIFIED placement by ASCII-rendering shape+dots and checking against real geography: Ethiopia (Harrar EAST,
  Yirgacheffe/Guji/Sidamo SOUTH-center), Colombia (dots down the Andean axis, Nari\u00f1o SW near Ecuador), Brazil
  (Bahia NE, Minas cluster S-center), Hawaii (dots ON the islands not the sea), Vietnam (all in Central
  Highlands). Confirmed dots land inside the shapes in the right places.

## RENDER: each map dot = its region color (REGION_COLORS) + number, drawn inside the same translate/scale group
## as the silhouette (so projection lines up). List dots recolored + numbered to MATCH -> the list is now a real
## KEY: dot N color in the list = dot N on the map. Generic (null) regions get a plain accent list dot, no number.

## Pipeline files kept in /home/claude/coffee for regeneration: region_coords.py (the lat/lon table, EDIT HERE to
## move/fix a dot), gen_with_dots.py, region_dots.json, gen_silhouettes.py, real_silhouettes.json, ne50.geojson.
## To adjust a dot: edit its lon/lat in region_coords.py, rerun gen_with_dots.py, rebuild REGION_DOTS block.

## QA: full regression ALL GREEN (100 learn, 71 diagrams, 36 real silhouettes, 36 with region dots, glossary fix
## intact). DEPLOY: region-map component; hard refresh. Cache v56.

## STILL TODO: latte-art diagram redraw (diaPourStroke, still weak - flagged in v55). GitHub deploy still needs
## the Settings->Pages->"Deploy from a branch" switch to publish.

## Group counts unchanged: 100 Learn + 36 origins + intro = 137 pages, 71 diagram-bearing, ~56,500 words, ~940 KB.

---

# v57 — Latte-art diagram REBUILT parametrically (Kevin: make it look freaking perfect, different method OK, search refs)

Method change, same philosophy as the maps fix: stop hand-eyeballing shapes, generate them. Cross-referenced real
pour photos via image search first (heart = round lobes + dimple + pull-through point + faint pour rings; rosetta
= fern of paired DROOPING leaves, big at base, tiny heart + stem on top; tulip = plump nested upward-wrapping
crescents + heart + pull-through). Then rebuilt diaPourStroke with PARAMETRIC Bezier generators. ~943 KB.

## WHAT CHANGED (diaPourStroke fully rewritten, kanji-stroke-order teaching layout KEPT)
- heartD(cx,cy,s): parametric cubic-Bezier latte heart (round lobes, shallow dimple, soft point). Finished heart
  gets faint clipped POUR RINGS inside (the disc phases) + the cut line extending past the point. clipPath ids
  lah1..n via counter.
- rosetta(cx,cy,r,nPairs,finished): fern generator — paired leaves, width/thickness/droop all functions of
  height t; partial pours (nPairs<6) stay LOW in the cup like a real mid-pour; finished = 6 pairs + tiny heart
  at crown + stem cut line. Leaves drawn top-first so base leaves overlap naturally.
- tulip(cx,cy,r,nPetals,finished): nested crescents via double-Q paths, tips curled up, PLUMP (inner control at
  h*0.12 after tuning — 0.38 rendered as thin smiles), finished = 3 petals + small heart + pull-through.
- RENDERING richness: top-down ceramic cup (white rim ring + dsoft shadow) + radial CREMA gradient (lacrema,
  a86636->63381a) + warm MILK radial gradient (lamilk, fbf5e6->ead7b9). Red cut/pull arrows got their own red
  marker (darrR) instead of borrowing the cream one.
- LAYOUT fix from Kevin\x27s screenshot: header desc was crossed by step arrows. Rows respaced (header y=16/170/324,
  cups at header+74), H 420->478, finished cup LARGER (RF=29 vs R=24) for emphasis. Verified 0 text/arrow
  collisions + 0 out-of-bounds (coordinate extraction test).
- Bare & in captions escaped to &amp; (was breaking strict XML; browsers tolerated it but hygiene).

## VERIFICATION: cairosvg render + high-res ASCII crops of each finished pour. Heart: lobes/dimple/point/rings/cut
## all read. Rosetta: fern with visible crema gaps between leaf pairs, crown heart, stem. Tulip: plump nested
## crescents (after the 0.38->0.12 tuning pass). View tool blank again (infra) — ASCII was the judge.

## QA: full regression ALL GREEN (100 learn, 71 diagrams, 36 origins w/ real dots, latte parametric + on
## brew_latteart page, glossary fix intact). Cache v57. Hard refresh. GitHub Pages branch-deploy switch still pending.

## Group counts unchanged: 137 pages, 71 diagram-bearing, ~56,500 words, ~943 KB.

---

# v58 — Diagram polish pass 1: cherry + grind rebuilt, 37 XML-breaking ampersands fixed (Kevin: the basic charts look like a 5-year-old drew them)

Kevin: go polish ALL the other images/charts we havent revisited - many look childish. Ran a systematic audit
(rendered all 69 diagrams, scored by bezier-density/gradient/shape-primitive counts to find the crude ones), then
fixed the worst + a widespread bug. This is PASS 1 of an ongoing effort. ~945 KB.

## AUDIT METHOD (repeatable): _audit/ dir has every diagram as SVG; crudeness ranked by bezier count / plain-shape
## ratio. Crudest tier flagged: cherry, grind, then flat charts (caffeine/extraction/cva/dtr/phasebar - many of
## these are FINE as clean data charts, not childish). pourstroke (v57 latte art) is the polish gold standard.

## FIXED THIS PASS
- CHERRY cross-section: was flat concentric circles (read as a bullseye/target). REBUILT as a botanical cut:
  ovoid fruit (not perfect circles), per-layer RADIAL gradients for volume (chSkin/chPulp/chMuc/chParch/chBean),
  two real beans nestled with a center groove + fold shadows, silverskin line, wet-cherry gloss highlight, stem
  dimple, leader lines from each layer to its label. Now reads as a real cherry.
- GRIND size: was random scattered circles (worst offender, near-empty 520x116). REBUILT as four DISHES of actual
  coffee grounds - irregular 5-vertex polygon particles with a radial coffee gradient, sized + densit-scaled per
  method (espresso = dense fine powder ... French press = few coarse chips), each in a shadowed dish with method +
  description + micron size (~250um .. ~1000um). Deterministic PRNG so builds are stable.
- XML BUG (widespread, real): 37 raw " & " ampersands across 20 diagrams (acidmap, blend, climatecoffee, cmarket,
  coldbrew, fermentmethods, geishastory, latteart, machtypes, maintenance, profiling, puckprep, roastdefects,
  scapath, speciesmap, spottypica, supplychain, teacoffee, waterchem, waterrecipe). Browsers tolerated them but
  they are invalid XML (broke cairosvg, fragile). Escaped all to &amp; (space-delimited " & " is always literal
  text; JS && and &0x bitwise untouched + verified). All 22 checked diagrams now 0 raw ampersands.

## STILL TODO (pass 2+): continue polishing mid-tier diagrams that could use depth (gradients/shadows on flat
## bars where it helps), case-by-case. NOT everything needs it - many clean charts are correct as-is; the goal is
## fixing CHILDISH, not adding noise. Latte art (v57) + maps (v55/56) already done.

## QA: full regression ALL GREEN (100 learn, 71 diagrams, 36 origins+dots, cherry rich, grind 264 particles, all
## ampersands clean, key diagrams render). Cache v58. Hard refresh. GitHub Pages branch-deploy switch still pending.

## Group counts unchanged: 137 pages, 71 diagram-bearing, ~56,500 words, ~945 KB.

---

# v59 — Realistic coffee beans (shared renderer) + family-tree REDESIGN (Kevin: beans need cherry-level polish; family tree = good data, rough-draft design)

Web-searched real references FIRST (per Kevin - going from memory is what caused earlier misses). Bean anatomy
sources (Sweet Marias, Stone Street, JayArr, Dark Matter): bean is oblong ~10x6mm (5:3), Arabica has a WAVY
center cut, the cut is a deep FOLD lined with paler SILVERSKIN, green=blue-green leathery matte, roasted browns +
crack opens. Variety-tree references (World Coffee Research, Cafe Imports posters): clean lineage groups from
Yemen stock, solid color-coded nodes, generous spacing, curved connectors. ~947 KB.

## FIX 1 - shared realistic BEAN renderer (diaBean), used by BOTH defect galleries
- New diaBean(cx,cy,s,col,kind,overlay) right after diaDefs. Real anatomy: oblong body (bezier, rounded ends,
  ~5:3), a folded CENTER CUT with paler silverskin lining (wavy S for roast, per Arabica) + parallel fold
  shadows to read as a valley, radial body gradient (lite->col->dark) for volume, top-left specular highlight,
  contact shadow. kind=green|roast sets crease/edge tone + silverskin color.
- All defect overlays clipped to the bean body: scorch/tip/face/chip/oil (roast) + fullblack/partblack/sour/
  insect(boreholes)/broken/floater/fungus/shell (green). diaRoastDefects + diaGreenDefects now just call
  diaBean instead of their old flat-ellipse-with-squiggle locals. Verified: beans read dimensional, center cut
  visible, defects distinct (quaker pale, overdeveloped oily-dark, etc).

## FIX 2 - family tree REDESIGN (was flat translucent pills + crossing straight lines = rough draft)
- Rebuilt diaFamilyTree: solid #241a12 node cards with a colored TOP ACCENT BAR + gradient fill + soft shadow
  (real depth), lineage COLOR-CODING (Typica gold, Bourbon red, Hybrid crimson, Geisha amber, SL pink, disease
  blue), CURVED elbow connectors (cubic bezier parent->child, tinted) instead of crossing diagonals, generous
  spacing (W 820->880, taller rows at y=14/92/176/260/344), clearer type hierarchy. Same correct data/lineage,
  now reads as finished design. Geisha stands apart bottom-left, Timor Hybrid anchors bottom-right.

## BUGS fixed in passing: a malformed color hack (fill="##a2907a" double-hash from a bad .replace) + one raw
## ampersand ("Catimor & Sarchimor") in the new tree. Both caught in render verification.

## STILL TODO (ongoing polish, per Kevin screenshots): green-defect beans looked near-identical before - partly
## the v58 ampersand fix, now further helped by the shared bean w/ distinct overlays. Continue case-by-case on any
## other diagrams Kevin flags. profiling loop had label collisions in an earlier shot - worth a spacing pass next.

## QA: full regression ALL GREEN (100 learn, 71 diagrams, 36 origins, diaBean shared + used by both galleries,
## family tree redesigned, 0 raw ampersands in checked diagrams). Cache v59. Hard refresh. Pages branch-deploy pending.

## Group counts unchanged: 137 pages, 71 diagram-bearing, ~56,500 words, ~947 KB.

---

# v60 — Profiling pentagon REDESIGNED (loop diagram) + confirmed particle-size fix; audited flow-diagram siblings

Kevin: the pentagon (profiling loop) needs the family-tree treatment; did particlesize + profiling get fixed;
find other charts in the same rough-draft vein. Pulled PROFESSIONAL loop/cycle diagram references first
(SlideModel, SlideBazaar, infodiagram, Dreamstime): pro pattern = circular numbered COLOR-CODED nodes, CURVED
directional arrows showing flow, each node label placed radially OUTWARD with clearance (no overlap), optional
hub/side card. ~948 KB.

## VERIFIED STATUS of the two Kevin asked about:
- particlesize: ALREADY FIXED in v58 (legend moved above frame at y=38, FINES/BOULDERS dropped to y=98 in the
  chart body; confirmed legend-above-FINES, 0 collision). Image 2 = the fixed version.
- profiling: was STILL broken (3 text collisions at the bottom - "change ONE variable"/"score blind"/caption
  overlapping). NOW REBUILT (see below).

## PROFILING PENTAGON rebuilt (diaProfiling) to the pro loop pattern:
- Taller canvas (H 250->320) for real breathing room. Pentagon ring on the LEFT (cx250,cy150,rx150,ry104),
  scale-up card on the RIGHT.
- 5 numbered COLOR-CODED nodes (r17, gradient fill, colored ring, drop shadow). CURVED directional arrows bow
  outward around the ring (clockwise flow), endpoints trimmed to the node edge so arrowheads meet the circles.
- Labels placed by position: top node ABOVE it, right-side nodes to the RIGHT (start-anchored), left-side nodes
  to the LEFT (end-anchored) - each with a one-line note, all with clearance. Caption moved fully clear at H-10.
- Verified: 0 text collisions (coordinate-overlap test), renders clean. Same design language as the v59 family tree.

## FLOW-DIAGRAM AUDIT (checked the node/connector siblings): supplychain (clean horizontal 5-stage row) and
## cmarket (block flow) look ACCEPTABLE - left as-is to avoid adding noise. profiling was the one true offender.
## If Kevin flags others (scapath, waves, historytimeline, fermentmethods) they can get the same pass.

## QA: full regression ALL GREEN (100 learn, 71 diagrams, 36 origins, profiling 0-collision + redesigned, 0 raw
## ampersands). Cache v60. Hard refresh. GitHub Pages branch-deploy switch still pending to view live.

## Group counts unchanged: 137 pages, 71 diagram-bearing, ~56,500 words, ~948 KB.

---

# v61 — Diagram polish batch 1 of the 19-screenshot audit: moka pot + brew-family icons made REAL

Kevin uploaded ~19 screenshots flagging every diagram needing polish, with the rule: anything trying to be an
IMAGE of something (moka pot, brew methods) should look like the REAL thing; judge all vs real-world examples;
do a few at a time. Created DIAGRAM_TODO.md cataloging all of them (Tier A illustration upgrades, Tier B flow/
hierarchy, Tier C minor). This is batch 1. Searched real references first for each. ~954 KB.

## TODO LIST captured in DIAGRAM_TODO.md (shipped alongside). Highlights still pending: processing beans,
## roasters, pourover, puckprep, milkdrinks, borerstory cherry (Tier A); scapath, cmarket, historytimeline,
## vartree (the SEPARATE older tree, NOT the v59 familytree), supplychain (Tier B); robustarise, waterchem (Tier C).

## FIXED THIS BATCH
- MOKA POT (diaMokaPot): was 3 disconnected floating trapezoids. Searched Bialetti official anatomy (octagonal
  body, bottom boiler filled to the valve, funnel-filter w/ plate holding grounds, upper collector, spout,
  black triangular handle, ~1.5 bar). REBUILT the left panel as a real cut-away Bialetti silhouette: faceted
  tapered base boiler with translucent WATER fill + safety-valve nub, the pinched-waist screw joint, the funnel
  stem + grounds basket at the waist, the faceted upper collector with brewed coffee pooling + lid/knob, the
  spout, the classic black handle, internal flow arrows (water up the stem -> through grounds -> into collector),
  flame underneath. Labels moved to the far left with leader lines (no overlap). Right-side moka-vs-espresso
  bar comparison kept (reads well). Verified via ASCII: clear moka silhouette.
- BREW FAMILIES (diaBrewFamilies): the 3 icons were abstract (bare cone outline / rect+dots / rect+arrow).
  Searched canonical vessels. REBUILT as recognizable brewers: Percolation = a real V60 CONE with interior
  spiral ridge lines + ground bed + drip stream into a carafe; Immersion = a FRENCH PRESS (glass carafe, lid,
  plunger rod + knob, mesh disc, steeping grounds, side handle); Pressure = an espresso PORTAFILTER (round
  basket group + handle to the right + twin espresso streams into a cup + pressure arrow). Verified via ASCII:
  all three read as their real device.

## Method reminder that keeps working: SEARCH real references first (Bialetti anatomy page, brew-method guides),
## then build parametrically. Same lesson as maps/beans/latte art.

## QA: full regression ALL GREEN (100 learn, 71 diagrams, 36 origins, mokapot + brewfamilies rebuilt, 0 raw
## ampersands). Cache v61. Hard refresh. Pages branch-deploy switch still pending to view live.

## Group counts unchanged: 137 pages, 71 diagram-bearing, ~954 KB. NEXT BATCH: continue down DIAGRAM_TODO.md
## (processing beans + roasters + pourover next, then the Tier B flow diagrams).

---

# v62 — Diagram polish batch 2: processing beans + roasters + pour-over made REAL

Continued down DIAGRAM_TODO.md (Tier A "make it look real" illustrations). Searched real references first for each.
~958 KB. 3 diagrams upgraded this batch.

## FIXED THIS BATCH
- PROCESSING (diaProcessing): washed/honey/natural were plain nested ellipses. REBUILT to use the shared realistic
  diaBean (green bean) as the seed, wrapped in the right amount of fruit per process: Washed = bare green bean;
  Honey = bean in a translucent gold mucilage coat; Natural = bean inside a full dark-red dried cherry w/ stem +
  sheen. The "more fruit stays on -> sweeter/fruitier/riskier" progression now reads with real beans.
- ROASTERS (diaRoasters): drum/fluid-bed/hybrid were abstract (circle+dots / floating dots / dashed circle).
  Searched real roaster architecture (Perfect Daily Grind, Scott Rao, Barista Hustle). REBUILT: Drum = horizontal
  rotating CYLINDER on legs with end-cap, tumbling beans, rotation arrow, flame below; Fluid-bed = a spouted-bed
  CONE chamber with beans levitating on upward air jets + heater coil; Hybrid = drum body + recirculating airflow
  LOOP arrows on both sides + flame. Each reads as its real machine.
- POUR-OVER (diaPourover): the 4 step cones were bare outlines. Upgraded to the realistic V60 dripper (rim collar
  + interior spiral ridges + ground bed), consistent with the v61 brew-families V60. Step actions now show:
  Rinse = water sheeting the filter (blue), Bloom = puffed grounds + CO2 bubbles, Pour = water stream from above,
  Draw down = drips into a carafe of brewed coffee. Clear progression.

## PROGRESS on the 19-screenshot audit (DIAGRAM_TODO.md, shipped): Tier A done so far = mokapot, brewfamilies
## (v61) + processing, roasters, pourover (v62). REMAINING Tier A: puckprep, milkdrinks, borerstory cherry.
## Tier B (flow/hierarchy) not started: scapath, cmarket, historytimeline (has text overlap!), vartree (the
## SEPARATE older tree), supplychain. Tier C minor: robustarise, waterchem.

## QA: full regression ALL GREEN (100 learn, 71 diagrams, 36 origins, processing uses diaBean, roasters +
## pourover rebuilt, 0 raw ampersands across 8 checked diagrams). Cache v62. Hard refresh. Pages branch-deploy pending.

## Group counts unchanged: 137 pages, 71 diagram-bearing, ~958 KB. NEXT BATCH: puckprep + milkdrinks (Tier A),
## then start Tier B with historytimeline (fix the FAMOUS DESCENDANTS text collision) + scapath + cmarket.

---

# v63 — Diagram polish batch 3: puck-prep tools + milk-drink vessels made REAL

Continued DIAGRAM_TODO.md. Searched real references first. This finishes the Tier A illustration upgrades except
the borer-story cherry. ~961 KB.

## FIXED THIS BATCH
- PUCK PREP (diaPuckPrep): baskets were bare cone outlines. Searched real puck-prep (Crema, Normcore, CompleteHome
  Barista): sequence Dose -> WDT (8 fine needles) -> Level -> Tamp. REBUILT: real portafilter BASKET (straight
  walls + rim + perforated-bottom dots); Dose = loose mounded grounds; WDT = a handle with fine needle rakes in
  loose grounds; Level = flat even bed; Tamp = cylindrical TAMPER (base + handle) pressing a compressed puck +
  press arrow. Each step now shows its real tool.
- MILK DRINKS (diaMilkDrinks): the 5 drinks were plain layered rectangles. REBUILT as real café VESSELS: cups
  (macchiato/flat white/cappuccino) are rounded with a HANDLE + saucer; glasses (cortado/latte) are handle-less
  tumblers; sizes scale with volume. Espresso/milk/foam layers clipped inside each vessel with a domed foam
  highlight + soft blend line. Reads as real drinks now, not a bar chart. Legend kept.

## AUDIT PROGRESS (DIAGRAM_TODO.md shipped): Tier A DONE = mokapot, brewfamilies (v61), processing, roasters,
## pourover (v62), puckprep, milkdrinks (v63). Only borerstory cherry left in Tier A.
## Tier B (flow/hierarchy) NEXT: historytimeline (has the FAMOUS DESCENDANTS text collision — priority),
## scapath (cert pathway), cmarket (C-price waterfall), vartree (the separate older tree), supplychain.
## Tier C minor: robustarise, waterchem.

## QA: full regression ALL GREEN (100 learn, 71 diagrams, 36 origins, puckprep + milkdrinks rebuilt, 0 raw
## ampersands across 7 checked). Cache v63. Hard refresh. Pages branch-deploy still pending.

## Group counts unchanged: 137 pages, 71 diagram-bearing, ~961 KB. NEXT: borerstory cherry to close Tier A, then
## Tier B starting with the historytimeline text-collision fix.

---

# v64 — Borer-story cherry made real (closes Tier A) + FAMOUS-DESCENDANTS text collision fixed

Searched real references first (per Kevin). ~962 KB. This CLOSES Tier A of the audit and starts Tier B.

## FILE-SAFETY NOTE: during the borerstory edit, a Python str.replace matched a NON-UNIQUE anchor (the
## `<line x1="380" y1="30"...>` divider appears in 3 diagrams) and clobbered build.py (ballooned to 11M lines).
## Recovered instantly by cp-ing the v63 build.py back from /mnt/user-data/outputs (the shipped copy = safety net).
## LESSON reaffirmed: for splices, use unique anchors or explicit LINE-RANGE slicing, never a string that repeats.
## Redid the edit via line-range splice. All 11 prior-fixed diagrams verified intact afterward.

## FIXED THIS BATCH
- BORER-STORY cherry (diaBorerStory LEFT panel): was flat concentric circles. Searched coffee-berry-borer biology
  (Hypothenemus hampei: female ~1.4-1.9mm bores through the cherry TIP, tunnels the seed, builds egg galleries;
  small dark-brown beetle w/ club antennae). REBUILT the cherry as the realistic botanical cross-section (ovoid,
  radial-gradient skin+pulp, two beans + groove, silverskin, gloss, stem) with the borer story on top: bore hole
  at the tip, dashed tunnel curving into the seed, 3 pale egg galleries, and a proper beetle (oblong body, head
  toward the hole, club antennae, legs, elytra seam). Right-side caffeine gut-bacteria cards untouched (read fine).
- SPOTTYPICA (img6 "FAMOUS DESCENDANTS" collision): the two diaCard titles render at y+21, but the body text
  started at y=165 = collided with the title. FIXED: cards taller (80->92), body text pushed to y=184 (clear of
  the y~159 title), canvas H 260->266. Verified 0 text collisions (coordinate test). (Note: the collision Kevin
  saw in img6 was in spottypica, not the separate diaHistoryTimeline which is already clean.)

## AUDIT PROGRESS: TIER A COMPLETE (mokapot, brewfamilies, processing, roasters, pourover, puckprep, milkdrinks,
## borerstory cherry). TIER B remaining: scapath (cert pathway), cmarket (C-price waterfall), vartree (separate
## older tree), supplychain (minor), coffeemap (minor). Tier C: robustarise, waterchem.

## QA: full regression ALL GREEN (100 learn, 71 diagrams, 36 origins, borerstory rebuilt, spottypica 0-collision,
## 0 raw ampersands, all 11 prior diagrams intact). Cache v64. Hard refresh. Pages branch-deploy still pending.

## Group counts unchanged: 137 pages, 71 diagram-bearing, ~962 KB. NEXT: Tier B — scapath + cmarket (both need
## the family-tree/pentagon treatment: solid nodes, curved connectors, spacing).

---

# v65 — Tier B batch 1: cert pathway + C-price waterfall redesigned

Started Tier B (flow/hierarchy diagrams needing the family-tree/pentagon treatment). Searched real references for
each diagram TYPE first (cert-pathway design, waterfall/price-bridge charts). ~963 KB.

## FIXED THIS BATCH
- SCAPATH (cert pathway): had 5 fanned CROSSING straight connector lines + cramped level cards. Searched pro
  cert-pathway/learning-path design (SlideBazaar, Salesforce cert map): clean left-to-right flow, solid color-
  coded nodes, curved connectors, spacing. REBUILT: Intro node -> 5 module cards (CURVED bezier connectors, no
  crossing) -> "EACH AT 3 LEVELS" pill stack -> two credential cards (Diploma, Q Grader), with directional
  arrows guiding the flow. Solid gradient nodes w/ colored top-accent bar (same design language as familytree).
  0 collisions.
- CMARKET (C-price waterfall): was a plain vertical stack of equal translucent boxes w/ tiny arrows + floating
  side notes. Searched waterfall/price-bridge chart design (Wikipedia, Domo, ChartEngine, price-waterfall). The
  point of a waterfall = show the cascading DESCENT. REBUILT as a real visual waterfall: bricks step DOWN and
  NARROW from the C price (full width) to Farmgate (~42% width) so you SEE the farmer\x27s shrinking slice; dashed
  connectors link each step; anchor bricks (C price, Farmgate) emphasized; volatility callout (2025 > $4/lb) kept
  clear on the right. Removed a redundant rotated label that collided. 0 collisions.

## AUDIT PROGRESS: Tier A COMPLETE. Tier B: scapath + cmarket DONE (v65). REMAINING Tier B: vartree (the separate
## older Ethiopian-Arabica tree, still flat boxes), supplychain (minor - already decent), coffeemap (minor).
## Tier C: robustarise, waterchem.

## QA: full regression ALL GREEN (100 learn, 71 diagrams, 36 origins, scapath + cmarket 0-collision, 0 raw
## ampersands). Cache v65. Hard refresh. Pages branch-deploy still pending.

## Group counts unchanged: 137 pages, 71 diagram-bearing, ~963 KB. NEXT: vartree (give the separate older variety
## tree the same family-tree redesign), then supplychain/coffeemap minor polish, then Tier C.

---

# v66 — Tier B: variety tree redesigned (family-tree treatment) + robustarise polish

Continued the audit. ~964 KB.

## FIXED THIS BATCH
- VARTREE (img5, the SEPARATE older Ethiopian-Arabica tree — distinct from the v59 familytree): had flat
  translucent boxes + awkward spacing (Geisha crowding Maragogype). REBUILT with the same family-tree design
  language: solid #241a12 nodes + colored top-accent bar + gradient + shadow, lineage color-coding (Ethiopian
  green, Typica gold-green, Bourbon gold, crosses brown, Catimor hybrid, Geisha pink), curved bezier connectors,
  cleaner spacing, Geisha clearly separated bottom-left ("its own lineage · stands apart"). 0 collisions. Now
  matches the main familytree visually.
- ROBUSTARISE (img10, Tier C minor): bars were fine but the growth read weakly + the "fine robusta" card text was
  one overflowing line. POLISHED: added a baseline axis under the two bars, made the growth arrow emphatic with
  an arrowhead + "+60%" label (was a faint "rising"), and wrapped the fine-robusta card text to two lines (card
  44->48 tall). 0 collisions.

## AUDIT PROGRESS: Tier A COMPLETE. Tier B: scapath, cmarket (v65) + vartree (v66) DONE. REMAINING Tier B minor:
## supplychain (already decent horizontal row), coffeemap (already decent). Tier C: robustarise DONE (v66),
## waterchem (sparse quadrant — last real candidate).

## QA: full regression ALL GREEN (100 learn, 71 diagrams, 36 origins, vartree redesigned + 0-collision,
## robustarise 0-collision, 0 raw ampersands). Cache v66. Hard refresh. Pages branch-deploy still pending.

## Group counts unchanged: 137 pages, 71 diagram-bearing, ~964 KB. NEXT: waterchem (the water-balance quadrant —
## add gridlines/better target framing), then a final look at supplychain/coffeemap to decide if they need
## anything. After that the 19-screenshot audit is essentially complete.

---

# v67 — Water-balance quadrant enriched → 19-SCREENSHOT AUDIT COMPLETE

Final batch of the diagram-polish audit. ~965 KB.

## FIXED THIS BATCH
- WATER (img18, diaWater — the sparse hardness/alkalinity quadrant; NOTE it is diaWater, not diaWaterChem which
  was already clean): was a big empty box + target rect + 4 corner labels. ENRICHED: dark plot frame with faint
  quarter GRIDLINES, a soft green radial GLOW radiating from the target sweet-spot, a bolder TARGET box, real
  AXES with arrowheads (Hardness \u2192 / Alkalinity \u2192), and the 4 corner labels each given a colored dot (chalky
  grey, scaly red, sour gold, sharp green). Now reads as a proper 2D balance chart. 0 collisions.
- SUPPLYCHAIN + COFFEEMAP: reviewed both (Tier B/minor). Both already read cleanly (supplychain = even 5-stage
  Farmer\u2192Caf\u00e9 row w/ arrows; coffeemap = the dashed-arc spread journey). LEFT AS-IS deliberately — forcing
  changes on working diagrams just adds noise (the standing principle from the start of this audit).

## ===== 19-SCREENSHOT DIAGRAM AUDIT: COMPLETE =====
## Tier A (make it look real): mokapot, brewfamilies, processing, roasters, pourover, puckprep, milkdrinks,
##   borerstory cherry \u2014 ALL rebuilt from real references (v61-64).
## Tier B (flow/hierarchy): scapath, cmarket, vartree \u2014 redesigned w/ family-tree treatment (v65-66);
##   spottypica text collision fixed (v64); supplychain + coffeemap reviewed & left clean (v67).
## Tier C (minor): robustarise (v66), water quadrant (v67).
## Plus earlier in the arc (v55-60): real Natural-Earth maps, region dots, latte art, shared realistic diaBean
##   (both defect galleries), family tree, profiling pentagon, cherry, grind, particlesize, +37 ampersand-bug fixes.
## FINAL SWEEP: all 21 reworked diagrams verified 0 raw ampersands + 0 text collisions.

## QA: full regression ALL GREEN (100 learn, 71 diagrams, 36 origins). Cache v67. Hard refresh.
## ONE OUTSTANDING USER ACTION: GitHub Pages "Deployment failed" \u2014 fix is Settings \u2192 Pages \u2192 Source \u2192
## "Deploy from a branch" (main /root). Until then Kevin\u2019s phone shows v54; ALL of v55\u2013v67 is invisible to him.

## Group counts unchanged: 137 pages, 71 diagram-bearing, ~56,500 words, ~965 KB.
## NEXT possible arc (when Kevin wants): the APPLICATIONS phase (interactive brew calc, roast timer, cupping form,
## dial-in troubleshooter) \u2014 logged from earlier. Reference content remains DONE; do not expand.

---

# v68 — heat-transfer diagram rebuilt (the last unchecked TODO item)

Kevin noticed 2 unchecked boxes in DIAGRAM_TODO.md. Audited both:
- vartree line = a STALE DUPLICATE note (vartree was actually rebuilt in v66). Cleaned up.
- heat (img9) = genuinely never touched (I had flagged it "decent, minor"). Since Kevin screenshotted it, FINISHED it.

## HEAT (diaHeat) rebuilt: was an abstract drum circle with beans in a ring + 3 thin arrows. NOW: heavy metal
## drum WALL ring with a hot-red inner glow (radial gradient), beans PILED at the bottom like a real drum,
## and the 3 heat modes made visually distinct — Conduction (short bold red arrow from wall into a touching
## bean), Convection (flowing gold air arrows curving up through the bean mass), Radiation (wavy orange infrared
## lines beaming inward from the wall). Wrapped legend kept. 0 collisions, 0 raw ampersands.

## DIAGRAM_TODO.md now 0 unchecked. The 19-screenshot audit is fully complete (Tiers A/B/C all done).
## QA ALL GREEN. Cache v68. Hard refresh. Pages branch-deploy still the one outstanding user action.
## Group counts unchanged: 137 pages, 71 diagram-bearing, ~965 KB.

---

# v69 — review-round fixes: &AMP; kicker bug, duplicate Water Chemistry, profiling overlap, latte contrast

Kevin reviewed the whole app on v68 (finally deployed! screenshots show v68 not v54). Overall very happy. Found:

## REAL BUGS FIXED
- **&AMP; kicker bug (affected MANY pages):** section kicker on Learn articles rendered "BREWING &AMP; BARISTA"
  (imgs 19/20). Root cause: group labels in METH_GROUPS/METH_CHAPTERS were stored PRE-escaped as "&amp;", then
  esc() escaped them AGAIN at render (line ~3970 `<div class="lvl">${esc(glabel)}</div>`) → &amp;amp; → literal
  &amp; → uppercased to &AMP;. FIX: changed 5 label defs from &amp; to plain & (Green Buying & QC, Cupping &
  Quality, Brewing & Barista, Tasting & Quality, Brewing & Business) AND added esc() to the raw methCard tag span
  (line 1031). Verified kicker now renders "Brewing & Barista". NOTE: the &amp; INSIDE svg <text> (pourstroke
  step labels, puckprep) is CORRECT and renders as & in-browser — those were not touched.
- **Duplicate "Water Chemistry" page (img2):** two entries both titled "Water Chemistry / The 98% ingredient" —
  brew_water (older, 1970 chars, diagram=water) and brew_waterchem (rewrite, 3511 chars, GH/KH framing,
  diagram=waterchem). The old brew_water was a leftover that should have been retired. FIX: deleted brew_water,
  repointed ALL its references (nav order + related links, 5 spots) to brew_waterchem, deduped. Learn count
  100→99, pages 137→136. Water Recipes (brew_waterrecipe) is a DISTINCT article, kept.

## POLISH
- **Profiling loop (img15):** "Sample roast"/"small batch" sub-labels overlapped the "THEN SCALE UP" card.
  Tightened pentagon (cx 250→224, rx 150→132), shortened two right-side sub-labels ("small batch, vary the
  curve"→"small batch"; "score blind, note flaws"→"score blind"), moved card to a clear right column. 0 collisions.
- **Latte art / pourstroke (img3):** "better but not great" per Kevin. Brightened the milk gradient (→ #fffdf7
  near-white) and deepened the crema gradient for stronger white-on-brown CONTRAST so the finished heart/rosetta/
  tulip pop more. Shapes are parametric + legible; detail is limited at ~120px/cup. May revisit if Kevin wants
  the finished patterns bigger/crisper.

## STILL OPEN (Kevin flagged, not yet done — mostly alignment, some real):
- img8 aromachem: italic caption overlaps the Sulfur cmpds bottom row.
- img12 particlesize: legend near FINES label; y-axis "of particles" clipped at left; curves could fill/separate better.
- img3 mokapot: leader-line labels collide with pot body / numbers sit on the metal.
- Latte art finished designs could still be crisper (Kevin: "some final designs don't look final").

## QA ALL GREEN (99 learn, 70 diagrams, 36 origins, 1 Water Chemistry, clean kicker, profiling 0-coll). Cache v69.
## ~963 KB. Pages IS deployed now (v68 was live). NEXT: work through the remaining flagged alignment items.

---

# v70 — full review sweep: ALL 23 screenshots + ALL 70 diagrams addressed

Kevin: "keep going with the polish on all 23 — you only focused on a few." Correct. Did a SYSTEMATIC pass:
built REVIEW_TODO.md from every screenshot, then ran an automated collision+edge-clip+ampersand sweep across all
70 diagrams to find real issues objectively (not just eyeballing).

## FIXED THIS ROUND
- **waves (img1):** wave cards (1st-4th staircase) had labels spilling below the short cards onto the axis dots.
  Reworked: min bar height 58px so number+name always fit inside; detail line only on tall cards (barH>=88).
- **aromachem (img8):** italic caption overlapped the Sulfur cmpds bottom card. H 250->262 for clearance.
- **particlesize (img12):** y-axis "# of particles" was clipped off the left edge. Rotated it vertical along the
  y-axis (like the water quadrant). ALSO filled both distribution curves (blue unimodal + orange bimodal) so they
  read as distinct — was just outlines before.
- **mokapot (img3-set1):** chamber labels (3/2/1) collided with the pot body + leader lines crossed it. Moved all
  labels to a clean column RIGHT of the pot (left-anchored, x=272), short leader lines from the pot edge, never
  crossing the body. Numbers now on labels, not on the metal.
- **milk steaming (img19):** "60°C" and "65°C" ticks overlapped at the right end. Dropped the redundant 60° tick,
  kept "65°C stop" (the meaningful one; caption already explains it).

## MAJOR BUG (bigger than the 2 screenshots showed): literal &amp; leaks.
  The v69 fix caught 5 group labels but the double-escape (esc() over a pre-escaped &amp;) also hit: the "Growing
  & Origin" group label (15 grow-group pages!) and the guided-path "Next:" labels ("Varietals & Cultivars",
  "First & Second Crack"). Fixed all at source. VERIFIED: now ZERO literal &amp; anywhere in the entire app
  (all 136 pages + every nav view scanned).

## VERIFIED CLEAN (full 70-diagram sweep, no changes needed): familytree, geishastory, cherrybyproduct, machtypes
  (boiler), grinder, milkstretch, coffeemap, supplychain, heat, roasters, robustarise, instantcoffee, roastdefects,
  coldbrew, milkdrinks, waterrecipe, pourstroke, flavorwheel, caffeine, acidmap, + all others. The collision-test
  false-positives (adjacent label+description pairs) were visually confirmed fine.

## QA ALL GREEN (99 learn, 70 diagrams, 36 origins, 6 flagged diagrams 0-collision, ZERO literal &amp;). Cache v70.
## ~963 KB. The 23-screenshot review is now fully worked through.

---

# v71 — country maps sharpened: 2-3x point density (fixes the last spikiness)

Kevin: maps "MUCH better but some still a little spiky — consider doubling/tripling points, esp. islands."

## ROOT CAUSE: the silhouette simplification used a FIXED degree-based tolerance (tol=0.35 mainland, 0.06-0.18
## islands). A fixed degree tolerance is huge relative to a small country: Jamaica (~1.5° span) collapsed to 7-15
## points while Brazil (~40° span) kept 83. Too few points = the Catmull-Rom smoother has nothing to round, so
## sharp vertices stay spiky. Islands were worst (Jamaica 15, Bali 15, Timor 14, Yemen 10, Zimbabwe 10, Uganda 12).

## FIX: switched to SPAN-RELATIVE tolerance (tol = bbox_span * frac). Now every country keeps a comparable NUMBER
## of vertices regardless of physical size. frac=0.006 mainland, 0.004 islands, 0.003 Bali (finest).
## Updated BOTH gen_silhouettes.py AND gen_with_dots.py (they must match so dots project onto the same shape).

## RESULT: avg points 35 -> 72; nobody below 30 now (was 7-15). Jamaica 15->30, Timor 14->33, Bali 15->35,
## Yemen 10->42, Zimbabwe 10->50, Ethiopia 21->53. Verified smooth via ASCII renders (Jamaica/Ethiopia/Yemen/Bali
## all read as natural coastlines, no jagged spikes). All 124 region dots still place correctly (0 out of bounds),
## all 36 origins render with silhouettes + dots.

## Pipeline (in /home/claude/coffee, synced to outputs): gen_silhouettes.py (span-tol) -> real_silhouettes.json;
## gen_with_dots.py (matching span-tol) -> region_dots.json; then injected into build.py COUNTRY_SIL + REGION_DOTS
## blocks. To sharpen further: lower the frac values (e.g. 0.004 mainland) and rerun both + reinject.

## Size 963 -> 1003 KB (~40 KB for the extra coastline detail; still one ~1MB offline file). QA ALL GREEN
## (99 learn, 70 diagrams, 36 origins+silhouettes+dots). Cache v71.

---

# v72-v76 — FULL 19-image review pass (all 20 checklist items done)

Kevin (rightly) called out that I keep fixing one thing and stopping. Built PASS_CHECKLIST.md with every item first,
then worked ALL of them across v72-v76, shipping incrementally so progress was saved each step.

## CENTERING / OVERLAP FIXES
- caffeine/TeaCoffee (img2): COFFEE word overflowed its circle + vs off-center. Moved words BELOW icon circles,
  centered vs at the true midpoint (180+560)/2=370.
- supplychain (img4): Farmer/Mill/etc labels sat high in circles. Centered vertically (cy+5). Fixed 2 &amp;.
- familytree (img5): "stands apart" caption was at x=470 overlapping the Timor node; it describes Geisha (x=70).
  Moved it under Geisha. Fixed Timor &amp;.
- species (img6): centered the ARABICA/ROBUSTA vs badge; fixed "hot & low" &amp;.
- profiling (img13): "Green / assess density" sub-label overlapped the ring. Pushed the top-node label to p-40.
  Fixed scale-up card &amp;.
- milkstretch (img17): 60/65C ticks crowded (done earlier v69) + moved "70C+ scalds" danger label clear of edge.

## ARROW FIXES
- instantcoffee (img12): branch arrows now fan symmetrically from the card center-bottom (Q-curves) to each method.
- geishastory (img7): journey arrows were 13px stubs floating in the gaps; now span the full gap between cards.
- spotworkhorse/caturra (img8): respaced the lineage chain evenly (40/235/430) + arrows span gaps + added arrow
  to the Everyday card.
- robustarise (img11): moved the +60% growth label clear of the bar numbers ("+60% growth" above the arc).

## REDESIGNS (searched real refs first per Kevin standing rule)
- roasters (img10): abstract blobs -> real machines. Drum = round body+door+hopper+chimney+legs+flame; Fluid-bed
  = vertical column roaster w/ base+coil; Hybrid = drum + air-recirc duct loop.
- coldbrew (img16): removed the arrow-to-nowhere. Now two real glasses -- iced-coffee tumbler (ice cubes+straw)
  and cold-brew jar (blue lid rim, steeping grounds) with a "HEAT?" divider badge.
- cherrybyproduct (img9): flat concentric circles -> realistic botanical cross-section (skin/pulp gradients, two
  beans w/ groove, silverskin, gloss, stem). skin/pulp/beans labels moved OUTSIDE with leader lines.
- milkdrinks (img20): uniform mugs -> DISTINCT real vessels per drink: Macchiato demitasse, Cortado tumbler,
  Flat White tulip cup, Cappuccino wide bowl, Latte tall glass. Increasing size L->R, correct esp/milk/foam layers.
- machtypes (img15/19 boilers): abstract text boxes -> real plumbing schematic. Metal boiler cylinders + group
  heads + brew pipe (HX). Single/HX/Dual configs.
- coffeemap (img1): "doesn't make sense" -> numbered 1->5 journey (Ethiopia->Yemen->Europe->Java->Americas) with
  faint landmass hints for geographic context + ordered dashed arrows.
- tastemap (img14): umami spilled below the TONGUE circle. Enlarged circles (r70), fit the 5-item list inside.
- pourstroke latte art (img18): enlarged the finished hero cups (RF 29->37) and pattern fill (heart 0.74*RF,
  fuller rosetta/tulip) so the heart/fern/tulip read clearly. (Milk brightness/contrast already boosted v69.)

## waves (img3): brightened the detail text (#d8c8b0 size 10) for legibility over the card gradient.

## QA: full regression ALL GREEN across v76 (99 learn, 70 diagrams, 36 origins+silhouettes, ZERO literal &amp;).
## Only "collisions" flagged are false positives (side-by-side brew/steam boiler labels). Cache v76. ~1012 KB.
## PASS_CHECKLIST.md = 0 pending. Every one of the 20 flagged items addressed.

---

# v77 — realism audit: found & upgraded the last "real object drawn as a box"

Kevin: go through the whole site, find anything still using stock text-boxes/basic shapes for something that is a
REAL physical object (like the moka pot / roasters were), and make it look real. Audited all 70 diagrams:

## FIXED
- espresso (the 1:2 ratio diagram): the "portafilter" was a plain rounded rectangle labeled 18g and the cup was a
  bare trapezoid labeled 36g. REDESIGNED both as real objects: a proper stainless PORTAFILTER (tapered basket +
  rim + coffee puck w/ grounds texture + spout + handle, metal gradient) and a real ESPRESSO CUP (curved body,
  espresso fill + crema band, handle, saucer). Still reads as the 1:2 ratio but now looks like actual gear.

## AUDITED, CONFIRMED ALREADY-REAL (no change needed): mokapot, roasters, brewfamilies (V60/press/portafilter),
## milkdrinks (5 real vessels), coldbrew (2 glasses), cherry + cherrybyproduct (botanical cross-sections),
## machtypes (boiler schematic), puckprep (real baskets), grinder (burr geometry), pourover (cones w/ drips),
## roastdefects/greendefects (realistic beans), bean galleries.

## AUDITED, CONFIRMED CORRECTLY ABSTRACT (charts/flows/comparisons — NOT single objects, boxes are right):
## extraction (spectrum bar), staling (freshness curve), dialring (recipe dial), decaf/decafmethods/fermentmethods
## (method comparison cards), blend (component mix), espmachine (water-path flow stages), supplychain, waves,
## cmarket, acidmap, particlesize, aromachem, all the lineage/tree/journey flows.

## QA ALL GREEN (99 learn, 70 diagrams, 36 origins+silhouettes, zero literal &amp;). Cache v77. ~1014 KB.

---

# v78 — bean-render pass: green defects + embedded icons I passed over

Kevin: one more pass — (1) find diagrams with small embedded images I skipped (like decaf methods) and spruce them,
and (2) the green coffee defects still need work on the actual render. Did BOTH.

## (1) GREEN COFFEE DEFECTS — improved the shared diaBean() green path + weak overlays:
- Green beans now read distinctly from roasted: flatter/more MATTE gradient (less gloss), and a wider, brighter
  SILVERSKIN-lined center crease (pale) — the characteristic look of green coffee where silverskin sits in the cut.
- Strengthened the defect overlays: sour = deeper reddish-brown mottling (not a flat wash); immature = pale-green
  body + prominent clinging silverskin down the crease + at the end; insect = deeper borer holes w/ tiny rim
  highlights; broken = exposed pale inner face w/ fracture lines; floater = faded low-density wash; fungus =
  layered mold blotches. Full-black / partial-black / shell unchanged (already read well).
- Verified roast-defect gallery still renders correctly (roast path of diaBean untouched).

## (2) EMBEDDED ICONS I PASSED OVER:
- decafmethods: the shared-start "green beans" was a flat colored disc with text. Now a REAL green bean (diaBean)
  sitting in a soft halo.
- decaf (the 3 method circles): each had a crude ellipse+S-line "bean". Now a REAL green bean inside each circle
  with caffeine dots escaping outward.
- Audited borerstory (cherry cross-section) + ruststory (leaf progression) — already real illustrations, left as-is.

## QA ALL GREEN (99 learn, 70 diagrams, 36 origins+silhouettes, zero literal &amp;, roast+green defect galleries
## both render). Cache v78. ~1015 KB.

---

# v79 — diagram-polish pass: bean shading overhaul, correct latte-art shapes, HX cutaway, arrow/label cleanups

Kevin sent 10 screenshots (all needing work): SCA cert path, latte-art pours, milk stretch/texture, espresso
boiler configs, roast-defect gallery, instant coffee, roaster types, processing methods, green-defect gallery,
variety family tree. Directive: research the real reference for EACH before redrawing; give each its own
treatment; don't skip any. Latte art flagged as needing the most work + online research.

## SHARED diaBean() — full anatomy + shading overhaul (fixes roast-defect, green-defect, processing, decaf at once)
- Egg-shaped body (one end slightly broader) instead of a symmetric oval — real coffee-seed proportion.
- REAL center-cut VALLEY: a thin dark closed ribbon down the Arabica-wavy seam (a `<linearGradient>` cut fill),
  not just a stroke — reads as depth. A lit silverskin edge catches the top-light on one side.
- Layered shading: 5-stop body radial offset up-left + an inner ambient-occlusion rim (scaled dark stroke) +
  a top-left specular sheen patch (its own radial). Beans now read as rounded solids, not flat discs.
- Green vs roast: green = cooler matte body + brighter/wider clinging silverskin; roast = deeper crease +
  thin dry silverskin trace + glossier sheen.
- Base GREEN color shifted olive → cooler dense sage (#66805c) to match "even blue-green, dense" (per SCA refs).
- Defect overlays rebuilt to match real references (mtpak / Royal Coffee / Green Coffee Collective):
  sour = reddish-brown mottle + reddish silverskin; immature = pale yellow-green + shiny clinging silverskin;
  insect (borer) = several deep holes with bored rims; broken = clean pale exposed inner face; fungus = powdery
  yellow→reddish-brown blotches; scorch/tip/face/oil strengthened.

## LATTE ART (diaPourStroke) — rebuilt heart / rosetta / tulip from real pour tutorials
Researched Verve, Barista Hustle, Artisti, Lattiz, Bazan, European Coffee Trip + finished-shape photos.
- ROSETTA: was stacked fish-scale bands. Now a central spine with symmetric SICKLE LEAVES fanning both sides,
  bulging mid-cup and tapering top+bottom (sinusoidal width), each a flat shallow crescent so rows stay
  SEPARATE with crema showing between, capped by a small rounded head, finished with a straight cut-through.
  Verified via scanline analysis: distinct leaf pairs at every level, clean central gap.
- TULIP: was blobby crescents. Now STACKED CHEVRON PETALS pushed forward — widest at the base, each smaller
  going up (per "stop, push, stack" technique), a round bloom on top, a stem/point pulled through the bottom.
- HEART: kept, removed the odd internal pour-rings, added a soft inner shade + single clean pull-through.
- Step cups (2 & 3 of each row) now show correct partial pours building toward the hero.

## HX ESPRESSO BOILER (diaMachTypes) — the "odd middle" — redrawn as a real cutaway
Researched home-barista.com, Bella Barista, 1st-line, Seattle Coffee Gear. The HX is ONE boiler, partly water /
partly steam, with a brew pipe (HX tube) traversing the water: cold in at the bottom, absorbs heat rising
through, hot out the top to the group; steam drawn off the top. Redrew all 3 cells as metal-shell cutaways with
a visible water/steam split (blue water fill, steam space + rising bubbles): single = one hot boiler feeding
group OR wand; HX = boiler + inverted-U brew pipe threading the water with cold-in→hot-out arrows + top wand;
dual = two separate boilers (brew hot, steam). Much clearer than the old crammed arc + label.

## ARROW / LABEL / LAYOUT cleanups
- SCA cert path: levels→credentials was two arbitrary arrows (top/bottom pills only). Now a collecting bracket
  gathers all 3 levels → two clean fan-out arrows to both credentials. Clearer "complete levels → both open."
- Milk stretch/texture: cleaner tapered pitchers w/ real spout + handle; STRETCH shows a foam ridge + air
  bubbles + "tsss" wand near the surface; TEXTURE shows a submerged wand + a proper whirlpool spiral arrow.
- Instant coffee: symmetric elbow branch arrows (were lopsided quadratics); added small powder-mound vs
  crystalline-granule icons so the two methods aren't text-only.
- Processing: clearer progressive fruit coats (bare seed → sticky gold honey coat w/ drip highlights →
  enclosed dried cherry w/ a seed-window cutaway + shrivel wrinkles); real bean depth inside each.
- Roaster types (drum/fluid-bed/hybrid): reviewed — already real machines + physically distinct; left as-is.
- Family tree: reviewed connectors; readable, left the layout.

## LATENT BUG FIXED: bare `&` in SVG <text> (10 spots)
Found bare ampersands in diagram data strings that render into SVG text (malformed XML, browser-tolerated but
wrong): boiler captions (switch & wait, etc.), supply-chain (grows & picks / roasts & sells), tea-coffee
(Morning & / All-day &), species (hot & low), family-tree (Catimor & Sarchimor), profiling (& airflow).
Changed to "and". Consistent with the app's zero-literal-&amp; rule. All 12 touched diagrams now validate as
well-formed XML; zero &amp;amp; double-escapes; zero &AMP;.

## QA (99 learn, 70 diagrams, 36 origins+silhouettes; roast+green galleries both render; all shapes verified via
## scanline analysis + XML validation). Cache v79. ~1020 KB.

---

# v80 → v82 — multi-file architecture + raster illustrations begin

## Decision: the app is no longer a single self-contained HTML file
Kevin's call (this session): offline/single-file is NOT a priority for CIG (unlike the CQV app). Most
users are online and it auto-updates like LTB. So we switched to a **multi-file** app so diagrams that need
to look photographic can be real raster PNGs instead of hand-drawn SVG.

**What deploys now (all of it, together — not just index.html):**
  index.html, sw.js, manifest.webmanifest, icon.svg, and an **img/** folder of PNGs.
Deploy = drop the whole set at the repo root. CIG_v82_deploy.zip contains exactly this.

**How it works in build.py:**
  - `IMG_ASSETS` list at the top names the PNGs.
  - Build copies `img_src/*.png` → `img/` and injects `./img/<f>` into the service-worker ASSETS precache.
  - `diaImg(file,cap,alt)` helper (next to diaWrap) emits `<figure class="diagram diagram-img"><img …>` —
    same figure/caption shell as SVG diagrams. CSS: `.diagram-img img{width:100%;height:auto;border-radius:8px}`.
  - To convert any diagram to raster: add the PNG to img_src/, add its name to IMG_ASSETS, and change its
    dispatch case from `return diaXxx();` to `return diaImg('xxx.png', '<caption>', '<alt>');`. The old SVG
    function stays in the file (unused) so nothing is lost.
  - Source generators live alongside build.py: `gen_placeholders.py`, `gen_defects.py` (Pillow, supersampled).

## Converted to raster so far (4 diagrams)
  - **latteart.png** (pourstroke) + **roasters.png** — currently CLEAN PLACEHOLDERS ("art pending" cards).
    The hand-SVG versions were the ones Kevin kept (rightly) rejecting; parked behind placeholders until real
    art can be made AND VERIFIED. Scaffold is done; dropping real art in is now mechanical.
  - **greendefects.png** + **roastdefects.png** — REAL raster art generated this session via gen_defects.py.
    Pillow renderer with radial shading, fine noise texture, soft-edged blotches, real cut/hole depth, per-defect
    overlays grounded in SCA refs (mtpak, Royal Coffee, Green Coffee Collective, PDG, Loring, Giesen). 9 beans each,
    3×3, CAT 1/2 tags on green. Colors verified by pixel-stats (full-black ~ (15,10,7); sour reddish-brown;
    quaker pale tan; overdeveloped dark ~ (39,30,24)). **NOT visually verified** — see caveat below.

## ⚠️ STANDING CAVEAT: the image preview tool was broken this entire session
Every render came back blank in the viewer (confirmed with plain PIL test images too). So the defect galleries
and any future raster art are validated only by pixel-statistics + XML/structure checks, NOT by eye. This is the
exact failure mode that produced the earlier "garbage" latte art. Kevin now views the live site
(https://stucky602.github.io/Coffee/) and is the visual judge. If the defect beans look off, regenerate via
gen_defects.py (tweak colors/overlays) — do NOT ship more blind raster art claiming it's verified.

## SVG diagram fixes still in this build (from the prior v80 pass, retained)
  Milk-drinks glassware rebuilt (latte = wide bowl cup, not a tall glass; real bases not floating coins);
  SCA path bracket spans the true pill centers; origin-map arrows stop at dot edges; waves descriptors wrap
  inside cards; family-tree viewBox widened to 940 (right column no longer clipped) + Geisha caption centered;
  roaster drum rotation arrow made concentric + hybrid recirc duct clears the base. (Roasters SVG is now moot —
  replaced by placeholder PNG — but the fixes remain in the unused function.)

---

# RASTER-CANDIDATE BACKLOG (audit of what should move to outside images vs stay SVG)

Kevin's guidance: origin country maps look great (leave), coffee cherries look nice (leave). Beans FOR SURE.

## DONE / SCAFFOLDED
  [x] greendefects  — real raster (this session)
  [x] roastdefects  — real raster (this session)
  [~] latteart (pourstroke) — placeholder; real art pending viewer
  [~] roasters — placeholder; real art pending viewer

## TIER 2 — organic objects, clear payoff (do next, once viewer works)
  [ ] processing — washed/honey/natural: the SEED inside each fruit coat is a drawn bean; real green seed reads better
  [ ] milkdrinks — the 5 vessels (macchiato→latte). Borderline object-art; my SVG cups have been the sore spot.
                   A clean illustrated vessel set would beat vector. Arguably promote to Tier 1.

## TIER 3 — real equipment; photos would look nicer but SVG schematics are functional (optional)
  [ ] espresso (ratio) — portafilter + cup objects
  [ ] grinder / burrs, mokapot, espmachine — real gear; current schematics teach fine
  [ ] blend — if it depicts beans as components

## FEATURE-ADD (currently text-only trait cards; a real bean/plant photo would enrich, not fix)
  [ ] variety spot cards: spotsl28, spotbourbon, spotpacamara, spotmaragogipe, spottypica, spotworkhorse

## STAY SVG (schematic/data/flow — vector is correct, looks sharp)
  roastcurve, phasebar, dtr, cracks, heat, extraction, flavorwheel, cva, water, brewfamilies, supplychain,
  waves, vartree, pourover, coldbrew, troubleshoot, decaf, coffeemap, caffeine(+science), tastemap, acidmap,
  waterrecipe, puckprep, staling, dialring, milkstretch, maintenance, aromachem, scapath, teacoffee, machtypes,
  waterchem, cmarket, climatecoffee, historytimeline, familytree, speciesmap, decafmethods, instantcoffee,
  esphistory, geishastory, particlesize, robustarise, ruststory, borerstory, profiling, fermentmethods, dtr.

## EXPLICITLY LEAVING ALONE (Kevin's call)
  origin country maps (generated silhouettes — look great); cherry + cherrybyproduct (cross-section diagram
  beats a photo because the layers are labeled).

## QA v82: 4 raster diagrams wired + precached; versions synced (APP_VERSION v82 / cache coffee-guide-v82);
## multi-file deploy confirmed (index.html + sw.js + manifest + icon + img/). ~1020 KB html + 4 PNGs.
