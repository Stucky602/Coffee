#!/usr/bin/env python3
"""Build the self-contained 'Coffee - An Industry Guide' HTML PWA from JSON data."""
import json, pathlib, re, shutil

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

def smooth_silhouette(d, tension=0.55, subdivide=False):
    # Real Natural-Earth outlines already carry fine detail, so we DON'T subdivide
    # (that would round off real features like peninsulas). A gentle Catmull-Rom pass
    # just softens the simplified straight segments into natural coastline curves.
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

APP_VERSION = "v81"
CACHE_C = "coffee-guide-v81"

# Illustrated raster diagrams (PNG) that ship alongside index.html in ./img/.
# These read better as art than hand-drawn SVG. Listed here so the build copies
# them into the output and the service worker precaches them for offline use.
IMG_ASSETS = ["latteart.png", "roasters.png"]

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
.diagram-img img{display:block;width:100%;height:auto;border-radius:8px}
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
  const tag=showGroup?`<span class="k">${esc(METH_GROUPS.find(g=>g[0]===m.group)?.[1]||'')}</span>`:'';
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
  // Real country outlines derived from Natural Earth (public-domain cartographic data),
  // simplified to clean silhouettes and normalized to a ~100x100 box. Accurate shapes.
  // v71: point density ~2-3x higher (span-relative tolerance) so smoothing removes the last spikiness.
  'Brazil':'M16.8 8.2 L19.5 11.7 L21.2 11.1 L21.8 11.9 L27.0 8.1 L27.1 7.5 L25.4 7.2 L25.0 4.5 L23.5 2.7 L28.4 4.5 L28.8 3.4 L33.2 2.0 L34.1 0.3 L35.7 0.7 L35.3 2.1 L36.9 3.6 L35.7 6.8 L36.6 9.2 L38.6 10.5 L43.1 8.5 L46.0 8.9 L46.0 7.2 L53.7 8.0 L57.5 2.6 L59.4 8.2 L61.3 9.4 L61.5 10.7 L58.0 13.8 L56.2 17.1 L54.4 17.6 L56.3 17.7 L59.0 16.0 L60.2 18.8 L63.0 18.0 L62.2 20.4 L63.2 18.5 L65.4 17.4 L66.0 15.5 L68.2 15.3 L72.8 17.1 L73.2 18.0 L73.8 17.4 L74.9 18.1 L74.6 19.4 L75.6 19.7 L74.7 21.8 L76.0 19.9 L76.1 20.8 L78.1 19.7 L83.0 21.1 L86.8 20.9 L94.0 26.2 L98.1 26.7 L98.9 27.8 L100.0 32.2 L99.6 35.1 L98.0 38.0 L93.5 42.3 L91.2 46.4 L89.7 46.2 L88.9 58.8 L87.6 60.2 L87.3 63.6 L84.3 67.8 L84.2 69.7 L82.4 70.5 L81.5 72.2 L78.7 71.6 L78.5 72.3 L74.9 72.4 L72.8 74.3 L69.2 75.5 L65.8 78.5 L64.5 78.3 L65.3 78.9 L64.4 80.6 L64.3 86.5 L61.9 88.5 L58.9 93.4 L56.0 95.6 L59.8 91.3 L57.9 90.2 L58.0 92.1 L56.2 93.7 L54.5 98.2 L52.6 99.7 L52.2 98.2 L53.3 97.1 L51.6 95.4 L46.9 92.3 L45.9 92.9 L43.8 90.4 L41.8 90.6 L46.6 85.6 L51.4 82.8 L51.9 80.5 L51.0 78.9 L49.5 78.9 L50.4 75.0 L47.4 74.7 L46.4 70.6 L40.9 69.9 L41.3 67.2 L40.4 65.1 L41.2 64.6 L40.5 64.0 L42.1 60.1 L39.8 57.6 L39.9 55.2 L35.3 55.1 L34.2 52.1 L35.0 52.1 L34.4 48.8 L31.2 48.1 L23.0 44.2 L22.0 42.3 L22.0 38.4 L18.9 38.9 L13.7 42.0 L8.6 41.7 L8.8 37.7 L7.1 39.0 L4.6 39.1 L4.1 37.9 L2.0 37.6 L2.6 36.6 L0.0 32.9 L2.2 30.1 L2.8 26.7 L8.2 24.3 L10.3 24.6 L11.7 16.7 L10.0 14.0 L10.1 12.1 L12.4 11.9 L12.0 10.9 L10.6 10.9 L10.6 9.3 L14.9 9.2 L14.8 8.5 L15.5 9.2 L16.8 8.2Z',
  'Colombia':'M60.9 2.2 L56.0 4.5 L51.6 9.5 L49.7 15.8 L47.5 19.4 L49.4 19.0 L50.9 19.9 L53.4 24.8 L52.9 29.4 L55.7 32.3 L63.3 32.0 L66.9 32.8 L71.2 37.8 L80.6 36.8 L82.8 37.5 L80.8 42.9 L80.6 47.5 L81.8 51.4 L83.9 54.1 L80.6 57.8 L82.0 57.8 L84.5 60.2 L86.4 66.4 L86.5 67.2 L85.2 67.5 L85.0 64.3 L83.3 61.9 L80.1 64.1 L78.6 62.6 L78.7 64.2 L68.6 64.3 L68.6 68.2 L71.8 68.3 L72.8 70.6 L67.4 71.1 L67.3 75.4 L69.9 77.6 L71.3 81.7 L67.9 100.0 L65.7 97.5 L63.3 97.3 L67.1 90.5 L61.9 87.8 L59.3 88.6 L57.2 87.5 L54.4 89.0 L50.1 88.9 L48.8 88.2 L48.5 85.6 L46.7 84.7 L45.7 82.1 L42.2 80.4 L38.9 75.8 L33.0 74.0 L30.1 71.9 L28.7 73.2 L23.3 72.2 L21.5 69.5 L17.8 68.3 L13.5 64.8 L14.9 63.5 L16.2 63.9 L16.1 60.4 L20.8 58.3 L25.2 51.1 L24.1 51.2 L24.0 50.2 L23.5 50.9 L23.2 49.1 L22.6 49.3 L24.0 46.2 L22.5 41.3 L24.2 39.9 L22.9 37.5 L23.5 35.1 L20.3 31.2 L21.1 28.3 L22.5 29.1 L24.5 26.7 L22.8 23.5 L23.3 22.7 L27.0 26.9 L26.2 23.1 L30.0 20.6 L31.5 18.3 L33.9 17.8 L34.5 13.3 L33.4 13.7 L35.0 10.9 L38.6 7.9 L41.7 8.5 L40.6 9.4 L41.3 9.9 L42.8 6.6 L47.8 6.7 L54.1 3.2 L54.9 1.4 L57.4 0.0 L60.1 0.5 L60.9 2.2Z',
  'Ethiopia':'M15.5 75.3 L13.2 72.0 L11.3 66.7 L5.9 61.0 L0.0 58.0 L1.8 54.8 L6.3 54.7 L7.2 53.8 L7.1 47.6 L8.7 43.1 L8.4 40.8 L10.4 38.5 L11.8 39.4 L12.8 38.6 L14.0 32.2 L17.8 26.8 L20.7 26.1 L23.5 15.9 L26.8 15.8 L28.4 14.6 L30.5 16.6 L32.6 11.9 L36.2 14.8 L40.5 13.4 L41.3 14.4 L47.6 14.6 L52.2 16.9 L62.6 27.9 L58.7 33.1 L58.7 37.8 L66.2 37.7 L64.4 40.3 L65.7 43.0 L70.0 48.5 L73.3 51.0 L93.3 57.7 L100.0 57.7 L79.7 78.3 L70.6 78.7 L67.6 80.1 L65.8 82.3 L60.2 83.5 L59.3 84.6 L54.3 84.7 L51.8 82.6 L45.6 85.4 L43.3 88.1 L33.9 86.8 L26.0 81.7 L20.1 81.3 L18.4 79.0 L18.3 75.5 L15.5 75.3Z',
  'Kenya':'M10.8 63.9 L11.2 52.3 L16.5 43.8 L19.6 41.8 L21.3 36.6 L20.6 29.6 L16.1 22.9 L16.0 18.1 L13.3 16.5 L11.5 12.5 L24.2 0.0 L24.7 1.3 L26.2 0.7 L28.9 1.5 L29.0 6.7 L31.6 10.1 L40.3 10.6 L51.9 18.1 L65.7 20.0 L69.2 16.1 L78.2 12.0 L81.9 15.0 L89.2 14.9 L80.2 26.3 L80.3 62.6 L85.8 70.7 L83.2 73.1 L79.5 73.9 L79.5 76.3 L77.0 79.0 L74.7 79.1 L72.9 80.4 L71.8 86.0 L69.3 89.2 L64.6 99.5 L62.7 100.0 L49.1 90.1 L47.2 88.4 L47.5 84.0 L10.8 63.9Z',
  'Vietnam':'M64.8 12.5 L61.0 14.0 L60.6 15.5 L59.3 16.3 L56.1 15.9 L56.6 17.7 L55.0 20.7 L51.3 23.1 L48.9 29.7 L50.7 32.8 L54.8 36.6 L54.7 38.1 L54.0 38.0 L63.9 47.6 L65.2 47.6 L70.6 54.0 L73.8 64.3 L73.6 68.3 L74.8 72.9 L74.1 71.8 L73.3 72.6 L73.5 77.2 L71.7 81.4 L60.0 87.8 L58.3 86.0 L57.9 87.8 L56.4 86.9 L55.6 87.3 L56.6 88.5 L54.6 88.5 L56.8 89.7 L55.5 91.4 L52.4 89.0 L55.3 92.9 L54.0 93.5 L50.3 90.5 L52.6 94.6 L48.1 96.6 L45.4 99.8 L43.1 100.0 L44.0 99.0 L43.6 93.2 L45.3 90.9 L40.8 87.7 L43.7 86.9 L45.0 85.7 L45.0 84.3 L46.8 84.8 L49.8 83.8 L52.6 85.1 L52.5 83.5 L50.5 81.7 L50.4 79.4 L51.5 78.6 L54.2 79.1 L54.3 77.3 L61.7 74.5 L61.5 69.9 L62.3 67.2 L60.5 62.5 L61.9 59.0 L61.5 56.7 L62.7 54.9 L59.4 51.1 L60.9 49.5 L57.2 46.3 L55.9 46.5 L54.9 43.3 L45.4 33.5 L45.7 31.8 L37.2 27.4 L38.3 26.2 L38.1 24.9 L41.9 25.3 L44.2 22.6 L43.6 21.3 L40.4 19.7 L41.8 18.3 L38.6 16.3 L35.4 18.0 L31.8 16.6 L30.1 14.1 L30.8 11.3 L29.9 10.4 L28.8 11.3 L25.2 6.6 L27.5 4.0 L31.0 6.1 L33.3 3.9 L34.5 5.1 L35.3 3.8 L37.5 5.5 L38.9 3.7 L40.4 4.3 L42.5 3.5 L43.8 1.4 L46.5 0.0 L50.4 2.9 L52.5 2.5 L56.7 3.8 L55.2 5.7 L55.9 9.3 L58.0 9.6 L60.6 11.8 L63.4 11.5 L64.8 12.5Z',
  'India':'M0.0 42.9 L1.9 42.5 L2.1 41.3 L5.6 41.8 L9.9 41.0 L8.5 36.7 L6.6 35.9 L6.8 33.8 L4.6 33.0 L4.7 31.7 L7.7 28.6 L9.0 29.7 L12.7 28.8 L17.9 22.1 L22.2 18.3 L21.9 15.6 L24.6 14.2 L20.0 10.9 L19.9 9.1 L20.9 8.3 L19.7 7.9 L19.9 5.9 L25.9 6.4 L33.0 3.0 L33.9 3.0 L34.9 6.0 L37.1 7.1 L36.2 8.1 L37.9 13.3 L35.1 13.2 L36.3 17.3 L37.5 17.0 L44.1 21.3 L42.0 22.8 L40.8 25.8 L50.0 30.3 L54.6 30.4 L58.6 33.0 L68.0 34.2 L68.5 28.9 L70.8 28.7 L70.6 31.5 L72.0 32.8 L81.7 32.6 L82.0 31.1 L80.5 29.5 L83.6 29.1 L86.0 26.5 L90.7 24.2 L93.4 25.1 L95.6 23.7 L96.7 24.4 L95.9 25.5 L97.0 25.1 L97.5 26.1 L96.4 27.3 L100.0 27.9 L98.5 30.1 L99.2 31.7 L96.1 31.2 L92.5 33.5 L92.5 35.4 L90.6 37.9 L91.0 38.8 L89.0 42.8 L86.3 42.2 L86.4 45.4 L84.9 49.3 L83.7 49.3 L82.6 43.5 L81.5 43.5 L80.4 45.9 L78.9 43.8 L79.6 42.1 L81.3 41.7 L83.4 39.2 L74.3 38.0 L73.8 34.8 L72.7 35.5 L71.5 34.1 L70.9 34.7 L69.3 33.6 L68.3 35.9 L71.3 38.1 L69.6 38.3 L68.1 40.3 L70.5 41.5 L70.0 43.5 L71.2 45.2 L71.6 50.5 L70.6 50.7 L70.2 48.9 L70.0 50.4 L68.4 50.5 L68.7 48.8 L67.8 48.0 L68.6 48.9 L67.9 49.9 L64.1 51.9 L64.5 53.7 L63.7 55.1 L61.9 56.5 L58.6 57.0 L59.3 57.4 L54.7 62.0 L48.7 66.1 L48.3 67.9 L45.0 68.7 L43.9 70.7 L41.6 70.8 L40.8 73.0 L41.6 78.5 L40.8 78.1 L41.8 78.9 L39.5 85.9 L40.0 89.3 L38.2 89.5 L37.0 91.9 L38.6 93.2 L35.2 93.5 L33.9 96.0 L32.1 97.0 L28.8 94.2 L28.1 90.7 L17.7 68.3 L16.2 60.8 L16.6 59.5 L15.9 59.3 L16.5 58.6 L15.4 56.7 L16.2 53.8 L15.3 51.1 L17.0 50.1 L15.0 50.3 L15.0 48.7 L15.9 48.5 L13.8 48.3 L13.3 49.9 L14.0 50.9 L13.2 52.2 L9.8 53.6 L8.0 53.2 L2.8 48.3 L6.9 47.3 L8.0 45.5 L3.7 46.4 L0.9 43.9 L2.1 42.9 L0.2 43.8 L0.0 42.9Z',
  'Mexico':'M0.0 20.7 L7.9 20.1 L7.6 20.8 L20.0 24.7 L29.4 24.6 L29.4 23.2 L35.2 23.2 L40.2 27.1 L41.9 30.4 L45.7 32.3 L47.8 29.8 L51.7 29.8 L58.1 37.1 L59.4 40.7 L65.8 42.3 L64.1 47.5 L63.5 53.7 L65.7 59.6 L69.9 65.8 L72.3 66.2 L74.7 68.0 L81.3 66.3 L84.3 67.0 L85.2 66.5 L84.6 65.6 L86.9 64.1 L88.2 58.6 L94.4 56.8 L98.8 56.6 L100.0 58.2 L97.0 63.2 L97.8 63.3 L96.6 67.4 L95.7 65.8 L92.1 69.2 L86.1 69.2 L86.1 71.0 L84.7 71.0 L88.0 73.8 L87.9 74.9 L83.6 74.9 L82.1 77.5 L82.0 79.9 L78.9 77.0 L76.5 75.0 L75.0 74.2 L76.2 75.1 L73.2 73.8 L73.6 74.4 L67.9 76.3 L53.6 71.2 L50.1 68.7 L45.1 67.5 L38.4 62.0 L37.7 60.7 L39.1 60.1 L38.3 59.3 L39.3 57.0 L37.3 53.3 L30.8 47.2 L31.7 47.2 L30.2 46.8 L29.1 45.2 L29.9 45.3 L26.7 43.9 L27.1 43.1 L25.5 43.1 L26.4 41.4 L25.9 40.4 L21.9 37.8 L21.7 36.1 L19.8 35.7 L16.4 32.2 L13.4 26.9 L13.4 25.1 L7.2 22.8 L8.5 28.9 L14.0 34.2 L17.3 40.0 L17.9 40.3 L17.6 39.3 L18.3 39.9 L21.3 47.7 L22.3 48.5 L22.6 47.6 L25.4 50.5 L24.1 52.3 L16.7 46.0 L16.3 42.5 L13.1 39.1 L11.6 39.8 L7.0 36.5 L10.1 36.7 L9.4 35.8 L10.1 34.2 L4.8 29.8 L0.0 20.7Z',
  'Peru':'M77.6 22.9 L73.0 22.6 L72.1 23.5 L67.3 24.4 L61.6 27.8 L59.7 33.1 L60.2 35.1 L56.8 37.5 L57.1 39.7 L55.5 41.1 L61.1 48.9 L59.8 51.2 L64.4 51.7 L65.5 54.4 L70.6 54.2 L74.4 51.3 L73.9 59.9 L79.7 59.6 L84.6 68.1 L83.0 70.1 L82.4 74.5 L83.5 77.2 L80.9 80.6 L81.9 83.0 L80.5 85.2 L81.7 88.0 L83.7 89.0 L79.4 93.7 L80.0 95.4 L78.2 96.5 L77.8 99.2 L75.1 100.0 L70.1 96.4 L69.0 94.3 L49.5 84.0 L45.0 79.7 L42.5 75.5 L43.4 72.8 L38.3 65.7 L37.9 63.5 L35.7 61.4 L29.5 46.8 L22.8 36.8 L16.5 32.9 L16.4 31.9 L17.7 31.7 L17.9 30.6 L15.4 25.3 L16.0 22.9 L21.0 18.3 L21.8 21.0 L20.1 21.7 L20.8 22.8 L20.1 24.0 L22.0 23.2 L24.7 24.1 L26.4 26.7 L28.0 26.9 L29.9 24.7 L31.8 18.3 L32.8 18.7 L34.4 16.1 L40.9 13.8 L46.9 8.1 L47.8 4.8 L48.7 5.0 L48.6 3.0 L46.6 0.4 L48.8 0.0 L52.2 1.8 L54.2 5.1 L57.4 6.6 L58.3 9.0 L59.9 9.8 L60.1 12.2 L61.3 12.9 L65.3 12.9 L67.8 11.5 L69.7 12.5 L72.1 11.8 L76.9 14.3 L73.4 20.4 L75.5 20.6 L77.6 22.9Z',
  'Papua New Guinea':'M1.1 74.9 L1.1 52.7 L0.0 51.1 L1.1 47.1 L1.1 9.7 L20.5 16.8 L26.5 17.9 L32.1 21.7 L36.2 21.9 L42.3 27.1 L44.8 27.5 L49.1 31.9 L48.9 37.7 L67.1 44.2 L69.5 46.8 L69.9 50.3 L62.6 50.9 L61.0 52.0 L63.4 57.5 L68.7 62.5 L72.7 64.7 L73.9 69.2 L76.0 70.6 L77.3 74.2 L83.5 74.0 L84.1 78.7 L91.6 80.6 L89.1 81.8 L90.2 83.8 L95.1 85.6 L100.0 86.1 L97.9 87.1 L96.0 86.8 L98.0 88.9 L94.7 90.3 L91.7 89.5 L89.0 87.3 L69.2 84.4 L61.6 77.6 L60.7 76.2 L61.1 74.3 L60.0 74.6 L57.8 73.2 L51.8 64.5 L41.2 61.7 L40.1 60.0 L36.5 59.4 L35.7 60.5 L32.8 61.3 L28.0 58.3 L30.8 63.1 L29.8 63.1 L29.7 64.0 L26.6 63.7 L27.5 65.7 L16.6 66.9 L14.9 65.4 L13.5 65.7 L14.6 65.7 L16.1 67.4 L19.4 67.1 L22.5 68.4 L25.2 71.3 L25.1 73.3 L17.9 77.0 L13.7 75.4 L2.7 75.9 L1.1 74.9Z',
  'Guatemala':'M0.9 80.2 L2.7 76.6 L2.1 73.5 L2.8 69.9 L4.8 67.2 L1.7 62.3 L13.1 42.8 L44.7 42.7 L45.5 34.9 L40.1 32.0 L38.3 27.2 L31.8 23.3 L21.1 13.7 L31.3 13.8 L31.4 0.0 L76.2 0.0 L74.4 47.1 L82.8 47.2 L89.9 50.3 L91.6 48.2 L90.1 45.7 L99.1 51.2 L81.1 65.3 L76.0 68.1 L74.7 72.3 L76.0 78.7 L73.2 80.6 L71.3 83.3 L66.1 84.0 L66.8 87.6 L54.5 95.9 L53.1 97.6 L53.3 100.0 L40.8 95.3 L27.6 95.4 L21.9 93.8 L11.1 87.9 L0.9 80.2Z',
  'Costa Rica':'M100.0 51.6 L97.6 53.7 L92.9 51.1 L88.7 55.4 L88.7 67.0 L93.4 69.1 L95.1 71.3 L90.5 74.7 L89.4 76.6 L91.3 79.7 L91.1 85.2 L86.1 88.6 L89.6 92.8 L90.6 96.6 L88.5 93.3 L83.3 88.2 L82.1 81.2 L78.4 78.9 L75.2 77.3 L72.9 77.6 L74.3 80.2 L78.0 83.6 L78.2 86.6 L68.9 84.4 L65.0 80.4 L68.6 74.7 L67.9 67.8 L64.9 64.3 L60.2 60.6 L53.5 57.5 L50.4 55.0 L39.7 51.8 L37.3 49.5 L37.8 45.2 L35.7 41.9 L26.4 35.5 L19.3 31.3 L20.1 35.7 L22.3 38.4 L28.3 40.9 L30.5 44.3 L25.4 48.9 L24.8 50.8 L23.7 51.4 L17.7 44.6 L8.5 41.9 L3.3 35.0 L1.7 30.2 L2.3 27.0 L7.3 19.9 L7.2 16.7 L0.0 12.1 L4.7 9.5 L4.9 7.2 L9.7 3.4 L29.9 10.7 L36.1 7.5 L46.6 9.6 L52.0 15.6 L59.5 17.0 L65.6 15.4 L67.2 13.9 L67.8 11.5 L73.5 25.0 L76.6 29.5 L83.2 37.7 L86.1 39.2 L93.6 48.8 L100.0 51.6Z',
  'Honduras':'M100.0 42.1 L93.9 42.3 L92.3 44.0 L85.4 45.4 L84.0 46.5 L82.6 46.0 L79.1 47.7 L76.0 47.4 L72.6 45.0 L70.5 46.0 L69.7 48.3 L67.7 49.6 L67.4 52.6 L59.3 58.4 L58.5 60.4 L54.5 58.6 L53.5 57.3 L48.8 61.8 L42.0 62.2 L42.7 69.2 L40.1 69.9 L38.7 73.3 L37.1 74.3 L32.6 74.5 L32.7 72.8 L31.4 72.1 L30.2 68.5 L25.0 67.8 L26.2 66.9 L25.5 65.8 L26.5 61.1 L25.1 59.9 L22.1 60.0 L19.5 58.3 L14.2 60.4 L13.7 58.4 L10.6 57.6 L3.9 52.1 L0.0 51.4 L3.1 48.3 L2.3 44.1 L3.5 40.8 L6.5 39.5 L18.3 30.2 L19.8 30.7 L24.0 27.8 L26.8 27.3 L28.1 27.3 L30.2 29.2 L33.5 28.5 L39.6 29.7 L48.4 29.3 L55.2 26.6 L54.4 25.5 L62.5 27.5 L67.7 27.2 L70.7 26.0 L76.0 27.7 L77.4 29.0 L79.6 28.6 L78.0 27.9 L82.2 28.7 L90.2 35.4 L86.9 33.6 L84.6 34.0 L84.9 35.5 L87.6 35.6 L90.3 38.4 L93.0 37.7 L94.5 38.4 L92.1 36.0 L96.6 38.1 L97.9 40.7 L100.0 42.1Z',
  'Nicaragua':'M100.0 2.8 L97.3 6.8 L95.9 4.8 L94.3 6.5 L95.2 7.9 L96.9 8.2 L99.3 17.3 L94.4 24.9 L90.9 39.9 L92.1 48.2 L91.5 55.9 L92.2 60.0 L90.3 60.4 L89.6 59.0 L90.3 53.3 L89.6 55.6 L86.8 58.0 L89.1 62.8 L88.4 68.6 L86.5 67.8 L86.4 70.7 L85.1 72.2 L87.9 73.0 L89.0 77.1 L87.0 78.8 L84.3 84.7 L86.5 91.1 L87.7 92.8 L89.3 93.1 L87.7 96.1 L83.1 97.2 L77.6 96.2 L73.6 91.8 L65.8 90.2 L61.2 92.5 L46.2 87.1 L42.7 89.9 L37.9 84.0 L26.6 75.0 L20.3 65.7 L0.1 49.1 L0.0 47.8 L1.9 46.0 L6.2 48.7 L7.4 47.5 L13.5 47.2 L15.8 45.8 L16.7 42.0 L21.3 40.0 L19.9 31.5 L20.8 30.1 L29.7 29.9 L33.7 25.0 L36.1 23.7 L37.4 25.6 L41.7 28.3 L42.9 28.0 L44.1 25.2 L55.2 17.2 L55.6 13.2 L58.4 11.4 L59.5 8.2 L62.3 6.9 L67.0 10.2 L71.3 10.6 L72.6 9.5 L75.4 9.4 L76.0 8.3 L78.0 8.9 L79.9 7.4 L81.9 7.7 L89.4 5.4 L91.6 3.2 L100.0 2.8Z',
  'El Salvador':'M28.7 23.5 L39.1 26.4 L41.2 26.0 L52.7 36.3 L58.5 40.2 L66.6 42.4 L67.9 47.6 L69.3 47.8 L81.8 42.1 L84.7 43.2 L88.5 46.6 L96.4 46.1 L99.3 48.2 L100.0 49.4 L97.2 61.6 L99.3 63.2 L99.1 64.5 L94.9 67.2 L95.6 71.4 L91.0 75.8 L80.5 76.5 L70.6 74.4 L63.3 71.6 L59.4 71.6 L67.8 75.1 L66.7 75.7 L51.8 71.5 L34.6 63.4 L12.6 59.9 L5.6 54.8 L0.4 52.6 L0.0 48.4 L2.4 45.5 L9.7 39.6 L13.0 39.4 L14.9 38.3 L18.1 33.9 L23.3 31.4 L22.2 25.2 L28.7 23.5Z',
  'Yemen':'M100.0 41.9 L92.7 45.3 L91.3 48.5 L91.7 51.4 L85.8 54.5 L64.2 61.2 L57.6 66.8 L51.1 66.8 L45.6 70.5 L39.6 72.4 L28.8 73.6 L22.8 78.6 L18.8 78.6 L12.9 80.6 L9.4 79.3 L8.0 79.8 L5.5 74.3 L6.0 70.2 L4.1 67.2 L2.7 58.3 L1.9 56.4 L0.0 55.5 L1.4 54.6 L0.6 51.4 L1.7 47.8 L1.4 44.5 L4.9 41.5 L5.1 35.1 L6.6 33.8 L8.5 33.7 L12.1 35.4 L23.9 34.4 L27.6 35.6 L39.0 36.0 L41.4 39.0 L43.0 39.0 L45.9 37.4 L47.2 34.2 L52.9 27.4 L62.7 23.0 L89.4 19.4 L100.0 41.9Z',
  'Tanzania':'M32.3 77.4 L27.9 75.1 L23.5 74.2 L23.3 73.2 L21.1 72.9 L18.2 70.2 L14.8 69.7 L8.0 56.1 L3.5 52.3 L2.0 49.6 L1.4 47.0 L2.5 44.3 L0.0 36.9 L0.7 32.9 L3.5 32.9 L5.6 31.6 L13.4 21.7 L13.1 19.7 L9.9 18.3 L10.9 14.7 L13.5 13.9 L13.9 12.2 L13.4 7.0 L10.6 3.8 L10.7 2.5 L41.8 1.9 L74.7 20.3 L74.4 24.3 L88.9 35.1 L85.1 47.4 L85.7 49.8 L91.8 56.0 L89.5 60.4 L89.4 62.8 L90.7 63.1 L90.8 64.9 L89.6 68.7 L90.9 73.2 L92.6 75.5 L93.9 81.9 L93.4 82.7 L100.0 86.9 L95.7 90.1 L89.7 92.8 L85.0 93.7 L82.3 95.4 L79.5 94.2 L77.2 94.3 L75.4 96.9 L72.3 98.1 L68.7 96.8 L62.7 98.0 L59.1 95.8 L56.0 97.1 L50.6 96.9 L47.4 92.4 L48.0 89.8 L47.1 84.9 L44.9 80.3 L41.9 78.2 L41.0 79.7 L32.3 77.4Z',
  'Rwanda':'M35.6 22.8 L47.9 20.2 L49.0 21.0 L50.7 25.9 L53.1 26.8 L61.6 21.8 L74.4 7.2 L81.8 6.9 L80.2 7.7 L79.9 10.0 L81.7 13.9 L87.9 21.7 L91.8 23.2 L96.8 31.4 L97.6 37.9 L96.5 45.7 L97.2 51.5 L99.4 55.3 L100.0 60.2 L97.6 69.8 L94.4 71.5 L92.0 71.1 L84.0 72.9 L80.5 71.7 L76.8 68.6 L68.2 70.3 L62.4 73.7 L55.3 69.8 L53.1 69.9 L52.2 80.2 L50.1 88.6 L41.6 92.4 L26.4 93.1 L24.4 92.3 L21.8 86.4 L16.8 83.8 L12.1 82.6 L10.2 82.9 L7.8 88.7 L3.2 86.9 L1.8 84.5 L1.7 80.6 L0.0 75.2 L0.9 72.9 L12.3 64.6 L13.6 62.7 L14.4 59.6 L13.5 46.2 L14.1 44.0 L24.5 29.2 L27.0 28.7 L35.6 22.8Z',
  'Ecuador':'M93.9 24.3 L90.9 25.1 L88.6 24.6 L94.3 31.8 L94.5 37.5 L92.0 37.0 L89.5 46.5 L81.4 55.9 L72.2 62.5 L53.8 69.1 L48.8 74.8 L49.2 76.6 L48.1 77.0 L46.3 75.5 L45.1 81.4 L41.1 90.0 L41.0 93.7 L37.5 96.0 L37.3 98.3 L35.6 100.0 L30.9 99.4 L28.3 95.4 L28.1 93.3 L26.1 92.0 L23.7 92.3 L18.4 89.5 L14.6 92.1 L13.1 91.6 L15.0 88.2 L12.9 87.5 L12.9 85.1 L15.8 85.0 L17.7 83.0 L15.5 75.4 L21.1 71.8 L24.7 62.8 L23.3 59.3 L23.0 54.8 L21.7 62.3 L20.1 62.5 L20.4 59.3 L16.1 64.8 L6.0 58.0 L5.5 56.7 L8.5 55.0 L8.7 52.8 L7.5 48.1 L8.0 44.2 L6.5 39.4 L7.4 37.8 L11.9 35.9 L13.4 31.8 L16.1 32.3 L14.5 31.7 L13.0 28.4 L19.8 20.2 L19.1 10.4 L20.0 9.7 L24.6 7.4 L26.5 7.5 L37.6 3.9 L38.8 2.5 L38.3 0.0 L48.8 7.6 L54.3 9.8 L56.3 9.6 L57.1 11.4 L59.9 12.7 L61.0 16.5 L69.9 18.8 L75.1 19.0 L76.1 18.6 L76.7 16.3 L78.6 15.8 L81.7 17.3 L86.3 21.3 L93.9 24.3Z',
  'Bolivia':'M6.3 62.5 L4.0 56.8 L9.9 50.3 L7.1 48.8 L5.5 45.0 L7.4 41.9 L5.9 39.8 L6.0 38.6 L9.7 33.8 L8.2 30.1 L8.9 24.0 L11.1 21.2 L4.3 9.4 L11.6 10.6 L15.8 7.5 L18.4 7.4 L27.1 1.4 L36.1 0.0 L36.8 3.3 L35.7 6.0 L36.6 10.0 L36.1 11.6 L39.1 17.2 L42.8 19.3 L43.5 20.7 L49.0 21.0 L51.6 22.5 L53.7 22.4 L56.0 24.9 L60.9 26.2 L63.4 28.9 L68.8 28.7 L73.2 30.9 L74.9 40.8 L72.6 40.9 L75.2 43.8 L75.7 49.8 L89.6 49.9 L88.6 53.0 L89.2 57.1 L93.5 59.2 L96.0 64.5 L93.8 69.8 L94.3 70.8 L91.2 76.1 L93.3 77.9 L91.5 79.2 L90.8 76.7 L83.9 72.7 L77.0 72.7 L63.7 75.4 L59.7 82.3 L59.7 86.2 L56.9 95.0 L55.4 93.2 L47.3 93.5 L44.2 99.5 L42.1 95.0 L33.2 94.0 L29.8 91.8 L28.7 94.1 L26.1 94.9 L22.4 99.5 L18.5 100.0 L17.2 99.5 L14.8 87.9 L12.1 84.9 L12.6 82.8 L10.5 81.2 L10.6 78.8 L12.1 77.8 L11.0 76.0 L12.7 73.6 L9.0 70.2 L8.0 63.3 L6.3 62.5Z',
  'Uganda':'M78.7 91.8 L24.3 91.7 L20.6 93.0 L16.5 93.1 L11.9 98.2 L8.9 100.0 L7.1 97.6 L2.7 98.6 L2.4 91.3 L5.2 72.4 L9.0 65.4 L9.1 59.8 L13.3 57.1 L15.8 53.3 L18.5 52.4 L32.1 38.2 L32.5 36.4 L30.8 34.3 L29.1 34.0 L27.0 31.9 L22.9 31.0 L25.1 23.3 L23.4 20.7 L26.1 14.3 L24.9 12.8 L28.5 8.7 L31.6 7.6 L37.3 9.5 L41.7 7.3 L44.2 10.8 L47.7 12.3 L51.2 9.0 L60.0 7.4 L62.8 6.0 L65.6 7.8 L71.4 8.2 L80.0 0.0 L82.7 5.8 L83.7 6.2 L83.3 7.2 L88.1 10.0 L87.4 14.2 L88.3 18.6 L89.6 19.3 L90.8 22.8 L93.5 24.6 L96.3 30.6 L97.6 43.9 L94.2 49.9 L94.5 52.3 L88.9 55.9 L87.6 58.9 L83.2 63.5 L79.4 71.1 L78.7 91.8Z',
  'Malawi':'M41.6 67.0 L35.3 58.9 L33.3 59.9 L29.1 54.3 L31.5 52.6 L33.0 49.6 L33.4 45.4 L32.7 44.1 L33.7 41.9 L38.6 40.1 L40.0 38.2 L37.8 37.7 L36.7 35.2 L37.3 29.7 L36.4 26.2 L38.3 22.8 L36.8 19.4 L39.4 18.0 L42.0 15.0 L40.3 10.9 L37.4 8.3 L38.0 6.0 L35.9 3.0 L33.4 2.9 L32.4 0.2 L33.1 0.0 L38.9 2.8 L44.9 3.6 L45.8 3.4 L46.3 1.3 L50.5 4.4 L53.1 8.2 L54.9 17.0 L54.2 21.8 L56.4 25.2 L57.9 25.9 L58.8 28.3 L54.4 28.8 L51.0 35.9 L53.7 51.3 L54.9 53.0 L58.1 53.8 L62.5 58.3 L70.3 68.3 L70.9 71.2 L69.1 86.3 L63.9 87.6 L61.5 92.8 L62.9 96.0 L62.8 100.0 L60.1 99.5 L60.3 96.3 L51.7 88.7 L51.6 86.6 L49.6 84.1 L53.4 76.4 L52.9 67.4 L50.7 64.9 L41.6 67.0Z',
  'Zambia':'M72.0 71.6 L64.3 72.1 L59.4 74.6 L58.7 78.3 L58.0 79.2 L51.0 82.3 L43.2 91.4 L41.1 92.1 L33.2 91.4 L23.6 87.7 L19.7 87.4 L12.0 88.7 L1.5 79.8 L0.5 76.9 L0.0 49.0 L17.0 48.9 L16.3 47.3 L17.7 35.3 L17.0 30.8 L20.4 33.0 L20.5 35.4 L28.3 33.7 L28.9 37.2 L34.6 39.5 L41.5 40.1 L44.3 36.8 L47.9 42.4 L55.1 44.9 L56.3 47.6 L57.8 48.4 L60.2 52.2 L64.8 51.1 L66.7 52.7 L66.9 41.8 L64.4 42.4 L64.3 44.0 L60.6 43.4 L55.7 38.8 L54.8 36.7 L57.1 28.0 L56.7 20.6 L55.0 16.7 L59.0 12.9 L59.2 10.4 L75.1 7.9 L77.5 11.3 L81.1 11.8 L83.0 14.0 L89.5 16.1 L93.7 18.2 L94.3 20.1 L96.0 20.1 L97.3 22.1 L97.0 23.6 L100.0 28.0 L96.6 31.0 L97.6 33.2 L96.3 35.4 L96.5 41.4 L97.2 43.1 L98.7 43.4 L94.5 45.8 L94.1 50.9 L91.5 54.0 L94.3 57.7 L95.6 57.0 L96.1 57.7 L70.6 66.0 L72.0 71.6Z',
  'Zimbabwe':'M77.9 93.5 L73.1 92.1 L63.7 92.1 L56.9 90.2 L53.1 90.8 L48.9 88.6 L48.7 85.7 L35.7 82.6 L31.3 76.3 L31.6 69.4 L26.3 68.8 L24.9 63.9 L18.5 61.2 L11.9 56.6 L9.0 48.9 L0.0 36.4 L0.2 34.2 L5.1 34.6 L9.7 36.4 L14.1 35.9 L19.8 37.4 L22.9 36.3 L34.6 22.6 L45.3 17.9 L47.3 10.9 L52.1 8.2 L57.8 6.5 L66.4 6.5 L66.9 11.0 L77.2 11.4 L83.0 13.8 L86.3 16.6 L90.2 16.9 L99.2 20.2 L98.3 22.5 L99.5 27.2 L99.8 41.5 L98.4 46.2 L96.3 47.5 L96.0 48.9 L98.0 51.1 L97.0 54.7 L100.0 61.0 L99.8 62.4 L95.7 69.2 L93.4 71.1 L93.2 74.8 L91.6 77.2 L92.6 79.3 L77.9 93.5Z',
  'Burundi':'M79.9 4.1 L73.9 15.3 L76.2 17.8 L73.9 23.8 L74.3 26.2 L78.1 28.2 L90.5 31.4 L91.9 37.5 L90.9 44.9 L83.3 48.3 L82.6 49.2 L83.6 51.6 L73.9 59.5 L71.8 66.2 L66.6 71.7 L60.9 82.7 L51.6 93.1 L40.9 100.0 L26.2 99.7 L22.9 83.2 L17.8 74.6 L17.3 71.0 L17.9 34.6 L8.2 22.7 L8.1 19.0 L10.4 13.5 L16.6 14.3 L21.3 16.8 L23.7 22.3 L25.6 23.1 L40.0 22.5 L47.9 18.8 L50.0 11.0 L50.8 1.2 L52.8 1.1 L59.5 4.8 L65.0 1.6 L73.1 0.0 L76.6 2.9 L79.9 4.1Z',
  'Thailand':'M39.1 0.0 L42.0 0.3 L43.3 1.7 L42.5 4.5 L43.3 5.9 L48.0 5.9 L48.5 9.8 L46.9 13.4 L47.5 15.4 L46.3 19.5 L47.7 19.8 L54.0 15.0 L57.8 17.6 L60.4 16.2 L62.0 13.6 L66.5 14.2 L72.4 21.1 L72.4 26.8 L78.0 32.2 L76.9 34.9 L76.8 39.9 L74.1 41.9 L72.1 40.6 L61.4 41.2 L59.5 42.5 L57.0 46.2 L55.5 46.6 L56.7 52.4 L58.4 54.1 L58.3 56.4 L59.6 59.0 L57.3 55.6 L57.0 56.2 L52.2 52.6 L45.9 52.5 L46.3 47.3 L43.9 46.4 L39.9 47.8 L39.7 55.8 L34.2 68.3 L34.1 72.3 L34.8 75.5 L38.7 75.3 L39.7 80.0 L41.7 82.2 L43.5 89.2 L41.5 85.5 L40.9 86.7 L42.7 89.5 L46.7 91.7 L49.9 91.7 L54.0 95.9 L52.5 98.7 L51.2 99.0 L50.3 98.2 L47.3 100.0 L46.4 99.1 L46.9 95.9 L41.6 92.9 L40.6 94.6 L37.8 91.6 L37.1 88.4 L35.5 88.3 L31.0 82.3 L30.2 81.7 L28.7 82.8 L27.9 81.2 L31.4 66.0 L37.2 58.4 L33.9 50.0 L34.0 45.4 L27.6 36.8 L27.6 35.3 L30.0 34.2 L30.3 29.6 L32.3 27.5 L30.7 27.7 L29.2 23.3 L24.3 17.8 L23.8 14.4 L22.0 12.9 L24.6 12.4 L25.0 6.5 L26.4 4.6 L32.5 4.4 L33.5 2.2 L36.3 1.9 L36.1 0.4 L39.1 0.0Z',
  'China (Yunnan)':'M58.9 75.0 L54.1 74.5 L54.3 73.2 L51.8 72.2 L49.7 73.6 L46.0 73.6 L46.0 75.8 L45.0 74.8 L43.4 75.3 L41.8 74.2 L42.4 72.9 L41.3 72.5 L41.3 71.0 L39.2 71.3 L39.6 69.1 L41.0 68.1 L41.0 65.3 L39.4 63.8 L37.1 63.9 L37.6 63.4 L36.7 62.2 L34.4 62.5 L30.1 65.1 L26.7 64.1 L25.0 65.7 L24.6 64.5 L20.3 64.8 L13.8 60.8 L12.3 61.3 L8.4 59.2 L7.8 57.2 L9.2 57.2 L8.7 54.3 L7.2 52.4 L4.2 51.8 L3.6 50.4 L1.2 49.6 L2.4 49.2 L2.0 47.6 L0.3 47.2 L0.0 45.9 L2.0 44.2 L4.4 44.4 L5.4 43.3 L10.8 41.6 L11.7 39.8 L11.2 37.2 L10.2 37.0 L14.6 36.6 L15.4 33.2 L19.4 33.4 L19.8 31.3 L21.7 30.1 L23.2 29.9 L23.5 30.9 L27.3 32.4 L28.5 34.2 L28.3 36.4 L35.6 37.9 L37.3 40.5 L45.7 40.8 L51.4 42.3 L60.2 40.4 L62.8 38.9 L61.9 37.8 L62.7 36.7 L65.5 37.2 L71.8 34.2 L75.8 34.0 L73.5 31.9 L69.3 32.4 L68.6 31.6 L70.5 28.9 L72.5 29.4 L74.8 28.5 L77.2 25.1 L76.0 24.1 L77.6 23.2 L81.9 22.8 L85.2 23.6 L88.3 28.9 L93.3 30.4 L94.0 32.4 L100.0 31.4 L97.5 36.5 L94.0 37.0 L94.4 39.4 L93.2 40.8 L92.2 40.0 L91.9 40.9 L89.2 41.7 L89.3 42.7 L87.0 42.1 L83.0 45.1 L77.9 47.0 L79.7 44.1 L79.0 43.4 L74.3 46.3 L72.3 46.4 L72.1 47.5 L74.2 48.2 L74.8 49.6 L77.2 48.5 L80.3 49.2 L79.8 50.1 L76.3 51.2 L74.6 53.4 L76.4 54.3 L77.4 57.0 L79.0 58.2 L78.9 58.6 L76.8 57.9 L76.0 58.2 L79.0 59.6 L76.3 60.9 L79.4 61.6 L78.4 62.2 L79.2 62.2 L78.3 62.8 L78.6 64.1 L77.2 64.6 L76.0 66.9 L75.3 66.6 L75.8 67.3 L74.6 67.7 L75.4 68.9 L70.2 72.9 L66.2 73.6 L65.4 72.6 L65.4 74.1 L60.3 75.5 L60.2 77.2 L59.4 77.1 L58.9 75.0Z',
  'Timor-Leste':'M6.4 75.1 L5.0 69.7 L2.2 66.0 L1.9 62.6 L2.6 61.8 L7.8 61.6 L9.8 58.8 L9.8 55.4 L7.8 53.8 L2.4 56.3 L0.9 55.9 L0.0 54.9 L0.3 51.2 L4.7 47.7 L8.4 41.4 L11.0 38.8 L19.6 35.8 L37.3 32.3 L71.6 30.9 L86.2 24.9 L96.6 27.3 L100.0 29.5 L92.4 36.1 L84.0 41.7 L73.5 44.5 L69.4 46.6 L66.0 50.0 L61.6 51.8 L52.5 53.5 L43.3 58.8 L38.9 59.1 L20.7 65.2 L6.4 75.1Z',
  'Jamaica':'M50.6 34.1 L67.2 37.2 L77.0 43.5 L93.5 48.4 L100.0 59.6 L95.7 61.2 L85.3 61.9 L78.5 59.0 L73.5 58.4 L74.7 57.2 L69.8 56.8 L65.5 62.7 L61.2 62.4 L59.6 60.2 L57.3 61.2 L55.5 62.8 L53.3 69.0 L45.9 63.4 L26.8 61.3 L21.5 54.7 L17.7 53.3 L13.9 47.4 L2.1 45.3 L0.0 42.1 L0.6 39.1 L5.8 34.5 L11.5 34.7 L17.0 33.6 L21.9 31.0 L50.6 34.1Z',
  'Panama':'M96.9 45.7 L95.2 48.5 L100.0 57.5 L97.4 59.8 L97.3 62.1 L94.1 64.5 L93.3 64.8 L90.3 62.2 L90.6 65.0 L87.9 70.2 L83.3 64.8 L79.0 56.0 L81.3 55.4 L81.4 52.8 L83.8 50.4 L90.3 54.7 L86.0 51.4 L84.5 48.5 L82.4 50.2 L79.4 48.3 L79.9 50.1 L79.2 50.9 L77.4 46.2 L67.6 39.9 L60.4 40.4 L57.3 42.4 L55.1 46.1 L56.2 46.8 L49.8 51.0 L45.6 52.1 L44.0 53.3 L44.1 55.7 L50.6 62.7 L51.7 65.6 L50.0 66.7 L47.0 66.9 L44.4 69.4 L40.5 70.3 L37.4 70.4 L36.5 69.4 L33.7 58.7 L32.1 59.5 L31.4 62.7 L30.2 63.4 L26.1 61.8 L22.3 54.7 L18.1 53.3 L14.9 53.7 L13.6 51.7 L11.4 52.3 L6.0 51.5 L2.8 52.8 L2.5 55.8 L0.0 51.2 L2.8 49.2 L2.9 46.1 L1.9 44.3 L5.1 41.3 L1.5 38.8 L1.5 32.2 L3.9 29.7 L6.6 31.2 L8.0 30.0 L11.3 32.5 L11.8 36.3 L14.4 36.6 L13.4 39.3 L16.3 41.0 L21.4 40.6 L19.4 37.5 L25.4 42.8 L28.7 43.6 L37.5 41.8 L42.5 38.5 L49.7 36.3 L59.2 29.6 L67.1 30.7 L70.2 32.5 L77.6 32.9 L84.8 35.8 L96.9 45.7Z',
  'DR Congo':'M97.3 71.7 L87.5 73.2 L87.4 74.8 L84.9 77.1 L86.1 80.3 L86.2 84.7 L84.7 88.9 L85.4 90.7 L88.4 93.5 L90.6 93.8 L90.7 92.8 L92.2 92.5 L92.1 99.2 L91.0 98.2 L88.7 99.0 L85.0 94.4 L80.4 92.7 L78.4 89.4 L76.7 91.5 L72.5 91.1 L68.9 89.7 L68.6 87.5 L63.8 88.6 L63.8 87.1 L61.7 85.7 L61.0 86.5 L52.8 87.4 L52.8 82.5 L50.4 78.4 L50.2 67.1 L44.0 66.9 L43.9 65.0 L40.2 65.3 L38.4 66.2 L37.4 70.5 L28.2 71.2 L25.0 66.8 L23.5 61.0 L22.1 59.6 L4.1 59.3 L1.6 60.2 L0.0 58.9 L1.5 58.6 L1.2 55.3 L3.2 53.5 L4.8 52.8 L6.3 54.1 L7.6 53.5 L7.9 52.1 L11.3 51.2 L11.5 54.0 L13.1 54.3 L19.8 48.4 L21.0 44.6 L21.0 40.1 L24.5 35.1 L29.1 31.6 L30.7 18.1 L33.6 11.3 L33.3 6.3 L36.0 3.0 L39.2 1.8 L43.8 5.3 L53.6 7.0 L55.9 3.9 L58.8 4.2 L63.5 2.5 L67.4 2.6 L69.8 0.8 L76.6 2.1 L78.2 1.4 L83.8 5.9 L86.6 5.0 L89.2 5.6 L91.6 4.6 L98.0 10.5 L97.1 15.8 L100.0 17.4 L93.0 24.4 L91.1 36.0 L89.1 37.7 L88.8 40.2 L87.3 41.5 L89.2 44.7 L89.8 54.4 L91.3 58.7 L90.9 61.8 L94.4 65.6 L97.3 71.7Z',
  'Indonesia (Sumatra)':'M14.0 3.3 L17.1 2.9 L23.2 3.5 L26.3 6.3 L27.1 8.2 L29.3 10.4 L29.2 12.3 L29.8 13.2 L32.9 14.6 L33.9 16.1 L42.2 21.1 L49.1 29.7 L52.2 31.8 L51.7 29.2 L53.6 29.1 L55.8 31.2 L57.3 34.0 L60.0 34.6 L62.1 36.2 L64.0 40.1 L65.3 41.4 L69.3 42.5 L70.8 43.7 L71.1 44.4 L70.6 45.1 L66.7 46.8 L69.7 46.3 L73.5 44.3 L74.7 44.5 L76.4 46.2 L77.4 48.3 L74.3 50.4 L74.1 51.9 L75.0 52.8 L74.4 53.7 L75.2 55.3 L76.8 56.4 L81.0 57.9 L82.4 57.7 L83.7 64.5 L86.6 66.9 L86.4 68.1 L84.9 69.8 L84.9 71.3 L87.7 69.3 L91.4 69.4 L93.0 70.4 L97.0 75.7 L97.1 76.7 L95.8 78.3 L95.3 80.1 L96.0 82.0 L95.2 84.9 L95.6 92.2 L94.4 99.3 L93.3 99.1 L91.0 96.9 L88.6 98.6 L84.8 96.7 L85.2 99.9 L84.5 100.0 L77.8 92.8 L66.5 84.8 L63.0 80.0 L58.2 76.2 L52.2 68.2 L51.9 65.5 L48.7 60.0 L47.2 55.9 L43.3 51.4 L41.6 48.3 L37.2 45.7 L34.1 35.7 L32.3 32.5 L24.5 28.2 L23.6 24.0 L21.8 22.9 L18.2 17.7 L16.7 16.5 L13.6 15.6 L6.1 8.2 L2.9 2.8 L3.1 0.4 L6.5 0.0 L10.9 2.7 L14.0 3.3Z',
  'Java':'M22.7 35.8 L25.8 38.0 L32.9 38.7 L34.9 40.7 L35.8 43.5 L36.6 44.1 L43.2 45.0 L45.5 44.4 L48.9 45.3 L55.4 45.8 L57.0 44.3 L58.3 41.2 L59.7 40.2 L61.2 40.3 L63.5 43.0 L67.3 42.6 L69.4 44.0 L72.1 44.3 L73.1 45.3 L78.0 45.6 L79.2 48.8 L80.7 49.7 L80.7 52.3 L83.1 53.4 L88.3 54.1 L94.4 53.2 L98.0 54.9 L98.4 57.1 L97.8 61.4 L98.8 63.6 L100.0 64.4 L99.9 65.3 L96.6 63.7 L93.0 63.2 L85.6 60.2 L79.5 61.5 L67.0 60.4 L57.3 58.7 L51.2 55.9 L43.1 53.9 L37.3 53.5 L34.2 54.9 L28.5 54.1 L21.7 51.4 L12.8 50.3 L12.4 49.0 L13.5 47.0 L10.1 45.6 L6.2 44.7 L0.0 44.6 L0.2 43.5 L1.2 42.8 L1.4 43.7 L2.4 44.1 L4.3 40.7 L5.7 40.6 L6.6 36.9 L8.8 34.8 L16.8 36.7 L18.8 35.8 L19.2 34.7 L22.7 35.8Z',
  'Sulawesi (Toraja)':'M89.0 9.4 L86.4 11.7 L82.8 16.5 L79.9 17.7 L73.7 18.7 L67.0 18.4 L64.6 16.3 L63.4 16.2 L47.7 16.9 L43.3 16.1 L36.5 16.9 L30.6 15.7 L27.5 16.8 L25.4 19.2 L23.0 25.5 L23.6 30.4 L26.0 34.6 L29.8 36.9 L31.8 41.4 L36.8 41.9 L38.3 41.0 L40.1 38.0 L44.1 34.1 L46.3 35.4 L49.5 35.5 L53.7 33.1 L61.9 33.1 L61.1 31.8 L65.8 30.6 L68.6 31.6 L69.3 33.4 L68.6 36.5 L66.5 36.4 L65.5 35.1 L64.1 34.7 L62.1 35.1 L56.8 41.1 L53.3 43.9 L48.0 45.8 L45.2 48.5 L41.7 47.7 L41.1 48.3 L41.1 49.2 L44.1 52.0 L46.8 53.2 L51.0 60.1 L53.8 62.2 L54.0 64.2 L55.3 66.2 L54.2 67.2 L53.3 71.9 L57.7 75.5 L59.2 78.2 L61.4 77.9 L62.1 80.2 L61.7 82.4 L59.6 81.7 L59.7 82.6 L56.3 82.8 L51.4 84.4 L50.6 85.5 L50.9 87.8 L50.4 88.3 L48.8 88.5 L44.3 87.3 L42.9 84.9 L44.7 78.3 L40.6 76.0 L34.9 70.6 L35.1 69.0 L37.1 65.8 L37.0 60.1 L36.2 59.0 L34.7 58.7 L31.6 59.0 L26.3 62.8 L26.2 64.2 L28.1 68.2 L28.7 73.1 L27.7 78.2 L28.5 85.4 L26.6 92.6 L28.6 98.6 L27.0 97.9 L22.1 98.4 L18.9 100.0 L16.8 98.9 L14.3 96.4 L14.1 94.9 L17.3 84.1 L17.7 77.5 L15.7 73.4 L15.6 70.5 L14.1 69.7 L9.2 70.8 L7.4 68.9 L6.7 65.6 L7.3 62.5 L6.3 59.7 L10.5 56.5 L11.6 51.8 L13.6 49.0 L13.4 41.9 L16.1 35.1 L18.9 32.1 L20.7 34.5 L19.0 24.0 L21.0 22.3 L20.2 19.6 L21.6 16.8 L23.3 15.2 L23.5 13.5 L25.9 11.2 L26.4 9.7 L27.2 9.5 L28.4 11.3 L29.8 11.8 L30.9 11.3 L34.5 5.9 L37.4 4.9 L39.2 5.7 L41.8 6.0 L44.4 8.4 L48.1 8.1 L55.8 9.0 L61.2 11.4 L64.3 10.1 L76.0 11.3 L80.7 9.0 L82.6 6.8 L84.2 6.2 L85.1 4.0 L87.7 3.0 L89.8 0.2 L92.0 0.0 L93.7 2.5 L89.0 9.4Z',
  'Flores (Bajawa)':'M93.0 53.0 L88.6 54.2 L83.2 56.6 L71.5 57.2 L63.5 60.8 L57.6 62.0 L55.6 59.6 L50.2 59.4 L47.5 62.6 L43.2 61.9 L38.4 63.2 L30.4 60.5 L23.2 59.0 L16.0 59.6 L9.8 58.2 L3.2 60.7 L0.0 55.7 L0.3 51.8 L2.1 47.0 L3.5 47.8 L4.9 47.5 L9.1 45.7 L13.2 43.0 L17.1 42.0 L19.3 41.7 L21.2 42.2 L25.1 41.4 L29.5 44.0 L33.7 44.1 L37.5 45.3 L45.9 48.9 L48.9 51.1 L51.2 52.0 L54.4 51.9 L56.4 50.4 L64.3 49.4 L67.5 48.1 L70.6 49.4 L76.8 53.5 L78.7 53.6 L82.1 52.7 L85.9 47.4 L95.1 43.4 L97.3 40.9 L92.3 39.7 L93.3 37.9 L95.0 36.8 L97.2 37.2 L99.1 38.7 L100.0 44.2 L93.9 49.0 L95.0 51.5 L93.0 53.0Z',
  'Bali (Kintamani)':'M79.3 25.6 L87.5 29.9 L98.9 42.4 L100.0 45.9 L96.5 49.3 L88.3 54.6 L70.0 62.8 L66.9 66.7 L63.0 74.3 L62.1 77.5 L60.9 79.3 L58.8 80.6 L54.8 81.7 L50.5 80.1 L54.4 75.2 L54.5 69.4 L51.6 63.9 L47.5 59.4 L39.2 53.2 L30.3 47.7 L21.3 44.9 L11.8 43.6 L8.4 40.9 L2.8 34.1 L0.9 30.4 L0.0 26.5 L0.6 22.7 L3.0 22.4 L12.3 23.3 L29.5 27.8 L38.1 28.1 L42.9 27.1 L55.5 18.3 L58.5 18.5 L79.3 25.6Z',
  'Hawaii (Kona)':'M85.3 79.8 L83.5 82.7 L82.4 82.6 L78.4 80.6 L77.9 79.4 L78.2 74.3 L75.0 66.9 L79.6 61.6 L78.2 58.5 L78.5 56.7 L79.4 56.4 L92.1 62.0 L94.3 64.4 L94.7 67.0 L96.3 67.3 L97.0 69.0 L100.0 71.4 L99.1 72.9 L95.0 75.6 L89.9 76.7 L85.3 79.8Z M64.3 41.2 L66.8 43.6 L70.4 42.8 L76.2 46.7 L73.9 49.0 L67.8 49.8 L67.2 49.5 L66.4 45.8 L65.1 46.1 L63.7 45.4 L62.0 42.9 L62.8 41.4 L64.3 41.2Z M50.9 37.2 L56.9 37.8 L61.7 38.7 L61.0 39.8 L58.8 40.7 L55.5 39.9 L50.1 39.6 L50.9 37.2Z M39.9 32.7 L41.5 32.7 L41.8 34.3 L43.2 35.7 L39.9 36.5 L37.9 35.0 L36.7 35.3 L36.3 34.3 L35.5 34.5 L36.3 35.5 L33.7 35.5 L31.1 32.0 L30.4 30.1 L33.4 29.8 L35.5 28.0 L36.6 27.8 L39.9 32.7Z M8.4 23.1 L6.6 24.3 L3.6 23.6 L0.0 20.9 L1.3 19.0 L4.2 17.3 L8.8 17.4 L9.8 19.7 L8.4 23.1Z',
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
// Distinct-but-harmonious colors for the growing-region key (dot on the map <-> dot in the list).
const REGION_COLORS=['#e0a84e','#c97b4a','#8faf6a','#d9b978','#b0895a','#9a9f5a','#cf9160','#7fa88a'];
// Real region positions (lon/lat projected into each silhouette's 0..100 box, same source
// as the shapes: Natural Earth). Aligned to regions2 order; null = generic entry, no dot.
const REGION_DOTS={
  'Brazil':[[69.1,61.8],[71.7,68.7],[68.9,66.9],[83.4,45.5]],
  'Colombia':[[34.1,35.5],[36.5,48.2],[34.7,59.6],[23.9,67.4]],
  'Ethiopia':[[34.7,70.0],[36.0,71.7],[36.7,66.4],[60.7,49.0]],
  'Kenya':[[40.7,58.1],[44.2,58.9],[45.6,59.2],[44.2,55.5]],
  'Vietnam':[[65.4,72.2],[65.7,77.9],[65.0,64.7],[65.0,70.1]],
  'India':[[25.8,80.5],[30.0,88.7],[29.3,85.6],[24.5,84.3]],
  'Mexico':[[81.1,76.1],[68.0,74.8],[66.6,64.6],[79.8,76.8]],
  'Peru':[[30.9,32.6],[34.2,30.9],[39.7,35.3],[69.2,71.9]],
  'Papua New Guinea':[[45.4,44.7],[34.4,41.7],[41.4,43.7],[38.4,42.7]],
  'Guatemala':[[19.6,61.2],[26.3,76.9],[37.8,79.8],[46.6,57.5]],
  'Costa Rica':[[48.1,37.4],[57.1,41.0],[56.5,49.4]],
  'Honduras':[[7.5,44.4],[20.3,53.3],[27.8,50.7],[55.8,42.0],[54.2,58.9]],
  'Nicaragua':[[25.9,31.5],[37.0,45.0],[38.8,48.5]],
  'El Salvador':[[12.8,47.8],[27.4,27.7],[50.4,58.3]],
  'Yemen':[[10.0,56.7],[12.9,54.8],[23.9,68.7],[11.9,58.6]],
  'Tanzania':[[68.9,21.7],[33.0,73.7],[56.3,89.0],[5.2,36.9]],
  'Rwanda':[[19.4,55.6],[41.7,82.8],[44.2,28.3],[81.3,48.1]],
  'Ecuador':[[33.0,84.9],[43.9,25.0],[50.1,17.2],null],
  'Bolivia':[[19.6,46.5],[17.8,49.2],null],
  'Uganda':[[87.4,54.8],[10.1,68.0],[31.2,25.0],null],
  'Malawi':[[39.9,3.9],[43.8,32.4],[46.4,26.7],[46.4,51.5]],
  'Zambia':[[79.8,21.6],[92.2,17.7],[78.8,25.1],[54.1,69.5]],
  'Zimbabwe':[[95.0,65.0],[95.7,49.3],null],
  'Burundi':[[36.3,28.3],[46.1,27.4],[49.4,50.7],[69.9,25.1]],
  'Thailand':[[32.9,11.0],[37.8,3.5],[38.7,0.8],null],
  'China (Yunnan)':[[44.8,73.2],[41.8,69.4],[40.9,70.4],null],
  'Timor-Leste':[[20.4,43.1],[28.8,46.9],[20.4,45.2],null],
  'Jamaica':[[74.7,53.2],[91.1,48.5],[93.5,57.9],null],
  'Panama':[[10.2,43.6],[6.8,43.8],[3.6,42.4]],
  'DR Congo':[[87.3,41.8],[88.3,40.0],[89.3,37.5],[92.8,21.9]],
  'Indonesia (Sumatra)':[[16.7,8.8],[29.7,27.9],[36.7,43.5]],
  'Java':[[94.7,58.2],[25.1,45.3],[50.8,49.6],null],
  'Sulawesi (Toraja)':[[20.7,64.2],[19.7,71.1],[14.0,62.8],[16.0,94.7]],
  'Bali (Kintamani)':[[71.4,33.2],null],
  'Flores (Bajawa)':[[36.7,58.6],[21.0,52.1]],
  'Hawaii (Kona)':[[77.0,69.9],[84.0,80.0],[94.1,69.9],[70.0,45.9]],
};
// Bounding box of a (possibly multi-subpath) silhouette path -> lets us FIT + center it.
function silBBox(d){
  const nums=(d.match(/-?\d+\.?\d*/g)||[]).map(Number);
  let minx=1e9,miny=1e9,maxx=-1e9,maxy=-1e9;
  for(let i=0;i+1<nums.length;i+=2){const x=nums[i],y=nums[i+1];
    if(x<minx)minx=x;if(x>maxx)maxx=x;if(y<miny)miny=y;if(y>maxy)maxy=y;}
  return {minx,miny,maxx,maxy,w:maxx-minx,h:maxy-miny};
}
function originRegionMap(m){
  const rm=m.regionMap; if(!rm)return '';
  const accent=m.accent||'#B07B3E';
  const regions=rm.regions2||[];
  if(!regions.length)return '';
  const W=440, padTop=64, rowH=34, padBot=18;
  const silName=m.country||m.name;
  const silKey=silName.replace(/ \(.*\)/,'');
  const sil=COUNTRY_SIL[silName]||COUNTRY_SIL[silKey];
  const country=silName.replace(/ \(.*\)/,'');
  // right zone stacks: map + country name + altitude. Card = taller of the two columns.
  const mapTop=16, mapBox=158;   // the square the map is fitted into
  const rightZoneH=mapTop+mapBox+22+(rm.alt?16:0)+10;
  const listH=padTop+regions.length*rowH+padBot;
  const H=Math.max(listH, rightZoneH);
  let g=diaDefs([accent]);
  g+=`<rect x="0" y="0" width="${W}" height="${H}" fill="#12100c" rx="14"/>`;
  const mapCx=W*0.72;
  if(sil){
    const bb=silBBox(sil);
    const fit=mapBox/Math.max(bb.w,bb.h);              // scale to fill the box on its long axis
    const drawW=bb.w*fit, drawH=bb.h*fit;
    const sx=mapCx-drawW/2 - bb.minx*fit;              // center the shape's bbox in the map zone
    const sy=mapTop + (mapBox-drawH)/2 - bb.miny*fit;
    const uid=_cid(accent)+regions.length+Math.round(fit*100);
    const gid='silfill'+uid, cid='silclip'+uid, hid='silhi'+uid;
    // soft elevation glow centered on the shape (subtle warmth, no misplaced markers)
    const hx=(bb.minx+bb.maxx)/2, hy=(bb.miny+bb.maxy)/2, rad=Math.max(bb.w,bb.h)*0.55;
    g+=`<defs>`+
       `<linearGradient id="${gid}" x1="0" y1="0" x2="1" y2="1">`+
         `<stop offset="0" stop-color="${accent}" stop-opacity="0.28"/>`+
         `<stop offset="1" stop-color="${accent}" stop-opacity="0.14"/></linearGradient>`+
       `<radialGradient id="${hid}" cx="${hx.toFixed(1)}" cy="${hy.toFixed(1)}" r="${rad.toFixed(1)}" gradientUnits="userSpaceOnUse">`+
         `<stop offset="0" stop-color="#e9cf94" stop-opacity="0.22"/>`+
         `<stop offset="1" stop-color="#d8b566" stop-opacity="0"/></radialGradient>`+
       `<clipPath id="${cid}"><path d="${sil}"/></clipPath></defs>`;
    const glow=`<rect x="${(bb.minx-10).toFixed(0)}" y="${(bb.miny-10).toFixed(0)}" width="${(bb.w+20).toFixed(0)}" height="${(bb.h+20).toFixed(0)}" fill="url(#${hid})"/>`;
    // real region dots (lon/lat projected into this shape's space), numbered + color-coded
    const rdots=REGION_DOTS[silName]||REGION_DOTS[silKey]||[];
    let dotsSvg='';
    rdots.forEach((xy,i)=>{
      if(!xy)return;
      const col=REGION_COLORS[i%REGION_COLORS.length];
      dotsSvg+=`<circle cx="${xy[0]}" cy="${xy[1]}" r="${(3.2/1).toFixed(1)}" fill="${col}" stroke="#12100c" stroke-width="0.7"/>`;
      dotsSvg+=`<text x="${xy[0]}" y="${(xy[1]+1.3).toFixed(1)}" fill="#12100c" font-size="3.4" font-weight="800" text-anchor="middle" font-family="ui-sans-serif">${i+1}</text>`;
    });
    g+=`<g transform="translate(${sx.toFixed(1)},${sy.toFixed(1)}) scale(${fit.toFixed(3)})" aria-hidden="true">`+
       `<path d="${sil}" fill="url(#${gid})"/>`+
       `<g clip-path="url(#${cid})">${glow}</g>`+
       `<path d="${sil}" fill="none" stroke="${accent}" stroke-opacity="0.45" stroke-width="${(0.8/fit).toFixed(2)}"/>`+
       dotsSvg+
       `</g>`;
    // country name + altitude beneath the map
    let cyn=mapTop+mapBox+22;
    g+=`<text x="${mapCx.toFixed(0)}" y="${cyn}" fill="#f0e6d8" font-size="18" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${esc(country)}</text>`;
    if(rm.alt){cyn+=16;g+=`<text x="${mapCx.toFixed(0)}" y="${cyn}" fill="${accent}" font-size="11.5" text-anchor="middle" font-family="ui-monospace">${esc(rm.alt)}</text>`;}
  }
  // ---- LEFT: big GROWING REGIONS header (with the pin) + the region list ----
  g+=`<g transform="translate(20,20)" filter="url(#dsoft)">
    <path d="M7 0 C2.6 0 -1 3.4 -1 7.7 C-1 13.7 7 20.6 7 20.6 C7 20.6 15 13.7 15 7.7 C15 3.4 11.4 0 7 0 Z" fill="${accent}"/>
    <circle cx="7" cy="7.7" r="2.9" fill="#12100c"/></g>`;
  g+=`<text x="42" y="30" fill="#f0e6d8" font-size="15" font-weight="700" letter-spacing="1.2" font-family="ui-monospace">GROWING</text>`;
  g+=`<text x="42" y="47" fill="${accent}" font-size="15" font-weight="700" letter-spacing="1.2" font-family="ui-monospace">REGIONS</text>`;
  const dotX=30, firstY=padTop+rowH/2;
  const lastY=padTop+(regions.length-1)*rowH+rowH/2;
  g+=`<line x1="${dotX}" y1="${firstY}" x2="${dotX}" y2="${lastY}" stroke="${accent}" stroke-width="1.5" opacity="0.25"/>`;
  const rdotsL=REGION_DOTS[silName]||REGION_DOTS[silKey]||[];
  regions.forEach((r,i)=>{
    const cy=padTop+i*rowH+rowH/2;
    const hasDot=rdotsL[i];
    const col=hasDot?REGION_COLORS[i%REGION_COLORS.length]:accent;
    g+=`<circle cx="${dotX}" cy="${cy}" r="7" fill="${col}" stroke="#12100c" stroke-width="2"/>`;
    if(hasDot)g+=`<text x="${dotX}" y="${cy+3.2}" fill="#12100c" font-size="9" font-weight="800" text-anchor="middle" font-family="ui-sans-serif">${i+1}</text>`;
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
// Image-based diagram: same <figure> shell, but an <img> pointing at a PNG in ./img/.
// Used for illustrations that read better as raster art than hand-drawn SVG (latte art, roasters).
// The service worker precaches ./img/* so these still work offline once visited.
function diaImg(file,cap,alt){
  const a=alt||cap||'';
  return `<figure class="diagram diagram-img"><img src="./img/${file}" alt="${esc(String(a).replace(/"/g,''))}" loading="lazy" decoding="async"/>${cap?`<figcaption>${cap}</figcaption>`:''}</figure>`;
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
// Realistic parametric coffee bean (cross-referenced with real bean anatomy: oblong ~5:3,
// a deep FOLDED center cut lined with paler silverskin, directional top-light shading).
// kind: 'green' or 'roast' sets the crease/edge tone. col = body color. overlay = defect id.
// Returns a <g> translated+scaled to (cx,cy,s). Bean drawn in a ~[-32..32]x[-22..22] box.
function diaBean(cx,cy,s,col,kind,overlay){
  kind=kind||'roast';
  const edge = kind==='green' ? '#37452a' : '#281810';
  const [r,gc,b]=_hex2rgb(col);
  const mul=(f)=>`rgb(${Math.min(255,Math.round(r*f))},${Math.min(255,Math.round(gc*f))},${Math.min(255,Math.round(b*f))})`;
  const dark=mul(0.58), mid=mul(0.82), lite=mul(1.20), litest=mul(1.34);
  const silver = kind==='green' ? '#dee3c6' : '#ecdfc6';
  const uid=_cid(col)+kind+(overlay||'x');
  const gid='bnb'+uid, gcut='bnv'+uid, gsheen='bns'+uid;
  let g=`<g transform="translate(${cx},${cy}) scale(${s})">`;
  // ---- gradients: a rounded body lit from top-left, plus a dark valley gradient for the cut ----
  // body radial is offset up-left; a lower-right fade gives the bean a solid, domed read
  const bcx = kind==='green' ? 0.40 : 0.38, bcy = kind==='green' ? 0.33 : 0.30, brad = kind==='green' ? 0.98 : 0.92;
  g+=`<defs>`+
     `<radialGradient id="${gid}" cx="${bcx}" cy="${bcy}" r="${brad}">`+
       `<stop offset="0" stop-color="${litest}"/><stop offset="0.30" stop-color="${lite}"/>`+
       `<stop offset="0.62" stop-color="${col}"/><stop offset="0.86" stop-color="${mid}"/><stop offset="1" stop-color="${dark}"/></radialGradient>`+
     `<linearGradient id="${gcut}" x1="0" y1="0" x2="1" y2="0">`+
       `<stop offset="0" stop-color="${dark}"/><stop offset="0.5" stop-color="${mul(0.42)}"/><stop offset="1" stop-color="${dark}"/></linearGradient>`+
     `<radialGradient id="${gsheen}" cx="0.32" cy="0.26" r="0.6">`+
       `<stop offset="0" stop-color="#ffffff" stop-opacity="${kind==='green'?0.16:0.24}"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></radialGradient>`+
     `</defs>`;
  // bean body: egg-shaped seed — one end a touch broader, flat-faced, rounded (real ~10x6mm)
  const body=`M0 -22 C 13.5 -21.5 21.5 -12.5 21.5 -0.5 C 21.5 12 13 22 0 22 C -13.5 22 -21.5 12 -21.5 -0.5 C -21.5 -12.5 -13.5 -21.5 0 -22 Z`;
  g+=`<ellipse cx="1.5" cy="3.5" rx="22.5" ry="22" fill="#000" opacity="0.18" filter="url(#dsoft)"/>`; // contact shadow
  g+=`<path d="${body}" fill="url(#${gid})" stroke="${edge}" stroke-width="1.4"/>`;
  // inner ambient-occlusion rim: a soft dark inset so the edge rounds away from the eye
  g+=`<path d="${body}" fill="none" stroke="${dark}" stroke-width="3" opacity="0.35" transform="scale(0.92)"/>`;
  // ---- the center cut: a real folded VALLEY (Arabica wavy S), filled dark with a lit silverskin edge ----
  // valley as a thin closed ribbon down the seam, so it reads as depth not a drawn line
  const valley=`M-2.6 -19 C -6.5 -10 3.5 -3 -1.5 5.5 C -5 12 2 16 -1 19.5 L2.8 19.5 C 6 16 -1 12 3 5.5 C 7.5 -3 -2 -10 2.4 -19 Z`;
  const seam = `M0 -19 C -4 -10 5 -3 0 5.5 C -3.4 12 3 16 0 19.5`;
  if(kind==='green'){
    // green coffee: the seam holds pale, tightly-adhering silverskin — bright lining, soft valley
    g+=`<path d="${valley}" fill="url(#${gcut})" opacity="0.55"/>`;
    g+=`<path d="${seam}" fill="none" stroke="${silver}" stroke-width="3.6" opacity="0.8" stroke-linecap="round"/>`;
    g+=`<path d="${seam}" fill="none" stroke="#c3c8a4" stroke-width="1.6" opacity="0.7" stroke-linecap="round"/>`;
    g+=`<path d="${seam}" fill="none" stroke="${mul(0.5)}" stroke-width="0.9" opacity="0.65" stroke-linecap="round"/>`;
  } else {
    // roast: deeper darker crease, a thinner drier silverskin trace catching the top light
    g+=`<path d="${valley}" fill="url(#${gcut})" opacity="0.85"/>`;
    g+=`<path d="${seam}" fill="none" stroke="${silver}" stroke-width="2.2" opacity="0.5" stroke-linecap="round"/>`;
    g+=`<path d="${seam}" fill="none" stroke="#120a06" stroke-width="1.3" opacity="0.85" stroke-linecap="round"/>`;
  }
  // sheen: a soft top-left glossy patch that sits ON the body (over the gradient), not a flat oval
  g+=`<ellipse cx="-8.5" cy="-10.5" rx="11" ry="8" fill="url(#${gsheen})"/>`;
  // ---- defect overlays (clipped to the bean body) ----
  if(overlay){
    const cid='bnc'+uid;
    g+=`<clipPath id="${cid}"><path d="${body}"/></clipPath><g clip-path="url(#${cid})">`;
    if(overlay==='scorch'){g+=`<ellipse cx="-11" cy="-3" rx="8" ry="6" fill="#160c04" opacity="0.85"/><ellipse cx="9" cy="8" rx="6" ry="4.5" fill="#160c04" opacity="0.8"/><ellipse cx="-11" cy="-3" rx="8" ry="6" fill="none" stroke="#000" stroke-width="0.6" opacity="0.4"/>`;}
    if(overlay==='tip'){g+=`<ellipse cx="-20" cy="0" rx="8" ry="7" fill="#120a04" opacity="0.9"/><ellipse cx="20" cy="0" rx="8" ry="7" fill="#120a04" opacity="0.9"/>`;}
    if(overlay==='face'){g+=`<path d="M0 -22 C -13.5 -21.5 -21.5 -12.5 -21.5 -0.5 C -21.5 12 -13.5 22 0 22 Z" fill="#0f0803" opacity="0.92"/>`;}
    if(overlay==='chip'){g+=`<path d="M11 -16 L26 -5 L22 10 L9 3 Z" fill="#0d0704"/><path d="M11 -16 L26 -5 L22 10 L9 3 Z" fill="none" stroke="${edge}" stroke-width="1"/>`;}
    if(overlay==='oil'){g+=`<ellipse cx="-7" cy="-8" rx="12" ry="8" fill="#fff" opacity="0.20"/><ellipse cx="9" cy="8" rx="8" ry="5" fill="#fff" opacity="0.15"/><ellipse cx="4" cy="-4" rx="18" ry="16" fill="#fff" opacity="0.05"/>`;}
    if(overlay==='fullblack'){g+=`<path d="${body}" fill="#0c0805" opacity="0.92"/><ellipse cx="-8" cy="-9" rx="9" ry="6" fill="#241a12" opacity="0.35"/>`;}
    if(overlay==='partblack'){g+=`<path d="M0 -22 C -13.5 -21.5 -21.5 -12.5 -21.5 -0.5 C -21.5 12 -13.5 22 0 22 Z" fill="#0c0805" opacity="0.9"/>`;}
    // sour: reddish-brown, over-fermented mottling + a reddish silverskin trace (per SCA description)
    if(overlay==='sour'){g+=`<path d="${body}" fill="#7a3a1e" opacity="0.6"/><ellipse cx="-7" cy="4" rx="13" ry="10" fill="#4a1c0c" opacity="0.55"/><ellipse cx="9" cy="-6" rx="8" ry="6" fill="#5e2812" opacity="0.5"/><ellipse cx="4" cy="12" rx="7" ry="5" fill="#3f1809" opacity="0.5"/><path d="${seam}" fill="none" stroke="#9a5236" stroke-width="2.2" opacity="0.7" stroke-linecap="round"/>`;}
    // insect (borer): several small deep holes with a darker bored rim
    if(overlay==='insect'){[[-12,-6,2.9],[6,-9,2.5],[12,5,2.7],[-4,9,2.4],[15,-1,2.2],[-14,5,2.3],[2,-2,2.0]].forEach(p=>{g+=`<circle cx="${p[0]}" cy="${p[1]}" r="${p[2]+0.8}" fill="#3a2a18" opacity="0.6"/><circle cx="${p[0]}" cy="${p[1]}" r="${p[2]}" fill="#160c05"/><circle cx="${p[0]+0.6}" cy="${p[1]+0.6}" r="${p[2]*0.4}" fill="#000" opacity="0.7"/>`;});}
    // broken/chipped: a clean cut face exposing the paler dense inner bean
    if(overlay==='broken'){g+=`<path d="M10 -17 L27 -4 L23 11 L8 3 Z" fill="${kind==='green'?'#c9cfa8':'#d8d2b0'}"/><path d="M10 -17 L27 -4 L23 11 L8 3 Z" fill="none" stroke="${edge}" stroke-width="1.1"/><path d="M13 -12 L23 -3" stroke="${mul(0.6)}" stroke-width="0.8" opacity="0.6"/><path d="M12 0 L22 6" stroke="${mul(0.6)}" stroke-width="0.8" opacity="0.5"/>`;}
    if(overlay==='floater'){g+=`<path d="${body}" fill="#e8e4d0" opacity="0.55"/><ellipse cx="-6" cy="-4" rx="13" ry="10" fill="#f2eeda" opacity="0.35"/>`;}
    // fungus/mould: powdery blotches ranging yellow -> reddish-brown (per references)
    if(overlay==='fungus'){g+=`<ellipse cx="-10" cy="-3" rx="9" ry="7" fill="#b8a238" opacity="0.68"/><ellipse cx="8" cy="7" rx="7" ry="6" fill="#8a5a26" opacity="0.62"/><circle cx="-3" cy="9" r="3.4" fill="#6e5820" opacity="0.6"/><circle cx="5" cy="-9" r="2.8" fill="#c0aa40" opacity="0.55"/><circle cx="-13" cy="6" r="2" fill="#9a7a2c" opacity="0.5"/>`;}
    // immature/underripe: pale yellowish-green body + strongly-adhering shiny silverskin down the seam
    if(overlay==='immature'){g+=`<path d="${body}" fill="#c2ca8e" opacity="0.6"/><path d="${valley}" fill="#eef0d8" opacity="0.6"/><path d="${seam}" fill="none" stroke="#f0f2dc" stroke-width="4.2" opacity="0.78" stroke-linecap="round"/><path d="M-18 -6 C -13 -2 -13 2 -18 6" fill="none" stroke="#eef0d8" stroke-width="2.2" opacity="0.55"/>`;}
    g+=`</g>`;
  }
  // shell/ear = a malformed concave bean; draw a distinct outline instead of the body overlay
  if(overlay==='shell'){g+=`<path d="M-4 -18 C 16 -12 16 12 -4 18 C 4 6 4 -6 -4 -18 Z" fill="${dark}" opacity="0.55" stroke="${edge}" stroke-width="1.2"/>`;}
  g+=`</g>`;
  return g;
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
  const W=760,H=230,cx=240,cy=112,rd=76;
  let g=`<defs><marker id="ah" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 z" fill="#e8dcc8"/></marker>
    <radialGradient id="drumWall" cx="0.5" cy="0.5" r="0.5"><stop offset="0.82" stop-color="#1a120a" stop-opacity="0"/><stop offset="1" stop-color="#c0433a" stop-opacity="0.35"/></radialGradient></defs>`;
  // drum: heavy metal wall ring + hot inner-wall glow
  g+=`<circle cx="${cx}" cy="${cy}" r="${rd}" fill="url(#drumWall)"/>`;
  g+=`<circle cx="${cx}" cy="${cy}" r="${rd}" fill="none" stroke="#8a7c66" stroke-width="5"/>`;
  g+=`<circle cx="${cx}" cy="${cy}" r="${rd-3}" fill="none" stroke="#c0433a" stroke-width="1.6" opacity="0.55"/>`;
  // tumbling beans piled at the bottom (like a real drum)
  const beans=[[-30,34],[-12,40],[8,42],[26,36],[-22,24],[0,28],[18,26],[-8,14],[10,16]];
  beans.forEach(b=>{g+=`<ellipse cx="${cx+b[0]}" cy="${cy+b[1]}" rx="9" ry="6" fill="#6a4326" stroke="#3a2414" stroke-width="0.8"/><path d="M${cx+b[0]} ${cy+b[1]-5} q-2 5 0 10" stroke="#e7dcc4" stroke-width="0.8" opacity="0.5" fill="none"/>`;});
  // 1) CONDUCTION: short bold arrow from hot wall directly into a bean touching it
  g+=`<path d="M${cx-rd+6} ${cy+30} L${cx-34} ${cy+30}" stroke="#c0433a" stroke-width="3" fill="none" marker-end="url(#ah)"/>`;
  // 2) CONVECTION: flowing air arrows curving up through the bean mass
  g+=`<path d="M${cx-24} ${cy+44} C${cx-30} ${cy} ${cx+10} ${cy-10} ${cx+4} ${cy-46}" stroke="#C9A34E" stroke-width="2.6" fill="none" marker-end="url(#ah)" opacity="0.9"/>`;
  g+=`<path d="M${cx+18} ${cy+40} C${cx+26} ${cy} ${cx+30} ${cy-16} ${cx+26} ${cy-42}" stroke="#C9A34E" stroke-width="2" fill="none" marker-end="url(#ah)" opacity="0.7"/>`;
  // 3) RADIATION: wavy infrared lines beaming inward from the wall
  for(let k=0;k<3;k++){const yy=cy-18+k*16;g+=`<path d="M${cx+rd-6} ${yy} q-10 -4 -20 0 q-10 4 -20 0" stroke="#e0864a" stroke-width="1.8" fill="none" opacity="0.8"/>`;}
  // legend on the right (wrapped)
  const leg=[['#c0433a','Conduction','Heat from the hot metal drum wall touching the beans.'],
             ['#C9A34E','Convection','Hot air moving through the bean mass \u2014 the biggest lever on most drums.'],
             ['#e0864a','Radiation','Infrared heat beaming off the drum and hot surfaces.']];
  leg.forEach((l,i)=>{const y=42+i*62;
    g+=`<rect x="440" y="${y-12}" width="14" height="14" rx="3" fill="${l[0]}"/>`;
    g+=`<text x="462" y="${y}" fill="${DIA.ink}" font-size="14" font-weight="700" font-family="ui-sans-serif">${l[1]}</text>`;
    g+=`<text x="462" fill="${DIA.ink3}" font-size="11.5" font-family="ui-sans-serif">${wrapTspans(l[2],462,y+17,14,34)}</text>`;});
  return diaWrap(`${W} ${H}`,g,'Three ways heat reaches the bean inside a drum roaster.');
}// 6. Extraction band: under / ideal / over.
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
  const W=760,H=180,cx1=180,cx2=560,cy=84;
  let g=diaDefs([DIA.dev,DIA.mail,DIA.accent]);
  g=`<defs>${diaArrowMarker(DIA.accent)}
    <linearGradient id="pfMetal" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8a8078"/><stop offset="0.5" stop-color="#d8d0c4"/><stop offset="1" stop-color="#6a625a"/></linearGradient></defs>`+g;
  // --- REAL PORTAFILTER (the dose) ---
  // stainless basket (tapered) holding a dry coffee puck, with a spouted body + handle
  const px=cx1;
  g+=`<path d="M${px-30} ${cy-24} L${px+30} ${cy-24} L${px+24} ${cy+14} L${px-24} ${cy+14} Z" fill="url(#pfMetal)" stroke="#5a544c" stroke-width="1.5"/>`; // basket
  g+=`<rect x="${px-33}" y="${cy-27}" width="66" height="6" rx="2" fill="url(#pfMetal)" stroke="#5a544c" stroke-width="1"/>`; // rim
  g+=`<rect x="${px-26} " y="${cy-21}" width="52" height="11" rx="2" fill="url(#${_cid(DIA.dev)})"/>`; // dry coffee puck
  for(let k=0;k<7;k++)g+=`<circle cx="${px-22+k*7.3}" cy="${cy-15}" r="0.9" fill="#3a2414" opacity="0.6"/>`; // grounds texture
  // spout + handle
  g+=`<path d="M${px-8} ${cy+14} L${px+8} ${cy+14} L${px+5} ${cy+26} L${px-5} ${cy+26} Z" fill="url(#pfMetal)" stroke="#5a544c" stroke-width="1"/>`;
  g+=`<rect x="${px+30}" y="${cy-6}" width="30" height="9" rx="4" fill="#2a2018" stroke="#5a544c" stroke-width="1"/>`; // handle
  g+=`<text x="${px}" y="${cy-2}" fill="#2a241c" font-size="12" font-weight="800" text-anchor="middle" font-family="ui-sans-serif">18 g</text>`;
  g+=`<text x="${px}" y="${cy+44}" fill="${DIA.ink}" font-size="12.5" text-anchor="middle" font-family="ui-sans-serif">dose (dry coffee)</text>`;
  // arrow
  g+=`<line x1="${px+66}" y1="${cy}" x2="${cx2-70}" y2="${cy}" stroke="${DIA.accent}" stroke-width="3" marker-end="url(#darr)"/>`;
  g+=`<text x="${(px+cx2)/2+20}" y="${cy-12}" fill="${DIA.accent}" font-size="13" font-weight="600" text-anchor="middle" font-family="ui-sans-serif">25\u201330 s \u00b7 9 bar</text>`;
  // --- REAL ESPRESSO CUP (the yield) ---
  const ux=cx2;
  g+=`<path d="M${ux-30} ${cy-24} Q${ux-34} ${cy+2} ${ux-22} ${cy+22} L${ux+22} ${cy+22} Q${ux+34} ${cy+2} ${ux+30} ${cy-24} Z" fill="#efe9dd" stroke="#b8ac98" stroke-width="1.6" filter="url(#dsoft)"/>`; // cup body
  g+=`<clipPath id="espCup"><path d="M${ux-30} ${cy-24} Q${ux-34} ${cy+2} ${ux-22} ${cy+22} L${ux+22} ${cy+22} Q${ux+34} ${cy+2} ${ux+30} ${cy-24} Z"/></clipPath>`;
  g+=`<g clip-path="url(#espCup)"><rect x="${ux-34}" y="${cy-12}" width="68" height="40" fill="url(#${_cid(DIA.dev)})"/><rect x="${ux-34}" y="${cy-16}" width="68" height="7" fill="#c69a6a"/></g>`; // espresso + crema
  g+=`<path d="M${ux+28} ${cy-18} q18 4 16 18 q-2 12 -16 12" fill="none" stroke="#b8ac98" stroke-width="3"/>`; // handle
  g+=`<ellipse cx="${ux}" cy="${cy+27}" rx="30" ry="4" fill="none" stroke="#8a7c66" stroke-width="1.3" opacity="0.6"/>`; // saucer
  g+=`<text x="${ux}" y="${cy+4}" fill="#f0e6d8" font-size="13" font-weight="800" text-anchor="middle" font-family="ui-sans-serif">36 g</text>`;
  g+=`<text x="${ux}" y="${cy+48}" fill="${DIA.ink}" font-size="12.5" text-anchor="middle" font-family="ui-sans-serif">yield (liquid espresso)</text>`;
  g+=`<text x="${W/2}" y="${cy+72}" fill="${DIA.ink3}" font-size="12.5" text-anchor="middle" font-family="ui-sans-serif">A 1:2 ratio \u2014 the modern espresso default. Weigh both, adjust grind to hit the time.</text>`;
  return diaWrap(`${W} ${H}`,g,'The standard espresso recipe as a ratio.');
}
// 8. Grind size across brew methods.
function diaGrind(){
  const W=760,H=210,L=20,T=24;const gap=(W-40)/4;
  const methods=[['Espresso','fine','~250 \u00b5m',3.2,34],['Pour-over','medium-fine','~600 \u00b5m',5.5,16],['Drip','medium','~800 \u00b5m',7,10],['French press','coarse','~1000 \u00b5m',11,6]];
  let g=diaDefs(['#8A5A34']);
  g+=`<defs><radialGradient id="grnd" cx="0.38" cy="0.32" r="0.72"><stop offset="0" stop-color="#7a5230"/><stop offset="1" stop-color="#3f2817"/></radialGradient></defs>`;
  // deterministic pseudo-random so builds are stable
  let seed=7;const rnd=()=>{seed=(seed*1103515245+12345)&0x7fffffff;return seed/0x7fffffff;};
  methods.forEach((m,i)=>{
    const cx=L+gap*i+gap/2, cy=T+58, R=42;
    // a round "pile" boundary (soft dish) for each grind
    g+=`<circle cx="${cx}" cy="${cy}" r="${R+6}" fill="#000" opacity="0.16" filter="url(#dsoft)"/>`;
    g+=`<circle cx="${cx}" cy="${cy}" r="${R+4}" fill="#241812"/>`;
    // scatter irregular coffee particles (rough polygons), sized by grind, filling the dish
    const pr=m[3], n=m[4];
    for(let k=0;k<n*4;k++){
      const ang=rnd()*6.283, rad=rnd()*R*0.94;
      const px=cx+Math.cos(ang)*rad, py=cy+Math.sin(ang)*rad*0.98;
      const s=pr*(0.7+rnd()*0.7);
      // irregular chip: a small rotated polygon
      const rot=rnd()*6.283;
      let pts='';
      const verts=5;
      for(let v=0;v<verts;v++){const va=rot+v/verts*6.283, vr=s*(0.6+rnd()*0.5);pts+=`${(px+Math.cos(va)*vr).toFixed(1)},${(py+Math.sin(va)*vr).toFixed(1)} `;}
      g+=`<polygon points="${pts.trim()}" fill="url(#grnd)" stroke="#2a1a10" stroke-width="0.4" opacity="0.95"/>`;
    }
    g+=`<circle cx="${cx}" cy="${cy}" r="${R+4}" fill="none" stroke="#4a3524" stroke-width="1"/>`;
    g+=`<text x="${cx.toFixed(0)}" y="${T+128}" fill="#f0e6d8" font-size="13.5" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${m[0]}</text>`;
    g+=`<text x="${cx.toFixed(0)}" y="${T+145}" fill="${DIA.ink3}" font-size="11.5" text-anchor="middle" font-family="ui-sans-serif">${m[1]}</text>`;
    g+=`<text x="${cx.toFixed(0)}" y="${T+161}" fill="#95602F" font-size="10.5" text-anchor="middle" font-family="ui-monospace">${m[2]}</text>`;
  });
  return diaWrap(`${W} ${H}`,g,'Grind size matched to method: short, intense brews need fine grounds; long, gentle ones need coarse.');
}// 9. Flavor wheel: 9 inner categories as a radial diagram.
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
  const W=760,H=220,cy=96;
  const cols=[
    ['Washed','#b8c48a','all fruit removed before drying','clean \u00b7 bright \u00b7 transparent',190,0],
    ['Honey','#d09a4a','skin off, sticky mucilage left on','sweet \u00b7 rounded \u00b7 in-between',380,1],
    ['Natural','#a0433a','whole cherry dried on the bean','fruity \u00b7 heavy \u00b7 wild',570,2],
  ];
  let g=diaDefs(['#9aaf6e','#b8c48a','#d09a4a','#a0433a']);
  g+=`<defs>`+
     `<radialGradient id="procCherry" cx="0.4" cy="0.32" r="0.85"><stop offset="0" stop-color="#c14a3c"/><stop offset="0.6" stop-color="#9a2e26"/><stop offset="1" stop-color="#6e2018"/></radialGradient>`+
     `<radialGradient id="procHoney" cx="0.4" cy="0.34" r="0.85"><stop offset="0" stop-color="#e8bc72"/><stop offset="0.6" stop-color="#cf9542"/><stop offset="1" stop-color="#a06f28"/></radialGradient>`+
     `</defs>`;
  cols.forEach(c=>{const cx=c[4], fruit=c[5];
    // fruit still on the bean: Natural = full cherry skin+pulp, Honey = sticky mucilage coat, Washed = bare
    if(fruit===2){ // natural: whole dried cherry around the seed
      g+=`<ellipse cx="${cx+1.5}" cy="${cy+4}" rx="43" ry="51" fill="#000" opacity="0.22" filter="url(#dsoft)"/>`;
      g+=`<ellipse cx="${cx}" cy="${cy}" rx="42" ry="50" fill="url(#procCherry)" stroke="#5f2018" stroke-width="1.6"/>`;
      // a wrinkle/shrivel hint (dried natural) + a glossy skin highlight
      g+=`<path d="M${cx-30} ${cy-8} Q${cx-24} ${cy+6} ${cx-30} ${cy+20}" fill="none" stroke="#6e2018" stroke-width="1.3" opacity="0.55"/>`;
      g+=`<path d="M${cx+30} ${cy-10} Q${cx+24} ${cy+4} ${cx+29} ${cy+18}" fill="none" stroke="#6e2018" stroke-width="1.3" opacity="0.5"/>`;
      g+=`<ellipse cx="${cx-14}" cy="${cy-18}" rx="12" ry="8" fill="#d86a54" opacity="0.5"/>`; // sheen
      g+=`<path d="M${cx} ${cy-50} q-4 -8 3 -14" stroke="#4a2216" stroke-width="3" fill="none" stroke-linecap="round"/>`; // stem
      // a cutaway window so the seed inside reads (the whole point of the panel)
      g+=`<path d="M${cx} ${cy-36} A36 44 0 0 1 ${cx} ${cy+36} Z" fill="#7a2a20" opacity="0.55"/>`;
    }
    if(fruit===1){ // honey: sticky translucent mucilage coat clinging to the seed
      g+=`<ellipse cx="${cx+1.5}" cy="${cy+3}" rx="35" ry="43" fill="#000" opacity="0.18" filter="url(#dsoft)"/>`;
      g+=`<ellipse cx="${cx}" cy="${cy}" rx="34" ry="42" fill="url(#procHoney)" stroke="${_rgba('#a06f28',0.8)}" stroke-width="1.6"/>`;
      // glossy sticky drip highlights
      g+=`<ellipse cx="${cx-11}" cy="${cy-16}" rx="9" ry="6" fill="#f0cc86" opacity="0.5"/>`;
      g+=`<path d="M${cx+18} ${cy+6} q3 8 -1 16" fill="none" stroke="#e8bc72" stroke-width="2" opacity="0.4" stroke-linecap="round"/>`;
    }
    // the seed itself (real bean) sits inside — green, kind='green'
    g+=diaBean(cx,cy,fruit===2?0.80:0.90,'#7f9464','green',null);
    // labels
    g+=`<text x="${cx}" y="${cy+74}" fill="${c[1]}" font-size="16" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${c[0]}</text>`;
    g+=`<text x="${cx}" y="${cy+92}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif">${c[2]}</text>`;
    g+=`<text x="${cx}" y="${cy-58}" fill="${DIA.ink}" font-size="11.5" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">${c[3]}</text>`;
  });
  return diaWrap(`${W} ${H}`,g,'The more fruit that stays on the bean during drying, the sweeter, fruitier, and heavier the cup \u2014 and the higher the risk of drying defects.');
}// 12. Milk steaming: two phases on a temperature track.
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
  [[4,'cold'],[37,'~37°C'],[65,'65°C stop']].forEach(t=>{g+=`<line x1="${X(t[0])}" y1="${cy+24}" x2="${X(t[0])}" y2="${cy+30}" stroke="${DIA.ink3}"/><text x="${X(t[0])}" y="${cy+44}" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-monospace">${t[1]}</text>`;});
  // danger zone
  g+=`<text x="${X(66)}" y="${cy-32}" fill="${DIA.hot}" font-size="11" text-anchor="end" font-family="ui-sans-serif">70°C+ scalds</text>`;
  g+=`<text x="${W/2}" y="${cy+78}" fill="${DIA.ink3}" font-size="12" text-anchor="middle" font-family="ui-sans-serif">Stretch first while the milk is cold, then texture. Stop by 65°C — past 70°C the milk scalds and the foam collapses.</text>`;
  return diaWrap(`${W} ${H}`,g,'The two phases of steaming milk, on a temperature track.');
}
// 13. Brew method families.
function diaBrewFamilies(){
  const W=760,H=230;
  const fam=[['Percolation','#C9A34E','water passes through once','V60 \u00b7 Chemex \u00b7 drip',150],
             ['Immersion','#7a9a6a','grounds steep, then separate','French press \u00b7 cold brew',380],
             ['Pressure','#d0553a','forced through a puck','espresso \u00b7 moka',610]];
  let g=`<defs>${diaArrowMarker('#e0864a')}</defs>`;
  fam.forEach(f=>{const cx=f[4],cy=86,col=f[1];
    if(f[0]==='Percolation'){
      // V60: a 60-degree cone with interior spiral ridges, a carafe below, a drip
      g+=`<path d="M${cx-34} ${cy-34} L${cx+34} ${cy-34} L${cx+3} ${cy+16} L${cx-3} ${cy+16} Z" fill="${_rgba(col,0.16)}" stroke="${col}" stroke-width="2.4" stroke-linejoin="round"/>`;
      // spiral ridge hints
      for(let i=1;i<=4;i++){const yy=cy-34+i*10, w=34-i*7.4;g+=`<line x1="${cx-w}" y1="${yy}" x2="${cx+w}" y2="${yy}" stroke="${col}" stroke-width="1" opacity="0.45"/>`;}
      // rim collar
      g+=`<line x1="${cx-38}" y1="${cy-34}" x2="${cx+38}" y2="${cy-34}" stroke="${col}" stroke-width="2.4"/>`;
      // ground bed inside
      g+=`<path d="M${cx-16} ${cy-9} L${cx+16} ${cy-9} L${cx+7} ${cy+8} L${cx-7} ${cy+8} Z" fill="#5a3a1e" opacity="0.6"/>`;
      // drip + carafe
      g+=`<line x1="${cx}" y1="${cy+16}" x2="${cx}" y2="${cy+30}" stroke="#6a8fb0" stroke-width="2"/>`;
      g+=`<path d="M${cx-22} ${cy+30} L${cx+22} ${cy+30} L${cx+18} ${cy+48} L${cx-18} ${cy+48} Z" fill="none" stroke="${col}" stroke-width="1.6" opacity="0.7"/>`;
      g+=`<path d="M${cx-19} ${cy+40} L${cx+19} ${cy+40} L${cx+18} ${cy+48} L${cx-18} ${cy+48} Z" fill="#3a2216" opacity="0.7"/>`;
    }
    if(f[0]==='Immersion'){
      // French press: glass carafe + lid + plunger rod/knob + mesh disc, grounds steeping
      g+=`<rect x="${cx-24}" y="${cy-26}" width="48" height="62" rx="4" fill="${_rgba(col,0.14)}" stroke="${col}" stroke-width="2.4"/>`;
      // brewed liquid
      g+=`<rect x="${cx-21}" y="${cy-8}" width="42" height="41" rx="2" fill="#3a2216" opacity="0.55"/>`;
      // steeping grounds
      for(let i=0;i<9;i++)g+=`<circle cx="${cx-16+((i*13)%34)}" cy="${cy+2+((i*9)%26)}" r="2" fill="#6a4326" opacity="0.9"/>`;
      // lid
      g+=`<rect x="${cx-27}" y="${cy-32}" width="54" height="8" rx="3" fill="${col}" opacity="0.5" stroke="${col}" stroke-width="1.6"/>`;
      // plunger rod + knob
      g+=`<line x1="${cx}" y1="${cy-32}" x2="${cx}" y2="${cy-46}" stroke="${col}" stroke-width="2.4"/>`;
      g+=`<circle cx="${cx}" cy="${cy-50}" r="5" fill="${_rgba(col,0.3)}" stroke="${col}" stroke-width="2"/>`;
      // mesh disc (mid-carafe)
      g+=`<line x1="${cx-20}" y1="${cy-6}" x2="${cx+20}" y2="${cy-6}" stroke="${col}" stroke-width="2" opacity="0.8"/>`;
      // handle
      g+=`<path d="M${cx+24} ${cy-16} q16 6 0 34" fill="none" stroke="${col}" stroke-width="2.2"/>`;
    }
    if(f[0]==='Pressure'){
      // Espresso portafilter: round group basket + spout + handle, twin shot pouring
      g+=`<ellipse cx="${cx}" cy="${cy-24}" rx="30" ry="9" fill="${_rgba(col,0.2)}" stroke="${col}" stroke-width="2.2"/>`; // basket rim
      g+=`<path d="M${cx-30} ${cy-24} L${cx-22} ${cy+2} L${cx+22} ${cy+2} L${cx+30} ${cy-24}" fill="${_rgba(col,0.14)}" stroke="${col}" stroke-width="2.2"/>`; // basket body
      g+=`<path d="M${cx-22} ${cy+2} L${cx-16} ${cy+12} L${cx+16} ${cy+12} L${cx+22} ${cy+2} Z" fill="${col}" opacity="0.5"/>`; // spout base
      // handle to the right
      g+=`<rect x="${cx+28}" y="${cy-28}" width="34" height="9" rx="4" fill="#2a2622" stroke="${col}" stroke-width="1.6"/>`;
      // twin espresso streams
      g+=`<line x1="${cx-6}" y1="${cy+12}" x2="${cx-6}" y2="${cy+34}" stroke="#7a4a2a" stroke-width="2.4"/>`;
      g+=`<line x1="${cx+6}" y1="${cy+12}" x2="${cx+6}" y2="${cy+34}" stroke="#7a4a2a" stroke-width="2.4"/>`;
      // little cup
      g+=`<path d="M${cx-14} ${cy+34} L${cx+14} ${cy+34} L${cx+11} ${cy+48} L${cx-11} ${cy+48} Z" fill="none" stroke="${col}" stroke-width="1.6" opacity="0.7"/>`;
      g+=`<path d="M${cx-13} ${cy+42} L${cx+13} ${cy+42} L${cx+11} ${cy+48} L${cx-11} ${cy+48} Z" fill="#3a2216" opacity="0.8"/>`;
      // downward pressure arrow above
      g+=`<path d="M${cx} ${cy-44} L${cx} ${cy-32}" stroke="${col}" stroke-width="2.4" marker-end="url(#darr)"/>`;
    }
    g+=`<text x="${cx}" y="${cy+74}" fill="${col}" font-size="15" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${f[0]}</text>`;
    g+=`<text x="${cx}" y="${cy+92}" fill="${DIA.ink}" font-size="11.5" text-anchor="middle" font-family="ui-sans-serif">${f[2]}</text>`;
    g+=`<text x="${cx}" y="${cy+108}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif">${f[3]}</text>`;
  });
  return diaWrap(`${W} ${H}`,g,'Almost every brewing method is one of three families \u2014 how the water and grounds meet.');
}// 14. Water balance: hardness vs alkalinity target box.
function diaWater(){
  const W=520,H=360,L=64,R=30,T=30,B=54,iw=W-L-R,ih=H-T-B;
  let g=`<defs>${diaArrowMarker('#8f7c66')}
    <radialGradient id="wtarget" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#7a9a6a" stop-opacity="0.32"/><stop offset="1" stop-color="#7a9a6a" stop-opacity="0"/></radialGradient></defs>`;
  // plot frame
  g+=`<rect x="${L}" y="${T}" width="${iw}" height="${ih}" fill="#161009" stroke="${DIA.line}" stroke-width="1.2"/>`;
  // faint gridlines (quarters)
  for(let i=1;i<4;i++){const gx=L+iw*i/4, gy=T+ih*i/4;
    g+=`<line x1="${gx}" y1="${T}" x2="${gx}" y2="${T+ih}" stroke="${DIA.line}" stroke-width="0.6" opacity="0.4"/>`;
    g+=`<line x1="${L}" y1="${gy}" x2="${L+iw}" y2="${gy}" stroke="${DIA.line}" stroke-width="0.6" opacity="0.4"/>`;
  }
  // soft "good zone" glow centered on the target
  const cx0=L+iw*0.55, cy0=T+ih*0.48;
  g+=`<ellipse cx="${cx0}" cy="${cy0}" rx="${iw*0.34}" ry="${ih*0.32}" fill="url(#wtarget)"/>`;
  // target sweet-spot box
  const bx=L+iw*0.4,bw=iw*0.32,by=T+ih*0.33,bh=ih*0.32;
  g+=`<rect x="${bx}" y="${by}" width="${bw}" height="${bh}" fill="#7a9a6a" opacity="0.28" stroke="#8fbf6a" stroke-width="2" rx="7"/>`;
  g+=`<text x="${(bx+bw/2).toFixed(0)}" y="${(by+bh/2-2).toFixed(0)}" fill="#a8cf88" font-size="13" font-weight="800" text-anchor="middle" font-family="ui-sans-serif">TARGET</text>`;
  g+=`<text x="${(bx+bw/2).toFixed(0)}" y="${(by+bh/2+14).toFixed(0)}" fill="${DIA.ink}" font-size="10" text-anchor="middle" font-family="ui-sans-serif">balanced water</text>`;
  // axes with arrowheads
  g+=`<line x1="${L}" y1="${T+ih}" x2="${L+iw+2}" y2="${T+ih}" stroke="#8f7c66" stroke-width="1.6" marker-end="url(#darr)"/>`;
  g+=`<line x1="${L}" y1="${T+ih}" x2="${L}" y2="${T-2}" stroke="#8f7c66" stroke-width="1.6" marker-end="url(#darr)"/>`;
  g+=`<text x="${(L+iw/2).toFixed(0)}" y="${H-16}" fill="${DIA.ink}" font-size="12" text-anchor="middle" font-family="ui-sans-serif">Hardness (minerals that extract) \u2192</text>`;
  g+=`<text x="20" y="${(T+ih/2).toFixed(0)}" fill="${DIA.ink}" font-size="12" text-anchor="middle" font-family="ui-sans-serif" transform="rotate(-90 20 ${(T+ih/2).toFixed(0)})">Alkalinity (buffer) \u2192</text>`;
  // corner annotations with a tiny colored dot each
  const corner=(x,y,anchor,t,c)=>{g+=`<circle cx="${anchor==='end'?x+6:x-6}" cy="${y-3}" r="2.5" fill="${c}" opacity="0.8"/>`;g+=`<text x="${x}" y="${y}" fill="${DIA.ink3}" font-size="10.5" text-anchor="${anchor}" font-family="ui-sans-serif">${t}</text>`;};
  corner(L+14,T+18,'start','flat, chalky','#8a7c66');
  corner(W-R-8,T+18,'end','harsh, scaly','#c0433a');
  corner(L+14,T+ih-8,'start','hollow, sour','#c9a34e');
  corner(W-R-8,T+ih-8,'end','bright but sharp','#8fbf3a');
  return diaWrap(`${W} ${H}`,g,'Coffee water is a balance of two things: enough hardness to extract flavor, low enough alkalinity to let acidity through.');
}// 15. Roaster types.
function diaRoasters(){
  const W=760,H=210;
  const t=[['Drum','#B07B3E','rotating metal drum over heat','body \u00b7 dark roasts \u00b7 workhorse',150],
           ['Fluid-bed','#C9A34E','beans levitated on hot air','fast \u00b7 clean \u00b7 bright roasts',400],
           ['Hybrid','#8A5A34','recirculated air + drum','blends both approaches',630]];
  let g=`<defs>${diaArrowMarker('#e0a860')}
    <marker id="ru2" markerWidth="8" markerHeight="8" refX="4" refY="1" orient="auto"><path d="M0 7 L4 0 L8 7 z" fill="#e0a860"/></marker></defs>`;
  t.forEach(r=>{const cx=r[4],cy=76,col=r[1];const met=_rgba(col,0.16);
    if(r[0]==='Drum'){
      // classic shop drum roaster: hopper on top, round drum body w/ front door, chimney, legs
      g+=`<path d="M${cx-14} ${cy-42} L${cx+14} ${cy-42} L${cx+8} ${cy-30} L${cx-8} ${cy-30} Z" fill="${met}" stroke="${col}" stroke-width="2"/>`; // hopper
      g+=`<line x1="${cx+26}" y1="${cy-44}" x2="${cx+26}" y2="${cy-18}" stroke="${col}" stroke-width="2.2"/>`; // chimney
      g+=`<circle cx="${cx}" cy="${cy-2}" r="30" fill="${met}" stroke="${col}" stroke-width="2.6"/>`; // drum body (round face)
      g+=`<circle cx="${cx}" cy="${cy-2}" r="20" fill="none" stroke="${_rgba(col,0.55)}" stroke-width="1.6"/>`; // door ring
      g+=`<circle cx="${cx}" cy="${cy-2}" r="3" fill="${col}"/>`; // door knob
      g+=`<circle cx="${cx-13}" cy="${cy-15}" r="2" fill="${_rgba(col,0.6)}"/><circle cx="${cx+13}" cy="${cy-15}" r="2" fill="${_rgba(col,0.6)}"/>`; // face bolts
      // rotation arrow: a 3/4 arc concentric with the drum face (circles the door knob)
      g+=`<path d="M${cx+7.7} ${cy-11.2} A12 12 0 1 1 ${cx-10.4} ${cy-10.0}" fill="none" stroke="${col}" stroke-width="1.5" opacity="0.65" marker-end="url(#darr)"/>`;
      // legs + base
      g+=`<rect x="${cx-30}" y="${cy+28}" width="60" height="6" rx="2" fill="${met}" stroke="${col}" stroke-width="1.4"/>`;
      g+=`<line x1="${cx-22}" y1="${cy+34}" x2="${cx-24}" y2="${cy+50}" stroke="${col}" stroke-width="2.2"/><line x1="${cx+22}" y1="${cy+34}" x2="${cx+24}" y2="${cy+50}" stroke="${col}" stroke-width="2.2"/>`;
      // flame under the drum
      for(let i=-1;i<=1;i++)g+=`<path d="M${cx+i*10} ${cy+28} q3 -8 0 -13 q-3 5 0 13" fill="#e0864a" opacity="0.75"/>`;
    }
    if(r[0]==='Fluid-bed'){
      // vertical column/popper air roaster: clear chamber on a base, beans floating on a jet
      g+=`<path d="M${cx-20} ${cy-40} L${cx+20} ${cy-40} L${cx+16} ${cy-6} L${cx-16} ${cy-6} Z" fill="${met}" stroke="${col}" stroke-width="2.4"/>`; // tapered glass chamber
      g+=`<line x1="${cx-20}" y1="${cy-40}" x2="${cx+20}" y2="${cy-40}" stroke="${col}" stroke-width="2.4"/>`; // chamber rim
      // levitating beans in the column
      [[-8,-30],[6,-34],[12,-24],[-3,-20],[8,-14],[-11,-13],[0,-26]].forEach(p=>{g+=`<ellipse cx="${cx+p[0]}" cy="${cy+p[1]}" rx="3.6" ry="2.5" fill="#6a4326"/>`;});
      // upward air jets
      for(let i=-1;i<=1;i++)g+=`<path d="M${cx+i*9} ${cy-6} L${cx+i*9} ${cy-36}" stroke="#e0a860" stroke-width="1.6" opacity="0.5" marker-end="url(#ru2)"/>`;
      // motor base + heating element
      g+=`<rect x="${cx-22}" y="${cy-6}" width="44" height="26" rx="5" fill="${met}" stroke="${col}" stroke-width="2.2"/>`;
      g+=`<path d="M${cx-14} ${cy+4} q7 -6 14 0 q7 6 14 0" fill="none" stroke="#e0864a" stroke-width="2" opacity="0.7"/>`; // coil
      g+=`<rect x="${cx-30}" y="${cy+20}" width="60" height="6" rx="2" fill="${met}" stroke="${col}" stroke-width="1.4"/>`; // foot
    }
    if(r[0]==='Hybrid'){
      // drum body + external air-recirculation ducting looping back in
      g+=`<circle cx="${cx}" cy="${cy-2}" r="28" fill="${met}" stroke="${col}" stroke-width="2.6"/>`;
      g+=`<circle cx="${cx}" cy="${cy-2}" r="18" fill="none" stroke="${_rgba(col,0.5)}" stroke-width="1.5"/>`;
      g+=`<circle cx="${cx}" cy="${cy-2}" r="3" fill="${col}"/>`;
      for(let i=0;i<4;i++){const a=i/4*6.28;g+=`<ellipse cx="${(cx+Math.cos(a)*10).toFixed(0)}" cy="${(cy-2+Math.sin(a)*10).toFixed(0)}" rx="3.4" ry="2.4" fill="#6a4326"/>`;}
      // recirc duct: out the top, loop right, back into the drum's right side (clear of the base)
      g+=`<path d="M${cx+4} ${cy-29} C${cx+46} ${cy-34} ${cx+50} ${cy+8} ${cx+26} ${cy+2}" fill="none" stroke="#e0a860" stroke-width="2.4" opacity="0.7" marker-end="url(#darr)"/>`;
      g+=`<text x="${cx+44}" y="${cy-8}" fill="#e0a860" font-size="8.5" text-anchor="middle" font-family="ui-sans-serif" opacity="0.85">air</text>`;
      // legs + base
      g+=`<rect x="${cx-28}" y="${cy+26}" width="56" height="6" rx="2" fill="${met}" stroke="${col}" stroke-width="1.4"/>`;
      g+=`<line x1="${cx-20}" y1="${cy+32}" x2="${cx-22}" y2="${cy+48}" stroke="${col}" stroke-width="2.2"/><line x1="${cx+20}" y1="${cy+32}" x2="${cx+22}" y2="${cy+48}" stroke="${col}" stroke-width="2.2"/>`;
      for(let i=-1;i<=1;i++)g+=`<path d="M${cx+i*10} ${cy+26} q3 -7 0 -12 q-3 5 0 12" fill="#e0864a" opacity="0.7"/>`;
    }
    g+=`<text x="${cx}" y="${cy+74}" fill="${col}" font-size="15" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${r[0]}</text>`;
    g+=`<text x="${cx}" y="${cy+92}" fill="${DIA.ink}" font-size="11" text-anchor="middle" font-family="ui-sans-serif">${r[2]}</text>`;
    g+=`<text x="${cx}" y="${cy+108}" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">${r[3]}</text>`;
  });
  return diaWrap(`${W} ${H}`,g,'The three main roaster architectures and what each is good at.');
}// 16. The waves of coffee as a timeline.
function diaWaves(){
  const W=760,H=250,L=20,R=20,T=30,iw=W-L-R,axisY=H-56;
  const waves=[['1st','1800s+','Commodity','cheap · instant · no origin','#8f7c66',.13],
    ['2nd','1960s+','Experience','café · espresso · Starbucks','#B07B3E',.34],
    ['3rd','2000s+','Craft','single origin · light · direct trade','#C9A34E',.62],
    ['4th','now','Science + home','precision · at-home · community','#e0864a',.88]];
  let g=diaDefs(waves.map(w=>w[4]));
  g+=`<line x1="${L}" y1="${axisY}" x2="${W-R}" y2="${axisY}" stroke="${DIA.line}" stroke-width="2"/>`;
  waves.forEach((w,i)=>{const x=L+iw*w[5];const barH=58+i*30;const y=axisY-barH;
    const cardW=124, hw=cardW/2;
    g+=`<rect x="${(x-hw).toFixed(0)}" y="${y.toFixed(0)}" width="${cardW}" height="${barH}" rx="7" fill="url(#${_cid(w[4])})" stroke="${w[4]}" stroke-width="1.5" filter="url(#dsoft)"/>`;
    // number + name stacked near the top of the card (always fits)
    g+=`<text x="${x.toFixed(0)}" y="${(y+26).toFixed(0)}" fill="${w[4]}" font-size="19" font-weight="800" text-anchor="middle" font-family="ui-sans-serif">${w[0]}</text>`;
    g+=`<text x="${x.toFixed(0)}" y="${(y+43).toFixed(0)}" fill="${DIA.ink}" font-size="11.5" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${w[2]}</text>`;
    // detail line on the taller cards — wrap onto two lines so it stays inside the card width
    if(barH>=88){
      const parts=w[3].split(' · ');
      const l1=parts.slice(0,Math.ceil(parts.length/2)).join(' · ');
      const l2=parts.slice(Math.ceil(parts.length/2)).join(' · ');
      g+=`<text x="${x.toFixed(0)}" y="${(y+60).toFixed(0)}" fill="#d8c8b0" font-size="9" text-anchor="middle" font-family="ui-sans-serif">${l1}</text>`;
      if(l2)g+=`<text x="${x.toFixed(0)}" y="${(y+72).toFixed(0)}" fill="#d8c8b0" font-size="9" text-anchor="middle" font-family="ui-sans-serif">${l2}</text>`;
    }
    g+=`<circle cx="${x.toFixed(0)}" cy="${axisY}" r="5" fill="${w[4]}"/>`;
    g+=`<text x="${x.toFixed(0)}" y="${axisY+22}" fill="${DIA.ink3}" font-size="11.5" text-anchor="middle" font-family="ui-monospace">${w[1]}</text>`;
  });
  g+=`<text x="${W-R}" y="${axisY+40}" fill="${DIA.ink3}" font-size="11" text-anchor="end" font-family="ui-sans-serif" font-style="italic">rising focus on the bean itself →</text>`;
  return diaWrap(`${W} ${H}`,g,'The waves overlap rather than replace each other — each is a shift in how people relate to coffee.');
}
// 17. Supply chain: cherry to cup with value flow.
function diaSupplyChain(){
  const W=760,H=200,cy=70,L=20;
  const steps=[['Farmer','grows and picks','#7d8f5a'],['Mill','processes green','#95602F'],['Exporter','+ Importer','#B07B3E'],['Roaster','roasts and sells','#8A5A34'],['Café / You','brews','#e0864a']];
  const gap=(W-40)/steps.length;
  let g=diaDefs(steps.map(s=>s[2]));
  g=`<defs>${diaArrowMarker(DIA.ink3)}</defs>`+g;
  steps.forEach((s,i)=>{const cx=L+gap*i+gap/2;
    g+=`<circle cx="${cx.toFixed(0)}" cy="${cy}" r="30" fill="url(#${_cid(s[2])})" stroke="${s[2]}" stroke-width="2" filter="url(#dsoft)"/>`;
    g+=`<text x="${cx.toFixed(0)}" y="${cy+5}" fill="${s[2]}" font-size="13" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${s[0].split(' ')[0]}</text>`;
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
  const comps=[['Base','body &amp; sweetness','#8A5A34',30],['Bright','acidity &amp; lift','#C9A34E',86],['Accent','aromatics','#e0864a',142]];
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
  const W=520,H=340,cx=196,cy=170;
  let g=diaDefs(['#c0433a','#d98a3a','#e8c27a','#9aaf6e']);
  const layerGrad=(id,c0,c1)=>`<radialGradient id="${id}" cx="0.4" cy="0.34" r="0.75"><stop offset="0" stop-color="${c0}"/><stop offset="1" stop-color="${c1}"/></radialGradient>`;
  g+=`<defs>`+layerGrad('chSkin','#e05a4a','#9c2f27')+layerGrad('chPulp','#e79a4a','#b56a24')+layerGrad('chMuc','#f0cf86','#c69a4e')+layerGrad('chParch','#e6dcc4','#bcac90')+layerGrad('chBean','#a6bb7c','#6f8a4c')+`<radialGradient id="chGloss" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#fff" stop-opacity="0.16"/><stop offset="0.7" stop-color="#fff" stop-opacity="0"/></radialGradient>`+`</defs>`;
  const ov=(rx,ry,fill)=>`<ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" fill="${fill}"/>`;
  g+=`<ellipse cx="${cx}" cy="${cy+6}" rx="98" ry="104" fill="#000" opacity="0.3" filter="url(#dsh)"/>`;
  g+=ov(96,102,'url(#chSkin)');
  g+=ov(82,88,'url(#chPulp)');
  g+=ov(64,70,'url(#chMuc)');
  g+=ov(54,60,'url(#chParch)');
  const bean=(sign)=>`<path d="M${cx} ${cy-44} C${cx+sign*4} ${cy-46} ${cx+sign*40} ${cy-40} ${cx+sign*40} ${cy} C${cx+sign*40} ${cy+40} ${cx+sign*4} ${cy+46} ${cx} ${cy+44} Z" fill="url(#chBean)" stroke="#5a4632" stroke-width="1.4"/>`;
  g+=bean(1)+bean(-1);
  g+=`<path d="M${cx} ${cy-42} Q${cx-2} ${cy} ${cx} ${cy+42}" stroke="#4a3826" stroke-width="1.6" fill="none" opacity="0.8"/>`;
  g+=`<path d="M${cx-14} ${cy-30} Q${cx-22} ${cy} ${cx-14} ${cy+30}" stroke="#5a7038" stroke-width="1" fill="none" opacity="0.4"/>`;
  g+=`<path d="M${cx+14} ${cy-30} Q${cx+22} ${cy} ${cx+14} ${cy+30}" stroke="#5a7038" stroke-width="1" fill="none" opacity="0.4"/>`;
  g+=`<ellipse cx="${cx}" cy="${cy}" rx="42" ry="47" fill="none" stroke="#efe6d2" stroke-width="1.3" opacity="0.55"/>`;
  g+=`<ellipse cx="${cx-20}" cy="${cy-34}" rx="60" ry="46" fill="url(#chGloss)"/>`;
  g+=`<path d="M${cx} ${cy-102} q-4 -10 2 -18" stroke="#7a4a2a" stroke-width="3" fill="none" stroke-linecap="round"/>`;
  const labs=[['#e05a4a','Skin (exocarp)','the outer red/yellow layer',cx+78,cy-72],['#e79a4a','Pulp (mesocarp)','sweet fruit flesh',cx+70,cy-30],['#f0cf86','Mucilage','sticky sugary layer',cx+58,cy+14],['#e6dcc4','Parchment','papery seed casing',cx+48,cy+50],['#a6bb7c','Seed = green bean','usually two per cherry',cx+30,cy+82]];
  labs.forEach((l,i)=>{const y=44+i*56, lx=346;g+=`<path d="M${l[3]} ${l[4]} L${lx-8} ${y-6}" stroke="${l[0]}" stroke-width="1" opacity="0.5" fill="none"/>`;g+=`<circle cx="${l[3]}" cy="${l[4]}" r="2" fill="${l[0]}"/>`;g+=`<rect x="${lx}" y="${y-13}" width="13" height="13" rx="3" fill="${l[0]}" filter="url(#dsoft)"/><text x="${lx+20}" y="${y-2}" fill="#f0e6d8" font-size="13" font-weight="700" font-family="ui-sans-serif">${l[1]}</text><text x="${lx+20}" y="${y+14}" fill="${DIA.ink3}" font-size="11" font-family="ui-sans-serif">${l[2]}</text>`;});
  return diaWrap(`${W} ${H}`,g,'A coffee cherry in cross-section \u2014 processing removes the outer fruit layers to reach the seed.');
}// 20. Varietal family tree.
function diaVarTree(){
  const W=760,H=390;
  // lineage colors: Typica gold-green, Bourbon gold, crosses brown, Geisha pink
  const ETH='#6f9a4a', TYP='#8caf5a', BOU='#C9A34E', CROSS='#9a6a3a', HYB='#a0522d', GSH='#c07fa8';
  let g=diaDefs([ETH,TYP,BOU,CROSS,HYB,GSH,'#B07B3E']);
  // solid node card with colored top-accent bar + gradient + shadow (family-tree style)
  const node=(x,y,w,label,color,sub,big)=>{
    const h=big?40:34;
    let s=`<g filter="url(#dsoft)"><rect x="${x-w/2}" y="${y}" width="${w}" height="${h}" rx="8" fill="#241a12" stroke="${color}" stroke-width="1.3"/>`;
    s+=`<rect x="${x-w/2}" y="${y}" width="${w}" height="3.5" rx="1.75" fill="${color}"/>`;
    s+=`<rect x="${x-w/2}" y="${y+2}" width="${w}" height="${h-2}" rx="7" fill="url(#${_cid(color)})"/>`;
    s+=`<text x="${x}" y="${y+(sub?18:22)}" fill="#f5ecdd" font-size="12.5" font-weight="${big?800:700}" text-anchor="middle" font-family="ui-sans-serif">${label}</text>`;
    if(sub)s+=`<text x="${x}" y="${y+31}" fill="#a2907a" font-size="9" text-anchor="middle" font-family="ui-sans-serif">${sub}</text>`;
    s+=`</g>`;return s;
  };
  const link=(x1,y1,x2,y2,c)=>`<path d="M${x1} ${y1} C ${x1} ${(y1+y2)/2}, ${x2} ${(y1+y2)/2}, ${x2} ${y2}" stroke="${c||'#7a6a52'}" stroke-width="1.5" fill="none" opacity="0.55"/>`;
  // ---- root ----
  g+=node(380,24,190,'Ethiopian Arabica',ETH,'wild origin, 1000s of types',true);
  // ---- two founders ----
  g+=link(380,64,185,104,TYP)+link(380,64,575,104,BOU);
  g+=node(185,104,150,'Typica',TYP,'clean, sweet',true);
  g+=node(575,104,150,'Bourbon',BOU,'sweet, productive',true);
  // ---- typica children ----
  g+=link(185,144,110,196,TYP)+link(185,144,270,196,TYP);
  g+=node(110,196,130,'Maragogype','#B07B3E','giant beans',false);
  g+=node(270,196,130,'Kona / JBM','#B07B3E','island coffees',false);
  // ---- bourbon children ----
  g+=link(575,144,490,196,BOU)+link(575,144,660,196,BOU);
  g+=node(490,196,130,'Caturra','#B07B3E','compact mutation',false);
  g+=node(660,196,130,'SL28 / SL34','#B07B3E','Kenya, wine-like',false);
  // ---- crosses row ----
  g+=link(270,230,345,286,CROSS)+link(490,230,345,286,CROSS);
  g+=node(345,286,140,'Mundo Novo',CROSS,'Bourbon \u00d7 Typica',false);
  g+=link(490,230,510,286,CROSS);
  g+=node(510,286,130,'Catua\u00ed',CROSS,'Caturra \u00d7 M.Novo',false);
  g+=link(660,230,660,286,HYB);
  g+=node(660,286,130,'Catimor',HYB,'\u00d7 Timor (rust-res.)',false);
  // ---- Geisha standalone (own lineage, clearly separated bottom-left) ----
  g+=node(120,300,150,'Geisha',GSH,'Ethiopia \u2192 Panama',false);
  g+=`<text x="120" y="346" fill="${DIA.ink3}" font-size="9.5" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">its own lineage \u00b7 stands apart</text>`;
  return diaWrap(`${W} ${H}`,g,'A simplified Arabica family tree \u2014 most classic varieties branch from Typica and Bourbon (real genetics are messier).');
}// 21. Pour-over method steps.
function diaPourover(){
  const W=760,H=190,L=20;
  const steps=[['1','Rinse','wet the filter, dump water'],['2','Bloom','2\u00d7 coffee wt, wait 30\u201345s'],['3','Pour','slow, even, to target'],['4','Draw down','let it finish, ~3 min']];
  const gap=(W-40)/steps.length;
  let g=diaDefs(['#C9A34E']);
  const col='#C9A34E';
  steps.forEach((s,i)=>{const cx=L+gap*i+gap/2,cy=70;
    // realistic V60 cone: body + rim collar + interior spiral ridges
    g+=`<path d="M${cx-30} ${cy-30} L${cx+30} ${cy-30} L${cx+3} ${cy+16} L${cx-3} ${cy+16} Z" fill="${_rgba(col,0.12)}" stroke="${col}" stroke-width="2.2" stroke-linejoin="round"/>`;
    g+=`<line x1="${cx-34}" y1="${cy-30}" x2="${cx+34}" y2="${cy-30}" stroke="${col}" stroke-width="2.2"/>`;
    for(let k=1;k<=3;k++){const yy=cy-30+k*11, ww=30-k*8;g+=`<line x1="${cx-ww}" y1="${yy}" x2="${cx+ww}" y2="${yy}" stroke="${col}" stroke-width="0.9" opacity="0.4"/>`;}
    // ground bed inside (present from bloom on)
    if(i>=1)g+=`<path d="M${cx-15} ${cy-10} L${cx+15} ${cy-10} L${cx+7} ${cy+6} L${cx-7} ${cy+6} Z" fill="#5a3a1e" opacity="0.6"/>`;
    // step-specific action
    if(i===0){ // rinse: water sheeting the filter (blue tint) + discard
      g+=`<path d="M${cx-24} ${cy-22} L${cx+24} ${cy-22} L${cx+5} ${cy+10} L${cx-5} ${cy+10} Z" fill="#6a8fb0" opacity="0.28"/>`;
    }
    if(i===1){ // bloom: puffed grounds + CO2 bubbles
      for(let k=0;k<4;k++)g+=`<circle cx="${cx-9+k*6}" cy="${cy-13-((k%2)*3)}" r="1.8" fill="#8a6a44" opacity="0.8"/>`;
    }
    if(i>=2){ // pour: water stream from above
      g+=`<line x1="${cx}" y1="${cy-44}" x2="${cx}" y2="${cy-30}" stroke="#6a8fb0" stroke-width="2.4"/>`;
      g+=`<circle cx="${cx}" cy="${cy-46}" r="1.6" fill="#8fb0cc"/>`;
    }
    if(i>=2){ // drips into carafe below
      for(let k=0;k<2;k++)g+=`<line x1="${cx-3+k*6}" y1="${cy+16}" x2="${cx-3+k*6}" y2="${cy+30}" stroke="#6a8fb0" stroke-width="1.8"/>`;
    }
    if(i===3){ // draw down: a small carafe with brewed coffee
      g+=`<path d="M${cx-20} ${cy+30} L${cx+20} ${cy+30} L${cx+16} ${cy+46} L${cx-16} ${cy+46} Z" fill="none" stroke="${col}" stroke-width="1.5" opacity="0.7"/>`;
      g+=`<path d="M${cx-17} ${cy+40} L${cx+17} ${cy+40} L${cx+16} ${cy+46} L${cx-16} ${cy+46} Z" fill="#3a2216" opacity="0.8"/>`;
    }
    // step badge + labels
    g+=`<circle cx="${cx}" cy="${cy+62}" r="12" fill="url(#${_cid(col)})" stroke="${col}" stroke-width="1.5" filter="url(#dsoft)"/><text x="${cx}" y="${cy+66}" fill="#e6c88a" font-size="12" font-weight="700" text-anchor="middle" font-family="ui-monospace">${s[0]}</text>`;
    g+=`<text x="${cx}" y="${cy+90}" fill="#f0e6d8" font-size="13" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${s[1]}</text>`;
    g+=`<text x="${cx}" y="${cy+106}" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">${s[2]}</text>`;
  });
  return diaWrap(`${W} ${H}`,g,'The universal pour-over sequence, whatever cone you use.');
}// 22. Cold brew vs iced coffee.
function diaColdBrew(){
  const W=760,H=210,cxA=200,cxB=560,cy=64;
  let g=diaDefs(['#d0553a','#6a8fb0']);
  g=`<defs>${diaArrowMarker('#8a7660')}
    <linearGradient id="cbcoffee" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6b4326"/><stop offset="1" stop-color="#3a2415"/></linearGradient></defs>`+g;
  // --- ICED COFFEE: a tall glass, dark coffee, ice cubes floating, condensation ---
  const glass=(cx,fill,label,l1,l2)=>{
    let s='';
    const gx=cx-24,gw=48,gy=cy-38,gh=84;
    // glass outline (slightly tapered tumbler)
    s+=`<path d="M${gx} ${gy} L${gx+gw} ${gy} L${gx+gw-4} ${gy+gh} L${gx+4} ${gy+gh} Z" fill="none" stroke="#b8ac98" stroke-width="2" filter="url(#dsoft)"/>`;
    // liquid fill
    s+=`<clipPath id="cl${cx}"><path d="M${gx+1} ${gy+14} L${gx+gw-1} ${gy+14} L${gx+gw-4} ${gy+gh-1} L${gx+4} ${gy+gh-1} Z"/></clipPath>`;
    s+=`<g clip-path="url(#cl${cx})"><rect x="${gx}" y="${gy+14}" width="${gw}" height="${gh}" fill="${fill}"/></g>`;
    return {s,gx,gw,gy,gh};
  };
  // iced coffee
  let A=glass(cxA,'url(#cbcoffee)');
  g+=A.s;
  // ice cubes floating near the top
  [[cxA-10,cy-30],[cxA+8,cy-26],[cxA-2,cy-16]].forEach(p=>{g+=`<rect x="${p[0]-6}" y="${p[1]-6}" width="12" height="12" rx="2" transform="rotate(${(p[0]%20)-10} ${p[0]} ${p[1]})" fill="#bcd6e8" opacity="0.55" stroke="#dcecf5" stroke-width="0.8"/>`;});
  // straw
  g+=`<line x1="${cxA+10}" y1="${cy-44}" x2="${cxA+2}" y2="${cy+40}" stroke="#d0553a" stroke-width="3"/>`;
  g+=`<text x="${cxA}" y="${cy+64}" fill="#f0e6d8" font-size="14" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">Iced coffee</text>`;
  g+=`<text x="${cxA}" y="${cy+82}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif">brew HOT, then pour over ice</text>`;
  g+=`<text x="${cxA}" y="${cy+98}" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">keeps acidity & aroma</text>`;
  // cold brew: mason jar with grounds steeping (dots suspended), no ice
  let B=glass(cxB,'url(#cbcoffee)');
  g+=B.s;
  // steeping grounds suspended throughout
  for(let i=0;i<14;i++){const px=cxB-16+((i*13)%34),py=cy-28+((i*17)%62);g+=`<circle cx="${px}" cy="${py}" r="2" fill="#4a2f18" opacity="0.85"/>`;}
  // jar lid rim
  g+=`<rect x="${cxB-26}" y="${cy-42}" width="52" height="7" rx="2" fill="#6a8fb0" opacity="0.5" stroke="#6a8fb0" stroke-width="1.4"/>`;
  g+=`<text x="${cxB}" y="${cy+64}" fill="#f0e6d8" font-size="14" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">Cold brew</text>`;
  g+=`<text x="${cxB}" y="${cy+82}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif">steep COLD 12\u201324 h, never heated</text>`;
  g+=`<text x="${cxB}" y="${cy+98}" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">smooth, low-acid, sweet</text>`;
  // center divider + labels of the KEY difference (heat vs no heat)
  const midX=(cxA+cxB)/2;
  g+=`<line x1="${midX}" y1="26" x2="${midX}" y2="150" stroke="${DIA.line}" stroke-dasharray="4 4"/>`;
  g+=`<circle cx="${midX}" cy="${cy}" r="18" fill="#160e08" stroke="${DIA.ink3}" stroke-width="1.2"/>`;
  g+=`<text x="${midX}" y="${cy+4}" fill="${DIA.ink3}" font-size="10" text-anchor="middle" font-family="ui-sans-serif">HEAT?</text>`;
  return diaWrap(`${W} ${H}`,g,'Same beans, opposite drinks \u2014 heat (or its absence) changes everything.');
}// 23. Brew troubleshooting decision.
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
  const W=760,H=250;
  // Each drink drawn in its REAL vessel. Fractions are of the FILLED liquid height (esp/milk/foam).
  // vessel: 'espcup'(macchiato), 'gibraltar'(cortado glass), 'cup'(flat white), 'bowl'(cappuccino), 'latteglass'(latte)
  const drinks=[
    ['Macchiato', 52,.70,.00,.30,'espcup'],    // tiny espresso cup, just a foam stain
    ['Cortado',   62,.50,.50,.00,'gibraltar'],  // Gibraltar glass, 1:1, no foam
    ['Flat White',72,.34,.56,.10,'cup'],        // ceramic cup, thin microfoam
    ['Cappuccino',82,.32,.30,.38,'bowl'],       // rounded cup, tall foam dome
    ['Latte',     86,.22,.66,.12,'latte'],      // wide bowl ceramic cup, thin foam
  ];
  const baseY=196, gap=(W-40)/drinks.length;
  const ESP='#43260f', MILK='#efe4d2', FOAM='#f8f2e6', GLASS='#c3b7a2', GLASSD='#8a7c66';
  let g=diaDefs(['#43260f','#efe4d2']);
  drinks.forEach((dk,i)=>{const [name,h,ef,mf,ff,vessel]=dk;
    const cx=20+gap*i+gap/2, top=baseY-h;
    const clip='md'+i;
    let wall, foot=null, saucer=false, handle=null, rimW;
    const midY=(top+baseY)/2;

    if(vessel==='espcup'){
      // small espresso cup: flared rim, rounded belly, tucked-in foot
      const rT=18, rB=11;
      wall=`M${cx-rT} ${top} C${cx-rT+1} ${top+h*0.5} ${cx-rB-2} ${baseY-4} ${cx-rB} ${baseY} L${cx+rB} ${baseY} C${cx+rB+2} ${baseY-4} ${cx+rT-1} ${top+h*0.5} ${cx+rT} ${top} Z`;
      rimW=rT; foot={r:rB+3,y:baseY}; saucer=true;
      handle=`M${cx+rT-1} ${top+h*0.34} q13 1 12 ${h*0.26} q-1 ${h*0.14} -12 ${h*0.12}`;
    } else if(vessel==='gibraltar'){
      // Gibraltar / cortado glass: straight walls, slight flare at rim, thick glass base (no saucer)
      const rT=21, rB=18;
      wall=`M${cx-rT} ${top} L${cx-rB} ${baseY} L${cx+rB} ${baseY} L${cx+rT} ${top} Z`;
      rimW=rT; foot={r:rB,y:baseY,glass:true};
    } else if(vessel==='cup'){
      // flat-white ceramic cup: wide, rounded, shorter — wider than tall feel
      const rT=27, rB=17;
      wall=`M${cx-rT} ${top} C${cx-rT-2} ${top+h*0.55} ${cx-rB-3} ${baseY-3} ${cx-rB} ${baseY} L${cx+rB} ${baseY} C${cx+rB+3} ${baseY-3} ${cx+rT+2} ${top+h*0.55} ${cx+rT} ${top} Z`;
      rimW=rT; foot={r:rB+2,y:baseY}; saucer=true;
      handle=`M${cx+rT-1} ${top+h*0.36} q17 1 16 ${h*0.30} q-1 ${h*0.16} -16 ${h*0.13}`;
    } else if(vessel==='bowl'){
      // cappuccino: big rounded bowl cup
      const rT=30, rB=18;
      wall=`M${cx-rT} ${top} C${cx-rT-4} ${top+h*0.5} ${cx-rB-4} ${baseY-3} ${cx-rB} ${baseY} C${cx} ${baseY+4} ${cx} ${baseY+4} ${cx+rB} ${baseY} C${cx+rB+4} ${baseY-3} ${cx+rT+4} ${top+h*0.5} ${cx+rT} ${top} Z`;
      rimW=rT; foot={r:rB+2,y:baseY}; saucer=true;
      handle=`M${cx+rT-2} ${top+h*0.34} q19 1 18 ${h*0.30} q-1 ${h*0.15} -18 ${h*0.12}`;
    } else { // latte — wide bowl-shaped ceramic cup with a handle (the café classic, biggest of the set)
      const rT=34, rB=20;
      wall=`M${cx-rT} ${top} C${cx-rT-4} ${top+h*0.52} ${cx-rB-5} ${baseY-3} ${cx-rB} ${baseY} C${cx} ${baseY+5} ${cx} ${baseY+5} ${cx+rB} ${baseY} C${cx+rB+5} ${baseY-3} ${cx+rT+4} ${top+h*0.52} ${cx+rT} ${top} Z`;
      rimW=rT; foot={r:rB+3,y:baseY}; saucer=true;
      handle=`M${cx+rT-2} ${top+h*0.30} q21 1 20 ${h*0.32} q-1 ${h*0.16} -20 ${h*0.13}`;
    }

    // draw handle behind the cup
    if(handle)g+=`<path d="${handle}" fill="none" stroke="${GLASS}" stroke-width="4" opacity="0.85"/>`;

    // fills clipped to the wall interior (espresso at bottom, milk, then foam on top)
    g+=`<defs><clipPath id="${clip}"><path d="${wall}"/></clipPath></defs>`;
    g+=`<g clip-path="url(#${clip})">`;
    const eH=h*ef, mH=h*mf, fH=h*ff;
    // faint glass tint so an empty glass still reads as glass
    if(foot&&foot.glass)g+=`<rect x="${cx-40}" y="${top-2}" width="80" height="${h+6}" fill="#dfe7ee" opacity="0.05"/>`;
    g+=`<rect x="${cx-40}" y="${baseY-eH}" width="80" height="${eH+3}" fill="url(#${_cid('#43260f')})"/>`;
    if(mH>0)g+=`<rect x="${cx-40}" y="${baseY-eH-mH}" width="80" height="${mH+1}" fill="url(#${_cid('#efe4d2')})"/>`;
    if(fH>0)g+=`<rect x="${cx-40}" y="${baseY-eH-mH-fH}" width="80" height="${fH+1}" fill="${FOAM}"/>`;
    // crema line between espresso and milk
    if(mH>0)g+=`<rect x="${cx-40}" y="${baseY-eH-1.5}" width="80" height="3" fill="#5a3418" opacity="0.45"/>`;
    // domed foam highlight for the foamy drinks
    if(ff>0.2)g+=`<ellipse cx="${cx-rimW*0.18}" cy="${baseY-eH-mH-fH*0.5}" rx="${rimW*0.5}" ry="${fH*0.35}" fill="#fff" opacity="0.3"/>`;
    g+=`</g>`;

    // cappuccino foam dome rising ABOVE the rim
    if(vessel==='bowl'){g+=`<path d="M${cx-rimW+3} ${top+2} Q${cx} ${top-9} ${cx+rimW-3} ${top+2} Z" fill="${FOAM}"/><path d="M${cx-rimW+3} ${top+2} Q${cx} ${top-9} ${cx+rimW-3} ${top+2}" fill="none" stroke="${GLASSD}" stroke-width="1" opacity="0.4"/>`;}

    // vessel wall stroke on top
    g+=`<path d="${wall}" fill="none" stroke="${GLASS}" stroke-width="1.8"/>`;
    // rim ellipse (opening) for round vessels so the top reads as a mouth, not a flat cut
    if(vessel!=='gibraltar')g+=`<ellipse cx="${cx}" cy="${top}" rx="${rimW}" ry="${rimW*0.22}" fill="none" stroke="${GLASS}" stroke-width="1.5" opacity="0.8"/>`;

    // FOOT / base — a real base, not a floating coin
    if(foot){
      if(foot.stem){ // latte glass: short stem + a flat foot disc
        g+=`<line x1="${cx}" y1="${baseY-2}" x2="${cx}" y2="${baseY+5}" stroke="${GLASS}" stroke-width="2.5"/>`;
        g+=`<path d="M${cx-foot.r} ${baseY+7} Q${cx} ${baseY+9} ${cx+foot.r} ${baseY+7}" fill="none" stroke="${GLASS}" stroke-width="2"/>`;
      } else if(foot.glass){ // gibraltar: a subtle thick-glass base band
        g+=`<line x1="${cx-foot.r+1}" y1="${baseY}" x2="${cx+foot.r-1}" y2="${baseY}" stroke="${GLASS}" stroke-width="2.4" opacity="0.9"/>`;
        g+=`<line x1="${cx-foot.r+3}" y1="${baseY-4}" x2="${cx+foot.r-3}" y2="${baseY-4}" stroke="${GLASSD}" stroke-width="1" opacity="0.4"/>`;
      }
    }
    // saucer for ceramic cups: an arc tucked under the foot, not a floating disc
    if(saucer){g+=`<path d="M${cx-foot.r-9} ${baseY+5} Q${cx} ${baseY+11} ${cx+foot.r+9} ${baseY+5}" fill="none" stroke="${GLASSD}" stroke-width="1.6" opacity="0.7"/>`;}

    // name — anchored a fixed distance below the shared base so all labels align
    g+=`<text x="${cx}" y="${baseY+30}" fill="#f0e6d8" font-size="12.5" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${name}</text>`;
  });
  // legend row, centered as a group under the drinks
  const lg=[['espresso',ESP],['steamed milk',MILK],['foam',FOAM]];
  let lx=232;
  lg.forEach(it=>{g+=`<rect x="${lx}" y="222" width="12" height="12" rx="2" fill="${it[1]}" stroke="${GLASSD}" stroke-width="0.5"/>`;
    g+=`<text x="${lx+17}" y="232" fill="${DIA.ink3}" font-size="11" font-family="ui-sans-serif">${it[0]}</text>`;
    lx+=it[0].length*6.6+34;});
  return diaWrap(`${W} ${H}`,g,'The same espresso shot, in the real glassware for each drink \u2014 milk and foam in different proportions.');
}// 25. Decaf methods.
function diaDecaf(){
  const W=760,H=200;
  const methods=[['Solvent','#B07B3E','MC or EA','EA = \u201csugarcane\u201d, sweet',150],['Swiss Water','#6a8fb0','water + carbon','chemical-free, ~99.9%',380],['CO2','#7a9a6a','supercritical CO2','commercial scale',610]];
  let g=diaDefs(methods.map(m=>m[1]));
  methods.forEach(m=>{const cx=m[4],cy=70;
    g+=`<circle cx="${cx}" cy="${cy}" r="36" fill="url(#${_cid(m[1])})" stroke="${m[1]}" stroke-width="2" filter="url(#dsoft)" opacity="0.9"/>`;
    // a real green bean losing caffeine (dots escaping outward)
    g+=diaBean(cx,cy,0.85,'#66805c','green',null);
    for(let k=0;k<4;k++){const a=k/4*6.28+0.4;g+=`<circle cx="${(cx+Math.cos(a)*30).toFixed(0)}" cy="${(cy+Math.sin(a)*30).toFixed(0)}" r="2.5" fill="${m[1]}" opacity="0.7"/>`;}
    g+=`<text x="${cx}" y="${cy+58}" fill="${m[1]}" font-size="14" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${m[0]}</text>`;
    g+=`<text x="${cx}" y="${cy+76}" fill="#f0e6d8" font-size="11.5" text-anchor="middle" font-family="ui-sans-serif">${m[2]}</text>`;
    g+=`<text x="${cx}" y="${cy+92}" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">${m[3]}</text>`;
  });
  g+=`<text x="380" y="${H-6}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">All done to green beans before roasting \u00b7 all target ~97\u201399.9% caffeine removal</text>`;
  return diaWrap(`${W} ${H}`,g,'Three ways to pull caffeine out of green coffee.');
}
// 26. Coffee's spread map (schematic).
function diaCoffeeMap(){
  const W=760,H=230;
  // Ordered spread of coffee out of Ethiopia. Positions roughly geographic (left=Africa/Arabia,
  // up=Europe, right=Asia, lower-mid=Americas) and NUMBERED so the sequence is unmistakable.
  const stops=[
    ['1','Ethiopia','origin \u00b7 wild Arabica','#5f8f4a',110,120],
    ['2','Yemen','15th c. \u00b7 first cultivation','#C9A34E',225,150],
    ['3','Europe','17th c. \u00b7 coffeehouses','#B07B3E',360,64],
    ['4','Java','1690s \u00b7 Dutch colony','#8A5A34',620,120],
    ['5','Americas','1700s \u00b7 French/colonial','#a0522d',470,175],
  ];
  let g=diaDefs(stops.map(s=>s[3]));
  g=`<defs>${diaArrowMarker('#b09876')}</defs>`+g;
  g+=`<rect x="0" y="0" width="${W}" height="${H}" fill="#12100c" rx="10"/>`;
  // faint landmass hints so it reads as a world map, not floating dots
  g+=`<g opacity="0.10" fill="#c9b8a4">
    <ellipse cx="150" cy="150" rx="95" ry="60"/>            <!-- Africa/Arabia blob -->
    <ellipse cx="360" cy="70" rx="120" ry="34"/>            <!-- Europe strip -->
    <ellipse cx="630" cy="130" rx="110" ry="52"/>           <!-- Asia blob -->
    <ellipse cx="470" cy="185" rx="80" ry="34"/>            <!-- Americas blob -->
  </g>`;
  // ordered dashed arrows following the numbered sequence
  for(let i=0;i<stops.length-1;i++){const a=stops[i],b=stops[i+1];
    const mx=(a[4]+b[4])/2, my=Math.min(a[5],b[5])-28;
    // back the arrow off both dots: start at edge of A, end ~20px short of B's center (r15 + head)
    const angEnd=Math.atan2(b[5]-my, b[4]-mx);
    const ex=b[4]-Math.cos(angEnd)*20, ey=b[5]-Math.sin(angEnd)*20;
    const angStart=Math.atan2(my-a[5], mx-a[4]);
    const sx=a[4]+Math.cos(angStart)*17, sy=a[5]+Math.sin(angStart)*17;
    g+=`<path d="M${sx.toFixed(1)} ${sy.toFixed(1)} Q${mx} ${my} ${ex.toFixed(1)} ${ey.toFixed(1)}" stroke="#b09876" stroke-width="1.8" fill="none" stroke-dasharray="5 4" marker-end="url(#darr)" opacity="0.85"/>`;
  }
  stops.forEach(s=>{
    g+=`<circle cx="${s[4]}" cy="${s[5]}" r="15" fill="url(#${_cid(s[3])})" stroke="${s[3]}" stroke-width="2"/>`;
    g+=`<text x="${s[4]}" y="${s[5]+4}" fill="#f5ecdd" font-size="12" font-weight="800" text-anchor="middle" font-family="ui-sans-serif">${s[0]}</text>`;
    g+=`<text x="${s[4]}" y="${s[5]-22}" fill="#f0e6d8" font-size="12.5" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${s[1]}</text>`;
    g+=`<text x="${s[4]}" y="${s[5]+30}" fill="${DIA.ink3}" font-size="9.5" text-anchor="middle" font-family="ui-sans-serif">${s[2]}</text>`;
  });
  return diaWrap(`${W} ${H}`,g,'Coffee\u2019s journey out of Ethiopia, in order (1\u21925) \u2014 climate plus colonial trade drew today\u2019s map.');
}// 27. Caffeine content comparison.
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
  const W=760,H=234;
  let g=diaDefs(['#8A5A34','#c86a9a']);
  const cyc=98, rc=70;
  // tongue side
  g+=`<circle cx="200" cy="${cyc}" r="${rc}" fill="url(#${_cid('#8A5A34')})" stroke="#8A5A34" stroke-width="2" filter="url(#dsoft)"/>`;
  g+=`<text x="200" y="${cyc-42}" fill="#f0e6d8" font-size="15" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">TONGUE</text>`;
  g+=`<text x="200" y="${cyc-25}" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">tastes structure</text>`;
  ['sweet','sour','bitter','salty','umami'].forEach((t,i)=>{g+=`<text x="200" y="${cyc-8+i*14}" fill="#f0e6d8" font-size="11.5" text-anchor="middle" font-family="ui-sans-serif">${t}</text>`;});
  // nose side
  g+=`<circle cx="560" cy="${cyc}" r="${rc}" fill="url(#${_cid('#c86a9a')})" stroke="#c86a9a" stroke-width="2" filter="url(#dsoft)"/>`;
  g+=`<text x="560" y="${cyc-42}" fill="#f0e6d8" font-size="15" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">NOSE</text>`;
  g+=`<text x="560" y="${cyc-25}" fill="${DIA.ink3}" font-size="10" text-anchor="middle" font-family="ui-sans-serif">smells flavor (retronasal)</text>`;
  ['berry \u00b7 citrus','floral \u00b7 jasmine','chocolate \u00b7 nut','spice \u00b7 caramel'].forEach((t,i)=>{g+=`<text x="560" y="${cyc-3+i*15}" fill="#f0e6d8" font-size="11" text-anchor="middle" font-family="ui-sans-serif">${t}</text>`;});
  // bridge
  g+=`<path d="M272 ${cyc} Q380 44 488 ${cyc}" stroke="#C9A34E" stroke-width="2" fill="none" stroke-dasharray="5 4"/>`;
  g+=`<text x="380" y="52" fill="#C9A34E" font-size="12" font-weight="600" text-anchor="middle" font-family="ui-sans-serif">slurp = both at once</text>`;
  g+=`<text x="${W/2}" y="212" fill="#f0e6d8" font-size="13" text-anchor="middle" font-family="ui-sans-serif">\u201cFlavor\u201d is mostly smell \u2014 which is why coffee tastes flat when you\u2019re congested.</text>`;
  return diaWrap(`${W} ${H}`,g,'What the tongue detects vs what the nose does \u2014 the core of tasting.');
}
// 30. Latte art: sink then surface.
function diaLatteArt(){
  const W=760,H=210;
  const steps=[['1 \u00b7 Sink','pitcher HIGH, thin center stream','#8A5A34',150,'high'],['2 \u00b7 Surface','pitcher CLOSE, more flow','#C9A34E',380,'low'],['3 \u00b7 Draw &amp; cut','move to pattern, cut through','#c9a878',610,'draw']];
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
  g+=`<text x="285" y="72" fill="#B07B3E" font-size="12.5" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">Hardness (Mg/Ca)</text><text x="285" y="88" fill="${DIA.ink3}" font-size="10" text-anchor="middle" font-family="ui-sans-serif">extracts flavor &amp; body</text>`;
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
  const W=760,H=220;
  const steps=[['Dose','into dry basket'],['WDT','stir out clumps'],['Level','flatten the bed'],['Tamp','straight &amp; level']];
  const gap=(W-40)/steps.length;
  let g=diaDefs(['#B07B3E']);
  const bkt='#8a7862';
  steps.forEach((s,i)=>{const cx=20+gap*i+gap/2,cy=76;
    // portafilter basket: straight-walled cup with a rim + perforated bottom
    g+=`<path d="M${cx-28} ${cy-26} L${cx+28} ${cy-26} L${cx+24} ${cy+18} L${cx-24} ${cy+18} Z" fill="${_rgba(bkt,0.14)}" stroke="${bkt}" stroke-width="2.2"/>`;
    g+=`<line x1="${cx-30}" y1="${cy-26}" x2="${cx+30}" y2="${cy-26}" stroke="${bkt}" stroke-width="2.4"/>`; // rim
    // perforated bottom dots
    for(let k=0;k<5;k++)g+=`<circle cx="${cx-16+k*8}" cy="${cy+16}" r="1" fill="${bkt}" opacity="0.7"/>`;
    if(i===0){ // Dose: loose mounded grounds
      for(let k=0;k<11;k++)g+=`<circle cx="${cx-18+(k%4)*12}" cy="${cy-12+Math.floor(k/4)*9}" r="2.6" fill="#6a4326"/>`;
    }
    if(i===1){ // WDT: a handle with fine needles raking loose grounds
      g+=`<rect x="${cx-10}" y="${cy-44}" width="20" height="9" rx="3" fill="#3a332c" stroke="${bkt}" stroke-width="1"/>`; // handle
      for(let k=0;k<7;k++)g+=`<line x1="${cx-9+k*3}" y1="${cy-35}" x2="${cx-9+k*3}" y2="${cy+6}" stroke="#c9b8a4" stroke-width="0.8" opacity="0.85"/>`; // needles
      for(let k=0;k<8;k++)g+=`<circle cx="${cx-18+(k%4)*12}" cy="${cy-4+Math.floor(k/4)*9}" r="2.4" fill="#6a4326" opacity="0.85"/>`;
    }
    if(i===2){ // Level: a flat, even bed
      g+=`<rect x="${cx-23}" y="${cy-8}" width="46" height="24" fill="#5a3a1e" opacity="0.75"/>`;
      g+=`<line x1="${cx-23}" y1="${cy-8}" x2="${cx+23}" y2="${cy-8}" stroke="#8a6a44" stroke-width="1.5"/>`;
    }
    if(i===3){ // Tamp: a cylindrical tamper pressing a compressed puck
      g+=`<rect x="${cx-23}" y="${cy-2}" width="46" height="20" fill="#4a2f18" opacity="0.85"/>`; // compressed puck
      g+=`<rect x="${cx-22}" y="${cy-10}" width="44" height="9" rx="2" fill="#c9a878" stroke="#a0824a" stroke-width="1"/>`; // tamper base
      g+=`<rect x="${cx-7}" y="${cy-32}" width="14" height="24" rx="4" fill="#b8945e" stroke="#a0824a" stroke-width="1"/>`; // tamper handle
      g+=`<path d="M${cx} ${cy-40} L${cx} ${cy-34}" stroke="#B07B3E" stroke-width="2.4" marker-end="url(#darr)"/>`; // press arrow
    }
    // step badge + labels
    g+=`<circle cx="${cx}" cy="${cy+44}" r="12" fill="url(#${_cid('#B07B3E')})" stroke="#B07B3E" stroke-width="1.5" filter="url(#dsoft)"/><text x="${cx}" y="${cy+48}" fill="#e6c88a" font-size="12" font-weight="700" text-anchor="middle" font-family="ui-monospace">${i+1}</text>`;
    g+=`<text x="${cx}" y="${cy+72}" fill="#f0e6d8" font-size="13" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${s[0]}</text>`;
    g+=`<text x="${cx}" y="${cy+88}" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">${s[1]}</text>`;
  });
  g=`<defs>${diaArrowMarker('#B07B3E')}</defs>`+g;
  g+=`<text x="${W/2}" y="${H-6}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">All to make one uniform bed \u2014 so water can\u2019t channel through weak spots.</text>`;
  return diaWrap(`${W} ${H}`,g,'The puck-prep sequence, each step fighting channeling.');
}// 34. Freshness curve over time.
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
  g+=`<text x="${baseX}" y="26" fill="#8f7c66" font-size="11" font-family="ui-monospace">FLAVOR &amp; PERCEIVED BRIGHTNESS</text>`;
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
    // steaming pitcher: tapered body (wider at top), a proper triangular spout, a handle
    g+=`<path d="M${cx-32} ${cy-40} L${cx+28} ${cy-40} L${cx+22} ${cy+36} L${cx-26} ${cy+36} Z" fill="#14120d" stroke="#8a7a62" stroke-width="2" filter="url(#dsoft)"/>`;
    g+=`<path d="M${cx+28} ${cy-40} L${cx+50} ${cy-30} L${cx+40} ${cy-16} L${cx+24} ${cy-24} Z" fill="#14120d" stroke="#8a7a62" stroke-width="2"/>`; // spout
    g+=`<path d="M${cx-32} ${cy-40} q-14 4 -10 22 q3 12 12 14" fill="none" stroke="#8a7a62" stroke-width="2.4"/>`; // handle (left)
    // milk fill
    g+=`<path d="M${cx-29} ${cy-8} L${cx+24} ${cy-8} L${cx+20} ${cy+32} L${cx-24} ${cy+32} Z" fill="url(#${_cid('#e8dcc8')})" opacity="0.95"/>`;
    if(p[5]==='air'){
      // surface breaking, folding air in — a raised foam ridge + bubbles + a "tsss" wand near top
      g+=`<ellipse cx="${cx-2}" cy="${cy-8}" rx="25" ry="6" fill="#f6efe1"/>`;
      [[-16,-4,2.2],[-6,-1,2.6],[4,-3,2],[12,0,2.4],[-2,3,1.8]].forEach(b=>{g+=`<circle cx="${cx+b[0]}" cy="${cy+b[1]}" r="${b[2]}" fill="#fff" opacity="0.75"/>`;});
      g+=`<line x1="${cx+2}" y1="${cy-54}" x2="${cx+2}" y2="${cy-12}" stroke="#b7a488" stroke-width="3"/>`; // steam wand, tip near surface
      g+=`<circle cx="${cx+2}" cy="${cy-11}" r="2.4" fill="#b7a488"/>`;
      // little "tsss" air ticks
      g+=`<path d="M${cx-8} ${cy-16} q-3 -3 0 -6 M${cx+12} ${cy-16} q3 -3 0 -6" fill="none" stroke="#e8dcc8" stroke-width="1.2" opacity="0.7"/>`;
    }
    if(p[5]==='spin'){
      // wand plunged deep, whirlpool spinning the milk — a clear circular arrow
      g+=`<line x1="${cx-3}" y1="${cy-52}" x2="${cx-3}" y2="${cy+6}" stroke="#b7a488" stroke-width="3"/>`; // wand submerged
      g+=`<circle cx="${cx-3}" cy="${cy+7}" r="2.4" fill="#b7a488"/>`;
      // whirlpool: a spiral of two arcs converging, with a flow arrowhead
      g+=`<path d="M${cx-17} ${cy+10} A17 9 0 1 1 ${cx+16} ${cy+8}" fill="none" stroke="#fff" stroke-width="1.8" opacity="0.8" marker-end="url(#ams)"/>`;
      g+=`<path d="M${cx-10} ${cy+14} A10 5 0 1 0 ${cx+9} ${cy+13}" fill="none" stroke="#fff" stroke-width="1.3" opacity="0.55"/>`;
    }
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
    ['DAILY','#C9A34E',['Wipe &amp; purge steam wand','Water backflush','Rinse portafilter/basket']],
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
  const W=760,H=262,cx=175,cy=125;
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
  const W=760,H=264;
  let g=diaDefs(['#5a8a9a','#C9A34E','#8fbf3a','#c86a4a']);
  g=`<defs>${diaArrowMarker('#9a8468')}</defs>`+g;
  const node=(x,y,w,h,color,label,sub,big)=>{
    let s=`<g filter="url(#dsoft)"><rect x="${x}" y="${y}" width="${w}" height="${h}" rx="9" fill="#241a12" stroke="${color}" stroke-width="1.4"/>`;
    s+=`<rect x="${x}" y="${y}" width="${w}" height="4" rx="2" fill="${color}"/>`;
    s+=`<rect x="${x}" y="${y+2}" width="${w}" height="${h-2}" rx="8" fill="url(#${_cid(color)})"/>`;
    s+=`<text x="${x+w/2}" y="${y+(sub?h/2:h/2+4)}" fill="#f5ecdd" font-size="${big?13:12}" font-weight="${big?800:650}" text-anchor="middle" font-family="ui-sans-serif">${label}</text>`;
    if(sub)s+=`<text x="${x+w/2}" y="${y+h/2+14}" fill="#a2907a" font-size="9" text-anchor="middle" font-family="ui-sans-serif">${sub}</text>`;
    s+=`</g>`;return s;
  };
  const curve=(x1,y1,x2,y2,c)=>{const mx=(x1+x2)/2;return `<path d="M${x1} ${y1} C ${mx} ${y1} ${mx} ${y2} ${x2} ${y2}" fill="none" stroke="${c}" stroke-width="1.5" opacity="0.5"/>`;};
  // ---- col 1: Intro (start) ----
  g+=node(20,105,116,54,'#5a8a9a','Intro to Coffee','start here',true);
  // ---- col 2: 5 modules, curved connectors from Intro ----
  const mods=['Barista','Brewing','Green Coffee','Roasting','Sensory'];
  const mx=190, mw=150;
  mods.forEach((m,i)=>{const y=18+i*46;
    g+=curve(136,132,mx,y+16,'#5a8a9a');
    g+=node(mx,y,mw,32,'#5a8a9a',m,null,false);
  });
  // ---- col 3: "each at 3 levels" pill stack ----
  g+=`<text x="428" y="16" fill="${DIA.ink3}" font-size="10" text-anchor="middle" font-family="ui-monospace" letter-spacing="1">EACH AT 3 LEVELS</text>`;
  ['Foundation','Intermediate','Professional'].forEach((lv,i)=>{const yy=30+i*44;
    g+=node(378,yy,100,32,'#C9A34E',lv,null,false);
  });
  // arrow from the modules block into the levels stack (aim at the stack's vertical middle)
  g+=`<path d="M${mx+mw+2} 100 L374 100" stroke="#9a8468" stroke-width="1.6" marker-end="url(#darr)" opacity="0.75"/>`;
  // a collecting bracket on the right of the 3 levels, then two clean fan-out arrows to the credentials
  const lvTop=46, lvBot=134, lvMid=(lvTop+lvBot)/2; // vertical CENTERS of the three pills (46, 90, 134)
  g+=`<path d="M482 ${lvTop} L498 ${lvTop} L498 ${lvBot} L482 ${lvBot}" fill="none" stroke="#9a8468" stroke-width="1.4" opacity="0.55"/>`;
  g+=`<path d="M498 ${lvMid} L508 ${lvMid}" stroke="#9a8468" stroke-width="1.4" opacity="0.55"/>`;
  g+=`<path d="M508 ${lvMid} C 516 ${lvMid} 516 89 524 89" fill="none" stroke="#9a8468" stroke-width="1.6" marker-end="url(#darr)" opacity="0.75"/>`;
  g+=`<path d="M508 ${lvMid} C 516 ${lvMid} 516 159 524 159" fill="none" stroke="#9a8468" stroke-width="1.6" marker-end="url(#darr)" opacity="0.75"/>`;
  // ---- col 4: the two credentials ----
  g+=node(526,62,214,54,'#8fbf3a','SCA Skills Diploma','earn points across modules',true);
  g+=node(526,132,214,54,'#c86a4a','Q Grader (CQI)','coffee\u2019s \u2018sommelier\u2019 license',true);
  g+=`<text x="${W/2}" y="${H-8}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">Modular &amp; flexible \u2014 start anywhere, build toward job-ready diplomas or the Q license.</text>`;
  return diaWrap(`${W} ${H}`,g,'The main coffee certification pathways.');
}// 41. Coffee cherry anatomy -> byproducts.
function diaCherryByproduct(){
  const W=760,H=230,cx=150,cy=104;
  let g=diaDefs(['#c0433a']);
  g=`<defs>${diaArrowMarker('#8a7660')}
    <radialGradient id="cbySkin" cx="0.4" cy="0.32" r="0.8"><stop offset="0" stop-color="#e05a48"/><stop offset="1" stop-color="#9a2e22"/></radialGradient>
    <radialGradient id="cbyPulp" cx="0.42" cy="0.36" r="0.8"><stop offset="0" stop-color="#efaa5a"/><stop offset="1" stop-color="#b0692a"/></radialGradient>
    <radialGradient id="cbyBean" cx="0.4" cy="0.34" r="0.78"><stop offset="0" stop-color="#a6bb7c"/><stop offset="1" stop-color="#7a5a38"/></radialGradient></defs>`+g;
  // realistic cherry cross-section: skin -> pulp -> two beans w/ groove -> silverskin
  g+=`<ellipse cx="${cx}" cy="${cy+4}" rx="50" ry="54" fill="#000" opacity="0.28" filter="url(#dsoft)"/>`;
  g+=`<ellipse cx="${cx}" cy="${cy}" rx="50" ry="54" fill="url(#cbySkin)"/>`;
  g+=`<ellipse cx="${cx}" cy="${cy}" rx="40" ry="44" fill="url(#cbyPulp)"/>`;
  // two beans nestled with groove
  const bn=(sgn)=>`<path d="M${cx} ${cy-30} C${cx+sgn*3} ${cy-32} ${cx+sgn*27} ${cy-26} ${cx+sgn*27} ${cy} C${cx+sgn*27} ${cy+26} ${cx+sgn*3} ${cy+32} ${cx} ${cy+30} Z" fill="url(#cbyBean)" stroke="#5a4632" stroke-width="1.1"/>`;
  g+=bn(1)+bn(-1);
  g+=`<path d="M${cx} ${cy-29} Q${cx-2} ${cy} ${cx} ${cy+29}" stroke="#4a3826" stroke-width="1.3" fill="none" opacity="0.8"/>`;
  g+=`<ellipse cx="${cx}" cy="${cy}" rx="29" ry="33" fill="none" stroke="#efe6d2" stroke-width="0.9" opacity="0.45"/>`;
  g+=`<ellipse cx="${cx-16}" cy="${cy-20}" rx="13" ry="10" fill="#fff" opacity="0.12"/>`;
  g+=`<path d="M${cx} ${cy-54} q-3 -7 2 -12" stroke="#5a2a1a" stroke-width="3" fill="none" stroke-linecap="round"/>`; // stem
  // external labels with leader lines (never on the fruit)
  g+=`<line x1="${cx-46}" y1="${cy-28}" x2="${cx-70}" y2="${cy-40}" stroke="#8a7660" stroke-width="0.8" opacity="0.5"/>`;
  g+=`<text x="${cx-72}" y="${cy-42}" fill="#c9b8a4" font-size="9.5" text-anchor="end" font-family="ui-sans-serif">skin</text>`;
  g+=`<line x1="${cx-38}" y1="${cy+2}" x2="${cx-70}" y2="${cy+10}" stroke="#8a7660" stroke-width="0.8" opacity="0.5"/>`;
  g+=`<text x="${cx-72}" y="${cy+13}" fill="#c9b8a4" font-size="9.5" text-anchor="end" font-family="ui-sans-serif">pulp</text>`;
  g+=`<line x1="${cx+20}" y1="${cy+30}" x2="${cx+66}" y2="${cy+46}" stroke="#8a7660" stroke-width="0.8" opacity="0.5"/>`;
  g+=`<text x="${cx+68}" y="${cy+49}" fill="#c9b8a4" font-size="9.5" text-anchor="start" font-family="ui-sans-serif">beans (seeds)</text>`;
  // caption
  g+=`<text x="${cx}" y="${cy+80}" fill="#f0e6d8" font-size="13" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">The coffee cherry</text>`;
  g+=`<text x="${cx}" y="${cy+96}" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">a fruit: seeds (beans) inside sweet pulp</text>`;
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
  const cols=[['COFFEE','#6E3E1E',180,['Roasted SEED of Coffea fruit','~95 mg caffeine / cup','Bolder, heavier, immediate','Morning and productivity']],
              ['TEA','#7a9a6a',560,['Dried LEAF of Camellia sinensis','~30\u201350 mg caffeine / cup','Lighter, L-theanine = steady','All-day and calm']]];
  let g=diaDefs(['#6E3E1E','#7a9a6a']);
  cols.forEach(c=>{const cx=c[2];
    // icon circle (no text inside — the title sits below so it never overflows)
    g+=`<circle cx="${cx}" cy="40" r="20" fill="url(#${_cid(c[1])})" stroke="${c[1]}" stroke-width="2" filter="url(#dsh)"/>`;
    g+=`<circle cx="${cx}" cy="40" r="20" fill="none" stroke="${_rgba(c[1],0.4)}" stroke-width="5"/>`;
    g+=`<text x="${cx}" y="82" fill="#f0e6d8" font-size="16" font-weight="800" text-anchor="middle" font-family="ui-sans-serif" letter-spacing="1.5">${c[0]}</text>`;
    c[3].forEach((t,i)=>{const y=108+i*29;
      g+=`<text x="${cx}" y="${y}" fill="#c9b8a4" font-size="12" text-anchor="middle" font-family="ui-sans-serif">${t}</text>`;
    });
  });
  // vs divider — centered at the true midpoint of the two columns
  const midX=(180+560)/2;
  g+=`<line x1="${midX}" y1="26" x2="${midX}" y2="200" stroke="${DIA.line}" stroke-dasharray="5 5"/>`;
  g+=`<circle cx="${midX}" cy="40" r="16" fill="#160e08" stroke="${DIA.ink3}" stroke-width="1.2" filter="url(#dsoft)"/>`;
  g+=`<text x="${midX}" y="45" fill="${DIA.ink3}" font-size="12" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">vs</text>`;
  g+=`<text x="${W/2}" y="${H-8}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">Parallel crafts \u2014 both obsess over terroir, processing, ritual, and brewing precision. Complements, not competitors.</text>`;
  return diaWrap(`${W} ${H}`,g,'The world\u2019s two great caffeinated drinks, compared.');
}
// 43. Espresso machine boiler configurations.
function diaMachTypes(){
  const W=760,H=250;
  const cols=[
    ['Single boiler','#8A5A34',130,'one boiler:\nbrew OR steam','switch and wait'],
    ['Heat exchanger','#B07B3E',380,'steam boiler +\nbrew pipe through it','flush to cool'],
    ['Dual boiler','#C9A34E',630,'two boilers:\nbrew + steam','direct, no wait'],
  ];
  let g=diaDefs(['#8A5A34','#B07B3E','#C9A34E','#5a8a9a','#c0433a']);
  g=`<defs>${diaArrowMarker('#8a7660')}
    <marker id="mtCold" markerWidth="8" markerHeight="8" refX="5" refY="3" orient="auto"><path d="M0 0 L5 3 L0 6 z" fill="#6a9fc8"/></marker>
    <marker id="mtHot" markerWidth="8" markerHeight="8" refX="5" refY="3" orient="auto"><path d="M0 0 L5 3 L0 6 z" fill="#d0553a"/></marker>
    <linearGradient id="mtShell" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8a8278"/><stop offset="0.5" stop-color="#c2bAac"/><stop offset="1" stop-color="#6a6258"/></linearGradient>
    <linearGradient id="mtWater" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a6a8a"/><stop offset="1" stop-color="#274a63"/></linearGradient>
    <linearGradient id="mtHotB" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c07a5a"/><stop offset="1" stop-color="#7a3e2a"/></linearGradient></defs>`+g;
  // a cutaway boiler: metal shell (rounded rect), a water fill in the lower portion, steam above.
  // opt: {steamTop:true} shades the upper space as steam.
  const boilerCut=(cx,cy,w,h,waterFrac,waterFill,col)=>{
    const x=cx-w/2, y=cy-h/2, rr=h*0.32;
    let s=`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${rr}" fill="url(#mtShell)" stroke="${col}" stroke-width="1.8"/>`;
    // clip the water region to the rounded shell
    const cid='bc'+Math.round(cx)+Math.round(cy);
    s+=`<clipPath id="${cid}"><rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${rr}"/></clipPath>`;
    const wy=y+h*(1-waterFrac);
    s+=`<g clip-path="url(#${cid})">`;
    s+=`<rect x="${x}" y="${y}" width="${w}" height="${h*(1-waterFrac)}" fill="#efe8dc" opacity="0.10"/>`; // steam space
    s+=`<rect x="${x}" y="${wy}" width="${w}" height="${h*waterFrac}" fill="${waterFill}"/>`;
    s+=`<line x1="${x}" y1="${wy}" x2="${x+w}" y2="${wy}" stroke="#dfeaf2" stroke-width="1" opacity="0.55"/>`; // water line
    // tiny steam bubbles rising in the top space
    if(waterFrac<0.95){[[cx-w*0.18,y+h*0.16],[cx+w*0.10,y+h*0.22],[cx+w*0.24,y+h*0.13]].forEach(p=>{s+=`<circle cx="${p[0]}" cy="${p[1]}" r="1.4" fill="#fff" opacity="0.4"/>`;});}
    s+=`</g>`;
    return s;
  };
  // a brew group head (portafilter) below a point
  const group=(cx,cy)=>`<path d="M${cx-9} ${cy} L${cx+9} ${cy} L${cx+6} ${cy+9} L${cx-6} ${cy+9} Z" fill="#3a332c" stroke="#8a7c66" stroke-width="1.2"/><rect x="${cx-11} " y="${cy-4}" width="22" height="5" rx="2" fill="#8a7c66"/>`;
  const wand=(cx,cy)=>`<line x1="${cx}" y1="${cy}" x2="${cx+7}" y2="${cy+16}" stroke="#8a7c66" stroke-width="2"/><circle cx="${cx+8}" cy="${cy+18}" r="3" fill="none" stroke="#8a7c66" stroke-width="1.5"/>`;
  cols.forEach((c,i)=>{const cx=c[2],cy=80,col=c[1];
    g+=`<text x="${cx}" y="34" fill="${col}" font-size="14" font-weight="800" text-anchor="middle" font-family="ui-sans-serif">${c[0]}</text>`;
    if(i===0){
      // ONE boiler, full of hot water — feeds either the group OR the wand (switch & wait)
      g+=boilerCut(cx,cy,92,40,0.72,'url(#mtHotB)',col);
      g+=`<text x="${cx}" y="${cy+3}" fill="#f4ece0" font-size="8.5" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">one boiler</text>`;
      g+=`<line x1="${cx-22}" y1="${cy+20}" x2="${cx-22}" y2="${cy+32}" stroke="#8a7c66" stroke-width="2"/>`; g+=group(cx-22,cy+32);
      g+=wand(cx+24,cy+20);
      g+=`<text x="${cx-22}" y="${cy+54}" fill="${DIA.ink3}" font-size="8" text-anchor="middle" font-family="ui-sans-serif">brew</text>`;
      g+=`<text x="${cx+30}" y="${cy+54}" fill="${DIA.ink3}" font-size="8" text-anchor="middle" font-family="ui-sans-serif">steam</text>`;
    }
    if(i===1){
      // ONE boiler (water below, steam above). A BREW PIPE (HX) traverses the water:
      // cold water enters the bottom, absorbs heat rising through, exits the top to the group.
      g+=boilerCut(cx,cy,100,44,0.66,'url(#mtWater)',col);
      g+=`<text x="${cx}" y="${cy-9}" fill="#dfeaf2" font-size="8" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">steam</text>`;
      g+=`<text x="${cx}" y="${cy+14}" fill="#dfeaf2" font-size="8" text-anchor="middle" font-family="ui-sans-serif">hot water</text>`;
      // the HX tube: an inverted-U passing DOWN into the water and back UP, drawn over the boiler
      const bx=cx-16, tx=cx+16, topY=cy-30, botY=cy+16;
      g+=`<path d="M${bx} ${cy+40} L${bx} ${botY} C${bx} ${topY} ${tx} ${topY} ${tx} ${botY} L${tx} ${cy+40}" fill="none" stroke="#9a6a4a" stroke-width="4.5" opacity="0.9"/>`;
      g+=`<path d="M${bx} ${cy+40} L${bx} ${botY} C${bx} ${topY} ${tx} ${topY} ${tx} ${botY} L${tx} ${cy+40}" fill="none" stroke="#c89a6a" stroke-width="1.6" opacity="0.7"/>`;
      // cold in (left, bottom) -> hot out (right, to group)
      g+=`<path d="M${bx} ${cy+48} L${bx} ${cy+41}" stroke="#6a9fc8" stroke-width="2.4" marker-end="url(#mtCold)"/>`;
      g+=`<text x="${bx-2}" y="${cy+58}" fill="#7fb0d8" font-size="7.5" text-anchor="middle" font-family="ui-sans-serif">cold in</text>`;
      g+=`<line x1="${tx}" y1="${cy+41}" x2="${tx}" y2="${cy+30}" stroke="#d0553a" stroke-width="2.4"/>`; g+=group(tx,cy+30);
      g+=`<text x="${tx+2}" y="${cy+58}" fill="#d68a5a" font-size="7.5" text-anchor="middle" font-family="ui-sans-serif">hot → group</text>`;
      // steam wand off the very top
      g+=wand(cx+46,cy-14);
    }
    if(i===2){
      // TWO separate boilers — a dedicated brew boiler and a dedicated steam boiler
      g+=boilerCut(cx-26,cy,46,36,0.82,'url(#mtHotB)',col);
      g+=`<text x="${cx-26}" y="${cy+3}" fill="#f4ece0" font-size="7.5" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">brew</text>`;
      g+=boilerCut(cx+26,cy,46,36,0.62,'url(#mtWater)','#c0433a');
      g+=`<text x="${cx+26}" y="${cy+3}" fill="#dfeaf2" font-size="7.5" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">steam</text>`;
      g+=`<line x1="${cx-26}" y1="${cy+18}" x2="${cx-26}" y2="${cy+32}" stroke="#8a7c66" stroke-width="2"/>`; g+=group(cx-26,cy+32);
      g+=wand(cx+24,cy+18);
      g+=`<text x="${cx-26}" y="${cy+54}" fill="${DIA.ink3}" font-size="8" text-anchor="middle" font-family="ui-sans-serif">brew</text>`;
      g+=`<text x="${cx+30}" y="${cy+54}" fill="${DIA.ink3}" font-size="8" text-anchor="middle" font-family="ui-sans-serif">steam</text>`;
    }
    c[3].split('\n').forEach((ln,j)=>{g+=`<text x="${cx}" y="${152+j*15}" fill="#c9b8a4" font-size="11.5" text-anchor="middle" font-family="ui-sans-serif">${ln}</text>`;});
    g+=`<text x="${cx}" y="${194}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">${c[4]}</text>`;
  });
  g+=`<line x1="255" y1="55" x2="255" y2="200" stroke="${DIA.line}" stroke-dasharray="4 5"/>`;
  g+=`<line x1="505" y1="55" x2="505" y2="200" stroke="${DIA.line}" stroke-dasharray="4 5"/>`;
  g+=`<text x="${W/2}" y="${H-8}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">All pump-driven at ~9 bars. Adding a PID sets brew temp precisely \u2014 the biggest consistency gain.</text>`;
  return diaWrap(`${W} ${H}`,g,'The three boiler configurations, simplest to most capable.');
}// 44. Water chemistry: GH/KH balance + SCA target.
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
  g+=`<text x="${W/2}" y="${H-8}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">Brewed coffee is ~98% water. Balance extracts flavor &amp; buffers acidity \u2014 but KH is also what forms scale.</text>`;
  return diaWrap(`${W} ${H}`,g,'The two hardnesses and the SCA target for brewing water.');
}
// 45. From C price to farmgate: the price waterfall.
function diaCmarket(){
  const W=760,H=270;
  let g=diaDefs(['#c86a6a','#C9A34E','#B07B3E','#8A5A34','#7a9a6a']);
  g=`<defs>${diaArrowMarker('#9a8468')}</defs>`+g;
  // A visual WATERFALL: start high at the C price, step DOWN as margins are taken,
  // land at the farmgate. Each brick's WIDTH shrinks to show the shrinking slice.
  // layout: left axis of descending bricks; labels to the right of each.
  const bx=70, topY=44, brickH=30, stepY=44;
  // running "value" as a fraction of full width -> shows the slice shrinking
  const rows=[
    ['The C price','ICE benchmark \u00b7 Arabica futures','#c86a6a',1.00,'anchor'],
    ['+/\u2212 Differential','country, quality, certs','#C9A34E',0.92,'down'],
    ['= FOB price','at the export port','#B07B3E',0.78,'sum'],
    ['\u2212 exporters, mills, middlemen','each takes a margin','#8A5A34',0.55,'down'],
    ['= Farmgate price','what the farmer actually gets','#7a9a6a',0.42,'anchor'],
  ];
  const fullW=300;
  rows.forEach((r,i)=>{const y=topY+i*stepY, w=fullW*r[3];
    // connector from previous brick's bottom to this brick's top-left
    if(i>0){const py=topY+(i-1)*stepY+brickH;g+=`<path d="M${bx} ${py} L${bx} ${y}" stroke="#9a8468" stroke-width="1.2" opacity="0.5" stroke-dasharray="3 3"/>`;}
    // the brick (waterfall bar)
    g+=diaCard(bx,y,w,brickH,r[2],{r:6,shadow:false,strong:(r[4]==='anchor')});
    g+=`<text x="${bx+12}" y="${y+19}" fill="#f0e6d8" font-size="12" font-weight="${r[4]==='anchor'?800:650}" font-family="ui-sans-serif">${r[0]}</text>`;
    // sub-label to the right of the brick
    g+=`<text x="${bx+w+12}" y="${y+13}" fill="${r[2]}" font-size="10.5" font-weight="700" font-family="ui-sans-serif">${r[4]==='down'?'\u2193 margin taken':(r[4]==='sum'?'subtotal':'')}</text>`;
    g+=`<text x="${bx+w+12}" y="${y+26}" fill="${DIA.ink3}" font-size="9.5" font-family="ui-sans-serif">${r[1]}</text>`;
  });
  // the shrinking-slice bracket on the far left (anchors only)
  g+=`<line x1="${bx-14}" y1="${topY}" x2="${bx-14}" y2="${topY+brickH}" stroke="#c86a6a" stroke-width="2"/>`;
  g+=`<line x1="${bx-14}" y1="${topY+4*stepY}" x2="${bx-14}" y2="${topY+4*stepY+brickH}" stroke="#7a9a6a" stroke-width="2"/>`;
  // volatility callout card (kept, repositioned clear on the right)
  g+=diaCard(590,44,150,58,'#c86a6a',{r:9,shadow:false});
  g+=`<text x="605" y="63" fill="${DIA.ink3}" font-size="10" font-family="ui-sans-serif">2018\u201319: &lt; $1/lb</text>`;
  g+=`<text x="605" y="80" fill="#e08a6a" font-size="13" font-weight="800" font-family="ui-sans-serif">2025: &gt; $4/lb</text>`;
  g+=`<text x="605" y="94" fill="${DIA.ink3}" font-size="9" font-family="ui-sans-serif">(50-yr high)</text>`;
  g+=`<text x="605" y="128" fill="${DIA.ink3}" font-size="10" font-family="ui-sans-serif">Driven by:</text>`;
  g+=`<text x="605" y="144" fill="#c9b8a4" font-size="10" font-family="ui-sans-serif">weather \u00b7 disease</text>`;
  g+=`<text x="605" y="158" fill="#c9b8a4" font-size="10" font-family="ui-sans-serif">harvest cycles</text>`;
  g+=`<text x="605" y="172" fill="#c9b8a4" font-size="10" font-family="ui-sans-serif">speculation</text>`;
  g+=`<text x="${W/2}" y="${H-8}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">The farmer often gets a small, shrinking slice \u2014 which is why specialty leans on differentials &amp; direct trade.</text>`;
  return diaWrap(`${W} ${H}`,g,'How the benchmark price becomes what a farmer is actually paid.');
}// 46. Climate: the squeeze on the bean belt.
function diaClimateCoffee(){
  const W=760,H=250;
  let g=diaDefs(['#c0433a','#7a9a6a']);
  g+=diaHeader(30,18,310,'The threat',null,'#c0433a');
  const threats=[['Warming','out of Arabica\u2019s 18\u201322\u00b0C band'],['Erratic rain','disrupts flowering &amp; harvest'],['Rust &amp; borer','spread to higher altitudes'],['Extreme events','frost, drought \u2192 crop loss']];
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
  const W=940,H=430;
  let g=diaDefs(['#C9A34E','#c86a6a','#B07B3E','#8A5A34','#8fbf3a','#7d9f4a','#c86a9a','#5a8a9a','#c0433a','#d0a850']);
  // lineage colors (a node's family = its accent)
  const TYP='#C9A34E', BOU='#c86a6a', HYB='#c0433a', GSH='#d8b45a', SL='#c07fa8', DIS='#6a9aae';
  // curved elbow connector (vertical parent -> child), color-tinted, soft
  const link=(x1,y1,x2,y2,c)=>{const my=(y1+y2)/2;return `<path d="M${x1} ${y1} C ${x1} ${my} ${x2} ${my} ${x2} ${y2}" fill="none" stroke="${c}" stroke-width="1.6" opacity="0.5"/>`;};
  // a solid node card with a colored top accent bar, title + sub. Depth via gradient + shadow.
  const node=(x,y,w,label,color,sub,big)=>{
    const h=big?42:38;
    let s=`<g filter="url(#dsoft)">`;
    s+=`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="9" fill="#241a12" stroke="${color}" stroke-width="1.4"/>`;
    s+=`<rect x="${x}" y="${y}" width="${w}" height="4" rx="2" fill="${color}"/>`;   // top accent bar
    s+=`<rect x="${x}" y="${y+2}" width="${w}" height="${h-2}" rx="8" fill="url(#${_cid(color)})"/>`;
    s+=`<text x="${x+w/2}" y="${y+(sub?21:24)}" fill="#f5ecdd" font-size="${big?13.5:12.5}" font-weight="${big?800:700}" text-anchor="middle" font-family="ui-sans-serif" letter-spacing="0.2">${label}</text>`;
    if(sub)s+=`<text x="${x+w/2}" y="${y+34}" fill="#a2907a" font-size="9.2" text-anchor="middle" font-family="ui-sans-serif">${sub}</text>`;
    s+=`</g>`;
    return s;
  };
  const cx=w2=>w2; // noop helper
  // ------- ROW 0: root -------
  const rootX=380,rootW=140,rootY=14;
  g+=node(rootX,rootY,rootW,'Yemen stock','#a0763d','the origin population',false);
  // ------- ROW 1: two founders (y=92) -------
  const y1=92;
  g+=link(rootX+rootW/2-40,rootY+38,300,y1,TYP);
  g+=link(rootX+rootW/2+40,rootY+38,620,y1,BOU);
  g+=node(210,y1,180,'TYPICA',TYP,'tall · sweet · clean',true);
  g+=node(560,y1,180,'BOURBON',BOU,'richer · higher-yield',true);
  // ------- ROW 2: mutations (y=176) -------
  const y2=176;
  // Typica branch
  g+=link(260,y1+42,150,y2,TYP); g+=link(320,y1+42,320,y2,TYP);
  g+=node(70,y2,150,'Maragogipe',TYP,'giant bean',false);
  g+=node(245,y2,150,'Mundo Novo','#b98a4a','Bourbon \u00d7 Typica',false);
  // Bourbon branch
  g+=link(600,y1+42,460,y2,BOU); g+=link(650,y1+42,650,y2,BOU); g+=link(700,y1+42,845,y2,SL);
  g+=node(420,y2,150,'Caturra','#9ab648','dwarf · BR ~1937',false);
  g+=node(595,y2,150,'Pacas / V.Sarchi','#8aa356','dwarf mutations',false);
  g+=node(770,y2,150,'SL28 / SL34',SL,'Kenya · blackcurrant',false);
  // ------- ROW 3: crosses (y=260) -------
  const y3=260;
  g+=link(145,y2+38,150,y3,TYP); g+=link(320,y2+38,325,y3,'#b98a4a');
  g+=node(75,y3,150,'Pacamara',TYP,'Pacas \u00d7 Maragogipe',false);
  g+=node(250,y3,150,'Catua\u00ed','#b98a4a','MundoNovo \u00d7 Caturra',false);
  g+=link(495,y2+38,500,y3,'#9ab648'); g+=link(670,y2+38,675,y3,'#8aa356');
  g+=node(425,y3,150,'(rust-prone branch \u2193)',DIS,'needs resistance',false);
  g+=node(600,y3,150,'Sarchimor','#8aa356','V.Sarchi \u00d7 Timor',false);
  g+=node(770,y3,150,'Catimor',DIS,'Caturra \u00d7 Timor',false);
  // ------- ROW 4: Timor hybrid source (y=344) -------
  const y4=344;
  g+=link(500,y3+38,560,y4,HYB); g+=link(675,y3+38,760,y4,HYB); g+=link(650,y3+38,650,y4,HYB);
  g+=node(470,y4,320,'Timor Hybrid \u2014 Arabica \u00d7 Robusta',HYB,'the disease-resistance source \u2192 Catimor and Sarchimor',true);
  // Geisha aside (stands apart, bottom-left)
  g+=node(70,y4,330,'Geisha \u2014 Ethiopian landrace',GSH,'jasmine / bergamot \u00b7 the modern superstar',true);
  g+=`<text x="235" y="${y4+56}" fill="#8a7658" font-size="9.5" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">stands apart from the Typica/Bourbon line</text>`;
  return diaWrap(`${W} ${H}`,g,'How the major Arabica varieties are related \u2014 two founders (Typica, Bourbon) branch into mutations and crosses, with the Timor Hybrid adding Robusta\u2019s disease resistance.');
}// 49. The coffee species map.
function diaSpeciesMap(){
  const W=760,H=250;
  const arab=['ARABICA','Coffea arabica','#8fbf3a',['~60\u201370% of production','high altitude, delicate','~1.2\u20131.5% caffeine','sweet, acidic, complex','THE specialty species']];
  const rob=['ROBUSTA','Coffea canephora','#a0824a',['~30\u201340% of production','hot and low, very hardy','~2.2\u20132.7% caffeine','heavy, bitter, less nuance','instant + espresso blends']];
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
  // green bean in center-left as the shared start (a real bean, not a flat disc)
  g+=`<circle cx="90" cy="120" r="40" fill="url(#${_cid('#7d9f4a')})" opacity="0.14"/>`;
  g+=diaBean(90,116,1.15,'#66805c','green',null);
  g+=`<text x="90" y="162" fill="#f0e6d8" font-size="11" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">green beans</text>`;
  g+=`<text x="90" y="178" fill="${DIA.ink3}" font-size="9" text-anchor="middle" font-family="ui-sans-serif">steam \u2192 extract \u2192 dry</text>`;
  methods.forEach(m=>{const y=m[3];
    g+=`<line x1="130" y1="120" x2="196" y2="${y+17}" stroke="${m[2]}" stroke-width="1.4" opacity="0.55"/>`;
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
  // clean symmetric branch: down from the card center, then split left/right into each method
  g+=`<path d="M380 55 L380 66 C380 72 372 72 366 72 L214 72 C206 72 200 74 200 80" stroke="#8a7660" stroke-width="1.6" fill="none" marker-end="url(#darr)"/>`;
  g+=`<path d="M380 55 L380 66 C380 72 388 72 394 72 L546 72 C554 72 560 74 560 80" stroke="#8a7660" stroke-width="1.6" fill="none" marker-end="url(#darr)"/>`;
  // spray drying
  g+=diaCard(40,80,320,118,'#B07B3E',{r:12});
  g+=`<text x="150" y="102" fill="#f0e6d8" font-size="14" font-weight="800" text-anchor="middle" font-family="ui-sans-serif">SPRAY DRYING</text>`;
  ['Mist into hot-air tower','Water flashes off instantly','\u2192 fine POWDER','Cheaper, high-volume','Heat costs aroma'].forEach((t,i)=>{
    g+=`<text x="150" y="${122+i*15}" fill="#c9b8a4" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">${t}</text>`;});
  // powder icon (right side of card): a small mound of fine dust
  g+=`<path d="M290 176 Q300 150 310 176 Z" fill="#c8a86a" opacity="0.6"/>`;
  [[292,170],[300,164],[308,170],[296,174],[304,173]].forEach(d=>{g+=`<circle cx="${d[0]}" cy="${d[1]}" r="1.1" fill="#e0c48a" opacity="0.8"/>`;});
  g+=`<text x="300" y="190" fill="#a07a3a" font-size="8" text-anchor="middle" font-family="ui-sans-serif">powder</text>`;
  // freeze drying
  g+=diaCard(400,80,320,118,'#5a8a9a',{r:12});
  g+=`<text x="510" y="102" fill="#f0e6d8" font-size="14" font-weight="800" text-anchor="middle" font-family="ui-sans-serif">FREEZE DRYING</text>`;
  ['Freeze to ~-40\u00b0C','Vacuum: ice \u2192 vapor (sublimes)','\u2192 crystalline GRANULES','Premium method','Cold preserves aroma'].forEach((t,i)=>{
    g+=`<text x="510" y="${122+i*15}" fill="#c9b8a4" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">${t}</text>`;});
  // granule icon (right side): a few angular crystals
  [[652,172,5],[662,168,4],[658,176,4.5],[669,174,3.5]].forEach(cr=>{const x=cr[0],y=cr[1],s=cr[2];g+=`<path d="M${x} ${y-s} L${x+s} ${y} L${x} ${y+s} L${x-s} ${y} Z" fill="#7fb0c8" opacity="0.55" stroke="#a8d0e0" stroke-width="0.7"/>`;});
  g+=`<text x="660" y="190" fill="#6a9ab0" font-size="8" text-anchor="middle" font-family="ui-sans-serif">granules</text>`;
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
    if(i<stops.length-1) g+=`<path d="M${x+152} ${y0+24} L${x+183} ${y0+24}" stroke="#8a7660" stroke-width="2" marker-end="url(#darr)"/>`;
  });
  g+=`<text x="30" y="30" fill="${DIA.ink3}" font-size="10.5" font-family="ui-monospace">THE JOURNEY</text>`;
  // flavor + price panels
  g+=diaCard(30,118,345,96,'#d0a850',{r:12,title:'THE FLAVOR',titleSize:12.5});
  ['Jasmine \u00b7 orange blossom \u00b7 bergamot','Peach \u00b7 tropical fruit \u00b7 tea-like body','From linalool + geraniol aromatics','Only at altitude, picked &amp; processed w/ care'].forEach((t,i)=>{
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
  const bean=(cx,cy,s,fill,overlay)=>diaBean(cx,cy,s*1.15,fill,'roast',overlay);
  // grid of 3 cols x 3 rows; each cell: bean + name + one-line cause + cup note
  const cells=[
    ['Healthy','#7a4a24','even color, matte-satin','sweet, balanced',null],
    ['Scorching','#6e3e1e','hot drum, flat-face burns','ashy, smoky',' scorch'],
    ['Tipping','#6e3e1e','too-fast heat, burnt tips','burnt, bitter','tip'],
    ['Facing','#5a3216','stuck on drum, one side charred','acrid, smoky','face'],
    ['Chipping','#5a3216','2nd-crack pressure, chunk lost','burnt bits','chip'],
    ['Underdeveloped','#a06a3a','too fast \u2014 pale, matte','grassy, sour, thin',null],
    ['Overdeveloped','#3a2412','too long \u2014 dark &amp; oily','bitter, charred, ashy','oil'],
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
  ['Tall, low-yield','Drought-tolerant, deep roots','Susceptible: rust &amp; CBD'],
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
    ['Co-fermentation','+ fruit/spice/cacao (debated)','layered candy &amp; spice notes','#c86a9a'],
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
  const W=760,H=290;
  let g=diaDefs(['#a0824a','#8A5A34','#c0433a','#7a9a6a']);
  g=`<defs>${diaArrowMarker('#e0864a')}
    <linearGradient id="mokaMetal" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#6f6a63"/><stop offset="0.4" stop-color="#b8b2a6"/><stop offset="0.5" stop-color="#d8d2c4"/><stop offset="0.6" stop-color="#b8b2a6"/><stop offset="1" stop-color="#5f5a53"/></linearGradient>
    <linearGradient id="mokaMetalT" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7a746c"/><stop offset="0.45" stop-color="#c2bcb0"/><stop offset="0.5" stop-color="#e2dccf"/><stop offset="0.6" stop-color="#c2bcb0"/><stop offset="1" stop-color="#6a655e"/></linearGradient>
  </defs>`+g;
  g+=diaHeader(24,16,320,'The three chambers','steam pressure pushes water up','#a0824a');
  // ---- LEFT: a REAL moka-pot silhouette (octagonal Bialetti), cut away to show flow ----
  // Overall: wide base boiler (bottom), pinched waist where it screws, faceted top that
  // tapers up to the lid; a spout on the right and the black triangular handle on the left.
  const cx=180, baseY=250, topY=70;
  // ---- BASE (boiler) : faceted tapered body, widest at bottom ----
  g+=`<path d="M${cx-58} ${baseY} L${cx-52} 176 L${cx-30} 166 L${cx+30} 166 L${cx+52} 176 L${cx+58} ${baseY} Z" fill="url(#mokaMetal)" stroke="#4a463f" stroke-width="1.4"/>`;
  // facet lines on the base (octagonal read)
  g+=`<path d="M${cx-30} ${baseY} L${cx-27} 168 M${cx+30} ${baseY} L${cx+27} 168 M${cx} ${baseY} L${cx} 166" stroke="#5a554d" stroke-width="0.8" opacity="0.5"/>`;
  // water inside the boiler (cut-away): a translucent blue fill in the lower base
  g+=`<clipPath id="mokaBase"><path d="M${cx-58} ${baseY} L${cx-52} 176 L${cx-30} 166 L${cx+30} 166 L${cx+52} 176 L${cx+58} ${baseY} Z"/></clipPath>`;
  g+=`<g clip-path="url(#mokaBase)"><rect x="${cx-58}" y="212" width="116" height="44" fill="#6a8fb0" opacity="0.32"/><rect x="${cx-58}" y="212" width="116" height="3" fill="#8fb0cc" opacity="0.5"/></g>`;
  // safety valve nub on the base side
  g+=`<circle cx="${cx+52}" cy="205" r="3" fill="#8a8579" stroke="#4a463f" stroke-width="0.8"/>`;
  // ---- WAIST: the screw joint (a narrow dark band) ----
  g+=`<rect x="${cx-30}" y="160" width="60" height="8" fill="#4a463f"/>`;
  // ---- FUNNEL + FILTER (inside, cut-away): stem down into base, basket of grounds at the waist ----
  g+=`<rect x="${cx-4}" y="168" width="8" height="42" fill="#9a948a" stroke="#5a554d" stroke-width="0.7"/>`;  // stem
  g+=`<path d="M${cx-30} 150 L${cx+30} 150 L${cx+22} 160 L${cx-22} 160 Z" fill="#8a847a" stroke="#5a554d" stroke-width="1"/>`; // filter basket
  for(let i=0;i<12;i++){g+=`<circle cx="${cx-24+((i*11)%48)}" cy="${152+((i*5)%7)}" r="1.7" fill="#4a2f18"/>`;} // grounds
  // ---- TOP (collector) : faceted body tapering up to a small lid + knob ----
  g+=`<path d="M${cx-50} 160 L${cx-40} ${topY+22} L${cx-22} ${topY} L${cx+22} ${topY} L${cx+40} ${topY+22} L${cx+50} 160 Z" fill="url(#mokaMetalT)" stroke="#4a463f" stroke-width="1.4"/>`;
  g+=`<path d="M${cx-18} 160 L${cx-14} ${topY+20} M${cx+18} 160 L${cx+14} ${topY+20} M${cx} 160 L${cx} ${topY}" stroke="#6a655e" stroke-width="0.8" opacity="0.45"/>`;
  // brewed coffee pooling in the collector (cut-away)
  g+=`<clipPath id="mokaTop"><path d="M${cx-50} 160 L${cx-40} ${topY+22} L${cx-22} ${topY} L${cx+22} ${topY} L${cx+40} ${topY+22} L${cx+50} 160 Z"/></clipPath>`;
  g+=`<g clip-path="url(#mokaTop)"><rect x="${cx-50}" y="132" width="100" height="28" fill="#3a2216" opacity="0.7"/></g>`;
  // lid + knob
  g+=`<path d="M${cx-24} ${topY} Q${cx} ${topY-12} ${cx+24} ${topY} Z" fill="url(#mokaMetalT)" stroke="#4a463f" stroke-width="1.2"/>`;
  g+=`<circle cx="${cx}" cy="${topY-9}" r="5" fill="#2a2622" stroke="#4a463f" stroke-width="1"/>`;
  // spout (right)
  g+=`<path d="M${cx+48} 150 L${cx+66} 140 L${cx+60} 152 L${cx+49} 158 Z" fill="url(#mokaMetalT)" stroke="#4a463f" stroke-width="1"/>`;
  // handle (left) — the classic black triangular bakelite handle
  g+=`<path d="M${cx-50} 150 C${cx-92} 150 ${cx-96} 200 ${cx-62} 206 L${cx-58} 198 C${cx-82} 194 ${cx-80} 158 ${cx-50} 160 Z" fill="#2a2622" stroke="#1a1613" stroke-width="1"/>`;
  // ---- internal flow arrows: water up the stem -> through grounds -> into collector ----
  g+=`<path d="M${cx} 224 L${cx} 172" stroke="#e0864a" stroke-width="2.2" marker-end="url(#darr)" opacity="0.92"/>`;
  g+=`<path d="M${cx} 150 L${cx} 128" stroke="#8a5a34" stroke-width="2.2" marker-end="url(#darr)" opacity="0.92"/>`;
  // flame under base
  for(let i=-1;i<=1;i++){g+=`<path d="M${cx+i*20} ${baseY+16} q5 -12 0 -20 q-5 8 0 20" fill="#e0864a" opacity="0.7"/>`;}
  // chamber labels (to the LEFT of the handle so they never overlap the pot)
  const lab=(y,n,t,sub)=>{g+=`<text x="66" y="${y}" fill="#f0e6d8" font-size="10.5" font-weight="700" text-anchor="end" font-family="ui-sans-serif">${n} ${t}</text>`;g+=`<text x="66" y="${y+13}" fill="${DIA.ink3}" font-size="8.5" text-anchor="end" font-family="ui-sans-serif">${sub}</text>`;};
  // put labels stacked down the far left
  // chamber labels — placed to the RIGHT of the pot, left-anchored, clear of the body
  const potR=246; // right extent of the pot (spout)
  const lx=272;
  g+=`<text x="${lx}" y="90" fill="#f0e6d8" font-size="10.5" font-weight="700" text-anchor="start" font-family="ui-sans-serif">3 \u00b7 Top: brewed coffee</text><text x="${lx}" y="103" fill="${DIA.ink3}" font-size="8.5" text-anchor="start" font-family="ui-sans-serif">collects up here</text>`;
  g+=`<text x="${lx}" y="150" fill="#f0e6d8" font-size="10.5" font-weight="700" text-anchor="start" font-family="ui-sans-serif">2 \u00b7 Grounds basket</text><text x="${lx}" y="163" fill="${DIA.ink3}" font-size="8.5" text-anchor="start" font-family="ui-sans-serif">coarse grind, no tamp</text>`;
  g+=`<text x="${lx}" y="212" fill="#f0e6d8" font-size="10.5" font-weight="700" text-anchor="start" font-family="ui-sans-serif">1 \u00b7 Base: water</text><text x="${lx}" y="225" fill="${DIA.ink3}" font-size="8.5" text-anchor="start" font-family="ui-sans-serif">heat \u2192 steam \u2192 pressure</text>`;
  // leader lines from the pot's right edge to each label (never cross the body)
  g+=`<line x1="${cx+50}" y1="95" x2="${lx-8}" y2="90" stroke="#6a5c48" stroke-width="0.8" opacity="0.45"/>`;
  g+=`<line x1="${cx+30}" y1="152" x2="${lx-8}" y2="150" stroke="#6a5c48" stroke-width="0.8" opacity="0.45"/>`;
  g+=`<line x1="${cx+56}" y1="218" x2="${lx-8}" y2="212" stroke="#6a5c48" stroke-width="0.8" opacity="0.45"/>`;
  // ---- RIGHT: moka vs espresso comparison (kept, it reads well) ----
  g+=diaHeader(410,16,330,'Not quite espresso','pressure is the difference','#7a9a6a');
  const rows=[['Moka pot','~1\u20132 bar','#a0824a','bold, light crema'],['True espresso','~9 bar','#c0433a','syrupy, full crema']];
  rows.forEach((r,i)=>{const y=64+i*54;
    g+=diaCard(410,y,330,44,r[2],{r:9});
    g+=`<text x="426" y="${y+19}" fill="#f0e6d8" font-size="13" font-weight="700" font-family="ui-sans-serif">${r[0]}</text>`;
    g+=`<text x="426" y="${y+35}" fill="${DIA.ink3}" font-size="10" font-family="ui-sans-serif">${r[3]}</text>`;
    g+=`<text x="724" y="${y+27}" fill="${r[2]}" font-size="15" font-weight="800" text-anchor="end" font-family="ui-monospace">${r[1]}</text>`;
  });
  g+=`<text x="575" y="192" fill="#c9b8a4" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">Lands between espresso and a strong pour-over.</text>`;
  g+=`<text x="575" y="209" fill="${DIA.ink3}" font-size="10" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">Tip: start with HOT water, don't tamp, pull off at the gurgle.</text>`;
  g+=`<text x="${W/2}" y="${H-8}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">Bialetti's 1933 idea: fit cafe-style pressure brewing into a pot for the home stove.</text>`;
  return diaWrap(`${W} ${H}`,g,'How a moka pot brews, and why it sits just short of true espresso.');
}// 58. Green-bean defect gallery — the SCA grading defects, as illustrated raw beans.
function diaGreenDefects(){
  const W=760,H=430;
  // a raw (green) coffee bean at (cx,cy), scale s, base fill, optional defect overlay
  const gbean=(cx,cy,s,fill,overlay)=>diaBean(cx,cy,s*1.15,fill,'green',overlay);
  // cells: [name, base-fill, category tag, cause/look, overlay]
  const green='#66805c', paleGreen='#9aa86a';
  const cells=[
    ['Healthy','#66805c','—','even blue-green, dense',null],
    ['Full black','#66805c','CAT 1','over-fermented / dead','fullblack'],
    ['Full sour','#66805c','CAT 1','reddish-brown, over-fermented','sour'],
    ['Partial black','#66805c','CAT 2','part of the bean blackened','partblack'],
    ['Insect damage','#66805c','CAT 2','borer holes (broca)','insect'],
    ['Broken / chipped','#66805c','CAT 2','cut, pale inner exposed','broken'],
    ['Immature','#9aa86a','CAT 2','pale, thin — silverskin sticks','immature'],
    ['Shell / ear','#66805c','CAT 2','malformed hollow shape','shell'],
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
// 59. Caturra &amp; Catuai workhorse spotlight: the parent-offspring pair + shared traits.
function diaSpotWorkhorse(){
  const W=760,H=260;
  let g=diaDefs(['#c9a34e','#8fbf3a','#c86a6a','#B07B3E']);
  g=`<defs>${diaArrowMarker('#8a7660')}</defs>`+g;
  // lineage across the top: Bourbon -> Caturra -> (x Mundo Novo) -> Catuai
  g+=`<text x="30" y="26" fill="${DIA.ink3}" font-size="10.5" font-family="ui-monospace">THE LINEAGE</text>`;
  const chain=[['Bourbon','the founder','#c86a6a',40],['Caturra','dwarf mutation','#c9a34e',235],['Catua\u00ed','\u00d7 Mundo Novo','#8fbf3a',430]];
  chain.forEach((c,i)=>{
    g+=diaCard(c[3],36,150,40,c[2],{r:9,strong:i>0});
    g+=`<text x="${c[3]+75}" y="54" fill="#f0e6d8" font-size="13" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">${c[0]}</text>`;
    g+=`<text x="${c[3]+75}" y="69" fill="${DIA.ink3}" font-size="9" text-anchor="middle" font-family="ui-sans-serif">${c[1]}</text>`;
    if(i<chain.length-1)g+=`<path d="M${c[3]+152} 56 L${c[3]+193} 56" stroke="#8a7660" stroke-width="2" marker-end="url(#darr)"/>`;
  });
  // note that a workhorse note lives at right
  g+=`<path d="M582 56 L623 56" stroke="#8a7660" stroke-width="2" marker-end="url(#darr)" opacity="0.6"/>`;
  g+=diaCard(626,36,110,40,'#B07B3E',{r:9,shadow:false});
  g+=`<text x="681" y="53" fill="#f0e6d8" font-size="10.5" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">Everyday</text>`;
  g+=`<text x="681" y="68" fill="${DIA.ink3}" font-size="9" text-anchor="middle" font-family="ui-sans-serif">backbone</text>`;
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
  const W=760,H=320;
  let g=diaDefs(['#7d9f4a','#C9A34E','#c86a4a','#8fbf3a','#B07B3E']);
  g=`<defs>${diaArrowMarker('#9a8468')}</defs>`+g;
  // Loop nodes in a clean pentagon on the LEFT; scale-up card on the RIGHT.
  // Labels are pushed radially outward with real clearance so nothing collides.
  const cx=224,cy=150,rx=132,ry=100;
  // order clockwise from top: 1 Green, 2 Sample roast, 3 Cup, 4 Adjust, 5 Repeat
  const nodes=[
    ['Green','assess density, moisture','#8caf5a',-90,'below'],
    ['Sample roast','small batch','#C9A34E',-18,'right'],
    ['Cup','score blind','#c86a4a',54,'right'],
    ['Adjust','change ONE variable','#8fbf3a',126,'left'],
    ['Repeat','converge on the target','#B07B3E',198,'left'],
  ];
  const pts=nodes.map(n=>{const a=n[3]*Math.PI/180;return [cx+Math.cos(a)*rx, cy+Math.sin(a)*ry];});
  // curved directional arrows around the ring (clockwise flow)
  nodes.forEach((n,i)=>{const p=pts[i],q=pts[(i+1)%nodes.length];
    const mx=(p[0]+q[0])/2,my=(p[1]+q[1])/2;
    // bow the arc outward from centre for a smooth ring
    const bx=mx+(mx-cx)*0.14, by=my+(my-cy)*0.14;
    // trim endpoints to the node radius so arrowheads meet the circle edge
    const trim=(from,to)=>{const dx=to[0]-from[0],dy=to[1]-from[1],d=Math.hypot(dx,dy);return [from[0]+dx/d*20, from[1]+dy/d*20];};
    const s=trim(p,[bx,by]), e=trim(q,[bx,by]);
    g+=`<path d="M${s[0].toFixed(0)} ${s[1].toFixed(0)} Q${bx.toFixed(0)} ${by.toFixed(0)} ${e[0].toFixed(0)} ${e[1].toFixed(0)}" stroke="#9a8468" stroke-width="2" fill="none" marker-end="url(#darr)" opacity="0.75"/>`;
  });
  // nodes: numbered, color-coded, with a label + one-line note placed clear of the ring
  nodes.forEach((n,i)=>{const p=pts[i];
    g+=`<circle cx="${p[0].toFixed(0)}" cy="${p[1].toFixed(0)}" r="17" fill="url(#${_cid(n[2])})" stroke="${n[2]}" stroke-width="2.4" filter="url(#dsoft)"/>`;
    g+=`<text x="${p[0].toFixed(0)}" y="${(p[1]+5).toFixed(0)}" fill="#f5ecdd" font-size="13" font-weight="800" text-anchor="middle" font-family="ui-sans-serif">${i+1}</text>`;
    let lx,ly,anchor;
    if(n[4]==='below'){lx=p[0];ly=p[1]-40;anchor='middle';}          // top node label well ABOVE it
    else if(n[4]==='right'){lx=p[0]+26;ly=p[1]-2;anchor='start';}
    else {lx=p[0]-26;ly=p[1]-2;anchor='end';}
    g+=`<text x="${lx.toFixed(0)}" y="${(ly).toFixed(0)}" fill="${n[2]}" font-size="13" font-weight="700" text-anchor="${anchor}" font-family="ui-sans-serif">${n[0]}</text>`;
    g+=`<text x="${lx.toFixed(0)}" y="${(ly+14).toFixed(0)}" fill="${DIA.ink3}" font-size="9.5" text-anchor="${anchor}" font-family="ui-sans-serif">${n[1]}</text>`;
  });
  // arrow out to the scale-up card
  g+=`<path d="M392 150 L486 150" stroke="#9a8468" stroke-width="2" marker-end="url(#darr)" opacity="0.75"/>`;
  // scale-to-production card on the right
  g+=diaCard(496,104,242,92,'#B07B3E',{r:12,title:'THEN SCALE UP',titleSize:12,strong:true});
  ['Re-map the curve to the','production roaster (mass','and airflow differ) \u2014 then','re-cup to confirm.'].forEach((t,i)=>{
    g+=`<text x="617" y="${140+i*15}" fill="#c9b8a4" font-size="10" text-anchor="middle" font-family="ui-sans-serif">${t}</text>`;});
  // caption, fully clear below everything
  g+=`<text x="${W/2}" y="${H-10}" fill="${DIA.ink3}" font-size="11" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">Change one variable at a time, cup blind, document everything \u2014 that's how a profile is built.</text>`;
  return diaWrap(`${W} ${H}`,g,'The sample-roasting loop: roast, cup, adjust one thing, repeat, then scale to production.');
}// 61. Typica spotlight: the great journey out of Yemen + famous descendants.
function diaSpotTypica(){
  const W=760,H=266;
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
  g+=`<text x="${W/2}" y="122" fill="${DIA.ink3}" font-size="9.5" text-anchor="middle" font-family="ui-sans-serif" font-style="italic">Until the 1940s, most Central &amp; South American coffee was Typica.</text>`;
  // DESCENDANTS + the bargain, two cards (taller, body text starts BELOW the title)
  g+=diaCard(30,138,350,92,'#8fbf3a',{r:11,title:'FAMOUS DESCENDANTS',titleSize:12});
  ['Jamaica Blue Mountain \u00b7 Hawaiian Kona','Maragogipe (the \u2018elephant bean\u2019 mutation)','a.k.a. Criollo \u00b7 Ar\u00e1bigo \u00b7 Pluma Hidalgo \u00b7 Sumatra'].forEach((t,i)=>{
    g+=`<text x="205" y="${184+i*18}" fill="#c9b8a4" font-size="10" text-anchor="middle" font-family="ui-sans-serif">${t}</text>`;});
  g+=diaCard(390,138,350,92,'#c86a6a',{r:11,title:'THE BARGAIN',titleSize:12});
  ['Cup: clean, elegant, sweet, refined','BUT ~20\u201330% lower yield than Bourbon','tall &amp; rust-prone \u2192 quality-over-yield choice'].forEach((t,i)=>{
    g+=`<text x="565" y="${184+i*18}" fill="#c9b8a4" font-size="10" text-anchor="middle" font-family="ui-sans-serif">${t}</text>`;});
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
  // baseline axis under the bars
  g+=`<line x1="${bx-10}" y1="${by}" x2="${bx+150+bw+10}" y2="${by}" stroke="${DIA.line}" stroke-width="1.5"/>`;
  [['early 1990s',25,'#7a6a52',bx],['today',40,'#a0824a',bx+150]].forEach(b=>{
    const h=b[1]/45*bmax;
    g+=`<rect x="${b[3]}" y="${by-h}" width="${bw}" height="${h}" rx="6" fill="url(#${_cid(b[2])})" stroke="${b[2]}" stroke-width="1.5" filter="url(#dsoft)"/>`;
    g+=`<text x="${b[3]+bw/2}" y="${by-h-8}" fill="#f0e6d8" font-size="16" font-weight="800" text-anchor="middle" font-family="ui-monospace">${b[1]}%</text>`;
    g+=`<text x="${b[3]+bw/2}" y="${by+16}" fill="${DIA.ink3}" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">${b[0]}</text>`;
  });
  // emphatic growth arrow between bar tops
  g+=`<path d="M${bx+bw+6} ${by-25/45*bmax} Q${bx+bw+40} ${by-100} ${bx+150-6} ${by-40/45*bmax-6}" stroke="#8fbf3a" stroke-width="2.4" fill="none" opacity="0.8" marker-end="url(#darr)"/>`;
  g+=`<text x="${bx+bw+40}" y="${by-118}" fill="#8fbf3a" font-size="12" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">+60% growth</text>`;
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
  g+=diaCard(404,172,330,48,'#B07B3E',{r:9,shadow:false});
  g+=`<text x="418" y="190" fill="#f0e6d8" font-size="11" font-weight="700" font-family="ui-sans-serif">Fine robusta = its own category</text>`;
  g+=`<text x="418" y="204" fill="${DIA.ink3}" font-size="9.5" font-family="ui-sans-serif">choc/nut/savory + thick crema + ~2\u00d7 caffeine.</text>`;
  g+=`<text x="418" y="215" fill="${DIA.ink3}" font-size="9.5" font-family="ui-sans-serif">CQI Q-Robusta grading now exists.</text>`;
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
  g+=`<text x="${gx0-16}" y="${(gy0+gy1)/2}" fill="${DIA.ink3}" font-size="9" text-anchor="middle" font-family="ui-sans-serif" transform="rotate(-90 ${gx0-16} ${(gy0+gy1)/2})"># of particles \u2192</text>`;
  // x helper
  const X=f=>gx0+f*(gx1-gx0);
  const Y=v=>gy1-v*(gy1-gy0); // v in 0..1
  // gaussian helper
  const gauss=(x,mu,sig)=>Math.exp(-0.5*Math.pow((x-mu)/sig,2));
  // UNIMODAL (flat burr) - single tight peak, blue (filled)
  let uni='';
  for(let i=0;i<=100;i++){const f=i/100;const v=gauss(f,0.52,0.1);uni+=(i?'L':'M')+X(f).toFixed(1)+' '+Y(v*0.92).toFixed(1)+' ';}
  g+=`<path d="${uni} L${X(1)} ${gy1} L${gx0} ${gy1} Z" fill="${_rgba('#6a8fb0',0.28)}"/>`;
  g+=`<path d="${uni}" fill="none" stroke="#6a8fb0" stroke-width="2.6"/>`;
  // BIMODAL (conical) - main peak + fines spike, red/orange (filled, distinct)
  let bi='';
  for(let i=0;i<=100;i++){const f=i/100;const v=gauss(f,0.55,0.11)*0.8+gauss(f,0.14,0.05)*0.5;bi+=(i?'L':'M')+X(f).toFixed(1)+' '+Y(v*0.92).toFixed(1)+' ';}
  g+=`<path d="${bi} L${X(1)} ${gy1} L${gx0} ${gy1} Z" fill="${_rgba('#c86a4a',0.16)}"/>`;
  g+=`<path d="${bi}" fill="none" stroke="#c86a4a" stroke-width="2.6"/>`;
  // mark fines + boulders zones (labels sit lower inside the frame, clear of the legend)
  g+=`<line x1="${X(0.14)}" y1="${gy0}" x2="${X(0.14)}" y2="${gy1}" stroke="#c86a4a" stroke-width="1" stroke-dasharray="3 3" opacity="0.6"/>`;
  g+=`<text x="${X(0.14)}" y="${gy0+44}" fill="#c86a4a" font-size="10" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">FINES</text>`;
  g+=`<text x="${X(0.14)}" y="${gy0+58}" fill="${DIA.ink3}" font-size="8" text-anchor="middle" font-family="ui-sans-serif">over-extract</text>`;
  g+=`<text x="${X(0.14)}" y="${gy0+68}" fill="${DIA.ink3}" font-size="8" text-anchor="middle" font-family="ui-sans-serif">= bitter</text>`;
  g+=`<line x1="${X(0.9)}" y1="${gy0}" x2="${X(0.9)}" y2="${gy1}" stroke="#c9a34e" stroke-width="1" stroke-dasharray="3 3" opacity="0.6"/>`;
  g+=`<text x="${X(0.9)}" y="${gy0+44}" fill="#c9a34e" font-size="10" font-weight="700" text-anchor="middle" font-family="ui-sans-serif">BOULDERS</text>`;
  g+=`<text x="${X(0.9)}" y="${gy0+58}" fill="${DIA.ink3}" font-size="8" text-anchor="middle" font-family="ui-sans-serif">under-extract</text>`;
  g+=`<text x="${X(0.9)}" y="${gy0+68}" fill="${DIA.ink3}" font-size="8" text-anchor="middle" font-family="ui-sans-serif">= sour</text>`;
  // legend — centered ABOVE the frame, clear of the curves and zone labels
  const _lgY=gy0-16, _lg0=gx0+66, _lg1=gx0+296;
  g+=`<rect x="${_lg0}" y="${_lgY-4}" width="18" height="3" fill="#6a8fb0"/><text x="${_lg0+24}" y="${_lgY}" fill="#c9b8a4" font-size="9.5" font-family="ui-sans-serif">Flat burr \u2014 unimodal (clarity)</text>`;
  g+=`<rect x="${_lg1}" y="${_lgY-4}" width="18" height="3" fill="#c86a4a"/><text x="${_lg1+24}" y="${_lgY}" fill="#c9b8a4" font-size="9.5" font-family="ui-sans-serif">Conical \u2014 bimodal (more body)</text>`;
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
  const ccx=150,ccy=142;
  g+=`<defs><radialGradient id="bsSkin" cx="0.4" cy="0.32" r="0.8"><stop offset="0" stop-color="#d84a3a"/><stop offset="1" stop-color="#8a2a20"/></radialGradient><radialGradient id="bsPulp" cx="0.42" cy="0.36" r="0.8"><stop offset="0" stop-color="#e79a4a"/><stop offset="1" stop-color="#b06a28"/></radialGradient><radialGradient id="bsBean" cx="0.4" cy="0.34" r="0.78"><stop offset="0" stop-color="#a6bb7c"/><stop offset="1" stop-color="#6f8a4c"/></radialGradient></defs>`;
  g+=`<ellipse cx="${ccx}" cy="${ccy+5}" rx="58" ry="62" fill="#000" opacity="0.28" filter="url(#dsh)"/>`;
  g+=`<ellipse cx="${ccx}" cy="${ccy}" rx="56" ry="60" fill="url(#bsSkin)"/>`;
  g+=`<ellipse cx="${ccx}" cy="${ccy}" rx="44" ry="48" fill="url(#bsPulp)"/>`;
  const bbean=(sgn)=>`<path d="M${ccx} ${ccy-34} C${ccx+sgn*3} ${ccy-36} ${ccx+sgn*30} ${ccy-30} ${ccx+sgn*30} ${ccy} C${ccx+sgn*30} ${ccy+30} ${ccx+sgn*3} ${ccy+36} ${ccx} ${ccy+34} Z" fill="url(#bsBean)" stroke="#5a4632" stroke-width="1.2"/>`;
  g+=bbean(1)+bbean(-1);
  g+=`<path d="M${ccx} ${ccy-33} Q${ccx-2} ${ccy} ${ccx} ${ccy+33}" stroke="#4a3826" stroke-width="1.4" fill="none" opacity="0.8"/>`;
  g+=`<ellipse cx="${ccx}" cy="${ccy}" rx="32" ry="37" fill="none" stroke="#efe6d2" stroke-width="1" opacity="0.5"/>`;
  g+=`<ellipse cx="${ccx-18}" cy="${ccy-22}" rx="16" ry="12" fill="#fff" opacity="0.12"/>`;
  g+=`<path d="M${ccx} ${ccy-60} q-3 -8 2 -13" stroke="#5a2a1a" stroke-width="3" fill="none" stroke-linecap="round"/>`;
  g+=`<circle cx="${ccx-6}" cy="${ccy-58}" r="3.5" fill="#1a1008"/>`;
  g+=`<path d="M${ccx-6} ${ccy-56} q-8 22 0 44" stroke="#1a1008" stroke-width="2.2" fill="none" stroke-dasharray="2 3" opacity="0.85"/>`;
  for(const dy of [-8,4,16]){g+=`<ellipse cx="${ccx-8}" cy="${ccy+dy}" rx="2" ry="1.2" fill="#efe6d2" opacity="0.7"/>`;}
  const bx=ccx-2,by=ccy-70;
  g+=`<ellipse cx="${bx}" cy="${by}" rx="8" ry="5" fill="#241611" stroke="#4a3020" stroke-width="0.8"/>`;
  g+=`<ellipse cx="${bx-7}" cy="${by-1}" rx="3.5" ry="3" fill="#2e1c12"/>`;
  g+=`<line x1="${bx-9}" y1="${by-2}" x2="${bx-14}" y2="${by-5}" stroke="#2e1c12" stroke-width="1"/><circle cx="${bx-14.5}" cy="${by-5.5}" r="1.2" fill="#2e1c12"/>`;
  g+=`<line x1="${bx-9}" y1="${by+1}" x2="${bx-13}" y2="${by+3}" stroke="#2e1c12" stroke-width="1"/><circle cx="${bx-13.5}" cy="${by+3.5}" r="1.1" fill="#2e1c12"/>`;
  for(const lx of [-3,1,5]){g+=`<line x1="${bx+lx}" y1="${by+4}" x2="${bx+lx+1}" y2="${by+8}" stroke="#2e1c12" stroke-width="0.8"/>`;}
  g+=`<text x="${ccx+40}" y="${ccy-66}" fill="${DIA.ink3}" font-size="9" font-family="ui-sans-serif">female bores the tip</text>`;
  g+=`<text x="${ccx}" y="${ccy+82}" fill="#c9b8a4" font-size="10.5" text-anchor="middle" font-family="ui-sans-serif">tunnels the seed \u00b7 lays eggs \u00b7 larvae eat</text>`;
  g+=`<text x="${ccx}" y="${ccy+97}" fill="${DIA.ink3}" font-size="9.5" text-anchor="middle" font-family="ui-sans-serif">the bean from the inside \u2192 up to 80% loss</text>`;
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
// 66. Latte-art pour, taught kanji-stroke-order style. The art itself is generated
// PARAMETRICALLY (Bezier math, cross-referenced against real pour photos) so hearts,
// rosetta ferns, and tulip stacks come out smooth, symmetric, and fluid - like milk, not clip-art.
function diaPourStroke(){
  const W=760,H=478;
  let g=diaDefs(['#c9a34e','#B07B3E','#7a9a6a','#a0764a']);
  g=`<defs>${diaArrowMarker('#e8dcc8')}
    <marker id="darrR" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="#c0433a"/></marker>
    <radialGradient id="lacrema" cx="0.5" cy="0.42" r="0.78">
      <stop offset="0" stop-color="#9c5c2f"/><stop offset="0.62" stop-color="#7d4820"/><stop offset="1" stop-color="#532e15"/>
    </radialGradient>
    <radialGradient id="lamilk" cx="0.42" cy="0.36" r="0.95">
      <stop offset="0" stop-color="#fffdf7"/><stop offset="0.7" stop-color="#f6ecd6"/><stop offset="1" stop-color="#eaddc2"/>
    </radialGradient>
  </defs>`+g;
  const milk='url(#lamilk)', cut='#8a5124';
  let _lc=0;
  // ceramic cup, top-down: white rim ring + crema gradient surface
  const cup=(cx,cy,r)=>`<circle cx="${cx}" cy="${cy}" r="${r+3.4}" fill="#ddd2bf" filter="url(#dsoft)"/><circle cx="${cx}" cy="${cy}" r="${r}" fill="url(#lacrema)"/>`;
  // --- parametric latte HEART: round lobes, shallow dimple, soft pull-through point ---
  const heartD=(cx,cy,s)=>`M${(cx).toFixed(1)} ${(cy+s).toFixed(1)} C${(cx-0.9*s).toFixed(1)} ${(cy+0.45*s).toFixed(1)} ${(cx-1.05*s).toFixed(1)} ${(cy-0.08*s).toFixed(1)} ${(cx-0.86*s).toFixed(1)} ${(cy-0.38*s).toFixed(1)} C${(cx-0.65*s).toFixed(1)} ${(cy-0.7*s).toFixed(1)} ${(cx-0.2*s).toFixed(1)} ${(cy-0.72*s).toFixed(1)} ${(cx).toFixed(1)} ${(cy-0.4*s).toFixed(1)} C${(cx+0.2*s).toFixed(1)} ${(cy-0.72*s).toFixed(1)} ${(cx+0.65*s).toFixed(1)} ${(cy-0.7*s).toFixed(1)} ${(cx+0.86*s).toFixed(1)} ${(cy-0.38*s).toFixed(1)} C${(cx+1.05*s).toFixed(1)} ${(cy-0.08*s).toFixed(1)} ${(cx+0.9*s).toFixed(1)} ${(cy+0.45*s).toFixed(1)} ${(cx).toFixed(1)} ${(cy+s).toFixed(1)} Z`;
  const heart=(cx,cy,s,detail)=>{
    _lc++;const id='lah'+_lc;
    let o=`<path d="${heartD(cx,cy,s)}" fill="${milk}"/>`;
    if(detail){ // a soft inner shading + the single pull-through line down the center
      o+=`<path d="${heartD(cx,cy-0.03*s,0.82*s)}" fill="#fff" opacity="0.16"/>`;
      o+=`<path d="M${cx} ${(cy-0.42*s).toFixed(1)} L${cx} ${(cy+s+3).toFixed(1)}" stroke="${cut}" stroke-width="1.3" opacity="0.55" stroke-linecap="round"/>`;
    }
    return o;
  };
  // --- parametric ROSETTA fern (from real pour refs): a central spine with symmetric sickle
  //     leaves fanning out both sides, largest mid-cup, tapering top & bottom, curving back
  //     toward the base; capped by a small rounded head, then a stem cut straight through. ---
  const rosetta=(cx,cy,r,nLeaves,finished)=>{
    // leaves are laid from the near (bottom) edge up toward the far (top) edge
    const baseY=cy+0.86*r, headY=cy-0.72*r, span=baseY-headY;
    const maxW=0.80*r;
    let o='';
    // when partial (mid-pour), the leaves fill only the lower part of the cup
    const fill = finished?1:(nLeaves<=3?0.42:0.7);
    const usedSpan=span*fill;
    const N=nLeaves;
    // one symmetric leaf: attaches at the spine (sx,sy), sweeps out to (tipx,tipy) and back,
    // the tip pulled DOWN toward the base so the fern reads as flowing forward
    const leaf=(sy,w,drop,m)=>{
      const lift = w*0.20;            // shallow leading-edge rise
      const dr   = w*0.16 + 2.4;      // shallow tip drop -> flat sickle, rows stay separate
      const tipX = cx+m*w, tipY = sy + dr*0.15;
      const l1x=cx+m*0.36*w, l1y=sy-lift*0.8;
      const l2x=cx+m*0.82*w, l2y=sy-lift*0.2;
      const t1x=cx+m*0.74*w, t1y=sy+dr*1.0;
      const t2x=cx+m*0.26*w, t2y=sy+dr*0.85;
      const backY=sy+dr*0.5;
      return `<path d="M${cx} ${sy.toFixed(1)} C${l1x.toFixed(1)} ${l1y.toFixed(1)} ${l2x.toFixed(1)} ${l2y.toFixed(1)} ${tipX.toFixed(1)} ${tipY.toFixed(1)} C${t1x.toFixed(1)} ${t1y.toFixed(1)} ${t2x.toFixed(1)} ${t2y.toFixed(1)} ${cx} ${backY.toFixed(1)} Z" fill="${milk}"/>`;
    };
    // draw from the TOP (smallest) down so lower/larger leaves overlap on top — real layering
    for(let i=N-1;i>=0;i--){
      const t=N<=1?0:i/(N-1);                 // 0 = base leaf, 1 = top leaf
      const sy=baseY - t*usedSpan;
      // width bulges in the lower-middle, tapers at both ends (sinusoid on t)
      const bulge=Math.sin(Math.min(1,t*1.1+0.08)*Math.PI);   // 0 at base/top, 1 mid
      const w=maxW*(0.30+0.70*bulge);
      const drop=0.26*w+3.2;
      o+=leaf(sy,w,drop,1);
      o+=leaf(sy,w,drop,-1);
    }
    // rounded head cap at the far end
    if(finished){
      o+=`<ellipse cx="${cx}" cy="${(headY+0.02*r).toFixed(1)}" rx="${(0.16*r).toFixed(1)}" ry="${(0.13*r).toFixed(1)}" fill="${milk}"/>`;
      // central spine + pull-through stem
      o+=`<path d="M${cx} ${(headY-0.06*r).toFixed(1)} L${cx} ${(baseY+3.4).toFixed(1)}" stroke="${cut}" stroke-width="1.25" opacity="0.5" stroke-linecap="round"/>`;
    }
    return o;
  };
  // --- parametric TULIP (from real pour refs): stacked chevron petals, each smaller going up,
  //     a small round bloom on top, and a stem/point pulled through the bottom. ---
  const tulip=(cx,cy,r,nPetals,finished)=>{
    // petals stack from the near (bottom) edge upward; bottom is widest
    const botY=cy+0.72*r, topBloomY=cy-0.62*r;
    const rows=Math.max(1,nPetals);
    const stackSpan=(botY-topBloomY)*(finished?0.86:0.62);
    let o='';
    // a single petal: a pushed crescent — a wide arc whose underside curves up, cupping the next
    const petal=(yBase,w)=>{
      const lip=w*0.60;             // how far the crescent rises
      const inner=w*0.34;           // inner scoop depth (the "cup" that cradles the next petal)
      return `<path d="M${(cx-w).toFixed(1)} ${yBase.toFixed(1)} `+
             `C${(cx-0.55*w).toFixed(1)} ${(yBase-lip).toFixed(1)} ${(cx-0.2*w).toFixed(1)} ${(yBase-lip*1.05).toFixed(1)} ${cx} ${(yBase-lip*1.08).toFixed(1)} `+
             `C${(cx+0.2*w).toFixed(1)} ${(yBase-lip*1.05).toFixed(1)} ${(cx+0.55*w).toFixed(1)} ${(yBase-lip).toFixed(1)} ${(cx+w).toFixed(1)} ${yBase.toFixed(1)} `+
             `C${(cx+0.5*w).toFixed(1)} ${(yBase-inner).toFixed(1)} ${(cx-0.5*w).toFixed(1)} ${(yBase-inner).toFixed(1)} ${(cx-w).toFixed(1)} ${yBase.toFixed(1)} Z" fill="${milk}"/>`;
    };
    for(let i=0;i<rows;i++){
      const f=rows<=1?0:i/(rows-1);           // 0 = bottom (widest), 1 = top (narrowest)
      const yBase=botY - f*stackSpan;
      const w=r*(0.66-0.30*f);
      o+=petal(yBase,w);
    }
    if(finished){
      o+=`<path d="${heartD(cx,cy-0.42*r,0.17*r)}" fill="${milk}"/>`;
      o+=`<path d="M${cx} ${(cy-0.52*r).toFixed(1)} L${cx} ${(cy+0.46*r+3.4).toFixed(1)}" stroke="${cut}" stroke-width="1.25" opacity="0.6" stroke-linecap="round"/>`;
    }
    return o;
  };
  const badge=(cx,cy,n,col)=>`<circle cx="${cx}" cy="${cy}" r="10" fill="url(#${_cid(col)})" stroke="${col}" stroke-width="1.5" filter="url(#dsoft)"/><text x="${cx}" y="${cy+4}" fill="#f0e6d8" font-size="11" font-weight="800" text-anchor="middle" font-family="ui-monospace">${n}</text>`;
  const stepText=(cx,y,t)=>`<text x="${cx}" y="${y}" fill="${DIA.ink3}" font-size="9.5" text-anchor="middle" font-family="ui-sans-serif">${t}</text>`;
  const R=24, RF=37; // step cups + a larger HERO cup for the finished pour
  const xs=[108,268,428,602];

  // ---- ROW 1: THE HEART ----
  let hy=16, cy=hy+74;
  g+=diaHeader(20,hy,300,'The Heart','pour, fill, then cut through','#c9a34e');
  g+=cup(xs[0],cy,R);
  g+=`<path d="M${xs[0]} ${cy-36} L${xs[0]} ${cy-8}" stroke="#e8dcc8" stroke-width="2" marker-end="url(#darr)"/>`;
  g+=stepText(xs[0],cy+42,'pour high &amp; thin');g+=stepText(xs[0],cy+54,'(milk sinks in)');g+=badge(xs[0]-30,cy-24,1,'#c9a34e');
  g+=cup(xs[1],cy,R);g+=`<circle cx="${xs[1]}" cy="${cy+4}" r="${0.34*R}" fill="${milk}"/>`;
  g+=`<path d="M${xs[1]} ${cy-32} L${xs[1]} ${cy-6}" stroke="#e8dcc8" stroke-width="3.5" marker-end="url(#darr)"/>`;
  g+=stepText(xs[1],cy+42,'drop low &amp; close');g+=stepText(xs[1],cy+54,'a white disc grows');g+=badge(xs[1]-30,cy-24,2,'#c9a34e');
  g+=cup(xs[2],cy,R);g+=`<circle cx="${xs[2]}" cy="${cy+1}" r="${0.62*R}" fill="${milk}"/>`;
  g+=`<circle cx="${xs[2]}" cy="${cy+1}" r="${0.4*R}" fill="none" stroke="${cut}" stroke-width="1" opacity="0.25"/>`;
  g+=stepText(xs[2],cy+42,'let it fill out');g+=stepText(xs[2],cy+54,'to a round pad');g+=badge(xs[2]-30,cy-24,3,'#c9a34e');
  g+=cup(xs[3],cy,RF);g+=heart(xs[3],cy,0.74*RF,true);
  g+=`<path d="M${xs[3]} ${cy-RF-8} L${xs[3]} ${cy+RF+6}" stroke="#c0433a" stroke-width="1.6" stroke-dasharray="3 3" marker-end="url(#darrR)"/>`;
  g+=stepText(xs[3],cy+RF+18,'cut up through it');g+=stepText(xs[3],cy+RF+30,'fast \u2192 a heart');g+=badge(xs[3]-34,cy-26,4,'#c9a34e');

  // ---- ROW 2: THE ROSETTA ----
  hy=170; cy=hy+74;
  g+=diaHeader(20,hy,300,'The Rosetta','wiggle side to side, then draw through','#7a9a6a');
  g+=cup(xs[0],cy,R);g+=`<circle cx="${xs[0]}" cy="${cy+8}" r="${0.3*R}" fill="${milk}"/>`;
  g+=`<path d="M${xs[0]} ${cy-34} L${xs[0]} ${cy-4}" stroke="#e8dcc8" stroke-width="3" marker-end="url(#darr)"/>`;
  g+=stepText(xs[0],cy+42,'settle a base');g+=stepText(xs[0],cy+54,'low &amp; close');g+=badge(xs[0]-30,cy-24,1,'#7a9a6a');
  g+=cup(xs[1],cy,R);g+=rosetta(xs[1],cy,R,3,false);
  g+=`<path d="M${xs[1]-7} ${cy-36} l7 4 l-14 4 l14 4 l-14 4 l10 4" stroke="#e8dcc8" stroke-width="2" fill="none" marker-end="url(#darr)"/>`;
  g+=stepText(xs[1],cy+42,'wiggle side-to-side');g+=stepText(xs[1],cy+54,'as you draw back');g+=badge(xs[1]-30,cy-24,2,'#7a9a6a');
  g+=cup(xs[2],cy,R);g+=rosetta(xs[2],cy,R,6,false);
  g+=stepText(xs[2],cy+42,'keep pulling back');g+=stepText(xs[2],cy+54,'leaves stack up');g+=badge(xs[2]-30,cy-24,3,'#7a9a6a');
  g+=cup(xs[3],cy,RF);g+=rosetta(xs[3],cy,RF*1.02,7,true);
  g+=`<path d="M${xs[3]} ${cy+RF+4} L${xs[3]} ${cy-RF-8}" stroke="#c0433a" stroke-width="1.6" stroke-dasharray="3 3" marker-end="url(#darrR)"/>`;
  g+=stepText(xs[3],cy+RF+18,'draw through the');g+=stepText(xs[3],cy+RF+30,'middle \u2192 a fern');g+=badge(xs[3]-34,cy-26,4,'#7a9a6a');

  // ---- ROW 3: THE TULIP ----
  hy=324; cy=hy+74;
  g+=diaHeader(20,hy,300,'The Tulip','stack pushes, then pull through','#B07B3E');
  g+=cup(xs[0],cy,R);g+=`<circle cx="${xs[0]}" cy="${cy+7}" r="${0.26*R}" fill="${milk}"/>`;
  g+=`<path d="M${xs[0]} ${cy-34} L${xs[0]} ${cy-4}" stroke="#e8dcc8" stroke-width="3" marker-end="url(#darr)"/>`;
  g+=stepText(xs[0],cy+42,'push a first blob');g+=badge(xs[0]-30,cy-24,1,'#B07B3E');
  g+=cup(xs[1],cy,R);g+=tulip(xs[1],cy,R,1,false);g+=`<circle cx="${xs[1]}" cy="${cy-2}" r="${0.24*R}" fill="${milk}"/>`;
  g+=`<path d="M${xs[1]} ${cy-34} L${xs[1]} ${cy-10}" stroke="#e8dcc8" stroke-width="3" marker-end="url(#darr)"/>`;
  g+=`<text x="${xs[1]+42}" y="${cy-28}" fill="${DIA.ink3}" font-size="9" font-family="ui-sans-serif">stop \u00b7 push again</text>`;
  g+=stepText(xs[1],cy+42,'stop, push behind');g+=badge(xs[1]-30,cy-24,2,'#B07B3E');
  g+=cup(xs[2],cy,R);g+=tulip(xs[2],cy,R,3,false);
  g+=stepText(xs[2],cy+42,'repeat = a stack');g+=stepText(xs[2],cy+54,'of nested cups');g+=badge(xs[2]-30,cy-24,3,'#B07B3E');
  g+=cup(xs[3],cy,RF);g+=tulip(xs[3],cy,RF*1.0,3,true);
  g+=`<path d="M${xs[3]} ${cy-RF-8} L${xs[3]} ${cy+RF+4}" stroke="#c0433a" stroke-width="1.6" stroke-dasharray="3 3" marker-end="url(#darrR)"/>`;
  g+=stepText(xs[3],cy+RF+18,'pull through \u2192');g+=stepText(xs[3],cy+RF+30,'a tulip');g+=badge(xs[3]-34,cy-26,4,'#B07B3E');

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
    case 'roasters':return diaImg('roasters.png','The three main roaster architectures and what each is good at.','Drum, fluid-bed, and hybrid coffee roasters compared');
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
    case 'pourstroke':return diaImg('latteart.png','The three foundational pours \u2014 sink a base, texture the surface, then cut or pull through to finish.','Heart, rosetta, and tulip latte-art pours shown step by step');
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
    'maillard':findDef('maillard'),'caramelization':findDef('maillard'),
    'first crack':findDef('first crack'),'second crack':findDef('second crack'),
    'rate of rise':findDef('rate of rise'),'development time ratio':findDef('development time ratio'),
    'drum roaster':findDef('drum'),'fluid-bed':findDef('fluid-bed'),'fluid bed':findDef('fluid-bed'),
    'washed process':findDef('washed'),'natural process':findDef('washed'),'honey process':findDef('washed'),
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
  // Stoplist: common English words that carry a coffee glossary sense but are usually
  // used in their ordinary meaning. Never auto-link these on their own — they produced
  // false positives ("washed repeatedly", "cherries' development", "clean tea-like body").
  const STOP=new Set(['washed','development','body','clean','wild','natural','green','roast','crack','bright','dry','wet','hard','soft','drop','charge','slurp','airflow','chaff','process','honey']);
  STOP.forEach(w=>{delete GLOSS_MAP[w];});
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

# --- Copy illustrated PNG diagrams into ./img/ (source lives in ./img_src/) ---
_img_src = BASE / "img_src"
_img_out = BASE / "img"
_img_out.mkdir(exist_ok=True)
_copied = []
for _f in IMG_ASSETS:
    _s = _img_src / _f
    if _s.exists():
        shutil.copy2(_s, _img_out / _f)
        _copied.append(_f)
    else:
        print(f"  WARNING: image asset missing: img_src/{_f}")
print(f"Copied {len(_copied)} image asset(s) into img/: {', '.join(_copied) if _copied else '(none)'}")

# --- Service worker: cache the shell + illustrated images for offline field use ---
_img_paths = "".join(f',"./img/{f}"' for f in IMG_ASSETS)
sw = f'''const CACHE="{CACHE_C}";
const ASSETS=["./","./index.html","./manifest.webmanifest","./icon.svg"{_img_paths}];
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
