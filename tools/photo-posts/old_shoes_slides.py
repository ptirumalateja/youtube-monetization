import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H=1080,1350
CREAM=(240,233,216); RUST=(170,62,38); GOLD=(240,190,92); INK=(12,14,24)
IB='/usr/share/fonts/opentype/inter/Inter-Black.otf'; F=lambda s: ImageFont.truetype(IB,s)
def grade(im,late=0.0):
    a=np.asarray(im.convert('RGB'),np.float32)/255.0
    a=np.clip((a-0.03)/(0.965-0.03),0,1); c=0.3; a=a*(1-c)+c*(a*a*(3-2*a))
    l=(a@np.array([0.2126,0.7152,0.0722],np.float32))[...,None]
    if late>0: a=l+(a-l)*(1-0.22*late); a=a*(1-0.06*late)
    a+=((1-l)**2)*np.array([-0.01,0.004,0.02],np.float32); a+=(l**2)*np.array([0.014,0.004,-0.012],np.float32)
    return Image.fromarray((np.clip(a,0,1)*255+0.5).astype(np.uint8))
def with_shadow(base,lay,r=16,k=0.55):
    sh=lay.getchannel('A').filter(ImageFilter.GaussianBlur(r)).point(lambda v:int(v*k)); b=Image.new('RGBA',(W,H),INK+(0,)); b.putalpha(sh); base.alpha_composite(b); base.alpha_composite(lay)
def slabs(im,lines,y,size,style):
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay); fnt=F(size)
    for i,txt in enumerate(lines):
        if style=='hook': bg,fg=(RUST,CREAM) if i==0 else (GOLD,INK); al=240
        else: bg,fg=INK,(CREAM if i==0 else GOLD); al=215
        if style=='cap2': fg=CREAM if i<1 else GOLD
        w=d.textlength(txt,font=fnt); yy=y+i*(size+int(size*0.36))
        d.rounded_rectangle([540-w/2-26,yy-11,540+w/2+26,yy+size+int(size*0.28)],radius=18,fill=bg+(al,),outline=(CREAM+(255,)) if style=='hook' else None,width=5 if style=='hook' else 0)
        d.text((540-w/2,yy-int(size*0.07)),txt,font=fnt,fill=fg+(255,))
    with_shadow(im,lay)
def pill(im,txt,cy,size=34,bg=CREAM,fg=INK,x=None):
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay); fnt=F(size); w=d.textlength(txt,font=fnt)
    cx=540 if x is None else x-w/2-26
    d.rounded_rectangle([cx-w/2-26,cy-size*0.95,cx+w/2+26,cy+size*0.95],radius=size,fill=bg+(240,),outline=GOLD+(255,),width=3); d.text((cx-w/2,cy-size*0.68),txt,font=fnt,fill=fg+(255,))
    with_shadow(im,lay,10,0.5)
def wm(im,n):
    d=ImageDraw.Draw(im); f=F(20); t='S L O W   L I G H T'; w=d.textlength(t,font=f)
    d.text((540-w/2,H-52),t,font=f,fill=(240,233,216,150))
    f2=F(24); d.text((W-56,H-50),f'{n}/3',font=f2,fill=(240,233,216,170),anchor='rt')
def edge(im):
    a=np.asarray(im.convert('L')).astype(float); return [(round(b.mean()),round(b.std())) for b in (a[:150],a[-200:],a[:,:80],a[:,-80:])]
# 1 hook
im=grade(Image.open('still-22.80.jpg'),0.5).convert('RGBA')
slabs(im,['HE NEVER','WORE THEM.'],150,104,'hook'); pill(im,'SWIPE  →',1180,30,INK,CREAM,x=None); wm(im,1); im.convert('RGB').save('old-shoes_1of3.png'); print(edge(im))
# 2 backstory
im=grade(Image.open('still-05.90.jpg')).convert('RGBA')
slabs(im,['MY SHOES TORE.','HE BOUGHT','MINE INSTEAD.'],110,74,'cap'); pill(im,'HIS GOT NEW CARDBOARD. EVERY YEAR.',1185,32); wm(im,2); im.convert('RGB').save('old-shoes_2of3.png'); print(edge(im))
# 3 gift
im=grade(Image.open('still-16.00.jpg')).convert('RGBA')
slabs(im,['MY FIRST SALARY','BOUGHT HIM NEW ONES.'],110,70,'cap'); slabs(im,['"I\'LL SAVE THEM','FOR A SPECIAL DAY."'],1010,62,'cap'); wm(im,3); im.convert('RGB').save('old-shoes_3of3.png'); print(edge(im))
