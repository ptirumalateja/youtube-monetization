"""India Ep 1, edit v2: existing globe renders + fold + Everest, cut to the v3 voiceover with
speed ramps, punch-ins, impact (flash / shake / shockwave / chroma), data panels and a sound design pass.
usage: python3 edit_ep1_v2.py <assets_dir> <out.mp4>"""
import sys, os, subprocess, math, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageChops
A,OUT=sys.argv[1],sys.argv[2]; P=lambda f:os.path.join(A,f); VID=os.path.join(os.path.dirname(os.path.abspath(OUT)),"_ep1_video.mp4")
W,H,FPS=1080,1920,24; TOTAL=28.95; N=int(round(TOTAL*FPS))
FB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; FR="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
font=lambda s,b=True: ImageFont.truetype(FB if b else FR,s)
def decode(path):
    w,h=W,H; raw=subprocess.run(["ffmpeg","-v","error","-i",path,"-vf",f"scale={w}:{h},fps={FPS}","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
    return np.frombuffer(raw,np.uint8).reshape(-1,h,w,3)
CLIP={k:decode(P(f)) for k,f in {"race":"race_clean.mp4","s4":"shot4_clean.mp4","s7":"shot7_clean.mp4","s10":"shot10_clean.mp4","fold":"fold.mp4","ev":"everest.mp4"}.items()}
ease=lambda u: (lambda v: v*v*(3-2*v))(min(max(u,0),1))
CONTACT=(470,955)
# segments: (out_t0, out_t1, clip, src_t0, src_t1, zoom0, zoom1, centre0, centre1)
SEG=[(0.00,3.20,"race",0.0,3.0,1.30,1.60,(540,1180),(540,1100)),
     (3.20,3.85,"s7",3.30,4.0,1.9,2.4,(520,1000),CONTACT),
     (3.85,4.35,"s7",3.99,3.99,2.4,2.6,CONTACT,CONTACT),
     (4.35,5.20,None,0,0,1,1,None,None),
     (5.20,9.60,"s4",0.0,4.0,1.35,1.55,(540,1150),(560,1080)),
     (9.60,11.60,"race",0.6,3.0,1.50,1.75,(540,1150),(540,1060)),
     (11.60,14.56,"s7",0.0,3.96,1.40,1.95,(540,1120),CONTACT),
     (14.56,15.60,"s7",3.99,3.99,1.95,2.25,CONTACT,CONTACT),
     (15.60,19.90,"fold",0.0,5.0,1.00,1.08,(540,960),(540,900)),
     (19.90,25.25,"ev",0.0,5.0,1.00,1.12,(540,960),(540,900)),
     (25.25,TOTAL,"s10",0.0,3.0,1.35,1.50,(540,1150),(560,1080))]
IMPACTS=[3.85,14.56]
def src_frame(clip,t):
    fr=CLIP[clip]; return fr[min(int(round(t*FPS)),len(fr)-1)]
def shockwave(img,t_since,c):
    if not (0<=t_since<0.8): return img
    u=t_since/0.8; r=40+700*ease(u**0.7); d=ImageDraw.Draw(img,"RGBA")
    for k,(w,a) in enumerate([(16,190),(6,255)]):
        al=int(a*(1-u)); d.ellipse([c[0]-r,c[1]-r*0.42,c[0]+r,c[1]+r*0.42],outline=(255,225,180,al),width=max(1,int(w*(1-u))))
    return img
# ---------- text / panels
def stroke_text(d,xy,txt,f,fill=(255,255,255,255),anchor="mm",sw=5):
    d.text(xy,txt,font=f,fill=fill,anchor=anchor,stroke_width=sw,stroke_fill=(0,0,0,int(fill[3]*0.85)))
def fade(t,t0,t1,fi=0.15,fo=0.2):
    if t<t0 or t>t1: return 0
    return min(1,(t-t0)/fi,(t1-t)/fo)
def panel(d,x,y,label,value,a):
    if a<=0: return
    w,h=560,170; d.rounded_rectangle([x,y,x+w,y+h],22,fill=(8,14,28,int(170*a)),outline=(120,200,255,int(150*a)),width=3)
    d.text((x+30,y+26),label,font=font(30,False),fill=(170,215,255,int(255*a)))
    d.text((x+30,y+68),value,font=font(70),fill=(255,255,255,int(255*a)))
def lerp(a,b,u): return a+(b-a)*min(max(u,0),1)
def overlay(t):
    L=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
    a=fade(t,0.0,3.85,0.01); 
    if a: 
        stroke_text(d,(W//2,330),"INDIA IS ABOUT",font(84),(255,255,255,int(255*a))); stroke_text(d,(W//2,430),"TO HIT ASIA",font(84),(255,210,120,int(255*a)))
        if t<3.2:
            yr=int(round(lerp(80,52,t/3.2))); panel(d,60,1240,"YEAR",f"{yr} MILLION YRS AGO",a)
            km=int(round(lerp(4470,1260,t/3.2),-1)); panel(d,60,1430,"DISTANCE TO ASIA",f"{km:,} km",a)
    # title slam on black, carries into the breakaway
    if t>=5.05:
        a=fade(t,5.05,7.6,0.01); s=1+0.35*max(0,1-(t-5.05)/0.12)
        if a: stroke_text(d,(W//2,330),"90 MILLION",font(int(96*s)),(255,255,255,int(255*a))); stroke_text(d,(W//2,440),"YEARS AGO",font(int(96*s)),(255,255,255,int(255*a)))
    a=fade(t,6.7,9.5); 
    if a: stroke_text(d,(W//2,560),"INDIA BREAKS FREE",font(64),(255,210,120,int(255*a)))
    a=fade(t,9.66,11.55); 
    if a: panel(d,60,1300,"SPEED","~20 CM / YEAR",a); stroke_text(d,(W//2,360),"5× FASTER",font(92),(255,210,120,int(255*a)))
    if 11.60<=t<15.6:
        a=fade(t,11.60,15.5)
        stroke_text(d,(W//2,330),"50 MILLION",font(90),(255,255,255,int(255*a))); stroke_text(d,(W//2,435),"YEARS AGO",font(90),(255,255,255,int(255*a)))
        if t<14.56: km=int(round(lerp(1020,30,(t-11.60)/2.96),-1)); panel(d,60,1360,"DISTANCE TO ASIA",f"{max(km,30):,} km",a)
        else: 
            b=fade(t,14.56,15.5,0.05); stroke_text(d,(W//2,1450),"CONTACT",font(110),(255,120,60,int(255*b)),sw=7)
    a=fade(t,15.75,17.9); 
    if a: stroke_text(d,(W//2,330),"OCEAN FLOOR",font(84),(255,255,255,int(255*a))); stroke_text(d,(W//2,430),"CRUSHED",font(84),(255,210,120,int(255*a)))
    a=fade(t,18.1,19.85); 
    if a: stroke_text(d,(W//2,330),"PUSHED INTO",font(84),(255,255,255,int(255*a))); stroke_text(d,(W//2,430),"THE SKY",font(84),(255,210,120,int(255*a)))
    a=fade(t,20.6,23.1); 
    if a: stroke_text(d,(W//2,330),"EVEREST'S SUMMIT",font(76),(255,255,255,int(255*a))); stroke_text(d,(W//2,430),"= ANCIENT SEAFLOOR",font(76),(255,210,120,int(255*a)))
    a=fade(t,23.2,25.2); 
    if a: stroke_text(d,(W//2,330),"FULL OF",font(84),(255,255,255,int(255*a))); stroke_text(d,(W//2,430),"SEA FOSSILS",font(84),(255,210,120,int(255*a)))
    a=fade(t,25.3,TOTAL,0.15,0.01)
    if a: stroke_text(d,(W//2,330),"STILL MOVING",font(84),(255,255,255,int(255*a))); panel(d,60,1360,"INDIA → ASIA","~4 CM / YEAR",a)
    a=fade(t,27.1,TOTAL,0.1,0.01)
    if a: stroke_text(d,(W//2,440),"EVEREST IS STILL RISING",font(62),(255,210,120,int(255*a)))
    return L
# ---------- render
if not os.environ.get("SKIP_VIDEO"):
  enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
       "-vf","unsharp=5:5:0.6,noise=alls=3:allf=t+u,format=yuv420p","-c:v","libx264","-crf","17","-preset","slow",VID],stdin=subprocess.PIPE)
  for n in range(N):
      t=n/FPS; seg=next(s for s in SEG if s[0]<=t<s[1] or (s is SEG[-1]))
      t0,t1,clip,a0,a1,z0,z1,c0,c1=seg; u=(t-t0)/(t1-t0)
      if clip is None: frame=Image.new("RGB",(W,H),(0,0,0))
      else:
          src=Image.fromarray(src_frame(clip,a0+(a1-a0)*u))
          for ti in IMPACTS: src=shockwave(src,t-ti,CONTACT)
          z=lerp(z0,z1,ease(u)); cx=lerp(c0[0],c1[0],ease(u)); cy=lerp(c0[1],c1[1],ease(u))
          sx=sy=0
          for ti in IMPACTS:
              if 0<=t-ti<0.6: k=math.exp(-(t-ti)*7); sx+=26*k*math.sin((t-ti)*90); sy+=34*k*math.cos((t-ti)*70)
          vw,vh=W/z,H/z; cx=min(max(cx+sx,vw/2),W-vw/2); cy=min(max(cy+sy,vh/2),H-vh/2)
          frame=src.crop((int(cx-vw/2),int(cy-vh/2),int(cx+vw/2),int(cy+vh/2))).resize((W,H),Image.BICUBIC)
          for ti in IMPACTS:
              dt=t-ti
              if 0<=dt<0.3:  # chromatic aberration
                  k=int(14*(1-dt/0.3)); r,g,b=frame.split(); frame=Image.merge("RGB",(ImageChops.offset(r,k,0),g,ImageChops.offset(b,-k,0)))
              if 0<=dt<0.2: frame=Image.blend(frame,Image.new("RGB",(W,H),(255,244,230)),0.9*(1-dt/0.2))
      if 5.05<=t<5.13: frame=Image.blend(frame,Image.new("RGB",(W,H),(255,255,255)),0.5*(1-(t-5.05)/0.08))
      frame=Image.alpha_composite(frame.convert("RGBA"),overlay(t)).convert("RGB")
      enc.stdin.write(frame.tobytes())
  enc.stdin.close(); enc.wait()
# ---------- sound design
S=lambda f:P(os.path.join("sfx",f))
ins=["-i",VID,"-i",P("india_ep1_vo_v3.mp3"),
     "-ss","5.0","-t","14.56","-i",S("music.mp3"),          # 2: tension build, peaks into the impact
     "-ss","34.0","-t","13.65","-i",S("music.mp3"),         # 3: second swell after the impact
     "-i",S("riser.mp3"),"-i",S("impact.mp3"),"-i",S("impact.mp3"),"-i",S("titlehit.mp3"),"-i",S("rift.mp3"),
     "-i",S("whoosh.mp3"),"-i",S("grind.mp3"),"-i",S("grind.mp3"),"-stream_loop","5","-i",S("wind.mp3"),"-stream_loop","4","-i",S("pulse.mp3")]
def at(i,t,vol,extra=""): ms=int(t*1000); return f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo{extra},volume={vol},adelay={ms}|{ms}[a{i}];"
fc=("[1:a]loudnorm=I=-16:TP=-1.5,aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[vo][vosc];"
    "[2:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.30,afade=t=in:d=0.3,afade=t=out:st=14.40:d=0.16[a2];"
    +at(3,15.30,0.30,",afade=t=in:d=0.8,afade=t=out:st=12.4:d=1.2")
    +at(4,0.00,0.55)+at(5,3.78,1.0)+at(6,14.49,1.0)+at(7,4.13,0.8)+at(8,6.60,0.8)+at(9,9.50,0.7)
    +at(10,14.60,0.75)+at(11,16.10,0.7)+at(12,19.90,0.45,",atrim=0:5.3,afade=t=in:d=0.5,afade=t=out:st=4.8:d=0.5")
    +at(13,25.25,0.6,",atrim=0:3.7"))
mix="".join(f"[a{i}]" for i in range(2,14))
fc+=f"{mix}amix=inputs=12:normalize=0[fx];[fx][vosc]sidechaincompress=threshold=0.05:ratio=6:attack=20:release=300[fxd];"
fc+=f"[fxd][vo]amix=inputs=2:normalize=0,atrim=0:{TOTAL},loudnorm=I=-14:TP=-1.0[aout]"
subprocess.run(["ffmpeg","-v","error","-y",*ins,"-filter_complex",fc,"-map","0:v","-map","[aout]","-c:v","copy","-c:a","aac","-b:a","192k","-shortest",OUT],check=True)
print("done",OUT)
