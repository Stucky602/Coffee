#!/usr/bin/env python3
"""Generate clean placeholder PNGs for the illustrated diagrams (latte art, roasters).
These match the app's dark theme and read as intentional 'art pending' cards, so the
app is fully functional until the real illustrations are dropped in (same filenames)."""
from PIL import Image, ImageDraw, ImageFont
import pathlib

OUT = pathlib.Path(__file__).parent / "img_src"
OUT.mkdir(exist_ok=True)

# app palette
PANEL = (36, 26, 18)
LINE = (74, 60, 44)
INK = (240, 230, 216)
INK3 = (162, 144, 122)
ACCENT = (201, 163, 78)

def font(sz, bold=False):
    # fall back to default bitmap font if no truetype available
    for name in (["DejaVuSans-Bold.ttf"] if bold else ["DejaVuSans.ttf"]):
        for p in ["/usr/share/fonts/truetype/dejavu/"+name,
                  "/usr/share/fonts/dejavu/"+name]:
            if pathlib.Path(p).exists():
                return ImageFont.truetype(p, sz)
    return ImageFont.load_default()

def placeholder(fname, W, H, title, subtitle, slots):
    scale = 2  # render at 2x for crispness
    im = Image.new("RGB", (W*scale, H*scale), PANEL)
    d = ImageDraw.Draw(im)
    s = scale
    # rounded border
    d.rounded_rectangle([6*s,6*s,(W-6)*s,(H-6)*s], radius=12*s, outline=LINE, width=2*s)
    # title
    d.text((W*s/2, 26*s), title, font=font(15*s, True), fill=ACCENT, anchor="mm")
    d.text((W*s/2, 46*s), subtitle, font=font(11*s), fill=INK3, anchor="mm")
    # slots: circles/labels laid across so the layout reads like the final art will
    n = len(slots)
    slotW = (W-40) / n
    cy = H*0.58
    for i, lab in enumerate(slots):
        cx = 20 + slotW*i + slotW/2
        r = 30
        d.ellipse([(cx-r)*s,(cy-r)*s,(cx+r)*s,(cy+r)*s], outline=LINE, width=2*s)
        # dashed inner ring to signal 'placeholder'
        d.ellipse([(cx-r+7)*s,(cy-r+7)*s,(cx+r-7)*s,(cy+r-7)*s], outline=(90,74,54), width=1*s)
        d.text((cx*s, cy*s), "art\npending", font=font(9*s), fill=INK3, anchor="mm", align="center")
        d.text((cx*s, (cy+r+16)*s), lab, font=font(11*s, True), fill=INK, anchor="mm")
    im.save(OUT / fname)
    print("wrote", (OUT/fname).name, im.size)

# Latte art: 3 patterns
placeholder("latteart.png", 760, 300,
            "Latte Art \u2014 the three foundational pours",
            "illustrated art pending \u2014 heart, rosetta, tulip",
            ["Heart", "Rosetta", "Tulip"])

# Roasters: 3 architectures
placeholder("roasters.png", 760, 260,
            "Roaster Types",
            "illustrated art pending \u2014 drum, fluid-bed, hybrid",
            ["Drum", "Fluid-bed", "Hybrid"])
