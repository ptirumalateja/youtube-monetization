"""python3 testframes.py OUT i1 i2 ...  -> plates + composited frames for chosen frame numbers only"""
import json, os, subprocess, sys
import cam, comp
O = sys.argv[1]; idx = [int(x) for x in sys.argv[2:]]; os.makedirs(f'{O}/plates', exist_ok=True); os.makedirs(f'{O}/frames', exist_ok=True)
jobs = []
for i in idx:
    f, v, a = cam.params(i / comp.FPS); jobs.append(dict(out=comp.plate_path(O, i), w=comp.W, h=comp.H, f=f, v=v, a=a))
json.dump(jobs, open(f'{O}/tjobs.json', 'w'))
subprocess.run(['node', os.path.dirname(os.path.abspath(__file__)) + '/gl/render.mjs', f'{O}/tjobs.json'], check=True)
for i in idx: comp.do_frame(O, i)
