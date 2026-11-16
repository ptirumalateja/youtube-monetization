import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H=1080,1350; FD='/tmp/claude-0/-home-user/ddaf730e-cf42-5f9c-b1f0-bc97d280f97a/scratchpad/spfonts/'
OS=lambda s: ImageFont.truetype(FD+'oswald-latin-700-normal.ttf',s)
CZ=lambda s: ImageFont.truetype(FD+'cinzel-latin-900-normal.ttf',s)
FE=lambda s: ImageFont.truetype(FD+'im-fell-english-sc-latin-400-normal.ttf',s)
CR=(238,230,214); RED=(232,38,30); DIM=(205,198,184)
def base(f):
    im=Image.open(f).convert('RGB').resize((W,H),Image.LANCZOS)
    a=np.asarray(im).astype(np.float32)/255
    # local contrast + gentle shadow lift so no edge reads as a black border
    blur=cv2.GaussianBlur(a,(0,0),18); a=np.clip(a+(a-blur)*0.35,0,1)
    a=1-(1-a)*(1-np.array([0.055,0.075,0.07]))
    return Image.fromarray((a*255).astype(np.uint8)).convert('RGBA')
def shade(im,y0,y1,k=0.55):
    # soft dark band behind text (feathered, never reaching the edges as a flat bar)
    a=np.zeros((H,W),np.float32); a[max(y0,0):y1, :]=k; a=cv2.GaussianBlur(a,(0,0),60)
    ov=Image.new('RGBA',(W,H),(6,8,8,0)); ov.putalpha(Image.fromarray((a*255).astype(np.uint8))); im.alpha_composite(ov)
def rich(im,lines,y,font,gap=1.18,glow=True):
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay); glo=Image.new('RGBA',(W,H),(0,0,0,0)); g=ImageDraw.Draw(glo)
    for i,segs in enumerate(lines):
        tw=sum(d.textlength(t,font=font) for t,_ in segs); x=(W-tw)/2; yy=y+i*font.size*gap
        for t,c in segs:
            d.text((x,yy),t,font=font,fill=c+(255,))
            if c==RED: g.text((x,yy),t,font=font,fill=(255,40,20,255))
            x+=d.textlength(t,font=font)
    a=np.asarray(lay)[...,3]; sh=Image.new('RGBA',(W,H),(0,0,0,0)); sh.putalpha(Image.fromarray((cv2.GaussianBlur(a,(0,0),10)*0.9).astype(np.uint8)))
    im.alpha_composite(sh)
    if glow:
        ga=np.asarray(glo)[...,3]; gl=Image.new('RGBA',(W,H),(255,30,10,0)); gl.putalpha(Image.fromarray((cv2.GaussianBlur(ga,(0,0),16)*0.7).astype(np.uint8))); im.alpha_composite(gl)
    im.alpha_composite(lay)
def foot(im,n,N=4,swipe=False):
    d=ImageDraw.Draw(im); f=OS(22); t='S L O W   L I G H T'; w=d.textlength(t,font=f)
    d.text(((W-w)/2,H-58),t,font=f,fill=CR+(150,)); d.text((W-56,H-58),f'{n}/{N}',font=OS(24),fill=CR+(170,),anchor='ra')
    if swipe: d.text((W-56,H-108),'SWIPE  ›',font=ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Bold.otf',30),fill=CR+(220,),anchor='ra')
def edge(im):
    a=np.asarray(im.convert('L')).astype(float); return [(round(b.mean()),round(b.std())) for b in (a[:150],a[-200:],a[:,:80],a[:,-80:])]
out=[]
# 1 hook: the thing in the corner
im=base('s_8.6.jpg'); shade(im,60,420)
d=ImageDraw.Draw(im); f=FE(30); t='A  TRUE  STORY'; w=d.textlength(t,font=f); d.text(((W-w)/2,92),t,font=f,fill=DIM+(230,))
rich(im,[[('IN THE 1980s, YOUNG MEN',CR)],[('STARTED ',CR),('DYING IN THEIR SLEEP.',RED)]],150,OS(70))
foot(im,1,swipe=True); out.append(im)
# 2 the bed
im=base('s_12.5.jpg'); shade(im,60,400); shade(im,1000,1260,0.5)
rich(im,[[('THEY WENT TO BED HEALTHY.',CR)],[('THEY ',CR),('NEVER WOKE UP.',RED)]],120,OS(70))
rich(im,[[('Hmong refugees, newly arrived in America.',DIM)],[('Autopsies found no cause. More than 100 died.',DIM)]],1040,FE(42),gap=1.3,glow=False)
foot(im,2); out.append(im)
# 3 the spirit
im=base('s_15.5.jpg'); shade(im,60,420); shade(im,1020,1260,0.5)
rich(im,[[('THEIR ELDERS BLAMED',CR)],[('A ',CR),('SPIRIT',RED),(' THAT SITS',CR)],[('ON YOUR CHEST.',CR)]],100,OS(70))
rich(im,[[('Today we have a name for that feeling:',DIM)],[('sleep paralysis.',CR)]],1050,FE(46),gap=1.3,glow=False)
foot(im,3); out.append(im)
# 4 the eyes + reveal
im=base('s_18.3.jpg'); shade(im,60,470); shade(im,950,1270,0.6)
rich(im,[[('ONE WAS SO SCARED,',CR)],[('HE REFUSED TO SLEEP.',CR)],[('WHEN HE FINALLY DID, ',CR)],[('HE ',CR),('NEVER WOKE UP.',RED)]],90,OS(64))
rich(im,[[('A director read his story.',DIM)]],1000,FE(44),glow=False)
rich(im,[[('He made',DIM)]],1060,FE(44),glow=False)
rich(im,[[('A NIGHTMARE ON ELM STREET.',RED)]],1112,CZ(52))
foot(im,4); out.append(im)
for i,im in enumerate(out,1):
    im.convert('RGB').save(f'sleep-deaths_{i}of4.png'); print(i,edge(im))
c=Image.new('RGB',(4*405,506))
for i,im in enumerate(out): c.paste(im.convert('RGB').resize((405,506)),(i*405,0))
c.save('slides_c.jpg')
