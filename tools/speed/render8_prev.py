#!/usr/bin/env python3
"""Speed Ladder v8 (13.05 s, 1080x1920, 30 fps). Pure black; a single twisting vortex does all the background work (its twist, spin and colour change with each object's speed);
every object carries a magnetic-field aura (dipole field lines) that grows, brightens and distorts with speed. The ladder starts on frame 0 (airliner, then a hard snap to the bullet).
usage: render8.py <out.mp4>            |   render8.py x t1,t2,.. ignore <png_dir>   (stills)"""
import sys, os, math, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R   # sprites (airliner, bullet, probe), the lattice Earth and galaxy glints; its old backdrop code is not used here
W,H,FPS,T=1080,1920,30,13.05
BEAT=0.45
CX,CY=540,700
ease,eout,ein=R.ease,R.eout,R.ein
WHITE=(255,255,255); RED=(224,32,32); GOLD=(255,205,100)
BEB=os.path.join(os.path.dirname(os.path.abspath(__file__)),'fonts','BebasNeue.ttf')
# ------------------------------------------------------------------ timeline (s): every cut on the 133 BPM grid
STOPS={'jet':(0.0,0.9),'bullet':(0.9,1.8),'earth':(1.8,3.6),'parker':(3.6,5.4)}
LAND_T,LIGHT_T,LAP_T,TWIST_T,LOOP_T=(5.4,5.85),(5.85,8.1),(8.1,10.8),(10.8,12.6),(12.6,13.05)
START={'jet':0.0,'bullet':0.9,'earth':1.8,'parker':3.6,'light':5.85}
THEME={'jet':(70,150,255),'bullet':(255,128,36),'earth':(40,225,235),'parker':(255,205,100),'light':(255,246,228),'lap':(255,200,110),'twist':(150,110,235)}
# stage -> (twist, forward speed, brightness, arms): jet barely twisted, bullet 3x the twist, probe a full wormhole spin
VP={'jet':(0.06,0.7,0.55,10),'bullet':(0.18,1.8,0.72,14),'earth':(0.30,2.8,0.80,16),'parker':(0.46,4.4,0.92,20),'black':(0.0,0.0,0.0,10),
    'light':(0.62,6.5,0.88,24),'lap':(0.30,2.2,0.55,16),'twist':(0.24,0.9,0.55,14)}
