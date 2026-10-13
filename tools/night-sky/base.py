import numpy as np
from PIL import Image, ImageFilter, ImageDraw
W,H=1080,1920
def fbm(h,w,oct=6,seed=0,base=4):
    r=np.random.default_rng(seed); out=np.zeros((h,w),np.float32); amp=1; tot=0
    for o in range(oct):
        n=base*2**o; g=r.random((n+1,n+1)); im=Image.fromarray((g*255).astype(np.uint8)).resize((w,h),Image.BICUBIC)
        out+=amp*np.asarray(im,np.float32)/255.; tot+=amp; amp*=0.55
    return out/tot
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
rng=np.random.default_rng(4)
def add_stars(img,n,maxb=1.0):
    for _ in range(n):
        x,y=rng.integers(1,W-1),rng.integers(1,H-1); b=(rng.random()**3)*maxb
        img[y,x]+=b
        if b>0.5: img[y,x+1]+=b*0.4; img[y+1,x]+=b*0.4; img[y,x-1]+=b*0.4; img[y-1,x]+=b*0.4
    return img
# ---------------- stargazer plate
sky=np.zeros((H,W,3),np.float32)
t=(yy/H)
sky[...,0]=0.015+0.02*t; sky[...,1]=0.025+0.035*t; sky[...,2]=0.06+0.07*t
# milky way band, diagonal
d=((xx-540)*0.55+(yy-700)*0.84)/1.0   # distance across band
band=np.exp(-(d/230)**2)
n1=fbm(H,W,7,3,4); n2=fbm(H,W,6,9,8)
mw=band*(0.35+0.9*n1)*(0.6+0.8*n2)
dust=np.clip((fbm(H,W,6,21,6)-0.55)*3,0,1)*band
mw=np.clip(mw-0.55*dust,0,2)
sky[...,0]+=mw*0.30; sky[...,1]+=mw*0.30; sky[...,2]+=mw*0.36
st=add_stars(np.zeros((H,W),np.float32),1500)
sky+=st[...,None]*np.array([0.95,0.95,1.0])
# hill silhouette
hill_y=1530+60*np.sin(xx/260.0+0.6)+40*np.sin(xx/95.0)-0.06*(xx-540)
mask=yy>hill_y
rim=np.exp(-np.abs(yy-hill_y)/5)*(~mask)*0.0
sky[mask]=np.array([0.006,0.008,0.011])
sky=np.clip(sky,0,1)
im=Image.fromarray((sky*255).astype(np.uint8)); d=ImageDraw.Draw(im)
# stargazer figure standing on hill at x=380
hx=380; hy=int(1530+60*np.sin(hx/260.0+0.6)+40*np.sin(hx/95.0)-0.06*(hx-540))
col=(4,5,8)
d.ellipse((hx-14,hy-150,hx+14,hy-122),fill=col)          # head (tilted up, slightly right)
d.polygon([(hx-20,hy-120),(hx+20,hy-120),(hx+26,hy-40),(hx+14,hy),(hx-14,hy),(hx-26,hy-40)],fill=col) # body
d.line([(hx+18,hy-112),(hx+46,hy-136)],fill=col,width=8)  # arm pointing up
im.save('stargazer_base.png')
# ---------------- andromeda plate
g=np.zeros((H,W,3),np.float32)
g[...]=np.array([0.004,0.005,0.012])
cx,cy=560,880; ang=np.deg2rad(-38)
x=((xx-cx)*np.cos(ang)+(yy-cy)*np.sin(ang))/1.55; y=(-(xx-cx)*np.sin(ang)+(yy-cy)*np.cos(ang))/1.55
y2=y/0.30; r=np.hypot(x,y2)+1e-3; th=np.arctan2(y2,x)
disc=np.exp(-r/330)
arms=0.55+0.45*np.cos(2*th-3.2*np.log(r/60+1)*2.4)
rings=1-0.55*np.exp(-((r-300)/22)**2)-0.45*np.exp(-((r-520)/30)**2)
tex=0.65+0.7*fbm(H,W,7,13,5)
core=np.exp(-(r/55)**2)*2.2+np.exp(-(r/160))*0.55
lum=(disc*arms*rings*tex*0.8+core)*(r<1100)*np.exp(-np.clip(r-800,0,None)/80)
warm=np.clip(np.exp(-r/260),0,1)[...,None]
col=warm*np.array([1.0,0.82,0.55])+(1-warm)*np.array([0.62,0.74,1.0])
g+=lum[...,None]*col*0.9
g+=(add_stars(np.zeros((H,W),np.float32),900))[...,None]*np.array([0.9,0.9,1.0])
# satellites
for (sx,sy,sr) in ((cx-250,cy+170,40),(cx+420,cy-360,70)):
    rr=np.hypot((xx-sx)/1.0,(yy-sy)/1.4); g+=(np.exp(-(rr/sr)**2)*0.55)[...,None]*np.array([1,0.9,0.7])
g=np.clip(g,0,1)
Image.fromarray((g*255).astype(np.uint8)).save('andromeda_base.png')
