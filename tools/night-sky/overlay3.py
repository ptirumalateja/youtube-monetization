import subprocess, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H,FPS,N=1080,1920,30,420
MB="/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"
MR="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
SI="/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
def F(p,s): return ImageFont.truetype(p,s)
GOLD=(255,196,92); WHITE=(246,240,228)
def ctext(d,y,txt,font,fill,a=255,spacing=0):
    if spacing:
        w=sum(d.textlength(c,font=font)+spacing for c in txt)-spacing; x=(W-w)/2
        for c in txt:
            d.text((x,y),c,font=font,fill=fill+(a,)); x+=d.textlength(c,font=font)+spacing
    else:
        w=d.textlength(txt,font=font); d.text(((W-w)/2,y),txt,font=font,fill=fill+(a,),stroke_width=(5 if font.size>=58 else 0),stroke_fill=(0,0,0,min(a,235)))
def clamp(x): return max(0,min(1,x))
p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgba","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","png","overlay3.mov"],stdin=subprocess.PIPE)
h1,h2="WHAT IF THE SUN","VANISHED RIGHT NOW?"
fh=F(MB,70); fl=F(MR,32); fc=F(MB,150); ft=F(SI,58); ftag=F(MR,25); fr=F(MR,34)
import math
def arc(d,a):
    R=1015; k=-0.62
    while k<0.62:
        x1=540+R*math.sin(k); y1=230+R*math.cos(k); x2=540+R*math.sin(k+0.008); y2=230+R*math.cos(k+0.008)
        d.line((x1,y1,x2,y2),fill=(255,226,170,a),width=3); k+=0.0165
for f in range(N):
    t=f/FPS
    im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    aa=int(160*clamp((t-0.3)/0.8))
    if aa>0: arc(d,aa)
    # hook typed 0.15-1.9 s, held, fades 4.2-4.6
    if 0.0<=t<4.6:
        a=int(255*(1-clamp((t-4.2)/0.4)))
        full=h1+h2; shown=len(full)
        l1=h1[:shown]; l2=h2[:max(0,shown-len(h1))]
        sh=Image.new("RGBA",(W,H),(0,0,0,0)); sd=ImageDraw.Draw(sh)
        for yy_,tx in ((760,l1),(850,l2)):
            if tx:
                ww=sd.textlength(tx,font=fh); sd.text(((W-ww)/2,yy_),tx,font=fh,fill=(0,0,0,255),stroke_width=14,stroke_fill=(0,0,0,255))
        sh=sh.filter(ImageFilter.GaussianBlur(16)); al=sh.split()[3].point(lambda v:min(255,int(v*1.5*a/255))); sh.putalpha(al)
        im=Image.alpha_composite(im,sh); d=ImageDraw.Draw(im)
        ctext(d,760,l1,fh,WHITE,a); ctext(d,850,l2,fh,GOLD,a)
        if int(t*2)%2==0 and t<2.5 and shown>=len(full):
            pass
    # counter 4.5-10.5, hold after
    if t>=4.5:
        sec=min(500,max(0,(t-4.5)/6.0*500)); s=int(sec)
        txt=f"{s//60:02d}:{s%60:02d}"
        fa=clamp((t-4.5)/0.3)*255
        done=t>=10.5
        col=GOLD if done else WHITE
        if t<12.0:
            lab="LIGHT STILL ARRIVING" if not done else "THE LAST LIGHT HAS ARRIVED"
            ctext(d,690,lab,fl,(255,214,150),int(fa*0.85),spacing=6)
            ctext(d,740,txt,fc,col,int(fa))
        else:
            fo=int(255*(1-clamp((t-12.0)/0.3)))
            if fo>0:
                ctext(d,690,"THE LAST LIGHT HAS ARRIVED",fl,(255,214,150),int(fo*0.85),spacing=6)
                ctext(d,740,txt,fc,GOLD,fo)
    if t>=12.2:
        a=int(255*clamp((t-12.2)/0.35))
        ctext(d,700,"Nothing changes for 8 min 20 s.",ft,WHITE,a)
        a2=int(255*clamp((t-12.9)/0.35))
        ctext(d,785,"Gravity travels at light speed too.",ft,GOLD,a2)
    ctext(d,1490 if t>=13.3 else 1490,"",ftag,WHITE,0)
    d.text((48,1500),"THOUGHT EXPERIMENT  ·  NOT TO SCALE",font=ftag,fill=(230,230,230,150))
    p.stdin.write(im.tobytes())
p.stdin.close(); p.wait(); print("overlay done")
