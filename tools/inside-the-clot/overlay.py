# python3 overlay.py proj.json out.mov  -> RGBA overlay (text, counters, markers, flashes) for Inside the Clot, 1080x1920, 24 s
import subprocess, math, sys, json
from PIL import Image, ImageDraw, ImageFont
PJ=json.load(open(sys.argv[1])); OUT=sys.argv[2]
W,H,FPS,T=1080,1920,30,24.0; N=int(T*FPS)
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
def flash(t):
    for ts,amp in ((2.25,0.14),(13.55,0.12)):
        k=t-ts
        if -0.03<=k<0.2: return solid((255,250,240),amp*(1-clamp(k/0.2)))
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
    t=f/FPS; im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    # hook
    if 0.25<=t<2.2:
        a=int(255*(1-sstep(2.0,2.2,t))); n=int((t-0.25)*24)+1
        l1="A HEART ATTACK"; ctext(d,300,l1[:min(len(l1),n)],fh,CREAM,a,stroke=6)
        if n>len(l1): typed_chip_line(d,396,"STARTS WITH A CRACK.","STARTS WITH A ",n-len(l1),fh,a)
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
    if t>=0.25:
        ta=int(140*(1-sstep(23.7,23.95,t))); d.text((48,1500),"ILLUSTRATION · NOT TO SCALE · TIME COMPRESSED",font=ftag,fill=(235,235,235,ta))
    fl_=flash(t)
    if fl_ is not None: im=Image.alpha_composite(im,fl_)
    if t>=23.72: im=Image.alpha_composite(im,solid((0,0,0),0.9*sstep(23.72,24.0,t)))
    p.stdin.write(im.tobytes())
p.stdin.close(); p.wait(); print("overlay done")
