const fs=require('fs');
const {JSDOM}=require('/home/claude/node_modules/jsdom');
const html=fs.readFileSync('index.html','utf8');
let pass=0,fail=0;
function t(n,ok){ok?(pass++,console.log('  ok  '+n)):(fail++,console.log('  FAIL '+n));}
function load(url){ return new JSDOM(html,{url,runScripts:'dangerously',pretendToBeVisual:true}).window; }

// tab injection
let w=load('https://stucky602.github.io/Coffee/');
t('no PM tab in neutral', !w.document.querySelector('[data-nav=pm]'));
w.eval('setPmMode(true)');
t('toolkit bar shown in PM mode', w.getComputedStyle(w.document.getElementById('pm-toolkitbar')).display!=='none');
t('PM entry in mobile nav', !!w.document.querySelector('.mobnav [data-nav=pm]'));
t('toolkit bar reads Proud Mary Toolkit', w.document.getElementById('pm-toolkitbar').textContent.indexOf('Proud Mary Toolkit')>=0);
w.eval('setPmMode(false)');
t('toolkit bar hidden when master off', w.getComputedStyle(w.document.getElementById('pm-toolkitbar')).display==='none');

// hub
w=load('https://stucky602.github.io/Coffee/');
w.eval('setPmMode(true); go("pmhub")');
t('hub renders title', w.document.querySelector('.pmhero .page-title').textContent.includes('toolkit'));
t('hub shows 12 tool cards (base)', w.document.querySelectorAll('.secdir .pmt-card').length===12);
t('hub nav highlights PM tab', w.document.querySelector('[data-nav=pm]').classList.contains('on'));

// each tool renders (not bounced home) when its flag is on
[['pmwholesale','Wholesale dial-in'],['pmcva','Cupping scorer'],['pmonboard','Staff onboarding'],['pmoffer','Current offerings'],['pmrecipes','House recipes']].forEach(function(pair){
  w=load('https://stucky602.github.io/Coffee/');
  w.eval('setPmMode(true); go("'+pair[0]+'")');
  t(pair[0]+' renders', w.document.getElementById('app').innerHTML.includes(pair[1]));
});

// tools bounce to hub when their flag is OFF (guard works)
w=load('https://stucky602.github.io/Coffee/');
w.eval('applyTheme("pm"); FF_OVERRIDE={}; go("pmwholesale")'); // theme on but features not enabled
t('pmwholesale guards to hub when flag off', w.document.querySelector('.pmhero') || w.document.getElementById('app').innerHTML.includes('toolkit'));

// wholesale list -> 2 coffees, each links to dial-in
w=load('https://stucky602.github.io/Coffee/');
w.eval('setPmMode(true); go("pmwholesale")');
t('wholesale lists 2 coffees', w.document.querySelectorAll('.origrid .origcard').length===2);

// onboarding: role list then detail path
w=load('https://stucky602.github.io/Coffee/');
w.eval('setPmMode(true); go("pmonboard")');
t('onboarding shows 4 role cards', w.document.querySelectorAll('.secdir .pmt-card').length===4);
w.eval('go("pmonboard","barista")');
t('barista path has 6 steps', w.document.querySelectorAll('.pathstep').length===6);
w.eval('go("pmonboard","roaster")');
t('roaster path has 6 steps', w.document.querySelectorAll('.pathstep').length===6);

// onboarding steps point at REAL meth pages (no dead links)
w=load('https://stucky602.github.io/Coffee/');
w.eval('setPmMode(true)');
let allIds=Object.keys(w.eval('METHODOLOGY'));
let roles=w.eval('PM_ROLES');
let deadLinks=[];
Object.keys(roles).forEach(function(rk){
  roles[rk].steps.forEach(function(st){ if(allIds.indexOf(st[0])<0) deadLinks.push(rk+':'+st[0]); });
});
t('all onboarding steps link to real pages', deadLinks.length===0 || (console.log('    dead:',deadLinks),false));

// CVA scorer computes
w=load('https://stucky602.github.io/Coffee/');
w.eval('setPmMode(true); go("pmcva")');
t('CVA scorer output present', w.document.getElementById('cvaout') && w.document.getElementById('cvaout').textContent.includes('cup score'));

// offerings grouped by tier
w=load('https://stucky602.github.io/Coffee/');
w.eval('setPmMode(true); go("pmoffer")');
t('offerings shows tier groups', w.document.querySelectorAll('.grouplabel').length>=1);

// recipes: honest placeholders (awaiting values)
w=load('https://stucky602.github.io/Coffee/');
w.eval('setPmMode(true); go("pmrecipes")');
t('recipes page renders cards', w.document.querySelectorAll('.di-card').length>=1);
t('recipes honestly flag missing values', w.document.getElementById('app').innerHTML.includes('Awaiting'));

