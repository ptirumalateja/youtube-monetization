import json, sys, cam, subprocess
out, w, h = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); ts = [float(x) for x in sys.argv[4:]]
jobs = []
for t in ts:
    f, v = cam.params(t); jobs.append(dict(out=f'{out}/s_{t:05.2f}.png', w=w, h=h, f=f, v=v))
json.dump(jobs, open(f'{out}/jobs.json', 'w'))
subprocess.run(['node', 'gl/render.mjs', f'{out}/jobs.json'], check=True)
