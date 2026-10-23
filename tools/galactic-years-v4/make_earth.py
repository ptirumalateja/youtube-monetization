# Builds the present-day Earth maps used by index.html from Natural Earth land polygons (public domain).
# python3 make_earth.py land_rings.json  -> earth_today.png (RGB land albedo, ocean left dark) + earth_aux.png (R land, G shelf, B ice)
import json, sys, math, numpy as np
from PIL import Image, ImageDraw, ImageFilter
W,H=4096,2048
rings=json.load(open(sys.argv[1]))
m=Image.new('L',(W,H),0); d=ImageDraw.Draw(m)
def px(r): return [((lo+180)/360*W,(90-la)/180*H) for lo,la in r]
def unwrap(r):  # rings that cross the antimeridian: make longitudes continuous, then draw twice (shifted by 360)
    out=[list(r[0])]
    for lo,la in r[1:]:
        p=out[-1][0]
        while lo-p>180: lo-=360
        while lo-p<-180: lo+=360
        out.append([lo,la])
    return out
for poly in rings:
    for k,ring in enumerate(poly):
        u=unwrap(ring); span=max(a for a,_ in u)-min(a for a,_ in u)
        if span>350 and k==0:      # Antarctica: close the ring along the pole
            d.polygon(px(ring),fill=255); continue
        for sh in (-360,0,360): d.polygon(px([[a+sh,b] for a,b in u]),fill=0 if k else 255)
land=np.asarray(m,np.float32)/255
def blur(a,r): return np.asarray(Image.fromarray((a*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r)),np.float32)/255
cont=blur(land,90)                    # continentality: how far inland
shelf=np.clip(blur(land,14)*2.2,0,1)*(1-land)
lat=np.repeat(np.linspace(90,-90,H)[:,None],W,1); lon=np.repeat(np.linspace(-180,180,W)[None,:],H,0); al=np.abs(lat)
rng=np.random.default_rng(7)
def fbm(sc,oct=5):
    out=np.zeros((H,W),np.float32); a=1.0
    for o in range(oct):
        n=rng.standard_normal((max(2,int(H/sc*2**o)),max(2,int(W/sc*2**o)))).astype(np.float32)
        out+=a*np.asarray(Image.fromarray(n).resize((W,H),Image.BICUBIC)); a*=0.5
    return out/1.9
nz=fbm(256); nz2=fbm(64)
sm=lambda a,b,x: np.clip((x-a)/(b-a),0,1)**2*(3-2*np.clip((x-a)/(b-a),0,1))
# aridity: subtropical deserts inland (Sahara, Arabia, Australia, Kalahari, Atacama), dry interiors (Gobi, central Asia)
arid=np.exp(-((al-23)/9.5)**2)*sm(0.35,0.75,cont+0.15*nz)
arid=np.maximum(arid,0.75*sm(36,44,lat)*(1-sm(50,56,lat))*sm(0.6,0.85,cont)*sm(40,60,lon)) # central Asia
arid=np.maximum(arid,0.9*np.exp(-((lat+22)/7)**2)*sm(-76,-72,lon)*(1-sm(-69,-66,lon)))       # Atacama
arid*=1-0.8*(sm(-64,-58,lon)*(1-sm(-36,-30,lon))*sm(-8,-12,lat)*(1-sm(-28,-34,lat)))  # Brazil/Chaco: savanna, not desert
arid=np.clip(arid+0.12*nz2,0,1)
cold=sm(52,70,al+4*nz)
C=lambda r,g,b: np.array([r,g,b],np.float32)
forest=C(0.10,0.22,0.08); trop=C(0.06,0.20,0.06); sav=C(0.42,0.40,0.20); desert=C(0.66,0.46,0.24); rust=C(0.70,0.45,0.28); tundra=C(0.40,0.38,0.30); ice=C(0.93,0.95,0.98)
w_trop=sm(14,4,al)
veg=forest[None,None]*(1-w_trop[...,None])+trop[None,None]*w_trop[...,None]
col=veg*(1-arid[...,None])+(sav*(1-sm(0.5,0.85,arid))[...,None]+desert*sm(0.5,0.85,arid)[...,None])*arid[...,None]
col=np.where((arid>0.7)[...,None]&(nz2[...,None]>0.3),rust,col)*(1)  # rusty patches in the deepest deserts
col=col*(1-cold[...,None])+tundra*cold[...,None]
icem=np.clip(sm(-60,-66,lat)+ (sm(60,66,lat)*sm(-74,-70,lon)*(1-sm(-22,-14,lon))) + sm(78,82,lat),0,1)*land
col=col*(1-icem[...,None])+ice*icem[...,None]
col*=(0.85+0.3*nz2[...,None]*0.5+0.15)[...,:]
col=np.clip(col,0,1)*land[...,None]
Image.fromarray((col**(1/2.2)*255).astype(np.uint8)).resize((2048,1024),Image.LANCZOS).save('earth_today.png')
aux=np.stack([land,shelf,icem],-1)
Image.fromarray((aux*255).astype(np.uint8)).resize((2048,1024),Image.LANCZOS).save('earth_aux.png')
print('ok land fraction',land.mean())