// master switch enables ALL six built features
w=load('https://stucky602.github.io/Coffee/');
w.eval('setPmMode(true)');
['cvatool','pm_dialin','pm_trace','pm_onboarding','pm_offerings','pm_recipes'].forEach(function(f){
  t('master enables '+f, w.eval('ff("'+f+'")')===true);
});

// ---- v108 new tools ----
[['roastplay','Roast playground'],['brewcompare','Brew face-off'],['glossaryhub','Glossary'],['pmmenu','What am I drinking'],['pmcardgen','Grower-story cards'],['pmwholesale2','Wholesale partner portal']].forEach(function(pair){
  var ww=load('https://stucky602.github.io/Coffee/');
  ww.eval('setPmMode(true); go("'+pair[0]+'")');
  t(pair[0]+' renders', ww.document.getElementById('app').innerHTML.indexOf(pair[1])>=0);
});
// each new tool guards to hub when its flag is off
[['roastplay','roastplay'],['brewcompare','brewcompare'],['glossaryhub','glossaryhub'],['pmmenu','pm_menu'],['pmcardgen','pm_cardgen'],['pmwholesale2','pm_wholesale']].forEach(function(pair){
  var ww=load('https://stucky602.github.io/Coffee/');
  ww.eval('applyTheme("pm"); FF_OVERRIDE={}; go("'+pair[0]+'")');
  t(pair[0]+' guards to hub when flag off', ww.document.getElementById('app').innerHTML.indexOf('toolkit')>=0);
});
// hub shows all 12 tool cards in PM mode
var wh=load('https://stucky602.github.io/Coffee/');
wh.eval('setPmMode(true); go("pmhub")');
t('hub shows 12 tool cards', wh.document.querySelectorAll('.secdir .pmt-card').length===12);
// master switch enables all 13 built features
var wm=load('https://stucky602.github.io/Coffee/');
wm.eval('setPmMode(true)');
['roastplay','brewcompare','glossaryhub','pm_menu','pm_cardgen','pm_wholesale'].forEach(function(f){
  t('master enables '+f, wm.eval('ff("'+f+'")')===true);
});
// roastplay interactivity
var wr=load('https://stucky602.github.io/Coffee/');
wr.eval('setPmMode(true); go("roastplay"); rpSet("dtr",25)');
t('roastplay DTR readout updates', wr.document.getElementById('rp-read').textContent.indexOf('25')>=0);
// cardgen honest producer handling (TODO names suppressed)
var wc=load('https://stucky602.github.io/Coffee/');
wc.eval('setPmMode(true); go("pmcardgen","honduras-la-salvaje-coe")');
t('cardgen suppresses TODO producer names', wc.document.getElementById('app').innerHTML.indexOf('TODO')<0);

// ---- v109: header restructure + history back ----
var wH=load('https://stucky602.github.io/Coffee/');
wH.eval('setPmMode(true)');
t('PM subrow visible in PM mode', wH.getComputedStyle(wH.document.getElementById('pm-subrow')).display!=='none');
t('top-row search hidden in PM mode', wH.getComputedStyle(wH.document.querySelector('.top .wrap .searchbtn')).display==='none');
t('subrow has version', wH.document.getElementById('verlabel2').textContent.length>0);
t('desktop nav has no PM tab (uses bar)', !wH.document.querySelector('.navtabs [data-nav=pm]'));
wH.eval('setPmMode(false)');
t('PM subrow hidden in neutral', wH.getComputedStyle(wH.document.getElementById('pm-subrow')).display==='none');
t('toolkit bar hidden in neutral', wH.getComputedStyle(wH.document.getElementById('pm-toolkitbar')).display==='none');

// history back: onboarding step returns to the role path, not Learn
var wB=load('https://stucky602.github.io/Coffee/');
wB.eval('setPmMode(true); go("pmhub"); go("pmonboard"); go("pmonboard","barista"); go("meth","history");');
t('meth back label reflects onboarding origin', wB.document.querySelector('.back').textContent.indexOf('Barista')>=0);
wB.eval('navBack("learn")');
t('back from step returns to barista path', wB.eval('state.view')==='pmonboard' && wB.eval('state.arg')==='barista');

// history back: meth opened from Learn returns to Learn
var wL=load('https://stucky602.github.io/Coffee/');
wL.eval('go("learn"); go("meth","history");');
wL.eval('navBack("learn")');
t('back from Learn-opened step returns to Learn', wL.eval('state.view')==='learn');


// ---- v111: PM catalog integration ----
var wC=load('https://stucky602.github.io/Coffee/');
wC.eval('setPmMode(true)');
t('PMCAT data present', wC.eval('!!PMCAT && PMCAT.coffees.length>0'));
t('PM tiers = 4', wC.eval('pmTiers().length')===4);
t('PM sources 8 origins', wC.eval('pmSourcedIds().length')===8);
t('pmLotsFor(panama) returns lots', wC.eval('pmLotsFor("origin_panama").length')>0);
t('pmIsSourced true for Ethiopia', wC.eval('pmIsSourced("origin_ethiopia")')===true);
t('pmIsSourced false for Yemen', wC.eval('pmIsSourced("origin_yemen")')===false);

