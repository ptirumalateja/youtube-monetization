import subprocess, math, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
VAR=sys.argv[1]
W,H,FPS,T=1080,1920,30,19.0; N=int(T*FPS)
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
PASS=[(3.0,"1.3 SEC","THE MOON"),(5.0,"8 MIN 20 SEC","THE SUN"),(7.0,"4.2 YEARS","PROXIMA CENTAURI"),(11.5,"2.5 MILLION YEARS","ANDROMEDA GALAXY")]
STOPS=[(2.1,0.0),(3.0,0.0),(5.0,1/3),(7.0,2/3),(11.5,1.0)]
def marker(Tm):
    for i in range(len(STOPS)-1):
        a,ua=STOPS[i]; b,ub=STOPS[i+1]
        if Tm<=b:
            k=sstep(a+0.3,b-0.05,Tm); return ua+(ub-ua)*k
    return 1.0
def speed_lines(seed,alpha,n=40,ri=(260,560),black_bg=False):
    rr=np.random.default_rng(seed); im=Image.new("RGBA",(W,H),(0,0,0,int(255*0.55) if black_bg else 0)); d=ImageDraw.Draw(im)
    cx,cy=540,900
    for _ in range(n):
        a=rr.random()*6.283; r0=rr.uniform(*ri); w=rr.uniform(0.003,0.010); r1=1700
        p=[(cx+r0*math.cos(a),cy+r0*math.sin(a)),(cx+r1*math.cos(a-w),cy+r1*math.sin(a-w)),(cx+r1*math.cos(a+w),cy+r1*math.sin(a+w))]
        d.polygon(p,fill=(255,255,255,int(255*alpha)))
    return im
def solid(c,a): return Image.new("RGBA",(W,H),c+(int(255*a),))
def impact_layer(f):
    t=f/FPS
    if 1.95<=t<2.1: return solid((255,255,255),0.5*sstep(1.95,2.1,t))
    if 2.1<=t<2.26: return solid((255,255,255),0.5*(1-sstep(2.1,2.26,t)))
    for t0 in (3.0,5.0,7.0):
        k=int(round((t-t0)*FPS))
        if 0<=k<5:
            lay=speed_lines(300+int(t0*10)+k,0.35*(1-k/5),n=36)
            if k==0: lay=Image.alpha_composite(lay,solid((255,255,255),0.16))
            return lay
    k=int(round((t-11.5)*FPS))
    if 0<=k<19:
        a=0.85 if k<3 else 0.85*(1-(k-3)/16); return solid((255,255,255),a)
    if 16.0<=t<16.3: return solid((0,0,0),1.0)
    return None
p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgba","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","png",f"night_overlay4_{VAR}.mov"],stdin=subprocess.PIPE)
fh=F(MB,78); fl=F(MR,27); fc=F(MB,88); fchip=F(MB,46); fnote=F(MB,46); ftag=F(MR,24); fend=F(MB,70); frul=F(MR,30)
for f in range(N):
    t=f/FPS; im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    # hook
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
    # counter + ruler 2.1..14.0
    if 2.1<=t<14.0:
        fa=sstep(2.1,2.35,t)*(1-sstep(13.6,14.0,t)); A=int(255*fa)
        # ruler
        x0,x1,y=190,890,560
        d.line((x0,y,x1,y),fill=CREAM+(int(A*0.55),),width=3)
        for i,(pt,_,lab) in enumerate(PASS):
            xx=x0+(x1-x0)*i/3; d.line((xx,y-10,xx,y+10),fill=CREAM+(int(A*0.8),),width=3)
            nm=["MOON","SUN","PROXIMA","ANDROMEDA"][i]; w=tw(d,nm,frul,2)
            xx2=xx-w/2
            for c in nm:
                d.text((xx2,y+20),c,font=frul,fill=CREAM+(int(A*0.75),),stroke_width=2,stroke_fill=(0,0,0,int(A*0.8))); xx2+=d.textlength(c,font=frul)+2
        mx=x0+(x1-x0)*marker(t); d.polygon([(mx,y-4),(mx-11,y-24),(mx+11,y-24)],fill=RED+(A,)); d.ellipse((mx-5,y-5,mx+5,y+5),fill=RED+(A,))
        # counter windows
        for i,(pt,txt,lab) in enumerate(PASS):
            last=(i==3); a0=pt-0.15; a1=14.0 if last else pt+0.75
            if a0<=t<a1:
                al=sstep(a0,a0+0.1,t)*(1-(sstep(13.6,14.0,t) if last else sstep(a1-0.2,a1,t)))
                ctext(d,296,"AGE OF THE LIGHT",fl,CREAM,int(255*al*0.8),sp=9,stroke=3)
                ctext(d,336,txt,fc,CREAM,int(255*al),stroke=6)
                ctext(d,452,lab,fchip,CREAM,int(255*al),sp=4,chip=RED)
    if 14.0<=t<16.0:
        a1=int(255*sstep(14.0,14.35,t)); a2=int(255*sstep(14.5,14.85,t))
        ctext(d,1330,"THIS LIGHT LEFT BEFORE",fnote,CREAM,a1,stroke=5)
        ctext(d,1395,"HOMO SAPIENS EXISTED.",fnote,CREAM,a2,stroke=5)
    if t>=16.3:
        n=int((t-16.4)*34); a=int(255*(1-sstep(18.65,19.0,t)))
        typed_two(d,1300,1390,"YOU'RE LOOKING","AT THE PAST.",n,fend,a)
    if not (16.0<=t<16.3) and t>=0.35:
        ta=int(140*(1-sstep(18.65,19.0,t))); d.text((48,1500),"THOUGHT EXPERIMENT  ·  NOT TO SCALE",font=ftag,fill=(235,235,235,ta))
    imp=impact_layer(f)
    if imp is not None: im=Image.alpha_composite(im,imp)
    p.stdin.write(im.tobytes())
p.stdin.close(); p.wait(); print("overlay",VAR,"done")
