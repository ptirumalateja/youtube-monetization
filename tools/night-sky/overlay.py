import subprocess, math, numpy as np
from PIL import Image, ImageDraw, ImageFont
W,H,FPS,T=1080,1920,30,18.0; N=int(T*FPS)
MB="/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"; MR="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"; SB="/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
def F(p,s): return ImageFont.truetype(p,s)
CREAM=(246,240,228); RED=(214,62,48); TEAL=(84,176,176)
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
# ---------- counter value
PASS=[3.0,4.8,6.6,8.4,11.5]; YR=3.15576e7
VAL=[0.0,1.28,499.0,4.24*YR,600*YR,2.5e6*YR]; TS=[2.1]+PASS
def val(Tm):
    if Tm<=TS[0]: return 0.0
    for i in range(len(PASS)):
        a,b=TS[i],TS[i+1]
        if Tm<=b:
            hold=0.45 if i>0 else 0.0
            u=clamp((Tm-(a+hold))/max(0.01,(b-0.04)-(a+hold)))
            u=u*u*(3-2*u)*0+u
            if i==0: return VAL[1]*u
            lo,hi=math.log10(VAL[i]),math.log10(VAL[i+1]); return 10**(lo+(hi-lo)*u)
    return VAL[-1]
def fmt(s):
    if s<59.95: return f"{s:.1f} SEC"
    if s<3600: return f"{int(s//60)} MIN {int(s%60):02d} SEC"
    if s<86400: return f"{s/3600:.0f} HOURS"
    if s<YR: return f"{s/86400:.0f} DAYS"
    y=s/YR
    if y<10: return f"{y:.1f} YEARS"
    if y<1e6: return f"{y:,.0f} YEARS" 
    return f"{y/1e6:.1f} MILLION YEARS"
LABEL=[(3.0,"THE MOON"),(4.8,"THE SUN"),(6.6,"PROXIMA CENTAURI"),(8.4,"BETELGEUSE"),(11.5,"ANDROMEDA GALAXY")]
EXACT={3.0:"1.3 SEC",4.8:"8 MIN 20 SEC",6.6:"4.2 YEARS",8.4:"~600 YEARS",11.5:"2.5 MILLION YEARS"}
# ---------- speed lines
def speed_lines(seed,alpha,n=80,ri=(200,520),white=True,black_bg=False):
    rr=np.random.default_rng(seed); im=Image.new("RGBA",(W,H),(0,0,0,255 if black_bg else 0)); d=ImageDraw.Draw(im)
    cx,cy=540,900
    for _ in range(n):
        a=rr.random()*6.283; r0=rr.uniform(*ri); w=rr.uniform(0.004,0.016); r1=1700
        p=[(cx+r0*math.cos(a),cy+r0*math.sin(a)),(cx+r1*math.cos(a-w),cy+r1*math.sin(a-w)),(cx+r1*math.cos(a+w),cy+r1*math.sin(a+w))]
        d.polygon(p,fill=(255,255,255,int(255*alpha)))
    return im
IMP=[(1.70,'big'),(3.0,'med'),(4.8,'med'),(6.6,'med'),(8.4,'med'),(11.5,'white')]
def impact_layer(f):
    t=f/FPS; base=None
    for t0,kind in IMP:
        k=int(round((t-t0)*FPS))
        if k<0: continue
        if kind=='big':
            if k in (0,1): return Image.new("RGBA",(W,H),(255,255,255,255))
            if k in (2,3): return speed_lines(100+k,1.0,n=110,ri=(120,420),black_bg=True)
            if k<10: return speed_lines(200+k,0.9*(1-(k-4)/6),n=90,ri=(180,500))
        if kind=='med' and k<6:
            lay=speed_lines(300+int(t0*10)+k,0.8*(1-k/6),n=60,ri=(260,560))
            if k<2: lay=Image.alpha_composite(lay,Image.new("RGBA",(W,H),(255,255,255,int(255*0.5))))
            return lay
        if kind=='white' and k<19:
            a=1.0 if k<4 else 1-(k-4)/15; return Image.new("RGBA",(W,H),(255,255,255,int(255*a)))
    if 16.0<=t<16.3: return Image.new("RGBA",(W,H),(0,0,0,255))
    return None
