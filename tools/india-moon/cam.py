"""Timeline: global time t (s) -> shader uniforms. One world, one camera (units: Earth radii).
Each smaller body hangs above the next, drops onto its upper-left limb, and India re-tiles the bigger body from the contact point."""
import math
import numpy as np

DUR = 21.6
RM, RE, RJ, RS = 0.27270, 1.0, 10.9733, 109.198          # NASA mean radii / Earth's
FOV = math.radians(40)
U = np.array([-0.42, 1.0, 0.22]); U /= np.linalg.norm(U)  # bigger -> smaller body direction
HOVER = dict(M=4.2 * RM, E=4.2 * RE, J=4.2 * RJ)          # gap while a body is the star of its own tier
SPIN_AX = np.array([.12, 1., 0.]); SPIN_AX /= np.linalg.norm(SPIN_AX)

# beats
T_SHEET = (0.0, 1.0)            # flat India descends and wraps onto the Moon at 1.0
T_MTILES = (1.65, 4.85)         # remaining 10 whole Indias, then the half at 4.85
T_DROP = dict(M=(5.2, 5.9), E=(8.8, 9.5), J=(12.4, 13.1))
T_WAVE = dict(E=(6.0, 8.45), J=(9.6, 12.05), S=(13.2, 15.65))
T_PAY = (16.0, 18.0); T_PROMPT = (18.0, 20.0); T_LOOP = (20.0, DUR)
T_LIFT = dict(J=(18.7, 19.8), E=(19.5, 20.6), M=(20.3, 21.35))   # the stack separates again on the push back in

COUNT = dict(M=11.5, E=155, J=18700, S=1850000)


def sm(x): x = min(max(x, 0.), 1.); return x * x * (3 - 2 * x)
def sm5(x): x = min(max(x, 0.), 1.); return x * x * x * (x * (6 * x - 15) + 10)
def clamp01(x): return min(max(x, 0.), 1.)
def lerp(a, b, k): return a + (b - a) * k


def rot(ax, a):
    ax = ax / np.linalg.norm(ax); c, s = math.cos(a), math.sin(a); x, y, z = ax
    return np.array([[c + x * x * (1 - c), x * y * (1 - c) - z * s, x * z * (1 - c) + y * s],
                     [y * x * (1 - c) + z * s, c + y * y * (1 - c), y * z * (1 - c) - x * s],
                     [z * x * (1 - c) - y * s, z * y * (1 - c) + x * s, c + z * z * (1 - c)]])


# ---- Moon spin: slow at both ends (so the loop matches), fast through the tiling, exactly one turn in total
_ts = np.linspace(0, DUR, 4321)
def _bump(t, a, b, e=.6): return np.clip((t - a) / e, 0, 1) ** 2 * (3 - 2 * np.clip((t - a) / e, 0, 1)) * (1 - np.clip((t - b + e) / e, 0, 1) ** 2 * (3 - 2 * np.clip((t - b + e) / e, 0, 1)))
_w = 0.12 + 0 * _ts
_extra = 2 * math.pi - 0.12 * DUR
_b1, _b2 = _bump(_ts, 1.2, 5.4), _bump(_ts, 18.6, 21.4)
_w = _w + _extra * (.78 * _b1 / np.trapezoid(_b1, _ts) + .22 * _b2 / np.trapezoid(_b2, _ts))
_spin = np.concatenate([[0], np.cumsum((_w[1:] + _w[:-1]) / 2 * np.diff(_ts))])
def spin(t): return float(np.interp(t, _ts, _spin))


# ---- Moon tile centres: icosahedron with one vertex facing the camera at t=0 (the hero)
def _ico():
    p = (1 + 5 ** .5) / 2
    v = np.array([[-1, p, 0], [1, p, 0], [-1, -p, 0], [1, -p, 0], [0, -1, p], [0, 1, p], [0, -1, -p], [0, 1, -p], [p, 0, -1], [p, 0, 1], [-p, 0, -1], [-p, 0, 1]], float)
    v /= np.linalg.norm(v, axis=1)[:, None]
    # rotate vertex [0,1,p] onto +z, then a small twist so no row of vertices lines up with the spin axis
    a = v[5]; b = np.array([0, 0, 1.]); ax = np.cross(a, b); ang = math.acos(np.clip(a @ b, -1, 1))
    v = v @ rot(ax, ang).T
    v = v @ rot(np.array([0, 0, 1.]), math.radians(14)).T
    return v
