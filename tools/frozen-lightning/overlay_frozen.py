# Text layer for Frozen Lightning (1080x1920, 30 fps, 20 s) -> PNG .mov with alpha.
# usage: python3 overlay_frozen.py <proj dir with proj_*.json> <out.mov>
import subprocess, math, sys, json, glob, numpy as np
from PIL import Image, ImageDraw, ImageFont
W,H,FPS,T=1080,1920,30,20.0; N=int(T*FPS)
PJ={}
for f in glob.glob(sys.argv[1]+'/proj_*.json'): PJ.update({int(k):v for k,v in json.load(open(f)).items()})
MB="/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"; MR="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
def F(p,s): return ImageFont.truetype(p,s)
CREAM=(246,240,228); RED=(214,62,48)
def clamp(x): return max(0.0,min(1.0,x))
def sstep(a,b,x): k=clamp((x-a)/(b-a)); return k*k*(3-2*k)
def tw(d,txt,font,sp=0): return sum(d.textlength(c,font=font)+sp for c in txt)-sp if sp else d.textlength(txt,font=font)
def ctext(d,y,txt,font,fill,a=255,sp=0,stroke=0,chip=None,x=None):
    w=tw(d,txt,font,sp); x=(W-w)/2 if x is None else x
    if chip is not None:
        pad=16; d.rectangle((x-pad,y-6,x+w+pad,y+font.size+10),fill=chip+(int(a*0.96),))
    if sp:
        for c in txt:
            d.text((x,y),c,font=font,fill=fill+(a,),stroke_width=stroke,stroke_fill=(0,0,0,min(a,235))); x+=d.textlength(c,font=font)+sp
    else: d.text((x,y),txt,font=font,fill=fill+(a,),stroke_width=stroke,stroke_fill=(0,0,0,min(a,235)))
def typed_two(d,y1,y2,l1,l2,n,font,a):
    s1=l1[:min(len(l1),n)]
    if s1: ctext(d,y1,s1,font,CREAM,a,stroke=6)
    if n>len(l1):
        m=min(len(l2),n-len(l1)); w2=tw(d,l2,font); x0=(W-w2)/2; pre=l2[:m]
        d.rectangle((x0-14,y2-4,x0+tw(d,pre,font)+14,y2+font.size+8),fill=RED+(int(a*0.97),)); d.text((x0,y2),pre,font=font,fill=CREAM+(a,))
# ---- temperature counter (only ever goes up; asserted below)
def temp(t):
    if t<2.75: return None
    if t<7.3: k=(t-2.75)/4.55; return 20+1680*k**2.0
    if t<10.3: k=sstep(7.3,10.3,t); return 1700+26000*k**1.5
    return 27700.0
def fmt(v):
    v=int(round(v/10.0)*10) if v<10000 else int(round(v/100.0)*100)
    return f"{v:,} °C"
STOPS=[ # (t0,t1,chip,sub)
 (2.75,4.55,"QUARTZ SAND","ONE GRAIN, UP CLOSE"),
 (4.85,7.25,"QUARTZ CRYSTAL","ATOMS LOCKED IN NEAT ROWS"),
 (7.30,8.55,"THE SAND MELTS","THE ROWS BREAK APART"),
 (8.60,10.45,"INSIDE THE BOLT","50,000 °F · 5× THE SUN'S SURFACE"),
 (11.0,12.65,"FROZEN IN A FLASH","SAME ATOMS. NO ORDER. GLASS."),
]
fl=F(MR,27); fc=F(MB,92); fchip=F(MB,46); fsub=F(MR,29); fcap=F(MB,54); fh=F(MB,80); fend=F(MB,70); ftag=F(MR,24); fpt=F(MR,30)
p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgba","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","png",sys.argv[2]],stdin=subprocess.PIPE)
last=-1
for f in range(N):
    t=f/FPS; im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    # hook
    if 0.25<=t<2.05:
        a=int(255*(1-sstep(1.8,2.05,t))); n=int((t-0.25)*38)
        if n>=1: typed_two(d,300,400,"LIGHTNING CAN","MAKE GLASS.",n,fh,a)
    # counter
    v=temp(t)
    if v is not None:
        assert v>=last-1e-6, ("counter went down",t,v,last); last=v
        ca=sstep(2.75,2.95,t)*(1-sstep(11.05,11.4,t)); A=int(255*ca)
        if A>0:
            ctext(d,296,"TEMPERATURE" if t<10.3 else "PEAK",fl,CREAM,int(A*0.85),sp=7,stroke=3); ctext(d,330,fmt(v),fc,CREAM,A,stroke=6)
    for (a0,a1,chip,sub) in STOPS:
        if a0<=t<a1:
            al=sstep(a0,a0+0.18,t)*(1-sstep(a1-0.2,a1,t)); A=int(255*al)
            y0=452 if a0<11 else 330
            ctext(d,y0,chip,fchip,CREAM,A,sp=4,chip=RED); ctext(d,y0+74,sub,fsub,CREAM,int(A*0.9),sp=2,stroke=3)
    # reveal
    if 13.75<=t<17.25:
        A=int(255*sstep(13.75,13.95,t)*(1-sstep(17.0,17.25,t)))
        ctext(d,250,"FULGURITE",fchip,CREAM,A,sp=4,chip=RED); ctext(d,324,"WHAT LIGHTNING LEAVES IN SAND",fsub,CREAM,int(A*0.9),sp=2,stroke=3)
        pj=PJ.get(f)
        if pj and t>=14.35:
            B=int(A*sstep(14.35,14.6,t))
            for (pt,lab,side,dy) in [(pj[0],"ROUGH, SANDY CRUST",1,-10),(pj[1],"HOLLOW, GLASSY INSIDE",-1,40)]:
                x,y=pt[0]*W,pt[1]*H
                if not (0<x<W and 0<y<H): continue
                rr=10+2*math.sin(t*6); d.ellipse((x-rr,y-rr,x+rr,y+rr),outline=RED+(B,),width=4)
                lw=tw(d,lab,fpt); tx=x+60 if side>0 else x-60-lw; tx=max(24,min(W-24-lw,tx)); ty=y+dy-fpt.size/2
                d.line((x+side*rr,y,(tx if side>0 else tx+lw)-side*8,ty+fpt.size/2),fill=CREAM+(int(B*0.9),),width=3)
                ctext(d,ty,lab,fpt,CREAM,B,stroke=4,x=tx)
        if t>=15.5:
            C=int(A*sstep(15.5,15.75,t))
            for i,ln in enumerate(["NOT CLEAR GLASS:","A ROUGH, HOLLOW TUBE","SHAPED LIKE THE BOLT."]):
                ctext(d,1300+i*66,ln,fcap,CREAM,C,stroke=6)
    # end line
    if 17.55<=t<19.45:
        a=int(255*(1-sstep(19.15,19.45,t))); n=int((t-17.55)*30)
        if n>=1: typed_two(d,560,650,"LIGHTNING,","FROZEN.",n,fend,a)
    if t>=0.25:
        ta=int(140*(1-sstep(19.55,19.85,t))); d.text((48,1500),"THOUGHT EXPERIMENT  ·  NOT TO SCALE",font=ftag,fill=(235,235,235,ta))
    p.stdin.write(im.tobytes())
p.stdin.close(); p.wait(); print("overlay done")
