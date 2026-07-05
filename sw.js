const CACHE="coffee-guide-v103";
const ASSETS=["./","./index.html","./manifest.webmanifest","./icon.svg","./img/roasters.png","./img/greendefects.png","./img/roastdefects.png","./img/processing.png","./img/milkdrinks.png","./img/blend.png","./img/teacoffee.png","./img/decafmethods.png","./img/beans_roast.png","./img/beans_green.png","./img/arabica_robusta.png","./img/cupping.png","./img/qcloop.png","./img/og-card.png","./img/roastchem.png","./img/degassing.png","./img/greenmetrics.png","./img/harvest.png","./img/betweenbatch.png","./img/grading.png","./img/threats.png","./fonts/fraunces-display.woff2"];
self.addEventListener("install",e=>{
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)).catch(()=>{}));
});
self.addEventListener("activate",e=>{
  e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));
});
self.addEventListener("fetch",e=>{
  if(e.request.method!=="GET")return;
  e.respondWith(
    caches.match(e.request).then(hit=>hit||fetch(e.request).then(res=>{
      const copy=res.clone();
      caches.open(CACHE).then(c=>c.put(e.request,copy)).catch(()=>{});
      return res;
    }).catch(()=>caches.match("./index.html")))
  );
});
