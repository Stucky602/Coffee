# CIG v109 — PM header fixes, visible back button, real history stack

## 1. PM header no longer clips search + version
In PM mode the wide "PROUD MARY" wordmark shared one row with the search button,
language flags, and version pill — and pushed them off the right edge. Fixed by
restructuring the PM header into three bands:
- **Row 1:** the wordmark + the nav tabs.
- **Row 2 (new sub-row):** a compact Search button, the language flags, and the version pill.
- **Row 3 (new bar):** a full-width red **"Proud Mary Toolkit"** bar.

All three PM-only pieces are CSS-hidden in the neutral theme, so the normal dark app's header
is completely untouched (verified: neutral keeps search + version in the top row; sub-row and
bar stay hidden).

## 2. "Proud Mary" tab moved out of the nav row
The injected "Proud Mary" nav tab cramped the desktop tab row. It's gone from the desktop tabs;
the full-width **"Proud Mary Toolkit"** bar under the tabs is the front door now (it highlights
when you're inside any PM view). The mobile bottom-nav still gets a compact "Proud Mary" entry.

## 3. Back button is now visible in PM mode
The sticky back button had a hardcoded dark background that was invisible on the cream PM theme
(you could barely see "← All roles"). In PM mode it's now a white pill with a black outline,
offset shadow, and warm-red text — clearly readable, and on-brand.

## 4. Back button now uses a real history stack (fixes the jank)
The big one. Back buttons used to jump to hardcoded destinations (e.g. every Learn page's back
went to the Learn list). So opening a step from the **Barista onboarding path** and pressing back
dumped you on the generic Learn tab instead of back in the Barista path.

Replaced that with a proper navigation history stack: every forward `go()` pushes the view you're
leaving, and `navBack()` pops it to return exactly where you came from, restoring scroll position.
The back-button **label** is now context-aware too — a step opened from the Barista path reads
"← Barista path"; the same page opened from Learn reads "← Learn". This fixes the jank everywhere,
not just in PM mode.

Verified both directions: onboarding step → back → returns to the exact role path; Learn page →
back → returns to Learn.

## 5. Removed the redundant "Flavor face-off" (radarcompare)
It overlapped the core Compare tab (which already overlays profile radars). Pulled from the hub
and from the master-switch set. The flag and view still exist for dev, but it's no longer surfaced
or enabled by PM mode — the Explorer tools row now has three tools (Roast playground, Brew
face-off, Glossary), and the hub shows 11 cards.

## Verification — 136 tests green
- qa_v101 24 · qa_locale 13 · qa_devpanel 17 · qa_pmmode 23 · qa_pmtools 59
- New tests cover: PM sub-row visible / top-row search hidden / version mirrored to sub-row /
  desktop has no PM tab / sub-row + bar hidden in neutral; history back from an onboarding step
  returns to the role path; history back from a Learn-opened step returns to Learn.
- Playwright confirms on both mobile (420px) and desktop (1100px): nothing clipped, red toolkit
  bar renders under the tabs, back button is cream-on-red-text in PM mode, neutral header
  unchanged.

## Deploy
Push `deploy/` to the repo root. Bumped APP_VERSION + CACHE_C to v109 together.
