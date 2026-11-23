import sys, math, numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0,"/home/user/youtube-monetization/tools/hole-hill")
import vinyl as V
V.RES['k']=2
T=np.array([0,520,0],np.float32); D=2300.0
C=np.array([D*math.sin(0.2),560,D*math.cos(0.2)],np.float32); r,u,f=V.lookat(C,T)
sheet=Image.new("RGB",(360*3,640),(244,244,246))
for i,(pose,mood,sc,tn) in enumerate([("guard","determined",1.0,1.0),("guard","determined",1.3,0.42),("stand","neutral",1.3,0.42)]):
    img,_=V.render(V.POSES[pose],mood,C,r,u,f,scale=sc,tone=tn)
    sheet.paste(Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8)).resize((360,640)),(i*360,0))
sheet.save(sys.argv[1])
