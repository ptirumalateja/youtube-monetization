"""Full-bleed 16:9 crops of the Navy sensor clips (no borders)."""
import subprocess, numpy as np
from PIL import Image, ImageFilter
SRC={'flir1':('src/flir1.mp4',352,264,(56,8,292,250)),
     'gofast':('src/gofast.mp4',640,480,(108,30,528,452)),'gimbal':('src/gimbal.mp4',640,480,(108,30,528,452))}
def grab(name,t):
    f,w,h,_=SRC[name]
    raw=subprocess.run(['ffmpeg','-v','error','-ss',str(t),'-i',f,'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
    return Image.fromarray(np.frombuffer(raw,np.uint8).reshape(h,w,3))
def fill(img,name,zoom=1.0,cx=0.5,cy=0.5,W=1920,H=1080):
    box=SRC[name][3]
    if box: img=img.crop(box)
    iw,ih=img.size
    cw=iw/zoom; ch=cw*H/W
    if ch>ih/zoom: ch=ih/zoom; cw=ch*W/H
    x0=min(max(cx*iw-cw/2,0),iw-cw); y0=min(max(cy*ih-ch/2,0),ih-ch)
    out=img.resize((W,H),Image.BICUBIC,box=(x0,y0,x0+cw,y0+ch))
    return out.filter(ImageFilter.UnsharpMask(3,60,2))
if __name__=='__main__':
    fill(grab('flir1',74.4),'flir1').save('stills/real_flir_end.jpg',quality=90)
    fill(grab('flir1',3),'flir1',zoom=1.3,cy=0.45).save('stills/real_flir_start.jpg',quality=90)
    fill(grab('flir1',30),'flir1',zoom=1.1,cy=0.45).save('stills/real_flir_mid.jpg',quality=90)
    fill(grab('gofast',20),'gofast').save('stills/real_gofast.jpg',quality=90)
