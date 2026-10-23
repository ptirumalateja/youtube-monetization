# Overlay for "Earth Is 20 Years Old" V4 (same text as V2; marker follows Earth, tag moved below the globe): hook, galactic-year counter, milestone chips, lap strip, Sun marker, twist captions, end line.
# python3 overlay.py <frames_dir>  (reads proj_*.json written by render.js) -> gy_overlay.mov (PNG, RGBA)
import subprocess, math, sys, json, glob
from PIL import Image, ImageDraw, ImageFont
FR=sys.argv[1]
HERE=__import__('os').path.dirname(__import__('os').path.abspath(__file__)); TL=json.load(open(HERE+'/timeline.json')); B=TL['beats']; MS=TL['milestones']
PJ={}
for f in glob.glob(f'{FR}/proj_*.json'): PJ.update({int(k):v for k,v in json.load(open(f)).items()})
W,H,FPS,T=1080,1920,30,TL['T']; N=int(T*FPS)
assert all(i in PJ for i in range(N)), 'missing projections'
MB="/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"; MR="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
def F(p,s): return ImageFont.truetype(p,s)
CREAM=(246,240,228); RED=(214,62,48); GOLD=(255,200,110)
def clamp(x): return max(0.0,min(1.0,x))
def sstep(a,b,x): k=clamp((x-a)/(b-a)); return k*k*(3-2*k)
def tw(d,txt,font,sp=0): return sum(d.textlength(c,font=font)+sp for c in txt)-sp if sp else d.textlength(txt,font=font)
def ctext(d,y,txt,font,fill,a=255,sp=0,stroke=0,chip=None,x=None):
    w=tw(d,txt,font,sp); x=(W-w)/2 if x is None else x-w/2
    if chip is not None:
        pad=16; d.rectangle((x-pad,y-6,x+w+pad,y+font.size+10),fill=chip+(int(a*0.96),))
    if sp:
        for c in txt:
            d.text((x,y),c,font=font,fill=fill+(a,),stroke_width=stroke,stroke_fill=(0,0,0,min(a,235))); x+=d.textlength(c,font=font)+sp
    else: d.text((x,y),txt,font=font,fill=fill+(a,),stroke_width=stroke,stroke_fill=(0,0,0,min(a,235)))
def typed(t,t0,txt,cps=34): return txt[:max(0,min(len(txt),int((t-t0)*cps)))]
def solid(c,a): return Image.new("RGBA",(W,H),c+(int(255*a),))
fh=F(MB,92); fsub=F(MR,30); flab=F(MR,27); fcnt=F(MB,128); fchip=F(MB,46); fago=F(MR,29); fcap=F(MB,58); fend=F(MB,72); ftag=F(MR,22); fsmall=F(MR,26); fpill=F(MR,20)
def flash(f):
    t=f/FPS
    for (ts,a,n) in [(0.0,0.14,5),(B['twistHit'],0.14,6),(B['snap'],0.06,4),(B['impact'],0.10,5)]:
        k=f-int(round(ts*FPS))
        if 0<=k<n: return solid((255,236,210),a*(1-k/n))
    return None
