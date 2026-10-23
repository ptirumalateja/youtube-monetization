"""Silhouette rig copied from tools/alien-perspective/render.py (branch claude/project-thread-tyboz9)."""
import math
import numpy as np


def lerp(a, b, u):
    return a + (b - a) * u


HOM = dict(hip=(.02, -.42), kf=(-.07, -.235), af=(-.04, -.035), tf=(-.14, 0), kb=(.07, -.22), ab=(.10, -.035), tb=(.02, 0),
           neck=(-.125, -.665), head=(-.165, -.725), sh=(-.10, -.645), ef=(-.17, -.50), hf=(-.19, -.33),
           eb=(-.04, -.50), hb=(-.035, -.34), gaze=(-.72, -.70))
MOD = dict(hip=(0, -.50), kf=(-.03, -.265), af=(-.035, -.035), tf=(-.135, 0), kb=(.04, -.265), ab=(.06, -.035), tb=(-.035, 0),
           neck=(.0, -.84), head=(.012, -.912), sh=(.012, -.81), ef=(.10, -.665), hf=(-.045, -.56),
           eb=(.085, -.66), hb=(-.03, -.565), gaze=(-.78, -.63))


def ell_poly(c, rx, ry, ang, n=40):
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    x, y = rx * np.cos(a), ry * np.sin(a)
    ca, sa = math.cos(ang), math.sin(ang)
    return [(c[0] + ca * xx - sa * yy, c[1] + sa * xx + ca * yy) for xx, yy in zip(x, y)]


def draw_figure(dr, ox, oy, s, m, hood=None, stone=None, spear=False):
    """Silhouette into ImageDraw dr (fill 255). origin = feet, s = px per unit, m = morph 0 hominin -> 1 modern."""
    hood = m if hood is None else hood
    stone = (1 - m) if stone is None else stone
    P = {k: (ox + s * lerp(HOM[k][0], MOD[k][0], m), oy + s * lerp(HOM[k][1], MOD[k][1], m)) for k in HOM if k != 'gaze'}
    g = np.array([lerp(HOM['gaze'][0], MOD['gaze'][0], m), lerp(HOM['gaze'][1], MOD['gaze'][1], m)])
    g /= np.linalg.norm(g)
    dn = np.array([g[1], -g[0]])              # toward the chin
    W_ = lambda a, b: s * lerp(a, b, m)

    def cap(a, b, w):
        dr.line([a, b], fill=255, width=int(w))
        for p in (a, b):
            dr.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=255)
    # legs
    for k, a, f in (('b', 'kb', 'ab'), ('f', 'kf', 'af')):
        cap(P['hip'], P[a], W_(.072, .078)); cap(P[a], P[f], W_(.046, .056)); cap(P[f], P['t' + k], W_(.032, .036))
    # torso: tapered quad hip -> neck
    hp_, nk = np.array(P['hip']), np.array(P['neck'])
    ax = nk - hp_; L = np.linalg.norm(ax); ax /= L; pr = np.array([-ax[1], ax[0]])
    wh, wc = W_(.105, .10) / 2, W_(.13, .14) / 2
    quad = [tuple(hp_ + pr * wh), tuple(hp_ - pr * wh), tuple(hp_ + ax * L * .7 - pr * wc), tuple(nk - pr * wc * .7),
            tuple(nk + pr * wc * .7), tuple(hp_ + ax * L * .7 + pr * wc)]
    dr.polygon(quad, fill=255)
    # belly / chest mass (hominin barrel chest)
    mid = hp_ + ax * L * .45
    dr.polygon(ell_poly(tuple(mid - pr * s * .01 * (1 - m)), W_(.085, .06), L * .32, math.atan2(ax[1], ax[0]) + math.pi / 2), fill=255)
    cap(P['hip'], tuple(hp_ + ax * L * .2), W_(.11, .10))
    # neck + head
    hc = np.array(P['head'])
    cap(P['neck'], tuple(hc - g * s * .01), W_(.055, .05))
    ang = math.atan2(g[1], g[0])
    dr.polygon(ell_poly(tuple(hc), s * lerp(.07, .060, m), s * lerp(.05, .068, m), ang), fill=255)
    # face: hominin muzzle + brow ridge, modern nose + chin
    dr.polygon(ell_poly(tuple(hc + g * s * .045 + dn * s * .022), s * .046 * (1 - m) + 1, s * .034 * (1 - m) + 1, ang), fill=255)
    dr.polygon(ell_poly(tuple(hc + g * s * .052 - dn * s * .022), s * .022 * (1 - m) + 1, s * .012 * (1 - m) + 1, ang), fill=255)
    dr.polygon(ell_poly(tuple(hc + g * s * .062 - dn * s * .004), s * .016 * m + 1, s * .009 * m + 1, ang), fill=255)
    dr.polygon(ell_poly(tuple(hc + g * s * .035 + dn * s * .048), s * .022 * m + 1, s * .018 * m + 1, ang), fill=255)
    # hominin: low skull vault with hair at the back, heavy brow
    if m < 0.99:
        dr.polygon(ell_poly(tuple(hc - g * s * .03 - dn * s * .012), s * .05 * (1 - m) + 1, s * .045 * (1 - m) + 1, ang), fill=255)
    # hood (modern)
    if hood > 0.01:
        dr.polygon(ell_poly(tuple(hc - g * s * .03 + dn * s * .02), s * .075 * hood, s * .07 * hood, ang), fill=255)
    # arms
    for e, h in (('eb', 'hb'), ('ef', 'hf')):
        cap(P['sh'], P[e], W_(.05, .06)); cap(P[e], P[h], W_(.04, .052))
        hr = s * lerp(.034, .028, m)
        dr.ellipse([P[h][0] - hr, P[h][1] - hr, P[h][0] + hr, P[h][1] + hr], fill=255)
    if stone > 0.01:   # Oldowan-style hand stone
        hf = P['hf']
        dr.polygon(ell_poly((hf[0] - s * .012, hf[1] + s * .022), s * .04 * stone, s * .03 * stone, .5, 9), fill=255)
    if spear:
        hf = P['hf']
        dr.line([(hf[0] - s * .05, hf[1] + s * .45), (hf[0] + s * .08, hf[1] - s * .62)], fill=255, width=max(2, int(s * .018)))
    return P


