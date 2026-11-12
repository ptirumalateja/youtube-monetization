# Full-reel compositor: grade, slap punch-ins, captions, rewind smear, CTA, watermark.
#   python3 compose_full.py out.mp4 mix.wav       stills: python3 compose_full.py out.jpg none 0,4.5
import json, sys, subprocess, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FPS=30; DUR=28.0; N=round(DUR*FPS); W,H=1080,1920; RW=(2.55,3.0)
CREAM=(240,233,216); RUST=(170,62,38); GOLD=(240,190,92); INK=(12,14,24)
IB='fonts/Inter-Black.otf'; F=lambda s: ImageFont.truetype(IB,s)
fH=F(106); fC=F(84); fP=F(44); fWm=F(24)
META=json.load(open('output/full/meta.json')); EVS=META['events']; SHOT=[m['shot'] for m in META['frames']]
SLAPS=[e['t'] for e in EVS if e['type']=='slap']
# (t0, t1, line1, line2, style)  style: hook = rust/gold slabs; cap = ink slab cream, line 2 gold
CAPS=[(0.0,2.75,'HE NEVER','WORE THEM.','hook'),(3.0,4.2,'MY SHOES TORE.',None,'cap'),(4.35,9.0,'HE BOUGHT','MINE INSTEAD.','cap'),
      (9.0,14.0,'NEW CARDBOARD.','EVERY YEAR.','cap'),(14.0,15.6,'MY FIRST SALARY.',None,'cap'),(15.6,19.0,'"I\'LL SAVE THEM','FOR A SPECIAL DAY."','cap'),
      (19.4,24.0,'THE BOX WAS','STILL CLOSED.','cap'),(24.0,25.9,'SOME PARENTS SAVE','THE BEST FOR YOU.','cap'),(25.9,28.01,'EVEN FROM','THEMSELVES.','cap')]
CAPY={0.0:440,9.0:1230,14.0:1180,15.6:1180}   # hook sits between the gift box and the shoes; the years caption goes below dad's head
AGES=[(9.0,'AGE 7'),(9+5/3,'AGE 11'),(9+10/3,'AGE 15')]
sm=lambda u:(lambda v:v*v*(3-2*v))(min(max(u,0.0),1.0))
def ease_back(u): u=min(max(u,0),1); c=1.7; return 1+(c+1)*(u-1)**3+c*(u-1)**2
def grade(im,late=0.0):
    a=np.asarray(im.convert('RGB'),np.float32)/255.0
    a=np.clip((a-0.03)/(0.965-0.03),0,1); c=0.3; a=a*(1-c)+c*(a*a*(3-2*a))
    l=(a@np.array([0.2126,0.7152,0.0722],np.float32))[...,None]
    if late>0: a=l+(a-l)*(1-0.22*late); a=a*(1-0.06*late)
    a+=((1-l)**2)*np.array([-0.01,0.004,0.02],np.float32); a+=(l**2)*np.array([0.014,0.004,-0.012],np.float32)
    return Image.fromarray((np.clip(a,0,1)*255+0.5).astype(np.uint8))
def src(t): f=min(max(round(t*FPS),0),N-1); return Image.open(f'output/full/frames/f{f:05d}.jpg'), SHOT[f]
def punch(t):
    z=1.0; dx=dy=0
    if t<RW[0]: z+=0.012*t
    for e in SLAPS:
        u=t-e
        if 0<=u<0.25: k=math.exp(-u/0.07); amp=1.0 if e<3 else 0.55; z+=0.035*k*amp; dx+=7*k*amp*math.sin(u*260); dy+=7*k*amp*math.cos(u*210)
    return z,dx,dy
def cam(im,z,dx,dy,cy=0.6):
    if z==1.0 and dx==0 and dy==0: return im
    w,h=im.size; cw,ch=w/z,h/z; x0=(w-cw)*0.5-dx/z; y0=(h-ch)*cy-dy/z
    return im.transform((w,h),Image.EXTENT,(x0,y0,x0+cw,y0+ch),resample=Image.BICUBIC)
def with_shadow(base,lay,r=16,k=0.55):
    sh=lay.getchannel('A').filter(ImageFilter.GaussianBlur(r)).point(lambda v:int(v*k)); b=Image.new('RGBA',(W,H),INK+(0,)); b.putalpha(sh); base.alpha_composite(b); base.alpha_composite(lay)
