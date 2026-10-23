# Overlay for "Earth Is 20 Years Old" V3. Three text levels only (big lap number, short event title, small note), upper-middle.
# The hook (0-2.7 s) is the V2 hook, unchanged.  python3 overlay3.py <frames_dir>  -> gy3_overlay.mov (PNG, RGBA)
import subprocess, math, sys, json, glob, os
from PIL import Image, ImageDraw, ImageFont
FR=sys.argv[1]
HERE=os.path.dirname(os.path.abspath(__file__)); TL=json.load(open(HERE+'/timeline.json')); B=TL['beats']; CARDS=TL['cards']; LK=TL['lapKeys']
PJ={}
for f in glob.glob(f'{FR}/proj_*.json'): PJ.update({int(k):v for k,v in json.load(open(f)).items() if v})
W,H,FPS,T=1080,1920,30,TL['T']; N=int(round(T*FPS))
# PCHIP lap curve, identical to index.html
n=len(LK); h=[LK[i+1][0]-LK[i][0] for i in range(n-1)]; dd=[(LK[i+1][1]-LK[i][1])/h[i] for i in range(n-1)]; m=[0.0]*n; m[0]=dd[0]; m[-1]=dd[-1]
for i in range(1,n-1):
    if dd[i-1]*dd[i]<=0: m[i]=0.0
    else: w1=2*h[i]+h[i-1]; w2=h[i]+2*h[i-1]; m[i]=(w1+w2)/(w1/dd[i-1]+w2/dd[i])
def lap_at(t):
    if t<=LK[0][0]: return LK[0][1]
    if t>=LK[-1][0]: return LK[-1][1]
    for i in range(n-1):
        t0,a=LK[i]; t1,b=LK[i+1]
        if t<=t1:
            hh=t1-t0; u=(t-t0)/hh; u2=u*u; u3=u2*u
            return (2*u3-3*u2+1)*a+(u3-2*u2+u)*hh*m[i]+(-2*u3+3*u2)*b+(u3-u2)*hh*m[i+1]
MB="/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"; MR="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
def F(p,s): return ImageFont.truetype(p,s)
CREAM=(246,240,228); RED=(214,62,48)
def clamp(x): return max(0.0,min(1.0,x))
def sstep(a,b,x): k=clamp((x-a)/(b-a)); return k*k*(3-2*k)
def tw(d,txt,font,sp=0): return sum(d.textlength(c,font=font)+sp for c in txt)-sp if sp else d.textlength(txt,font=font)
def ctext(d,y,txt,font,fill,a=255,sp=0,stroke=0,chip=None,x=None):
    w=tw(d,txt,font,sp); x=(W-w)/2 if x is None else x-w/2
    if chip is not None:
        pad=18; d.rectangle((x-pad,y-8,x+w+pad,y+font.size+12),fill=chip+(int(a*0.96),))
    if sp:
        for c in txt:
            d.text((x,y),c,font=font,fill=fill+(a,),stroke_width=stroke,stroke_fill=(0,0,0,min(a,235))); x+=d.textlength(c,font=font)+sp
    else: d.text((x,y),txt,font=font,fill=fill+(a,),stroke_width=stroke,stroke_fill=(0,0,0,min(a,235)))
def typed(t,t0,txt,cps=34): return txt[:max(0,min(len(txt),int((t-t0)*cps)))]
def solid(c,a): return Image.new("RGBA",(W,H),c+(int(255*a),))
fh=F(MB,92); fsub=F(MR,30); flab=F(MR,27); fcap=F(MB,58)
fnum=F(MB,150); funit=F(MR,30); ftitle=F(MB,56); fnote=F(MR,31); fc1=F(MB,62); fc2=F(MB,58); fend=F(MB,74); ftag=F(MR,23)
SEGS=TL['segments']
def seg_at(t): return next(g for g in SEGS if g['t0']-1e-6<=t<g['t1']-1e-6) if t<T else SEGS[-1]
# cut flashes: warm bursts out of the two impacts, soft dips elsewhere, and the hook/clock hits
FL=[(0.0,(255,236,210),0.14,5),(1.9,(255,236,210),0.06,4),(3.3,(255,200,140),0.20,5),(4.9,(255,190,120),0.55,8),(7.4,(200,255,245),0.18,5),
    (9.2,(255,236,210),0.14,5),(11.8,(255,220,170),0.14,5),(14.4,(255,200,140),0.55,9),(16.0,(230,240,255),0.10,5),(17.6,(255,240,220),0.22,6),(B['cap2'],(255,236,210),0.10,5)]
def flash(f):
    for (ts,c,a,nf) in FL:
        k=f-int(round(ts*FPS))
        if 0<=k<nf: return solid(c,a*(1-k/nf)**1.5)
    return None
