"""Dark illustrative map of the Southern California Bight (Natural Earth, public domain)."""
import json, math, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
W,H=1920,1080
HERE=__file__.rsplit('/',1)[0]
LAND=json.load(open(HERE+'/data/land_socal.json'))
COAST=json.load(open(HERE+'/data/coast_socal.json'))
FB='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def font(sz,bold=True):
    for f in (['/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf'] if bold else [])+[FB]:
        try: return ImageFont.truetype(f,sz)
        except OSError: pass
NIMITZ=(-117.9,31.6)   # illustrative position, ~100 mi SW of San Diego
SANDIEGO=(-117.16,32.72)
def proj(lon,lat,c,s):
    k=math.cos(math.radians(c[1]))
    return (W/2+(lon-c[0])*s*k, H/2-(lat-c[1])*s)
def ease(x): x=min(max(x,0),1); return x*x*(3-2*x)
def render(t,c=(-118.2,32.2),s=220,marker=1.0,cap=0.0,labels=1.0,grid=1.0):
    S=2
    im=Image.new('RGB',(W*S,H*S),(6,10,20)); d=ImageDraw.Draw(im)
    # sea dot grid
    if grid>0:
        g=int(26*S); col=(int(20*grid)+6,int(32*grid)+10,int(52*grid)+20)
        off=int((t*6*S)%g)
        for y in range(-g,H*S+g,g):
            for x in range(-g,W*S+g,g):
                d.ellipse([x+off-2,y-2,x+off+2,y+2],fill=col)
    for r in LAND:
        pts=[(p[0]*S,p[1]*S) for p in (proj(a,b,c,s) for a,b in r)]
        d.polygon(pts,fill=(22,22,28))
    glow=Image.new('RGB',(W*S,H*S),(0,0,0)); gd=ImageDraw.Draw(glow)
    for r in COAST:
        pts=[(p[0]*S,p[1]*S) for p in (proj(a,b,c,s) for a,b in r)]
        gd.line(pts,fill=(235,215,180),width=3*S)
    im=Image.fromarray(np.clip(np.asarray(im,dtype=np.int32)+np.asarray(glow.filter(ImageFilter.GaussianBlur(10*S)),dtype=np.int32)*0.5+np.asarray(glow,dtype=np.int32)*0.55,0,255).astype(np.uint8))
    im=im.resize((W,H),Image.LANCZOS); d=ImageDraw.Draw(im,'RGBA')
    ov=Image.new('RGBA',(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    nx,ny=proj(*NIMITZ,c,s)
    if marker>0:
        for k in range(3):
            ph=((t*0.7+k/3)%1.0)
            R=10+ph*120; a=int(200*(1-ph)*marker)
            od.ellipse([nx-R,ny-R,nx+R,ny+R],outline=(230,40,40,a),width=3)
        od.ellipse([nx-9,ny-9,nx+9,ny+9],fill=(235,45,45,int(255*marker)))
    if cap>0:
        # 60 nautical-ish miles (~1 deg) illustrative jump to CAP point
        cx,cy=proj(NIMITZ[0]-1.0,NIMITZ[1]+0.35,c,s)
        e=ease(cap)
        od.line([nx,ny,nx+(cx-nx)*e,ny+(cy-ny)*e],fill=(240,230,210,220),width=3)
        if cap>0.95:
            od.ellipse([cx-12,cy-12,cx+12,cy+12],outline=(240,230,210,255),width=3)
            od.text((cx-20,cy-60),'CAP POINT',font=font(34),fill=(240,230,210,255),anchor='rs')
    ovb=ov.filter(ImageFilter.GaussianBlur(6))
    im=Image.alpha_composite(Image.alpha_composite(im.convert('RGBA'),ovb),ov)
    d=ImageDraw.Draw(im)
    if labels>0:
        a=int(255*labels)
        sx,sy=proj(*SANDIEGO,c,s)
        d.ellipse([sx-6,sy-6,sx+6,sy+6],fill=(240,230,210,a))
        d.text((sx+18,sy),'SAN DIEGO',font=font(30),fill=(240,230,210,a),anchor='lm')
        px,py=proj(-120.6,31.0,c,s)
        d.text((px,py),'P A C I F I C   O C E A N',font=font(30),fill=(120,140,170,a),anchor='mm')
        if marker>0:
            d.text((nx+26,ny+4),'USS NIMITZ STRIKE GROUP',font=font(30),fill=(240,230,210,int(a*marker)),anchor='lm')
    return im.convert('RGB')
if __name__=='__main__':
    render(1.0,cap=1.0).save('stills/map.jpg',quality=92)
