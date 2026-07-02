#!/usr/bin/env python3
"""Build the self-contained 'Coffee - An Industry Guide' HTML PWA from JSON data."""
import json, pathlib

BASE = pathlib.Path(__file__).parent
profiles = json.loads((BASE / "data_profiles.json").read_text())["PROFILES"]
_meth_raw = json.loads((BASE / "data_methodology.json").read_text())
methodology = _meth_raw["METHODOLOGY"]
glossary = _meth_raw.get("GLOSSARY", [])

APP_VERSION = "v14"
CACHE_C = "coffee-guide-v14"

PROFILE_GROUPS = [
    ("light", "Light"),
    ("medium", "Medium"),
    ("mediumdark", "Medium-Dark"),
    ("dark", "Dark"),
    ("purpose", "Purpose-Built"),
]
METH_GROUPS = [
    ("green", "Green Buying & QC"),
    ("read", "Reading the Roast"),
    ("science", "Roast Science"),
    ("practice", "In Practice"),
    ("cupping", "Cupping & Quality"),
    ("ops", "Roastery Operations"),
    ("brew", "Brewing & Barista"),
]

# Per-group metadata for the Learn hub: one-line description + accent color.
# Ordered to follow the bean's journey: buy green → roast → taste → run the shop → brew.
METH_GROUP_META = {
    "green":   {"desc": "Grading defects, moisture and density, processing methods, and reading a green coffee before you buy it.", "accent": "#7d8f5a"},
    "read":    {"desc": "The roast curve, rate of rise, the phases, first and second crack, and development time — how to read a roast as it happens.", "accent": "#C9A34E"},
    "science": {"desc": "What's chemically happening inside the bean, how heat moves through the drum, and the machines that do it.", "accent": "#B07B3E"},
    "practice":{"desc": "Roast defects and how to diagnose them, plus sample roasting and dialing in a profile.", "accent": "#95602F"},
    "origin":  {"desc": "How coffee from eight origins behaves in the roaster and the target roast for each.", "accent": "#8A5A34"},
    "cupping": {"desc": "Cupping mechanics, the modern CVA and legacy scoring, the flavor wheel, and the roaster's QC loop.", "accent": "#6E3E1E"},
    "ops":     {"desc": "Running the roastery day: warm-up, between-batch protocol, fire safety, decaf, degassing, and logging.", "accent": "#7A4A28"},
    "brew":    {"desc": "Behind the bar: extraction theory, dialing espresso, grind, brew methods, milk, and water.", "accent": "#5A2F16"},
}

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
    "METH_GROUP_META": METH_GROUP_META,
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
a,a:visited{color:inherit}
button{font-family:inherit;cursor:pointer}
h1,h2,h3,h4{margin:0;font-weight:650;letter-spacing:-0.01em}
.wrap{max-width:1120px;margin:0 auto;padding:0 20px}

/* header */
header.top{position:sticky;top:0;z-index:40;background:rgba(22,14,8,.92);
  backdrop-filter:blur(10px);border-bottom:1px solid var(--line);
  padding-top:env(safe-area-inset-top,0px)}
.top .wrap{display:flex;align-items:center;gap:14px;height:60px;
  padding-left:calc(20px + env(safe-area-inset-left,0px));
  padding-right:calc(20px + env(safe-area-inset-right,0px))}
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
.hero .lede{font-size:17.5px;line-height:1.55;max-width:64ch}
.heatbar{display:flex;height:6px;margin-top:28px;border-radius:4px;overflow:hidden;max-width:520px}
.heatbar i{flex:1}
.hero .beans{position:absolute;inset:0;z-index:1;opacity:.5}

/* home section directory */
.dirlead{font-family:var(--mono);font-size:11px;letter-spacing:.18em;text-transform:uppercase;
  color:var(--ink3);margin:34px 0 16px}
.secdir{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:14px}
.secard{display:flex;gap:16px;text-align:left;background:var(--panel);border:1px solid var(--line);
  border-radius:16px;padding:20px;cursor:pointer;transition:.16s;align-items:flex-start}
.secard:hover{border-color:var(--heat3);background:var(--panel2);transform:translateY(-2px)}
.secard-ic{flex-shrink:0;width:44px;height:44px;border-radius:11px;display:flex;align-items:center;
  justify-content:center;background:var(--bg);border:1px solid var(--line);color:var(--heat2)}
.secard-body{display:flex;flex-direction:column;gap:6px;min-width:0}
.secard-title{font-size:18px;font-weight:700;color:var(--ink1);letter-spacing:-.01em}
.secard-blurb{font-size:13.5px;color:var(--ink3);line-height:1.5}
.secard-cta{font-size:13px;font-weight:600;color:var(--heat1);margin-top:3px}

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
.mgrid{grid-template-columns:repeat(auto-fill,minmax(230px,1fr))}

/* learn hub */
.lcount,.hublist .lcount{font-family:var(--mono);font-size:11px;letter-spacing:.12em;text-transform:uppercase;
  color:var(--ink3);margin-bottom:12px}
.hublist{display:flex;flex-direction:column;gap:12px}
.hubgroup{border:1px solid var(--line);border-radius:14px;overflow:hidden;background:var(--panel);transition:.16s}
.hubgroup.open{background:var(--panel2);border-color:var(--ink3)}
.hubhead{width:100%;display:flex;align-items:center;gap:14px;padding:16px 18px;background:none;border:none;
  text-align:left;cursor:pointer;transition:.16s}
.hubhead:hover{background:var(--panel2)}
.hubbar{width:4px;align-self:stretch;border-radius:3px;background:var(--ga);flex-shrink:0;min-height:34px}
.hubtxt{display:flex;flex-direction:column;gap:3px;flex:1;min-width:0}
.hubname{font-size:18px;font-weight:600;color:var(--ink1)}
.hubdesc{font-size:13px;color:var(--ink3);line-height:1.45}
.hubcount{font-family:var(--mono);font-size:12.5px;color:var(--ink2);background:var(--bg);border:1px solid var(--line);
  border-radius:20px;padding:3px 10px;flex-shrink:0;line-height:1;align-self:center}
.hubchev{font-family:var(--mono);font-size:18px;color:var(--ink3);width:16px;text-align:center;flex-shrink:0;
  align-self:center;line-height:1}
.hubcards{padding:4px 18px 18px}

/* origins tab */
.originmapwrap{margin:18px 0 8px;border:1px solid var(--line);border-radius:16px;overflow:hidden;background:#12100c}
.mapcap{font-size:12.5px;color:var(--ink3);padding:10px 14px;border-top:1px solid var(--line);text-align:center}
.mapdot text{pointer-events:none}
.mapdot:hover circle:last-of-type{r:9}
.originnote{color:var(--ink2);font-size:15px;line-height:1.6;max-width:70ch;margin:20px 0 8px}
.origrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:13px;margin-top:4px}
.origcard{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:17px;cursor:pointer;
  transition:.16s;display:flex;flex-direction:column;gap:9px}
.origcard:hover{border-color:var(--heat3);background:var(--panel2);transform:translateY(-2px)}
.origcard-top{display:flex;align-items:center;justify-content:space-between;gap:10px}
.origcard-name{font-size:18px;font-weight:700;letter-spacing:-.01em}
.origcard-roast{font-family:var(--mono);font-size:10px;letter-spacing:.06em;text-transform:uppercase;
  color:var(--rc);border:1px solid var(--rc);border-radius:20px;padding:3px 9px;opacity:.9;white-space:nowrap}
.origcard-blurb{font-size:13px;color:var(--ink3);line-height:1.5;flex:1}
.origcard-tags{display:flex;flex-wrap:wrap;gap:5px}
.origcard-tags span{font-size:11px;color:var(--ink2);background:var(--bg);border:1px solid var(--line);
  border-radius:20px;padding:2px 8px}
.origcard-meta{font-family:var(--mono);font-size:11px;color:var(--ink3)}
/* origin detail */
.odhead{display:flex;flex-wrap:wrap;gap:24px;align-items:flex-start;padding-bottom:8px}
.odtxt{flex:1;min-width:260px}
.odtxt h1{font-size:34px;letter-spacing:-.03em;margin:6px 0 2px}
.odtxt .sub{color:var(--ink3);font-size:15px}
.odtxt .oneline{color:var(--ink2);font-size:15.5px;line-height:1.55;max-width:60ch}
.origtags{display:flex;flex-wrap:wrap;gap:6px;margin-top:14px}
.origtags span{font-size:12px;color:var(--ink2);background:var(--panel2);border:1px solid var(--line);
  border-radius:20px;padding:3px 10px}
.odroast{flex-shrink:0;margin:0 auto}
.odroast-ring{width:120px;height:120px;border-radius:50%;border:3px solid var(--rc);display:flex;
  flex-direction:column;align-items:center;justify-content:center;gap:3px;
  background:radial-gradient(circle,color-mix(in srgb,var(--rc) 14%,transparent),transparent)}
.odroast-ring span{font-size:16px;font-weight:700;color:var(--ink1);text-align:center;padding:0 8px;line-height:1.1}
.odroast-ring small{font-family:var(--mono);font-size:9px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink3)}
.factstrip{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1px;background:var(--line);
  border:1px solid var(--line);border-radius:12px;overflow:hidden;margin:22px 0 8px}
