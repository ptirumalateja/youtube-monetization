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
ROWS=[('r93',0),('r6',720),('r1',1310)]; LABY=[330,752,1342]
LAB=['93% OF PEOPLE','6% OF PEOPLE','1% OF PEOPLE']
grad=Image.new('RGBA',(W,H),(0,0,0,0)); gd=ImageDraw.Draw(grad)
for y in range(0,820): gd.line([(0,y),(W,y)],fill=(6,12,18,int(150*(1-y/820)**1.6)))
DROP=cues['drop']

def label_row(img,i,t0,t,res=None,res_t=None,gold=False,alpha=1.0):
    a,s=pop(t,t0)
    if i==2: put(img,(540,LABY[i]),LAB[i],F(BOLD,40),alpha=a*alpha,scale=s,chip=True)
    else: put(img,(540,LABY[i]),LAB[i],F(MED,38),alpha=a*alpha,scale=s,spacing=5,shadow=6)
    if res:
        a2,s2=pop(t,res_t)
        put(img,(540,LABY[i]+64),res,F(BOLD,58 if not gold else 62),fill=GOLD if gold else CREAM,alpha=a2*alpha,scale=s2)

def frame(F_):
    t=F_['t']; m=F_['mode']
    if 'full' in F_:
        img=Image.open(f"{D}/frames/{F_['full']}.jpg").convert('RGB')
    else:
        img=Image.new('RGB',(W,H)); act=F_.get('act')
        for (k,y0),i in zip(ROWS,range(3)):
            p=Image.open(f"{D}/frames/{F_['rows'][k]}.jpg").convert('RGB')
            dim=1.0
            if act and act!=k: dim=0.5
            if m=='closing': dim=1-0.62*ss(20.0,20.35,t)
            if m=='rows' and act is None and t>5.3: dim=1.0
            if dim<1: p=Image.fromarray((np.asarray(p).astype(np.float32)*dim).astype(np.uint8))
            img.paste(p,(0,y0))
        d=ImageDraw.Draw(img)
        for y in (720,1310): d.line([(0,y),(W,y)],fill=(120,118,110),width=2)
    # punch-in on impacts
    k=0
    for t0,amp in ((0.33,0.035),(DROP,0.05)):
        if t0<=t<t0+0.5: k=max(k,amp*math.exp(-(t-t0)*7))
    if k>0:
        sw,sh=int(W*(1+k)),int(H*(1+k)); img=img.resize((sw,sh),Image.BICUBIC).crop(((sw-W)//2,(sh-H)//2,(sw-W)//2+W,(sh-H)//2+H))
    img=img.convert('RGBA')
    # cut flashes
    fl=0
    for tc in (3.1,11.0,18.9,23.0):
        if tc<=t<tc+0.1: fl=0.12*(1-(t-tc)/0.1)
    if t<0.1 and False: fl=0
    if fl>0: img.alpha_composite(Image.new('RGBA',(W,H),(255,244,225,int(255*fl))))
    # ---- text ----
    if m in ('hook','rewind'):
        a=1-ss(2.45,2.7,t)
        g=grad.copy(); g.putalpha(g.split()[3].point(lambda v:int(v*a))); img.alpha_composite(g)
        put(img,(540,380),'ONLY 1% SEE',F(BOLD,132),alpha=a)
        put(img,(540,530),'THIS HOLE.',F(BOLD,132),alpha=a)
        a2,s2=pop(t,0.9); put(img,(540,660),'34 MISSES LATER',F(BOLD,54),fill=GOLD,alpha=a2*a,spacing=4,shadow=8)
    elif m=='rows':
        act=F_.get('act')
        for i,t0 in enumerate((3.3,3.55,3.8)):
            res=None; rt=0
            if t<5.5: res=['SAME CLUB.','SAME BALL.','SAME HOLE.'][i]; rt=[3.95,4.35,4.75][i]
            elif i==0 and t>=5.8: res,rt='NEVER SWING.',5.8
            elif i==1 and t>=10.55: res,rt='MISS ONCE. QUIT.',10.55
            elif i==1 and t>=9.95: res,rt='MISS ONCE.',9.95
            dimA=1.0 if (act is None or ROWS[i][0]==act) else 0.6
            ra=1-ss(5.3,5.5,t) if t<5.5 else 1
            a,s=pop(t,t0)
            if i==2: put(img,(540,LABY[i]),LAB[i],F(BOLD,40),alpha=a*dimA,scale=s,chip=True)
            else: put(img,(540,LABY[i]),LAB[i],F(MED,38),alpha=a*dimA,scale=s,spacing=5,shadow=6)
            if res:
                a2,s2=pop(t,rt); put(img,(540,LABY[i]+64),res,F(BOLD,58),alpha=a2*ra*dimA,scale=s2)
    elif m in ('one','final'):
        g=grad.copy(); img.alpha_composite(g)
        put(img,(540,330),'1% OF PEOPLE',F(BOLD,40),chip=True)
        n=F_.get('n',0)
        if t<DROP:
            if n>0:
                a,s=1,1+0.12*math.exp(-((t*30)%1)*0)  # steady
                put(img,(540,450),f'MISS {n}',F(BOLD,124),fill=GOLD)
            elif t<11.6: put(img,(540,450),'KEEP SWINGING',F(BOLD,84),alpha=ss(11.0,11.2,t))
        else:
            a,s=pop(t,DROP,0.2)
            put(img,(540,480),'IN.',F(BOLD,220),fill=GOLD,alpha=a,scale=s)
            a2,s2=pop(t,DROP+0.35); put(img,(540,640),'ON TRY 35.',F(BOLD,64),alpha=a2,scale=s2)
    elif m=='closing':
        la=1-ss(19.9,20.1,t)
        rs=[('NEVER SWING.',False),('MISS ONCE. QUIT.',False),('MISS 34 TIMES. IN.',True)]
        for i in range(3):
            if la>0.01:
                if i==2: put(img,(540,LABY[i]),LAB[i],F(BOLD,40),alpha=la,chip=True)
                else: put(img,(540,LABY[i]),LAB[i],F(MED,38),alpha=la,spacing=5,shadow=6)
                put(img,(540,LABY[i]+64),rs[i][0],F(BOLD,62 if rs[i][1] else 58),fill=GOLD if rs[i][1] else CREAM,alpha=la)
        if 20.0<=t<21.4:
            a=ss(20.05,20.3,t)*(1-ss(21.25,21.4,t))
            put(img,(540,880),'THE MISSES',F(BOLD,120),alpha=a); put(img,(540,1020),'ARE THE PATH.',F(BOLD,120),fill=GOLD,alpha=a)
        if t>=21.4:
            a=ss(21.45,21.7,t)
            put(img,(540,880),'WHICH ROW',F(BOLD,120),alpha=a); put(img,(540,1020),'ARE YOU?',F(BOLD,120),alpha=a)
            a2,s2=pop(t,21.9); put(img,(540,1190),'COMMENT 93, 6 OR 1',F(BOLD,56),fill=GOLD,alpha=a2,scale=s2)
    return img.convert('RGB')

if ONLY is not None:
    for i in ONLY: frame(frames[i]).save(f'{D}/still_{i:04d}.jpg',quality=90)
    sys.exit()
p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-',
   '-c:v','libx264','-preset','slow','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',OUT],stdin=subprocess.PIPE)
for F_ in frames: p.stdin.write(frame(F_).tobytes())
p.stdin.close(); p.wait(); print('wrote',OUT)