ICO = _ico()
import json as _json, os as _os
_mt = _json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'tex/moon_tiles.json')))
ICO = np.array(_mt['C']); MROT = list(_mt['A'])   # packed placement (pack_moon.py): index 0 = hero, 11 = half


def cam_dir(az, el):
    az, el = math.radians(az), math.radians(el); return np.array([math.sin(az) * math.cos(el), math.sin(el), math.cos(az) * math.cos(el)])


def _moon_schedule():
    hero = 0
    view = cam_dir(0, 4)
    rest = [i for i in range(12) if i != hero]
    # first time each vertex faces the camera during the tiling window
    first = {}
    for i in rest:
        ft = None
        for tt in np.linspace(T_MTILES[0], T_MTILES[1] + .4, 200):
            n = rot(SPIN_AX, spin(tt)) @ ICO[i]
            if n @ view > .45: ft = tt; break
        first[i] = ft if ft is not None else 99 + (-(rot(SPIN_AX, spin(T_MTILES[1])) @ ICO[i]) @ view)
    rest.sort(key=lambda i: first[i])
    # half India: the vertex best facing the camera at the end of the window
    endface = {i: (rot(SPIN_AX, spin(T_MTILES[1])) @ ICO[i]) @ view for i in rest}
    half = max(rest, key=lambda i: endface[i]); rest.remove(half)
    times = np.linspace(T_MTILES[0], T_MTILES[1] - .35, len(rest))
    sched = [(hero, T_SHEET[1])] + list(zip(rest, times)) + [(half, T_MTILES[1])]
    return sched   # last entry is the half tile
MOON_SCHED = _moon_schedule()


def moon_count(t):
    n = 0.
    for k, (i, ta) in enumerate(MOON_SCHED):
        if t >= ta: n += .5 if k == len(MOON_SCHED) - 1 else 1
    return n


def wave_frac(t, key):
    a, b = T_WAVE[key]; x = clamp01((t - a) / (b - a)); return 1 - (1 - x) ** 1.8 if x < 1 else 1.


def gap(t, key):
    a, b = T_DROP[key]; g0 = HOVER[key]
    if t < a: g = g0
    elif t < b: x = (t - a) / (b - a); g = g0 * (1 - x * x)
    else: g = 0.
    la, lb = T_LIFT[key]
    return g + g0 * sm5((t - la) / (lb - la))


def bodies(t):
    S = np.zeros(3)
    J = S + (RS + RJ + gap(t, 'J')) * U
    E = J + (RJ + RE + gap(t, 'E')) * U
    M = E + (RE + RM + gap(t, 'M')) * U
    return M, E, J, S


FIT = 5.55        # distance / radius that fills ~88% of the frame width
OFF = np.array([-0.1, 0.35, 0.])


def frame(key, t):
    M, E, J, S = bodies(t)
    if key == 'M': return M + np.array([0, -0.06, 0]) * RM, FIT * RM * 1.02
    if key == 'E': return E + OFF * RE, FIT * RE
    if key == 'J': return J + OFF * RJ, FIT * RJ
    if key == 'S': return S + OFF * RS, FIT * RS
    if key == 'SJ': return J + np.array([0.35, -1.25, 0.]) * RJ, FIT * RJ * 2.0
    if key == 'P': return S + np.array([-0.15, 0.55, 0.]) * RS, FIT * RS * 1.75


def blend(fa, fb, k):
    (ta, da), (tb, db) = fa, fb
    d = math.exp(lerp(math.log(da), math.log(db), k))
    # target follows the zoom linearly in distance, so whatever we zoom toward stays in frame the whole way
    w = (d - db) / (da - db) if abs(da - db) > 1e-6 else 1 - k
    return tb + (ta - tb) * w, d


KEYS = [  # (time, frame, dist multiplier, az, el)
    (0.0, 'M', 1.00, 0, 4), (1.6, 'M', .97, -2, 4), (5.2, 'M', 1.06, 3, 5),
    (6.0, 'E', 1.00, -4, 4), (8.8, 'E', 1.07, 3, 6),
    (9.6, 'J', 1.00, -4, 4), (12.4, 'J', 1.07, 3, 6),
    (13.2, 'SJ', 1.00, -4, 4), (16.0, 'S', 1.06, 2, 6),
    (17.1, 'P', 1.00, 0, 5), (18.0, 'P', 1.03, 0, 5),
    (DUR, 'M', 1.00, 0, 4),
]


