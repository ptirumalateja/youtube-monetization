import subprocess, math, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
VAR=sys.argv[1]
import json; PJ=json.load(open('n3d/proj5.json'))
W,H,FPS,T=1080,1920,30,19.17; N=int(T*FPS)
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
def eout(u): u=clamp(u); return 1-(1-u)**3
YR=3.156e7
def fmt_age(v):
    """one odometer: seconds -> minutes -> hours -> days -> years. v is in SECONDS."""
    if v<10: return f"{v:.1f} SECONDS AGO"
    if v<60: return f"{int(v)} SECONDS AGO"
    if v<3600: return f"{int(v//60)} MIN {int(v%60):02d} SEC AGO"
    if v<86400:
        h=int(v//3600); return f"{h} HOUR{'S' if h!=1 else ''} {int((v%3600)//60):02d} MIN AGO"
    if v<YR:
        dd=int(v//86400); return f"{dd} DAY{'S' if dd!=1 else ''} AGO"
    y=v/YR
    if y<100: return f"{y:.1f} YEARS AGO"
    return f"{int(y):,} YEARS AGO"
def gl(a,b,u): return a*(b/a)**clamp(u)          # geometric interpolation (sec -> years spans 8 orders of magnitude)
# ONE monotonic odometer across the whole video (seconds). value(t) never decreases.
def age(t):
    if t<3.3: return 0.0
    if t<4.1: return 1.3*eout((t-3.3)/0.8)
    if t<5.2: return 1.3
    if t<6.0: return gl(1.3,500.0,eout((t-5.2)/0.8))
    if t<7.1: return 500.0
    if t<7.9: return gl(500.0,4.2*YR,eout((t-7.1)/0.8))
    if t<8.45: return 4.2*YR
    if t<9.9: return gl(4.2*YR,2.1e6*YR,(t-8.45)/1.45)
    if t<10.9: return 2.1e6*YR
    if t<11.7: return 2.1e6*YR+(2.5e6-2.1e6)*YR*eout((t-10.9)/0.8)
    return 2.5e6*YR
_prev=-1.0
for _f in range(int(19.17*30)):
    _v=age(_f/30.0); assert _v>=_prev-1e-6,("counter went backwards at",_f/30.0,_v,_prev); _prev=_v
STOPS_T=[(3.30,"THE MOON","MOONLIGHT TAKES 1.3 SECONDS TO ARRIVE",4.45),
         (5.20,"THE SUN","IF IT VANISHED NOW, YOU'D STILL SEE IT",6.45),
         (7.10,"PROXIMA CENTAURI","THE NEAREST STAR AFTER THE SUN",8.35),
         (10.90,"ANDROMEDA GALAXY","BEFORE MODERN HUMANS EXISTED",13.0)]
LAD=["NOW","MOON","SUN","PROXIMA","ANDROMEDA"]
LAD_Y=[1420,1260,1100,940,780]
def lad_pos(t):
    ks=[(2.1,0.0),(3.3,1.0),(5.2,2.0),(7.1,3.0),(10.9,4.0)]
    for i in range(len(ks)-1):
        a,ua=ks[i]; b,ub=ks[i+1]
        if t<=b: return ua+(ub-ua)*sstep(a+0.2,b-0.05,t)
    return 4.0
def impact_layer(f):
    t=f/FPS
    if 2.08<=t<2.2: return solid((255,255,255),0.14*(1-(t-2.08)/0.12))
    k=int(round((t-10.55)*FPS))
    if 0<=k<10: return solid((255,255,255),0.08*(1-k/10))
    return None
p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgba","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","png",f"night_overlay81_{VAR}.mov"],stdin=subprocess.PIPE)
fh=F(MB,78); fl=F(MR,27); fchip=F(MB,46); fsub=F(MR,29); fcap=F(MB,54); fcapc=F(MB,42); ftag=F(MR,24); fend=F(MB,70); flad=F(MB,36); fladA=F(MB,42)
_dd=ImageDraw.Draw(Image.new("RGBA",(10,10))); FB=fit(_dd,"2,500,000 YEARS AGO",MB,92,960)   # one counter size for every stop
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
    shown=False
    for (t0,chip,sub,t1) in STOPS_T:
        if t0<=t<t1:
            shown=True; al=sstep(t0,t0+0.15,t)*(1-sstep(t1-0.3,t1,t)); A=int(255*al)
            ctext(d,262,"THE LIGHT YOU SEE LEFT",fl,CREAM,int(A*0.85),sp=7,stroke=3)
            ctext(d,306,fmt_age(age(t)),FB,CREAM,A,stroke=6)
            ca=int(A*sstep(t0+0.35,t0+0.6,t))
            ctext(d,306+FB.size+26,chip,fchip,CREAM,ca,sp=4,chip=RED)
            ctext(d,306+FB.size+26+84,sub,fsub,CREAM,int(ca*0.92),sp=1,stroke=3)
    if (not shown) and 8.45<=t<10.05:
        al=sstep(8.45,8.65,t)*(1-sstep(9.8,10.05,t)); A=int(255*al)
        ctext(d,262,"THE LIGHT YOU SEE LEFT",fl,CREAM,int(A*0.85),sp=7,stroke=3)
        ctext(d,306,fmt_age(age(t)),FB,CREAM,A,stroke=6)
    # time ladder: names only, active rung lit, big red marker
    if 2.1<=t<12.5:
        fa=sstep(2.1,2.5,t)*(1-sstep(12.0,12.5,t)); A=int(255*fa)
        x=64; u=lad_pos(t); act=int(round(u)); d.line((x,LAD_Y[0],x,LAD_Y[-1]),fill=CREAM+(int(A*0.55),),width=4)
        for i,(nm,y) in enumerate(zip(LAD,LAD_Y)):
            on=(i==act and u>0.02) or (i==0 and u<=0.5)
            d.line((x-12,y,x+12,y),fill=(CREAM+(A,)) if on else (CREAM+(int(A*0.6),)),width=4)
            font=fladA if on else flad; xx=x+30; al_=A if on else int(A*0.62)
            for c in nm:
                d.text((xx,y-font.size//2-2),c,font=font,fill=CREAM+(al_,),stroke_width=3,stroke_fill=(0,0,0,int(al_*0.9))); xx+=d.textlength(c,font=font)
        i=min(int(u),3); fr=u-i; my=LAD_Y[i]+(LAD_Y[i+1]-LAD_Y[i])*fr; pr=24+4*math.sin(t*6)
        d.ellipse((x-15,my-15,x+15,my+15),fill=RED+(A,)); d.ellipse((x-pr,my-pr,x+pr,my+pr),outline=RED+(int(A*0.65),),width=3)
    # paradox caption: bigger, simplified, held longer
    if 13.2<=t<16.1:
        fo=1-sstep(15.7,16.05,t)
        ctext(d,1130,"FROM THERE, YOU'D SEE EARTH",fcap,CREAM,int(255*sstep(13.2,13.5,t)*fo),stroke=6)
        ctext(d,1196,"AS IT WAS 2.5 MILLION",fcap,CREAM,int(255*sstep(13.6,13.9,t)*fo),stroke=6)
        ctext(d,1262,"YEARS AGO.",fcap,CREAM,int(255*sstep(13.8,14.1,t)*fo),stroke=6)
        ctext(d,1344,"NO MODERN HUMANS YET.",fcapc,CREAM,int(255*sstep(14.4,14.7,t)*fo),sp=3,chip=RED)
    if 12.9<=t<16.3:
        pj=PJ.get(str(min(f,498)))
        if pj and 0<pj[0]<1 and 0<pj[1]<1:
            cx,cy=pj[0]*W,pj[1]*H; ra=sstep(13.0,13.4,t)*(1-sstep(16.0,16.35,t)); rr=(36+4*math.sin(t*6))*(1+2.0*sstep(15.2,16.0,t))
            d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),outline=RED+(int(255*ra),),width=5)
    if t>=16.17:
        n=int((t-16.57)*34); a=int(255*(1-sstep(18.8,19.17,t)))
        typed_two(d,1300,1390,"YOU'RE LOOKING","AT THE PAST.",n,fend,a)
    if t>=0.35:
        ta=int(140*(1-sstep(18.8,19.17,t))); d.text((48,1500),"THOUGHT EXPERIMENT  ·  NOT TO SCALE",font=ftag,fill=(235,235,235,ta))
    imp=impact_layer(f)
    if imp is not None: im=Image.alpha_composite(im,imp)
    p.stdin.write(im.tobytes())
p.stdin.close(); p.wait(); print("overlay",VAR,"done (counter monotonic: verified)")
