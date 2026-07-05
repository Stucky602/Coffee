#!/usr/bin/env python3
"""Generate the latte-art pour guide (heart / rosetta / tulip) as raster art.
Milk is rendered with soft-edged brushes on a crema-gradient cup, so patterns read
like poured microfoam rather than hard vector shapes.

Finished-shape geometry grounded in real pour references (Barista Hustle, Verve,
Loveramics WLAC cup): heart = round lobes + point + pulled stem; rosetta = central
spine with symmetric sickle leaves that get smaller toward the top, capped and cut
through; tulip = stacked pushed crescents narrowing upward + bloom + stem.
"""
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import numpy as np, pathlib, math

OUT = pathlib.Path(__file__).parent / "img_src"
OUT.mkdir(exist_ok=True)
SS = 4

PANEL=(36,26,18); LINE=(74,60,44); INK=(240,230,216); INK3=(162,144,122)
GOLD=(201,163,78); GREEN=(122,154,106); RED=(192,86,72)

def font(sz, bold=False, italic=False):
    name = "DejaVuSans-Bold.ttf" if bold else ("DejaVuSans-Oblique.ttf" if italic else "DejaVuSans.ttf")
    for p in ["/usr/share/fonts/truetype/dejavu/"+name,"/usr/share/fonts/dejavu/"+name]:
        if pathlib.Path(p).exists(): return ImageFont.truetype(p, sz)
    return ImageFont.load_default()

# ---- a cup: crema-gradient disc with a pale ceramic rim ----
def cup(draw_size, R):
    D=draw_size
    im=Image.new("RGBA",(D,D),(0,0,0,0))
    cx=cy=D/2
    # rim
    ImageDraw.Draw(im).ellipse([cx-R-R*0.06,cy-R-R*0.06,cx+R+R*0.06,cy+R+R*0.06],fill=(221,210,191,255))
    # crema radial gradient
    yy,xx=np.mgrid[0:D,0:D].astype(np.float32)
    dist=np.sqrt((xx-cx)**2+(yy-cy)**2)/R
    inner=np.array([156,92,47],np.float32); outer=np.array([83,46,21],np.float32)
    t=np.clip(dist,0,1)[...,None]
    crema=(inner*(1-t)+outer*t)
    # subtle lit top-left
    lit=np.clip(1-((xx-(cx-R*0.3))**2+(yy-(cy-R*0.3))**2)/(R*1.4)**2,0,1)[...,None]
    crema=np.clip(crema*(0.9+0.22*lit),0,255).astype(np.uint8)
    crema_img=Image.fromarray(crema,"RGB").convert("RGBA")
    m=Image.new("L",(D,D),0); ImageDraw.Draw(m).ellipse([cx-R,cy-R,cx+R,cy+R],fill=255)
    im=Image.composite(crema_img,im,m)
    return im, m  # return the crema mask to clip milk

MILK=(247,241,228)

def milk_layer(D):
    return Image.new("RGBA",(D,D),(0,0,0,0))

def stamp(layer, poly_or_pts, fill=MILK, blur=0):
    """draw a filled polygon (soft if blur>0) onto a milk layer via lighten."""
    tmp=Image.new("L",(layer.size[0],layer.size[1]),0)
    ImageDraw.Draw(tmp).polygon(poly_or_pts,fill=255)
    if blur: tmp=tmp.filter(ImageFilter.GaussianBlur(blur))
    col=Image.new("RGBA",layer.size,(*fill,255))
    layer.alpha_composite(Image.composite(col,Image.new("RGBA",layer.size,(0,0,0,0)),tmp))

def stamp_ellipse(layer, box, fill=MILK, blur=0):
    tmp=Image.new("L",(layer.size[0],layer.size[1]),0)
    ImageDraw.Draw(tmp).ellipse(box,fill=255)
    if blur: tmp=tmp.filter(ImageFilter.GaussianBlur(blur))
    col=Image.new("RGBA",layer.size,(*fill,255))
    layer.alpha_composite(Image.composite(col,Image.new("RGBA",layer.size,(0,0,0,0)),tmp))

# ---------------- FINISHED PATTERNS ----------------
def heart_pattern(D, cx, cy, R, finished=True):
    L=milk_layer(D)
    s=R*0.82
    # round heart: two lobes + point
    stamp_ellipse(L,[cx-s*0.95,cy-s*0.7,cx-s*0.02,cy+s*0.25],blur=D*0.004)
    stamp_ellipse(L,[cx+s*0.02,cy-s*0.7,cx+s*0.95,cy+s*0.25],blur=D*0.004)
    stamp(L,[(cx-s*0.9,cy-s*0.1),(cx+s*0.9,cy-s*0.1),(cx,cy+s*1.05)],blur=D*0.004)
    if finished:
        # pulled-through stem: a thin crema line down the center (erase milk)
        cut=Image.new("L",(D,D),0)
        ImageDraw.Draw(cut).line([(cx,cy-s*0.55),(cx,cy+s*1.05)],fill=255,width=int(D*0.006))
        cut=cut.filter(ImageFilter.GaussianBlur(D*0.002))
        a=L.split()[3]; a=ImageChops.subtract(a,cut); L.putalpha(a)
    return L

