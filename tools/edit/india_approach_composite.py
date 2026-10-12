# India approach (A2 + India #1): India translates toward a fixed Asia; camera tilts up and pushes in; contact jolt.
import numpy as np, subprocess, math
from PIL import Image, ImageFilter, ImageChops
from scipy import ndimage
I="/tmp/claude-0/-home-user-youtube-monetization/96a43257-9cfd-5e8b-a4a4-3357705cc188/images/"
W,H,FPS,DUR=1080,1920,24,5.0; N=int(FPS*DUR); K=1.3; CW,CH=int(W*K),int(H*K)   # oversized canvas for camera moves
# India layer
im=np.array(Image.open(I+"15.webp").convert("RGB")).astype(np.int16); r,g,b=im[...,0],im[...,1],im[...,2]
a=(~((g>130)&(g>r+50)&(g>b+50))).astype(np.uint8); lab,n=ndimage.label(a); sz=ndimage.sum(a,lab,range(1,n+1))
keep=np.isin(lab,[i+1 for i,s in enumerate(sz) if s>5000]); keep=ndimage.binary_erosion(keep,iterations=1)
rgb=im.astype(np.uint8).copy(); sp=(rgb[...,1].astype(int)-np.maximum(rgb[...,0],rgb[...,2])).clip(0,None); rgb[...,1]=(rgb[...,1]-sp*0.9).astype(np.uint8)
ind=Image.fromarray(rgb).convert("RGBA"); ind.putalpha(Image.fromarray((keep*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.0))); ind=ind.crop(ind.getbbox())
# background + Asia mask (land in the top part)
bg=Image.open(I+"20.webp").convert("RGB").resize((CW,CH),Image.LANCZOS); B=np.array(bg).astype(np.int16)
ocean=(B[...,2]>B[...,0]+10)&(B[...,2]>=B[...,1]-30); land=~ocean; land[int(CH*0.32):]=False
land=ndimage.binary_opening(land,iterations=3); lab,n=ndimage.label(land); sz=ndimage.sum(land,lab,range(1,n+1))
asia=ndimage.binary_fill_holes(np.isin(lab,[i+1 for i,s in enumerate(sz) if s>20000]))
sky=np.zeros_like(asia); sky[:int(CH*0.075)]=True; asia|=sky
asiaM=Image.fromarray((asia*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))
ys,xs=np.nonzero(asia&~sky)
def coast_at(x0,x1): return int(np.mean([ys[(xs==x)].max() for x in range(x0,x1,4) if (xs==x).any()]))
# motion: India centre path in canvas coords (bottom-left -> toward the coast, perspective shrink)
s0,s1=0.95*CW/ind.width*0.62, None
T0,TC=0.4,3.4
def ease(u): u=min(max(u,0),1); return u*u*(3-2*u)
iw0=int(CW*0.62); ih0=int(ind.height*iw0/ind.width*0.80)       # 0.80 squash = oblique camera
CX0,CX1=int(CW*0.44),int(CW*0.52)
sc1=0.80                                                         # smaller near the horizon
top0=int(CH*0.70)
contact_x=(int(CX1-iw0*sc1*0.10),int(CX1+iw0*sc1*0.30))
top1=coast_at(*contact_x)-int(ih0*sc1*0.05)                     # north edge tucks just under the coast
enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
     "-c:v","libx264","-crf","17","-pix_fmt","yuv420p","approach_test.mp4"],stdin=subprocess.PIPE)
log=[]; prev=None
for f in range(N):
    t=f/FPS; p=ease((t-T0)/(TC-T0)) if t<TC else 1.0
    sc=1+(sc1-1)*p; cx=CX0+(CX1-CX0)*p; top=top0+(top1-top0)*p
    iw,ih=int(iw0*sc),int(ih0*sc); L=ind.resize((iw,ih),Image.BILINEAR); al=L.split()[3]
    x0,y0=int(cx-iw/2),int(top)
    fr=bg.convert("RGBA")
    sh=Image.new("RGBA",fr.size,(0,0,0,0)); s_=Image.new("RGBA",L.size,(0,8,22,0)); s_.putalpha(al.point(lambda v:int(v*0.6)))
    sh.paste(s_,(x0+int(14*sc),y0+int(22*sc)),s_); fr=Image.alpha_composite(fr,sh.filter(ImageFilter.GaussianBlur(12)))
    v=0 if prev is None else abs(top-prev); prev=top
    if v>0.8:  # smooth wake: India's alpha smeared backwards (south), minus India itself, soft and faint
        smear=Image.new("L",fr.size,0)
        for k in range(1,9): smear.paste(255,(x0,y0+int(k*v*1.1)),al.point(lambda q:int(q*(1-k/9))))
        smear=ImageChops.subtract(smear,Image.new("L",fr.size,0)); hole=Image.new("L",fr.size,0); hole.paste(al,(x0,y0))
        smear=ImageChops.subtract(smear,hole).filter(ImageFilter.GaussianBlur(10)).point(lambda q:int(q*min(1,v/12)*0.22))
        wk=Image.new("RGBA",fr.size,(170,215,240,0)); wk.putalpha(smear); fr=Image.alpha_composite(fr,wk)
    fr.paste(L,(x0,y0),L); fr.paste(bg,(0,0),asiaM)            # Asia occludes India: it slides under the coast
    # camera: tilt up from the ocean to the coast, push in towards contact, jolt at contact
    # camera: starts low over open ocean, tilts up and pushes in on the contact point
    cxp,cyp=sum(contact_x)//2, top1+int(ih0*sc1*0.15)
    q=ease((t-0.8)/(TC-0.8)) if t<TC else 1.0
    cy=int(CH*0.62+(cyp-CH*0.62)*q); cxx=int(CW//2+(cxp-CW//2)*q)
    z=1.0+0.55*q+(0.03*(t-TC)/(DUR-TC) if t>=TC else 0)
    jx=jy=0
    if TC<=t<TC+0.5: k_=math.exp(-(t-TC)*8); jx=int(10*k_*math.sin(t*90)); jy=int(14*k_*math.cos(t*75))
    vw,vh=int(W/z),int(H/z); ccx=min(max(cxx+jx,vw//2),CW-vw//2); ccy=min(max(cy+jy,vh//2),CH-vh//2)
    out=fr.convert("RGB").crop((ccx-vw//2,ccy-vh//2,ccx-vw//2+vw,ccy-vh//2+vh)).resize((W,H),Image.BICUBIC)
    enc.stdin.write(out.tobytes())
    log.append((round(t,2),int(top),int(top-top1)))
enc.stdin.close(); enc.wait()
for i in (0,int(1.5*FPS),int(2.5*FPS),int(TC*FPS),N-1): print(f"t={log[i][0]:4.2f}s  India north edge y={log[i][1]:5d}  distance to contact line={log[i][2]:5d}px (canvas)")
