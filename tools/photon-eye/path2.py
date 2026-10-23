"""v2 world: the photon's 3D path and the one continuous camera that follows it (shared by the shader jobs and the compositor).

World: y up, z forward. The Sun's surface is the plane y = YS (the photon is born below it).
Camera space: x right, y up, z forward; the shader builds rays as R(roll, pitch, yaw) * normalize(uv * F, 1).
"""
import math

import numpy as np

F = 0.70                       # half-width of the view at unit depth (uv x in [-1, 1])
YS = 1.15                      # the photosphere
T_LIT0, T_LIT1 = 1.05, 1.75    # the fog lights up around the dot
T_WALK0, T_WALK1 = 1.60, 5.55  # the random walk
T_SPACE = 7.30                 # hand-over to the space/eye shader
DT = 1 / 240


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


# the dot sits where the frame-0 dot is drawn: screen (540, 845) -> uv (0, .213)
P0 = np.array([0.0, .213 * F * 1.4, 1.4])
C0 = np.array([0.0, 0.0, -0.25])


def rot_x(v, a):
    c, s = math.cos(a), math.sin(a)
    return np.array([v[0], v[1] * c - v[2] * s, v[1] * s + v[2] * c])


def rot_y(v, a):
    c, s = math.cos(a), math.sin(a)
    return np.array([v[0] * c + v[2] * s, v[1], -v[0] * s + v[2] * c])


def rot_z(v, a):
    c, s = math.cos(a), math.sin(a)
    return np.array([v[0] * c - v[1] * s, v[0] * s + v[1] * c, v[2]])


# ---------------------------------------------------------------- the photon: stuttering random walk, then the run for the surface
def build_walk(seed=9):
    r = np.random.default_rng(seed)
    pts, times = [P0.copy()], [T_WALK0]
    p = P0.copy()
    segs = []
    while len(segs) < 30:
        d = r.normal(size=3); d /= np.linalg.norm(d)
        d[2] += .45; d[1] += .08; d /= np.linalg.norm(d)                  # drifts forward (the camera follows) and slightly up
        L = r.uniform(.10, .42)
        q = p + d * L
        q[0] = np.clip(q[0], -.55, .55); q[1] = np.clip(q[1], -.25, .75)
        speed = math.exp(r.normal(0, .55))                                  # stutter: slow in dense knots, fast in gaps
        segs.append((p, q, L / speed, r.normal(0, .06, 3)))
        p = q
    tot = sum(s[2] for s in segs)
    k = (T_WALK1 - T_WALK0) / tot
    t = T_WALK0
    scat = []
    for a, b, dur, bend in segs:
        dur *= k
        n = max(2, int(dur / DT))
        for i in range(1, n + 1):
            u = i / n
            c = (a + b) / 2 + bend                                          # a slight curve, never a ruler line
            pts.append((1 - u) ** 2 * a + 2 * u * (1 - u) * c + u * u * b)
            times.append(t + u * dur)
        t += dur
        scat.append(t)
    # the run: straight for the surface, then on toward Earth
    last = pts[-1]
    exit_pt = np.array([last[0] + .12, YS, last[2] + .95])
    d_exit = exit_pt - last; d_exit /= np.linalg.norm(d_exit)
    run0 = t
    t_exit = run0 + np.linalg.norm(exit_pt - last) / 2.4
    tt = run0
    while tt < 12:
        tt += DT
        dt_ = tt - run0
        s = 2.4 * dt_ + (0 if tt < t_exit else 3.0 * (tt - t_exit) ** 2)   # light leaves the camera behind once outside
        pts.append(last + d_exit * s)
        times.append(tt)
    return np.array(pts), np.array(times), scat[:-1], exit_pt, d_exit, t_exit


WALK, WTIMES, SCAT, EXIT, DEXIT, T_EXIT = build_walk()


def photon(t):
    if t <= T_WALK0:
        return P0.copy()
    i = min(np.searchsorted(WTIMES, t), len(WTIMES) - 1)
    return WALK[i].copy()


def walk_upto(t):
    i = min(np.searchsorted(WTIMES, t), len(WTIMES) - 1)
    return WALK[:i + 1]


# ---------------------------------------------------------------- the camera: follows with lag, handheld float, tilts up after the escape
def _noise(seed, n, sig):
    r = np.random.default_rng(seed)
    x = r.normal(size=n)
    k = np.exp(-np.arange(-60, 61) ** 2 / (2 * sig ** 2)); k /= k.sum()
    y = np.convolve(x, k, 'same')
    return y / (y.std() + 1e-9)


