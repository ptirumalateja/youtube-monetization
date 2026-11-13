# Telugu caption PNGs (PIL raqm shaping; libass does not shape Telugu here).
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import json, os
F="/tmp/claude-0/ram/fonts/NotoSansTelugu-800.ttf"
EMO="/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
OUT="/tmp/claude-0/ram/work/caps"; os.makedirs(OUT,exist_ok=True)
W,H=1080,1920
Y=(255,214,64); Wh=(255,255,255)
def render(lines,size,y,name,emoji_after=None):
    while True:
        try: return _render(lines,size,y,name,emoji_after)
        except AssertionError as e:
            if size<=80: raise
            size-=4
def _render(lines,size,y,name,emoji_after=None):
    im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    f=ImageFont.truetype(F,size,layout_engine=ImageFont.Layout.RAQM)
    sw=max(6,size//9); lh=int(size*1.45)
    for i,(txt,col) in enumerate(lines):
        bb=d.textbbox((0,0),txt,font=f,stroke_width=sw); w=bb[2]-bb[0]
        ew=0
        if emoji_after is not None and i==emoji_after: ew=int(size*1.15)
        assert w+ew<=870,(txt,w)
        x=(W-w-ew)//2-bb[0]; yy=y+i*lh
        d.text((x,yy),txt,font=f,fill=col,stroke_width=sw,stroke_fill=(0,0,0))
        if ew:
            ef=ImageFont.truetype(EMO,109); e=Image.new("RGBA",(140,140),(0,0,0,0))
            ImageDraw.Draw(e).text((0,0),"👇",font=ef,embedded_color=True)
            e=e.crop(e.getbbox()).resize((int(size*0.95),int(size*0.95)),Image.LANCZOS)
            im.alpha_composite(e,(x+bb[2]+int(size*0.15),yy+bb[1]+(bb[3]-bb[1]-e.height)//2))
    a=im.getbbox()
    if os.environ.get("BOX","1")=="1":
        bg=Image.new("RGBA",(W,H),(0,0,0,0)); bd=ImageDraw.Draw(bg)
        bd.rounded_rectangle((a[0]-34,a[1]-22,a[2]+34,a[3]+22),radius=34,fill=(0,0,0,120))
        sh=Image.new("RGBA",(W,H),(0,0,0,0)); sh.putalpha(im.getchannel("A").point(lambda v:min(255,int(v*0.9))))
        sh=sh.filter(ImageFilter.GaussianBlur(14))
        bg=Image.alpha_composite(bg,sh); bg.alpha_composite(im); im=bg
        a=im.getbbox()
    assert a[1]>=300 and a[3]<=1440 and a[0]>=60 and a[2]<=1020,(name,a)
    im.save(f"{OUT}/{name}.png"); return a
CY=1170  # caption band
caps=[
 (0.00,1.36,[("నీళ్లలో తేలే",Wh),("ఇటుకలతో",Y)],"big"),
 (1.36,2.22,[("కట్టిన గుడి…",Wh)],"big"),
 (2.22,3.20,[("మన తెలంగాణలోనే",Y)],"big"),
 (3.20,4.36,[("ఉందని మీకు తెలుసా?",Wh)],"big"),
 (4.36,5.76,[("ఇది రామప్ప దేవాలయం",Wh)],"c"),
 (5.76,6.80,[("కాకతీయుల కాలంలో",Y)],"c"),
 (6.80,7.92,[("కట్టిన శివాలయం",Wh)],"c"),
 (7.92,9.70,[("గోపురం బరువు",Wh),("తగ్గించడానికి…",Wh)],"c"),
 (9.70,10.84,[("నీళ్లలో తేలేంత",Y)],"c"),
 (10.84,12.40,[("తేలికైన ఇటుకలు వాడారు",Wh)],"c"),
 (12.40,13.16,[("అంతేకాదు,",Wh)],"c"),
 (13.16,14.66,[("పునాది కింద ఇసుక నింపే",Wh)],"c"),
 (14.66,15.92,[("శాండ్‌బాక్స్ టెక్నిక్‌తో",Y)],"c"),
 (15.92,17.94,[("భూకంపాలను",Y),("తట్టుకునేలా కట్టారు",Wh)],"c"),
 (17.94,19.44,[("అందుకే 800 ఏళ్ల",Y)],"c"),
 (19.44,20.40,[("తర్వాత కూడా",Wh)],"c"),
 (20.40,21.86,[("చెక్కుచెదరకుండా",Y),("ఉంది!",Y)],"c"),
 (21.86,23.44,[("ఇలాంటి మరిన్ని",Wh),("విషయాల కోసం…",Wh)],"c"),
 (23.44,99,[("లైక్, షేర్,",Wh),("సబ్‌స్క్రైబ్ చేయండి!",Wh)],"c"),
]
import sys
T=json.load(open(os.environ['TIMES'])) if os.environ.get('TIMES') else None
if T: caps=[(T[i],T[i+1],c[2],c[3]) for i,c in enumerate(caps)]
meta=[]
for i,(a,b,lines,kind) in enumerate(caps):
    if kind=="big": bbox=render(lines,104,420,f"cap{i:02d}")
    else: bbox=render(lines,78,CY,f"cap{i:02d}")
    meta.append((a,b,f"{OUT}/cap{i:02d}.png"))
# end card (text only), upper-middle band
render([("మీరు రామప్ప గుడి",Wh),("చూశారా?",Y),("కామెంట్ చేయండి!",Wh)],92,430,"endcard",emoji_after=2)
json.dump(meta,open(f"{OUT}/caps.json","w"))
print("ok",len(meta))
