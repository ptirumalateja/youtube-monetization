import subprocess, math, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
VAR=sys.argv[1]
import json; PJ=json.load(open('n3d/proj5.json'))
W,H,FPS,T=1080,1920,30,18.88; N=int(T*FPS)
MB="/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"; MR="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
def F(p,s): return ImageFont.truetype(p,s)
CREAM=(246,240,228); RED=(214,62,48)
def clamp(x): return max(0.0,min(1.0,x))
def sstep(a,b,x): k=clamp((x-a)/(b-a)); return k*k*(3-2*k)
def tw(d,txt,font,sp=0): return sum(d.textlength(c,font=font)+sp for c in txt)-sp if sp else d.textlength(txt,font=font)
def ctext(d,y,txt,font,fill,a=255,sp=0,stroke=0,chip=None):
    w=tw(d,txt,font,sp); x=(W-w)/2
    if chip is not None:
        pad=16; d.rectangle((x-pad,y-6,x+w+pad,y+font.size+10),fill=chip+(int(a*0.96),))
    if sp:
        for c in txt:
            d.text((x,y),c,font=font,fill=fill+(a,),stroke_width=stroke,stroke_fill=(0,0,0,min(a,235))); x+=d.textlength(c,font=font)+sp
    else: d.text((x,y),txt,font=font,fill=fill+(a,),stroke_width=stroke,stroke_fill=(0,0,0,min(a,235)))
def typed_two(d,y1,y2,l1,l2,n,font,a,chip2=True):
    # l1 cream, l2 on red chip; n = characters revealed overall
    s1=l1[:min(len(l1),n)]
    if s1: ctext(d,y1,s1,font,CREAM,a,stroke=6)
    if n>len(l1):
        m=min(len(l2),n-len(l1)); w2=tw(d,l2,font); x0=(W-w2)/2; pre=l2[:m]
        d.rectangle((x0-14,y2-4,x0+tw(d,pre,font)+14,y2+font.size+8),fill=RED+(int(a*0.97),))
        d.text((x0,y2),pre,font=font,fill=CREAM+(a,))
def speed_lines(seed,alpha,n=40,ri=(260,560),black_bg=False):
    rr=np.random.default_rng(seed); im=Image.new("RGBA",(W,H),(0,0,0,int(255*0.55) if black_bg else 0)); d=ImageDraw.Draw(im)
    cx,cy=540,900
    for _ in range(n):
        a=rr.random()*6.283; r0=rr.uniform(*ri); w=rr.uniform(0.003,0.010); r1=1700
        p=[(cx+r0*math.cos(a),cy+r0*math.sin(a)),(cx+r1*math.cos(a-w),cy+r1*math.sin(a-w)),(cx+r1*math.cos(a+w),cy+r1*math.sin(a+w))]
        d.polygon(p,fill=(255,255,255,int(255*alpha)))
    return im
def solid(c,a): return Image.new("RGBA",(W,H),c+(int(255*a),))

def fit(d,txt,path,size,maxw=980,sp=0):
    f=F(path,size)
    while tw(d,txt,f,sp)>maxw and size>34: size-=3; f=F(path,size)
    return f
STOPS_T=[(3.00,"1.3 SECONDS AGO","THE MOON","MOONLIGHT TAKES 1.3 SECONDS TO ARRIVE",2.55,4.10),
         (4.70,"8 MIN 20 SEC AGO","THE SUN","IF IT VANISHED NOW, YOU'D STILL SEE IT",4.20,5.80),
         (6.40,"4.2 YEARS AGO","PROXIMA CENTAURI","THE NEAREST STAR AFTER THE SUN",5.85,7.35),
         (10.05,"2.5 MILLION YEARS AGO","ANDROMEDA GALAXY","BEFORE MODERN HUMANS EXISTED",10.0,12.35)]
LAD=[("NOW",0),("MOON  1.3 SEC",3.0),("SUN  8 MIN 20 SEC",4.7),("PROXIMA  4.2 YEARS",6.4),("ANDROMEDA  2.5 MILLION YEARS",10.05)]
LAD_Y=[1420,1260,1100,940,780]
def lad_pos(t):
    ks=[(2.1,0.0),(3.0,1.0),(4.7,2.0),(6.4,3.0),(10.05,4.0)]
    for i in range(len(ks)-1):
        a,ua=ks[i]; b,ub=ks[i+1]
        if t<=b: return ua+(ub-ua)*sstep(a+0.25,b-0.05,t)
    return 4.0
def impact_layer(f):
    t=f/FPS
    if 2.08<=t<2.2: return solid((255,255,255),0.16*(1-(t-2.08)/0.12))
    for t0,al in ((2.57,0.10),(4.05,0.12),(6.08,0.12)):
        k=int(round((t-t0)*FPS))
        if 0<=k<4: return speed_lines(300+int(t0*10)+k,al*(1-k/4),n=28)
    k=int(round((t-10.05)*FPS))
    if 0<=k<14: return solid((255,255,255),0.22*(1-k/14))
    return None
