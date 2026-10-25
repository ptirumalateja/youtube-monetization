# Overlay for the "It Fell" opening (0-5.57 s): hook text, depth counter, to-scale depth ladder, caption.
# usage: python3 overlay_open.py <frames_dir_with_meta_json> <out_dir>
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
def ctext(d,y,txt,font,fill,a=255,stroke=6,chip=None):
    w=tw(d,txt,font); x=(W-w)/2
    if chip is not None: d.rectangle((x-18,y-8,x+w+18,y+font.size+12),fill=chip+(int(a*0.97),))
    d.text((x,y),txt,font=font,fill=fill+(a,),stroke_width=0 if chip else stroke,stroke_fill=(0,0,0,min(a,235)))
LAD_TOP,LAD_LEN=560,800
def ly(d): return LAD_TOP+d/3800*LAD_LEN
RUNGS=[("SURFACE",0),("SUNLIGHT ENDS · 200 M",200),("LAST LIGHT · 1,000 M",1000),("WRECK · 3,800 M",3800)]
prev=-1
for f in range(N):
    t=f/FPS; im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    # hook (0.15 - 1.95 s)
    if t<1.98:
        fade=1-sstep(1.75,1.95,t); a=int(255*fade)
        l1="IT DIDN'T JUST SINK."; n1=int(len(l1)*clamp((t-0.15)/0.75)); f1=F(MB,64)
        if n1>=1: ctext(d,250,l1[:n1],f1,CREAM,a)
        l2="IT FELL."; n2=int(len(l2)*clamp((t-1.1)/0.5)); f2=F(MB,112)
        if n2>=1: ctext(d,340,l2[:n2],f2,CREAM,a,chip=RED)
    # counter, ladder (from 2.0 s)
    if t>=2.0:
        dep=meta[f]; v=int(round(dep)); assert v>=prev, (f,v,prev); prev=v
        a=int(255*sstep(2.0,2.25,t)); ctext(d,205,f"{v:,} M",F(MB,92),CREAM,a)
        ctext(d,322,"DEPTHS TO SCALE · TIME COMPRESSED",F(MR,26),CREAM,int(a*0.75),stroke=3)
        slide=int((1-sstep(2.0,2.45,t))*-160); x0=64+slide; la=int(255*sstep(2.0,2.4,t))
        d.line((x0,ly(0),x0,ly(3800)),fill=CREAM+(int(la*0.45),),width=3)
        for name,dd in RUNGS:
            act = dep>=dd-2 if dd>0 else True; fs=42 if (act and dd>0) else 36; col=CREAM if act else (170,165,155)
            y=ly(dd); d.line((x0-10,y,x0+14,y),fill=CREAM+(la,),width=4)
            d.text((x0+30,y-fs/2-2-(30 if dd==0 else 0)),name,font=F(MB,fs),fill=col+(la,),stroke_width=4,stroke_fill=(0,0,0,min(la,230)))
        my=ly(dep); pr=10*(0.5+0.5*math.sin(t*7)); d.ellipse((x0-16-pr,my-16-pr,x0+16+pr,my+16+pr),outline=RED+(int(la*0.5),),width=3); d.ellipse((x0-12,my-12,x0+12,my+12),fill=RED+(la,),outline=CREAM+(la,),width=2)
    # caption
    if t>=5.0:
        a=int(255*sstep(5.0,5.2,t)); fc=F(MB,44)
        ctext(d,1440,"RED IS THE FIRST COLOUR",fc,CREAM,a,stroke=5); ctext(d,1496,"THE SEA TAKES",fc,CREAM,a,stroke=5)
    im.save(os.path.join(out,f"o{f:04d}.png"))
print("overlay frames:",N,"final depth",meta[N-1])
