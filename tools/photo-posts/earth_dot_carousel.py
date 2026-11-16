import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
F='/usr/share/fonts/truetype/jetbrains-mono/'
import glob; mono=[f for f in glob.glob(F+'*.ttf') if f.endswith('JetBrainsMono-Bold.ttf')][0]
picks=['1.6','4.2','10.5','16.8','21.6','25.3']
for i,t in enumerate(picks,1):
    im=np.asarray(Image.open(f'f_{t}.png').convert('RGB')).astype(np.float32)/255
    c=im[200:1550]
    H,W=c.shape[:2]
    yy=np.linspace(0,1,H)[:,None,None]; xx=np.linspace(-1,1,W)[None,:,None]
    floor=np.array([0.05,0.045,0.10])+np.array([0.035,0.03,0.07])*np.exp(-((yy-0.5)**2)/0.25)
    c=1-(1-c)*(1-floor)
    out=Image.fromarray((np.clip(c,0,1)*255).astype(np.uint8)).convert('RGBA')
    d=ImageDraw.Draw(out)
    f=ImageFont.truetype(mono,26)
    d.text((W-60,H-58),f'{i}/6',font=f,fill=(255,255,255,150),anchor='rs')
    if i==1:
        f2=ImageFont.truetype(mono,30)
        d.text((W-60,H-110),'SWIPE TO ZOOM OUT  →',font=f2,fill=(255,255,255,220),anchor='rs')
    out.convert('RGB').save(f'earth-is-a-dot_{i}.png')
    a=np.asarray(out.convert('L')).astype(float)
    print(i,[(round(b.mean(),1),round(b.std(),1)) for b in (a[:150],a[-200:],a[:,:80],a[:,-80:])])
