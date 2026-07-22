#!/usr/bin/env python3
"""Generate raster art for four diagrams: roasters, processing, milkdrinks, blend.
Shared soft-shaded bean helper (same look as gen_defects). All match the app's dark theme.
References: espresso glassware sizes (Roasty/Fluent/Perfect Daily Grind), processing
(washed/honey/natural), roaster architectures (drum/fluid-bed/hybrid)."""
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import numpy as np, pathlib, math, random

OUT=pathlib.Path(__file__).parent/"img_src"; OUT.mkdir(exist_ok=True)
SS=4
PANEL=(36,26,18); LINE=(74,60,44); INK=(240,230,216); INK3=(162,144,122)
GOLD=(201,163,78)

def font(sz,bold=False,italic=False):
    name="DejaVuSans-Bold.ttf" if bold else ("DejaVuSans-Oblique.ttf" if italic else "DejaVuSans.ttf")
    for p in ["/usr/share/fonts/truetype/dejavu/"+name,"/usr/share/fonts/dejavu/"+name]:
        if pathlib.Path(p).exists(): return ImageFont.truetype(p,sz)
    return ImageFont.load_default()
def mul(c,f): return tuple(max(0,min(255,int(x*f))) for x in c)

def draw_bean(D,base,kind='green',elong=1.0,straight_seam=False):
    """soft-shaded coffee seed, DxD RGBA, with center-cut valley + silverskin.
    elong>1 = more elongated (arabica); <1 = rounder (robusta).
    straight_seam=True gives robusta's straighter central cut."""
    img=Image.new("RGBA",(D,D),(0,0,0,0)); cx=cy=D/2
    rx,ry=D*0.32/max(1.0,elong)**0.4, D*0.42*elong**0.5
    m=Image.new("L",(D,D),0); md=ImageDraw.Draw(m)
    pts=[]
    for a in range(0,360,3):
        t=math.radians(a); yr=ry*(1.02 if math.sin(t)>0 else 0.98); xr=rx*(1+0.05*math.sin(t))
        pts.append((cx+xr*math.cos(t),cy+yr*math.sin(t)))
    md.polygon(pts,fill=255); m=m.filter(ImageFilter.GaussianBlur(D*0.006))
    yy,xx=np.mgrid[0:D,0:D].astype(np.float32)
    nx=(xx-(cx-rx*0.32))/(rx*1.5); ny=(yy-(cy-ry*0.3))/(ry*1.5); dist=np.sqrt(nx*nx+ny*ny)
    shade=np.clip(1-dist*0.5,0,1)
    lit=np.array(mul(base,1.28),np.float32); dk=np.array(mul(base,0.55),np.float32)
    body=lit[None,None,:]*shade[...,None]+dk[None,None,:]*(1-shade[...,None])
    tex=(np.random.rand(D,D).astype(np.float32)-0.5)*2*0.045
    body=np.clip(body*(1+tex[...,None]),0,255)
    img=Image.composite(Image.fromarray(body.astype(np.uint8),"RGB").convert("RGBA"),img,m)
    # AO rim
    rim=Image.new("L",(D,D),0); ImageDraw.Draw(rim).ellipse([cx-rx,cy-ry,cx+rx,cy+ry],outline=255,width=int(D*0.05))
    rim=rim.filter(ImageFilter.GaussianBlur(D*0.02)); rim=ImageChops.multiply(rim,m)
    img=Image.composite(Image.new("RGBA",(D,D),(*mul(base,0.4),150)),img,rim)
    # seam: arabica = wavy S; robusta = nearly straight
    amp = 0.04 if straight_seam else 0.16
    seam=[(cx+math.sin(i/40*math.pi*2.1)*rx*amp, cy-ry*0.82+i/40*ry*1.64) for i in range(41)]
    val=Image.new("L",(D,D),0); ImageDraw.Draw(val).line(seam,fill=255,width=int(D*0.10),joint="curve")
    val=val.filter(ImageFilter.GaussianBlur(D*0.02)); val=ImageChops.multiply(val,m)
    img=Image.composite(Image.new("RGBA",(D,D),(*mul(base,0.32),200)),img,val)
    ss=Image.new("L",(D,D),0); ImageDraw.Draw(ss).line(seam,fill=210,width=int(D*0.045),joint="curve")
    ss=ss.filter(ImageFilter.GaussianBlur(D*0.008)); ss=ImageChops.multiply(ss,m)
    img=Image.composite(Image.new("RGBA",(D,D),(222,226,196,255)),img,ss)
    # sheen
    sh=Image.new("L",(D,D),0); ImageDraw.Draw(sh).ellipse([cx-rx*0.55,cy-ry*0.6,cx-rx*0.08,cy-ry*0.12],fill=60)
    sh=sh.filter(ImageFilter.GaussianBlur(D*0.03)); sh=ImageChops.multiply(sh,m)
    img=Image.composite(Image.new("RGBA",(D,D),(255,255,255,255)),img,sh)
    return img

def card(d,x0,y0,x1,y1,s,outline=(58,46,32)):
    d.rounded_rectangle([x0*s,y0*s,x1*s,y1*s],radius=10*s,outline=outline,width=1*s)

def frame(W,H,s,intro=None):
    im=Image.new("RGB",(W*s,H*s),PANEL); d=ImageDraw.Draw(im)
    d.rounded_rectangle([4*s,4*s,(W-4)*s,(H-4)*s],radius=14*s,outline=LINE,width=1*s)
    if intro: d.text((30*s,24*s),intro,font=font(11*s),fill=INK3)
    return im,d

def finish(im,W,H,fname):
    # Render is at SS x; save at 2x device scale (not 1x) so text stays crisp on high-DPI screens.
    # The <img> is width:100%, so the browser scales the 2x asset down cleanly.
    im=im.resize((W*2,H*2),Image.LANCZOS); im.save(OUT/fname); print("wrote",fname,im.size)

# ============ 1. PROCESSING ============
def gen_processing():
    W,H,s=760,300,SS
    im,d=frame(W,H,s)
    cols=[("Washed","all fruit removed before drying","clean \u00b7 bright \u00b7 transparent",0,150),
          ("Honey","skin off, sticky mucilage left on","sweet \u00b7 rounded \u00b7 in-between",1,380),
          ("Natural","whole cherry dried on the bean","fruity \u00b7 heavy \u00b7 wild",2,610)]
    cy=140
    for name,sub,tag,fruit,cx in cols:
        d.text((cx*s,(50)*s),tag,font=font(11*s,italic=True),fill=INK3,anchor="mm")
        # fruit coat
        if fruit==2:  # natural: dried cherry
            d.ellipse([(cx-52)*s,(cy-60)*s,(cx+52)*s,(cy+60)*s],fill=(110,40,30))
            d.ellipse([(cx-48)*s,(cy-56)*s,(cx+48)*s,(cy+56)*s],fill=(150,52,40))
            d.ellipse([(cx-14)*s,(cy-40)*s,(cx-2)*s,(cy-28)*s],fill=(184,74,56))  # sheen
        elif fruit==1:  # honey: sticky gold coat
            d.ellipse([(cx-42)*s,(cy-48)*s,(cx+42)*s,(cy+48)*s],fill=(207,150,66))
            d.ellipse([(cx-40)*s,(cy-46)*s,(cx+40)*s,(cy+46)*s],fill=(224,180,110))
        # the seed
        D=int((64 if fruit==2 else 70)*s)
        bean=draw_bean(D,(127,148,100),'green')
        im.paste(bean,(int(cx*s-D/2),int(cy*s-D/2)),bean)
        d=ImageDraw.Draw(im)
        d.text((cx*s,(cy+72)*s),name,font=font(15*s,True),fill=(GOLD if fruit else (154,175,110)),anchor="mm")
        d.text((cx*s,(cy+92)*s),sub,font=font(11*s),fill=INK3,anchor="mm")
    dd=ImageDraw.Draw(im)
    dd.text((30*s,(H-20)*s),"The more fruit that stays on the bean during drying, the sweeter and heavier the cup \u2014 and the higher the drying-defect risk.",font=font(10.5*s),fill=INK3)
    finish(im,W,H,"processing.png")