STAGES=[(0.0,'jet'),(0.9,'bullet'),(1.8,'earth'),(3.6,'parker'),(5.4,'black'),(5.85,'light'),(8.1,'lap'),(10.8,'twist'),(12.6,'jet')]
LVL={'jet':0.30,'bullet':0.52,'earth':0.76,'parker':1.0}   # field strength = speed on a log-ish scale
# ------------------------------------------------------------------ text (Bebas Neue, heavier via stroke)
_tc={}
def txt(s,size,fill=WHITE,sw=None):
    k=(s,size,fill)
    if k in _tc: return _tc[k]
    f=ImageFont.truetype(BEB,size); w=int(f.getlength(s))+size; h=int(size*1.4)
    im=Image.new('RGBA',(w,h),(0,0,0,0)); d=ImageDraw.Draw(im); sw=max(1,size//40) if sw is None else sw
    d.text((size//2,int(size*0.1)),s,font=f,fill=fill+(255,),stroke_width=sw,stroke_fill=fill+(255,))
    bb=im.getbbox(); im=im.crop(bb) if bb else im; _tc[k]=im; return im
def chip(s,size):
    k=('chip',s,size)
    if k in _tc: return _tc[k]
    t=txt(s,size); pw,ph=int(size*0.2),int(size*0.1)
    im=Image.new('RGBA',(t.width+2*pw,t.height+2*ph),(0,0,0,0)); d=ImageDraw.Draw(im); d.rounded_rectangle((0,0,im.width-1,im.height-1),radius=int(size*0.08),fill=RED+(255,))
    im.alpha_composite(t,(pw,ph)); _tc[k]=im; return im
def row(parts,size,gap=0.18):
    ims=[chip(p[1:],size) if p.startswith('#') else txt(p,size) for p in parts]; g=int(size*gap)
    w=sum(i.width for i in ims)+g*(len(ims)-1); h=max(i.height for i in ims); out=Image.new('RGBA',(w,h),(0,0,0,0)); x=0
    for i in ims: out.alpha_composite(i,(x,(h-i.height)//2)); x+=i.width+g
    return out
def put(fr,im,cx,y,al=1.0):
    if al<=0: return
    if al<1.0: im=im.copy(); im.putalpha(im.getchannel('A').point(lambda v:int(v*al)))
    fr.alpha_composite(im,(int(cx-im.width/2),int(y)))
def fade(t,a,b,fi=0.12,fo=0.12): return min(ease((t-a)/fi),ease((b-t)/fo)) if a<=t<b else 0.0
def paste(fr,im,cx,cy,sc=1.0,al=1.0):
    if sc!=1.0: im=im.resize((max(1,int(im.width*sc)),max(1,int(im.height*sc))),Image.BICUBIC)
    if al<1: im=im.copy(); im.putalpha(im.getchannel('A').point(lambda x:int(x*al)))
    fr.alpha_composite(im,(int(cx-im.width/2),int(cy-im.height/2)))
# ------------------------------------------------------------------ counter (monotonic km/s odometer)
VALUES=[('jet',0.25),('bullet',0.9),('earth',30.0),('parker',192.0),('light',299792.0)]
def counter(t):
    v=0.25
    for (n0,v0),(n1,v1) in zip(VALUES,VALUES[1:]):
        a=START[n1]+(0.12 if n1=='light' else 0.0); b=a+(0.3 if n1=='light' else 0.001)   # stops snap to their exact value on the cut; only the light leap rolls (0.3 s)
        if t>=a: p=ease((t-a)/(b-a)); v=math.exp(math.log(v0)+(math.log(v1)-math.log(v0))*p)
    return v
def fmt(v): return f'{v:.2f}' if v<1 else f'{int(round(v)):,}'
# ------------------------------------------------------------------ vortex
def stage(t):
    for i in range(len(STAGES)-1,-1,-1):
        if t>=STAGES[i][0]: return i
    return 0
def vparams(t):
    i=stage(t); a0,nm=STAGES[i]; cur=VP[nm]; col=THEME.get(nm,(0,0,0))
    if nm=='black': col=THEME['parker']
    if i>0 and t<a0+0.12:   # hard snap, not a slow blend
        pn=STAGES[i-1][1]; u=ease((t-a0)/0.12); prev=VP[pn]; pc=THEME.get(pn,col)
        cur=tuple(prev[k]+(cur[k]-prev[k])*u for k in range(4)); col=tuple(pc[k]+(col[k]-pc[k])*u for k in range(3))
    if i==len(STAGES)-1 and t>=LOOP_T[0] and False: pass
    return cur,col
def vparams_loop(t):
    """last beat blends the twist stage back into the jet stage so the last frame matches frame 0"""
    if t<LOOP_T[0]: return vparams(t)
    u=ease((t-LOOP_T[0])/(T-LOOP_T[0])); a=VP['twist']; b=VP['jet']; ca=THEME['twist']; cb=THEME['jet']
    return tuple(a[k]+(b[k]-a[k])*u for k in range(4)),tuple(ca[k]+(cb[k]-ca[k])*u for k in range(3))
_ts=np.arange(0,T+0.01,1/300); _P=[vparams_loop(x)[0] for x in _ts]
_Z=np.cumsum([p[1]/300 for p in _P]); _S=np.cumsum([p[1]*0.5/300 for p in _P])
def vortex_layer(t):
    (tw,sp,br,na),col=vparams_loop(t)
    if br<=0.01: return None
    VB=0.34 if t<LIGHT_T[0] or t>=LAP_T[0] else 0.5   # vortex dimmed a lot (the objects are the focus); the light stage keeps a little more
    img=np.zeros((H,W,3),np.uint8); F=520.0; cx,cy=CX,960; Z=float(np.interp(t,_ts,_Z)); S=float(np.interp(t,_ts,_S)); rgb=np.array(col,float)[::-1]
    for k in range(36):   # rings rushing outward
        z=((k*0.38-Z)%13.7)+0.32; r=F/z; al=max(0.0,1-z/14.0)**1.1*min(1.0,z/0.8)*br*VB
        if al<0.02: continue
        cv2.ellipse(img,(cx,cy),(int(r),int(r*1.25)),0,0,360,tuple(int(v*al) for v in rgb),2,cv2.LINE_AA)
    n=int(round(na)); zs=np.geomspace(0.32,14.0,50)
    for j in range(n):   # spiral arms: the twist grows with depth, the whole thing spins
        ph=2*math.pi*j/n+S; pts=[]
        for z in zs:
            th=ph+tw*(14.0-z)*0.9; r=F/z; pts.append((cx+r*math.cos(th),cy+r*math.sin(th)*1.25))
        a_=br*0.85*VB
        cv2.polylines(img,[np.array(pts,np.int32)],False,tuple(int(v*a_) for v in rgb),2,cv2.LINE_AA)
    g=cv2.GaussianBlur(img,(0,0),8).astype(float)
    img=np.clip(img.astype(float)+g*0.9,0,255).astype('uint8')
    a=np.clip(img.max(axis=2).astype(float)*1.4,0,255).astype('uint8')
    return Image.fromarray(np.dstack([img[...,::-1],a]),'RGBA')
# ------------------------------------------------------------------ magnetic-field aura
A0={'jet':380,'bullet':410,'earth':330,'parker':380,None:380}
def aura_layer(t,lvl,col,cx=CX,cy=CY,al=1.0,half=380):
    """magnetic-field loops: nested lens-shaped lines joining the object's nose and tail (like field lines between two poles), plus wider outer loops;
    faster object = more loops, taller, brighter, thicker and more distorted"""
    RW,RH=1200,900; img=np.zeros((RH,RW,3),np.uint8); c_=np.array(col,float); c_=(0.7*c_+0.3*c_.mean())*(0.50+0.14*lvl); rgb=c_[::-1]; ox,oy=RW/2,RH/2   # softer, less saturated and dimmer
    nl=3+int(round(6*lvl)); bmax=90+190*lvl; amp=0.02+0.30*lvl**2; w=2+int(2*lvl); om=1.0+4.0*lvl
    tt=np.linspace(0,2*math.pi,160)
    for k in range(nl):
        u=(k+1)/nl; a=(half+30+90*u*(0.6+0.4*lvl))*(1.0+0.0*k); b=bmax*(0.30+0.70*u)
        x=a*np.cos(tt)+amp*a*0.10*np.sin(3*tt+om*t+k*0.9); y=b*np.sin(tt)+amp*b*0.45*np.cos(2*tt-om*t*0.8+k)
        fall=(0.40+0.60*(1-u*0.6))*(0.55+0.45*lvl)*al
        p=np.stack([ox+x,oy+y],1).astype(np.int32)
        cv2.polylines(img,[p],True,tuple(int(v*fall) for v in rgb),w,cv2.LINE_AA)
    g=cv2.GaussianBlur(img,(0,0),6+7*lvl).astype(float); img=np.clip(img.astype(float)+g*(0.5+0.5*lvl),0,255).astype('uint8')
    a_=np.clip(img.max(axis=2).astype(float)*1.3,0,255).astype('uint8')
    return Image.fromarray(np.dstack([img[...,::-1],a_]),'RGBA'),(int(cx-ox),int(cy-oy))
# ------------------------------------------------------------------ scene
def pulse(t):
    for a,b in ((0.0,LAND_T[0]),(LIGHT_T[0],LAP_T[1])):
        if a<=t<b: return math.exp(-(((t-a)%BEAT))/0.09)
    return 0.0
def popscale(t,a): u=(t-a)/0.16; return 0.82+0.18*ease(u)+0.10*math.exp(-max(0,t-a)/0.08)*(1 if t>=a else 0)
JS=0.78
def draw(t):
    pl=pulse(t); fr=Image.new('RGBA',(W,H),(0,0,0,255))
    blackout=LAND_T[0]<=t<LIGHT_T[0]
    vl=vortex_layer(t)
    if vl is not None and not blackout: fr.alpha_composite(vl)
    obj=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(obj)
    PSC=1.0+0.03*pl
    names={'jet':('AIRLINER','900 KM/H'),'bullet':('RIFLE BULLET','~3,200 KM/H'),'earth':('YOU, RIGHT NOW','AROUND THE SUN - 107,000 KM/H'),'parker':('PARKER SOLAR PROBE','FASTEST HUMAN-MADE OBJECT')}
    # ---- hero objects with their field auras
    cur=None
    for n,(a,b) in STOPS.items():
        if a<=t<b: cur=n
    if t>=LOOP_T[0]: cur='jet'   # last beat re-forms the opening frame
    if cur:
        a,b=STOPS[cur]; al=ease((t-LOOP_T[0])/(T-LOOP_T[0])) if t>=LOOP_T[0] else 1.0
        ts=(t-a) if t<LOOP_T[0] else 1.0
        ps=0.82+0.18*ease(ts/0.16)+0.10*math.exp(-max(0,ts)/0.08) if cur!='jet' or t>=LOOP_T[0] else 1.0
        au,(ax,ay)=aura_layer(t,LVL[cur],THEME[cur],al=al,half=A0[cur]-30); obj.alpha_composite(au,(ax,ay))
        if cur=='jet':
            for k in range(14): d.line((CX-300-k*34,CY+5,CX-300-(k+1)*34,CY+5),fill=R.STEEL+(int(140*(1-k/14)*al),),width=5)
            paste(obj,R.SPR['jet'],CX,CY,JS*PSC*ps,al)
        elif cur=='bullet':
            paste(obj,R.SPR['bullet'],CX,CY,0.86*PSC*ps,al)
        elif cur=='earth':
            paste(obj,R.earth(0.5+(t-a)*0.35),CX,CY,0.9*PSC*ps,al)
        else:
            paste(obj,R.SPR['parker'],CX-10,CY+2.5*math.sin(t*40),0.8*PSC*ps,al)
    # ---- light beat
    if LIGHT_T[0]<=t<LIGHT_T[1]:
        u=t-LIGHT_T[0]; xb=-200+(W+400)*min(1,u/0.12); a0=int(255*(1-ease((u-0.12)/0.9)))
        d.line((0,CY,min(W,xb),CY),fill=(255,250,235,a0),width=int(10+16*(1-min(1,u/0.6))))
        for k in range(8): d.line((0,CY+(k-4)*6,min(W,xb),CY+(k-4)*6),fill=GOLD+(int(a0*0.18),),width=2)
        if u<0.16: obj.alpha_composite(Image.new('RGBA',(W,H),(255,250,235,int(140*(1-u/0.16)))))
        paste(obj,R.SPR['parker'],300-120*ease(u/1.5),CY+130,0.16,ease((u-0.2)/0.3))
    # ---- laps
    if LAP_T[0]<=t<LAP_T[1]:
        u=t-LAP_T[0]; e=ease(u/0.35); uu=u-0.3; laps=7.5*max(0.0,min(1.0,uu/1.0)); th=2*math.pi*laps; fo=ease((LAP_T[1]-t)/0.3)
        def op(a,rx=430,ry=118): return CX+rx*math.cos(a),CY+ry*math.sin(a)
        d.ellipse((CX-430,CY-118,CX+430,CY+118),outline=GOLD+(int(70*e*fo),),width=3); pts=[]
        if uu>=0:
            span=1.65 if uu<1.0 else 0.0
            for k in range(110):
                a=th-span*k/109 if span>0 else th-0.05*k; x,y=op(a); pts.append((x,y,max(0.0,1-k/109),math.sin(a)))
        for x,y,w,sn in pts:
            if sn<0: r=2+8*w; d.ellipse((x-r,y-r,x+r,y+r),fill=(255,244,214,int(150*w*e*fo)))
        paste(obj,R.earth(0.5+(t-STOPS['earth'][0])*0.35),CX,CY,0.62+0.33*e,fo)
        for x,y,w,sn in pts:
            if sn>=0: r=2+9*w; d.ellipse((x-r,y-r,x+r,y+r),fill=(255,244,214,int(175*w*e*fo)))
        if pts:
            hx,hy=pts[0][0],pts[0][1]; gl=Image.new('RGBA',(120,120),(0,0,0,0)); gd=ImageDraw.Draw(gl)
            for r_,a_ in ((52,40),(30,90),(14,200),(6,255)): gd.ellipse((60-r_,60-r_,60+r_,60+r_),fill=(255,236,190,int(a_*e*fo)))
            obj.alpha_composite(gl,(int(hx-60),int(hy-60)))
    # ---- galaxies (twist)
    if TWIST_T[0]<=t<TWIST_T[1]:
        u=t-TWIST_T[0]; ak=math.exp(0.45*u)
        for i in range(64):
            r=np.random.default_rng(100+i); dd=r.uniform(-430,430); yy=CY+r.uniform(-400,400); x=CX+dd*ak
            if not(-60<x<W+60): continue
            fast=abs(dd*0.45*ak)>180; paste(obj,R.GAL[i%3],x,yy,1.3*ease(u/0.3))
            if fast and u>0.5: d.ellipse((x-24,yy-18,x+24,yy+18),outline=RED+(int(220*ease((u-0.5)/0.4)),),width=2)
        bx=CX+180*u
        for k in range(10): d.line((bx-k*14,CY,bx-(k+1)*14,CY),fill=(255,250,235,int(255*(1-k/10))),width=6)
        d.ellipse((bx-10,CY-10,bx+10,CY+10),fill=(255,250,235,255)); put(obj,txt('LIGHT',34),bx,CY+26,ease(u/0.5))
    fr.alpha_composite(obj)
    # ---- hard-cut accents: colour flash + shake on every stop change
    for s0 in (0.9,1.8,3.6):
        if s0<=t<s0+0.12:
            c=THEME[[n for n,(a,b) in STOPS.items() if a==s0][0]]; fr.alpha_composite(Image.new('RGBA',(W,H),c+(int(70*(1-(t-s0)/0.12)),)))
    # ---- text
    tx=Image.new('RGBA',(W,H),(0,0,0,0))
    title_al=1.0 if t<LAND_T[0]-0.15 else ease((LAND_T[0]-t)/0.15)
    if t>=LOOP_T[0]: title_al=ease((t-LOOP_T[0])/(T-LOOP_T[0]))
    if (t<LAND_T[0] or t>=LOOP_T[0]) and title_al>0: put(tx,row(['HOW FAST IS','#FAST','?'],104),CX,215,title_al)
    for n,(a,b) in STOPS.items():
        al=(1.0 if t>=a+0.04 else ease((t-a)/0.04))*(ease((b-t)/0.06) if t>b-0.06 else 1.0) if a<=t<b else 0.0
        if n=='jet' and t<b-0.06: al=1.0
        if al>0:
            nm,sb=names[n]; put(tx,txt(nm,60),CX,1050,al); put(tx,txt(sb,34,GOLD),CX,1050+68,al)
    if t>=LOOP_T[0]: al=ease((t-LOOP_T[0])/(T-LOOP_T[0])); put(tx,txt(names['jet'][0],60),CX,1050,al); put(tx,txt(names['jet'][1],34,GOLD),CX,1118,al)
    if LIGHT_T[0]<=t<LIGHT_T[1]:
        al=fade(t,LIGHT_T[0]+0.55,LIGHT_T[1]-0.1); put(tx,txt('LIGHT',118),CX,215,al); put(tx,row(['#~1,560X','FASTER THAN PARKER'],46),CX,215+140,al)
    if LAP_T[0]<=t<LAP_T[1]:
        u=t-LAP_T[0]; uu=max(0.0,u-0.3); laps=7.5*min(1.0,uu/1.0); al=fade(t,LAP_T[0]+0.15,LAP_T[1]-0.05,0.2,0.2)
        put(tx,txt('LIGHT CIRCLES EARTH',78),CX,215,al); put(tx,txt('EQUATOR: 40,075 KM' if uu<1.0 else 'IN ONE SECOND.',40,GOLD),CX,215+96,al)
        put(tx,row(['7.5' if uu>=1.0 else str(int(laps)),'#LAPS'],112),CX,1130,al); put(tx,txt(f'{min(uu,1.0):.2f} S',48),CX,1130+140,al)
    if TWIST_T[0]<=t<TWIST_T[1]:
        a_=fade(t,TWIST_T[0]+0.2,TWIST_T[1]-0.1); put(tx,txt('FAR GALAXIES RECEDE',80),CX,215,a_); put(tx,txt('FASTER THAN LIGHT.',80),CX,215+88,a_)
        put(tx,txt('(SPACE ITSELF STRETCHES.)',40,GOLD),CX,215+190,fade(t,TWIST_T[0]+1.0,TWIST_T[1]-0.05))
        put(tx,txt('NOT TO SCALE',36,(170,170,180)),CX,1500,fade(t,TWIST_T[0]+0.5,TWIST_T[1],0.3,0.15))
    # counter and ladder
    if (t<LAP_T[0] and not blackout) or t>=LOOP_T[0]:
        al=1.0 if t<LAP_T[0]-0.25 else ease((LAP_T[0]-t)/0.25)
        if t>=LOOP_T[0]: al=ease((t-LOOP_T[0])/(T-LOOP_T[0]))
        if t>=LOOP_T[0] or t<LAP_T[0]: put(tx,row([fmt(counter(t) if t<LOOP_T[0] else 0.25),'#KM/S'],100),CX,1240,al)
        rn=['JET','BULLET','EARTH','PARKER','LIGHT']; act=0
        for i,nm in enumerate(rn):
            if t>=START[nm.lower()] and t<LAP_T[0]: act=i
        for i,nm in enumerate(rn):
            yy=930-i*70; on=i==act; im=txt(nm,40 if on else 32,WHITE if on else (110,110,120)); tx.alpha_composite(im,(46,int(yy)))
            if on: ImageDraw.Draw(tx).ellipse((16,yy+im.height//2-7,30,yy+im.height//2+7),fill=RED+(255,))
    fr.alpha_composite(tx)
    # ---- screen shake: small on each cut, big on the drop
    sh=0.0
    for s0,amp in ((0.9,7),(1.8,7),(3.6,7),(LIGHT_T[0],16)):
        if s0<=t<s0+0.4: sh=max(sh,amp*math.exp(-(t-s0)/0.1))
    if sh>0.3: fr=ImageChops.offset(fr,int(sh*math.sin(t*95)),int(sh*math.cos(t*83)))
    return fr.convert('RGB')
if __name__=='__main__':
    out=sys.argv[1]
    if len(sys.argv)>4:
        os.makedirs(sys.argv[4],exist_ok=True)
        for t in [float(x) for x in sys.argv[2].split(',')]: draw(t).save(f'{sys.argv[4]}/f_{t:05.2f}.png')
        sys.exit()
    n=int(T*FPS); vs=[counter(i/FPS) for i in range(n)]; assert all(b>=a-1e-9 for a,b in zip(vs,vs[1:])),'counter went backwards'
    p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','16','-preset','medium','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
    for i in range(n): p.stdin.write(draw(i/FPS).tobytes())
    p.stdin.close(); p.wait()
