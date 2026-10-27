"""python3 stills.py OUTDIR w h t1 t2 ...  -> raw shader plates for quick checks"""
import json, os, subprocess, sys
import cam
O, w, h = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); os.makedirs(O, exist_ok=True)
jobs = []
for ts in sys.argv[4:]:
    t = float(ts); f, v, a = cam.params(t); jobs.append(dict(out=f'{O}/s{t:05.2f}.png', w=w, h=h, f=f, v=v, a=a))
json.dump(jobs, open(f'{O}/jobs.json', 'w'))
subprocess.run(['node', os.path.dirname(os.path.abspath(__file__)) + '/gl/render.mjs', f'{O}/jobs.json'], check=True)
