# Full-reel compositor: panels -> frame, dims, punch-ins, flashes, text (all text inside y 300-1440).
# python3 compose.py <fulldir> <out.mp4> [frame list for stills]
import sys, json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import subprocess
D=sys.argv[1]; OUT=sys.argv[2]; ONLY=[int(x) for x in sys.argv[3].split(',')] if len(sys.argv)>3 else None
frames=json.load(open(f'{D}/frames.json')); cues=json.load(open(f'{D}/cues.json'))
W,H=1080,1920; CREAM=(243,234,214); RED=(200,38,30); GOLD=(255,196,110)
BOLD='/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf'; MED='/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf'
FC={}
def F(p,s):
    if (p,s) not in FC: FC[(p,s)]=ImageFont.truetype(p,s)
    return FC[(p,s)]
TC={}
def tlayer(s,font,fill,spacing=0,shadow=8,chip=False):
    """pre-rendered text sprite (RGBA) centred on its own canvas"""
    k=(s,font.path,font.size,fill,spacing,shadow,chip)
    if k in TC: return TC[k]
    d0=ImageDraw.Draw(Image.new('RGBA',(10,10)))
    w=int(sum(d0.textlength(c,font=font) for c in s)+spacing*(len(s)-1)) if spacing else int(d0.textlength(s,font=font))
    pad=40; cw,ch=w+2*pad+60,font.size*2+2*pad
    lay=Image.new('RGBA',(cw,ch),(0,0,0,0)); d=ImageDraw.Draw(lay); cy=ch//2
    if chip:
        d.rounded_rectangle((cw/2-w/2-22,cy-34,cw/2+w/2+22,cy+34),radius=12,fill=RED+(255,))
        d.text((cw/2,cy+2),s,font=font,fill=CREAM,anchor='mm'); TC[k]=lay; return lay
    if spacing:
        x=cw/2-w/2
        for c in s: d.text((x,cy),c,font=font,fill=fill,anchor='lm'); x+=d.textlength(c,font=font)+spacing
    else: d.text((cw/2,cy),s,font=font,fill=fill,anchor='mm')
    sh=Image.new('RGBA',lay.size,(0,0,0,0)); sh.putalpha(lay.split()[3].filter(ImageFilter.GaussianBlur(shadow)).point(lambda a:int(a*0.8)))
    out=Image.alpha_composite(sh,lay); TC[k]=out; return out
def put(img,xy,s,font,fill=CREAM,alpha=1.0,scale=1.0,**kw):
    if alpha<=0.01: return
    L=tlayer(s,font,fill,**kw)
    if scale!=1.0: L=L.resize((max(1,int(L.width*scale)),max(1,int(L.height*scale))),Image.LANCZOS)
    if alpha<1: L=L.copy(); L.putalpha(L.split()[3].point(lambda a:int(a*alpha)))
    img.alpha_composite(L,(int(xy[0]-L.width/2),int(xy[1]-L.height/2)))
def cl(x,a=0,b=1): return max(a,min(b,x))
def ss(a,b,x): u=cl((x-a)/(b-a)); return u*u*(3-2*u)
def pop(t,t0,d=0.18):  # appear with a small overshoot
    if t<t0: return 0,1
    u=cl((t-t0)/d); return min(1,u*1.6), 1+0.18*math.sin(u*math.pi)*(1-u)+0.0