.fact{background:var(--panel);padding:13px 15px}
.fact .fl{font-family:var(--mono);font-size:9.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink3);margin-bottom:4px}
.fact .fv{font-size:13.5px;color:var(--ink1);line-height:1.35}

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
.radarbox{flex-shrink:0;text-align:center;margin:0 auto}
.radarbox svg{display:block;margin:0 auto}
.radarbox .cap{font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;
  text-transform:uppercase;color:var(--ink3);margin-top:6px}
@media(max-width:640px){
  .dhead{justify-content:center}
  .dhead .txt{flex:1 1 100%}
  .radarbox{flex:1 1 100%;margin-top:6px}
}

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
.pairintro{color:var(--ink2);font-size:14.5px;line-height:1.55;max-width:72ch;margin-bottom:14px}
.opairgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px}
.opair{text-align:left;background:var(--panel);border:1px solid var(--line);border-radius:11px;padding:13px 15px;
  cursor:pointer;transition:.15s;display:flex;flex-direction:column;gap:4px}
.opair:hover{border-color:var(--heat3);background:var(--panel2);transform:translateY(-2px)}
.opair-name{font-size:15.5px;font-weight:650;color:var(--ink1)}
.opair-tags{font-size:12px;color:var(--ink3)}
.pairnote{font-size:12.5px;color:var(--ink3);margin-top:12px;font-style:italic}
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
.curvehead{display:flex;align-items:center;justify-content:space-between;margin-bottom:6px}
.curvetitle{font-family:var(--mono);font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink3)}
.unittoggle{display:flex;gap:0;border:1px solid var(--line);border-radius:8px;overflow:hidden}
.unittoggle button{background:var(--panel);border:none;color:var(--ink3);font-size:12px;font-weight:600;
  padding:5px 12px;font-family:var(--mono);transition:.14s}
.unittoggle button.on{background:var(--heat3);color:#fff}

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
.refs{margin-top:26px;max-width:74ch}
.refs h4{font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--ink3);margin-bottom:10px}
.refs ul{margin:0;padding:0;list-style:none}
.refs li{margin-bottom:7px;padding-left:16px;position:relative}
.refs li:before{content:"↗";position:absolute;left:0;color:var(--ink3);font-size:11px}
.refs a,.refs a:visited{color:var(--ink2);font-size:13px;text-decoration:none;border-bottom:1px solid var(--line);
  transition:.14s}
.refs a:hover{color:var(--heat1);border-color:var(--heat3)}
.siblings{margin-top:34px;padding-top:26px;border-top:1px solid var(--line)}
.siblings h4{font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--ink3);margin-bottom:14px}
.beangal{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:14px;margin-top:14px}
.beanfig{margin:0;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 12px;
  display:flex;flex-direction:column;align-items:center;gap:8px;text-align:center}
.beanfig svg{display:block}
.beanfig figcaption{display:flex;flex-direction:column;gap:2px}
.beanfig figcaption b{font-size:13.5px;color:var(--ink1)}
.beanfig figcaption span{font-size:11.5px;color:var(--ink3);line-height:1.4}
.diagram{margin:20px 0 8px;background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px 18px 14px}
.diagram svg{display:block}
.diagram figcaption{font-size:12.5px;color:var(--ink3);line-height:1.5;margin-top:10px;max-width:70ch}

