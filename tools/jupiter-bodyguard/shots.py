"""Timeline v2: cameras, planets and fireball swarms for every frame.

Beat sheet (seconds):
  A  0.00-1.30  action hook: fireballs aimed at Earth get yanked into Jupiter (push-in)
  B1 1.30-2.90  Saturn, whole ringed planet, slow push   | "Earth, you're so tiny"
  B2 2.90-4.20  Earth close                              | "I have life"
  B3 4.20-6.60  Saturn, skimming the rings               | brag + "who protects YOU?"
  C  6.60-9.60  Earth types; Jupiter rises from behind, Earth drifts left | "I have him." 9.0
  D  9.60-13.40 the swarm: aimed at Earth, bent into Jupiter, impacts + shake
  E  13.40-END  hold, end line, ease back to the frame-0 framing for the loop
"""
import math
import numpy as np
from scene import EARTH, SATURN, JUPITER, obj, camera, norm, prm, ease, ease_io, lerp

FPS = 30
DUR = 14.0

L_EJ = norm([-0.72, 0.30, 0.62])     # sun for Earth/Jupiter shots
L_S = norm([-0.92, 0.32, 0.22])      # Saturn: side light, ~35% night side

RJ = 11.2
J_FINAL = np.array([0.0, 6.0, -14.0])
J_A = J_FINAL + np.array([0.0, -2.2, 0.0])     # hook: Jupiter sits lower so its limb fills the bottom
TGT = np.array([0.75, 0.5, 0.0])
CAM_HERO = np.array([1.2, -2.0, 10.5])
CAM_A = np.array([0.0, 0.45, 7.5])
TGT_A = np.array([0.36, 0.0, 0.0])   # Earth sits left of centre and a little low
GRS_ROT = -0.43

SHOTS = [("A", 0.0, 1.5), ("B1", 1.5, 2.3), ("B2", 2.3, 3.4), ("B3", 3.4, 5.6),
         ("C", 5.6, 7.9), ("D", 7.9, 12.0), ("E", 12.0, DUR)]


def shot_at(t):
    for name, a, b in SHOTS:
        if a <= t < b:
            return name, a, b
    return SHOTS[-1]


def shake(t, amp, seed=0):
    return np.array([math.sin(t * 37.0 + seed) * 0.6 + math.sin(t * 71.0 + 2 * seed) * 0.4,
                     math.sin(t * 43.0 + 1.3 + seed) * 0.6 + math.sin(t * 83.0 + seed) * 0.4,
                     0.0]) * amp


# --------------------------------------------------------------- fireballs
GM = 32000.0


def simulate(spawns, J, t_end, dt=1 / 240):
    out = []
    for sp_ in spawns:
        t0, p, v, grab_r = sp_[:4]
        gmul = sp_[4] if len(sp_) > 4 else 1.0
        tgt = np.array(sp_[5], float) if len(sp_) > 5 and sp_[5] is not None else None
        p = np.array(p, float); v = np.array(v, float)
        ts, ps = [t0], [p.copy()]
        t = t0
        hit = None
        grabbed = 0.0
        grab_t = None
        while t < t_end + 1:
            d = (J if tgt is None else tgt) - p
            r = max(np.linalg.norm(d), 2.0)
            de = np.linalg.norm(p)
            g = min(max((grab_r - de) / 2.5, 0.0), 1.0)
            grabbed = max(grabbed, g)
            if grabbed > 0 and grab_t is None:
                grab_t = t
            a = GM * gmul * grabbed * d / r ** 3
            v = v + a * dt
            p = p + v * dt
            t += dt
            ts.append(t); ps.append(p.copy())
            dd = (p - J) * np.array([1, 1 / 0.935, 1])
            if np.linalg.norm(dd) < RJ:
                hit = (t, p.copy(), v.copy())
                break
        out.append(dict(ts=np.array(ts), ps=np.array(ps), hit=hit, t0=t0, grab=grab_t))
    return out


