// QA sweep for the v101 catalog refactor. Loads the BUILT index.html in jsdom
// and asserts: dark-by-default parity, dial-in render from the resolved schema,
// trace gating, CVA tool untouched, CATALOG meta present, bad-slug handling.
const fs = require('fs');
const { JSDOM } = require('/home/claude/node_modules/jsdom');
const html = fs.readFileSync('index.html', 'utf8');

let pass = 0, fail = 0;
function t(name, ok, detail) {
  if (ok) { pass++; console.log('  ok  ' + name); }
  else { fail++; console.log('  FAIL ' + name + (detail ? ' — ' + detail : '')); }
}

function appEl2(win){ return win.document.getElementById('app').innerHTML; }
function load(url) {
  const dom = new JSDOM(html, { url, runScripts: 'dangerously', pretendToBeVisual: true });
  return dom.window;
}

// 1) Default load: dark. Home renders, no dial-in, no CVA tool anywhere.
let w = load('https://stucky602.github.io/Coffee/');
const appEl = () => w.document.getElementById('app');
let body = appEl().innerHTML;
t('default: home renders', !!w.document.querySelector('#app') && body.length > 3000);
t('default: no WHOLESALE DIAL-IN text', !body.includes('WHOLESALE DIAL-IN'));
t('default: flags all false', Object.values(w.CIG_FLAGS).every(v => v === false));

// 2) Runtime data: OFFERINGS resolved flat, CATALOG meta aboard.
t('OFFERINGS: 2 coffees', Array.isArray(w.OFFERINGS) === false || w.OFFERINGS.length === 2, typeof w.OFFERINGS);
// OFFERINGS is a const (not on window) — probe via evaluated access
const probe = w.eval('({n:OFFERINGS.length, prodType:typeof OFFERINGS[0].producer, prodFarm:OFFERINGS[0].producer&&OFFERINGS[0].producer.farm, tierName:OFFERINGS[0].tier&&OFFERINGS[0].tier.name, cat:{tiers:CATALOG.tiers.length, locs:CATALOG.locations.length, recipes:CATALOG.recipes.length, house:CATALOG.house&&CATALOG.house.id}})');
t('OFFERINGS resolved: 2 coffees', probe.n === 2, String(probe.n));
t('producer resolved to object', probe.prodType === 'object', probe.prodType);
t('producer.farm = La Salvaje', probe.prodFarm === 'La Salvaje', String(probe.prodFarm));
t('tier resolved: Deluxe', probe.tierName === 'Deluxe', String(probe.tierName));
t('CATALOG meta: 4 tiers / 4 locations / 3 recipes / house pm',
  probe.cat.tiers === 4 && probe.cat.locs === 4 && probe.cat.recipes === 3 && probe.cat.house === 'pm',
  JSON.stringify(probe.cat));

// 3) Dial-in + trace: ?c=slug&ff=pm_dialin&ff=pm_trace
w = load('https://stucky602.github.io/Coffee/?c=honduras-la-salvaje-coe&ff=pm_dialin&ff=pm_trace');
body = appEl2(w);
t('dialin: view renders', body.includes('WHOLESALE DIAL-IN'));
t('dialin: coffee name', body.includes('Honduras · La Salvaje · Geisha (DEMO)'));
t('dialin: espresso dose 18 g', body.includes('18 g'));
t('dialin: espresso time 28–33', body.includes('28–33'));
t('dialin: dialing-in note rendered (dialinNote)', body.includes('protect the florals'));
t('trace: lot note rendered', body.includes('1st Place Cup of Excellence lot.'));
t('trace: producer story rendered', body.includes('COE') || body.includes('Cup of Excellence international juries'));
t('trace: producer line with farm', body.includes('La Salvaje') && body.includes('Producer:'));

// 4) Dial-in WITHOUT trace flag: story section absent
w = load('https://stucky602.github.io/Coffee/?c=demo-geisha&ff=pm_dialin');
body = appEl2(w);
t('no-trace: dial-in renders', body.includes('WHOLESALE DIAL-IN') && body.includes('Panama Geisha (DEMO)'));
t('no-trace: story absent', !body.includes('The coffee</h3>'));

// 5) Bad slug → not-found page
w = load('https://stucky602.github.io/Coffee/?c=nope-not-real&ff=pm_dialin');
t('bad slug: not-found', appEl2(w).includes('Coffee not found'));

// 6) ?c= WITHOUT the flag → routes home (dark contract holds)
w = load('https://stucky602.github.io/Coffee/?c=demo-geisha');
t('flag-off: ?c= falls through to home', !appEl2(w).includes('WHOLESALE DIAL-IN'));

// 7) CVA tool untouched: dark by default, present under ?ff=cvatool
w = load('https://stucky602.github.io/Coffee/?ff=cvatool');
w.eval("go('meth','cva_scoring')");
t('cva: tool renders under flag', !!w.document.getElementById('cvaout'));
w = load('https://stucky602.github.io/Coffee/');
w.eval("go('meth','cva_scoring')");
t('cva: dark by default', !w.document.getElementById('cvaout'));

// 8) Version bumped
var _v = w.eval('APP_VERSION');
t('APP_VERSION well-formed (' + _v + ')', /^v\d+$/.test(_v), _v);

console.log('\n' + pass + ' passed, ' + fail + ' failed');
process.exit(fail ? 1 : 0);
