#!/usr/bin/env python3
"""Speed Ladder reel (14 s, 1080x1920, 30 fps), drawn in code with PIL. usage: render.py <out.mp4> [t0 t1 png_dir]
2-D vector sprites + parallax speed streaks + glow; Earth is the lattice-point globe from ../mosquito/land.json. No AI footage."""
import sys, math, json, subprocess, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H,FPS,T=1080,1920,30,17.1
BEAT=0.45   # 133 BPM grid: every cut, ring and pulse lands on it
CREAM=(247,238,220); GOLD=(232,184,96); TEAL=(96,196,196); RED=(214,62,48); DARK=(8,6,6); STEEL=(214,222,232)
FM='/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf'
rng=np.random.default_rng(11)
def ease(x): x=max(0.0,min(1.0,x)); return x*x*(3-2*x)
def eout(x): x=max(0.0,min(1.0,x)); return 1-(1-x)**3
def ein(x): x=max(0.0,min(1.0,x)); return x**3
# ------------------------------------------------------------------ text
_tc={}
def txt(s,size,fill=CREAM,stroke=True):
    k=(s,size,fill,stroke)
    if k in _tc: return _tc[k]
    f=ImageFont.truetype(FM,size); w=int(f.getlength(s))+size; h=int(size*1.5)
    im=Image.new('RGBA',(w,h),(0,0,0,0)); d=ImageDraw.Draw(im); sw=max(2,int(size*0.07)) if stroke else 0
    d.text((size//2,int(size*0.12)),s,font=f,fill=fill+(255,),stroke_width=sw,stroke_fill=DARK+(235,))
    bb=im.getbbox(); im=im.crop(bb) if bb else im; _tc[k]=im; return im
def chip(s,size):
    k=('chip',s,size)
    if k in _tc: return _tc[k]
    t=txt(s,size,CREAM,False); pw,ph=int(size*.34),int(size*.18)
    im=Image.new('RGBA',(t.width+2*pw,t.height+2*ph),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle((0,0,im.width-1,im.height-1),radius=int(size*.2),fill=RED+(255,)); im.alpha_composite(t,(pw,ph)); _tc[k]=im; return im
def row(parts,size,gap=0.4):
    ims=[chip(p[1:],size) if p.startswith('#') else txt(p,size) for p in parts]
    g=int(size*gap); w=sum(i.width for i in ims)+g*(len(ims)-1); h=max(i.height for i in ims)
    out=Image.new('RGBA',(w,h),(0,0,0,0)); x=0
    for i in ims: out.alpha_composite(i,(x,(h-i.height)//2)); x+=i.width+g
    return out
def put(fr,im,cx,y,al=1.0,crop=1.0):
    if al<=0: return
    if crop<1.0: im=im.crop((0,0,max(1,int(im.width*crop)),im.height))
    if al<1.0: im=im.copy(); im.putalpha(im.getchannel('A').point(lambda v:int(v*al)))
    x=int(cx-(im.width if crop>=1 else im.width/crop)/2); fr.alpha_composite(im,(x,int(y)))
def fade(t,a,b,fi=0.18,fo=0.15): return min(ease((t-a)/fi),ease((b-t)/fo)) if a<=t<b else 0.0
# ------------------------------------------------------------------ timeline
HOOK_END=1.8
STOPS={'jet':(1.8,3.6),'bullet':(3.6,5.4),'earth':(5.4,7.2),'parker':(7.2,9.0)}
LAND_T,LIGHT_T,LAP_T,TWIST_T,LOOP_T=(9.0,9.45),(9.45,11.7),(11.7,14.4),(14.4,16.65),(16.65,17.1)
VALUES=[('jet',0.25),('bullet',0.9),('earth',30.0),('parker',192.0),('light',299792.0)]
START={'jet':1.8,'bullet':3.6,'earth':5.4,'parker':7.2,'light':9.45}
def counter(t):
    """monotonic odometer value (km/s) or None while hidden; rolls to the next stop's value 0.8-1.3 s after it lands"""
    if t<START['jet']+0.7: return None
    v=0.25
    for (n0,v0),(n1,v1) in zip(VALUES,VALUES[1:]):
        a=START[n1]+(0.5 if n1=='light' else 0.3); b=a+(0.7 if n1=='light' else 0.4)
        if t>=a: p=ease((t-a)/(b-a)); v=math.exp(math.log(v0)+(math.log(v1)-math.log(v0))*p)
    return v
def fmt(v):
    if v<1: return f'{v:.2f}'
    return f'{int(round(v)):,}'
# speed (px/s) of the background streaks, integrated for continuous parallax
KEYS=[(0,700),(1.8,700),(3.6,1000),(5.4,1700),(7.2,2800),(9.0,5200),(9.1,0),(9.4,0),(9.45,26000),(9.7,900),(11.7,200),(14.4,150),(16.4,150),(16.65,800),(17.1,800)]
def vel(t):
    for (t0,v0),(t1,v1) in zip(KEYS,KEYS[1:]):
        if t0<=t<=t1: return v0+(v1-v0)*((t-t0)/(t1-t0) if t1>t0 else 1)
    return KEYS[-1][1]
_ts=np.arange(0,T+0.01,1/600); _cum=np.cumsum([vel(x)/600 for x in _ts])
def off(t): return float(np.interp(t,_ts,_cum))
STAR=[(rng.uniform(0,W),rng.uniform(150,1700),rng.uniform(0.25,1.0),rng.uniform(0.5,1.0)) for _ in range(95)]
# ------------------------------------------------------------------ background
def make_bg():
    y=np.linspace(0,1,H)[:,None,None]; top=np.array([14,20,38]); bot=np.array([4,5,10])
    a=(top*(1-y)+bot*y)*np.ones((1,W,1)); xx=np.linspace(-1,1,W)[None,:,None]; yy=np.linspace(-1,1,H)[:,None,None]
    a*= (1-0.35*np.clip(xx**2+yy**2-0.3,0,1)); a=np.clip(a,0,255).astype('uint8')
    return Image.fromarray(a,'RGB').convert('RGBA')
BG=make_bg()
def sprite_finish(im,glow_col,gr=14,ga=0.55):
    """add a soft coloured glow under a finished RGBA sprite"""
    pad=gr*3; big=Image.new('RGBA',(im.width+2*pad,im.height+2*pad),(0,0,0,0)); big.alpha_composite(im,(pad,pad))
    g=Image.new('RGBA',big.size,glow_col+(0,)); g.putalpha(big.getchannel('A').filter(ImageFilter.GaussianBlur(gr)).point(lambda v:int(v*ga)))
    g.alpha_composite(big); return g
def ss(w,h,draw,k=2):
    im=Image.new('RGBA',(w*k,h*k),(0,0,0,0)); d=ImageDraw.Draw(im); draw(d,k); return im.resize((w,h),Image.LANCZOS)
# ------------------------------------------------------------------ sprites (nominal size, facing right)
def jet():
    def f(d,k):
        P=lambda pts:[(x*k,y*k) for x,y in pts]
        d.polygon(P([(110,175),(40,208),(96,208),(190,180)]),fill=(170,180,196))            # far stabiliser
        d.polygon(P([(430,170),(330,262),(390,266),(580,178)]),fill=(150,162,180))           # far wing
        d.polygon(P([(70,128),(160,118),(700,112),(790,122),(850,148),(862,158),(840,172),(760,186),(120,186),(70,160)]),fill=(228,232,238))
        d.polygon(P([(70,128),(34,34),(122,34),(215,118)]),fill=(236,240,246))               # fin
        d.polygon(P([(70,128),(34,34),(60,34),(100,124)]),fill=RED)                          # fin stripe (red marker colour)
        d.polygon(P([(120,166),(850,166),(840,172),(760,186),(120,186),(70,160)]),fill=(176,188,204)) # belly
        d.polygon(P([(480,176),(350,276),(414,282),(640,186)]),fill=(244,246,250))           # near wing
        d.ellipse(P([(440,210),(540,250)]),fill=(196,206,220)); d.ellipse(P([(432,214),(452,246)]),fill=(70,80,96))  # engine
        for i in range(17): x=250+i*28; d.ellipse(P([(x-5,138),(x+5,148)]),fill=(44,56,80))
        d.polygon(P([(800,132),(840,148),(846,152),(800,152)]),fill=(44,56,80))               # cockpit
    return sprite_finish(ss(900,300,f),TEAL,16,0.5)
def bullet():
    def f(d,k):
        P=lambda pts:[(x*k,y*k) for x,y in pts]
        body=[(110,86),(560,80)]+[(560+240*(i/24),120-44*math.sqrt(max(0,1-(i/24)**2))*1.0-0) for i in range(0,25)]
        top=[(560+240*(i/24),120-40*(1-(i/24)**1.6)) for i in range(25)]
        bot=[(560+240*(i/24),120+40*(1-(i/24)**1.6)) for i in range(25)]
        d.polygon(P([(130,92),(560,80)]+top+bot[::-1]+[(560,160),(130,148)]),fill=(214,128,74))
        d.polygon(P([(130,92),(560,80)]+top[:14]+[(560+240*(13/24),120)]+[(560,120)]),fill=(236,160,98))   # light top half
        d.rectangle(P([(300,84),(312,156)]),fill=(150,84,48))                                           # cannelure
        d.polygon(P([(130,92),(110,100),(110,140),(130,148)]),fill=(180,150,80))                      # base / brass
    return sprite_finish(ss(900,240,f),GOLD,14,0.55)
def parker():
    def f(d,k):
        P=lambda pts:[(x*k,y*k) for x,y in pts]
        d.polygon(P([(500,200),(380,40),(470,34),(612,196)]),fill=(28,44,104)); d.polygon(P([(500,300),(380,460),(470,466),(612,304)]),fill=(28,44,104))  # solar wings
        for i in range(1,5):
            t=i/5; d.line(P([(500-120*t,200-160*t*1.0),(612-142*t,196-162*t)]),fill=(110,130,190),width=2*k//2)
            d.line(P([(500-120*t,300+160*t),(612-142*t,304+162*t)]),fill=(110,130,190),width=2*k//2)
        d.polygon(P([(430,225),(700,214),(700,286),(430,275)]),fill=(160,166,178))                      # body
        d.rectangle(P([(430,225),(470,275)]),fill=(120,126,140)); d.ellipse(P([(380,238),(432,262)]),fill=(200,204,214)) # antenna
        d.ellipse(P([(676,110),(760,390)]),fill=(214,216,222)); d.ellipse(P([(688,122),(764,378)]),fill=(244,236,214))  # heat shield disc
        d.ellipse(P([(676,110),(760,390)]),outline=GOLD,width=5*k//2)
    return sprite_finish(ss(900,500,f),(255,150,60),22,0.8)
def mkgal(col):
    im=Image.new('RGBA',(80,50),(0,0,0,0)); d=ImageDraw.Draw(im)
    for r,a in ((22,40),(14,90),(7,200),(3,255)): d.ellipse((40-r,25-r*0.55,40+r,25+r*0.55),fill=col+(a,))
    return im.filter(ImageFilter.GaussianBlur(1))
SPR={'jet':jet(),'bullet':bullet(),'parker':parker()}
GAL=[mkgal(CREAM),mkgal(GOLD),mkgal(TEAL)]
LAND=np.array(json.load(open(os.path.join(os.path.dirname(__file__),'..','mosquito','land.json'))),float)
LAT=np.radians(LAND[:,0]/100.0); LON=np.radians(LAND[:,1]/100.0)
def earth(lon0,R=330):
    S=R*2+60; im=Image.new('RGBA',(S,S),(0,0,0,0)); d=ImageDraw.Draw(im); c=S/2
    for i in range(R,0,-6): g=i/R; d.ellipse((c-i,c-i,c+i,c+i),fill=(int(10+22*g),int(24+40*g),int(60+70*g),255))
    lam=LON-lon0; x=np.cos(LAT)*np.sin(lam); y=np.sin(LAT); z=np.cos(LAT)*np.cos(lam); m=z>0.02
    for px,py,pz in zip(x[m],y[m],z[m]):
        r=3.1*(0.5+0.5*pz); cx=c+px*R; cy=c-py*R; d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(int(190+50*pz),int(205+30*pz),int(190+20*pz),255))
    return sprite_finish(im,TEAL,22,0.9)
# ------------------------------------------------------------------ scene pieces
def streaks(fr,t,power=1.0):
    o=off(t); v=vel(t); dr=ImageDraw.Draw(fr)
    for x0,y0,dp,br in STAR:
        x=(x0-o*dp)%W; L=max(2,min(900,v*0.045*dp)); a=int(255*br*0.7*min(1,0.35+dp*0.6)*power)
        dr.line((x,y0,x+L,y0),fill=CREAM+(a,),width=2 if dp>.6 else 1)
def rings(fr,t,t0,cx,cy):
    dr=ImageDraw.Draw(fr)
    for k in range(3):
        u=(t-t0-k*0.09)/0.55
        if 0<u<1: r=60+760*eout(u); a=int(200*(1-u)); dr.ellipse((cx-r,cy-r,cx+r,cy+r),outline=CREAM+(a,),width=3)
def state(t,a,b):
    """object offset/scale for a stop in [a,b]: enters from the right, exits to the left as the next one arrives"""
    u=(t-(a-0.15))/0.5; v=(t-(b-0.2))/0.45
    dx=(1-eout(u))*950-ein(v)*1250; sc=0.55+0.45*ease(u)
    return dx,sc,(0 if u<0 or v>1 else 1)
PS=1.0
def paste(fr,im,cx,cy,sc=1.0,al=1.0):
    sc=sc*PS
    if sc!=1.0: im=im.resize((max(1,int(im.width*sc)),max(1,int(im.height*sc))),Image.BICUBIC)
    if al<1: im=im.copy(); im.putalpha(im.getchannel('A').point(lambda x:int(x*al)))
    fr.alpha_composite(im,(int(cx-im.width/2),int(cy-im.height/2)))
CX,CY=540,900
def make_bokeh():
    r=np.random.default_rng(21); im=Image.new('RGBA',(W*2,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    for _ in range(46):
        x=r.uniform(0,2*W); y=r.uniform(200,1700); rad=r.uniform(14,60); c=[GOLD,TEAL,CREAM][int(r.integers(0,3))]
        d.ellipse((x-rad,y-rad,x+rad,y+rad),fill=c+(int(r.uniform(10,26)),))
    return im.filter(ImageFilter.GaussianBlur(9))
BOKEH=make_bokeh()
def tint(t):
    for (a,b),c in (((STOPS['jet'][0],STOPS['jet'][1]),(40,150,170)),((STOPS['bullet'][0],STOPS['bullet'][1]),(220,120,60)),((STOPS['earth'][0],STOPS['earth'][1]),(60,130,200)),((STOPS['parker'][0],STOPS['parker'][1]),(240,130,40)),(LIGHT_T,(255,230,170)),(LAP_T,(230,190,100)),(TWIST_T,(90,90,190))):
        if a<=t<b: return c,ease(min((t-a)/0.3,(b-t)/0.3,1.0))*0.10
    return (0,0,0),0.0
def pulse(t):
    for a,b in ((STOPS['jet'][0],LAND_T[0]),(LIGHT_T[0],LAP_T[1])):
        if a<=t<b: return math.exp(-((t-a)%BEAT)/0.09)
    return 0.0
def orbit_pt(th,cx,cy,rx=430,ry=118): return cx+rx*math.cos(th),cy+ry*math.sin(th)
JS=0.78
def jet_pose(t):
    if t<2.5:  # hook: already moving, flies in to the centre
        u=ease(t/2.5); return -240*(1-u),(0.55+0.45*u)*JS,640+260*u
    if t>=LOOP_T[0]:  # loop: flies back in from the left to the frame-0 pose
        u=ease((t-LOOP_T[0])/0.45); return -1250*(1-u)-240*u,0.55*JS,640
    dx,sc,_=state(t,*STOPS['jet']); return dx,sc*JS,CY
def draw(t):
    global PS
    pl=pulse(t); PS=1.0+0.03*pl+(0.06*math.exp(-(t-LIGHT_T[0])/0.12) if LIGHT_T[0]<=t<LIGHT_T[0]+0.6 else 0)
    fr=BG.copy(); lay=Image.new('RGBA',(W,H),(0,0,0,0))
    bx0=int((off(t)*0.06)%W); fr.alpha_composite(BOKEH.crop((bx0,0,bx0+W,H)))
    tc,ta=tint(t)
    if ta>0: fr.alpha_composite(Image.new('RGBA',(W,H),tc+(int(255*ta*(0.8+0.5*pl)),)))
    light=LIGHT_T[0]<=t<LIGHT_T[1]; blackout=LAND_T[0]<=t<LIGHT_T[0]
    # ---- speed streaks
    streaks(lay,t,power=0.0 if blackout else min(1.0,0.8+0.4*pl)); fr.alpha_composite(lay)
    obj=Image.new('RGBA',(W,H),(0,0,0,0)); tl=Image.new('RGBA',(W,H),(0,0,0,0))
    # ---- hero objects
    if t<STOPS['jet'][1]+0.25 or t>=LOOP_T[0]:
        dx,sc,y=jet_pose(t); x=CX+dx
        d=ImageDraw.Draw(obj)
        for k in range(14): d.line((x-380*sc-k*30*sc,y+6,x-380*sc-(k+1)*30*sc,y+6),fill=STEEL+(int(150*(1-k/14)),),width=max(2,int(6*sc)))   # contrail
        paste(obj,SPR['jet'],x,y,sc)
    a,b=STOPS['bullet']; dx,sc,vis=state(t,a,b)
    if vis and a-0.2<=t<b+0.3:
        x=CX+dx; d=ImageDraw.Draw(obj); tipx=x+400*sc*0.78
        for s in (-1,1):
            for j in range(3): d.line((tipx,CY,tipx-320*sc,CY+s*(120+j*34)*sc),fill=CREAM+(int(150-40*j),),width=2)
        paste(obj,SPR['bullet'],x,CY,sc*0.86)
    a,b=STOPS['earth']; dx,sc,vis=state(t,a,b)
    if vis and a-0.2<=t<b+0.3:
        x=CX+dx; d=ImageDraw.Draw(obj)
        R=1500; oy=CY+400+R*0.55  # huge orbit arc under the Earth, moving left
        cxo=x+R*0.15; d.arc((cxo-R*1.9,oy-R*0.55,cxo+R*1.9,oy+R*1.4),215,325,fill=CREAM+(120,),width=3)
        sun=Image.new('RGBA',(700,700),(0,0,0,0)); sd=ImageDraw.Draw(sun)
        for r in range(300,0,-6): g=1-r/300; sd.ellipse((350-r,350-r,350+r,350+r),fill=(255,int(150+90*g),int(60+80*g),int(30+200*g*g)))
        paste(obj,sun,x-760*sc,CY+160,1.0,0.9)
        paste(obj,earth(0.5+(t-a)*0.35),x,CY,sc*0.95)
    a,b=STOPS['parker']; dx,sc,vis=state(t,a,b)
    if vis and a-0.2<=t<b+0.3 and not blackout:
        x=CX+dx; sunb=Image.new('RGBA',(1500,1500),(0,0,0,0)); sd=ImageDraw.Draw(sunb)
        for r in range(740,0,-10): g=1-r/740; sd.ellipse((750-r,750-r,750+r,750+r),fill=(255,int(120+120*g),int(40+70*g),int(20+190*g*g)))
        paste(obj,sunb,x+700,CY+620,1.0,0.95); sh=2.5*math.sin(t*40)
        paste(obj,SPR['parker'],x-10,CY+sh,sc*0.8)
    # ---- light beat and galaxies
    if light:
        u=t-LIGHT_T[0]; d=ImageDraw.Draw(tl)
        xb=-200+(W+400)*min(1,u/0.12); 
        a0=int(255*(1-ease((u-0.12)/0.9)))
        d.line((0,CY,min(W,xb),CY),fill=(255,250,235,a0),width=int(10+16*(1-min(1,u/0.6))))
        for k in range(8): d.line((0,CY+(k-4)*6,min(W,xb),CY+(k-4)*6),fill=GOLD+(int(a0*0.18),),width=2)
        if u<0.2: tl.paste((255,250,235,int(150*(1-u/0.2))),(0,0,W,H)) 
        paste(obj,SPR['parker'],300-120*ease(u/1.5),CY+130,0.16,ease((u-0.2)/0.3))
        fr.alpha_composite(tl)
    if TWIST_T[0]<=t<TWIST_T[1]:
        u=t-TWIST_T[0]; ak=math.exp(0.45*u); d=ImageDraw.Draw(obj)
        gy=np.random.default_rng(5); 
        for i in range(64):
            r=np.random.default_rng(100+i); dd=r.uniform(-430,430); yy=CY+r.uniform(-400,400); x=CX+dd*ak; 
            if not (-60<x<W+60): continue
            fast=abs(dd*0.45*ak)>180; paste(obj,GAL[i%3],x,yy,1.3*ease(u/0.3))
            if fast and u>0.5: ra=int(220*ease((u-0.5)/0.4)); d.ellipse((x-24,yy-18,x+24,yy+18),outline=RED+(ra,),width=2)
        bx=CX+180*u; 
        for k in range(10): d.line((bx-k*14,CY,bx-(k+1)*14,CY),fill=(255,250,235,int(255*(1-k/10))),width=6)
        d.ellipse((bx-10,CY-10,bx+10,CY+10),fill=(255,250,235,255))
        fr.alpha_composite(obj); obj=Image.new('RGBA',(W,H),(0,0,0,0))
        put(fr,txt('LIGHT',30,CREAM),bx,CY+26,ease(u/0.5))
    if LAP_T[0]<=t<LAP_T[1]:
        u=t-LAP_T[0]; e=ease(u/0.35); uu=u-0.3; laps=7.5*max(0.0,min(1.0,uu/1.0)); th=2*math.pi*laps
        cx,cy=CX,CY; d=ImageDraw.Draw(obj)
        fadeout=ease((LAP_T[1]-t)/0.3)
        # faint full ring + back half of the comet
        d.ellipse((cx-430,cy-118,cx+430,cy+118),outline=GOLD+(int(70*e*fadeout),),width=3)
        pts=[]
        if 0<=uu:
            span=1.65 if uu<1.0 else 0.0   # radians swept since the last frame (motion blur at 7.5 laps/s)
            for k in range(110):
                a=th-span*k/109 if span>0 else th-0.05*k; x,y=orbit_pt(a,cx,cy); pts.append((x,y,max(0.0,1-k/109),math.sin(a)))
        for x,y,w,sn in pts:
            if sn<0: r=2+8*w; d.ellipse((x-r,y-r,x+r,y+r),fill=(255,244,214,int(150*w*e*fadeout)))
        paste(obj,earth(0.5+(t-STOPS['earth'][0])*0.35),cx,cy,0.62+0.33*e,fadeout)
        for x,y,w,sn in pts:
            if sn>=0: r=2+9*w; d.ellipse((x-r,y-r,x+r,y+r),fill=(255,244,214,int(175*w*e*fadeout)))
        if pts:
            hx,hy=pts[0][0],pts[0][1]; gl=Image.new('RGBA',(120,120),(0,0,0,0)); gd=ImageDraw.Draw(gl)
            for r_,a_ in ((52,40),(30,90),(14,200),(6,255)): gd.ellipse((60-r_,60-r_,60+r_,60+r_),fill=(255,236,190,int(a_*e*fadeout)))
            obj.alpha_composite(gl,(int(hx-60),int(hy-60)))
    fr.alpha_composite(obj)
    # ---- rings on landing
    rl=Image.new('RGBA',(W,H),(0,0,0,0))
    for n,(a,b) in STOPS.items():
        if n!='jet' or True: rings(rl,t,a+0.35,CX,CY)
    rings(rl,t,LIGHT_T[0]+0.0,CX,CY); fr.alpha_composite(rl)
    # ---- text layer
    tx=Image.new('RGBA',(W,H),(0,0,0,0))
    if t<HOOK_END: 
        hk1=txt('HOW FAST',112); hk2=row(['IS','#FAST','?'],112,0.3); f=min(1,t/1.1); 
        al=fade(t,0,HOOK_END,0.01,0.2); put(tx,hk1,CX,250,al,min(1,f*2)); put(tx,hk2,CX,250+150,al,max(0.04,min(1,(f-0.5)*2)) if f>0.5 else 0.0001)
    names={'jet':('AIRLINER','900 KM/H'),'bullet':('RIFLE BULLET','~3,200 KM/H'),'earth':('YOU, RIGHT NOW','AROUND THE SUN - 107,000 KM/H'),'parker':('PARKER SOLAR PROBE','FASTEST HUMAN-MADE OBJECT')}
    for n,(a,b) in STOPS.items():
        al=fade(t,a+0.45,b-0.05,0.15,0.15)
        if al>0:
            nm,sb=names[n]; put(tx,txt(nm,84 if len(nm)<14 else 64),CX,250,al); put(tx,txt(sb,40 if len(sb)<26 else 34,GOLD),CX,250+112,al)
    if light:
        al=fade(t,LIGHT_T[0]+0.55,LIGHT_T[1]-0.1,0.12,0.15); put(tx,txt('LIGHT',112),CX,250,al); put(tx,row(['#~1,560X','FASTER THAN PARKER'],44,0.3),CX,250+146,al)
    if TWIST_T[0]<=t<TWIST_T[1]:
        put(tx,txt('FAR GALAXIES RECEDE',76),CX,250,fade(t,TWIST_T[0]+0.2,TWIST_T[1]-0.1)); put(tx,txt('FASTER THAN LIGHT.',76),CX,250+98,fade(t,TWIST_T[0]+0.2,TWIST_T[1]-0.1))
        put(tx,txt('(SPACE ITSELF STRETCHES.)',44,GOLD),CX,250+215,fade(t,TWIST_T[0]+1.0,TWIST_T[1]-0.05))
    if t>=TWIST_T[0]+0.5: put(tx,txt('NOT TO SCALE',34),CX,1500,fade(t,TWIST_T[0]+0.5,LOOP_T[0]+0.1,0.3,0.25))
    if LAP_T[0]<=t<LAP_T[1]:
        u=t-LAP_T[0]; uu=max(0.0,u-0.3); laps=7.5*min(1.0,uu/1.0); al=fade(t,LAP_T[0]+0.15,LAP_T[1]-0.05,0.2,0.2)
        put(tx,txt('LIGHT CIRCLES EARTH',62),CX,250,al)
        put(tx,txt('EQUATOR: 40,075 KM' if uu<1.0 else 'IN ONE SECOND.',40,GOLD),CX,250+104,al)
        shown='7.5' if uu>=1.0 else str(int(laps))
        put(tx,row([shown,'#LAPS'],130,0.35),CX,1230,al)
        put(tx,txt(f'{min(uu,1.0):.2f} S',48,CREAM),CX,1230+190,al)
    # counter and ladder
    v=counter(t)
    if v is not None and not blackout and t<LAP_T[0]:
        al=min(ease((t-(START['jet']+0.7))/0.2),1.0 if t<LAP_T[0]-0.25 else ease((LAP_T[0]-t)/0.25)); put(tx,row([fmt(v),'#KM/S'],120,0.35),CX,1230,al)
        rn=['JET','BULLET','EARTH','PARKER','LIGHT']; act=0
        for i,nm in enumerate(rn):
            if t>=START[nm.lower()]: act=i
        for i,nm in enumerate(rn):
            yy=960-i*80; on=i==act; im=txt(nm,38 if on else 30,CREAM if on else (150,150,160))
            tx.alpha_composite(im,(64,int(yy)));
            if on: d=ImageDraw.Draw(tx); d.ellipse((30,yy+im.height//2-9,48,yy+im.height//2+9),fill=RED+(255,))
    fr.alpha_composite(tx)
    if LIGHT_T[0]<=t<LIGHT_T[0]+0.5:
        a=14*math.exp(-(t-LIGHT_T[0])/0.12); from PIL import ImageChops
        fr=ImageChops.offset(fr,int(a*math.sin(t*95)),int(a*math.cos(t*83)))
    out=fr.convert('RGB')
    if light and (t-LIGHT_T[0])<0.35: pass
    return out
if __name__=='__main__':
    out=sys.argv[1]
    if len(sys.argv)>4:
        os.makedirs(sys.argv[4],exist_ok=True)
        for t in [float(x) for x in sys.argv[2].split(',')]: draw(t).save(f'{sys.argv[4]}/f_{t:05.2f}.png')
        sys.exit()
    n=int(T*FPS); vals=[counter(i/FPS) for i in range(n)]; vs=[v for v in vals if v is not None]; assert all(b>=a-1e-9 for a,b in zip(vs,vs[1:])),'counter went backwards'
    p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','16','-preset','medium','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
    for i in range(n): p.stdin.write(draw(i/FPS).tobytes())
    p.stdin.close(); p.wait()
