"""Place 11.5 true-scale Indias on the Moon with as little overlap as possible (annealing over centres + rotations).
python3 pack_moon.py -> tex/moon_tiles.json  (hero stays facing the camera, north up)."""
import json, math
import numpy as np
from scipy.ndimage import map_coordinates

meta = json.load(open('tex/india_meta.json')); B, S = meta['B'], meta['S']
sdf = np.fromfile('tex/india_sdf.f32', np.float32).reshape(S, S)
K = 1 / 0.2727                                   # Earth radius / Moon radius
n = 30000; i = np.arange(n) + .5
z = 1 - 2 * i / n; r = np.sqrt(1 - z * z); ph = math.pi * (1 + 5 ** .5) * i
P = np.stack([r * np.cos(ph), z, r * np.sin(ph)], 1)   # sample points (x, y, z) unit sphere, y = north

def inside(c, a, half=False):
    e = np.cross([0, 1, 0], c); e /= np.linalg.norm(e); nn = np.cross(c, e)
    cs = P @ c; tv = P - np.outer(cs, c); tl = np.linalg.norm(tv, axis=1) + 1e-12
    rho = np.sqrt(np.maximum(2 * (1 - cs), 0))
    x = rho * (tv @ e) / tl; y = rho * (tv @ nn) / tl
    ca, sa = math.cos(a), math.sin(a); qx, qy = (ca * x + sa * y) / K, (-sa * x + ca * y) / K
    u = (qx / (2 * B) + .5) * S - .5; v = (qy / (2 * B) + .5) * S - .5
    d = map_coordinates(sdf, [v, u], order=1, mode='constant', cval=1.)
    m = d < 0
    if half: m &= qy > meta['ysplit']
    return m

def score(C, A):
    cnt = np.zeros(n)
    for k in range(12): cnt += inside(C[k], A[k], k == 11)
    return np.sum(cnt >= 1) / n, np.sum(cnt >= 2) / n

rng = np.random.default_rng(3)
def rnd():
    v = rng.standard_normal(3); return v / np.linalg.norm(v)
p = (1 + 5 ** .5) / 2
C = np.array([[0, 0, 1.]] + [rnd() for _ in range(11)]); A = np.zeros(12)
cur = score(C, A); cov = cur[0]
T = .02
for it in range(2500):
    k = rng.integers(1, 12); C2, A2 = C.copy(), A.copy()
    C2[k] = C2[k] + rng.standard_normal(3) * .25 * (1 - it / 2500) + 0.02; C2[k] /= np.linalg.norm(C2[k])
    A2[k] = np.clip(A2[k] + rng.standard_normal() * .4, -.7, .7)
    s = score(C2, A2)
    if s[0] > cov or rng.random() < math.exp((s[0] - cov) / T):
        C, A, cov = C2, A2, s[0]
    T *= .998
    if it % 250 == 0: print(it, round(cov, 4), score(C, A))
print('final', score(C, A))
json.dump(dict(C=C.tolist(), A=A.tolist()), open('tex/moon_tiles.json', 'w'))
