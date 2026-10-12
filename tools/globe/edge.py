# edge.py <seqdir> [band_px]: glowing line along India's leading (northernmost) edge only, written to mask B
import sys,glob,numpy as np
from PIL import Image,ImageFilter
seq=sys.argv[1]; band=int(sys.argv[2]) if len(sys.argv)>2 else 10
for f in sorted(glob.glob(f"{seq}/mask_*.png")):
    m=np.array(Image.open(f)); ind=m[...,1]>0; H,W=ind.shape
    has=ind.any(0); top=np.where(has,ind.argmax(0),H)            # first (northernmost) India row in each column
    rows=np.arange(H)[:,None]; edge=ind&(rows>=top[None,:])&(rows<top[None,:]+band)
    e=Image.fromarray((edge*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(band/2))
    m[...,2]=np.clip(np.array(e).astype(np.float32)*1.8,0,255).astype(np.uint8); Image.fromarray(m).save(f)
print("edge done")
