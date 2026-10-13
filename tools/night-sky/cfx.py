import numpy as np, subprocess, math
from PIL import Image, ImageDraw, ImageFilter
W,H,N=1080,1920,135
CX,CY=562,883
rng=np.random.default_rng(31); P=2200
born=rng.uniform(0,2.2,P); ang=rng.random(P)*6.283; spd=rng.uniform(140,620,P); r0=rng.uniform(30,220,P); wid=rng.choice([1,1,2,2,3],P); bri=rng.uniform(0.45,1.0,P)
col=[(255,214,150),(200,225,255)]; cc=rng.integers(0,2,P)
p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r","30","-i","-","-c:v","libx264","-crf","10","-pix_fmt","yuv420p","seg/C_fx.mp4"],stdin=subprocess.PIPE)
for f in range(N):
    t=f/30
    if t>3.6: p.stdin.write(bytes(W*H*3)); continue
    im=Image.new("RGB",(W,H),(0,0,0)); d=ImageDraw.Draw(im)
    fade=1.0 if t<2.4 else max(0,1-(t-2.4)/1.0)
    for i in range(P):
        a=t-born[i]
        if a<0: continue
        r=r0[i]+spd[i]*a; x=CX+r*math.cos(ang[i]); y=CY+r*math.sin(ang[i])
        if x<-40 or x>W+40 or y<-40 or y>H+40: continue
        L=min(70,spd[i]*0.05); x2=x-L*math.cos(ang[i]); y2=y-L*math.sin(ang[i])
        v=bri[i]*fade*max(0,1-r/1500)
        if v<0.04: continue
        c=col[cc[i]]; d.line((x2,y2,x,y),fill=(int(c[0]*v),int(c[1]*v),int(c[2]*v)),width=int(wid[i]))
    # shockwave ring
    if t<1.3:
        r=1700*(1-math.exp(-t*3.2)); a=max(0,1-t/1.3)*0.85
        d.ellipse((CX-r,CY-r,CX+r,CY+r),outline=(int(255*a),int(210*a),int(140*a)),width=5)
    g=im.filter(ImageFilter.GaussianBlur(4))
    arr=np.clip(np.asarray(im,np.float32)+np.asarray(g,np.float32)*1.3,0,255).astype(np.uint8)
    p.stdin.write(arr.tobytes())
p.stdin.close(); p.wait(); print("C_fx done")