p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgba","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","png",f"night_overlay7_{VAR}.mov"],stdin=subprocess.PIPE)
fh=F(MB,78); fl=F(MR,27); fchip=F(MB,46); fsub=F(MR,29); fnote=F(MB,44); ftag=F(MR,24); fend=F(MB,70); flad=F(MB,26); fmech=F(MB,40)
def fmt(n): return f"{int(n):,}"
dummy=ImageDraw.Draw(Image.new("RGBA",(10,10)))
for f in range(N):
    t=f/FPS; im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    if 0.35<=t<2.12:
        a=int(255*(1-sstep(1.95,2.10,t))); n=int((t-0.35)*46)
        if VAR=="A": typed_two(d,290,385,"YOU'RE SEEING","THE PAST.",n,fh,a)
        else:
            HOOK="THIS LIGHT IS OLD."; pre="THIS LIGHT IS "; txt=HOOK[:min(len(HOOK),n)]
            if len(txt)<=len(pre): ctext(d,300,txt,fh,CREAM,a,stroke=6)
            else:
                x0=(W-tw(d,HOOK,fh))/2; d.text((x0,300),pre,font=fh,fill=CREAM+(a,),stroke_width=6,stroke_fill=(0,0,0,min(a,235)))
                xo=x0+tw(d,pre,fh); wo=tw(d,HOOK[len(pre):len(txt)],fh)
                d.rectangle((xo-12,294,xo+wo+12,300+fh.size+10),fill=RED+(int(a*0.97),)); d.text((xo,300),HOOK[len(pre):len(txt)],font=fh,fill=CREAM+(a,))
    # one-line mechanism, right after the snap
    if 2.35<=t<3.1:
        al=sstep(2.35,2.55,t)*(1-sstep(2.85,3.1,t)); n=int((t-2.35)*60)
        txt="LIGHT TAKES TIME TO ARRIVE."[:n]; ctext(d,330,txt,fmech,CREAM,int(255*al),stroke=5)
    shown=False
    for (pt,big,chip,sub,a0,a1) in STOPS_T:
        if a0<=t<a1:
            al=sstep(a0,a0+0.2,t)*(1-sstep(a1-0.3,a1,t)); shown=True; A=int(255*al)
            ctext(d,262,"THE LIGHT YOU SEE LEFT",fl,CREAM,int(A*0.85),sp=7,stroke=3)
            fb=fit(d,big,MB,92,960); ctext(d,306,big,fb,CREAM,A,stroke=6)
            ctext(d,306+fb.size+26,chip,fchip,CREAM,A,sp=4,chip=RED)
            ctext(d,306+fb.size+26+84,sub,fsub,CREAM,int(A*0.92),sp=1,stroke=3)
    if (not shown) and 7.35<=t<10.05:
        u=sstep(7.4,9.9,t); val=4.2*(2.5e6/4.2)**u; al=sstep(7.35,7.55,t)*(1-sstep(9.8,10.05,t)); A=int(255*al)
        ctext(d,262,"THE LIGHT YOU SEE LEFT",fl,CREAM,int(A*0.85),sp=7,stroke=3)
        big=fmt(val)+" YEARS AGO"; fb=fit(d,big,MB,92,960); ctext(d,306,big,fb,CREAM,A,stroke=6)
    # vertical time ladder (NOW at the bottom, deeper past upward)
    if 2.1<=t<12.5:
        fa=sstep(2.1,2.5,t)*(1-sstep(12.0,12.5,t)); A=int(255*fa)
        x=64; d.line((x,LAD_Y[0],x,LAD_Y[-1]),fill=CREAM+(int(A*0.5),),width=3)
        for (nm,_),y in zip(LAD,LAD_Y):
            d.line((x-9,y,x+9,y),fill=CREAM+(int(A*0.85),),width=3)
            xx=x+24
            for c in nm:
                d.text((xx,y-14),c,font=flad,fill=CREAM+(int(A*0.82),),stroke_width=2,stroke_fill=(0,0,0,int(A*0.85))); xx+=d.textlength(c,font=flad)
        u=lad_pos(t); i=min(int(u),3); fr=u-i; my=LAD_Y[i]+(LAD_Y[i+1]-LAD_Y[i])*fr
        d.ellipse((x-11,my-11,x+11,my+11),fill=RED+(A,)); d.ellipse((x-19,my-19,x+19,my+19),outline=RED+(int(A*0.6),),width=2)
    # paradox + red ring on our galaxy dot
    if 13.0<=t<15.5:
        fo=1-sstep(14.8,15.15,t)
        ctext(d,1250,"FROM THERE, YOU'D SEE EARTH",fnote,CREAM,int(255*sstep(13.0,13.3,t)*fo),stroke=5)
        ctext(d,1312,"AS IT WAS 2.5 MILLION YEARS AGO.",fnote,CREAM,int(255*sstep(13.4,13.7,t)*fo),stroke=5)
        ctext(d,1374,"NO MODERN HUMANS YET.",fnote,CREAM,int(255*sstep(13.85,14.15,t)*fo),stroke=5)
        pj=PJ.get(str(min(f,486)))
        if pj and 0<pj[0]<1 and 0<pj[1]<1:
            cx,cy=pj[0]*W,pj[1]*H; ra=sstep(12.6,12.95,t)*(1-sstep(15.2,15.6,t)); rr=(30+4*math.sin(t*6))*(1+2.5*sstep(14.6,15.4,t))
            d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),outline=RED+(int(255*ra),),width=4)
    # ending (stargazer): dissolves in from 20.6, line typed once the sky has settled
    if t>=15.9:
        n=int((t-16.15)*34); a=int(255*(1-sstep(18.5,18.88,t)))
        typed_two(d,1300,1390,"YOU'RE LOOKING","AT THE PAST.",n,fend,a)
    if t>=0.35:
        ta=int(140*(1-sstep(18.5,18.88,t))); d.text((48,1500),"THOUGHT EXPERIMENT  ·  NOT TO SCALE",font=ftag,fill=(235,235,235,ta))
    imp=impact_layer(f)
    if imp is not None: im=Image.alpha_composite(im,imp)
    p.stdin.write(im.tobytes())
p.stdin.close(); p.wait(); print("overlay",VAR,"done")
