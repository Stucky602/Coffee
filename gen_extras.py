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

def draw_bean(D,base,kind='green'):
    """soft-shaded coffee seed, DxD RGBA, with center-cut valley + silverskin."""
    img=Image.new("RGBA",(D,D),(0,0,0,0)); cx=cy=D/2; rx,ry=D*0.32,D*0.42
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
    # seam
    seam=[(cx+math.sin(i/40*math.pi*2.1)*rx*0.16, cy-ry*0.82+i/40*ry*1.64) for i in range(41)]
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
    im=im.resize((W,H),Image.LANCZOS); im.save(OUT/fname); print("wrote",fname,im.size)

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
            else:  # hybrid: a clean external recirculation pipe looping out the top and back into the side
                duct=(224,168,96); pw=int(2.4*s)
                # up from top of drum
                d.line([(cx+R*0.5)*s,(cy-R+2)*s,(cx+R*0.5)*s,(cy-R-14)*s],fill=duct,width=pw)
                # across the top to the right
                d.line([(cx+R*0.5)*s,(cy-R-14)*s,(cx+R+18)*s,(cy-R-14)*s],fill=duct,width=pw)
                # down the right side
                d.line([(cx+R+18)*s,(cy-R-14)*s,(cx+R+18)*s,(cy)*s],fill=duct,width=pw)
                # back into the drum side, with an arrowhead pointing in
                d.line([(cx+R+18)*s,(cy)*s,(cx+R-2)*s,(cy)*s],fill=duct,width=pw)
                d.polygon([((cx+R-2)*s,(cy)*s),((cx+R+7)*s,(cy-5)*s),((cx+R+7)*s,(cy+5)*s)],fill=duct)
                d.text(((cx+R+8)*s,(cy-R-22)*s),"air",font=font(8.5*s),fill=duct,anchor="mm")
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
    # TEA leaf (right): a pointed leaf with a central vein + serrated hint
    lx,ly=530,cyimg; L=42
    leaf=Image.new("RGBA",(W*s,H*s),(0,0,0,0)); ld=ImageDraw.Draw(leaf)
    pts=[(lx*s,(ly-L)*s)]
    for k in range(1,20):
        t=k/20; yy=ly-L+2*L*t
        xw=math.sin(t*math.pi)*L*0.5
        pts.append(((lx+xw)*s,yy*s))
    pts.append((lx*s,(ly+L)*s))
    for k in range(19,0,-1):
        t=k/20; yy=ly-L+2*L*t; xw=math.sin(t*math.pi)*L*0.5
        pts.append(((lx-xw)*s,yy*s))
    ld.polygon(pts,fill=(74,120,58,255))
    leaf=leaf.filter(ImageFilter.GaussianBlur(1))
    # vein
    ld=ImageDraw.Draw(leaf)
    ld.line([(lx*s,(ly-L)*s),(lx*s,(ly+L)*s)],fill=(52,90,42),width=int(1.6*s))
    for k in range(-3,4):
        vy=ly+k*10
        ld.line([(lx*s,vy*s),((lx+abs(k)*3+6)*s,(vy+8)*s)],fill=(52,90,42),width=int(1*s))
        ld.line([(lx*s,vy*s),((lx-abs(k)*3-6)*s,(vy+8)*s)],fill=(52,90,42),width=int(1*s))
    # leaf sheen
    ld.ellipse([(lx-12)*s,(ly-24)*s,(lx-2)*s,(ly-6)*s],fill=(120,170,96,120))
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

gen_processing()
gen_roasters()
gen_milkdrinks()
gen_blend()
gen_teacoffee()
gen_decafmethods()
