#!/usr/bin/env python3
"""Build the self-contained 'Coffee - An Industry Guide' HTML PWA from JSON data."""
import json, pathlib

BASE = pathlib.Path(__file__).parent
profiles = json.loads((BASE / "data_profiles.json").read_text())["PROFILES"]
methodology = json.loads((BASE / "data_methodology.json").read_text())["METHODOLOGY"]

APP_VERSION = "v1"
CACHE_C = "coffee-guide-v1"

PROFILE_GROUPS = [
    ("light", "Light"),
    ("medium", "Medium"),
    ("mediumdark", "Medium-Dark"),
    ("dark", "Dark"),
    ("purpose", "Purpose-Built"),
]
METH_GROUPS = [
    ("read", "Reading the Roast"),
    ("science", "Roast Science"),
    ("practice", "In Practice"),
]

FLAVOR_AXES = [
    ("acidity", "Acidity"),
    ("aroma", "Aroma"),
    ("sweetness", "Sweetness"),
    ("body", "Body"),
    ("bitterness", "Bitterness"),
    ("roast", "Roast"),
]

DATA_JSON = json.dumps({
    "PROFILES": profiles,
    "METHODOLOGY": methodology,
    "PROFILE_GROUPS": PROFILE_GROUPS,
    "METH_GROUPS": METH_GROUPS,
    "FLAVOR_AXES": FLAVOR_AXES,
    "APP_VERSION": APP_VERSION,
}, ensure_ascii=False)

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#1a120b">
<title>Coffee — An Industry Guide</title>
<style>
:root{
  --bg:#160e08; --panel:#1f1610; --panel2:#281c13; --line:#3a2a1c;
  --ink:#f0e6d8; --ink2:#c9b8a4; --ink3:#8f7c66;
  --heat1:#C9A34E; --heat2:#B07B3E; --heat3:#95602F; --heat4:#6E3E1E; --heat5:#43220F;
  --accent:#C9A34E;
  --mono:'SFMono-Regular',ui-monospace,Menlo,Consolas,monospace;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:var(--bg);color:var(--ink);
  font-family:ui-sans-serif,system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
  -webkit-font-smoothing:antialiased;line-height:1.5}
a{color:inherit}
button{font-family:inherit;cursor:pointer}
h1,h2,h3,h4{margin:0;font-weight:650;letter-spacing:-0.01em}
.wrap{max-width:1120px;margin:0 auto;padding:0 20px}

/* header */
header.top{position:sticky;top:0;z-index:40;background:rgba(22,14,8,.92);
  backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.top .wrap{display:flex;align-items:center;gap:14px;height:60px}
.brand{display:flex;align-items:baseline;gap:9px;cursor:pointer;user-select:none}
.brand .mark{font-family:var(--mono);font-size:12px;letter-spacing:.18em;
  color:var(--bg);background:linear-gradient(135deg,var(--heat1),var(--heat3));
  padding:4px 8px;border-radius:5px;font-weight:700}
.brand .nm{font-size:16px;font-weight:700;letter-spacing:-.02em}
.brand .nm b{color:var(--heat1)}
.ver{margin-left:auto;font-family:var(--mono);font-size:11px;color:var(--ink3);
  border:1px solid var(--line);padding:3px 8px;border-radius:20px}
.navtabs{display:flex;gap:2px}
.navtabs button{background:none;border:none;color:var(--ink3);font-size:13.5px;
  font-weight:600;padding:8px 12px;border-radius:7px;transition:.15s}
.navtabs button:hover{color:var(--ink2)}
.navtabs button.on{color:var(--ink);background:var(--panel2)}

/* hero */
.hero{padding:52px 0 30px;border-bottom:1px solid var(--line);position:relative;overflow:hidden}
.hero .wrap{position:relative;z-index:2}
.hero h1{font-size:clamp(30px,5.5vw,52px);line-height:1.02;letter-spacing:-.03em;max-width:15ch}
.hero h1 .grad{background:linear-gradient(100deg,var(--heat1),var(--heat4));
  -webkit-background-clip:text;background-clip:text;color:transparent}
.hero p{color:var(--ink2);font-size:16.5px;max-width:60ch;margin:18px 0 0}
.heatbar{display:flex;height:6px;margin-top:28px;border-radius:4px;overflow:hidden;max-width:520px}
.heatbar i{flex:1}
.hero .beans{position:absolute;inset:0;z-index:1;opacity:.5}

/* section head */
.seclead{display:flex;align-items:baseline;gap:12px;margin:40px 0 4px}
.seclead .no{font-family:var(--mono);font-size:12px;color:var(--heat3);letter-spacing:.1em}
.seclead h2{font-size:22px}
.seclead p{color:var(--ink3);font-size:14px;margin:2px 0 0}
.grouplabel{font-family:var(--mono);font-size:11px;letter-spacing:.16em;text-transform:uppercase;
  color:var(--ink3);margin:26px 0 12px;display:flex;align-items:center;gap:10px}
.grouplabel:after{content:"";flex:1;height:1px;background:var(--line)}

/* profile grid */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px}
.pcard{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px;
  cursor:pointer;transition:.16s;position:relative;overflow:hidden}
