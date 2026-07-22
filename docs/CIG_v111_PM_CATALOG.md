# CIG v111 — Proud Mary mode now knows Proud Mary's actual catalog

## The problem
Through v110, PM mode was a **skin plus a toolkit**: real logo, real palette, a Proud Mary
Toolkit bar, and eleven working tools. But the 36 origin pages, the roast profiles, and the
home page were still a generic coffee encyclopedia. Anyone who actually works at Proud Mary
(and especially anyone in B2B) would notice within seconds that the app didn't know a single
thing about what PM sources or sells.

v111 fixes that. Flipping the switch now changes the **content**, not just the paint.

## New foundation: `data_pm_catalog.json`
A point-in-time scan of Proud Mary's public US store, structured for the app:
- **4 tiers** (Mild / Curious / Wild / Deluxe) with PM's own descriptions and roast lean
- **17 current single-origin lots** with origin, lot name, variety, process, tier, price, and
  flags for Limited / Decaf / accolades
- **3 blends** (Humbler, Angel Wings, Ghost Rider)
- **origin → country map** linking 8 origin pages to what PM buys from them
- **café locations and hours** (Portland Alberta, Austin S Lamar, Portland roastery)

It's inlined into the single-file build, so the app still works fully offline. It's labelled
as a snapshot everywhere it surfaces ("Lots rotate with the harvest"), so nothing pretends to
be a live feed.

## What changes when PM mode is on

**Origins tab is re-sorted around what we actually buy.** Leads with "On our menu now": the 8
origins PM sources, each card badged with its real tiers and lot count ("Deluxe · 4 lots on
now"), above a tier key explaining Mild/Curious/Wild/Deluxe in PM's words. The remaining 28
origins follow as "The wider world", still grouped by continent. The heading becomes
"Where our coffee comes from".

**Origin detail pages show the real lots.** Open Panama and you get a bordered block:
"What we have from Panama right now — 4 lots", listing Los Lajones Bambu, Altieri, Mama Cata,
and Finca Momoto with variety, process, and tier pill. Honduras surfaces La Salvaje with a
★ 1st Place Cup of Excellence flag.

**New tool: "Our coffees"** (`pmmenucoffee`), now the lead card on the toolkit hub. The whole
menu grouped into PM's four tiers with their real blurbs and prices, plus the blends. Every
coffee card links through to its origin page.

**Home page gets an "On the menu now" strip.** Six lots (Deluxe first), plus both café
addresses and hours. This makes the transformation visible the instant the switch flips,
before navigating anywhere.

**Roast profiles** retitle to "How we roast" with a tier key showing which tier roasts light
versus medium.

**New onboarding path: "New café partner"** — a week-one wholesale account ramp (what you're
serving, extraction, dialing our espresso, grind, troubleshooting, calibrating with us). The
existing paths covered barista / roaster / QC but not the wholesale-partner side, which is the
single most relevant path for a B2B audience.

## Neutral mode is untouched
Six explicit tests assert this: no PM section on origins, no sourced badges, original headings
intact on origins and profiles, no lots block on origin detail, no home strip. A normal visitor
to the guide sees exactly the app they saw in v110.

## Verification — 160 tests green
- qa_v101 24 · qa_locale 13 · qa_devpanel 17 · qa_pmmode 23 · **qa_pmtools 83** (was 59)
- 24 new tests cover: catalog data loading, tier/lot helpers, the origins transformation,
  per-origin lots, the menu view, the home strip, PM profile copy, the café-partner path, and
  the six neutral-mode isolation checks.
- check_catalog invariants pass. Playwright confirms no horizontal overflow at 420px mobile.

## Known limits / next
- Prices and lots drift as PM rotates stock. The snapshot note covers it, but re-scan before
  any demo that happens well after this build.
- The catalog is scanned from the **US** store only; the AU store has a different lineup.
- Bumped APP_VERSION + CACHE_C to v111 together.
