"""Hero frames v3: GPU shader plates (gl/shots.glsl) + light trails, photon, dust and type composited in numpy.

python3 compose.py OUTDIR [scale] [names...]
"""
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

import hero
from hero import (W, H, XX, YY, px, bloom, bokeh, point, put, footer, smooth, BLACK, MONO, CREAM, GOLDT)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1]


def plate(shot, name):
    path = os.path.join(OUT, f'plate_{name}.png')
    subprocess.run(['node', os.path.join(HERE, 'gl', 'shoot.mjs'), str(shot), path, str(W), str(H)], check=True)
    a = np.asarray(Image.open(path).convert('RGB'), np.float32) / 255
    return a


def screen(base, add):
    """Add light on top of an already tonemapped plate without clipping harshly."""
    add = 1 - np.exp(-np.maximum(add, 0))
    return 1 - (1 - base) * (1 - add)


def to_img(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255 + .5).astype(np.uint8))


def vignette(a, k=.45):
    v = 1 - k * (((XX - W / 2) / (W * .72)) ** 2 + ((YY - H / 2) / (H * .62)) ** 2)
    return a * np.clip(v, 0, 1)[..., None]


def gl_xy(u, v):
    """shader uv (x in [-1,1], y up) -> pixel coords"""
    return (u + 1) * W / 2, H / 2 - v * W / 2


# ---------------------------------------------------------------- trails: long, smooth arcs with sharp scatter turns
def arc_walk(seed, cx, cy, rx, ry, n_arcs=16):
    r = np.random.default_rng(seed)
    x, y = cx, cy
    a = r.uniform(0, 2 * math.pi)
    arcs = []
    for i in range(n_arcs):
        R = px(r.uniform(120, 520)) * r.choice([-1, 1])
        L = px(r.uniform(380, 1100))
        pts = [(x, y)]
        steps = int(L / px(4))
        for s in range(steps):
            ex, ey = (x - cx) / rx, (y - cy) / ry
            if math.hypot(ex, ey) > .92:         # bend back inside
                want = math.atan2(-ey * ry, -ex * rx)
                a += ((want - a + math.pi) % (2 * math.pi) - math.pi) * .08
            a += px(4) / R
            x += px(4) * math.cos(a); y += px(4) * math.sin(a)
            pts.append((x, y))
        arcs.append(pts)
        a += r.uniform(1.3, 2.9) * r.choice([-1, 1])  # the scatter
    return arcs


def draw_arcs(arcs, ss=3):
    """arcs start at the photon (index 0 = newest light), fading as the walk goes back in time."""
    pts = [q for arc in arcs for q in arc]
    img = Image.new('F', (W * ss, H * ss), 0)
    dr = ImageDraw.Draw(img)
    m = len(pts)
    for j in range(1, m):
        age = j / m
        v = math.exp(-age * 2.2)
        w = ss * px(1.2 + 4.0 * v ** 1.5)
        dr.line([(pts[j - 1][0] * ss, pts[j - 1][1] * ss), (pts[j][0] * ss, pts[j][1] * ss)], fill=float(.12 + v), width=max(1, int(w)))
    return np.asarray(img.resize((W, H), Image.LANCZOS), np.float32)


def f_trap():
    base = plate(1, 'trap')
    cx, cy = gl_xy(0, .02)
    arcs = arc_walk(4, cx, cy, px(360), px(470), n_arcs=26)
    L = draw_arcs(arcs)
    light = L[..., None] * np.array([1.0, .95, .85]) * 3.0 + bloom(L * 1.1, (2, 7, 22, 60), (1, .8, .55, .35))[..., None] * np.array([1, .72, .32])
    p = point(cx, cy, 8, 30)
    light += p[..., None] + bloom(p * .2, (8, 30, 90, 260), (1, .8, .6, .45))[..., None] * np.array([1, .7, .3])
    star = (np.exp(-((YY - cy) / px(2.2)) ** 2) * np.exp(-np.abs(XX - cx) / px(240)) +
            np.exp(-((XX - cx) / px(2.2)) ** 2) * np.exp(-np.abs(YY - cy) / px(170)) * .7)
    light += star[..., None] * np.array([1, .9, .7]) * 1.4
    light += bokeh(21, 900, 1.0, 3.0, (1.8, 1.2, .45), power=1)
    light += bokeh(22, 45, 8, 40, (.45, .28, .06))
    a = screen(vignette(base, .5), light)
    img = to_img(a)
    img = put(img, ['YEAR'], 1400, 66, BLACK, (255, 232, 196))
    img = put(img, ['61,240'], 1468, 210, BLACK, CREAM, glow_col=(255, 160, 50))
    return footer(img)