.pcard:hover{transform:translateY(-2px);border-color:var(--ink3)}
.pcard .swatch{position:absolute;top:0;left:0;width:4px;height:100%}
.pcard .lvl{font-family:var(--mono);font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--ink3)}
.pcard h3{font-size:19px;margin:5px 0 2px}
.pcard .sub{color:var(--ink3);font-size:12.5px}
.pcard .mini{display:flex;justify-content:center;margin:10px 0 4px}
.pcard .agt{font-family:var(--mono);font-size:11px;color:var(--ink2);text-align:center;margin-top:6px}
.pcard .oneline{color:var(--ink2);font-size:13px;margin-top:10px;line-height:1.45}

/* meth cards */
.mcard{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px 18px;
  cursor:pointer;transition:.16s;display:flex;flex-direction:column;gap:5px}
.mcard:hover{border-color:var(--ink3);background:var(--panel2)}
.mcard .k{font-family:var(--mono);font-size:10.5px;color:var(--heat2);letter-spacing:.1em}
.mcard h3{font-size:17px}
.mcard .sub{color:var(--ink3);font-size:13px}

/* detail */
.detail{padding-bottom:60px}
.back{background:var(--panel2);border:1px solid var(--line);color:var(--ink2);font-size:13px;
  padding:7px 14px;border-radius:8px;margin:22px 0 20px;font-weight:600}
.back:hover{color:var(--ink)}
.dhead{display:flex;flex-wrap:wrap;gap:20px;align-items:flex-start;
  border-bottom:1px solid var(--line);padding-bottom:24px}
.dhead .txt{flex:1;min-width:260px}
.dhead .lvl{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase}
.dhead h1{font-size:34px;letter-spacing:-.03em;margin:6px 0 2px}
.dhead .sub{color:var(--ink3);font-size:15px}
.dhead .oneline{color:var(--ink2);font-size:15.5px;margin:14px 0 0;max-width:56ch;line-height:1.5}
.dhead .usefor{margin-top:14px;font-size:13.5px;color:var(--ink2)}
.dhead .usefor b{color:var(--heat1);font-weight:600}
.radarbox{flex-shrink:0;text-align:center}
.radarbox .cap{font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;
  text-transform:uppercase;color:var(--ink3);margin-top:6px}

.block{margin-top:34px}
.block > h2{font-size:15px;font-family:var(--mono);letter-spacing:.12em;text-transform:uppercase;
  color:var(--heat2);margin-bottom:16px;display:flex;align-items:center;gap:10px}
.block > h2:after{content:"";flex:1;height:1px;background:var(--line)}

/* curve stat table */
.curvegrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.stat .lab{font-size:11.5px;color:var(--ink3);text-transform:uppercase;letter-spacing:.06em}
.stat .val{font-family:var(--mono);font-size:18px;color:var(--ink);margin-top:4px}
.stat .val small{font-size:12px;color:var(--ink3);margin-left:4px}
.stat.hi{border-color:var(--heat3)}
.stat.hi .val{color:var(--heat1)}

/* phases */
.phase{display:flex;gap:16px;padding:16px 0;border-bottom:1px solid var(--line)}
.phase:last-child{border-bottom:none}
.phase .n{font-family:var(--mono);font-size:13px;color:var(--bg);flex-shrink:0;
  width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;
  font-weight:700;background:var(--heat2)}
.phase .c h4{font-size:15.5px;margin-bottom:4px}
.phase .c p{color:var(--ink2);font-size:14px;margin:0}

