#!/usr/bin/env python3
"""Build the self-contained 'Coffee - An Industry Guide' HTML PWA from JSON data."""
import json, pathlib

BASE = pathlib.Path(__file__).parent
profiles = json.loads((BASE / "data_profiles.json").read_text())["PROFILES"]
_meth_raw = json.loads((BASE / "data_methodology.json").read_text())
methodology = _meth_raw["METHODOLOGY"]
glossary = _meth_raw.get("GLOSSARY", [])

APP_VERSION = "v6"
CACHE_C = "coffee-guide-v6"

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
    "GLOSSARY": glossary,
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
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Coffee Guide">
<link rel="manifest" href="manifest.webmanifest">
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
.filterbar{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin:22px 0 4px}
.searchwrap{display:flex;align-items:center;gap:8px;background:var(--panel);border:1px solid var(--line);
  border-radius:10px;padding:0 12px;flex:1;min-width:220px;color:var(--ink3)}
.searchwrap:focus-within{border-color:var(--heat3)}
.searchwrap input{background:none;border:none;outline:none;color:var(--ink);font-size:14px;
  padding:10px 0;flex:1;font-family:inherit}
.searchwrap input::placeholder{color:var(--ink3)}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chips button{background:var(--panel);border:1px solid var(--line);color:var(--ink3);font-size:12.5px;
  font-weight:600;padding:7px 12px;border-radius:20px;transition:.14s}