# ============ 2. ROASTERS ============
def gen_roasters():
    W,H,s=760,300,SS
    im,d=frame(W,H,s)
    accent=(176,123,62)
    items=[("Drum","rotating metal drum over heat","body \u00b7 dark roasts \u00b7 workhorse",150,"drum"),
           ("Fluid-bed","beans levitated on hot air","fast \u00b7 clean \u00b7 bright roasts",380,"fluid"),
           ("Hybrid","recirculated air + drum","blends both approaches",610,"hybrid")]
    cy=118
    for name,sub,tag,cx,kind in items:
        col=(201,163,78) if kind=='fluid' else (176,123,62) if kind=='drum' else (150,120,70)
        if kind in ('drum','hybrid'):
            R=40
            d.ellipse([(cx-R)*s,(cy-R)*s,(cx+R)*s,(cy+R)*s],outline=col,width=int(2.6*s))
            d.ellipse([(cx-R*0.62)*s,(cy-R*0.62)*s,(cx+R*0.62)*s,(cy+R*0.62)*s],outline=mul(col,0.7),width=int(1.5*s))
            d.ellipse([(cx-3)*s,(cy-3)*s,(cx+3)*s,(cy+3)*s],fill=col)
            # hopper on top
            d.polygon([((cx-16)*s,(cy-R-16)*s),((cx+16)*s,(cy-R-16)*s),((cx+9)*s,(cy-R+1)*s),((cx-9)*s,(cy-R+1)*s)],outline=col,width=int(2*s))
            # legs
            d.line([(cx-26)*s,(cy+R-4)*s,(cx-30)*s,(cy+R+18)*s],fill=col,width=int(2.2*s))
            d.line([(cx+26)*s,(cy+R-4)*s,(cx+30)*s,(cy+R+18)*s],fill=col,width=int(2.2*s))
            if kind=='drum':
                # rotation cue: arc + arrowhead inside the door ring
                d.arc([(cx-14)*s,(cy-14)*s,(cx+14)*s,(cy+14)*s],-60,150,fill=mul(col,0.85),width=int(1.6*s))
                ex,ey=cx+14*math.cos(math.radians(150)),cy+14*math.sin(math.radians(150))
                d.polygon([((ex)*s,(ey)*s),((ex+6)*s,(ey-2)*s),((ex+1)*s,(ey+6)*s)],fill=mul(col,0.85))
                # real flames under the drum
                for i in (-1,0,1):
                    fx=cx+i*11
                    d.pieslice([(fx-4)*s,(cy+R+2)*s,(fx+4)*s,(cy+R+14)*s],0,180,fill=(224,120,60))
                    d.ellipse([(fx-2.5)*s,(cy+R+5)*s,(fx+2.5)*s,(cy+R+13)*s],fill=(240,180,90))
            else:  # hybrid: a clean external recirculation loop — air exits top, loops right, re-enters the side
                duct=(224,168,96); pw=int(2.6*s)
                tx=cx+R+22   # right edge of the loop
                topY=cy-R-16
                # up from top-right of drum
                d.line([(cx+R*0.45)*s,(cy-R+4)*s,(cx+R*0.45)*s,topY*s],fill=duct,width=pw)
                # arrow along the top showing flow direction (left->right)
                d.line([(cx+R*0.45)*s,topY*s,tx*s,topY*s],fill=duct,width=pw)
                d.polygon([((tx)*s,(topY)*s),((tx-8)*s,(topY-4)*s),((tx-8)*s,(topY+4)*s)],fill=duct)
                # down the right side
                d.line([tx*s,topY*s,tx*s,cy*s],fill=duct,width=pw)
                # back into the drum side with an arrowhead pointing IN
                d.line([tx*s,cy*s,(cx+R+2)*s,cy*s],fill=duct,width=pw)
                d.polygon([((cx+R-4)*s,(cy)*s),((cx+R+6)*s,(cy-5)*s),((cx+R+6)*s,(cy+5)*s)],fill=duct)
                d.text((tx*s,(topY-10)*s),"air",font=font(9*s,True),fill=duct,anchor="mm")
        else:  # fluid-bed
            d.polygon([((cx-22)*s,(cy-40)*s),((cx+22)*s,(cy-40)*s),((cx+15)*s,(cy+4)*s),((cx-15)*s,(cy+4)*s)],outline=col,width=int(2.4*s))
            d.line([(cx-22)*s,(cy-40)*s,(cx+22)*s,(cy-40)*s],fill=col,width=int(2.4*s))
            for hx,hy in [(-8,-30),(6,-34),(12,-22),(-3,-18),(8,-12),(-11,-11),(0,-26)]:
                d.ellipse([(cx+hx-4)*s,(cy+hy-3)*s,(cx+hx+4)*s,(cy+hy+3)*s],fill=(120,80,44))
            for i in (-1,0,1):
                jx=cx+i*10
                d.line([(jx)*s,(cy+2)*s,(jx)*s,(cy-32)*s],fill=(224,168,96),width=int(1.4*s))
                d.polygon([((jx)*s,(cy-34)*s),((jx-3)*s,(cy-28)*s),((jx+3)*s,(cy-28)*s)],fill=(224,168,96))
            d.rounded_rectangle([(cx-22)*s,(cy+4)*s,(cx+22)*s,(cy+28)*s],radius=5*s,outline=col,width=int(2.2*s))
            d.line([(cx-30)*s,(cy+32)*s,(cx+30)*s,(cy+32)*s],fill=col,width=int(2*s))
        d.text((cx*s,(cy+80)*s),name,font=font(15*s,True),fill=col,anchor="mm")
        d.text((cx*s,(cy+100)*s),sub,font=font(11*s),fill=INK,anchor="mm")
        d.text((cx*s,(cy+116)*s),tag,font=font(10*s),fill=INK3,anchor="mm")
    d.text((30*s,(H-20)*s),"The three main roaster architectures and what each is good at.",font=font(11*s),fill=INK3)
    finish(im,W,H,"roasters.png")