p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgba","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","png","night_overlay.mov"],stdin=subprocess.PIPE)
fh=F(MB,78); fl=F(MR,27); fc=F(MB,88); fchip=F(MB,46); fb=F(MB,52); ftag=F(MR,24); fend=F(MB,70); fnote=F(MB,46)
HOOK="THIS LIGHT IS OLD."
for f in range(N):
    t=f/FPS; im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    # hook 0.2..1.7, typed 0.2-0.7 (26 cps)
    if 0.2<=t<1.72:
        n=min(len(HOOK),int((t-0.2)*30)); a=int(255*(1-clamp((t-1.55)/0.17)))
        txt=HOOK[:n]
        if n<=len("THIS LIGHT IS "): ctext(d,300,txt,fh,CREAM,a,stroke=6)
        else:
            full_w=tw(d,HOOK,fh); x0=(W-full_w)/2; pre="THIS LIGHT IS "; 
            d.text((x0,300),pre,font=fh,fill=CREAM+(a,),stroke_width=6,stroke_fill=(0,0,0,min(a,235)))
            xo=x0+tw(d,pre,fh); wo=tw(d,HOOK[len(pre):n],fh)
            d.rectangle((xo-12,294,xo+wo+12,300+fh.size+10),fill=RED+(int(a*0.96),))
            d.text((xo,300),HOOK[len(pre):n],font=fh,fill=CREAM+(a,),stroke_width=0)
    # counter 2.1..14.0
    if 2.1<=t<14.0:
        a=int(255*sstep(2.1,2.35,t)*(1-sstep(13.6,14.0,t)))
        s=val(t); txt=fmt(s)
        for pt,ex in EXACT.items():
            if abs(t-pt)<0.5/FPS+0.35 and t>=pt: txt=ex
        ctext(d,296,"AGE OF THE LIGHT",fl,CREAM,int(a*0.8),sp=9,stroke=3)
        ctext(d,336,txt,fc,CREAM,a,stroke=6)
        lab=None
        for i,(pt,l) in enumerate(LABEL):
            nxt=LABEL[i+1][0]-0.08 if i+1<len(LABEL) else 14.0
            if pt<=t<nxt: lab=(pt,l)
        if lab and t>=lab[0]:
            last=(lab[0]==11.5)
            fade=(1-sstep(13.6,14.0,t)) if last else (1-sstep(lab[0]+0.42,lab[0]+0.58,t))
            la=int(255*sstep(lab[0],lab[0]+0.1,t)*fade)
            if la>0: ctext(d,452,lab[1],fchip,CREAM,la,sp=4,chip=RED)
    # hold lines 14..16
    if 14.0<=t<16.0:
        a1=int(255*sstep(14.0,14.35,t)); a2=int(255*sstep(14.5,14.85,t))
        ctext(d,1330,"THIS LIGHT LEFT BEFORE",fnote,CREAM,a1,stroke=5)
        ctext(d,1395,"MODERN HUMANS EXISTED.",fnote,CREAM,a2,stroke=5)
    # end lines 16.3..18
    if t>=16.3:
        n=int((t-16.4)*30); l1="YOU'RE LOOKING"; l2="AT THE PAST."
        a=255
        if n>0:
            ctext(d,1300,l1[:min(len(l1),n)],fend,CREAM,a,stroke=6)
        if n>len(l1):
            m=min(len(l2),n-len(l1)); w2=tw(d,l2,fend); x0=(W-w2)/2
            pre=l2[:m]
            if m>=3:
                d.rectangle((x0-14,1390-4,x0+tw(d,pre,fend)+14,1390+fend.size+8),fill=RED+(250,))
            d.text((x0,1390),pre,font=fend,fill=CREAM+(255,),stroke_width=0 if m>=3 else 6,stroke_fill=(0,0,0,235))
    if t>=0.0 and not (16.0<=t<16.3):
        d.text((48,1500),"THOUGHT EXPERIMENT  ·  NOT TO SCALE",font=ftag,fill=(235,235,235,140))
    imp=impact_layer(f)
    if imp is not None: im=Image.alpha_composite(im,imp)
    p.stdin.write(im.tobytes())
p.stdin.close(); p.wait(); print("overlay done")