.chips button:hover{color:var(--ink2)}
.chips button.on{background:var(--heat3);border-color:var(--heat3);color:#fff}
.sortwrap{display:flex;align-items:center;gap:7px}
.sortwrap label{font-size:12px;color:var(--ink3);font-weight:600}
.sortwrap select{background:var(--panel);border:1px solid var(--line);color:var(--ink);font-size:13px;
  padding:8px 10px;border-radius:9px;font-family:inherit;cursor:pointer}
.empty{text-align:center;color:var(--ink3);font-size:14px;padding:44px 20px;
  background:var(--panel);border:1px solid var(--line);border-radius:12px;margin-top:16px}

/* start here */
.starthero{padding:40px 0 8px}
.starthero .eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:var(--heat2);margin-bottom:14px}
.starthero h1{font-size:clamp(26px,4.5vw,40px);letter-spacing:-.03em;line-height:1.05}
.starthero .lede{color:var(--ink2);font-size:16.5px;max-width:66ch;margin:18px 0 0;line-height:1.55}
.block2{margin-top:44px}
.block2 .bh{font-size:20px;letter-spacing:-.01em}
.block2 .bsub{color:var(--ink3);font-size:14px;margin:5px 0 18px}
.block2 .bsub b{color:var(--heat1);font-weight:600}
.journey{display:flex;flex-direction:column}
.jstep{display:flex;gap:16px;position:relative;padding-bottom:20px}
.jstep .jdot{width:32px;height:32px;border-radius:50%;flex-shrink:0;display:flex;align-items:center;
  justify-content:center;font-family:var(--mono);font-size:13px;font-weight:700;color:#160e08;z-index:2}
.jstep .jline{position:absolute;left:15.5px;top:32px;bottom:0;width:2px;background:var(--line)}
.jstep .jbody{padding-top:4px}
.jstep .jbody h4{font-size:16px;margin-bottom:3px}
.jstep .jbody p{color:var(--ink2);font-size:14.5px;margin:0;max-width:64ch}
.tradeoff{display:flex;flex-wrap:wrap;align-items:stretch;gap:14px}
.tside{flex:1;min-width:220px;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:18px}
.tside.light{border-left:3px solid var(--heat1)}
.tside.dark{border-left:3px solid var(--heat5)}
.tside .tlabel{font-weight:700;font-size:14.5px;margin-bottom:10px}
.tside.light .tlabel{color:var(--heat1)}
.tside.dark .tlabel{color:#c98a5a}
.tside ul{margin:0;padding-left:18px}
.tside li{color:var(--ink2);font-size:14px;margin-bottom:6px}
.tarrow{display:flex;align-items:center;justify-content:center;font-family:var(--mono);font-size:12px;
  letter-spacing:.1em;color:var(--ink3);padding:0 4px}
.glist{display:flex;flex-direction:column;gap:0;border:1px solid var(--line);border-radius:12px;overflow:hidden}
.grow{display:grid;grid-template-columns:180px 1fr;gap:18px;padding:14px 18px;border-bottom:1px solid var(--line);background:var(--panel)}
.grow:last-child{border-bottom:none}
.grow .gterm{font-weight:650;font-size:14.5px;color:var(--heat1)}
.grow .gdef{color:var(--ink2);font-size:14px;line-height:1.5}
.startcta{margin-top:44px;background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:26px;text-align:center}
.startcta p{font-size:16px;margin:0 0 16px;color:var(--ink)}
.ctarow{display:flex;flex-wrap:wrap;gap:10px;justify-content:center}
.ctarow button{background:var(--heat3);border:1px solid var(--heat3);color:#fff;font-size:14px;
  font-weight:600;padding:11px 18px;border-radius:10px}
.ctarow button.ghost{background:none;border-color:var(--line);color:var(--ink2)}
.ctarow button:hover{opacity:.9}
@media(max-width:560px){.grow{grid-template-columns:1fr;gap:5px}.tarrow{display:none}}

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
.dhead .aka{margin-top:9px;font-size:12.5px;color:var(--ink3);display:flex;flex-wrap:wrap;
  align-items:center;gap:6px}
.dhead .aka span{background:var(--panel2);border:1px solid var(--line);border-radius:20px;
  padding:2px 9px;color:var(--ink2);font-size:12px}
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
.snav{display:grid;grid-template-columns:1fr 1fr;gap:12px;max-width:520px}
.snav-cell{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 16px;
  cursor:pointer;transition:.15s;display:flex;flex-direction:column;gap:3px}
.snav-cell:not(.empty):hover{border-color:var(--ink3);transform:translateY(-2px)}
.snav-cell.empty{background:none;border:1px dashed var(--line);cursor:default;opacity:.4}
.snav-cell .snav-dir{font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;color:var(--ink3);text-transform:uppercase}
.snav-cell .snav-name{font-size:17px;font-weight:650}
.snav-cell .snav-lvl{font-size:12px;color:var(--ink3)}
.snav-cell:last-child{text-align:right;align-items:flex-end}
.curvechart{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 16px 8px;margin-top:16px}
.clegend{display:flex;flex-wrap:wrap;align-items:center;gap:18px;padding:6px 4px 4px;font-size:12px;color:var(--ink2)}
.clegend span{display:flex;align-items:center;gap:7px}
.clegend .ln{width:16px;height:2.6px;border-radius:2px;display:inline-block}
.clegend .ln.dash{background:repeating-linear-gradient(90deg,#7a6a52 0 4px,transparent 4px 7px);height:2px}
.clegend .hint{color:var(--ink3);font-size:11.5px;flex:1;min-width:200px}

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
      <button data-nav="start" onclick="go('start')">Start Here</button>
      <button data-nav="profiles" onclick="go('profiles')">Roast Profiles</button>
      <button data-nav="compare" onclick="go('compare')">Compare</button>
      <button data-nav="learn" onclick="go('learn')">Roasting Knowledge</button>
    </nav>
    <span class="ver" id="verlabel"></span>
  </div>
</header>
<nav class="mobnav">
  <button data-nav="home" onclick="go('home')">Overview</button>
  <button data-nav="start" onclick="go('start')">Start</button>
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
const {PROFILES,METHODOLOGY,GLOSSARY,PROFILE_GROUPS,METH_GROUPS,FLAVOR_AXES,APP_VERSION}=D;
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

/* ---------- ROAST CURVE RENDERER ---------- */
// Parses "a–b" range strings to a midpoint number.
function midRange(s){
  if(s==null)return 0;
  const m=String(s).replace('%','').split(/[–\-]/).map(x=>parseFloat(x)).filter(x=>!isNaN(x));
  return m.length?m.reduce((a,b)=>a+b,0)/m.length:0;
}
// "m:ss" -> seconds
function mmssToSec(s){const p=String(s).split(':').map(Number);return p.length===2?p[0]*60+p[1]:midRange(s)*60;}
// Build BT + RoR sample points for a profile from its curve data. Returns {bt:[[t,temp]],ror:[[t,ror]],marks}
function buildCurve(c){
  const totalSec=midRange(c.totalTime.split('–').map(x=>{const p=x.split(':').map(Number);return p[0]*60+(p[1]||0);}).join('–'));
  // total time as seconds: parse both ends as mm:ss then midpoint
  const ends=c.totalTime.split('–').map(x=>{const p=x.trim().split(':').map(Number);return p[0]*60+(p[1]||0);});
  const total=ends.reduce((a,b)=>a+b,0)/ends.length;
  const dtr=midRange(c.dtr)/100;
  const fcTime=total*(1-dtr);           // first crack occurs so that remaining = dtr
  const charge=midRange(c.chargeC);
  const tp=midRange(c.tpC);
  const tpTime=Math.min(60, total*0.09);// turning point ~ first ~9% or 60s
  const dryEnd=midRange(c.dryEndC);
  const dryTime=total*0.48;             // yellowing ~ 48% of roast
  const fcTemp=midRange(c.fcC);
  const drop=midRange(c.dropC);
  // BT anchor points (time, temp)
  const bt=[[0,charge],[tpTime,tp],[dryTime,dryEnd],[fcTime,fcTemp],[total,drop]];
  // Smooth-sample BT with monotone-ish interpolation between anchors
  const btPts=[];
  const steps=90;
  for(let i=0;i<=steps;i++){
    const t=total*i/steps;
    // find segment
    let a=bt[0],b=bt[1];
    for(let k=0;k<bt.length-1;k++){if(t>=bt[k][0]&&t<=bt[k+1][0]){a=bt[k];b=bt[k+1];break;}}
    const span=(b[0]-a[0])||1; let f=(t-a[0])/span;
    f=f<0?0:f>1?1:f;
    // ease so the turning-point dip and the decelerating climb feel real
    const ef=a===bt[0]?(1-Math.pow(1-f,1.7)):(f*f*(3-2*f)*0.4+f*0.6);
    btPts.push([t, a[1]+(b[1]-a[1])*ef]);
  }
  // RoR = derivative of BT, degrees per 30s, smoothed
  const ror=[];
  for(let i=1;i<btPts.length;i++){
    const dt=btPts[i][0]-btPts[i-1][0];
    const dT=btPts[i][1]-btPts[i-1][1];
    ror.push([btPts[i][0], dt>0?(dT/dt)*30:0]);
  }
  // smooth RoR (moving avg) and clamp negatives near the turn
  const sm=[];
  for(let i=0;i<ror.length;i++){
    let s=0,n=0;for(let k=Math.max(0,i-4);k<=Math.min(ror.length-1,i+4);k++){s+=ror[k][1];n++;}
    sm.push([ror[i][0], Math.max(0,s/n)]);
  }
  return {bt:btPts,ror:sm,total,marks:{tpTime,tp,dryTime,dryEnd,fcTime,fcTemp,drop,charge}};
}
function roastCurve(c,accent,w,h){
  w=w||620;h=h||300;
  const cv=buildCurve(c);
  const L=44,R=44,T=18,B=34;
  const iw=w-L-R, ih=h-T-B;
  const total=cv.total;
  // BT temp scale
  const temps=cv.bt.map(p=>p[1]);
  const tmin=Math.min(...temps)-10, tmax=Math.max(...temps)+8;
  const rorMax=Math.max(...cv.ror.map(p=>p[1]),1)*1.15;
  const X=t=>L+iw*(t/total);
  const Ybt=v=>T+ih*(1-(v-tmin)/(tmax-tmin));
  const Yror=v=>T+ih*(1-v/rorMax);
  const mm=s=>`${Math.floor(s/60)}:${String(Math.round(s%60)).padStart(2,'0')}`;
  let g='';
  // phase shading
  const phases=[[0,cv.marks.dryTime,'Drying','#2a1c10'],[cv.marks.dryTime,cv.marks.fcTime,'Maillard','#33230f'],[cv.marks.fcTime,total,'Development','#3d2913']];
  phases.forEach(ph=>{g+=`<rect x="${X(ph[0]).toFixed(1)}" y="${T}" width="${(X(ph[1])-X(ph[0])).toFixed(1)}" height="${ih}" fill="${ph[3]}" opacity="0.55"/>`;
    const mx=(X(ph[0])+X(ph[1]))/2;g+=`<text x="${mx.toFixed(1)}" y="${T+13}" fill="#8f7c66" font-size="10.5" font-family="ui-sans-serif" text-anchor="middle" letter-spacing="0.5">${ph[2]}</text>`;});
  // gridlines (time)
  for(let s=0;s<=total;s+=120){g+=`<line x1="${X(s).toFixed(1)}" y1="${T}" x2="${X(s).toFixed(1)}" y2="${T+ih}" stroke="#3a2a1c" stroke-width="1" opacity="0.5"/><text x="${X(s).toFixed(1)}" y="${h-14}" fill="#8f7c66" font-size="10" text-anchor="middle" font-family="ui-monospace">${mm(s)}</text>`;}
  // RoR line (secondary, thin, muted)
  let rorPath=cv.ror.map((p,i)=>(i?'L':'M')+X(p[0]).toFixed(1)+' '+Yror(p[1]).toFixed(1)).join(' ');
  g+=`<path d="${rorPath}" fill="none" stroke="#7a6a52" stroke-width="1.6" stroke-dasharray="4 3" opacity="0.85"/>`;
  // BT line (primary, accent)
  let btPath=cv.bt.map((p,i)=>(i?'L':'M')+X(p[0]).toFixed(1)+' '+Ybt(p[1]).toFixed(1)).join(' ');
  g+=`<path d="${btPath}" fill="none" stroke="${accent}" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"/>`;
  // landmark markers
  const mk=(t,v,lab,below)=>{const x=X(t),y=Ybt(v);const ly=below?y+16:y-9;return `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="3.6" fill="${accent}" stroke="#160e08" stroke-width="1.5"/><text x="${x.toFixed(1)}" y="${ly.toFixed(1)}" fill="#f0e6d8" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif" font-weight="600">${lab}</text>`;};
  g+=mk(cv.marks.tpTime,cv.marks.tp,'TP',true);
  // if first crack is within ~8% of total time from the drop, push 1C label below to avoid Drop collision
  const fcClose=(total-cv.marks.fcTime)/total < 0.13;
  g+=mk(cv.marks.fcTime,cv.marks.fcTemp,'1C',fcClose);
  g+=mk(total,cv.marks.drop,'Drop');
  // axis labels
  g+=`<text x="${L-8}" y="${Ybt(tmax)+4}" fill="#8f7c66" font-size="10" text-anchor="end" font-family="ui-monospace">${Math.round(tmax)}°C</text>`;
  g+=`<text x="${L-8}" y="${Ybt(tmin)+4}" fill="#8f7c66" font-size="10" text-anchor="end" font-family="ui-monospace">${Math.round(tmin)}°C</text>`;
  g+=`<text x="${w-R+8}" y="${T+ih-4}" fill="#7a6a52" font-size="10" text-anchor="start" font-family="ui-monospace">RoR</text>`;
  return `<svg viewBox="0 0 ${w} ${h}" width="100%" style="max-width:${w}px" preserveAspectRatio="xMidYMid meet">${g}</svg>`;
}

/* ---------- ROUTING ---------- */
let state={view:'home'};
function setNav(n){document.querySelectorAll('[data-nav]').forEach(b=>b.classList.toggle('on',b.dataset.nav===n));}
function go(view,arg){state={view,arg};render();window.scrollTo(0,0);
  const top=['home','start','profiles','compare','learn'].includes(view)?view:
    (view==='profile'?'profiles':view==='meth'?'learn':'home');
  setNav(top);}

function render(){
  const v=state.view;
  if(v==='home')return home();
  if(v==='start')return startHere();
  if(v==='profiles')return profileList();
  if(v==='profile')return profileDetail(state.arg);
  if(v==='compare')return compare();
  if(v==='learn')return learnList();
  if(v==='meth')return methDetail(state.arg);
  home();
}

/* ---------- START HERE ---------- */
function startHere(){
  const journey=[
    {k:'Green',c:'#7d8f5a',d:"Raw coffee beans — actually fruit seeds — dense, grassy, about 10-12% water. Not drinkable yet."},
    {k:'Charge',c:'#C9A34E',d:"You tip the green beans into the hot roaster. The clock starts. The beans immediately cool the drum down."},
    {k:'Drying',c:'#B07B3E',d:"Beans shed moisture and turn from green to yellow. They smell grassy, then like hay, then like baking bread."},
    {k:'Maillard',c:'#95602F',d:"Yellow to light brown. The browning chemistry that crusts bread kicks in. Most of the flavor is built right here."},
    {k:'First crack',c:'#6E3E1E',d:"A popcorn-like POP around 196°C. Beans nearly double in size. The roaster's key landmark — light roasts drop just after."},
    {k:'Development',c:'#5A2F16',d:"From first crack to the drop. Sharpness mellows into sweetness. Go longer and darker for bolder, roastier coffee."},
    {k:'Drop',c:'#3a2412',d:"You dump the beans into the cooling tray to stop the roast. Done. How dark you let it get before dropping is the whole game."},
  ];
  app.innerHTML=`<div class="wrap">
    <div class="starthero">
      <div class="eyebrow">Start Here</div>
      <h1>New to roasting? Read this first.</h1>
      <p class="lede">Roasting is how raw, grassy green coffee seeds become the brown, aromatic beans you grind and brew. You apply heat over roughly 8 to 17 minutes, the beans dry out, brown, and crack open, and you decide exactly when to stop. Stop early for bright, fruity, light coffee; go longer for bold, dark, roasty coffee. That's the whole craft — everything else is detail.</p>
    </div>

    <div class="block2"><h2 class="bh">The journey, green to cup</h2>
    <p class="bsub">Every roast, on every machine, moves through these stages in order. This is the map.</p>
    <div class="journey">${journey.map((s,i)=>`
      <div class="jstep">
        <div class="jdot" style="background:${s.c}">${i+1}</div>
        ${i<journey.length-1?'<div class="jline"></div>':''}
        <div class="jbody"><h4>${s.k}</h4><p>${s.d}</p></div>
      </div>`).join('')}
    </div></div>

    <div class="block2"><h2 class="bh">The one trade-off to understand</h2>
    <p class="bsub">If you remember nothing else, remember this.</p>
    <div class="tradeoff">
      <div class="tside light"><div class="tlabel">Stop earlier / lighter</div><ul><li>Brighter, more acidic, fruitier</li><li>Origin character shines through</li><li>More delicate, more aromatic</li></ul></div>
      <div class="tarrow">→ darker →</div>
      <div class="tside dark"><div class="tlabel">Stop later / darker</div><ul><li>Bolder, heavier body, more bitter</li><li>Roast flavor takes over origin</li><li>Smoky, toasty, lower acidity</li></ul></div>
    </div>
    <p class="bsub" style="margin-top:14px">The <b>drop</b> — when you pull the beans out — is where you commit to that choice. That's why you saw the word everywhere.</p>
    </div>

    <div class="block2"><h2 class="bh">Every term, in plain English</h2>
    <p class="bsub">The jargon the rest of the app uses. Filter to jump to one.</p>
    <div class="searchwrap" style="max-width:340px;margin-bottom:16px">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg>
      <input id="glsearch" type="search" placeholder="Filter terms…" autocomplete="off">
    </div>
    <div class="glist" id="glist">${glossaryRows(GLOSSARY)}</div>
    </div>

    <div class="startcta">
      <p>Ready to see it in action?</p>
      <div class="ctarow">
        <button onclick="go('profiles')">Browse roast profiles →</button>
        <button class="ghost" onclick="go('learn')">Go deeper on the fundamentals →</button>
      </div>
    </div>
    <div style="height:40px"></div>
  </div>`;
  const gs=document.getElementById('glsearch');
  if(gs)gs.oninput=e=>{
    const q=e.target.value.toLowerCase().trim();
    const rows=GLOSSARY.filter(g=>!q||(g.term+' '+g.def).toLowerCase().includes(q));
    document.getElementById('glist').innerHTML=rows.length?glossaryRows(rows):`<div class="empty">No term matches that.</div>`;
  };
}
function glossaryRows(rows){
  return rows.map(g=>`<div class="grow"><div class="gterm">${esc(g.term)}</div><div class="gdef">${esc(g.def)}</div></div>`).join('');
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
let profQuery='', profLevel='all', profSort='spectrum';
function profileList(){
  app.innerHTML=`<div class="wrap"><div class="seclead"><span class="no">01</span><div><h2>Roast Profiles</h2><p>Ten core profiles spanning the full roast spectrum.</p></div></div>
    <div class="filterbar">
      <div class="searchwrap">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg>
        <input id="psearch" type="search" placeholder="Search profiles — name, use, flavor…" value="${esc(profQuery)}" autocomplete="off">
      </div>
      <div class="chips" id="plevels"></div>
      <div class="sortwrap"><label>Sort</label><select id="psort"></select></div>
    </div>
    <div id="presults"></div>
    <div style="height:50px"></div></div>`;
  const levels=['all',...PROFILE_GROUPS.map(g=>g[1])];
  document.getElementById('plevels').innerHTML=levels.map(l=>`<button data-lv="${l}" class="${profLevel===l?'on':''}" onclick="setProfLevel('${l}')">${l==='all'?'All':l}</button>`).join('');
  const sorts=[['spectrum','Roast spectrum'],['acidity','Most acidic'],['body','Most body'],['sweetness','Sweetest'],['bitterness','Most bitter'],['roast','Most roast'],['aroma','Most aromatic']];
  document.getElementById('psort').innerHTML=sorts.map(s=>`<option value="${s[0]}" ${profSort===s[0]?'selected':''}>${s[1]}</option>`).join('');
  document.getElementById('psort').onchange=e=>{profSort=e.target.value;drawProfResults();};
  const si=document.getElementById('psearch');
  si.oninput=e=>{profQuery=e.target.value;drawProfResults();};
  drawProfResults();
  // keep focus after redraw
  const s2=document.getElementById('psearch'); if(profQuery){s2.focus();s2.setSelectionRange(profQuery.length,profQuery.length);}
}
function setProfLevel(l){profLevel=l;document.querySelectorAll('#plevels button').forEach(b=>b.classList.toggle('on',b.dataset.lv===l));drawProfResults();}
function matchProf(p,q){
  if(!q)return true; q=q.toLowerCase().trim();
  const hay=[p.name,p.sub,p.level,p.oneLine,p.useFor,p.agtron,(p.aka||[]).join(' ')].join(' ').toLowerCase();
  // flavor descriptors that score high (>=4) for this profile
  const strong=FLAVOR_AXES.filter(a=>(p.flavor[a[0]]||0)>=4).map(a=>a[1]).join(' ').toLowerCase();
  // synonym map: search word -> flavor axis that must score high
  const SYN={bright:'acidity',acidic:'acidity',fruity:'acidity',juicy:'acidity',citrus:'acidity',lively:'acidity',
    sweet:'sweetness',caramel:'sweetness',
    bold:'body','full-bodied':'body',heavy:'body',rich:'body',
    bitter:'bitterness',dark:'bitterness',
    roasty:'roast',smoky:'roast',toasty:'roast',
    floral:'aroma',aromatic:'aroma',fragrant:'aroma',complex:'aroma'};
  if(SYN[q] && (p.flavor[SYN[q]]||0)>=4)return true;
  return (hay+' '+strong).includes(q);
}
function drawProfResults(){
  const box=document.getElementById('presults'); if(!box)return;
  let entries=Object.entries(PROFILES).filter(([id,p])=>matchProf(p,profQuery));
  if(profLevel!=='all')entries=entries.filter(([id,p])=>PROFILE_GROUPS.find(g=>g[1]===profLevel)?.[0]===p.group);
  if(profSort==='spectrum'){
    const order=PROFILE_GROUPS.map(g=>g[0]);
    // grouped view, spectrum order
    let html='';
    for(const [gid,glabel] of PROFILE_GROUPS){
      const items=entries.filter(([id,p])=>p.group===gid);
      if(!items.length)continue;
      html+=`<div class="grouplabel">${glabel}</div><div class="grid">${items.map(([id,p])=>profileCard(id,p)).join('')}</div>`;
    }
    box.innerHTML=html||emptyState();
  }else{
    // flat, sorted by chosen flavor axis descending
    entries.sort((a,b)=>(b[1].flavor[profSort]||0)-(a[1].flavor[profSort]||0));
    const label=FLAVOR_AXES.find(a=>a[0]===profSort)?.[1]||'';
    box.innerHTML=entries.length?`<div class="grouplabel">Sorted by ${label.toLowerCase()} — highest first</div><div class="grid">${entries.map(([id,p])=>profileCard(id,p)).join('')}</div>`:emptyState();
  }
}
function emptyState(){return `<div class="empty">No profiles match that. Try a roast level, a flavor like “bright” or “bitter,” or clear the search.</div>`;}

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
        ${p.aka&&p.aka.length?`<div class="aka">also called ${p.aka.map(a=>`<span>${esc(a)}</span>`).join('')}</div>`:''}
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
      <div class="curvechart">${roastCurve(p.curve,p.accent,620,300)}
        <div class="clegend"><span><i class="ln" style="background:${p.accent}"></i>Bean temp</span><span><i class="ln dash"></i>Rate of rise</span><span class="hint">Idealized from this profile's data — your machine's curve will differ in absolute temps, not in shape.</span></div>
      </div></div>

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
    ${spectrumNav(id)}
    <div style="height:40px"></div>
  </div>`;
}
function spectrumNav(id){
  // walk the light→dark spectrum (exclude purpose-built, which aren't on the line)
  const line=Object.entries(PROFILES).filter(([k,pp])=>pp.group!=='purpose').map(([k])=>k);
  const i=line.indexOf(id);
  if(i<0)return '';
  const lighter=i>0?line[i-1]:null, darker=i<line.length-1?line[i+1]:null;
  const cell=(nid,dir)=>{
    if(!nid)return `<div class="snav-cell empty"></div>`;
    const n=PROFILES[nid];
    return `<div class="snav-cell" onclick="go('profile','${nid}')">
      <span class="snav-dir">${dir==='light'?'← Lighter':'Darker →'}</span>
      <span class="snav-name" style="color:${n.accent}">${esc(n.name)}</span>
      <span class="snav-lvl">${esc(n.level)}</span></div>`;
  };
  return `<div class="block"><h2>Along the Spectrum</h2>
    <div class="snav">${cell(lighter,'light')}${cell(darker,'dark')}</div></div>`;
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

if('serviceWorker' in navigator){
  window.addEventListener('load',()=>{navigator.serviceWorker.register('sw.js').catch(()=>{});});
}
</script>
</body>
</html>"""

out = HTML.replace("__DATA__", DATA_JSON)
(BASE / "index.html").write_text(out, encoding="utf-8")

# --- PWA manifest ---
manifest = {
    "name": "Coffee — An Industry Guide",
    "short_name": "Coffee Guide",
    "description": "A working roasting reference for coffee professionals.",
    "start_url": "./",
    "scope": "./",
    "display": "standalone",
    "background_color": "#160e08",
    "theme_color": "#1a120b",
    "icons": [
        {"src": "icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any"}
    ],
}
(BASE / "manifest.webmanifest").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

# --- App icon (simple roasted-bean mark, SVG scales to any size) ---
icon = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
<rect width="512" height="512" rx="96" fill="#160e08"/>
<defs><linearGradient id="h" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#C9A34E"/><stop offset="1" stop-color="#95602F"/></linearGradient></defs>
<ellipse cx="256" cy="256" rx="132" ry="168" fill="url(#h)"/>
<path d="M256 96 C 210 180, 302 332, 256 416" fill="none" stroke="#160e08" stroke-width="26" stroke-linecap="round"/>
</svg>'''
(BASE / "icon.svg").write_text(icon, encoding="utf-8")

# --- Service worker: cache the shell for offline field use ---
sw = f'''const CACHE="{CACHE_C}";
const ASSETS=["./","./index.html","./manifest.webmanifest","./icon.svg"];
self.addEventListener("install",e=>{{
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)).catch(()=>{{}}));
}});
self.addEventListener("activate",e=>{{
  e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));
}});
self.addEventListener("fetch",e=>{{
  if(e.request.method!=="GET")return;
  e.respondWith(
    caches.match(e.request).then(hit=>hit||fetch(e.request).then(res=>{{
      const copy=res.clone();
      caches.open(CACHE).then(c=>c.put(e.request,copy)).catch(()=>{{}});
      return res;
    }}).catch(()=>caches.match("./index.html")))
  );
}});
'''
(BASE / "sw.js").write_text(sw, encoding="utf-8")

print(f"Built index.html — {len(out):,} bytes")
print(f"Profiles: {len(profiles)} | Methodology pages: {len(methodology)}")
print("Also wrote: manifest.webmanifest, icon.svg, sw.js")