# ============ 3. MILK DRINKS ============
def gen_milkdrinks():
    W,H,s=760,320,SS
    im,d=frame(W,H,s)
    ESP=(64,36,14); MILK=(226,210,182); FOAM=(250,246,238); GLASS=(198,186,164); SAUCER=(150,136,112)
    drinks=[("Macchiato",58,.70,.0,.30,"espcup"),("Cortado",66,.5,.5,.0,"gib"),
            ("Flat White",78,.34,.56,.10,"cup"),("Cappuccino",88,.30,.30,.40,"bowl"),
            ("Latte",96,.22,.66,.12,"latte")]
    baseY=196; gap=(W-40)/5
    for i,(name,h,ef,mf,ff,vessel) in enumerate(drinks):
        cx=20+gap*i+gap/2; top=baseY-h
        rT,rB={"espcup":(18,12),"gib":(21,18),"cup":(27,20),"bowl":(30,21),"latte":(26,20)}[vessel]
        # ---- vessel silhouette as a smooth path (curved sides for cups, straight for glass) ----
        curve = vessel in ("espcup","cup","bowl")   # latte is a straight-ish tall glass
        # build left & right wall point lists
        n=10; leftpts=[]; rightpts=[]
        for k in range(n+1):
            t=k/n; y=top+(baseY-top)*t
            if curve:
                belly = math.sin(t*math.pi)*(5 if vessel in("cup","bowl") else 1.5)  # rounder cups
                w=rT+(rB-rT)*t - belly
            else:
                w=rT+(rB-rT)*t
            leftpts.append((cx-w,y)); rightpts.append((cx+w,y))
        wallpath=leftpts+rightpts[::-1]
        Dd=W*s; clip=Image.new("L",(Dd,H*s),0)
        ImageDraw.Draw(clip).polygon([(x*s,y*s) for x,y in wallpath],fill=255)
        # ---- fills ----
        eH=h*ef; mH=h*mf; fH=h*ff
        fillimg=Image.new("RGBA",(Dd,H*s),(0,0,0,0)); fd=ImageDraw.Draw(fillimg)
        fd.rectangle([(cx-40)*s,(baseY-eH)*s,(cx+40)*s,(baseY+2)*s],fill=(*ESP,255))
        if mH>0: fd.rectangle([(cx-40)*s,(baseY-eH-mH)*s,(cx+40)*s,(baseY-eH)*s],fill=(*MILK,255))
        if fH>0: fd.rectangle([(cx-40)*s,(baseY-eH-mH-fH)*s,(cx+40)*s,(baseY-eH-mH)*s],fill=(*FOAM,255))
        if mH>0: fd.rectangle([(cx-40)*s,(baseY-eH-1.5)*s,(cx+40)*s,(baseY-eH+1.5)*s],fill=(96,56,26,200)) # crema line
        # thin line between milk and foam so the two whites separate
        if fH>0 and mH>0: fd.rectangle([(cx-40)*s,(baseY-eH-mH-1)*s,(cx+40)*s,(baseY-eH-mH+1)*s],fill=(198,182,150,160))
        fillimg=Image.composite(fillimg,Image.new("RGBA",(Dd,H*s),(0,0,0,0)),clip); im.paste(fillimg,(0,0),fillimg)
        d=ImageDraw.Draw(im)
        # cappuccino foam dome above the rim
        if vessel=="bowl":
            d.pieslice([(cx-rT+4)*s,(top-14)*s,(cx+rT-4)*s,(top+10)*s],180,360,fill=FOAM)
            d.arc([(cx-rT+4)*s,(top-14)*s,(cx+rT-4)*s,(top+10)*s],180,360,fill=GLASS,width=int(1.2*s))
        # ---- handle on the RIGHT (ceramic cups only; latte + cortado are glasses) ----
        if vessel in ("espcup","cup","bowl"):
            hy=top+h*0.34; hh=h*0.42; hw=(15 if vessel=="bowl" else 12)
            d.arc([(cx+rT-hw*0.3)*s,hy*s,(cx+rT+hw)*s,(hy+hh)*s],-78,88,fill=GLASS,width=int(3.5*s))
        # ---- vessel wall stroke (follow the silhouette) ----
        d.line([(p[0]*s,p[1]*s) for p in leftpts],fill=GLASS,width=int(1.8*s),joint="curve")
        d.line([(p[0]*s,p[1]*s) for p in rightpts],fill=GLASS,width=int(1.8*s),joint="curve")
        # rim ellipse
        d.ellipse([(cx-rT)*s,(top-rT*0.22)*s,(cx+rT)*s,(top+rT*0.22)*s],outline=GLASS,width=int(1.6*s))
        # ---- base: a closed rounded bottom only (NO saucer half-circle) ----
        # draw a shallow bottom curve so the vessel reads as closed
        d.arc([(cx-rB)*s,(baseY-6)*s,(cx+rB)*s,(baseY+6)*s],10,170,fill=GLASS,width=int(1.8*s))
        if vessel=="gib":
            d.line([(cx-rB+2)*s,(baseY-2)*s,(cx+rB-2)*s,(baseY-2)*s],fill=mul(GLASS,0.7),width=int(1*s)) # glass base band
        d.text((cx*s,(baseY+30)*s),name,font=font(12*s,True),fill=INK,anchor="mm")
    # ---- legend: moved DOWN to its own row, clear of the drink names ----
    ly=baseY+64
    items=[("espresso",ESP),("steamed milk",MILK),("foam",FOAM)]
    # center the legend group
    total=sum(len(l)*6.4+40 for l,_ in items); lx=(W-total)/2
    for lab,col in items:
        d.rounded_rectangle([lx*s,(ly-6)*s,(lx+12)*s,(ly+6)*s],radius=2*s,fill=col,outline=SAUCER,width=int(0.5*s))
        d.text(((lx+17)*s,ly*s),lab,font=font(11*s),fill=INK3,anchor="lm")
        lx+=len(lab)*6.4+40
    d.text((30*s,(H-18)*s),"The same espresso shot, in the real glassware for each drink \u2014 milk and foam in different proportions.",font=font(10.5*s),fill=INK3)
    finish(im,W,H,"milkdrinks.png")

# ============ 4. BLEND ============
def gen_blend():
    W,H,s=760,220,SS
    im,d=frame(W,H,s)
    comps=[("Base","body & sweetness",(138,90,52),60),
           ("Bright","acidity & lift",(201,163,78),110),
           ("Accent","aromatics",(224,134,74),160)]
    cupx=590; cupy=110
    for name,sub,col,cy in comps:
        D=int(40*s); bean=draw_bean(D,mul(col,1.0) if name!="Base" else (150,110,70),'roast')
        # tint the bean toward its role color for distinction
        im.paste(bean,(int(70*s-D/2),int(cy*s-D/2)),bean)
        d=ImageDraw.Draw(im)
        d.text((100*s,(cy-6)*s),name,font=font(13.5*s,True),fill=col,anchor="lm")
        d.text((100*s,(cy+12)*s),sub,font=font(11*s),fill=INK3,anchor="lm")
        # arrow to cup
        d.line([(200)*s,cy*s,(cupx-46)*s,cupy*s],fill=(*col,140),width=int(2*s))
    # ---- the blend: a single bean whose color is a MIX of the three components ----
    Dd=int(64*s)
    # average the three component colors for the blend base, then draw a bean and overlay
    # soft patches of each component color so it reads as a genuine blend.
    mixbase=tuple(int(sum(c[2][k] for c in comps)/3) for k in range(3))
    blendbean=draw_bean(Dd,mixbase,'roast')
    dd=ImageDraw.Draw(blendbean)
    # soft color patches from each component, blurred, clipped to the bean
    patch=Image.new("RGBA",(Dd,Dd),(0,0,0,0)); pd=ImageDraw.Draw(patch)
    spots=[((138,90,52),Dd*0.32,Dd*0.36),((201,163,78),Dd*0.64,Dd*0.5),((224,134,74),Dd*0.44,Dd*0.66)]
    for col,px,py in spots:
        pd.ellipse([px-Dd*0.2,py-Dd*0.2,px+Dd*0.2,py+Dd*0.2],fill=(*col,120))
    patch=patch.filter(ImageFilter.GaussianBlur(Dd*0.06))
    # clip patch to bean alpha
    patch.putalpha(ImageChops.multiply(patch.split()[3],blendbean.split()[3]))
    blendbean.alpha_composite(patch)
    im.paste(blendbean,(int(cupx*s-Dd/2),int(cupy*s-Dd/2)),blendbean)
    d=ImageDraw.Draw(im)
    d.text((cupx*s,(cupy+50)*s),"The blend",font=font(14*s,True),fill=INK,anchor="mm")
    d.text((30*s,(H-16)*s),"A blend is built from components that each play a role \u2014 dial the ratio by cupping them together.",font=font(11*s),fill=INK3)
    finish(im,W,H,"blend.png")

def gen_teacoffee():
    W,H,s=760,300,SS
    im,d=frame(W,H,s)
    cyimg=110
    # COFFEE bean (left)
    Dd=int(80*s); bean=draw_bean(Dd,(150,96,54),'roast')
    im.paste(bean,(int(230*s-Dd/2),int(cyimg*s-Dd/2)),bean)
    # TEA leaf (right): botanically-shaped Camellia sinensis leaf — elliptic (~2.3:1),
    # pointed tip, finely SERRATED margin, curved midrib + 7 pairs of arching lateral veins, short stalk.
    lx,ly=535,cyimg-6
    LEN=92; WID=24          # slightly smaller and raised so it clears the TEA label below
    tipY=ly-LEN*0.52; baseY=ly+LEN*0.48
    leaf=Image.new("RGBA",(W*s,H*s),(0,0,0,0)); ld=ImageDraw.Draw(leaf)
    import math as _m
    def half(sign):
        pts=[]
        N=64
        for i in range(N+1):
            t=i/N                       # 0 at base -> 1 at tip
            yy=baseY+(tipY-baseY)*t
            # elliptic width profile, skewed so the widest point is slightly below middle;
            # taper to sharp points at tip and base
            base_w = _m.sin(min(1,t*1.04)*_m.pi)**0.72   # sharper taper at tip & base
            w = WID*base_w
            # fine serration: many small forward-pointing teeth along the margin
            if 0.06<t<0.94:
                w += (_m.sin(t*72)*0.5+0.5)* (WID*0.09) * (0.5+0.5*base_w)
            pts.append(((lx+sign*w)*s, yy*s))
        return pts
    outline=half(+1)+half(-1)[::-1]
    ld.polygon(outline,fill=(86,132,64,255))
    leaf=leaf.filter(ImageFilter.GaussianBlur(0.8))
    ld=ImageDraw.Draw(leaf)
    # midrib: a gently curved central vein from stalk to tip
    rib=[]
    for i in range(41):
        t=i/40; yy=baseY+(tipY-baseY)*t
        bow=_m.sin(t*_m.pi)*4      # slight bow
        rib.append(((lx+bow)*s,yy*s))
    ld.line(rib,fill=(58,96,46),width=int(1.8*s),joint="curve")
    # 7 pairs of lateral veins, arching upward toward the tip, stopping short of the margin
    for k in range(1,8):
        t=0.12+k*0.10
        yy=baseY+(tipY-baseY)*t
        bx=lx+_m.sin(t*_m.pi)*4
        wv=WID*_m.sin(min(1,t*1.04)*_m.pi)**0.72
        for sign in (+1,-1):
            ex=lx+sign*wv*0.72; ey=yy-LEN*0.05
            midx=lx+sign*wv*0.4; midy=yy+2
            ld.line([(bx*s,yy*s),(midx*s,midy*s),(ex*s,ey*s)],fill=(64,104,50),width=int(1.0*s),joint="curve")
    # short stalk (petiole)
    ld.line([(lx*s,baseY*s),((lx-2)*s,(baseY+10)*s)],fill=(96,120,70),width=int(2.2*s))
    im.alpha_composite(leaf) if im.mode=='RGBA' else im.paste(Image.alpha_composite(im.convert('RGBA'),leaf).convert('RGB'),(0,0))
    d=ImageDraw.Draw(im)
    # vs divider
    d.line([(380)*s,70*s,(380)*s,150*s],fill=(120,104,80),width=int(1*s))
    d.ellipse([(365)*s,95*s,(395)*s,125*s],fill=PANEL,outline=(120,104,80),width=int(1*s))
    d.text((380*s,110*s),"vs",font=font(10*s,italic=True),fill=INK3,anchor="mm")
    # columns
    cols=[("COFFEE",(176,123,62),230,["Roasted SEED of Coffea fruit","~95 mg caffeine / cup","Bolder, heavier, immediate","Morning and productivity"]),
          ("TEA",(122,154,106),530,["Dried LEAF of Camellia sinensis","~30\u201350 mg caffeine / cup","Lighter, L-theanine = steady","All-day and calm"])]
    for name,col,cx,lines in cols:
        d.text((cx*s,168*s),name,font=font(17*s,True),fill=col,anchor="mm")
        for j,ln in enumerate(lines):
            d.text((cx*s,(190+j*22)*s),ln,font=font(11*s),fill=INK,anchor="mm")
    d.text((30*s,(H-16)*s),"The world\u2019s two great caffeinated drinks, compared.",font=font(11*s),fill=INK3)
    finish(im,W,H,"teacoffee.png")