def f_escape():
    base = plate(2, 'escape')
    sx, sy = gl_xy(.10, -2.05 + 1.55 + .005)
    py = sy - px(470)
    tt = np.clip((sy - YY) / (sy - py), 0, 1) * (YY > py) * (YY < sy)
    streak = np.exp(-((XX - sx) / px(2.6)) ** 2) * tt ** 1.6 * 2.6
    light = streak[..., None] * np.array([1, .96, .88]) + bloom(streak * .5, (3, 12, 40), (1, .7, .4))[..., None] * np.array([1, .7, .3])
    p = point(sx, py, 11, 34)
    light += p[..., None] + bloom(p * .2, (10, 40, 140, 380), (1, .8, .6, .5))[..., None] * np.array([1, .72, .32])
    flare = np.exp(-((YY - py) / px(2.6)) ** 2) * np.exp(-np.abs(XX - sx) / px(200)) * 2.2
    flare2 = np.exp(-((YY - sy) / px(4)) ** 2) * np.exp(-np.abs(XX - sx) / px(600)) * 1.6     # the shock along the surface
    light += (flare + flare2)[..., None] * np.array([1, .78, .45])
    # ejecta: sparks flung outward from the break-out
    r = np.random.default_rng(7)
    lay = Image.new('F', (W, H), 0); dr = ImageDraw.Draw(lay)
    for _ in range(320):
        a = r.uniform(math.pi * 1.04, math.pi * 1.96); rad = px(r.uniform(40, 520))
        x0 = sx + math.cos(a) * rad; y0 = sy + math.sin(a) * rad * .8
        L = px(r.uniform(6, 34)) * (1 + rad / px(300))
        dr.line([(x0, y0), (x0 + math.cos(a) * L, y0 + math.sin(a) * L * .8)], fill=float(r.uniform(.2, 1) * math.exp(-rad / px(400))), width=max(1, int(px(2))))
    ej = np.asarray(lay, np.float32)
    light += (ej * 1.5)[..., None] * np.array([1.2, .8, .4]) + bloom(ej * .4, (3, 10), (1, .5))[..., None] * np.array([1, .6, .2])
    a = screen(vignette(base, .3), light)
    img = to_img(a)
    img = put(img, ['THEN IT ESCAPED.'], 260, 112, BLACK, glow_col=(255, 160, 60))
    return footer(img)


def f_eye():
    base = plate(3, 'eye')
    tx, ty = gl_xy(0, 0)
    x0, y0 = tx - px(420), -px(60)
    vx, vy = tx - x0, ty - y0; L = math.hypot(vx, vy); vx /= L; vy /= L
    along = (XX - x0) * vx + (YY - y0) * vy
    perp = np.abs((XX - x0) * vy - (YY - y0) * vx)
    on = smooth(0, px(80), along) * smooth(L + px(2), L - px(40), along)
    core = np.exp(-(perp / px(2.6)) ** 2) * on * (.5 + 1.6 * (along / L) ** 2)
    shaft = np.exp(-(perp / px(46)) ** 2) * on * .16
    light = (core + shaft)[..., None] * np.array([1, .9, .7]) + bloom(core * .4, (3, 12, 40, 110), (1, .7, .45, .3))[..., None] * np.array([1, .68, .28])
    light += bokeh(61, 420, 1, 3.5, (1.4, 1.0, .5), power=1, box=lambda x, y: abs((x - x0) * vy - (y - y0) * vx) < px(90) and y < ty)
    hit = point(tx, ty, 6, 14)
    light += hit[..., None] * np.array([1, .95, .85]) * .6 + bloom(hit * .12, (8, 30, 90), (1, .7, .5))[..., None] * np.array([1, .7, .3])
    a = screen(vignette(base, .4), light)
    img = to_img(a)
    img = put(img, ['AND ENDED IN YOUR EYE.'], 1640, 50, BLACK, (255, 236, 205))
    return footer(img)


