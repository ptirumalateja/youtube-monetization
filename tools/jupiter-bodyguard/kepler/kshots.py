"""Kepler-452b vs Earth: shot/reverse-shot conversation, then Jupiter. Timeline and per-frame cameras."""
import math
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scene import EARTH, SATURN, JUPITER, obj, camera, norm, prm, ease, ease_io, lerp  # noqa: E402

FPS = 30
W, H = 1080, 1920
GRS_ROT = -0.43

# (start, end, shot, speaker, line)
SHOTS = [
    (0.0, 2.6, "K", "Kepler-452b", "Hey Earth… they're calling me Earth 2.0 now."),
    (2.6, 4.2, "E", "Earth", "Earth 2.0? Says who?"),
    (4.2, 6.8, "K", "Kepler-452b", "Bigger. Older. Basically you… but upgraded."),
    (6.8, 8.0, "E", "Earth", "Wow. Okay."),
    (8.0, 10.7, "K", "Kepler-452b", "And my gravity? Strong enough to swat asteroids myself."),
    (10.7, 12.5, "E", "Earth", "Wait… you handle asteroids alone?"),
    (12.5, 14.0, "K", "Kepler-452b", "Of course. Don't you?"),
    (14.0, 15.6, "E", "Earth", "Nope. I have him."),
    (15.6, 18.6, "J", "Jupiter", "Is there a problem here?"),
    (18.6, 21.0, "G", None, "(Jupiter's gravity has been flinging asteroids away from Earth for billions of years.)"),
    (21.0, 22.8, "K", "Kepler-452b", "…no problem at all."),
    (22.8, 25.8, "C", "Earth", "Everyone needs a Jupiter."),
]
DUR = SHOTS[-1][1]

COL = {"Kepler-452b": (64, 214, 186), "Earth": (88, 166, 255), "Jupiter": (255, 140, 66)}


def shot_at(t):
    for i, s in enumerate(SHOTS):
        if s[0] <= t < s[1]:
            return i, s
    return len(SHOTS) - 1, SHOTS[-1]


def _pix(fov):
    return math.radians(fov) / H


def setup(t):
    """Returns dict(cam, objs, prm, L, tex, bg, line, shot)."""
    i, (a, b, kind, who, line) = shot_at(t)
    u = (t - a) / (b - a)
    k_idx = sum(1 for s in SHOTS[:i] if s[2] == kind)       # how many times we've cut to this speaker
    out = dict(line=(who, line), shot=kind, idx=i, u=u, tex="earth", bg=None, nebpatch=None)
    if kind in ("K", "E"):
        # medium planet, centred a little high, lit from the upper left; slow push and spin per shot
        d = lerp(6.6, 6.15, ease_io(u, 1.5)) - 0.12 * (k_idx % 2)
        az = (0.18 if kind == "K" else -0.12) + 0.05 * (k_idx % 3)
        pos = np.array([math.sin(az) * d, 0.55 + 0.1 * (k_idx % 2), math.cos(az) * d])
        cam = camera(pos, [0.0, -0.10, 0.0], 40, roll=0.04 if kind == "K" else -0.03)
        L = norm([-0.75, 0.55, 0.45]) if kind == "K" else norm([-0.55, 0.62, 0.35])
        er = (0.95 if kind == "K" else 0.18) + 0.004 * t + 0.03 * k_idx
        p = prm(earth_rot=er, cloud_rot=0.002 * t, sky=0.05, star=0.55, pix=_pix(40), sky_roll=0.8,
                sky_yaw=2.2 + (1.4 if kind == "K" else 0.0), t=t)
        out.update(cam=cam, objs=[obj(EARTH, [0, 0, 0], 1.0, 1.0, 0.41 if kind == "E" else -0.2)], prm=p, L=L,
                   tex="kepler" if kind == "K" else "earth",
                   nebpatch="carina" if kind == "K" else None)
        return out
    if kind == "J":
        # the reveal: Jupiter rolled so its bands run diagonally, on a nebula; slow push; Io crossing
        d = lerp(80.0, 72.0, ease_io(u, 1.6))
        cam = camera([0.0, 0.0, d], [0.0, -2.2, 0.0], 40, roll=1.05)
        io = obj(SATURN, [-5.0 + 8.0 * u, -8.0, 16.0], 0.45, 1.0, 0.0)
        p = prm(jup_rot=GRS_ROT + 0.25 + 0.01 * u, shear=0.002, sky=0.0, star=0.0, pix=_pix(40), t=t,
                rin=0.0, rout=0.0, sat_rot=0.3)
        out.update(cam=cam, objs=[obj(JUPITER, [0, 0, 0], 11.2, 0.935, 0.05), io], prm=p,
                   L=norm([-0.42, 0.30, 0.86]), tex="io", bg="pillars")
        return out
    if kind == "G":
        # Great Red Spot close: skim low over the clouds, horizon across the frame
        lat = -0.39
        dirg = np.array([0.0, math.sin(lat), math.cos(lat)])
        up = np.array([0.0, math.cos(lat), -math.sin(lat)])
        R = 11.2
        pos = dirg * R * lerp(1.62, 1.52, ease_io(u, 1.4)) + up * 5.5
        tgt = dirg * R * 1.0 - up * 1.2
        cam = camera(pos, tgt, 50, roll=math.pi)
        p = prm(jup_rot=GRS_ROT, shear=0.002, sky=0.0, star=0.0, pix=_pix(52), t=t, sky_roll=0.8, sky_yaw=1.0)
        out.update(cam=cam, objs=[obj(JUPITER, [0, 0, 0], R, 0.935, 0.0)], prm=p, L=norm([-0.35, 0.55, 0.76]),
                   bg="carina")
        return out
    # "C": closing tableau: the bodyguard and the protected. Jupiter rising huge from the bottom, little Earth above it.
    d = lerp(50.0, 47.0, ease_io(u, 1.5))
    cam = camera([0.0, 0.0, d], [0.0, 9.5, 0.0], 40, roll=-0.10)
    L = norm([-0.62, 0.40, 0.68])
    er = obj(EARTH, [-2.6, 7.6, d - 22.0], 0.85, 1.0, 0.41)
    p = prm(jup_rot=GRS_ROT + 0.35 + 0.01 * u, earth_rot=0.4 + 0.004 * t, cloud_rot=0.002 * t, shear=0.002,
            sky=0.0, star=0.0, pix=_pix(40), t=t, rin=0.0, rout=0.0)
    out.update(cam=cam, objs=[obj(JUPITER, [0, 0, 0], 11.2, 0.935, 0.05), er], prm=p, L=L, tex="earth", bg="orion")
    return out