def gen_decafmethods():
    W,H,s=760,280,SS
    im,d=frame(W,H,s)
    methods=[("Solvent","MC or EA","EA = \u2018sugarcane\u2019, sweet",(201,163,78),150),
             ("Swiss Water","water + carbon","chemical-free, ~99.9%",(122,148,180),380),
             ("CO2","supercritical CO2","commercial scale",(150,175,110),610)]
    cyimg=110
    for name,sub,note,ring,cx in methods:
        # colored process ring
        d.ellipse([(cx-46)*s,(cyimg-46)*s,(cx+46)*s,(cyimg+46)*s],outline=ring,width=int(2.4*s))
        # 3 small dots on the ring (process nodes)
        for a in (30,150,270):
            dx=cx+42*math.cos(math.radians(a)); dy=cyimg+42*math.sin(math.radians(a))
            d.ellipse([(dx-3)*s,(dy-3)*s,(dx+3)*s,(dy+3)*s],fill=ring)
        # green bean in the center (decaf is done to GREEN coffee)
        Dd=int(58*s); bean=draw_bean(Dd,(127,148,100),'green')
        im.paste(bean,(int(cx*s-Dd/2),int(cyimg*s-Dd/2)),bean)
        d=ImageDraw.Draw(im)
        d.text((cx*s,(cyimg+66)*s),name,font=font(15*s,True),fill=ring,anchor="mm")
        d.text((cx*s,(cyimg+86)*s),sub,font=font(11*s,True),fill=INK,anchor="mm")
        d.text((cx*s,(cyimg+104)*s),note,font=font(10*s),fill=INK3,anchor="mm")
    d.text((W/2*s,(H-40)*s),"All done to green beans before roasting \u00b7 all target ~97\u201399.9% caffeine removal",font=font(10.5*s,italic=True),fill=INK3,anchor="mm")
    d.text((30*s,(H-18)*s),"Three ways to pull caffeine out of green coffee.",font=font(11*s),fill=INK3)
    finish(im,W,H,"decafmethods.png")

def gen_arabica_robusta():
    W,H,s=760,340,SS
    im,d=frame(W,H,s)
    ARA=(122,150,100); ROB=(168,158,96)
    axc=380
    beanY=88
    Da=int(96*s); ba=draw_bean(Da,(118,146,96),'green',elong=1.35,straight_seam=False)
    im.paste(ba,(int(200*s-Da/2),int(beanY*s-Da/2)),ba)
    Dr=int(74*s); br=draw_bean(Dr,(150,148,96),'green',elong=0.8,straight_seam=True)
    im.paste(br,(int(560*s-Dr/2),int(beanY*s-Dr/2)),br)
    d=ImageDraw.Draw(im)
    d.text((200*s,(beanY+62)*s),"ARABICA",font=font(16*s,True),fill=ARA,anchor="mm")
    d.text((200*s,(beanY+80)*s),"Coffea arabica",font=font(10*s,italic=True),fill=INK3,anchor="mm")
    d.text((560*s,(beanY+62)*s),"ROBUSTA",font=font(16*s,True),fill=ROB,anchor="mm")
    d.text((560*s,(beanY+80)*s),"Coffea canephora",font=font(10*s,italic=True),fill=INK3,anchor="mm")
    d.line([(axc)*s,52*s,(axc)*s,188*s],fill=(90,74,54),width=int(1*s))
    d.ellipse([(axc-15)*s,105*s,(axc+15)*s,135*s],fill=PANEL,outline=(120,104,80),width=int(1*s))
    d.text((axc*s,120*s),"vs",font=font(10*s,italic=True),fill=INK3,anchor="mm")
    rows=[("Caffeine","~1.2\u20131.5%","~2.2\u20132.7%"),
          ("Chromosomes","44 (tetraploid)","22 (diploid)"),
          ("Bean shape","larger, oval, curved crease","smaller, round, straight crease"),
          ("Sugar & lipid","high \u2014 sweeter, more body","lower \u2014 flatter"),
          ("Grows at","~600\u20132000 m, cool highlands","~0\u2013800 m, hot lowlands"),
          ("Hardiness","delicate, disease-prone","hardy, disease-resistant"),
          ("Cup","sweet, complex, bright","bold, bitter, earthy"),
          ("World crop","~60\u201370%","~30\u201340%")]
    y0=204; rh=15
    for i,(lab,a,b) in enumerate(rows):
        yy=y0+i*rh
        if i%2==0: d.rectangle([30*s,(yy-6)*s,(W-30)*s,(yy+7)*s],fill=(30,22,15))
        d.text((axc*s,yy*s),lab,font=font(9*s,True),fill=(201,180,150),anchor="mm")
        d.text((210*s,yy*s),a,font=font(9*s),fill=ARA,anchor="mm")
        d.text((558*s,yy*s),b,font=font(9*s),fill=ROB,anchor="mm")
    d.text((30*s,(H-14)*s),"Two species, very different cups \u2014 caffeine, chemistry, and where they grow all track together.",font=font(10*s),fill=INK3)
    finish(im,W,H,"arabica_robusta.png")

