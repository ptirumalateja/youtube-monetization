# Overlay for the full "It Fell" reel (0-24 s): hook, depth counter + ladder, ghost-ship count, impact chip, paradox, end line.
# usage: python3 overlay_full.py <frames_dir_with_meta_json> <out_dir>
import sys, json, glob, os, math
from PIL import Image, ImageDraw, ImageFont
W,H,FPS=1080,1920,30
MB="/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"; MR="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
F=lambda p,s: ImageFont.truetype(p,s)
CREAM=(246,240,228); RED=(214,62,48)
clamp=lambda x: max(0.0,min(1.0,x))
def sstep(a,b,x): k=clamp((x-a)/(b-a)); return k*k*(3-2*k)
src,out=sys.argv[1],sys.argv[2]; os.makedirs(out,exist_ok=True)
meta={}
for fn in glob.glob(os.path.join(src,'meta_*.json')):
    for f,d in json.load(open(fn)): meta[int(f)]=d
N=max(meta)+1
def tw(d,txt,font): return d.textlength(txt,font=font)
def ctext(d,y,txt,font,fill,a=255,stroke=6,chip=None,cx=W/2):
    w=tw(d,txt,font); x=cx-w/2
    if chip is not None: d.rectangle((x-18,y-8,x+w+18,y+font.size+12),fill=chip+(int(a*0.97),))
    d.text((x,y),txt,font=font,fill=fill+(a,),stroke_width=0 if chip else stroke,stroke_fill=(0,0,0,min(a,235)))
LAD_TOP,LAD_LEN=560,800
def ly(d): return LAD_TOP+d/3800*LAD_LEN
RUNGS=[("SURFACE",0),("SUNLIGHT ENDS · 200 M",200),("LAST LIGHT · 1,000 M",1000),("WRECK · 3,800 M",3800)]
def counter(f,t):
    """monotonic depth readout: camera depth until the bow lands, then locked on the wreck depth"""
    if t<11.9: return meta[f]
    return max(meta[f] if t<12.0 else 0, lerp(meta[int(11.9*FPS)],3800,sstep(11.9,12.6,t)))
def lerp(a,b,u): return a+(b-a)*u
prev=-1; prevN=-1
for f in range(N):
    t=f/FPS; im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    if t<1.98:
        fade=1-sstep(1.75,1.95,t); a=int(255*fade)
        l1="IT DIDN'T JUST SINK."; n1=int(len(l1)*clamp((t-0.15)/0.75)); f1=F(MB,64)
        if n1>=1: ctext(d,250,l1[:n1],f1,CREAM,a)
        l2="IT FELL."; n2=int(len(l2)*clamp((t-1.1)/0.5)); f2=F(MB,112)
        if n2>=1: ctext(d,340,l2[:n2],f2,CREAM,a,chip=RED)
    ui=sstep(2.0,2.25,t)*(1-sstep(21.0,21.4,t))
    if ui>0:
        dep=counter(f,t); v=int(round(dep)); v=max(v,prev); prev=v; a=int(255*ui)
        ctext(d,205,f"{v:,} M",F(MB,92),CREAM,a)
        ctext(d,322,"DEPTHS TO SCALE · TIME COMPRESSED",F(MR,26),CREAM,int(a*0.75),stroke=3)
        slide=int((1-sstep(2.0,2.45,t))*-160); x0=64+slide; la=a
        d.line((x0,ly(0),x0,ly(3800)),fill=CREAM+(int(la*0.45),),width=3)
        for name,dd in RUNGS:
            act = v>=dd-2 if dd>0 else True; fs=42 if (act and dd>0) else 36; col=CREAM if act else (170,165,155)
            y=ly(dd); d.line((x0-10,y,x0+14,y),fill=CREAM+(la,),width=4)
            d.text((x0+30,y-fs/2-2-(30 if dd==0 else 0)),name,font=F(MB,fs),fill=col+(la,),stroke_width=4,stroke_fill=(0,0,0,min(la,230)))
        my=ly(min(v,3800)); pr=10*(0.5+0.5*math.sin(t*7)); d.ellipse((x0-16-pr,my-16-pr,x0+16+pr,my+16+pr),outline=RED+(int(la*0.5),),width=3); d.ellipse((x0-12,my-12,x0+12,my+12),fill=RED+(la,),outline=CREAM+(la,),width=2)
    # ghost-ship count (own monotonic counter) while the camera climbs past the outlines
    if 14.2<=t<19.6:
        n=int(clamp((3800-meta[f])/269)*14) if False else min(14,max(0,int((3800-meta[f])/269))); n=max(n,prevN); prevN=n
        a=int(255*sstep(14.3,14.7,t)*(1-sstep(19.0,19.6,t))); ctext(d,395,f"×{n}",F(MB,84),CREAM,a)
    def cap(t0,t1,txt,y,size=44,fi=0.2,fo=0.3,chip=None):
        if t0<=t<=t1:
            a=int(255*sstep(t0,t0+fi,t)*(1-sstep(t1-fo,t1,t))); ctext(d,y,txt,F(MB,size),CREAM,a,stroke=5,chip=chip)
    cap(5.0,6.2,"RED IS THE FIRST COLOUR",1440); cap(5.0,6.2,"THE SEA TAKES",1496)
    cap(9.0,10.6,"IT KEPT FALLING",1470,size=56)
    cap(12.4,14.3,"THE WRECK",1440,size=60,chip=RED); cap(12.6,14.3,"NORTH ATLANTIC · 1912",1530,size=38)
    cap(17.9,19.6,"14 TITANICS DEEP",1420,size=64,chip=RED)
    cap(19.4,21.5,"IT LAY IN THE DARK",1010,size=54,fo=0.4); cap(19.9,21.5,"FOR 73 YEARS",1080,size=54,fo=0.4); cap(20.4,21.5,"BEFORE ANYONE SAW IT AGAIN.",1150,size=54,fo=0.4)
    # end line, typed once
    if 21.8<=t<=23.7:
        txt="IT'S STILL DOWN THERE."; n=int(len(txt)*clamp((t-21.85)/0.85)); a=int(255*(1-sstep(23.35,23.65,t)))
        if n>=1: ctext(d,980,txt[:n],F(MB,70),CREAM,a,chip=RED)
    im.save(os.path.join(out,f"o{f:04d}.png"))
print("overlay frames:",N)
