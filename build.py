#!/usr/bin/env python3
"""Build the self-contained 'Coffee - An Industry Guide' HTML PWA from JSON data."""
import json, pathlib, re

# ---- Country-silhouette curve smoothing -------------------------------------
# The COUNTRY_SIL paths are hand-authored as straight-line polygons (readable,
# capture each country's proportions). At build time we convert every polygon
# into a smooth closed Bezier curve (Catmull-Rom -> cubic Bezier) so the outlines
# flow like real coastlines instead of reading as angular blobs.
def _cr_to_bezier(pts, tension=0.8):
    n = len(pts)
    if n < 3:
        return None
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(n):
        p0 = pts[(i - 1) % n]; p1 = pts[i]; p2 = pts[(i + 1) % n]; p3 = pts[(i + 2) % n]
        c1x = p1[0] + (p2[0] - p0[0]) / 6.0 * tension
        c1y = p1[1] + (p2[1] - p0[1]) / 6.0 * tension
        c2x = p2[0] - (p3[0] - p1[0]) / 6.0 * tension
        c2y = p2[1] - (p3[1] - p1[1]) / 6.0 * tension
        d += f" C{c1x:.1f} {c1y:.1f} {c2x:.1f} {c2y:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return d + "Z"

def _subdivide(pts):
    """Insert a midpoint between each pair of vertices -> doubles the point count,
    giving the curve smoother finer coastline detail to work with."""
    out = []
    n = len(pts)
    for i in range(n):
        a = pts[i]; b = pts[(i + 1) % n]
        out.append(a)
        out.append(((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0))
    return out

def smooth_silhouette(d, tension=0.8, subdivide=True):
    out = []
    for part in re.split(r'Z', d):
        nums = re.findall(r'-?\d+\.?\d*', part)
        if len(nums) >= 6:
            pts = [(float(nums[j]), float(nums[j + 1])) for j in range(0, len(nums) - 1, 2)]
            if subdivide:
                pts = _subdivide(pts)
            b = _cr_to_bezier(pts, tension)
            if b:
                out.append(b)
    return " ".join(out)

BASE = pathlib.Path(__file__).parent
profiles = json.loads((BASE / "data_profiles.json").read_text())["PROFILES"]
_meth_raw = json.loads((BASE / "data_methodology.json").read_text())
methodology = _meth_raw["METHODOLOGY"]
glossary = _meth_raw.get("GLOSSARY", [])

APP_VERSION = "v53"
CACHE_C = "coffee-guide-v53"

PROFILE_GROUPS = [
    ("light", "Light"),
    ("medium", "Medium"),
    ("mediumdark", "Medium-Dark"),
    ("dark", "Dark"),
    ("purpose", "Purpose-Built"),
]
METH_GROUPS = [
    ("culture", "Coffee, the Bigger Picture"),
    ("grow", "Growing & Origin"),
    ("green", "Green Buying & QC"),
    ("read", "Reading the Roast"),
    ("science", "Roast Science"),
    ("practice", "In Practice"),
    ("cupping", "Cupping & Quality"),
    ("ops", "Roastery Operations"),
    ("brew", "Brewing & Barista"),
    ("business", "The Business of Coffee"),
]

# Top-level chapters that organize the 10 areas into a clear journey, so the Learn
# hub reads as five stages rather than one long flat list of groups.
METH_CHAPTERS = [
    ("world",  "The World of Coffee", "History, culture, economics, and the plant itself",       "#c98a2e", ["culture", "grow"]),
    ("green",  "From Cherry to Green", "Processing, grading, and buying green coffee",            "#7d8f5a", ["green"]),
    ("roast",  "The Craft of Roasting", "Reading the roast, the science, and diagnosing it",      "#C9A34E", ["read", "science", "practice"]),
    ("taste",  "Tasting & Quality",     "Cupping, scoring, and the language of flavor",           "#6E3E1E", ["cupping"]),
    ("serve",  "Brewing & Business",    "Behind the bar, running the roastery, and the trade",    "#5A2F16", ["brew", "ops", "business"]),
]

# Per-group metadata for the Learn hub: one-line description + accent color.
# Ordered to follow the bean's journey: buy green → roast → taste → run the shop → brew.
METH_GROUP_META = {
    "culture": {"desc": "The story and economics of coffee — coffee history and the coffeehouse, how the trade and prices work, direct trade, sustainability and climate, blending, and spotlights on the drink itself.", "accent": "#c98a2e"},
    "grow":    {"desc": "Where coffee comes from before the green bean — the plant, the varieties and their family tree (with spotlights on Geisha, Bourbon, SL28 and more), the two species, harvest, and the climate pressures on the crop.", "accent": "#5f8f4a"},
    "green":   {"desc": "Grading defects, moisture and density, processing methods, and reading a green coffee before you buy it.", "accent": "#7d8f5a"},
    "read":    {"desc": "The roast curve, rate of rise, the phases, first and second crack, and development time — how to read a roast as it happens.", "accent": "#C9A34E"},
    "science": {"desc": "What's chemically happening inside the bean, how heat moves through the drum, and the machines that do it.", "accent": "#B07B3E"},
    "practice":{"desc": "Roast defects and how to diagnose them, plus sample roasting and dialing in a profile.", "accent": "#95602F"},
    "origin":  {"desc": "How coffee from eight origins behaves in the roaster and the target roast for each.", "accent": "#8A5A34"},
    "cupping": {"desc": "Cupping mechanics, the modern CVA and legacy scoring, the flavor wheel, and the roaster's QC loop.", "accent": "#6E3E1E"},
    "ops":     {"desc": "Running the roastery day: warm-up, between-batch protocol, fire safety, decaf, degassing, and logging.", "accent": "#7A4A28"},
    "brew":    {"desc": "Behind the bar: extraction theory, dialing espresso, grind, brew methods, milk, and water.", "accent": "#5A2F16"},
    "business":{"desc": "Coffee as a livelihood — the roastery as a business, wholesale vs retail vs direct, café operations, and menu and pricing.", "accent": "#9a6a3a"},
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
    "METH_CHAPTERS": METH_CHAPTERS,
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
  --ink:#f0e6d8; --ink1:#f0e6d8; --ink2:#c9b8a4; --ink3:#8f7c66;
  --heat1:#C9A34E; --heat2:#B07B3E; --heat3:#95602F; --heat4:#6E3E1E; --heat5:#43220F;
  --accent:#C9A34E;
  --mono:'SFMono-Regular',ui-monospace,Menlo,Consolas,monospace;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:var(--bg);color:var(--ink);
  font-family:ui-sans-serif,system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
  -webkit-font-smoothing:antialiased;line-height:1.5}
a,a:visited{color:inherit}
button{font-family:inherit;cursor:pointer;color:inherit}
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
.ver{font-family:var(--mono);font-size:11px;color:var(--ink3);
  border:1px solid var(--line);padding:3px 8px;border-radius:20px}
.navtabs{display:flex;gap:2px;margin-left:auto}
.navtabs button{background:none;border:none;color:var(--ink3);font-size:13.5px;
  font-weight:600;padding:8px 12px;border-radius:7px;transition:.15s}
.navtabs button:hover{color:var(--ink2)}
.navtabs button.on{color:var(--ink);background:var(--panel2)}
.searchbtn{background:var(--panel2);border:1px solid var(--line);color:var(--ink2);width:36px;height:36px;
  border-radius:9px;display:flex;align-items:center;justify-content:center;transition:.15s;flex-shrink:0}
.searchbtn:hover{color:var(--ink);border-color:var(--ink3)}
/* search overlay */
.searchoverlay{position:fixed;inset:0;z-index:100;background:rgba(10,8,6,.72);backdrop-filter:blur(6px);
  display:flex;justify-content:center;align-items:flex-start;padding:8vh 16px 16px}
.searchpanel{width:100%;max-width:640px;background:var(--panel);border:1px solid var(--line);border-radius:16px;
  box-shadow:0 24px 70px rgba(0,0,0,.6);overflow:hidden;max-height:82vh;display:flex;flex-direction:column}
.searchtop{display:flex;align-items:center;gap:12px;padding:16px 18px;border-bottom:1px solid var(--line);color:var(--ink3)}
.searchtop input{flex:1;background:none;border:none;outline:none;color:var(--ink);font-size:17px;font-family:inherit}
.searchtop input::placeholder{color:var(--ink3)}
.searchclose{background:var(--bg);border:1px solid var(--line);color:var(--ink3);font-family:var(--mono);
  font-size:11px;padding:4px 9px;border-radius:7px;flex-shrink:0}
.searchresults{overflow-y:auto;padding:10px}
.searchhint{color:var(--ink3);font-size:14px;line-height:1.6;padding:24px 14px;text-align:center}
.searchhint b{color:var(--ink2);font-weight:600}
.searchgroup{margin-bottom:12px}
.searchglabel{font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--ink3);padding:8px 12px 6px}
.searchitem{display:flex;flex-direction:column;gap:2px;width:100%;text-align:left;background:none;border:none;
  padding:10px 12px;border-radius:9px;transition:.12s}
.searchitem:hover{background:var(--panel2)}
.searchitem .si-name{font-size:15px;font-weight:600;color:var(--ink1)}
.searchitem .si-meta{font-size:11.5px;color:var(--ink3);font-family:var(--mono)}
.searchitem .si-def{font-size:12.5px;color:var(--ink3);line-height:1.4}
.searchmore{font-size:12px;color:var(--ink3);padding:6px 12px;font-style:italic}
/* glossary inline term links + popover */
.termref{border-bottom:1px dotted var(--heat2);cursor:help;color:inherit}
.termref:hover{border-bottom-color:var(--heat1);color:var(--heat1)}
.termpop{position:absolute;z-index:200;background:var(--panel2);border:1px solid var(--heat3);border-radius:12px;
  padding:13px 15px;box-shadow:0 14px 40px rgba(0,0,0,.55);animation:popin .12s ease}
@keyframes popin{from{opacity:0;transform:translateY(-4px)}to{opacity:1;transform:none}}
.termpop-term{font-size:14px;font-weight:700;color:var(--heat1);margin-bottom:5px}
.termpop-def{font-size:13px;color:var(--ink2);line-height:1.5}
/* guided path */
.pathlist{display:flex;flex-direction:column;gap:8px}
.pathstep{display:flex;align-items:center;gap:14px;width:100%;text-align:left;background:var(--panel);
  border:1px solid var(--line);border-radius:11px;padding:13px 15px;cursor:pointer;transition:.15s}
.pathstep:hover{border-color:var(--heat3);background:var(--panel2);transform:translateX(3px)}
.pathnum{flex-shrink:0;width:28px;height:28px;border-radius:50%;background:var(--bg);border:1px solid var(--heat3);
  color:var(--heat1);font-family:var(--mono);font-size:13px;font-weight:700;display:flex;align-items:center;justify-content:center}
.pathtxt{display:flex;flex-direction:column;gap:2px;flex:1;min-width:0}
.pathname{font-size:15px;font-weight:650;color:var(--ink1)}
.pathwhy{font-size:12.5px;color:var(--ink3);line-height:1.4}
.patharrow{color:var(--ink3);font-size:16px;flex-shrink:0}
.pathnav{margin-top:34px;padding-top:22px;border-top:1px solid var(--line)}
.pathnav-label{font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--heat2);display:block;margin-bottom:10px}
.pathnav-next{display:flex;flex-direction:column;gap:3px;width:100%;text-align:left;background:linear-gradient(100deg,var(--panel2),var(--panel));
  border:1px solid var(--heat3);border-radius:12px;padding:15px 18px;cursor:pointer;transition:.15s}
.pathnav-next:hover{border-color:var(--heat1);transform:translateY(-2px)}
.pathnav-next span:first-child{font-size:16px;font-weight:700;color:var(--heat1)}
.pathnav-why{font-size:12.5px;color:var(--ink3)}
.pathnav-done{font-size:14px;color:var(--ink2);background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:15px 18px;font-style:italic}
/* related concept chips */
.related{margin-top:28px;display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}
.related-label{font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink3)}
.relchips{display:flex;flex-wrap:wrap;gap:8px}
.relchip{background:var(--panel2);border:1px solid var(--line);color:var(--ink2);font-size:13px;font-weight:600;
  padding:6px 13px;border-radius:20px;cursor:pointer;transition:.14s}
.relchip:hover{border-color:var(--heat3);color:var(--heat1)}

/* hero */
.hero{padding:52px 0 30px;border-bottom:1px solid var(--line);position:relative;overflow:hidden}
.hero .wrap{position:relative;z-index:2}
.hero h1{font-size:clamp(30px,5.5vw,52px);line-height:1.02;letter-spacing:-.03em;max-width:15ch}
.hero h1 .grad{background:linear-gradient(100deg,var(--heat1),var(--heat2),var(--heat1),var(--heat4));
  background-size:280% 100%;-webkit-background-clip:text;background-clip:text;color:transparent;
  animation:shimmer 9s ease-in-out infinite}
@keyframes shimmer{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}
/* heat haze rising behind the hero title */
.hero::before{content:"";position:absolute;inset:-40% -10% auto -10%;height:150%;z-index:1;pointer-events:none;
  background:
    radial-gradient(60% 40% at 18% 120%, rgba(201,163,78,.10), transparent 70%),
    radial-gradient(50% 45% at 62% 130%, rgba(176,123,62,.09), transparent 70%),
    radial-gradient(45% 40% at 88% 120%, rgba(110,62,30,.08), transparent 70%);
  filter:blur(6px);animation:haze 14s ease-in-out infinite alternate}
@keyframes haze{0%{transform:translate3d(0,0,0) scale(1)}
  50%{transform:translate3d(-2%,-3%,0) scale(1.06)}
  100%{transform:translate3d(2%,-1%,0) scale(1.03)}}
.hero p{color:var(--ink2);font-size:16.5px;max-width:60ch;margin:18px 0 0}
.hero .lede{font-size:17.5px;line-height:1.55;max-width:64ch}
.heatbar{display:flex;height:6px;margin-top:28px;border-radius:4px;overflow:hidden;max-width:520px;position:relative;
  box-shadow:0 0 18px rgba(201,163,78,.22)}
.heatbar i{flex:1}
.heatbar::after{content:"";position:absolute;inset:0;pointer-events:none;
  background:linear-gradient(100deg,transparent 20%,rgba(255,240,214,.55) 50%,transparent 80%);
  background-size:220% 100%;mix-blend-mode:screen;animation:heatsweep 4.5s ease-in-out infinite}
@keyframes heatsweep{0%{background-position:180% 0}60%,100%{background-position:-80% 0}}
.herosig{margin-top:22px!important;font-family:var(--mono);font-size:12px;letter-spacing:.02em;
  color:var(--ink3);max-width:60ch;font-style:normal;position:relative;padding-left:14px}
.herosig::before{content:"";position:absolute;left:0;top:2px;bottom:2px;width:2px;border-radius:2px;
  background:linear-gradient(var(--heat1),var(--heat4))}
.hero .beans{position:absolute;inset:0;z-index:1;opacity:.5}

/* home section directory */
.dirlead{font-family:var(--mono);font-size:11px;letter-spacing:.18em;text-transform:uppercase;
  color:var(--ink3);margin:34px 0 16px}
.secdir{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:14px}
.secard{display:flex;gap:16px;text-align:left;background:var(--panel);border:1px solid var(--line);
  border-radius:16px;padding:20px;cursor:pointer;transition:.16s;align-items:flex-start}
.secard:hover{border-color:var(--heat3);background:var(--panel2);transform:translateY(-3px);box-shadow:0 10px 28px rgba(0,0,0,.35),0 0 0 1px rgba(201,163,78,.12),0 6px 22px rgba(201,163,78,.10)}
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
.pcard:hover{transform:translateY(-3px);border-color:var(--ink3);box-shadow:0 10px 28px rgba(0,0,0,.35),0 6px 22px rgba(201,163,78,.10)}
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
.learntools{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:20px;
  padding-bottom:14px;border-bottom:1px solid var(--line)}
.ltcount{font-family:var(--mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink3)}
.ltbtn{display:inline-flex;align-items:center;gap:6px;font-size:12.5px;font-weight:600;color:var(--ink1);
  background:var(--panel);border:1px solid var(--line);border-radius:9px;padding:7px 13px;cursor:pointer;
  transition:.15s;white-space:nowrap}
.ltbtn:hover{background:var(--panel2);border-color:var(--ink3);color:var(--heat1)}
.ltbtn svg{opacity:.85}
.chaplist{display:flex;flex-direction:column;gap:26px}
.chapter{--ca:#B07B3E}
.chaphead{display:flex;align-items:center;gap:13px;padding:0 2px 12px;border-bottom:1px solid var(--line);margin-bottom:13px}
.chapnum{width:5px;height:26px;border-radius:3px;background:var(--ca);flex-shrink:0}
.chaptxt{display:flex;flex-direction:column;gap:2px;flex:1;min-width:0}
.chapname{font-size:20px;font-weight:700;color:var(--ink1);letter-spacing:-.01em}
.chapdesc{font-size:12.5px;color:var(--ink3)}
.chapcount{font-family:var(--mono);font-size:12px;color:var(--ca);font-weight:600;
  border:1px solid var(--ca);border-radius:20px;padding:2px 10px;flex-shrink:0;opacity:.85}
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
.regionmap{margin:20px auto 8px;text-align:center}
.regionmap svg{margin:0 auto}
.regionmap figcaption{text-align:left}
.originnote{color:var(--ink2);font-size:15px;line-height:1.6;max-width:70ch;margin:20px 0 8px}
.origrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:13px;margin-top:4px}
.origcard{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:17px;cursor:pointer;
  transition:.16s;display:flex;flex-direction:column;gap:9px}
.origcard:hover{border-color:var(--heat3);background:var(--panel2);transform:translateY(-3px);box-shadow:0 10px 28px rgba(0,0,0,.35),0 6px 22px rgba(201,163,78,.10)}
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
/* sticky back on detail pages — follows the scroll, pins below the nav */
.back.sticky{position:sticky;top:calc(72px + env(safe-area-inset-top,0px));z-index:20;
  box-shadow:0 4px 14px rgba(0,0,0,.35);backdrop-filter:blur(6px);background:rgba(42,33,26,.92)}
@media(max-width:640px){.back.sticky{top:calc(112px + env(safe-area-inset-top,0px))}}
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
.diagram{margin:20px 0 8px;background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px 18px 14px;
  position:relative;overflow:hidden;animation:diareveal .5s cubic-bezier(.2,.7,.3,1) both;transition:border-color .3s,box-shadow .3s}
