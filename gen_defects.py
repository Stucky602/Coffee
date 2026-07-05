#!/usr/bin/env python3
"""Generate the green-coffee and roast-defect gallery images as raster art.
Uses Pillow with techniques SVG couldn't do: radial shading, fine noise texture,
soft-edged blotches, real cut/hole depth. Each bean is drawn from anatomy up:
body -> shading -> center-cut valley + silverskin -> defect overlay -> sheen.

Visual targets are grounded in SCA references (mtpak, Royal Coffee, Green Coffee
Collective, Perfect Daily Grind, Loring, Giesen).
"""
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import numpy as np, pathlib, math, random

OUT = pathlib.Path(__file__).parent / "img_src"
OUT.mkdir(exist_ok=True)
random.seed(7); np.random.seed(7)

# ---- app palette ----
PANEL=(36,26,18); LINE=(74,60,44); INK=(240,230,216); INK3=(162,144,122)
GOLD=(201,163,78); RED=(200,90,74); CAT1=(198,80,64)

SS = 4  # supersample factor for crisp anti-aliased beans

def font(sz, bold=False):
    names = ["DejaVuSans-Bold.ttf"] if bold else ["DejaVuSans.ttf"]
    names += ["DejaVuSans-Oblique.ttf"]
    for name in names:
        for p in ["/usr/share/fonts/truetype/dejavu/"+name, "/usr/share/fonts/dejavu/"+name]:
            if pathlib.Path(p).exists():
                return ImageFont.truetype(p, sz)
    return ImageFont.load_default()

def lerp(a,b,t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))
def mul(c,f): return tuple(max(0,min(255,int(x*f))) for x in c)

def noise_layer(size, amp, blur=0):
    """grayscale noise as an np array centered at 0, +/- amp."""
    n = np.random.rand(size,size).astype(np.float32)
    img = Image.fromarray((n*255).astype(np.uint8))
    if blur: img = img.filter(ImageFilter.GaussianBlur(blur))
    arr = np.asarray(img).astype(np.float32)/255.0
    return (arr-0.5)*2*amp

def bean_mask(D, kind):
    """return an L-mode mask (uint8) of an egg-shaped coffee bean of diameter ~D."""
    m = Image.new("L",(D,D),0); d=ImageDraw.Draw(m)
    cx,cy=D/2,D/2; rx,ry=D*0.34,D*0.44
    # egg: one end slightly broader (top narrower)
    pts=[]
    for a in range(0,360,3):
        t=math.radians(a)
        # asymmetry: widen lower half a touch
        yr = ry*(1.02 if math.sin(t)>0 else 0.98)
        xr = rx*(1.0 + 0.05*math.sin(t))
        pts.append((cx+xr*math.cos(t), cy+yr*math.sin(t)))
    d.polygon(pts, fill=255)
    m=m.filter(ImageFilter.GaussianBlur(D*0.006))
    return m

