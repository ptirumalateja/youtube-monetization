# Look-test compositor: grade, slap punch-ins, hook text, rewind smear, watermark.  python3 compose.py out.mp4 mix.wav  |  stills: python3 compose.py out.jpg none 0,0.4
import json, sys, subprocess, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FPS=30; DUR=3.0; N=round(DUR*FPS); W,H=1080,1920; RW=2.55   # RW: rewind smear starts
CREAM=(240,233,216); RUST=(170,62,38); GOLD=(240,190,92); INK=(12,14,24)
fH=ImageFont.truetype('fonts/Inter-Black.otf',106); fWm=ImageFont.truetype('fonts/Inter-Black.otf',24)
EV=[e['t'] for e in json.load(open('output/hook/meta.json'))['events']]
sm=lambda u:(lambda v:v*v*(3-2*v))(min(max(u,0.0),1.0))
def grade(im):
    a=np.asarray(im.convert('RGB'),np.float32)/255.0
    a=np.clip((a-0.03)/(0.965-0.03),0,1); c=0.3; a=a*(1-c)+c*(a*a*(3-2*a))
    l=(a@np.array([0.2126,0.7152,0.0722],np.float32))[...,None]
    a+=((1-l)**2)*np.array([-0.01,0.004,0.02],np.float32); a+=(l**2)*np.array([0.014,0.004,-0.012],np.float32)
    return Image.fromarray((np.clip(a,0,1)*255+0.5).astype(np.uint8))
def src(t): return Image.open(f'output/hook/frames/f{min(round(t*FPS),N-1):05d}.jpg')
def punch(t):   # small zoom + shake on every sole slap
    z=1.0+0.012*t; dx=dy=0
    for e in EV:
        u=t-e
        if 0<=u<0.25: k=math.exp(-u/0.07); z+=0.035*k; dx+=7*k*math.sin(u*260); dy+=7*k*math.cos(u*210)
    return z,dx,dy
def cam(im,z,dx,dy,cy=0.62):
    w,h=im.size; cw,ch=w/z,h/z; x0=(w-cw)*0.5-dx/z; y0=(h-ch)*cy-dy/z
    return im.transform((w,h),Image.EXTENT,(x0,y0,x0+cw,y0+ch),resample=Image.BICUBIC)
def hook_text(im,t):
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay); y=300
    for i,(txt,bg,fg) in enumerate([('HE NEVER',RUST,CREAM),('WORE THEM.',GOLD,INK)]):
        w=d.textlength(txt,font=fH); yy=y+i*(fH.size+30)
        d.rounded_rectangle([540-w/2-30,yy-12,540+w/2+30,yy+fH.size+26],radius=22,fill=bg+(245,),outline=CREAM+(255,),width=5)
        d.text((540-w/2,yy-6),txt,font=fH,fill=fg+(255,))
    sh=lay.getchannel('A').filter(ImageFilter.GaussianBlur(18)).point(lambda v:int(v*0.55)); b=Image.new('RGBA',(W,H),INK+(0,)); b.putalpha(sh)
    im.alpha_composite(b); im.alpha_composite(lay)
def frame(f):
    t=f/FPS
    if t<RW:
        im=cam(grade(src(t)),*punch(t)).convert('RGBA'); hook_text(im,t)
    else:   # rewind: the shot runs backwards fast, smeared sideways, flashing toward cream
        u=(t-RW)/(DUR-RW); ts=max(RW-u*RW*1.6,0); k=math.sin(math.pi*min(u*1.1,1))
        a=np.asarray(cam(grade(src(ts)),*punch(ts)),np.float32); off=int(220*k)
        a=np.pad(a,((0,0),(240,240),(0,0)),mode='reflect')[:,240+off:240+off+W]
        a=a*(1-0.5*u)+np.array(CREAM,np.float32)*0.5*u
        im=Image.fromarray(a.clip(0,255).astype(np.uint8)).filter(ImageFilter.BoxBlur(int(22*k)+1)).convert('RGBA')
        if u<0.35: hook_text(im,t)
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
        '-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p',*aopt,'-movflags','+faststart',out],stdin=subprocess.PIPE)
    for f in range(N): ff.stdin.write(frame(f).tobytes())
    ff.stdin.close(); ff.wait(); print('wrote',out)