def curve_path(t0, P0, v, tb, T, db, J=None, accel=0.6, dt=1 / 240, lmin=0.0, h2=0.35):
    """Fly straight (P0, v) until tb, then one smooth cubic arc into target T on Jupiter over db s.
    No kinks: the arc leaves along v and dives into the surface along its normal."""
    J = J_FINAL if J is None else J
    P0 = np.asarray(P0, float); v = np.asarray(v, float); T = np.asarray(T, float)
    sp = np.linalg.norm(v); vd = v / sp
    Pb = P0 + v * (tb - t0)
    L = max(sp * db / (3 * accel), lmin)
    a = min(1.0, sp * db / (3 * L))
    nrm = (T - J) / np.linalg.norm(T - J)
    P1 = Pb + vd * L
    # keep the handle (and so the arc) outside 1.5 Earth radii: push it radially out, keep its length
    r1 = np.linalg.norm(P1)
    if r1 < 1.5:
        P1 = P1 / max(r1, 1e-6) * 1.5
    P2 = T + nrm * (h2 * np.linalg.norm(T - Pb))
    ts = np.arange(t0, tb + db + 1e-9, dt)
    ps = []
    for t in ts:
        if t <= tb:
            ps.append(P0 + v * (t - t0))
        else:
            tau = (t - tb) / db
            u = a * tau + (1 - a) * tau * tau
            m = 1 - u
            ps.append(m ** 3 * Pb + 3 * m * m * u * P1 + 3 * m * u * u * P2 + u ** 3 * T)
    ps = np.array(ps)
    return dict(ts=ts, ps=ps, hit=(ts[-1], T.copy(), (ps[-1] - ps[-2]) / dt), t0=t0, grab=tb)


def screen_to_jupiter(cam, sx, sy, J=None):
    """Point on Jupiter's visible face under screen pixel (sx, sy)."""
    J = J_FINAL if J is None else J
    th = cam[12]
    px = (sx / 1080 * 2 - 1) * th * 1080 / 1920
    py = (1 - sy / 1920 * 2) * th
    d = cam[9:12] + cam[3:6] * px + cam[6:9] * py
    d = d / np.linalg.norm(d)
    o = cam[0:3]
    oc = o - J
    b = oc @ d
    c = oc @ oc - (RJ * 0.97) ** 2
    disc = b * b - c
    if disc < 0:
        return None
    return o + d * (-b - math.sqrt(disc))


def _swarm(t_first, n, rate, seed):
    """D swarm: rocks streak up from the lower right straight at Earth, then whip up and away into Jupiter."""
    rng = np.random.default_rng(seed)
    out = []
    for i in range(n):
        t0 = t_first + i / rate + rng.uniform(-0.05, 0.05)
        side = 1 if (i % 4) else -1
        start = np.array([side * rng.uniform(9, 13), rng.uniform(-7.5, -4.0), rng.uniform(-1, 3)])
        aim = np.array([rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3), rng.uniform(0, 0.4)])
        v = norm(aim - start) * rng.uniform(11, 13)
        d0 = np.linalg.norm(start - aim)
        tb = t0 + max(d0 - rng.uniform(2.7, 3.1), 0.5) / np.linalg.norm(v)
        db = rng.uniform(0.5, 0.6)
        cam = setup(min(tb + db, 11.9))[0]
        for _ in range(50):
            sx, sy = rng.uniform(250, 1000), rng.uniform(330, 780)
            T = screen_to_jupiter(cam, sx, sy)
            if T is not None:
                break
        cp = curve_path(t0, start, v, tb, T, db, accel=1.0, h2=0.3)
        tries = 0
        while np.min(np.linalg.norm(cp["ps"], axis=1)) < 1.3 and tries < 30:
            tries += 1
            aim = aim + norm(np.array([aim[0], aim[1], 0.0]) + 1e-3) * 0.15 + np.array([0.0, 0.1, 0.0])
            v = norm(aim - start) * np.linalg.norm(v)
            cp = curve_path(t0, start, v, tb, T, db, accel=1.0, h2=0.3)
        if np.min(np.linalg.norm(cp["ps"], axis=1)) >= 1.2:
            out.append(cp)
    return out


