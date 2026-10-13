import numpy as np, subprocess, math
from PIL import Image, ImageDraw, ImageFilter
W,H,FPS=1080,1920,30
SX,SY=540,800
rng=np.random.default_rng(21)
def ease(u): u=max(0,min(1,u)); return u*u*(3-2*u)
def zoom(t):
    if t<0.5: return 1.0+0.03*t/0.5
    if t<1.0: return 1.03+(3.6-1.03)*ease((t-0.5)/0.5)
    if t<1.7: return 3.6+(5.5-3.6)*((t-1.0)/0.7)
    return 5.5*math.exp(math.log(18/5.5)*ease((t-1.7)/0.4))
def zexpr():
    # zoompan expression string equivalent (on = frame index)
    e=lambda u:f"({u}*{u}*(3-2*{u}))"
    t="(on/30)"
    u1=f"clip(({t}-0.5)/0.5,0,1)"; u3=f"clip(({t}-1.7)/0.4,0,1)"
    return (f"if(lt({t},0.5),1+0.03*{t}/0.5,if(lt({t},1.0),1.03+2.57*{e(u1)},if(lt({t},1.7),3.6+1.9*(({t}-1.0)/0.7),5.5*exp(1.1896*{e(u3)}))))")
open("zexpr.txt","w").write(zexpr())
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
def amp(t):
    a=0.45+0.9*math.exp(-t/0.10)                      # hit at 0.0
    a+=0.7*math.exp(-((t-0.5)/0.05)**2)                # snap
    if 0.5<=t<1.7: a+=0.35+0.4*ease((t-0.5)/1.2)
    if t>=1.7: a+=0.75+1.0*ease((t-1.7)/0.4)
    return a
def ring_layer(t,z):
    if not (1.0<=t<2.1): return None
    u=ease((t-1.0)/0.9); r=40+360*u+ (80*max(0,(t-1.7)/0.4))
    im=Image.new("RGB",(W,H),(0,0,0)); d=ImageDraw.Draw(im)
    n=1500; rr=np.random.default_rng(7); th0=rr.random(n)*6.283; om=(rr.random(n)*1.2+0.6)*(1 if t>0 else 1); jit=rr.normal(0,1,n); sz=rr.random(n)
    a=min(1.0,(t-1.0)/0.2)*(1-ease((t-1.95)/0.15))
    for i in range(n):
        th=th0[i]+om[i]*(t-1.0)*2.2; rad=r+jit[i]*(5+10*u)
        x=SX+rad*math.cos(th); y=SY+rad*math.sin(th)
        s=1+2*sz[i]**2; c=(int(255*a),int(205*a),int(130*a)) if sz[i]<0.75 else (int(255*a),int(245*a),int(225*a))
        d.ellipse((x-s,y-s,x+s,y+s),fill=c)
    # bright thin core ring
    d.ellipse((SX-r,SY-r,SX+r,SY+r),outline=(int(150*a),int(110*a),int(60*a)),width=2)
    return im.filter(ImageFilter.GaussianBlur(1.2))
def speed_lines(t,alpha,n=34):
    im=Image.new("RGB",(W,H),(0,0,0)); d=ImageDraw.Draw(im); rr=np.random.default_rng(int(t*100)+3)
    for _ in range(n):
        a=rr.random()*6.283; r0=rr.uniform(250,600); w=rr.uniform(0.003,0.009); r1=1700
        p=[(SX+r0*math.cos(a),SY+r0*math.sin(a)),(SX+r1*math.cos(a-w),SY+r1*math.sin(a-w)),(SX+r1*math.cos(a+w),SY+r1*math.sin(a+w))]
        c=int(255*alpha); d.polygon(p,fill=(c,c,c))
    return im
def star_layer(t,z,base_amp):
    d=np.hypot(xx-SX,yy-SY); s=16*z**0.85
    core=np.exp(-(d/s)**2)*1.3+np.exp(-d/(s*3.5))*0.30
    hs=np.exp(-((yy-SY)/(2.0*z**0.5))**2)*np.exp(-np.abs(xx-SX)/(130*z**0.65))
    vs=np.exp(-((xx-SX)/(2.0*z**0.5))**2)*np.exp(-np.abs(yy-SY)/(130*z**0.65))
    g=(core+0.7*(hs+vs))*base_amp
    # soft sky glow lit by the flare
    g+=np.exp(-d/(380*z**0.5))*0.16*base_amp
    return np.stack([g*1.0,g*0.93,g*0.82],-1)
p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-crf","10","-pix_fmt","yuv420p","seg/A_fx.mp4"],stdin=subprocess.PIPE)
for on in range(63):
    t=on/FPS; z=zoom(t)
    img=star_layer(t,z,min(1.8,amp(t)))
    rl=ring_layer(t,z)
    if rl is not None: img=img+np.asarray(rl,np.float32)/255.
    for t0,al in ((0.5,0.45),(0.53,0.35),(0.57,0.22),(0.6,0.12),(1.75,0.30),(1.85,0.40),(1.95,0.45)):
        if abs(t-t0)<0.5/FPS: img=img+np.asarray(speed_lines(t,al),np.float32)/255.
    if abs(t-0.5)<0.5/FPS: img=img+0.28            # soft impact frame
    p.stdin.write((np.clip(img,0,1)*255).astype(np.uint8).tobytes())
p.stdin.close(); p.wait(); print("A_fx done")