def draw_bean(D, base, kind, overlay=None):
    """Render one bean RGBA image of size DxD. kind in {'green','roast'}."""
    img = Image.new("RGBA",(D,D),(0,0,0,0))
    mask = bean_mask(D, kind)
    cx,cy=D/2,D/2; rx,ry=D*0.34,D*0.44

    # ---- body base with radial shading (lit top-left) ----
    yy,xx = np.mgrid[0:D,0:D].astype(np.float32)
    nx=(xx-(cx-rx*0.32))/(rx*1.5); ny=(yy-(cy-ry*0.3))/(ry*1.5)
    dist=np.sqrt(nx*nx+ny*ny)  # 0 near lit point -> larger outward
    shade=np.clip(1.0-dist*0.5,0,1)  # 1 lit -> 0 dark
    litc=np.array(mul(base,1.30),dtype=np.float32)
    darkc=np.array(mul(base,0.55),dtype=np.float32)
    body=(litc[None,None,:]*shade[...,None]+darkc[None,None,:]*(1-shade[...,None]))
    # fine matte/texture noise (green = matte, roast = a touch glossier)
    amp = 0.05 if kind=='green' else 0.06
    tex = noise_layer(D, amp, blur=0.6)
    body = np.clip(body*(1+tex[...,None]),0,255)
    bodyimg=Image.fromarray(body.astype(np.uint8),"RGB").convert("RGBA")
    img=Image.composite(bodyimg, img, mask)

    d=ImageDraw.Draw(img)
    # ---- ambient-occlusion rim (dark edge) ----
    rim=Image.new("L",(D,D),0); rd=ImageDraw.Draw(rim)
    rd.ellipse([cx-rx,cy-ry,cx+rx,cy+ry],outline=255,width=int(D*0.05))
    rim=rim.filter(ImageFilter.GaussianBlur(D*0.02))
    rim=ImageChops.multiply(rim,mask)
    dark=Image.new("RGBA",(D,D),(*mul(base,0.4),150))
    img=Image.composite(dark,img,rim)

    # ---- center-cut valley (wavy S) + silverskin ----
    def seam_pts(n=40):
        pts=[]
        for i in range(n+1):
            t=i/n
            y=cy-ry*0.82 + t*(ry*1.64)
            x=cx + math.sin(t*math.pi*2.1)*rx*0.16
            pts.append((x,y))
        return pts
    seam=seam_pts()
    # valley: dark channel underneath
    def draw_seam(strength=1.0):
        nonlocal img
        val=Image.new("L",(D,D),0); vd=ImageDraw.Draw(val)
        vd.line(seam,fill=int(255*strength),width=int(D*0.10),joint="curve")
        val=val.filter(ImageFilter.GaussianBlur(D*0.02)); val=ImageChops.multiply(val,mask)
        valdark=Image.new("RGBA",(D,D),(*mul(base,0.32),int(200*strength)))
        img=Image.composite(valdark,img,val)
        ss_col=(222,226,196) if kind=='green' else (232,220,196)
        ss=Image.new("L",(D,D),0); sd=ImageDraw.Draw(ss)
        sd.line(seam,fill=int((210 if kind=='green' else 150)*strength),width=int(D*0.045),joint="curve")
        ss=ss.filter(ImageFilter.GaussianBlur(D*0.008)); ss=ImageChops.multiply(ss,mask)
        img=Image.composite(Image.new("RGBA",(D,D),(*ss_col,255)),img,ss)
    draw_seam()

    # ================= DEFECT OVERLAYS =================
    def soft_blob(cxx,cyy,r,col,alpha,blur=None):
        bl=Image.new("L",(D,D),0); bd=ImageDraw.Draw(bl)
        bd.ellipse([cxx-r,cyy-r,cxx+r,cyy+r],fill=alpha)
        bl=bl.filter(ImageFilter.GaussianBlur(blur if blur else r*0.4))
        bl=ImageChops.multiply(bl,mask)
        ov=Image.new("RGBA",(D,D),(*col,255))
        return ov,bl

    def paste_blob(*a,**k):
        ov,bl=soft_blob(*a,**k); img.alpha_composite(Image.composite(ov,Image.new("RGBA",(D,D),(0,0,0,0)),bl))

    if overlay=='fullblack':
        blk=Image.new("RGBA",(D,D),(14,10,7,235)); img=Image.composite(blk,img,mask)
        # shrivel wrinkles (rebind draw to current img)
        d=ImageDraw.Draw(img)
        for k in range(5):
            yk=cy-ry*0.6+k*ry*0.3
            d.line([(cx-rx*0.5,yk),(cx+rx*0.5,yk+8)],fill=(40,30,22,120),width=2)
    elif overlay=='partblack':
        half=Image.new("L",(D,D),0); hd=ImageDraw.Draw(half)
        hd.pieslice([cx-rx,cy-ry,cx+rx,cy+ry],90,270,fill=230); half=ImageChops.multiply(half,mask)
        img=Image.composite(Image.new("RGBA",(D,D),(16,11,8,230)),img,half)
    elif overlay=='sour':
        # yellow->reddish-brown discoloration + reddish silverskin
        img=Image.composite(Image.new("RGBA",(D,D),(150,96,40,120)),img,mask)
        paste_blob(cx-rx*0.3,cy+ry*0.2,rx*0.7,(96,50,22),160)
        paste_blob(cx+rx*0.35,cy-ry*0.25,rx*0.5,(120,64,30),140)
        paste_blob(cx+rx*0.1,cy+ry*0.45,rx*0.4,(80,40,18),150)
        # reddish silverskin
        rs=Image.new("L",(D,D),0); rsd=ImageDraw.Draw(rs)
        rsd.line(seam,fill=170,width=int(D*0.04),joint="curve"); rs=rs.filter(ImageFilter.GaussianBlur(D*0.008)); rs=ImageChops.multiply(rs,mask)
        img=Image.composite(Image.new("RGBA",(D,D),(170,92,60,255)),img,rs)
    elif overlay=='insect':
        # several small deep borer holes — rebind draw to the CURRENT img (composites replaced it)
        d=ImageDraw.Draw(img)
        holes=[(-0.28,-0.15),(0.15,-0.22),(0.28,0.12),(-0.1,0.22),(0.34,-0.02),(-0.32,0.12),(0.05,-0.05)]
        for hx,hy in holes:
            px,py=cx+hx*rx*2,cy+hy*ry*2; r=D*0.030*random.uniform(0.85,1.35)
            d.ellipse([px-r*1.7,py-r*1.7,px+r*1.7,py+r*1.7],fill=(60,44,28,140))   # bored rim (frass)
            d.ellipse([px-r,py-r,px+r,py+r],fill=(14,9,5,255))                      # dark hole
            d.ellipse([px-r*0.5,py-r*0.5,px+r*0.2,py+r*0.2],fill=(0,0,0,255))       # deep center
    elif overlay=='broken':
        # clean cut face exposing paler inner
        inner=(200,206,168) if kind=='green' else (214,196,158)
        poly=[(cx+rx*0.2,cy-ry*0.7),(cx+rx*1.05,cy-ry*0.15),(cx+rx*0.9,cy+ry*0.5),(cx+rx*0.15,cy+ry*0.1)]
        cutm=Image.new("L",(D,D),0); ImageDraw.Draw(cutm).polygon(poly,fill=255); cutm=ImageChops.multiply(cutm,mask)
        img=Image.composite(Image.new("RGBA",(D,D),(*inner,255)),img,cutm)
        ImageDraw.Draw(img).line([poly[0],poly[3]],fill=(*mul(base,0.6),160),width=2)
    elif overlay=='immature':
        # pale yellow-green, shiny clinging silverskin, u-curl hint
        img=Image.composite(Image.new("RGBA",(D,D),(196,204,140,150)),img,mask)
        sk=Image.new("L",(D,D),0); ImageDraw.Draw(sk).line(seam,fill=200,width=int(D*0.07),joint="curve")
        sk=sk.filter(ImageFilter.GaussianBlur(D*0.01)); sk=ImageChops.multiply(sk,mask)
        img=Image.composite(Image.new("RGBA",(D,D),(238,240,214,255)),img,sk)
    elif overlay=='fungus':
        # powdery yellow -> reddish-brown mold blotches
        paste_blob(cx-rx*0.4,cy-ry*0.1,rx*0.55,(180,160,60),150)
        paste_blob(cx+rx*0.3,cy+ry*0.25,rx*0.45,(140,96,44),150)
        paste_blob(cx-rx*0.05,cy+ry*0.35,rx*0.3,(110,84,40),140)
        paste_blob(cx+rx*0.15,cy-ry*0.35,rx*0.22,(190,170,70),130)
        # speckle (rebind draw to current img)
        d=ImageDraw.Draw(img)
        for _ in range(40):
            a=random.uniform(0,2*math.pi); rr=random.uniform(0,0.85)
            px,py=cx+math.cos(a)*rx*rr,cy+math.sin(a)*ry*rr
            d.ellipse([px-1,py-1,px+2,py+2],fill=(150,120,50,120))
    elif overlay=='floater':
        # faded low-density: wash toward pale, lose contrast
        img=Image.composite(Image.new("RGBA",(D,D),(232,228,200,120)),img,mask)
    elif overlay=='shell':
        # malformed hollow 'ear': carve a concave scoop OUT of the bean so the card background
        # shows through (a shell is hollow) — leaving a curved shell wall with a shaded inner lip.
        scoop=Image.new("L",(D,D),0)
        ImageDraw.Draw(scoop).ellipse([cx-rx*0.15,cy-ry*0.72,cx+rx*1.25,cy+ry*0.72],fill=255)
        scoop=scoop.filter(ImageFilter.GaussianBlur(D*0.006))
        # shade the inner lip just inside the scoop before erasing (reads as a curved wall)
        lip=scoop.filter(ImageFilter.GaussianBlur(D*0.03))
        lip=ImageChops.subtract(lip,scoop); lip=ImageChops.multiply(lip,mask)
        img=Image.composite(Image.new("RGBA",(D,D),(*mul(base,0.45),255)),img,lip)
        # erase the scoop from alpha -> background shows through
        a=img.split()[3]; a=ImageChops.subtract(a,ImageChops.multiply(scoop,mask)); img.putalpha(a)
    elif overlay=='pale':
        # underdeveloped: pale light-brown, matte wash
        img=Image.composite(Image.new("RGBA",(D,D),(196,150,96,150)),img,mask)
    elif overlay=='quaker':
        # unripe bean stays pale beige/tan after roast
        img=Image.composite(Image.new("RGBA",(D,D),(214,180,120,180)),img,mask)
    elif overlay=='baked':
        # looks normal but flat/dull — very slight desaturating wash
        img=Image.composite(Image.new("RGBA",(D,D),(150,120,90,60)),img,mask)
    # roast-specific
    elif overlay=='scorch':
        paste_blob(cx-rx*0.45,cy-ry*0.1,rx*0.5,(22,14,6),210,blur=rx*0.15)
        paste_blob(cx+rx*0.3,cy+ry*0.3,rx*0.35,(22,14,6),200,blur=rx*0.12)
    elif overlay=='tip':
        paste_blob(cx,cy-ry*0.9,rx*0.4,(18,11,5),220,blur=rx*0.12)
        paste_blob(cx,cy+ry*0.9,rx*0.4,(18,11,5),220,blur=rx*0.12)
    elif overlay=='facing':
        half=Image.new("L",(D,D),0); ImageDraw.Draw(half).pieslice([cx-rx,cy-ry,cx+rx,cy+ry],90,270,fill=230)
        half=half.filter(ImageFilter.GaussianBlur(D*0.03)); half=ImageChops.multiply(half,mask)
        img=Image.composite(Image.new("RGBA",(D,D),(20,12,6,220)),img,half)
    elif overlay=='chip':
        # a missing chunk at the edge: fully erase a notch so the panel shows through,
        # with a thin pale 'exposed inner' rim on the BEAN side of the fresh break.
        notch=[(cx+rx*0.30,cy-ry*0.62),(cx+rx*1.30,cy-ry*0.62),(cx+rx*1.30,cy+ry*0.35),(cx+rx*0.72,cy+ry*0.20)]
        nm=Image.new("L",(D,D),0); ImageDraw.Draw(nm).polygon(notch,fill=255)
        # pale exposed-inner rim: draw a bright band just inside the break line first
        inner=(214,196,158) if kind=='roast' else (200,206,168)
        brk=Image.new("L",(D,D),0); ImageDraw.Draw(brk).line([notch[0],notch[3]],fill=220,width=int(D*0.045))
        brk=brk.filter(ImageFilter.GaussianBlur(D*0.006)); brk=ImageChops.multiply(brk,mask)
        img=Image.composite(Image.new("RGBA",(D,D),(*inner,255)),img,brk)
        # now erase the notch (full)
        a=img.split()[3]; a=ImageChops.subtract(a,ImageChops.multiply(nm,mask)); img.putalpha(a)
    elif overlay=='oil':
        # overdeveloped: dark + oily sheen patches
        img=Image.composite(Image.new("RGBA",(D,D),(30,18,10,140)),img,mask)
        for (ox,oy,orr) in [(-0.2,-0.2,0.5),(0.25,0.15,0.35),(0.05,-0.05,0.7)]:
            paste_blob(cx+ox*rx,cy+oy*ry,rx*orr,(255,240,220),60,blur=rx*0.3)

    # washes above cover the seam — redraw it so every bean keeps its S-curve center cut
    if overlay in ('sour','floater','pale','quaker','baked','oil'):
        draw_seam(strength=0.7 if overlay in ('pale','quaker','baked') else 0.85)

    # ---- top sheen: a TIGHT curved glint, not a soft fog (avoids the 'spraypaint' look) ----
    # matte defects get no glint; glossy/dark ones get a small bright streak following the bean curve.
    gloss = {'green':0.0,'roast':0.0}  # base amount by kind
    glint_alpha = 0
    if kind=='roast' and overlay in (None,'scorch','tip','chip','facing'): glint_alpha=60
    if overlay=='oil': glint_alpha=120           # overdeveloped is oily-shiny
    if kind=='green' and overlay in (None,'broken'): glint_alpha=34
    if overlay in ('immature','floater','pale','quaker','baked','sour','fungus','fullblack','partblack','shell'):
        glint_alpha=0                             # matte / not applicable
    if glint_alpha>0:
        sh=Image.new("L",(D,D),0); sd2=ImageDraw.Draw(sh)
        # a slim curved streak in the upper-left quadrant, angled along the bean's long axis
        streak=[(cx-rx*0.42,cy-ry*0.42),(cx-rx*0.18,cy-ry*0.30),(cx-rx*0.10,cy-ry*0.02),(cx-rx*0.30,cy-ry*0.06)]
        sd2.polygon(streak,fill=glint_alpha)
        sh=sh.filter(ImageFilter.GaussianBlur(D*0.012))   # tight blur, not D*0.03
        sh=ImageChops.multiply(sh,mask)
        img=Image.composite(Image.new("RGBA",(D,D),(255,252,244,255)),img,sh)

    return img