/* defects */
.defect{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin-bottom:10px}
.defect h4{font-size:14.5px;color:#e08a5a}
.defect .row{font-size:13.5px;color:var(--ink2);margin-top:6px}
.defect .row b{color:var(--ink3);font-weight:600;font-family:var(--mono);font-size:11px;
  text-transform:uppercase;letter-spacing:.08em;margin-right:6px}

.prose{color:var(--ink2);font-size:14.5px;max-width:70ch}
.machine{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--heat3);
  border-radius:10px;padding:16px 18px;color:var(--ink2);font-size:14.5px;max-width:74ch}

/* methodology detail */
.msection{margin-top:22px;max-width:74ch}
.msection h3{font-size:16.5px;color:var(--ink);margin-bottom:6px}
.msection p{color:var(--ink2);font-size:14.5px;margin:0}
.keypoints{background:var(--panel);border:1px solid var(--line);border-radius:12px;
  padding:18px 20px;margin-top:28px;max-width:74ch}
.keypoints h4{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--heat2);margin-bottom:12px}
.keypoints li{color:var(--ink);font-size:14px;margin-bottom:9px;list-style:none;
  padding-left:20px;position:relative}
.keypoints li:before{content:"→";position:absolute;left:0;color:var(--heat3)}

/* compare */
.cmpbar{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0 20px}
.cmpbar button{background:var(--panel);border:1px solid var(--line);color:var(--ink3);
  font-size:12.5px;font-weight:600;padding:6px 12px;border-radius:20px}
.cmpbar button.on{color:var(--bg);border-color:transparent}
.cmpwrap{display:flex;flex-wrap:wrap;gap:24px;align-items:flex-start;justify-content:center;
  background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:26px}
.cmpwrap .lg{flex:1;min-width:280px;display:flex;justify-content:center}
.cmplegend{display:flex;flex-direction:column;gap:10px;min-width:180px}
.cmplegend .it{display:flex;align-items:center;gap:9px;font-size:14px}
.cmplegend .it i{width:12px;height:12px;border-radius:3px;flex-shrink:0}
.cmphint{color:var(--ink3);font-size:13px;margin-top:2px}

footer{border-top:1px solid var(--line);padding:26px 0 44px;color:var(--ink3);font-size:12.5px}
footer .wrap{display:flex;flex-wrap:wrap;gap:8px;justify-content:space-between}

@media(max-width:640px){
  .navtabs{display:none}
  .dhead h1{font-size:27px}
  .hero{padding:36px 0 24px}
}
.mobnav{display:none}
@media(max-width:640px){
  .mobnav{display:flex;position:sticky;top:60px;z-index:30;background:var(--bg);
    border-bottom:1px solid var(--line)}
  .mobnav button{flex:1;background:none;border:none;color:var(--ink3);font-size:13px;
    font-weight:600;padding:11px 0;border-bottom:2px solid transparent}
  .mobnav button.on{color:var(--heat1);border-bottom-color:var(--heat1)}
}
</style>
</head>
<body>
<header class="top">
  <div class="wrap">
    <div class="brand" onclick="go('home')">
      <span class="mark">☕ CIG</span>
      <span class="nm">Coffee<b>·</b>An Industry Guide</span>
    </div>
    <nav class="navtabs">
      <button data-nav="home" onclick="go('home')">Overview</button>
      <button data-nav="profiles" onclick="go('profiles')">Roast Profiles</button>
      <button data-nav="compare" onclick="go('compare')">Compare</button>
      <button data-nav="learn" onclick="go('learn')">Roasting Knowledge</button>
    </nav>
    <span class="ver" id="verlabel"></span>
  </div>
</header>
<nav class="mobnav">
  <button data-nav="home" onclick="go('home')">Overview</button>
  <button data-nav="profiles" onclick="go('profiles')">Profiles</button>
  <button data-nav="compare" onclick="go('compare')">Compare</button>
  <button data-nav="learn" onclick="go('learn')">Learn</button>
</nav>
<main id="app"></main>
<footer><div class="wrap">
  <span>Coffee — An Industry Guide · Roasting reference for working professionals</span>
  <span id="footver"></span>
</div></footer>

