# Photon Rain overlay: hook, sensor labels, zoom counter, photon counters, pixel markers, end line.
# Reads the per-frame projections the renderer wrote (frames/fNNNN.json) and pipes an RGBA PNG .mov to ffmpeg.
import subprocess, math, json, sys
from PIL import Image, ImageDraw, ImageFont
FR=sys.argv[1] if len(sys.argv)>1 else 'frames'; OUT=sys.argv[2] if len(sys.argv)>2 else 'photon_overlay.mov'
W,H,FPS,T=1080,1920,30,22.0; N=int(T*FPS)
MB="/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"; MR="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
def F(p,s): return ImageFont.truetype(p,s)
CREAM=(246,240,228); RED=(214,62,48); GOLD=(255,196,96); TEALC=(90,215,205)
def clamp(x): return max(0.0,min(1.0,x))
def sstep(a,b,x): k=clamp((x-a)/(b-a)); return k*k*(3-2*k)
def smr(a,b,x): k=clamp((x-a)/(b-a)); return k*k*k*(k*(6*k-15)+10)
def win(t,a,b,fi=0.18,fo=0.2): return sstep(a,a+fi,t)*(1-sstep(b-fo,b,t))
def tw(d,txt,font,sp=0): return sum(d.textlength(c,font=font)+sp for c in txt)-sp if sp else d.textlength(txt,font=font)
def text(d,x,y,txt,font,fill,a=255,sp=0,stroke=0,chip=None,anchor='l'):
    w=tw(d,txt,font,sp)
    if anchor=='c': x=x-w/2
    elif anchor=='r': x=x-w
    if chip is not None:
        pad=14; d.rectangle((x-pad,y-6,x+w+pad,y+font.size+8),fill=chip+(int(a*0.96),))
    if sp:
        for c in txt:
            d.text((x,y),c,font=font,fill=fill+(a,),stroke_width=stroke,stroke_fill=(0,0,0,min(a,235))); x+=d.textlength(c,font=font)+sp
    else: d.text((x,y),txt,font=font,fill=fill+(a,),stroke_width=stroke,stroke_fill=(0,0,0,min(a,235)))
    return w
def typed(d,y,l1,l2,n,font,a,chip2=True):
    # line 1 cream with stroke, line 2 on a red chip; typing always starts at n>=1
    if n<1: return
    s1=l1[:min(len(l1),n)]; text(d,W/2-tw(d,l1,font)/2,y,s1,font,CREAM,a,stroke=6)
    if n>len(l1):
        m=min(len(l2),n-len(l1)); pre=l2[:m]; x0=W/2-tw(d,l2,font)/2; y2=y+font.size+26
        if chip2: d.rectangle((x0-14,y2-6,x0+tw(d,pre,font)+14,y2+font.size+8),fill=RED+(int(a*0.97),)); d.text((x0,y2),pre,font=font,fill=CREAM+(a,))
        else: text(d,x0,y2,pre,font,CREAM,a,stroke=6)
def P(p): return (p[0]*W,p[1]*H)
def solid(c,a): return Image.new("RGBA",(W,H),c+(int(255*a),))
# camera distance (mirrors camAt in index.html) for the zoom counter
D0,DM,DM2=86000,78,64
def lerp(a,b,k): return a+(b-a)*k
def lD(t):
    l0,lm,lm2=math.log(D0),math.log(DM),math.log(DM2)
    if t<6.6: return l0-0.10*sstep(0,6.6,t)
    if t<9.2: return lerp(l0-0.10,lm,smr(6.6,9.2,t))
    return lerp(lm,lm2,sstep(9.2,15.3,t))
