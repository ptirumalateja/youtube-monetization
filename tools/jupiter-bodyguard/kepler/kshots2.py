"""v2: close replica of the reference Kepler-vs-Earth reel. Timeline + per-shot cameras."""
import math
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scene import EARTH, SATURN, JUPITER, obj, camera, norm, prm, ease_io, lerp  # noqa: E402

FPS = 30
W, H = 1080, 1920
GRS_ROT = -0.43

# (start, end, shot, speaker, line)
SHOTS = [
    (0.0, 2.4, "K", "Kepler", "Hey Earth, don't you ever feel… a little jealous?"),
    (2.4, 4.2, "E", "Earth", "Jealous? Of what exactly?"),
    (4.2, 6.6, "K", "Kepler", "Well… I'm a lot more habitable than you."),
    (6.6, 7.6, "E", "Earth", "Oh!"),
    (7.6, 10.0, "K", "Kepler", "My oceans are so vast, they call me a Super Earth."),
    (10.0, 11.2, "E", "Earth", "Hmm. Not bad."),
    (11.2, 13.8, "K", "Kepler", "And my atmosphere? Thick enough to punch asteroids out of the sky."),
    (13.8, 15.6, "E", "Earth", "Wait… you handle asteroids yourself?"),
    (15.6, 17.0, "K", "Kepler", "Of course! Don't you?"),
    (17.0, 21.0, "J", "Jupiter", "She doesn't have to."),
    (21.0, 22.8, "G", None, ""),
    (22.8, 25.8, "M", None, "(Thanks to Jupiter's gravity, Earth has a cosmic bodyguard. No asteroid punching required.)"),
    (25.8, 28.6, "C", None, ""),
]
DUR = SHOTS[-1][1]

SUB_DELAY = {"J": 2.0}      # Jupiter speaks only once the light has swept across him

COL = {"Kepler": (72, 222, 190), "Earth": (70, 150, 255), "Jupiter": (255, 128, 48)}


def shot_at(t):
    for i, s in enumerate(SHOTS):
        if s[0] <= t < s[1]:
            return i, s
    return len(SHOTS) - 1, SHOTS[-1]


def _pix(fov):
    return math.radians(fov) / H


def _dist(R, r_px, fov=40):
    return R * (H / 2) / (r_px * math.tan(math.radians(fov) / 2))


def place(cam, sx, sy, dist):
    """World point at screen pixel (sx, sy), dist along the view ray."""
    th = cam[12]
    px = (sx / W * 2 - 1) * th * W / H
    py = (1 - sy / H * 2) * th
    d = cam[9:12] + cam[3:6] * px + cam[6:9] * py
    d = d / np.linalg.norm(d)
    return cam[0:3] + d * dist


def jupiter_front(t, u, r_px, cy_px, fov=40, roll=math.pi / 2, push=0.06, L=(0.35, 0.10, 0.93)):
    """Jupiter seen face-on with vertical bands (rolled 90 deg), centred at screen y cy_px."""
    R = 11.2
    d = _dist(R, r_px, fov) * (1 - push * ease_io(u, 1.6))
    ppu = (H / 2) / (d * math.tan(math.radians(fov) / 2))
    off = (cy_px - H / 2) / ppu                         # planet below centre -> look above it
    # roll pi/2 swaps screen axes: "screen up" is world -x
    tgt = [off * math.sin(roll), off * math.cos(roll), 0.0]
    cam = camera([0.0, 0.0, d], tgt, fov, roll=roll)
    return cam, R, d


def _tgt_j(cam):
    """Point the push-in camera keeps looking at (the original framing target)."""
    return cam[0:3] + cam[9:12] * np.linalg.norm(cam[0:3])


