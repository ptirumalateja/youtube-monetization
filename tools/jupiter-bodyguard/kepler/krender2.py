"""Render v2 frames: python3 krender2.py OUTDIR START END [STEP] [SS]"""
import sys, os, time
import kshots2 as ks, kcomp2
out = sys.argv[1]; a = int(sys.argv[2]); b = int(sys.argv[3])
step = int(sys.argv[4]) if len(sys.argv) > 4 else 1
ss = int(sys.argv[5]) if len(sys.argv) > 5 else 2
os.makedirs(out, exist_ok=True)
for f in range(a, b, step):
    p = f"{out}/f{f:04d}.jpg"
    if os.path.exists(p):
        continue
    t0 = time.time()
    kcomp2.frame(f / ks.FPS, ss).save(p, quality=95)
    print(f, f"{time.time()-t0:.1f}s", flush=True)
