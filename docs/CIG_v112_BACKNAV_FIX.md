# CIG v112 — back button now works from every entry point

## The bug
Tapping a coffee in the PM-mode "On the menu now" strip on the home page took you to the
right origin page, but the back button dumped you on the **Origins** list instead of
returning you home. Same problem coming from the new "Our coffees" menu.

## Cause
v109 introduced a real navigation history stack (`_navStack` / `navBack()`), and the Learn
pages were migrated to it. Two detail views were missed and kept their old hardcoded
destinations:

- `originDetail()` used `goBack('origins')` — always Origins, regardless of where you came from.
- `profileDetail()` used `goBack('profiles')` — same problem, so opening a profile from the
  Compare tab and pressing back sent you to the Profiles list.

Because the new home strip and the "Our coffees" menu both link straight into origin pages,
the origin bug became much more visible in v111.

## Fix
Both views now use `navBack(fallback)` with a context-aware label from `backLabelFor()`,
matching what the Learn pages already do. The fallback is preserved, so if the stack is
empty (deep link, refresh) you still land somewhere sensible.

`backLabelFor()` also gained:
- `pmmenucoffee: 'Our coffees'` in the name map (was falling through to a generic "Back").
- Origin-to-origin: names the country you came from, so back from Panama reads "← Kenya"
  instead of "← Origin".
- Profile-to-profile: names the profile the same way.

## Behaviour now

| You came from | Back button says | Returns you to |
|---|---|---|
| Home "On the menu now" strip | ← Overview | Home |
| Our coffees menu | ← Our coffees | The menu |
| Origins list | ← Origins | Origins |
| Another origin page | ← Kenya (the country) | That origin |
| Compare tab → a profile | ← Compare | Compare |
| Profiles list → a profile | ← Profiles | Profiles |

Scroll position is restored in every case, as with the rest of the history stack.

## Verification — 169 tests green
- qa_v101 24 · qa_locale 13 · qa_devpanel 17 · qa_pmmode 23 · **qa_pmtools 92** (was 83)
- 9 new tests cover every row of the table above, including the exact reported flow
  (home strip → origin → back lands on home) and confirmation that the pre-existing
  origins-list flow still behaves.
- Neutral mode unaffected: origin back still reads "← Origins" there.

Bumped APP_VERSION + CACHE_C to v112 together.
