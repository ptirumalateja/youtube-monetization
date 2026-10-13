import numpy as np, subprocess, math
W,H=1080,1920; FPS=30; N=63
SX,SY=540,800
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
def pulse(t,c,w,a): return a*math.exp(-((t-c)/w)**2)
def zoom(on): return 1+0.05*on/51 if on<51 else 1.05*math.exp(2.2*(on-51)/12)
p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-crf","10","-pix_fmt","yuv420p","seg/flare_A.mp4"],stdin=subprocess.PIPE)
for on in range(N):
    t=on/FPS; z=zoom(on)
    amp=0.30+pulse(t,0.32,0.09,0.55)+pulse(t,0.86,0.10,0.75)+pulse(t,1.30,0.11,0.95)+(1.0*((t-1.45)/0.25) if 1.45<=t<1.70 else 0)+(1.0 if t>=1.70 else 0)
    amp=min(amp,1.6)
    d=np.hypot(xx-SX,yy-SY); s=18*z**0.9
    core=np.exp(-(d/s)**2)*1.4+np.exp(-d/(s*3.2))*0.35
    hs=np.exp(-((yy-SY)/(2.2*z**0.5))**2)*np.exp(-np.abs(xx-SX)/(160*z**0.7))
    vs=np.exp(-((xx-SX)/(2.2*z**0.5))**2)*np.exp(-np.abs(yy-SY)/(160*z**0.7))
    g=(core+0.8*(hs+vs))*amp
    rgb=np.stack([g*1.0,g*0.93,g*0.82],-1)
    p.stdin.write((np.clip(rgb,0,1)*255).astype(np.uint8).tobytes())
p.stdin.close(); p.wait(); print("flare done")
