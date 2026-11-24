import sys, math, numpy as np
from PIL import Image
sys.path.insert(0,"/home/user/youtube-monetization/tools/hole-hill")
import vinyl as V, hh_poses as H
V.RES['k']=2
sheet=Image.new("RGB",(360*4,640),(30,28,30))
cams=[("kneel_draw",(900,700,-900),(0,150,-120)),("kneel_draw",(0,1800,-700),(0,0,-120)),("prone_write",(-700,250,-800),(0,100,-200)),("prone_write",(0,1500,-900),(0,0,-100))]
for i,(p,c,t) in enumerate(cams):
    C=np.array(c,np.float32);T=np.array(t,np.float32);r,u,f=V.lookat(C,T)
    img,_=V.render(V.POSES[p],"determined",C,r,u,f,tint=(1.0,0.74,0.34))
    sheet.paste(Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8)).resize((360,640)),(i*360,0))
sheet.save(sys.argv[1])