# v4: content moved down DOWN px for a gap under the title. Same renders: row1's top sky is stretched (smooth gradient),
# row3 is cropped at the bottom (lens-shift renders keep one scale, so a crop equals a shorter panel).
DOWN=150
ROWS=[('r93',0),('r6',790+DOWN),('r1',1120+DOWN)]
BOT=Image.new('RGBA',(W,420),(0,0,0,0)); _bd=ImageDraw.Draw(BOT)
for y in range(420): _bd.line([(0,y),(W,y)],fill=(10,26,14,int(110*min(1,y/300)**1.5)))
TX=480
LAB=['93% OF PEOPLE','6% OF PEOPLE','1% OF PEOPLE']; LABY=[482+DOWN,822+DOWN,1152+DOWN]
DROP=cues['drop']
def frame(F_):
    t=F_['t']
    img=Image.new('RGB',(W,H))
    for i,(k,y0) in enumerate(ROWS):
        p=Image.open(f"{D}/frames/{F_['rows'][k]}.jpg").convert('RGB')
        if k=='r93':
            q=Image.new('RGB',(W,790+DOWN)); q.paste(p.crop((0,0,W,200)).resize((W,200+DOWN),Image.BICUBIC),(0,0)); q.paste(p.crop((0,200,W,790)),(0,200+DOWN)); p=q
        dim=1-0.42*ss(8.3,8.8,t) if i<2 else 1.0
        if dim<1: p=Image.fromarray((np.asarray(p).astype(np.float32)*dim).astype(np.uint8))
        img.paste(p,(0,y0))
    d=ImageDraw.Draw(img)
    for y in (790+DOWN,1120+DOWN): d.line([(0,y),(W,y)],fill=(120,118,110),width=2)
    img=img.convert('RGBA'); img.alpha_composite(BOT,(0,1500))
    if DROP<=t<DROP+0.35:  # warm flash on the 1% row as the ball drops
        a=0.16*(1-(t-DROP)/0.35); fl=Image.new('RGBA',(W,800),(255,214,150,int(255*a))); img.alpha_composite(fl,(0,1120+DOWN))
    # fixed title (whole reel, from frame 0)
    put(img,(540,345),'HOW MANY MISSES',F(BOLD,106),fill=GOLD,shadow=12)
    put(img,(540,462),'BEFORE YOU QUIT?',F(BOLD,92),shadow=12)
    a2,s2=pop(t,11.35); put(img,(540,565),'COMMENT 93, 6 OR 1',F(BOLD,48),shadow=8,alpha=a2,scale=s2)
    fade=1-0.35*ss(8.3,8.8,t)
    # row labels from frame 0
    put(img,(TX,LABY[0]),LAB[0],F(MED,36),alpha=fade,spacing=5,shadow=6)
    put(img,(TX,LABY[1]),LAB[1],F(MED,36),alpha=fade,spacing=5,shadow=6)
    put(img,(TX,LABY[2]),LAB[2],F(BOLD,38),chip=True)
    # results
    a,s_=pop(t,0.95); put(img,(TX,LABY[0]+58),'NEVER SWING.',F(BOLD,56),alpha=a*fade,scale=s_)
    if cues['miss6_stop']<=t<cues['fall']:
        a,s_=pop(t,cues['miss6_stop']); put(img,(TX,LABY[1]+58),'MISS ONCE.',F(BOLD,56),alpha=a*fade,scale=s_)
    elif t>=cues['fall']:
        a,s_=pop(t,cues['fall']); put(img,(TX,LABY[1]+58),'MISS ONCE. QUIT.',F(BOLD,56),alpha=fade,scale=s_)
    n=F_['n']
    if t<DROP:
        if n>0:
            last=max([x+T for x,T in zip(cues['imp1'],cues['T1']) if x+T<=t] or [0])
            s_=1+0.14*math.exp(-(t-last)*14)
            put(img,(TX,LABY[2]+64),f'MISS {n}',F(BOLD,66),fill=GOLD,scale=s_)
    else:
        a,s_=pop(t,DROP,0.22); put(img,(TX,LABY[2]+66),'MISS 34. THEN IN.',F(BOLD,56),fill=GOLD,alpha=a,scale=s_)
    return img.convert('RGB')

if ONLY is not None:
    for i in ONLY: frame(frames[i]).save(f'{D}/still_{i:04d}.jpg',quality=90)
    sys.exit()
p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-',
   '-c:v','libx264','-preset','slow','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',OUT],stdin=subprocess.PIPE)
for F_ in frames: p.stdin.write(frame(F_).tobytes())
p.stdin.close(); p.wait(); print('wrote',OUT)