<script id="appdata" type="application/json">__DATA__</script>
<script>
const D = JSON.parse(document.getElementById('appdata').textContent);
const {PROFILES,METHODOLOGY,PROFILE_GROUPS,METH_GROUPS,FLAVOR_AXES,APP_VERSION}=D;
document.getElementById('verlabel').textContent=APP_VERSION;
document.getElementById('footver').textContent=APP_VERSION;
const app=document.getElementById('app');
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

/* ---------- RADAR RENDERER ---------- */
// vals: {axisKey:1..5}. size px. accent color. opts: {small, color2, vals2}
function radar(vals, size, accent, opts){
  opts=opts||{};
  const axes=FLAVOR_AXES, N=axes.length;
  const cx=size/2, cy=size/2;
  const pad=opts.small?18:44;
  const R=size/2-pad;
  const rings=5;
  const ptFor=(v,i)=>{
    const ang=-Math.PI/2 + i*(2*Math.PI/N);
    const r=R*(v/5);
    return [cx+r*Math.cos(ang), cy+r*Math.sin(ang)];
  };
  let g='';
  // rings
  for(let ring=1;ring<=rings;ring++){
    let pts=[];
    for(let i=0;i<N;i++){
      const ang=-Math.PI/2 + i*(2*Math.PI/N);
      const r=R*(ring/rings);
      pts.push((cx+r*Math.cos(ang)).toFixed(1)+','+(cy+r*Math.sin(ang)).toFixed(1));
    }
    g+=`<polygon points="${pts.join(' ')}" fill="none" stroke="#3a2a1c" stroke-width="1"/>`;
  }
  // spokes + labels
  for(let i=0;i<N;i++){
    const ang=-Math.PI/2 + i*(2*Math.PI/N);
    const ex=cx+R*Math.cos(ang), ey=cy+R*Math.sin(ang);
    g+=`<line x1="${cx}" y1="${cy}" x2="${ex.toFixed(1)}" y2="${ey.toFixed(1)}" stroke="#3a2a1c" stroke-width="1"/>`;
    if(!opts.small){
      const lx=cx+(R+16)*Math.cos(ang), ly=cy+(R+16)*Math.sin(ang);
      let anchor='middle';
      if(Math.cos(ang)>0.3)anchor='start'; else if(Math.cos(ang)<-0.3)anchor='end';
      g+=`<text x="${lx.toFixed(1)}" y="${(ly+4).toFixed(1)}" fill="#c9b8a4" font-size="11.5" font-family="ui-sans-serif,system-ui" text-anchor="${anchor}">${axes[i][1]}</text>`;
    }
  }
  const drawShape=(vv,col,fillOp)=>{
    let pts=[];
    for(let i=0;i<N;i++){const p=ptFor(vv[axes[i][0]]||0,i);pts.push(p[0].toFixed(1)+','+p[1].toFixed(1));}
    let s=`<polygon points="${pts.join(' ')}" fill="${col}" fill-opacity="${fillOp}" stroke="${col}" stroke-width="2" stroke-linejoin="round"/>`;
    if(!opts.small){for(let i=0;i<N;i++){const p=ptFor(vv[axes[i][0]]||0,i);s+=`<circle cx="${p[0].toFixed(1)}" cy="${p[1].toFixed(1)}" r="2.6" fill="${col}"/>`;}}
    return s;
  };
  g+=drawShape(vals,accent,opts.color2?0.16:0.28);
  if(opts.vals2){g+=drawShape(opts.vals2,opts.color2,0.16);}
  return `<svg viewBox="0 0 ${size} ${size}" width="${size}" height="${size}" style="max-width:100%">${g}</svg>`;
}

/* ---------- ROUTING ---------- */
let state={view:'home'};
function setNav(n){document.querySelectorAll('[data-nav]').forEach(b=>b.classList.toggle('on',b.dataset.nav===n));}
function go(view,arg){state={view,arg};render();window.scrollTo(0,0);
  const top=['home','profiles','compare','learn'].includes(view)?view:
    (view==='profile'?'profiles':view==='meth'?'learn':'home');
  setNav(top);}

function render(){
  const v=state.view;
  if(v==='home')return home();
  if(v==='profiles')return profileList();
  if(v==='profile')return profileDetail(state.arg);
  if(v==='compare')return compare();
  if(v==='learn')return learnList();
  if(v==='meth')return methDetail(state.arg);
  home();
}

