# python3 overlay.py proj.json out.mov  -> RGBA overlay (text, counters, markers, flashes) for Inside the Clot, 1080x1920, 24 s
import subprocess, math, sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
PJ=json.load(open(sys.argv[1])); OUT=sys.argv[2]
W,H,FPS,T=1080,1920,30,24.9; N=int(round(T*FPS))
# video -> scene time (same monotone cubic as index.html)
WK=[(3.2,0.4),(4.4,2.25),(9.75,8.6),(10.75,9.3),(14.4,13.55),(19.0,18.7),(21.6,21.0),(24.9,24.0)]
_d=[(WK[i+1][1]-WK[i][1])/(WK[i+1][0]-WK[i][0]) for i in range(len(WK)-1)]
_m=[_d[0]]+[0 if _d[i-1]*_d[i]<=0 else 2/(1/_d[i-1]+1/_d[i]) for i in range(1,len(_d))]+[_d[-1]]
def warp(t):
    if t<=WK[0][0]: return WK[0][1]
    if t>=WK[-1][0]: return WK[-1][1]
    i=0
    while t>WK[i+1][0]: i+=1
    h=WK[i+1][0]-WK[i][0]; u=(t-WK[i][0])/h
    return (2*u**3-3*u**2+1)*WK[i][1]+(u**3-2*u**2+u)*h*_m[i]+(-2*u**3+3*u**2)*WK[i+1][1]+(u**3-u**2)*h*_m[i+1]
MB="/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"; MR="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
def F(p,s): return ImageFont.truetype(p,s)
CREAM=(246,240,228); RED=(214,62,48)
def clamp(x): return max(0.0,min(1.0,x))
def sstep(a,b,x): k=clamp((x-a)/(b-a)); return k*k*(3-2*k)
def tw(d,txt,font,sp=0): return sum(d.textlength(c,font=font)+sp for c in txt)-sp if sp else d.textlength(txt,font=font)
def ctext(d,y,txt,font,fill,a=255,sp=0,stroke=0,chip=None):
    if not txt: return
    w=tw(d,txt,font,sp); x=(W-w)/2
    if chip is not None:
        pad=16; d.rectangle((x-pad,y-6,x+w+pad,y+font.size+10),fill=chip+(int(a*0.96),))
    if sp:
        for c in txt:
            d.text((x,y),c,font=font,fill=fill+(a,),stroke_width=stroke,stroke_fill=(0,0,0,min(a,235))); x+=d.textlength(c,font=font)+sp
    else: d.text((x,y),txt,font=font,fill=fill+(a,),stroke_width=stroke,stroke_fill=(0,0,0,min(a,235)))
def typed_chip_line(d,y,full,pre,n,font,a):
    # types `full`; the part after `pre` sits on a red chip
    txt=full[:max(0,min(len(full),n))]
    if not txt: return
    x0=(W-tw(d,full,font))/2
    d.text((x0,y),txt[:len(pre)],font=font,fill=CREAM+(a,),stroke_width=6,stroke_fill=(0,0,0,min(a,235)))
    if len(txt)>len(pre):
        xo=x0+tw(d,pre,font); wo=tw(d,txt[len(pre):],font)
        d.rectangle((xo-12,y-6,xo+wo+12,y+font.size+10),fill=RED+(int(a*0.97),)); d.text((xo,y),txt[len(pre):],font=font,fill=CREAM+(a,))
def solid(c,a): return Image.new("RGBA",(W,H),c+(int(255*a),))
def streaks(seed,alpha,n=40):
    rr=np.random.default_rng(seed); im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im); cx,cy=540,960
    for _ in range(n):
        a=rr.random()*6.283; r0=rr.uniform(260,620); w=rr.uniform(0.003,0.009); r1=1750
        d.polygon([(cx+r0*math.cos(a),cy+r0*math.sin(a)),(cx+r1*math.cos(a-w),cy+r1*math.sin(a-w)),(cx+r1*math.cos(a+w),cy+r1*math.sin(a+w))],fill=(255,240,220,int(255*alpha)))
    return im
def flash(t,tv):
    k=tv-3.2
    if -0.12<=k<0.25: return solid((255,236,220),0.30*(1-clamp(abs(k)/0.25 if k>0 else abs(k)/0.12)))
    for ts,amp in ((2.25,0.14),(13.55,0.12)):
        k=t-ts
        if -0.2<=k<0.2:
            lay=streaks(int(ts*100)+int(round(k*30)),0.20*(1-abs(k)/0.2))
            if k>=-0.03: lay=Image.alpha_composite(lay,solid((255,250,240),amp*(1-clamp(k/0.2))))
            return lay
    k=t-9.3
    if 0<=k<0.12: return solid((255,120,90),0.10*(1-k/0.12))
    return None
