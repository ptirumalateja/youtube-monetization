import sys, math, numpy as np
from PIL import Image
sys.path.insert(0,"/home/user/youtube-monetization/tools/hole-hill")
import vinyl as V, hh_poses as H
V.RES['k']=2
T=np.array([0,470,0],np.float32); Dd=1700.0
cases=[("dig","strain"),("dig_up","strain"),("shove","smirk"),("sad","neutral"),("lookup","neutral"),("fall","shocked")]
sheet=Image.new("RGB",(300*6,533),(244,244,246))
for i,(p,m) in enumerate(cases):
    th=-0.95
    C=np.array([Dd*math.sin(th),520,Dd*math.cos(th)],np.float32); r,u,f=V.lookat(C,T)
    img,_=V.render(V.POSES[p],m,C,r,u,f,scale=1.0 if p!="shove" else 1.3,tone=1.0 if p!="shove" else .42)
    sheet.paste(Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8)).resize((300,533)),(i*300,0))
sheet.save(sys.argv[1])
