# CIG_ONBOARDING_ENGINE — the curriculum/progress/checkpoint engine
### Fable architecture artifact #3 · design spec (`ff:'pm_onboarding'`) · Opus builds the engine, Sonnet writes the lessons

**Scope discipline:** this specs the ENGINE — how a path is data, how progress persists, how
checkpoints gate, how completion certifies. Lesson content, quiz questions, and which pages belong
to which role are Sonnet/PM work later. The 136 methodology pages ARE the curriculum; the engine is
additive and touches none of them. The business case: Guadalupe opens ~Sept 2026 with a brand-new
team — a role path is the co-flagship demo (R4.7).

---

## 1. DATA: `data_onboarding.json` (schema cig-onboarding/1, new file)

```json
{ "schema": "cig-onboarding/1",
  "paths": [
    { "id": "pm-new-barista-austin",
      "role": "New Barista",
      "title": "PM Coffee Foundations — New Barista",
      "blurb": "Everything behind the bar expects you to know, in order.",
      "cert": { "title": "PM Coffee Foundations", "subtitle": "New Barista path" },
      "modules": [
        { "id": "m1-espresso-basics",
          "title": "Espresso fundamentals",
          "pages": ["brew_extraction", "brew_espresso", "brew_grind"],
          "gate": true,
          "practical": { "kind": "dialin", "coffeeSlug": null,
                         "prompt": "Dial in today's espresso with your trainer; log dose/yield/time." },
          "checkpoint": {
            "id": "c1", "pass": 3,
            "questions": [
              { "id": "q1", "type": "mcq",     "q": "...", "options": ["...","...","..."], "answer": 1 },
              { "id": "q2", "type": "multi",   "q": "...", "options": ["..."], "answer": [0,2] },
              { "id": "q3", "type": "numeric", "q": "...", "answer": 2.0, "tolerance": 0.1 },
              { "id": "q4", "type": "cva",     "given": { "sections": [8,7,7.5,8,7,8,7.5,8], "nonuniform": 0, "defective": 1 },
                "q": "Compute this cup's CVA score.", "tolerance": 0.25 }
            ] } } ] } ] }
```

Semantics:
- `pages` are METHODOLOGY ids — validated at build (a `check_onboarding.py` mirroring
  check_catalog: unique ids, page refs exist, `pass ≤ questions.length`, cva answers recompute
  correctly against the verified formula, coffeeSlug resolves or null).
- `gate:true` ⇒ module N+1 locked until this module's checkpoint passes. `gate:false` ⇒ advisory.
- Question types and grading: `mcq` index equality · `multi` set equality · `numeric` |x−a|≤tol ·
  `cva` — the engine recomputes `0.65625×Σ+52.75−2nu−4d` via the EXISTING `cvaCompute` path and
  compares within tolerance. The built CVA tool becomes a teaching checkpoint for a team whose
  leaders sit COE juries — that's the pitch line, and it costs nothing because the tool exists.
- `practical` is unauditable by the engine (real espresso machines aren't in scope) — it renders as
  a self-attested check item, optionally embedding `renderCoffee(slug,'lesson')` (CIG_RENDER_ARCH)
  when a coffeeSlug is set. Honesty over theater: the engine grades what it can grade.

## 2. PROGRESS STORE — localStorage, versioned envelope

Key `cig_onb_v1` (this is the real deployed site on Pages — the artifact localStorage restriction
does not apply here):

```json
{ "v": 1, "paths": { "pm-new-barista-austin": { "modules": {
      "m1-espresso-basics": { "pages": { "brew_espresso": 1730000000 },
        "practical": { "done": true, "ts": 1730000000 },
        "checkpoint": { "passed": true, "score": 4, "attempts": 2, "ts": 1730000000 } } } } } }
```

Rules:
- **Page completion is an explicit "Mark complete" tap** on the page (shown only in path chrome).
  Not scroll- or timer-inferred — auto-detection is flaky and dishonest; a trainee tapping "done"
  is the same self-attestation a paper checklist gets.
- Checkpoint attempts unlimited, count recorded (a manager can see 7 attempts and coach).
- Migration: unknown `v` ⇒ archive under `cig_onb_v1_old`, start clean, tell the user. Never
  silently discard a trainee's progress.
- Multi-device honesty: localStorage is per-device. Say so in the UI ("progress lives on this
  device"). Server sync is a hosting decision (Cloudflare, like LTB) — a later adapter, not core.

## 3. ENGINE SURFACES (all gated `ff('pm_onboarding')`)
1. `onboardingView()` — path list → path detail (modules, lock/done states). New `render()` case +
   nav entry, same pattern as `learn`.
2. **Path chrome on `methDetail`** — when `state.pathCtx` is set (entered via a path), the page
   gets a top strip (path · module · step i/N) + "Mark complete → next". Zero changes to page data;
   one wrapper in one function. Mirrors the existing `pathNav()` guided-path pattern already in the app.
3. `checkpointView(pathId, moduleId)` — renders questions, grades client-side, writes progress.
   Reuses CVA machinery for cva questions.
4. `certView(pathId)` — all modules passed ⇒ render certificate via the PRINT chrome
   (CIG_RENDER_ARCH §2): title, path, date, module list. Print = the deliverable; no PDF machinery.

## 4. INVARIANTS + TESTS
- `check_onboarding.py` at build (refs, shapes, cva self-consistency).
- jsdom: dark by default; `?ff=pm_onboarding` shows nav; grading truth-table per question type;
  gate logic (locked → pass → unlocked); storage round-trip; migration path; cert renders only
  when complete.

## 5. WHAT THE ENGINE IS NOT
Not an LMS account system (no logins), not analytics (no tracking), not a content CMS (pages stay
where they are), not manager dashboards (v2 at most, needs hosting). The engine is: **paths as
data, progress as a versioned local envelope, checkpoints as pure grading functions, certificate
as a print render.** Opus can build all four surfaces against this spec in one session; Sonnet then
fills `data_onboarding.json` with the real PM curriculum once PM says which pages map to which role
(Business Case Part 5).
