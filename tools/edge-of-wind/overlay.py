# Overlay for The Edge of the Wind: hook, AU odometer + year, stop chips, left distance ladder, Voyager tag, end line.
# usage: python3 overlay.py proj.json out.mov
import subprocess, math, sys, json
from PIL import Image, ImageDraw, ImageFont
PJ=json.load(open(sys.argv[1])); OUT=sys.argv[2]
W,H,FPS,T=1080,1920,30,22.0; N=int(T*FPS)
MB="/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"; MR="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
def F(p,s): return ImageFont.truetype(p,s)
CREAM=(246,240,228); RED=(214,62,48); TEALT=(120,230,215)
def clamp(x): return max(0.0,min(1.0,x))
def sstep(a,b,x): k=clamp((x-a)/(b-a)); return k*k*(3-2*k)
def tw(d,txt,font,sp=0): return sum(d.textlength(c,font=font)+sp for c in txt)-sp if sp else d.textlength(txt,font=font)
def ctext(d,y,txt,font,fill,a=255,sp=0,stroke=0,chip=None,x=None):
    w=tw(d,txt,font,sp); x=(W-w)/2 if x is None else x
    if chip is not None:
        pad=16; d.rectangle((x-pad,y-6,x+w+pad,y+font.size+10),fill=chip+(int(a*0.96),))
    if sp:
        for c in txt:
            d.text((x,y),c,font=font,fill=fill+(a,),stroke_width=stroke,stroke_fill=(0,0,0,min(a,235))); x+=d.textlength(c,font=font)+sp
    else: d.text((x,y),txt,font=font,fill=fill+(a,),stroke_width=stroke,stroke_fill=(0,0,0,min(a,235)))
def typed_chip(d,y,pre,post,n,font,a):
    # types pre+post; the post part sits on a red chip
    full=pre+post; n=max(1,min(len(full),n)); txt=full[:n]; x0=(W-tw(d,full,font))/2
    d.text((x0,y),txt[:len(pre)],font=font,fill=CREAM+(a,),stroke_width=6,stroke_fill=(0,0,0,min(a,235)))
    if n>len(pre):
        xo=x0+tw(d,pre,font); s=txt[len(pre):]; wo=tw(d,s,font)
        d.rectangle((xo-12,y-6,xo+wo+12,y+font.size+10),fill=RED+(int(a*0.97),)); d.text((xo,y),s,font=font,fill=CREAM+(a,))
def solid(c,a): return Image.new("RGBA",(W,H),c+(int(255*a),))
# AU -> year along Voyager 1's real track (1977 launch, termination shock Dec 2004 at 94 AU, heliopause Aug 2012 at 121 AU)
def year(au):
    if au<=94: return 1977+(au-1)/(94-1)*(2004-1977)
    return 2004+min(1,(au-94)/(121-94))*(2012-2004)
def au_txt(au):
    if au<10: return f"{au:.1f} AU"
    return f"{int(math.floor(au+1e-6))} AU"
# left ladder: rungs by distance
RUNGS=[(1,"SUN",1290),(30,"NEPTUNE",1150),(94,"SHOCK",1010),(121,"HELIOPAUSE",870)]
def ladder_y(au):
    for (a0,_,y0),(a1,_,y1) in zip(RUNGS,RUNGS[1:]):
        if au<=a1: return y0+(y1-y0)*clamp((au-a0)/(a1-a0))
    return RUNGS[-1][2]
STOPS=[(2.35,5.6,"SOLAR WIND","400 KM/S · CROSSES EARTH IN 32 SECONDS",None),
       (6.15,8.1,"PAST NEPTUNE","AND THE WIND KEEPS BLOWING",None),
       (9.6,12.3,"TERMINATION SHOCK","THE WIND SUDDENLY SLOWS",None),
       (14.05,15.4,"HELIOPAUSE","THE SUN'S WIND STOPS.",None)]
