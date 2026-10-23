"""Hero frames v2 for "The Photon That Made Your Eye" (volumetric look; storyboard stills, not the final renderer).

python3 hero.py OUTDIR [scale] [names...]   -> hero_1_birth .. hero_5_punch .png + contact.jpg
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.ndimage import gaussian_filter, map_coordinates

SC = float(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].replace('.', '').isdigit() else 1.0
W, H = int(1080 * SC), int(1920 * SC)
BOLD = '/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf'
BLACK = '/usr/share/fonts/opentype/inter/InterDisplay-Black.otf'
MONO = '/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf'
CREAM = (252, 244, 228)
GOLDT = (255, 196, 96)
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


def px(v):
    return v * SC


def norm01(a):
    return (a - a.min()) / (a.max() - a.min() + 1e-9)


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def fbm(seed, sig, wt, h=None, w=None):
    h = h or H; w = w or W
    r = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    for s, k in zip(sig, wt):
        s = max(.5, px(s))
        n = gaussian_filter(r.standard_normal((h, w)).astype(np.float32), s)
        out += k * n / (n.std() + 1e-9)
    return out / sum(wt)


def warp(a, seed, amt, sig=(140, 50)):
    wx = fbm(seed, sig, (1, .5)); wy = fbm(seed + 1, sig, (1, .5))
    return map_coordinates(a, [YY + wy * px(amt), XX + wx * px(amt)], order=1, mode='reflect')


def ramp(t, stops):
    t = np.clip(t, 0, 1)
    xs = np.array([s[0] for s in stops]); cs = np.array([s[1] for s in stops], np.float32)
    return np.stack([np.interp(t, xs, cs[:, c]) for c in range(3)], -1)


def bloom(L, sig=(2, 7, 22, 70, 180), wt=(1, .8, .55, .35, .25)):
    return sum(k * gaussian_filter(L, px(s)) for s, k in zip(sig, wt))


def tonemap(rgb, exposure=1.0):
    x = np.maximum(rgb * exposure, 0)
    a, b, c, d, e = 2.51, 0.03, 2.43, 0.59, 0.14            # ACES fit
    y = (x * (a * x + b)) / (x * (c * x + d) + e)
    return np.clip(y, 0, 1)


def finish(rgb, exposure=1.0, grain=0.012, vign=0.35, seed=0):
    rgb = tonemap(rgb, exposure)
    v = 1 - vign * (((XX - W / 2) / (W * .75)) ** 2 + ((YY - H / 2) / (H * .7)) ** 2)
    rgb = rgb * np.clip(v, 0, 1)[..., None]
    rgb += np.random.default_rng(seed).normal(0, grain, rgb.shape[:2])[..., None]
    rgb = np.clip(rgb, 0, 1) ** (1 / 1.05)
    return Image.fromarray((rgb * 255 + .5).astype(np.uint8))


def point(cx, cy, r, hot):
    d2 = (XX - cx) ** 2 + (YY - cy) ** 2
    return np.exp(-d2 / (2 * px(r) ** 2)) * hot + px(r) ** 2 / (d2 + px(r) ** 2) * hot * .12


def bokeh(seed, n, rmin, rmax, cols, box=None, power=2.2):
    """Soft out-of-focus dust discs, bigger = fainter."""
    r = np.random.default_rng(seed)
    out = np.zeros((H, W, 3), np.float32)
    lay = Image.new('F', (W, H), 0)
    for _ in range(n):
        u = r.random() ** power
        rad = px(rmin + (rmax - rmin) * u)
        x = r.uniform(0, W); y = r.uniform(0, H)
        if box is not None and not box(x, y):
            continue
        v = float(r.uniform(.25, 1) * (1.15 - .85 * u))
        ImageDraw.Draw(lay).ellipse([x - rad, y - rad, x + rad, y + rad], fill=v)
    a = np.asarray(lay, np.float32)
    a = gaussian_filter(a, px(1.5))
    return a[..., None] * np.array(cols, np.float32)


# ------------------------------------------------------------------------ text
def font(p, f=BOLD):
    return ImageFont.truetype(f, int(px(p)))


def put(img, lines, y, size, f=BOLD, col=CREAM, track=0, glow_col=None, shadow=.75):
    """Centred lines; each line may be [(text, colour), ...]."""
    base = img.convert('RGBA')
    sh = Image.new('L', img.size, 0); dsh = ImageDraw.Draw(sh)
    fg = Image.new('RGBA', img.size, (0, 0, 0, 0)); dfg = ImageDraw.Draw(fg)
    fo = font(size, f)
    for i, line in enumerate(lines):
        parts = line if isinstance(line, list) else [(line, col)]
        wtot = sum(dfg.textlength(t, font=fo) for t, _ in parts)
        x = (W - wtot) / 2; yy = px(y) + i * px(size) * 1.06
        for t, c in parts:
            dsh.text((x, yy + px(5)), t, font=fo, fill=int(255 * shadow))
            dfg.text((x, yy), t, font=fo, fill=c + (255,))
            x += dfg.textlength(t, font=fo)
    sh = sh.filter(ImageFilter.GaussianBlur(px(14)))
    base.paste((0, 0, 0, 255), (0, 0), sh)
    if glow_col:
        g = fg.split()[3].filter(ImageFilter.GaussianBlur(px(18)))
        base.paste(glow_col + (255,), (0, 0), g.point(lambda v: int(v * .45)))
    base.alpha_composite(fg)
    return base.convert('RGB')


def footer(img):
    return put(img, ['THOUGHT EXPERIMENT · NOT TO SCALE'], 1846, 24, MONO, (215, 200, 175), shadow=.9)


# ------------------------------------------------------------------------ the golden fog
def gold_fog(seed, hole=(0.5, 0.47), hole_r=(0.30, 0.25), light=None, swirl=0.0):
    """Volumetric-looking plasma: three depth layers of wispy fog around a darker hollow, lit from the photon."""
    cx, cy = W * hole[0], H * hole[1]
    if light is None:
        light = (cx, cy)
    nx, ny = (XX - cx) / (W * hole_r[0] * 2), (YY - cy) / (H * hole_r[1] * 2)
    rr = np.sqrt(nx ** 2 + ny ** 2)
    th = np.arctan2(ny, nx)
    acc = np.zeros((H, W, 3), np.float32)
    trans = np.ones((H, W), np.float32)
    dl = np.sqrt((XX - light[0]) ** 2 + (YY - light[1]) ** 2) / px(520)
    illum = 1 / (1 + dl ** 2) * 1.4 + .12
    # back to front: blurred far wall, mid wisps, sharp near wisps
    for li, (blur, scale, dens_k, warp_amt, bright) in enumerate(
            [(9, 1.25, .85, 120, .55), (2.5, 1.0, 1.0, 90, 1.0), (0, .8, 1.15, 70, 1.25)]):
        s = seed + 17 * li
        n = fbm(s, (240 * scale, 90 * scale, 34 * scale, 12 * scale, 5), (1, .7, .45, .3, .15))
        # wisps: ridged noise, swirled around the hollow
        ridge = 1 - np.abs(fbm(s + 3, (60 * scale, 22 * scale, 8), (1, .5, .25)))
        ridge = smooth(.35, 1.0, ridge) ** 1.6
        d = .55 * norm01(n) + .55 * ridge
        if swirl:
            a = th + swirl * (1 - np.clip(rr, 0, 1.5))
            d = map_coordinates(d, [cy + rr * np.sin(a) * H * hole_r[1] * 2, cx + rr * np.cos(a) * W * hole_r[0] * 2], order=1, mode='reflect') * .5 + d * .5
        d = warp(d, s + 7, warp_amt)
        hollow = smooth(.45 - .08 * li, 1.15 - .05 * li, rr + .18 * fbm(s + 9, (120, 40), (1, .5)))
        dens = np.clip((d - .42) * 2.4, 0, 1) * hollow * dens_k
        if blur:
            dens = gaussian_filter(dens, px(blur))
        # fake self-shadowing: brighter where density faces the light
        gx = np.gradient(gaussian_filter(dens, px(4)), axis=1); gy = np.gradient(gaussian_filter(dens, px(4)), axis=0)
        lx, ly = light[0] - XX, light[1] - YY
        ln = np.sqrt(lx ** 2 + ly ** 2) + 1
        facing = np.clip(-(gx * lx + gy * ly) / ln * px(60), -1, 1)
        rim = np.clip(facing, 0, 1) ** 1.5
        lit = illum * (0.5 + 0.9 * rim) * bright * (1 - .35 * np.clip(-facing, 0, 1))
        col = ramp(np.clip(lit * .55 + dens * .25, 0, 1),
                   [(0, (.05, .015, .0)), (.25, (.35, .12, .02)), (.5, (.85, .42, .08)), (.75, (1.1, .74, .3)), (1, (1.6, 1.3, .9))])
        emit = col * (lit[..., None] * 1.3) * dens[..., None]
        a = np.clip(dens * (0.75 + .1 * li), 0, 1)
        acc = acc * (1 - a[..., None]) + emit       # front layers occlude back
        trans *= (1 - a)
    # dark-amber haze filling the hollow (depth)
    haze = np.exp(-(rr / .9) ** 2) * .10
    acc += (haze * illum)[..., None] * np.array([1, .55, .15]) * trans[..., None]
    return acc


def curvy_walk(seed, n, x0, y0, rx, ry, step=6.0):
    """Smooth, curving path with occasional sharp scatters; steered to stay inside an ellipse."""
    r = np.random.default_rng(seed)
    x, y, a = x0, y0, r.uniform(0, 2 * math.pi)
    k = 0.0
    pts = [(x, y)]
    for i in range(n):
        if r.random() < .012:                       # a scattering: sharp new direction
            a += r.uniform(-2.6, 2.6)
            k = r.normal(0, .06)
        k += r.normal(0, .004); k = max(-.09, min(.09, k))
        ex, ey = (x - x0) / rx, (y - y0) / ry
        e = math.hypot(ex, ey)
        if e > .75:                                  # curl back toward the middle
            want = math.atan2(-ey * ry, -ex * rx)
            da = (want - a + math.pi) % (2 * math.pi) - math.pi
            a += da * .06 * (e - .75) * 4
        a += k
        x += px(step) * math.cos(a); y += px(step) * math.sin(a)
        pts.append((x, y))
    return pts


def draw_trails(pts, fade=3.0, ss=2, width=(1.0, 3.2)):
    img = Image.new('F', (W * ss, H * ss), 0)
    dr = ImageDraw.Draw(img)
    n = len(pts)
    for i in range(1, n, 1):
        age = (n - i) / n
        v = math.exp(-age * fade)
        w = max(1, int(ss * px(width[0] + (width[1] - width[0]) * v ** 2)))
        dr.line([(pts[i - 1][0] * ss, pts[i - 1][1] * ss), (pts[i][0] * ss, pts[i][1] * ss)], fill=float(.25 + .75 * v), width=w)
    return np.asarray(img.resize((W, H), Image.BILINEAR), np.float32)


# ------------------------------------------------------------------------ frames
def f_birth():
    rgb = np.zeros((H, W, 3), np.float32)
    cx, cy = W / 2, H * .44
    p = point(cx, cy, 7, 14)
    streak = np.exp(-((YY - cy) ** 2) / px(3) ** 2) * np.exp(-np.abs(XX - cx) / px(330)) * 1.2
    v = np.exp(-((XX - cx) ** 2) / px(2.5) ** 2) * np.exp(-np.abs(YY - cy) / px(120)) * .5
    rgb += (p + streak + v)[..., None] * np.array([1, .95, .85])
    rgb += bloom(p * .2, (20, 60, 160), (.5, .5, .4))[..., None] * np.array([1, .55, .15])
    rgb += bokeh(3, 40, 4, 22, (.5, .3, .08), box=lambda x, y: math.hypot(x - cx, y - cy) < px(420))
    img = finish(rgb, 1.0, vign=.2)
    img = put(img, ['THIS LIGHT WAS MADE'], 1150, 92, BLACK)
    img = put(img, [[('100,000', GOLDT), (' YEARS AGO', CREAM)]], 1262, 92, BLACK, glow_col=(255, 150, 40))
    return footer(img)


def f_trap():
    cx, cy = W * .5, H * .47
    rgb = gold_fog(5, (0.5, 0.47), (0.36, 0.27), swirl=1.4)
    # trails: two passes, long faint history + bright recent loops
    pts = curvy_walk(12, 5200, cx, cy, px(360), px(470), step=5.5)
    old = draw_trails(pts, fade=1.2, width=(.6, 1.6))
    new = draw_trails(pts[-1100:], fade=2.2, width=(1.0, 3.6))
    L = old * .55 + new * 1.6
    trail_col = np.array([1.0, .93, .78])
    rgb += (L * 1.1)[..., None] * trail_col + bloom(L * .55)[..., None] * np.array([1, .78, .4])
    hx, hy = pts[-1]
    p = point(hx, hy, 9, 16)
    rgb += p[..., None] * np.array([1, .97, .92]) + bloom(p * .25, (10, 40, 120, 300), (1, .8, .6, .4))[..., None] * np.array([1, .7, .3])
    # dust: fine sparks + big bokeh
    rgb += bokeh(21, 900, 1.2, 3.5, (1.6, 1.1, .45), power=1)
    rgb += bokeh(22, 70, 10, 46, (.45, .3, .08))
    img = finish(rgb, 1.05, vign=.45, seed=2)
    img = put(img, ['YEAR'], 1290, 64, BLACK, (255, 236, 205))
    img = put(img, ['61,240'], 1352, 196, BLACK, CREAM, glow_col=(255, 170, 60))
    return footer(img)


def f_escape():
    cy_s, R = H * 1.62, H * 1.0
    sx = W * .52
    d = np.sqrt((XX - W / 2) ** 2 + (YY - cy_s) ** 2)
    surf_y = cy_s - R
    inside = smooth(-px(3), px(3), R - d)
    # photosphere: granulation + fog, limb-darkened
    gran = 1 - np.abs(fbm(41, (9, 4), (1, .4)))
    gran = smooth(.3, 1, gran)
    big = norm01(fbm(42, (160, 60, 20), (1, .6, .3)))
    t = np.clip(.45 * big + .45 * gran + .15, 0, 1) * (.55 + .45 * smooth(0, px(300), R - d))
    sun = ramp(t, [(0, (.25, .06, 0)), (.45, (.9, .35, .04)), (.75, (1.3, .8, .25)), (1, (1.8, 1.4, .8))])
    rgb = sun * inside[..., None]
    # corona / prominences: wispy fog hugging the limb
    wisp = norm01(warp(1 - np.abs(fbm(43, (50, 18, 6), (1, .5, .25))), 44, 60))
    above = np.clip(d - R, 0, None)
    corona = np.exp(-above / px(90)) * (0.5 + 0.9 * smooth(.55, 1, wisp)) * (1 - inside)
    rgb += corona[..., None] * np.array([1.2, .55, .14])
    # the shockwave: an expanding dome of light rising off the surface, rim-lit at its edge
    py = surf_y - px(330)
    dx, dyy = (XX - sx) / px(470), (YY - surf_y) / px(400)
    rs = np.sqrt(dx ** 2 + dyy ** 2)
    shell = np.exp(-((rs - 1) / .035) ** 2) * (YY < surf_y + px(10))
    fres = smooth(.0, 1.0, np.abs(dx)) ** 2 * .9 + .35                # brighter at the dome's flanks
    shell = shell * fres * (0.75 + .5 * smooth(.4, 1, wisp))
    inner = np.exp(-((rs - .93) / .12) ** 2) * (YY < surf_y) * .35
    rgb += (shell * 2.6 + inner)[..., None] * np.array([1.2, .85, .5])
    rgb += bloom(shell * .9, (6, 25, 80), (.8, .5, .35))[..., None] * np.array([1, .6, .25])
    # the surface ripple where the dome meets the photosphere
    ripple = np.exp(-((d - R + px(10)) / px(14)) ** 2) * np.exp(-((XX - sx) / px(520)) ** 2) * 1.8
    rgb += ripple[..., None] * np.array([1.3, .8, .35])
    # ejecta sparks blown off by the shock
    r = np.random.default_rng(7)
    lay = Image.new('F', (W, H), 0); dr = ImageDraw.Draw(lay)
    for _ in range(260):
        a = r.uniform(math.pi * 1.05, math.pi * 1.95); rad = r.uniform(.7, 1.25)
        x0 = sx + math.cos(a) * px(470) * rad; y0 = surf_y + math.sin(a) * px(400) * rad
        L = px(r.uniform(8, 40))
        dr.line([(x0, y0), (x0 + math.cos(a) * L, y0 + math.sin(a) * L)], fill=float(r.uniform(.3, 1)), width=max(1, int(px(2))))
    ej = np.asarray(lay, np.float32)
    rgb += (ej + bloom(ej * .3, (3, 12), (1, .6)))[..., None] * np.array([1.2, .8, .4])
    # the photon: slow-mo smear up out of the dome
    tt = np.clip((surf_y - YY) / (surf_y - py), 0, 1) * (YY > py) * (YY < surf_y)
    streak = np.exp(-((XX - sx) ** 2) / px(2.2) ** 2) * tt ** 1.5 * 3.0
    rgb += streak[..., None] * np.array([1, .97, .9]) + bloom(streak * .4, (3, 12, 40), (1, .6, .4))[..., None] * np.array([1, .75, .4])
    p = point(sx, py, 10, 20)
    rgb += p[..., None] + bloom(p * .25, (12, 50, 160, 400), (1, .8, .55, .35))[..., None] * np.array([1, .75, .35])
    flare = np.exp(-((YY - py) / px(3)) ** 2) * np.exp(-np.abs(XX - sx) / px(380)) * 1.3
    rgb += flare[..., None] * np.array([1, .8, .5])
    # stars in black space
    st = np.zeros((H, W), np.float32)
    st[r.integers(0, H, 700), r.integers(0, W, 700)] = r.uniform(.3, 2.2, 700)
    rgb += (gaussian_filter(st, px(.8)) * 2.2 * (1 - inside) * (YY < surf_y - px(60)))[..., None] * np.array([.85, .9, 1])
    img = finish(rgb, .95, vign=.3, seed=3)
    img = put(img, ['THEN IT ESCAPED.'], 300, 110, BLACK, glow_col=(255, 170, 70))
    return footer(img)


def earth_tex(cx, cy, R, seed=31):
    d = np.sqrt((XX - cx) ** 2 + (YY - cy) ** 2)
    m = smooth(px(1), -px(1), d - R)
    n = norm01(fbm(seed, (R / SC * .25, R / SC * .1, R / SC * .04), (1, .5, .3)))
    land = smooth(.56, .6, n)
    cloud = smooth(.5, .75, norm01(warp(fbm(seed + 1, (R / SC * .15, R / SC * .05), (1, .5)), seed + 2, R / SC * .1)))
    col = np.array([.02, .12, .40]) * (1 - land[..., None]) + np.array([.18, .32, .12]) * land[..., None]
    col = col * (1 - cloud[..., None] * .9) + cloud[..., None] * .9
    nz = np.sqrt(np.clip(1 - (d / R) ** 2, 0, 1))
    lx = (XX - cx) / R; ly = (YY - cy) / R
    lit = np.clip(.15 + 1.0 * (.5 * nz - .45 * lx - .35 * ly), .03, 1.3)
    atm = np.exp(-np.abs(d - R) / (R * .05)) * .7
    return col * (m * lit)[..., None] + atm[..., None] * np.array([.3, .55, 1.0]), m


def f_eye():
    cx, cy, R = W / 2, H * .47, px(470)
    dx, dy = XX - cx, YY - cy
    r = np.sqrt(dx * dx + dy * dy) / R; th = np.arctan2(dy, dx)
    rng = np.random.default_rng(5)
    nb = 3000
    f1 = norm01(gaussian_filter(rng.standard_normal(nb), 1.0, mode='wrap'))
    f2 = norm01(gaussian_filter(rng.standard_normal(nb), 5, mode='wrap'))
    wob = fbm(17, (40, 12), (1, .5))
    idx = ((th / (2 * np.pi) + .5) * nb + wob * 8 + r * 40).astype(int) % nb
    fib = f1[idx] * .55 + f2[idx] * .45
    crypt = smooth(.55, .9, norm01(fbm(19, (14, 6), (1, .5)))) * smooth(.35, .5, r) * smooth(.85, .7, r)
    pupil = .30
    t = np.clip(fib * .75 + .25 * norm01(fbm(18, (30, 8), (1, .4))) - .35 * crypt, 0, 1)
    iris = ramp(t, [(0, (.03, .012, .004)), (.35, (.16, .07, .02)), (.62, (.48, .26, .07)), (.85, (.85, .58, .22)), (1, (1.1, .85, .45))])
    iris *= (.35 + .9 * smooth(1.0, .5, r))[..., None]                        # depth falloff to the rim
    iris *= (1 - .85 * smooth(.86, 1.0, r))[..., None]                        # dark limbal ring
    iris += (np.exp(-((r - .46) / .03) ** 2) * .35)[..., None] * np.array([.9, .55, .2])   # collarette
    pup = smooth(pupil + .01, pupil - .01, r)
    iris = iris * (1 - pup[..., None]) + pup[..., None] * np.array([.004, .004, .006])
    # the photon's light lights the iris from where it arrives (upper left)
    lg = np.clip(1 - np.sqrt((XX - (cx - px(160))) ** 2 + (YY - (cy - px(260))) ** 2) / px(700), 0, 1) ** 2
    iris *= (1 + 1.4 * lg)[..., None]
    in_i = smooth(1.01, .99, r)
    scl = np.array([.62, .55, .52]) * (.35 + .65 * smooth(1.9, 1.0, r))[..., None]
    veins = smooth(.82, .95, norm01(1 - np.abs(fbm(41, (6, 2.5), (1, .5))))) * smooth(1.1, 1.8, r)
    scl = scl * (1 - veins[..., None] * np.array([0, .5, .5]))
    rgb = scl * (1 - in_i[..., None]) + iris * in_i[..., None]
    # Earth reflected in the pupil (cornea mirror), slightly off-centre
    ex, ey = cx + px(30), cy - px(22)
    earth, em = earth_tex(ex, ey, R * .17)
    rgb = rgb * (1 - em[..., None] * .92) + earth * 1.25
    # wet cornea: broad soft window reflection + sharp sun catchlight
    corn = np.exp(-(((XX - (cx - px(210))) / px(120)) ** 2 + ((YY - (cy - px(250))) / px(70)) ** 2)) * .35 * in_i
    rgb += corn[..., None] * np.array([1, .9, .75])
    cat = point(cx - px(205), cy - px(245), 9, 10) * smooth(1.1, .95, r)
    rgb += cat[..., None] * np.array([1, .95, .85]) + bloom(cat * .15, (8, 30), (1, .6))[..., None] * np.array([1, .7, .3])
    # lids and skin: macro, so the lids crop the frame
    u = dx / px(760)
    top = cy - px(560) * np.clip(1 - u ** 2, 0, 1) ** .8 + px(70)
    bot = cy + px(470) * np.clip(1 - u ** 2, 0, 1) ** 1.05 + px(20)
    op = smooth(-px(5), px(5), YY - top) * smooth(-px(5), px(5), bot - YY)
    shade = smooth(0, px(170), YY - top) ** .7 * (.55 + .45 * smooth(0, px(120), bot - YY))
    skin_t = norm01(fbm(51, (80, 20, 4), (1, .4, .2)))
    skin = ramp(skin_t, [(0, (.10, .05, .03)), (1, (.30, .17, .11))]) * (.4 + .6 * lg[..., None] + .2)
    rgb = rgb * (shade * op)[..., None] + skin * (1 - op)[..., None]
    lay = Image.new('F', (W, H), 0); dr = ImageDraw.Draw(lay)
    for i in range(220):
        x = rng.uniform(0, W); uu = (x - cx) / px(760)
        y = cy - px(560) * max(0, 1 - uu * uu) ** .8 + px(70)
        L = px(rng.uniform(70, 170)) * max(.25, 1 - abs(uu))
        a = -math.pi / 2 + uu * 1.0 + rng.normal(0, .12)
        bend = rng.uniform(.1, .3)
        p0 = (x, y); p1 = (x + L * .5 * math.cos(a), y + L * .5 * math.sin(a)); p2 = (x + L * math.cos(a + bend), y + L * math.sin(a + bend))
        dr.line([p0, p1, p2], fill=1.0, width=max(1, int(px(rng.uniform(2, 4)))))
    lash = gaussian_filter(np.asarray(lay, np.float32), px(.8))
    rgb *= (1 - np.clip(lash, 0, 1) * .95)[..., None]
    # the beam: soft gold shaft with dust, ending in the pupil
    x0, y0 = cx - px(330), -px(40); x1, y1 = cx + px(4), cy + px(4)
    vx, vy = x1 - x0, y1 - y0; L = math.hypot(vx, vy); vx /= L; vy /= L
    along = (XX - x0) * vx + (YY - y0) * vy
    perp = np.abs((XX - x0) * vy - (YY - y0) * vx)
    on = smooth(0, px(60), along) * smooth(L + px(2), L - px(30), along)
    core = np.exp(-(perp / px(2.4)) ** 2) * on * 2.4 * (.4 + .6 * along / L)
    shaft = np.exp(-(perp / px(38)) ** 2) * on * .22
    rgb += (core + shaft)[..., None] * np.array([1, .9, .7]) + bloom(core * .35, (4, 16, 60), (1, .6, .4))[..., None] * np.array([1, .7, .3])
    dust = bokeh(61, 260, 1, 4, (1.2, .9, .5), power=1, box=lambda x, y: abs((x - x0) * vy - (y - y0) * vx) < px(70))
    rgb += dust
    hit = point(x1, y1, 7, 9)
    rgb += hit[..., None] + bloom(hit * .2, (10, 40, 120), (1, .7, .4))[..., None] * np.array([1, .7, .3])
    img = finish(rgb, 1.05, vign=.55, seed=4)
    img = put(img, ['AND ENDED IN YOUR EYE.'], 1700, 46, BLACK, (255, 236, 205))
    return footer(img)


def f_punch():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from rig import draw_figure
    hz = H * .70
    sx, sy = W * .64, hz - px(40)
    h01 = np.clip((hz - YY) / hz, 0, 1)
    sky = ramp(h01 ** .55, [(0, (1.6, .75, .22)), (.18, (1.1, .40, .12)), (.42, (.42, .13, .12)), (.7, (.10, .04, .08)), (1, (.02, .015, .03))])
    d = np.sqrt((XX - sx) ** 2 + ((YY - sy) * 1.0) ** 2)
    sun = smooth(px(112), px(108), d) * 6 + np.exp(-d / px(120)) * 1.6 + np.exp(-d / px(420)) * .7
    rgb = sky + sun[..., None] * np.array([1, .72, .38])
    rays = (.5 + .5 * np.sin(np.arctan2(YY - sy, XX - sx) * 23 + fbm(71, (200,), (1,)) * 2)) * np.exp(-d / px(700)) * .25 * (YY < sy)
    rgb += rays[..., None] * np.array([1, .6, .25])
    # haze banks
    for k, (yb, dark) in enumerate([(hz + px(10), .55), (hz + px(70), .3)]):
        prof = yb - px(30) * np.sin(XX / px(260) + k * 2) - px(20) * np.cos(XX / px(90) + k)
        m = smooth(-px(2), px(2), YY - prof)
        hcol = np.array([.55, .22, .08]) * dark
        rgb = rgb * (1 - m[..., None]) + m[..., None] * hcol * (1 + .6 * np.exp(-np.abs(XX - sx) / px(300)))[..., None]
    # foreground ridge with grass, near black
    prof = hz + px(160) - px(70) * np.exp(-((XX - W * .3) / px(420)) ** 2) + px(10) * np.sin(XX / px(40))
    fg = smooth(-px(2), px(2), YY - prof)
    lay = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(lay)
    r = np.random.default_rng(8)
    for _ in range(int(900 * SC)):
        x = r.uniform(0, W); yb = hz + px(160) - px(70) * math.exp(-((x - W * .3) / px(420)) ** 2) + px(10) * math.sin(x / px(40))
        L = px(r.uniform(10, 46)); a = -math.pi / 2 + r.normal(0, .25)
        dr.line([(x, yb + 2), (x + L * math.cos(a), yb + L * math.sin(a))], fill=255, width=max(1, int(px(2))))
    grass = np.asarray(lay, np.float32) / 255
    fg = np.maximum(fg, grass)
    # stargazer: upright modern rig, big, facing the sun, gold rim light
    ss = 3
    m = Image.new('L', (W * ss, H * ss), 0)
    s = px(980)
    fx = W - W * .30
    yfeet = hz + px(160) - px(70) * math.exp(-((W * .3 - W * .3) / px(420)) ** 2) + px(8)
    draw_figure(ImageDraw.Draw(m), fx * ss, yfeet * ss, s * ss, 1.0, hood=0.6, stone=0.0)
    a = np.asarray(m.resize((W, H), Image.LANCZOS), np.float32)[:, ::-1] / 255
    a = np.maximum(a, fg)
    toward = np.clip(a - np.roll(np.roll(a, -int(px(5)), axis=1), int(px(3)), axis=0), 0, 1)
    rim = gaussian_filter(toward, px(1.2)) * a
    wrap = gaussian_filter(a, px(10)) * (1 - a) * np.exp(-d / px(500)) * .0
    rgb = rgb * (1 - a[..., None]) + a[..., None] * np.array([.012, .008, .01]) + rim[..., None] * np.array([1.6, .8, .3]) * 1.3
    # light wrap: the sun bleeds over the silhouette edge
    rgb += bloom(sun * .06 * (1 - a), (10, 40), (1, .6))[..., None] * np.array([1, .6, .25])
    rgb += bokeh(81, 60, 3, 18, (.6, .35, .1), box=lambda x, y: y < hz)
    img = finish(rgb, 1.0, vign=.35, seed=5)
    img = put(img, ['THE LIGHT YOU SEE WITH'], 210, 78, BLACK)
    img = put(img, ['IS OLDER THAN', 'CIVILIZATION.'], 312, 128, BLACK, GOLDT, glow_col=(255, 140, 40))
    return footer(img)


FRAMES = [('hero_1_birth', f_birth), ('hero_2_trap', f_trap), ('hero_3_escape', f_escape), ('hero_4_eye', f_eye), ('hero_5_punch', f_punch)]

if __name__ == '__main__':
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    only = [a for a in sys.argv[3:]]
    for name, fn in FRAMES:
        if only and not any(o in name for o in only):
            continue
        fn().save(os.path.join(out, name + '.png'))
        print(name, flush=True)
    ims = [Image.open(os.path.join(out, n + '.png')).resize((432, 768), Image.LANCZOS) for n, _ in FRAMES if os.path.exists(os.path.join(out, n + '.png'))]
    sheet = Image.new('RGB', (442 * len(ims) + 10, 788), (12, 12, 15))
    for i, im in enumerate(ims):
        sheet.paste(im, (10 + i * 442, 10))
    sheet.save(os.path.join(out, 'contact.jpg'), quality=90)