def P(f): x,y=PJ[min(f,len(PJ)-1)]; return (x*W,y*H) if x>=0 else None
def age(t): return 25+int(math.floor(30*sstep(2.6,8.4,t)+1e-6))
def minutes(t): u=clamp((t-13.8)/4.6); return int(math.floor(90*u**0.9+1e-6))
fh=F(MB,70); fl=F(MR,27); fc=F(MB,92); fchip=F(MB,46); fsub=F(MR,27); ftag=F(MR,24); ftw=F(MB,54); fend=F(MB,70); fcall=F(MB,32)
prev_age=prev_min=-1
p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgba","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","png",OUT],stdin=subprocess.PIPE)
for f in range(N):
    tv=f/FPS; t=warp(tv) if tv>=3.2 else -1.0; im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    # crowd hook, on screen from frame 0
    if tv<3.25:
        a=int(255*(1-sstep(3.0,3.25,tv)))
        ctext(d,280,"EVERY 40 SECONDS",fh,CREAM,a,stroke=6)
        B=int(a*sstep(0.6,0.8,tv)); ctext(d,378,"SOMEONE IN THE US",fchip,CREAM,B,stroke=5)
        if tv>=1.5: typed_chip_line(d,452,"HAS A HEART ATTACK.","",int((tv-1.5)*30)+1,fchip,a)
        if 1.3<=tv<2.75 and P(f):
            A=int(a*sstep(1.3,1.5,tv)*(1-sstep(2.55,2.75,tv))); cx,cy=P(f); rr=46+6*math.sin(tv*7)
            d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),outline=RED+(A,),width=5)
    # culprit marker on the heart
    for (a0,a1,col) in ((0.6,2.2,RED),(14.0,21.0,RED)):
        if a0<=t<a1 and P(f):
            A=int(255*sstep(a0,a0+0.25,t)*(1-sstep(a1-0.2,a1,t))); cx,cy=P(f); rr=34+5*math.sin(t*7)
            d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),outline=col+(A,),width=4)
    # inside the artery
    if 2.6<=t<4.6:
        A=int(255*sstep(2.6,2.8,t)*(1-sstep(4.4,4.6,t))); ctext(d,300,"INSIDE A HEART ARTERY",fl,CREAM,int(A*0.9),sp=7,stroke=3)
    if 4.6<=t<8.6:
        A=int(255*sstep(4.6,4.8,t)*(1-sstep(8.4,8.6,t))); ag=age(t); assert ag>=prev_age; prev_age=ag
        ctext(d,296,"PLAQUE BUILDS FOR DECADES",fl,CREAM,int(A*0.85),sp=7,stroke=3); ctext(d,330,f"AGE {ag}",fc,CREAM,A,stroke=6)
        ctext(d,452,"PLAQUE",fchip,CREAM,A,sp=4,chip=RED); ctext(d,526,"FAT + CHOLESTEROL INSIDE THE WALL",fsub,CREAM,int(A*0.85),sp=1,stroke=3)
    if 9.3<=t<11.2:
        A=int(255*sstep(9.35,9.5,t)*(1-sstep(11.0,11.2,t)))
        ctext(d,452,"THE CAP CRACKS",fchip,CREAM,A,sp=4,chip=RED); ctext(d,526,"THE BODY TREATS IT AS A WOUND",fsub,CREAM,int(A*0.85),sp=1,stroke=3)
    if 11.2<=t<13.45:
        A=int(255*sstep(11.2,11.4,t)*(1-sstep(13.25,13.45,t)))
        ctext(d,452,"A CLOT SEALS IT",fchip,CREAM,A,sp=4,chip=RED); ctext(d,526,"PLATELETS + FIBRIN. BLOOD STOPS.",fsub,CREAM,int(A*0.85),sp=1,stroke=3)
    # muscle without blood
    if 13.8<=t<18.7:
        A=int(255*sstep(13.8,14.0,t)*(1-sstep(18.5,18.7,t))); mn=minutes(t); assert mn>=prev_min; prev_min=mn
        ctext(d,296,"MINUTES WITHOUT BLOOD",fl,CREAM,int(A*0.85),sp=7,stroke=3); ctext(d,330,f"{mn} MIN",fc,CREAM,A,stroke=6)
        if mn>=20:
            B=int(A*sstep(14.6,14.8,t)); ctext(d,452,"MUSCLE STARTS TO DIE",fchip,CREAM,B,sp=4,chip=RED); ctext(d,526,"FROM ~20-40 MIN, THEN IT SPREADS",fsub,CREAM,int(B*0.85),sp=1,stroke=3)
    # the twist
    if 18.8<=t<21.0:
        A=int(255*(1-sstep(20.8,21.0,t))); n=int((t-18.8)*30)+1
        L=["THE PLAQUE","DIDN'T BLOCK IT."]; k=n
        for i,l in enumerate(L):
            if k>0: ctext(d,300+i*74,l[:min(len(l),k)],ftw,CREAM,A,stroke=6)
            k-=len(l)
        if k>0: typed_chip_line(d,300+2*74+14,"THE CLOT DID.","",k,ftw,A)
    # end line
    if 21.1<=t<24.0:
        A=int(255*(1-sstep(23.7,23.95,t))); n=int((t-21.1)*26)+1
        typed_chip_line(d,300,"TIME IS MUSCLE.","TIME IS ",n,fend,A)
        B=int(A*sstep(21.9,22.2,t)); ctext(d,410,"CHEST PAIN? CALL EMERGENCY SERVICES.",fcall,CREAM,B,stroke=4)
    if True:
        ta=int(140*(1-sstep(23.7,23.95,t))); d.text((48,1500),"ILLUSTRATION · NOT TO SCALE · TIME COMPRESSED",font=ftag,fill=(235,235,235,ta))
    fl_=flash(t,tv)
    if fl_ is not None: im=Image.alpha_composite(im,fl_)
    if t>=23.72: im=Image.alpha_composite(im,solid((0,0,0),0.9*sstep(23.72,24.0,t)))
    p.stdin.write(im.tobytes())
p.stdin.close(); p.wait(); print("overlay done")
