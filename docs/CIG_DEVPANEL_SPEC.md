# CIG_DEVPANEL_SPEC — the hidden demo/dev panel (long-press the version number)
### Sonnet-tier build spec · a DEMO instrument for Kevin, NOT a public product feature

## The intent (and the honesty guardrail)
Kevin wants a physical, tactile way to reveal the dormant PM layer live in an interview:
hand Nolan the phone showing the neutral guide, tap one thing, and the PM layer appears. The
`?ff=` URL preview already does this, but a URL isn't demo-friendly in the room. This spec adds a
**hidden** panel that flips the same `ff()` preview state with toggles.

**Why hidden, not a visible feature:** the whole architecture depends on the public app shipping
dark and honest. A visible "unlock features" button on the live site would let any visitor surface
PM branding and clearly-labeled placeholder recipes, which undercuts the exact honesty posture
(CIG_WHITELABEL, Business Case R2.5/R3.3) that makes the pitch trustworthy. So the panel is a
**dev/demo affordance**, discoverable only on purpose, invisible to normal visitors, obviously a
tool when open. It is NOT the `pm_house` product toggle and NOT shipped as a user feature.

## Access (deliberately obscure)
- **Long-press the version label** (`#verlabel` in the header, or `#footver`) for ~700ms → panel opens.
- Also openable via `?dev=1` for desktop demo prep.
- No nav entry, no hint, no hover cue. If you don't know it's there, you never find it.
- Optional: also require the press to be a deliberate long-press (not a tap) so accidental
  discovery is near-zero.

## What the panel shows
A small fixed overlay (bottom sheet on mobile, corner card on desktop), clearly labeled
**"DEV / DEMO PANEL — not a shipped feature."** Contents:
1. **A toggle per CIG_FLAGS entry**, grouped: BUILT (cvatool, pm_dialin, pm_trace) at top and live-
   togglable; RESERVED (everything else) shown disabled with a "not built yet" tag, so the panel
   also documents build state honestly.
2. Each toggle flips the SAME preview state `ff()` reads (see wiring below), then calls `render()`.
3. A **locale mirror** of the flag toggle (handy in demo) — optional, since the flags already exist
   in the header.
4. A **"Reset to shipped state"** button: clears all preview flags, returns to the honest dark app.
5. A tiny note line: current APP_VERSION + "previews are session-only, nothing is written to the
   live site."

## Wiring (small, self-contained)
The current `ff(name)` reads two sources: `?ff=` URL params (preview) and `CIG_FLAGS[name]`
(shipped state). Add a THIRD, highest-priority, in-memory session override the panel writes:

```js
var FF_OVERRIDE = {};                 // session-only, never persisted, never in shipped data
function ff(name){
  if(name in FF_OVERRIDE) return FF_OVERRIDE[name];      // dev panel wins (session only)
  try{ var q=new URLSearchParams(location.search).getAll('ff');
       if(q.indexOf(name)>=0) return true; }catch(e){}   // URL preview
  return !!CIG_FLAGS[name];                              // shipped state
}
function devSetFlag(name,on){ FF_OVERRIDE[name]=!!on; render(); }
function devReset(){ FF_OVERRIDE={}; render(); }
```

Because `FF_OVERRIDE` is a plain in-memory object (never localStorage, never a URL, never in the
built data), it evaporates on reload. The shipped app is byte-identical for real visitors; the panel
only mutates a runtime object that starts empty.

## Interaction with pm_house (the "changes how it looks" part)
Once the `pm_house` helper is built (CIG_WHITELABEL §2, an Opus task), toggling `pm_house` in this
panel visibly re-skins the app (PM voice/branding on). Until then, the panel can flip the three
built flags (cvatool surfaces the CVA scorer; pm_dialin + pm_trace surface the dial-in layer via a
demo coffee), and the reserved toggles sit disabled. So the panel is useful now and gets more
dramatic as features land, with zero rework (it reads CIG_FLAGS dynamically).

## Testing (jsdom, same pattern as qa_locale.js)
- Panel absent from DOM by default; present after long-press / `?dev=1`.
- `devSetFlag('pm_dialin',true)` → dial-in view reachable without a URL flag; `devReset()` restores.
- FF_OVERRIDE never touches localStorage (assert storage untouched).
- Shipped state unchanged: with panel never opened, app renders identically to pre-panel build
  (run qa_v101.js — all 24 must still pass).
- Reserved flags render disabled.

## Build size / tier
~60–90 lines (panel HTML/CSS + the FF_OVERRIDE wiring + long-press handler). Self-contained,
gated, testable. **Sonnet-tier** — no architecture decisions, just a careful small feature against
the existing flag system. Ship it as its own version bump when built.

## What NOT to do
- Do NOT persist FF_OVERRIDE (that would make previews leak across reloads for real visitors).
- Do NOT add a visible entry point. The obscurity IS the safety.
- Do NOT let the panel write CIG_FLAGS or any data file. It only writes the in-memory override.
- Do NOT present the panel as a product feature to PM — it's how Kevin demos, not what PM ships.