def gen_cupping():
    W,H,s=760,300,SS
    im,d=frame(W,H,s)
    ACC=(201,163,78)
    d.text((30*s,26*s),"The SCA protocol: 8.25 g coffee : 150 ml water (1:18) \u00b7 93\u00b0C \u00b7 one 4-minute steep, tasted as it cools.",font=font(10.5*s),fill=INK3)
    steps=[("1","Grind & smell","dry fragrance,\nwithin 15 min","grind"),
           ("2","Pour","93\u00b0C water,\nstart the timer","pour"),
           ("3","Steep","4 min \u2014 a crust\nof grounds forms","steep"),
           ("4","Break the crust","3 stirs, nose in \u2014\nthe aroma burst","break"),
           ("5","Skim","lift off foam\n& floating grounds","skim"),
           ("6","Slurp & score","taste ~70\u00b0C, then\nas it cools","taste")]
    n=len(steps); gap=(W-40)/n; cy=118
    for i,(num,title,sub,kind) in enumerate(steps):
        cx=20+gap*i+gap/2
        cupw=26; cuph=30; top=cy-cuph/2
        d.line([(cx-cupw/2)*s,top*s,(cx-cupw/2+3)*s,(top+cuph)*s],fill=(198,186,164),width=int(1.8*s))
        d.line([(cx+cupw/2)*s,top*s,(cx+cupw/2-3)*s,(top+cuph)*s],fill=(198,186,164),width=int(1.8*s))
        d.arc([(cx-cupw/2+3)*s,(top+cuph-6)*s,(cx+cupw/2-3)*s,(top+cuph+4)*s],10,170,fill=(198,186,164),width=int(1.8*s))
        d.ellipse([(cx-cupw/2)*s,(top-cupw*0.16)*s,(cx+cupw/2)*s,(top+cupw*0.16)*s],outline=(198,186,164),width=int(1.5*s))
        if kind=='grind':
            for gx,gy in [(-6,2),(0,0),(6,2),(-3,4),(3,4)]:
                d.ellipse([(cx+gx-3)*s,(top+8+gy)*s,(cx+gx+3)*s,(top+14+gy)*s],fill=(96,60,30))
        elif kind=='pour':
            d.rectangle([(cx-cupw/2+3)*s,(top+10)*s,(cx+cupw/2-3)*s,(top+cuph-3)*s],fill=(80,50,26))
            d.line([(cx)*s,(top-14)*s,(cx)*s,(top)*s],fill=(150,180,200),width=int(2*s))
        elif kind=='steep':
            d.rectangle([(cx-cupw/2+3)*s,(top+6)*s,(cx+cupw/2-3)*s,(top+cuph-3)*s],fill=(80,50,26))
            d.ellipse([(cx-cupw/2+2)*s,(top+2)*s,(cx+cupw/2-2)*s,(top+10)*s],fill=(120,80,44))
        elif kind=='break':
            d.rectangle([(cx-cupw/2+3)*s,(top+6)*s,(cx+cupw/2-3)*s,(top+cuph-3)*s],fill=(80,50,26))
            for wx in (-5,0,5):
                d.arc([(cx+wx-3)*s,(top-12)*s,(cx+wx+3)*s,(top-2)*s],200,340,fill=(150,130,100),width=int(1.2*s))
            d.line([(cx+10)*s,(top-6)*s,(cx+2)*s,(top+8)*s],fill=(198,186,164),width=int(1.6*s))
        elif kind=='skim':
            d.rectangle([(cx-cupw/2+3)*s,(top+8)*s,(cx+cupw/2-3)*s,(top+cuph-3)*s],fill=(84,52,28))
            d.line([(cx-12)*s,(top+2)*s,(cx-2)*s,(top+8)*s],fill=(198,186,164),width=int(1.6*s))
            d.line([(cx+12)*s,(top+2)*s,(cx+2)*s,(top+8)*s],fill=(198,186,164),width=int(1.6*s))
        else:
            d.rectangle([(cx-cupw/2+3)*s,(top+8)*s,(cx+cupw/2-3)*s,(top+cuph-3)*s],fill=(84,52,28))
            d.line([(cx+6)*s,(top+12)*s,(cx+16)*s,(top+2)*s],fill=(198,186,164),width=int(1.8*s))
            d.ellipse([(cx+14)*s,(top-1)*s,(cx+20)*s,(top+5)*s],outline=(198,186,164),width=int(1.4*s))
        d.ellipse([(cx-cupw/2-10)*s,(top-8)*s,(cx-cupw/2+2)*s,(top+4)*s],fill=PANEL,outline=ACC,width=int(1.2*s))
        d.text(((cx-cupw/2-4)*s,(top-2)*s),num,font=font(8.5*s,True),fill=INK,anchor="mm")
        d.text((cx*s,(cy+30)*s),title,font=font(11*s,True),fill=ACC,anchor="mm")
        for j,ln in enumerate(sub.split("\n")):
            d.text((cx*s,(cy+46+j*13)*s),ln,font=font(8.5*s),fill=INK3,anchor="mm")
        if i<n-1:
            d.line([(cx+cupw/2+8)*s,cy*s,(cx+gap-cupw/2-8)*s,cy*s],fill=(120,104,80),width=int(1.4*s))
    d.text((30*s,(H-16)*s),"Five bowls per lot check consistency; the rigid recipe means any difference you taste is the coffee, not the brew.",font=font(10*s),fill=INK3)
    finish(im,W,H,"cupping.png")

def gen_qcloop():
    W,H,s=760,300,SS
    im,d=frame(W,H,s)
    d.text((30*s,26*s),"Roasting isn't done when the beans cool. The cup decides, and the curve gets adjusted until they agree.",font=font(10.5*s),fill=INK3)
    nodes=[("ROAST","run the batch\nto the target curve",(176,123,62),190,108),
           ("CUP","taste it blind\nagainst standard",(201,163,78),570,108),
           ("COMPARE","score vs a\nreference cup",(122,150,180),570,208),
           ("ADJUST","tweak the next\nroast's curve",(150,175,110),190,208)]
    rw,rh=150,54
    for name,sub,col,cx,cy in nodes:
        d.rounded_rectangle([(cx-rw/2)*s,(cy-rh/2)*s,(cx+rw/2)*s,(cy+rh/2)*s],radius=9*s,fill=(30,22,15),outline=col,width=int(1.6*s))
        d.rectangle([(cx-rw/2)*s,(cy-rh/2)*s,(cx+rw/2)*s,(cy-rh/2+4)*s],fill=col)
        d.text((cx*s,(cy-8)*s),name,font=font(13*s,True),fill=col,anchor="mm")
        for j,ln in enumerate(sub.split("\n")):
            d.text((cx*s,(cy+6+j*12)*s),ln,font=font(9*s),fill=INK3,anchor="mm")
    def arr(x1,y1,x2,y2):
        d.line([x1*s,y1*s,x2*s,y2*s],fill=(150,130,100),width=int(1.8*s))
        ang=math.atan2(y2-y1,x2-x1)
        # solid triangular arrowhead at the destination end
        L,Wd=13,5
        tipx,tipy=x2,y2
        bx,by=x2-L*math.cos(ang),y2-L*math.sin(ang)
        lx,ly=bx-Wd*math.sin(ang),by+Wd*math.cos(ang)
        rx,ry=bx+Wd*math.sin(ang),by-Wd*math.cos(ang)
        d.polygon([(tipx*s,tipy*s),(lx*s,ly*s),(rx*s,ry*s)],fill=(150,130,100))
    # arrows connect box EDGES at matching centers, with a small gap before the arrowhead.
    gap=6
    # ROAST(190,108) -> CUP(570,108): along y=108, from right edge of ROAST to left edge of CUP
    arr(190+rw/2+gap,108, 570-rw/2-gap,108)
    # CUP(570,108) -> COMPARE(570,208): along x=570, top box bottom to bottom box top
    arr(570,108+rh/2+gap, 570,208-rh/2-gap)
    # COMPARE(570,208) -> ADJUST(190,208): along y=208, right to left
    arr(570-rw/2-gap,208, 190+rw/2+gap,208)
    # ADJUST(190,208) -> ROAST(190,108): along x=190, bottom box top to top box bottom
    arr(190,208-rh/2-gap, 190,108+rh/2+gap)
    d.multiline_text((380*s,158*s),"repeat every\nbatch",font=font(9.5*s,italic=True),fill=INK3,anchor="mm",align="center")
    d.text((30*s,(H-16)*s),"Cup what you ship, cup against a reference, and feed what you taste back into the roast log.",font=font(10*s),fill=INK3)
    finish(im,W,H,"qcloop.png")

