"""The Photon That Made Your Eye: the 12 s motion renderer.

    python3 anim.py plates OUTDIR        # writes OUTDIR/jobs.json and renders the shader plates (headless Chromium)
    python3 anim.py frames OUTDIR [a b]  # composites frames a..b-1 (default all) to OUTDIR/frames/f%04d.png
    python3 anim.py events OUTDIR        # writes OUTDIR/events.json (sound cue times)

Timeline (s): 0-1.5 birth | 1.5-6.0 trap | 6.0-8.0 escape | 8.0-10.0 eye | 10.0-12.0 punch, then back to frame 0.
Light is the transition: the dot becomes the photon, the photon bursts into the escape, the beam lands in the eye,
the pupil swallows the frame and the sunset rises out of it; the sun sets back into the frame-0 dot.
"""
import json
import math
import os
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter

import hero
from hero import W, H, XX, YY, put, footer, smooth, BLACK, CREAM, GOLDT, MONO

HERE = os.path.dirname(os.path.abspath(__file__))
FPS, DUR = 30, 12.0
NF = int(FPS * DUR)
T_TRAP, T_ESC, T_EYE, T_PUNCH = 1.5, 6.0, 8.0, 10.0
TRAP_W, TRAP_H = 720, 1280          # the fog is soft; rendered smaller and upscaled
YEARS = 100_000


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def ease_in(x):
    x = min(max(x, 0.0), 1.0)
    return x ** 3


def to_uv(x, y):
    return (x - W / 2) / (W / 2), (H / 2 - y) / (W / 2)


def to_px(u, v):
    return u * W / 2 + W / 2, H / 2 - v * W / 2


