# CIG v115 — the app updates itself now

## The problem
An installed home-screen copy never picked up a new version. The only fix was
deleting it and re-adding it. LTB does not have this problem, which suggested a
hosting difference, but the cause was entirely in the service worker.

## Why it happened
Three things, all in `sw.js` and the registration block:

1. **Cache-first on everything.** The fetch handler was
   `caches.match(req).then(hit => hit || fetch(req))`. Once `index.html` was in
   the cache it was served from there forever and the network was never
   consulted, so the app could not discover that a new build existed.
2. **The service worker file itself was being cached** by the browser, so even
   the version-bump mechanism could be delayed by hours.
3. **No update path.** Nothing checked for a new worker, and nothing told the
   running page to reload when one took over.

Hosting was never the issue. GitHub Pages is fine.

## The fix

**Split the caching strategy.**
- HTML and navigations: **network first**, falling back to cache when offline.
  This is what lets a new build reach an installed app.
- Images, fonts, icon: **cache first**, as before. Offline use is unchanged.

**Registration now actively manages updates.**
- `updateViaCache:'none'` so the browser never serves a stale `sw.js`.
- An update check on load, on `visibilitychange`, on window focus, and hourly
  while the app stays open.
- A new worker that installs while an old one is controlling gets sent
  `SKIP_WAITING` and activates immediately.
- `controllerchange` triggers a single guarded `location.reload()`.

Net effect: open the app, and within a few seconds of it regaining focus it
picks up the new version and refreshes itself. No deleting, no re-adding.

## What this does not change
Offline still works. Static assets are still precached and still cache-first,
and the HTML branch falls back to the cached copy when the network is gone.

## New suite: `qa_sw.js`
16 checks on the generated output: that HTML is network-first with an offline
fallback, that assets stay cache-first, the activate/claim/purge lifecycle, the
SKIP_WAITING channel, and every part of the registration block. It also asserts
**the cache name matches `APP_VERSION`**, which catches the one mistake that
would silently disable updates again.

## Verification
JS suites 216 (qa_v101 24, qa_locale 13, qa_devpanel 17, qa_pmmode 23,
qa_pmtools 123, **qa_sw 16**) plus the 24-check responsive suite. **240 total.**

## One-time note for this upgrade
The currently installed copy on your phone is still running the old cache-first
worker, so it cannot auto-update *to* this version. Delete and re-add it once
more. From v115 onward it updates itself.

Bumped APP_VERSION + CACHE_C to v115 together.