def pop(lay,t,t0,cy,dur=0.14):
    if t0<=0.0: return lay
    s=0.82+0.18*ease_back((t-t0)/dur)
    if abs(s-1)>1e-3: lay=lay.transform((W,H),Image.AFFINE,(1/s,0,540-540/s,0,1/s,cy-cy/s),resample=Image.BICUBIC)
    return lay
def caption(im,t):
    for t0,t1,a,b,st in CAPS:
        if not (t0<=t<t1): continue
        lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay); y=CAPY.get(t0,440)
        fnt=fH if st=='hook' else fC
        for i,txt in enumerate([a,b]):
            if not txt: continue
            if st=='hook': bg,fg=(RUST,CREAM) if i==0 else (GOLD,INK)
            else: bg,fg=INK,(CREAM if i==0 else GOLD)
            w=d.textlength(txt,font=fnt); yy=y+i*(fnt.size+30)
            d.rounded_rectangle([540-w/2-28,yy-12,540+w/2+28,yy+fnt.size+24],radius=20,fill=bg+(240 if st=='hook' else 215,),outline=(CREAM+(255,)) if st=='hook' else None,width=5 if st=='hook' else 0)
            d.text((540-w/2,yy-6),txt,font=fnt,fill=fg+(255,))
        with_shadow(im,pop(lay,t,t0,y+fnt.size))
    for i,(ta,txt) in enumerate(AGES):
        tb=AGES[i+1][0] if i+1<len(AGES) else 14.0
        if ta<=t<tb:
            lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay); w=d.textlength(txt,font=fP); cy=480
            d.rounded_rectangle([540-w/2-26,cy-38,540+w/2+26,cy+40],radius=38,fill=GOLD+(245,)); d.text((540-w/2,cy-28),txt,font=fP,fill=INK+(255,))
            with_shadow(im,pop(lay,t,ta,cy),10,0.5)
    if t>=26.3:  # CTA
        lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay); txt='SEND THIS TO YOUR DAD.'; w=d.textlength(txt,font=fP); cy=760
        d.rounded_rectangle([540-w/2-30,cy-42,540+w/2+30,cy+44],radius=42,fill=CREAM+(245,),outline=GOLD+(255,),width=4); d.text((540-w/2,cy-29),txt,font=fP,fill=INK+(255,))
        with_shadow(im,pop(lay,t,26.3,cy),10,0.5)
def frame(f):
    t=f/FPS
    if RW[0]<=t<RW[1]:   # rewind: the hook runs backwards fast, smeared sideways, washing to cream
        u=(t-RW[0])/(RW[1]-RW[0]); ts=max(RW[0]-u*RW[0]*1.6,0); k=math.sin(math.pi*min(u*1.1,1))
        a=np.asarray(cam(grade(src(ts)[0],0.5),*punch(ts)),np.float32); off=int(220*k)
        a=np.pad(a,((0,0),(240,240),(0,0)),mode='reflect')[:,240+off:240+off+W]
        a=a*(1-0.5*u)+np.array(CREAM,np.float32)*0.5*u
        im=Image.fromarray(a.clip(0,255).astype(np.uint8)).filter(ImageFilter.BoxBlur(int(22*k)+1)).convert('RGBA')
    else:
        fr,sh=src(t); late=0.5 if sh=='A' else (sm((t-19)/2.0) if sh=='E' else 0.0)
        im=cam(grade(fr,late),*punch(t)).convert('RGBA')
    caption(im,t)
    d=ImageDraw.Draw(im); wm='SLOW LIGHT'; ww=d.textlength(wm,font=fWm)+9*10; x=540-ww/2
    for ch in wm: d.text((x,1850),ch,font=fWm,fill=(240,232,215,150)); x+=d.textlength(ch,font=fWm)+10
    return im.convert('RGB')
if __name__=='__main__':
    out=sys.argv[1]; aud=sys.argv[2] if len(sys.argv)>2 else 'none'
    if len(sys.argv)>3:
        for t in sys.argv[3].split(','): frame(round(float(t)*FPS)).save(out.replace('.jpg',f'_{t}.jpg'),quality=92)
        sys.exit()
    ain=[] if aud=='none' else ['-i',aud]; aopt=[] if aud=='none' else ['-c:a','aac','-b:a','192k','-shortest']
    ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',*ain,
        '-c:v','libx264','-preset','slow','-crf','19','-pix_fmt','yuv420p','-profile:v','high','-maxrate','9M','-bufsize','18M',*aopt,'-movflags','+faststart',out],stdin=subprocess.PIPE)
    for f in range(N): ff.stdin.write(frame(f).tobytes())
    ff.stdin.close(); ff.wait(); print('wrote',out)
