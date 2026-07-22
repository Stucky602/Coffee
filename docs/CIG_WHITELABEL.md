# CIG_WHITELABEL — the house-layer boundary + flag taxonomy
### Fable architecture artifact #4 · supersedes the ad-hoc flag notes in CIG_ARCHITECTURE_HANDOFF §3

**The question this settles:** how does ONE codebase ship as (a) the neutral generic guide,
(b) the Proud Mary house build, (c) some-other-roaster's build later — without the identities
bleeding into each other or the boundary calcifying wrong?

**The answer is three layers, and the load-bearing call is which layer each decision lives in.**

---

## 1. THE THREE LAYERS

### L0 — BUILD IDENTITY (which data compiles in)
A `HOUSE` constant in `build.py` (today implicitly `'pm'`) decides **what data exists in the
artifact at all**: whether `data_offerings.json` loads, which house block ships, brand strings in
`<meta>`/OG/manifest. A neutral export (`HOUSE=None`) contains NO PM data — not hidden, absent.
A future other-roaster build points at a different catalog file.

**Why identity is build-time, not a runtime flag:** a white-label build for another roaster must
not carry PM's lots, stories, and recipes in its payload where view-source finds them. Different
identity = different artifact. Runtime flags hide UI; they cannot un-ship data.

### L1 — RUNTIME FEATURE FLAGS (`CIG_FLAGS` + `ff()`, what's VISIBLE)
Exactly today's proven mechanism: dark by default, `?ff=` preview, one-line flip to go live.
Flags gate FEATURES within whatever house the build is. Naming rule: generic features unprefixed
(`cvatool`, `brewcompare`); house-scoped features prefixed (`pm_dialin`, `pm_onboarding`).
**Consistency rule:** a house-prefixed flag must no-op cleanly when its house data is absent —
which the code already does for free, because every pm_ feature reads catalog data that a neutral
build simply doesn't contain. (v101's `?c=` boot check demonstrates the pattern: flag off OR data
absent ⇒ fall through to home.)

### L2 — CONTENT KEYS (where house words live in data)
House content lives ONLY in: `data_offerings.json` (the whole file is house data), the `house{}`
block, and — the one legacy exception — **four audited PM touchpoints in otherwise-generic
content:** the `origin_panama` sentence, the `origin_nicaragua` sentence, the `<meta description>`,
and the OG-card/footer line. These four route through the `pm()` helper (§2). Nothing else in the
136 pages is PM-branded (verified by grep in the architecture audit). New house content NEVER goes
inline in generic pages — it goes in house data keys, rendered by house-gated sections.

---

## 2. `pm_house` — REDEFINED PRECISELY (it was ambiguous; now it isn't)

`pm_house` is **the voice/branding toggle WITHIN the PM build** — NOT the white-label switch
(that's L0). When built (Option A from the architecture handoff, an Opus task, ~30 lines):

- Add `function pm(text){ return ff('pm_house') ? text : ''; }` (build-time equivalent fine too).
- Route exactly the four audited touchpoints through it. **Do not delete the PM sentences** —
  Kevin's standing rule; the goal is toggleable, not removed.
- Semantics after: `pm_house` OFF ⇒ the PM build READS neutral (today's live experience,
  unchanged); ON ⇒ PM voice + footer promotion + house links surface.
- Feature flags stay independent of `pm_house` — `pm_dialin` can demo without the full brand
  switch. This is already how the pitch links work (`?ff=pm_dialin&ff=pm_trace`); keep it.

Default when PM signs off: `pm_house:true` in the PM build. Until then it ships dark like
everything else.

## 3. FLAG LIFECYCLE
`reserved` (name + comment in CIG_FLAGS, no code) → `built-dark` (code gated, flag false, jsdom
proof both states) → `live` (true + version bump + tiny ship) → `retired` (feature unconditional,
flag deleted — don't hoard dead flags; when a feature has been live and stable for a while, remove
its gate).
Current census (v101): built-dark = cvatool, pm_dialin, pm_trace · reserved = everything else.
The README's flag table is the single source of truth; update it every ship that changes a state.

## 4. THE NEUTRAL-EXPORT CHECKLIST (when someone actually asks for one)
1. `HOUSE=None` in build.py ⇒ skip catalog load, `pm()` yields '', neutral meta/OG/footer strings.
2. Build; grep the artifact: zero case-insensitive "proud mary" hits (the audit grep, mechanized).
3. jsdom: pm_ flags via `?ff=` render nothing (no data ⇒ no-op — rule L1 verified, not assumed).
4. Separate repo/Pages target; independent version line.
Do not build this until there's a real second customer for it — the checklist existing is the
insurance; running it early is speculative work.

## 5. WHAT THIS SETTLES (so it doesn't get relitigated)
- Identity is build-time; visibility is flag-time; house words live in house keys. One sentence,
  three layers, every future decision routes to one of them.
- The current live deploy is: **house='pm' build, all flags dark** — which is why it reads neutral
  today and why the pitch can flip features on with a URL. That duality is a feature; keep it.
- The ordering app, if ever, is outside all three layers (external reader of the catalog —
  CIG_DATA_MODEL §3). No flag reserved for it, deliberately.
