from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os
D="/tmp/claude-0/ram/thumb/"; F="/tmp/claude-0/ram/fonts/NotoSansTelugu-800.ttf"
W,H=1080,1920; Y=(255,214,64); Wh=(255,255,255)
def crop(p,box=None):
    im=Image.open(D+p).convert("RGB").crop((74,0,1005,1655)).resize((W,int(1655*W/931)),Image.LANCZOS)
    return im.crop((0,0,W,H))
def text(im,lines,y,size,boxa=150):
    lay=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    lh=int(size*1.35); yy=y; bbs=[]
    for txt,col,sz in lines:
        f=ImageFont.truetype(F,sz,layout_engine=ImageFont.Layout.RAQM)
        bb=d.textbbox((0,0),txt,font=f,stroke_width=sz//9); w=bb[2]-bb[0]
        while w>900: sz-=4; f=ImageFont.truetype(F,sz,layout_engine=ImageFont.Layout.RAQM); bb=d.textbbox((0,0),txt,font=f,stroke_width=sz//9); w=bb[2]-bb[0]
        x=(W-w)//2-bb[0]; d.text((x,yy),txt,font=f,fill=col,stroke_width=sz//9,stroke_fill=(0,0,0)); yy+=int(sz*1.35)
    a=lay.getbbox()
    bg=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(bg).rounded_rectangle((a[0]-40,a[1]-28,a[2]+40,a[3]+28),radius=40,fill=(0,0,0,boxa))
    sh=Image.new("RGBA",(W,H),(0,0,0,0)); sh.putalpha(lay.getchannel("A")); sh=sh.filter(ImageFilter.GaussianBlur(18))
    out=im.convert("RGBA"); out=Image.alpha_composite(out,bg); out=Image.alpha_composite(out,sh); out=Image.alpha_composite(out,lay)
    assert a[1]>=300 and a[3]<=1440,a
    return out.convert("RGB")
# A: floating brick in a bowl, full frame
a=ImageEnhance.Contrast(ImageEnhance.Brightness(crop("hold.png")).enhance(1.06)).enhance(1.08)
a=text(a,[("తేలే ఇటుకల",Wh,150),("గుడి!",Y,190)],330,150)
a=text(a,[("రామప్ప • మన తెలంగాణ",Wh,80)],1010,80,boxa=140)
a.save(D+"ramappa_thumb_A.jpg",quality=93)
# B: temple top half, floating brick bottom half, text across the seam
t=crop("temple.png").crop((0,180,W,1140)); b=crop("hold.png").crop((0,620,W,1580))
bb=Image.new("RGB",(W,H)); bb.paste(t,(0,0)); bb.paste(b,(0,960))
dr=ImageDraw.Draw(bb); dr.rectangle((0,954,W,966),fill=(255,214,64))
bb=text(bb,[("ఈ గుడి ఇటుకలు",Wh,120),("నీళ్లలో తేలుతాయి!",Y,120)],760,120,boxa=170)
bb.save(D+"ramappa_thumb_B.jpg",quality=93)
print("ok")