def build_camera():
    ts = np.arange(0, T_SPACE + .5, DT)
    n = len(ts)
    hx, hy, hz = _noise(1, n, 40), _noise(2, n, 40), _noise(3, n, 40)
    ha, hb, hc = _noise(4, n, 50), _noise(5, n, 50), _noise(6, n, 50)
    C = C0.copy(); cams = []
    yaw = pitch = roll = 0.0
    for i, t in enumerate(ts):
        P = photon(t)
        if t < T_WALK0:
            C = C0 + (np.array([0, 0, 0.0]) - C0) * ease(t / T_WALK0)          # slow dolly toward the dot
            tgt_pitch = 0.0; tgt_yaw = 0.0
        else:
            if t < T_EXIT:
                back = np.array([0, -.04, -1.25])
            else:
                lag = 1.25 + 2.2 * ease((t - T_EXIT) / 1.4)
                back = -DEXIT * lag
            target = P + back
            k = 1 - math.exp(-DT / (.30 if t < T_EXIT else .22))
            C = C + (target - C) * k
            rel = P - C
            tgt_yaw = .55 * math.atan2(rel[0], rel[2])
            tgt_pitch = -.55 * math.atan2(rel[1], math.hypot(rel[0], rel[2]))
            if t > T_EXIT:                                                    # look along the beam
                u = ease((t - T_EXIT) / 1.2)
                full_p = -math.atan2(rel[1], math.hypot(rel[0], rel[2]))
                full_y = math.atan2(rel[0], rel[2])
                tgt_pitch = tgt_pitch * (1 - u) + full_p * u
                tgt_yaw = tgt_yaw * (1 - u) + full_y * u
        kk = 1 - math.exp(-DT / .25)
        yaw += (tgt_yaw - yaw) * kk; pitch += (tgt_pitch - pitch) * kk
        roll = .06 * math.sin(t * .7) + (.18 * ease((t - 3.6) / .7) if t > 3.6 else 0) * (1 - ease((t - 5.4) / .8))
        amp = .004 if t < T_EXIT else .002
        cams.append((t, C + amp * np.array([hx[i], hy[i], hz[i]]), yaw + .003 * ha[i], pitch + .003 * hb[i], roll + .003 * hc[i]))
    return ts, cams


CAM_T, CAMS = build_camera()


def camera(t):
    i = min(int(round(t / DT)), len(CAMS) - 1)
    return CAMS[i][1:]


def to_cam(P, cam):
    C, yaw, pitch, roll = cam
    v = np.asarray(P, float) - C
    if v.ndim == 1:
        return rot_z(rot_x(rot_y(v, -yaw), -pitch), -roll)
    # vectorised
    c, s = math.cos(-yaw), math.sin(-yaw)
    x, y, z = v[:, 0] * c + v[:, 2] * s, v[:, 1], -v[:, 0] * s + v[:, 2] * c
    c, s = math.cos(-pitch), math.sin(-pitch)
    y, z = y * c - z * s, y * s + z * c
    c, s = math.cos(-roll), math.sin(-roll)
    x, y = x * c - y * s, x * s + y * c
    return np.stack([x, y, z], -1)


def project(P, cam, W=1080, H=1920):
    """world -> pixel (x, y), depth"""
    q = to_cam(P, cam)
    z = q[..., 2]
    zs = np.maximum(z, 1e-3)
    u, v = q[..., 0] / zs / F, q[..., 1] / zs / F
    return u * W / 2 + W / 2, H / 2 - v * W / 2, z


def sun_uniforms(t):
    C, yaw, pitch, roll = camera(t)
    P = photon(t)
    lit = ease((t - T_LIT0) / (T_LIT1 - T_LIT0))
    sg = (.30 + .55 * ease((t - 3.0) / 3.0)) * lit
    if t > T_EXIT:
        sg = .45 + .15 * ease((t - T_EXIT) / .4)
    te = max(0.0, t - T_EXIT)
    return dict(uT=t, uCx=C[0], uCy=C[1], uCz=C[2], uYaw=yaw, uPitch=pitch, uRoll=roll, uF=F,
                uPx=P[0], uPy=P[1], uPz=P[2], uLit=lit * (1.0 + .5 * ease((t - 5.0) / 1.0)), uYS=YS,
                uEx=EXIT[0], uEz=EXIT[2], uTe=te if t > T_EXIT else 0.0, uSG=sg, uRing=.05 + 2.4 * ease_out(te / 1.6))