p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgba","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","png","gy4_overlay.mov"],stdin=subprocess.PIPE)
last=-1.0; shown=[]
for f in range(N):
    t=f/FPS; pj=PJ[f]; lap=pj['lap']; im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    sx,sy=pj['sun'][0]*W,pj['sun'][1]*H
    # ---- hook (frame 0 onward)
    if t<2.7:
        a=int(255*(1-sstep(2.4,2.7,t)))
        l1="EARTH IS"; l2="20 YEARS OLD."; n=max(1,int((t+0.05)*30))
        s1=l1[:min(len(l1),n)]; ctext(d,300,s1,fh,CREAM,a,stroke=7)
        if n>len(l1):
            m=min(len(l2),n-len(l1)); pre=l2[:m]; w2=tw(d,l2,fh); x0=(W-w2)/2
            d.rectangle((x0-16,404,x0+tw(d,pre,fh)+16,410+fh.size+12),fill=RED+(int(a*0.97),)); d.text((x0,410),pre,font=fh,fill=CREAM+(a,))
        sub=typed(t,0.95,"IN GALACTIC YEARS",30)
        if sub: ctext(d,540,sub,fsub,CREAM,int(a*0.9),sp=8,stroke=3)
    # ---- what a galactic year is (during the pull-back)
    if 2.5<=t<3.55:
        a=int(255*sstep(2.5,2.7,t)*(1-sstep(3.35,3.55,t)))
        ctext(d,300,"1 GALACTIC YEAR = 1 LAP",flab,CREAM,int(a*0.9),sp=6,stroke=3); ctext(d,345,"≈230 MILLION",fcap,CREAM,a,stroke=6); ctext(d,420,"YEARS",fcap,CREAM,a,stroke=6)
    # ---- counter + milestone chip + lap strip
    if 3.3<=t<B['dive']+0.4:
        A=int(255*sstep(3.3,3.5,t)*(1-sstep(B['dive'],B['dive']+0.4,t)))
        v=math.floor(max(0.0,lap)*10+1e-6)/10; assert v>=last-1e-9, ('counter went backwards',f,v,last); last=v
        ctext(d,250,"EARTH'S AGE IN GALACTIC YEARS",flab,CREAM,int(A*0.85),sp=5,stroke=3)
        ctext(d,288,f"{v:.1f}",fcnt,CREAM,A,stroke=7)
        # chip: the latest milestone reached, until the twist takes the stage
        cur=None
        for m in MS:
            if t>=m['t']-0.12: cur=m
        if cur and t<B['twistHit']:
            ca=int(A*sstep(cur['t']-0.12,cur['t']+0.08,t))
            ctext(d,440,cur['name'],fchip,CREAM,ca,sp=3,chip=RED)
            if cur['ago']: ctext(d,514,cur['ago'],fago,CREAM,int(ca*0.9),sp=2,stroke=3)
        # lap strip: 20 pills, gold as laps complete; red notches at milestones
        if t<B['twistHit']:
            y0=600; pw,gap=40,10; x0=(W-(20*pw+19*gap))/2
            for i in range(20):
                x=x0+i*(pw+gap); fill=clamp(lap-i)
                d.rounded_rectangle((x,y0,x+pw,y0+14),radius=7,outline=CREAM+(int(A*0.55),),width=2)
                if fill>0: d.rounded_rectangle((x,y0,x+max(8,pw*fill),y0+14),radius=7,fill=GOLD+(int(A*0.95),))
            for m in MS[1:-1]:
                if t>=m['t']-0.12:
                    i=min(19,int(m['lap'])); fr=m['lap']-int(m['lap']); x=x0+i*(pw+gap)+pw*fr
                    d.polygon([(x-7,y0-14),(x+7,y0-14),(x,y0-3)],fill=RED+(A,))
            ctext(d,y0+26,"EACH BAR = ONE LAP OF THE GALAXY",fpill,CREAM,int(A*0.7),sp=3,stroke=2)
    # ---- red marker ring on Earth while it is a small disc (wide shots)
    er=pj.get('er',0)*H
    if 2.9<=t<B['now']+0.6 and er<46 and 0<sx<W and 0<sy<H:
        a=int(255*sstep(2.9,3.3,t)*(1-sstep(B['now']+0.2,B['now']+0.6,t))*(1-sstep(30,46,er))); rr=max(24,er*1.5)+3*math.sin(t*7)
        d.ellipse((sx-rr,sy-rr,sx+rr,sy+rr),outline=RED+(a,),width=4)
        if 6.4<t<8.6: ctext(d,int(sy-rr-44),"EARTH",fsmall,CREAM,int(a*sstep(6.4,6.8,t)*(1-sstep(8.2,8.6,t))),sp=4,stroke=3,x=sx)
    # ---- twist: dinosaurs
    if B['twistHit']<=t<B['humans']+0.2:
        a=int(255*sstep(B['twistHit'],B['twistHit']+0.15,t)*(1-sstep(B['humans'],B['humans']+0.2,t)))
        lines=["DINOSAURS DIED","LESS THAN ONE","ORBIT AGO."]; n=max(1,int((t-B['twistHit'])*40)); k=n
        for j,l in enumerate(lines):
            s=l[:max(0,min(len(l),k))]; k-=len(l)
            if s: ctext(d,450+j*72,s,fcap,CREAM if j<2 else CREAM,a,stroke=6,chip=RED if j==2 and len(s)==len(l) else None)
        mx,my=pj['dinoMid'][0]*W,pj['dinoMid'][1]*H; la=int(a*sstep(B['twistHit']+0.7,B['twistHit']+1.1,t))
        lx=min(W-210,mx+190); ly=int(my)
        ctext(d,ly-22,"66 MILLION YEARS",F(MB,34),CREAM,la,stroke=6,x=lx); ctext(d,ly+24,"= 0.29 OF A LAP",F(MB,30),CREAM,la,stroke=6,x=lx)
    # ---- twist 2: modern humans
    if B['humans']+0.2<=t<B['dive']+0.3:
        a=int(255*sstep(B['humans']+0.2,B['humans']+0.4,t)*(1-sstep(B['dive'],B['dive']+0.3,t)))
        lines=["ALL OF MODERN HUMANITY:","THE LAST HALF DEGREE."]; k=max(1,int((t-B['humans']-0.2)*40))
        for j,l in enumerate(lines):
            s=l[:max(0,min(len(l),k))]; k-=len(l)
            if s: ctext(d,460+j*74,s,fcap if j==1 else F(MB,48),CREAM,a,stroke=6,chip=RED if j==1 and len(s)==len(l) else None)
        hx,hy=pj['human'][0]*W,pj['human'][1]*H; la=int(a*sstep(B['humans']+1.2,B['humans']+1.5,t))
        ctext(d,int(hy+46),"~300,000 YEARS",F(MB,32),CREAM,la,stroke=6,x=hx)
    # ---- end line (loops into the hook)
    if B['dive']+0.3<=t<T:
        a=int(255*(1-sstep(T-0.55,T-0.15,t))); s=typed(t,B['dive']+0.3,"WE JUST GOT HERE.",22)
        if s: ctext(d,330,s,fend,CREAM,a,stroke=7)
    # ---- tag
    if 2.4<=t<B['dive']:
        a=int(255*0.75*sstep(2.4,2.8,t)*(1-sstep(B['dive']-0.3,B['dive'],t)))
        ctext(d,1700,"THOUGHT EXPERIMENT · NOT TO SCALE",ftag,CREAM,a,sp=3,stroke=2)
    fl=flash(f)
    if fl is not None: im=Image.alpha_composite(im,fl)
    p.stdin.write(im.tobytes())
p.stdin.close(); p.wait(); print('overlay ok, counter ends at',last)
