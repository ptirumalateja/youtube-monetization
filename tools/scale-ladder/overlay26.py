import subprocess, math, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.argv=[sys.argv[0]]+sys.argv[1:]; VAR=sys.argv[1]
import json; PJ=json.load(open('w3d/proj.json'))
W,H,FPS,T=1080,1920,30,26.0; N=int(T*FPS)
MB="/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"; MR="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
def F(p,s): return ImageFont.truetype(p,s)
CREAM=(246,240,228); RED=(214,62,48); GOLD=(255,200,110)
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
def typed_two(d,y1,y2,l1,l2,n,font,a):
    s1=l1[:min(len(l1),n)]
    if s1: ctext(d,y1,s1,font,CREAM,a,stroke=6)
    if n>len(l1):
        m=min(len(l2),n-len(l1)); w2=tw(d,l2,font); x0=(W-w2)/2; pre=l2[:m]
        d.rectangle((x0-14,y2-4,x0+tw(d,pre,font)+14,y2+font.size+8),fill=RED+(int(a*0.97),)); d.text((x0,y2),pre,font=font,fill=CREAM+(a,))
def speed_lines(seed,alpha,n=36):
    rr=np.random.default_rng(seed); im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im); cx,cy=540,960
    for _ in range(n):
        a=rr.random()*6.283; r0=rr.uniform(280,600); w=rr.uniform(0.003,0.009); r1=1700
        p=[(cx+r0*math.cos(a),cy+r0*math.sin(a)),(cx+r1*math.cos(a-w),cy+r1*math.sin(a-w)),(cx+r1*math.cos(a+w),cy+r1*math.sin(a+w))]
        d.polygon(p,fill=(255,255,255,int(255*alpha)))
    return im
def solid(c,a): return Image.new("RGBA",(W,H),c+(int(255*a),))
TS=[5.4,11.0,22.5]
def impact(f):
    t=f/FPS
    for ts in TS:
        k=int(round((t-ts)*FPS))
        if 0<=k<4:
            lay=speed_lines(500+int(ts*10)+k,0.22*(1-k/4))
            return Image.alpha_composite(lay,solid((255,255,255),0.08)) if k==0 else lay
    k=int(round((t-18.0)*FPS))
    if 0<=k<14: return solid((255,255,255),0.34*(1-k/14))
    k=int(round((t-24.1)*FPS))
    if 0<=k<6: return solid((255,255,255),0.30*(1-k/6))
    return None
STOPS=[(2.0,5.4,"WIDER THAN EARTH","109×","THE SUN","1.3 MILLION EARTHS FIT INSIDE",2),
       (7.6,11.0,"WIDER THAN THE SUN","6,500×","SOLAR SYSTEM","TO NEPTUNE'S ORBIT",3),
       (13.0,17.9,"WIDER THAN THE SOLAR SYSTEM","100 MILLION×","MILKY WAY","~100,000 LIGHT-YEARS ACROSS",4),
       (20.0,22.5,"WIDER THAN THE MILKY WAY","930,000×","OBSERVABLE UNIVERSE","~93 BILLION LIGHT-YEARS ACROSS",5)]
def PBpos(k,f):
    f=min(f,len(PJ)-1)
    if k==2: a=PJ[f][0]
    else: a=PJ[f][1]
    return (a[0]*W,a[1]*H)