/* ---------- HOME ---------- */
function home(){
  const heat=['--heat1','--heat2','--heat3','--heat4','--heat5'].map(h=>`<i style="background:var(${h})"></i>`).join('');
  const nP=Object.keys(PROFILES).length, nM=Object.keys(METHODOLOGY).length;
  app.innerHTML=`
  <section class="hero">
    <div class="wrap">
      <h1>The roast is where green coffee <span class="grad">becomes flavor.</span></h1>
      <p>A working reference for the roastery floor — ${nP} core roast profiles broken down by curve, phase, flavor signature, and failure mode, plus the ${nM} fundamentals every roaster reads by instinct. Built for practitioners, not the shelf.</p>
      <div class="heatbar">${heat}</div>
    </div>
  </section>
  <div class="wrap">
    <div class="seclead"><span class="no">01</span><div><h2>Roast Profiles</h2><p>From Nordic light to Italian dark, plus purpose-built espresso and omni.</p></div></div>
    <div class="grid" style="margin-top:16px">${
      Object.entries(PROFILES).slice(0,6).map(([id,p])=>profileCard(id,p)).join('')
    }</div>
    <div style="margin-top:16px"><button class="back" style="margin:0" onclick="go('profiles')">See all ${nP} profiles →</button></div>

    <div class="seclead"><span class="no">02</span><div><h2>Roasting Knowledge</h2><p>The curve, the chemistry, the machine, and the craft of profiling.</p></div></div>
    <div class="grid" style="margin-top:16px;grid-template-columns:repeat(auto-fill,minmax(230px,1fr))">${
      Object.entries(METHODOLOGY).slice(0,6).map(([id,m])=>methCard(id,m)).join('')
    }</div>
    <div style="margin:16px 0 50px"><button class="back" style="margin:0" onclick="go('learn')">All roasting knowledge →</button></div>
  </div>`;
}

function profileCard(id,p){
  return `<div class="pcard" onclick="go('profile','${id}')">
    <span class="swatch" style="background:${p.accent}"></span>
    <div class="lvl">${esc(p.level)}</div>
    <h3>${esc(p.name)}</h3>
    <div class="sub">${esc(p.sub)}</div>
    <div class="mini">${radar(p.flavor,150,p.accent,{small:true})}</div>
    <div class="agt">AGTRON ${esc(p.agtron)}</div>
    <div class="oneline">${esc(p.oneLine)}</div>
  </div>`;
}
function methCard(id,m){
  return `<div class="mcard" onclick="go('meth','${id}')">
    <span class="k">${METH_GROUPS.find(g=>g[0]===m.group)?.[1]||''}</span>
    <h3>${esc(m.name)}</h3>
    <div class="sub">${esc(m.sub)}</div>
  </div>`;
}

/* ---------- PROFILE LIST ---------- */
function profileList(){
  let html=`<div class="wrap"><div class="seclead"><span class="no">01</span><div><h2>Roast Profiles</h2><p>Ten core profiles spanning the full roast spectrum.</p></div></div>`;
  for(const [gid,glabel] of PROFILE_GROUPS){
    const items=Object.entries(PROFILES).filter(([id,p])=>p.group===gid);
    if(!items.length)continue;
    html+=`<div class="grouplabel">${glabel}</div><div class="grid">${items.map(([id,p])=>profileCard(id,p)).join('')}</div>`;
  }
  html+=`<div style="height:50px"></div></div>`;
  app.innerHTML=html;
}

