const fs=require('fs');
const {JSDOM}=require('/home/claude/node_modules/jsdom');
const html=fs.readFileSync('index.html','utf8');
let pass=0,fail=0;
function t(n,ok){ok?(pass++,console.log('  ok  '+n)):(fail++,console.log('  FAIL '+n));}

function load(url){ return new JSDOM(html,{url,runScripts:'dangerously',pretendToBeVisual:true}).window; }

// 1) panel absent by default
let w=load('https://stucky602.github.io/Coffee/');
t('panel hidden by default', w.document.getElementById('devpanel').style.display==='none');

// 2) ?dev=1 opens it
w=load('https://stucky602.github.io/Coffee/?dev=1');
t('?dev=1 opens panel', w.document.getElementById('devpanel').style.display==='flex');
t('flags rendered', w.document.querySelectorAll('.devflag-row').length===14);
t('built flags show "built" tag, reserved show "not built"', w.document.body.innerHTML.includes('built</span>') && w.document.body.innerHTML.includes('reserved (not built)'));

// 3) devSetFlag flips ff() and dial-in becomes reachable without URL flag
w=load('https://stucky602.github.io/Coffee/?dev=1&c=honduras-la-salvaje-coe');
t('pm_dialin off by default (no ?ff=)', w.eval("ff('pm_dialin')")===false);
w.eval("devSetFlag('pm_dialin', true)");
t('devSetFlag flips ff() live', w.eval("ff('pm_dialin')")===true);
w.eval("go('coffee','honduras-la-salvaje-coe')");
t('dial-in view reachable via override, no URL flag', w.document.getElementById('app').innerHTML.includes('WHOLESALE DIAL-IN'));

// 4) FF_OVERRIDE never touches localStorage
w=load('https://stucky602.github.io/Coffee/?dev=1');
w.eval("devSetFlag('pm_dialin', true); devSetFlag('cvatool', true);");
let lsKeys=w.eval("Object.keys(localStorage)");
t('FF_OVERRIDE never persisted to localStorage', !lsKeys.some(k=>k.toLowerCase().includes('ff')||k.toLowerCase().includes('flag')));

// 5) devReset clears overrides and theme
w.eval("devSetTheme('pm')");
t('theme is pm after set', w.document.documentElement.getAttribute('data-theme')==='pm');
w.eval("devReset()");
t('devReset clears flag override', w.eval("ff('pm_dialin')")===false);
t('devReset clears theme', w.document.documentElement.getAttribute('data-theme')===null);

// 6) the one genuinely-unbuilt flag (pm_house alias) renders disabled
w=load('https://stucky602.github.io/Coffee/?dev=1');
let radarRow = [...w.document.querySelectorAll('.devflag-row')].find(r=>r.textContent.includes('pm_house'));
t('reserved flag row is disabled', radarRow && radarRow.classList.contains('disabled'));
t('reserved flag toggle button disabled attr set', radarRow && radarRow.querySelector('.devflag-toggle').disabled);

// 7) shipped state unchanged: app with panel never opened renders identically (spot check home)
w=load('https://stucky602.github.io/Coffee/');
let home=w.document.getElementById('app').innerHTML;
t('normal load still renders home normally', home.length>1000 && !home.includes('WHOLESALE'));

// 8) theme toggle buttons in panel reflect state after switching
w=load('https://stucky602.github.io/Coffee/?dev=1');
w.eval("devSetTheme('pm'); renderDevPanel();");
t('PM theme button shows active', w.document.getElementById('devtheme-pm').classList.contains('on'));
t('Neutral theme button not active', !w.document.getElementById('devtheme-neutral').classList.contains('on'));

// 9) close button hides panel
w.eval("closeDevPanel()");
t('closeDevPanel hides it', w.document.getElementById('devpanel').style.display==='none');

console.log('\n'+pass+' passed, '+fail+' failed');
process.exit(fail?1:0);
