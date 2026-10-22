import subprocess, sys
from PIL import Image, ImageDraw, ImageFont
W,H,FPS,T=1080,1920,30,25.0; N=int(T*FPS)
MB="/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"; MR="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
F=lambda p,s: ImageFont.truetype(p,s)
CREAM=(246,240,228); RED=(214,62,48)
cl=lambda x: max(0.0,min(1.0,x))
def ss(a,b,x): k=cl((x-a)/(b-a)); return k*k*(3-2*k)
def tw(d,t,f,sp=0): return sum(d.textlength(c,font=f)+sp for c in t)-sp if sp else d.textlength(t,font=f)
def ctext(d,y,t,f,fill,a=255,sp=0,stroke=0,chip=None):
    w=tw(d,t,f,sp); x=(W-w)/2
    if chip is not None: d.rectangle((x-16,y-6,x+w+16,y+f.size+10),fill=chip+(int(a*0.96),))
    if sp:
        for c in t: d.text((x,y),c,font=f,fill=fill+(a,),stroke_width=stroke,stroke_fill=(0,0,0,min(a,235))); x+=d.textlength(c,font=f)+sp
    else: d.text((x,y),t,font=f,fill=fill+(a,),stroke_width=stroke,stroke_fill=(0,0,0,min(a,235)))
fh=F(MB,84); fchip=F(MB,46); fsub=F(MR,27); ftag=F(MR,23); fend=F(MB,82); fsm=F(MR,30)
def typed2(d,y1,y2,l1,l2,n,f,a):
    s1=l1[:min(len(l1),n)]
    if s1: ctext(d,y1,s1,f,CREAM,a,stroke=6)
    if n>len(l1):
        m=min(len(l2),n-len(l1)); w2=tw(d,l2,f); x0=(W-w2)/2; pre=l2[:m]
        d.rectangle((x0-14,y2-4,x0+tw(d,pre,f)+14,y2+f.size+8),fill=RED+(int(a*0.97),)); d.text((x0,y2),pre,font=f,fill=CREAM+(a,))
CH=[(2.9,5.4,"BAR MAGNET",None),(6.4,10.0,"EARTH","SAME DONUT · NOT TO SCALE"),(11.2,14.2,"ELECTRIC CURRENT",None),(14.6,17.2,"SMOKE RING","FLOW THROUGH THE MIDDLE, BACK AROUND"),(18.2,21.4,"FUSION REACTOR",None)]
p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgba","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","png",sys.argv[1]],stdin=subprocess.PIPE)
for f in range(N):
    t=f/FPS; im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    if 0.05<=t<5.8:
        a=int(255*(1-ss(5.2,5.8,t))); n=max(1,int((t-0.05)*34))
        typed2(d,250,345,"EVERY MAGNET","HIDES A DONUT.",n,fh,a)
        if t>=3.0: ctext(d,470,"THE DONUT SHAPE HAS A NAME: TORUS",fsm,CREAM,int(a*ss(3.0,3.4,t)*0.9),sp=2,stroke=3)
    for a0,a1,lab,sub in CH:
        if a0<=t<a1:
            al=ss(a0,a0+0.2,t)*(1-ss(a1-0.25,a1,t)); A=int(255*al)
            ctext(d,1330,lab,fchip,CREAM,A,sp=4,chip=RED)
            if sub: ctext(d,1405,sub,fsub,CREAM,int(A*0.85),sp=2,stroke=3)
    if 22.5<=t<25.0:
        a=255; n=max(1,int((t-22.5)*32)); typed2(d,1250,1345,"TORUS:","THE SHAPE OF FLOW.",n,fend,a)
    ctext(d,1500,"THOUGHT EXPERIMENT · NOT TO SCALE",ftag,CREAM,int(150*ss(0.3,0.8,t)),sp=2,stroke=2)
    # flash on frame-0 hit and reveal
    if f<4: im=Image.alpha_composite(Image.new("RGBA",(W,H),(255,255,255,int(255*0.08*(1-f/4)))),im)
    p.stdin.write(im.tobytes())
p.stdin.close(); p.wait()
