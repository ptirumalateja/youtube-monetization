#!/usr/bin/env python3
"""Text and chip overlay for the mosquito Reel. usage: overlay.py <out_overlay.mov> [t0 t1]  (renders RGBA frames to an alpha .mov).
Style: cream condensed bold caps with a dark stroke, red chips (red only on chips), safe zone y 220..1570 of 1920."""
import sys, subprocess, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H,FPS=1080,1920,30
CREAM=(247,238,220); RED=(214,62,48); DARK=(8,6,6)
FB='/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
SQ=0.84   # horizontal squeeze for a condensed look
def txt_img(s,size,fill=CREAM,stroke=True):
    f=ImageFont.truetype(FB,size); w=int(f.getlength(s))+size; h=int(size*1.5)
    im=Image.new('RGBA',(w,h),(0,0,0,0)); d=ImageDraw.Draw(im)
    sw=max(2,int(size*0.075)) if stroke else 0
    d.text((size//2,int(size*0.12)),s,font=f,fill=fill+(255,),stroke_width=sw,stroke_fill=DARK+(235,))
    bb=im.getbbox(); im=im.crop(bb) if bb else im
    return im.resize((max(1,int(im.width*SQ)),im.height),Image.LANCZOS)
def chip_img(s,size):
    t=txt_img(s,size,CREAM,False); pw,ph=int(size*0.32),int(size*0.16)
    im=Image.new('RGBA',(t.width+2*pw,t.height+2*ph),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle((0,0,im.width-1,im.height-1),radius=int(size*0.2),fill=RED+(255,))
    im.alpha_composite(t,(pw,ph)); return im
def line(parts,size,gap=0.28):
    ims=[chip_img(p[1:],size) if p.startswith('#') else txt_img(p,size) for p in parts]
    g=int(size*gap); w=sum(i.width for i in ims)+g*(len(ims)-1); h=max(i.height for i in ims)
    out=Image.new('RGBA',(w,h),(0,0,0,0)); x=0
    for i in ims: out.alpha_composite(i,(x,(h-i.height)//2)); x+=i.width+g
    return out
def block(lines,size,lead=1.22):
    """lines: str | list of parts | (content, size) to override the size of that line"""
    items=[]
    for l in lines:
        sz=size
        if isinstance(l,tuple): l,sz=l
        items.append((line(l if isinstance(l,list) else [l],sz),sz))
    w=max(i.width for i,_ in items); y=0; pos=[]
    for im,sz in items:
        pos.append(y); y+=int(sz*lead)
    h=y+int(items[-1][1]*0.3)
    out=Image.new('RGBA',(w,h),(0,0,0,0))
    for (im,sz),yy in zip(items,pos): out.alpha_composite(im,((w-im.width)//2,yy+max(0,(int(sz*lead)-im.height)//2)))
    sh=Image.new('RGBA',out.size,(0,0,0,0)); sh.putalpha(out.getchannel('A').point(lambda a:int(a*0.55)).filter(ImageFilter.GaussianBlur(size*0.08)))
    res=Image.new('RGBA',out.size,(0,0,0,0)); res.alpha_composite(sh); res.alpha_composite(out); return res
# (name, start, end, y, image, mode)  mode: 'fade' | 'type' | 'pop'
HOOK12=block(['WHAT IF',['EVERY','#MOSQUITO']],112)
CAPS=[
 ('hook12', 0.0, 3.15, 250, HOOK12, 'type', 1.1),
 ('hook3',  1.55,3.15, 250+HOOK12.height+4, block(['VANISHED?'],112), 'pop', 0),
 ('allgone',3.40,4.55, 260, block(['OVERNIGHT.','ALL GONE.'],118), 'fade', 0),
 ('everywhere',4.55,5.95,260, block(['EVERYWHERE','ON EARTH.'],104), 'fade', 0),
 ('arctic',6.10,8.65, 260, block(['ARCTIC SWARMS:',['#GONE']],104), 'fade', 0),
 ('num',   10.00,11.85,230, block([(['#~610,000'],150),('DEATHS FROM MALARIA,',60),('2024 (WHO)',60)],60), 'pop', 0),
 ('sec',   11.85,13.65,290, block([('ONE EVERY ~52 SECONDS.',64),('MOSTLY CHILDREN UNDER 5.',64)],64), 'fade', 0),
 ('illus', 10.50,13.65,1470, block(['RED = WHO AFRICAN REGION (ILLUSTRATIVE)'],36), 'fade', 0),
 ('nature',13.85,15.00,260, block(['BUT NATURE','NOTICES.'],104), 'fade', 0),
 ('switch',15.00,16.20,260, block(['SOME PREDATORS','LOSE A MEAL.','MOST WOULD SWITCH.'],70), 'fade', 0),
 ('food',  16.35,18.60,260, block(['FOOD WEBS','MIGHT SHIFT.'],104), 'fade', 0),
 ('orchid',18.85,20.90,260, block(['ONE ORCHID','DEPENDS ON THEM.'],98), 'fade', 0),
 ('choc',  20.95,22.20,260, block([(['#CHOCOLATE? SAFE.'],64),('MIDGES POLLINATE IT.',60)],60), 'fade', 0),
 ('y10',   22.45,24.55,260, block([(['#YEAR 10'],88),('SOMETHING ELSE',98),('MOVES IN.',98)],98), 'fade', 0),
 ('web',   24.55,25.75,260, block(['ONE SMALL CREATURE.','A BIGGER WEB.'],72), 'fade', 0),
 ('q',     26.00,29.75,240, block(['WOULD EARTH BE',['#BETTER'],'WITHOUT THEM?'],100), 'fade', 0),
 ('tag',   26.20,29.75,1470, block(['THOUGHT EXPERIMENT  -  AI-ASSISTED VISUALS'],38), 'fade', 0),
]
def ease(x): x=max(0,min(1,x)); return x*x*(3-2*x)
def frame(t):
    fr=Image.new('RGBA',(W,H),(0,0,0,0))
    for name,a,b,y,im,mode,tw in CAPS:
        if not(a<=t<b): continue
        fin=ease((t-a)/0.18); fout=ease((b-t)/0.15); al=min(fin,fout)
        x=(W-im.width)//2; cur=im
        if mode=='type':
            # reveal left-to-right by character fraction (never negative), simple wipe
            f=max(1/40,min(1,(t-a)/tw)); cw=max(1,int(im.width*f)); cur=im.crop((0,0,cw,im.height)); x=(W-im.width)//2; al=fout
        if mode=='pop':
            s=1+0.28*max(0,1-(t-a)/0.14); cur=im.resize((int(im.width*s),int(im.height*s)),Image.LANCZOS); x=(W-cur.width)//2; y2=y-(cur.height-im.height)//2; al=min(1,(t-a)/0.05)*fout
        else: y2=y+int(10*(1-fin))
        if al<1: cur=cur.copy(); cur.putalpha(cur.getchannel('A').point(lambda v,al=al:int(v*al)))
        fr.alpha_composite(cur,(x,y2))
    return fr
if __name__=='__main__':
    out=sys.argv[1]; T=32.3; n=int(T*FPS)
    a,b=(int(float(sys.argv[2])*FPS),int(float(sys.argv[3])*FPS)) if len(sys.argv)>3 else (0,n)
    p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgba','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','png','-pix_fmt','rgba',out],stdin=subprocess.PIPE)
    for i in range(a,b): p.stdin.write(frame(i/FPS).tobytes())
    p.stdin.close(); p.wait()