/* ---------- PROFILE DETAIL ---------- */
function profileDetail(id){
  const p=PROFILES[id]; if(!p)return go('profiles');
  const c=p.curve;
  const stat=(lab,val,unit,hi)=>`<div class="stat ${hi?'hi':''}"><div class="lab">${lab}</div><div class="val">${val}${unit?`<small>${unit}</small>`:''}</div></div>`;
  const dual=(cv,fv)=>`${cv}<small>°C</small> · ${fv}<small>°F</small>`;
  app.innerHTML=`<div class="wrap detail">
    <button class="back" onclick="go('profiles')">← All profiles</button>
    <div class="dhead">
      <div class="txt">
        <div class="lvl" style="color:${p.accent}">${esc(p.level)} · Agtron ${esc(p.agtron)}</div>
        <h1>${esc(p.name)}</h1>
        <div class="sub">${esc(p.sub)}</div>
        <div class="oneline">${esc(p.oneLine)}</div>
        <div class="usefor"><b>Use for —</b> ${esc(p.useFor)}</div>
      </div>
      <div class="radarbox">
        ${radar(p.flavor,240,p.accent,{})}
        <div class="cap">Flavor Signature</div>
      </div>
    </div>

    <div class="block"><h2>The Curve</h2>
      <div class="curvegrid">
        ${stat('Charge',dual(c.chargeC,c.chargeF),'')}
        ${stat('Turning Point',dual(c.tpC,c.tpF),'')}
        ${stat('Drying End',dual(c.dryEndC,c.dryEndF),'')}
        ${stat('First Crack',dual(c.fcC,c.fcF),'',true)}
        ${stat('Drop',dual(c.dropC,c.dropF),'',true)}
        ${stat('Total Time',c.totalTime,'')}
        ${stat('Dev. Ratio (DTR)',c.dtr,'',true)}
      </div>
      <p class="prose" style="margin-top:12px;font-size:13px;color:var(--ink3)">Temperatures are typical bean-temp ranges and vary by roaster; the phase relationships and DTR transfer across machines better than absolute numbers do.</p>
    </div>

    <div class="block"><h2>Phase Walkthrough</h2>
      ${p.phases.map((ph,i)=>`<div class="phase"><div class="n">${i+1}</div><div class="c"><h4>${esc(ph.h)}</h4><p>${esc(ph.body)}</p></div></div>`).join('')}
    </div>

    <div class="block"><h2>Defects &amp; Pitfalls</h2>
      ${p.defects.map(d=>`<div class="defect"><h4>${esc(d.d)}</h4>
        <div class="row"><b>Cause</b>${esc(d.cause)}</div>
        <div class="row"><b>Avoid</b>${esc(d.avoid)}</div></div>`).join('')}
    </div>

    <div class="block"><h2>Machine Considerations</h2>
      <div class="machine">${esc(p.machine)}</div>
    </div>
    <div style="height:40px"></div>
  </div>`;
}

/* ---------- COMPARE ---------- */
let cmpSel=['nordic','cityplus','french'];
const CMP_COLORS=['#C9A34E','#B07B3E','#8A5A34','#6E3E1E','#e08a5a'];
function compare(){
  const ids=Object.keys(PROFILES);
  app.innerHTML=`<div class="wrap">
    <div class="seclead"><span class="no">02</span><div><h2>Compare Profiles</h2><p>Overlay flavor signatures across the fixed six-axis scale. Pick up to four.</p></div></div>
    <div class="cmpbar" id="cmpbar">${ids.map(id=>`<button data-id="${id}" onclick="toggleCmp('${id}')">${esc(PROFILES[id].name)}</button>`).join('')}</div>
    <div class="cmpwrap"><div class="lg" id="cmplg"></div><div class="cmplegend" id="cmpleg"></div></div>
    <div style="height:50px"></div>
  </div>`;
  drawCmp();
}
function toggleCmp(id){
  if(cmpSel.includes(id))cmpSel=cmpSel.filter(x=>x!==id);
  else{if(cmpSel.length>=4)cmpSel.shift();cmpSel.push(id);}
  drawCmp();
}
function drawCmp(){
  document.querySelectorAll('#cmpbar button').forEach(b=>{
    const on=cmpSel.includes(b.dataset.id);b.classList.toggle('on',on);
    if(on){const i=cmpSel.indexOf(b.dataset.id);b.style.background=CMP_COLORS[i];b.style.borderColor=CMP_COLORS[i];}
    else{b.style.background='';b.style.borderColor='';}
  });
  const lg=document.getElementById('cmplg'),leg=document.getElementById('cmpleg');
  if(!cmpSel.length){lg.innerHTML='<p class="cmphint">Select profiles to compare.</p>';leg.innerHTML='';return;}
  // overlay: draw multi-shape radar manually
  const size=340,N=FLAVOR_AXES.length,cx=size/2,cy=size/2,pad=44,R=size/2-pad;
  let g='';
  for(let ring=1;ring<=5;ring++){let pts=[];for(let i=0;i<N;i++){const a=-Math.PI/2+i*(2*Math.PI/N);const r=R*(ring/5);pts.push((cx+r*Math.cos(a)).toFixed(1)+','+(cy+r*Math.sin(a)).toFixed(1));}g+=`<polygon points="${pts.join(' ')}" fill="none" stroke="#3a2a1c" stroke-width="1"/>`;}
  for(let i=0;i<N;i++){const a=-Math.PI/2+i*(2*Math.PI/N);const ex=cx+R*Math.cos(a),ey=cy+R*Math.sin(a);g+=`<line x1="${cx}" y1="${cy}" x2="${ex.toFixed(1)}" y2="${ey.toFixed(1)}" stroke="#3a2a1c"/>`;const lx=cx+(R+16)*Math.cos(a),ly=cy+(R+16)*Math.sin(a);let an='middle';if(Math.cos(a)>0.3)an='start';else if(Math.cos(a)<-0.3)an='end';g+=`<text x="${lx.toFixed(1)}" y="${(ly+4).toFixed(1)}" fill="#c9b8a4" font-size="11.5" text-anchor="${an}">${FLAVOR_AXES[i][1]}</text>`;}
  cmpSel.forEach((id,idx)=>{const col=CMP_COLORS[idx];const f=PROFILES[id].flavor;let pts=[];for(let i=0;i<N;i++){const a=-Math.PI/2+i*(2*Math.PI/N);const r=R*((f[FLAVOR_AXES[i][0]]||0)/5);pts.push((cx+r*Math.cos(a)).toFixed(1)+','+(cy+r*Math.sin(a)).toFixed(1));}g+=`<polygon points="${pts.join(' ')}" fill="${col}" fill-opacity="0.13" stroke="${col}" stroke-width="2" stroke-linejoin="round"/>`;});
  lg.innerHTML=`<svg viewBox="0 0 ${size} ${size}" width="${size}" height="${size}" style="max-width:100%">${g}</svg>`;
  leg.innerHTML=cmpSel.map((id,i)=>`<div class="it"><i style="background:${CMP_COLORS[i]}"></i><span>${esc(PROFILES[id].name)} <span style="color:var(--ink3)">· ${esc(PROFILES[id].level)}</span></span></div>`).join('')+`<div class="cmphint">Tap a profile above to add or remove it.</div>`;
}

