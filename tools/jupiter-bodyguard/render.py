"""Render frames: python3 render.py OUTDIR START END [STEP] [SS]"""
import sys, os, time, numpy as np
from keys import raw
import shots, comp
out = sys.argv[1]; a = int(sys.argv[2]); b = int(sys.argv[3])
step = int(sys.argv[4]) if len(sys.argv) > 4 else 1
ss = int(sys.argv[5]) if len(sys.argv) > 5 else 2
os.makedirs(out, exist_ok=True)
for f in range(a, b, step):
    p = f"{out}/f{f:04d}.jpg"
    if os.path.exists(p): continue
    t = f / shots.FPS
    t0 = time.time()
    cam, objs, prm, L, name = shots.setup(t)
    r = raw(t, comp.W, comp.H, ss)
    fr = comp.overlay(comp.finish(r, t, cam, objs, name), t)
    fr.save(p, quality=95)
    print(f, f"{time.time()-t0:.1f}s", flush=True)