def gallery(fname, title, kind, base, cells):
    """cells: list of (label, sublabel, overlay, cat) ; 3x3 grid."""
    W,H = 760, 470
    im=Image.new("RGB",(W*SS,H*SS),PANEL); d=ImageDraw.Draw(im)
    s=SS
    d.rounded_rectangle([4*s,4*s,(W-4)*s,(H-4)*s],radius=14*s,outline=LINE,width=1*s)
    # intro line
    intro = ("Graders sort a 350g sample bean-by-bean. Cat 1 = severe (disqualifies specialty); Cat 2 = milder, by equivalence."
             if kind=='green' else
             "Same target color can hide very different roasts \u2014 many defects show on the bean, some only in the cup.")
    d.text((30*s,24*s), intro, font=font(11*s), fill=INK3)
    cols,rows=3,3; gx0,gy0=30,46; cw=(W-60)/cols; ch=(H-70)/rows
    D=int(78*s)
    for i,(label,sub,overlay,cat) in enumerate(cells):
        r,c=divmod(i,cols); cx=gx0+cw*c+cw/2; cy=gy0+ch*r+ch*0.40
        # cell card
        d.rounded_rectangle([(gx0+cw*c+6)*s,(gy0+ch*r+4)*s,(gx0+cw*c+cw-6)*s,(gy0+ch*r+ch-6)*s],
                            radius=10*s, outline=(58,46,32), width=1*s)
        bean=draw_bean(D, base, kind, overlay)
        im.paste(bean,(int(cx*s-D/2),int(cy*s-D/2)),bean)
        # labels
        d.text((cx*s,(cy+42)*s), label, font=font(12*s,True), fill=INK, anchor="mm")
        d.text((cx*s,(cy+58)*s), sub, font=font(9.5*s), fill=INK3, anchor="mm")
        if cat:
            col = CAT1 if cat=='1' else GOLD
            d.text(((gx0+cw*c+cw-14)*s,(gy0+ch*r+14)*s), f"CAT {cat}", font=font(8.5*s,True), fill=col, anchor="rm")
    # caption
    cap = ("A visual field guide to the common green-coffee defects and their SCA categories."
           if kind=='green' else
           "A visual field guide to the common roast defects.")
    d.text((30*s,(H-20)*s), cap, font=font(11*s), fill=INK3)
    im=im.resize((W,H), Image.LANCZOS)
    im.save(OUT/fname)
    print("wrote",(OUT/fname).name, im.size)

