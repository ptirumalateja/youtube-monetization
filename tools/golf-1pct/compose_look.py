# Text layer for the look-test stills. python3 compose_look.py <lookdir>
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D=sys.argv[1]
CREAM=(243,234,214); RED=(200,38,30); GOLD=(255,196,110)
BOLD='/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf'
MED='/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf'
def F(p,s): return ImageFont.truetype(p,s)
def text(img,xy,s,font,fill=CREAM,anchor='mm',spacing=0,shadow=10):
    lay=Image.new('RGBA',img.size,(0,0,0,0)); d=ImageDraw.Draw(lay)
    if spacing:
        w=sum(d.textlength(c,font=font) for c in s)+spacing*(len(s)-1)
        x=xy[0]-w/2
        for c in s:
            d.text((x,xy[1]),c,font=font,fill=fill,anchor='lm'); x+=d.textlength(c,font=font)+spacing
    else: d.text(xy,s,font=font,fill=fill,anchor=anchor)
    sh=Image.new('RGBA',img.size,(0,0,0,0)); sh.putalpha(lay.split()[3].filter(ImageFilter.GaussianBlur(shadow)).point(lambda a:int(a*0.75)))
    img.alpha_composite(sh); img.alpha_composite(lay)
def chip(img,cx,cy,s,font):
    d=ImageDraw.Draw(img); w=d.textlength(s,font=font)+44
    d.rounded_rectangle((cx-w/2,cy-34,cx+w/2,cy+34),radius=12,fill=RED+(255,))
    d.text((cx,cy+2),s,font=font,fill=CREAM,anchor='mm')

# 1) hook frame 0
h=Image.open(f'{D}/hook.png').convert('RGBA')
g=Image.new('RGBA',h.size,(0,0,0,0)); gd=ImageDraw.Draw(g)
for y in range(0,760): gd.line([(0,y),(1080,y)],fill=(6,12,18,int(150*(1-y/760)**1.6)))
h.alpha_composite(g)
text(h,(540,380),'ONLY 1% SEE',F(BOLD,132))
text(h,(540,530),'THIS HOLE.',F(BOLD,132))
text(h,(540,660),'34 MISSES LATER',F(MED,40),fill=GOLD,spacing=6,shadow=6)
h.convert('RGB').save(f'{D}/look_hook_frame0.jpg',quality=93)

# 2) closing three-row frame
rows=[('row93','93% OF PEOPLE','NEVER SWING.'),('row6','6% OF PEOPLE','MISS ONCE. QUIT.'),('row1','1% OF PEOPLE','MISS 34 TIMES. SINK IT.')]
c=Image.new('RGBA',(1080,1920))
for i,(f,lab,res) in enumerate(rows):
    im=Image.open(f'{D}/{f}.png').convert('RGBA'); c.paste(im,(0,i*640))
d=ImageDraw.Draw(c)
for y in (640,1280): d.line([(0,y),(1080,y)],fill=(243,234,214,70),width=2)
for i,(f,lab,res) in enumerate(rows):
    y0=i*640
    if i==2: chip(c,540,y0+92,lab,F(BOLD,40))
    else: text(c,(540,y0+92),lab,F(MED,38),spacing=5,shadow=6)
    text(c,(540,y0+158),res,F(BOLD,58 if i<2 else 62),fill=(CREAM if i<2 else GOLD),shadow=8)
c.convert('RGB').save(f'{D}/look_rows_close.jpg',quality=93)
# side-by-side for chat
s=Image.new('RGB',(2160+40,1920),(20,24,28)); s.paste(Image.open(f'{D}/look_hook_frame0.jpg'),(0,0)); s.paste(Image.open(f'{D}/look_rows_close.jpg'),(1120,0))
s.resize((1100,960)).save(f'{D}/look_pair.jpg',quality=90)
