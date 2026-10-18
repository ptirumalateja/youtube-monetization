import sys, math
sys.argv=['x']
import render as R
from PIL import Image, ImageDraw
W,H=R.W,R.H
def base(t):
    fr=R.BG.copy(); return fr
def hooktext(fr):
    tx=Image.new('RGBA',(W,H),(0,0,0,0)); R.put(tx,R.txt('HOW FAST',112),540,250,1); R.put(tx,R.row(['IS','#FAST','?'],112,0.3),540,400,1); fr.alpha_composite(tx)
def lanes(t):
    fr=base(t); d=ImageDraw.Draw(fr); obj=Image.new('RGBA',(W,H),(0,0,0,0)); od=ImageDraw.Draw(obj)
    ys=[1250,1080,910,740,570]; names=['jet','bullet','earth','parker','light']
    xs0=[250,400,560,740,1000]; vs=[300,700,1300,2200,9000]
    for y,n,x0,v in zip(ys,names,xs0,vs):
        od.line((60,y,W-60,y),fill=R.CREAM+(40,),width=2)
        x=x0+v*t
        if n=='light':
            xx=min(W+200,(x0+v*t)); 
            for w_,c_,a_ in ((22,(232,184,96),70),(10,(255,244,214),170),(4,(255,255,255),255)): od.line((max(0,xx-900),y,xx,y),fill=c_+(a_,),width=w_)
            continue
        for k in range(8): od.line((x-70-k*26,y+(k%3-1)*10,x-90-k*26,y+(k%3-1)*10),fill=R.CREAM+(int(160*(1-k/8)),),width=3)
        spr={'jet':R.SPR['jet'],'bullet':R.SPR['bullet'],'earth':R.earth(0.5),'parker':R.SPR['parker']}[n]
        sc={'jet':0.36,'bullet':0.42,'earth':0.36,'parker':0.34}[n]
        R.paste(obj,spr,x,y,sc)
    fr.alpha_composite(obj); hooktext(fr); return fr.convert('RGB')
def tunnel(t):
    fr=base(t); d=ImageDraw.Draw(fr); cx,cy=540,980; r=R.np.random.default_rng(3)
    for i in range(140):
        a=r.uniform(0,6.283); r0=r.uniform(40,900)*(1+3*t); ln=60+r.uniform(60,380)
        x0=cx+math.cos(a)*r0; y0=cy+math.sin(a)*r0*1.5; x1=cx+math.cos(a)*(r0+ln); y1=cy+math.sin(a)*(r0+ln)*1.5
        d.line((x0,y0,x1,y1),fill=R.CREAM+(int(70+120*r.uniform()),),width=2 if r0<400 else 3)
    obj=Image.new('RGBA',(W,H),(0,0,0,0)); od=ImageDraw.Draw(obj)
    for k in range(4):
        u=(t*2.2+k*0.25)%1; rr=80+700*u; od.ellipse((cx-rr,cy-rr*1.0,cx+rr,cy+rr*1.0),outline=R.GOLD+(int(200*(1-u)),),width=4)
    R.paste(obj,R.SPR['bullet'],cx+30,cy,1.55+1.2*t)
    fr.alpha_composite(obj); hooktext(fr); return fr.convert('RGB')
def zoomout(t):
    fr=base(t); obj=Image.new('RGBA',(W,H),(0,0,0,0)); od=ImageDraw.Draw(obj)
    # 0: giant bullet filling the frame -> 0.45: bullet small, Earth appears -> 0.8: Earth small, light streak
    u=min(1,t/0.9); s=2.4-1.95*R.ease(u)
    R.paste(obj,R.SPR['bullet'],540,980,s*0.9)
    e=R.ease((u-0.3)/0.7); 
    if e>0:
        R.paste(obj,R.earth(0.5),540+300*(1-e),980-380*e,0.15+0.4*e,e)
    for k in range(10): od.line((540-460,980+(k-5)*18,540+460,980+(k-5)*18),fill=R.CREAM+(int(40*(1-abs(k-5)/6)),),width=2)
    fr.alpha_composite(obj); hooktext(fr); return fr.convert('RGB')
imgs=[]
for f in (lanes,tunnel,zoomout):
    for t in (0.0,0.3,0.7): imgs.append(f(t).resize((300,533)))
sheet=Image.new('RGB',(900,1599))
for i,im in enumerate(imgs): sheet.paste(im,((i%3)*300,(i//3)*533))
sheet.save(sys.argv[0] if False else '/tmp/claude-0/-home-user-youtube-monetization/d79d5b50-4ce5-5d03-bd17-d5bd8027e2a2/scratchpad/concepts.png')