ZREF=math.exp(math.log(D0)-0.10)
def fmt(n): return f"{int(n):,}"
fh=F(MB,84); fhs=F(MB,64); flab=F(MB,40); fsmall=F(MR,27); fcnt=F(MB,92); fcnt2=F(MB,60); fcap=F(MB,50); ftag=F(MR,24); fchip=F(MB,44); fend=F(MB,66)
p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgba","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","png",OUT],stdin=subprocess.PIPE)
prev={'ph':-1,'ff':-1,'z':0}
for f in range(N):
    t=f/FPS; I=json.load(open(f"{FR}/f{f:04d}.json"))
    im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    # ---- hook (typed by ~1.6 s)
    if 0.15<=t<2.3:
        a=int(255*(1-sstep(2.05,2.3,t))); typed(d,210,"200 MEGAPIXELS","LOSES TO 24.",int((t-0.15)*20),fh,a)
    # ---- sensor labels during the overview
    if t<6.8:
        a=int(255*win(t,0.5,6.8,0.25,0.3)); phx,phy=P(I['phR']); ffx,ffy=P(I['ffBot'])
        text(d,phx+28,phy-58,"PHONE",flab,CREAM,a,sp=3,stroke=4); text(d,phx+28,phy-8,"200 MP",flab,GOLD,a,stroke=4)
        text(d,W/2,ffy+26,"CAMERA  ·  24 MP",flab,CREAM,a,sp=2,stroke=4,anchor='c')
    if 2.3<=t<4.3:
        a=int(255*win(t,2.3,4.3)); text(d,W/2,230,"SAME LIGHT.",fcap,CREAM,a,stroke=5,anchor='c'); text(d,W/2,300,"SAME SHUTTER.",fcap,CREAM,a,stroke=5,anchor='c')
    if 4.3<=t<6.7:
        a=int(255*win(t,4.3,6.7)); text(d,W/2,214,"THE CAMERA SENSOR HAS",fsmall,CREAM,int(a*0.9),sp=5,stroke=3,anchor='c')
        text(d,W/2,262,"12× THE AREA",fchip,CREAM,a,sp=3,chip=RED,anchor='c'); text(d,W/2,338,"SO IT CATCHES 12× THE LIGHT",fsmall,CREAM,int(a*0.9),sp=2,stroke=3,anchor='c')
    # ---- dive: zoom counter (monotonic)
    if 6.75<=t<9.6:
        a=int(255*win(t,6.75,9.6,0.2,0.3)); z=max(prev['z'],ZREF/math.exp(lD(t))); prev['z']=z
        text(d,W/2,224,"ZOOM",fsmall,CREAM,int(a*0.85),sp=8,stroke=3,anchor='c'); text(d,W/2,262,"×"+fmt(round(z)),fcnt,CREAM,a,stroke=6,anchor='c')
    if 8.6<=t<11.0:
        a=int(255*win(t,8.6,11.0,0.25,0.25)); text(d,W/2,1250,"1 CAMERA PIXEL",fcap,CREAM,a,stroke=5,anchor='c'); text(d,W/2,1320,"= 100 PHONE PIXELS",fcap,GOLD,a,stroke=5,anchor='c')
    # ---- buckets: two photon counters (monotonic), red markers on the two followed pixels
    if 9.45<=t<15.0:
        a=int(255*win(t,9.45,15.0,0.25,0.35)); cph=max(prev['ph'],I['cPh']); cff=max(prev['ff'],I['cFF']); prev['ph']=cph; prev['ff']=cff
        text(d,W/2,200,"PHOTONS CAUGHT",fsmall,CREAM,int(a*0.85),sp=7,stroke=3,anchor='c')
        text(d,150,246,"PHONE PIXEL",flab,CREAM,int(a*0.9),sp=1,stroke=4); text(d,W-150,236,fmt(cph),fcnt2,GOLD,a,stroke=5,anchor='r')
        text(d,150,326,"CAMERA PIXEL",flab,CREAM,int(a*0.9),sp=1,stroke=4); text(d,W-150,316,fmt(cff),fcnt2,GOLD,a,stroke=5,anchor='r')
        for q,lw in [(I['qPh'],3),(I['qFF'],4)]:
            pts=[P(c) for c in q]; cx=sum(x for x,_ in pts)/4; cy=sum(y for _,y in pts)/4
            g=1.35 if lw==3 else 1.08; pts=[(cx+(x-cx)*g,cy+(y-cy)*g) for x,y in pts]
            d.line(pts+[pts[0]],fill=RED+(int(a*0.95),),width=lw,joint='curve')
    if 11.0<=t<13.0:
        a=int(255*win(t,11.0,13.0)); text(d,W/2,1250,"EVERY PIXEL IS",fcap,CREAM,a,stroke=5,anchor='c'); text(d,W/2,1320,"A BUCKET OF LIGHT.",fcap,CREAM,a,stroke=5,anchor='c')
    if 13.0<=t<14.95:
        a=int(255*win(t,13.0,14.95,0.2,0.3))
        text(d,W/2,1180,"SMALL BUCKETS: ±10% NOISE",fcap,CREAM,a,stroke=5,anchor='c')
        text(d,W/2,1262,"BIG BUCKETS: ±1%",fchip,CREAM,a,sp=2,chip=RED,anchor='c')
    # ---- reveal: the two photos
    if 17.5<=t<20.7:
        a=int(255*win(t,17.5,20.7,0.25,0.3)); phx,phy=P(I['phR']); ffx,ffy=P(I['ffBot'])
        text(d,phx+28,phy-58,"200 MP",flab,CREAM,a,stroke=4); text(d,phx+28,phy-8,"GRAINY",flab,GOLD,a,sp=2,stroke=4)
        text(d,W/2,ffy+26,"24 MP  ·  CLEAN",flab,CREAM,a,sp=2,stroke=4,anchor='c')
    if 17.9<=t<21.2:
        a=int(255*(1-sstep(20.85,21.2,t))); typed(d,214,"MEGAPIXELS COUNT BUCKETS.","LIGHT FILLS THEM.",int((t-17.9)*24),fend,a)
    # ---- tag (always on, so the loop is seamless)
    d.text((48,1500),"THOUGHT EXPERIMENT  ·  SENSOR AREAS TO SCALE",font=ftag,fill=(235,235,235,130))
    # ---- flashes: frame 0 shutter and the reveal
    k=f;
    if k<3: im=Image.alpha_composite(im,solid((255,255,255),0.10*(1-k/3)))
    k=int(round((t-17.40)*FPS))
    if 0<=k<5: im=Image.alpha_composite(im,solid((255,240,220),0.12*(1-k/5)))
    p.stdin.write(im.tobytes())
p.stdin.close(); p.wait(); print("overlay done")
