# Compose the 1080x1920 reel: room frames, split-screen owner's day (2.2-5.0 s), captions, story clock, JINGLE tag, CTA, watermark.
# python3 compose.py [out.mp4] [audio.wav|none]     stills: python3 compose.py out.jpg none 0.5,3.2
import json, sys, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FPS=30; DUR=13.0; N=round(DUR*FPS); W,H=1080,1920
FB='fonts/JetBrainsMono-Bold.ttf'
F=lambda s: ImageFont.truetype(FB,s)
fT=F(66); fCap=F(50); fLab=F(28); fClk=F(44); fJ=F(40); fCTA=F(31); fWm=F(22)
CREAM=(237,230,214); GOLD=(232,184,90); INK=(12,14,24)
SPLIT=(2.2,5.0); CROP=760          # bottom panel = room rows CROP..CROP+960
meta=json.load(open('output/dog/meta.json'))['frames']
TITLES=[(0.0,1.6,'HE WAITS','ALL DAY.'),(5.0,6.4,'HE HAS','THE DOOR.'),(8.0,8.6,'YOU HAVE LOTS.',None),(8.6,13.01,"YOU'RE HIS",'ENTIRE WORLD.')]
SPLITCAP=[(2.2,3.0,'YOU HAVE A JOB,'),(3.0,3.9,'FRIENDS,'),(3.9,5.0,'A LIFE.')]
def sw(d,txt,font,sp): return sum(d.textlength(c,font=font)+sp for c in txt)-sp
def spaced(d,x,y,txt,font,fill,sp,**k):
    for ch in txt: d.text((x,y),ch,font=font,fill=fill,**k); x+=d.textlength(ch,font=font)+sp
def ease_back(u): u=min(max(u,0),1); c=1.7; return 1+(c+1)*(u-1)**3+c*(u-1)**2
def pop(base,lay,t,t0,cx,cy,dur=0.2):
    s=0.6+0.4*ease_back((t-t0)/dur)
    if s!=1: lay=lay.transform((W,H),Image.AFFINE,(1/s,0,cx-cx/s,0,1/s,cy-cy/s),resample=Image.BICUBIC)
    a=min(1,(t-t0)/0.08)
    if a<1: lay.putalpha(lay.getchannel('A').point(lambda v:int(v*a)))
    base.alpha_composite(lay)
def shadowed(base,lay,r=10,k=0.75):
    sh=lay.getchannel('A').filter(ImageFilter.GaussianBlur(r)).point(lambda v:int(v*k)); blk=Image.new('RGBA',(W,H),INK+(0,)); blk.putalpha(sh); base.alpha_composite(blk)
def title(base,t):
    for t0,t1,a,b in TITLES:
        if not (t0<=t<t1): continue
        lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
        y=170
        for i,(txt,col) in enumerate([(a,CREAM),(b,GOLD)]):
            if not txt: continue
            w=sw(d,txt,fT,7); d.rounded_rectangle([540-w/2-26,y+i*92-8,540+w/2+26,y+i*92+86],radius=16,fill=INK+(170,)); spaced(d,540-w/2,y+i*92,txt,fT,col+(255,),7)
        shadowed(base,lay,18,0.6); pop(base,lay,t,t0,540,230)
def pill(d,cx,cy,txt,font,sp,fg,bg=INK+(225,),padx=30,h=None,outline=None):
    w=sw(d,txt,font,sp); h=h or font.size+30; x0=cx-w/2-padx
    d.rounded_rectangle([x0,cy-h/2,cx+w/2+padx,cy+h/2],radius=h/2,fill=bg,outline=outline,width=3 if outline else 0)
    spaced(d,cx-w/2,cy-font.size*0.62,txt,font,fg,sp)
def clock_txt(m): return f'{m//60:02d}:{m%60:02d}'
def frame(f):
    t=f/FPS; m=meta[min(f,len(meta)-1)]
    room=Image.open(f'output/dog/frames/f{f:05d}.jpg').convert('RGBA')
    split=SPLIT[0]<=t<SPLIT[1]
    if split:
        im=Image.new('RGBA',(W,H),INK+(255,))
        im.paste(Image.open(f'output/day/frames/f{f:05d}.jpg').convert('RGBA'),(0,0))
        im.paste(room.crop((0,CROP,W,CROP+960)),(0,960))
    else: im=room
    d=ImageDraw.Draw(im)
    if split:
        d.rectangle([0,957,W,963],fill=GOLD+(255,))
        lay=Image.new('RGBA',(W,H),(0,0,0,0)); g=ImageDraw.Draw(lay)
        pill(g,150,70,'YOUR DAY',fLab,5,CREAM+(255,)); pill(g,138,1032,'HIS DAY',fLab,5,GOLD+(255,))
        im.alpha_composite(lay)
        for t0,t1,txt in SPLITCAP:
            if t0<=t<t1:
                lay=Image.new('RGBA',(W,H),(0,0,0,0)); g=ImageDraw.Draw(lay); pill(g,540,960,txt,fCap,5,CREAM+(255,),outline=GOLD+(255,),h=92); pop(im,lay,t,t0,540,960)
    else: title(im,t)
    # story clock (24 h, like the ref)
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); g=ImageDraw.Draw(lay); txt=clock_txt(m['min'])
    cx,cy=(930,1032) if split else (930,1765)
    pill(g,cx,cy,txt,fClk,3,GOLD+(255,),bg=INK+(200,),padx=22,h=70)
    im.alpha_composite(lay)
    # JINGLE at the door handle
    if 6.42<=t<7.35:
        kx,ky=m['knob']; lay=Image.new('RGBA',(W,H),(0,0,0,0)); g=ImageDraw.Draw(lay)
        jx=min(max(kx+40,140),900); jy=ky-90; pill(g,jx,jy,'JINGLE',fJ,6,INK+(255,),bg=GOLD+(245,),h=66)
        lay=lay.rotate(-6,center=(jx,jy),resample=Image.BICUBIC); pop(im,lay,t,6.42,jx,jy,0.16)
    # CTA
    if t>=10.4:
        lay=Image.new('RGBA',(W,H),(0,0,0,0)); g=ImageDraw.Draw(lay); pill(g,540,1640,'TAG THE PERSON YOUR DOG WAITS FOR',fCTA,2,CREAM+(255,),outline=GOLD+(255,),h=74); pop(im,lay,t,10.4,540,1640)
    # watermark
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); g=ImageDraw.Draw(lay); wm='SLOW LIGHT'; ww=sw(g,wm,fWm,10); spaced(g,540-ww/2,1850,wm,fWm,(225,215,195,150),10); im.alpha_composite(lay)
    return im.convert('RGB')
if __name__=='__main__':
    out=sys.argv[1] if len(sys.argv)>1 else 'output/he-waits-all-day.mp4'; aud=sys.argv[2] if len(sys.argv)>2 else 'output/mix.wav'
    if len(sys.argv)>3:
        for t in sys.argv[3].split(','): frame(round(float(t)*FPS)).save(out.replace('.jpg',f'_{t}.jpg'),quality=92)
        sys.exit()
    ain=[] if aud=='none' else ['-i',aud]; aopt=[] if aud=='none' else ['-c:a','aac','-b:a','192k','-shortest']
    ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',*ain,
        '-c:v','libx264','-preset','slow','-crf','19','-pix_fmt','yuv420p','-profile:v','high','-maxrate','9M','-bufsize','18M',*aopt,'-movflags','+faststart',out],stdin=subprocess.PIPE)
    for f in range(N): ff.stdin.write(frame(f).tobytes())
    ff.stdin.close(); ff.wait(); print('wrote',out)
