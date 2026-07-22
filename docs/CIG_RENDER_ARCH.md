# CIG_RENDER_ARCH — one coffee, many surfaces
### Fable architecture artifact #2 · design spec (Opus builds against this)

**The problem:** the SAME resolved coffee record must render as (a) a wholesale dial-in page,
(b) a retail "what am I drinking" page, (c) an onboarding lesson embed, (d) a printed grower-story
card, and eventually (e) an ordering surface. Five divergent view functions would each drift; one
context-aware renderer keeps them coherent. **The current `coffeeDialInView` is secretly already
`render(coffee, 'wholesale')` — this spec names that fact and generalizes it.**

---

## 1. THE DESIGN: sections × contexts

Two small registries, both plain data + pure functions. No framework.

### 1.1 Section registry
Each section is a pure function `(o) → html-string` over ONE resolved coffee record
(cig-catalog/1, post-resolution — producer/tier are objects). Sections render `''` when their data
is absent or their gating flag is off. **Every section already exists inside today's
`coffeeDialInView` as an inline chunk; the refactor is extraction, not invention.**

| section id | content | data it reads | flag gate |
|---|---|---|---|
| `secIdentity` | eyebrow + name + origin·variety·process·roast line | name, origin, variety, process, roast | context supplies the eyebrow text |
| `secNotes` | tasting-note chips | notes[] | — |
| `secStory` | lotNote ¶ + producer story ¶ + producer line | lotNote, producer.{story,name,farm,region,altitude} | `ff('pm_trace')` |
| `secEspresso` / `secBatch` / `secHome` | dial-in cards (the row() pattern) | dialin.* | — |
| `secDialNote` | the "every bag drifts; re-dial" keypoints box | dialinNote | — |
| `secTroubleshoot` | sour→finer / bitter→coarser chip | static | — |
| `secTierCTA` | tier name + blurb + subscribe link | tier.{name,blurb,subscribeUrl}, house.links | `ff('pm_offerings')` |
| `secDeepLinks` | Learn-more chips into METHODOLOGY (+ producer.originPage chip when present) | producer.originPage | — |

### 1.2 Context registry
A context = an ordered list of section ids + chrome (back button, eyebrow label, wrapper class).

```js
var COFFEE_CONTEXTS = {
  wholesale: { eyebrow:'WHOLESALE DIAL-IN', back:'Full guide',
               sections:['secIdentity','secNotes','secStory','secEspresso','secBatch',
                         'secHome','secDialNote','secDeepLinks'] },           // ≡ today's view, exactly
  retail:    { eyebrow:'WHAT YOU\'RE DRINKING', back:'Full guide',
               sections:['secIdentity','secNotes','secStory','secHome',
                         'secTierCTA','secDeepLinks'] },                      // ff:pm_menu — home recipe leads, no bar numbers
  lesson:    { eyebrow:'ON THE BAR TODAY', back:null,  chrome:'embedded',
               sections:['secIdentity','secNotes','secEspresso','secDialNote'] }, // onboarding practical embed
  card:      { eyebrow:null, back:null, chrome:'print',
               sections:['secIdentity','secStory'] }                          // ff:pm_cardgen — the grower card
};
function renderCoffee(slug, ctxName){ /* find coffee, honor coffee.channels, compose sections, wrap in chrome */ }
```

**Channel enforcement:** `renderCoffee` checks `coffee.channels` against the context's channel
(wholesale→wholesale, retail/card→retail, lesson→any) and falls through to not-found when excluded.
This is why channels live in the data model.

---

## 2. THE PRINT CONTEXT (`chrome:'print'`) — one mechanism, two features

The `card` context renders into a print-styled wrapper (`@media print` CSS: card dimensions, hide
app chrome, serif scale). This ONE mechanism serves BOTH:
- **`pm_cardgen`** — the grower-story card. PM's premium pour-over ritual is a PRINTED card the
  reviewers love (R4.4). This generates that card from `producer.story` — the digital FEEDS the
  analog, never replaces it. Augment, don't virtualize; that framing is the pitch.
- **The onboarding certificate** (CIG_ONBOARDING_ENGINE §5) — same print chrome, different content
  function. Build the chrome once under whichever flag lands first.

Recipe: a `?print=card&c=<slug>` (or in-app "Print card" button under `ff('pm_cardgen')`) →
`renderCoffee(slug,'card')` → `window.print()`. Pure client-side; nothing new to host.

---

## 3. MIGRATION RECIPE (Opus, when a second context is actually needed)

**Do not refactor speculatively.** Today one context exists and the code is fine. Trigger: the
FIRST session that builds `pm_menu`, `pm_cardgen`, or the lesson embed does the extraction as
step 1 of that build. Steps:
1. Extract today's inline chunks of `coffeeDialInView` into the named section functions —
   byte-identical output. (`row()`/`esc()` stay as-is.)
2. Add `COFFEE_CONTEXTS` + `renderCoffee`; make `coffeeDialInView(slug)` = `renderCoffee(slug,'wholesale')`.
3. **Parity gate:** run `qa_v101.js` unchanged — all 24 must still pass. The suite asserts rendered
   output, so it IS the parity test. Only then add the new context.
4. New contexts get their own jsdom cases in the same file (retail: no espresso numbers present,
   CTA present under flag; card: story present, dial-in absent).

## 4. RULES
- Sections are pure string functions of one resolved record — no DOM reads, no state, no fetches.
- A context never reaches around a section to grab data directly; if a context needs new content,
  that's a new section.
- Flags gate SECTIONS (pm_trace) or CONTEXT ENTRY POINTS (pm_menu, pm_cardgen) — never both for
  the same feature, or preview links get confusing.
- The `order` surface is NOT a context in core. It's an external app reading the same catalog
  (see CIG_DATA_MODEL §3). Keeping it out of this registry is the R5.3 "not the app guy" rule,
  enforced in architecture.
