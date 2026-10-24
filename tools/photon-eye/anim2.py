"""The Photon That Made Your Eye, v2: one continuous camera.

    python3 anim2.py plates OUTDIR [a b]   # shader plates (headless Chromium, gl/shots2.glsl)
    python3 anim2.py frames OUTDIR [a b]   # composite frames
    python3 anim2.py events OUTDIR         # sound cue times

0.0-13.5  one 3D camera (path2.py): the dot in the dark (hook, 2.5 s) -> the fog lights up -> follow the photon's random
          walk through the Sun for 8.5 s while the year counter runs 0 -> 100,000; at year 51,000 it nearly reaches the
          surface and is knocked back down -> the final run: the surface boils up, it breaks through, we rise after it,
          a ring of light races across the surface, we turn to ride the beam
13.5-15.5 the travel: stars streak past, a blue dot ahead grows into Earth (one Earth only)
15.5-17.25 the photon lands; pull back while the iris grows out of the black around it: Earth was the reflection in a pupil
17.25-17.6 push into the eye's catchlight until it flares
17.6-22   the flare is the setting sun: pull back to the stargazer; the text holds; the sun sets into the frame-0 dot
"""
import json
import math
import os
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import gaussian_filter

import hero
from hero import W, H, XX, YY, put, smooth, BLACK, CREAM, GOLDT, MONO
import path2 as P2

HERE = os.path.dirname(os.path.abspath(__file__))
FPS, DUR = 30, 23.0
NF = int(FPS * DUR)
T_SPACE, T_HIT, T_HOLD, T_PUSH, T_SKY = 13.50, 17.00, 17.90, 19.15, 19.50
T_CTA = 22.0
SUN_W, SUN_H = 540, 960
EARTH_C = (.035, .03)
Z_HIT = 4.0                    # Earth's size when the photon lands (then the camera pulls back to the pupil, zoom 1)
YEARS = 100_000
WARM = np.array([1.0, .92, .78], np.float32)


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def ease_in(x):
    x = min(max(x, 0.0), 1.0)
    return x ** 3


def lerp(a, b, u):
    return a + (b - a) * u


# ---------------------------------------------------------------- per-segment parameters (shared by plates + compositor)
def eye_params(t):
    """zoom, centre (p units), pupil radius, space-mode, saccade"""
    if t < T_HIT:
        u = (t - T_SPACE) / (T_HIT - T_SPACE)
        zz = math.exp(lerp(math.log(.035), math.log(Z_HIT), u ** 1.9))         # dot -> marble -> atmosphere
        c = EARTH_C
    elif t < T_HOLD:
        u = ease((t - T_HIT) / (T_HOLD - T_HIT))
        zz = math.exp(lerp(math.log(Z_HIT), 0.0, u))
        c = (EARTH_C[0] * (1 - u), EARTH_C[1] * (1 - u))
    elif t < T_PUSH:
        zz, c = 1.0, (0.0, 0.0)
    else:
        u = ease_in((t - T_PUSH) / (T_SKY - T_PUSH))
        zz = math.exp(lerp(0.0, math.log(30), u))
        c = (lerp(0, -.27, ease((t - T_PUSH) / .25)), lerp(0, .29, ease((t - T_PUSH) / .25)))
    s = 1.0 - ease((t - (T_HIT + .05)) / .75)                                   # the iris grows out of the black around Earth
    pupil = .27 - .05 * ease_out((t - (T_HOLD + .1)) / .5)                        # then the pupil tightens on the light
    sx = sy = 0.0
    for at, dx, dy in ((T_HOLD + .35, .006, -.003), (T_HOLD + .65, -.004, .004)):   # micro-saccades
        k = ease((t - at) / .04)
        sx += dx * k; sy += dy * k
    return zz, c, pupil, s, (sx, sy)


def sky_params(t):
    zz = math.exp(lerp(math.log(7.0), 0.0, ease_out((t - T_SKY) / .9)))
    sun_set = .07 * ease((t - T_SKY) / (DUR - T_SKY))
    return zz, sun_set


def plate_jobs(out, a=0, b=NF):
    pd = os.path.join(out, 'plates'); os.makedirs(pd, exist_ok=True)
    jobs = []
    base_eye = dict(uZ=1, uCX2=0, uCY2=0, uS=0, uSX=0, uSY=0, uA=.25, uT=0)
    for f in range(a, b):
        t = f / FPS
        o = f'{pd}/p{f:04d}.png'
        if t < T_SPACE:
            jobs.append(dict(shot=5, out=o, w=SUN_W, h=SUN_H, u={k: float(v) for k, v in P2.sun_uniforms(t).items()}))
        elif t < T_SKY:
            zz, c, pupil, s, (sx, sy) = eye_params(t)
            u = dict(base_eye, uT=t - T_SPACE, uZ=zz, uCX2=c[0], uCY2=c[1], uS=s, uSX=sx, uSY=sy, uA=pupil)
            jobs.append(dict(shot=3, out=o, w=W, h=H, u=u))
        else:
            zz, ss = sky_params(t)
            jobs.append(dict(shot=4, out=o, w=W, h=H, u=dict(uT=t - T_SKY, uZ=zz, uSun=ss)))
    return jobs


