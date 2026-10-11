# trail.py <seqdir> [decay]: writes India's fading motion trail into the B channel of each mask (ocean only, behind India)
import sys,glob,numpy as np
from PIL import Image
seq=sys.argv[1]; decay=float(sys.argv[2]) if len(sys.argv)>2 else 0.92
files=sorted(glob.glob(f"{seq}/mask_*.png")); trail=None
for f in files:
    m=np.array(Image.open(f)); g=m[...,1].astype(np.float32)/255
    trail=g.copy() if trail is None else np.maximum(trail*decay,g)
    t=np.clip(trail-g,0,1)*(m[...,0]==0)   # only where there's ocean now, not on India itself
    m[...,2]=(t*255).astype(np.uint8); Image.fromarray(m).save(f)
print("trail done",len(files))