def rosetta_pattern(D, cx, cy, R, nLeaves=7, finished=True, fill_frac=1.0):
    L=milk_layer(D)
    baseY=cy+R*0.82; headY=cy-R*0.80; span=(baseY-headY)*fill_frac
    maxW=R*0.86
    def leaf(sy,w,m):
        # a flat sickle: leading edge up-out, tip, trailing edge back-in-down
        lift=w*0.18; drop=w*0.14+D*0.006
        tip=(cx+m*w, sy+drop*0.15)
        l1=(cx+m*0.36*w, sy-lift*0.8); l2=(cx+m*0.82*w, sy-lift*0.2)
        t1=(cx+m*0.74*w, sy+drop*1.0); t2=(cx+m*0.26*w, sy+drop*0.85)
        back=(cx, sy+drop*0.5)
        pts=[(cx,sy),l1,l2,tip,t1,t2,back]
        stamp(L,pts,blur=D*0.003)
    for i in range(nLeaves-1,-1,-1):
        t=0 if nLeaves<=1 else i/(nLeaves-1)
        sy=baseY - t*span
        bulge=math.sin(min(1,t*1.1+0.08)*math.pi)
        w=maxW*(0.30+0.70*bulge)
        leaf(sy,w,1); leaf(sy,w,-1)
    if finished:
        stamp_ellipse(L,[cx-R*0.14,headY-R*0.02,cx+R*0.14,headY+R*0.22],blur=D*0.003) # head
        # cut a thin spine through the middle
        cut=Image.new("L",(D,D),0)
        ImageDraw.Draw(cut).line([(cx,headY),(cx,baseY+D*0.01)],fill=255,width=int(D*0.005))
        cut=cut.filter(ImageFilter.GaussianBlur(D*0.0015))
        a=L.split()[3]; a=ImageChops.subtract(a,cut); L.putalpha(a)
    return L

def tulip_pattern(D, cx, cy, R, nPetals=4, finished=True, fill_frac=1.0):
    L=milk_layer(D)
    botY=cy+R*0.66; topBloomY=cy-R*0.58
    stackSpan=(botY-topBloomY)*(0.86 if finished else 0.6)*fill_frac
    rows=max(1,nPetals)
    def petal(yBase,w):
        lip=w*0.60; inner=w*0.34
        pts=[(cx-w,yBase),(cx-0.55*w,yBase-lip),(cx,yBase-lip*1.08),(cx+0.55*w,yBase-lip),
             (cx+w,yBase),(cx+0.5*w,yBase-inner),(cx-0.5*w,yBase-inner)]
        stamp(L,pts,blur=D*0.003)
    for i in range(rows):
        f=0 if rows<=1 else i/(rows-1)
        yBase=botY - f*stackSpan
        w=R*(0.62-0.28*f)
        petal(yBase,w)
    if finished:
        stamp_ellipse(L,[cx-R*0.12,topBloomY-R*0.02,cx+R*0.12,topBloomY+R*0.20],blur=D*0.003) # bloom
        cut=Image.new("L",(D,D),0)
        ImageDraw.Draw(cut).line([(cx,topBloomY),(cx,botY+D*0.01)],fill=255,width=int(D*0.005))
        cut=cut.filter(ImageFilter.GaussianBlur(D*0.0015))
        a=L.split()[3]; a=ImageChops.subtract(a,cut); L.putalpha(a)
    return L

# soft milk shading: give the flat white a subtle inner glow so it looks like foam
def shade_milk(L, D):
    alpha=L.split()[3]
    # inner highlight
    glow=alpha.filter(ImageFilter.GaussianBlur(D*0.01))
    hi=Image.new("RGBA",(D,D),(255,253,247,255))
    L=Image.composite(hi,L,ImageChops.multiply(glow, alpha))
    return L

def render_cup_with(D, R, pattern_fn, **kw):
    base,mask=cup(D,R)
    L=pattern_fn(D, D/2, D/2, R, **kw)
    L=shade_milk(L,D)
    # clip milk to crema
    L=Image.composite(L,Image.new("RGBA",(D,D),(0,0,0,0)),mask)
    base.alpha_composite(L)
    return base

