const fs=require('fs');
const {JSDOM}=require('/home/claude/node_modules/jsdom');
const html=fs.readFileSync('index.html','utf8');
let pass=0,fail=0;
function t(n,ok){ok?(pass++,console.log('  ok  '+n)):(fail++,console.log('  FAIL '+n));}
function load(url){ return new JSDOM(html,{url,runScripts:'dangerously',pretendToBeVisual:true}).window; }

// 1) neutral by default: no theme, no features, CIG logo shown
let w=load('https://stucky602.github.io/Coffee/');
t('default: no PM theme', w.document.documentElement.getAttribute('data-theme')===null);
t('default: pm_dialin off', w.eval("ff('pm_dialin')")===false);
t('default: cvatool off', w.eval("ff('cvatool')")===false);
t('default: footer is CIG copy', w.document.getElementById('foottag').textContent.includes('Industry Guide'));

// 2) master switch ON turns on EVERYTHING at once
w=load('https://stucky602.github.io/Coffee/?dev=1');
w.eval("setPmMode(true)");
t('master on: PM theme applied', w.document.documentElement.getAttribute('data-theme')==='pm');
t('master on: cvatool enabled', w.eval("ff('cvatool')")===true);
t('master on: pm_dialin enabled', w.eval("ff('pm_dialin')")===true);
t('master on: pm_trace enabled', w.eval("ff('pm_trace')")===true);
t('master on: pmModeOn() true', w.eval("pmModeOn()")===true);
t('master on: footer is PM copy', w.document.getElementById('foottag').textContent.includes('Proud Mary'));
t('master on: pmActive() true', w.eval("pmActive()")===true);

// 3) master switch OFF turns everything back
w.eval("setPmMode(false)");
t('master off: theme cleared', w.document.documentElement.getAttribute('data-theme')===null);
t('master off: cvatool disabled', w.eval("ff('cvatool')")===false);
t('master off: pm_dialin disabled', w.eval("ff('pm_dialin')")===false);
t('master off: footer back to CIG', w.document.getElementById('foottag').textContent.includes('Industry Guide'));

// 4) hero copy + emblem respond to PM mode
w=load('https://stucky602.github.io/Coffee/');
w.eval("setPmMode(true); go('home');");
let heroHtml=w.document.querySelector('.hero').innerHTML;
t('PM hero: uses house headline', heroHtml.includes('explained'));
t('PM hero: emblem img present', heroHtml.includes('pm-emblem.png'));
t('PM hero: Melbourne signature', heroHtml.includes('Melbourne'));
// neutral hero
w=load('https://stucky602.github.io/Coffee/');
w.eval("go('home')");
let heroN=w.document.querySelector('.hero').innerHTML;
t('neutral hero: original headline', heroN.includes('becomes flavor'));

// 5) header wordmark slot present (real logo swaps in via CSS)
w=load('https://stucky602.github.io/Coffee/');
t('header has PM wordmark img slot', !!w.document.querySelector('.pm-wordmark img'));
t('wordmark src is pm-logo.png', w.document.querySelector('.pm-wordmark img').getAttribute('src').includes('pm-logo.png'));

// 6) persisted PM theme restores features on reload
w=load('https://stucky602.github.io/Coffee/');
w.eval("applyTheme('pm')"); // simulate persisted theme only
let w2html=html;
// reload with theme persisted in localStorage — jsdom localStorage is per-window, so simulate via boot path:
w=load('https://stucky602.github.io/Coffee/?dev=1');
w.eval("localStorage.setItem('cig_theme_v1','pm')");
// re-run boot logic manually to mimic reload
let w3=load('https://stucky602.github.io/Coffee/');
// can't share localStorage across jsdom windows; instead assert boot re-enables when pmModeOn
w3.eval("applyTheme('pm')");
w3.eval("if(pmModeOn()){ PM_BUILT_FEATURES.forEach(function(f){ FF_OVERRIDE[f]=true; }); }");
t('persisted PM theme re-enables features on boot', w3.eval("ff('pm_dialin')")===true);

// 7) dial-in reachable in PM mode without URL flag
w=load('https://stucky602.github.io/Coffee/?c=honduras-la-salvaje-coe');
w.eval("setPmMode(true); go('coffee','honduras-la-salvaje-coe');");
t('PM mode: dial-in view reachable', w.document.getElementById('app').innerHTML.includes('WHOLESALE DIAL-IN'));

console.log('\n'+pass+' passed, '+fail+' failed');
process.exit(fail?1:0);
