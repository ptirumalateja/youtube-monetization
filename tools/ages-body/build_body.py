"""Build age-morphed MakeHuman (CC0) body meshes for three.js.

Reads the MakeHuman base mesh and macro age targets from mh_src/ (downloaded from the
makehumancommunity/makehuman repo, CC0 since 2020) and writes:
  out/body_idx.bin        uint32 triangle indices (shared by every age)
  out/body_<age>.bin      float32 xyz per vertex, metres, feet on y=0
  out/joints_<age>.json   joint-centre positions (for skeleton / nerve overlays)
  out/eyes_<age>.json     eye centres
Usage: python3 build_body.py [gender 0..1, 1 = male] ages...
"""
import json, os, sys
import numpy as np

SRC = os.path.join(os.path.dirname(__file__), 'mh_src')
OUT = os.path.join(os.path.dirname(__file__), 'out')
os.makedirs(OUT, exist_ok=True)

def load_obj(path):
    v, groups, cur = [], {}, None
    for line in open(path):
        if line.startswith('v '):
            v.append([float(x) for x in line.split()[1:4]])
        elif line.startswith('g '):
            cur = line.split()[1]; groups[cur] = []
        elif line.startswith('f ') and cur:
            groups[cur].append([int(t.split('/')[0]) - 1 for t in line.split()[1:]])
    return np.array(v), groups

def load_target(path):
    d = []
    for line in open(path):
        if line.startswith('#') or not line.strip():
            continue
        p = line.split()
        d.append((int(p[0]), float(p[1]), float(p[2]), float(p[3])))
    return d

def age_weights(years):
    if years <= 1: a = 0.0
    elif years <= 11: a = 0.1875 * (years - 1) / 10
    elif years <= 25: a = 0.1875 + 0.3125 * (years - 11) / 14
    else: a = 0.5 + 0.5 * min(1.0, (years - 25) / 65)
    w = dict(baby=0, child=0, young=0, old=0)
    if a < 0.1875: w['baby'] = 1 - a / 0.1875; w['child'] = a / 0.1875
    elif a < 0.5: w['child'] = 1 - (a - 0.1875) / 0.3125; w['young'] = (a - 0.1875) / 0.3125
    else: w['young'] = 1 - (a - 0.5) / 0.5; w['old'] = (a - 0.5) / 0.5
    return w

V, G = load_obj(os.path.join(SRC, 'base.obj'))
body = G['body']
nbody = max(max(f) for f in body) + 1
tris = []
for f in body:
    tris += [[f[0], f[1], f[2]], [f[0], f[2], f[3]]] if len(f) == 4 else [f]
tris = np.array(tris, dtype=np.uint32)
tris.tofile(os.path.join(OUT, 'body_idx.bin'))

joint_ids = {g: sorted({i for f in fs for i in f}) for g, fs in G.items() if g.startswith('joint-')}
cache = {}
def tgt(name):
    if name not in cache:
        cache[name] = load_target(os.path.join(SRC, name + '.target'))
    return cache[name]

gender = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
ages = [float(a) for a in sys.argv[2:]] or [5, 30, 80]
for age in ages:
    P = V.copy()
    aw = age_weights(age)
    for race in ('african', 'asian', 'caucasian'):
        for gname, gw in (('male', gender), ('female', 1 - gender)):
            for a, w in aw.items():
                wt = w * gw / 3
                if wt <= 1e-5: continue
                for i, x, y, z in tgt(f'{race}-{gname}-{a}'):
                    P[i] += wt * np.array([x, y, z])
    P *= 0.1  # decimetres -> metres
    P[:, 1] -= P[:nbody, 1].min()
    P[:nbody].astype('<f4').tofile(os.path.join(OUT, f'body_{int(age)}.bin'))
    joints = {g: P[ids].mean(axis=0).round(4).tolist() for g, ids in joint_ids.items()}
    json.dump(joints, open(os.path.join(OUT, f'joints_{int(age)}.json'), 'w'))
    print(f'age {age:>5}: height {P[:nbody,1].max():.2f} m, weights {aw}')
