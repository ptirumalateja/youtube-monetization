#!/usr/bin/env python3
"""Build a smooth organic hand mesh (neutral pose: fingers straight, +x forward, +y back of hand, +z lateral) from
signed-distance primitives (round cones, smooth-unioned so knuckles, palm and thumb web blend), extract it with marching
cubes, and compute linear-blend-skinning weights to 17 bones. Output hand.json for the three.js renderer.
usage: python3 make_hand.py <out.json> [res]"""
import json, sys
import numpy as np
from skimage import measure

out = sys.argv[1]; RES = float(sys.argv[2]) if len(sys.argv) > 2 else 0.17

def rc(p, a, b, r1, r2):  # iq round cone
    a = np.array(a, float); b = np.array(b, float)
    ba = b - a; l2 = ba @ ba; rr = r1 - r2; a2 = l2 - rr * rr; il2 = 1.0 / l2
    pa = p - a; y = pa @ ba; z = y - l2
    t = pa * l2 - np.outer(y, ba); x2 = (t * t).sum(1)
    y2 = y * y * l2; z2 = z * z * l2; k = np.sign(rr) * rr * rr * x2
    d1 = np.sqrt(x2 + z2) * il2 - r2
    d2 = np.sqrt(x2 + y2) * il2 - r1
    d3 = (np.sqrt(np.maximum(x2 * a2 * il2, 0)) + y * rr) * il2 - r1
    return np.where(np.sign(z) * a2 * z2 > k, d1, np.where(np.sign(y) * a2 * y2 < k, d2, d3))

def rbox(p, c, h, r):
    q = np.abs(p - np.array(c)) - np.array(h)
    return np.sqrt((np.maximum(q, 0) ** 2).sum(1)) + np.minimum(np.max(q, axis=1), 0) - r

def smin(a, b, k):
    h = np.maximum(k - np.abs(a - b), 0) / k
    return np.minimum(a, b) - h * h * k * 0.25

# ---- hand definition (units ~ cm; adult proportions: palm 10.2, middle finger 8.6, width ~8.5) ----
PALM_X = 10.2
FZ = [3.0, 1.0, -1.0, -2.9]                        # finger base z (index, middle, ring, pinky)
FL = [[4.0, 2.3, 1.8], [4.5, 2.5, 1.9], [4.2, 2.3, 1.8], [3.3, 1.8, 1.6]]
FR = [[0.88, 0.80, 0.72, 0.60], [0.92, 0.82, 0.74, 0.62], [0.86, 0.78, 0.70, 0.58], [0.76, 0.68, 0.6, 0.5]]
TH = [(1.6, -0.6, 2.9), (4.4, -0.9, 5.0), (6.9, -0.9, 6.5), (8.8, -0.8, 7.6)]   # thumb joints
THR = [1.45, 1.15, 0.95, 0.78]

bones = []   # index: 0 forearm, 1 palm, 2.. fingers (3 each), 14.. thumb (3)
bones.append(((-13, 0, 0), (0, 0, 0))); bones.append(((0, 0, 0), (PALM_X, 0, 0)))
FJ = []
for f in range(4):
    pts = [(PALM_X, 0.0, FZ[f])]
    for L in FL[f]: pts.append((pts[-1][0] + L, 0.0, FZ[f]))
    FJ.append(pts)
    for j in range(3): bones.append((pts[j], pts[j + 1]))
for j in range(3): bones.append((TH[j], TH[j + 1]))

def ell(p, c, r):
    q = (p - np.array(c)) / np.array(r)
    return (np.linalg.norm(q, axis=1) - 1.0) * min(r)

def sdf(P):
    d = rc(P * np.array([1, 1.15, 1]), (-13, 0, 0), (0, 0, 0), 3.0, 2.15)                  # forearm -> slim wrist
    d = smin(d, rbox(P, (PALM_X / 2 + 0.2, -0.1, 0.05), (PALM_X / 2 - 0.2, 0.55, 3.15), 1.0), 0.9)   # palm
    d = smin(d, ell(P, (3.3, -0.95, 2.4), (3.4, 1.5, 1.9)), 1.0)                               # thenar (thumb ball)
    d = smin(d, ell(P, (4.4, -0.75, -2.5), (3.0, 1.1, 1.2)), 0.8)                              # hypothenar
    for f in range(4):                                                                         # knuckle bulges on the back
        d = smin(d, ell(P, (PALM_X - 0.1, 0.55, FZ[f]), (1.0, 0.75, 0.95)), 0.5)
    for f in range(4):
        for j in range(3):
            d = smin(d, rc(P, FJ[f][j], FJ[f][j + 1], FR[f][j], FR[f][j + 1]), 0.5)
        for j in (1, 2):                                                                       # finger joint swellings
            d = smin(d, ell(P, (FJ[f][j][0], 0.0, FZ[f]), (0.55, FR[f][j] * 1.08, FR[f][j] * 1.08)), 0.25)
        a2 = FJ[f][2]; L3 = FL[f][2]                                                           # fingernail on the back of the tip
        d = smin(d, ell(P, (a2[0] + L3 * 0.52, FR[f][3] * 0.78, FZ[f]), (L3 * 0.42, 0.22, FR[f][3] * 0.78)), 0.12)
    for j in range(3): d = smin(d, rc(P, TH[j], TH[j + 1], THR[j], THR[j + 1]), 0.7)
    d = smin(d, ell(P, (TH[3][0] + 0.2, TH[3][1] + THR[3] * 0.75, TH[3][2] + 0.25), (0.8, 0.2, 0.62)), 0.12)   # thumbnail
    return d

lo = np.array([-14, -4.0, -5.5]); hi = np.array([21, 4.5, 10.0])
xs = np.arange(lo[0], hi[0], RES); ys = np.arange(lo[1], hi[1], RES); zs = np.arange(lo[2], hi[2], RES)
G = np.stack(np.meshgrid(xs, ys, zs, indexing="ij"), -1).reshape(-1, 3)
vol = sdf(G).reshape(len(xs), len(ys), len(zs))
verts, faces, normals, _ = measure.marching_cubes(vol, 0.0, spacing=(RES, RES, RES))
verts += lo
print("verts", len(verts), "faces", len(faces))

# skinning weights (nearest bone segments, soft)
def seg_dist(P, a, b):
    a = np.array(a, float); b = np.array(b, float); ab = b - a
    t = np.clip(((P - a) @ ab) / (ab @ ab), 0, 1)
    return np.linalg.norm(P - (a + np.outer(t, ab)), axis=1)
D = np.stack([seg_dist(verts, a, b) for a, b in bones], 1)
tau = 0.3
W = np.exp(-(D - D.min(1, keepdims=True)) / tau); W[D - D.min(1, keepdims=True) > 1.2] = 0
idx = np.argsort(-W, 1)[:, :4]; w4 = np.take_along_axis(W, idx, 1); w4 /= w4.sum(1, keepdims=True)
json.dump({"v": np.round(verts, 3).flatten().tolist(), "f": faces.flatten().tolist(),
           "bi": idx.flatten().tolist(), "bw": np.round(w4, 3).flatten().tolist(),
           "bones": [[list(a), list(b)] for a, b in bones], "fingerJoints": FJ, "thumb": TH},
          open(out, "w"), separators=(",", ":"))
print("wrote", out)
