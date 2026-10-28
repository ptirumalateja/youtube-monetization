"""Timeline: global time t (s) -> shader uniforms. One Moon, one camera (units: Earth radii).
India (11.5 packed tiles), then Pakistan, Bangladesh, Nepal, Sri Lanka, Bhutan tile the Moon at true scale; each new country wipes the last."""
import json, math, os
import numpy as np

DUR = 26.0
RM = 0.27270
FOV = math.radians(40)
HERE = os.path.dirname(os.path.abspath(__file__))
CT = json.load(open(os.path.join(HERE, 'tex/countries.json')))
MOON_KM2 = 37.93e6
SPIN_AX = np.array([.12, 1., 0.]); SPIN_AX /= np.linalg.norm(SPIN_AX)

# (iso, wave start, wave end, hold end, big number, label, area line)
# every entrance and landing sits on a 120 BPM grid (beats at 0.25 + 0.5 k)
SEQ = [
    ('IND', 0.75, 4.25, 5.5, '11.5', 'INDIAS ON THE MOON', '32.9 LAKH KM²'),
    ('PAK', 5.75, 7.25, 9.5, '47.6', 'PAKISTANS ON THE MOON', '7.96 LAKH KM²'),
    ('BGD', 9.75, 11.25, 13.0, '255', 'BANGLADESHES ON THE MOON', '1.48 LAKH KM²'),
    ('NPL', 13.25, 14.75, 16.5, '257', 'NEPALS ON THE MOON', '1.47 LAKH KM²'),
    ('LKA', 16.75, 18.25, 20.5, '578', 'SRI LANKAS ON THE MOON', '65,610 KM²'),
    ('BTN', 20.75, 22.25, 24.0, '988', 'BHUTANS ON THE MOON', '38,394 KM²'),
]
BPM = 120; BEAT0 = 0.25
COUNT = {iso: MOON_KM2 / CT[iso]['km2'] for iso in CT}
TINT = {'PAK': (.35, .85, .7), 'BGD': (.35, .8, .4), 'NPL': (1., .4, .4), 'LKA': (1., .72, .3), 'BTN': (1., .55, .2)}
T_SHEET = 0.75
T_INDIA = (1.75, 4.25)
T_END = 24.25           # Bhutan wipes off, the hero India re-forms above the Moon


def sm(x): x = min(max(x, 0.), 1.); return x * x * (3 - 2 * x)
def sm5(x): x = min(max(x, 0.), 1.); return x * x * x * (x * (6 * x - 15) + 10)
def clamp01(x): return min(max(x, 0.), 1.)
def lerp(a, b, k): return a + (b - a) * k


def rot(ax, a):
    ax = ax / np.linalg.norm(ax); c, s = math.cos(a), math.sin(a); x, y, z = ax
    return np.array([[c + x * x * (1 - c), x * y * (1 - c) - z * s, x * z * (1 - c) + y * s],
                     [y * x * (1 - c) + z * s, c + y * y * (1 - c), y * z * (1 - c) - x * s],
                     [z * x * (1 - c) - y * s, z * y * (1 - c) + x * s, c + z * z * (1 - c)]])


def spin(t): return 2 * math.pi * t / DUR          # one full turn per loop, constant speed: seamless
def cam_dir(az, el):
    az, el = math.radians(az), math.radians(el); return np.array([math.sin(az) * math.cos(el), math.sin(el), math.cos(az) * math.cos(el)])
VIEW = cam_dir(0, 4)

_mt = json.load(open(os.path.join(HERE, 'tex/moon_tiles.json')))
ICO = np.array(_mt['C']); MROT = list(_mt['A'])


def _moon_schedule():
    rest = list(range(1, 12)); first = {}
    for i in rest:
        ft = None
        for tt in np.linspace(T_INDIA[0], T_INDIA[1] + .4, 200):
            if (rot(SPIN_AX, spin(tt)) @ ICO[i]) @ VIEW > .45: ft = tt; break
        first[i] = ft if ft is not None else 99 - (rot(SPIN_AX, spin(T_INDIA[1])) @ ICO[i]) @ VIEW
    rest.sort(key=lambda i: first[i])
    endface = {i: (rot(SPIN_AX, spin(T_INDIA[1])) @ ICO[i]) @ VIEW for i in rest}
    half = max(rest, key=lambda i: endface[i]); rest.remove(half)
    times = np.linspace(T_INDIA[0], T_INDIA[1] - .25, len(rest))   # one India per 16th note
    return [(0, T_SHEET)] + list(zip(rest, times)) + [(half, T_INDIA[1])]
MOON_SCHED = _moon_schedule()


def wave_frac(t, a, b):
    x = clamp01((t - a) / (b - a)); return 1 - (1 - x) ** 1.8


def wave_angle(t, a, b):
    c = wave_frac(t, a, b); return math.acos(1 - 2 * c) if c > 0 else 0.


def origin_at(t):
    """body-local point facing the camera (a little up-left) at time t: where each country starts"""
    w = np.array([-.4, .3, 1.]); w /= np.linalg.norm(w)
    return rot(SPIN_AX, spin(t)).T @ w


