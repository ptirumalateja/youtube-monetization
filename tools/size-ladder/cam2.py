"""Extended cut (21 s): the original 19.6 s timeline is time-warped into 0-10.3 s (plates are reused), then new tiers:
Sun -> Stephenson 2-18, payoff on a dark starfield, comment prompt, and a one-world zoom back to the opening Moon (seamless loop)."""
import math
import numpy as np
import cam

DUR2 = 21.0
KN = [(0., 0.), (1.5, 2.6), (4.5, 6.4), (7.5, 11.6), (10.3, 17.3)]     # new time -> original time
def W(t): return float(np.interp(t, [k[0] for k in KN], [k[1] for k in KN]))
def Winv(o): return float(np.interp(o, [k[1] for k in KN], [k[0] for k in KN]))
FPS = 30
T_SHRINK, T_COUNT, T_JUMP, T_WHIP, T_CUT, T_PROMPT, T_LOOP = 10.3, 11.3, 12.6, 13.4, 14.0, 16.6, 21.0
RS_W = 109.1; R_ST = 2150. * RS_W                                      # Stephenson 2-18 radius, estimate 2,150 solar radii
D_FAR = 8.6e5
S = cam.S
_f17, _v17 = cam.params(17.3)
_cp17, _tg17 = np.array(_v17['uCamP']), np.array(_v17['uCamT'])
D17 = float(np.linalg.norm(_cp17 - _tg17)); d17 = (_cp17 - _tg17) / D17
_f0, _v0 = cam.params(0.0)
_cp0, _tg0 = np.array(_v0['uCamP']), np.array(_v0['uCamT'])
D0 = float(np.linalg.norm(_cp0 - _tg0)); d0 = (_cp0 - _tg0) / D0
STAR_C = S - d17 * (R_ST + 3000.)

def sm(x): return cam.sm(x)
def sm5(x): return cam.sm5(x)
def lg(a, b, k): return math.exp(math.log(a) + (math.log(b) - math.log(a)) * k)

def plate_src(t):
    """-> (kind, index): ('old', i) re-uses an original plate, ('new', i) is rendered for this cut"""
    if t <= T_SHRINK + 1e-6: return 'old', int(round(W(t) * FPS))
    return 'new', int(round(t * FPS))

def params(t):
    kind, i = plate_src(t)
    if kind == 'old':
        f, v = cam.params(i / FPS)
    else:
        if t < T_CUT:
            f, v = cam.params(17.3); f = dict(f); v = dict(v)
            f['uT'] = 17.3 + (t - T_SHRINK)
            if t < T_COUNT: D = lg(D17, 3500., sm((t - T_SHRINK) / (T_COUNT - T_SHRINK)))
            elif t < T_WHIP: D = lg(3500., 2.5e4, (t - T_COUNT) / (T_WHIP - T_COUNT))
            else: D = lg(2.5e4, D_FAR, sm5((t - T_WHIP) / (T_CUT - T_WHIP)))
            tg = np.array(_tg17) + (S - _tg17) * sm((t - T_SHRINK) / 1.0)
            cp = tg + d17 * D
            v['uCamP'] = cp.tolist(); v['uCamT'] = tg.tolist()
            f['uStarVis'] = float(np.clip((t - 13.55) / .3, 0, 1)); f['uBead'] = float(np.clip((t - 11.0) / .6, 0, 1))
            f['uExpo'] = .55
        else:
            f, v = cam.params(0.0); f = dict(f); v = dict(v)
            s = min(max((t - T_PROMPT) / (T_LOOP - T_PROMPT), 0.), 1.); k = sm5(s)
            D = lg(D_FAR, D0, k)
            tg = S + (_tg0 - S) * k
            dv = d17 + (d0 - d17) * k; dv = dv / np.linalg.norm(dv)
            cp = tg + dv * D
            v['uCamP'] = cp.tolist(); v['uCamT'] = tg.tolist()
            f['uRoll'] = f['uRoll'] * k
            f['uStarVis'] = 0.; f['uBead'] = 0.
    f.setdefault('uStarVis', 0.); f.setdefault('uBead', 0.); f['uStarR'] = R_ST
    v['uStarC'] = STAR_C.tolist()
    return f, v