def f_punch():
    from rig import draw_figure
    base = plate(4, 'sky')
    hzy = gl_xy(0, -.42)[1]
    sx, sy = gl_xy(.34, -.37)
    # foreground ridge with grass
    prof = hzy + px(260) - px(150) * np.exp(-((XX - W * .28) / px(380)) ** 2) + px(6) * np.sin(XX / px(37))
    fg = smooth(-px(1.5), px(1.5), YY - prof)
    lay = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(lay)
    r = np.random.default_rng(8)
    for _ in range(int(1600 * hero.SC)):
        x = r.uniform(0, W)
        yb = hzy + px(260) - px(150) * math.exp(-((x - W * .28) / px(380)) ** 2) + px(6) * math.sin(x / px(37))
        L = px(r.uniform(8, 50)); a = -math.pi / 2 + r.normal(0, .3)
        dr.line([(x, yb + 3), (x + L * math.cos(a), yb + L * math.sin(a))], fill=255, width=max(1, int(px(1.6))))
    fg = np.maximum(fg, np.asarray(lay, np.float32) / 255)
    ss = 3
    m = Image.new('L', (W * ss, H * ss), 0)
    fx = W * .28
    yfeet = hzy + px(260) - px(150) + px(10)
    draw_figure(ImageDraw.Draw(m), (W - fx) * ss, yfeet * ss, px(640) * ss, 1.0, hood=0.0, stone=0.0)
    fig = np.asarray(m.resize((W, H), Image.LANCZOS), np.float32)[:, ::-1] / 255
    a = np.maximum(fig, fg)
    # rim light on the sun-facing edge + light wrap
    sh = np.roll(a, -int(px(4)), axis=1)
    rim = np.clip(a - sh, 0, 1)
    rim = bloom(rim, (1, 3), (1, .4)) * np.exp(-np.abs(YY - sy) / px(900))
    col = base * (1 - a[..., None]) + a[..., None] * np.array([.012, .008, .01])
    light = rim[..., None] * np.array([1.5, .75, .28]) * 1.6
    light += bokeh(81, 120, 2, 16, (.7, .4, .12), box=lambda x, y: y < hzy + px(40))
    out = screen(vignette(col, .35), light)
    img = to_img(out)
    img = put(img, ['THE LIGHT YOU SEE WITH'], 200, 80, BLACK)
    img = put(img, ['IS OLDER THAN', 'CIVILIZATION.'], 300, 132, BLACK, GOLDT, glow_col=(255, 130, 30))
    return footer(img)


FRAMES = [('hero_1_birth', hero.f_birth), ('hero_2_trap', f_trap), ('hero_3_escape', f_escape),
          ('hero_4_eye', f_eye), ('hero_5_punch', f_punch)]

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    only = sys.argv[3:]
    for name, fn in FRAMES:
        if only and not any(o in name for o in only):
            continue
        fn().save(os.path.join(OUT, name + '.png'))
        print(name, flush=True)
    ims = [Image.open(os.path.join(OUT, n + '.png')).resize((432, 768), Image.LANCZOS) for n, _ in FRAMES if os.path.exists(os.path.join(OUT, n + '.png'))]
    sheet = Image.new('RGB', (442 * len(ims) + 10, 788), (12, 12, 15))
    for i, im in enumerate(ims):
        sheet.paste(im, (10 + i * 442, 10))
    sheet.save(os.path.join(OUT, 'contact.jpg'), quality=90)