# ---------------------------------------------------------------- light helpers
def fbloom(L, sig=(2, 7, 22, 70, 180), wt=(1, .8, .55, .35, .25)):
    out = np.zeros_like(L)
    small = None
    for s, k in zip(sig, wt):
        if s < 10:
            out += k * gaussian_filter(L, s)
        else:
            if small is None:
                small = np.asarray(Image.fromarray(L.astype(np.float32)).resize((W // 4, H // 4), Image.BILINEAR), np.float32)
            b = gaussian_filter(small, s / 4)
            out += k * np.asarray(Image.fromarray(b).resize((W, H), Image.BILINEAR), np.float32)
    return out


def point(cx, cy, r, hot):
    d2 = (XX - cx) ** 2 + (YY - cy) ** 2
    return np.exp(-d2 / (2 * r * r)) * hot + r * r / (d2 + r * r) * hot * .12


def screen(base, add):
    add = 1 - np.exp(-np.maximum(add, 0))
    return 1 - (1 - base) * (1 - add)


def flash(a, k):
    return a + (WARM - a) * min(max(k, 0), 1)


def photon_glow(x, y, size, hot, flare=1.0):
    p = point(x, y, size, hot)
    L = p[..., None] * np.array([1, .97, .92]) + fbloom(p * .2, (8, 30, 90, 260), (1, .8, .6, .45))[..., None] * np.array([1, .7, .3])
    st = (np.exp(-((YY - y) / 2.0) ** 2) * np.exp(-np.abs(XX - x) / (240 * flare)) +
          np.exp(-((XX - x) / 2.0) ** 2) * np.exp(-np.abs(YY - y) / (170 * flare)) * .7)
    return L + st[..., None] * np.array([1, .9, .7]) * 1.3 * min(1, hot / 20)


def load_plate(out, f):
    im = Image.open(os.path.join(out, 'plates', f'p{f:04d}.png')).convert('RGB')
    if im.size != (W, H):
        im = im.resize((W, H), Image.BICUBIC)
    return np.asarray(im, np.float32) / 255


# ---------------------------------------------------------------- 3D dust (three depths for free: it is in the world)
_r = np.random.default_rng(31)
DUST_N = 1700
DUST0 = np.stack([_r.uniform(-1.6, 1.6, DUST_N), _r.uniform(-1.0, 1.5, DUST_N), _r.uniform(-.6, 12.0, DUST_N)], 1)
DUST_V = _r.normal(0, .035, (DUST_N, 3))
DUST_PH = _r.uniform(0, 6.28, (DUST_N, 3))
DUST_B = _r.uniform(.3, 1.0, DUST_N)


def dust_world(t):
    return DUST0 + DUST_V * t + .03 * np.sin(t * .9 + DUST_PH)                   # drift + Brownian-ish wobble


def draw_dust(t, cam, photon, k_inside):
    if k_inside <= 0.01:
        return 0
    D = dust_world(t)
    x, y, z = P2.project(D, cam)
    inside = (D[:, 1] < P2.YS)
    lit = 1 / (1 + np.sum((D - photon) ** 2, 1) * 5) + .10
    far = Image.new('F', (W, H), 0); near = Image.new('F', (W, H), 0)
    df, dn = ImageDraw.Draw(far), ImageDraw.Draw(near)
    for i in np.argsort(-z):
        if z[i] < .06 or not inside[i] or not (-60 < x[i] < W + 60 and -60 < y[i] < H + 60):
            continue
        r = 1.6 / z[i]
        v = float(DUST_B[i] * lit[i] * min(1, z[i] * 2) * 1.6)
        if r < 5:
            df.ellipse([x[i] - r, y[i] - r, x[i] + r, y[i] + r], fill=v)
        else:
            r = min(r * 2.2, 48)
            dn.ellipse([x[i] - r, y[i] - r, x[i] + r, y[i] + r], fill=v * .35)
    a = gaussian_filter(np.asarray(far, np.float32), .8) + gaussian_filter(np.asarray(near, np.float32), 3.0)
    return (a * k_inside)[..., None] * np.array([1.6, 1.1, .45])


# ---------------------------------------------------------------- the photon's trail, in 3D
TRAIL_SEED = np.random.default_rng(5).normal(0, .6, (len(P2.WALK), 2))


def draw_trail(t, cam):
    pts = P2.walk_upto(t)
    if len(pts) < 3:
        return 0
    n = len(pts)
    times = P2.WTIMES[:n]
    x, y, z = P2.project(pts, cam)
    x = x + TRAIL_SEED[:n, 0]; y = y + TRAIL_SEED[:n, 1]                        # never a ruler line
    ss = 2
    img = Image.new('F', (W * ss, H * ss), 0)
    dr = ImageDraw.Draw(img)
    halo = Image.new('F', (W, H), 0)
    dh = ImageDraw.Draw(halo)
    vel = np.r_[0, np.linalg.norm(np.diff(pts, axis=0), axis=1)] / P2.DT
    step = 2
    for j in range(step, n, step):
        zj = z[j]
        if zj < .25 or z[j - step] < .25:                                       # too close to the lens: it would smear across the frame
            continue
        age = t - times[j]
        v = math.exp(-age / 1.4) * .95 + .10                                      # fresh light bright, old tangle faint
        v *= math.exp(-max(zj - .4, 0) * .55) * float(smooth(.25, .5, min(zj, z[j - step])))   # deeper in the fog = dimmer
        w = (1.6 + 3.6 * math.exp(-age / .8)) * min(2.6, 1.1 / zj) * (1 + .25 * math.sin(j * .07))
        dr.line([(x[j - step] * ss, y[j - step] * ss), (x[j] * ss, y[j] * ss)], fill=float(v), width=max(1, int(w * ss)))
        dh.line([(x[j - step], y[j - step]), (x[j], y[j])], fill=float(v * .45), width=max(2, int(w * 4.5)))   # the tube's glow
    L = np.asarray(img.resize((W, H), Image.BILINEAR), np.float32)
    Hh = gaussian_filter(np.asarray(halo, np.float32), 5)
    light = (L[..., None] * np.array([1.0, .95, .85]) * 2.2 + Hh[..., None] * np.array([1.2, .78, .34]) * 1.5 +
             fbloom(L * 1.0, (2, 7, 22, 60), (1, .8, .55, .35))[..., None] * np.array([1, .72, .32]))
    # scatter pops
    for st in P2.SCAT:
        if st <= t < st + .35:
            i = np.searchsorted(P2.WTIMES, st)
            px_, py_, pz = P2.project(P2.WALK[i], cam)
            if pz > .08:
                light += point(float(px_), float(py_), 5, 9 * math.exp(-(t - st) / .1))[..., None] * np.array([1, .9, .7])
    hx, hy, hz = P2.project(P2.photon(t), cam)
    sp = float(vel[-1]) if n > 1 else 0
    return light, (float(hx), float(hy), float(hz)), sp


# ---------------------------------------------------------------- stars
_s = np.random.default_rng(77)
SN = 900
STAR_DIR = _s.normal(size=(SN, 3)); STAR_DIR /= np.linalg.norm(STAR_DIR, axis=1, keepdims=True)
STAR_B = _s.uniform(.2, 1.0, SN) ** 2
STAR_Q = np.stack([_s.uniform(-6, 6, SN), _s.uniform(-10, 10, SN), _s.uniform(.5, 30, SN)], 1)


def stars_sky(cam, k):
    """distant stars (direction only) seen by the sun camera after the escape"""
    C, yaw, pitch, roll = cam
    q = P2.to_cam(STAR_DIR * 1000 + C, cam)
    m = q[:, 2] > 1
    u = q[m, 0] / q[m, 2] / P2.F; v = q[m, 1] / q[m, 2] / P2.F
    x, y = u * W / 2 + W / 2, H / 2 - v * W / 2
    img = Image.new('F', (W, H), 0); dr = ImageDraw.Draw(img)
    for xi, yi, b in zip(x, y, STAR_B[m]):
        if 0 <= xi < W and 0 <= yi < H:
            dr.ellipse([xi - 1.1, yi - 1.1, xi + 1.1, yi + 1.1], fill=float(b))
    return gaussian_filter(np.asarray(img, np.float32), .6)[..., None] * np.array([.85, .9, 1.0]) * 2.2 * k


def stars_warp(t, k):
    """riding the beam: stars rush past (camera-space points, wrapping in depth)"""
    s = 2.0 + 60 * ease_in((t - T_SPACE) / (T_HIT - T_SPACE)) ** .7
    dist = lambda tt: 1.5 * (tt - T_SPACE) + 30 * ease_in((tt - T_SPACE) / (T_HIT - T_SPACE)) * (T_HIT - T_SPACE)
    z1 = (STAR_Q[:, 2] - dist(t)) % 30 + .2
    z0 = (STAR_Q[:, 2] - dist(t - 1 / 60)) % 30 + .2
    img = Image.new('F', (W, H), 0); dr = ImageDraw.Draw(img)
    for i in range(SN):
        if z0[i] < z1[i]:
            continue
        x1, y1 = STAR_Q[i, 0] / z1[i] / P2.F * W / 2 + W / 2, H / 2 - STAR_Q[i, 1] / z1[i] / P2.F * W / 2
        x0, y0 = STAR_Q[i, 0] / z0[i] / P2.F * W / 2 + W / 2, H / 2 - STAR_Q[i, 1] / z0[i] / P2.F * W / 2
        if -50 < x1 < W + 50 and -50 < y1 < H + 50:
            dr.line([(x0, y0), (x1, y1)], fill=float(STAR_B[i] * min(1, 6 / z1[i])), width=2)
    return gaussian_filter(np.asarray(img, np.float32), .7)[..., None] * np.array([.85, .9, 1.0]) * 2.0 * k


# ---------------------------------------------------------------- text
def put_alpha(img, fn, al):
    if al <= .01:
        return img
    if al >= .999:
        return fn(img)
    return Image.blend(img, fn(img), al)


DIGIT_FONT = hero.font(66, BLACK)


def odometer(img, value, y, al, rate=0.0):
    """six rolling digits, leading zeros dimmed, ticks like a real counter"""
    if al <= .01:
        return img
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay)
    cw, ch = 46, 76
    groups = [5, 4, 3, None, 2, 1, 0]
    total_w = cw * 6 + 18
    x = (W - total_w) / 2
    lead = True
    for g in groups:
        if g is None:
            dr.text((x + 2, y + 6), ',', font=DIGIT_FONT, fill=(252, 244, 228, int(255 * al * (1 if value >= 1000 else .35))))
            x += 18
            continue
        p = value / 10 ** g
        d = int(p) % 10
        if g == 0:
            off = p - int(p)
        else:
            low = (value % 10 ** g) / 10 ** g
            off = max(0.0, (low - .92) / .08)
        if rate / 10 ** g > 6:                                                    # a blur of a wheel: it ticks, it can't roll
            off = 0.0
        if value >= 10 ** g:
            lead = False
        a = .32 if lead else 1.0
        cell = Image.new('RGBA', (cw, ch), (0, 0, 0, 0)); dc = ImageDraw.Draw(cell)
        for k, dd in ((0, d), (1, (d + 1) % 10)):
            yy = (k - off) * ch
            tw = dc.textlength(str(dd), font=DIGIT_FONT)
            dc.text(((cw - tw) / 2, yy - 2), str(dd), font=DIGIT_FONT, fill=(252, 244, 228, int(255 * al * a)))
        lay.alpha_composite(cell, (int(x), int(y)))
        x += cw
    sh = lay.split()[3].filter(ImageFilter.GaussianBlur(10))
    base = img.convert('RGBA')
    base.paste((0, 0, 0, 255), (0, 0), sh.point(lambda v: int(v * .7)))
    base.alpha_composite(lay)
    base = put(base.convert('RGB'), ['YEAR'], y - 40, 30, BLACK, (255, 226, 180)) if al > .5 else base.convert('RGB')
    return base


YEAR_KNOTS = ((P2.T_WALK0 + .15, 0), (7.0, 18_485), (P2.T_BOUNCE, 35_645), (11.0, 57_305), (P2.T_EXIT - .12, YEARS))


def year_at(t):
    ts, ys = zip(*YEAR_KNOTS)
    return float(np.interp(t, ts, ys))


# ---------------------------------------------------------------- the film layer: grain, chromatic aberration, lens dust, breathing bloom
LENS_DUST = None


def lens_dust():
    global LENS_DUST
    if LENS_DUST is None:
        r = np.random.default_rng(91)
        img = Image.new('F', (W // 2, H // 2), 0); dr = ImageDraw.Draw(img)
        for _ in range(26):
            x, y, rad = r.uniform(0, W / 2), r.uniform(0, H / 2), r.uniform(6, 40)
            dr.ellipse([x - rad, y - rad, x + rad, y + rad], fill=float(r.uniform(.2, 1)))
        a = gaussian_filter(np.asarray(img, np.float32), 4)
        LENS_DUST = np.asarray(Image.fromarray(a).resize((W, H), Image.BILINEAR), np.float32)
    return LENS_DUST


def film(a, t, f):
    lum = a.mean(2)
    hi = np.clip(lum - .72, 0, None)
    breathe = .22 + .06 * math.sin(t * 2.3)
    a = screen(a, fbloom(hi * 2.0, (6, 20, 60), (.6, .5, .4))[..., None] * np.array([1, .8, .5]) * breathe)
    g = lens_dust()
    a = a + (g * min(1.0, float(lum.mean()) * 2.5) * .035)[..., None] * np.array([1, .9, .7])
    # chromatic aberration: red out, blue in, about the centre
    out = np.empty_like(a)
    for c, s in ((0, 1.0016), (1, 1.0), (2, .9984)):
        if s == 1.0:
            out[..., c] = a[..., c]; continue
        m = (1 / s, 0, W / 2 * (1 - 1 / s), 0, 1 / s, H / 2 * (1 - 1 / s))
        out[..., c] = np.asarray(Image.fromarray(a[..., c].astype(np.float32)).transform((W, H), Image.AFFINE, m, Image.BILINEAR), np.float32)
    rng = np.random.default_rng(f)
    grain = gaussian_filter(rng.normal(0, 1, (H, W)).astype(np.float32), .6) * .028
    out = out + grain[..., None] * (.4 + .6 * np.sqrt(np.clip(out.mean(2), 0, 1)))[..., None]
    v = 1 - .30 * (((XX - W / 2) / (W * .75)) ** 2 + ((YY - H / 2) / (H * .65)) ** 2)
    return np.clip(out * np.clip(v, 0, 1)[..., None], 0, 1)


def to_img(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255 + .5).astype(np.uint8))


def footer(img):
    return hero.footer(img)


# ---------------------------------------------------------------- segments
DOT0 = None


def dot0():
    global DOT0
    if DOT0 is None:
        x, y, z = P2.project(P2.P0, P2.camera(0.0))
        DOT0 = (float(x), float(y))
    return DOT0


_h = np.random.default_rng(23)
HOOK_N = 20                                                                     # the hook's gold dust: 3 depths, 3 speeds
HOOK_P = np.stack([_h.uniform(-.45, .45, HOOK_N), _h.uniform(-.75, .75, HOOK_N), _h.choice([.45, 1.0, 2.2], HOOK_N)], 1)
HOOK_V = np.stack([_h.normal(0, .02, HOOK_N), _h.uniform(.005, .03, HOOK_N), np.zeros(HOOK_N)], 1)
LOCKIN = (('INSIDE THE SUN', 3.0), ('A PHOTON BOUNCES RANDOMLY', 3.7), ('TRYING TO ESCAPE', 4.4),
          ([('FOR ', CREAM), ('100,000', GOLDT), (' YEARS', CREAM)], 5.1))


def hook_dust(t, cam):
    k = 1 - ease((t - P2.T_LIT1) / .8)
    if k <= .01:
        return 0
    P = P2.C0 + HOOK_P * np.array([HOOK_P[:, 2:3].ravel(), HOOK_P[:, 2:3].ravel(), np.ones(HOOK_N)]).T + HOOK_V * t
    P[:, 0] += .015 * np.sin(t * .8 + np.arange(HOOK_N))
    x, y, z = P2.project(P, cam)
    img = Image.new('F', (W, H), 0); dr = ImageDraw.Draw(img)
    for i in range(HOOK_N):
        if z[i] < .1:
            continue
        r = 2.2 / z[i]
        v = .9 * (.6 + .4 * math.sin(t * 1.7 + i)) / (1 + .3 * z[i])
        dr.ellipse([x[i] - r, y[i] - r, x[i] + r, y[i] + r], fill=float(v))
    a = gaussian_filter(np.asarray(img, np.float32), 1.5)
    return (a * k)[..., None] * np.array([1.4, .95, .45])


def timer(img, secs, y, al):
    """the 8 m 20 s trip, ticking: fixed-width cells so the digits never jitter"""
    if al <= .01:
        return img
    s = f'{int(secs) // 60}:{int(secs) % 60:02d}'
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); dr = ImageDraw.Draw(lay)
    cw = 46
    x = (W - sum(18 if ch == ':' else cw for ch in s)) / 2
    for ch in s:
        w_ = 18 if ch == ':' else cw
        tw = dr.textlength(ch, font=DIGIT_FONT)
        dr.text((x + (w_ - tw) / 2, y - 2), ch, font=DIGIT_FONT, fill=(252, 244, 228, int(255 * al)))
        x += w_
    sh = lay.split()[3].filter(ImageFilter.GaussianBlur(10))
    base = img.convert('RGBA')
    base.paste((0, 0, 0, 255), (0, 0), sh.point(lambda v: int(v * .7)))
    base.alpha_composite(lay)
    return put_alpha(base.convert('RGB'), lambda im: put(im, ['MINUTES TO EARTH'], y - 40, 30, BLACK, (180, 215, 255)), al)


def atmosphere(t, zz, c, s, sac):
    """Earth's blue limb as we fall toward it; gone once the iris has grown around it"""
    k = s * ease((zz - .4) / 1.6)
    if k <= .01:
        return 0
    ux, uy = (EARTH_C[0] - c[0] + sac[0]) * zz / .80, (EARTH_C[1] - c[1] + sac[1]) * zz / .80
    cx, cy, R = W / 2 + ux * W / 2, H / 2 - uy * W / 2, .085 * zz / .80 * W / 2
    d = np.sqrt((XX - cx) ** 2 + (YY - cy) ** 2)
    limb = np.exp(-((d - R) / (2 + R * .035)) ** 2) * .9 + (d > R) * np.exp(-np.maximum(d - R, 0) / (3 + R * .14)) * .55
    return (limb * k)[..., None] * np.array([.30, .62, 1.25])


def seg_sun(out, f, t):
    cam = P2.camera(t)
    base = load_plate(out, f)
    ph = P2.photon(t)
    light = 0
    res = draw_trail(t, cam)
    if res:
        tl, (hx, hy, hz), sp = res
        light = light + tl
    else:
        hx, hy, hz = P2.project(ph, cam); hx, hy, hz = float(hx), float(hy), float(hz)
        sp = 0
    k_inside = 1 - ease((t - (P2.T_EXIT + .15)) / .4)
    light = light + draw_dust(t, cam, ph, k_inside * (.35 + .65 * ease((t - .2) / 1.4)))
    if hz > .05:
        breathe = 1 + .14 * math.sin(2 * math.pi * 1.4 * t)
        size = min(26, 9 / max(hz, .3) ** .6) * (1 + .3 * min(sp / 3, 1))
        hot = 22 * breathe * (1 + .5 * min(sp / 3, 1))
        light = light + photon_glow(hx, hy, size, hot, flare=1 + .4 * (breathe - 1))
    light = light + hook_dust(t, cam)
    if t > P2.T_EXIT - .1:
        light = light + stars_sky(cam, ease((t - P2.T_EXIT - .2) / .4))
    a = screen(base, light)
    # breaking through the surface: the photon first, then the camera
    a = flash(a, .55 * math.exp(-abs(t - P2.T_EXIT) / .07) + .7 * math.exp(-abs(t - (P2.T_EXIT + .30)) / .09))
    a = flash(a, .30 * math.exp(-abs(t - P2.T_BOUNCE) / .06))                     # the near-escape: knocked back in
    img = to_img(film(a, t, f))
    if t < P2.T_WALK0:
        al = 1 - ease((t - (P2.T_WALK0 - .35)) / .25)
        img = put_alpha(img, lambda im: put(put(im, ['THIS LIGHT WAS MADE'], 1160, 76, BLACK),
                                            [[('100,000', GOLDT), (' YEARS AGO', CREAM)]], 1252, 76, BLACK, glow_col=(255, 150, 40)), al)
    for i, (ln, at) in enumerate(LOCKIN):                                        # lock-in: four small lines, one by one
        lal = ease((t - at) / .25) * (1 - ease((t - 6.75) / .25))
        img = put_alpha(img, lambda im, ln=ln, i=i: put(im, [ln], 230 + 64 * i, 46, BLACK), lal)
    oal = ease((t - (P2.T_WALK0 + .15)) / .25) * (1 - ease((t - (P2.T_EXIT - .1)) / .2))
    img = odometer(img, year_at(t), 1580, oal, rate=(year_at(t + .02) - year_at(t - .02)) / .04)
    eal = ease((t - (P2.T_EXIT + .35)) / .2) * (1 - ease((t - (T_SPACE - .1)) / .2))
    img = put_alpha(img, lambda im: put(im, ['THEN IT ESCAPED.'], 270, 94, BLACK, glow_col=(255, 160, 60)), eal)
    return img


def seg_eye(out, f, t):
    base = load_plate(out, f)
    zz, c, pupil, s, sac = eye_params(t)
    light = 0
    if t < T_HIT + .05:
        light = light + stars_warp(t, ease((t - T_SPACE) / .2) * (1 - ease((t - (T_HIT - .15)) / .15)))
        # the photon just ahead of us, falling toward Earth
        u = (t - T_SPACE) / (T_HIT - T_SPACE)
        light = light + photon_glow(W / 2, H / 2, 10 * (1 - .6 * u), 26, flare=1.2 + 2 * u)
    hit = math.exp(-max(0, t - T_HIT) / .12) * (t >= T_HIT - .03)
    if hit > .01:
        light = light + photon_glow(W / 2, H / 2, 14, 30 * hit, flare=3)
    if T_HIT <= t < T_SKY:                                                       # warm light lingering in the pupil + dust in the air
        lin = math.exp(-(t - T_HIT) / 1.1) * (1 + .25 * math.sin(t * 37) * math.sin(t * 11.3))   # the beam flickers
        light = light + point(W / 2, H / 2, 40, 1.2 * lin)[..., None] * np.array([1, .75, .35])
    light = light + atmosphere(t, zz, c, s, sac)
    a = screen(base, light)
    a = flash(a, .35 * hit)
    if t > T_PUSH:                                                               # the catchlight flares into the sun
        k = ease_in((t - T_PUSH) / (T_SKY - T_PUSH))
        a = screen(a, point(W / 2, H / 2, 60 + 500 * k, 6 * k)[..., None] * np.array([1, .85, .6]))
        a = flash(a, k ** 2)
    img = to_img(film(a, t, f))
    tal = ease((t - (T_SPACE + .2)) / .25) * (1 - ease((t - (T_HIT - .25)) / .2))
    img = timer(img, 500 * ease((t - (T_SPACE + .2)) / (T_HIT - .45 - T_SPACE)) ** 1.15, 1580, tal)
    al = ease((t - (T_HIT + .35)) / .2) * (1 - ease((t - (T_PUSH - .05)) / .15))
    img = put_alpha(img, lambda im: put(im, ['AND ENDED', 'IN YOUR EYE.'], 1520, 88, BLACK, glow_col=(255, 160, 60)), al)
    return img


GRASS = None
SIL = None


def sky_layers():
    global GRASS, SIL
    if SIL is None:
        from rig import draw_figure
        hzy = H / 2 + .42 * W / 2
        prof = hzy + 260 - 150 * np.exp(-((XX - W * .28) / 380) ** 2) + 6 * np.sin(XX / 37)
        fg = smooth(-1.5, 1.5, YY - prof)
        ss = 3
        m = Image.new('L', (W * ss, H * ss), 0)
        draw_figure(ImageDraw.Draw(m), (W - W * .28) * ss, (hzy + 120) * ss, 640 * ss, 1.0, hood=0.0, stone=0.0)
        fig = np.asarray(m.resize((W, H), Image.LANCZOS), np.float32)[:, ::-1] / 255
        SIL = (hzy, np.maximum(gaussian_filter(fig, .7), fg))                        # a soft edge, not a razor
        r = np.random.default_rng(8)
        GRASS = []
        for cx in r.uniform(0, W, 140):                                               # clumps, not a comb
            for _ in range(r.integers(4, 14)):
                x = cx + r.normal(0, 9)
                GRASS.append((x, r.uniform(10, 26) * r.choice([1, 1, 1.8]), r.normal(0, .25), r.uniform(0, 6.28), r.choice([1.0, 2.3])))
    return SIL, GRASS


def seg_sky(out, f, t):
    lt = t - T_SKY
    base = load_plate(out, f)
    zz, sset = sky_params(t)
    (hzy, solid), grass = sky_layers()
    sun_uv = (.34, -.42 + .05 - sset)
    sx, sy = sun_uv[0] * W / 2 + W / 2, H / 2 - sun_uv[1] * W / 2
    lay = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(lay)
    for x, L, a0, ph, spd in grass:
        yb = hzy + 260 - 150 * math.exp(-((x - W * .28) / 380) ** 2) + 6 * math.sin(x / 37)
        a = -math.pi / 2 + a0 + .09 * math.sin(lt * spd * 1.6 + ph + x / 140) + .04 * math.sin(lt * 5.1 + ph)
        dr.line([(x, yb + 3), (x + L * math.cos(a), yb + L * math.sin(a))], fill=255, width=2)
    al = np.maximum(solid, np.asarray(lay, np.float32) / 255)
    # the silhouette layer is in the same camera: zoom it about the sun with the plate
    zf = zz ** 1.3                                                                   # nearer than the sky: shrinks faster (parallax)
    if zf > 1.0005:
        w2, h2 = W / zf, H / zf
        box = (sx - w2 * sx / W, sy - h2 * sy / H, sx - w2 * sx / W + w2, sy - h2 * sy / H + h2)
        al = np.asarray(Image.fromarray(al.astype(np.float32)).resize((W, H), Image.BILINEAR, box=box), np.float32)
    rim = np.clip(al - np.roll(al, -4, axis=1), 0, 1)
    rim = fbloom(rim, (1, 3), (1, .4)) * np.exp(-np.abs(YY - sy) / 900)
    col = base * (1 - al[..., None]) + al[..., None] * np.array([.012, .008, .01])
    light = rim[..., None] * np.array([1.5, .75, .28]) * 1.6
    # three dust depths drifting in the evening air
    r = np.random.default_rng(81)
    img = Image.new('F', (W, H), 0); d2 = ImageDraw.Draw(img)
    for depth, n, rad, spd in ((3, 60, 1.2, 10), (2, 40, 3, 26), (1, 14, 12, 60)):
        for _ in range(n):
            x0, y0, ph = r.uniform(0, W), r.uniform(0, hzy), r.uniform(0, 6.28)
            x = (x0 - spd * lt + 8 * math.sin(lt + ph)) % W; y = (y0 - spd * .4 * lt + 6 * math.cos(lt * .8 + ph)) % hzy
            d2.ellipse([x - rad, y - rad, x + rad, y + rad], fill=float(.5 / depth + .2))
    dust = gaussian_filter(np.asarray(img, np.float32), 1.2)
    light = light + dust[..., None] * np.array([.8, .45, .14])
    a = screen(col, light)
    a = flash(a, math.exp(-lt / .18))                                              # out of the catchlight's flare
    # the sun sets back into the frame-0 dot
    end = ease((t - (DUR - .60)) / .45)
    if end > 0:
        a = a * (1 - end)
        dx, dy = dot0()
        px_, py_ = lerp(sx, dx, ease((t - (DUR - .55)) / .45)), lerp(sy, dy, ease((t - (DUR - .55)) / .45))
        a = screen(a, photon_glow(px_, py_, lerp(30, 7, end), 22, flare=1)[...] * end)
    # handheld float
    img = to_img(film(a, t, f))
    ox = 3 * math.sin(lt * 1.1) + 2 * math.sin(lt * 2.7 + 1); oy = 2 * math.sin(lt * 1.4 + 2)
    img = img.transform(img.size, Image.AFFINE, (1, 0, ox, 0, 1, oy), resample=Image.BILINEAR) if end < .5 else img
    a1 = ease((lt - .15) / .2) * (1 - ease((t - (DUR - .70)) / .2))
    a2 = ease((lt - .35) / .2) * (1 - ease((t - (DUR - .70)) / .2))
    cal = ease((t - T_CTA) / .25) * (1 - ease((t - (DUR - .2)) / .15))
    img = put_alpha(img, lambda im: put(im, ['FOLLOW @SLOWLIGHTTV', 'I TRACK ONE PHOTON EVERY WEEK'], 1500, 40, BLACK, (255, 236, 205)), cal)
    img = put_alpha(img, lambda im: put(im, ['THE LIGHT YOU SEE WITH'], 210, 68, BLACK), a1)
    img = put_alpha(img, lambda im: put(im, ['IS OLDER THAN', 'CIVILIZATION.'], 296, 112, BLACK, GOLDT, glow_col=(255, 130, 30)), a2)
    return img


def frame(args):
    out, f = args
    path = os.path.join(out, 'frames', f'f{f:04d}.png')
    if os.path.exists(path):
        return
    t = f / FPS
    if t < T_SPACE:
        img = seg_sun(out, f, t)
    elif t < T_SKY:
        img = seg_eye(out, f, t)
    else:
        img = seg_sky(out, f, t)
    img = footer(img)
    img.save(path + '.tmp.png')
    os.replace(path + '.tmp.png', path)


def events():
    return dict(scatter=[round(s, 3) for s in P2.SCAT], year_end=P2.T_WALK1 + .25,
                cuts=dict(trap=P2.T_WALK0, escape=P2.T_EXIT, eye=T_HIT, punch=T_SKY),
                beam_hit=T_HOLD + .1, space=T_SPACE, push=T_PUSH, near=P2.T_BOUNCE, dur=DUR)


if __name__ == '__main__':
    mode, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    a = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    b = int(sys.argv[4]) if len(sys.argv) > 4 else NF
    if mode == 'plates':
        jp = os.path.join(out, f'jobs_{a}_{b}.json')
        json.dump(plate_jobs(out, a, b), open(jp, 'w'))
        subprocess.run(['node', os.path.join(HERE, 'gl', 'render.mjs'), jp], check=True, env=dict(os.environ, SHADER='shots2.glsl'))
    elif mode == 'frames':
        os.makedirs(os.path.join(out, 'frames'), exist_ok=True)
        fl = [int(x) for x in os.environ['ONLY'].split(',')] if os.environ.get('ONLY') else range(a, b)
        with Pool(int(os.environ.get('PROCS', 4))) as pool:
            for _ in pool.imap_unordered(frame, [(out, f) for f in fl]):
                pass
    elif mode == 'events':
        json.dump(events(), open(os.path.join(out, 'events.json'), 'w'), indent=1)