RUNG_Y={1:1260,2:1140,3:1020,4:900,5:780}
p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgba","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","png",f"ladder_overlay_{VAR}.mov"],stdin=subprocess.PIPE)
fh=F(MB,78); fl=F(MR,27); fc=F(MB,100); fchip=F(MB,44); fsub=F(MR,26); ftag=F(MR,24); fend=F(MB,76)
for f in range(N):
    t=f/FPS; im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    if 0.30<=t<2.0:
        a=int(255*(1-sstep(1.8,2.0,t))); n=int((t-0.30)*40)
        if VAR=="A":
            full="EARTH IS A DOT."; pre="EARTH IS A "; txt=full[:min(len(full),n)]
            if len(txt)<=len(pre): ctext(d,300,txt,fh,CREAM,a,stroke=6)
            else:
                x0=(W-tw(d,full,fh))/2; d.text((x0,300),pre,font=fh,fill=CREAM+(a,),stroke_width=6,stroke_fill=(0,0,0,min(a,235)))
                xo=x0+tw(d,pre,fh); wo=tw(d,full[len(pre):len(txt)],fh)
                d.rectangle((xo-12,294,xo+wo+12,300+fh.size+10),fill=RED+(int(a*0.97),)); d.text((xo,300),full[len(pre):len(txt)],font=fh,fill=CREAM+(a,))
        else: typed_two(d,290,385,"1.3 MILLION EARTHS","FIT INSIDE THE SUN.",n,fh,a)
    for (a0,a1,lab,cnt,chip,sub,k) in STOPS:
        if a0<=t<a1:
            al=sstep(a0,a0+0.18,t)*(1-sstep(a1-0.2,a1,t)); A=int(255*al)
            ctext(d,296,lab,fl,CREAM,int(A*0.85),sp=7,stroke=3); ctext(d,330,cnt,fc,CREAM,A,stroke=6)
            ctext(d,452,chip,fchip,CREAM,A,sp=4,chip=RED); ctext(d,526,sub,fsub,CREAM,int(A*0.85),sp=2,stroke=3)
            # marker ring around the previous scene's blob
            cx,cy=PBpos(k,f); rr=(34 if k==2 else 26)+4*math.sin(t*6); A=int(A*sstep(a0+0.2,a0+0.5,t)); d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),outline=RED+(int(A*0.95),),width=3)
    # ladder UI
    if 2.0<=t<22.5:
        la=sstep(2.0,2.3,t)*(1-sstep(22.2,22.5,t)); LA=int(255*la)
        cur=2 if t<6.5 else 3 if t<12.0 else 4 if t<19.0 else 5
        d.line((64,RUNG_Y[5],64,RUNG_Y[1]),fill=CREAM+(int(LA*0.5),),width=3)
        for k in range(1,6):
            y=RUNG_Y[k]
            if k==cur: d.ellipse((64-11,y-11,64+11,y+11),fill=RED+(LA,))
            elif k<cur: d.ellipse((64-6,y-6,64+6,y+6),fill=CREAM+(int(LA*0.9),))
            else: d.ellipse((64-6,y-6,64+6,y+6),outline=CREAM+(int(LA*0.7),),width=2)
    # ending
    if t>=24.1:
        ra=sstep(24.4,24.7,t)*(1-sstep(25.5,25.8,t)); cx,cy=PBpos(5,0)[0],960; cx=540; rr=285+6*math.sin(t*5)
        d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),outline=RED+(int(255*ra),),width=5)
        n=int((t-24.5)*34); a=int(255*(1-sstep(25.5,25.8,t)))
        if n>0:
            full="YOU ARE HERE."; pre="YOU ARE "; txt=full[:min(len(full),n)]
            if len(txt)<=len(pre): ctext(d,1300,txt,fend,CREAM,a,stroke=6)
            else:
                x0=(W-tw(d,full,fend))/2; d.text((x0,1300),pre,font=fend,fill=CREAM+(a,),stroke_width=6,stroke_fill=(0,0,0,min(a,235)))
                xo=x0+tw(d,pre,fend); wo=tw(d,full[len(pre):len(txt)],fend)
                d.rectangle((xo-12,1294,xo+wo+12,1300+fend.size+10),fill=RED+(int(a*0.97),)); d.text((xo,1300),full[len(pre):len(txt)],font=fend,fill=CREAM+(a,))
    if t>=0.30 and not (False):
        ta=int(140*(1-sstep(25.4,25.8,t))); d.text((48,1500),"THOUGHT EXPERIMENT  ·  NOT TO SCALE",font=ftag,fill=(235,235,235,ta))
    imp=impact(f)
    if imp is not None: im=Image.alpha_composite(im,imp)
    ba=0.0
    if t>=25.6: ba=0.88*sstep(25.6,26.0,t)
    if ba>0: im=Image.alpha_composite(im,solid((0,0,0),ba)) if ba<1 else Image.alpha_composite(Image.new('RGBA',(W,H),(0,0,0,255)),Image.new('RGBA',(W,H),(0,0,0,0)))
    p.stdin.write(im.tobytes())
p.stdin.close(); p.wait(); print("overlay",VAR,"done")