/* compare */
.cmpmodebar{display:flex;gap:0;border:1px solid var(--line);border-radius:9px;overflow:hidden;width:fit-content;margin-bottom:16px}
.cmpmodebar button{background:var(--panel);border:none;color:var(--ink3);font-size:13px;font-weight:600;padding:8px 18px;transition:.14s}
.cmpmodebar button.on{background:var(--heat3);color:#fff}
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
  .mobnav{display:flex;position:sticky;top:calc(60px + env(safe-area-inset-top,0px));z-index:30;background:var(--bg);
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
      <button data-nav="origins" onclick="go('origins')">Origins</button>
      <button data-nav="compare" onclick="go('compare')">Compare</button>
      <button data-nav="learn" onclick="go('learn')">Learn</button>
    </nav>
    <span class="ver" id="verlabel"></span>
  </div>
</header>
<nav class="mobnav">
  <button data-nav="home" onclick="go('home')">Overview</button>
  <button data-nav="profiles" onclick="go('profiles')">Profiles</button>
  <button data-nav="origins" onclick="go('origins')">Origins</button>
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
const {PROFILES,METHODOLOGY,GLOSSARY,PROFILE_GROUPS,METH_GROUPS,METH_GROUP_META,FLAVOR_AXES,APP_VERSION}=D;
document.getElementById('verlabel').textContent=APP_VERSION;
document.getElementById('footver').textContent=APP_VERSION;
const app=document.getElementById('app');
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

/* ---------- RADAR RENDERER ---------- */
// vals: {axisKey:1..5}. size px. accent color. opts: {small, color2, vals2}
function radar(vals, size, accent, opts){
  opts=opts||{};
  const axes=FLAVOR_AXES, N=axes.length;
  // Horizontal margin so side labels (e.g. "Bitterness") aren't clipped by the viewBox edge.
  const M=opts.small?0:48;
  const cx=size/2+M, cy=size/2;
  const vbW=size+M*2;
  const pad=opts.small?18:30;
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
      const lx=cx+(R+15)*Math.cos(ang), ly=cy+(R+15)*Math.sin(ang);
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
  return `<svg viewBox="0 0 ${vbW} ${size}" width="${size}" height="${size}" style="max-width:100%">${g}</svg>`;
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
function roastCurve(c,accent,w,h,units){
  w=w||620;h=h||300;units=units||'C';
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
  const showT=cVal=>units==='F'?Math.round(cVal*9/5+32)+'°F':Math.round(cVal)+'°C';
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
  g+=`<text x="${L-8}" y="${Ybt(tmax)+4}" fill="#8f7c66" font-size="10" text-anchor="end" font-family="ui-monospace">${showT(tmax)}</text>`;
  g+=`<text x="${L-8}" y="${Ybt(tmin)+4}" fill="#8f7c66" font-size="10" text-anchor="end" font-family="ui-monospace">${showT(tmin)}</text>`;
  g+=`<text x="${w-R+8}" y="${T+ih-4}" fill="#7a6a52" font-size="10" text-anchor="start" font-family="ui-monospace">RoR</text>`;
  return `<svg viewBox="0 0 ${w} ${h}" width="100%" style="max-width:${w}px" preserveAspectRatio="xMidYMid meet">${g}</svg>`;
}

/* ---------- ROUTING ---------- */
let state={view:'home'};
function setNav(n){document.querySelectorAll('[data-nav]').forEach(b=>b.classList.toggle('on',b.dataset.nav===n));}
function go(view,arg){state={view,arg};render();window.scrollTo(0,0);
  const top=['home','start','profiles','origins','compare','learn'].includes(view)?view:
    (view==='profile'?'profiles':view==='origin'?'origins':view==='meth'?'learn':'home');
  setNav(top);}

function render(){
  const v=state.view;
  if(v==='home')return home();
  if(v==='start')return startHere();
  if(v==='profiles')return profileList();
  if(v==='profile')return profileDetail(state.arg);
  if(v==='origins')return originList();
  if(v==='origin')return originDetail(state.arg);
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
  const nO=Object.entries(METHODOLOGY).filter(([id,m])=>m.group==='origin').length;
  const nLearn=nM-nO; // learn topics excluding origins (now its own tab)
  // section directory: [icon-svg, title, blurb, button label, target view]
  const sections=[
    [svgIcon('profiles'),'Roast Profiles',`Every roast level from Nordic light to Italian dark — plus purpose-built espresso and omni — broken down by curve, phase, flavor signature, and the ways each one fails.`,`Browse ${nP} profiles`,`profiles`],
    [svgIcon('compare'),'Compare',`Lay any profiles side by side — overlay their flavor radars or their roast curves to see exactly how a light and a dark diverge.`,`Open compare`,`compare`],
    [svgIcon('origin'),'Roasting by Origin',`How coffee from ${nO} growing regions behaves in the roaster — what the green is like, how to handle it, and the roast level that shows it best.`,`Explore origins`,`origins`],
    [svgIcon('learn'),'Learn',`${nLearn} deep-dives across the whole craft: green buying and grading, reading the roast, the science, cupping and quality, running a roastery, and brewing behind the bar.`,`Start learning`,`learn`],
    [svgIcon('start'),'New to Coffee?',`Start here. A plain-language tour of how green becomes the cup, the light-versus-dark tradeoff, and a glossary that decodes the jargon.`,`Get oriented`,`start`],
  ];
  app.innerHTML=`
  <section class="hero">
    <div class="wrap">
      <h1>Where green coffee <span class="grad">becomes flavor.</span></h1>
      <p class="lede">A field reference for people who roast, brew, and buy coffee for a living — from the green bean and the roast curve all the way to the cup. The theory that actually changes what you do at the machine, with none of the fluff.</p>
      <div class="heatbar">${heat}</div>
    </div>
  </section>
  <div class="wrap">
    <div class="dirlead">Jump in anywhere</div>
    <div class="secdir">${sections.map(s=>`
      <button class="secard" onclick="go('${s[4]}')">
        <span class="secard-ic">${s[0]}</span>
        <span class="secard-body">
          <span class="secard-title">${s[1]}</span>
          <span class="secard-blurb">${s[2]}</span>
          <span class="secard-cta">${s[3]} →</span>
        </span>
      </button>`).join('')}
    </div>
    <div style="height:50px"></div>
  </div>`;
}
// Small inline line-icons for the home directory (stroke-based, inherit accent).
function svgIcon(kind){
  const s='width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"';
  const paths={
    profiles:`<path d="M3 3v18h18"/><path d="M6 15l4-6 4 3 5-8"/>`,
    compare:`<circle cx="12" cy="12" r="9"/><path d="M12 3v18"/><path d="M12 8l4 4-4 4"/><path d="M12 8l-4 4 4 4" opacity=".4"/>`,
    origin:`<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3a14 14 0 0 1 0 18 14 14 0 0 1 0-18"/>`,
    learn:`<path d="M3 5.5A2.5 2.5 0 0 1 5.5 3H12v16H5.5A2.5 2.5 0 0 0 3 21.5z"/><path d="M21 5.5A2.5 2.5 0 0 0 18.5 3H12v16h6.5a2.5 2.5 0 0 1 2.5 2.5z"/>`,
    start:`<circle cx="12" cy="12" r="9"/><path d="M12 16v-4"/><path d="M12 8h.01"/>`,
  };
  return `<svg ${s}>${paths[kind]||''}</svg>`;
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
function methCard(id,m,showGroup){
  const tag=showGroup?`<span class="k">${METH_GROUPS.find(g=>g[0]===m.group)?.[1]||''}</span>`:'';
  return `<div class="mcard" onclick="go('meth','${id}')">
    ${tag}
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
      <p class="prose" style="margin-top:12px;font-size:13px;color:var(--ink3)">Temperatures are typical bean-temp ranges and vary by roaster — charge temperature is the most roaster-specific number here, swinging widely with drum thermal mass and batch size. The phase relationships and DTR transfer across machines far better than absolute numbers do. Agtron ranges follow the prevailing US specialty convention.</p>
      <div class="curvechart">
        <div class="curvehead"><span class="curvetitle">Idealized Roast Curve</span>
          <div class="unittoggle"><button id="unitC" class="on" onclick="setCurveUnits('${id}','C')">°C</button><button id="unitF" onclick="setCurveUnits('${id}','F')">°F</button></div>
        </div>
        <div id="curvesvg">${roastCurve(p.curve,p.accent,620,300,'C')}</div>
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
    ${originPairing(p)}
    ${spectrumNav(id)}
    <div style="height:40px"></div>
  </div>`;
}
// Map roast-level strings to a numeric band 0(lightest)..4(darkest) for matching profiles<->origins.
function roastBand(level){
  const m={'Light':0,'Light–Medium':1,'Light-Medium':1,'Medium':2,'Medium–Dark':3,'Medium-Dark':3,'Dark':4};
  return m[level]!=null?m[level]:null;
}
// Which origins suit this profile's roast level? Match on band overlap (±0 for exact, allow the origin's
// recommended band to sit within one step of the profile). Purpose profiles (espresso/omni) show versatile origins.
function originPairing(p){
  const origins=Object.entries(METHODOLOGY).filter(([id,m])=>m.group==='origin'&&id!=='origin_intro'&&m.roastLevel);
  if(!origins.length)return '';
  let picks;
  let intro;
  if(p.group==='purpose'){
    // espresso/omni: origins that make classic espresso bases (medium→dark bands) + a note
    picks=origins.filter(([id,m])=>{const b=roastBand(m.roastLevel);return b!=null&&b>=2;});
    intro=p.name==='Espresso'
      ? "Classic espresso leans on origins that hold up sweet and full under pressure — chocolatey, nutty, lower-acid coffees. Lighter, floral origins can make a stunning single-origin espresso too, but these are the traditional blend backbone."
      : "An omni profile wants forgiving, balanced origins that taste good both as filter and espresso — nothing too extreme in either direction.";
  }else{
    const pb=roastBand(p.level);
    if(pb==null)return '';
    // origin fits if its recommended band is within one step of the profile band
    picks=origins.filter(([id,m])=>{const b=roastBand(m.roastLevel);return b!=null&&Math.abs(b-pb)<=1;});
    // prefer exact-band matches first
    picks.sort((a,b)=>Math.abs(roastBand(a[1].roastLevel)-pb)-Math.abs(roastBand(b[1].roastLevel)-pb));
    intro= pb<=1
      ? "Light roasting lives or dies on the green. These origins have the acidity, clarity, and aromatic complexity that a light roast is meant to reveal — roast a flat commodity coffee this light and there's nothing to show."
      : pb===2
      ? "A medium roast balances origin character against developed sweetness, so it suits a wide range of origins — from brighter high-grown coffees to sweeter, rounder ones."
      : "Dark roasting trades origin character for body, sweetness, and roast depth, so it pairs best with origins whose appeal is chocolate, nuttiness, and heavy body rather than delicate acidity — and with coffees priced to be roasted dark.";
  }
  if(!picks.length)return '';
  const chips=picks.map(([id,m])=>`<button class="opair" onclick="go('origin','${id}')">
    <span class="opair-name">${esc(m.name)}</span>
    <span class="opair-tags">${(m.flavorTags||[]).slice(0,2).map(t=>esc(t)).join(' · ')}</span>
  </button>`).join('');
  return `<div class="block"><h2>Origins That Shine Here</h2>
    <p class="pairintro">${intro}</p>
    <div class="opairgrid">${chips}</div>
    <div class="pairnote">Roast level is a starting point, not a rule — any coffee can be roasted any way. Tap an origin for how it behaves in the roaster.</div>
  </div>`;
}
function setCurveUnits(id,u){
  const p=PROFILES[id]; if(!p)return;
  document.getElementById('curvesvg').innerHTML=roastCurve(p.curve,p.accent,620,300,u);
  document.getElementById('unitC').classList.toggle('on',u==='C');
  document.getElementById('unitF').classList.toggle('on',u==='F');
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
let cmpMode='radar';
const CMP_COLORS=['#C9A34E','#B07B3E','#8A5A34','#6E3E1E','#e08a5a'];
function compare(){
  const ids=Object.keys(PROFILES);
  app.innerHTML=`<div class="wrap">
    <div class="seclead"><span class="no">02</span><div><h2>Compare Profiles</h2><p>Overlay flavor signatures or roast curves. Pick up to four.</p></div></div>
    <div class="cmpmodebar">
      <button id="modeRadar" class="${cmpMode==='radar'?'on':''}" onclick="setCmpMode('radar')">Flavor Radar</button>
      <button id="modeCurve" class="${cmpMode==='curve'?'on':''}" onclick="setCmpMode('curve')">Roast Curve</button>
    </div>
    <div class="cmpbar" id="cmpbar">${ids.map(id=>`<button data-id="${id}" onclick="toggleCmp('${id}')">${esc(PROFILES[id].name)}</button>`).join('')}</div>
    <div class="cmpwrap"><div class="lg" id="cmplg"></div><div class="cmplegend" id="cmpleg"></div></div>
    <div style="height:50px"></div>
  </div>`;
  drawCmp();
}
function setCmpMode(m){cmpMode=m;document.getElementById('modeRadar').classList.toggle('on',m==='radar');document.getElementById('modeCurve').classList.toggle('on',m==='curve');drawCmp();}
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
  if(cmpMode==='curve')return drawCmpCurve(lg,leg);
  // overlay: draw multi-shape radar manually. M = horizontal margin so side labels aren't clipped.
  const size=340,N=FLAVOR_AXES.length,M=48,vbW=size+M*2,cx=size/2+M,cy=size/2,pad=30,R=size/2-pad;
  let g='';
  for(let ring=1;ring<=5;ring++){let pts=[];for(let i=0;i<N;i++){const a=-Math.PI/2+i*(2*Math.PI/N);const r=R*(ring/5);pts.push((cx+r*Math.cos(a)).toFixed(1)+','+(cy+r*Math.sin(a)).toFixed(1));}g+=`<polygon points="${pts.join(' ')}" fill="none" stroke="#3a2a1c" stroke-width="1"/>`;}
  for(let i=0;i<N;i++){const a=-Math.PI/2+i*(2*Math.PI/N);const ex=cx+R*Math.cos(a),ey=cy+R*Math.sin(a);g+=`<line x1="${cx}" y1="${cy}" x2="${ex.toFixed(1)}" y2="${ey.toFixed(1)}" stroke="#3a2a1c"/>`;const lx=cx+(R+15)*Math.cos(a),ly=cy+(R+15)*Math.sin(a);let an='middle';if(Math.cos(a)>0.3)an='start';else if(Math.cos(a)<-0.3)an='end';g+=`<text x="${lx.toFixed(1)}" y="${(ly+4).toFixed(1)}" fill="#c9b8a4" font-size="11.5" text-anchor="${an}">${FLAVOR_AXES[i][1]}</text>`;}
  cmpSel.forEach((id,idx)=>{const col=CMP_COLORS[idx];const f=PROFILES[id].flavor;let pts=[];for(let i=0;i<N;i++){const a=-Math.PI/2+i*(2*Math.PI/N);const r=R*((f[FLAVOR_AXES[i][0]]||0)/5);pts.push((cx+r*Math.cos(a)).toFixed(1)+','+(cy+r*Math.sin(a)).toFixed(1));}g+=`<polygon points="${pts.join(' ')}" fill="${col}" fill-opacity="0.13" stroke="${col}" stroke-width="2" stroke-linejoin="round"/>`;});
  lg.innerHTML=`<svg viewBox="0 0 ${vbW} ${size}" width="${size}" height="${size}" style="max-width:100%">${g}</svg>`;
  leg.innerHTML=cmpSel.map((id,i)=>`<div class="it"><i style="background:${CMP_COLORS[i]}"></i><span>${esc(PROFILES[id].name)} <span style="color:var(--ink3)">· ${esc(PROFILES[id].level)}</span></span></div>`).join('')+`<div class="cmphint">Tap a profile above to add or remove it.</div>`;
}
function drawCmpCurve(lg,leg){
  // overlay BT curves on a shared time+temp axis
  const w=560,h=340,L=48,R=20,T=20,B=40,iw=w-L-R,ih=h-T-B;
  const curves=cmpSel.map(id=>({id,col:CMP_COLORS[cmpSel.indexOf(id)],cv:buildCurve(PROFILES[id].curve)}));
  const maxTime=Math.max(...curves.map(c=>c.cv.total));
  let allTemps=[];curves.forEach(c=>c.cv.bt.forEach(p=>allTemps.push(p[1])));
  const tmin=Math.min(...allTemps)-10,tmax=Math.max(...allTemps)+8;
  const X=t=>L+iw*(t/maxTime);
  const Y=v=>T+ih*(1-(v-tmin)/(tmax-tmin));
  const mm=s=>`${Math.floor(s/60)}:${String(Math.round(s%60)).padStart(2,'0')}`;
  let g='';
  // gridlines
  for(let s=0;s<=maxTime;s+=120){g+=`<line x1="${X(s).toFixed(1)}" y1="${T}" x2="${X(s).toFixed(1)}" y2="${T+ih}" stroke="#3a2a1c" stroke-width="1" opacity="0.5"/><text x="${X(s).toFixed(1)}" y="${h-16}" fill="#8f7c66" font-size="10" text-anchor="middle" font-family="ui-monospace">${mm(s)}</text>`;}
  g+=`<text x="${L-8}" y="${Y(tmax)+4}" fill="#8f7c66" font-size="10" text-anchor="end" font-family="ui-monospace">${Math.round(tmax)}°C</text>`;
  g+=`<text x="${L-8}" y="${Y(tmin)+4}" fill="#8f7c66" font-size="10" text-anchor="end" font-family="ui-monospace">${Math.round(tmin)}°C</text>`;
  // each BT curve + drop dot
  curves.forEach(c=>{
    let path=c.cv.bt.map((p,i)=>(i?'L':'M')+X(p[0]).toFixed(1)+' '+Y(p[1]).toFixed(1)).join(' ');
    g+=`<path d="${path}" fill="none" stroke="${c.col}" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"/>`;
    // first crack + drop markers
    const fc=c.cv.marks;
    g+=`<circle cx="${X(fc.fcTime).toFixed(1)}" cy="${Y(fc.fcTemp).toFixed(1)}" r="3" fill="${c.col}" stroke="#160e08" stroke-width="1.2"/>`;
    g+=`<circle cx="${X(c.cv.total).toFixed(1)}" cy="${Y(fc.drop).toFixed(1)}" r="3.4" fill="${c.col}" stroke="#160e08" stroke-width="1.2"/>`;
  });
  lg.innerHTML=`<svg viewBox="0 0 ${w} ${h}" width="100%" style="max-width:${w}px">${g}</svg>`;
  leg.innerHTML=cmpSel.map((id,i)=>{const cv=buildCurve(PROFILES[id].curve);return `<div class="it"><i style="background:${CMP_COLORS[i]}"></i><span>${esc(PROFILES[id].name)} <span style="color:var(--ink3)">· ${mm(cv.total)} · DTR ${esc(PROFILES[id].curve.dtr)}</span></span></div>`;}).join('')+`<div class="cmphint">Dots mark first crack and drop. Shorter, earlier-dropping curves are lighter roasts.</div>`;
}

/* ---------- ORIGINS TAB ---------- */
// Equirectangular projection helper: lng/lat -> x/y in a mapW x mapH box.
function projXY(lng,lat,mapW,mapH){
  const x=(lng+180)/360*mapW;
  const y=(90-lat)/180*mapH;
  return [x,y];
}
function originList(){
  const origins=Object.entries(METHODOLOGY).filter(([id,m])=>m.group==='origin'&&id!=='origin_intro');
  const intro=METHODOLOGY['origin_intro'];
  // group by continent for the card sections
  const byCont={};
  origins.forEach(([id,m])=>{(byCont[m.continent]=byCont[m.continent]||[]).push([id,m]);});
  const contOrder=['Africa','Central America','South America','Asia'];
  app.innerHTML=`<div class="wrap">
    <div class="seclead"><span class="no">◍</span><div><h2>Roasting by Origin</h2><p>Where the coffee comes from shapes the cup before you ever light the burner. ${origins.length} origins, how each behaves, and the roast that shows it best.</p></div></div>
    ${originMap(origins)}
    <div class="originnote">${esc(intro.sections[0].body)}</div>
    ${contOrder.filter(c=>byCont[c]).map(cont=>`
      <div class="grouplabel">${cont}</div>
      <div class="origrid">${byCont[cont].map(([id,m])=>originCard(id,m)).join('')}</div>
    `).join('')}
    <div style="height:20px"></div>
    <button class="back" style="margin:0" onclick="go('meth','origin_intro')">Read: the practical rule for roasting any origin →</button>
    <div style="height:50px"></div>
  </div>`;
}
function originMap(origins){
  const mapW=1000, mapH=500;
  // Simplified continent silhouettes (very rough, evocative not accurate) as filled blobs.
  // We draw a subtle world backdrop + the Bean Belt band + a dot per origin.
  const beltTop=projXY(0,23.5,mapW,mapH)[1];
  const beltBot=projXY(0,-23.5,mapW,mapH)[1];
  let dots='';
  origins.forEach(([id,m])=>{
    if(m.lng==null)return;
    const [x,y]=projXY(m.lng,m.lat,mapW,mapH);
    dots+=`<g class="mapdot" onclick="go('origin','${id}')" style="cursor:pointer">
      <circle cx="${x.toFixed(0)}" cy="${y.toFixed(0)}" r="18" fill="var(--heat3)" opacity="0.18"/>
      <circle cx="${x.toFixed(0)}" cy="${y.toFixed(0)}" r="7" fill="var(--heat1)" stroke="#160e08" stroke-width="2"/>
      <text x="${x.toFixed(0)}" y="${(y-16).toFixed(0)}" fill="#f0e6d8" font-size="19" font-weight="600" text-anchor="middle" font-family="ui-sans-serif">${esc(m.country.replace(/ \(.*\)/,''))}</text>
    </g>`;
  });
  return `<div class="originmapwrap">
    <svg viewBox="0 0 ${mapW} ${mapH}" width="100%" style="display:block">
      <rect x="0" y="0" width="${mapW}" height="${mapH}" fill="#12100c"/>
      <!-- bean belt band -->
      <rect x="0" y="${beltTop.toFixed(0)}" width="${mapW}" height="${(beltBot-beltTop).toFixed(0)}" fill="var(--heat5)" opacity="0.08"/>
      <line x1="0" y1="${beltTop.toFixed(0)}" x2="${mapW}" y2="${beltTop.toFixed(0)}" stroke="var(--heat4)" stroke-width="1" stroke-dasharray="6 5" opacity="0.5"/>
      <line x1="0" y1="${beltBot.toFixed(0)}" x2="${mapW}" y2="${beltBot.toFixed(0)}" stroke="var(--heat4)" stroke-width="1" stroke-dasharray="6 5" opacity="0.5"/>
      <text x="14" y="${(beltTop-8).toFixed(0)}" fill="var(--heat3)" font-size="15" font-family="ui-monospace" opacity="0.8">Tropic of Cancer</text>
      <text x="14" y="${(beltBot+22).toFixed(0)}" fill="var(--heat3)" font-size="15" font-family="ui-monospace" opacity="0.8">Tropic of Capricorn</text>
      <text x="${(mapW-14).toFixed(0)}" y="${((beltTop+beltBot)/2+5).toFixed(0)}" fill="var(--heat2)" font-size="16" font-family="ui-monospace" text-anchor="end" opacity="0.7" letter-spacing="2">THE BEAN BELT</text>
      ${dots}
    </svg>
    <div class="mapcap">Coffee grows in a band around the equator — the Bean Belt. Tap a dot for the origin.</div>
  </div>`;
}
function originCard(id,m){
  const tags=(m.flavorTags||[]).slice(0,3).map(t=>`<span>${esc(t)}</span>`).join('');
  return `<div class="origcard" onclick="go('origin','${id}')">
    <div class="origcard-top">
      <div class="origcard-name">${esc(m.name)}</div>
      <div class="origcard-roast" style="--rc:${roastColor(m.roastLevel)}">${esc(m.roastLevel)}</div>
    </div>
    <div class="origcard-blurb">${esc(m.blurb)}</div>
    <div class="origcard-tags">${tags}</div>
    <div class="origcard-meta">${esc(m.altitude)} · ${esc((m.process||'').split(' ')[0])}</div>
  </div>`;
}
function roastColor(level){
  const map={'Light':'#C9A34E','Light–Medium':'#BC8A43','Medium':'#B07B3E','Medium–Dark':'#8A5A34','Dark':'#6E3E1E'};
  return map[level]||'#B07B3E';
}
function originDetail(id){
  const m=METHODOLOGY[id]; if(!m)return go('origins');
  if(id==='origin_intro'){ // intro page uses the plain meth layout but back to origins
    return methLike(m,'origins','← All origins');
  }
  const facts=[
    ['Regions',m.regions],['Altitude',m.altitude],['Varieties',m.varieties],
    ['Process',m.process],['Harvest',m.harvest]
  ].filter(f=>f[1]);
  const siblings=Object.entries(METHODOLOGY).filter(([sid,sm])=>sm.group==='origin'&&sid!==id&&sid!=='origin_intro');
  app.innerHTML=`<div class="wrap detail">
    <button class="back" onclick="go('origins')">← All origins</button>
    <div class="odhead">
      <div class="odtxt">
        <div class="lvl" style="color:${m.accent}">${esc(m.continent)}</div>
        <h1>${esc(m.name)}</h1>
        <div class="sub">${esc(m.sub)}</div>
        <div class="oneline" style="margin-top:12px">${esc(m.blurb)}</div>
        <div class="origtags">${(m.flavorTags||[]).map(t=>`<span>${esc(t)}</span>`).join('')}</div>
      </div>
      <div class="odroast">
        <div class="odroast-ring" style="--rc:${roastColor(m.roastLevel)}">
          <span>${esc(m.roastLevel)}</span>
          <small>target roast</small>
        </div>
      </div>
    </div>
    <div class="factstrip">${facts.map(f=>`<div class="fact"><div class="fl">${esc(f[0])}</div><div class="fv">${esc(f[1])}</div></div>`).join('')}</div>
    ${m.sections.map(s=>`<div class="msection"><h3>${esc(s.h)}</h3><p>${esc(s.body)}</p></div>`).join('')}
    ${m.keypoints?`<div class="keypoints"><h4>Key Points</h4><ul style="margin:0;padding:0">${m.keypoints.map(k=>`<li>${esc(k)}</li>`).join('')}</ul></div>`:''}
    ${refsBlock(m.refs)}
    ${siblings.length?`<div class="siblings"><h4>More origins</h4><div class="origrid">${siblings.map(([sid,sm])=>originCard(sid,sm)).join('')}</div></div>`:''}
    <div style="height:40px"></div>
  </div>`;
}
// Generic meth-style render used by the origin intro page.
function methLike(m,backView,backLabel){
  app.innerHTML=`<div class="wrap detail">
    <button class="back" onclick="go('${backView}')">${esc(backLabel)}</button>
    <div class="dhead" style="border-bottom:none;padding-bottom:6px"><div class="txt">
      <div class="lvl" style="color:${m.accent}">Roasting by Origin</div>
      <h1>${esc(m.name)}</h1><div class="sub">${esc(m.sub)}</div>
    </div></div>
    ${m.sections.map(s=>`<div class="msection"><h3>${esc(s.h)}</h3><p>${esc(s.body)}</p></div>`).join('')}
    ${m.keypoints?`<div class="keypoints"><h4>Key Points</h4><ul style="margin:0;padding:0">${m.keypoints.map(k=>`<li>${esc(k)}</li>`).join('')}</ul></div>`:''}
    ${refsBlock(m.refs)}
    <div style="height:40px"></div>
  </div>`;
}

/* ---------- LEARN LIST ---------- */
/* ---------- LEARN HUB ---------- */
let learnQuery='', learnOpen=null;
function learnList(){
  app.innerHTML=`<div class="wrap">
    <div class="seclead"><span class="no">03</span><div><h2>Learn</h2><p>The full craft, green to cup — ${Object.keys(METHODOLOGY).length} deep-dives across ${METH_GROUPS.length} areas.</p></div></div>
    <div class="filterbar">
      <div class="searchwrap">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg>
        <input id="lsearch" type="search" placeholder="Search all topics — defect, DTR, espresso, water…" value="${esc(learnQuery)}" autocomplete="off">
      </div>
    </div>
    <div id="lresults"></div>
    <div style="height:50px"></div></div>`;
  const si=document.getElementById('lsearch');
  si.oninput=e=>{learnQuery=e.target.value;drawLearn();};
  drawLearn();
  const s2=document.getElementById('lsearch'); if(learnQuery){s2.focus();s2.setSelectionRange(learnQuery.length,learnQuery.length);}
}
function matchMeth(m,q){
  q=q.toLowerCase().trim(); if(!q)return true;
  const secText=(m.sections||[]).map(s=>s.h+' '+s.body).join(' ');
  const kp=(m.keypoints||[]).join(' ');
  const glabel=METH_GROUPS.find(g=>g[0]===m.group)?.[1]||'';
  return (m.name+' '+m.sub+' '+glabel+' '+secText+' '+kp).toLowerCase().includes(q);
}
function drawLearn(){
  const box=document.getElementById('lresults'); if(!box)return;
  const q=learnQuery.trim();
  if(q){
    // flat, cross-group search results
    const hits=Object.entries(METHODOLOGY).filter(([id,m])=>m.group!=='origin'&&matchMeth(m,q));
    if(!hits.length){box.innerHTML=`<div class="empty">No topic matches that. Try "crack", "grind", "moisture", or "defect".</div>`;return;}
    box.innerHTML=`<div class="lcount">${hits.length} topic${hits.length>1?'s':''}</div>
      <div class="grid mgrid">${hits.map(([id,m])=>methCard(id,m,true)).join('')}</div>`;
    return;
  }
  // hub view: group tiles, click to expand into cards
  box.innerHTML=`<div class="hublist">${METH_GROUPS.map(([gid,glabel])=>{
    const items=Object.entries(METHODOLOGY).filter(([id,m])=>m.group===gid);
    if(!items.length)return '';
    const meta=METH_GROUP_META[gid]||{desc:'',accent:'#B07B3E'};
    const open=learnOpen===gid;
    return `<div class="hubgroup ${open?'open':''}">
      <button class="hubhead" onclick="toggleHub('${gid}')" style="--ga:${meta.accent}">
        <span class="hubbar"></span>
        <span class="hubtxt">
          <span class="hubname">${esc(glabel)}</span>
          <span class="hubdesc">${esc(meta.desc)}</span>
        </span>
        <span class="hubcount">${items.length}</span>
        <span class="hubchev">${open?'−':'+'}</span>
      </button>
      ${open?`<div class="grid mgrid hubcards">${items.map(([id,m])=>methCard(id,m,false)).join('')}</div>`:''}
    </div>`;
  }).join('')}</div>`;
}
function toggleHub(gid){learnOpen=learnOpen===gid?null:gid;drawLearn();}

/* ---------- METH DETAIL ---------- */
/* ---------- DEFECT BEAN ILLUSTRATIONS (inline SVG, zero-byte, offline) ---------- */
/* ---------- CONCEPT DIAGRAMS (inline SVG, zero-byte, offline, teaching-first) ---------- */
// Shared palette pulled from the app's heat vars so diagrams match the aesthetic.
const DIA={bg:'#1b140e',line:'#3a2e24',ink:'#c9b8a4',ink3:'#8f7c66',
  dry:'#C9A34E',mail:'#B07B3E',dev:'#8A5A34',accent:'#e0864a',ror:'#7a9a6a',hot:'#d0553a'};
function diaWrap(vb,inner,cap){
  return `<figure class="diagram"><svg viewBox="0 0 ${vb}" width="100%" role="img" preserveAspectRatio="xMidYMid meet">${inner}</svg>${cap?`<figcaption>${cap}</figcaption>`:''}</figure>`;
}
// 1. Annotated roast curve: BT rising S-curve + declining RoR, phase bands, TP/1C/2C/Drop, crash/flick callouts.
function diaRoastCurve(opts){
  opts=opts||{};
  const W=760,H=380,L=52,R=20,T=26,B=44,iw=W-L-R,ih=H-T-B;
  const X=t=>L+iw*t, Y=v=>T+ih*(1-v);
  // phase x-boundaries (fractions of time): drying .0-.45, maillard .45-.78, development .78-1
  const dryEnd=.45,fcAt=.78;
  const bands=[[0,dryEnd,DIA.dry,'Drying'],[dryEnd,fcAt,DIA.mail,'Maillard'],[fcAt,1,DIA.dev,'Development']];
  let g='';
  bands.forEach(bd=>{g+=`<rect x="${X(bd[0]).toFixed(0)}" y="${T}" width="${(X(bd[1])-X(bd[0])).toFixed(0)}" height="${ih}" fill="${bd[2]}" opacity="0.13"/>`;
    g+=`<text x="${((X(bd[0])+X(bd[1]))/2).toFixed(0)}" y="${T+16}" fill="${bd[2]}" font-size="13" font-weight="600" text-anchor="middle" font-family="ui-sans-serif">${bd[3]}</text>`;});
  // axes
  g+=`<line x1="${L}" y1="${T}" x2="${L}" y2="${T+ih}" stroke="${DIA.line}"/><line x1="${L}" y1="${T+ih}" x2="${W-R}" y2="${T+ih}" stroke="${DIA.line}"/>`;
  g+=`<text x="14" y="${T+12}" fill="${DIA.ink3}" font-size="11" font-family="ui-monospace">temp</text>`;
  g+=`<text x="${W-R}" y="${H-14}" fill="${DIA.ink3}" font-size="11" text-anchor="end" font-family="ui-monospace">time →</text>`;
  // BT curve: quick dip to turning point then rising, decelerating S to drop
  // sample points (t, v) — v is normalized temp
  const bt=[[0,.62],[.06,.20],[.12,.24],[.25,.42],[.45,.60],[.62,.72],[.78,.82],[.9,.88],[1,.93]];
  let btp=bt.map((p,i)=>(i?'L':'M')+X(p[0]).toFixed(1)+' '+Y(p[1]).toFixed(1)).join(' ');
  g+=`<path d="${btp}" fill="none" stroke="${DIA.accent}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>`;
  // RoR curve: rises after TP, peaks, declines gently
  const ror=[[.06,.05],[.12,.55],[.2,.66],[.35,.6],[.55,.5],[.78,.4],[1,.3]];
  let rp=ror.map((p,i)=>(i?'L':'M')+X(p[0]).toFixed(1)+' '+Y(p[1]).toFixed(1)).join(' ');
  g+=`<path d="${rp}" fill="none" stroke="${DIA.ror}" stroke-width="2.2" stroke-dasharray="5 4"/>`;
  // markers
  const dot=(t,v,lab,dy)=>`<circle cx="${X(t).toFixed(1)}" cy="${Y(v).toFixed(1)}" r="4" fill="${DIA.accent}" stroke="${DIA.bg}" stroke-width="1.5"/><text x="${X(t).toFixed(1)}" y="${(Y(v)+(dy||-10)).toFixed(1)}" fill="#f0e6d8" font-size="11.5" font-weight="600" text-anchor="middle" font-family="ui-sans-serif">${lab}</text>`;
  g+=dot(.09,.22,'Turning point',18);
  g+=dot(.45,.60,'Dry end',-10);
  g+=dot(.78,.82,'First crack',-10);
  g+=dot(1,.93,'Drop',-10);
  // legend
  g+=`<line x1="${L+8}" y1="${T+ih+30}" x2="${L+34}" y2="${T+ih+30}" stroke="${DIA.accent}" stroke-width="3"/><text x="${L+40}" y="${T+ih+34}" fill="${DIA.ink}" font-size="12" font-family="ui-sans-serif">Bean temp</text>`;
  g+=`<line x1="${L+150}" y1="${T+ih+30}" x2="${L+176}" y2="${T+ih+30}" stroke="${DIA.ror}" stroke-width="2.2" stroke-dasharray="5 4"/><text x="${L+182}" y="${T+ih+34}" fill="${DIA.ink}" font-size="12" font-family="ui-sans-serif">Rate of rise (RoR)</text>`;
  return diaWrap(`${W} ${H}`,g,opts.cap||'A healthy roast: bean temp climbs in a decelerating S-curve while the rate of rise peaks after the turning point and then glides steadily downward to the drop.');
}
// 2. Phase timeline bar with temps + what happens.
function diaPhaseBar(){
  const W=760,H=150,L=10,R=10,T=28,barH=46,iw=W-L-R;
  const segs=[[.0,.45,DIA.dry,'Drying','green → yellow','~160°C'],[.45,.78,DIA.mail,'Maillard','yellow → brown','~160–196°C'],[.78,1,DIA.dev,'Development','1st crack → drop','196–205°C+']];
  let g='';
  segs.forEach(s=>{const x=L+iw*s[0],w=iw*(s[1]-s[0]);
    g+=`<rect x="${x.toFixed(0)}" y="${T}" width="${w.toFixed(0)}" height="${barH}" fill="${s[2]}" opacity="0.85" rx="3"/>`;
    g+=`<text x="${(x+w/2).toFixed(0)}" y="${(T+barH/2-2).toFixed(0)}" fill="#1b140e" font-size="14" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${s[3]}</text>`;
    g+=`<text x="${(x+w/2).toFixed(0)}" y="${(T+barH/2+14).toFixed(0)}" fill="#1b140e" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif" opacity="0.75">${s[4]}</text>`;
    g+=`<text x="${(x+w/2).toFixed(0)}" y="${T-8}" fill="${s[2]}" font-size="11.5" text-anchor="middle" font-family="ui-monospace">${s[5]}</text>`;});
  // proportion note
  g+=`<text x="${L}" y="${T+barH+24}" fill="${DIA.ink3}" font-size="12" font-family="ui-sans-serif">Roughly the proportions of a balanced roast — most flavor is built in the Maillard phase; development sets the final roast level.</text>`;
  return diaWrap(`${W} ${H}`,g,'The three phases of a roast, start to drop.');
}
// 3. DTR: total time bar with the development portion highlighted + percentage band.
function diaDTR(){
  const W=760,H=170,L=10,R=10,T=24,barH=40,iw=W-L-R;
  const rows=[['Light / Nordic',.12],['Balanced City+',.20],['Dark',.25]];
  let g='';
  rows.forEach((r,i)=>{const y=T+i*46;
    g+=`<rect x="${L}" y="${y}" width="${iw}" height="${barH}" fill="${DIA.mail}" opacity="0.2" rx="3"/>`;
    const dx=L+iw*(1-r[1]);
    g+=`<rect x="${dx.toFixed(0)}" y="${y}" width="${(iw*r[1]).toFixed(0)}" height="${barH}" fill="${DIA.dev}" opacity="0.9" rx="3"/>`;
    g+=`<text x="${L+8}" y="${(y+barH/2+4).toFixed(0)}" fill="${DIA.ink}" font-size="12.5" font-weight="600" font-family="ui-sans-serif">${r[0]}</text>`;
    g+=`<text x="${(dx+iw*r[1]/2).toFixed(0)}" y="${(y+barH/2+4).toFixed(0)}" fill="#1b140e" font-size="12" font-weight="700" text-anchor="middle" font-family="ui-mono">${Math.round(r[1]*100)}%</text>`;
  });
  g+=`<text x="${L}" y="${T+3*46+6}" fill="${DIA.ink3}" font-size="11.5" font-family="ui-sans-serif">Dark portion = development time (first crack → drop) as a share of total roast time. Higher isn't better — it's a lever.</text>`;
  return diaWrap(`${W} ${H}`,g,'Development Time Ratio across roast styles.');
}
// 4. Crack timeline on a temperature axis.
function diaCracks(){
  const W=760,H=180,L=20,R=20,T=40,iw=W-L-R,axisY=T+40;
  const X=temp=>L+iw*((temp-150)/(240-150));
  let g='';
  g+=`<line x1="${L}" y1="${axisY}" x2="${W-R}" y2="${axisY}" stroke="${DIA.line}" stroke-width="2"/>`;
  [150,175,196,224,240].forEach(t=>{g+=`<line x1="${X(t).toFixed(0)}" y1="${axisY-4}" x2="${X(t).toFixed(0)}" y2="${axisY+4}" stroke="${DIA.ink3}"/><text x="${X(t).toFixed(0)}" y="${axisY+20}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-monospace">${t}°C</text>`;});
  // first crack marker
  const fc=(temp,lab,sub,col)=>{const x=X(temp);return `<circle cx="${x.toFixed(0)}" cy="${axisY}" r="7" fill="${col}" stroke="${DIA.bg}" stroke-width="2"/><text x="${x.toFixed(0)}" y="${axisY-16}" fill="#f0e6d8" font-size="13" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${lab}</text><text x="${x.toFixed(0)}" y="${axisY-48}" fill="${col}" font-size="11.5" text-anchor="middle" font-family="ui-sans-serif">${sub}</text>`;};
  g+=fc(196,'1st crack','popcorn · loud · slow',DIA.dry);
  g+=fc(224,'2nd crack','crackle · quiet · fast',DIA.hot);
  // light/med/dark drop zones
  g+=`<text x="${X(200).toFixed(0)}" y="${axisY+42}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif">↑ light–medium drop here</text>`;
  g+=`<text x="${X(228).toFixed(0)}" y="${axisY+42}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif">↑ dark drop here</text>`;
  return diaWrap(`${W} ${H}`,g,'The two cracks are the roaster\u2019s audible landmarks — where you drop between or past them sets the roast level.');
}
// 5. Heat transfer in a drum (three modes).
function diaHeat(){
  const W=760,H=230,cx=250,cy=115,rd=78;
  let g='';
  // drum
  g+=`<circle cx="${cx}" cy="${cy}" r="${rd}" fill="none" stroke="${DIA.mail}" stroke-width="4"/>`;
  g+=`<circle cx="${cx}" cy="${cy}" r="${rd+10}" fill="none" stroke="${DIA.line}" stroke-width="2" stroke-dasharray="3 4"/>`;
  // beans
  for(let i=0;i<7;i++){const a=i/7*Math.PI*2;g+=`<ellipse cx="${(cx+Math.cos(a)*38).toFixed(0)}" cy="${(cy+Math.sin(a)*30+10).toFixed(0)}" rx="9" ry="6" fill="${DIA.dev}"/>`;}
  // conduction (drum wall arrow)
  g+=`<path d="M${cx-rd+4} ${cy+40} Q${cx-40} ${cy+30} ${cx-20} ${cy+18}" stroke="${DIA.hot}" stroke-width="2.5" fill="none" marker-end="url(#ah)"/>`;
  // convection (hot air swirl)
  g+=`<path d="M${cx-10} ${cy-50} Q${cx+30} ${cy-40} ${cx+20} ${cy-10}" stroke="${DIA.dry}" stroke-width="2.5" fill="none" marker-end="url(#ah)"/>`;
  // radiation (from wall)
  g+=`<path d="M${cx+rd-6} ${cy} L${cx+30} ${cy}" stroke="${DIA.accent}" stroke-width="2.5" fill="none" marker-end="url(#ah)"/>`;
  // arrowhead marker
  g=`<defs><marker id="ah" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 z" fill="${DIA.ink}"/></marker></defs>`+g;
  // labels on right
  const leg=[[DIA.hot,'Conduction','Heat from the hot metal drum wall touching the beans.'],[DIA.dry,'Convection','Hot air moving through the bean mass — the biggest lever on most drums.'],[DIA.accent,'Radiation','Infrared heat radiating from the drum and surfaces.']];
  leg.forEach((l,i)=>{const y=44+i*56;g+=`<rect x="440" y="${y-12}" width="14" height="14" rx="3" fill="${l[0]}"/><text x="462" y="${y}" fill="${DIA.ink}" font-size="14" font-weight="700" font-family="ui-sans-serif">${l[1]}</text><text x="462" y="${y+18}" fill="${DIA.ink3}" font-size="11.5" font-family="ui-sans-serif"><tspan x="462">${l[2].slice(0,42)}</tspan></text>`;});
  return diaWrap(`${W} ${H}`,g,'Three ways heat reaches the bean inside a drum roaster.');
}
// 6. Extraction band: under / ideal / over.
function diaExtraction(){
  const W=760,H=150,L=20,R=20,T=40,barH=42,iw=W-L-R;
  const X=p=>L+iw*(p/30);
  let g='';
  // gradient bands
  g+=`<rect x="${X(0).toFixed(0)}" y="${T}" width="${(X(18)-X(0)).toFixed(0)}" height="${barH}" fill="${DIA.dry}" opacity="0.5"/>`;
  g+=`<rect x="${X(18).toFixed(0)}" y="${T}" width="${(X(22)-X(18)).toFixed(0)}" height="${barH}" fill="${DIA.ror}" opacity="0.85"/>`;
  g+=`<rect x="${X(22).toFixed(0)}" y="${T}" width="${(X(30)-X(22)).toFixed(0)}" height="${barH}" fill="${DIA.hot}" opacity="0.5"/>`;
  // labels
  g+=`<text x="${X(9).toFixed(0)}" y="${(T+barH/2+5).toFixed(0)}" fill="#1b140e" font-size="13" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">UNDER</text>`;
  g+=`<text x="${X(20).toFixed(0)}" y="${(T+barH/2+5).toFixed(0)}" fill="#1b140e" font-size="13" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">IDEAL</text>`;
  g+=`<text x="${X(26).toFixed(0)}" y="${(T+barH/2+5).toFixed(0)}" fill="#1b140e" font-size="13" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">OVER</text>`;
  // ticks
  [0,18,22,30].forEach(p=>{g+=`<text x="${X(p).toFixed(0)}" y="${T+barH+18}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-monospace">${p}%</text>`;});
  g+=`<text x="${X(9).toFixed(0)}" y="${T-10}" fill="${DIA.dry}" font-size="11.5" text-anchor="middle" font-family="ui-sans-serif">sour · weak · grassy</text>`;
  g+=`<text x="${X(20).toFixed(0)}" y="${T-10}" fill="${DIA.ror}" font-size="11.5" text-anchor="middle" font-family="ui-sans-serif">sweet · balanced</text>`;
  g+=`<text x="${X(26).toFixed(0)}" y="${T-10}" fill="${DIA.hot}" font-size="11.5" text-anchor="middle" font-family="ui-sans-serif">bitter · dry · harsh</text>`;
  return diaWrap(`${W} ${H}`,g,'Extraction yield — the % of coffee dissolved into the cup. The Golden Cup window is 18–22%.');
}
// 7. Espresso ratio: dose in → yield out.
function diaEspresso(){
  const W=760,H=150,cx1=190,cx2=560,cy=80;
  let g='';
  // portafilter (dose)
  g+=`<rect x="${cx1-50}" y="${cy-30}" width="100" height="42" rx="5" fill="${DIA.dev}"/><text x="${cx1}" y="${cy-4}" fill="#1b140e" font-size="20" font-weight="800" text-anchor="middle" font-family="ui-sans-serif">18 g</text><text x="${cx1}" y="${cy+34}" fill="${DIA.ink}" font-size="13" text-anchor="middle" font-family="ui-sans-serif">dose (dry coffee)</text>`;
  // arrow
  g+=`<line x1="${cx1+70}" y1="${cy-8}" x2="${cx2-90}" y2="${cy-8}" stroke="${DIA.accent}" stroke-width="3" marker-end="url(#ae)"/><text x="${(cx1+cx2)/2}" y="${cy-20}" fill="${DIA.accent}" font-size="13" font-weight="600" text-anchor="middle" font-family="ui-sans-serif">25–30 s · 9 bar</text>`;
  g=`<defs><marker id="ae" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0 0 L7 3 L0 6 z" fill="${DIA.accent}"/></marker></defs>`+g;
  // cup (yield)
  g+=`<path d="M${cx2-42} ${cy-32} L${cx2+42} ${cy-32} L${cx2+34} ${cy+18} L${cx2-34} ${cy+18} Z" fill="${DIA.mail}"/><text x="${cx2}" y="${cy-2}" fill="#1b140e" font-size="20" font-weight="800" text-anchor="middle" font-family="ui-sans-serif">36 g</text><text x="${cx2}" y="${cy+40}" fill="${DIA.ink}" font-size="13" text-anchor="middle" font-family="ui-sans-serif">yield (liquid espresso)</text>`;
  g+=`<text x="${W/2}" y="${cy+70}" fill="${DIA.ink3}" font-size="12.5" text-anchor="middle" font-family="ui-sans-serif">A 1:2 ratio — the modern espresso default. Weigh both, adjust grind to hit the time.</text>`;
  return diaWrap(`${W} ${H}`,g,'The standard espresso recipe as a ratio.');
}
// 8. Grind size across brew methods.
function diaGrind(){
  const W=760,H=170,L=20,T=30,gap=(W-40)/4;
  const methods=[['Espresso','fine',3],['Pour-over','medium',6],['Drip','medium',7],['French press','coarse',11]];
  let g='';
  methods.forEach((m,i)=>{const cx=L+gap*i+gap/2, cy=T+40;
    // draw a cluster of dots sized by grind
    const n=m[2]<5?26:m[2]<8?14:7, r=m[3];
    for(let k=0;k<n;k++){const ang=k/n*6.28,rad=18+((k*7)%20);g+=`<circle cx="${(cx+Math.cos(ang)*rad*0.6).toFixed(0)}" cy="${(cy+Math.sin(ang)*rad*0.5).toFixed(0)}" r="${r}" fill="${DIA.dev}" opacity="0.85"/>`;}
    g+=`<text x="${cx.toFixed(0)}" y="${T+120}" fill="${DIA.ink}" font-size="13.5" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${m[0]}</text>`;
    g+=`<text x="${cx.toFixed(0)}" y="${T+138}" fill="${DIA.ink3}" font-size="11.5" text-anchor="middle" font-family="ui-sans-serif">${m[1]}</text>`;
  });
  return diaWrap(`${W} ${H}`,g,'Grind size matched to method: short, intense brews need fine grounds; long, gentle ones need coarse.');
}
// 9. Flavor wheel: 9 inner categories as a radial diagram.
function diaFlavorWheel(){
  const W=420,H=420,cx=210,cy=210,rIn=54,rOut=150;
  const cats=[['Fruity','#c0433a'],['Sour /\nFermented','#c98a2e'],['Green /\nVeg.','#5a8a3a'],['Other','#6a8a8a'],['Roasted','#7a4a28'],['Spices','#a0522d'],['Nutty /\nCocoa','#8a5a34'],['Sweet','#c99a2e'],['Floral','#c86a9a']];
  const N=cats.length;let g='';
  cats.forEach((c,i)=>{const a0=i/N*6.283-1.5708,a1=(i+1)/N*6.283-1.5708,am=(a0+a1)/2;
    const p=(r,a)=>[(cx+r*Math.cos(a)).toFixed(1),(cy+r*Math.sin(a)).toFixed(1)];
    const [x0,y0]=p(rIn,a0),[x1,y1]=p(rOut,a0),[x2,y2]=p(rOut,a1),[x3,y3]=p(rIn,a1);
    g+=`<path d="M${x0} ${y0} L${x1} ${y1} A${rOut} ${rOut} 0 0 1 ${x2} ${y2} L${x3} ${y3} A${rIn} ${rIn} 0 0 0 ${x0} ${y0} Z" fill="${c[1]}" opacity="0.82" stroke="${DIA.bg}" stroke-width="2"/>`;
    const [lx,ly]=p((rIn+rOut)/2,am);
    const lines=c[0].split('\n');
    g+=lines.map((ln,li)=>`<text x="${lx}" y="${(+ly+li*12-(lines.length-1)*6).toFixed(1)}" fill="#fff" font-size="11.5" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${ln}</text>`).join('');
  });
  g+=`<circle cx="${cx}" cy="${cy}" r="${rIn}" fill="${DIA.bg}" stroke="${DIA.line}"/><text x="${cx}" y="${cy-4}" fill="${DIA.ink}" font-size="13" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">Coffee</text><text x="${cx}" y="${cy+12}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif">start here</text>`;
  return diaWrap(`${W} ${H}`,g,'The nine inner categories of the SCA Flavor Wheel — you work outward from the center to more specific notes.');
}
// 10. CVA score build: 8 sections → formula → number.
function diaCVA(){
  const W=760,H=200,L=20,T=20;
  const secs=['Fragrance','Aroma','Flavor','Aftertaste','Acidity','Sweetness','Mouthfeel','Overall'];
  let g='';
  const bw=(W-40)/8;
  secs.forEach((s,i)=>{const x=L+bw*i;g+=`<rect x="${(x+3).toFixed(0)}" y="${T}" width="${(bw-6).toFixed(0)}" height="34" rx="4" fill="${DIA.mail}" opacity="0.8"/><text x="${(x+bw/2).toFixed(0)}" y="${T+22}" fill="#1b140e" font-size="10" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${s.slice(0,7)}</text>`;});
  g+=`<text x="${W/2}" y="${T+56}" fill="${DIA.ink3}" font-size="12" text-anchor="middle" font-family="ui-sans-serif">each rated 1–9 (how much you like it), then summed</text>`;
  // formula box
  g+=`<rect x="${(W/2-230).toFixed(0)}" y="${T+70}" width="460" height="52" rx="8" fill="${DIA.bg}" stroke="${DIA.accent}" stroke-width="1.5"/>`;
  g+=`<text x="${W/2}" y="${T+102}" fill="${DIA.ink}" font-size="16" text-anchor="middle" font-family="ui-monospace">Score = 0.65625 × Σ + 52.75</text>`;
  // arrow to result
  g+=`<text x="${W/2}" y="${T+150}" fill="${DIA.ink3}" font-size="12" text-anchor="middle" font-family="ui-sans-serif">e.g. sections sum to 48  →  <tspan fill="${DIA.accent}" font-weight="700" font-size="15">84.25</tspan>  (specialty)</text>`;
  g+=`<text x="${W/2}" y="${T+172}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif">minus 2 per non-uniform cup, 4 per defective cup</text>`;
  return diaWrap(`${W} ${H}`,g,'How the CVA affective score is built from eight liking ratings.');
}
function diagram(kind){
  switch(kind){
    case 'roastcurve':return diaRoastCurve();
    case 'phasebar':return diaPhaseBar();
    case 'dtr':return diaDTR();
    case 'cracks':return diaCracks();
    case 'heat':return diaHeat();
    case 'extraction':return diaExtraction();
    case 'espresso':return diaEspresso();
    case 'grind':return diaGrind();
    case 'flavorwheel':return diaFlavorWheel();
    case 'cva':return diaCVA();
    default:return '';
  }
}
function beanSVG(kind){
  const W=90,H=64,cx=W/2,cy=H/2,stroke="#5a4632",green="#9aaf6e";
  const crease=`<path d="M${cx} ${cy-24} C ${cx-7} ${cy-10}, ${cx+7} ${cy+10}, ${cx} ${cy+24}" stroke="#3a2c1e" stroke-width="2.4" fill="none"/>`;
  const body=(f,st)=>`<ellipse cx="${cx}" cy="${cy}" rx="26" ry="30" fill="${f}" stroke="${st||stroke}" stroke-width="2"/>`;
  let inner;
  switch(kind){
    case 'healthy': inner=body(green)+crease; break;
    case 'fullblack': inner=body('#241a12','#160f0a')+`<path d="M${cx} ${cy-24} C ${cx-7} ${cy-10}, ${cx+7} ${cy+10}, ${cx} ${cy+24}" stroke="#0e0906" stroke-width="2.4" fill="none"/>`; break;
    case 'partialblack': inner=body(green)+`<path d="M${cx} ${cy-30} A26 30 0 0 1 ${cx} ${cy+30} Z" fill="#241a12"/>`+crease; break;
    case 'sour': inner=body('#8a5a3a')+`<circle cx="${cx-8}" cy="${cy-6}" r="6" fill="#5f3218" opacity="0.75"/><circle cx="${cx+6}" cy="${cy+9}" r="7" fill="#5f3218" opacity="0.6"/><circle cx="${cx+5}" cy="${cy-11}" r="4" fill="#5f3218" opacity="0.6"/>`+crease; break;
    case 'broken': inner=`<path d="M${cx-3} ${cy-30} A26 30 0 1 0 ${cx+19} ${cy+23} L${cx} ${cy} Z" fill="${green}" stroke="${stroke}" stroke-width="2" stroke-linejoin="round"/>`+crease; break;
    case 'insect': inner=body(green)+`<circle cx="${cx-6}" cy="${cy-8}" r="3.2" fill="#241a12"/><circle cx="${cx+7}" cy="${cy+4}" r="2.6" fill="#241a12"/><circle cx="${cx-2}" cy="${cy+13}" r="2.2" fill="#241a12"/>`+crease; break;
    case 'quaker': inner=body('#cbb083')+crease; break;
    case 'shell': inner=`<path d="M${cx} ${cy-30} A26 30 0 0 1 ${cx} ${cy+30} A14 26 0 0 0 ${cx} ${cy-30} Z" fill="${green}" stroke="${stroke}" stroke-width="2"/>`; break;
    case 'immature': inner=body('#b7c48a')+`<path d="M${cx} ${cy-24} C ${cx-6} ${cy-10}, ${cx+6} ${cy+10}, ${cx} ${cy+24}" stroke="#6a7a48" stroke-width="2" fill="none"/>`; break;
    default: inner=body(green)+crease;
  }
  return `<svg viewBox="0 0 ${W} ${H}" width="100%" style="max-width:110px" role="img">${inner}</svg>`;
}
// Render a labelled gallery of bean illustrations for a defect page.
function beanGallery(items){
  if(!items||!items.length)return '';
  return `<div class="beangal">${items.map(it=>`<figure class="beanfig">
    ${beanSVG(it.kind)}
    <figcaption><b>${esc(it.label)}</b><span>${esc(it.cap)}</span></figcaption>
  </figure>`).join('')}</div>`;
}
function refsBlock(refs){
  if(!refs||!refs.length)return '';
  return `<div class="refs"><h4>Sources</h4><ul>${refs.map(r=>
    `<li><a href="${esc(r.link)}" target="_blank" rel="noopener noreferrer">${esc(r.label)}</a></li>`
  ).join('')}</ul></div>`;
}
function methDetail(id){
  const m=METHODOLOGY[id]; if(!m)return go('learn');
  const glabel=METH_GROUPS.find(g=>g[0]===m.group)?.[1]||'';
  const siblings=Object.entries(METHODOLOGY).filter(([sid,sm])=>sm.group===m.group&&sid!==id);
  const sibBlock=siblings.length?`<div class="siblings">
    <h4>More in ${esc(glabel)}</h4>
    <div class="grid mgrid">${siblings.map(([sid,sm])=>methCard(sid,sm,false)).join('')}</div>
  </div>`:'';
  app.innerHTML=`<div class="wrap detail">
    <button class="back" onclick="go('learn')">← All topics</button>
    <div class="dhead" style="border-bottom:none;padding-bottom:6px">
      <div class="txt">
        <div class="lvl" style="color:${m.accent}">${esc(glabel)}</div>
        <h1>${esc(m.name)}</h1>
        <div class="sub">${esc(m.sub)}</div>
      </div>
    </div>
    ${m.sections.map((s,i)=>`<div class="msection"><h3>${esc(s.h)}</h3><p>${esc(s.body)}</p></div>${i===0&&m.diagram?diagram(m.diagram):''}`).join('')}
    ${m.visuals?`<div class="msection"><h3>${esc(m.visuals.title||'Defect Reference')}</h3>${m.visuals.note?`<p>${esc(m.visuals.note)}</p>`:''}${beanGallery(m.visuals.beans)}</div>`:''}
    ${m.keypoints?`<div class="keypoints"><h4>Key Points</h4><ul style="margin:0;padding:0">${m.keypoints.map(k=>`<li>${esc(k)}</li>`).join('')}</ul></div>`:''}
    ${refsBlock(m.refs)}
    ${sibBlock}
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