def camera(t):
    for k in range(len(KEYS) - 1):
        if KEYS[k][0] <= t <= KEYS[k + 1][0]: break
    t0, f0, m0, az0, el0 = KEYS[k]; t1, f1, m1, az1, el1 = KEYS[k + 1]
    x = (t - t0) / (t1 - t0)
    big = f0 != f1
    e = sm5(x) if big else x
    if (f0, f1) == ('P', 'M'):   # the push back in: fast through the middle, soft landing on frame one
        e = sm5(x) ** .8
    ta, da = frame(f0, t); tb, db = frame(f1, t)
    tg, d = blend((ta, da * m0), (tb, db * m1), e)
    az = lerp(az0, az1, sm(x)); el = lerp(el0, el1, sm(x))
    return tg + cam_dir(az, el) * d, tg, d


def params(t):
    M, E, J, S = bodies(t)
    cp, tg, d = camera(t)
    sp = spin(t)
    mc = []
    for k, (i, ta) in enumerate(MOON_SCHED):
        mc += list(ICO[i]) + [ta]
    # tile opacity: everything fades as the push passes it, the Moon last
    tile = [1 - sm((t - 20.35) / .7), 1 - sm((t - 19.7) / .6), 1 - sm((t - 18.9) / .6), 1 - sm((t - 18.1) / .6)]
    wave = []; popw = []; wo = {}
    for key, R_ in (('E', RE), ('J', RJ), ('S', RS)):
        c = wave_frac(t, key); th = math.acos(1 - 2 * c) if c > 0 else 0.
        wave.append(th if t >= T_WAVE[key][0] else 0.)
        a, b = T_WAVE[key]; popw.append(max(math.pi / (b - a) * (.35 if key == 'E' else .12), .004))
        wo[key] = list(U)   # contact point, body-local (big bodies do not rotate their tile frame)
    # hero sheet: hovers, descends, wraps at 1.0; re-forms on the loop
    if t < T_SHEET[1]:
        h = .42 * (1 - sm(t / T_SHEET[1]) ** 1.0) ** 1.2; al = 1.; fl = 0.
    else:
        h = 0.; al = 1 - clamp01((t - T_SHEET[1]) / .18); fl = 1.
    if t > 20.4:
        r = sm((t - 20.4) / 1.0); al = r; h = .42 * (1 - (1 - r) ** 2); fl = 0.
    imp = [math.exp(-max(t - T_DROP[k][1], 0) / .18) * (t >= T_DROP[k][1]) * (t < T_DROP[k][1] + 1.2) for k in ('M', 'E', 'J')]
    sunk = sm((t - 12.3) / .9) * (1 - sm((t - 18.6) / .8))       # how much the Sun owns the frame
    expo = lerp(.74, .56, sunk)
    glow = max(sunk, .0)
    f = dict(uT=t, uFov=FOV, uRoll=0., uExpo=expo, uSpinM=sp, uGlow=glow)
    v = dict(uCamP=list(cp), uCamT=list(tg), uCM=list(M), uCE=list(E), uCJ=list(J), uCS=list(S),
             uTile=tile, uWave=wave, uPopW=popw, uWoE=wo['E'], uWoJ=wo['J'], uWoS=wo['S'], uSheet=[h, al, fl, 0.], uImp=imp + [0.])
    a = dict(uMC=mc, uMR=[MROT[i] for i, _ in MOON_SCHED])
    return f, v, a


def counter(t):
    """(value string, label, alpha-key) for the on-screen counter."""
    if t < 5.6:
        n = moon_count(t)
        return (('11.5' if n == 11.5 else f'{int(n)}') if n > 0 else None), 'INDIAS ON THE MOON'
    for key, lab in (('E', 'INDIAS ON EARTH'), ('J', 'INDIAS ON JUPITER'), ('S', 'INDIAS ON THE SUN')):
        a, b = T_WAVE[key]
        if t < b + .55 + (0.35 if key == 'S' else 0):
            if t < a: return None, lab
            v = COUNT[key] * wave_frac(t, key)
            if v < .5: return None, lab
            if key == 'S' and wave_frac(t, key) >= 1: return '1.85 MILLION', lab
            return f'{int(round(v)):,}', lab
    return None, ''
