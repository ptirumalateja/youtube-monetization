"""Timeline for 'We Found It on the Sun First': params(t) -> (floats, vec3/vec4 uniforms) for gl/scene2.glsl."""
import math
import numpy as np
import cam as C1
DUR = 21.0
sm, cl, lerp = C1.sm, C1.cl, C1.lerp
L = C1.L

BASE = dict(uT=0., uShot=0, uZoom=1, uMR=1, uExp=1, uDark=0, uFov=.5, uA=0, uB=0, uC=0, uD=0, uE=0, uSky=0, uPhot=1,
            uL=[0, 0, 0, 0], uMoonC=[0, 0, 0], uBead=[0, 0, 0], uCamP=[0, 0, 5], uCamT=[0, 0, 0], uSun=[1, 0, 0], uCen=[0, 0, 0])

def ll2p(lon, lat, rot):
    la, lo = math.radians(lat), math.radians(lon)
    X, Z = math.cos(la) * math.sin(lo), math.cos(la) * math.cos(lo)
    return np.array([X * math.cos(rot) + Z * math.sin(rot), math.sin(la), -X * math.sin(rot) + Z * math.cos(rot)])

def shake(t, a=.004):
    return [a * math.sin(t * 7.3) + a * .6 * math.sin(t * 13.1 + 1), a * .8 * math.sin(t * 5.9 + 2) + a * .5 * math.sin(t * 11.7), 0]

def pop(t, t0, d=.18): return sm(t0, t0 + d, t)

def spec(t, span, centre, yellow, L4, ruler=0., jit=.004):
    return dict(uShot=10, uZoom=span, uA=centre, uB=yellow, uC=0., uD=ruler, uL=L4, uCen=shake(t, jit))

def params(t):
    p = dict(BASE); p['uT'] = t
    if t < 2.5:                                     # HOOK: the yellow line ignites in the eyepiece
        ign = .3 + 1.2 * pop(t, .28, .12) * (1. - .06 * math.sin(t * 40.))
        p.update(spec(t, lerp(150., 66., sm(0., 2.5, t) ** .8), 588., ign, [0, 0, 0, 0], jit=.003 + .004 * sm(.3, .8, t)))
    elif t < 4.5:                                   # LOCK-IN a: rooftop under totality
        u = t - 2.5
        p.update(dict(uShot=11, uZoom=1.5, uExp=1., uD=lerp(1., 1.16, sm(0., 2., u)), uMoonC=[0, 0, 0]))
    elif t < 6.5:                                   # LOCK-IN b: three hydrogen lines pop
        u = t - 4.5
        p.update(spec(t, lerp(330., 300., u / 2.), 545., 0., [pop(t, 4.62), pop(t, 5.05), pop(t, 5.48), pop(t, 5.48)], jit=.004))
        p['uC'] = 0.
    elif t < 10.0:                                  # BODY 1: the yellow line, then zoom onto the sodium ruler
        u = t - 6.5
        z = sm(.4, 2.9, u)
        span = math.exp(lerp(math.log(330.), math.log(40.), z))
        centre = lerp(545., 588.2, z)
        p.update(spec(t, span, centre, pop(t, 6.62, .2), [1, 1, 1, 1], ruler=sm(2.2, 2.9, u), jit=.003))
    elif t < 11.5:                                  # REHOOK 1: letters of light converge on Paris
        u = t - 10.
        rot = 2.4 + .03
        cam = ll2p(42, 30, rot) * lerp(5.6, 5.1, sm(0, 1.5, u))
        sun = ll2p(-130, 10, rot)
        p.update(dict(uShot=13, uFov=.62, uA=sm(0.1, 1.2, u), uB=1., uSun=sun.tolist(), uCamP=cam.tolist(), uCamT=[0, 0, 0]))
    elif t < 15.0:                                  # BODY 2: the Sun (diamond ring, then totality) 
        u = t - 11.5
        s = sm(0., 1.3, u)
        mc = (lerp(.04, 0., s), lerp(-.03, 0., s))
        p.update(C1.totality(t, mc, 1.03, lerp(2.3, 1.85, sm(0, 3.5, u)), cor=lerp(.55, 1., sm(.3, 1.3, u))))
        p['uA'] = 1.
    elif t < 18.3:                                  # REHOOK 2 + CLOSE a: the tube, cold then lit
        u = t - 15.
        lit = pop(t, 17.3, .12) * (.92 + .08 * math.sin(t * 29.)) if t >= 17.3 else 0.
        p.update(dict(uShot=14, uA=lit, uC=lerp(1.25, 1.5, sm(0, 3.3, u))))
    elif t < 20.0:                                  # CLOSE b: the balloon crosses the Sun
        u = t - 18.3
        y = lerp(.06, .98, u / 1.7)
        x = .5625 * .5 + .03 * math.sin(u * 2.4)
        p.update(dict(uShot=15, uA=x, uB=y, uC=lerp(1.0, 1.12, u / 1.7)))
    else:                                           # CTA: back to the thin line (loops to frame 0)
        u = (t - 20.) / 1.
        p.update(spec(t, lerp(66., 150., sm(0., 1., u)), 588., lerp(1., .3, sm(0., 1., u)), [0, 0, 0, 0], jit=.003))
    f = {k: float(v) for k, v in p.items() if not isinstance(v, (list, np.ndarray))}
    v = {k: [float(x) for x in vv] for k, vv in p.items() if isinstance(vv, (list, np.ndarray))}
    return f, v
