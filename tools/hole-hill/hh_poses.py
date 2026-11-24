"""Hole-hill extra poses + pose lerp (uses the locked vinyl figure)."""
import numpy as np
import vinyl as V
D = lambda x, y, z: (x, y, z)
P = V.POSES
# shovel up and over: body upright, blade lifted forward
P["dig_up"] = dict(spine=D(0.0, 1, 0.12), head_pitch=0.15, neck=D(0, 1, 0.15), pelvis=(0, 450, -20),
    uaL=D(-0.20, -0.75, 0.62), faL=D(0.10, 0.15, 1.0), uaR=D(0.20, -0.75, 0.62), faR=D(-0.05, 0.25, 1.0),
    thL=D(-0.30, -1.0, 0.30), sh_L=D(-0.10, -1.0, -0.10), thR=D(0.30, -1.0, 0.25), sh_R=D(0.10, -1.0, -0.10),
    ftL=D(-0.5, 0, 1), ftR=D(0.5, 0, 1),
    props=[("cap", (0, 430, 90), (0, 640, 520), 10), ("ell", (0, 660, 560), 52, 9, 62)])
# crowd shove: arms straight forward, lunging
P["shove"] = dict(spine=D(0.0, 1, 0.25), head_pitch=0.15, neck=D(0, 1, 0.25), pelvis=(0, 450, 0),
    uaL=D(-0.10, -0.05, 1.0), faL=D(-0.05, 0.0, 1.0), uaR=D(0.10, -0.05, 1.0), faR=D(0.05, 0.0, 1.0),
    thL=D(-0.55, -1.0, 0.45), sh_L=D(-0.40, -1.0, -0.05), thR=D(0.45, -1.0, -0.30), sh_R=D(0.45, -1.0, -0.05),
    ftL=D(-0.6, 0, 1), ftR=D(0.6, 0, 1))
P["lookup"] = dict(head_pitch=-0.55, neck=D(0, 1, -0.4), spine=D(0, 1, -0.05))
P["sad"] = dict(head_pitch=0.55, neck=D(0, 1, 0.5), spine=D(0, 1, 0.18), pelvis=(0, 462, 0),
    uaL=D(-0.05, -1.0, 0.1), faL=D(0.0, -1.0, 0.1), uaR=D(0.05, -1.0, 0.1), faR=D(0.0, -1.0, 0.1))
V.MOODS["smirk"] = dict(brow=(-0.45, 0.0), eye=0.7, mouth="grin", pupil=(0, 0))

DEF = dict(spine=D(0, 1, 0), neck=D(0, 1, 0), pelvis=(0, 470, 0), head_pitch=0.0, head_yaw=0.0,
    uaL=D(-0.10, -1, 0), uaR=D(0.10, -1, 0), faL=D(-0.05, -1, 0), faR=D(0.05, -1, 0),
    thL=D(-0.04, -1, 0), thR=D(0.04, -1, 0), sh_L=D(-0.02, -1, 0), sh_R=D(0.02, -1, 0), ftL=D(-0.35, 0, 1), ftR=D(0.35, 0, 1))

def lerp_pose(a, b, t):
    A = {**DEF, **(V.POSES[a] if isinstance(a, str) else a)}; B = {**DEF, **(V.POSES[b] if isinstance(b, str) else b)}
    out = {}
    for k in DEF:
        va, vb = A[k], B[k]
        out[k] = tuple(np.array(va, float) * (1 - t) + np.array(vb, float) * t) if isinstance(va, (tuple, list)) else va * (1 - t) + vb * t
    pa, pb = A.get("props"), B.get("props")
    pr = pb if (t >= 0.5 and pb) else pa
    if pa and pb and len(pa) == len(pb):
        pr = [(x[0],) + tuple(tuple(np.array(x[i], float) * (1 - t) + np.array(y[i], float) * t) if isinstance(x[i], (tuple, list)) else x[i] * (1 - t) + y[i] * t for i in range(1, len(x))) for x, y in zip(pa, pb)]
    if pr: out["props"] = pr
    return out