def _hook_swarm(seed=5):
    """Frame 0: separate streaks converging on Earth from 1 to 3 o'clock at different depths; each sweeps up into Jupiter."""
    rng = np.random.default_rng(seed)
    cam = setup(0.6)[0]
    out = []
    # (clock angle rad, distance from Earth centre, depth z, speed, target px)
    specs = [(0.68, 1.85, 0.4, 4.2, (230, 470)), (0.48, 1.70, -0.8, 3.6, (400, 330)),
             (0.30, 1.85, 0.0, 4.6, (110, 380)), (0.10, 1.60, 0.6, 4.0, (520, 430)),
             (0.42, 1.45, 2.6, 5.0, (300, 580)),      # big foreground rock, nearest the camera
             (-0.08, 1.85, -0.6, 4.4, (660, 330))]
    for k, (ang, r, z, spd, tp) in enumerate(specs):
        X0 = np.array([math.cos(ang) * r, math.sin(ang) * r, z])
        aim = np.array([-0.2, 1.2, 0.0])     # grazing Earth's top: "was about to hit"
        v = norm(aim - X0) * spd
        tb = [0.03, 0.08, 0.0, 0.11, 0.05, 0.14][k]
        out.append(curve_path(-0.9, X0 - v * 0.9, v, tb, screen_to_jupiter(cam, *tp, J_A),
                              rng.uniform(0.5, 0.62), J=J_A, accel=1.0, h2=rng.uniform(0.2, 0.45)))
    for k, (ang, r, z, tz, tp) in enumerate([(0.55, 2.1, 0.4, 0.66, (200, 330)), (0.2, 2.2, -0.4, 0.80, (470, 400)),
                                             (0.4, 2.2, 1.0, 0.90, (90, 480))]):
        X0 = np.array([math.cos(ang) * r, math.sin(ang) * r, z])
        v = norm(np.array([-0.2, 1.25, 0.0]) - X0) * rng.uniform(4.4, 4.8)
        out.append(curve_path(tz - 0.9, X0 - v * 0.9, v, tz, screen_to_jupiter(cam, *tp, J_A), 0.48, J=J_A, accel=1.0, h2=0.3))
    return out


def asteroid_state(t):
    if t < 1.5:
        return SWARM_A
    if 7.4 <= t < 14.1:
        return SWARM_D
    return []


def impact_times(t):
    sw = asteroid_state(t)
    return [a["hit"][0] for a in sw if a["hit"] is not None and a["hit"][0] <= t]


def impact_shake(t):
    k = sum(math.exp(-(t - h) * 9.0) for h in impact_times(t) if t - h < 0.6)
    return min(k, 1.6)


# --------------------------------------------------------------- frame setup
def _ej_prm(t, fov, lens=0.0, J=J_FINAL):
    return prm(earth_rot=0.10 + t * 0.002, cloud_rot=t * 0.0012, jup_rot=GRS_ROT + t * 0.004,
               shear=0.002, lens=lens, sky=0.40, pix=fov_pix(fov), sky_roll=0.8, sky_yaw=2.2,
               jpos=tuple(J), jfill=0.15)


D_END = CAM_HERO + np.array([0.3, -0.4, 1.2])