def gen_roastchem():
    W,H,s=760,320,SS
    im,d=frame(W,H,s)
    # temperature axis (x) with overlapping reaction bands (grounded in refs)
    x0,x1=70,700; ay=250
    tmin,tmax=90,230
    def tx(t): return x0+(x1-x0)*(t-tmin)/(tmax-tmin)
    # axis
    d.line([x0*s,ay*s,x1*s,ay*s],fill=(120,104,80),width=int(1.4*s))
    for t in range(100,231,20):
        d.line([tx(t)*s,ay*s,tx(t)*s,(ay+5)*s],fill=(120,104,80),width=int(1*s))
        d.text((tx(t)*s,(ay+16)*s),f"{t}\u00b0C",font=font(9*s),fill=INK3,anchor="mm")
    # bean color strip along the axis (green->yellow->brown->dark)
    for i in range(120):
        t=tmin+(tmax-tmin)*i/120; xx=tx(t)
        if t<150: c=(120-int((t-90)/60*30),140,80)          # green->yellow
        elif t<175: c=(150,120,70)                            # tan
        elif t<200: c=(120,80,44)                             # brown
        else: c=(80,50,28)                                    # dark
        d.line([xx*s,(ay-8)*s,xx*s,(ay-2)*s],fill=c,width=int((x1-x0)/120*s)+s)
    # reaction bands (label, tStart, tEnd, y, color)
    bands=[("Drying \u2014 water evaporates, green \u2192 yellow",90,150,70,(150,160,90)),
           ("Maillard \u2014 amino acids + sugars \u2192 most aromatics",150,215,110,(176,123,62)),
           ("Caramelization \u2014 sugars break down \u2192 sweetness",170,225,150,(201,163,78)),
           ("Chlorogenic acids degrade \u2192 quinic/caffeic, bitterness up",120,230,190,(150,120,150))]
    for lab,ta,tb,by,col in bands:
        d.rounded_rectangle([tx(ta)*s,(by-11)*s,tx(tb)*s,(by+11)*s],radius=8*s,fill=(*mul(col,0.3),255) if False else (30,22,15),outline=col,width=int(1.4*s))
        # gradient-ish fill bar
        d.rectangle([tx(ta)*s,(by-11)*s,tx(tb)*s,(by-11+3)*s],fill=col)
        d.text((tx(ta)*s+6*s,by*s),lab,font=font(9*s,True),fill=INK,anchor="lm")
    # first crack marker
    fc=199
    d.line([tx(fc)*s,60*s,tx(fc)*s,ay*s],fill=(224,120,60),width=int(1.4*s))
    d.text((tx(fc)*s,52*s),"1st crack ~196\u2013205\u00b0C",font=font(9*s,True),fill=(224,134,74),anchor="mm")
    d.text((30*s,26*s),"Roasting Chemistry",font=font(13*s,True),fill=INK)
    d.text((30*s,(H-14)*s),"The reactions overlap on a rising temperature curve \u2014 where you stop sets acidity, sweetness, and bitterness.",font=font(10*s),fill=INK3)
    finish(im,W,H,"roastchem.png")

def gen_degassing():
    W,H,s=760,300,SS
    im,d=frame(W,H,s)
    # CO2 release curve over days (decaying), + one-way valve inset
    x0,x1=70,470; y0,y1=90,220
    d.line([x0*s,y1*s,x1*s,y1*s],fill=(120,104,80),width=int(1.4*s))  # x axis (days)
    d.line([x0*s,y0*s,x0*s,y1*s],fill=(120,104,80),width=int(1.4*s))  # y axis (CO2)
    import math as _m
    pts=[]
    for i in range(101):
        t=i/100; xx=x0+(x1-x0)*t
        co2=_m.exp(-t*3.2)   # fast then slow release
        yy=y1-(y1-y0)*co2
        pts.append((xx*s,yy*s))
    d.line(pts,fill=(201,163,78),width=int(2.4*s),joint="curve")
    # fill under curve
    for i in range(0,100,2):
        t=i/100; xx=x0+(x1-x0)*t; co2=_m.exp(-t*3.2); yy=y1-(y1-y0)*co2
        d.line([xx*s,yy*s,xx*s,y1*s],fill=(80,62,30),width=int((x1-x0)/100*s)+s)
    d.line(pts,fill=(201,163,78),width=int(2.4*s),joint="curve")
    for lab,xt in [("day 0",0),("~4 days",0.33),("~2 weeks",0.75)]:
        xx=x0+(x1-x0)*xt
        d.text((xx*s,(y1+14)*s),lab,font=font(9*s),fill=INK3,anchor="mm")
    d.text((x0*s-6*s,y0*s),"CO\u2082",font=font(9*s,True),fill=INK3,anchor="rm")
    d.text(((x0+120)*s,(y0-4)*s),"most CO\u2082 leaves in the first days",font=font(9*s),fill=INK3,anchor="lm")
    # rest windows note
    d.text((x0*s,y0*s-26*s),"Rest windows: dark roasts ready in a few days; light roasts often want 1\u20132+ weeks.",font=font(9.5*s),fill=INK2 if False else (201,180,150))
    # one-way valve inset (right)
    vx,vy=600,150
    d.rounded_rectangle([(vx-70)*s,(vy-46)*s,(vx+70)*s,(vy+58)*s],radius=10*s,outline=(90,74,54),width=int(1.2*s))
    d.text((vx*s,(vy-58)*s),"the one-way valve",font=font(10*s,True),fill=ACC if False else (201,163,78),anchor="mm")
    # bag
    d.rounded_rectangle([(vx-30)*s,(vy-30)*s,(vx+30)*s,(vy+40)*s],radius=8*s,fill=(48,36,24),outline=(120,100,72),width=int(1.4*s))
    # valve circle
    d.ellipse([(vx-9)*s,(vy-14)*s,(vx+9)*s,(vy+4)*s],fill=(30,22,15),outline=(201,163,78),width=int(1.4*s))
    # CO2 out arrow (up)
    d.line([vx*s,(vy-14)*s,vx*s,(vy-30)*s],fill=(201,163,78),width=int(1.6*s))
    for da in (2.4,-2.4):
        d.line([vx*s,(vy-30)*s,(vx-7*_m.cos(-1.57+da))*s,(vy-30-7*_m.sin(-1.57+da))*s],fill=(201,163,78),width=int(1.6*s))
    d.text((vx*s,(vy-38)*s),"CO\u2082 out",font=font(8.5*s),fill=(201,163,78),anchor="mm")
    # O2 blocked (x)
    d.line([(vx+16)*s,(vy-8)*s,(vx+9)*s,(vy-4)*s],fill=(180,90,80),width=int(1.4*s))
    d.text(((vx+30)*s,(vy-8)*s),"O\u2082 kept out",font=font(8.5*s),fill=(180,120,110),anchor="lm")
    d.text((30*s,26*s),"Degassing, Storage & Packaging",font=font(13*s,True),fill=INK)
    d.text((30*s,(H-14)*s),"Fresh roast off-gasses CO\u2082 for days; the valve lets it escape while keeping oxygen (staleness) out.",font=font(10*s),fill=INK3)
    finish(im,W,H,"degassing.png")

def gen_greenmetrics():
    W,H,s=760,300,SS
    im,d=frame(W,H,s)
    d.text((30*s,26*s),"Density, Moisture & Water Activity",font=font(13*s,True),fill=INK)
    d.text((30*s,44*s),"The four physical numbers a green buyer checks before tasting.",font=font(10*s),fill=INK3)
    cards=[("Moisture","10\u201312%","how much water is in the bean; too high molds, too low bakes flat",(122,150,180),103),
           ("Water activity","< 0.60 aw","free water available for microbes; the real spoilage/shelf-life signal",(150,175,110),288),
           ("Density","tracks altitude","harder, denser beans grew higher and took heat better, so they score higher",(201,163,78),472),
           ("Screen size","64ths of an inch","bean size and uniformity; a grading cue, NOT quality itself",(176,123,62),657)]
    cw=170; cy=155
    for name,big,desc,col,cx in cards:
        d.rounded_rectangle([(cx-cw/2)*s,(cy-70)*s,(cx+cw/2)*s,(cy+70)*s],radius=10*s,fill=(30,22,15),outline=col,width=int(1.5*s))
        d.rectangle([(cx-cw/2)*s,(cy-70)*s,(cx+cw/2)*s,(cy-66)*s],fill=col)
        d.text((cx*s,(cy-52)*s),name,font=font(12*s,True),fill=col,anchor="mm")
        # auto-fit the big value to the card width
        bigsz=14
        while bigsz>9 and d.textlength(big,font=font(bigsz*s,True))>(cw-16)*s:
            bigsz-=1
        d.text((cx*s,(cy-28)*s),big,font=font(bigsz*s,True),fill=INK,anchor="mm")
        # wrap desc
        words=desc.split(); line=""; ln=0
        for w in words:
            if len(line+" "+w)>24:
                d.text((cx*s,(cy-4+ln*13)*s),line,font=font(8.5*s),fill=INK3,anchor="mm"); line=w; ln+=1
            else: line=(line+" "+w).strip()
        d.text((cx*s,(cy-4+ln*13)*s),line,font=font(8.5*s),fill=INK3,anchor="mm")
    d.text((30*s,(H-14)*s),"None is quality alone; together they de-risk a purchase before a single cup is brewed.",font=font(10*s),fill=INK3)
    finish(im,W,H,"greenmetrics.png")

