# CIG v107 — the Proud Mary toolkit: a real tab, a hub, and five working tools

## The problem this fixes
In v106 the master switch turned on `cvatool`, `pm_dialin`, and `pm_trace` — but you couldn't
find them. `pm_dialin` was only reachable by hand-typing `?c=<slug>` in the URL, `pm_trace` was a
sub-section of that hidden page, and `cvatool` was wired into the diagram dispatch but embedded on
no page at all, so it rendered nowhere. The switch turned on things that were invisible.

## What v107 adds
When PM mode is on, an obvious **"Proud Mary" tab** now appears in the nav (both desktop and
mobile, in the brand's warm red). It lands on a **hub page — "The Proud Mary toolkit"** — with a
card for each tool. The tab is injected/removed live; a normal visitor never sees it.

Five tools, all reachable from the hub, all real (demo data where PM's real numbers aren't in yet,
labelled honestly rather than faked):

1. **Wholesale dial-in** (flagship). A list of the wholesale coffees; tap one for the full recipe
   card the barista sees — espresso, batch, and at-home specs, plus the grower story (that's
   `pm_trace`). This is the "scan the bag, get the recipe" feature, now with a real front door
   instead of a hand-typed URL. The QR-on-the-bag flow (`?c=<coffee>`) still works exactly as before.
2. **Cupping scorer** (`cvatool`). The SCA CVA affective calculator, finally on its own page —
   rate eight sections 1–9, get the live cup score (e.g. 84.25 → "Specialty"). Previously orphaned;
   now surfaced.
3. **Staff onboarding** (`pm_onboarding`, NEW). Three role-based training paths — Barista, Roaster,
   Wholesale/QC — each an ordered walk through exactly the Learn pages that role needs. This is the
   feature that maps directly to PM's actual scaling problem: ramping new hires consistently. Every
   step links to a real, verified guide page (a test asserts no dead links).
4. **Current offerings** (`pm_offerings`, NEW). The demo coffees as shelf-ready cards, grouped by
   Proud Mary's Mild → Curious → Wild → Deluxe tiers, pulled from the catalog.
5. **House recipes** (`pm_recipes`, NEW). Proud Mary's standard brew presets. The structure is
   built; the actual numbers are theirs to set, so the cards read "Awaiting Proud Mary's house
   numbers" rather than inventing a spec — the honest choice for a pitch.

The master switch now turns on all six built features at once. The Advanced panel still lists each
flag individually and correctly tags all six as "built".

## Also in this build: the dev-panel exit fix
The demo panel was hard to close — the ✕ button was rendering literal broken text (`\u2715` inside
a raw string). Fixed, plus three more ways out: a labelled **"Close ×"** pill, a big red **"Done —
view the site"** button, **tap-outside-to-close**, and the **Escape key**. All four verified.

## Architecture notes
- Routing: added `pmhub`, `pmwholesale`, `pmcva`, `pmonboard`, `pmoffer`, `pmrecipes` views; all
  map to the PM nav-tab highlight in `go()`.
- `syncPmTab()` injects/removes the tab on mode change and on boot (persisted PM mode restores it).
- Each tool guards on its own flag (`ff('pm_onboarding')` etc.), so the Advanced panel can still
  toggle them one at a time; the master switch just flips the whole set.
- Onboarding paths (`PM_ROLES`) reference real methodology page IDs — validated against
  `METHODOLOGY` keys in the test suite so a renamed page can't silently break a path.
- Offerings correctly reads the *resolved* tier object (`o.tier.id`), since the build denormalizes
  the tier reference at build time.

## Verification — 106 tests green
- qa_v101 24/24 · qa_locale 13/13 · qa_devpanel 17/17 · qa_pmmode 23/23 · **qa_pmtools 29/29 (new)**
- check_catalog invariants pass
- Playwright end-to-end: tab appears/disappears with the master switch, hub shows 5 cards, all five
  tools render real content, barista/roaster paths have their 6 steps, CVA computes live, wholesale
  cards link to dial-in pages with producer stories, and everything sits on the cream PM theme.

## What's still demo / next
- Producer names in the two demo coffees are still "TODO — family name"; the story text is real but
  the names await PM's data. (18 TODO markers tracked by check_catalog.)
- House recipe numbers await PM's real specs (deliberately shown as "awaiting values").
- `pm_menu`, `pm_wholesale` (portal), `pm_cardgen`, and the four non-PM reserved flags remain
  unbuilt — candidates for a future pass.

## Deploy
Push `deploy/` to the repo root. Bumped APP_VERSION + CACHE_C to v107 together.
