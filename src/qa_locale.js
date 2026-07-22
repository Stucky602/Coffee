const fs=require('fs');
const {JSDOM}=require('/home/claude/node_modules/jsdom');
const html=fs.readFileSync('index.html','utf8');
let pass=0,fail=0;
function t(n,ok){ok?(pass++,console.log('  ok  '+n)):(fail++,console.log('  FAIL '+n));}

// flags present in header
let w=new JSDOM(html,{url:'https://stucky602.github.io/Coffee/',runScripts:'dangerously',pretendToBeVisual:true}).window;
t('flag buttons render (top row)', w.document.querySelectorAll('.top .wrap .flagbtn').length===2);
t('US flag SVG injected', !!w.document.querySelector('.flagbtn[data-loc=us] svg'));
t('AU flag SVG injected', !!w.document.querySelector('.flagbtn[data-loc=au] svg'));
t('US flag default active', w.document.querySelector('.flagbtn[data-loc=us]').classList.contains('on'));
t('AU flag not active by default', !w.document.querySelector('.flagbtn[data-loc=au]').classList.contains('on'));

// switch to AU, home copy should localize
w.eval("switchLocale('au')");
let home=w.document.getElementById('app').innerHTML;
t('AU active after switch', w.document.querySelector('.flagbtn[data-loc=au]').classList.contains('on'));
t('home shows flavour (AU)', home.includes('flavour'));
t('home shows no US flavor', !/\bflavor\b/.test(home));

// a Learn page also localizes (technical page, vocab still swaps)
w.eval("go('meth','chemistry')");
let chem=w.document.getElementById('app').innerHTML;
t('technical page localizes (caramelis or colour or flavour present)', /caramelis|colour|flavour|centre|litre/.test(chem));

// switch back to US = identity
w.eval("switchLocale('us')");
w.eval("go('home')");
let homeUS=w.document.getElementById('app').innerHTML;
t('US restores flavor', /\bflavor\b/.test(homeUS));
t('US has no flavour', !homeUS.includes('flavour'));

// numbers/units never corrupted in AU
w.eval("switchLocale('au')");
w.eval("go('home',null)");
// dial-in numbers safe
let dw=new JSDOM(html,{url:'https://stucky602.github.io/Coffee/?c=honduras-la-salvaje-coe&ff=pm_dialin',runScripts:'dangerously',pretendToBeVisual:true}).window;
dw.eval("switchLocale('au')");
dw.eval("go('coffee','honduras-la-salvaje-coe')");
let di=dw.document.getElementById('app').innerHTML;
t('dial-in dose 18 g intact in AU', di.includes('18 g'));
t('dial-in ratio 1:2.3 intact in AU', di.includes('1:2.3'));

console.log('\n'+pass+' passed, '+fail+' failed');
process.exit(fail?1:0);