# ---- door reel poses
P["rage_a"] = dict(spine=D(0, 1, 0.12), head_pitch=0.1, neck=D(0, 1, 0.1), uaL=D(-0.55, -0.1, 0.7), faL=D(0.25, 1.0, 0.45), uaR=D(0.55, -0.1, 0.7), faR=D(-0.25, 1.0, 0.45),
    thL=D(-0.12, -1, 0.05), sh_L=D(-0.06, -1, -0.05), thR=D(0.12, -1, 0.05), sh_R=D(0.06, -1, -0.05), ftL=D(-0.4, 0, 1), ftR=D(0.4, 0, 1))
P["rage_b"] = dict(spine=D(0, 1, 0.2), head_pitch=0.2, neck=D(0, 1, 0.2), uaL=D(-0.5, 0.2, 0.7), faL=D(0.4, 1.0, 0.2), uaR=D(0.5, 0.2, 0.7), faR=D(-0.4, 1.0, 0.2),
    thL=D(-0.12, -1, 0.05), sh_L=D(-0.06, -1, -0.05), thR=D(0.12, -1, 0.05), sh_R=D(0.06, -1, -0.05), ftL=D(-0.4, 0, 1), ftR=D(0.4, 0, 1))
P["reach"] = dict(spine=D(0, 1, 0.1), head_pitch=0.1, neck=D(0, 1, 0.1), uaL=D(-0.12, -0.5, 0.85), faL=D(0.0, -0.1, 1.0), uaR=D(0.12, -0.5, 0.85), faR=D(0.0, -0.1, 1.0))
P["calm"] = dict(head_pitch=0.12, neck=D(0, 1, 0.1), spine=D(0, 1, 0.04))
def walk_pose(ph):
    s = np.sin(ph); c = np.cos(ph)
    return dict(spine=D(0, 1, 0.05), pelvis=(0, 470 - 8 * abs(s), 0),
        thL=D(-0.04, -1, 0.38 * s), sh_L=D(-0.02, -1, 0.38 * s - 0.3 * max(0.0, c) - 0.05), thR=D(0.04, -1, -0.38 * s), sh_R=D(0.02, -1, -0.38 * s - 0.3 * max(0.0, -c) - 0.05),
        ftL=D(-0.35, 0, 1), ftR=D(0.35, 0, 1),
        uaL=D(-0.10, -1, -0.4 * s), faL=D(-0.05, -1, -0.4 * s + 0.25), uaR=D(0.10, -1, 0.4 * s), faR=D(0.05, -1, 0.4 * s + 0.25))

P["glare_a"] = dict(spine=D(0, 1, 0.08), head_pitch=0.18, neck=D(0, 1, 0.15), head_yaw=0.0)
P["glare_b"] = dict(spine=D(0, 1, 0.1), head_pitch=0.25, neck=D(0, 1, 0.2), head_yaw=0.22,
    uaL=D(-0.12, -1, 0.1), faL=D(0.0, -1, 0.3), uaR=D(0.12, -1, 0.1), faR=D(0.0, -1, 0.3))

# ---- "the plan" reel poses (hero faces +z in local space)
P["kneel_draw"] = dict(spine=D(0, 1, 0.55), neck=D(0, 1, 0.45), head_pitch=0.5, pelvis=(0, 232, -60),
    thL=D(-0.10, -1, 0.0), sh_L=D(-0.02, -0.03, -1), thR=D(0.10, -1, 0.0), sh_R=D(0.02, -0.03, -1), ftL=D(-0.2, 0, -1), ftR=D(0.2, 0, -1),
    uaL=D(-0.2, -0.6, 0.8), faL=D(-0.05, -0.8, 0.6), uaR=D(0.25, -0.6, 0.8), faR=D(0.1, -0.7, 0.7))
P["prone_write"] = dict(spine=D(0, 0.10, 1), neck=D(0, 0.55, 1), head_pitch=0.15, pelvis=(0, 62, -230),
    thL=D(-0.10, -0.14, -1), sh_L=D(-0.04, -0.04, -1), thR=D(0.10, -0.14, -1), sh_R=D(0.04, -0.04, -1), ftL=D(-0.2, -0.3, -1), ftR=D(0.2, -0.3, -1),
    uaL=D(-0.2, -0.9, 0.5), faL=D(-0.05, -0.2, 1), uaR=D(0.25, -0.9, 0.5), faR=D(0.1, -0.15, 1))