.diagram:hover{border-color:var(--heat3);box-shadow:0 0 24px rgba(201,163,78,.08)}
@keyframes diareveal{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
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
/* the roast-curve bean-temp line draws itself in, like a live roast being plotted */
.rc-bt{stroke-dasharray:1400;stroke-dashoffset:1400;animation:rcdraw 1.6s cubic-bezier(.4,.6,.3,1) .15s forwards}
@keyframes rcdraw{to{stroke-dashoffset:0}}
/* content view fade-in on navigation */
#app{animation:viewfade .34s ease both}
@keyframes viewfade{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
/* subtle staggered entrance for grids of cards */
.grid>*,.origrid>*,.secdir>*{animation:cardrise .42s cubic-bezier(.2,.7,.3,1) both}
.grid>*:nth-child(2),.origrid>*:nth-child(2),.secdir>*:nth-child(2){animation-delay:.03s}
.grid>*:nth-child(3),.origrid>*:nth-child(3),.secdir>*:nth-child(3){animation-delay:.06s}
.grid>*:nth-child(4),.origrid>*:nth-child(4),.secdir>*:nth-child(4){animation-delay:.09s}
.grid>*:nth-child(n+5),.origrid>*:nth-child(n+5){animation-delay:.12s}
@keyframes cardrise{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
/* gentle glow pulse on the live stat counters / accent dots */
@keyframes emberpulse{0%,100%{opacity:.55}50%{opacity:1}}
/* RESPECT reduced-motion: disable all non-essential motion */
@media(prefers-reduced-motion:reduce){
  *,*::before,*::after{animation-duration:.001ms!important;animation-iteration-count:1!important;
    transition-duration:.001ms!important;scroll-behavior:auto!important}
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
    <button class="searchbtn" onclick="openSearch()" aria-label="Search everything">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg>
    </button>
    <span class="ver" id="verlabel"></span>
  </div>
</header>
<div id="searchoverlay" class="searchoverlay" style="display:none">
  <div class="searchpanel">
    <div class="searchtop">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg>
      <input id="globalsearch" type="search" placeholder="Search profiles, origins, topics, terms…" autocomplete="off">
      <button class="searchclose" onclick="closeSearch()" aria-label="Close search">Esc</button>
    </div>
    <div id="searchresults" class="searchresults"></div>
  </div>
</div>
<nav class="mobnav">
  <button data-nav="home" onclick="go('home')">Overview</button>
  <button data-nav="profiles" onclick="go('profiles')">Profiles</button>
  <button data-nav="origins" onclick="go('origins')">Origins</button>
  <button data-nav="compare" onclick="go('compare')">Compare</button>
  <button data-nav="learn" onclick="go('learn')">Learn</button>
</nav>
<main id="app"></main>
<footer><div class="wrap">
  <span>Coffee — An Industry Guide · Made for the people who take it seriously.</span>
  <span id="footver"></span>
</div></footer>

<script id="appdata" type="application/json">__DATA__</script>
<script>
const D = JSON.parse(document.getElementById('appdata').textContent);
const {PROFILES,METHODOLOGY,GLOSSARY,PROFILE_GROUPS,METH_GROUPS,METH_CHAPTERS,METH_GROUP_META,FLAVOR_AXES,APP_VERSION}=D;
// Guided beginner path: an ordered spine through the fundamentals.
const PATH=[
  {id:'history',label:"Coffee\u2019s Origin Story",why:"Where it all came from, before anything else."},
  {id:'plant',label:'The Coffee Plant',why:"What coffee actually is \u2014 a fruit seed."},
  {id:'varietals',label:'Varietals & Cultivars',why:"Why the variety sets the flavor ceiling."},
  {id:'green_processing',label:'Processing Methods',why:"How the cherry becomes the green bean."},
  {id:'green_intro',label:'Buying Green Coffee',why:"The green caps everything downstream."},
  {id:'curve',label:'Reading the Roast Curve',why:"The roaster's core instrument."},
  {id:'phases',label:'The Phases of a Roast',why:"Drying, Maillard, development \u2014 the three acts."},
  {id:'cracks',label:'First & Second Crack',why:"The audible landmarks that set roast level."},
  {id:'chemistry',label:'Roasting Chemistry',why:"What's actually happening inside the bean."},
  {id:'cupping_intro',label:'Cupping',why:"How the industry tastes and scores coffee."},
  {id:'brew_extraction',label:'Extraction Theory',why:"The one idea behind every brew method."},
  {id:'brew_troubleshoot',label:'Brew Troubleshooting',why:"Turn theory into a better cup at home."},
];
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
  g+=`<path class="rc-bt" d="${btPath}" fill="none" stroke="${accent}" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"/>`;
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
// Scroll-position memory: remember where each view was scrolled to, so pressing
// "back" returns you to the same spot instead of jumping to the top.
let scrollMemo=Object.create(null);
function viewKey(s){return s.view+(s.arg?(':'+s.arg):'');}
function go(view,arg,restore){
  // save the scroll position of the view we're leaving
  if(state) scrollMemo[viewKey(state)]=window.scrollY||window.pageYOffset||0;
  const prev=state;
  state={view,arg};
  render();
  const top=['home','start','profiles','origins','compare','learn'].includes(view)?view:
    (view==='profile'?'profiles':view==='origin'?'origins':view==='meth'?'learn':'home');
  setNav(top);
  // restore remembered position when returning to a view; otherwise go to top.
  const y = restore ? (scrollMemo[viewKey(state)]||0) : 0;
  // wait for layout, then restore (double rAF is reliable across mobile browsers)
  const raf = (typeof requestAnimationFrame==='function') ? requestAnimationFrame : (cb)=>setTimeout(cb,0);
  raf(()=>raf(()=>window.scrollTo(0,y)));
}
// A "back" navigation: same as go() but restores the previous scroll spot.
function goBack(view,arg){go(view,arg,true);}

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

    <div class="block2"><h2 class="bh">A path through the fundamentals</h2>
    <p class="bsub">New here and want a route, not a pile of topics? Read these in order — each builds on the last.</p>
    <div class="pathlist">${PATH.map((step,i)=>`
      <button class="pathstep" onclick="go('meth','${step.id}')">
        <span class="pathnum">${i+1}</span>
        <span class="pathtxt"><span class="pathname">${esc(step.label)}</span><span class="pathwhy">${esc(step.why)}</span></span>
        <span class="patharrow">→</span>
      </button>`).join('')}
    </div></div>

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
    [svgIcon('profiles'),'Roast Profiles',`Every roast level from Nordic light to Italian dark — plus purpose-built espresso and omni. Each one broken down by curve, phase, and flavor signature, including the honest bit: exactly how it falls apart when you push it too far.`,`Browse ${nP} profiles`,`profiles`],
    [svgIcon('compare'),'Compare',`Put any two profiles nose to nose. Overlay their flavor radars or their roast curves and watch a light and a dark pull apart in front of you — no guessing, just the shapes.`,`Open compare`,`compare`],
    [svgIcon('origin'),'Roasting by Origin',`${nO} growing regions, and how each one actually behaves in the drum — what the green wants, where it fights you, and the roast level that finally lets it sing.`,`Explore origins`,`origins`],
    [svgIcon('learn'),'Learn',`${nLearn} deep-dives across the whole craft — green buying and grading, reading the roast, the science underneath it, cupping, running a roastery, and holding it together behind the bar. The good stuff, none of the padding.`,`Start learning`,`learn`],
    [svgIcon('start'),'New to Coffee?',`Start here, no shame in it. A plain-language tour of how a grassy green seed becomes the cup, the light-versus-dark tradeoff that decides everything, and a glossary that quietly translates the jargon.`,`Get oriented`,`start`],
  ];
  app.innerHTML=`
  <section class="hero">
    <div class="wrap">
      <h1>Where green coffee <span class="grad">becomes flavor.</span></h1>
      <p class="lede">A field reference for the people who roast, brew, and buy coffee for a living. From the green bean to the roast curve to the cup — the theory that actually changes what you do at the machine. Opinionated where it counts, honest about the rest, and blessedly free of fluff.</p>
      <div class="heatbar">${heat}</div>
      <p class="herosig">Light to dark, seed to cup — every step here has a reason, and we tell you what it is.</p>
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
  app.innerHTML=`<div class="wrap"><div class="seclead"><span class="no">01</span><div><h2>Roast Profiles</h2><p>Ten core profiles, from the palest Nordic to the darkest Italian — the whole spectrum, warts and all.</p></div></div>
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
function emptyState(){return `<div class="empty">Nothing here matches that one. Try a roast level, a flavor like “bright” or “bitter,” or clear the search and start over — no harm done.</div>`;}

/* ---------- PROFILE DETAIL ---------- */
function profileDetail(id){
  const p=PROFILES[id]; if(!p)return go('profiles');
  const c=p.curve;
  const stat=(lab,val,unit,hi)=>`<div class="stat ${hi?'hi':''}"><div class="lab">${lab}</div><div class="val">${val}${unit?`<small>${unit}</small>`:''}</div></div>`;
  const dual=(cv,fv)=>`${cv}<small>°C</small> · ${fv}<small>°F</small>`;
  app.innerHTML=`<div class="wrap detail">
    <button class="back sticky" onclick="goBack('profiles')">← All profiles</button>
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
    <div class="seclead"><span class="no">02</span><div><h2>Compare Profiles</h2><p>Overlay flavor signatures or roast curves and let them argue it out. Up to four at a time.</p></div></div>
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
function originList(){
  const origins=Object.entries(METHODOLOGY).filter(([id,m])=>m.group==='origin'&&id!=='origin_intro');
  const intro=METHODOLOGY['origin_intro'];
  const byCont={};
  origins.forEach(([id,m])=>{(byCont[m.continent]=byCont[m.continent]||[]).push([id,m]);});
  const contOrder=['Africa','Middle East','Central America','Caribbean','North America','South America','Asia','Oceania'];
  app.innerHTML=`<div class="wrap">
    <div class="seclead"><span class="no">◍</span><div><h2>Roasting by Origin</h2><p>Where the coffee comes from shapes the cup before you ever light the burner. ${origins.length} origins, how each behaves, and the roast that shows it best.</p></div></div>
    ${beltStrip(origins.length)}
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
// Compact "bean belt" context strip (not an interactive map — just the equatorial-band idea, done well).
function beltStrip(n){
  const W=760,H=120,cy=60;
  let g=`<rect x="0" y="0" width="${W}" height="${H}" fill="#12100c" rx="12"/>`;
  // band
  g+=`<rect x="0" y="${cy-26}" width="${W}" height="52" fill="var(--heat5)" opacity="0.12"/>`;
  g+=`<line x1="0" y1="${cy-26}" x2="${W}" y2="${cy-26}" stroke="var(--heat4)" stroke-dasharray="6 5" opacity="0.55"/>`;
  g+=`<line x1="0" y1="${cy+26}" x2="${W}" y2="${cy+26}" stroke="var(--heat4)" stroke-dasharray="6 5" opacity="0.55"/>`;
  g+=`<line x1="0" y1="${cy}" x2="${W}" y2="${cy}" stroke="var(--heat3)" stroke-width="1" opacity="0.35"/>`;
  g+=`<text x="16" y="${cy-32}" fill="var(--heat3)" font-size="12" font-family="ui-monospace" opacity="0.8">Tropic of Cancer</text>`;
  g+=`<text x="16" y="${cy+42}" fill="var(--heat3)" font-size="12" font-family="ui-monospace" opacity="0.8">Tropic of Capricorn</text>`;
  g+=`<text x="16" y="${cy+4}" fill="var(--heat3)" font-size="11" font-family="ui-monospace" opacity="0.6">equator</text>`;
  // a scatter of bean dots inside the band representing the growing world
  const xs=[120,175,205,235,265,300,430,470,620,700];
  xs.forEach((x,i)=>{const yy=cy+((i*13)%34-17)*0.7;g+=`<circle cx="${x}" cy="${yy.toFixed(0)}" r="5" fill="var(--heat1)" opacity="0.9"/>`;});
  g+=`<text x="${W-16}" y="${cy+4}" fill="var(--heat2)" font-size="13" font-family="ui-monospace" text-anchor="end" letter-spacing="2" opacity="0.75">THE BEAN BELT</text>`;
  return `<figure class="diagram" style="margin-top:14px"><svg viewBox="0 0 ${W} ${H}" width="100%" role="img">${g}</svg><figcaption>Coffee grows only in a warm band circling the equator, between the Tropics of Cancer and Capricorn — every origin below sits inside it. Each origin page has a map of its own growing regions.</figcaption></figure>`;
}
// Per-origin regional locator: stylized country silhouette with growing regions plotted as dots.
// Simplified, recognizable country silhouettes (normalized to a ~100x100 box).
// Rendered faintly in the empty lower-right of the region-map card as a watermark.
// Only distinctive, identifiable shapes are included; origins without one render nothing (no fake blob).
const COUNTRY_SIL={
  // Higher-detail, recognizable country silhouettes normalized to a ~100x100 box.
  // Drawn to fill the box and capture each country's distinctive contour, not a blob.
  'Brazil':'M50 6 L57 9 L61 5 L67 9 L65 16 L72 18 L79 25 L83 34 L86 45 L84 55 L80 63 L82 71 L76 80 L68 87 L59 91 L50 90 L43 84 L45 77 L38 79 L33 72 L36 65 L28 62 L22 54 L18 45 L20 37 L26 31 L22 24 L28 19 L36 22 L41 16 L46 19 Z',
  'Colombia':'M42 8 L50 6 L55 12 L60 10 L64 16 L70 18 L73 25 L71 32 L66 36 L70 44 L67 54 L70 62 L64 74 L57 86 L50 90 L45 82 L47 72 L42 66 L44 56 L38 52 L34 44 L38 36 L33 30 L36 22 L31 16 Z',
  'Ethiopia':'M16 42 L26 34 L34 30 L40 20 L48 16 L54 22 L62 20 L70 26 L80 30 L88 38 L86 46 L78 50 L84 58 L76 66 L66 70 L58 76 L50 72 L42 78 L34 72 L30 62 L36 54 L26 52 L20 48 Z',
  'Kenya':'M30 16 L42 14 L50 18 L84 28 L78 38 L74 46 L76 56 L70 66 L60 80 L52 88 L46 80 L44 66 L36 60 L32 50 L38 42 L30 36 L34 28 L26 22 Z',
  'Vietnam':'M36 6 L46 8 L50 16 L48 24 L54 30 L58 40 L56 48 L64 54 L70 62 L66 70 L58 68 L54 78 L50 90 L44 86 L48 74 L44 64 L50 58 L46 50 L50 42 L44 36 L48 28 L42 22 L46 14 L38 12 Z',
  'India':'M28 12 L38 8 L48 10 L58 8 L70 12 L78 18 L82 26 L76 32 L80 38 L74 44 L78 50 L70 58 L64 50 L62 62 L56 76 L50 88 L45 76 L42 62 L36 54 L30 48 L34 40 L26 34 L30 26 L24 20 Z',
  'Indonesia (Sumatra)':'M18 20 L28 14 L34 22 L44 28 L52 38 L62 46 L72 56 L82 66 L88 74 L82 80 L72 74 L62 64 L54 56 L44 48 L36 40 L28 32 L22 26 Z',
  'Mexico':'M8 22 L20 18 L32 22 L42 20 L52 26 L60 22 L70 20 L80 26 L86 34 L80 40 L88 44 L84 52 L74 50 L78 60 L70 72 L64 62 L58 68 L54 58 L46 52 L40 56 L34 48 L26 42 L18 38 L12 30 Z',
  'Peru':'M58 8 L68 12 L74 20 L72 30 L80 40 L76 50 L66 58 L60 70 L50 82 L40 90 L32 82 L40 74 L46 62 L50 50 L54 40 L52 30 L56 20 Z',
  'Papua New Guinea':'M10 42 L22 36 L32 42 L42 38 L50 44 L58 38 L68 42 L78 48 L88 52 L84 60 L74 62 L64 56 L56 62 L48 56 L40 62 L30 56 L20 54 L12 50 Z',
  'Panama':'M8 40 L20 36 L30 44 L38 40 L46 48 L56 44 L64 40 L74 46 L86 50 L82 58 L72 62 L62 56 L54 62 L46 56 L38 60 L30 54 L20 52 L12 46 Z',
  'Costa Rica':'M26 24 L38 20 L48 26 L58 24 L66 32 L74 42 L72 54 L64 66 L56 76 L48 68 L44 58 L38 60 L34 50 L28 44 L24 34 Z',
  'Guatemala':'M18 30 L30 24 L44 22 L58 26 L70 30 L80 38 L76 48 L66 50 L58 46 L52 56 L46 66 L40 58 L44 48 L34 46 L26 42 L20 38 Z',
  'Honduras':'M12 32 L26 26 L40 24 L54 28 L68 32 L82 38 L78 48 L68 50 L60 46 L52 54 L44 62 L38 54 L42 46 L30 46 L20 44 Z',
  'Nicaragua':'M22 22 L34 20 L46 24 L58 30 L70 38 L76 50 L72 62 L64 72 L56 82 L48 74 L46 62 L50 50 L42 46 L34 42 L28 34 L24 28 Z',
  'El Salvador':'M12 42 L26 36 L40 34 L54 36 L68 40 L82 46 L76 56 L62 56 L50 60 L38 58 L26 60 L16 52 Z',
  'Yemen':'M12 38 L28 32 L44 30 L60 30 L74 34 L86 40 L82 52 L70 58 L58 60 L46 58 L34 62 L24 58 L16 48 Z',
  'Tanzania':'M22 24 L36 20 L50 22 L64 26 L78 32 L84 44 L80 56 L72 68 L62 78 L52 74 L46 62 L40 56 L32 50 L26 42 L28 34 L22 30 Z',
  'Uganda':'M24 26 L38 22 L52 24 L66 28 L78 34 L82 46 L76 58 L64 68 L52 72 L44 64 L40 54 L32 50 L26 42 L28 34 Z',
  'Rwanda':'M22 30 L34 24 L48 22 L62 26 L74 32 L82 42 L78 54 L68 62 L56 66 L46 62 L38 56 L30 50 L24 42 L26 36 Z',
  'Ecuador':'M26 26 L40 22 L54 22 L68 28 L76 36 L72 46 L64 42 L60 54 L52 64 L44 70 L36 62 L40 52 L32 48 L28 40 L24 34 Z',
  'Bolivia':'M30 18 L44 14 L58 16 L72 22 L80 32 L78 44 L70 54 L62 66 L52 76 L42 72 L38 60 L44 50 L36 46 L30 38 L34 30 L28 24 Z',
  'DR Congo':'M18 24 L32 18 L46 16 L60 20 L72 18 L82 26 L86 38 L80 48 L84 58 L76 68 L64 76 L52 72 L44 62 L36 66 L28 58 L24 48 L18 40 L22 32 Z',
  'Thailand':'M40 6 L52 10 L54 20 L48 28 L56 34 L62 44 L58 52 L64 62 L60 72 L54 86 L48 76 L52 64 L46 56 L50 46 L44 40 L48 30 L42 24 L46 16 L38 14 Z',
  'China (Yunnan)':'M12 22 L28 14 L44 12 L60 14 L74 18 L86 26 L90 36 L82 42 L72 44 L62 52 L54 62 L46 56 L40 48 L34 52 L28 44 L22 38 L16 32 Z',
  'Timor-Leste':'M10 44 L26 38 L42 36 L58 38 L74 42 L88 48 L82 58 L66 58 L52 62 L38 60 L24 62 L14 54 Z',
  'Malawi':'M44 8 L54 12 L56 22 L52 32 L58 42 L62 52 L58 64 L52 76 L46 88 L40 76 L46 64 L50 54 L44 44 L48 34 L42 24 L46 16 Z',
  'Zambia':'M14 30 L30 24 L46 22 L60 20 L76 24 L86 32 L82 44 L86 54 L74 62 L62 66 L52 60 L44 66 L34 62 L26 54 L20 44 L24 36 Z',
  'Zimbabwe':'M16 32 L30 26 L46 24 L62 26 L76 32 L86 42 L80 54 L68 62 L56 68 L46 64 L38 58 L30 60 L22 52 L18 42 Z',
  'Burundi':'M26 28 L38 22 L52 22 L66 28 L74 38 L72 50 L64 60 L54 66 L44 62 L36 56 L28 48 L24 40 L26 34 Z',
  'Jamaica':'M8 42 L24 36 L40 34 L56 36 L72 38 L88 44 L84 54 L70 58 L54 60 L38 58 L22 58 L10 52 Z',
  // Island origins (keyed by display name). Distinctive island shapes, same vector style.
  'Java':'M6 48 L18 42 L28 46 L38 42 L48 46 L58 42 L68 46 L78 42 L90 46 L94 52 L84 58 L72 54 L62 58 L50 54 L40 58 L28 54 L18 58 L8 54 Z',
  'Sulawesi (Toraja)':'M28 6 L38 10 L40 22 L36 32 L46 30 L50 18 L58 14 L62 24 L58 36 L50 42 L60 48 L58 62 L52 76 L44 72 L48 58 L40 52 L34 64 L26 60 L32 48 L26 38 L18 42 L14 34 L24 30 L20 20 L26 16 Z',
  'Bali (Kintamani)':'M10 38 L26 30 L44 28 L62 30 L82 36 L90 46 L82 56 L64 60 L48 56 L30 60 L14 52 L8 44 Z',
  'Flores (Bajawa)':'M4 50 L18 44 L30 48 L44 44 L58 48 L72 44 L86 48 L96 52 L88 60 L74 58 L60 62 L46 58 L32 62 L18 58 L6 56 Z',
  'Hawaii (Kona)':'M10 26 L18 22 L24 28 L20 36 L12 34 Z M30 36 L40 32 L46 40 L38 48 L30 44 Z M50 48 L62 44 L70 52 L60 62 L50 56 Z M76 62 L86 58 L92 66 L84 74 L76 68 Z'
};
// Topography per country (coords in the same 0..100 box as COUNTRY_SIL).
// mtns: clusters of [x,y] peak positions placed where the real ranges sit.
// coast: [x,y] points tracing the main coastline edge for a shoreline accent.
// Only the coffee-relevant terrain is marked — enough to read as real geography.
const COUNTRY_TOPO={
  'Brazil':{mtns:[[70,58],[76,54],[73,64],[80,60],[66,62]],coast:[[86,45],[84,55],[80,63],[76,72],[68,80],[60,86]]},
  'Colombia':{mtns:[[44,30],[42,42],[46,54],[40,64],[48,68],[43,48],[45,38]],coast:[[36,22],[31,30],[34,40],[38,20]]},
  'Ethiopia':{mtns:[[46,40],[54,36],[40,48],[58,46],[50,52],[44,56],[60,38]]},
  'Kenya':{mtns:[[44,44],[50,50],[40,54],[54,46],[46,58]],coast:[[70,66],[60,80],[52,88]]},
  'Vietnam':{mtns:[[48,30],[50,44],[46,54],[50,62]],coast:[[58,40],[64,54],[58,68],[52,80]]},
  'India':{mtns:[[36,18],[48,14],[60,18],[68,24],[30,44],[40,56],[52,66]],coast:[[70,30],[64,50],[54,72],[46,84],[34,52],[28,36]]},
  'Indonesia (Sumatra)':{mtns:[[34,26],[44,34],[54,44],[64,54],[74,62]],coast:[[28,18],[40,30],[52,42],[64,54],[78,66]]},
  'Mexico':{mtns:[[28,32],[40,36],[52,34],[62,38],[36,44],[48,42]],coast:[[70,22],[80,30],[74,40],[60,26]]},
  'Peru':{mtns:[[58,24],[62,36],[56,48],[50,60],[44,72],[54,42],[52,54]],coast:[[68,14],[62,30],[52,50],[42,72],[34,84]]},
  'Papua New Guinea':{mtns:[[32,42],[44,46],[54,44],[64,48],[74,52]],coast:[[22,38],[42,42],[62,42],[80,50]]},
  'Guatemala':{mtns:[[36,34],[48,38],[58,36],[44,44]],coast:[[22,32],[64,32]]},
  'Costa Rica':{mtns:[[40,34],[50,40],[58,48],[46,50]],coast:[[28,28],[68,46],[52,72]]},
  'Honduras':{mtns:[[34,34],[46,36],[58,38],[42,44]]},
  'Nicaragua':{mtns:[[40,34],[50,42],[46,54]],coast:[[26,30],[70,40]]},
  'El Salvador':{mtns:[[36,42],[50,44],[62,44]],coast:[[30,54],[64,54]]},
  'Yemen':{mtns:[[30,42],[44,44],[24,50]],coast:[[30,56],[48,58],[66,56]]},
  'Tanzania':{mtns:[[42,34],[52,32],[36,44],[46,50]],coast:[[74,42],[64,64],[54,76]]},
  'Rwanda':{mtns:[[36,38],[48,36],[42,48],[56,42]]},
  'Ecuador':{mtns:[[46,32],[50,44],[44,54],[52,54]],coast:[[30,32],[40,52],[36,64]]},
  'Bolivia':{mtns:[[40,26],[46,38],[42,50],[50,44]]},
  'DR Congo':{mtns:[[68,30],[74,44],[70,56],[76,50]],coast:[[22,42],[28,54]]},
  'China (Yunnan)':{mtns:[[30,26],[44,22],[56,28],[40,40],[52,48]]},
  'Malawi':{mtns:[[48,24],[52,40],[48,56],[52,72]]},
  'Zambia':{mtns:[[36,34],[50,32],[64,34],[46,46]]},
  'Zimbabwe':{mtns:[[38,36],[52,34],[64,40],[48,50]]},
  'Burundi':{mtns:[[36,36],[48,34],[42,48]]},
  'Uganda':{mtns:[[34,36],[46,32],[40,52],[68,40]]},
  'Bali (Kintamani)':{mtns:[[40,40],[52,42],[62,44]]},
  'Flores (Bajawa)':{mtns:[[30,50],[46,48],[60,50],[74,48]]},
  'Sulawesi (Toraja)':{mtns:[[34,30],[44,44],[52,36],[40,56]]},
  'Java':{mtns:[[24,50],[40,48],[56,50],[72,48]]},
};
function originRegionMap(m){
  const rm=m.regionMap; if(!rm)return '';
  const accent=m.accent||'#B07B3E';
  const regions=rm.regions2||[];
  if(!regions.length)return '';
  const W=440, padTop=52, rowH=34, padBot=16;
  const H=padTop+regions.length*rowH+padBot;
  const country=(m.country||m.name).replace(/ \(.*\)/,'');
  let g=diaDefs([accent]);
  g+=`<rect x="0" y="0" width="${W}" height="${H}" fill="#12100c" rx="14"/>`;
  // Country silhouette watermark, lower-right — an elegant engraved-map treatment.
  // One clean shape with a crisp outline, soft tonal "elevation" shading where the
  // highlands sit (no cartoon peaks), and a single quiet marker for the growing heart.
  // Restraint over clutter: it should read as a considered map, not a diorama.
  const silKey=(m.country||m.name).replace(/ \(.*\)/,'');
  const silName=m.country||m.name;
  const sil=COUNTRY_SIL[silName]||COUNTRY_SIL[silKey];
  if(sil){
    const silSize=Math.max((H-padTop)*1.18, 168);        // larger, fills the right side
    const sx=W-silSize+silSize*0.20, sy=H-silSize+silSize*0.18;  // anchor & bleed off the corner
    const uid=_cid(accent)+(''+silSize).replace('.','');
    const gid='silfill'+uid, cid='silclip'+uid, hid='silhi'+uid;
    const topo=COUNTRY_TOPO[silName]||COUNTRY_TOPO[silKey]||{};
    // centroid of the highland points = where the terrain shading + growing marker sit
    let hx=52, hy=48;
    if(topo.mtns&&topo.mtns.length){
      hx=topo.mtns.reduce((a,p)=>a+p[0],0)/topo.mtns.length;
      hy=topo.mtns.reduce((a,p)=>a+p[1],0)/topo.mtns.length;
    }
    // spread of the highlands -> radius of the elevation glow
    let rad=26;
    if(topo.mtns&&topo.mtns.length>1){
      const dmax=Math.max(...topo.mtns.map(p=>Math.hypot(p[0]-hx,p[1]-hy)));
      rad=Math.max(16, Math.min(40, dmax+14));
    }
    g+=`<defs>`+
       `<linearGradient id="${gid}" x1="0" y1="0" x2="1" y2="1">`+
         `<stop offset="0" stop-color="${accent}" stop-opacity="0.26"/>`+
         `<stop offset="1" stop-color="${accent}" stop-opacity="0.13"/></linearGradient>`+
       `<radialGradient id="${hid}" cx="${hx.toFixed(1)}" cy="${hy.toFixed(1)}" r="${rad.toFixed(1)}" gradientUnits="userSpaceOnUse">`+
         `<stop offset="0" stop-color="#e9cf94" stop-opacity="0.42"/>`+
         `<stop offset="0.55" stop-color="#d8b566" stop-opacity="0.16"/>`+
         `<stop offset="1" stop-color="#d8b566" stop-opacity="0"/></radialGradient>`+
       `<clipPath id="${cid}"><path d="${sil}"/></clipPath></defs>`;
    let inner=`<rect x="-10" y="-10" width="120" height="120" fill="url(#${hid})"/>`; // soft highland shading
    // one quiet marker for the coffee-growing heart: a small ring, not a cherry
    inner+=`<circle cx="${hx.toFixed(1)}" cy="${hy.toFixed(1)}" r="2.4" fill="none" stroke="#f0dca0" stroke-width="1" stroke-opacity="0.55"/>`+
           `<circle cx="${hx.toFixed(1)}" cy="${hy.toFixed(1)}" r="0.9" fill="#f0dca0" fill-opacity="0.7"/>`;
    g+=`<g transform="translate(${sx.toFixed(0)},${sy.toFixed(0)}) scale(${(silSize/100).toFixed(3)})" aria-hidden="true">`+
       `<path d="${sil}" fill="url(#${gid})"/>`+
       `<g clip-path="url(#${cid})">${inner}</g>`+
       `<path d="${sil}" fill="none" stroke="${accent}" stroke-opacity="0.35" stroke-width="0.8"/>`+  // crisp outline
       `</g>`;
  }
  // header: a location-pin mark + country + altitude band.
  // Pin sits on the country-name row only; the GROWING REGIONS label is indented
  // to start past the pin so the two never overlap.
  g+=`<g transform="translate(22,14)" filter="url(#dsoft)">
    <path d="M8 0 C3 0 -1 4 -1 9 C-1 16 8 24 8 24 C8 24 17 16 17 9 C17 4 13 0 8 0 Z" fill="${accent}"/>
    <circle cx="8" cy="9" r="3.4" fill="#12100c"/></g>`;
  g+=`<text x="50" y="30" fill="#f0e6d8" font-size="17" font-weight="700" font-family="ui-sans-serif">${esc(country)}</text>`;
  if(rm.alt)g+=`<text x="${W-20}" y="30" fill="${accent}" font-size="12" text-anchor="end" font-family="ui-monospace">${esc(rm.alt)}</text>`;
  g+=`<text x="50" y="46" fill="#8f7c66" font-size="10.5" letter-spacing="1.5" font-family="ui-monospace">GROWING REGIONS</text>`;
  // a subtle vertical spine connecting the region dots
  const dotX=30, firstY=padTop+rowH/2;
  const lastY=padTop+(regions.length-1)*rowH+rowH/2;
  g+=`<line x1="${dotX}" y1="${firstY}" x2="${dotX}" y2="${lastY}" stroke="${accent}" stroke-width="1.5" opacity="0.3"/>`;
  regions.forEach((r,i)=>{
    const cy=padTop+i*rowH+rowH/2;
    g+=`<circle cx="${dotX}" cy="${cy}" r="6.5" fill="url(#${_cid(accent)})" opacity="0.9"/>`;
    g+=`<circle cx="${dotX}" cy="${cy}" r="5.5" fill="${accent}" stroke="#12100c" stroke-width="2"/>`;
    g+=`<text x="${dotX+18}" y="${cy-1}" fill="#f0e6d8" font-size="13.5" font-weight="650" font-family="ui-sans-serif">${esc(r[0])}</text>`;
    g+=`<text x="${dotX+18}" y="${cy+13}" fill="#8f7c66" font-size="11" font-family="ui-sans-serif">${esc(r[1])}</text>`;
  });
  return `<figure class="diagram regionmap"><svg viewBox="0 0 ${W} ${H}" width="100%" style="max-width:460px" role="img" aria-label="Coffee growing regions of ${esc(country)}">${g}</svg><figcaption>${esc(rm.note)}</figcaption></figure>`;
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
    <button class="back sticky" onclick="goBack('origins')">← All origins</button>
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
    ${originRegionMap(m)}
    ${m.sections.map(s=>`<div class="msection"><h3>${esc(s.h)}</h3><p>${linkTerms(s.body, m.name)}</p></div>`).join('')}
    ${m.keypoints?`<div class="keypoints"><h4>Key Points</h4><ul style="margin:0;padding:0">${m.keypoints.map(k=>`<li>${esc(k)}</li>`).join('')}</ul></div>`:''}
    ${refsBlock(m.refs)}
    ${siblings.length?`<div class="siblings"><h4>More origins</h4><div class="origrid">${siblings.map(([sid,sm])=>originCard(sid,sm)).join('')}</div></div>`:''}
    <div style="height:40px"></div>
  </div>`;
}
// Generic meth-style render used by the origin intro page.
function methLike(m,backView,backLabel){
  app.innerHTML=`<div class="wrap detail">
    <button class="back sticky" onclick="goBack('${backView}')">${esc(backLabel)}</button>
    <div class="dhead" style="border-bottom:none;padding-bottom:6px"><div class="txt">
      <div class="lvl" style="color:${m.accent}">Roasting by Origin</div>
      <h1>${esc(m.name)}</h1><div class="sub">${esc(m.sub)}</div>
    </div></div>
    ${m.sections.map(s=>`<div class="msection"><h3>${esc(s.h)}</h3><p>${linkTerms(s.body, m.name)}</p></div>`).join('')}
    ${m.keypoints?`<div class="keypoints"><h4>Key Points</h4><ul style="margin:0;padding:0">${m.keypoints.map(k=>`<li>${esc(k)}</li>`).join('')}</ul></div>`:''}
    ${refsBlock(m.refs)}
    <div style="height:40px"></div>
  </div>`;
}

/* ---------- LEARN LIST ---------- */
/* ---------- LEARN HUB ---------- */
let learnQuery='', learnOpen=new Set();
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
    if(!hits.length){box.innerHTML=`<div class="empty">Drew a blank on that one. Try “crack”, “grind”, “moisture”, or “defect” — or wander the chapters below.</div>`;return;}
    box.innerHTML=`<div class="lcount">${hits.length} topic${hits.length>1?'s':''}</div>
      <div class="grid mgrid">${hits.map(([id,m])=>methCard(id,m,true)).join('')}</div>`;
    return;
  }
  // hub view: chapters → group tiles, click a tile to expand into cards
  const gids=allGroupIds();
  const openCount=gids.filter(g=>learnOpen.has(g)).length;
  const allOpen=openCount===gids.length;
  const toolbar=`<div class="learntools">
    <span class="ltcount">${gids.length} areas · ${Object.values(METHODOLOGY).filter(m=>m.group!=='origin').length} topics</span>
    <button class="ltbtn" onclick="${allOpen?'collapseAllHubs()':'expandAllHubs()'}">
      ${allOpen
        ? '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="18 15 12 9 6 15"/></svg> Collapse all'
        : '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg> Expand all'}
    </button></div>`;
  box.innerHTML=toolbar+`<div class="chaplist">${METH_CHAPTERS.map(([cid,ctitle,cdesc,caccent,groups])=>{
    const chapGroups=groups.filter(gid=>Object.entries(METHODOLOGY).some(([id,m])=>m.group===gid));
    if(!chapGroups.length)return '';
    const total=chapGroups.reduce((n,gid)=>n+Object.entries(METHODOLOGY).filter(([id,m])=>m.group===gid).length,0);
    return `<section class="chapter" style="--ca:${caccent}">
      <div class="chaphead">
        <span class="chapnum"></span>
        <span class="chaptxt"><span class="chapname">${esc(ctitle)}</span><span class="chapdesc">${esc(cdesc)}</span></span>
        <span class="chapcount">${total}</span>
      </div>
      <div class="hublist">${chapGroups.map(gid=>{
        const glabel=METH_GROUPS.find(g=>g[0]===gid)?.[1]||gid;
        const items=Object.entries(METHODOLOGY).filter(([id,m])=>m.group===gid);
        const meta=METH_GROUP_META[gid]||{desc:'',accent:caccent};
        const open=learnOpen.has(gid);
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
      }).join('')}</div>
    </section>`;
  }).join('')}</div>`;
}
function toggleHub(gid){ if(learnOpen.has(gid))learnOpen.delete(gid); else learnOpen.add(gid); drawLearn(); }
function allGroupIds(){ return METH_GROUPS.map(g=>g[0]).filter(gid=>Object.values(METHODOLOGY).some(m=>m.group===gid)); }
function expandAllHubs(){ allGroupIds().forEach(gid=>learnOpen.add(gid)); drawLearn(); }
function collapseAllHubs(){ learnOpen.clear(); drawLearn(); }

/* ---------- METH DETAIL ---------- */
/* ---------- DEFECT BEAN ILLUSTRATIONS (inline SVG, zero-byte, offline) ---------- */
/* ---------- CONCEPT DIAGRAMS (inline SVG, zero-byte, offline, teaching-first) ---------- */
// Shared palette pulled from the app's heat vars so diagrams match the aesthetic.
const DIA={bg:'#1b140e',line:'#3a2e24',ink:'#c9b8a4',ink3:'#8f7c66',
  dry:'#C9A34E',mail:'#B07B3E',dev:'#8A5A34',accent:'#e0864a',ror:'#7a9a6a',hot:'#d0553a'};
function diaWrap(vb,inner,cap){
  const lbl=cap?` aria-label="${esc(cap.replace(/"/g,''))}"`:'';
  return `<figure class="diagram"><svg viewBox="0 0 ${vb}" width="100%" role="img"${lbl} preserveAspectRatio="xMidYMid meet">${inner}</svg>${cap?`<figcaption>${cap}</figcaption>`:''}</figure>`;
}
// Wrap a string into <tspan> lines at ~maxChars, returned as tspans anchored at x.
function wrapTspans(text, x, startY, lineH, maxChars, attrs){
  const words=text.split(' '); const lines=[]; let cur='';
  words.forEach(wd=>{ if((cur+' '+wd).trim().length>maxChars){ if(cur)lines.push(cur); cur=wd; } else cur=(cur+' '+wd).trim(); });
  if(cur)lines.push(cur);
  return lines.map((ln,i)=>`<tspan x="${x}" y="${startY+i*lineH}">${ln}</tspan>`).join('');
}
/* ---------- RICHER-STYLING SVG TOOLKIT ----------
   Shared visual primitives so diagrams read as designed, not utilitarian:
   soft drop shadow, panel gradient, accent glow, hex→rgba helper. Inject
   diaDefs(colors) ONCE per SVG (dedupes gradients by color hash). */
function _hex2rgb(h){h=h.replace('#','');if(h.length===3)h=h.split('').map(c=>c+c).join('');return [parseInt(h.slice(0,2),16),parseInt(h.slice(2,4),16),parseInt(h.slice(4,6),16)];}
function _rgba(h,a){const[r,g,b]=_hex2rgb(h);return `rgba(${r},${g},${b},${a})`;}
function _cid(h){return 'g'+h.replace('#','').toLowerCase();} // stable gradient id from color
// A reusable <defs>: one soft-shadow filter + a vertical gradient per accent color passed in.
function diaDefs(colors){
  const uniq=[...new Set(colors)];
  let grads=uniq.map(c=>{
    const[r,g,b]=_hex2rgb(c);
    return `<linearGradient id="${_cid(c)}" x1="0" y1="0" x2="0" y2="1">`+
      `<stop offset="0" stop-color="rgba(${r},${g},${b},0.22)"/>`+
      `<stop offset="1" stop-color="rgba(${r},${g},${b},0.07)"/></linearGradient>`;
  }).join('');
  const shadow=`<filter id="dsh" x="-20%" y="-20%" width="140%" height="150%">`+
    `<feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#000000" flood-opacity="0.38"/></filter>`;
  const soft=`<filter id="dsoft" x="-30%" y="-30%" width="160%" height="160%">`+
    `<feDropShadow dx="0" dy="1" stdDeviation="1.5" flood-color="#000000" flood-opacity="0.3"/></filter>`;
  return `<defs>${grads}${shadow}${soft}</defs>`;
}
// A gradient-filled rounded card with soft depth. opt: {title, titleColor, r, shadow, strong}
function diaCard(x,y,w,h,color,opt){
  opt=opt||{}; const r=opt.r??12; const sh=opt.shadow===false?'':' filter="url(#dsh)"';
  const sw=opt.strong?1.9:1.3; const so=opt.strong?0.95:0.72;
  let s=`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" fill="url(#${_cid(color)})" stroke="${_rgba(color,so)}" stroke-width="${sw}"${sh}/>`;
  if(opt.title){
    s+=`<text x="${x+w/2}" y="${y+21}" fill="${opt.titleColor||color}" font-size="${opt.titleSize||12.5}" font-weight="800" text-anchor="middle" font-family="ui-sans-serif" letter-spacing="0.4">${opt.title}</text>`;
  }
  return s;
}
// A small pill/chip.
function diaChip(cx,cy,label,color,w){
  w=w||(label.length*7+22);
  return `<rect x="${cx-w/2}" y="${cy-11}" width="${w}" height="22" rx="11" fill="${_rgba(color,0.16)}" stroke="${_rgba(color,0.6)}" stroke-width="1.1"/>`+
    `<text x="${cx}" y="${cy+4}" fill="#f0e6d8" font-size="11" font-weight="600" text-anchor="middle" font-family="ui-sans-serif">${label}</text>`;
}
// A left-accent-bar section header inside a diagram.
function diaHeader(x,y,w,title,sub,color){
  let s=`<rect x="${x}" y="${y}" width="4.5" height="26" rx="2.5" fill="${color}"/>`;
  s+=`<text x="${x+13}" y="${y+13}" fill="#f0e6d8" font-size="14.5" font-weight="800" font-family="ui-sans-serif">${title}</text>`;
  if(sub)s+=`<text x="${x+13}" y="${y+27}" fill="${DIA.ink3}" font-size="10.5" font-family="ui-sans-serif">${sub}</text>`;
  return s;
}
// A directional connector with a soft arrowhead (uses marker 'darr' — inject once via diaArrowMarker).
function diaArrowMarker(color){return `<marker id="darr" markerWidth="9" markerHeight="9" refX="6.5" refY="3" orient="auto"><path d="M0 0 L6.5 3 L0 6 Z" fill="${color||'#8a7660'}"/></marker>`;}
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
  g+=`<text x="${L}" y="${T+barH+24}" fill="${DIA.ink3}" font-size="12" font-family="ui-sans-serif">Roughly the proportions of a balanced roast — most flavor is built in the Maillard phase;</text>`;
  g+=`<text x="${L}" y="${T+barH+42}" fill="${DIA.ink3}" font-size="12" font-family="ui-sans-serif">development sets the final roast level.</text>`;
  return diaWrap(`${W} ${H}`,g,'The three phases of a roast, start to drop.');
}
// 3. DTR: total time bar with the development portion highlighted + percentage band.
function diaDTR(){
  const W=760,H=188,L=10,R=10,T=24,barH=40,iw=W-L-R;
  const rows=[['Light / Nordic',.12],['Balanced City+',.20],['Dark',.25]];
  let g='';
  rows.forEach((r,i)=>{const y=T+i*46;
    g+=`<rect x="${L}" y="${y}" width="${iw}" height="${barH}" fill="${DIA.mail}" opacity="0.2" rx="3"/>`;
    const dx=L+iw*(1-r[1]);
    g+=`<rect x="${dx.toFixed(0)}" y="${y}" width="${(iw*r[1]).toFixed(0)}" height="${barH}" fill="${DIA.dev}" opacity="0.9" rx="3"/>`;
    g+=`<text x="${L+8}" y="${(y+barH/2+4).toFixed(0)}" fill="${DIA.ink}" font-size="12.5" font-weight="600" font-family="ui-sans-serif">${r[0]}</text>`;
    g+=`<text x="${(dx+iw*r[1]/2).toFixed(0)}" y="${(y+barH/2+4).toFixed(0)}" fill="#1b140e" font-size="12" font-weight="700" text-anchor="middle" font-family="ui-monospace">${Math.round(r[1]*100)}%</text>`;
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
  // labels on right (wrapped, no truncation)
  const leg=[[DIA.hot,'Conduction','Heat from the hot metal drum wall touching the beans.'],[DIA.dry,'Convection','Hot air moving through the bean mass \u2014 the biggest lever on most drums.'],[DIA.accent,'Radiation','Infrared heat radiating from the drum and surfaces.']];
  leg.forEach((l,i)=>{const y=40+i*62;g+=`<rect x="430" y="${y-12}" width="14" height="14" rx="3" fill="${l[0]}"/><text x="452" y="${y}" fill="${DIA.ink}" font-size="14" font-weight="700" font-family="ui-sans-serif">${l[1]}</text><text x="452" fill="${DIA.ink3}" font-size="11.5" font-family="ui-sans-serif">${wrapTspans(l[2],452,y+17,14,34)}</text>`;});
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
  const W=760,H=172,cx1=190,cx2=560,cy=80;
  let g=diaDefs([DIA.dev,DIA.mail,DIA.accent]);
  g=`<defs>${diaArrowMarker(DIA.accent)}</defs>`+g;
  // portafilter (dose)
  g+=`<rect x="${cx1-50}" y="${cy-30}" width="100" height="42" rx="5" fill="url(#${_cid(DIA.dev)})" stroke="${DIA.dev}" stroke-width="1.5" filter="url(#dsoft)"/><text x="${cx1}" y="${cy-4}" fill="#f0e6d8" font-size="20" font-weight="800" text-anchor="middle" font-family="ui-sans-serif">18 g</text><text x="${cx1}" y="${cy+34}" fill="${DIA.ink}" font-size="13" text-anchor="middle" font-family="ui-sans-serif">dose (dry coffee)</text>`;
  // arrow
  g+=`<line x1="${cx1+70}" y1="${cy-8}" x2="${cx2-90}" y2="${cy-8}" stroke="${DIA.accent}" stroke-width="3" marker-end="url(#darr)"/><text x="${(cx1+cx2)/2}" y="${cy-20}" fill="${DIA.accent}" font-size="13" font-weight="600" text-anchor="middle" font-family="ui-sans-serif">25\u201330 s \u00b7 9 bar</text>`;
  // cup (yield)
  g+=`<path d="M${cx2-42} ${cy-32} L${cx2+42} ${cy-32} L${cx2+34} ${cy+18} L${cx2-34} ${cy+18} Z" fill="url(#${_cid(DIA.mail)})" stroke="${DIA.mail}" stroke-width="1.5" filter="url(#dsoft)"/><text x="${cx2}" y="${cy-2}" fill="#f0e6d8" font-size="20" font-weight="800" text-anchor="middle" font-family="ui-sans-serif">36 g</text><text x="${cx2}" y="${cy+40}" fill="${DIA.ink}" font-size="13" text-anchor="middle" font-family="ui-sans-serif">yield (liquid espresso)</text>`;
  g+=`<text x="${W/2}" y="${cy+70}" fill="${DIA.ink3}" font-size="12.5" text-anchor="middle" font-family="ui-sans-serif">A 1:2 ratio \u2014 the modern espresso default. Weigh both, adjust grind to hit the time.</text>`;
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
    g+=lines.map((ln,li)=>`<text x="${lx}" y="${(+ly+li*13-(lines.length-1)*6.5).toFixed(1)}" fill="#fff" font-size="11.5" font-weight="700" text-anchor="middle" dominant-baseline="central" font-family="ui-sans-serif">${ln}</text>`).join('');
  });
  g+=`<circle cx="${cx}" cy="${cy}" r="${rIn}" fill="${DIA.bg}" stroke="${DIA.line}"/><text x="${cx}" y="${cy-6}" fill="${DIA.ink}" font-size="13" font-weight="700" text-anchor="middle" dominant-baseline="central" font-family="ui-sans-serif">Coffee</text><text x="${cx}" y="${cy+10}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" dominant-baseline="central" font-family="ui-sans-serif">start here</text>`;
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
// 11. Processing methods: three cherries showing how much fruit stays on through drying.
function diaProcessing(){
  const W=760,H=210,cy=90;
  const cols=[
    ['Washed','#b8c48a','all fruit removed before drying','clean · bright · transparent',190],
    ['Honey','#d09a4a','skin off, sticky mucilage left on','sweet · rounded · in-between',380],
    ['Natural','#a0433a','whole cherry dried on the bean','fruity · heavy · wild',570],
  ];
  let g=diaDefs(['#9aaf6e','#b8c48a','#d09a4a','#a0433a']);
  cols.forEach(c=>{const cx=c[4];
    // fruit layer amount (behind the seed) with gradient depth
    if(c[0]==='Natural'){g+=`<ellipse cx="${cx}" cy="${cy}" rx="38" ry="46" fill="url(#${_cid(c[1])})"/>`;g+=`<ellipse cx="${cx}" cy="${cy}" rx="38" ry="46" fill="none" stroke="${c[1]}" stroke-width="2.5"/>`;}
    if(c[0]==='Honey'){g+=`<ellipse cx="${cx}" cy="${cy}" rx="31" ry="38" fill="url(#${_cid(c[1])})"/>`;g+=`<ellipse cx="${cx}" cy="${cy}" rx="31" ry="38" fill="none" stroke="${_rgba(c[1],0.5)}" stroke-width="1.5"/>`;}
    // seed with gradient + soft depth
    g+=`<ellipse cx="${cx}" cy="${cy}" rx="26" ry="32" fill="url(#${_cid('#9aaf6e')})" stroke="#5a4632" stroke-width="2" filter="url(#dsoft)"/>`;
    g+=`<path d="M${cx} ${cy-26} C ${cx-6} ${cy-10}, ${cx+6} ${cy+10}, ${cx} ${cy+26}" stroke="#3a2c1e" stroke-width="2" fill="none"/>`;
    g+=`<text x="${cx}" y="${cy+70}" fill="${c[1]}" font-size="16" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${c[0]}</text>`;
    g+=`<text x="${cx}" y="${cy+90}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif">${c[2]}</text>`;
    g+=`<text x="${cx}" y="${cy-56}" fill="${DIA.ink}" font-size="11.5" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">${c[3]}</text>`;
  });
  return diaWrap(`${W} ${H}`,g,'The more fruit that stays on the bean during drying, the sweeter, fruitier, and heavier the cup — and the higher the risk of drying defects.');
}
// 12. Milk steaming: two phases on a temperature track.
function diaMilk(){
  const W=760,H=190,L=30,R=30,iw=W-L-R,cy=70;
  let g=diaDefs([DIA.dry,DIA.mail]);
  // temperature track
  g+=`<line x1="${L}" y1="${cy}" x2="${W-R}" y2="${cy}" stroke="${DIA.line}" stroke-width="3"/>`;
  const X=t=>L+iw*(t/70);
  // stretch zone (cold→~37) and texture zone (37→65)
  g+=`<rect x="${X(4)}" y="${cy-24}" width="${X(37)-X(4)}" height="48" rx="6" fill="url(#${_cid(DIA.dry)})" opacity="0.5" filter="url(#dsoft)"/>`;
  g+=`<rect x="${X(37)}" y="${cy-24}" width="${X(65)-X(37)}" height="48" rx="6" fill="url(#${_cid(DIA.mail)})" opacity="0.6" filter="url(#dsoft)"/>`;
  g+=`<text x="${X(20)}" y="${cy-32}" fill="${DIA.dry}" font-size="13" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">1 · STRETCH</text>`;
  g+=`<text x="${X(20)}" y="${cy+4}" fill="${DIA.ink}" font-size="11" text-anchor="middle" font-family="ui-sans-serif">tip near surface</text>`;
  g+=`<text x="${X(20)}" y="${cy+18}" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">add air · &quot;tss tss&quot;</text>`;
  g+=`<text x="${X(51)}" y="${cy-32}" fill="${DIA.mail}" font-size="13" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">2 · TEXTURE</text>`;
  g+=`<text x="${X(51)}" y="${cy+4}" fill="${DIA.ink}" font-size="11" text-anchor="middle" font-family="ui-sans-serif">wand deep · whirlpool</text>`;
  g+=`<text x="${X(51)}" y="${cy+18}" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">shred bubbles to microfoam</text>`;
  // temp ticks
  [[4,'cold'],[37,'~37°C'],[60,'60°C'],[65,'65°C']].forEach(t=>{g+=`<line x1="${X(t[0])}" y1="${cy+24}" x2="${X(t[0])}" y2="${cy+30}" stroke="${DIA.ink3}"/><text x="${X(t[0])}" y="${cy+44}" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-monospace">${t[1]}</text>`;});
  // danger zone
  g+=`<text x="${X(68)}" y="${cy-32}" fill="${DIA.hot}" font-size="11" text-anchor="middle" font-family="ui-sans-serif">70°C+</text>`;
  g+=`<text x="${W/2}" y="${cy+78}" fill="${DIA.ink3}" font-size="12" text-anchor="middle" font-family="ui-sans-serif">Stretch first while the milk is cold, then texture. Stop by 65°C — past 70°C the milk scalds and the foam collapses.</text>`;
  return diaWrap(`${W} ${H}`,g,'The two phases of steaming milk, on a temperature track.');
}
// 13. Brew method families.
function diaBrewFamilies(){
  const W=760,H=210;
  const fam=[['Percolation','#C9A34E','water passes through once','V60 · Chemex · drip',150],['Immersion','#7a9a6a','grounds steep, then separate','French press · cold brew',380],['Pressure','#d0553a','forced through a puck','espresso · moka',610]];
  let g='';
  fam.forEach(f=>{const cx=f[4],cy=80;
    if(f[0]==='Percolation'){g+=`<path d="M${cx-30} ${cy-30} L${cx+30} ${cy-30} L${cx+16} ${cy+20} L${cx-16} ${cy+20} Z" fill="none" stroke="${f[1]}" stroke-width="2.5"/>`;for(let i=0;i<3;i++)g+=`<line x1="${cx-10+i*10}" y1="${cy+24}" x2="${cx-12+i*10}" y2="${cy+40}" stroke="${f[1]}" stroke-width="2"/>`;}
    if(f[0]==='Immersion'){g+=`<rect x="${cx-26}" y="${cy-28}" width="52" height="58" rx="4" fill="${f[1]}" opacity="0.18" stroke="${f[1]}" stroke-width="2.5"/>`;for(let i=0;i<8;i++)g+=`<circle cx="${cx-16+((i*11)%36)}" cy="${cy-14+((i*9)%34)}" r="2.6" fill="${f[1]}"/>`;}
    if(f[0]==='Pressure'){g+=`<rect x="${cx-26}" y="${cy-20}" width="52" height="22" rx="3" fill="${f[1]}" opacity="0.3" stroke="${f[1]}" stroke-width="2.5"/>`;g+=`<path d="M${cx} ${cy-30} L${cx} ${cy-22}" stroke="${f[1]}" stroke-width="3" marker-end="url(#dp)"/>`;for(let i=0;i<3;i++)g+=`<line x1="${cx-8+i*8}" y1="${cy+6}" x2="${cx-9+i*8}" y2="${cy+24}" stroke="${f[1]}" stroke-width="2"/>`;}
    g+=`<text x="${cx}" y="${cy+64}" fill="${f[1]}" font-size="15" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${f[0]}</text>`;
    g+=`<text x="${cx}" y="${cy+82}" fill="${DIA.ink}" font-size="11.5" text-anchor="middle" font-family="ui-sans-serif">${f[2]}</text>`;
    g+=`<text x="${cx}" y="${cy+98}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif">${f[3]}</text>`;
  });
  g=`<defs><marker id="dp" markerWidth="8" markerHeight="8" refX="4" refY="6" orient="auto"><path d="M0 0 L4 6 L8 0 z" fill="${DIA.hot}"/></marker></defs>`+g;
  return diaWrap(`${W} ${H}`,g,'Almost every brewing method is one of three families — how the water and grounds meet.');
}
// 14. Water balance: hardness vs alkalinity target box.
function diaWater(){
  const W=520,H=360,L=64,R=30,T=30,B=54,iw=W-L-R,ih=H-T-B;
  let g='';
  g+=`<rect x="${L}" y="${T}" width="${iw}" height="${ih}" fill="none" stroke="${DIA.line}"/>`;
  // target sweet-spot box
  const bx=L+iw*0.35,bw=iw*0.4,by=T+ih*0.28,bh=ih*0.4;
  g+=`<rect x="${bx}" y="${by}" width="${bw}" height="${bh}" fill="${DIA.ror}" opacity="0.22" stroke="${DIA.ror}" stroke-width="2" rx="6"/>`;
  g+=`<text x="${(bx+bw/2).toFixed(0)}" y="${(by+bh/2).toFixed(0)}" fill="${DIA.ror}" font-size="13" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">target</text>`;
  g+=`<text x="${(bx+bw/2).toFixed(0)}" y="${(by+bh/2+16).toFixed(0)}" fill="${DIA.ink}" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">balanced water</text>`;
  // axes labels
  g+=`<text x="${(L+iw/2).toFixed(0)}" y="${H-16}" fill="${DIA.ink}" font-size="12.5" text-anchor="middle" font-family="ui-sans-serif">Hardness (minerals that extract) →</text>`;
  g+=`<text x="20" y="${(T+ih/2).toFixed(0)}" fill="${DIA.ink}" font-size="12.5" text-anchor="middle" font-family="ui-sans-serif" transform="rotate(-90 20 ${(T+ih/2).toFixed(0)})">Alkalinity (buffer) →</text>`;
  // corner annotations
  g+=`<text x="${L+8}" y="${T+18}" fill="${DIA.ink3}" font-size="10.5" font-family="ui-sans-serif">flat, chalky</text>`;
  g+=`<text x="${W-R-8}" y="${T+18}" fill="${DIA.ink3}" font-size="10.5" text-anchor="end" font-family="ui-sans-serif">harsh, scaly</text>`;
  g+=`<text x="${L+8}" y="${T+ih-8}" fill="${DIA.ink3}" font-size="10.5" font-family="ui-sans-serif">hollow, sour</text>`;
  g+=`<text x="${W-R-8}" y="${T+ih-8}" fill="${DIA.ink3}" font-size="10.5" text-anchor="end" font-family="ui-sans-serif">bright but sharp</text>`;
  return diaWrap(`${W} ${H}`,g,'Coffee water is a balance of two things: enough hardness to extract flavor, low enough alkalinity to let acidity through.');
}
// 15. Roaster types.
function diaRoasters(){
  const W=760,H=200;
  const t=[['Drum','#B07B3E','rotating metal drum over heat','body · dark roasts · workhorse',150],['Fluid-bed','#C9A34E','beans levitated on hot air','fast · clean · bright roasts',400],['Hybrid','#8A5A34','recirculated air + drum','blends both approaches',630]];
  let g='';
  t.forEach(r=>{const cx=r[4],cy=80;
    if(r[0]==='Drum'){g+=`<circle cx="${cx}" cy="${cy}" r="34" fill="none" stroke="${r[1]}" stroke-width="3"/>`;for(let i=0;i<5;i++){const a=i/5*6.28;g+=`<ellipse cx="${(cx+Math.cos(a)*16).toFixed(0)}" cy="${(cy+Math.sin(a)*14).toFixed(0)}" rx="5" ry="3.5" fill="${r[1]}"/>`;}g+=`<path d="M${cx-40} ${cy+40} q40 14 80 0" stroke="${DIA.hot}" stroke-width="2.5" fill="none"/>`;}
    if(r[0]==='Fluid-bed'){for(let i=0;i<7;i++){g+=`<ellipse cx="${cx-22+((i*13)%44)}" cy="${cy-20+((i*17)%40)}" rx="5" ry="3.5" fill="${r[1]}"/>`;}for(let i=0;i<4;i++)g+=`<path d="M${cx-24+i*16} ${cy+38} q4 -14 0 -28" stroke="${DIA.dry}" stroke-width="2" fill="none" marker-end="url(#ru)"/>`;}
    if(r[0]==='Hybrid'){g+=`<circle cx="${cx}" cy="${cy}" r="30" fill="none" stroke="${r[1]}" stroke-width="2.5" stroke-dasharray="5 4"/>`;g+=`<path d="M${cx-34} ${cy} q34 -30 68 0" stroke="${DIA.dry}" stroke-width="2" fill="none"/>`;for(let i=0;i<4;i++){const a=i/4*6.28;g+=`<ellipse cx="${(cx+Math.cos(a)*13).toFixed(0)}" cy="${(cy+Math.sin(a)*13).toFixed(0)}" rx="4.5" ry="3" fill="${r[1]}"/>`;}}
    g+=`<text x="${cx}" y="${cy+62}" fill="${r[1]}" font-size="15" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${r[0]}</text>`;
    g+=`<text x="${cx}" y="${cy+80}" fill="${DIA.ink}" font-size="11" text-anchor="middle" font-family="ui-sans-serif">${r[2]}</text>`;
    g+=`<text x="${cx}" y="${cy+96}" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">${r[3]}</text>`;
  });
  g=`<defs><marker id="ru" markerWidth="7" markerHeight="7" refX="3" refY="1" orient="auto"><path d="M0 6 L3 0 L6 6 z" fill="${DIA.dry}"/></marker></defs>`+g;
  return diaWrap(`${W} ${H}`,g,'The three main roaster architectures and what each is good at.');
}
// 16. The waves of coffee as a timeline.
function diaWaves(){
  const W=760,H=250,L=20,R=20,T=30,iw=W-L-R,axisY=H-56;
  const waves=[['1st','1800s+','Commodity','cheap · instant · no origin','#8f7c66',.13],
    ['2nd','1960s+','Experience','café · espresso · Starbucks','#B07B3E',.34],
    ['3rd','2000s+','Craft','single origin · light · direct trade','#C9A34E',.62],
    ['4th','now','Science + home','precision · at-home · community','#e0864a',.88]];
  let g=diaDefs(waves.map(w=>w[4]));
  g+=`<line x1="${L}" y1="${axisY}" x2="${W-R}" y2="${axisY}" stroke="${DIA.line}" stroke-width="2"/>`;
  waves.forEach((w,i)=>{const x=L+iw*w[5];const barH=40+i*34;const y=axisY-barH;
    g+=`<rect x="${(x-52).toFixed(0)}" y="${y.toFixed(0)}" width="104" height="${barH}" rx="7" fill="url(#${_cid(w[4])})" stroke="${w[4]}" stroke-width="1.5" filter="url(#dsoft)"/>`;
    g+=`<text x="${x.toFixed(0)}" y="${(y+24).toFixed(0)}" fill="${w[4]}" font-size="20" font-weight="800" text-anchor="middle" font-family="ui-sans-serif">${w[0]}</text>`;
    g+=`<text x="${x.toFixed(0)}" y="${(y+42).toFixed(0)}" fill="${DIA.ink}" font-size="12" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${w[2]}</text>`;
    if(barH>60)g+=`<text x="${x.toFixed(0)}" y="${(y+60).toFixed(0)}" fill="${DIA.ink3}" font-size="10" text-anchor="middle" font-family="ui-sans-serif">${w[3]}</text>`;
    g+=`<circle cx="${x.toFixed(0)}" cy="${axisY}" r="5" fill="${w[4]}"/>`;
    g+=`<text x="${x.toFixed(0)}" y="${axisY+22}" fill="${DIA.ink3}" font-size="11.5" text-anchor="middle" font-family="ui-monospace">${w[1]}</text>`;
  });
  g+=`<text x="${W-R}" y="${axisY+40}" fill="${DIA.ink3}" font-size="11" text-anchor="end" font-family="ui-sans-serif" font-style="italic">rising focus on the bean itself →</text>`;
  return diaWrap(`${W} ${H}`,g,'The waves overlap rather than replace each other — each is a shift in how people relate to coffee.');
}
// 17. Supply chain: cherry to cup with value flow.
function diaSupplyChain(){
  const W=760,H=200,cy=70,L=20;
  const steps=[['Farmer','grows & picks','#7d8f5a'],['Mill','processes green','#95602F'],['Exporter','+ Importer','#B07B3E'],['Roaster','roasts & sells','#8A5A34'],['Café / You','brews','#e0864a']];
  const gap=(W-40)/steps.length;
  let g=diaDefs(steps.map(s=>s[2]));
  g=`<defs>${diaArrowMarker(DIA.ink3)}</defs>`+g;
  steps.forEach((s,i)=>{const cx=L+gap*i+gap/2;
    g+=`<circle cx="${cx.toFixed(0)}" cy="${cy}" r="30" fill="url(#${_cid(s[2])})" stroke="${s[2]}" stroke-width="2" filter="url(#dsoft)"/>`;
    g+=`<text x="${cx.toFixed(0)}" y="${cy-2}" fill="${s[2]}" font-size="13" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${s[0].split(' ')[0]}</text>`;
    g+=`<text x="${cx.toFixed(0)}" y="${cy+50}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif">${s[1]}</text>`;
    if(i<steps.length-1)g+=`<path d="M${(cx+32).toFixed(0)} ${cy} L${(cx+gap-32).toFixed(0)} ${cy}" stroke="${DIA.ink3}" stroke-width="2" marker-end="url(#darr)"/>`;
  });
  g+=`<text x="${W/2}" y="${cy+96}" fill="${DIA.ink}" font-size="12.5" text-anchor="middle" font-family="ui-sans-serif">Every link adds cost and takes margin — historically the farmer did the most work for the least return.</text>`;
  g+=`<text x="${W/2}" y="${cy+116}" fill="${DIA.ink3}" font-size="11.5" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">Direct trade shortens the chain and pushes more value back to the farm.</text>`;
  return diaWrap(`${W} ${H}`,g,'The path from coffee cherry to your cup.');
}
// 18. Blend construction: components → blend.
function diaBlend(){
  const W=760,H=200,cx2=590,cy=80,L=40;
  const comps=[['Base','body & sweetness','#8A5A34',30],['Bright','acidity & lift','#C9A34E',86],['Accent','aromatics','#e0864a',142]];
  let g=diaDefs(['#8A5A34','#C9A34E','#e0864a']);
  comps.forEach(c=>{g+=`<circle cx="${L+30}" cy="${c[3]}" r="16" fill="url(#${_cid(c[2])})" stroke="${c[2]}" stroke-width="2" filter="url(#dsoft)"/>`;
    g+=`<text x="${L+56}" y="${c[3]-2}" fill="${c[2]}" font-size="13.5" font-weight="700" font-family="ui-sans-serif">${c[0]}</text>`;
    g+=`<text x="${L+56}" y="${c[3]+14}" fill="${DIA.ink3}" font-size="11" font-family="ui-sans-serif">${c[1]}</text>`;
    g+=`<path d="M${L+150} ${c[3]} Q${L+260} ${c[3]}, ${cx2-46} ${cy}" stroke="${c[2]}" stroke-width="2" fill="none" opacity="0.55"/>`;
  });
  // the blend cup with depth
  g+=`<circle cx="${cx2}" cy="${cy}" r="40" fill="#000" opacity="0.25" filter="url(#dsoft)"/>`;
  g+=`<circle cx="${cx2}" cy="${cy}" r="40" fill="none" stroke="${DIA.accent}" stroke-width="2.5"/>`;
  g+=`<path d="M${cx2} ${cy-40} A40 40 0 0 1 ${cx2} ${cy+40} Z" fill="#8A5A34" opacity="0.55"/>`;
  g+=`<path d="M${cx2} ${cy-40} A40 40 0 0 0 ${cx2} ${cy+40} Z" fill="#C9A34E" opacity="0.45"/>`;
  g+=`<text x="${cx2}" y="${cy+64}" fill="${DIA.ink}" font-size="14" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">The blend</text>`;
  g+=`<text x="${W/2}" y="${H-16}" fill="${DIA.ink3}" font-size="12" text-anchor="middle" font-family="ui-sans-serif">Dial the ratio by cupping the components together until the cup is balanced.</text>`;
  return diaWrap(`${W} ${H}`,g,'A blend is built from components that each play a role.');
}
// 19. Coffee cherry cross-section (anatomy).
function diaCherry(){
  const W=520,H=340,cx=200,cy=170;
  const layers=[[95,'#c0433a','Skin (exocarp)'],[80,'#d98a3a','Pulp (mesocarp)'],[64,'#e8c27a','Mucilage'],[52,'#d8cbb0','Parchment'],[44,'#cbb89a','Silverskin']];
  let g=diaDefs(['#c0433a','#d98a3a','#e8c27a','#9aaf6e']);
  // soft outer shadow for depth
  g+=`<circle cx="${cx}" cy="${cy}" r="97" fill="#000" opacity="0.28" filter="url(#dsoft)"/>`;
  layers.forEach((l,i)=>{
    g+=`<circle cx="${cx}" cy="${cy}" r="${l[0]}" fill="${l[1]}"/>`;
    // subtle top-light highlight ring on outer layers for volume
    if(i<2)g+=`<ellipse cx="${cx}" cy="${cy-l[0]*0.35}" rx="${l[0]*0.62}" ry="${l[0]*0.32}" fill="#ffffff" opacity="0.09"/>`;
  });
  // two seeds (beans) - flat faces together, with a gentle gradient
  g+=`<path d="M${cx} ${cy-40} A28 40 0 0 0 ${cx} ${cy+40} L${cx-3} ${cy+40} A28 40 0 0 1 ${cx-3} ${cy-40} Z" fill="url(#${_cid('#9aaf6e')})" stroke="#5a4632" stroke-width="1.5"/>`;
  g+=`<path d="M${cx} ${cy-40} A28 40 0 0 1 ${cx} ${cy+40} L${cx+3} ${cy+40} A28 40 0 0 0 ${cx+3} ${cy-40} Z" fill="#8aa05e" stroke="#5a4632" stroke-width="1.5"/>`;
  // labels with leader lines on the right
  const labs=[['#c0433a','Skin (exocarp)','the outer red/yellow layer'],['#d98a3a','Pulp (mesocarp)','sweet fruit flesh'],['#e8c27a','Mucilage','sticky sugary layer'],['#d8cbb0','Parchment','papery seed casing'],['#9aaf6e','Seed = green bean','usually two per cherry']];
  labs.forEach((l,i)=>{const y=40+i*56;g+=`<rect x="330" y="${y-12}" width="13" height="13" rx="3" fill="${l[0]}"/><text x="350" y="${y-1}" fill="#f0e6d8" font-size="13" font-weight="700" font-family="ui-sans-serif">${l[1]}</text><text x="350" y="${y+15}" fill="${DIA.ink3}" font-size="11" font-family="ui-sans-serif">${l[2]}</text>`;});
  return diaWrap(`${W} ${H}`,g,'A coffee cherry in cross-section \u2014 processing removes the outer fruit layers to reach the seed.');
}
// 20. Varietal family tree.
function diaVarTree(){
  const W=760,H=380;
  const cols=['#5f8f4a','#7d9f4a','#C9A34E','#95602F','#B07B3E','#8A5A34','#a0522d','#c86a9a'];
  const node=(x,y,label,col,sub)=>`<g>${diaCard(x-56,y-16,112,(sub?42:32),col,{r:8,shadow:false})}<text x="${x}" y="${y+(sub?-1:5)}" fill="#f0e6d8" font-size="12.5" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${label}</text>${sub?`<text x="${x}" y="${y+15}" fill="${DIA.ink3}" font-size="9.5" text-anchor="middle" font-family="ui-sans-serif">${sub}</text>`:''}</g>`;
  const link=(x1,y1,x2,y2)=>`<path d="M${x1} ${y1} C ${x1} ${(y1+y2)/2}, ${x2} ${(y1+y2)/2}, ${x2} ${y2}" stroke="#7a6a52" stroke-width="1.5" fill="none"/>`;
  let g=diaDefs(cols);
  // root
  g+=node(380,34,'Ethiopian Arabica','#5f8f4a','wild origin, 1000s of types');
  // two founders
  g+=link(380,50,180,104)+link(380,50,560,104);
  g+=node(180,114,'Typica','#7d9f4a','clean, sweet');
  g+=node(560,114,'Bourbon','#C9A34E','sweet, productive');
  // typica children
  g+=link(180,130,110,190)+link(180,130,250,190);
  g+=node(110,200,'Maragogype','#95602F','giant beans');
  g+=node(250,200,'Kona / JBM','#95602F','island coffees');
  // bourbon children
  g+=link(560,130,470,190)+link(560,130,650,190);
  g+=node(470,200,'Caturra','#B07B3E','compact mutation');
  g+=node(650,200,'SL28 / SL34','#B07B3E','Kenya, wine-like');
  // crosses
  g+=link(250,216,330,276)+link(470,216,330,276);
  g+=node(330,286,'Mundo Novo','#8A5A34','Bourbon\u00d7Typica');
  g+=link(470,216,470,276);
  g+=node(470,286,'Catuai','#8A5A34','Caturra\u00d7M.Novo');
  // hybrids branch
  g+=node(645,286,'Catimor','#a0522d','\u00d7 Timor (rust-res.)');
  g+=link(650,216,645,276);
  // geisha standalone
  g+=node(120,300,'Geisha','#c86a9a','Ethiopia\u2192Panama');
  g+=`<text x="120" y="332" fill="${DIA.ink3}" font-size="10" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">its own lineage</text>`;
  return diaWrap(`${W} ${H}`,g,'A simplified Arabica family tree \u2014 most classic varieties branch from Typica and Bourbon (real genetics are messier).');
}
// 21. Pour-over method steps.
function diaPourover(){
  const W=760,H=170,L=20;
  const steps=[['1','Rinse','wet the filter, dump water'],['2','Bloom','2\u00d7 coffee wt, wait 30\u201345s'],['3','Pour','slow, even, to target'],['4','Draw down','let it finish, ~3 min']];
  const gap=(W-40)/steps.length;
  let g=diaDefs(['#C9A34E']);
  steps.forEach((s,i)=>{const cx=L+gap*i+gap/2,cy=64;
    // cone
    g+=`<path d="M${cx-26} ${cy-30} L${cx+26} ${cy-30} L${cx+10} ${cy+14} L${cx-10} ${cy+14} Z" fill="none" stroke="#C9A34E" stroke-width="2.5"/>`;
    if(i>=1)for(let k=0;k<3;k++)g+=`<circle cx="${cx-8+k*8}" cy="${cy-6}" r="2.5" fill="#8A5A34"/>`;
    if(i>=2)g+=`<path d="M${cx} ${cy-40} L${cx} ${cy-30}" stroke="#6a8fb0" stroke-width="2"/>`;
    if(i>=3)for(let k=0;k<2;k++)g+=`<line x1="${cx-4+k*8}" y1="${cy+16}" x2="${cx-5+k*8}" y2="${cy+30}" stroke="#8A5A34" stroke-width="1.6"/>`;
    g+=`<circle cx="${cx}" cy="${cy+52}" r="12" fill="url(#${_cid('#C9A34E')})" stroke="#C9A34E" stroke-width="1.5" filter="url(#dsoft)"/><text x="${cx}" y="${cy+56}" fill="#e6c88a" font-size="12" font-weight="700" text-anchor="middle" font-family="ui-monospace">${s[0]}</text>`;
    g+=`<text x="${cx}" y="${cy+82}" fill="#f0e6d8" font-size="13" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${s[1]}</text>`;
    g+=`<text x="${cx}" y="${cy+98}" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">${s[2]}</text>`;
  });
  return diaWrap(`${W} ${H}`,g,'The universal pour-over sequence, whatever cone you use.');
}
// 22. Cold brew vs iced coffee.
function diaColdBrew(){
  const W=760,H=200,cxA=200,cxB=560,cy=70;
  let g=diaDefs(['#d0553a','#6a8fb0']);
  g=`<defs>${diaArrowMarker('#8a7660')}</defs>`+g;
  // iced coffee (hot then ice)
  g+=`<circle cx="${cxA}" cy="${cy}" r="30" fill="url(#${_cid('#d0553a')})" stroke="#d0553a" stroke-width="2.5" filter="url(#dsoft)"/><text x="${cxA}" y="${cy+5}" fill="#d0553a" font-size="22" text-anchor="middle">\u2668</text>`;
  g+=`<path d="M${cxA+34} ${cy} L${cxA+70} ${cy}" stroke="#8a7660" stroke-width="2" marker-end="url(#darr)"/>`;
  g+=`<text x="${cxA}" y="${cy+52}" fill="#f0e6d8" font-size="14" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">Iced coffee</text>`;
  g+=`<text x="${cxA}" y="${cy+70}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif">brew HOT \u2192 cool over ice</text>`;
  g+=`<text x="${cxA}" y="${cy+86}" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">keeps acidity & aroma</text>`;
  // cold brew (never heated)
  g+=`<circle cx="${cxB}" cy="${cy}" r="30" fill="url(#${_cid('#6a8fb0')})" stroke="#6a8fb0" stroke-width="2.5" filter="url(#dsoft)"/><text x="${cxB}" y="${cy+6}" fill="#6a8fb0" font-size="20" text-anchor="middle">\u2744</text>`;
  g+=`<text x="${cxB}" y="${cy+52}" fill="#f0e6d8" font-size="14" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">Cold brew</text>`;
  g+=`<text x="${cxB}" y="${cy+70}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif">steep COLD 12\u201324 h, never heated</text>`;
  g+=`<text x="${cxB}" y="${cy+86}" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">smooth, low-acid, sweet</text>`;
  g+=`<line x1="${(cxA+cxB)/2}" y1="30" x2="${(cxA+cxB)/2}" y2="150" stroke="${DIA.line}" stroke-dasharray="4 4"/>`;
  return diaWrap(`${W} ${H}`,g,'Same beans, opposite drinks \u2014 heat (or its absence) changes everything.');
}
// 23. Brew troubleshooting decision.
function diaTroubleshoot(){
  const W=760,H=210;
  const cards=[['SOUR / thin','#C9A34E','UNDER-extracted','grind finer \u00b7 hotter \u00b7 longer',150],['BALANCED','#7a9a6a','just right','keep your recipe',380],['BITTER / dry','#d0553a','OVER-extracted','grind coarser \u00b7 cooler \u00b7 shorter',610]];
  let g='';
  // spectrum bar
  g+=`<rect x="40" y="40" width="680" height="14" rx="7" fill="url(#tg)"/>`;
  g=`<defs><linearGradient id="tg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#C9A34E"/><stop offset="0.5" stop-color="#7a9a6a"/><stop offset="1" stop-color="#d0553a"/></linearGradient></defs>`+g;
  cards.forEach(c=>{const cx=c[4];
    g+=`<circle cx="${cx}" cy="47" r="9" fill="${c[1]}" stroke="#1b140e" stroke-width="2"/>`;
    g+=`<text x="${cx}" y="90" fill="${c[1]}" font-size="14" font-weight="800" text-anchor="middle" font-family="ui-sans-serif">${c[0]}</text>`;
    g+=`<text x="${cx}" y="110" fill="#f0e6d8" font-size="12" text-anchor="middle" font-family="ui-sans-serif">${c[2]}</text>`;
    g+=`<text x="${cx}" y="132" fill="#8f7c66" font-size="11.5" text-anchor="middle" font-family="ui-sans-serif">${c[3]}</text>`;
  });
  g+=`<text x="380" y="176" fill="#c9b8a4" font-size="12.5" text-anchor="middle" font-family="ui-sans-serif">Separately: watery/too strong = adjust the RATIO, not the grind.</text>`;
  return diaWrap(`${W} ${H}`,g,'Diagnose the cup, then turn the right dial.');
}
// 24. Milk drink ratios.
function diaMilkDrinks(){
  const W=760,H=230;
  // each drink: [name, size-oz-ish height, espresso frac, milk frac, foam frac]
  const drinks=[['Macchiato',60,.7,.0,.3],['Cortado',70,.45,.45,.1],['Flat White',95,.3,.6,.1],['Cappuccino',100,.33,.34,.33],['Latte',120,.22,.68,.1]];
  const baseY=180, maxH=120, gap=(W-60)/drinks.length;
  let g=diaDefs(['#5A2F16','#e8dcc8']);
  drinks.forEach((dk,i)=>{const cx=30+gap*i+gap/2, w=54, h=dk[1]/120*maxH;
    const top=baseY-h;
    const eF=dk[2],mF=dk[3],fF=dk[4];
    const eH=h*eF, mH=h*mF, fH=h*fF;
    // cup outline with soft depth
    g+=`<rect x="${cx-w/2}" y="${top}" width="${w}" height="${h}" rx="5" fill="#12100c" stroke="#7a6a52" stroke-width="1.5" filter="url(#dsoft)"/>`;
    // espresso (bottom)
    g+=`<rect x="${cx-w/2+2}" y="${baseY-eH}" width="${w-4}" height="${eH-1}" fill="url(#${_cid('#5A2F16')})"/>`;
    // milk (middle)
    g+=`<rect x="${cx-w/2+2}" y="${baseY-eH-mH}" width="${w-4}" height="${mH}" fill="url(#${_cid('#e8dcc8')})"/>`;
    // foam (top) with a subtle top highlight
    g+=`<rect x="${cx-w/2+2}" y="${top+1}" width="${w-4}" height="${fH}" fill="#f5eee0"/>`;
    if(fH>4)g+=`<rect x="${cx-w/2+2}" y="${top+1}" width="${w-4}" height="3" fill="#fff" opacity="0.35"/>`;
    g+=`<text x="${cx}" y="${baseY+18}" fill="#f0e6d8" font-size="12" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${dk[0]}</text>`;
  });
  // legend
  g+=`<rect x="250" y="200" width="12" height="12" fill="#5A2F16"/><text x="266" y="210" fill="${DIA.ink3}" font-size="11" font-family="ui-sans-serif">espresso</text>`;
  g+=`<rect x="360" y="200" width="12" height="12" fill="#e8dcc8"/><text x="376" y="210" fill="${DIA.ink3}" font-size="11" font-family="ui-sans-serif">steamed milk</text>`;
  g+=`<rect x="490" y="200" width="12" height="12" fill="#f5eee0"/><text x="506" y="210" fill="${DIA.ink3}" font-size="11" font-family="ui-sans-serif">foam</text>`;
  return diaWrap(`${W} ${H}`,g,'The same espresso shot, dressed in milk and foam in different proportions.');
}
// 25. Decaf methods.
function diaDecaf(){
  const W=760,H=200;
  const methods=[['Solvent','#B07B3E','MC or EA','EA = \u201csugarcane\u201d, sweet',150],['Swiss Water','#6a8fb0','water + carbon','chemical-free, ~99.9%',380],['CO2','#7a9a6a','supercritical CO2','commercial scale',610]];
  let g=diaDefs(methods.map(m=>m[1]));
  methods.forEach(m=>{const cx=m[4],cy=70;
    g+=`<circle cx="${cx}" cy="${cy}" r="34" fill="url(#${_cid(m[1])})" stroke="${m[1]}" stroke-width="2" filter="url(#dsoft)"/>`;
    // a bean losing caffeine dots
    g+=`<ellipse cx="${cx}" cy="${cy}" rx="15" ry="20" fill="${m[1]}"/><path d="M${cx} ${cy-16} C ${cx-4} ${cy-6}, ${cx+4} ${cy+6}, ${cx} ${cy+16}" stroke="#1b140e" stroke-width="1.4" fill="none"/>`;
    for(let k=0;k<3;k++){const a=k/3*6.28;g+=`<circle cx="${(cx+Math.cos(a)*28).toFixed(0)}" cy="${(cy+Math.sin(a)*24).toFixed(0)}" r="2.5" fill="${m[1]}" opacity="0.6"/>`;}
    g+=`<text x="${cx}" y="${cy+58}" fill="${m[1]}" font-size="14" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${m[0]}</text>`;
    g+=`<text x="${cx}" y="${cy+76}" fill="#f0e6d8" font-size="11.5" text-anchor="middle" font-family="ui-sans-serif">${m[2]}</text>`;
    g+=`<text x="${cx}" y="${cy+92}" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">${m[3]}</text>`;
  });
  g+=`<text x="380" y="${H-6}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">All done to green beans before roasting \u00b7 all target ~97\u201399.9% caffeine removal</text>`;
  return diaWrap(`${W} ${H}`,g,'Three ways to pull caffeine out of green coffee.');
}
// 26. Coffee's spread map (schematic).
function diaCoffeeMap(){
  const W=760,H=220;
  const stops=[['Ethiopia','origin',120,120,'#5f8f4a'],['Yemen','15th c.',210,105,'#C9A34E'],['Europe','17th c.',330,70,'#B07B3E'],['Java','Dutch',560,140,'#8A5A34'],['Americas','French/colonial',430,160,'#a0522d']];
  let g=diaDefs(stops.map(s=>s[4]));
  g=`<defs>${diaArrowMarker('#8a7660')}</defs>`+g;
  g+=`<rect x="0" y="0" width="${W}" height="${H}" fill="#12100c" rx="10"/>`;
  // arrows in sequence
  for(let i=0;i<stops.length-1;i++){const a=stops[i],b=stops[i+1];g+=`<path d="M${a[2]} ${a[3]} Q${(a[2]+b[2])/2} ${Math.min(a[3],b[3])-24} ${b[2]} ${b[3]}" stroke="#8a7660" stroke-width="1.6" fill="none" stroke-dasharray="4 3" marker-end="url(#darr)"/>`;}
  stops.forEach(s=>{
    g+=`<circle cx="${s[2]}" cy="${s[3]}" r="16" fill="url(#${_cid(s[4])})" opacity="0.9"/>`;
    g+=`<circle cx="${s[2]}" cy="${s[3]}" r="7" fill="${s[4]}" stroke="#12100c" stroke-width="2"/>`;
    g+=`<text x="${s[2]}" y="${s[3]-18}" fill="#f0e6d8" font-size="12.5" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${s[0]}</text>`;
    g+=`<text x="${s[2]}" y="${s[3]+26}" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">${s[1]}</text>`;});
  return diaWrap(`${W} ${H}`,g,'Coffee\u2019s rough journey out of Ethiopia \u2014 climate plus colonial trade drew today\u2019s map.');
}
// 27. Caffeine content comparison.
function diaCaffeine(){
  const W=760,H=210,L=140,baseX=L,maxW=520;
  const rows=[['Brewed 8oz',95,'#B07B3E'],['Double espresso',80,'#8A5A34'],['Cold brew (cup)',110,'#6a8fb0'],['Decaf 8oz',7,'#7d8f5a'],['Instant 8oz',62,'#95602F']];
  const mx=120;
  let g='';
  rows.forEach((r,i)=>{const y=30+i*34;const w=r[1]/mx*maxW;
    g+=`<text x="${L-10}" y="${y+14}" fill="#f0e6d8" font-size="12" text-anchor="end" font-family="ui-sans-serif">${r[0]}</text>`;
    g+=`<rect x="${baseX}" y="${y}" width="${w.toFixed(0)}" height="20" rx="4" fill="${r[2]}"/>`;
    g+=`<text x="${baseX+w+8}" y="${y+15}" fill="#c9b8a4" font-size="11.5" font-family="ui-monospace">~${r[1]} mg</text>`;
  });
  g+=`<text x="${baseX}" y="${H-8}" fill="#8f7c66" font-size="11" font-family="ui-sans-serif" font-style="italic">Approximate caffeine per typical serving. A big brewed coffee beats one espresso on total caffeine.</text>`;
  return diaWrap(`${W} ${H}`,g,'Roughly how much caffeine different servings deliver.');
}
// 28. Espresso machine water path.
function diaEspMachine(){
  const W=760,H=210,cy=90;
  const stages=[['Source','tank / line','#6a8fb0',110],['Pump','builds ~9 bar','#B07B3E',300],['Boiler','heats ~93\u00b0C','#d0553a',490],['Group','\u2192 portafilter','#8A5A34',660]];
  let g=diaDefs(stages.map(s=>s[2]));
  g=`<defs>${diaArrowMarker('#6a8fb0')}</defs>`+g;
  stages.forEach((s,i)=>{const cx=s[3];
    g+=diaCard(cx-52,cy-28,104,56,s[2],{r:9,strong:true});
    g+=`<text x="${cx}" y="${cy-4}" fill="${s[2]}" font-size="14" font-weight="700" text-anchor="middle" dominant-baseline="central" font-family="ui-sans-serif">${s[0]}</text>`;
    g+=`<text x="${cx}" y="${cy+14}" fill="#c9b8a4" font-size="10.5" text-anchor="middle" dominant-baseline="central" font-family="ui-sans-serif">${s[1]}</text>`;
    if(i<stages.length-1)g+=`<path d="M${cx+54} ${cy} L${stages[i+1][3]-54} ${cy}" stroke="#8a7660" stroke-width="2.5" marker-end="url(#darr)"/>`;
  });
  g+=`<text x="${W/2}" y="${cy+64}" fill="#f0e6d8" font-size="12.5" text-anchor="middle" font-family="ui-sans-serif">The boiler design (single / heat-exchanger / dual) decides if you can brew and steam at once.</text>`;
  g+=`<text x="${W/2}" y="${cy+82}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">A PID holds the boiler within ~1\u00b0F instead of swinging 5\u201310\u00b0F.</text>`;
  return diaWrap(`${W} ${H}`,g,'Every espresso machine, traced by following the water.');
}
// 29. Taste map: tongue (structure) vs nose (flavor).
function diaTasteMap(){
  const W=760,H=230;
  let g=diaDefs(['#8A5A34','#c86a9a']);
  // tongue side
  g+=`<circle cx="200" cy="90" r="60" fill="url(#${_cid('#8A5A34')})" stroke="#8A5A34" stroke-width="2" filter="url(#dsoft)"/>`;
  g+=`<text x="200" y="60" fill="#f0e6d8" font-size="15" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">TONGUE</text>`;
  g+=`<text x="200" y="78" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif">tastes structure</text>`;
  ['sweet','sour','bitter','salty','umami'].forEach((t,i)=>{g+=`<text x="200" y="${96+i*15}" fill="#c9b8a4" font-size="11.5" text-anchor="middle" font-family="ui-sans-serif">${t}</text>`;});
  // nose side
  g+=`<circle cx="560" cy="90" r="60" fill="url(#${_cid('#c86a9a')})" stroke="#c86a9a" stroke-width="2" filter="url(#dsoft)"/>`;
  g+=`<text x="560" y="60" fill="#f0e6d8" font-size="15" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">NOSE</text>`;
  g+=`<text x="560" y="78" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif">smells flavor (retronasal)</text>`;
  ['berry \u00b7 citrus','floral \u00b7 jasmine','chocolate \u00b7 nut','spice \u00b7 caramel'].forEach((t,i)=>{g+=`<text x="560" y="${98+i*15}" fill="#c9b8a4" font-size="11" text-anchor="middle" font-family="ui-sans-serif">${t}</text>`;});
  // bridge
  g+=`<path d="M262 90 Q380 40 498 90" stroke="#C9A34E" stroke-width="2" fill="none" stroke-dasharray="5 4"/>`;
  g+=`<text x="380" y="48" fill="#C9A34E" font-size="12" font-weight="600" text-anchor="middle" font-family="ui-sans-serif">slurp = both at once</text>`;
  g+=`<text x="${W/2}" y="195" fill="#f0e6d8" font-size="13" text-anchor="middle" font-family="ui-sans-serif">\u201cFlavor\u201d is mostly smell \u2014 which is why coffee tastes flat when you\u2019re congested.</text>`;
  return diaWrap(`${W} ${H}`,g,'What the tongue detects vs what the nose does \u2014 the core of tasting.');
}
// 30. Latte art: sink then surface.
function diaLatteArt(){
  const W=760,H=210;
  const steps=[['1 \u00b7 Sink','pitcher HIGH, thin center stream','#8A5A34',150,'high'],['2 \u00b7 Surface','pitcher CLOSE, more flow','#C9A34E',380,'low'],['3 \u00b7 Draw & cut','move to pattern, cut through','#c9a878',610,'draw']];
  let g='';
  steps.forEach(s=>{const cx=s[3],cupY=110;
    // cup
    g+=`<path d="M${cx-30} ${cupY-26} L${cx+30} ${cupY-26} L${cx+24} ${cupY+22} L${cx-24} ${cupY+22} Z" fill="none" stroke="#7a6a52" stroke-width="2"/>`;
    // crema fill
    g+=`<path d="M${cx-27} ${cupY-20} L${cx+27} ${cupY-20} L${cx+22} ${cupY+18} L${cx-22} ${cupY+18} Z" fill="#8A5A34" opacity="0.6"/>`;
    if(s[4]==='high'){g+=`<path d="M${cx} ${cupY-58} L${cx} ${cupY-24}" stroke="#e8dcc8" stroke-width="2"/>`;}
    if(s[4]==='low'){g+=`<path d="M${cx} ${cupY-34} L${cx} ${cupY-20}" stroke="#e8dcc8" stroke-width="4"/><ellipse cx="${cx}" cy="${cupY-4}" rx="12" ry="8" fill="#f5eee0"/>`;}
    if(s[4]==='draw'){g+=`<ellipse cx="${cx}" cy="${cupY-2}" rx="16" ry="11" fill="#f5eee0"/><path d="M${cx} ${cupY-14} L${cx} ${cupY+14}" stroke="#8A5A34" stroke-width="1.5"/>`;}
    g+=`<text x="${cx}" y="${cupY+46}" fill="${s[2]}" font-size="14" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${s[0]}</text>`;
    g+=`<text x="${cx}" y="${cupY+64}" fill="#8f7c66" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">${s[1]}</text>`;
  });
  g+=`<text x="${W/2}" y="${H-8}" fill="#8f7c66" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">It only works with glossy, bubble-free microfoam \u2014 art is a sign the milk was steamed right.</text>`;
  return diaWrap(`${W} ${H}`,g,'The universal latte-art sequence: sink the milk, then let the foam surface and draw.');
}
// 31. Water recipe: two dials.
function diaWaterRecipe(){
  const W=760,H=210;
  let g=diaDefs(['#B07B3E','#6a8fb0','#7a9a6a']);
  g=`<defs>${diaArrowMarker('#8a7660')}</defs>`+g;
  // distilled base
  g+=`<rect x="40" y="70" width="120" height="60" rx="8" fill="#12100c" stroke="#6a8fb0" stroke-width="2"/><text x="100" y="95" fill="#6a8fb0" font-size="13" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">Distilled</text><text x="100" y="112" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">blank slate</text>`;
  // plus two additions
  g+=`<text x="185" y="105" fill="#f0e6d8" font-size="22" text-anchor="middle">+</text>`;
  g+=diaCard(210,52,150,44,'#B07B3E',{r:8,shadow:false});
  g+=`<text x="285" y="72" fill="#B07B3E" font-size="12.5" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">Hardness (Mg/Ca)</text><text x="285" y="88" fill="${DIA.ink3}" font-size="10" text-anchor="middle" font-family="ui-sans-serif">extracts flavor & body</text>`;
  g+=diaCard(210,104,150,44,'#6a8fb0',{r:8,shadow:false});
  g+=`<text x="285" y="124" fill="#6a8fb0" font-size="12.5" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">Buffer (bicarbonate)</text><text x="285" y="140" fill="${DIA.ink3}" font-size="10" text-anchor="middle" font-family="ui-sans-serif">tames acidity</text>`;
  // arrow to target
  g+=`<path d="M370 100 L440 100" stroke="#8a7660" stroke-width="2.5" marker-end="url(#darr)"/>`;
  g+=`<circle cx="560" cy="100" r="56" fill="url(#${_cid('#7a9a6a')})" stroke="#7a9a6a" stroke-width="2" filter="url(#dsoft)"/><text x="560" y="86" fill="#7a9a6a" font-size="14" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">Target</text><text x="560" y="104" fill="#f0e6d8" font-size="11.5" text-anchor="middle" font-family="ui-sans-serif">~150 mg/L TDS</text><text x="560" y="120" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">hardness>alkalinity</text>`;
  g+=`<text x="${W/2}" y="${H-8}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">Enough hardness to extract, low enough alkalinity to let acidity through. Lock a recipe and keep it constant.</text>`;
  return diaWrap(`${W} ${H}`,g,'Building brewing water from distilled: two dials, hardness and buffer.');
}
// 32. Conical vs flat burrs.
function diaGrinder(){
  const W=760,H=230,cxA=200,cxB=560,cy=95;
  let g=diaDefs(['#B07B3E','#C9A34E']);
  g=`<defs>${diaArrowMarker('#8A5A34')}</defs>`+g;
  // conical: cone inside ring (side view)
  g+=`<text x="${cxA}" y="30" fill="#f0e6d8" font-size="15" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">Conical</text>`;
  g+=`<path d="M${cxA-46} ${cy-30} L${cxA-30} ${cy-30} L${cxA-30} ${cy+30} L${cxA-46} ${cy+30}" fill="none" stroke="#B07B3E" stroke-width="3"/>`;
  g+=`<path d="M${cxA+46} ${cy-30} L${cxA+30} ${cy-30} L${cxA+30} ${cy+30} L${cxA+46} ${cy+30}" fill="none" stroke="#B07B3E" stroke-width="3"/>`;
  g+=`<path d="M${cxA} ${cy-34} L${cxA-22} ${cy+30} L${cxA+22} ${cy+30} Z" fill="url(#${_cid('#B07B3E')})" stroke="#B07B3E" stroke-width="1.5" filter="url(#dsoft)"/>`;
  // beans falling
  for(let k=0;k<3;k++)g+=`<circle cx="${cxA-8+k*8}" cy="${cy-42}" r="3" fill="#8A5A34"/>`;
  g+=`<text x="${cxA}" y="${cy+58}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif">gravity-fed \u00b7 cooler \u00b7 low retention</text>`;
  g+=`<text x="${cxA}" y="${cy+74}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif">forgiving \u00b7 punchy, textured shot</text>`;
  // flat: two discs (side view)
  g+=`<text x="${cxB}" y="30" fill="#f0e6d8" font-size="15" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">Flat</text>`;
  g+=`<rect x="${cxB-40}" y="${cy-26}" width="80" height="10" rx="2" fill="url(#${_cid('#C9A34E')})" stroke="${_rgba('#C9A34E',0.7)}" stroke-width="1" filter="url(#dsoft)"/>`;
  g+=`<rect x="${cxB-40}" y="${cy+16}" width="80" height="10" rx="2" fill="url(#${_cid('#C9A34E')})" stroke="${_rgba('#C9A34E',0.7)}" stroke-width="1" filter="url(#dsoft)"/>`;
  // centrifugal arrows
  g+=`<path d="M${cxB} ${cy-6} L${cxB} ${cy+6}" stroke="#8A5A34" stroke-width="2"/>`;
  g+=`<path d="M${cxB-6} ${cy} L${cxB-34} ${cy}" stroke="#8A5A34" stroke-width="1.6" marker-end="url(#darr)"/><path d="M${cxB+6} ${cy} L${cxB+34} ${cy}" stroke="#8A5A34" stroke-width="1.6" marker-end="url(#darr)"/>`;
  g+=`<text x="${cxB}" y="${cy+58}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif">centrifugal \u00b7 hotter \u00b7 uniform (unimodal)</text>`;
  g+=`<text x="${cxB}" y="${cy+74}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif">clarity \u00b7 espresso standard</text>`;
  g+=`<line x1="380" y1="55" x2="380" y2="150" stroke="${DIA.line}" stroke-dasharray="4 4"/>`;
  return diaWrap(`${W} ${H}`,g,'The two burr geometries \u2014 both crush to uniform particles, but with different character.');
}
// 33. Puck prep sequence + channeling.
function diaPuckPrep(){
  const W=760,H=210;
  const steps=[['Dose','into dry basket'],['WDT','stir out clumps'],['Level','flatten the bed'],['Tamp','straight & level']];
  const gap=(W-40)/steps.length;
  let g=diaDefs(['#B07B3E']);
  steps.forEach((s,i)=>{const cx=20+gap*i+gap/2,cy=70;
    // basket
    g+=`<path d="M${cx-28} ${cy-24} L${cx+28} ${cy-24} L${cx+22} ${cy+16} L${cx-22} ${cy+16} Z" fill="none" stroke="#7a6a52" stroke-width="2"/>`;
    if(i===0){for(let k=0;k<9;k++)g+=`<circle cx="${cx-16+(k%3)*16+(k>2?4:0)}" cy="${cy-14+Math.floor(k/3)*10}" r="2.6" fill="#8A5A34"/>`;}
    if(i===1){g+=`<path d="M${cx-14} ${cy-12} L${cx+14} ${cy+8}" stroke="#C9A34E" stroke-width="1.5"/><path d="M${cx+14} ${cy-12} L${cx-14} ${cy+8}" stroke="#C9A34E" stroke-width="1.5"/>`;for(let k=0;k<6;k++)g+=`<circle cx="${cx-16+k*7}" cy="${cy-2+((k%2)?4:-2)}" r="2.4" fill="#8A5A34"/>`;}
    if(i>=2){g+=`<rect x="${cx-22}" y="${cy-6}" width="44" height="20" fill="${_rgba('#8A5A34',0.6)}"/>`;}
    if(i===3){g+=`<rect x="${cx-16}" y="${cy-30}" width="32" height="10" rx="2" fill="#c9a878"/><path d="M${cx} ${cy-20} L${cx} ${cy-8}" stroke="#c9a878" stroke-width="3"/>`;}
    g+=`<circle cx="${cx}" cy="${cy+40}" r="12" fill="url(#${_cid('#B07B3E')})" stroke="#B07B3E" stroke-width="1.5" filter="url(#dsoft)"/><text x="${cx}" y="${cy+44}" fill="#e6c88a" font-size="12" font-weight="700" text-anchor="middle" font-family="ui-monospace">${i+1}</text>`;
    g+=`<text x="${cx}" y="${cy+68}" fill="#f0e6d8" font-size="13" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${s[0]}</text>`;
    g+=`<text x="${cx}" y="${cy+84}" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">${s[1]}</text>`;
  });
  g+=`<text x="${W/2}" y="${H-6}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">All to make one uniform bed \u2014 so water can\u2019t channel through weak spots.</text>`;
  return diaWrap(`${W} ${H}`,g,'The puck-prep sequence, each step fighting channeling.');
}
// 34. Freshness curve over time.
function diaStaling(){
  const W=760,H=230,L=60,R=W-30,T=30,B=170;
  let g='';
  // axes
  g+=`<line x1="${L}" y1="${B}" x2="${R}" y2="${B}" stroke="${DIA.line}" stroke-width="1.5"/>`;
  g+=`<line x1="${L}" y1="${T}" x2="${L}" y2="${B}" stroke="${DIA.line}" stroke-width="1.5"/>`;
  // freshness curve: rises (degassing), plateaus, slow decline
  g+=`<path d="M${L} ${B-20} C ${L+70} ${T+30}, ${L+120} ${T+18}, ${L+200} ${T+20} C ${L+330} ${T+24}, ${L+430} ${B-60}, ${R} ${B-95}" fill="none" stroke="#C9A34E" stroke-width="3"/>`;
  // zones
  const zx=[[L,L+90,'too fresh','gassy, uneven'],[L+95,L+290,'peak window','best','#7a9a6a'],[L+300,R,'slow decline','oxidizing']];
  zx.forEach(z=>{const mid=(z[0]+z[1])/2;g+=`<text x="${mid}" y="${B+18}" fill="${z[4]||'#8f7c66'}" font-size="11.5" font-weight="${z[4]?'700':'400'}" text-anchor="middle" font-family="ui-sans-serif">${z[2]}</text><text x="${mid}" y="${B+32}" fill="#8f7c66" font-size="10" text-anchor="middle" font-family="ui-sans-serif">${z[3]}</text>`;});
  // peak band highlight
  g+=`<rect x="${L+95}" y="${T}" width="${195}" height="${B-T}" fill="#7a9a6a" opacity="0.08"/>`;
  g+=`<text x="${L-8}" y="${T+6}" fill="${DIA.ink3}" font-size="10.5" text-anchor="end" font-family="ui-sans-serif">flavor</text>`;
  g+=`<text x="${R}" y="${B+18}" fill="${DIA.ink3}" font-size="10.5" text-anchor="end" font-family="ui-sans-serif">days since roast \u2192</text>`;
  g+=`<text x="${L+10}" y="${T+2}" fill="#8f7c66" font-size="10" font-family="ui-sans-serif"></text>`;
  return diaWrap(`${W} ${H}`,g,'Roasted coffee climbs as it degasses, plateaus at its peak, then slowly declines \u2014 whole beans hold the plateau for weeks.');
}
// 35. Acid map: each acid and its flavor.
function diaAcidMap(){
  const W=760,H=250,L=150,baseX=L;
  // [acid, flavor, intensity-of-brightness 0-1, color]
  const acids=[['Citric','lemon, orange \u2014 juicy',0.9,'#d9c02e'],['Malic','green apple, pear \u2014 tart',0.8,'#8fbf3a'],['Phosphoric','sparkling, cola-like',0.85,'#e0843a'],['Acetic','vinegar \u2014 winey/sour',0.5,'#c0433a'],['Lactic','creamy, buttery body',0.35,'#e8dcc8'],['Quinic','stale, hot-plate sour',0.3,'#95602F'],['Chlorogenic','bitter, astringent',0.25,'#6E3E1E']];
  const maxW=440,rowH=27;
  let g='';
  g+=`<text x="${L-10}" y="26" fill="#8f7c66" font-size="11" text-anchor="end" font-family="ui-monospace">ACID</text>`;
  g+=`<text x="${baseX}" y="26" fill="#8f7c66" font-size="11" font-family="ui-monospace">FLAVOR & PERCEIVED BRIGHTNESS</text>`;
  acids.forEach((a,i)=>{const y=44+i*rowH;const w=a[2]*maxW;
    g+=`<text x="${L-10}" y="${y+13}" fill="#f0e6d8" font-size="12.5" font-weight="650" text-anchor="end" font-family="ui-sans-serif">${a[0]}</text>`;
    g+=`<rect x="${baseX}" y="${y+2}" width="${w.toFixed(0)}" height="18" rx="4" fill="${a[3]}" opacity="0.85"/>`;
    g+=`<text x="${baseX+8}" y="${y+15}" fill="#1b140e" font-size="11" font-weight="600" font-family="ui-sans-serif">${a[1]}</text>`;
  });
  g+=`<text x="${baseX}" y="${H-8}" fill="#8f7c66" font-size="11" font-family="ui-sans-serif" font-style="italic">Bar length \u2248 how much each drives pleasant brightness. Top three = the 'juicy' bright acids.</text>`;
  return diaWrap(`${W} ${H}`,g,'The main acids in coffee and the sensations they create.');
}
// 36. Espresso dial ring: recipe + fixes.
function diaDialRing(){
  const W=760,H=250,cx=210,cy=125;
  let g=diaDefs(['#5A2F16','#C9A34E','#d0553a']);
  // central recipe (glowing)
  g+=`<circle cx="${cx}" cy="${cy}" r="78" fill="url(#${_cid('#5A2F16')})" stroke="#5A2F16" stroke-width="3" filter="url(#dsh)"/>`;
  g+=`<circle cx="${cx}" cy="${cy}" r="78" fill="none" stroke="${_rgba('#C9A34E',0.25)}" stroke-width="6"/>`;
  g+=`<text x="${cx}" y="${cy-30}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-monospace">RECIPE</text>`;
  g+=`<text x="${cx}" y="${cy-8}" fill="#f0e6d8" font-size="17" font-weight="700" text-anchor="middle" dominant-baseline="central" font-family="ui-monospace">18g \u2192 36g</text>`;
  g+=`<text x="${cx}" y="${cy+14}" fill="#c9b8a4" font-size="13" text-anchor="middle" dominant-baseline="central" font-family="ui-sans-serif">1:2 ratio</text>`;
  g+=`<text x="${cx}" y="${cy+34}" fill="#C9A34E" font-size="13" text-anchor="middle" dominant-baseline="central" font-family="ui-monospace">~27\u201330 s</text>`;
  g+=`<text x="${cx}" y="${cy-88}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif">dose in</text>`;
  // fixes panel with gradient cards
  const fixes=[['Too SOUR','#C9A34E','grind finer','longer ratio \u00b7 hotter'],['Too BITTER','#d0553a','grind coarser','shorter ratio \u00b7 cooler']];
  fixes.forEach((f,i)=>{const y=70+i*70;
    g+=diaCard(380,y,350,56,f[1],{r:10});
    g+=`<text x="398" y="${y+23}" fill="${f[1]}" font-size="14" font-weight="800" font-family="ui-sans-serif">${f[0]}</text>`;
    g+=`<text x="398" y="${y+42}" fill="#f0e6d8" font-size="12.5" font-family="ui-sans-serif">${f[2]} \u00b7 <tspan fill="${DIA.ink3}">${f[3]}</tspan></text>`;
  });
  g+=`<text x="555" y="222" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">Grind is the master dial. Change one thing, taste, repeat.</text>`;
  return diaWrap(`${W} ${H}`,g,'The espresso recipe and how to steer it by taste.');
}
// 37. Milk steaming: stretch then texture.
function diaMilkStretch(){
  const W=760,H=230;
  let g=diaDefs(['#e8dcc8','#8A5A34','#C9A34E']);
  g=`<defs>${diaArrowMarker('#8a7660')}<marker id="ams" markerWidth="7" markerHeight="7" refX="4" refY="3" orient="auto"><path d="M0 0 L5 3 L0 6 z" fill="#fff"/></marker></defs>`+g;
  // phase 1: stretch
  const cxA=210,cxB=560,cy=100;
  [['1 \u00b7 STRETCH','add air EARLY (cold)','tip near surface \u00b7 \u201ctsss\u201d','#8A5A34',cxA,'air'],
   ['2 \u00b7 TEXTURE','spin into microfoam','tip submerged \u00b7 whirlpool','#C9A34E',cxB,'spin']].forEach(p=>{
    const cx=p[4];
    // pitcher
    g+=`<path d="M${cx-34} ${cy-38} L${cx+30} ${cy-38} L${cx+24} ${cy+34} L${cx-28} ${cy+34} Z" fill="#12100c" stroke="#7a6a52" stroke-width="2" filter="url(#dsoft)"/>`;
    g+=`<path d="M${cx+30} ${cy-30} L${cx+50} ${cy-24} L${cx+42} ${cy-12} L${cx+26} ${cy-18} Z" fill="none" stroke="#7a6a52" stroke-width="2"/>`;
    // milk
    g+=`<path d="M${cx-30} ${cy-6} L${cx+26} ${cy-6} L${cx+22} ${cy+30} L${cx-26} ${cy+30} Z" fill="url(#${_cid('#e8dcc8')})" opacity="0.9"/>`;
    if(p[5]==='air'){g+=`<ellipse cx="${cx-2}" cy="${cy-10}" rx="24" ry="6" fill="#f5eee0"/>`;for(let k=0;k<4;k++)g+=`<circle cx="${cx-16+k*10}" cy="${cy-2}" r="2" fill="#fff" opacity="0.7"/>`;
      g+=`<path d="M${cx} ${cy-52} L${cx} ${cy-14}" stroke="#c9b8a4" stroke-width="3"/>`;}
    if(p[5]==='spin'){g+=`<path d="M${cx-16} ${cy+6} A16 8 0 1 0 ${cx+16} ${cy+6}" fill="none" stroke="#fff" stroke-width="1.6" opacity="0.7" marker-end="url(#ams)"/>`;
      g+=`<path d="M${cx-4} ${cy-46} L${cx-4} ${cy+2}" stroke="#c9b8a4" stroke-width="3"/>`;}
    g+=`<text x="${cx}" y="${cy+58}" fill="${p[3]}" font-size="14" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${p[0]}</text>`;
    g+=`<text x="${cx}" y="${cy+76}" fill="#f0e6d8" font-size="12" text-anchor="middle" font-family="ui-sans-serif">${p[1]}</text>`;
    g+=`<text x="${cx}" y="${cy+92}" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">${p[2]}</text>`;
  });
  g+=`<path d="M300 ${cy} L470 ${cy}" stroke="#8a7660" stroke-width="1.5" stroke-dasharray="5 4" marker-end="url(#darr)"/>`;
  g+=`<text x="${W/2}" y="${H-6}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">Stretch only while cold, then stop adding air and spin. Target ~55\u201365\u00b0C \u2014 past ~70\u00b0C it scalds.</text>`;
  return diaWrap(`${W} ${H}`,g,'The two phases of steaming milk, in order.');
}
// 38. Maintenance cadence: what to do how often.
function diaMaintenance(){
  const W=760,H=250,L=20;
  const cols=[
    ['DAILY','#C9A34E',['Wipe & purge steam wand','Water backflush','Rinse portafilter/basket']],
    ['WEEKLY','#B07B3E',['Detergent backflush','Brush the group head','Soak basket in cleaner']],
    ['MONTHLY','#8A5A34',['Brush grinder burrs','Clean shower screen','Check water hardness']],
    ['PERIODIC','#6E3E1E',['Descale (by hardness)','Grinder pellets (few mo.)','Replace gasket / burrs']],
  ];
  const cw=(W-L*2)/cols.length, gap=12;
  let g=diaDefs(cols.map(c=>c[1]));
  cols.forEach((c,i)=>{const x=L+i*cw;
    g+=diaCard(x+gap/2,10,cw-gap,H-40,c[1],{r:12});
    g+=`<text x="${x+cw/2}" y="36" fill="${c[1]}" font-size="14" font-weight="800" text-anchor="middle" font-family="ui-monospace" letter-spacing="1">${c[0]}</text>`;
    g+=`<line x1="${x+gap/2+12}" y1="46" x2="${x+cw-gap/2-12}" y2="46" stroke="${_rgba(c[1],0.35)}" stroke-width="1"/>`;
    c[2].forEach((t,j)=>{const yy=68+j*44;
      g+=`<circle cx="${x+gap/2+18}" cy="${yy}" r="3.5" fill="${c[1]}"/>`;
      const words=t.split(' ');let line='',lines=[],max=15;
      words.forEach(w=>{if((line+' '+w).trim().length>max){lines.push(line.trim());line=w;}else line+=' '+w;});
      if(line.trim())lines.push(line.trim());
      lines.forEach((ln,k)=>{g+=`<text x="${x+gap/2+30}" y="${yy+4+k*13}" fill="#f0e6d8" font-size="11.5" font-family="ui-sans-serif">${ln}</text>`;});
    });
  });
  g+=`<text x="${W/2}" y="${H-8}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">A neglected machine ruins good coffee before you see it \u2014 oils go rancid in days, scale drifts temperature.</text>`;
  return diaWrap(`${W} ${H}`,g,'The espresso maintenance cadence \u2014 small habits protect flavor and the machine.');
}
// 39. Aroma compound families and their smells.
function diaAromaChem(){
  const W=760,H=250,cx=175,cy=125;
  const fams=[['Pyrazines','nutty, roasty','#8A5A34'],['Furans','sweet, caramel','#C9A34E'],['Aldehydes','fruity, malty','#b0703a'],['Ketones','buttery','#d0a850'],['Sulfur cmpds','tiny but huge','#7a6a52']];
  let g=diaDefs(['#c98a3a',...fams.map(f=>f[2])]);
  // center: heat -> reactions, glowing radial
  g+=`<circle cx="${cx}" cy="${cy}" r="62" fill="url(#${_cid('#c98a3a')})" stroke="#c98a3a" stroke-width="3" filter="url(#dsh)"/>`;
  g+=`<circle cx="${cx}" cy="${cy}" r="62" fill="none" stroke="${_rgba('#c98a3a',0.35)}" stroke-width="8"/>`;
  g+=`<text x="${cx}" y="${cy-16}" fill="#f0e6d8" font-size="14" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">Green bean</text>`;
  g+=`<text x="${cx}" y="${cy+2}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif">+ HEAT \u2192</text>`;
  g+=`<text x="${cx}" y="${cy+20}" fill="#C9A34E" font-size="11.5" text-anchor="middle" font-family="ui-monospace">Maillard</text>`;
  g+=`<text x="${cx}" y="${cy+35}" fill="#C9A34E" font-size="11.5" text-anchor="middle" font-family="ui-monospace">caramelize</text>`;
  const rx=440;
  fams.forEach((f,i)=>{const y=28+i*44;
    g+=`<line x1="${cx+62}" y1="${cy}" x2="${rx-14}" y2="${y+17}" stroke="${f[2]}" stroke-width="1.6" opacity="0.55"/>`;
    g+=`<circle cx="${rx-14}" cy="${y+17}" r="2.5" fill="${f[2]}"/>`;
    g+=diaCard(rx,y,290,34,f[2],{r:8,shadow:false});
    g+=`<text x="${rx+14}" y="${y+15}" fill="#f0e6d8" font-size="13" font-weight="700" font-family="ui-sans-serif">${f[0]}</text>`;
    g+=`<text x="${rx+14}" y="${y+29}" fill="${DIA.ink3}" font-size="11" font-family="ui-sans-serif">${f[1]}</text>`;
  });
  g+=`<text x="${W/2}" y="${H-6}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">Raw green coffee has almost no flavor \u2014 heat creates 800+ aroma compounds. Roast level = how far the reactions run.</text>`;
  return diaWrap(`${W} ${H}`,g,'How roasting turns a flavorless seed into hundreds of aroma compounds.');
}
// 40. SCA certification pathway.
function diaScaPath(){
  const W=760,H=250;
  let g=diaDefs(['#5a8a9a','#C9A34E','#8fbf3a','#c86a4a']);
  g=`<defs>${diaArrowMarker('#8a7660')}</defs>`+g;
  // Intro card at left
  g+=diaCard(20,95,120,60,'#5a8a9a',{r:10,strong:true});
  g+=`<text x="80" y="120" fill="#f0e6d8" font-size="12.5" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">Intro to</text>`;
  g+=`<text x="80" y="136" fill="#f0e6d8" font-size="12.5" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">Coffee</text>`;
  g+=`<text x="80" y="150" fill="${DIA.ink3}" font-size="9.5" text-anchor="middle" font-family="ui-sans-serif">start here</text>`;
  // 5 modules
  const mods=['Barista','Brewing','Green Coffee','Roasting','Sensory'];
  mods.forEach((m,i)=>{const y=15+i*46;
    g+=`<line x1="140" y1="125" x2="196" y2="${y+16}" stroke="#5a8a9a" stroke-width="1.3" opacity="0.45"/>`;
    g+=diaCard(200,y,150,34,'#5a8a9a',{r:8,shadow:false});
    g+=`<text x="212" y="${y+22}" fill="#f0e6d8" font-size="13" font-weight="650" font-family="ui-sans-serif">${m}</text>`;
  });
  // levels bracket
  g+=`<text x="425" y="20" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-monospace">EACH AT 3 LEVELS</text>`;
  ['Foundation','Intermediate','Professional'].forEach((lv,i)=>{const yy=52+i*52;
    g+=diaCard(375,yy,100,34,'#C9A34E',{r:8,shadow:false});
    g+=`<text x="425" y="${yy+21}" fill="#f0e6d8" font-size="11.5" font-weight="600" text-anchor="middle" font-family="ui-sans-serif">${lv}</text>`;
  });
  g+=`<path d="M478 125 L520 125" stroke="#8a7660" stroke-width="1.6" marker-end="url(#darr)"/>`;
  // Diploma + Q
  g+=diaCard(525,60,215,55,'#8fbf3a',{r:10,strong:true});
  g+=`<text x="632" y="82" fill="#f0e6d8" font-size="13" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">SCA Skills Diploma</text>`;
  g+=`<text x="632" y="100" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">earn points across modules</text>`;
  g+=diaCard(525,130,215,55,'#c86a4a',{r:10,strong:true});
  g+=`<text x="632" y="152" fill="#f0e6d8" font-size="13" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">Q Grader (CQI)</text>`;
  g+=`<text x="632" y="170" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">coffee's 'sommelier' license</text>`;
  g+=`<text x="${W/2}" y="${H-8}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">Modular & flexible \u2014 start anywhere, build toward job-ready diplomas or the Q license.</text>`;
  return diaWrap(`${W} ${H}`,g,'The main coffee certification pathways.');
}
// 41. Coffee cherry anatomy -> byproducts.
function diaCherryByproduct(){
  const W=760,H=230,cx=160,cy=110;
  let g=diaDefs(['#c0433a']);
  g=`<defs>${diaArrowMarker('#8a7660')}</defs>`+g;
  // cherry cross-section (concentric) with soft depth
  const layers=[['#c0433a',52],['#d98a4a',40],['#e8dcc8',26]];
  g+=`<circle cx="${cx}" cy="${cy}" r="54" fill="#000" opacity="0.3" filter="url(#dsoft)"/>`;
  layers.forEach(l=>{g+=`<circle cx="${cx}" cy="${cy}" r="${l[1]}" fill="${l[0]}" opacity="0.92"/>`;});
  g+=`<circle cx="${cx}" cy="${cy}" r="15" fill="#6E3E1E"/>`;
  g+=`<line x1="${cx}" y1="${cy-15}" x2="${cx}" y2="${cy+15}" stroke="#e8dcc8" stroke-width="1.5"/>`;
  // ring labels (small)
  g+=`<text x="${cx-38}" y="${cy-40}" fill="#e8dcc8" font-size="8.5" font-family="ui-sans-serif">skin</text>`;
  g+=`<text x="${cx+20}" y="${cy-30}" fill="#4a3018" font-size="8" font-family="ui-sans-serif">pulp</text>`;
  // labels
  g+=`<text x="${cx}" y="${cy+78}" fill="#f0e6d8" font-size="13" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">The coffee cherry</text>`;
  g+=`<text x="${cx}" y="${cy+94}" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">a fruit: seeds (beans) inside sweet pulp</text>`;
  // arrow to products
  g+=`<path d="M228 ${cy} L280 ${cy}" stroke="#8a7660" stroke-width="1.6" marker-end="url(#darr)"/>`;
  g+=`<text x="300" y="26" fill="${DIA.ink3}" font-size="10.5" font-family="ui-monospace">THE 'WASTE' BECOMES:</text>`;
  const prods=[['Cascara','dried husk \u2192 fruity tea'],['Coffee flour','milled cherry, high-fiber baking'],['Fruit extracts','antioxidant supplements'],['Compost / biogas','closes the loop']];
  prods.forEach((p,i)=>{const y=40+i*42;
    g+=diaCard(300,y,440,34,'#c0433a',{r:8,shadow:false});
    g+=`<text x="312" y="${y+15}" fill="#f0e6d8" font-size="12.5" font-weight="700" font-family="ui-sans-serif">${p[0]}</text>`;
    g+=`<text x="312" y="${y+29}" fill="${DIA.ink3}" font-size="11" font-family="ui-sans-serif">${p[1]}</text>`;
  });
  g+=`<text x="${W/2}" y="${H-6}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">Using the whole fruit reduces pollution from discarded pulp and adds farmer income.</text>`;
  return diaWrap(`${W} ${H}`,g,'The coffee cherry and the products made from its fruit.');
}
// 42. Coffee vs tea comparison.
function diaTeaCoffee(){
  const W=760,H=230;
  const cols=[['COFFEE','#6E3E1E',180,['Roasted SEED of Coffea fruit','~95 mg caffeine / cup','Bolder, heavier, immediate','Morning & productivity']],
              ['TEA','#7a9a6a',560,['Dried LEAF of Camellia sinensis','~30\u201350 mg caffeine / cup','Lighter, L-theanine = steady','All-day & calm']]];
  let g=diaDefs(['#6E3E1E','#7a9a6a']);
  cols.forEach(c=>{const cx=c[2];
    g+=`<circle cx="${cx}" cy="46" r="27" fill="url(#${_cid(c[1])})" stroke="${c[1]}" stroke-width="2" filter="url(#dsh)"/>`;
    g+=`<circle cx="${cx}" cy="46" r="27" fill="none" stroke="${_rgba(c[1],0.4)}" stroke-width="6"/>`;
    g+=`<text x="${cx}" y="51" fill="#f0e6d8" font-size="14" font-weight="800" text-anchor="middle" font-family="ui-sans-serif" letter-spacing="1">${c[0]}</text>`;
    c[3].forEach((t,i)=>{const y=92+i*33;
      g+=`<text x="${cx}" y="${y}" fill="#c9b8a4" font-size="12" text-anchor="middle" font-family="ui-sans-serif">${t}</text>`;
    });
  });
  // vs divider
  g+=`<line x1="380" y1="30" x2="380" y2="200" stroke="${DIA.line}" stroke-dasharray="5 5"/>`;
  g+=`<circle cx="380" cy="46" r="16" fill="#160e08" stroke="${DIA.ink3}" stroke-width="1.2" filter="url(#dsoft)"/>`;
  g+=`<text x="380" y="51" fill="${DIA.ink3}" font-size="12" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">vs</text>`;
  g+=`<text x="${W/2}" y="${H-8}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">Parallel crafts \u2014 both obsess over terroir, processing, ritual, and brewing precision. Complements, not competitors.</text>`;
  return diaWrap(`${W} ${H}`,g,'The world\u2019s two great caffeinated drinks, compared.');
}
// 43. Espresso machine boiler configurations.
function diaMachTypes(){
  const W=760,H=250;
  const cols=[
    ['Single boiler','#8A5A34',130,'one boiler:\nbrew OR steam','switch & wait'],
    ['Heat exchanger','#B07B3E',380,'steam boiler +\nbrew pipe through it','flush to cool'],
    ['Dual boiler','#C9A34E',630,'two boilers:\nbrew + steam','direct, no wait'],
  ];
  let g=diaDefs(['#8A5A34','#B07B3E','#C9A34E','#5a8a9a','#c0433a']);
  cols.forEach((c,i)=>{const cx=c[2],by=70;
    g+=`<text x="${cx}" y="34" fill="${c[1]}" font-size="14" font-weight="800" text-anchor="middle" font-family="ui-sans-serif">${c[0]}</text>`;
    if(i===0){
      g+=diaCard(cx-42,by,84,52,c[1],{r:10,strong:true});
      g+=`<text x="${cx}" y="${by+31}" fill="#f0e6d8" font-size="11" text-anchor="middle" font-family="ui-monospace">BREW\u21c4STEAM</text>`;
    }
    if(i===1){
      g+=diaCard(cx-46,by,92,52,c[1],{r:10,strong:true});
      g+=`<text x="${cx}" y="${by-2}" fill="${DIA.ink3}" font-size="9" text-anchor="middle" font-family="ui-sans-serif">steam boiler</text>`;
      g+=`<rect x="${cx-30}" y="${by+16}" width="60" height="20" rx="6" fill="${_rgba('#5a8a9a',0.55)}" stroke="#5a8a9a" stroke-width="1.5"/>`;
      g+=`<text x="${cx}" y="${by+30}" fill="#f0e6d8" font-size="9.5" text-anchor="middle" font-family="ui-monospace">brew pipe</text>`;
    }
    if(i===2){
      g+=diaCard(cx-46,by,42,52,c[1],{r:8,strong:true});
      g+=diaCard(cx+4,by,42,52,'#c0433a',{r:8,strong:true});
      g+=`<text x="${cx-25}" y="${by+30}" fill="#f0e6d8" font-size="9.5" text-anchor="middle" font-family="ui-monospace">brew</text>`;
      g+=`<text x="${cx+25}" y="${by+30}" fill="#f0e6d8" font-size="9.5" text-anchor="middle" font-family="ui-monospace">steam</text>`;
    }
    c[3].split('\n').forEach((ln,j)=>{g+=`<text x="${cx}" y="${150+j*15}" fill="#c9b8a4" font-size="11.5" text-anchor="middle" font-family="ui-sans-serif">${ln}</text>`;});
    g+=`<text x="${cx}" y="${192}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">${c[4]}</text>`;
  });
  g+=`<line x1="255" y1="55" x2="255" y2="200" stroke="${DIA.line}" stroke-dasharray="4 5"/>`;
  g+=`<line x1="505" y1="55" x2="505" y2="200" stroke="${DIA.line}" stroke-dasharray="4 5"/>`;
  g+=`<text x="${W/2}" y="${H-8}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">All pump-driven at ~9 bars. Adding a PID sets brew temp precisely \u2014 the biggest consistency gain.</text>`;
  return diaWrap(`${W} ${H}`,g,'The three boiler configurations, simplest to most capable.');
}
// 44. Water chemistry: GH/KH balance + SCA target.
function diaWaterChem(){
  const W=760,H=250;
  let g=diaDefs(['#5a8a9a','#B07B3E','#8fbf3a']);
  // two hardness columns with header bars
  g+=diaHeader(60,20,300,'GH \u2014 General Hardness','calcium + magnesium = EXTRACTS flavor','#5a8a9a');
  g+=`<text x="200" y="82" fill="#c9b8a4" font-size="11" text-anchor="middle" font-family="ui-sans-serif">too little \u2192 flat, hollow</text>`;
  g+=`<text x="200" y="100" fill="#c9b8a4" font-size="11" text-anchor="middle" font-family="ui-sans-serif">too much \u2192 heavy, chalky</text>`;
  g+=diaHeader(420,20,300,'KH \u2014 Alkalinity','bicarbonate = BUFFERS acidity','#B07B3E');
  g+=`<text x="560" y="82" fill="#c9b8a4" font-size="11" text-anchor="middle" font-family="ui-sans-serif">too much \u2192 dull, flat</text>`;
  g+=`<text x="560" y="100" fill="#c9b8a4" font-size="11" text-anchor="middle" font-family="ui-sans-serif">too little \u2192 sharp, sour</text>`;
  g+=`<line x1="380" y1="24" x2="380" y2="110" stroke="${DIA.line}" stroke-dasharray="4 5"/>`;
  // SCA target card
  g+=diaCard(150,130,460,78,'#8fbf3a',{r:12,title:'SCA WATER TARGET',titleSize:13});
  const specs=[['TDS','~150 mg/L'],['Calcium','~50\u201375'],['Alkalinity','~40'],['pH','~7'],['Chlorine','~0']];
  const sw=440/specs.length;
  specs.forEach((s,i)=>{const x=160+i*sw+sw/2;
    if(i>0)g+=`<line x1="${160+i*sw}" y1="160" x2="${160+i*sw}" y2="200" stroke="${_rgba('#8fbf3a',0.22)}" stroke-width="1"/>`;
    g+=`<text x="${x}" y="${178}" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">${s[0]}</text>`;
    g+=`<text x="${x}" y="${196}" fill="#f0e6d8" font-size="12.5" font-weight="700" text-anchor="middle" font-family="ui-monospace">${s[1]}</text>`;
  });
  g+=`<text x="${W/2}" y="${H-8}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">Brewed coffee is ~98% water. Balance extracts flavor & buffers acidity \u2014 but KH is also what forms scale.</text>`;
  return diaWrap(`${W} ${H}`,g,'The two hardnesses and the SCA target for brewing water.');
}
// 45. From C price to farmgate: the price waterfall.
function diaCmarket(){
  const W=760,H=250;
  const steps=[
    ['+ / \u2212 Differential','country, quality, certifications','#C9A34E'],
    ['= FOB price','at the export port','#B07B3E'],
    ['\u2212 exporters, mills, middlemen','each takes a margin','#8A5A34'],
    ['= Farmgate price','what the farmer actually gets','#7a9a6a'],
  ];
  let g=diaDefs(['#c86a6a',...steps.map(s=>s[2])]);
  g=`<defs>${diaArrowMarker('#8a7660')}</defs>`+g;
  // C price at top as source
  g+=diaCard(280,18,200,46,'#c86a6a',{r:11,strong:true});
  g+=`<text x="380" y="38" fill="#f0e6d8" font-size="14" font-weight="800" text-anchor="middle" font-family="ui-sans-serif">The C Price</text>`;
  g+=`<text x="380" y="55" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">ICE benchmark \u00b7 Arabica futures</text>`;
  steps.forEach((s,i)=>{const y=80+i*38,cx=380;
    g+=`<path d="M${cx} ${y-14} L${cx} ${y-3}" stroke="#8a7660" stroke-width="1.6" marker-end="url(#darr)"/>`;
    g+=diaCard(230,y,300,30,s[2],{r:8,shadow:false});
    g+=`<text x="245" y="${y+13}" fill="#f0e6d8" font-size="12.5" font-weight="700" font-family="ui-sans-serif">${s[0]}</text>`;
    g+=`<text x="245" y="${y+26}" fill="${DIA.ink3}" font-size="10" font-family="ui-sans-serif">${s[1]}</text>`;
  });
  // side note about speculation & volatility
  g+=`<text x="40" y="120" fill="${DIA.ink3}" font-size="10.5" font-family="ui-sans-serif">Driven by:</text>`;
  g+=`<text x="40" y="138" fill="#c9b8a4" font-size="11" font-family="ui-sans-serif">\u00b7 weather, disease,</text>`;
  g+=`<text x="52" y="153" fill="#c9b8a4" font-size="11" font-family="ui-sans-serif">harvest cycles</text>`;
  g+=`<text x="40" y="173" fill="#c9b8a4" font-size="11" font-family="ui-sans-serif">\u00b7 speculation</text>`;
  g+=diaCard(596,108,140,52,'#c86a6a',{r:9,shadow:false});
  g+=`<text x="610" y="126" fill="${DIA.ink3}" font-size="10.5" font-family="ui-sans-serif">2018\u201319: &lt; $1/lb</text>`;
  g+=`<text x="610" y="143" fill="#e08a6a" font-size="12" font-weight="800" font-family="ui-sans-serif">2025: &gt; $4/lb</text>`;
  g+=`<text x="610" y="156" fill="${DIA.ink3}" font-size="9.5" font-family="ui-sans-serif">(50-yr high)</text>`;
  g+=`<text x="${W/2}" y="${H-8}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">The farmer often gets a small, shrinking slice \u2014 which is why specialty leans on differentials & direct trade.</text>`;
  return diaWrap(`${W} ${H}`,g,'How the benchmark price becomes what a farmer is actually paid.');
}
// 46. Climate: the squeeze on the bean belt.
function diaClimateCoffee(){
  const W=760,H=250;
  let g=diaDefs(['#c0433a','#7a9a6a']);
  g+=diaHeader(30,18,310,'The threat',null,'#c0433a');
  const threats=[['Warming','out of Arabica\u2019s 18\u201322\u00b0C band'],['Erratic rain','disrupts flowering & harvest'],['Rust & borer','spread to higher altitudes'],['Extreme events','frost, drought \u2192 crop loss']];
  threats.forEach((t,i)=>{const y=54+i*40;
    g+=diaCard(30,y,310,32,'#c0433a',{r:8,shadow:false});
    g+=`<text x="44" y="${y+14}" fill="#f0e6d8" font-size="12.5" font-weight="700" font-family="ui-sans-serif">${t[0]}</text>`;
    g+=`<text x="44" y="${y+27}" fill="${DIA.ink3}" font-size="10" font-family="ui-sans-serif">${t[1]}</text>`;
  });
  g+=diaHeader(420,18,310,'Adapting',null,'#7a9a6a');
  const adapt=[['Resistant varieties','heat/drought/disease + quality'],['Forgotten species','stenophylla, liberica'],['Shade / agroforestry','buffers temperature'],['New higher ground','shifting cultivation up']];
  adapt.forEach((t,i)=>{const y=54+i*40;
    g+=diaCard(420,y,310,32,'#7a9a6a',{r:8,shadow:false});
    g+=`<text x="434" y="${y+14}" fill="#f0e6d8" font-size="12.5" font-weight="700" font-family="ui-sans-serif">${t[0]}</text>`;
    g+=`<text x="434" y="${y+27}" fill="${DIA.ink3}" font-size="10" font-family="ui-sans-serif">${t[1]}</text>`;
  });
  g+=`<line x1="380" y1="48" x2="380" y2="216" stroke="${DIA.line}" stroke-dasharray="4 5"/>`;
  g+=`<text x="${W/2}" y="${H-8}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">Arabica-suitable land could ~halve by 2050 \u2014 and the burden falls hardest on smallholder families.</text>`;
  return diaWrap(`${W} ${H}`,g,'Climate change is squeezing the coffee-growing world \u2014 and the industry is racing to adapt.');
}
// 47. Coffee history timeline.
function diaHistoryTimeline(){
  const W=820,H=270,L=44,R=W-30,axisY=138;
  let g='';
  g+=`<line x1="${L}" y1="${axisY}" x2="${R}" y2="${axisY}" stroke="#b0894a" stroke-width="2.5"/>`;
  g+=`<path d="M${R} ${axisY} l-9 -5 l0 10 z" fill="#b0894a"/>`;
  const events=[
    ['~1400','Ethiopia:','brewed in ceremony',1,'#7d9f4a'],
    ['15th c.','Yemen:','Sufi drink, Mocha',0,'#a0522d'],
    ['~1475','1st coffeehouse','Constantinople',1,'#c86a9a'],
    ['~1600','Europe via Venice','the Pope approves',0,'#c86a6a'],
    ['1652','London','coffeehouses',1,'#5a8a9a'],
    ['~1720','de Clieu\u2019s seedling','\u2192 Martinique',0,'#B07B3E'],
    ['1727','Brazil','(\u2192 #1 producer)',1,'#8A5A34'],
    ['1948','Gaggia lever','espresso + crema',0,'#C9A34E'],
    ['2000s','3rd wave','specialty',1,'#8fbf3a'],
  ];
  const span=R-L-30;
  events.forEach((e,i)=>{const x=L+18+(span/(events.length-1))*i;
    const above=e[3];
    g+=`<circle cx="${x}" cy="${axisY}" r="5.5" fill="${e[4]}"/>`;
    g+=`<line x1="${x}" y1="${above?axisY-9:axisY+9}" x2="${x}" y2="${above?axisY-30:axisY+30}" stroke="${e[4]}" stroke-width="1.3" opacity="0.55"/>`;
    const yYear=above?axisY-62:axisY+50;
    g+=`<text x="${x}" y="${yYear}" fill="${e[4]}" font-size="12.5" font-weight="800" text-anchor="middle" font-family="ui-monospace">${e[0]}</text>`;
    g+=`<text x="${x}" y="${yYear+15}" fill="#f0e6d8" font-size="10.5" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${e[1]}</text>`;
    g+=`<text x="${x}" y="${yYear+29}" fill="#8f7c66" font-size="9.5" text-anchor="middle" font-family="ui-sans-serif">${e[2]}</text>`;
  });
  g+=`<text x="${L}" y="24" fill="#8f7c66" font-size="11.5" font-family="ui-sans-serif" font-style="italic">From a wild Ethiopian shrub to a global craft \u2014 six centuries.</text>`;
  return diaWrap(`${W} ${H}`,g,'The spread of coffee across the world, by date.');
}
// 48. The Arabica family tree.
function diaFamilyTree(){
  const W=820,H=340;
  let g='';
  const box=(x,y,w,label,color,sub,strong)=>{
    const h=sub?36:28;
    let s=`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="8" fill="${color}" opacity="${strong?0.22:0.13}" stroke="${color}" stroke-width="${strong?1.8:1.2}"/>`;
    s+=`<text x="${x+w/2}" y="${y+(sub?16:18)}" fill="#f0e6d8" font-size="${strong?13:12}" font-weight="${strong?800:700}" text-anchor="middle" font-family="ui-sans-serif">${label}</text>`;
    if(sub) s+=`<text x="${x+w/2}" y="${y+30}" fill="#8f7c66" font-size="9" text-anchor="middle" font-family="ui-sans-serif">${sub}</text>`;
    return s;
  };
  const line=(x1,y1,x2,y2,c)=>`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${c||'#5a4a38'}" stroke-width="1.3" opacity="0.65"/>`;
  // Row 0 — root
  g+=box(350,12,120,'Yemen stock','#a0522d',null,false);
  // Row 1 — two founders (y=64)
  g+=line(390,40,250,64); g+=line(430,40,560,64);
  g+=box(170,64,170,'TYPICA','#C9A34E','tall, sweet, clean',true);
  g+=box(480,64,170,'BOURBON','#c86a6a','richer, higher-yield',true);
  // Row 2 — mutations & first branches (y=124)
  g+=line(210,100,150,124); g+=line(255,100,300,124);
  g+=box(95,124,120,'Maragogipe','#B07B3E','giant bean',false);
  g+=box(250,124,120,'Mundo Novo','#8A5A34','Bourbon\u00d7Typica',false);
  g+=line(530,100,420,124); g+=line(560,100,555,124); g+=line(590,100,690,124);
  g+=box(380,124,120,'Caturra','#8fbf3a','dwarf, BR ~1937',false);
  g+=box(510,124,120,'Pacas / V.Sarchi','#7d9f4a','dwarf mutations',false);
  g+=box(640,124,120,'SL28 / SL34','#c86a9a','Kenya, blackcurrant',false);
  // Row 3 — crosses (y=190)
  g+=line(150,160,150,190); g+=line(310,160,300,190); g+=line(440,160,375,190); g+=line(560,160,555,190);
  g+=box(90,190,125,'Pacamara','#B07B3E','Pacas\u00d7Maragogipe',false);
  g+=box(245,190,120,'Catua\u00ed','#8A5A34','MundoNovo\u00d7Caturra',false);
  g+=box(380,190,120,'(disease branch \u2193)','#5a8a9a','needs rust resistance',false);
  g+=box(510,190,120,'Sarchimor','#7d9f4a','V.Sarchi\u00d7Timor',false);
  g+=box(640,190,120,'Catimor','#5a8a9a','Caturra\u00d7Timor',false);
  // Row 4 — Timor hybrid feeding the introgressed families (y=252)
  g+=line(570,226,555,252); g+=line(690,226,690,252);
  g+=box(470,252,290,'Timor Hybrid  (Arabica \u00d7 Robusta)','#c0433a','the disease-resistance source \u2192 Catimor / Sarchimor',true);
  // Geisha aside (bottom-left, clearly separate)
  g+=box(60,252,300,'Geisha \u2014 Ethiopian landrace (stands apart)','#d0a850','jasmine/bergamot \u00b7 the modern superstar',true);
  g+=`<text x="${W/2}" y="${H-10}" fill="#8f7c66" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">Two founders (Typica &amp; Bourbon) branch into mutations &amp; crosses. The Timor Hybrid adds Robusta\u2019s disease resistance.</text>`;
  return diaWrap(`${W} ${H}`,g,'How the major Arabica varieties are related.');
}
// 49. The coffee species map.
function diaSpeciesMap(){
  const W=760,H=250;
  const arab=['ARABICA','Coffea arabica','#8fbf3a',['~60\u201370% of production','high altitude, delicate','~1.2\u20131.5% caffeine','sweet, acidic, complex','THE specialty species']];
  const rob=['ROBUSTA','Coffea canephora','#a0824a',['~30\u201340% of production','hot & low, very hardy','~2.2\u20132.7% caffeine','heavy, bitter, less nuance','instant + espresso blends']];
  let g=diaDefs(['#8fbf3a','#a0824a','#7a6a52']);
  [[arab,60],[rob,410]].forEach(([sp,x])=>{
    g+=diaCard(x,24,290,150,sp[2],{r:12,strong:true});
    g+=`<text x="${x+145}" y="48" fill="#f0e6d8" font-size="16" font-weight="800" text-anchor="middle" font-family="ui-sans-serif" letter-spacing="1">${sp[0]}</text>`;
    g+=`<text x="${x+145}" y="64" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-monospace" font-style="italic">${sp[1]}</text>`;
    g+=`<line x1="${x+40}" y1="72" x2="${x+250}" y2="72" stroke="${_rgba(sp[2],0.3)}" stroke-width="1"/>`;
    sp[3].forEach((t,i)=>{g+=`<text x="${x+145}" y="${88+i*17.5}" fill="#c9b8a4" font-size="11" text-anchor="middle" font-family="ui-sans-serif">${t}</text>`;});
  });
  // vs badge
  g+=`<circle cx="380" cy="99" r="17" fill="#160e08" stroke="${DIA.ink3}" stroke-width="1.2" filter="url(#dsoft)"/>`;
  g+=`<text x="380" y="104" fill="${DIA.ink}" font-size="12" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">vs</text>`;
  // forgotten species strip
  g+=diaCard(60,186,640,34,'#7a6a52',{r:9,shadow:false});
  g+=`<text x="72" y="200" fill="${DIA.ink3}" font-size="9.5" font-family="ui-monospace">THE REST:</text>`;
  g+=`<text x="72" y="214" fill="#c9b8a4" font-size="11" font-family="ui-sans-serif">Liberica (smoky, hardy \u00b7 'Barako')   \u00b7   Excelsa (tart, fruity)   \u00b7   Stenophylla (Arabica-like but heat-tolerant \u2014 a climate hope)</text>`;
  g+=`<text x="${W/2}" y="${H-6}" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">Arabica is a natural eugenioides\u00d7canephora hybrid \u2014 refined but genetically fragile.</text>`;
  return diaWrap(`${W} ${H}`,g,'The two species that run the coffee world, and the forgotten ones.');
}
// 50. Decaffeination methods compared.
function diaDecafMethods(){
  const W=760,H=250;
  const methods=[
    ['Solvent (MC)','methylene chloride \u2014 aggressive','#a0524a',30],
    ['Solvent (EA)','ethyl acetate \u2014 gentler, \u2018sugarcane\u2019','#B07B3E',82],
    ['Swiss Water','caffeine-free extract, no chemicals','#5a8a9a',134],
    ['CO2','supercritical \u2014 top flavor, pricey','#8fbf3a',186],
  ];
  let g=diaDefs(['#7d9f4a',...methods.map(m=>m[2])]);
  // green bean in center-left as the shared start (glowing)
  g+=`<circle cx="90" cy="120" r="34" fill="url(#${_cid('#7d9f4a')})" stroke="#7d9f4a" stroke-width="2" filter="url(#dsh)"/>`;
  g+=`<text x="90" y="116" fill="#f0e6d8" font-size="11" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">green</text>`;
  g+=`<text x="90" y="130" fill="#f0e6d8" font-size="11" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">beans</text>`;
  g+=`<text x="90" y="168" fill="${DIA.ink3}" font-size="9" text-anchor="middle" font-family="ui-sans-serif">steam \u2192 extract \u2192 dry</text>`;
  methods.forEach(m=>{const y=m[3];
    g+=`<line x1="124" y1="120" x2="196" y2="${y+17}" stroke="${m[2]}" stroke-width="1.4" opacity="0.55"/>`;
    g+=`<circle cx="196" cy="${y+17}" r="2.5" fill="${m[2]}"/>`;
    g+=diaCard(200,y,540,34,m[2],{r:8,shadow:false});
    g+=`<text x="214" y="${y+15}" fill="#f0e6d8" font-size="13" font-weight="700" font-family="ui-sans-serif">${m[0]}</text>`;
    g+=`<text x="214" y="${y+28}" fill="${DIA.ink3}" font-size="10.5" font-family="ui-sans-serif">${m[1]}</text>`;
  });
  g+=`<text x="${W/2}" y="${H-8}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">All remove ~97\u201399% caffeine. The agent \u2014 solvent, water, or CO2 \u2014 decides the flavor and the price.</text>`;
  return diaWrap(`${W} ${H}`,g,'The four ways caffeine is removed from coffee.');
}
// 51. Instant coffee: spray vs freeze drying.
function diaInstantCoffee(){
  const W=760,H=250;
  let g=diaDefs(['#a0824a','#B07B3E','#5a8a9a']);
  g=`<defs>${diaArrowMarker('#8a7660')}</defs>`+g;
  // shared start: brewed concentrate
  g+=diaCard(300,16,160,38,'#a0824a',{r:9,strong:true});
  g+=`<text x="380" y="34" fill="#f0e6d8" font-size="12.5" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">Concentrated brew</text>`;
  g+=`<text x="380" y="48" fill="${DIA.ink3}" font-size="9.5" text-anchor="middle" font-family="ui-sans-serif">remove ALL the water \u2192</text>`;
  g+=`<path d="M340 56 L206 76" stroke="#8a7660" stroke-width="1.4" marker-end="url(#darr)"/>`;
  g+=`<path d="M420 56 L554 76" stroke="#8a7660" stroke-width="1.4" marker-end="url(#darr)"/>`;
  // spray drying
  g+=diaCard(40,80,320,118,'#B07B3E',{r:12});
  g+=`<text x="200" y="102" fill="#f0e6d8" font-size="14" font-weight="800" text-anchor="middle" font-family="ui-sans-serif">SPRAY DRYING</text>`;
  ['Mist into hot-air tower','Water flashes off instantly','\u2192 fine POWDER','Cheaper, high-volume','Heat costs aroma'].forEach((t,i)=>{
    g+=`<text x="200" y="${122+i*15}" fill="#c9b8a4" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">${t}</text>`;});
  // freeze drying
  g+=diaCard(400,80,320,118,'#5a8a9a',{r:12});
  g+=`<text x="560" y="102" fill="#f0e6d8" font-size="14" font-weight="800" text-anchor="middle" font-family="ui-sans-serif">FREEZE DRYING</text>`;
  ['Freeze to ~-40\u00b0C','Vacuum: ice \u2192 vapor (sublimes)','\u2192 crystalline GRANULES','Premium method','Cold preserves aroma'].forEach((t,i)=>{
    g+=`<text x="560" y="${122+i*15}" fill="#c9b8a4" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">${t}</text>`;});
  g+=`<text x="${W/2}" y="${H-8}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">Instant = brewed coffee with the water removed. Cold-drying keeps more flavor \u2014 hence premium freeze-dried.</text>`;
  return diaWrap(`${W} ${H}`,g,'The two ways instant coffee is dried.');
}
// 52. The evolution of espresso pressure.
function diaEspHistory(){
  const W=820,H=260;
  let g='';
  const eras=[
    ['1884','Moriondo','steam, bulk','#8A5A34','~1.5 bar'],
    ['1901','Bezzera','portafilter','#a0522d','~1.5 bar'],
    ['1905','Pavoni','1st commercial','#B07B3E','~1.5\u20132 bar'],
    ['1948','Gaggia','LEVER \u2192 crema!','#C9A34E','8\u201310 bar'],
    ['1961','Faema E61','motor PUMP','#8fbf3a','9 bar'],
    ['1990s+','3rd wave','PID, profiling','#5a8a9a','9 bar, tuned'],
  ];
  const L=50,R=W-30,axisY=150;
  g+=`<line x1="${L}" y1="${axisY}" x2="${R}" y2="${axisY}" stroke="#B07B3E" stroke-width="2.5"/>`;
  g+=`<path d="M${R} ${axisY} l-9 -5 l0 10 z" fill="#B07B3E"/>`;
  const span=R-L-30;
  eras.forEach((e,i)=>{const x=L+18+(span/(eras.length-1))*i;
    g+=`<circle cx="${x}" cy="${axisY}" r="5.5" fill="${e[3]}"/>`;
    g+=`<line x1="${x}" y1="${axisY-9}" x2="${x}" y2="${axisY-30}" stroke="${e[3]}" stroke-width="1.3" opacity="0.55"/>`;
    g+=`<text x="${x}" y="${axisY-62}" fill="${e[3]}" font-size="12.5" font-weight="800" text-anchor="middle" font-family="ui-monospace">${e[0]}</text>`;
    g+=`<text x="${x}" y="${axisY-47}" fill="#f0e6d8" font-size="11.5" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${e[1]}</text>`;
    g+=`<text x="${x}" y="${axisY-33}" fill="#8f7c66" font-size="9.5" text-anchor="middle" font-family="ui-sans-serif">${e[2]}</text>`;
    g+=`<text x="${x}" y="${axisY+24}" fill="${e[3]}" font-size="11" font-weight="700" text-anchor="middle" font-family="ui-monospace">${e[4]}</text>`;
  });
  g+=`<text x="${L}" y="${axisY+52}" fill="#8f7c66" font-size="11" font-family="ui-sans-serif" font-style="italic">The whole story is better ways to make pressure: steam \u2192 lever \u2192 pump \u2192 computer.</text>`;
  return diaWrap(`${W} ${H}`,g,'140 years of the espresso machine, by pressure.');
}
// 53. The journey and rise of Geisha.
function diaGeishaStory(){
  const W=760,H=250;
  const stops=[['Gori Gesha','Ethiopia, 1930s','#7d9f4a'],['CATIE','Costa Rica, 1950s (T2722)','#B07B3E'],['Panama','1960s \u2014 for rust resistance','#C9A34E'],['Best of Panama','2004 \u2014 the moment','#d0a850']];
  let g=diaDefs(['#7d9f4a','#B07B3E','#C9A34E','#d0a850','#c86a6a']);
  g=`<defs>${diaArrowMarker('#8a7660')}</defs>`+g;
  const y0=44;
  stops.forEach((s,i)=>{const x=30+i*185;
    g+=diaCard(x,y0,150,48,s[2],{r:10,strong:i===3});
    g+=`<text x="${x+75}" y="${y0+20}" fill="#f0e6d8" font-size="12.5" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${s[0]}</text>`;
    g+=`<text x="${x+75}" y="${y0+37}" fill="${DIA.ink3}" font-size="9" text-anchor="middle" font-family="ui-sans-serif">${s[1]}</text>`;
    if(i<stops.length-1) g+=`<path d="M${x+150} ${y0+24} l13 0" stroke="#8a7660" stroke-width="1.6" marker-end="url(#darr)"/>`;
  });
  g+=`<text x="30" y="30" fill="${DIA.ink3}" font-size="10.5" font-family="ui-monospace">THE JOURNEY</text>`;
  // flavor + price panels
  g+=diaCard(30,118,345,96,'#d0a850',{r:12,title:'THE FLAVOR',titleSize:12.5});
  ['Jasmine \u00b7 orange blossom \u00b7 bergamot','Peach \u00b7 tropical fruit \u00b7 tea-like body','From linalool + geraniol aromatics','Only at altitude, picked & processed w/ care'].forEach((t,i)=>{
    g+=`<text x="202" y="${160+i*15}" fill="#c9b8a4" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">${t}</text>`;});
  g+=diaCard(390,118,345,96,'#c86a6a',{r:12,title:'THE PRICE (world\u2019s most expensive)',titleSize:12});
  ['2004: ~$21/lb (\u224810\u00d7 the going rate)','2019: broke $1,000/lb','2020s: top lots >$2,000/lb green','Scarcity + narrative'].forEach((t,i)=>{
    g+=`<text x="562" y="${160+i*15}" fill="#c9b8a4" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">${t}</text>`;});
  g+=`<text x="${W/2}" y="${H-6}" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">A forgotten rust-resistant plant \u2192 the most celebrated variety of the modern era.</text>`;
  return diaWrap(`${W} ${H}`,g,'How Geisha travelled the world and became coffee\u2019s superstar.');
}
// 54. Roast-defect visual gallery — custom coffee-bean SVGs showing each defect.
function diaRoastDefects(){
  const W=760,H=430;
  // a single coffee bean drawn at (cx,cy), scale s, base fill color, with an optional overlay(kind)
  const bean=(cx,cy,s,fill,overlay)=>{
    let b=`<g transform="translate(${cx},${cy}) scale(${s})">`;
    // bean body: an ellipse
    b+=`<ellipse cx="0" cy="0" rx="30" ry="20" fill="${fill}" stroke="#2a1c10" stroke-width="1.5"/>`;
    // center crease (the classic coffee-bean fold) — an S curve
    b+=`<path d="M0 -18 C -6 -8, 6 8, 0 18" fill="none" stroke="#2a1c10" stroke-width="2" opacity="0.85"/>`;
    // overlays for defects
    if(overlay==='scorch'){ // dark burnt patches on flat faces
      b+=`<ellipse cx="-13" cy="-4" rx="6" ry="4" fill="#1a0f06" opacity="0.85"/>`;
      b+=`<ellipse cx="11" cy="6" rx="5" ry="3.5" fill="#1a0f06" opacity="0.8"/>`;
    }
    if(overlay==='tip'){ // burnt tips/edges
      b+=`<ellipse cx="-26" cy="0" rx="6" ry="5" fill="#160c05" opacity="0.9"/>`;
      b+=`<ellipse cx="26" cy="0" rx="6" ry="5" fill="#160c05" opacity="0.9"/>`;
    }
    if(overlay==='face'){ // one whole side charred black
      b+=`<path d="M0 -20 A 30 20 0 0 0 0 20 Z" fill="#120a04" opacity="0.9"/>`;
    }
    if(overlay==='chip'){ // a chunk missing (black), broken edge
      b+=`<path d="M14 -14 L30 -6 L26 8 L12 2 Z" fill="#0e0805"/>`;
      b+=`<path d="M14 -14 L30 -6 L26 8 L12 2 Z" fill="none" stroke="#2a1c10" stroke-width="1"/>`;
    }
    if(overlay==='oil'){ // oily sheen for overdeveloped — light highlights
      b+=`<ellipse cx="-8" cy="-8" rx="9" ry="5" fill="#ffffff" opacity="0.13"/>`;
      b+=`<ellipse cx="9" cy="7" rx="6" ry="3" fill="#ffffff" opacity="0.10"/>`;
    }
    b+=`</g>`;
    return b;
  };
  // grid of 3 cols x 3 rows; each cell: bean + name + one-line cause + cup note
  const cells=[
    ['Healthy','#7a4a24','even color, matte-satin','sweet, balanced',null],
    ['Scorching','#6e3e1e','hot drum, flat-face burns','ashy, smoky',' scorch'],
    ['Tipping','#6e3e1e','too-fast heat, burnt tips','burnt, bitter','tip'],
    ['Facing','#5a3216','stuck on drum, one side charred','acrid, smoky','face'],
    ['Chipping','#5a3216','2nd-crack pressure, chunk lost','burnt bits','chip'],
    ['Underdeveloped','#a06a3a','too fast \u2014 pale, matte','grassy, sour, thin',null],
    ['Overdeveloped','#3a2412','too long \u2014 dark & oily','bitter, charred, ashy','oil'],
    ['Baked','#8a5a30','temp stalled \u2014 looks fine!','flat, bready, lifeless',null],
    ['Quaker','#c79a5a','unripe bean \u2014 stays pale','papery, cereal, dry',null],
  ];
  let g='';
  g+=`<text x="20" y="22" fill="#8f7c66" font-size="11.5" font-family="ui-sans-serif" font-style="italic">Same target color can hide very different roasts \u2014 many defects show on the bean, some only in the cup.</text>`;
  const cols=3,cw=W/cols,ch=128,y0=42;
  cells.forEach((c,i)=>{
    const col=i%cols,row=Math.floor(i/cols);
    const cx=col*cw+cw/2, cy=y0+row*ch;
    // card bg
    g+=`<rect x="${col*cw+12}" y="${cy-6}" width="${cw-24}" height="${ch-14}" rx="10" fill="#20160e" stroke="#2f2318" stroke-width="1"/>`;
    // bean
    g+=bean(cx,cy+34,1.0,c[1],c[4]);
    // name
    g+=`<text x="${cx}" y="${cy+74}" fill="#f0e6d8" font-size="13" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${c[0]}</text>`;
    // cause
    g+=`<text x="${cx}" y="${cy+90}" fill="#8f7c66" font-size="9.5" text-anchor="middle" font-family="ui-sans-serif">${c[2]}</text>`;
    // cup note
    g+=`<text x="${cx}" y="${cy+104}" fill="#c9a35a" font-size="9.5" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">${c[3]}</text>`;
  });
  return diaWrap(`${W} ${H}`,g,'A visual field guide to the common roast defects.');
}
// 55. Reusable variety spotlight card (used by SL28, Bourbon, Pacamara, Maragogipe).
function diaVarietyCard(name,color,parent,traits,flavor,legacy){
  const W=760,H=252;
  const cols=['#B07B3E','#d0a850','#8fbf3a'];
  let g=diaDefs([color,...cols]);
  // big name header — gradient + depth + accent bar
  g+=diaCard(30,18,700,54,color,{r:13,strong:true});
  g+=`<rect x="30" y="18" width="5" height="54" rx="2.5" fill="${color}"/>`;
  g+=`<text x="52" y="44" fill="#f0e6d8" font-size="20" font-weight="800" font-family="ui-sans-serif" letter-spacing="-0.01em">${name}</text>`;
  g+=`<text x="52" y="63" fill="${DIA.ink3}" font-size="11" font-family="ui-monospace">${parent}</text>`;
  // three gradient panels
  const panels=[['TRAITS',traits,cols[0]],['IN THE CUP',flavor,cols[1]],['LEGACY',legacy,cols[2]]];
  panels.forEach((p,i)=>{const x=30+i*234;
    g+=diaCard(x,88,222,120,p[2],{r:11,title:p[0],titleSize:11.5});
    g+=`<line x1="${x+14}" y1="118" x2="${x+208}" y2="118" stroke="${_rgba(p[2],0.3)}" stroke-width="1"/>`;
    p[1].forEach((t,j)=>{
      g+=`<circle cx="${x+18}" cy="${133+j*17.5}" r="2" fill="${p[2]}"/>`;
      g+=`<text x="${x+27}" y="${137+j*17.5}" fill="#c9b8a4" font-size="10.5" font-family="ui-sans-serif">${t}</text>`;});
  });
  g+=`<text x="${W/2}" y="${H-8}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">Part of the Arabica family \u2014 see the family tree for how it connects.</text>`;
  return diaWrap(`${W} ${H}`,g,`${name} at a glance.`);
}
function diaSpotSl28(){return diaVarietyCard('SL28','#c86a9a','Scott Labs selection \u00b7 Bourbon-related \u00b7 Kenya, 1930s',
  ['Tall, low-yield','Drought-tolerant, deep roots','Susceptible: rust & CBD'],
  ['BLACKCURRANT signature','Wine-like acidity','Dark fruit, full juicy body'],
  ['Backbone of Kenyan coffee','Paired with SL34','Benchmark for complexity']);}
function diaSpotBourbon(){return diaVarietyCard('Bourbon','#c86a6a','Founder \u00b7 mutated on R\u00e9union (Bourbon) \u00b7 early 1700s',
  ['Higher-yield than Typica','Red/yellow/orange/pink forms','Classic quality plant'],
  ['Pronounced sweetness','Rounded body, balanced','Caramel, chocolate, red fruit'],
  ['Caturra/Pacas/V.Sarchi','Mundo Novo \u2192 Catua\u00ed','Parent of most LatAm kinds']);}
function diaSpotPacamara(){return diaVarietyCard('Pacamara','#8fbf3a','Bred in El Salvador (ISIC) \u00b7 Pacas \u00d7 Maragogipe \u00b7 1958',
  ['ENORMOUS beans','Somewhat unstable','Compact-ish plant'],
  ['Intense, wild, complex','Fruit, floral, herbal','Sometimes savory/tomato'],
  ['Cup of Excellence favorite','Central American signature','Cult following']);}
function diaSpotMaragogipe(){return diaVarietyCard('Maragogipe','#B07B3E','\u2018Elephant bean\u2019 \u00b7 Typica mutation \u00b7 Brazil ~1870',
  ['LARGEST beans in coffee','Big plant, wide spacing','Low-yielding'],
  ['Soft, mild, smooth, clean','Gentle sweetness','Low-moderate acidity'],
  ['The \u2018giant bean\u2019 gene','Parent of Pacamara','Distinctive novelty']);}
// 56. Caffeine science: adenosine-blocking mechanism + the ~5hr half-life decay.
function diaCaffeineScience(){
  const W=760,H=270;
  let g=diaDefs(['#c86a4a','#5a8a9a','#8fbf3a']);
  // LEFT: the receptor mechanism
  g+=diaHeader(24,18,340,'The mechanism','caffeine blocks the "tired" signal','#c86a4a');
  // receptor (a notch) with adenosine blocked and caffeine plugged in
  const ry=110;
  // receptor body
  g+=`<path d="M60 ${ry+40} L60 ${ry-10} Q60 ${ry-20} 75 ${ry-20} L110 ${ry-20} Q120 ${ry-20} 120 ${ry-8} L120 ${ry+8} Q120 ${ry+18} 130 ${ry+18} L150 ${ry+18} Q160 ${ry+18} 160 ${ry+8} L160 ${ry-8} Q160 ${ry-20} 170 ${ry-20} L205 ${ry-20} Q220 ${ry-20} 220 ${ry-10} L220 ${ry+40} Z" fill="url(#${_cid('#8fbf3a')})" stroke="${_rgba('#8fbf3a',0.6)}" stroke-width="1.5"/>`;
  g+=`<text x="140" y="${ry+34}" fill="${DIA.ink3}" font-size="9.5" text-anchor="middle" font-family="ui-sans-serif">adenosine receptor</text>`;
  // caffeine molecule plugged into the notch
  g+=`<circle cx="140" cy="${ry-2}" r="15" fill="url(#${_cid('#c86a4a')})" stroke="#c86a4a" stroke-width="2" filter="url(#dsoft)"/>`;
  g+=`<text x="140" y="${ry+2}" fill="#f0e6d8" font-size="9" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">CAFF</text>`;
  // adenosine floating away, blocked
  g+=`<circle cx="270" cy="${ry-30}" r="13" fill="${_rgba('#5a8a9a',0.3)}" stroke="#5a8a9a" stroke-width="1.5" stroke-dasharray="3 2"/>`;
  g+=`<text x="270" y="${ry-27}" fill="${DIA.ink}" font-size="8" font-weight="600" text-anchor="middle" font-family="ui-sans-serif">aden.</text>`;
  g+=`<text x="270" y="${ry-9}" fill="#5a8a9a" font-size="8.5" text-anchor="middle" font-family="ui-sans-serif">blocked!</text>`;
  g+=`<path d="M255 ${ry-18} L230 ${ry-6}" stroke="#5a8a9a" stroke-width="1.3" stroke-dasharray="3 2" opacity="0.6"/>`;
  g+=`<text x="140" y="${ry+64}" fill="#c9b8a4" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">Same shape as adenosine \u2192 plugs the</text>`;
  g+=`<text x="140" y="${ry+79}" fill="#c9b8a4" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">receptor without switching it on.</text>`;
  // divider
  g+=`<line x1="380" y1="30" x2="380" y2="240" stroke="${DIA.line}" stroke-dasharray="4 5"/>`;
  // RIGHT: half-life decay curve
  g+=diaHeader(404,18,340,'The ~5-hour half-life','why afternoon coffee wrecks sleep','#5a8a9a');
  const gx0=430,gx1=730,gy0=70,gy1=190; // graph box
  // axes
  g+=`<line x1="${gx0}" y1="${gy0}" x2="${gx0}" y2="${gy1}" stroke="${DIA.line}"/>`;
  g+=`<line x1="${gx0}" y1="${gy1}" x2="${gx1}" y2="${gy1}" stroke="${DIA.line}"/>`;
  g+=`<text x="${gx0-6}" y="${gy0+4}" fill="${DIA.ink3}" font-size="9" text-anchor="end" font-family="ui-monospace">200mg</text>`;
  g+=`<text x="${gx0-6}" y="${(gy0+gy1)/2+4}" fill="${DIA.ink3}" font-size="9" text-anchor="end" font-family="ui-monospace">100</text>`;
  // exponential decay: half every 5h; plot 0..15h across width
  const hours=15; const pts=[];
  for(let h=0;h<=hours;h+=0.5){ const frac=Math.pow(0.5,h/5); const x=gx0+(h/hours)*(gx1-gx0); const y=gy1-frac*(gy1-gy0); pts.push([x,y]); }
  const path=pts.map((p,i)=>(i?'L':'M')+p[0].toFixed(1)+' '+p[1].toFixed(1)).join(' ');
  // area under curve
  g+=`<path d="${path} L${gx1} ${gy1} L${gx0} ${gy1} Z" fill="url(#${_cid('#c86a4a')})"/>`;
  g+=`<path d="${path}" fill="none" stroke="#e0864a" stroke-width="2.5" stroke-linecap="round"/>`;
  // markers at 3pm(0h), 8pm(5h), 1am(10h)
  const mk=(h,lab,mg)=>{const frac=Math.pow(0.5,h/5);const x=gx0+(h/hours)*(gx1-gx0);const y=gy1-frac*(gy1-gy0);
    return `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="3.5" fill="#e0864a" stroke="${DIA.bg}" stroke-width="1.5"/>`+
      `<text x="${x.toFixed(1)}" y="${gy1+13}" fill="${DIA.ink3}" font-size="8.5" text-anchor="middle" font-family="ui-sans-serif">${lab}</text>`+
      `<text x="${x.toFixed(1)}" y="${(y-8).toFixed(1)}" fill="#e0864a" font-size="9" font-weight="700" text-anchor="middle" font-family="ui-monospace">${mg}</text>`;};
  g+=mk(0,'3pm','200');
  g+=mk(5,'8pm','100');
  g+=mk(10,'1am','50');
  g+=`<text x="${(gx0+gx1)/2}" y="${gy1+30}" fill="#c9b8a4" font-size="10" text-anchor="middle" font-family="ui-sans-serif">Half clears every ~5 hours (much slower if you're a "slow metabolizer").</text>`;
  g+=`<text x="${W/2}" y="${H-8}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">Caffeine hides fatigue by blocking adenosine \u2014 then lingers for hours. Genes (CYP1A2, ADORA2A) set your response.</text>`;
  return diaWrap(`${W} ${H}`,g,'How caffeine blocks the brain\u2019s tiredness signal, and how slowly it clears.');
}
// 57. Experimental processing / fermentation methods.
function diaFermentMethods(){
  const W=760,H=290;
  const methods=[
    ['Anaerobic','sealed, no oxygen \u00b7 one-way valve','heavy body, winey, boozy fruit','#8A5A34'],
    ['Carbonic maceration','whole cherries in CO\u2082 (from wine)','uniform, vibrant, juicy red fruit','#c0433a'],
    ['Lactic','anaerobic favoring LAB \u00b7 80+ hrs','velvety, yogurt-tang, sweet','#d0a850'],
    ['Thermal shock','hot\u2194cold swings shift microbes','intensified sweetness, exotic','#5a8a9a'],
    ['Co-fermentation','+ fruit/spice/cacao (debated)','layered candy & spice notes','#c86a9a'],
  ];
  let g=diaDefs(['#7d9f4a',...methods.map(m=>m[3])]);
  // shared start: the cherry + microbes
  g+=`<circle cx="70" cy="130" r="30" fill="url(#${_cid('#7d9f4a')})" stroke="#7d9f4a" stroke-width="2" filter="url(#dsh)"/>`;
  g+=`<text x="70" y="126" fill="#f0e6d8" font-size="10.5" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">cherry</text>`;
  g+=`<text x="70" y="140" fill="#f0e6d8" font-size="8.5" text-anchor="middle" font-family="ui-sans-serif">+ microbes</text>`;
  g+=`<text x="70" y="176" fill="${DIA.ink3}" font-size="8.5" text-anchor="middle" font-family="ui-sans-serif">fermentation =</text>`;
  g+=`<text x="70" y="188" fill="${DIA.ink3}" font-size="8.5" text-anchor="middle" font-family="ui-sans-serif">flavor lever</text>`;
  g+=`<text x="20" y="24" fill="${DIA.ink3}" font-size="10.5" font-family="ui-monospace">CONTROL THE MICROBES \u2192 UNLOCK FLAVOR</text>`;
  methods.forEach((m,i)=>{const y=36+i*48;
    g+=`<line x1="100" y1="130" x2="176" y2="${y+22}" stroke="${m[3]}" stroke-width="1.5" opacity="0.5"/>`;
    g+=`<circle cx="176" cy="${y+22}" r="2.5" fill="${m[3]}"/>`;
    g+=diaCard(180,y,560,44,m[3],{r:9,shadow:false});
    g+=`<text x="194" y="${y+19}" fill="#f0e6d8" font-size="13.5" font-weight="700" font-family="ui-sans-serif">${m[0]}</text>`;
    g+=`<text x="194" y="${y+35}" fill="${DIA.ink3}" font-size="10" font-family="ui-sans-serif">${m[1]}</text>`;
    g+=`<text x="726" y="${y+19}" fill="${_rgba(m[3],1)}" font-size="10.5" font-weight="600" text-anchor="end" font-family="ui-sans-serif">\u2192 in the cup:</text>`;
    g+=`<text x="726" y="${y+35}" fill="#c9b8a4" font-size="10.5" text-anchor="end" font-family="ui-sans-serif" font-style="italic">${m[2]}</text>`;
  });
  g+=`<text x="${W/2}" y="${H-8}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">Trustworthy lots name the method + fermentation time + origin. Vague "specialty fermented" = a red flag.</text>`;
  return diaWrap(`${W} ${H}`,g,'The experimental fermentation methods and the flavors they create.');
}
// 57. Moka pot cross-section: three chambers + steam-pressure flow, and how it differs from espresso.
function diaMokaPot(){
  const W=760,H=270;
  let g=diaDefs(['#a0824a','#8A5A34','#c0433a','#7a9a6a']);
  g=`<defs>${diaArrowMarker('#e0864a')}</defs>`+g;
  // ---- LEFT: cross-section of the pot ----
  const cx=175;
  g+=diaHeader(24,16,320,'The three chambers','steam pressure pushes water up','#a0824a');
  // top chamber (collector) - trapezoid widening up
  g+=`<path d="M${cx-70} 60 L${cx+70} 60 L${cx+55} 110 L${cx-55} 110 Z" fill="url(#${_cid('#8A5A34')})" stroke="${_rgba('#8A5A34',0.7)}" stroke-width="1.6"/>`;
  g+=`<text x="${cx}" y="82" fill="#f0e6d8" font-size="10.5" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">3. Top: brewed</text>`;
  g+=`<text x="${cx}" y="96" fill="${DIA.ink3}" font-size="9" text-anchor="middle" font-family="ui-sans-serif">coffee collects here</text>`;
  // middle: coffee basket (funnel) - small trapezoid
  g+=`<path d="M${cx-40} 118 L${cx+40} 118 L${cx+30} 150 L${cx-30} 150 Z" fill="url(#${_cid('#a0824a')})" stroke="${_rgba('#a0824a',0.8)}" stroke-width="1.4"/>`;
  // coffee grounds dots
  for(let i=0;i<10;i++){g+=`<circle cx="${cx-28+((i*13)%56)}" cy="${124+((i*7)%20)}" r="2" fill="#4a2f18"/>`;}
  g+=`<text x="${cx}" y="139" fill="#f0e6d8" font-size="9" font-weight="600" text-anchor="middle" font-family="ui-sans-serif">2. Grounds</text>`;
  // funnel stem down into base
  g+=`<rect x="${cx-4}" y="150" width="8" height="30" fill="${_rgba('#a0824a',0.5)}" stroke="${_rgba('#a0824a',0.7)}" stroke-width="1"/>`;
  // bottom chamber (boiler) - larger trapezoid
  g+=`<path d="M${cx-60} 180 L${cx+60} 180 L${cx+50} 235 L${cx-50} 235 Z" fill="url(#${_cid('#c0433a')})" stroke="${_rgba('#c0433a',0.7)}" stroke-width="1.6"/>`;
  // water fill
  g+=`<path d="M${cx-56} 205 L${cx+56} 205 L${cx+50} 233 L${cx-50} 233 Z" fill="${_rgba('#6a8fb0',0.4)}"/>`;
  g+=`<text x="${cx}" y="198" fill="#f0e6d8" font-size="10" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">1. Base: water</text>`;
  g+=`<text x="${cx}" y="222" fill="${_rgba('#cfe0f0',1)}" font-size="8.5" text-anchor="middle" font-family="ui-sans-serif">heat \u2192 steam \u2192 pressure</text>`;
  // upward flow arrows through stem
  g+=`<path d="M${cx} 205 L${cx} 156" stroke="#e0864a" stroke-width="2" marker-end="url(#darr)" opacity="0.9"/>`;
  g+=`<path d="M${cx} 118 L${cx} 100" stroke="#e0864a" stroke-width="2" marker-end="url(#darr)" opacity="0.9"/>`;
  // flame under base
  for(let i=-1;i<=1;i++){g+=`<path d="M${cx+i*18} 250 q4 -10 0 -16 q-4 6 0 16" fill="#e0864a" opacity="0.7"/>`;}
  // ---- RIGHT: moka vs espresso comparison ----
  g+=diaHeader(410,16,330,'Not quite espresso','pressure is the difference','#7a9a6a');
  const rows=[['Moka pot','~1\u20132 bar','#a0824a','bold, light crema'],['True espresso','~9 bar','#c0433a','syrupy, full crema']];
  rows.forEach((r,i)=>{const y=64+i*54;
    g+=diaCard(410,y,330,44,r[2],{r:9});
    g+=`<text x="426" y="${y+19}" fill="#f0e6d8" font-size="13" font-weight="700" font-family="ui-sans-serif">${r[0]}</text>`;
    g+=`<text x="426" y="${y+35}" fill="${DIA.ink3}" font-size="10" font-family="ui-sans-serif">${r[3]}</text>`;
    g+=`<text x="724" y="${y+27}" fill="${r[2]}" font-size="15" font-weight="800" text-anchor="end" font-family="ui-monospace">${r[1]}</text>`;
  });
  g+=`<text x="575" y="188" fill="#c9b8a4" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">Lands between espresso and a strong pour-over.</text>`;
  g+=`<text x="575" y="205" fill="${DIA.ink3}" font-size="10" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">Tip: start with HOT water, don't tamp, pull off at the gurgle.</text>`;
  g+=`<text x="${W/2}" y="${H-8}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">Bialetti's 1933 idea: fit cafe-style pressure brewing into a pot for the home stove.</text>`;
  return diaWrap(`${W} ${H}`,g,'How a moka pot brews, and why it sits just short of true espresso.');
}
// 58. Green-bean defect gallery — the SCA grading defects, as illustrated raw beans.
function diaGreenDefects(){
  const W=760,H=430;
  // a raw (green) coffee bean at (cx,cy), scale s, base fill, optional defect overlay
  const gbean=(cx,cy,s,fill,overlay)=>{
    let b=`<g transform="translate(${cx},${cy}) scale(${s})">`;
    b+=`<ellipse cx="0" cy="0" rx="30" ry="20" fill="${fill}" stroke="#3a4a2e" stroke-width="1.5"/>`;
    b+=`<path d="M0 -18 C -6 -8, 6 8, 0 18" fill="none" stroke="#3a4a2e" stroke-width="2" opacity="0.8"/>`;
    if(overlay==='fullblack'){ // whole bean blackened
      b+=`<ellipse cx="0" cy="0" rx="30" ry="20" fill="#100c08" opacity="0.9"/>`;
      b+=`<path d="M0 -18 C -6 -8, 6 8, 0 18" fill="none" stroke="#000" stroke-width="2" opacity="0.6"/>`;
    }
    if(overlay==='partblack'){ // half blackened
      b+=`<path d="M0 -20 A 30 20 0 0 0 0 20 Z" fill="#100c08" opacity="0.88"/>`;
    }
    if(overlay==='sour'){ // reddish-brown discoloration (sour bean)
      b+=`<ellipse cx="0" cy="0" rx="30" ry="20" fill="#7a3420" opacity="0.7"/>`;
      b+=`<ellipse cx="-8" cy="4" rx="10" ry="7" fill="#4a1c10" opacity="0.5"/>`;
    }
    if(overlay==='insect'){ // small dark boreholes
      [[-12,-6],[6,-8],[10,5],[-4,7],[16,-1]].forEach(p=>{b+=`<circle cx="${p[0]}" cy="${p[1]}" r="2.4" fill="#2a1408"/>`;});
    }
    if(overlay==='broken'){ // a piece cut off, pale exposed inner
      b+=`<path d="M13 -15 L30 -4 L27 9 L12 3 Z" fill="#c8c0a0"/>`;
      b+=`<path d="M13 -15 L30 -4 L27 9 L12 3 Z" fill="none" stroke="#3a4a2e" stroke-width="1"/>`;
    }
    if(overlay==='immature'){} // handled by pale fill + thin look
    if(overlay==='shell'){ // hollow ear-shape: draw a concave inner cut
      b+=`<path d="M-6 -16 C 14 -10, 14 10, -6 16 C 2 6, 2 -6, -6 -16 Z" fill="${DIA.bg}" opacity="0.65" stroke="#3a4a2e" stroke-width="1"/>`;
    }
    if(overlay==='floater'){ // faded/whitish, low-density
      b+=`<ellipse cx="0" cy="0" rx="30" ry="20" fill="#e8e4d0" opacity="0.4"/>`;
    }
    if(overlay==='fungus'){ // yellowish mold blotches
      b+=`<ellipse cx="-10" cy="-3" rx="7" ry="5" fill="#b8a83a" opacity="0.6"/>`;
      b+=`<ellipse cx="9" cy="6" rx="5" ry="4" fill="#9a8a2a" opacity="0.55"/>`;
    }
    b+=`</g>`;
    return b;
  };
  // cells: [name, base-fill, category tag, cause/look, overlay]
  const green='#6b7f4a', paleGreen='#9aa86a';
  const cells=[
    ['Healthy','#6b7f4a','—','even blue-green, dense',null],
    ['Full black','#6b7f4a','CAT 1','over-fermented / dead','fullblack'],
    ['Full sour','#6b7f4a','CAT 1','reddish-brown, over-fermented','sour'],
    ['Partial black','#6b7f4a','CAT 2','part of the bean blackened','partblack'],
    ['Insect damage','#6b7f4a','CAT 2','borer holes (broca)','insect'],
    ['Broken / chipped','#6b7f4a','CAT 2','cut, pale inner exposed','broken'],
    ['Immature','#9aa86a','CAT 2','pale, thin — silverskin sticks','immature'],
    ['Shell / ear','#6b7f4a','CAT 2','malformed hollow shape','shell'],
    ['Floater / fungus','#8a9a5a','CAT 2','faded, low-density / mold','fungus'],
  ];
  let g='';
  g+=`<text x="20" y="22" fill="${DIA.ink3}" font-size="11.5" font-family="ui-sans-serif" font-style="italic">Graders sort a 350g sample bean-by-bean. Category 1 = severe (disqualifies specialty); Category 2 = milder, counted by equivalence.</text>`;
  const cols=3,cw=W/cols,ch=128,y0=42;
  cells.forEach((c,i)=>{
    const col=i%cols,row=Math.floor(i/cols);
    const cx=col*cw+cw/2, cy=y0+row*ch;
    g+=`<rect x="${col*cw+12}" y="${cy-6}" width="${cw-24}" height="${ch-14}" rx="10" fill="#1a1e12" stroke="#2c3320" stroke-width="1"/>`;
    // category tag
    const tagCol = c[2]==='CAT 1' ? '#c0433a' : (c[2]==='CAT 2' ? '#c9a34e' : '#7a9a6a');
    if(c[2]!=='—') g+=`<text x="${col*cw+cw-24}" y="${cy+8}" fill="${tagCol}" font-size="8.5" font-weight="800" text-anchor="end" font-family="ui-monospace" letter-spacing="0.5">${c[2]}</text>`;
    g+=gbean(cx,cy+34,1.0,c[1],c[4]);
    g+=`<text x="${cx}" y="${cy+74}" fill="#f0e6d8" font-size="12.5" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${c[0]}</text>`;
    g+=`<text x="${cx}" y="${cy+90}" fill="${DIA.ink3}" font-size="9.5" text-anchor="middle" font-family="ui-sans-serif">${c[3]}</text>`;
  });
  return diaWrap(`${W} ${H}`,g,'A visual field guide to the common green-coffee defects and their SCA categories.');
}
// 59. Caturra & Catuai workhorse spotlight: the parent-offspring pair + shared traits.
function diaSpotWorkhorse(){
  const W=760,H=260;
  let g=diaDefs(['#c9a34e','#8fbf3a','#c86a6a','#B07B3E']);
  g=`<defs>${diaArrowMarker('#8a7660')}</defs>`+g;
  // lineage across the top: Bourbon -> Caturra -> (x Mundo Novo) -> Catuai
  g+=`<text x="30" y="26" fill="${DIA.ink3}" font-size="10.5" font-family="ui-monospace">THE LINEAGE</text>`;
  const chain=[['Bourbon','the founder','#c86a6a',40],['Caturra','dwarf mutation','#c9a34e',230],['Catua\u00ed','\u00d7 Mundo Novo','#8fbf3a',470]];
  chain.forEach((c,i)=>{
    g+=diaCard(c[3],36,150,40,c[2],{r:9,strong:i>0});
    g+=`<text x="${c[3]+75}" y="54" fill="#f0e6d8" font-size="13" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${c[0]}</text>`;
    g+=`<text x="${c[3]+75}" y="69" fill="${DIA.ink3}" font-size="9" text-anchor="middle" font-family="ui-sans-serif">${c[1]}</text>`;
    if(i<chain.length-1)g+=`<path d="M${c[3]+150} 56 l14 0" stroke="#8a7660" stroke-width="1.6" marker-end="url(#darr)"/>`;
  });
  // note that a workhorse note lives at right
  g+=diaCard(636,36,100,40,'#B07B3E',{r:9,shadow:false});
  g+=`<text x="686" y="53" fill="#f0e6d8" font-size="10.5" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">Everyday</text>`;
  g+=`<text x="686" y="68" fill="${DIA.ink3}" font-size="9" text-anchor="middle" font-family="ui-sans-serif">backbone</text>`;
  // two detail cards: Caturra vs Catuai
  const cards=[
    ['CATURRA','#c9a34e',30,['Bourbon mutation, Brazil ~1915\u201318','Compact \u2192 dense planting, easy pick','Bright citric, clean, light-med body','The WCR yield-reference baseline']],
    ['CATUA\u00cd','#8fbf3a',390,['Caturra \u00d7 Mundo Novo (1949\u201372)','~20% higher yield, ~2\u00d7 density','Cherries CLING (wind/rain/machine)','Balanced choc/nut; great w/ honey/natural']],
  ];
  cards.forEach(c=>{
    g+=diaCard(c[2],92,340,120,c[1],{r:11,title:c[0],titleSize:13});
    g+=`<line x1="${c[2]+16}" y1="118" x2="${c[2]+324}" y2="118" stroke="${_rgba(c[1],0.3)}" stroke-width="1"/>`;
    c[3].forEach((t,j)=>{
      g+=`<circle cx="${c[2]+20}" cy="${134+j*18}" r="2" fill="${c[1]}"/>`;
      g+=`<text x="${c[2]+30}" y="${138+j*18}" fill="#c9b8a4" font-size="10.5" font-family="ui-sans-serif">${t}</text>`;});
  });
  g+=`<text x="${W/2}" y="${H-8}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">Bred for productivity, not fame \u2014 they fill more cups than all the celebrated rarities combined. (Both rust-susceptible.)</text>`;
  return diaWrap(`${W} ${H}`,g,'The two workhorse varieties behind most Latin American coffee.');
}
// 60. Sample-roasting iteration loop: green -> sample roast -> cup -> adjust -> scale.
function diaProfiling(){
  const W=760,H=250;
  let g=diaDefs(['#7d9f4a','#C9A34E','#c86a4a','#8fbf3a','#B07B3E']);
  g=`<defs>${diaArrowMarker('#8a7660')}</defs>`+g;
  // the loop nodes around an oval
  const cx=264,cy=128,rx=178,ry=82;
  const nodes=[
    ['Green','assess density\n& moisture','#7d9f4a',-90],
    ['Sample roast','small batch,\nvary the curve','#C9A34E',-18],
    ['Cup','score blind,\nnote the flaws','#c86a4a',54],
    ['Adjust','change ONE\nvariable','#8fbf3a',126],
    ['Repeat','converge on\nthe target','#B07B3E',198],
  ];
  // draw connecting oval path (dashed) behind
  g+=`<ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" fill="none" stroke="${DIA.line}" stroke-dasharray="4 5"/>`;
  const pts=nodes.map(n=>{const a=n[3]*Math.PI/180;return [cx+Math.cos(a)*rx, cy+Math.sin(a)*ry];});
  // arrows along the loop
  nodes.forEach((n,i)=>{const p=pts[i],q=pts[(i+1)%nodes.length];
    const mx=(p[0]+q[0])/2,my=(p[1]+q[1])/2;
    g+=`<path d="M${p[0].toFixed(0)} ${p[1].toFixed(0)} Q${((p[0]+q[0])/2+ (cx-mx)*0.12).toFixed(0)} ${((p[1]+q[1])/2+(cy-my)*0.12).toFixed(0)} ${q[0].toFixed(0)} ${q[1].toFixed(0)}" stroke="#8a7660" stroke-width="1.5" fill="none" marker-end="url(#darr)" opacity="0.7"/>`;
  });
  nodes.forEach((n,i)=>{const p=pts[i];
    g+=`<circle cx="${p[0].toFixed(0)}" cy="${p[1].toFixed(0)}" r="15" fill="url(#${_cid(n[2])})" stroke="${n[2]}" stroke-width="2" filter="url(#dsoft)"/>`;
    g+=`<text x="${p[0].toFixed(0)}" y="${(p[1]+4).toFixed(0)}" fill="#f0e6d8" font-size="10" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${i+1}</text>`;
    // label outside the node
    const a=n[3]*Math.PI/180; const lx=p[0]+Math.cos(a)*34, ly=p[1]+Math.sin(a)*30;
    const anchor = Math.cos(a)>0.3?'start':(Math.cos(a)<-0.3?'end':'middle');
    g+=`<text x="${lx.toFixed(0)}" y="${(ly-4).toFixed(0)}" fill="${n[2]}" font-size="12" font-weight="700" text-anchor="${anchor}" font-family="ui-sans-serif">${n[0]}</text>`;
    n[1].split('\n').forEach((ln,j)=>{g+=`<text x="${lx.toFixed(0)}" y="${(ly+10+j*12).toFixed(0)}" fill="${DIA.ink3}" font-size="9" text-anchor="${anchor}" font-family="ui-sans-serif">${ln}</text>`;});
  });
  // scale-to-production card on the right
  g+=diaCard(560,80,180,90,'#B07B3E',{r:11,title:'THEN SCALE UP',titleSize:11.5});
  ['Re-map the curve to','the production roaster','(mass & airflow differ)','\u2014 then re-cup to confirm'].forEach((t,i)=>{
    g+=`<text x="650" y="${118+i*15}" fill="#c9b8a4" font-size="9.5" text-anchor="middle" font-family="ui-sans-serif">${t}</text>`;});
  g+=`<path d="M456 125 L556 125" stroke="#8a7660" stroke-width="1.6" marker-end="url(#darr)" opacity="0.7"/>`;
  g+=`<text x="${W/2}" y="${H-8}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">Change one variable at a time, cup blind, document everything \u2014 that's how a profile is built.</text>`;
  return diaWrap(`${W} ${H}`,g,'The sample-roasting loop: roast, cup, adjust one thing, repeat, then scale to production.');
}
// 61. Typica spotlight: the great journey out of Yemen + famous descendants.
function diaSpotTypica(){
  const W=760,H=260;
  let g=diaDefs(['#8fbf3a','#7d9f4a','#C9A34E','#c86a6a','#B07B3E']);
  g=`<defs>${diaArrowMarker('#8a7660')}</defs>`+g;
  // THE JOURNEY as a stepped chain
  g+=`<text x="30" y="24" fill="${DIA.ink3}" font-size="10.5" font-family="ui-monospace">THE GREAT JOURNEY (a chain of single plants)</text>`;
  const stops=[['Ethiopia','origin','#7d9f4a'],['Yemen','15\u201316th c.','#C9A34E'],['India','~1700','#B07B3E'],['Java','~1696\u201399','#8fbf3a'],['Amsterdam','1706','#c86a6a'],['Americas','early 1700s','#B07B3E']];
  const n=stops.length, x0=34, gap=(W-68)/(n-1), y=58;
  stops.forEach((s,i)=>{const x=x0+gap*i;
    g+=`<circle cx="${x}" cy="${y}" r="16" fill="url(#${_cid(s[2])})" stroke="${s[2]}" stroke-width="2" filter="url(#dsoft)"/>`;
    g+=`<text x="${x}" y="${y+4}" fill="#f0e6d8" font-size="9" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${i+1}</text>`;
    g+=`<text x="${x}" y="${y+32}" fill="${s[2]}" font-size="10.5" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${s[0]}</text>`;
    g+=`<text x="${x}" y="${y+45}" fill="${DIA.ink3}" font-size="8.5" text-anchor="middle" font-family="ui-sans-serif">${s[1]}</text>`;
    if(i<n-1)g+=`<path d="M${x+17} ${y} L${x+gap-17} ${y}" stroke="#8a7660" stroke-width="1.5" marker-end="url(#darr)" opacity="0.75"/>`;
  });
  g+=`<text x="${W/2}" y="122" fill="${DIA.ink3}" font-size="9.5" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">Until the 1940s, most Central & South American coffee was Typica.</text>`;
  // DESCENDANTS + the bargain, two cards
  g+=diaCard(30,140,350,80,'#8fbf3a',{r:11,title:'FAMOUS DESCENDANTS',titleSize:12});
  ['Jamaica Blue Mountain \u00b7 Hawaiian Kona','Maragogipe (the \u2018elephant bean\u2019 mutation)','a.k.a. Criollo \u00b7 Ar\u00e1bigo \u00b7 Pluma Hidalgo \u00b7 Sumatra'].forEach((t,i)=>{
    g+=`<text x="205" y="${165+i*17}" fill="#c9b8a4" font-size="10" text-anchor="middle" font-family="ui-sans-serif">${t}</text>`;});
  g+=diaCard(390,140,350,80,'#c86a6a',{r:11,title:'THE BARGAIN',titleSize:12});
  ['Cup: clean, elegant, sweet, refined','BUT ~20\u201330% lower yield than Bourbon','tall & rust-prone \u2192 quality-over-yield choice'].forEach((t,i)=>{
    g+=`<text x="565" y="${165+i*17}" fill="#c9b8a4" font-size="10" text-anchor="middle" font-family="ui-sans-serif">${t}</text>`;});
  g+=`<text x="${W/2}" y="${H-8}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">The coffee family began not with the most productive plant \u2014 but with the one that simply tasted wonderful.</text>`;
  return diaWrap(`${W} ${H}`,g,'The original Arabica: its journey around the world and its famous descendants.');
}
// 62. The rise of fine robusta: production growth bar + drivers + flavor reframe.
function diaRobustaRise(){
  const W=760,H=270;
  let g=diaDefs(['#a0824a','#7a9a6a','#c86a4a','#B07B3E','#8fbf3a']);
  // LEFT: the production-share growth (two bars 25% -> 40%)
  g+=diaHeader(24,16,330,'Robusta\u2019s share of world coffee','~25% \u2192 ~40% in 30 years','#a0824a');
  const bx=40,bw=90,bmax=150,by=200;
  [['early 1990s',25,'#7a6a52',bx],['today',40,'#a0824a',bx+150]].forEach(b=>{
    const h=b[1]/45*bmax;
    g+=`<rect x="${b[3]}" y="${by-h}" width="${bw}" height="${h}" rx="6" fill="url(#${_cid(b[2])})" stroke="${b[2]}" stroke-width="1.5" filter="url(#dsoft)"/>`;
    g+=`<text x="${b[3]+bw/2}" y="${by-h-8}" fill="#f0e6d8" font-size="16" font-weight="800" text-anchor="middle" font-family="ui-monospace">${b[1]}%</text>`;
    g+=`<text x="${b[3]+bw/2}" y="${by+16}" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">${b[0]}</text>`;
  });
  // growth arrow between bars
  g+=`<path d="M${bx+bw+8} ${by-25/45*bmax} Q${bx+bw+40} ${by-90} ${bx+150-8} ${by-40/45*bmax-4}" stroke="#8fbf3a" stroke-width="2" fill="none" opacity="0.7"/>`;
  g+=`<text x="${bx+bw+42}" y="${by-96}" fill="#8fbf3a" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">rising</text>`;
  g+=`<line x1="380" y1="30" x2="380" y2="240" stroke="${DIA.line}" stroke-dasharray="4 5"/>`;
  // RIGHT: two driver cards + a flavor reframe strip
  g+=diaHeader(404,16,330,'Why it\u2019s rising','and being taken seriously','#7a9a6a');
  const drivers=[['Climate + cost','#c86a4a',['Grows low/hot, resists rust,','yields more \u00b7 Arabica pricey (>$4/lb)']],
                 ['Quality movement','#8fbf3a',['Vietnam, Uganda, India apply','specialty processing \u2014 washed/anaerobic']]];
  drivers.forEach((dv,i)=>{const y=52+i*58;
    g+=diaCard(404,y,330,48,dv[1],{r:9});
    g+=`<text x="418" y="${y+20}" fill="${dv[1]}" font-size="12.5" font-weight="800" font-family="ui-sans-serif">${dv[0]}</text>`;
    dv[2].forEach((t,j)=>{g+=`<text x="418" y="${y+33+j*12}" fill="#c9b8a4" font-size="9.5" font-family="ui-sans-serif">${t}</text>`;});
  });
  g+=diaCard(404,172,330,44,'#B07B3E',{r:9,shadow:false});
  g+=`<text x="418" y="190" fill="#f0e6d8" font-size="11" font-weight="700" font-family="ui-sans-serif">Fine robusta = its own category</text>`;
  g+=`<text x="418" y="206" fill="${DIA.ink3}" font-size="9.5" font-family="ui-sans-serif">choc/nut/savory + thick crema + ~2\u00d7 caffeine. CQI Q-Robusta grading now exists.</text>`;
  g+=`<text x="${W/2}" y="${H-8}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">The bean once written off as inferior is now treated as a serious part of coffee\u2019s future.</text>`;
  return diaWrap(`${W} ${H}`,g,'How robusta went from instant-jar footnote to nearly half the world\u2019s coffee.');
}
// 63. Particle-size distribution: unimodal (flat burr) vs bimodal (conical) curves.
function diaParticleSize(){
  const W=760,H=270;
  let g=diaDefs(['#6a8fb0','#c86a4a','#c9a34e']);
  // graph frame
  const gx0=70,gx1=690,gy0=54,gy1=180;
  g+=`<line x1="${gx0}" y1="${gy1}" x2="${gx1}" y2="${gy1}" stroke="${DIA.line}" stroke-width="1.5"/>`;
  g+=`<line x1="${gx0}" y1="${gy0}" x2="${gx0}" y2="${gy1}" stroke="${DIA.line}" stroke-width="1.5"/>`;
  g+=`<text x="${(gx0+gx1)/2}" y="${gy1+34}" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">particle size \u2192 (fine to coarse, microns)</text>`;
  g+=`<text x="${gx0-8}" y="${gy0-2}" fill="${DIA.ink3}" font-size="9" text-anchor="end" font-family="ui-sans-serif"># of particles</text>`;
  // x helper
  const X=f=>gx0+f*(gx1-gx0);
  const Y=v=>gy1-v*(gy1-gy0); // v in 0..1
  // gaussian helper
  const gauss=(x,mu,sig)=>Math.exp(-0.5*Math.pow((x-mu)/sig,2));
  // UNIMODAL (flat burr) - single tight peak, blue
  let uni='';
  for(let i=0;i<=100;i++){const f=i/100;const v=gauss(f,0.52,0.1);uni+=(i?'L':'M')+X(f).toFixed(1)+' '+Y(v*0.92).toFixed(1)+' ';}
  g+=`<path d="${uni} L${X(1)} ${gy1} L${gx0} ${gy1} Z" fill="url(#${_cid('#6a8fb0')})"/>`;
  g+=`<path d="${uni}" fill="none" stroke="#6a8fb0" stroke-width="2.5"/>`;
  // BIMODAL (conical) - main peak + fines spike, red/orange
  let bi='';
  for(let i=0;i<=100;i++){const f=i/100;const v=gauss(f,0.55,0.11)*0.8+gauss(f,0.14,0.05)*0.5;bi+=(i?'L':'M')+X(f).toFixed(1)+' '+Y(v*0.92).toFixed(1)+' ';}
  g+=`<path d="${bi}" fill="none" stroke="#c86a4a" stroke-width="2.5" stroke-dasharray="1 0"/>`;
  // mark fines + boulders zones
  g+=`<line x1="${X(0.14)}" y1="${gy0}" x2="${X(0.14)}" y2="${gy1}" stroke="#c86a4a" stroke-width="1" stroke-dasharray="3 3" opacity="0.6"/>`;
  g+=`<text x="${X(0.14)}" y="${gy0+10}" fill="#c86a4a" font-size="10" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">FINES</text>`;
  g+=`<text x="${X(0.14)}" y="${gy0+24}" fill="${DIA.ink3}" font-size="8" text-anchor="middle" font-family="ui-sans-serif">over-extract</text>`;
  g+=`<text x="${X(0.14)}" y="${gy0+34}" fill="${DIA.ink3}" font-size="8" text-anchor="middle" font-family="ui-sans-serif">= bitter</text>`;
  g+=`<line x1="${X(0.9)}" y1="${gy0}" x2="${X(0.9)}" y2="${gy1}" stroke="#c9a34e" stroke-width="1" stroke-dasharray="3 3" opacity="0.6"/>`;
  g+=`<text x="${X(0.9)}" y="${gy0+10}" fill="#c9a34e" font-size="10" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">BOULDERS</text>`;
  g+=`<text x="${X(0.9)}" y="${gy0+24}" fill="${DIA.ink3}" font-size="8" text-anchor="middle" font-family="ui-sans-serif">under-extract</text>`;
  g+=`<text x="${X(0.9)}" y="${gy0+34}" fill="${DIA.ink3}" font-size="8" text-anchor="middle" font-family="ui-sans-serif">= sour</text>`;
  // legend
  g+=`<rect x="${gx0+10}" y="${gy0+6}" width="18" height="3" fill="#6a8fb0"/><text x="${gx0+32}" y="${gy0+10}" fill="#c9b8a4" font-size="9.5" font-family="ui-sans-serif">Flat burr \u2014 unimodal (clarity)</text>`;
  g+=`<rect x="${gx0+10}" y="${gy0+22}" width="18" height="3" fill="#c86a4a"/><text x="${gx0+32}" y="${gy0+26}" fill="#c9b8a4" font-size="9.5" font-family="ui-sans-serif">Conical \u2014 bimodal (body, more fines)</text>`;
  g+=`<text x="${W/2}" y="${H-30}" fill="#f0e6d8" font-size="11.5" text-anchor="middle" font-family="ui-sans-serif">A wide spread has fines AND boulders \u2014 so a bad grind tastes bitter and sour at the same time.</text>`;
  g+=`<text x="${W/2}" y="${H-12}" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">Uniformity (a tight distribution), not just the average size, is what a good burr grinder buys you.</text>`;
  return diaWrap(`${W} ${H}`,g,'Two grinders at the same average size can pour very different cups \u2014 the distribution is why.');
}
// 64. Coffee leaf rust: the history timeline + the Red Queen breeding arms race.
function diaRustStory(){
  const W=760,H=280;
  let g=diaDefs(['#c9843a','#c0433a','#7a9a6a','#8fbf3a']);
  g=`<defs>${diaArrowMarker('#8a7660')}</defs>`+g;
  // TIMELINE across the top
  g+=`<text x="24" y="22" fill="${DIA.ink3}" font-size="10.5" font-family="ui-monospace">THE SPREAD</text>`;
  const ty=64;
  g+=`<line x1="60" y1="${ty}" x2="700" y2="${ty}" stroke="${DIA.line}" stroke-width="2"/>`;
  const events=[
    ['1861','first seen','Lake Victoria','#7a9a6a',90],
    ['1869','Ceylon collapse','\u2192 replanted as TEA','#c0433a',250],
    ['1869\u201385','spreads worldwide','nearly every region','#c9843a',430],
    ['2012','the Big Rust','C. America, \u201335% yield','#c0433a',600],
  ];
  events.forEach(e=>{
    g+=`<circle cx="${e[4]}" cy="${ty}" r="7" fill="${e[3]}" stroke="${DIA.bg}" stroke-width="2" filter="url(#dsoft)"/>`;
    g+=`<text x="${e[4]}" y="${ty-30}" fill="${e[3]}" font-size="13" font-weight="800" text-anchor="middle" font-family="ui-monospace">${e[0]}</text>`;
    g+=`<text x="${e[4]}" y="${ty-15}" fill="#f0e6d8" font-size="10" font-weight="600" text-anchor="middle" font-family="ui-sans-serif">${e[1]}</text>`;
    g+=`<text x="${e[4]}" y="${ty+22}" fill="${DIA.ink3}" font-size="9" text-anchor="middle" font-family="ui-sans-serif">${e[2]}</text>`;
  });
  // the fungus fact strip
  g+=diaCard(60,104,640,40,'#c9843a',{r:10,shadow:false});
  g+=`<text x="76" y="122" fill="#c9843a" font-size="11.5" font-weight="800" font-family="ui-sans-serif">Hemileia vastatrix</text>`;
  g+=`<text x="76" y="136" fill="#c9b8a4" font-size="10" font-family="ui-sans-serif">obligate fungus \u00b7 orange spores under the leaf \u2192 early leaf drop \u00b7 spreads by wind/rain + on tools \u00b7 germinates ~13\u201331\u00b0C</text>`;
  // THE ARMS RACE (bottom): resistance vs evolving fungus
  g+=`<text x="24" y="172" fill="${DIA.ink3}" font-size="10.5" font-family="ui-monospace">THE RED QUEEN (a breeding arms race)</text>`;
  g+=diaCard(60,182,300,72,'#7a9a6a',{r:11,title:'BREED RESISTANCE',titleSize:11.5});
  ['H\u00edbrido de Timor (natural Arabica\u00d7Robusta)','\u2192 Catimor, Sarchimor families','resistance bred into the crop'].forEach((t,i)=>{
    g+=`<text x="210" y="${218+i*15}" fill="#c9b8a4" font-size="10" text-anchor="middle" font-family="ui-sans-serif">${t}</text>`;});
  // vs arrows both ways
  g+=`<path d="M366 206 L${396} 206" stroke="#8a7660" stroke-width="1.6" marker-end="url(#darr)"/>`;
  g+=`<path d="M${396} 230 L366 230" stroke="#8a7660" stroke-width="1.6" marker-end="url(#darr)"/>`;
  g+=`<text x="381" y="200" fill="${DIA.ink3}" font-size="9" text-anchor="middle" font-family="ui-sans-serif">vs</text>`;
  g+=diaCard(402,182,298,72,'#c0433a',{r:11,title:'FUNGUS EVOLVES',titleSize:11.5});
  ['New virulence races emerge','\u2192 break the bred-in resistance','\u2192 must re-breed, forever'].forEach((t,i)=>{
    g+=`<text x="551" y="${218+i*15}" fill="#c9b8a4" font-size="10" text-anchor="middle" font-family="ui-sans-serif">${t}</text>`;});
  g+=`<text x="${W/2}" y="${H-6}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">Resistance is never permanent \u2014 you run just to stay in place, and climate change now hands rust new ground.</text>`;
  return diaWrap(`${W} ${H}`,g,'How one fungus reshaped the coffee world \u2014 and why the fight against it never ends.');
}
// 65. Coffee berry borer: its life inside the bean + the gut-bacteria caffeine trick.
function diaBorerStory(){
  const W=760,H=270;
  let g=diaDefs(['#a0764a','#c0433a','#7a9a6a','#c9a34e']);
  g=`<defs>${diaArrowMarker('#8a7660')}</defs>`+g;
  // LEFT: cherry with a borer hole + tunnel into the seed
  g+=diaHeader(24,16,330,'A life inside the bean','sprays can\u2019t reach it','#a0764a');
  const ccx=150,ccy=140;
  // cherry
  g+=`<circle cx="${ccx}" cy="${ccy}" r="58" fill="#000" opacity="0.28" filter="url(#dsoft)"/>`;
  g+=`<circle cx="${ccx}" cy="${ccy}" r="56" fill="#b53a2e"/>`;
  g+=`<circle cx="${ccx}" cy="${ccy}" r="42" fill="#d98a4a" opacity="0.6"/>`;
  // the two seeds
  g+=`<path d="M${ccx} ${ccy-30} A20 30 0 0 0 ${ccx} ${ccy+30} L${ccx-2} ${ccy+30} A20 30 0 0 1 ${ccx-2} ${ccy-30} Z" fill="#9aaf6e" stroke="#5a4632" stroke-width="1.2"/>`;
  g+=`<path d="M${ccx} ${ccy-30} A20 30 0 0 1 ${ccx} ${ccy+30} L${ccx+2} ${ccy+30} A20 30 0 0 0 ${ccx+2} ${ccy-30} Z" fill="#8aa05e" stroke="#5a4632" stroke-width="1.2"/>`;
  // bore hole at the tip + tunnel
  g+=`<circle cx="${ccx}" cy="${ccy-56}" r="4.5" fill="#1a1008"/>`;
  g+=`<path d="M${ccx} ${ccy-54} q-6 20 -2 40" stroke="#1a1008" stroke-width="2.5" fill="none" stroke-dasharray="2 2"/>`;
  // the beetle (small) at the hole
  g+=`<ellipse cx="${ccx+14}" cy="${ccy-64}" rx="7" ry="4.5" fill="#2a1a10" stroke="#a0764a" stroke-width="1"/>`;
  g+=`<line x1="${ccx+8}" y1="${ccy-66}" x2="${ccx+3}" y2="${ccy-70}" stroke="#2a1a10" stroke-width="1"/>`;
  g+=`<text x="${ccx+34}" y="${ccy-62}" fill="${DIA.ink3}" font-size="9" font-family="ui-sans-serif">female bores in</text>`;
  g+=`<text x="${ccx}" y="${ccy+80}" fill="#c9b8a4" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">tunnels the seed \u00b7 lays eggs \u00b7 larvae eat</text>`;
  g+=`<text x="${ccx}" y="${ccy+95}" fill="${DIA.ink3}" font-size="9.5" text-anchor="middle" font-family="ui-sans-serif">the bean from the inside \u2192 up to 80% loss</text>`;
  g+=`<line x1="380" y1="30" x2="380" y2="240" stroke="${DIA.line}" stroke-dasharray="4 5"/>`;
  // RIGHT: the caffeine gut-bacteria trick
  g+=diaHeader(404,16,330,'How it beats caffeine','a borrowed superpower','#7a9a6a');
  // caffeine = pesticide card
  g+=diaCard(404,52,330,40,'#c0433a',{r:9,shadow:false});
  g+=`<text x="418" y="70" fill="#c0433a" font-size="11.5" font-weight="800" font-family="ui-sans-serif">Caffeine = the plant\u2019s pesticide</text>`;
  g+=`<text x="418" y="84" fill="${DIA.ink3}" font-size="9.5" font-family="ui-sans-serif">toxic to nearly every other insect at bean levels</text>`;
  g+=`<path d="M569 96 L569 108" stroke="#8a7660" stroke-width="1.6" marker-end="url(#darr)"/>`;
  // gut bacteria card
  g+=diaCard(404,112,330,56,'#7a9a6a',{r:9});
  g+=`<text x="418" y="132" fill="#7a9a6a" font-size="11.5" font-weight="800" font-family="ui-sans-serif">Gut bacteria (Pseudomonas)</text>`;
  g+=`<text x="418" y="147" fill="#c9b8a4" font-size="9.5" font-family="ui-sans-serif">living in the beetle\u2019s gut break caffeine down</text>`;
  g+=`<text x="418" y="160" fill="#c9b8a4" font-size="9.5" font-family="ui-sans-serif">and eat it \u2014 as carbon + nitrogen (food)</text>`;
  g+=`<path d="M569 172 L569 184" stroke="#8a7660" stroke-width="1.6" marker-end="url(#darr)"/>`;
  g+=diaCard(404,188,330,32,'#c9a34e',{r:9,shadow:false});
  g+=`<text x="569" y="208" fill="#f0e6d8" font-size="11" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">Kill the microbes \u2192 the beetle can\u2019t detox caffeine</text>`;
  g+=`<text x="${W/2}" y="${H-8}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">With rust, the borer is one of coffee\u2019s two great enemies \u2014 both worsening as the climate warms.</text>`;
  return diaWrap(`${W} ${H}`,g,'The beetle that lives inside the bean, and the gut microbes that let it eat caffeine.');
}
// 66. Latte-art pour, taught kanji-stroke-order style: each pattern as numbered
// movement steps with directional arrows showing the pour, step by step.
function diaPourStroke(){
  const W=760,H=420;
  let g=diaDefs(['#c9a34e','#B07B3E','#7a9a6a','#a0764a']);
  g=`<defs>${diaArrowMarker('#e8dcc8')}</defs>`+g;
  // a coffee cup (top-down) at (cx,cy) radius r; crema brown, optional white milk shapes on top
  const cup=(cx,cy,r)=>`<circle cx="${cx}" cy="${cy}" r="${r+3}" fill="#2a1a10" stroke="#4a3018" stroke-width="1.5"/><circle cx="${cx}" cy="${cy}" r="${r}" fill="url(#${_cid('#a0764a')})"/><circle cx="${cx}" cy="${cy}" r="${r}" fill="#6E3E1E" opacity="0.55"/>`;
  const white='#f0e6d8';
  // step number badge
  const badge=(cx,cy,n,col)=>`<circle cx="${cx}" cy="${cy}" r="10" fill="url(#${_cid(col)})" stroke="${col}" stroke-width="1.5" filter="url(#dsoft)"/><text x="${cx}" y="${cy+4}" fill="#f0e6d8" font-size="11" font-weight="800" text-anchor="middle" font-family="ui-monospace">${n}</text>`;
  const rowLabel=(y,name,col,desc)=>diaHeader(20,y,300,name,desc,col);
  const R=26; // cup radius
  const xs=[110,270,430,590]; // up to 4 steps per row
  const stepText=(cx,y,t)=>`<text x="${cx}" y="${y}" fill="${DIA.ink3}" font-size="9.5" text-anchor="middle" font-family="ui-sans-serif">${t}</text>`;

  // ---- ROW 1: THE HEART ----
  let cy=78;
  g+=rowLabel(20,'The Heart','#c9a34e','pour, fill, then cut through');
  // step 1: pour high, thin stream, milk sinks (no white)
  g+=cup(xs[0],cy,R);
  g+=`<path d="M${xs[0]} ${cy-40} L${xs[0]} ${cy-8}" stroke="#e8dcc8" stroke-width="2.5" marker-end="url(#darr)"/>`;
  g+=stepText(xs[0],cy+42,'pour high & thin');g+=stepText(xs[0],cy+54,'(milk sinks in)');g+=badge(xs[0]-30,cy-24,1,'#c9a34e');
  // step 2: drop low & close, white disc grows
  g+=cup(xs[1],cy,R);g+=`<circle cx="${xs[1]}" cy="${cy+4}" r="13" fill="${white}"/>`;
  g+=`<path d="M${xs[1]} ${cy-34} L${xs[1]} ${cy-6}" stroke="#e8dcc8" stroke-width="3.5" marker-end="url(#darr)"/>`;
  g+=stepText(xs[1],cy+42,'drop low & close');g+=stepText(xs[1],cy+54,'a white disc grows');g+=badge(xs[1]-30,cy-24,2,'#c9a34e');
  // step 3: disc fills the cup
  g+=cup(xs[2],cy,R);g+=`<circle cx="${xs[2]}" cy="${cy}" r="19" fill="${white}"/>`;
  g+=stepText(xs[2],cy+42,'let it fill out');g+=stepText(xs[2],cy+54,'to a round pad');g+=badge(xs[2]-30,cy-24,3,'#c9a34e');
  // step 4: cut through fast, high, to the top -> heart
  g+=cup(xs[3],cy,R);
  g+=`<path d="M${xs[3]} ${cy+16} C ${xs[3]-9} ${cy+2}, ${xs[3]-16} ${cy-10}, ${xs[3]-8} ${cy-14} C ${xs[3]-2} ${cy-17}, ${xs[3]} ${cy-8}, ${xs[3]} ${cy-6} C ${xs[3]} ${cy-8}, ${xs[3]+2} ${cy-17}, ${xs[3]+8} ${cy-14} C ${xs[3]+16} ${cy-10}, ${xs[3]+9} ${cy+2}, ${xs[3]} ${cy+16} Z" fill="${white}"/>`;
  g+=`<path d="M${xs[3]} ${cy-30} L${xs[3]} ${cy+22}" stroke="#c0433a" stroke-width="1.6" stroke-dasharray="3 3" marker-end="url(#darr)"/>`;
  g+=stepText(xs[3],cy+42,'cut up through it');g+=stepText(xs[3],cy+54,'fast \u2192 a heart');g+=badge(xs[3]-30,cy-24,4,'#c9a34e');

  // ---- ROW 2: THE ROSETTA ----
  cy=214;
  g+=rowLabel(156,'The Rosetta','#7a9a6a','wiggle side to side, then draw through');
  g+=cup(xs[0],cy,R);g+=`<circle cx="${xs[0]}" cy="${cy+6}" r="11" fill="${white}"/>`;
  g+=`<path d="M${xs[0]} ${cy-34} L${xs[0]} ${cy-6}" stroke="#e8dcc8" stroke-width="3" marker-end="url(#darr)"/>`;
  g+=stepText(xs[0],cy+42,'settle a base');g+=stepText(xs[0],cy+54,'low & close');g+=badge(xs[0]-30,cy-24,1,'#7a9a6a');
  // step 2: wiggle the pitcher -> leaves start (zigzag arrow)
  g+=cup(xs[1],cy,R);
  for(let i=0;i<5;i++){const yy=cy-12+i*7;g+=`<ellipse cx="${xs[1]}" cy="${yy}" rx="${13-i*1.2}" ry="3.2" fill="${white}"/>`;}
  g+=`<path d="M${xs[1]-10} ${cy-20} L${xs[1]+10} ${cy-14} L${xs[1]-10} ${cy-6} L${xs[1]+10} ${cy+2} L${xs[1]-10} ${cy+10}" stroke="#e8dcc8" stroke-width="2" fill="none" marker-end="url(#darr)"/>`;
  g+=stepText(xs[1],cy+42,'wiggle side-to-side');g+=stepText(xs[1],cy+54,'as you draw back');g+=badge(xs[1]-30,cy-24,2,'#7a9a6a');
  // step 3: leaves fill the cup, moving toward you
  g+=cup(xs[2],cy,R);
  for(let i=0;i<7;i++){const yy=cy-16+i*5.5;g+=`<ellipse cx="${xs[2]}" cy="${yy}" rx="${17-Math.abs(i-3)*2}" ry="2.8" fill="${white}"/>`;}
  g+=`<path d="M${xs[2]} ${cy-26} L${xs[2]} ${cy+6}" stroke="#e8dcc8" stroke-width="2.5" marker-end="url(#darr)"/>`;
  g+=stepText(xs[2],cy+42,'keep pulling back');g+=stepText(xs[2],cy+54,'leaves stack up');g+=badge(xs[2]-30,cy-24,3,'#7a9a6a');
  // step 4: draw a line straight through -> finished fern
  g+=cup(xs[3],cy,R);
  for(let i=0;i<7;i++){const yy=cy-16+i*5.5;g+=`<ellipse cx="${xs[3]}" cy="${yy}" rx="${17-Math.abs(i-3)*2}" ry="2.8" fill="${white}"/>`;}
  g+=`<rect x="${xs[3]-1.5}" y="${cy-19}" width="3" height="40" fill="${white}"/>`;
  g+=`<path d="M${xs[3]} ${cy-26} L${xs[3]} ${cy+24}" stroke="#c0433a" stroke-width="1.6" stroke-dasharray="3 3" marker-end="url(#darr)"/>`;
  g+=stepText(xs[3],cy+42,'draw through the');g+=stepText(xs[3],cy+54,'middle \u2192 a fern');g+=badge(xs[3]-30,cy-24,4,'#7a9a6a');

  // ---- ROW 3: THE TULIP ----
  cy=350;
  g+=rowLabel(292,'The Tulip','#B07B3E','stack pushes, then pull through');
  g+=cup(xs[0],cy,R);g+=`<circle cx="${xs[0]}" cy="${cy+6}" r="10" fill="${white}"/>`;
  g+=`<path d="M${xs[0]} ${cy-32} L${xs[0]} ${cy-4}" stroke="#e8dcc8" stroke-width="3" marker-end="url(#darr)"/>`;
  g+=stepText(xs[0],cy+42,'push a first blob');g+=badge(xs[0]-30,cy-24,1,'#B07B3E');
  // step 2: stop, push a second blob behind it
  g+=cup(xs[1],cy,R);g+=`<circle cx="${xs[1]}" cy="${cy+9}" r="8" fill="${white}"/><circle cx="${xs[1]}" cy="${cy-1}" r="10" fill="${white}"/>`;
  g+=`<path d="M${xs[1]} ${cy-30} L${xs[1]} ${cy-9}" stroke="#e8dcc8" stroke-width="3" marker-end="url(#darr)"/>`;
  g+=`<text x="${xs[1]+30}" y="${cy-14}" fill="${DIA.ink3}" font-size="9" font-family="ui-sans-serif">stop \u00b7 push again</text>`;
  g+=stepText(xs[1],cy+42,'stop, push behind');g+=badge(xs[1]-30,cy-24,2,'#B07B3E');
  // step 3: repeat -> stacked blobs
  g+=cup(xs[2],cy,R);[10,1,-8].forEach((dy,i)=>g+=`<circle cx="${xs[2]}" cy="${cy+dy}" r="${9-i*0.5}" fill="${white}"/>`);
  g+=stepText(xs[2],cy+42,'repeat = a stack');g+=stepText(xs[2],cy+54,'of nested cups');g+=badge(xs[2]-30,cy-24,3,'#B07B3E');
  // step 4: pull a line through all -> tulip
  g+=cup(xs[3],cy,R);[10,1,-8].forEach((dy,i)=>g+=`<circle cx="${xs[3]}" cy="${cy+dy}" r="${9-i*0.5}" fill="${white}"/>`);
  g+=`<rect x="${xs[3]-1.5}" y="${cy-18}" width="3" height="34" fill="${white}"/>`;
  g+=`<path d="M${xs[3]} ${cy-28} L${xs[3]} ${cy+20}" stroke="#c0433a" stroke-width="1.6" stroke-dasharray="3 3" marker-end="url(#darr)"/>`;
  g+=stepText(xs[3],cy+42,'pull through \u2192');g+=stepText(xs[3],cy+54,'a tulip');g+=badge(xs[3]-30,cy-24,4,'#B07B3E');

  return diaWrap(`${W} ${H}`,g,'The three foundational pours, taught one movement at a time \u2014 sink a base, texture the surface, then cut or pull through to finish.');
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
    case 'processing':return diaProcessing();
    case 'milk':return diaMilk();
    case 'brewfamilies':return diaBrewFamilies();
    case 'water':return diaWater();
    case 'roasters':return diaRoasters();
    case 'waves':return diaWaves();
    case 'supplychain':return diaSupplyChain();
    case 'blend':return diaBlend();
    case 'cherry':return diaCherry();
    case 'vartree':return diaVarTree();
    case 'pourover':return diaPourover();
    case 'coldbrew':return diaColdBrew();
    case 'troubleshoot':return diaTroubleshoot();
    case 'milkdrinks':return diaMilkDrinks();
    case 'decaf':return diaDecaf();
    case 'coffeemap':return diaCoffeeMap();
    case 'caffeine':return diaCaffeine();
    case 'espmachine':return diaEspMachine();
    case 'tastemap':return diaTasteMap();
    case 'latteart':return diaLatteArt();
    case 'waterrecipe':return diaWaterRecipe();
    case 'grinder':return diaGrinder();
    case 'puckprep':return diaPuckPrep();
    case 'staling':return diaStaling();
    case 'acidmap':return diaAcidMap();
    case 'dialring':return diaDialRing();
    case 'milkstretch':return diaMilkStretch();
    case 'maintenance':return diaMaintenance();
    case 'aromachem':return diaAromaChem();
    case 'scapath':return diaScaPath();
    case 'cherrybyproduct':return diaCherryByproduct();
    case 'teacoffee':return diaTeaCoffee();
    case 'machtypes':return diaMachTypes();
    case 'waterchem':return diaWaterChem();
    case 'cmarket':return diaCmarket();
    case 'climatecoffee':return diaClimateCoffee();
    case 'historytimeline':return diaHistoryTimeline();
    case 'familytree':return diaFamilyTree();
    case 'speciesmap':return diaSpeciesMap();
    case 'decafmethods':return diaDecafMethods();
    case 'instantcoffee':return diaInstantCoffee();
    case 'esphistory':return diaEspHistory();
    case 'geishastory':return diaGeishaStory();
    case 'roastdefects':return diaRoastDefects();
    case 'spotsl28':return diaSpotSl28();
    case 'spotbourbon':return diaSpotBourbon();
    case 'spotpacamara':return diaSpotPacamara();
    case 'spotmaragogipe':return diaSpotMaragogipe();
    case 'caffeinescience':return diaCaffeineScience();
    case 'fermentmethods':return diaFermentMethods();
    case 'mokapot':return diaMokaPot();
    case 'greendefects':return diaGreenDefects();
    case 'spotworkhorse':return diaSpotWorkhorse();
    case 'profiling':return diaProfiling();
    case 'spottypica':return diaSpotTypica();
    case 'robustarise':return diaRobustaRise();
    case 'particlesize':return diaParticleSize();
    case 'ruststory':return diaRustStory();
    case 'borerstory':return diaBorerStory();
    case 'pourstroke':return diaPourStroke();
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
  return `<svg viewBox="0 0 ${W} ${H}" width="100%" style="max-width:110px" role="img" aria-label="Illustration of a ${esc(kind)} coffee bean">${inner}</svg>`;
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
// If this page is a step on the guided path, show a "next" nudge.
// If this page is a step on the guided path, show a "next" nudge.
function relatedBlock(rel){
  if(!rel||!rel.length)return '';
  const chips=rel.map(id=>{const m=METHODOLOGY[id];if(!m)return '';return `<button class="relchip" onclick="go('meth','${id}')">${esc(m.name)}</button>`;}).join('');
  return `<div class="related"><span class="related-label">Related</span><div class="relchips">${chips}</div></div>`;
}
function pathNav(id){
  const i=PATH.findIndex(s=>s.id===id);
  if(i<0)return '';
  const next=i<PATH.length-1?PATH[i+1]:null;
  return `<div class="pathnav">
    <span class="pathnav-label">Guided path · step ${i+1} of ${PATH.length}</span>
    ${next?`<button class="pathnav-next" onclick="go('meth','${next.id}')"><span>Next: ${esc(next.label)}</span><span class="pathnav-why">${esc(next.why)}</span></button>`
      :`<div class="pathnav-done">That's the path — you've got the fundamentals. Explore anything from here.</div>`}
  </div>`;
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
    <button class="back sticky" onclick="goBack('learn')">← All topics</button>
    <div class="dhead" style="border-bottom:none;padding-bottom:6px">
      <div class="txt">
        <div class="lvl" style="color:${m.accent}">${esc(glabel)}</div>
        <h1>${esc(m.name)}</h1>
        <div class="sub">${esc(m.sub)}</div>
      </div>
    </div>
    ${m.sections.map((s,i)=>`<div class="msection"><h3>${esc(s.h)}</h3><p>${linkTerms(s.body, m.name)}</p></div>${i===0&&m.diagram?diagram(m.diagram):''}`).join('')}
    ${m.visuals?`<div class="msection"><h3>${esc(m.visuals.title||'Defect Reference')}</h3>${m.visuals.note?`<p>${esc(m.visuals.note)}</p>`:''}${beanGallery(m.visuals.beans)}</div>`:''}
    ${m.keypoints?`<div class="keypoints"><h4>Key Points</h4><ul style="margin:0;padding:0">${m.keypoints.map(k=>`<li>${esc(k)}</li>`).join('')}</ul></div>`:''}
    ${relatedBlock(m.related)}
    ${refsBlock(m.refs)}
    ${pathNav(id)}
    ${sibBlock}
    <div style="height:40px"></div>
  </div>`;
}

/* ---------- GLOBAL SEARCH ---------- */
function openSearch(){
  const ov=document.getElementById('searchoverlay');
  ov.style.display='flex';
  document.body.style.overflow='hidden';
  const inp=document.getElementById('globalsearch');
  inp.value='';
  document.getElementById('searchresults').innerHTML=searchEmptyState();
  setTimeout(()=>inp.focus(),30);
  inp.oninput=()=>runGlobalSearch(inp.value);
}
function closeSearch(){
  document.getElementById('searchoverlay').style.display='none';
  document.body.style.overflow='';
}
function searchEmptyState(){
  return `<div class="searchhint">Search across everything — try <b>first crack</b>, <b>Ethiopia</b>, <b>espresso ratio</b>, <b>mucilage</b>, or <b>direct trade</b>.</div>`;
}
function goFromSearch(view,arg){closeSearch();go(view,arg);}
function runGlobalSearch(q){
  const box=document.getElementById('searchresults');
  const norm=s=>s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');
  q=norm(q).trim();
  if(!q){box.innerHTML=searchEmptyState();return;}
  const results={profiles:[],origins:[],learn:[],glossary:[]};
  // profiles
  Object.entries(PROFILES).forEach(([id,p])=>{
    const hay=norm([p.name,p.sub,p.level,p.oneLine,p.useFor,(p.aka||[]).join(' ')].join(' '));
    if(hay.includes(q))results.profiles.push([id,p.name,p.level]);
  });
  // origins + learn (both in METHODOLOGY)
  Object.entries(METHODOLOGY).forEach(([id,m])=>{
    if(id==='origin_intro')return;
    const secText=(m.sections||[]).map(s=>s.h+' '+s.body).join(' ');
    const kp=(m.keypoints||[]).join(' ');
    const hay=norm(m.name+' '+m.sub+' '+secText+' '+kp);
    if(hay.includes(q)){
      if(m.group==='origin')results.origins.push([id,m.name,m.roastLevel||'']);
      else{const gl=METH_GROUPS.find(g=>g[0]===m.group);results.learn.push([id,m.name,gl?gl[1]:'']);}
    }
  });
  // glossary
  GLOSSARY.forEach(g=>{
    if(norm(g.term+' '+g.def).includes(q))results.glossary.push(g);
  });
  const total=results.profiles.length+results.origins.length+results.learn.length+results.glossary.length;
  if(!total){box.innerHTML=`<div class="searchhint">No matches for "${esc(q)}". Try a broader term.</div>`;return;}
  let html='';
  const section=(title,items,render)=>{
    if(!items.length)return '';
    return `<div class="searchgroup"><div class="searchglabel">${title} · ${items.length}</div>${items.slice(0,8).map(render).join('')}${items.length>8?`<div class="searchmore">+${items.length-8} more — keep typing to narrow</div>`:''}</div>`;
  };
  html+=section('Roast Profiles',results.profiles,r=>`<button class="searchitem" onclick="goFromSearch('profile','${r[0]}')"><span class="si-name">${esc(r[1])}</span><span class="si-meta">${esc(r[2])}</span></button>`);
  html+=section('Origins',results.origins,r=>`<button class="searchitem" onclick="goFromSearch('origin','${r[0]}')"><span class="si-name">${esc(r[1])}</span><span class="si-meta">${esc(r[2])}</span></button>`);
  html+=section('Learn',results.learn,r=>`<button class="searchitem" onclick="goFromSearch('meth','${r[0]}')"><span class="si-name">${esc(r[1])}</span><span class="si-meta">${esc(r[2])}</span></button>`);
  html+=section('Glossary',results.glossary,g=>`<button class="searchitem gloss" onclick="goFromSearch('start')"><span class="si-name">${esc(g.term)}</span><span class="si-def">${esc(g.def.slice(0,90))}${g.def.length>90?'…':''}</span></button>`);
  box.innerHTML=html;
}
// keyboard: Esc closes, "/" opens
document.addEventListener('keydown',e=>{
  if(e.key==='Escape')closeSearch();
  if(e.key==='/'&&document.getElementById('searchoverlay').style.display==='none'&&document.activeElement.tagName!=='INPUT'){e.preventDefault();openSearch();}
});
document.getElementById('searchoverlay').addEventListener('click',e=>{if(e.target.id==='searchoverlay')closeSearch();});

/* ---------- GLOSSARY TOOLTIPS ---------- */
// Build a lookup of glossary terms (lowercased) -> definition, plus a regex to find them.
let GLOSS_MAP={}, GLOSS_RE=null;
(function buildGloss(){
  GLOSSARY.forEach(g=>{GLOSS_MAP[g.term.toLowerCase()]=g.def;});
  // Alias triggers: extra words that should surface an existing definition, keyed to the fullest term.
  const findDef=frag=>{const g=GLOSSARY.find(x=>x.term.toLowerCase().includes(frag));return g?g.def:null;};
  const ALIASES={
    'maillard':findDef('maillard'),'caramelization':findDef('maillard'),'browning':findDef('maillard'),
    'first crack':findDef('first crack'),'second crack':findDef('second crack'),
    'rate of rise':findDef('rate of rise'),'development time ratio':findDef('development time ratio'),
    'drum roaster':findDef('drum'),'fluid-bed':findDef('fluid-bed'),'fluid bed':findDef('fluid-bed'),
    'washed':findDef('washed'),'natural process':findDef('washed'),'honey process':findDef('washed'),
    'mucilage':"The sticky, sugary fruit layer clinging to the coffee seed under the skin. How much of it is left on during drying defines washed vs honey vs natural processing.",
    'chlorogenic acids':"Acids abundant in green coffee that break down as it roasts — high in light roasts (bright, sometimes harsh), broken into bitter-tasting compounds in darker roasts.",
    'chlorogenic':"Acids abundant in green coffee that break down as it roasts — high in light roasts, broken into bitter compounds when darker.",
    'endothermic':"A reaction that absorbs heat. First crack is endothermic — the beans briefly pull in energy, which can crash the rate of rise if unmanaged.",
    'exothermic':"A reaction that releases heat. Dense coffees can turn exothermic after first crack, adding energy the roaster didn't put in.",
    'microlot':"A small, separated batch of coffee from a specific plot, day, or process — kept apart because it's distinctive enough to be worth more.",
    'single origin':"Coffee from one place — one country, region, farm, or lot — sold unblended to showcase that origin's character.",
    'direct trade':"A roaster buying green coffee straight from a specific producer, usually above market price, for quality and traceability. A relationship, not a certification.",
    'c-price':"The benchmark futures-market price for commodity-grade Arabica. Volatile; acts as the reference floor that specialty premiums are quoted against.",
    'agtron':findDef('agtron'),'degassing':findDef('degassing'),'quaker':findDef('quaker'),'robusta':findDef('robusta'),
    'water activity':findDef('water activity'),'screen size':findDef('screen size'),'extraction yield':findDef('extraction'),'tds':findDef('tds'),
  };
  Object.entries(ALIASES).forEach(([k,v])=>{if(v&&!GLOSS_MAP[k])GLOSS_MAP[k]=v;});
  const terms=Object.keys(GLOSS_MAP).sort((a,b)=>b.length-a.length)
    .map(t=>t.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'));
  const B=String.fromCharCode(92)+'b'; // word boundary, escaping-safe
  GLOSS_RE=new RegExp(B+'('+terms.join('|')+')'+B,'i');
})();
// Given a plain-text body, wrap the FIRST occurrence of any glossary term in a tappable span.
// Only links one term per body paragraph to avoid clutter. Skips if term equals the page title.
function linkTerms(text, skipTerm){
  if(!GLOSS_RE)return esc(text);
  // We escape first, then inject markup around a matched term.
  const m=GLOSS_RE.exec(text);
  if(!m)return esc(text);
  const term=m[1];
  if(skipTerm && term.toLowerCase()===skipTerm.toLowerCase())return esc(text);
  const idx=m.index;
  const before=esc(text.slice(0,idx));
  const hit=esc(text.slice(idx,idx+term.length));
  const after=esc(text.slice(idx+term.length));
  const key=term.toLowerCase().replace(/"/g,'');
  return `${before}<span class="termref" onclick="showTerm(event,'${key}')">${hit}</span>${after}`;
}
function showTerm(ev,key){
  ev.stopPropagation();
  const def=GLOSS_MAP[key]; if(!def)return;
  closeTermPop();
  const pop=document.createElement('div');
  pop.className='termpop';
  pop.id='termpop';
  pop.innerHTML=`<div class="termpop-term"></div><div class="termpop-def">${esc(def)}</div>`;
  // capitalize term nicely
  pop.querySelector('.termpop-term').textContent=key.replace(/\b\w/g,c=>c.toUpperCase());
  document.body.appendChild(pop);
  const r=ev.target.getBoundingClientRect();
  const pw=Math.min(300,window.innerWidth-24);
  pop.style.width=pw+'px';
  let left=r.left+window.scrollX; if(left+pw>window.scrollX+window.innerWidth-12)left=window.scrollX+window.innerWidth-pw-12;
  pop.style.left=Math.max(12,left)+'px';
  pop.style.top=(r.bottom+window.scrollY+8)+'px';
  setTimeout(()=>document.addEventListener('click',closeTermPop,{once:true}),10);
}
function closeTermPop(){const p=document.getElementById('termpop');if(p)p.remove();}

go('home');

if('serviceWorker' in navigator){
  window.addEventListener('load',()=>{navigator.serviceWorker.register('sw.js').catch(()=>{});});
}
</script>
</body>
</html>"""

out = HTML.replace("__DATA__", DATA_JSON)

# Smooth every COUNTRY_SIL path into flowing Bezier curves (coastline look).
_n_smoothed = [0]
def _smooth_paths(mobj):
    block = mobj.group(1)
    def repl(pm):
        _n_smoothed[0] += 1
        return pm.group(1) + smooth_silhouette(pm.group(2)) + pm.group(3)
    new_block = re.sub(r"(:')([ML][^']*)(')", repl, block)
    return "const COUNTRY_SIL={" + new_block + "\n};"

out = re.sub(r"const COUNTRY_SIL=\{(.*?)\n\};", _smooth_paths, out, flags=re.S)
print(f"Smoothed {_n_smoothed[0]} country silhouettes into Bezier curves")

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
