# CIG v113 — ten upgrades that make PM mode Proud Mary's app

Selected by running ten rounds of generate-25 / cut-to-10, carrying survivors forward.
Two rules emerged and shaped the final list:

1. **Anything needing invented data is a trap.** Account dashboards, sales forecasting,
   and drift alerting all demo beautifully and collapse the moment someone asks a
   question. Cut, every time.
2. **"Structure ready for your content" is a feature, not an apology.** Where the shape
   is real and the specifics are Proud Mary's, say so plainly on the page.

## The ten

**1. Content infusion.** In PM mode the guide's prose names Proud Mary's real lots. Origin
pages carry an "Ours" line ("From Honduras right now we have La Salvaje, Benjamin Paz and
Ovidio Gomez"), and Learn pages match on variety, process, and accolade, so the Geisha,
SL-28, Bourbon, Pacamara, and decaf spotlights all name actual coffees. Fires on 7 Learn
pages plus every sourced origin. This is the deepest change: it stops the guide reading as
an encyclopedia with a logo on it.

**2. Quality system.** Five modules borrowed from regulated manufacturing and pointed at
multi-site coffee: standard procedures, a deviation log that chases root cause, a training
matrix (with a worked example grid), a calibration schedule, and a quality visit checklist.
Structure complete, content labelled as Proud Mary's to write.

**3. Toolkit hub regrouped by audience.** "For your café partners", "For your team", "For
the counter", plus Explorer tools. A visitor taps three things and forms an opinion, so the
hub itself has to tell the story. 18 tools, organised by who uses them.

**4. Partner onboarding as a timeline.** The café-partner path now groups into Week 1 /
Week 2 / Month 1 with phase headers, rather than a flat list of pages.

**5. "Why does it taste different today?"** Six symptoms in plain barista language, each
opening to a likely cause, why it happens, and an ordered list of what to check. Ends by
pointing back at the deviation log.

**6. Rep playbook and account handover.** How a territory runs and how it survives changing
hands: knowing the book, the first month, a good visit, keeping the gaps warm, and the
handover itself.

**7. Opening a new site.** A runbook from T-8 weeks to first 90 days, written with a
small-format on-the-go site in mind.

**8. Café visit checklist.** The audit module as a working, tickable, printable form with a
live tally. Ticks are per-visit and deliberately not saved.

**9. "Is this bag ready?"** Enter a roast date, pick espresso or filter, get days off roast,
a verdict (resting / in the window / past peak / old), what to do about it, and a timeline
bar. General specialty guidance, labelled as such.

**10. Bar mode.** A floating toggle in PM mode that scales touch targets and body text for
6am, one-handed, wet-handed use. Persists per device. Verified to measurably change type
size without breaking layout.

## Verification, 200 tests green
qa_v101 24 · qa_locale 13 · qa_devpanel 17 · qa_pmmode 23 · **qa_pmtools 123** (was 92)

33 new tests cover every feature above plus neutral-mode isolation for all of them: no
infusion on origin or Learn pages, and all six new views declining to render outside PM mode.
Playwright confirms no horizontal overflow at 420px on any new view.

Bumped APP_VERSION + CACHE_C to v113 together.