p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgba","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","png","gy3_overlay.mov"],stdin=subprocess.PIPE)
last=-1.0
for f in range(N):
    t=f/FPS; lap=lap_at(t); g=seg_at(t); im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    # ---- hook: unchanged from V2
    if t<2.7:
        a=int(255*(1-sstep(2.4,2.7,t)))
        l1="EARTH IS"; l2="20 YEARS OLD."; nn=max(1,int((t+0.05)*30))
        s1=l1[:min(len(l1),nn)]; ctext(d,300,s1,fh,CREAM,a,stroke=7)
        if nn>len(l1):
            mm=min(len(l2),nn-len(l1)); pre=l2[:mm]; w2=tw(d,l2,fh); x0=(W-w2)/2
            d.rectangle((x0-16,404,x0+tw(d,pre,fh)+16,410+fh.size+12),fill=RED+(int(a*0.97),)); d.text((x0,410),pre,font=fh,fill=CREAM+(a,))
        sub=typed(t,0.95,"IN GALACTIC YEARS",30)
        if sub: ctext(d,540,sub,fsub,CREAM,int(a*0.9),sp=8,stroke=3)
    if 2.5<=t<3.3:
        a=int(255*sstep(2.5,2.7,t)*(1-sstep(3.15,3.3,t)))
        ctext(d,300,"1 GALACTIC YEAR = 1 LAP",flab,CREAM,int(a*0.9),sp=6,stroke=3); ctext(d,345,"≈230 MILLION",fcap,CREAM,a,stroke=6); ctext(d,420,"YEARS",fcap,CREAM,a,stroke=6)
    # ---- level 1: the big lap number (+ small unit)
    if 3.3<=t<B['dive']+0.35:
        A=int(255*sstep(3.3,3.45,t)*(1-sstep(B['dive'],B['dive']+0.35,t)))
        v=math.floor(max(0.0,lap)*10+1e-6)/10; assert v>=last-1e-9,('counter went backwards',f,v,last); last=v
        s=f"{v:.1f}"; wn=tw(d,s,fnum); wu=tw(d," LAPS",funit); x0=(W-wn-wu)/2
        d.text((x0,200),s,font=fnum,fill=CREAM+(A,),stroke_width=8,stroke_fill=(0,0,0,min(A,235))); d.text((x0+wn,200+fnum.size-funit.size-22)," LAPS",font=funit,fill=CREAM+(int(A*0.85),),stroke_width=3,stroke_fill=(0,0,0,min(A,235)))
    # ---- levels 2 and 3: event title (red chip) + small note
    for c in CARDS:
        if c['t0']<=t<c['t1']:
            a=int(255*sstep(c['t0'],c['t0']+0.12,t)*(1-sstep(c['t1']-0.12,c['t1'],t)))
            if c['title']: ctext(d,392,c['title'],ftitle,CREAM,a,sp=2,chip=RED)
            if c['note']: ctext(d,480 if c['title'] else 410,c['note'],fnote,CREAM,int(a*0.92),sp=2,stroke=4)
    # ---- the final reveal
    if B['cap1']<=t<B['dive']+0.3:
        a=int(255*(1-sstep(B['dive'],B['dive']+0.3,t)))
        s1=typed(t,B['cap1'],"ALL OF HUMAN HISTORY...",26)
        if s1: ctext(d,392,s1,fc1,CREAM,a,stroke=7)
        if t>=B['cap2']:
            s2=typed(t,B['cap2'],"...BARELY MOVES THE CLOCK.",40)
            if s2: ctext(d,486,s2,fc2,CREAM,a,stroke=0 if len(s2)==26 else 6,chip=RED if len(s2)==26 else None)
        if t>=B['cap2']+0.7: ctext(d,586,"MODERN HUMANS: ~300,000 YEARS ≈ 0.5° OF ONE LAP",F(MR,27),CREAM,int(a*0.9*sstep(B['cap2']+0.7,B['cap2']+1.0,t)),stroke=4)
    # ---- red marker on the Sun in the first lap shot, so the eye knows what to follow
    if 4.9<=t<6.6 and f in PJ:
        sx,sy=PJ[f]['sun'][0]*W,PJ[f]['sun'][1]*H; a=int(255*sstep(5.05,5.3,t)*(1-sstep(6.3,6.6,t))); rr=26+3*math.sin(t*7)
        d.ellipse((sx-rr,sy-rr,sx+rr,sy+rr),outline=RED+(a,),width=4); ctext(d,int(sy-rr-46),"THE SUN",F(MR,27),CREAM,a,sp=4,stroke=4,x=sx)
    # ---- schematic tag, only on the two main orbit shots
    for (a0,a1) in [(5.0,7.3),(17.8,19.3)]:
        if a0<=t<a1: ctext(d,1530,"SCHEMATIC ORBIT · NOT TO SCALE",ftag,CREAM,int(190*sstep(a0,a0+0.3,t)*(1-sstep(a1-0.3,a1,t))),sp=3,stroke=2)
    # ---- end line, loops into the hook
    if B['dive']+0.4<=t<T:
        a=int(255*(1-sstep(25.45,25.85,t))); s=typed(t,B['dive']+0.4,"WE JUST GOT HERE.",22)
        if s: ctext(d,330,s,fend,CREAM,a,stroke=7)
    fl=flash(f)
    if fl is not None: im=Image.alpha_composite(im,fl)
    p.stdin.write(im.tobytes())
p.stdin.close(); p.wait(); print('overlay ok, counter ends at',last)