# ---------------------------------------------------------------- fast light helpers
def fbloom(L, sig=(2, 7, 22, 70, 180), wt=(1, .8, .55, .35, .25)):
    out = np.zeros_like(L)
    small = None
    for s, k in zip(sig, wt):
        if s < 10:
            out += k * gaussian_filter(L, s)
        else:
            if small is None:
                small = np.asarray(Image.fromarray(L).resize((W // 4, H // 4), Image.BILINEAR), np.float32)
            b = gaussian_filter(small, s / 4)
            out += k * np.asarray(Image.fromarray(b).resize((W, H), Image.BILINEAR), np.float32)
    return out


def point(cx, cy, r, hot):
    d2 = (XX - cx) ** 2 + (YY - cy) ** 2
    return np.exp(-d2 / (2 * r * r)) * hot + r * r / (d2 + r * r) * hot * .12


WARM = np.array([1.0, .92, .78], np.float32)


def flash(a, k):
    return a + (WARM - a) * k


def screen(base, add):
    add = 1 - np.exp(-np.maximum(add, 0))
    return 1 - (1 - base) * (1 - add)


def vignette(a, k=.45):
    v = 1 - k * (((XX - W / 2) / (W * .72)) ** 2 + ((YY - H / 2) / (H * .62)) ** 2)
    return a * np.clip(v, 0, 1)[..., None]


def zoom_img(a, z, cx=W / 2, cy=H / 2):
    """Scale an HxWx3 float image about (cx, cy) by z >= 1."""
    if abs(z - 1) < 1e-4:
        return a
    img = Image.fromarray((np.clip(a, 0, 1) * 65535).astype(np.uint16)[..., 0]) if False else None
    w2, h2 = W / z, H / z
    box = (cx - w2 * cx / W, cy - h2 * cy / H, cx - w2 * cx / W + w2, cy - h2 * cy / H + h2)
    out = np.empty_like(a)
    for c in range(3):
        ch = Image.fromarray(a[..., c].astype(np.float32))
        out[..., c] = np.asarray(ch.resize((W, H), Image.BICUBIC, box=box), np.float32)
    return out


# ---------------------------------------------------------------- dust (bokeh) that drifts
def dust_field(seed, n, rmin, rmax, col, power=2.2, pad=200):
    r = np.random.default_rng(seed)
    lay = Image.new('F', (W + 2 * pad, H + 2 * pad), 0)
    dr = ImageDraw.Draw(lay)
    for _ in range(n):
        u = r.random() ** power
        rad = rmin + (rmax - rmin) * u
        x = r.uniform(0, W + 2 * pad); y = r.uniform(0, H + 2 * pad)
        dr.ellipse([x - rad, y - rad, x + rad, y + rad], fill=float(r.uniform(.25, 1) * (1.15 - .85 * u)))
    a = gaussian_filter(np.asarray(lay, np.float32), 1.5)
    return a, np.array(col, np.float32), pad


def dust_at(field, dx, dy):
    a, col, pad = field
    ox = int(round(pad + dx)) % (2 * pad) if pad else 0
    oy = int(round(pad + dy)) % (2 * pad) if pad else 0
    return a[oy:oy + H, ox:ox + W][..., None] * col


# ---------------------------------------------------------------- the photon's random walk (world uv coords)
def arc_walk(seed=4, n_arcs=26, rx=360, ry=470):
    r = np.random.default_rng(seed)
    cx, cy = W / 2, H / 2
    x, y = cx, cy
    a = r.uniform(0, 2 * math.pi)
    pts, scat = [(x, y)], []
    for i in range(n_arcs):
        R = r.uniform(120, 520) * r.choice([-1, 1])
        L = r.uniform(380, 1100)
        for s in range(int(L / 4)):
            ex, ey = (x - cx) / rx, (y - cy) / ry
            if math.hypot(ex, ey) > .92:
                want = math.atan2(-ey * ry, -ex * rx)
                a += ((want - a + math.pi) % (2 * math.pi) - math.pi) * .08
            a += 4 / R
            x += 4 * math.cos(a); y += 4 * math.sin(a)
            pts.append((x, y))
        scat.append(len(pts) - 1)
        a += r.uniform(1.3, 2.9) * r.choice([-1, 1])
    uv = np.array([to_uv(px_, py_) for px_, py_ in pts], np.float32)
    return uv, scat[:-1]


WALK, SCAT = arc_walk()


def head_index(t):
    u = (t - T_TRAP - .15) / (T_ESC - T_TRAP - .15)
    return int(np.clip(u, 0, 1) * (len(WALK) - 1))


def trap_cam(t):
    lt = t - T_TRAP
    zz = 1 + 7 * (1 - ease_out(lt / .5)) + .08 * ease(lt / 4.5)        # rush back out of the dot, then a slow push
    roll = .035 * lt + .26 * ease((lt - 2.6) / .6)                      # the 4.3 s mini rehook: a 15 degree roll
    return zz, roll


def world_to_screen(uv, zz, roll):
    c, s = math.cos(-roll), math.sin(-roll)
    u = (uv[..., 0] * c - uv[..., 1] * s) * zz
    v = (uv[..., 0] * s + uv[..., 1] * c) * zz
    return to_px(u, v)


def year_at(t):
    u = (t - (T_TRAP + .2)) / (T_ESC - .15 - (T_TRAP + .2))
    u = min(max(u, 0), 1)
    return max(1, int(round(YEARS * u ** 1.35)))


# ---------------------------------------------------------------- plates
def plate_jobs(out):
    jobs = []
    pd = os.path.join(out, 'plates'); os.makedirs(pd, exist_ok=True)
    for f in range(NF):
        t = f / FPS
        if T_TRAP - 1 / FPS < t < T_ESC:
            zz, roll = trap_cam(t)
            hu, hv = WALK[head_index(t)]
            jobs.append(dict(shot=1, out=f'{pd}/p{f:04d}.png', w=TRAP_W, h=TRAP_H, u=dict(uT=t - T_TRAP, uZ=zz, uR=roll, uPX=float(hu), uPY=float(hv))))
        elif T_ESC <= t < T_EYE:
            jobs.append(dict(shot=2, out=f'{pd}/p{f:04d}.png', w=W, h=H, u=dict(uT=t - T_ESC)))
        elif T_EYE <= t < T_PUNCH:
            lt = t - T_EYE
            jobs.append(dict(shot=3, out=f'{pd}/p{f:04d}.png', w=W, h=H, u=dict(uT=lt, uZ=eye_zoom(t), uA=pupil(t))))
        elif t >= T_PUNCH:
            jobs.append(dict(shot=4, out=f'{pd}/p{f:04d}.png', w=W, h=H, u=dict(uT=t - T_PUNCH)))
    return jobs


def eye_zoom(t):
    lt = t - T_EYE
    return 1 + .06 * ease(lt / 1.55) + 8 * ease_in((lt - 1.55) / .45)


def pupil(t):
    return .27 - .05 * ease_out((t - (T_EYE + .25)) / .35)


def load_plate(out, f, size=None):
    im = Image.open(os.path.join(out, 'plates', f'p{f:04d}.png')).convert('RGB')
    if im.size != (W, H):
        im = im.resize((W, H), Image.BICUBIC)
    return np.asarray(im, np.float32) / 255


# ---------------------------------------------------------------- shots
DUST_FINE = DUST_BIG = None


def dusts():
    global DUST_FINE, DUST_BIG, DUST_BIRTH, DUST_SKY
    if DUST_FINE is None:
        DUST_FINE = dust_field(21, 1100, 1.0, 3.0, (1.8, 1.2, .45), power=1)
        DUST_BIG = dust_field(22, 55, 8, 40, (.45, .28, .06))
        DUST_BIRTH = dust_field(3, 70, 3, 20, (.5, .3, .08))
        DUST_SKY = dust_field(81, 140, 2, 14, (.7, .4, .12))


def text_layer(img, f_texts):
    for fn in f_texts:
        img = fn(img)
    return img


def birth(t, base=None):
    """0-1.5 s, and the last frames of the loop. The dot breathes; at the end it swells into the trap."""
    dusts()
    rgb = np.zeros((H, W, 3), np.float32) if base is None else base
    cx, cy = W / 2, H * .44
    br = 1 + .14 * math.sin(2 * math.pi * 1.4 * t)
    swell = ease_in((t - 1.2) / .3) if t < T_TRAP else 0
    hot = 14 * br * (1 + 6 * swell)
    p = point(cx, cy, 7 * (1 + 10 * swell), hot)
    fl = 330 * br * (1 + 2 * swell)
    streak = np.exp(-((YY - cy) / 3) ** 2) * np.exp(-np.abs(XX - cx) / fl) * 1.2 * br
    vst = np.exp(-((XX - cx) / 2.5) ** 2) * np.exp(-np.abs(YY - cy) / (120 * br)) * .5
    L = p + streak + vst
    light = L[..., None] * np.array([1, .95, .85]) + fbloom(p * .2, (20, 60, 160), (.5, .5, .4))[..., None] * np.array([1, .55, .15])
    light += dust_at(DUST_BIRTH, -t * 22, -t * 30)
    a = screen(rgb, light)
    a = flash(a, swell * .9)
    return a


def trap(out, f, t):
    dusts()
    lt = t - T_TRAP
    base = vignette(load_plate(out, f), .5)
    zz, roll = trap_cam(t)
    hi = head_index(t)
    sx, sy = world_to_screen(WALK[:hi + 1], zz, roll)
    # trails, drawn up to the head: recent light bright, the old tangle faint
    ss = 2
    img = Image.new('F', (W * ss, H * ss), 0)
    dr = ImageDraw.Draw(img)
    step = 2
    for j in range(max(1, hi % step), hi + 1, step):
        back = (hi - j) / 2200.0
        v = math.exp(-back * 2.2)
        w = ss * (1.2 + 4.0 * v ** 1.5) * min(zz, 3) ** .5
        dr.line([(sx[j - step] * ss if j >= step else sx[0] * ss, sy[j - step] * ss if j >= step else sy[0] * ss), (sx[j] * ss, sy[j] * ss)],
                fill=float(.14 + v), width=max(1, int(w)))
    L = np.asarray(img.resize((W, H), Image.BILINEAR), np.float32)
    light = L[..., None] * np.array([1.0, .95, .85]) * 3.0 + fbloom(L * 1.1, (2, 7, 22, 60), (1, .8, .55, .35))[..., None] * np.array([1, .72, .32])
    hx, hy = sx[-1], sy[-1]
    # scatter flashes: a tiny pop at each recent kink
    for k in SCAT:
        if k <= hi and hi - k < 260:
            fade = math.exp(-(hi - k) / 70)
            kx, ky = world_to_screen(WALK[k:k + 1], zz, roll)
            light += point(float(kx[0]), float(ky[0]), 5, 6 * fade)[..., None] * np.array([1, .9, .7])
    burst = ease_in((t - (T_ESC - .3)) / .3)                       # the photon bursts at the cut
    p = point(hx, hy, 8 * (1 + 8 * burst), 30 * (1 + 3 * burst))
    light += p[..., None] + fbloom(p * .2, (8, 30, 90, 260), (1, .8, .6, .45))[..., None] * np.array([1, .7, .3])
    sl = 240 * (1 + 2 * burst)
    star = (np.exp(-((YY - hy) / 2.2) ** 2) * np.exp(-np.abs(XX - hx) / sl) + np.exp(-((XX - hx) / 2.2) ** 2) * np.exp(-np.abs(YY - hy) / (sl * .7)) * .7)
    light += star[..., None] * np.array([1, .9, .7]) * 1.4
    light += dust_at(DUST_FINE, -lt * 40, -lt * 26) + dust_at(DUST_BIG, lt * 18, -lt * 12)
    a = screen(base, light)
    flash_in = math.exp(-lt / .12) * .95                             # arriving out of the swollen dot
    a = flash(a, flash_in)
    a = flash(a, burst * .9)
    img = Image.fromarray((np.clip(a, 0, 1) * 255 + .5).astype(np.uint8))
    al = ease((lt - .2) / .25) * (1 - ease((t - (T_ESC - .25)) / .2))
    if al > .01:
        y = year_at(t)
        img = put_alpha(img, lambda im: put(put(im, ['YEAR'], 1478, 40, BLACK, (255, 232, 196)), [f'{y:,}'], 1522, 126, BLACK, CREAM, glow_col=(255, 160, 50)), al)
    return img


def put_alpha(img, fn, al):
    if al >= .999:
        return fn(img)
    return Image.blend(img, fn(img), al)


ESC_SP = to_px(.10, -2.05 + 1.55 + .005)


def escape(out, f, t):
    lt = t - T_ESC
    z = 1 + .12 * ease(lt / 2)
    base = vignette(load_plate(out, f), .3)
    sx, sy = ESC_SP
    py = sy - (sy - 560) * ease_out(lt / 1.6)                    # rises in slow motion, stays clear of the text
    tt = np.clip((sy - YY) / max(sy - py, 1), 0, 1) * (YY > py) * (YY < sy)
    streak = np.exp(-((XX - sx) / 2.6) ** 2) * tt ** 1.6 * 2.6
    light = streak[..., None] * np.array([1, .96, .88]) + fbloom(streak * .5, (3, 12, 40), (1, .7, .4))[..., None] * np.array([1, .7, .3])
    beam = ease_in((t - (T_EYE - .25)) / .25)                      # the beam flares into the next shot
    p = point(sx, py, 11 * (1 + 5 * beam), 34 * (1 + 2 * beam))
    light += p[..., None] + fbloom(p * .2, (10, 40, 140, 380), (1, .8, .6, .5))[..., None] * np.array([1, .72, .32])
    flare = np.exp(-((YY - py) / 2.6) ** 2) * np.exp(-np.abs(XX - sx) / (200 * (1 + 3 * beam))) * 2.2
    flare2 = np.exp(-((YY - sy) / 4) ** 2) * np.exp(-np.abs(XX - sx) / (150 + 450 * ease_out(lt / 1.2))) * 1.6
    light += (flare + flare2)[..., None] * np.array([1, .78, .45])
    # ejecta flung outward
    r = np.random.default_rng(7)
    lay = Image.new('F', (W, H), 0); dr = ImageDraw.Draw(lay)
    for _ in range(320):
        a = r.uniform(math.pi * 1.04, math.pi * 1.96); rad0 = r.uniform(10, 300); spd = r.uniform(150, 520)
        rad = rad0 + spd * lt
        x0 = sx + math.cos(a) * rad; y0 = sy + math.sin(a) * rad * .8
        L = r.uniform(6, 34) * (1 + rad / 300)
        dr.line([(x0, y0), (x0 + math.cos(a) * L, y0 + math.sin(a) * L * .8)], fill=float(r.uniform(.2, 1) * math.exp(-rad / 420)), width=2)
    ej = np.asarray(lay, np.float32)
    light += (ej * 1.5)[..., None] * np.array([1.2, .8, .4]) + fbloom(ej * .4, (3, 10), (1, .5))[..., None] * np.array([1, .6, .2])
    a = screen(base, light)
    a = zoom_img(a, z, sx, sy)
    a = flash(a, min(1, math.exp(-lt / .14) * .95 + beam * .95))
    img = Image.fromarray((np.clip(a, 0, 1) * 255 + .5).astype(np.uint8))
    al = ease((lt - .1) / .2) * (1 - ease((t - (T_EYE - .3)) / .15))
    if al > .01:
        img = put_alpha(img, lambda im: put(im, ['THEN IT ESCAPED.'], 270, 94, BLACK, glow_col=(255, 160, 60)), al)
    return img


def eye(out, f, t):
    dusts()
    lt = t - T_EYE
    base = vignette(load_plate(out, f), .4)
    zz = eye_zoom(t)
    tx, ty = W / 2, H / 2
    x0, y0 = tx - 420 * zz ** .3, -60
    vx, vy = tx - x0, ty - y0; Lb = math.hypot(vx, vy); vx /= Lb; vy /= Lb
    head = ease_out(lt / .25) * Lb                                  # the beam arrives, then holds
    along = (XX - x0) * vx + (YY - y0) * vy
    perp = np.abs((XX - x0) * vy - (YY - y0) * vx)
    flick = 1 + .10 * math.sin(lt * 41) + .06 * math.sin(lt * 67 + 1)
    gone = 1 - ease((lt - 1.5) / .25)
    on = smooth(0, 80, along) * smooth(head + 2, head - 40, along) * gone
    core = np.exp(-(perp / 2.6) ** 2) * on * (.5 + 1.6 * (along / Lb) ** 2) * flick
    shaft = np.exp(-(perp / 46) ** 2) * on * .16 * flick
    light = (core + shaft)[..., None] * np.array([1, .9, .7]) + fbloom(core * .4, (3, 12, 40, 110), (1, .7, .45, .3))[..., None] * np.array([1, .68, .28])
    d = dust_at(DUST_FINE, lt * 30, lt * 50) * (np.exp(-(perp / 90) ** 2) * on)[..., None] * .8
    light += d
    hitk = ease((lt - .22) / .06) * math.exp(-max(0, lt - .28) / .5) * gone
    hit = point(tx, ty, 6, 14 * (.4 + 1.6 * hitk))
    light += hit[..., None] * np.array([1, .95, .85]) * .6 * gone + fbloom(hit * .12, (8, 30, 90), (1, .7, .5))[..., None] * np.array([1, .7, .3]) * gone
    a = screen(base, light)
    a = flash(a, math.exp(-lt / .14) * .95)                          # out of the escape's flare
    img = Image.fromarray((np.clip(a, 0, 1) * 255 + .5).astype(np.uint8))
    al = ease((lt - .3) / .2) * (1 - ease((lt - 1.45) / .15))
    if al > .01:
        img = put_alpha(img, lambda im: put(im, ['AND ENDED IN YOUR EYE.'], 1640, 50, BLACK, (255, 236, 205)), al)
    return img


GRASS = None


def grass_blades():
    global GRASS
    if GRASS is None:
        r = np.random.default_rng(8)
        GRASS = [(r.uniform(0, W), r.uniform(8, 50), r.normal(0, .3), r.uniform(0, 6.28)) for _ in range(1600)]
    return GRASS


PUNCH_STATIC = None


def punch_static():
    global PUNCH_STATIC
    if PUNCH_STATIC is None:
        from rig import draw_figure
        hzy = to_px(0, -.42)[1]
        prof = hzy + 260 - 150 * np.exp(-((XX - W * .28) / 380) ** 2) + 6 * np.sin(XX / 37)
        fg = smooth(-1.5, 1.5, YY - prof)
        ss = 3
        m = Image.new('L', (W * ss, H * ss), 0)
        fx = W * .28
        yfeet = hzy + 260 - 150 + 10
        draw_figure(ImageDraw.Draw(m), (W - fx) * ss, yfeet * ss, 640 * ss, 1.0, hood=0.0, stone=0.0)
        fig = np.asarray(m.resize((W, H), Image.LANCZOS), np.float32)[:, ::-1] / 255
        PUNCH_STATIC = (hzy, np.maximum(fig, fg))
    return PUNCH_STATIC


def punch(out, f, t):
    dusts()
    lt = t - T_PUNCH
    base = load_plate(out, f)
    hzy, solid = punch_static()
    sx, sy = to_px(.34, -.37 - lt * .012)
    lay = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(lay)
    for x, L, a0, ph in grass_blades():
        yb = hzy + 260 - 150 * math.exp(-((x - W * .28) / 380) ** 2) + 6 * math.sin(x / 37)
        a = -math.pi / 2 + a0 + .10 * math.sin(lt * 2.2 + ph + x / 160)
        dr.line([(x, yb + 3), (x + L * math.cos(a), yb + L * math.sin(a))], fill=255, width=2)
    a = np.maximum(solid, np.asarray(lay, np.float32) / 255)
    sh = np.roll(a, -4, axis=1)
    rim = np.clip(a - sh, 0, 1)
    rim = fbloom(rim, (1, 3), (1, .4)) * np.exp(-np.abs(YY - sy) / 900)
    col = base * (1 - a[..., None]) + a[..., None] * np.array([.012, .008, .01])
    light = rim[..., None] * np.array([1.5, .75, .28]) * 1.6
    light += dust_at(DUST_SKY, -lt * 14, -lt * 20) * (YY < hzy + 40)[..., None]
    out_ = screen(vignette(col, .35), light)
    # rise out of the pupil's black, and set back into the frame-0 dot
    rise = ease((lt - .02) / .4)
    fall = ease((t - 11.45) / .4)
    out_ = out_ * rise * (1 - fall)
    img = Image.fromarray((np.clip(out_, 0, 1) * 255 + .5).astype(np.uint8))
    a1 = ease((lt - .15) / .2) * (1 - ease((t - 11.35) / .2))
    a2 = ease((lt - .40) / .2) * (1 - ease((t - 11.35) / .2))
    if a1 > .01:
        img = put_alpha(img, lambda im: put(im, ['THE LIGHT YOU SEE WITH'], 210, 68, BLACK), a1)
    if a2 > .01:
        img = put_alpha(img, lambda im: put(im, ['IS OLDER THAN', 'CIVILIZATION.'], 296, 112, BLACK, GOLDT, glow_col=(255, 130, 30)), a2)
    if t > 11.75:                                                   # the frame-0 dot ignites again
        k = ease((t - 11.75) / .2)
        b = birth(0.0) * k
        img = Image.fromarray((np.clip(np.maximum(np.asarray(img, np.float32) / 255, b), 0, 1) * 255 + .5).astype(np.uint8))
    return img


def frame(args):
    out, f = args
    path = os.path.join(out, 'frames', f'f{f:04d}.png')
    if os.path.exists(path):
        return
    t = f / FPS
    if t < T_TRAP:
        a = birth(t)
        img = Image.fromarray((np.clip(a, 0, 1) * 255 + .5).astype(np.uint8))
        al = 1 - ease((t - 1.25) / .2)
        if al > .01:
            img = put_alpha(img, lambda im: put(put(im, ['THIS LIGHT WAS MADE'], 1160, 76, BLACK),
                                                   [[('100,000', GOLDT), (' YEARS AGO', CREAM)]], 1252, 76, BLACK, glow_col=(255, 150, 40)), al)
    elif t < T_ESC:
        img = trap(out, f, t)
    elif t < T_EYE:
        img = escape(out, f, t)
    elif t < T_PUNCH:
        img = eye(out, f, t)
    else:
        img = punch(out, f, t)
    img = footer(img)
    img.save(path + '.tmp.png')
    os.replace(path + '.tmp.png', path)


def events():
    ev = {'scatter': [], 'year_end': T_ESC - .15}
    for k in SCAT:
        # invert head_index
        u = k / (len(WALK) - 1)
        ev['scatter'].append(round(T_TRAP + .15 + u * (T_ESC - T_TRAP - .15), 3))
    ev['cuts'] = dict(trap=T_TRAP, escape=T_ESC, eye=T_EYE, punch=T_PUNCH)
    ev['beam_hit'] = T_EYE + .25
    ev['text'] = dict(escape=T_ESC + .1, eye=T_EYE + .3, punch1=T_PUNCH + .15, punch2=T_PUNCH + .4)
    return ev


if __name__ == '__main__':
    mode, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    if mode == 'plates':
        jobs = plate_jobs(out)
        jp = os.path.join(out, 'jobs.json')
        json.dump(jobs, open(jp, 'w'))
        subprocess.run(['node', os.path.join(HERE, 'gl', 'render.mjs'), jp], check=True)
    elif mode == 'frames':
        os.makedirs(os.path.join(out, 'frames'), exist_ok=True)
        a = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        b = int(sys.argv[4]) if len(sys.argv) > 4 else NF
        with Pool(int(os.environ.get('PROCS', 4))) as pool:
            for _ in pool.imap_unordered(frame, [(out, f) for f in range(a, b)]):
                pass
    elif mode == 'events':
        json.dump(events(), open(os.path.join(out, 'events.json'), 'w'), indent=1)