# ---- GREEN gallery ----
gallery("greendefects.png","Green defects","green",(102,128,92),[
    ("Healthy","even blue-green, dense",None,None),
    ("Full black","over-fermented / dead","fullblack","1"),
    ("Full sour","reddish-brown, over-fermented","sour","1"),
    ("Partial black","part of the bean blackened","partblack","2"),
    ("Insect damage","borer holes (broca)","insect","2"),
    ("Broken / chipped","cut, pale inner exposed","broken","2"),
    ("Immature","pale, thin \u2014 silverskin sticks","immature","2"),
    ("Shell / ear","malformed hollow shape","shell","2"),
    ("Floater / fungus","faded, low-density / mold","fungus","2"),
])

# ---- ROAST gallery ----
gallery("roastdefects.png","Roast defects","roast",(150,96,54),[
    ("Healthy","even color, matte-satin",None,None),
    ("Scorching","hot drum, flat-face burns","scorch",None),
    ("Tipping","too-fast heat, burnt tips","tip",None),
    ("Facing","stuck on drum, one side charred","facing",None),
    ("Chipping","2nd-crack pressure, chunk lost","chip",None),
    ("Underdeveloped","too fast \u2014 pale, matte","pale",None),
    ("Overdeveloped","too long \u2014 dark & oily","oil",None),
    ("Baked","temp stalled \u2014 looks fine!","baked",None),
    ("Quaker","unripe bean \u2014 stays pale","quaker",None),
])