wC.eval('go("origins")');
t('origins shows "On our menu now"', wC.document.getElementById('app').innerHTML.indexOf('On our menu now')>=0);
t('origins shows tier key', !!wC.document.querySelector('.pmtierkey'));
t('sourced origin cards badged', wC.document.querySelectorAll('.origcard.pmsourced').length===8);

wC.eval('go("origin","origin_panama")');
t('Panama page lists our lots', wC.document.getElementById('app').innerHTML.indexOf('What we have from Panama')>=0);
t('Panama shows 4 lots', wC.document.querySelectorAll('.pmlot').length===4);
wC.eval('go("origin","origin_honduras")');
t('Honduras shows CoE accolade', wC.document.getElementById('app').innerHTML.indexOf('Cup of Excellence')>=0);

wC.eval('go("pmmenucoffee")');
t('menu view renders tier blocks', wC.document.querySelectorAll('.pmtierblock').length>=4);
t('menu view renders coffee cards', wC.document.querySelectorAll('.pmmenucard').length>=17);

wC.eval('go("home")');
t('home shows on-menu-now strip', wC.document.querySelectorAll('.pmstripcard').length>0);
t('home shows cafe locations', wC.document.getElementById('app').innerHTML.indexOf('Austin')>=0);

wC.eval('go("profiles")');
t('profiles retitled in PM mode', wC.document.getElementById('app').innerHTML.indexOf('How we roast')>=0);

wC.eval('go("pmonboard","cafepartner")');
t('cafe partner path has 6 steps', wC.document.querySelectorAll('.pathstep').length===6);

// NEUTRAL MODE must be completely untouched
var wN=load('https://stucky602.github.io/Coffee/');
wN.eval('go("origins")');
t('neutral origins has no PM section', wN.document.getElementById('app').innerHTML.indexOf('On our menu now')<0);
t('neutral origins has no sourced badges', wN.document.querySelectorAll('.origcard.pmsourced').length===0);
t('neutral origins keeps original heading', wN.document.getElementById('app').innerHTML.indexOf('Roasting by Origin')>=0);
wN.eval('go("origin","origin_panama")');
t('neutral origin page has no lots block', wN.document.querySelectorAll('.pmlot').length===0);
wN.eval('go("home")');
t('neutral home has no PM strip', wN.document.querySelectorAll('.pmstripcard').length===0);
wN.eval('go("profiles")');
t('neutral profiles keeps original heading', wN.document.getElementById('app').innerHTML.indexOf('Roast Profiles')>=0);



// ---- v112: back button uses real history from every entry point ----
var wB2=load('https://stucky602.github.io/Coffee/');
wB2.eval('setPmMode(true)');
// home strip -> origin -> back returns HOME (the reported bug)
wB2.eval('go("home"); go("origin","origin_panama");');
t('origin opened from home labels back as Overview', wB2.document.querySelector('.back').textContent.indexOf('Overview')>=0);
wB2.eval('navBack("origins")');
t('back from home-opened origin returns home', wB2.eval('state.view')==='home');
// our coffees -> origin -> back returns to the menu
wB2.eval('go("pmmenucoffee"); go("origin","origin_ethiopia");');
t('origin opened from menu labels back as Our coffees', wB2.document.querySelector('.back').textContent.indexOf('Our coffees')>=0);
wB2.eval('navBack("origins")');
t('back from menu-opened origin returns to menu', wB2.eval('state.view')==='pmmenucoffee');
// origins list -> origin -> back still returns to origins
wB2.eval('go("origins"); go("origin","origin_kenya"); navBack("origins");');
t('back from origins-opened origin returns to origins', wB2.eval('state.view')==='origins');
// origin -> origin names the country
wB2.eval('go("origins"); go("origin","origin_kenya"); go("origin","origin_panama");');
t('origin-to-origin back names the country', wB2.document.querySelector('.back').textContent.indexOf('Kenya')>=0);
// profile detail also uses history
var wP=load('https://stucky602.github.io/Coffee/');
wP.eval('go("compare"); go("profile","cinnamon");');
t('profile opened from compare labels back as Compare', wP.document.querySelector('.back').textContent.indexOf('Compare')>=0);
wP.eval('navBack("profiles")');
t('back from compare-opened profile returns to compare', wP.eval('state.view')==='compare');
wP.eval('go("profiles"); go("profile","french"); navBack("profiles");');
t('back from profiles-opened profile returns to profiles', wP.eval('state.view')==='profiles');

console.log('');
console.log(pass+' passed, '+fail+' failed');
process.exit(fail?1:0);