# ---------------- FULL GALLERY ----------------
def build():
    W,H=760,470; s=SS
    im=Image.new("RGB",(W*s,H*s),PANEL); d=ImageDraw.Draw(im)
    d.rounded_rectangle([4*s,4*s,(W-4)*s,(H-4)*s],radius=14*s,outline=LINE,width=1*s)

    rows=[("The Heart","pour, fill, then cut through",GOLD,"heart",
           ["pour high & thin","drop low & close","let it fill out","cut up \u2192 a heart"]),
          ("The Rosetta","wiggle side to side, then draw through",GREEN,"rosetta",
           ["settle a base","wiggle side-to-side","keep pulling back","draw through \u2192 fern"]),
          ("The Tulip","stack pushes, then pull through",(210,150,70),"tulip",
           ["push a first blob","stop, push behind","repeat = a stack","pull through \u2192 tulip"])]

    y0=40; rowH=138; col_x=[150,330,510,660]; Rstep=30; Rhero=44
    for ri,(title,sub,accent,kind,caps) in enumerate(rows):
        ry=y0+ri*rowH
        # row label bar
        d.rectangle([30*s,ry*s,33*s,(ry+22)*s],fill=accent)
        d.text((40*s,(ry+2)*s),title,font=font(13*s,True),fill=INK)
        d.text((40*s,(ry+20)*s),sub,font=font(10*s),fill=INK3)
        cyc=ry+64
        for step in range(4):
            cx=col_x[step]; hero=(step==3)
            R=Rhero if hero else Rstep
            # build the step's pattern at increasing completeness
            Dd=int((R*2+R*0.5)*s)
            if kind=="heart":
                if step==0: patt=lambda D,x,y,r: (lambda L:(stamp_ellipse(L,[x-r*0.25,y-r*0.25,x+r*0.25,y+r*0.25],blur=D*0.006) or L))(milk_layer(D))
                elif step==1: patt=lambda D,x,y,r: (lambda L:(stamp_ellipse(L,[x-r*0.5,y-r*0.5,x+r*0.5,y+r*0.5],blur=D*0.006) or L))(milk_layer(D))
                elif step==2: patt=lambda D,x,y,r: (lambda L:(stamp_ellipse(L,[x-r*0.7,y-r*0.7,x+r*0.7,y+r*0.7],blur=D*0.006) or L))(milk_layer(D))
                else: patt=lambda D,x,y,r: heart_pattern(D,x,y,r,finished=True)
            elif kind=="rosetta":
                if step==0: patt=lambda D,x,y,r:(lambda L:(stamp_ellipse(L,[x-r*0.3,y-r*0.3,x+r*0.3,y+r*0.3],blur=D*0.006) or L))(milk_layer(D))
                elif step==1: patt=lambda D,x,y,r: rosetta_pattern(D,x,y,r,nLeaves=3,finished=False,fill_frac=0.5)
                elif step==2: patt=lambda D,x,y,r: rosetta_pattern(D,x,y,r,nLeaves=5,finished=False,fill_frac=0.75)
                else: patt=lambda D,x,y,r: rosetta_pattern(D,x,y,r,nLeaves=8,finished=True)
            else:
                if step==0: patt=lambda D,x,y,r:(lambda L:(stamp_ellipse(L,[x-r*0.28,y-r*0.28,x+r*0.28,y+r*0.28],blur=D*0.006) or L))(milk_layer(D))
                elif step==1: patt=lambda D,x,y,r: tulip_pattern(D,x,y,r,nPetals=2,finished=False,fill_frac=0.6)
                elif step==2: patt=lambda D,x,y,r: tulip_pattern(D,x,y,r,nPetals=3,finished=False,fill_frac=0.8)
                else: patt=lambda D,x,y,r: tulip_pattern(D,x,y,r,nPetals=4,finished=True)

            base,mask=cup(Dd,R*s if False else R* s)
            # NOTE: build cup at Dd with radius R*s
            base,mask=cup(Dd,R*s)
            L=patt(Dd, Dd/2, Dd/2, R*s)
            L=shade_milk(L,Dd)
            L=Image.composite(L,Image.new("RGBA",(Dd,Dd),(0,0,0,0)),mask)
            base.alpha_composite(L)
            base=base.resize((int(Dd),int(Dd)),Image.LANCZOS) if False else base
            im.paste(base,(int(cx*s-Dd/2),int(cyc*s-Dd/2)),base)
            # step number badge
            bx,by=cx-R-6, cyc-R-6
            d.ellipse([(bx-8)*s,(by-8)*s,(bx+8)*s,(by+8)*s],fill=PANEL,outline=accent,width=1*s)
            d.text((bx*s,by*s),str(step+1),font=font(9*s,True),fill=INK,anchor="mm")
            # caption under each step
            d.text((cx*s,(cyc+R+14)*s),caps[step],font=font(8.5*s),fill=INK3,anchor="mm")

    d.text((30*s,(H-20)*s),"The three foundational pours \u2014 sink a base, texture the surface, then cut or pull through to finish.",
           font=font(11*s),fill=INK3)
    im=im.resize((W,H),Image.LANCZOS)
    im.save(OUT/"latteart.png")
    print("wrote latteart.png",im.size)

build()
