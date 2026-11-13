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
TGT = np.array([0.75, 0.5, 0.0])
CAM_HERO = np.array([1.2, -2.0, 10.5])
CAM_A = np.array([0.0, 0.5, 8.0])
TGT_A = np.array([0.0, 0.0, 0.0])
GRS_ROT = -0.43

SHOTS = [("A", 0.0, 1.3), ("B1", 1.3, 2.3), ("B2", 2.3, 3.4), ("B3", 3.4, 5.6),
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
        p = np.array(p, float); v = np.array(v, float)
        ts, ps = [t0], [p.copy()]
        t = t0
        hit = None
        grabbed = 0.0
        grab_t = None
        while t < t_end + 1:
            d = J - p
            r = np.linalg.norm(d)
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


def _swarm(t_first, n, rate, seed, t_last=None):
    """D swarm: rocks fly in from the right, straight at Earth, then get yanked."""
    rng = np.random.default_rng(seed)
    sp = []
    for i in range(n):
        t0 = t_first + i / rate + rng.uniform(-0.04, 0.04)
        start = np.array([rng.uniform(13, 19), rng.uniform(-4, 2.5), rng.uniform(-2, 4)])
        aim = np.array([rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.4), rng.uniform(0, 0.5)])
        vel = norm(aim - start) * rng.uniform(12, 15)
        sp.append((t0, start, vel, rng.uniform(3.6, 4.4)))
    return sp


def _hook_swarm(seed=5):
    """Frame 0: fireballs just ~1 Earth radius from the atmosphere, long trails aimed at Earth."""
    rng = np.random.default_rng(seed)
    sp = []
    specs = [(-0.15, 1.45, 0.35), (0.30, 1.55, -0.20), (-0.60, 1.65, 0.45), (0.70, 1.75, 0.1),
             (0.05, 1.95, -0.45), (-0.95, 1.9, 0.6), (1.05, 2.0, 0.3)]
    for k, (ang, r0, dz) in enumerate(specs):
        d = norm([math.cos(ang), math.sin(ang), dz * 0.3])
        p0 = d * r0
        v = -d * rng.uniform(3.0, 3.5)
        t0 = -0.6
        start = p0 - v * 0.6
        sp.append((t0, start, v, r0 - 0.04, 6.0))
    # second wave: enters from the right edge, reaches Earth's doorstep at tz, then yanked
    for k, (ang, r0, dz, tz) in enumerate([(0.15, 1.5, 0.2, 0.55), (-0.45, 1.6, -0.3, 0.68),
                                           (0.55, 1.7, 0.4, 0.80), (-0.05, 1.55, 0.0, 0.92)]):
        d = norm([math.cos(ang), math.sin(ang), dz * 0.3])
        v = -d * rng.uniform(4.5, 5.0)
        start = d * r0 - v * 0.6
        sp.append((tz - 0.6, start, v, r0 - 0.04, 6.0))
    return sp


SWARM_A = simulate(_hook_swarm(), J_FINAL, 1.4)
SWARM_D = simulate(_swarm(7.45, 34, 9.0, 11), J_FINAL, 14.2)


def asteroid_state(t):
    if t < 1.3:
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
               jpos=tuple(J), jfill=1.0)


D_END = CAM_HERO + np.array([0.3, -0.4, 1.2])


def setup(t):
    name, a, b = shot_at(t)
    u = (t - a) / (b - a)
    objs_ej = [obj(JUPITER, J_FINAL, RJ, 0.935, 0.05), obj(EARTH, [0, 0, 0], 1.0, 1.0, 0.41)]
    if name == "A":
        # push in on the big Earth under a towering Jupiter
        pos = lerp(CAM_A, CAM_A + [0.0, 0.1, -0.9], ease_io(u, 1.4))
        sh = shake(t, 0.02 + 0.10 * impact_shake(t))
        lens = 0.8 + 3.0 * impact_shake(t)
        cam = camera(pos + sh, TGT_A + sh * 0.3, 46)
        return cam, objs_ej, _ej_prm(t, 46, lens), L_EJ, name
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
        return cam, objs_ej, _ej_prm(t, 46, 0.8 + 2.0 * impact_shake(t)), L_EJ, name
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
        pos = lerp([0.0, -0.6, 6.4], [0.0, -0.65, 5.7], u)
        tgt = np.array([0.0, -1.0, 0.0])
        cam = camera(pos, tgt, 40, roll=-0.05)
        objs = [obj(EARTH, [0, 0, 0], 1.0, 1.0, 0.41)]
        p = prm(earth_rot=0.10 + t * 0.002, cloud_rot=t * 0.0012, sky=0.40, pix=fov_pix(40),
                sky_roll=0.8, sky_yaw=2.9)
        return cam, objs, p, L_EJ, name
    RS = 9.4
    if name == "B1":
        ang = -0.38 + 0.26 * u
        r = 64 - 10 * ease_io(u, 1.5)
        pos = np.array([math.sin(ang) * r, 6.0 - 2.0 * u, math.cos(ang) * r])
        tgt = np.array([0.0, -9.0, 0.0])
        cam = camera(pos, tgt, 42, roll=0.10)
    else:  # B3: skim just above the ring plane, rings stretching past camera
        ang = 0.55 + 0.16 * u
        r = 44 - 7 * ease_io(u, 2)
        pos = np.array([math.sin(ang) * r, 4.5 - 0.8 * u, math.cos(ang) * r])
        tgt = np.array([0.0, -13.0, 0.0])
        cam = camera(pos, tgt, 50, roll=-0.06)
    objs = [obj(SATURN, [0, 0, 0], RS, 0.90, 0.40, 0.28)]
    Ls = L_S if name == "B1" else norm([-0.45, 0.45, 0.77])
    p = prm(sat_rot=t * 0.012, sky=0.40, pix=fov_pix(46), sky_roll=0.8, sky_yaw=2.2,
            rin=1.22, rout=2.30)
    return cam, objs, p, Ls, name


def fov_pix(fov_deg, H=1920):
    return math.radians(fov_deg) / H