def setup(t):
    i, (a, b, kind, who, line) = shot_at(t)
    u = (t - a) / (b - a)
    k_idx = sum(1 for s in SHOTS[:i] if s[2] == kind)
    out = dict(line=(who, line), shot=kind, idx=i, u=u, t=t, tex="earth", bg=None)
    if kind == "K":
        # Kepler: ocean super-Earth, sits low (clear gap under the line), turning steadily the whole reel
        R = 1.0
        d = _dist(R, 310) * lerp(1.0, 0.97, ease_io(u, 1.4))
        cam = camera([0.0, 0.0, d], [0.0, 0.55, 0.0], 40, roll=0.0)
        p = prm(earth_rot=1.10 + 0.045 * t, cloud_rot=0.006 * t, sky=0.0, star=0.32, pix=_pix(40),
                sky_roll=0.8, sky_yaw=3.6, t=t, atm=0.45)
        out.update(cam=cam, objs=[obj(EARTH, [0, 0, 0], R, 1.0, -0.25, 0.25)], prm=p,
                   L=norm([-0.62, 0.50, 0.62]), tex="kepler", bg="kblack")
        return out
    if kind == "E":
        # Earth: day side full of detail, terminator with city lights, navy sky; same continuous spin
        R = 1.0
        d = _dist(R, 340) * lerp(1.0, 0.97, ease_io(u, 1.4))
        cam = camera([0.0, 0.0, d], [0.0, 0.48, 0.0], 40, roll=0.0)
        p = prm(earth_rot=0.28 + 0.040 * t, cloud_rot=0.005 * t, sky=0.0, star=0.18, pix=_pix(40), t=t, atm=0.55,
                sky_roll=0.3, sky_yaw=1.0)
        out.update(cam=cam, objs=[obj(EARTH, [0, 0, 0], R, 1.0, 0.0, 0.42)], prm=p,
                   L=norm([-0.45, 0.62, 0.55]), tex="earth", bg="navy")
        return out
    if kind == "J":
        # the reveal: black silhouette against a blazing star cluster, then the light sweeps across him
        # while the camera pushes in. Jupiter is the biggest thing in the reel (diameter ~ 0.9 of frame width).
        ke = ease_io(min(u / 0.85, 1.0), 1.8)
        cam, R, d = jupiter_front(t, u, 480, 1010, push=0.0, roll=math.pi / 2 + 0.10 * (1 - ke))
        cam = camera(cam[0:3] * lerp(1.32, 1.0, ke), cam[0:3] * 0 + np.array([0.0, 0.0, 0.0]) + _tgt_j(cam), 40,
                     roll=math.pi / 2 + 0.10 * (1 - ke))
        kl = ease_io(min(max((u - 0.10) / 0.45, 0.0), 1.0), 1.6)
        ph = lerp(2.75, 0.32, kl)
        L = norm([math.sin(ph) * 0.95, 0.10, math.cos(ph)])
        p = prm(jup_rot=GRS_ROT + 0.55 + 0.012 * (t - a), shear=0.002, sky=0.0, star=0.0, pix=_pix(40), t=t,
                rin=0.0, rout=0.0, sat_rot=0.3, jlimb=1.0, jglow=0.0)
        io = obj(SATURN, [-3.6 + 2.6 * u, 2.6, 13.0], 0.30, 1.0, 0.0)
        out.update(cam=cam, objs=[obj(JUPITER, [0, 0, 0], R, 0.935, 0.0), io], prm=p, L=L, tex="io", bg="cluster",
                   reveal=u)
        return out
    if kind == "G":
        out.update(cam=None, objs=[], prm=None, L=None)
        return out
    if kind == "M":
        cam, R, d = jupiter_front(t, u, 250, 960, push=0.04, L=None)
        p = prm(jup_rot=GRS_ROT + 0.8 + 0.012 * (t - a), shear=0.002, sky=0.0, star=0.0, pix=_pix(40), t=t,
                rin=0.0, rout=0.0, jlimb=1.0, jglow=0.0)
        out.update(cam=cam, objs=[obj(JUPITER, [0, 0, 0], R, 0.935, 0.0)], prm=p, L=norm([0.25, 0.0, 0.97]),
                   tex="io", bg="magneto")
        return out
    # "C": huge Jupiter lower-left, lit from the front-left, two moons upper right
    fov = 40
    d = 40.0 * lerp(1.0, 0.95, ease_io(u, 1.4))
    cam = camera([0.0, 0.0, d], [6.2, 3.0, 0.0], fov, roll=-0.55)
    ppu = (H / 2) / ((d - 14) * math.tan(math.radians(fov) / 2))
    eu = obj(SATURN, place(cam, 820 - 30 * u, 640, d - 13.0), 92 / ppu, 1.0, 0.0)
    ppu2 = (H / 2) / ((d - 18) * math.tan(math.radians(fov) / 2))
    io = obj(SATURN, place(cam, 650 + 25 * u, 800, d - 17.0), 30 / ppu2, 1.0, 0.0)
    p = prm(jup_rot=GRS_ROT + 0.25 + 0.012 * (t - a), shear=0.002, sky=0.0, star=0.12, pix=_pix(fov), t=t,
            rin=0.0, rout=0.0, sat_rot=0.8, jlimb=1.0, jglow=0.0)
    out.update(cam=cam, objs=[obj(JUPITER, [0, 0, 0], 11.2, 0.935, 0.0), eu, io], prm=p,
               L=norm([-0.55, -0.15, 0.82]), tex="europa", bg="kblack")
    return out