/* ---------- LEARN LIST ---------- */
function learnList(){
  let html=`<div class="wrap"><div class="seclead"><span class="no">03</span><div><h2>Roasting Knowledge</h2><p>The fundamentals behind every profile.</p></div></div>`;
  for(const [gid,glabel] of METH_GROUPS){
    const items=Object.entries(METHODOLOGY).filter(([id,m])=>m.group===gid);
    if(!items.length)continue;
    html+=`<div class="grouplabel">${glabel}</div><div class="grid" style="grid-template-columns:repeat(auto-fill,minmax(230px,1fr))">${items.map(([id,m])=>methCard(id,m)).join('')}</div>`;
  }
  html+=`<div style="height:50px"></div></div>`;
  app.innerHTML=html;
}

/* ---------- METH DETAIL ---------- */
function methDetail(id){
  const m=METHODOLOGY[id]; if(!m)return go('learn');
  app.innerHTML=`<div class="wrap detail">
    <button class="back" onclick="go('learn')">← All knowledge</button>
    <div class="dhead" style="border-bottom:none;padding-bottom:6px">
      <div class="txt">
        <div class="lvl" style="color:${m.accent}">${esc(METH_GROUPS.find(g=>g[0]===m.group)?.[1]||'')}</div>
        <h1>${esc(m.name)}</h1>
        <div class="sub">${esc(m.sub)}</div>
      </div>
    </div>
    ${m.sections.map(s=>`<div class="msection"><h3>${esc(s.h)}</h3><p>${esc(s.body)}</p></div>`).join('')}
    ${m.keypoints?`<div class="keypoints"><h4>Key Points</h4><ul style="margin:0;padding:0">${m.keypoints.map(k=>`<li>${esc(k)}</li>`).join('')}</ul></div>`:''}
    <div style="height:40px"></div>
  </div>`;
}

go('home');
</script>
</body>
</html>"""

out = HTML.replace("__DATA__", DATA_JSON)
(BASE / "index.html").write_text(out, encoding="utf-8")
print(f"Built index.html — {len(out):,} bytes")
print(f"Profiles: {len(profiles)} | Methodology pages: {len(methodology)}")
