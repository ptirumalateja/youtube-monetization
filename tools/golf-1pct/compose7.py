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


ROWS=[('r93',0),('r6',940),('r1',1270)]
TX=440
LAB=['93% OF PEOPLE','6% OF PEOPLE','1% OF PEOPLE']; LABY=[632,972,1302]
import os
C6=json.load(open(sys.argv[1]+'/../v6/cues.json'))       # row text runs on v6's clock (frames carry v6 time in 't')
DROP=C6['drop']; LIPS=[x+1.0 for x in C6['lips']]
FIN=cues['fin']; FDROP=cues['drop']
HOOK=os.environ.get('HOOK','until')
TITLE={'until':(('HOW MANY MISSES',106,GOLD),('UNTIL YOU QUIT?',92,CREAM)),
       'break':(("WHAT'S YOUR",112,CREAM),('BREAKING POINT?',104,GOLD))}[HOOK]
BOT=Image.new('RGBA',(W,420),(0,0,0,0)); _bd=ImageDraw.Draw(BOT)
for y in range(420): _bd.line([(0,y),(W,y)],fill=(10,26,14,int(110*min(1,y/300)**1.5)))
def frame(F_):
    if F_['mode']=='fin': return finale(F_)
    t=F_['t']; tn=F_['tn']
    img=Image.new('RGB',(W,H))
    for i,(k,y0) in enumerate(ROWS):
        p=np.asarray(Image.open(f"{D}/frames/{F_['rows'][k]}.jpg").convert('RGB')).astype(np.float32)
        if i<2:   # the 93% and 6% lanes stay quieter so the 1% lane leads
            dim=0.74-0.2*ss(11.2,11.7,t); g=p.mean(2,keepdims=True); p=(p*0.75+g*0.25)*dim
        else: p=p*1.08
        img.paste(Image.fromarray(np.clip(p,0,255).astype(np.uint8)),(0,y0))
    d=ImageDraw.Draw(img)
    for y in (940,1270): d.line([(0,y),(W,y)],fill=(120,118,110),width=2)
    z=1+0.08*ss(0,FIN,tn)
    if z>1.0005:
        cx,cy=540,1500; sw,sh=int(W*z),int(H*z); big=img.resize((sw,sh),Image.BICUBIC)
        x0=int(cx*z-cx); y0=int(cy*z-cy); img=big.crop((x0,y0,x0+W,y0+H))
    img=img.convert('RGBA'); img.alpha_composite(BOT,(0,1500))
    for lt in LIPS:   # red pulse on the 1% lane each time a near-miss lips out
        if lt<=t<lt+0.3: a=0.13*(1-(t-lt)/0.3); img.alpha_composite(Image.new('RGBA',(W,650),(220,40,30,int(255*a))),(0,1270))
    if DROP<=t<DROP+0.4:
        a=0.2*(1-(t-DROP)/0.4); img.alpha_composite(Image.new('RGBA',(W,650),(255,214,150,int(255*a))),(0,1270))
    ta=1-ss(7.6,8.0,tn)
    (l1,s1,c1),(l2,s2,c2)=TITLE
    put(img,(540,345),l1,F(BOLD,s1),fill=c1,shadow=12,alpha=ta)
    put(img,(540,462),l2,F(BOLD,s2),fill=c2,shadow=12,alpha=ta)
    q=(0.8-0.25*ss(11.2,11.7,t))*(1-ss(7.6,8.0,tn))
    # percentages arrive after the balls land, so the challenge reads first
    a,s_=pop(t,0.45); put(img,(TX,LABY[0]),LAB[0],F(MED,42),alpha=a*q,scale=s_,spacing=5,shadow=6)
    a,s_=pop(t,0.55); put(img,(TX,LABY[1]),LAB[1],F(MED,42),alpha=a*q,scale=s_,spacing=5,shadow=6)
    a,s_=pop(t,0.65); put(img,(TX,LABY[2]),LAB[2],F(BOLD,44),alpha=a*(1-ss(7.6,8.0,tn)),scale=s_,chip=True)
    a,s_=pop(t,1.2); put(img,(TX,LABY[0]+62),'NEVER SWING.',F(BOLD,58),alpha=a*q,scale=s_)
    if cues['miss6_stop']<=t<cues['fall']:
        a,s_=pop(t,cues['miss6_stop']); put(img,(TX,LABY[1]+62),'MISS ONCE.',F(BOLD,58),alpha=a*q,scale=s_)
    elif t>=cues['fall']:
        a,s_=pop(t,cues['fall']); put(img,(TX,LABY[1]+62),'MISS ONCE. QUIT.',F(BOLD,58),alpha=q,scale=s_)
    n=F_['n']
    if t<DROP:
        if n>0:
            stops=[x+T for x,T in zip(cues['imp1'],cues['T1']) if x+T<=t]; last=max(stops or [0])
            lip=n>26
            s_=1+(0.22 if lip else 0.14)*math.exp(-(t-last)*12)
            put(img,(TX,LABY[2]+72),f'MISS {n}',F(BOLD,74),fill=(255,120,100) if lip and t-last<0.25 else GOLD,scale=s_,alpha=1-ss(7.6,8.0,tn))
    else:
        a,s_=pop(t,DROP,0.22); put(img,(TX,LABY[2]+72),'MISS 34. THEN IN.',F(BOLD,60),fill=GOLD,alpha=a,scale=s_)
    return img.convert('RGB')

def finale(F_):
    t=F_['t']
    img=Image.open(f"{D}/frames/{F_['full']}.jpg").convert('RGBA')
    if FIN<=t<FIN+0.12: img.alpha_composite(Image.new('RGBA',(W,H),(255,244,225,int(255*0.12*(1-(t-FIN)/0.12)))))
    if FDROP<=t<FDROP+0.45: img.alpha_composite(Image.new('RGBA',(W,H),(255,214,150,int(255*0.22*(1-(t-FDROP)/0.45)))))
    k=0.05*math.exp(-(t-FDROP)*7) if FDROP<=t<FDROP+0.6 else 0
    if k>0:
        sw,sh=int(W*(1+k)),int(H*(1+k)); img=img.resize((sw,sh),Image.BICUBIC).crop(((sw-W)//2,(sh-H)//2,(sw-W)//2+W,(sh-H)//2+H))
    # MISS 34 hangs over the dark lane until the putt drops
    if t<FDROP: put(img,(540,480),'MISS 34',F(BOLD,84),fill=GOLD,alpha=ss(FIN,FIN+0.3,t)*0.9)
    a,s_=pop(t,FDROP+0.3,0.22); put(img,(540,560),'THE ONLY DIFFERENCE?',F(BOLD,74),alpha=a,scale=s_,shadow=12)
    a,s_=pop(t,FDROP+0.85,0.24); put(img,(540,690),'THEY KEPT GOING.',F(BOLD,106),fill=GOLD,alpha=a,scale=s_,shadow=14)
    a,s_=pop(t,FDROP+1.9); put(img,(540,1330),'COMMENT 93, 6 OR 1',F(BOLD,50),alpha=a,scale=s_,shadow=10)
    return img.convert('RGB')

if ONLY is not None:
    for i in ONLY: frame(frames[i]).save(f'{D}/still_{i:04d}.jpg',quality=90)
    sys.exit()
p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-',
   '-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',OUT],stdin=subprocess.PIPE)
for F_ in frames: p.stdin.write(frame(F_).tobytes())
p.stdin.close(); p.wait(); print('wrote',OUT)
