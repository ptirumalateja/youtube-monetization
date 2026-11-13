import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
src,out=sys.argv[1],sys.argv[2]
im=Image.open(src).convert('RGB')
# bloom: brighten highlights softly
hi=im.point(lambda v: max(0,v-238)*5)
bl=hi.filter(ImageFilter.GaussianBlur(28))
im=ImageChops.add(im,bl.point(lambda v:int(v*0.30)))
W,H=im.size; d=ImageDraw.Draw(im,'RGBA')
B='/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf'
SB='/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
ink=(28,34,52,255); gold=(214,104,40,255)
def center(y,txt,font,fill,shadow=True):
    w=d.textlength(txt,font=font); x=(W-w)/2
    assert w<=W-220, (txt,w)
    if shadow:
        g=Image.new('L',im.size,0); ImageDraw.Draw(g).text((x,y),txt,font=font,fill=255)
        g=g.filter(ImageFilter.GaussianBlur(14))
        im.paste(Image.new('RGB',im.size,(255,250,240)),(0,0),g.point(lambda v:int(v*0.85)))
    d.text((x,y),txt,font=font,fill=fill)
    return w
f1=ImageFont.truetype(SB,50); f2=ImageFont.truetype(B,128)
center(330,"Why do fingers wrinkle in water?",f1,ink)
center(420,"IT'S NOT",f2,ink)
center(560,"THE WATER.",f2,gold)
im.save(out,quality=92)
# guides copy
g=im.copy(); gd=ImageDraw.Draw(g)
for y in (300,1440): gd.line([(0,y),(W,y)],fill=(0,200,255),width=3)
for x in (110,W-110): gd.line([(x,0),(x,H)],fill=(0,200,255),width=2)
g.resize((540,960)).save(out.replace('.jpg','_guides.jpg'),quality=85)