def setup(t):
    name, a, b = shot_at(t)
    u = (t - a) / (b - a)
    objs_ej = [obj(JUPITER, J_FINAL, RJ, 0.935, 0.05), obj(EARTH, [0, 0, 0], 1.0, 1.0, 0.41)]
    if name == "A":
        # push in on the big Earth under a towering Jupiter
        pos = lerp(CAM_A, CAM_A + [0.0, 0.05, -0.45], ease_io(u, 1.4))
        sh = shake(t, 0.02)
        lens = 0.8 + 3.0 * impact_shake(t)
        cam = camera(pos + sh, TGT_A + sh * 0.3, 46)
        objs = [obj(JUPITER, J_A, RJ, 0.935, 0.05), obj(EARTH, [0, 0, 0], 1.0, 1.0, 0.41)]
        return cam, objs, _ej_prm(t, 46, lens, J_A), L_EJ, name
    if name == "D":
        pos = lerp(CAM_HERO, D_END, ease_io(u, 1.8))
        sh = shake(t, 0.02 + 0.12 * impact_shake(t))
        cam = camera(pos + sh, TGT + sh * 0.3, 46)
        return cam, objs_ej, _ej_prm(t, 46, 0.8 + 2.5 * impact_shake(t)), L_EJ, name
    if name == "E":
        # hero move: glide from the wide two-shot into the frame-0 close framing (seamless loop)
        e = ease_io((t - 12.0) / 2.0, 2.2)
        pos = lerp(D_END, CAM_A, e)
        tgt = lerp(TGT, TGT_A, e)
        sh = shake(t, 0.08 * impact_shake(t))
        cam = camera(pos + sh, tgt, 46)
        J = lerp(J_FINAL, J_A, e)
        objs = [obj(JUPITER, J, RJ, 0.935, 0.05), obj(EARTH, [0, 0, 0], 1.0, 1.0, 0.41)]
        return cam, objs, _ej_prm(t, 46, 0.8 + 2.0 * impact_shake(t), J), L_EJ, name
    if name == "C":
        # Earth alone, typing; Jupiter climbs up from behind Earth while the camera dollies back
        # and tilts up; Earth drifts to the left third
        e = ease_io((t - 5.7) / 1.6, 2.0)            # rise 5.7 -> 7.3
        e2 = ease_io((t - 5.6) / 2.3, 1.8)
        J = J_FINAL + np.array([0.0, -17.0 * (1 - e), 0.0])
        pos = lerp([0.0, -0.3, 5.8], CAM_HERO, e2)
        tgt = lerp([0.0, -0.4, 0.0], TGT, e2)
        sh = shake(t, 0.03 * ease((t - 6.0) / 0.4) * (1 - ease((t - 7.1) / 0.3))
                   + 0.10 * math.exp(-max(t - 7.35, 0) * 6) * (t >= 7.35))
        cam = camera(pos + sh, tgt + sh * 0.3, 46)
        objs = [obj(JUPITER, J, RJ, 0.935, 0.05), obj(EARTH, [0, 0, 0], 1.0, 1.0, 0.41)]
        return cam, objs, _ej_prm(t, 46, 0.0, J), L_EJ, name
    if name == "B2":
        pos = lerp([0.0, -0.45, 5.6], [0.0, -0.5, 5.0], u)
        tgt = np.array([0.0, -0.55, 0.0])
        cam = camera(pos, tgt, 40, roll=-0.05)
        objs = [obj(EARTH, [0, 0, 0], 1.0, 1.0, 0.41)]
        p = prm(earth_rot=0.10 + t * 0.002, cloud_rot=t * 0.0012, sky=0.40, pix=fov_pix(40),
                sky_roll=0.8, sky_yaw=2.9)
        return cam, objs, p, L_EJ, name
    RS = 9.4
    if name == "B1":
        ang = -0.38 + 0.26 * u
        r = 64 - 15 * ease_io(u, 1.2)
        pos = np.array([math.sin(ang) * r, 6.0 - 2.0 * u, math.cos(ang) * r])
        tgt = np.array([0.0, -9.0, 0.0])
        cam = camera(pos, tgt, 42, roll=0.10)
    else:  # B3: skim just above the ring plane, rings stretching past camera
        ang = 0.55 + 0.16 * u
        r = 44 - 7 * ease_io(u, 2)
        pos = np.array([math.sin(ang) * r, 4.5 - 0.8 * u, math.cos(ang) * r])
        tgt = np.array([0.0, 2.5, 0.0])
        cam = camera(pos, tgt, 50, roll=-0.06)
    objs = [obj(SATURN, [0, 0, 0], RS, 0.90, 0.40, 0.28)]
    Ls = L_S if name == "B1" else norm([-0.45, 0.45, 0.77])
    p = prm(sat_rot=t * 0.012, sky=0.40, pix=fov_pix(46), sky_roll=0.8, sky_yaw=2.2,
            rin=1.22, rout=2.30)
    return cam, objs, p, Ls, name


def fov_pix(fov_deg, H=1920):
    return math.radians(fov_deg) / H


SWARM_A = []
SWARM_D = []
SWARM_A = _hook_swarm()
SWARM_D = _swarm(7.45, 22, 5.5, 11)
