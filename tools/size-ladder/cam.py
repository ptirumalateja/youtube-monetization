"""Timeline: global time t (s) -> shader uniforms (one world, one camera). Used for stills and for the full render."""
import math
import numpy as np

DUR = 19.6
TE, RM = 0.05, 0.2727
M_SITE = np.array([0., -1. + TE + RM + .01, 0.])
J = np.array([0., 9.82, 0.]); S = np.array([0., 107.35, 0.])


def sm(x): x = min(max(x, 0.), 1.); return x * x * (3 - 2 * x)
def sm5(x): x = min(max(x, 0.), 1.); return x * x * x * (x * (6 * x - 15) + 10)
def lerp(a, b, k): return a + (b - a) * k
def vlerp(a, b, k): return np.array(a, float) + (np.array(b, float) - np.array(a, float)) * k
def dirv(az, el): az, el = math.radians(az), math.radians(el); return np.array([math.sin(az) * math.cos(el), math.sin(el), math.cos(az) * math.cos(el)])

# beat times
T_FILL_E = (3.0, 5.5); T_CLOSE_E = (5.6, 6.4); T_WAVE_J = (5.8, 7.2); T_FILL_J = (7.8, 10.7); T_CLOSE_J = (10.8, 11.6)
T_WAVE_S = (11.7, 13.0); T_FILL_S = (13.4, 16.4); T_CLOSE_S = (16.5, 17.3)


def ease_fill(t, a, b): x = (t - a) / (b - a); return 1.06 * (1 - (1 - x) ** 1.6) if 0 < x < 1 else (0. if x <= 0 else 1.06)


def moon_pos(t):
    p0 = np.array([0.5, 2.5, 0.3])
    drift = np.array([math.sin(t * .9) * .05, math.sin(t * 1.3) * .03, math.cos(t * .7) * .04])
    if t < 2.05: return p0 + drift
    k = min((t - 2.05) / 0.95, 1.)
    a = p0 + drift * (1 - k)
    # gravity fall: y quadratic, x/z glide
    return np.array([lerp(a[0], M_SITE[0], sm(k)), lerp(a[1], M_SITE[1], k * k), lerp(a[2], M_SITE[2], sm(k))])


def params(t):
    f, v = {}, {}
    f['uT'] = t
    mp = moon_pos(t)
    # --- camera: all stages share one log-distance path -------------------------------------------------
    if t < 2.6:
        k = sm5(t / 2.6)
        D = math.exp(lerp(math.log(0.95), math.log(4.0), k))
        tg = vlerp(mp, [0, .15, 0], sm(max(0, (t - .6) / 2.0)))
        d = dirv(lerp(-18, 14, k), lerp(8, 33, k))
        roll = lerp(.08, 0, k)
    elif t < T_CLOSE_E[0]:
        k = (t - 2.6) / (T_CLOSE_E[0] - 2.6)
        D = lerp(4.0, 5.3, k); tg = np.array([0, .1, 0]); d = dirv(lerp(14, 62, k), lerp(33, 30, k)); roll = 0
    elif t < T_FILL_J[0]:     # Earth shuts, camera climbs out of the Jupiter bowl
        k = sm5((t - T_CLOSE_E[0]) / (T_FILL_J[0] - T_CLOSE_E[0]))
        D = math.exp(lerp(math.log(5.3), math.log(62), k)); tg = vlerp([0, .1, 0], [0, 8.2, 0], k)
        d = dirv(lerp(62, 100, k), lerp(30, 27, k)); roll = 0
    elif t < T_CLOSE_J[0]:
        k = (t - T_FILL_J[0]) / (T_CLOSE_J[0] - T_FILL_J[0])
        D = lerp(62, 68, k); tg = np.array([0, 8.2, 0]); d = dirv(lerp(100, 150, k), lerp(27, 25, k)); roll = 0
    elif t < T_FILL_S[0]:
        k = sm5((t - T_CLOSE_J[0]) / (T_FILL_S[0] - T_CLOSE_J[0]))
        D = math.exp(lerp(math.log(68), math.log(540), k)); tg = vlerp([0, 8.2, 0], [0, 62, 0], k)
        d = dirv(lerp(150, 190, k), lerp(25, 27, k)); roll = 0
    elif t < T_CLOSE_S[0]:
        k = (t - T_FILL_S[0]) / (T_CLOSE_S[0] - T_FILL_S[0])
        D = lerp(540, 560, k); tg = np.array([0, 62, 0]); d = dirv(lerp(190, 225, k), lerp(27, 25, k)); roll = 0
    else:
        k = sm((t - T_CLOSE_S[0]) / (DUR - T_CLOSE_S[0]))
        D = lerp(560, 330, k); tg = vlerp([0, 62, 0], [0, 99, 0], k); d = dirv(lerp(225, 262, k), lerp(25, 10, k)); roll = 0
    D *= float(np.interp(t, [1.2, 2.6, 6.5, 8.0, 10.8, 13.0, 19.6], [1., 1.38, 1.38, 1.2, 1.2, 1.32, 1.32]))   # breathing room: planets sit smaller in a wider frame
    cp = tg + d * D
    f['uFov'] = math.radians(48); f['uRoll'] = roll
    # --- bowls --------------------------------------------------------------------------------------------
    fE = ease_fill(t, *T_FILL_E); fJ = ease_fill(t, *T_FILL_J); fS = ease_fill(t, *T_FILL_S)
    cE = lerp(.5, 1.2, sm((t - T_CLOSE_E[0]) / (T_CLOSE_E[1] - T_CLOSE_E[0])))
    cJ = lerp(.42, 1.2, sm((t - T_CLOSE_J[0]) / (T_CLOSE_J[1] - T_CLOSE_J[0])))
    cS = lerp(.42, 1.2, sm((t - T_CLOSE_S[0]) / (T_CLOSE_S[1] - T_CLOSE_S[0])))
    wJ = 0. if t < T_WAVE_J[0] else 1.2 * math.exp(math.log(30 / 1.2) * sm((t - T_WAVE_J[0]) / (T_WAVE_J[1] - T_WAVE_J[0])))
    wS = 0. if t < T_WAVE_S[0] else 12. * math.exp(math.log(320 / 12.) * sm((t - T_WAVE_S[0]) / (T_WAVE_S[1] - T_WAVE_S[0])))
    hh = lambda a, b: 1. - sm((t - a) / (b - a) / .6)
    v['uHeap'] = [hh(*T_CLOSE_E), hh(*T_CLOSE_J), hh(*T_CLOSE_S)]
    v.update(uCamP=cp.tolist(), uCamT=tg.tolist(), uF=[fE, fJ, fS], uCut=[cE, cJ, cS], uWave=[wJ, wS, 0.], uM0=mp.tolist())
    f['uExpo'] = lerp(.78, .55, sm((t - 11.0) / 3.)) if t > 11.0 else lerp(.72, .78, sm((t - 5.6) / 4))
    return f, v
