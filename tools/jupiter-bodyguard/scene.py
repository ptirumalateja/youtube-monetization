"""Scene helpers: object packing, cameras, tonemap."""
import math
import numpy as np

EARTH, SATURN, JUPITER = 0, 1, 2


def rot(tilt_z=0.0, tilt_x=0.0, yaw=0.0):
    cz, sz = math.cos(tilt_z), math.sin(tilt_z)
    cx, sx = math.cos(tilt_x), math.sin(tilt_x)
    cy, sy = math.cos(yaw), math.sin(yaw)
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    return Ry @ Rz @ Rx


def obj(kind, c, R, flat=1.0, tilt_z=0.0, tilt_x=0.0, yaw=0.0):
    M = rot(tilt_z, tilt_x, yaw)
    p = np.zeros(16, np.float64)
    p[0:3] = c
    p[3] = R
    p[4] = flat
    p[5:8] = M[:, 0]
    p[8:11] = M[:, 1]
    p[11:14] = M[:, 2]
    p[14] = kind
    return p


def camera(pos, target, fov_y_deg, roll=0.0):
    pos = np.asarray(pos, float); target = np.asarray(target, float)
    f = target - pos; f /= np.linalg.norm(f)
    up = np.array([math.sin(roll), math.cos(roll), 0.0])
    r = np.cross(f, up); r /= np.linalg.norm(r)
    u = np.cross(r, f)
    return np.array([*pos, *r, *u, *f, math.tan(math.radians(fov_y_deg) / 2)], np.float64)


def norm(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def tonemap(img, exposure=1.0):
    x = img * exposure
    # ACES-ish filmic curve
    a, b, c, d, e = 2.51, 0.03, 2.43, 0.59, 0.14
    y = np.clip((x * (a * x + b)) / (x * (c * x + d) + e), 0, 1)
    return y ** (1 / 2.2)


def prm(earth_rot=0.0, cloud_rot=0.0, jup_rot=0.0, sat_rot=0.0, lens=0.0, sky=1.0,
        neb=1.0, rin=1.22, rout=2.30, shear=0.0, t=0.0, jglow=1.0, pix=0.0006, star=1.0, sky_roll=0.6, sky_yaw=0.0, jpos=(0.0, 0.0, 0.0), jfill=0.0, atm=1.0, jlimb=0.0):
    return np.array([earth_rot, cloud_rot, jup_rot, sat_rot, lens, sky, neb, rin, rout,
                     shear, t, jglow, pix, star, sky_roll, sky_yaw, jpos[0], jpos[1], jpos[2], jfill, atm, jlimb], np.float64)


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def ease_io(x, p=3.0):
    x = min(max(x, 0.0), 1.0)
    return x ** p / (x ** p + (1 - x) ** p)


def lerp(a, b, t):
    return np.asarray(a, float) + (np.asarray(b, float) - np.asarray(a, float)) * t