def gen_harvest():
    W,H,s=760,290,SS
    im,d=frame(W,H,s)
    d.text((30*s,26*s),"Harvest & Picking",font=font(13*s,True),fill=INK)
    d.text((30*s,44*s),"The single biggest quality lever at harvest is picking only ripe cherries.",font=font(10*s),fill=INK3)
    # two branches: selective (all red) vs strip (mixed)
    def branch(cx,title,sub,cherries,col):
        d.text((cx*s,80*s),title,font=font(13*s,True),fill=col,anchor="mm")
        d.text((cx*s,98*s),sub,font=font(9.5*s),fill=INK3,anchor="mm")
        # a branch line with cherries
        by=150
        d.line([(cx-70)*s,(by+30)*s,(cx+70)*s,(by-20)*s],fill=(96,70,44),width=int(3*s))
        for (ox,oy,ripe) in cherries:
            ccol=(198,54,44) if ripe==2 else (150,150,70) if ripe==1 else (90,140,70) if ripe==0 else (110,40,34)
            cxp=cx+ox; cyp=by+oy
            d.ellipse([(cxp-8)*s,(cyp-8)*s,(cxp+8)*s,(cyp+8)*s],fill=ccol)
            d.ellipse([(cxp-6)*s,(cyp-6)*s,(cxp-1)*s,(cyp-1)*s],fill=mul(ccol,1.4))
    # selective: all ripe red
    branch(200,"Selective picking","multiple passes \u2014 only the ripe reds",
           [(-50,18,2),(-20,8,2),(10,-2,2),(40,-12,2),(-35,-2,2),(25,12,2)],(198,90,60))
    d.text((200*s,240*s),"Higher quality, higher labor cost",font=font(9.5*s,italic=True),fill=INK3,anchor="mm")
    # strip: everything at once (mixed ripeness)
    branch(560,"Strip picking","one pass \u2014 everything comes off",
           [(-50,18,0),(-20,8,2),(10,-2,3),(40,-12,1),(-35,-2,2),(25,12,0)],(150,140,90))
    d.text((560*s,240*s),"Faster & cheaper, mixed ripeness",font=font(9.5*s,italic=True),fill=INK3,anchor="mm")
    # legend
    lx=250
    for lab,cc in [("ripe",(198,54,44)),("underripe",(90,140,70)),("overripe",(110,40,34)),("green/yellow",(150,150,70))]:
        d.ellipse([lx*s,(268-5)*s,(lx+10)*s,(268+5)*s],fill=cc)
        d.text(((lx+15)*s,268*s),lab,font=font(8.5*s),fill=INK3,anchor="lm"); lx+=len(lab)*6+40
    finish(im,W,H,"harvest.png")

def gen_betweenbatch():
    W,H,s=760,290,SS
    im,d=frame(W,H,s)
    d.text((30*s,26*s),"Between-Batch Protocol",font=font(13*s,True),fill=INK)
    d.text((30*s,44*s),"Bring the drum back to the SAME charge temperature every time, or batches drift.",font=font(10*s),fill=INK3)
    # temperature-vs-time sawtooth: drop -> falls -> recovers to charge temp -> next charge (on the RISE)
    x0,x1=70,700; y0,y1=80,210
    charge=180
    d.line([x0*s,y1*s,x1*s,y1*s],fill=(120,104,80),width=int(1.2*s))
    # charge temp reference line
    cy=y1-(y1-y0)*0.55
    d.line([x0*s,cy*s,x1*s,cy*s],fill=(120,100,72),width=int(1*s))
    d.text(((x1)*s,cy*s-10*s),"charge temp",font=font(9*s),fill=(201,163,78),anchor="rm")
    import math as _m
    # three batches
    seg=(x1-x0)/3
    for b in range(3):
        bx=x0+seg*b
        # roast rises during batch
        d.line([bx*s,cy*s,(bx+seg*0.5)*s,(y0+10)*s],fill=(176,123,62),width=int(2*s))
        # drop (vertical fall)
        d.line([(bx+seg*0.5)*s,(y0+10)*s,(bx+seg*0.5)*s,(y1-14)*s],fill=(120,90,70),width=int(1.6*s))
        # recovery dip then rise back toward charge
        rpts=[]
        for i in range(31):
            t=i/30; xx=bx+seg*0.5+seg*0.5*t
            yy=(y1-14)-((y1-14)-cy)*_m.sin(t*_m.pi/2)
            rpts.append((xx*s,yy*s))
        d.line(rpts,fill=(150,175,110),width=int(1.8*s),joint="curve")
        # charge marker at the point it crosses charge temp ON THE RISE
        d.ellipse([(bx+seg-6)*s,(cy-6)*s,(bx+seg-0)*s,(cy+0)*s],fill=(224,134,74)) if b<3 else None
        d.text((bx*s+seg*0.25*s,(y1+14)*s),f"batch {b+1}",font=font(9*s),fill=INK3,anchor="mm")
    d.text(((x0+40)*s,(y0+4)*s),"roast",font=font(8.5*s),fill=(176,123,62),anchor="lm")
    d.text((x0*s+ (x1-x0)*0.62*s,(cy+16)*s),"recover \u2014 charge while RISING, not falling",font=font(9*s,italic=True),fill=(150,175,110),anchor="lm")
    d.text((30*s,(H-14)*s),"A hot drum after batch 1 makes batch 5 roast differently \u2014 consistent recovery keeps profiles reproducible.",font=font(10*s),fill=INK3)
    finish(im,W,H,"betweenbatch.png")

def gen_grading():
    W,H,s=760,270,SS
    im,d=frame(W,H,s)
    d.text((30*s,26*s),"Country Grading Systems",font=font(13*s,True),fill=INK)
    d.text((30*s,44*s),"The SCA system is universal, but every origin adds its own grade names \u2014 by two broad logics.",font=font(10*s),fill=INK3)
    # two columns: defect-count systems vs size systems
    cols=[("Defect-count systems","grade by how many defects in a sample",(122,150,180),200,
           [("Brazil","Type 2\u2013Type 8 (fewer defects = better)"),("Ethiopia","Grade 1\u2013Grade 5"),("Indonesia","Grade 1\u2013Grade 6")]),
          ("Size / screen systems","grade by bean size \u2014 NOT directly quality",(201,163,78),560,
           [("Kenya","AA, AB, PB (screen size)"),("Colombia","Supremo, Excelso"),("Central America","SHB / SHG by altitude")])]
    for title,sub,col,cx,rows in cols:
        d.rounded_rectangle([(cx-170)*s,70*s,(cx+170)*s,225*s],radius=10*s,fill=(30,22,15),outline=col,width=int(1.5*s))
        d.rectangle([(cx-170)*s,70*s,(cx+170)*s,74*s],fill=col)
        d.text((cx*s,88*s),title,font=font(12*s,True),fill=col,anchor="mm")
        d.text((cx*s,105*s),sub,font=font(9*s,italic=True),fill=INK3,anchor="mm")
        for j,(c,g) in enumerate(rows):
            yy=128+j*30
            d.text(((cx-155)*s,yy*s),c,font=font(10.5*s,True),fill=INK,anchor="lm")
            d.text(((cx-155)*s,(yy+14)*s),g,font=font(9*s),fill=INK3,anchor="lm")
    d.text((30*s,(H-14)*s),"The trap: a size grade like Kenya AA tells you the beans are big \u2014 not that the cup is good.",font=font(10*s),fill=INK3)
    finish(im,W,H,"grading.png")

