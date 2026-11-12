# Compose the 1080x1920 reel: black padding + two stacked panels (ref layout x1.5), labels, speech bubbles, red clock, watermark, fade.
# python3 compose.py [out.mp4]   reads output/{top,bot}/frames + meta.json, output/mix.wav
import json, sys, subprocess, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FPS=30; DUR=11.2; N=round(DUR*FPS); W,H=1080,1920
PT,PB,PH=300,940,558            # panel tops, panel height (ref 200/627, 372 px at 720 wide)
FB='fonts/JetBrainsMono-Bold.ttf'
fLab=ImageFont.truetype(FB,40); fBub=ImageFont.truetype(FB,36); fClk=ImageFont.truetype(FB,52); fPM=ImageFont.truetype(FB,20); fWm=ImageFont.truetype(FB,19); fBig=ImageFont.truetype(FB,58)
BUB_LIFT=58
CREAM=(237,230,214); RED=(232,58,44); BUBBG=(14,18,30)
meta={k:json.load(open(f'output/{k}/meta.json'))['frames'] for k in ('top','bot')}
# clock (shared)
CLOCK=[(0,'9:30','PM'),(2.4,'9:31','PM'),(3.0,'9:32','PM'),(3.55,'10:48','PM'),(4.3,'10:50','PM'),(4.8,'11:58','PM'),(5.3,'11:59','PM'),(5.9,'1:40','AM'),(7.0,'1:41','AM'),(8.6,'1:42','AM')]
# lines: panel, speaker, text, t0, t1, side ('L' bubble left of head, 'R' right, 'C' centred), kind
LINES=[('top','kid','CAN I GO OUT TONIGHT?',0.15,1.05,'L','b'),('top','par','NO.',0.7,1.6,'C','b'),
       ('top','par','?!',4.05,5.2,'R','x'),('top','kid','!',6.82,7.9,'C','x'),
       ('top','par',"YOU COULD'VE JUST ASKED.",6.95,10.4,'R','b'),('top','kid','I DID.',7.95,10.4,'C','b'),
       ('bot','kid','CAN I GO OUT TONIGHT?',0.15,1.0,'L','b'),('bot','par','SURE! BACK BY 12.',1.0,1.95,'L','b'),
       ('bot','par','HOW WAS IT?',4.65,6.0,'L','b')]
def spaced(d,xy,txt,font,fill,sp,anchor_w=None):
    x,y=xy
    for ch in txt: d.text((x,y),ch,font=font,fill=fill); x+=d.textlength(ch,font=font)+sp
    return x
def spaced_w(d,txt,font,sp): return sum(d.textlength(c,font=font)+sp for c in txt)-sp
def ease_back(u): u=min(max(u,0),1); c=1.7; return 1+(c+1)*(u-1)**3+c*(u-1)**2
def bubble(base,t,top,line):
    pan,who,txt,t0,t1,side,kind=line
    if not (t0<=t<t1): return
    f=min(int(t*FPS),N-1); hx,hy=meta[pan][f][who]; hy+=top
    a=min(1,(t1-t)/0.12); s=0.55+0.45*ease_back((t-t0)/0.18)
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    if kind=='x':
        tw=d.textlength(txt,font=fBig); x=hx+(26 if side=='R' else -tw/2); y=hy-92
        d.text((x,y),txt,font=fBig,fill=CREAM+(255,),stroke_width=3,stroke_fill=(10,12,20,255))
    else:
        tw=spaced_w(d,txt,fBub,2); ph=int(fBub.size*1.8); pw=tw+44
        if side=='L': bx=hx-pw+40
        elif side=='R': bx=hx-40
        else: bx=hx-pw/2
        bx=max(24,min(W-24-pw,bx)); by=hy-ph-BUB_LIFT
        tail=[(hx-12 if side!='L' else hx-22, by+ph-2),(hx+ (12 if side!='L' else 2), by+ph-2),(hx-4 if side!='L' else hx-14, by+ph+18)]
        d.rounded_rectangle([bx,by,bx+pw,by+ph],radius=ph/2,fill=BUBBG+(235,),outline=CREAM+(255,),width=3)
        d.polygon(tail,fill=BUBBG+(235,)); d.line([tail[0],tail[2],tail[1]],fill=CREAM+(255,),width=3)
        d.rectangle([tail[0][0]+3,by+ph-4,tail[1][0]-3,by+ph-1],fill=BUBBG+(235,))
        spaced(d,(bx+22,by+(ph-fBub.size)/2-3),txt,fBub,CREAM+(255,),2)
    if s!=1 or a<1:
        cx,cy=hx,hy-60
        lay=lay.resize((W,H)) if s==1 else lay.transform((W,H),Image.AFFINE,(1/s,0,cx-cx/s,0,1/s,cy-cy/s),resample=Image.BICUBIC)
        if a<1: lay.putalpha(lay.getchannel('A').point(lambda v:int(v*max(a,0))))
    base.alpha_composite(lay)
def frame(f):
    t=f/FPS
    im=Image.new('RGBA',(W,H),(0,0,0,255))
    for key,top in (('top',PT),('bot',PB)):
        p=Image.open(f'output/{key}/frames/f{f:05d}.jpg').convert('RGBA'); im.paste(p,(0,top))
    d=ImageDraw.Draw(im)
    for lab,top in (('STRICT PARENTS',PT),('CHILL PARENTS',PB)):
        spaced(d,(96,top+20),lab,fLab,CREAM,5)
    # clock with soft red glow
    hh,ap=[c for c in CLOCK if c[0]<=t][-1][1:]
    gl=Image.new('RGBA',(W,H),(0,0,0,0)); g=ImageDraw.Draw(gl)
    tw=g.textlength(hh,font=fClk); pw=g.textlength(ap,font=fPM); x0=540-(tw+6+pw)/2; y0=(PT+PH+PB)/2-34
    g.text((x0,y0),hh,font=fClk,fill=RED+(255,)); g.text((x0+tw+6,y0+28),ap,font=fPM,fill=RED+(255,))
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(9))); im.alpha_composite(gl)
    for ln in LINES: bubble(im,t,PT if ln[0]=='top' else PB,ln)
    wm='SLOW LIGHT'; ww=spaced_w(d,wm,fWm,9); spaced(d,(540-ww/2,1586),wm,fWm,(120,118,112),9)
    fa=max(0.0,min(1.0,(11.15-t)/1.15)) if t>10.0 else 1.0
    im=im.convert('RGB')
    if fa<1: im=Image.eval(im,lambda v:int(v*fa))
    return im
if __name__=='__main__':
    out=sys.argv[1] if len(sys.argv)>1 else 'output/strict-vs-chill.mp4'
    if len(sys.argv)>2:   # stills mode: compose.py out.jpg t1,t2,...
        for t in sys.argv[2].split(','): frame(round(float(t)*FPS)).save(out.replace('.jpg',f'_{t}.jpg'),quality=92)
        sys.exit()
    ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i','output/mix.wav',
        '-c:v','libx264','-preset','slow','-crf','17','-pix_fmt','yuv420p','-profile:v','high','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',out],stdin=subprocess.PIPE)
    for f in range(N): ff.stdin.write(frame(f).tobytes())
    ff.stdin.close(); ff.wait(); print('wrote',out)
