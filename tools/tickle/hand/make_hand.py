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

# ---- hand definition (units ~ cm) ----
FZ = [3.0, 1.0, -0.95, -2.75]                        # finger base z (index, middle, ring, pinky)
FL = [[4.7, 2.8, 2.3], [5.2, 3.3, 2.5], [4.9, 3.1, 2.4], [3.9, 2.3, 2.1]]
FR = [[1.05, 0.96, 0.86, 0.72], [1.1, 1.0, 0.88, 0.74], [1.04, 0.94, 0.84, 0.7], [0.9, 0.82, 0.72, 0.6]]
PALM_X = 9.0
TH = [(1.3, -0.5, 2.6), (4.3, -0.7, 4.9), (6.9, -0.7, 6.6), (8.9, -0.6, 7.9)]   # thumb joints
THR = [1.35, 1.15, 1.0, 0.8]

bones = []   # (a, b) segments in the neutral pose; index: 0 forearm, 1 palm, 2.. fingers (3 each), 14.. thumb (3)
bones.append(((-13, 0, 0), (0, 0, 0))); bones.append(((0, 0, 0), (PALM_X, 0, 0)))
FJ = []
for f in range(4):
    pts = [(PALM_X, 0.0, FZ[f])]
    for L in FL[f]: pts.append((pts[-1][0] + L, 0.0, FZ[f]))
    FJ.append(pts)
    for j in range(3): bones.append((pts[j], pts[j + 1]))
for j in range(3): bones.append((TH[j], TH[j + 1]))

def sdf(P):
    d = rc(P * np.array([1, 1.2, 1]), (-13, 0, 0), (0, 0, 0), 3.3, 2.3)                    # forearm (flattened)
    d = smin(d, rbox(P, (4.6, -0.1, 0.1), (4.2, 0.6, 3.05), 1.0), 0.9)                       # palm
    for f in range(4):
        for j in range(3):
            d = smin(d, rc(P, FJ[f][j], FJ[f][j + 1], FR[f][j], FR[f][j + 1]), 0.55)
    for j in range(3): d = smin(d, rc(P, TH[j], TH[j + 1], THR[j], THR[j + 1]), 0.8)
    return d

lo = np.array([-14, -4.0, -5.0]); hi = np.array([20, 4.0, 10.5])
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
