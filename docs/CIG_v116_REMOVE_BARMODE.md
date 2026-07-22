# CIG v116 — bar mode removed

Bar mode was added in v113 on the theory that the guide would get used behind a
bar at 6am, one-handed, with wet hands, and would benefit from larger touch
targets and body text.

In practice it did not earn its place. On desktop it was a floating button that
made no sense with a mouse (hidden in v114). On a phone it mostly just made
things look worse: inflated type and padding that broke the visual rhythm of
pages that were already comfortably usable at normal size.

Removed entirely rather than left in as an option nobody would turn on.

## What came out
- The `html[data-barmode="1"]` CSS block (12 rules).
- The floating `.barmodebtn` and its desktop hide-override.
- `barModeOn()`, `applyBarMode()`, `toggleBarMode()`, `initBarMode()`.
- The boot call and the `cig_barmode` localStorage key.

Nothing else changed. Verified: no `barmode` reference survives in the built
`index.html`, no leftover `data-barmode` attribute, and body type is back to its
normal size at every width.

## Test changes
- `qa_pmtools.js`: the three bar-mode behaviour tests became a single assertion
  that the feature is gone (121 tests, was 123).
- `qa_responsive.py`: three bar-mode visibility checks removed, one "no bar mode
  button anywhere" check added (21 tests, was 24).

## Verification
JS suites 214 (qa_v101 24, qa_locale 13, qa_devpanel 17, qa_pmmode 23,
qa_pmtools 121, qa_sw 16) plus responsive 21. **235 total**, no failures.

Bumped APP_VERSION + CACHE_C to v116 together.