def gen_threats():
    W,H,s=760,270,SS
    im,d=frame(W,H,s)
    d.text((30*s,26*s),"Pests, Disease & Climate",font=font(13*s,True),fill=INK)
    d.text((30*s,44*s),"Three forces threaten the coffee supply \u2014 two biological, one existential.",font=font(10*s),fill=INK3)
    items=[("Leaf rust","(la roya)","orange fungal spores on leaves \u2014 defoliates the plant; devastated Central America in 2012\u201313",(210,140,60),150,"rust"),
           ("Borer beetle","(broca)","tiny beetle bores into the cherry & bean \u2014 the most damaging insect pest worldwide",(150,110,80),380,"borer"),
           ("Climate change","(existential)","heat & erratic rain push the coffee belt uphill; up to ~50% of arable land at risk by 2050",(150,175,180),610,"climate")]
    cy=140
    for name,tag,desc,col,cx,kind in items:
        # icon
        if kind=="rust":
            d.ellipse([(cx-26)*s,(cy-26)*s,(cx+26)*s,(cy+26)*s],fill=(96,128,80))  # leaf disc
            for ox,oy in [(-8,-4),(6,-8),(10,6),(-4,10),(2,0),(-12,4)]:
                d.ellipse([(cx+ox-5)*s,(cy+oy-5)*s,(cx+ox+5)*s,(cy+oy+5)*s],fill=(198,120,50))
        elif kind=="borer":
            # cherry with a bore hole
            d.ellipse([(cx-24)*s,(cy-24)*s,(cx+24)*s,(cy+24)*s],fill=(170,54,42))
            d.ellipse([(cx+4)*s,(cy-2)*s,(cx+14)*s,(cy+8)*s],fill=(30,20,14))  # hole
            d.ellipse([(cx+6)*s,(cy)*s,(cx+11)*s,(cy+5)*s],fill=(10,8,6))
        else:
            # thermometer / rising
            d.rounded_rectangle([(cx-6)*s,(cy-24)*s,(cx+6)*s,(cy+20)*s],radius=6*s,outline=(180,180,180),width=int(1.6*s))
            d.ellipse([(cx-12)*s,(cy+12)*s,(cx+12)*s,(cy+30)*s],fill=(198,80,60))
            d.rectangle([(cx-3)*s,(cy-8)*s,(cx+3)*s,(cy+20)*s],fill=(198,80,60))
        d.text((cx*s,(cy+48)*s),name,font=font(13*s,True),fill=col,anchor="mm")
        d.text((cx*s,(cy+64)*s),tag,font=font(9*s,italic=True),fill=INK3,anchor="mm")
        # wrap desc
        words=desc.split(); line=""; ln=0
        for w in words:
            if len(line+" "+w)>26:
                d.text((cx*s,(cy+82+ln*12)*s),line,font=font(8.5*s),fill=INK3,anchor="mm"); line=w; ln+=1
            else: line=(line+" "+w).strip()
        d.text((cx*s,(cy+82+ln*12)*s),line,font=font(8.5*s),fill=INK3,anchor="mm")
    finish(im,W,H,"threats.png")

def gen_grinder():
    import math as _m
    W,H,s=760,300,SS
    im,d=frame(W,H,s)
    d.text((30*s,26*s),"The two burr geometries in cross-section. Both shear beans into grounds, but the path and the particle bed differ.",font=font(10.5*s),fill=INK3)
    STEEL=(150,140,120); STEEL2=(110,100,84); BEAN=(138,90,52); GOLDc=(201,163,78)

    def bean(cx,cy,r=4):
        d.ellipse([(cx-r)*s,(cy-r*0.7)*s,(cx+r)*s,(cy+r*0.7)*s],fill=BEAN)

    # ---------- CONICAL (left) : a cone seated inside a ring burr ----------
    cxA,cyA=200,150
    d.text((cxA*s,58*s),"Conical",font=font(15*s,True),fill=INK,anchor="mm")
    # outer ring burr walls (two angled steel walls forming a funnel)
    # left wall
    d.polygon([(cxA-70)*s,(cyA-40)*s,(cxA-52)*s,(cyA-40)*s,(cxA-30)*s,(cyA+44)*s,(cxA-48)*s,(cyA+44)*s],fill=STEEL2,outline=STEEL,width=int(1.4*s))
    # right wall
    d.polygon([(cxA+70)*s,(cyA-40)*s,(cxA+52)*s,(cyA-40)*s,(cxA+30)*s,(cyA+44)*s,(cxA+48)*s,(cyA+44)*s],fill=STEEL2,outline=STEEL,width=int(1.4*s))
    # central cone (the spinning inner burr), pointing up
    d.polygon([(cxA)*s,(cyA-46)*s,(cxA-26)*s,(cyA+44)*s,(cxA+26)*s,(cyA+44)*s],fill=GOLDc,outline=(160,120,50),width=int(1.5*s))
    # cone ridges (teeth) - a few diagonal lines
    for k in range(-2,3):
        d.line([(cxA+k*8)*s,(cyA+44)*s,(cxA+k*3)*s,(cyA-30)*s],fill=(160,120,50),width=int(1*s))
    # beans falling into the top gap
    for k in range(3): bean(cxA-8+k*8, cyA-64+ (k%2)*4)
    # ground coffee exiting the bottom sides (small dots fanning out+down)
    for k in range(6):
        d.ellipse([(cxA-40-k*3)*s,(cyA+50+k*2)*s,(cxA-37-k*3)*s,(cyA+53+k*2)*s],fill=INK3)
        d.ellipse([(cxA+37+k*3)*s,(cyA+50+k*2)*s,(cxA+40+k*3)*s,(cyA+53+k*2)*s],fill=INK3)
    d.text((cxA*s,(cyA+82)*s),"beans fall in by gravity, ground exits the base",font=font(9.5*s),fill=INK3,anchor="mm")
    d.text((cxA*s,(cyA+100)*s),"gravity-fed \u00b7 cooler \u00b7 low retention \u00b7 forgiving",font=font(10*s),fill=INK3,anchor="mm")
    d.text((cxA*s,(cyA+116)*s),"punchy, textured shot",font=font(10*s),fill=INK3,anchor="mm")

    # ---------- FLAT (right) : two parallel ring discs, face to face ----------
    cxB,cyB=560,150
    d.text((cxB*s,58*s),"Flat",font=font(15*s,True),fill=INK,anchor="mm")
    # top disc and bottom disc (rings seen edge-on), with a small gap between
    d.rounded_rectangle([(cxB-64)*s,(cyB-30)*s,(cxB+64)*s,(cyB-14)*s],radius=3*s,fill=GOLDc,outline=(160,120,50),width=int(1.4*s))
    d.rounded_rectangle([(cxB-64)*s,(cyB+14)*s,(cxB+64)*s,(cyB+30)*s],radius=3*s,fill=GOLDc,outline=(160,120,50),width=int(1.4*s))
    # burr teeth hint: short verticals on facing edges
    for k in range(-6,7):
        x=cxB+k*9
        d.line([x*s,(cyB-14)*s,x*s,(cyB-10)*s],fill=(160,120,50),width=int(1*s))
        d.line([x*s,(cyB+14)*s,x*s,(cyB+10)*s],fill=(160,120,50),width=int(1*s))
    # beans fed to the center
    for k in range(2): bean(cxB-4+k*8, cyB-46+k*3)
    d.line([cxB*s,(cyB-38)*s,cxB*s,(cyB-16)*s],fill=STEEL,width=int(1.4*s))
    # centrifugal throw: arrows outward along the gap to both sides
    def flatarr(x1,x2,y):
        d.line([x1*s,y*s,x2*s,y*s],fill=STEEL,width=int(1.6*s))
        ang=0 if x2>x1 else _m.pi
        L,Wd=10,4
        d.polygon([(x2)*s,(y)*s,(x2-L*_m.cos(ang)-Wd*_m.sin(ang))*s,(y-L*_m.sin(ang)+Wd*_m.cos(ang))*s,
                   (x2-L*_m.cos(ang)+Wd*_m.sin(ang))*s,(y-L*_m.sin(ang)-Wd*_m.cos(ang))*s],fill=STEEL)
    flatarr(cxB-4,cxB-58,cyB)
    flatarr(cxB+4,cxB+58,cyB)
    # ground exits both edges
    for k in range(5):
        d.ellipse([(cxB-64-k*3)*s,(cyB-2)*s,(cxB-61-k*3)*s,(cyB+1)*s],fill=INK3)
        d.ellipse([(cxB+61+k*3)*s,(cyB-2)*s,(cxB+64+k*3)*s,(cyB+1)*s],fill=INK3)
    d.text((cxB*s,(cyB+82)*s),"beans thrown out through the gap by centrifugal force",font=font(9.5*s),fill=INK3,anchor="mm")
    d.text((cxB*s,(cyB+100)*s),"centrifugal \u00b7 hotter \u00b7 uniform (unimodal) \u00b7 clarity",font=font(10*s),fill=INK3,anchor="mm")
    d.text((cxB*s,(cyB+116)*s),"espresso standard",font=font(10*s),fill=INK3,anchor="mm")

    # divider
    for yy in range(70,230,10):
        d.line([380*s,yy*s,380*s,(yy+5)*s],fill=LINE,width=int(1*s))
    d.text((30*s,(H-16)*s),"Both crush to uniform particles; the geometry sets temperature, retention, and the feel of the shot.",font=font(10*s),fill=INK3)
    finish(im,W,H,"grinder.png")

gen_processing()
gen_roasters()
gen_milkdrinks()
gen_blend()
gen_teacoffee()
gen_decafmethods()
gen_arabica_robusta()
gen_cupping()
gen_qcloop()
gen_roastchem()
gen_degassing()
gen_greenmetrics()
gen_harvest()
gen_betweenbatch()
gen_grading()
gen_threats()
gen_grinder()