PUSH0, PUSHT = 1.10, 2.4      # frame one is already pushing in; the end arrives at PUSH0 still moving in, so the loop has no stall
def zoom(t):
    if t < PUSHT: x = t / PUSHT; return 1 + (PUSH0 - 1) * (1 - x) ** 2
    if t < T_END: return 1 + .35 * sm5((t - 22.3) / 1.5)               # Bhutan: macro pull-out to the whole Moon
    # Hermite from (1.35, still) at T_END to (PUSH0, moving in at the start's speed) at DUR
    p0, p1, v1 = 1.35, PUSH0, -2 * (PUSH0 - 1) / PUSHT; h = DUR - T_END; x = (t - T_END) / h
    return (2 * x ** 3 - 3 * x * x + 1) * p0 + (-2 * x ** 3 + 3 * x * x) * p1 + (x ** 3 - x * x) * h * v1


def camera(t):
    M = np.zeros(3)
    d = 5.55 * RM * 1.02 * .9 * zoom(t)                                  # Moon nearly full width
    az = 2.5 * math.sin(2 * math.pi * t / DUR); el = 4 + 1.5 * math.sin(4 * math.pi * t / DUR)
    tg = M + np.array([0, -0.12 * RM, 0])
    return tg + cam_dir(az, el) * d, tg


def grid(iso, t, a, b, clr, op):
    m = CT[iso]
    g = [m['IA'], m['B'], m['asp'], wave_angle(t, a, b) if t >= a else 0.]
    g2 = [clr, max(math.pi / (b - a) * .3, .02), op, 0.]
    return g, g2


def params(t):
    cp, tg = camera(t)
    mc = []
    for i, ta in MOON_SCHED: mc += list(ICO[i]) + [ta]
    # which grid sets are live: B = the latest country whose wave has started, A = the one before it
    live = [k for k in range(1, len(SEQ)) if t >= SEQ[k][1] - .3]
    kB = live[-1] if live else None; kA = live[-2] if len(live) > 1 else None
    blank = ([0, .05, 1, 0], [0, .1, 0, 0])
    gB, gB2, oB, cB, isoB = *blank, [0, 0, 1], [1, 1, 1], 'PAK'
    gA, gA2, oA, cA, isoA = *blank, [0, 0, 1], [1, 1, 1], 'PAK'
    if kB is not None:
        iso, a, b = SEQ[kB][:3]
        endclr = wave_angle(t + .3, T_END, T_END + 1.0) if kB == len(SEQ) - 1 and t > T_END - .3 else 0.
        gB, gB2 = grid(iso, t, a, b, endclr, 1.); oB = list(origin_at(a)); cB = TINT[iso]; isoB = iso
    if kA is not None:
        iso, a, b = SEQ[kA][:3]; na = SEQ[kB][1]
        nb_ = SEQ[kB][2]; popw_b = max(math.pi / (nb_ - na) * .3, .02)
        clr = max(wave_angle(t, na, nb_) - .7 * popw_b, 0.) if t >= na else 0.   # old tiles vanish only once the new ones over them have grown in: never a bare Moon
        gA, gA2 = grid(iso, t, a, b, clr, 1.); oA = list(origin_at(a)); cA = TINT[iso]; isoA = iso
    # India: packed tiles, wiped by Pakistan's front
    pa = SEQ[1][1]
    ind = [1. if t < SEQ[1][2] + .5 else 0., max(wave_angle(t, pa, SEQ[1][2]) - .7 * max(math.pi / (SEQ[1][2] - pa) * .3, .02), 0.) if t >= pa else 0., 0., 0.]
    # hero sheet: hovers, descends, wraps at T_SHEET; re-forms over the Moon at the end
    if t < T_SHEET:
        h = .42 * (1 - sm(t / T_SHEET)) ** 1.2; al = 1.; fl = 0.
    else:
        h = 0.; al = 1 - clamp01((t - T_SHEET) / .18); fl = 1.
    if t > T_END + .4:
        r = sm((t - T_END - .4) / 1.1); al = r; h = .42 * (1 - (1 - r) ** 2); fl = 0.
    f = dict(uT=t, uFov=FOV, uRoll=0., uExpo=.74, uSpinM=spin(t))
    v = dict(uCamP=list(cp), uCamT=list(tg), uCM=[0., 0., 0.], uSheet=[h, al, fl, 0.], uInd=ind, uIndO=list(origin_at(pa)),
             uGA=gA, uGA2=gA2, uGB=gB, uGB2=gB2, uGAo=oA, uGBo=oB, uGAc=list(cA), uGBc=list(cB))
    a = dict(uMC=mc, uMR=[MROT[i] for i, _ in MOON_SCHED])
    return f, v, a, [isoA, isoB]


def counter(t):
    """(big value, label, area line) for the bottom counter. The last landed number stays up until the next count starts."""
    def show(k):
        iso, a, b, hold, big, lab, area = SEQ[k]
        if iso == 'IND':
            n = sum((.5 if j == len(MOON_SCHED) - 1 else 1) for j, (_, ta) in enumerate(MOON_SCHED) if t >= ta)
            return ((big if n == 11.5 else f'{int(n)}'), lab, area) if n > 0 else None
        c = wave_frac(t, a, b)
        if c >= 1: return big, lab, area
        v = int(COUNT[iso] * c)
        return (f'{v:,}', lab, area) if v > 0 else None
    if t >= T_END: return None
    started = [k for k in range(len(SEQ)) if t >= SEQ[k][1]]
    for k in reversed(started):
        r = show(k)
        if r: return r
        if k > 0:      # new count not visible yet: keep the previous country's final number
            iso, a, b, hold, big, lab, area = SEQ[k - 1]; return big, lab, area
    return None
