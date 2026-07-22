/* Service worker for Coffee: An Industry Guide.

   STRATEGY
   - Navigations / HTML: NETWORK FIRST. The app always tries to fetch a fresh
     index.html and only falls back to cache when offline. This is what lets a
     new version reach an installed home-screen app without reinstalling it.
   - Static assets (images, fonts, icon): CACHE FIRST. They are versioned by the
     cache name, never change within a version, and are what make offline work.
   - On activate we delete every old cache and claim open clients immediately.

   The page also polls for updates and, when a new worker takes over, reloads
   itself once. See the registration block in index.html.
*/
const CACHE="coffee-guide-v115";
const ASSETS=["./","./index.html","./manifest.webmanifest","./icon.svg","./img/roasters.png","./img/greendefects.png","./img/roastdefects.png","./img/processing.png","./img/milkdrinks.png","./img/blend.png","./img/teacoffee.png","./img/decafmethods.png","./img/beans_roast.png","./img/beans_green.png","./img/arabica_robusta.png","./img/cupping.png","./img/qcloop.png","./img/og-card.png","./img/roastchem.png","./img/degassing.png","./img/greenmetrics.png","./img/harvest.png","./img/betweenbatch.png","./img/grading.png","./img/threats.png","./img/grinder.png","./img/pm-logo.png","./img/pm-emblem.png","./fonts/fraunces-display.woff2"];

self.addEventListener("install",e=>{
  self.skipWaiting();                       // do not wait for old tabs to close
  e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)).catch(()=>{}));
});

self.addEventListener("activate",e=>{
  e.waitUntil(
    caches.keys()
      .then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k))))
      .then(()=>self.clients.claim())
  );
});

// Allow the page to ask a waiting worker to take over right now.
self.addEventListener("message",e=>{
  if(e.data==="SKIP_WAITING") self.skipWaiting();
});

function isHTML(req){
  return req.mode==="navigate" ||
         (req.headers.get("accept")||"").includes("text/html");
}

self.addEventListener("fetch",e=>{
  if(e.request.method!=="GET") return;
  const req=e.request;

  // HTML: network first, so a new build is picked up as soon as it exists.
  if(isHTML(req)){
    e.respondWith(
      fetch(req).then(res=>{
        const copy=res.clone();
        caches.open(CACHE).then(c=>c.put("./index.html",copy)).catch(()=>{});
        return res;
      }).catch(()=>caches.match("./index.html").then(hit=>hit||caches.match("./")))
    );
    return;
  }

  // Everything else: cache first, fill the cache on a miss.
  e.respondWith(
    caches.match(req).then(hit=>hit||fetch(req).then(res=>{
      const copy=res.clone();
      caches.open(CACHE).then(c=>c.put(req,copy)).catch(()=>{});
      return res;
    }).catch(()=>caches.match("./index.html")))
  );
});
