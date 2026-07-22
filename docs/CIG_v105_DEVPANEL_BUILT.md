# CIG v105 — diagram fixes, PM theme engine, hidden dev/demo panel (BUILT)
### Builds on v104. Flags still dark for real visitors. The dev panel is real now, not a spec.

## Part 1 — Five diagram fixes (all verified against rendered pixels, not just code review)

1. **greenmetrics** — the real bug (caught on the second look) was **clipping**, not a word-count
   mismatch. The Moisture card was centered at x=60 with half-width 91, putting its left edge at
   x=-31: off the canvas the entire time. Re-centered all four cards at [103, 288, 472, 657] with
   width 170, canvas raised 270→300px so the closing line clears the frame. Verified by sampling
   actual pixels: Moisture's border now sits at x=36 (inside the x=8 frame), symmetric with the
   right edge at x=1511. Em-dashes in the four card descriptions cleaned to semicolons/commas.
2. **robusta** — "+60% growth" restored (you were right, 25%→40% is +60% relative). The arrow
   redesigned as a clean arc over the gap between bars, apex-labeled, clear of both value labels.
3. **CVA static diagram** — the 8 section chips (Fragrance...Overall) were hard-truncated to 7
   characters (`Sweetne`, `Mouthfe`, `Afterta`). Replaced with an auto-fit sizer that shrinks the
   font per chip until the full word fits. No word is ever cut again.
4. **qcloop** — arrowheads were detached/malformed line-pairs. Rebuilt `arr()` to draw solid
   triangular arrowheads connecting at exact box-center alignment, with a small gap before the tip.
   Em-dash in the header line cleaned.
5. **grinder** — was a crude SVG (a triangle between two brackets). Per your call, rebuilt as a
   proper raster (`gen_grinder()` in gen_extras.py): a real conical cross-section (cone seated in a
   funnel, beans falling in, grounds exiting the base) and a real flat cross-section (two parallel
   discs, beans fed to center, thrown out centrifugally). Registered in IMG_ASSETS, dispatch
   switched from `diaGrinder()` (SVG) to `diaImg('grinder.png', ...)`.

All five confirmed by rendering to actual pixels and inspecting them, not just reading the code.

## Part 2 — What the toggle actually gives you (the answer to "what new features")

Long-press the version number (bottom-right `v105` chip in the header, or the footer copy) for
about 700ms, or open any URL with `?dev=1`. A panel slides up. **Nothing here is visible to a
normal visitor** — no nav entry, no hint, evaporates on reload except the theme (which persists on
purpose, since a demo phone should stay skinned between sessions until reset).

### Theme: Neutral ⇄ Proud Mary house
Tap **"Proud Mary house"** and the ENTIRE app re-skins live, verified via actual computed CSS
values, not a guess:
- Background goes from `#160e08` (neutral brown-black) to `#141210` (PM's cooler charcoal)
- Accent/heat colors go from gold (`#C9A34E`) to PM's warm terracotta (`#d98c6a`)
- The "☕ CIG" mark badge picks up the new accent as a filled background
- Every surface in the app reads through these same CSS variables, so this is a true one-flip
  re-skin, not a per-page patch. Tap "Neutral (shipped)" to snap back instantly.

This is what you'd flip in front of Nolan to make the app visibly become "Proud Mary's app" rather
than describing it.

### Flags: 14 toggles, honestly labeled
Every entry in `CIG_FLAGS` gets a row with a live toggle switch:
- **3 tagged "built"** — cvatool, pm_dialin, pm_trace. These actually work when flipped: cvatool
  surfaces the interactive CVA scorer on its page; pm_dialin + pm_trace together surface the full
  wholesale dial-in page (scan-a-bag experience) for the two demo coffees, including the producer
  story section.
- **11 tagged "reserved (not built)"** — their toggle is visibly disabled (dimmed row, switch won't
  move). This is deliberate: the panel documents true build state rather than pretending an unbuilt
  feature works. When one of these gets built in a future session, its row activates automatically
  with zero panel changes needed (it reads CIG_FLAGS dynamically).

### What this means for the interview demo specifically
Hand Nolan the phone on the neutral app. Long-press the version number. Tap pm_dialin + pm_trace
on, tap the coffee link (or it's already open) — the dial-in page appears with the producer story.
Tap "Proud Mary house" — the whole app shifts to PM's palette. Tap "Reset to shipped state" and
you're back to the honest dark app in one tap. That's the whole "it's already built, shipping
dark, ready when you are" pitch line (Business Case R2.5), now literally demoable without typing
a URL once.

### Reset
"Reset to shipped state" clears every override and the theme in one tap — confirmed by test to
restore `ff('pm_dialin')` to false and remove the `data-theme` attribute entirely.

## Part 3 — The machinery under the hood (for whoever builds the next flag)
- `FF_OVERRIDE` — plain in-memory object, session-only, never in localStorage (verified by test),
  never in the shipped data. Read at highest priority in `ff()`, above the `?ff=` URL preview and
  the shipped `CIG_FLAGS` value.
- `applyTheme('pm'|'neutral')` — sets/clears `data-theme` on `<html>`, persists to
  `localStorage cig_theme_v1` (this one DOES persist, deliberately, for a stable demo phone).
- `pm(text)` / `pmActive()` — the WHITELABEL `pm_house` content helper. Active when either
  `ff('pm_house')` OR the PM theme is on, so switching the demo theme also brings house voice
  online for any future content routed through `pm()`. Not yet wired into the deep methodology
  sentences (Panama/Nicaragua name-drops) — those need sentence-level editing in data, a clean
  Sonnet content task when wanted, now that the mechanism exists.
- `devFlagState()` / `devSetFlag()` / `devSetTheme()` / `devReset()` — the full control API the
  panel calls. Nothing else in the app calls these; they're dev-only entry points.

## Verification (54 tests green)
- `qa_v101.js`: 24/24 (architecture untouched)
- `qa_locale.js`: 13/13 (locale untouched)
- `qa_devpanel.js`: 17/17 — panel hidden by default, `?dev=1` opens it, 14 flags render with
  correct built/reserved tags, `devSetFlag` flips `ff()` live and unlocks the dial-in view without
  a URL param, `FF_OVERRIDE` never touches localStorage, theme switches and computed CSS changes
  confirmed, reserved flags render genuinely disabled, reset clears both flag and theme state,
  normal page loads are unaffected by the panel's mere existence.
- Theme swap additionally verified via Playwright computed-style read (not just DOM presence):
  `--bg` and `--accent` genuinely change value when `data-theme` flips.

## Notes for next session
- The five diagram fixes only need regeneration if `gen_extras.py`/`gen_defects.py` change again;
  the corrected PNGs are already baked into this bundle's `deploy/img/`.
- Wiring `pm()` into the Panama/Nicaragua sentences and the meta description is the natural next
  step to make the house theme change more than just color, a Sonnet content task.
- The panel's disabled rows are the honest to-do list: build one of the 11 reserved features and
  its row activates with no panel code changes.
