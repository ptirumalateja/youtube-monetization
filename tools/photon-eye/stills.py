"""Concept stills for "The Photon That Made Your Eye" storyboard (not the final renderer).

python3 stills.py OUTDIR    -> still_01..07.png + contact.jpg
numpy + PIL + scipy; the stargazer silhouette is the rig from tools/alien-perspective (modern pose).
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter, map_coordinates

W, H = 1080, 1920
BOLD = '/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf'
MONO = '/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf'
CREAM = (250, 240, 220)


def lerp(a, b, u):
    return a + (b - a) * u


def fbm(h, w, seed, sig=(90, 30, 10, 3), wt=(1, .55, .3, .15)):
    r = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    for s, k in zip(sig, wt):
        out += k * gaussian_filter(r.standard_normal((h, w)).astype(np.float32), s) * (2 * math.sqrt(math.pi) * s)
    return out / sum(wt)


def norm01(a):
    return (a - a.min()) / (a.max() - a.min() + 1e-9)


def to_img(rgb):
    rgb = 1 - np.exp(-np.maximum(rgb, 0) * 1.25)     # soft filmic shoulder
    return Image.fromarray((np.clip(rgb, 0, 1) * 255 + .5).astype(np.uint8))


def ramp(t, stops):
    t = np.clip(t, 0, 1)
    xs = np.array([s[0] for s in stops]); cs = np.array([s[1] for s in stops], np.float32)
    return np.stack([np.interp(t, xs, cs[:, c]) for c in range(3)], -1)


def glow(mask, sigmas=(2, 8, 30, 90), wts=(1, .7, .45, .3)):
    return sum(k * gaussian_filter(mask, s) for s, k in zip(sigmas, wts))


YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


# ------------------------------------------------------------------ text
def font(px, f=BOLD):
    return ImageFont.truetype(f, px)


def text(img, lines, y, px, f=BOLD, col=CREAM, shadow=True, gap=1.08):
    dr = ImageDraw.Draw(img)
    fo = font(px, f)
    for i, s in enumerate(lines):
        w = dr.textlength(s, font=fo)
        x = (W - w) / 2; yy = y + i * px * gap
        if shadow:
            sh = Image.new('L', img.size, 0)
            ImageDraw.Draw(sh).text((x, yy + 4), s, font=fo, fill=200)
            sh = sh.filter(__import__('PIL.ImageFilter', fromlist=['x']).GaussianBlur(10))
            img.paste((0, 0, 0), (0, 0), sh)
            dr = ImageDraw.Draw(img)
        dr.text((x, yy), s, font=fo, fill=col)


def label(img, s, y, px=34, col=(255, 214, 150)):
    text(img, [s], y, px, MONO, col, shadow=True)


def footer(img):
    label(img, 'THOUGHT EXPERIMENT · NOT TO SCALE', 1840, 26, (200, 190, 170))


# ------------------------------------------------------------------ shots
def photon_core(cx, cy, r=10, hot=6.0):
    d2 = (XX - cx) ** 2 + (YY - cy) ** 2
    core = np.exp(-d2 / (2 * r * r)) * hot
    halo = 1.2 * r * r / (d2 + r * r) * 1.6
    return core, halo


def shot_birth():
    rgb = np.zeros((H, W, 3), np.float32)
    core, halo = photon_core(W / 2, H / 2 - 40, 9, 8)
    streak = np.exp(-((YY - (H / 2 - 40)) ** 2) / 8) * np.exp(-np.abs(XX - W / 2) / 260) * 0.9
    lum = core + halo * 0.6 + streak
    rgb += lum[..., None] * np.array([1.0, 0.93, 0.80])
    rgb += (halo * 0.5)[..., None] * np.array([1.0, 0.55, 0.15])
    img = to_img(rgb)
    text(img, ['THIS LIGHT WAS MADE'], 1180, 84)
    text(img, ['100,000 YEARS AGO'], 1290, 104, col=(255, 200, 110))
    return img


def plasma(seed=3, warp=60):
    base = fbm(H, W, seed, sig=(160, 60, 22, 7), wt=(1, .6, .35, .18))
    wx = fbm(H, W, seed + 1, sig=(120, 40), wt=(1, .5)); wy = fbm(H, W, seed + 2, sig=(120, 40), wt=(1, .5))
    wx /= wx.std(); wy /= wy.std()
    b = map_coordinates(base, [YY + wy * warp, XX + wx * warp], order=1, mode='reflect')
    t = norm01(b)
    cells = norm01(gaussian_filter(np.abs(fbm(H, W, seed + 5, sig=(14, 5), wt=(1, .4))), 2))
    t = 0.75 * t + 0.25 * (1 - cells)
    vign = np.clip(1 - (((XX - W / 2) / (W * .8)) ** 2 + ((YY - H / 2) / (H * .75)) ** 2), 0, 1) ** .8
    col = ramp(t ** 1.1, [(0, (0.10, 0.02, 0.0)), (.35, (0.55, 0.16, 0.02)), (.6, (0.95, 0.48, 0.08)),
                          (.82, (1.0, 0.76, 0.32)), (1, (1.2, 1.05, 0.8))])
    return col * (0.35 + 0.75 * vign[..., None])


def random_walk(n, seed, x0, y0, box, step=46):
    r = np.random.default_rng(seed)
    pts = [(x0, y0)]
    x, y = x0, y0
    for _ in range(n):
        a = r.uniform(0, 2 * math.pi); L = r.exponential(step)
        x += L * math.cos(a); y += L * math.sin(a)
        if x < box[0] or x > box[2]: x = 2 * (box[0] if x < box[0] else box[2]) - x
        if y < box[1] or y > box[3]: y = 2 * (box[1] if y < box[1] else box[3]) - y
        pts.append((x, y))
    return pts


def trail_layer(pts, ss=2):
    img = Image.new('F', (W * ss, H * ss), 0)
    dr = ImageDraw.Draw(img)
    n = len(pts)
    for i in range(1, n):
        age = (n - i) / n
        v = float(math.exp(-age * 4.0))
        wdt = max(1, int(ss * lerp(1.2, 4.5, v)))
        dr.line([(pts[i - 1][0] * ss, pts[i - 1][1] * ss), (pts[i][0] * ss, pts[i][1] * ss)], fill=v, width=wdt)
    a = np.asarray(img.resize((W, H), Image.BILINEAR), np.float32)
    kinks = np.zeros((H, W), np.float32)
    for i in range(max(1, n - 14), n):      # the last scatterings flash
        x, y = int(pts[i][0]), int(pts[i][1])
        if 0 <= x < W and 0 <= y < H:
            kinks[y, x] = 60 * math.exp(-(n - i) / 5)
    return a, kinks


def shot_trap(hook_text=False):
    rgb = plasma()
    # scattering sites: faint sparks in the fog
    r = np.random.default_rng(9)
    sp = np.zeros((H, W), np.float32)
    sp[r.integers(0, H, 2500), r.integers(0, W, 2500)] = r.uniform(.5, 3, 2500)
    rgb += glow(sp, (1.2, 4), (1, .4))[..., None] * np.array([1, .8, .5])
    pts = random_walk(1400, 21, W / 2, H / 2, (90, 340, W - 90, H - 400), step=34)
    tr, kinks = trail_layer(pts)
    g = tr * 1.4 + glow(tr, (3, 12, 40), (.8, .45, .25)) + glow(kinks, (2, 8, 26), (1, .6, .3))
    rgb += g[..., None] * np.array([1.0, 0.95, 0.85])
    hx, hy = pts[-1]
    core, halo = photon_core(hx, hy, 8, 9)
    rgb += (core + halo * .5)[..., None] * np.array([1, 1, 1])
    img = to_img(rgb)
    if hook_text:
        text(img, ['THIS LIGHT IS'], 300, 92)
        text(img, ['100,000 YEARS OLD.'], 410, 104, col=(255, 236, 200))
        label(img, 'IT STILL HASN\'T LEFT THE SUN', 1560, 38)
    else:
        label(img, 'INSIDE THE SUN', 230, 40)
        text(img, ['YEAR 61,240'], 1500, 112, f=MONO, col=(255, 246, 225))
    footer(img)
    return img


def shot_escape():
    # sun limb across the lower half, black space above; photon bursting out with a flash
    cy = H * 1.55; R = H * 0.98
    d = np.sqrt((XX - W / 2) ** 2 + (YY - cy) ** 2)
    inside = np.clip((R - d) / 6, 0, 1)
    pl = plasma(seed=7, warp=40)
    limb = np.clip((R - d) / 260, 0, 1) ** .6        # limb darkening toward the edge
    rgb = pl * (0.45 + 0.85 * limb[..., None]) * inside[..., None]
    corona = np.exp(-np.clip(d - R, 0, None) / 70) * (1 - inside)
    rgb += (corona * 0.7)[..., None] * np.array([1, .55, .18])
    px, py = W * 0.70, cy - R - 150
    # escape flash ring at the surface
    ring = np.exp(-((np.sqrt((XX - px) ** 2 + (YY - (cy - R)) ** 2) - 120) ** 2) / 300) * 0.8
    rgb += ring[..., None] * np.array([1, .9, .7])
    # motion streak (slow-mo smear) from the surface to the photon
    t = np.clip(((cy - R) - YY) / ((cy - R) - py), 0, 1) * (YY < cy - R) * (YY > py)
    streak = np.exp(-((XX - px) ** 2) / 30) * t ** 2 * 2.5
    rgb += (streak + glow(streak, (6, 24), (.6, .3)))[..., None] * np.array([1, .95, .85])
    core, halo = photon_core(px, py, 12, 10)
    rgb += (core + halo)[..., None] * np.array([1, 1, 1])
    flash = np.exp(-((XX - px) ** 2 + (YY - py) ** 2) / (2 * 420 ** 2)) * 0.5
    rgb += flash[..., None] * np.array([1, .9, .75])
    r = np.random.default_rng(4); st = np.zeros((H, W), np.float32)
    st[r.integers(0, H, 500), r.integers(0, W, 500)] = r.uniform(.2, 1.2, 500)
    rgb += (gaussian_filter(st, .8) * 3 * (1 - inside))[..., None]
    img = to_img(rgb)
    text(img, ['THEN IT ESCAPED.'], 300, 104)
    footer(img)
    return img


def earth_disc(cx, cy, R):
    d = np.sqrt((XX - cx) ** 2 + (YY - cy) ** 2)
    m = np.clip((R - d) / 1.5, 0, 1)
    n = norm01(fbm(H, W, 31, sig=(R * .12, R * .05, R * .02), wt=(1, .5, .3)))
    land = (n > .58).astype(np.float32)
    cloud = np.clip((norm01(fbm(H, W, 32, sig=(R * .08, R * .03), wt=(1, .5))) - .55) * 3, 0, 1)
    col = (np.array([0.05, 0.22, 0.55]) * (1 - land[..., None]) + np.array([0.25, 0.42, 0.18]) * land[..., None])
    col = col * (1 - cloud[..., None]) + cloud[..., None] * 0.95
    # lit from below (the Sun is behind the camera, low)
    nz = np.sqrt(np.clip(1 - (d / R) ** 2, 0, 1)); ny = (YY - cy) / R
    lit = np.clip(0.25 + 0.75 * (0.55 * nz + 0.6 * ny + .2), 0.05, 1.2)
    atm = np.exp(-np.abs(d - R) / (R * .06)) * 0.6
    return col * (m * lit)[..., None] + atm[..., None] * np.array([.35, .6, 1.0])


def shot_fall():
    rgb = np.zeros((H, W, 3), np.float32)
    ex, ey = W / 2, 560
    # star streaks radiating from the destination (warp speed)
    r = np.random.default_rng(12)
    lay = Image.new('F', (W, H), 0); dr = ImageDraw.Draw(lay)
    for _ in range(420):
        a = r.uniform(0, 2 * math.pi); d0 = r.uniform(80, 1500); L = d0 * r.uniform(.15, .45)
        x0, y0 = ex + d0 * math.cos(a), ey + d0 * math.sin(a)
        x1, y1 = ex + (d0 + L) * math.cos(a), ey + (d0 + L) * math.sin(a)
        dr.line([(x0, y0), (x1, y1)], fill=float(r.uniform(.15, .8)), width=2)
    st = np.asarray(lay, np.float32)
    rgb += (st + gaussian_filter(st, 3) * .6)[..., None] * np.array([.8, .88, 1.0])
    # sun glow far below, out of frame
    sg = np.exp(-np.sqrt((XX - W / 2) ** 2 + (YY - (H + 300)) ** 2) / 380) * 2.2
    rgb += sg[..., None] * np.array([1, .6, .2])
    # the beam: one straight line from the Sun to Earth
    py = 1180
    on = (YY > py) & (YY < H)
    beam = np.exp(-((XX - W / 2) ** 2) / 6) * on * 1.4
    rgb += (beam + glow(beam.astype(np.float32), (4, 16, 50), (.7, .35, .2)))[..., None] * np.array([1, .9, .7])
    core, halo = photon_core(W / 2, py, 11, 10)
    rgb += (core + halo * .9)[..., None]
    # faint guide ahead of the photon
    ahead = np.exp(-((XX - W / 2) ** 2) / 2) * ((YY < py) & (YY > ey + 150)) * 0.12
    rgb += ahead[..., None] * np.array([1, .9, .75])
    rgb += earth_disc(ex, ey, 130)
    img = to_img(rgb)
    text(img, ['8 MIN 20 S TO EARTH'], 250, 88)
    label(img, '299,792 KM/S', 360, 40, (190, 215, 255))
    footer(img)
    return img


def shot_eye():
    cx, cy, R = W / 2, H / 2 + 20, 400.0
    dx, dy = XX - cx, YY - cy
    r = np.sqrt(dx * dx + dy * dy) / R; th = np.arctan2(dy, dx)
    rng = np.random.default_rng(5)
    # iris fibres: angular noise, crinkled by radius
    nb = 2048
    f1 = gaussian_filter(rng.standard_normal(nb), 1.2, mode='wrap'); f1 = norm01(f1)
    f2 = gaussian_filter(rng.standard_normal(nb), 4, mode='wrap'); f2 = norm01(f2)
    wob = fbm(H, W, 17, sig=(30, 10), wt=(1, .5)); wob /= wob.std()
    idx = ((th / (2 * np.pi) + .5) * nb + wob * 6 + r * 30).astype(int) % nb
    fib = f1[idx] * .65 + f2[idx] * .35
    pupil = 0.24
    collar = np.exp(-((r - 0.42) ** 2) / 0.004)
    iris_t = np.clip(fib * .8 + .2 * norm01(-wob) - 0.25 * np.clip((r - .75) * 4, 0, 1), 0, 1)
    iris = ramp(iris_t, [(0, (0.06, 0.03, 0.01)), (.4, (0.25, 0.13, 0.04)), (.7, (0.55, 0.35, 0.12)), (1, (0.85, 0.66, 0.35))])
    iris *= (1 - 0.75 * np.clip((r - .88) / .12, 0, 1) ** 1.5)[..., None]        # limbal ring
    iris += collar[..., None] * np.array([.25, .15, .05])
    iris *= np.clip((r - pupil) / .03, 0, 1)[..., None]
    # sclera
    scl = np.array([.86, .82, .80]) * (0.55 + 0.45 * np.clip(1 - (np.abs(dx) / (W * .6)) ** 2, 0, 1))[..., None]
    veins = np.clip(norm01(np.abs(fbm(H, W, 41, sig=(8, 3), wt=(1, .5)))) - .82, 0, 1) * 3 * np.clip(np.abs(dx) / W, 0, 1) * 2
    scl = scl * (1 - veins[..., None] * np.array([0, .6, .6]))
    inI = np.clip((1 - r) * R / 2, 0, 1)[..., None]
    rgb = scl * (1 - inI) + iris * inI
    # eyelids: almond opening
    u = dx / (W * .62)
    top = cy - 520 * np.clip(1 - u ** 2, 0, 1) ** .9 + 40
    bot = cy + 430 * np.clip(1 - u ** 2, 0, 1) ** 1.1 + 10
    open_ = np.clip((YY - top) / 6, 0, 1) * np.clip((bot - YY) / 6, 0, 1)
    shade = np.clip((YY - top) / 120, 0, 1) ** .5        # lid shadow on the eyeball
    skin = ramp(norm01(fbm(H, W, 51, sig=(60, 12), wt=(1, .3))), [(0, (.22, .12, .08)), (1, (.45, .27, .18))])
    rgb = rgb * (shade * open_)[..., None] + skin * (1 - open_)[..., None] * 0.6
    # lashes
    lay = Image.new('F', (W, H), 0); dr = ImageDraw.Draw(lay)
    for i in range(120):
        x = rng.uniform(40, W - 40); uu = (x - cx) / (W * .62)
        y = cy - 520 * max(0, 1 - uu * uu) ** .9 + 40
        L = rng.uniform(60, 140) * max(.3, 1 - abs(uu)); a = -math.pi / 2 + uu * .9 + rng.normal(0, .15)
        dr.line([(x, y), (x + L * math.cos(a) * .6 + uu * 40, y + L * math.sin(a))], fill=1.0, width=3)
    lash = gaussian_filter(np.asarray(lay, np.float32), .7)
    rgb *= (1 - np.clip(lash, 0, 1) * .9)[..., None]
    # Sun reflection (catchlight) + wet highlight
    sx, sy = cx - 150, cy - 170
    core, halo = photon_core(sx, sy, 16, 7)
    rgb += (core + halo * .5)[..., None] * np.array([1, .9, .7]) * open_[..., None]
    # the photon arriving, straight into the pupil
    t = np.clip((YY - (cy - 900)) / (900 - 30), 0, 1) * (YY < cy - 10)
    beam = np.exp(-((XX - (cx + (YY - cy) * -0.18)) ** 2) / 8) * t ** 3 * 1.6
    rgb += (beam + glow(beam.astype(np.float32), (4, 16), (.6, .3)))[..., None] * np.array([1, .95, .85])
    core, halo = photon_core(cx, cy - 10, 9, 8)
    rgb += (core + halo * .6)[..., None]
    img = to_img(rgb)
    text(img, ['AND ENDED IN YOUR EYE.'], 1560, 84)
    footer(img)
    return img


def shot_punch():
    from rig import draw_figure                        # modern stargazer pose (m = 1), from What Andromeda Sees
    hz = 1330
    sky = ramp(np.clip((hz - YY) / hz, 0, 1) ** .7, [(0, (1.0, .55, .18)), (.25, (.85, .30, .14)), (.55, (.30, .10, .18)), (1, (.03, .02, .06))])
    sx, sy = 760, hz - 60
    d = np.sqrt((XX - sx) ** 2 + (YY - sy) ** 2)
    sun = np.clip((95 - d) / 2, 0, 1) * 2.2 + np.exp(-d / 160) * 0.9 + np.exp(-d / 600) * 0.4
    rgb = sky + sun[..., None] * np.array([1, .78, .45])
    ground = (YY > hz + 30 * np.sin(XX / 300) - 20 * np.cos(XX / 130)).astype(np.float32)
    ground = gaussian_filter(ground, 1)
    rgb = rgb * (1 - ground[..., None]) + ground[..., None] * np.array([.03, .02, .03])
    ss = 3
    m = Image.new('L', (W * ss, H * ss), 0)
    draw_figure(ImageDraw.Draw(m), (W - 300) * ss, (hz + 30) * ss, 640 * ss, 1.0, hood=0.0, stone=0.0)
    a = np.asarray(m.resize((W, H), Image.LANCZOS), np.float32) / 255
    a = a[:, ::-1]                                       # face the sun (right)
    rim = np.clip(a - np.roll(a, -4, axis=1), 0, 1)
    rgb = rgb * (1 - a[..., None]) + a[..., None] * np.array([.02, .015, .02]) + rim[..., None] * np.array([1, .6, .25]) * .9
    img = to_img(rgb)
    text(img, ['THE LIGHT YOU SEE WITH'], 260, 80)
    text(img, ['IS OLDER THAN', 'CIVILIZATION.'], 370, 118, col=(255, 222, 160))
    footer(img)
    return img


SHOTS = [('still_01_birth', shot_birth), ('still_02_trap', shot_trap), ('still_03_escape', shot_escape),
         ('still_04_fall', shot_fall), ('still_05_eye', shot_eye), ('still_06_punch', shot_punch),
         ('still_07_alt_hook', lambda: shot_trap(hook_text=True))]

if __name__ == '__main__':
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    only = sys.argv[2:]
    for name, fn in SHOTS:
        if only and not any(o in name for o in only):
            continue
        fn().save(os.path.join(out, name + '.png'))
        print(name, flush=True)
    ims = [Image.open(os.path.join(out, n + '.png')).resize((360, 640), Image.LANCZOS) for n, _ in SHOTS if os.path.exists(os.path.join(out, n + '.png'))]
    sheet = Image.new('RGB', (360 * 4 + 50, 640 * 2 + 30), (14, 14, 18))
    for i, im in enumerate(ims):
        sheet.paste(im, (10 + (i % 4) * 370, 10 + (i // 4) * 650))
    sheet.save(os.path.join(out, 'contact.jpg'), quality=90)
