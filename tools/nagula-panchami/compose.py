# Nagula Panchami compositor: hook line, timed English subtitles (hero yellow, uncle white), bang punch-ins, clip audio + door bangs.
#   python3 compose.py out.mp4 REF.mp4          full reel
#   python3 compose.py out.jpg none 0,5,9.4     stills
import sys, subprocess, math
from PIL import Image, ImageDraw, ImageFont
FPS=30; DUR=14.2; N=round(DUR*FPS); W,H=1080,1920
FR='output/full/frames'
fB=lambda s: ImageFont.truetype('fonts/Inter-Black.otf',s)
BANGS=[0.0,0.27,0.52]; CUTS=[0,4.5,8.8,11.2167,13.05,DUR]
HERO=(255,214,64); UNC=(255,255,255); INK=(18,14,12)
SUBS=[(0.75,1.7,UNC,"Why haven't you gone to office?"),
      (3.3,4.45,HERO,"It's Nagula Panchami today."),
      (4.7,5.12,UNC,"Huh?"),
      (5.15,6.15,HERO,"Nagula Panchami!"),
      (6.6,8.85,UNC,"Your office gives a holiday for Nagula Panchami too?"),
      (9.0,10.1,HERO,"My office gives."),
      (10.15,11.2,UNC,"“My office gives.”"),
      (11.4,13.0,UNC,"Well, how would we know? We never studied."),
      (13.3,14.2,HERO,"Ugh, come on!")]
def wrap(d,txt,font,maxw):
    out=[]; cur=''
    for w in txt.split():
        t=(cur+' '+w).strip()
        if d.textlength(t,font=font)<=maxw: cur=t
        else: out.append(cur); cur=w
    out.append(cur); return out
def text_block(d,lines,font,cy,fill,stroke=7):
    lh=font.size*1.12; y=cy-lh*len(lines)/2
    for ln in lines:
        w=d.textlength(ln,font=font); d.text((W/2-w/2,y),ln,font=font,fill=fill,stroke_width=stroke,stroke_fill=INK); y+=lh
def overlay(im,t):
    d=ImageDraw.Draw(im)
    if t<3.2:   # hook: payoff line on frame 0
        a=1.0 if t<2.9 else max(0,(3.2-t)/0.3)
        f1,f2=fB(54),fB(104); l1='NAGULA PANCHAMI LEAVE?'; l2='MY OFFICE GIVES.'
        w1=d.textlength(l1,font=f1); d.rounded_rectangle([W/2-w1/2-26,318,W/2+w1/2+26,318+f1.size+30],radius=18,fill=(214,58,42))
        d.text((W/2-w1/2,328),l1,font=f1,fill=(255,246,226))
        text_block(d,[l2],f2,318+f1.size+30+80,(255,214,64),stroke=9)
    for a,b,col,txt in SUBS:
        if a<=t<b:
            f=fB(66); lines=wrap(d,txt,f,940); text_block(d,lines,f,1330,col)
    return im
def punch(t):
    z=1.0; dx=dy=0
    for e in BANGS:
        u=t-e
        if 0<=u<0.22: k=math.exp(-u/0.06); z+=0.03*k; dx+=9*k*math.sin(u*250); dy+=7*k*math.cos(u*200)
    return z,dx,dy
def frame(f):
    t=f/FPS; im=Image.open(f'{FR}/f{min(f,N-1):05d}.jpg').convert('RGB')
    z,dx,dy=punch(t)
    if z>1.0005 or dx or dy:
        cw,ch=W/z,H/z; x0=(W-cw)/2-dx/z; y0=(H-ch)/2-dy/z
        im=im.transform((W,H),Image.EXTENT,(x0,y0,x0+cw,y0+ch),resample=Image.BICUBIC)
    return overlay(im,t)
if __name__=='__main__':
    out,ref=sys.argv[1],sys.argv[2]
    if len(sys.argv)>3:
        for s in sys.argv[3].split(','): frame(round(float(s)*FPS)).save(out.replace('.jpg',f'_{s}.jpg'),quality=92)
        sys.exit()
    # audio: the clip's own track + three door bangs before the first line
    bang=['-i','sfx/bang.mp3']
    filt=('[1:a]atrim=0:0.3,afade=t=out:st=0.2:d=0.1,volume=1.6,asplit=3[b0][b1][b2];'
          '[b1]adelay=270|270[b1d];[b2]adelay=520|520[b2d];'
          '[0:a]aresample=48000[m];[m][b0][b1d][b2d]amix=inputs=4:normalize=0,alimiter=limit=0.89[a]')
    subprocess.run(['ffmpeg','-v','error','-y','-i',ref,*bang,'-filter_complex',filt,'-map','[a]','-t',str(DUR),'-ar','48000','output/mix.wav'],check=True)
    ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i','output/mix.wav',
        '-c:v','libx264','-preset','slow','-crf','20','-pix_fmt','yuv420p','-profile:v','high','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',out],stdin=subprocess.PIPE)
    for f in range(N): ff.stdin.write(frame(f).tobytes())
    ff.stdin.close(); ff.wait(); print('wrote',out)
