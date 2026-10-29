"""Timeline for The Moon Shouldn't Fit: params(t) -> (floats, vec3s) for gl/scene.glsl."""
import math
import numpy as np
DUR = 21.0

def cl(x, a=0., b=1.): return min(max(x, a), b)
def sm(a, b, x): x = cl((x - a) / (b - a)); return x * x * (3 - 2 * x)
def lerp(a, b, x): return a + (b - a) * x
def un(v): v = np.asarray(v, float); return v / np.linalg.norm(v)

BASE = dict(uT=0., uShot=0, uZoom=1, uMR=1, uExp=1, uDark=0, uFov=.5, uA=0, uB=0, uSky=0, uPhot=1,
            uMoonC=[0, 0, 0], uBead=[0, 0, 0], uCamP=[0, 0, 5], uCamT=[0, 0, 0], uSun=[1, 0, 0], uCen=[0, 0, 0])
L = un([1, .3, .55]); SIDE = un(np.cross(L, [0, 1, 0])); UP = np.cross(SIDE, L)

def bead_for(mc, mr):
    """Diamond-ring bead sits on the solar limb opposite the Moon's offset; brightness from the exposed sliver."""
    off = np.array(mc[:2]); d = np.linalg.norm(off)
    if d < 1e-6: return [0, 0, 0]
    gap = d + 1. - mr                      # >0 means a sliver of photosphere shows
    k = cl(gap / .02) ** 1.5
    p = -off / d
    return [float(p[0]), float(p[1]), 1.7 * k]

def totality(t, mc, mr, zoom, sky=1., cor=1., cen=(0, 0)):
    return dict(uShot=0, uZoom=zoom, uMR=mr, uExp=1., uDark=cor, uSky=sky, uPhot=1., uMoonC=[mc[0], mc[1], 0],
                uBead=bead_for(mc, mr), uCen=[cen[0], cen[1], 0])

def params(t):
    p = dict(BASE); p['uT'] = t
    if t < 2.5:                                     # HOOK: diamond ring -> corona blooms
        s = sm(0., 1.4, t)
        mc = (lerp(.04, .0, s), lerp(-.03, .0, s))
        p.update(totality(t, mc, 1.03, lerp(2.45, 2.1, sm(0, 2.5, t)), cor=lerp(.55, 1., sm(.4, 1.6, t))))
        p['uA'] = .3
    elif t < 6.5:                                   # LOCK-IN: transit -> Moon rushes in -> fits
        u = t - 2.5
        g = sm(1.3, 3.0, u)                         # Moon flight 0..1
        mr = (1 / 400) * (400 * 1.03) ** g
        mc = (lerp(.32, 0., sm(.0, 1., g)) + .03 * (1 - g) * u, lerp(.35, 0., sm(0., 1., g)))
        zoom = lerp(1.95, 1.85, sm(0, 2.9, u)) + .45 * sm(3.0, 4.0, u)
        cov = sm(2.85, 3.05, u)
        p.update(dict(uShot=0, uZoom=zoom, uMR=mr, uExp=lerp(.55, 1., cov), uDark=cov, uSky=0., uPhot=1. - .0 * cov,
                      uMoonC=[mc[0], mc[1], 0], uBead=[0, 0, 0]))
    elif t < 8.2:                                   # BODY 1a: the shadow on Earth
        u = (t - 6.5) / 1.7
        M = L * 57 + SIDE * lerp(-.32, .38, u) + UP * .2
        cam = L * lerp(63.5, 62.5, u) + SIDE * -.42 + UP * -.22
        tgt = cam + un(-cam) * .8 + un(M - cam) * .2
        p.update(dict(uShot=1, uA=1., uB=0., uFov=lerp(.1, .094, u), uSun=L.tolist(), uMoonC=M.tolist(), uCamP=cam.tolist(), uCamT=tgt.tolist()))
    elif t < 10.0:                                  # BODY 1b: on the hill, day turns to night
        u = t - 8.2
        p.update(dict(uShot=2, uDark=lerp(.6, 1., sm(0, .6, u)), uZoom=.04, uCen=[.6 - .01 * u, .74, 0], uExp=lerp(.55, 1., sm(0, .6, u)),
                      uMoonC=[.01, 0, 0], uB=sm(.3, 1., u), uA=-.02 * u))
    elif t < 11.5:                                  # REHOOK 1: the fit slips
        u = t - 10.
        mc = (lerp(0., .05, sm(.2, 1.3, u)), lerp(0., .02, sm(.2, 1.3, u)))
        p.update(totality(t, mc, 1.03, lerp(1.9, 1.75, u / 1.5)))
    elif t < 17.0:                                  # BODY 2 + REHOOK 2: Moon shrinks, ring of fire, the last one
        u = t - 11.5
        mr = lerp(1.03, .935, sm(.4, 3.0, u)) - .1 * sm(3.6, 5.2, u)
        cov = 1. - sm(.9, 1.6, u)                   # corona fades once photosphere shows
        p.update(dict(uShot=0, uZoom=lerp(1.8, 1.9, sm(0, 3, u)) + .2 * sm(3.5, 5.5, u), uMR=mr, uExp=lerp(1., .55, sm(.9, 1.7, u)),
                      uDark=cov, uSky=lerp(0.6, 0., sm(0, 1., u)), uPhot=1. + 1.6 * sm(1.4, 2.6, u) + 2.5 * sm(4.8, 5.5, u),
                      uMoonC=[0, 0, 0], uBead=[0, 0, 0]))
    elif t < 19.5:                                  # CLOSE: face looking up
        u = t - 17.
        p.update(dict(uShot=3, uZoom=lerp(.08, .095, u / 2.5), uCen=[.66, .74 - .01 * u, 0], uExp=sm(0., .6, u), uMoonC=[.01, 0, 0],
                      uA=-.006 * u, uB=-.01 * u))
    else:                                           # CTA: diamond ring re-forms -> loops to frame 0
        u = (t - 19.5) / 1.5
        s = sm(.1, 1., u)
        mc = (lerp(.0, .04, s), lerp(.0, -.03, s))
        p.update(totality(t, mc, 1.03, lerp(2.15, 2.45, sm(0, 1, u)), cor=lerp(1., .55, sm(.5, 1., u))))
        p['uA'] = .3
    if p['uShot'] == 0:
        p['uCen'] = [0, .22 * p['uZoom'], 0]
    f = {k: float(v) for k, v in p.items() if not isinstance(v, list)}
    v = {k: [float(x) for x in vv] for k, vv in p.items() if isinstance(vv, list)}
    return f, v