IMP=[(2.0,6,0.10),(9.6,6,0.12),(14.05,10,0.16)]
p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgba","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","png",OUT],stdin=subprocess.PIPE)
fh=F(MB,80); fhead=F(MR,28); fc=F(MB,96); fchip=F(MB,46); fsub=F(MR,29); ftag=F(MR,24); fend=F(MB,72); fcap=F(MB,54); flad=F(MR,24); fvg=F(MB,26)
last_au=-1; last_year=-1
for f in range(N):
    t=f/FPS; im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im); P=PJ[min(f,len(PJ)-1)]; au=P['au']
    # hook
    if 0.25<=t<2.15:
        a=int(255*(1-sstep(1.95,2.15,t))); n=int((t-0.25)*13)+1
        typed_chip(d,300,"THE SUN HAS A ","WIND.",n,fh,a)
    # odometer (only ever increases; asserted)
    if 2.0<=t<15.4:
        A=int(255*sstep(2.0,2.25,t)*(1-sstep(15.18,15.4,t))); txt=au_txt(au); yr=int(math.floor(year(au)+1e-6))
        assert au>=last_au-1e-9 and yr>=last_year, (f,au,yr); last_au=au; last_year=yr
        ctext(d,236,f"VOYAGER 1  ·  {yr}",fhead,CREAM,int(A*0.85),sp=6,stroke=3)
        ctext(d,276,txt,fc,CREAM,A,stroke=6)
    for (a0,a1,chip,sub,sub2) in STOPS:
        if a0<=t<a1:
            A=int(255*sstep(a0,a0+0.18,t)*(1-sstep(a1-0.22,a1,t)))
            ctext(d,402,chip,fchip,CREAM,A,sp=4,chip=RED); ctext(d,478,sub,fsub,CREAM,int(A*0.9),sp=1,stroke=3)
            if sub2: ctext(d,520,sub2,fsub,TEALT,int(A*0.95),sp=1,stroke=3)
    # ladder
    if 2.0<=t<15.4:
        LA=int(255*sstep(2.0,2.3,t)*(1-sstep(15.18,15.4,t)))
        d.line((64,RUNGS[-1][2],64,RUNGS[0][2]),fill=CREAM+(int(LA*0.45),),width=3)
        my=ladder_y(au)
        for (ra,name,y) in RUNGS:
            done=au>=ra-1e-6
            if done: d.ellipse((64-6,y-6,64+6,y+6),fill=CREAM+(int(LA*0.9),))
            else: d.ellipse((64-6,y-6,64+6,y+6),outline=CREAM+(int(LA*0.7),),width=2)
            d.text((84,y-13),name,font=flad,fill=CREAM+(int(LA*(0.95 if done else 0.6)),),stroke_width=2,stroke_fill=(0,0,0,int(LA*0.8)))
        d.ellipse((64-11,my-11,64+11,my+11),fill=RED+(LA,))
    # Voyager tag: early (identify the craft) and in the pull-out (red ring once it is a dot)
    vx,vy=P['p'][0][0]*W,P['p'][0][1]*H
    ta=sstep(2.3,2.6,t)*(1-sstep(4.6,4.9,t))
    if ta>0: ctext(d,vy+70,"VOYAGER 1",fvg,CREAM,int(255*ta*0.9),sp=3,stroke=3,x=vx+40)
    ra=sstep(15.0,15.5,t)*(1-sstep(20.6,20.9,t))
    if ra>0:
        rr=24+3*math.sin(t*6); A=int(255*ra); d.ellipse((vx-rr,vy-rr,vx+rr,vy+rr),outline=RED+(A,),width=4)
        ctext(d,vy-15,"VOYAGER 1",fvg,CREAM,int(A*0.92),sp=3,stroke=3,x=vx+rr+14)
    if 15.2<=t<16.8:
        A=int(255*sstep(15.2,15.45,t)*(1-sstep(16.55,16.8,t)))
        ctext(d,1330,"INTERSTELLAR SPACE",fcap,TEALT,A,stroke=5); ctext(d,1398,"BEGINS HERE.",fcap,TEALT,A,stroke=5)
    # pull-out caption, then the end line with a ring on the Sun
    if 16.9<=t<19.2:
        A=int(255*sstep(16.9,17.15,t)*(1-sstep(18.95,19.2,t)))
        ctext(d,1330,"THE SUN'S WIND BLOWS A BUBBLE",fcap,CREAM,A,stroke=5); ctext(d,1398,"AROUND EVERY PLANET.",fcap,CREAM,A,stroke=5)
    if 19.2<=t<21.0:
        a=int(255*(1-sstep(20.75,21.0,t))); n=int((t-19.25)*16)+1
        if t>=19.25: typed_chip(d,1350,"WE LIVE ","INSIDE IT.",n,fend,a)
        sx,sy=P['p'][1][0]*W,P['p'][1][1]*H; rr=40+4*math.sin(t*5); A=int(255*sstep(19.3,19.6,t)*(1-sstep(20.6,20.9,t)))
        d.ellipse((sx-rr,sy-rr,sx+rr,sy+rr),outline=RED+(A,),width=4)
    if t>=0.25:
        ta=int(140*(1-sstep(20.8,21.2,t))); d.text((48,1500),"THOUGHT EXPERIMENT  ·  NOT TO SCALE",font=ftag,fill=(235,235,235,ta))
    for ts,nf,amp in IMP:
        k=int(round((t-ts)*FPS))
        if 0<=k<nf: im=Image.alpha_composite(im,solid((255,250,240),amp*(1-k/nf)))
    p.stdin.write(im.tobytes())
p.stdin.close(); p.wait(); print("overlay done")
