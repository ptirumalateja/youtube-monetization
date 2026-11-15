#!/usr/bin/env python3
"""Starship Flight 15 ship-catch reel renderer (Roadster-flip ref look).

python3 render.py out.mp4 [--frames a:b] [--still t1,t2,...] [--scale 0.5]
Monochrome glowing vehicles, wireframe tower with pink-striped chopsticks,
glossy water floor with reflections, smoke sprites, bloom, Michroma text.
"""
import math, sys, os, subprocess, argparse
import numpy as np
import cairo
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.ndimage import gaussian_filter, zoom

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, 'fonts', 'Michroma-Regular.ttf')
W, H, FPS = 1080, 1920, 30
YF = 1360            # water line
TOWER_X0, TOWER_X1, TOWER_TOP = 640, 780, 770
HINGE_X = 636
ARM_Y = 905
ARM_LEN = 330
SHIP_L = 430
SHIP_X = 440
SS = 0.88
CATCH_Y = ARM_Y + SS * (SHIP_L / 2 - 135)   # ship centre when hanging on the arms
PINK = (1.0, 0.33, 0.45)
RED = (1.0, 0.18, 0.22)

# ---------------------------------------------------------------- helpers
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x

def lerp(a, b, t):
    return a + (b - a) * t

def smooth(t):
    t = clamp(t); return t * t * (3 - 2 * t)

def ease_out(t, p=3):
    t = clamp(t); return 1 - (1 - t) ** p

def ease_in(t, p=2):
    t = clamp(t); return t ** p

def hrand(*k):
    """deterministic hash -> [0,1)"""
    h = 0
    for v in k:
        h = (h * 1000003) ^ int(v * 7919 + 13)
        h &= 0xFFFFFFFF
    h ^= h >> 13; h = (h * 0x5bd1e995) & 0xFFFFFFFF; h ^= h >> 15
    return (h & 0xFFFFFF) / float(0x1000000)

# ---------------------------------------------------------------- timeline
OPEN_END = 2.7
REW_END = 3.5
MONTAGE = [  # (flight, fate, duration)
    (1, 'stack', 1.30), (2, 'ascent', 0.95), (3, 'breakup', 0.85),
    (4, 'splash', 0.75), (5, 'splash', 0.58), (6, 'splash', 0.52),
    (7, 'ascent', 0.50), (8, 'ascent', 0.46), (9, 'breakup', 0.42),
    (10, 'splash', 0.38), (11, 'splash', 0.36),
    (12, 'blur', 0.26), (13, 'blur', 0.26), (14, 'blur', 0.26),
]
_t = REW_END
SEGS = []
for fl, fate, d in MONTAGE:
    SEGS.append((fl, fate, _t, d)); _t += d
FINALE_START = _t          # ~11.25
F_REENTRY = 1.5            # plasma pass
F_FLIP = 0.6
F_DESC = 1.25
CONTACT = FINALE_START + F_REENTRY + F_FLIP + F_DESC
QUIT_T = CONTACT + 1.25
END = CONTACT + 3.0
NFRAMES = int(round(END * FPS))


def segment_at(t):
    if t < OPEN_END: return ('open', None, 0.0, OPEN_END)
    if t < REW_END: return ('rewind', None, OPEN_END, REW_END - OPEN_END)
    for fl, fate, s, d in SEGS:
        if s <= t < s + d: return (fate, fl, s, d)
    return ('finale', 15, FINALE_START, END - FINALE_START)

# ---------------------------------------------------------------- catch motion (shared by open + finale)
def catch_state(u, drop=240):
    """u = seconds relative to contact (negative before). Returns ship pose + arms."""
    # descent: from flip end (u=-F_DESC) at y0 down to CATCH_Y, strongly decelerating
    y0 = CATCH_Y - drop
    if u < 0:
        p = 1 + u / F_DESC
        y = lerp(y0, CATCH_Y - 14, ease_out(p, 2.4))
        ang = 0.0
        plume = 1.0
    else:
        # settle: drop 14px onto the arms and bounce
        y = CATCH_Y - 12 * math.exp(-u * 9) * math.cos(u * 26) if u < 1.5 else CATCH_Y
        ang = 0.012 * math.exp(-u * 3) * math.sin(u * 9)
        plume = clamp(1 - u / 0.22)
    arms = 1 - smooth((u + 0.45) / 0.42)     # 1 open -> 0 closed, closes just before contact
    sway = 0.0
    return dict(x=SHIP_X, y=y, ang=ang, plume=plume, arms=arms)

def flip_state(u, drop=240):
    """u in [0, F_FLIP]: ship rotates belly-first (-90deg) to upright with landing burn igniting"""
    p = u / F_FLIP
    ang = lerp(-math.pi / 2, 0.0, smooth(p) ** 0.9)
    y0 = CATCH_Y - drop
    x = lerp(SHIP_X - 60, SHIP_X, smooth(p))
    y = lerp(y0 - 40, y0, smooth(p))
    plume = clamp(p * 3) * (0.8 + 0.4 * math.exp(-p * 4))
    return dict(x=x, y=y, ang=ang, plume=plume, arms=1.0)

# ---------------------------------------------------------------- drawing: vehicles
def ship_path_body(ctx, L=SHIP_L, Wd=92):
    h = Wd / 2; top = -L / 2; nose = 112
    ctx.move_to(-h, top + nose)
    ctx.curve_to(-h, top + nose * 0.45, -h * 0.45, top, 0, top)
    ctx.curve_to(h * 0.45, top, h, top + nose * 0.45, h, top + nose)
    ctx.line_to(h, L / 2); ctx.line_to(-h, L / 2); ctx.close_path()

def draw_ship(ctx, glow, x, y, ang, s=1.0, plume=0.0, plasma=0.0, t=0.0, lit=1.0, alpha=1.0, pieces=None):
    L = SHIP_L; hw = 46
    for c in (ctx, glow):
        c.save(); c.translate(x, y); c.rotate(ang); c.scale(s, s)
    # plume first (additive, on glow layer)
    if plume > 0.01:
        draw_plume(glow, L / 2 + 14, plume, t, width=58)
    if plasma > 0.01:
        draw_plasma(glow, L, plasma, t)
    ctx.push_group()
    # aft flaps (behind body)
    for sgn in (-1, 1):
        ctx.move_to(sgn * hw, L / 2 - 100); ctx.line_to(sgn * (hw + 34), L / 2 - 74)
        ctx.line_to(sgn * (hw + 36), L / 2 - 6); ctx.line_to(sgn * hw, L / 2 - 2); ctx.close_path()
        ctx.set_source_rgb(0.62 * lit, 0.62 * lit, 0.66 * lit); ctx.fill()
        ctx.move_to(sgn * hw, -L / 2 + 70); ctx.line_to(sgn * (hw + 22), -L / 2 + 92)
        ctx.line_to(sgn * (hw + 24), -L / 2 + 128); ctx.line_to(sgn * hw, -L / 2 + 134); ctx.close_path()
        ctx.fill()
    # body: cylinder shading
    ship_path_body(ctx)
    g = cairo.LinearGradient(-hw, 0, hw, 0)
    g.add_color_stop_rgb(0.00, 0.20 * lit, 0.20 * lit, 0.22 * lit)
    g.add_color_stop_rgb(0.30, 0.30 * lit, 0.30 * lit, 0.33 * lit)   # heat-shield side
    g.add_color_stop_rgb(0.36, 0.80 * lit, 0.80 * lit, 0.83 * lit)
    g.add_color_stop_rgb(0.60, 1.00 * lit, 1.00 * lit, 1.00 * lit)
    g.add_color_stop_rgb(1.00, 0.55 * lit, 0.55 * lit, 0.58 * lit)
    ctx.set_source(g); ctx.fill_preserve()
    ctx.set_line_width(1.6); ctx.set_source_rgba(1, 1, 1, 0.35); ctx.stroke()
    # tile seams on heat shield + ring panel lines
    ctx.set_line_width(1.0)
    for yy in np.arange(-L / 2 + 120, L / 2, 26):
        ctx.move_to(-hw + 2, yy); ctx.line_to(-hw * 0.28, yy)
        ctx.set_source_rgba(0, 0, 0, 0.35); ctx.stroke()
    for yy in np.arange(-L / 2 + 150, L / 2, 64):
        ctx.move_to(-hw * 0.28, yy); ctx.line_to(hw, yy)
        ctx.set_source_rgba(0, 0, 0, 0.16); ctx.stroke()
    # catch pin
    ctx.rectangle(hw - 2, -L / 2 + 132, 9, 8); ctx.set_source_rgb(0.7 * lit, 0.7 * lit, 0.72 * lit); ctx.fill()
    # engines
    for ex in (-24, 0, 24):
        ctx.move_to(ex - 7, L / 2); ctx.line_to(ex + 7, L / 2)
        ctx.line_to(ex + 10, L / 2 + 14); ctx.line_to(ex - 10, L / 2 + 14); ctx.close_path()
        ctx.set_source_rgb(0.35 * lit, 0.35 * lit, 0.38 * lit); ctx.fill()
    ctx.pop_group_to_source(); ctx.paint_with_alpha(alpha)
    # red nav light at the nose (the ref car's tail light)
    nl = glow
    rg = cairo.RadialGradient(0, -L / 2 + 14, 0, 0, -L / 2 + 14, 22)
    rg.add_color_stop_rgba(0, 1, 0.35, 0.4, 0.95 * alpha); rg.add_color_stop_rgba(1, 1, 0.1, 0.15, 0)
    nl.set_source(rg); nl.arc(0, -L / 2 + 14, 22, 0, 2 * math.pi); nl.fill()
    for c in (ctx, glow):
        c.restore()

def draw_booster(ctx, glow, x, y, ang, s, plume, t, ship_on_top=True):
    L = 560; hw = 46
    for c in (ctx, glow):
        c.save(); c.translate(x, y); c.rotate(ang); c.scale(s, s)
    if plume > 0.01:
        draw_plume(glow, L / 2 + 16, plume, t, width=110, length=1.25)
    ctx.rectangle(-hw, -L / 2, 2 * hw, L)
    g = cairo.LinearGradient(-hw, 0, hw, 0)
    g.add_color_stop_rgb(0, 0.42, 0.42, 0.45); g.add_color_stop_rgb(0.55, 0.95, 0.95, 0.97); g.add_color_stop_rgb(1, 0.5, 0.5, 0.53)
    ctx.set_source(g); ctx.fill()
    ctx.set_line_width(1)
    for yy in np.arange(-L / 2 + 60, L / 2, 60):
        ctx.move_to(-hw, yy); ctx.line_to(hw, yy); ctx.set_source_rgba(0, 0, 0, 0.18); ctx.stroke()
    # hot-stage ring
    ctx.rectangle(-hw, -L / 2 - 26, 2 * hw, 26); ctx.set_source_rgb(0.18, 0.18, 0.2); ctx.fill()
    for i in range(6):
        ctx.rectangle(-hw + 6 + i * 15, -L / 2 - 20, 8, 14); ctx.set_source_rgb(0.5, 0.5, 0.52); ctx.fill()
    # grid fins
    for sgn in (-1, 1):
        ctx.rectangle(sgn * hw if sgn > 0 else -hw - 30, -L / 2 + 26, 30, 44)
        ctx.set_source_rgb(0.55, 0.55, 0.58); ctx.fill()
    for ex in range(-36, 37, 12):
        ctx.rectangle(ex - 5, L / 2, 10, 14); ctx.set_source_rgb(0.3, 0.3, 0.32); ctx.fill()
    for c in (ctx, glow):
        c.restore()
    if ship_on_top:
        ox = math.sin(ang) * (L / 2 + 26 + SHIP_L / 2) * s
        oy = -math.cos(ang) * (L / 2 + 26 + SHIP_L / 2) * s
        draw_ship(ctx, glow, x + ox, y + oy, ang, s, 0, 0, t)

def draw_plume(glow, y0, k, t, width=58, length=1.0):
    fl = 0.9 + 0.1 * math.sin(t * 61) + 0.06 * math.sin(t * 37 + 1)
    Lp = (260 + 60 * fl) * k * length
    # wide soft cone (the "headlight beam")
    glow.save()
    glow.move_to(-width * 0.5, y0); glow.line_to(width * 0.5, y0)
    glow.line_to(width * 1.9, y0 + Lp * 2.3); glow.line_to(-width * 1.9, y0 + Lp * 2.3); glow.close_path()
    g = cairo.LinearGradient(0, y0, 0, y0 + Lp * 2.3)
    g.add_color_stop_rgba(0, 0.9, 0.9, 1.0, 0.22 * k); g.add_color_stop_rgba(1, 0.9, 0.9, 1.0, 0.0)
    glow.set_source(g); glow.fill()
    # bright core teardrop
    glow.move_to(-width * 0.42, y0)
    glow.curve_to(-width * 0.55, y0 + Lp * 0.3, -width * 0.18, y0 + Lp * 0.8, 0, y0 + Lp)
    glow.curve_to(width * 0.18, y0 + Lp * 0.8, width * 0.55, y0 + Lp * 0.3, width * 0.42, y0)
    glow.close_path()
    g = cairo.LinearGradient(0, y0, 0, y0 + Lp)
    g.add_color_stop_rgba(0, 1, 1, 1, 1.0 * k); g.add_color_stop_rgba(0.35, 1, 0.92, 0.95, 0.85 * k)
    g.add_color_stop_rgba(1, 1, 0.5, 0.6, 0.0)
    glow.set_source(g); glow.fill()
    # mach diamonds hint
    for i in range(3):
        yy = y0 + Lp * (0.18 + i * 0.17)
        rg = cairo.RadialGradient(0, yy, 0, 0, yy, width * 0.35)
        rg.add_color_stop_rgba(0, 1, 1, 1, 0.55 * k); rg.add_color_stop_rgba(1, 1, 1, 1, 0)
        glow.set_source(rg); glow.arc(0, yy, width * 0.35, 0, 2 * math.pi); glow.fill()
    glow.restore()

def draw_plasma(glow, L, k, t):
    """reentry plasma on the belly (local -x side = heat shield, which faces 'down' when ang=-90)."""
    glow.save()
    for i in range(5):
        off = 18 + i * 16
        rg = cairo.RadialGradient(-46 - off * 0.2, 0, 0, -46 - off * 0.2, 0, L * 0.62 + off)
        a = (0.42 - i * 0.07) * k
        rg.add_color_stop_rgba(0, 1, 0.55, 0.7, a); rg.add_color_stop_rgba(0.5, 1, 0.3, 0.5, a * 0.5)
        rg.add_color_stop_rgba(1, 0.9, 0.2, 0.4, 0)
        glow.save(); glow.scale(0.32, 1.0)
        glow.arc((-46 - off * 0.2) / 0.32, 0, L * 0.62 + off, 0, 2 * math.pi)
        glow.restore(); glow.set_source(rg); glow.fill()
    # bright rim on the shield edge
    glow.rectangle(-52, -L / 2 + 100, 8, L - 100)
    glow.set_source_rgba(1, 0.85, 0.9, 0.8 * k); glow.fill()
    glow.restore()

# ---------------------------------------------------------------- drawing: tower + arms
def draw_tower(ctx, glow):
    x0, x1, top, bot = TOWER_X0, TOWER_X1, TOWER_TOP, YF
    # faint body fill
    ctx.rectangle(x0, top, x1 - x0, bot - top); ctx.set_source_rgba(0.13, 0.13, 0.15, 0.85); ctx.fill()
    ctx.set_line_width(2.2); ctx.set_source_rgba(0.62, 0.62, 0.68, 0.95)
    for xx in (x0, x1):
        ctx.move_to(xx, top); ctx.line_to(xx, bot); ctx.stroke()
    ctx.set_line_width(1.3); ctx.set_source_rgba(0.55, 0.55, 0.6, 0.7)
    step = 70
    y = top
    while y < bot:
        y2 = min(y + step, bot)
        ctx.move_to(x0, y); ctx.line_to(x1, y); ctx.stroke()
        ctx.move_to(x0, y); ctx.line_to(x1, y2); ctx.stroke()
        ctx.move_to(x1, y); ctx.line_to(x0, y2); ctx.stroke()
        y = y2
    # inner rail (depth)
    ctx.set_line_width(1.0); ctx.set_source_rgba(0.5, 0.5, 0.55, 0.45)
    ctx.move_to(x0 + 26, top + 20); ctx.line_to(x0 + 26, bot); ctx.stroke()
    ctx.move_to(x1 + 22, top + 30); ctx.line_to(x1 + 22, bot); ctx.stroke()
    y = top + 30
    while y < bot:
        ctx.move_to(x1, y); ctx.line_to(x1 + 22, y + 16); ctx.stroke(); y += 70
    # crown + lightning mast
    ctx.set_line_width(2.0); ctx.set_source_rgba(0.62, 0.62, 0.68, 0.95)
    ctx.move_to(x0 - 10, top); ctx.line_to(x1 + 30, top); ctx.stroke()
    ctx.move_to(x1 - 30, top); ctx.line_to(x1 - 30, top - 70); ctx.stroke()
    rg = cairo.RadialGradient(x1 - 30, top - 72, 0, x1 - 30, top - 72, 14)
    rg.add_color_stop_rgba(0, 1, 0.25, 0.3, 0.9); rg.add_color_stop_rgba(1, 1, 0.2, 0.3, 0)
    glow.set_source(rg); glow.arc(x1 - 30, top - 72, 14, 0, 2 * math.pi); glow.fill()

def arm_poly(ctx, theta, y, length=ARM_LEN):
    hx = HINGE_X
    c, s = math.cos(theta), math.sin(theta)
    def P(px, py):  # px along arm (negative = left), py across
        return hx + px * c - py * s, y + px * s + py * c
    pts = [P(0, -20), P(-length, -12), P(-length - 10, 0), P(-length, 12), P(0, 20)]
    ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    ctx.close_path()
    return P

def draw_arm(ctx, glow, theta, y, front=True):
    P = arm_poly(ctx, theta, y)
    sh = 1.0 if front else 0.6
    ctx.set_source_rgb(0.62 * sh, 0.62 * sh, 0.66 * sh); ctx.fill()
    # white top line + pink stripe, like the ref track
    ax, ay = P(-6, -9); bx, by = P(-ARM_LEN + 4, -6)
    ctx.set_line_width(3.2); ctx.set_source_rgba(1, 1, 1, 0.9 * sh)
    ctx.move_to(ax, ay); ctx.line_to(bx, by); ctx.stroke()
    ax, ay = P(-6, 4); bx, by = P(-ARM_LEN + 4, 3)
    for c, wdt, a in ((ctx, 3.4, 0.95), (glow, 7, 0.45)):
        c.set_line_width(wdt); c.set_source_rgba(PINK[0], PINK[1], PINK[2], a * sh)
        c.move_to(ax, ay); c.line_to(bx, by); c.stroke()
    # hinge carriage
    ctx.rectangle(HINGE_X - 6, y - 34, 26, 68); ctx.set_source_rgb(0.42 * sh, 0.42 * sh, 0.46 * sh); ctx.fill()

def arm_angles(open_k):
    th = math.radians(17) * open_k
    return th, -th   # back arm tips up, front arm tips down

# ---------------------------------------------------------------- smoke particles
class Smoke:
    def __init__(self):
        self.parts = []   # arrays per emitter

    def burst(self, t0, x, y, n, speed, up, r0, grow, life, bright, seed, spread_x=1.0, dur=0.0, follow=None):
        rng = np.random.default_rng(seed)
        e = dict(t0=t0, n=n, x=x, y=y,
                 te=t0 + rng.random(n) * dur,
                 ang=rng.uniform(-math.pi, math.pi, n),
                 sp=speed * (0.35 + rng.random(n)),
                 up=up * (0.5 + rng.random(n)),
                 r0=r0 * (0.6 + 0.8 * rng.random(n)),
                 grow=grow * (0.6 + 0.8 * rng.random(n)),
                 life=life * (0.6 + 0.8 * rng.random(n)),
                 br=bright * (0.75 + 0.5 * rng.random(n)),
                 sx=spread_x, follow=follow,
                 jx=rng.uniform(-1, 1, n), jy=rng.uniform(-1, 1, n))
        self.parts.append(e)

    def state(self, t):
        out = []
        for e in self.parts:
            dt = t - e['te']
            m = (dt > 0) & (dt < e['life'])
            if not m.any(): continue
            d = dt[m]
            k = 2.2
            disp = (1 - np.exp(-k * d)) / k
            if e['follow'] is not None:
                fx, fy = zip(*[e['follow'](te) for te in e['te'][m]])
                ox, oy = np.array(fx), np.array(fy)
            else:
                ox, oy = e['x'], e['y']
            px = ox + np.cos(e['ang'][m]) * e['sp'][m] * disp * e['sx'] + e['jx'][m] * 6
            py = oy + np.sin(e['ang'][m]) * e['sp'][m] * disp * 0.35 - e['up'][m] * d + e['jy'][m] * 6
            py = np.minimum(py, YF + 10)
            r = e['r0'][m] + e['grow'][m] * np.sqrt(d)
            a = np.clip(1 - d / e['life'][m], 0, 1) ** 1.4 * np.clip(d / 0.06, 0, 1)
            out.append(np.stack([px, py, r, a, e['br'][m]], 1))
        return np.concatenate(out) if out else np.zeros((0, 5))

_SPR = {}
def sprite(r):
    r = int(max(2, r))
    if r not in _SPR:
        yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
        d = np.sqrt(xx * xx + yy * yy) / r
        _SPR[r] = np.clip(1 - d, 0, 1) ** 1.8
    return _SPR[r]

def render_smoke(img, P, scale=0.5):
    """img float HxWx3; composite smoke particles (rendered at half res)."""
    h, w = int(H * scale), int(W * scale)
    acc_a = np.zeros((h, w), np.float32)
    acc_c = np.zeros((h, w), np.float32)
    for px, py, r, a, br in P:
        rr = int(r * scale)
        if rr < 2: continue
        cx, cy = int(px * scale), int(py * scale)
        x0, y0 = cx - rr, cy - rr
        x1, y1 = cx + rr + 1, cy + rr + 1
        if x1 <= 0 or y1 <= 0 or x0 >= w or y0 >= h: continue
        s = sprite(rr) * (a * 0.45)
        sx0, sy0 = max(0, -x0), max(0, -y0)
        sx1, sy1 = s.shape[1] - max(0, x1 - w), s.shape[0] - max(0, y1 - h)
        sub = s[sy0:sy1, sx0:sx1]
        X0, Y0 = max(0, x0), max(0, y0)
        reg = (slice(Y0, Y0 + sub.shape[0]), slice(X0, X0 + sub.shape[1]))
        acc_c[reg] = acc_c[reg] * (1 - sub) + br * sub
        acc_a[reg] = acc_a[reg] * (1 - sub) + sub
    if acc_a.max() <= 0: return img
    A = zoom(acc_a, 1 / scale, order=1)[:H, :W, None]
    C = zoom(acc_c, 1 / scale, order=1)[:H, :W, None]
    col = np.clip(C / np.maximum(A, 1e-4), 0, 1.2)
    return img * (1 - A) + col * A * np.array([0.62, 0.62, 0.66])

# ---------------------------------------------------------------- background
_BG = None
def background():
    """Darker 'moonlit sea' tone (v2, after Teja liked the other version's tone): near-black sky with a
    faint haze so no edge is flat black, a fog band on the horizon, dark sea (glints added per frame)."""
    global _BG
    if _BG is not None: return _BG
    y = np.arange(H, dtype=np.float32)[:, None]
    sky = np.where(y < YF, lerp(0.022, 0.05, (y / YF) ** 2.0), 0)
    flo = np.where(y >= YF, lerp(0.045, 0.02, np.clip((y - YF) / (H - YF), 0, 1) ** 0.6), 0)
    band = 0.06 * np.exp(-((y - YF) / 22.0) ** 2) + 0.045 * np.exp(-((y - YF + 90) / 140.0) ** 2)
    base = (sky + flo + band) * np.ones((1, W), np.float32)
    rng = np.random.default_rng(7)
    n = gaussian_filter(rng.standard_normal((H // 8, W // 8)).astype(np.float32), 9)
    n = zoom(n / (n.std() + 1e-6), 8, order=1)[:H, :W]
    base = base + 0.004 * n + 0.012 * np.clip(n, 0, None) * np.exp(-y / 500.0)
    # fog banks sitting on the horizon (like the other cut's soft grey mounds)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    for cx, cy, rx, ry, a in ((120, YF - 70, 260, 110, 0.05), (520, YF - 40, 300, 80, 0.035), (980, YF - 80, 280, 120, 0.045)):
        base += a * np.exp(-(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2))
    base += 0.03 * np.exp(-(((xx - 560) / 520) ** 2 + ((yy - 950) / 620) ** 2))
    _BG = np.repeat(base[:, :, None], 3, 2) * np.array([1.0, 1.0, 1.03], np.float32)
    return _BG

_GL = None
def sea_glints(t):
    """moving light glints on the sea, wider and brighter toward the camera"""
    global _GL
    if _GL is None:
        r = np.random.default_rng(11)
        _GL = dict(z=r.random(70) ** 0.8, x=r.random(70) * 1400 - 160, ph=r.random(70) * 6.28, sp=r.uniform(4, 14, 70))
    g = _GL
    out = np.zeros((H - YF, W), np.float32)
    hh = H - YF
    for z, x0, ph, sp in zip(g['z'], g['x'], g['ph'], g['sp']):
        cy = 6 + (hh - 6) * z ** 1.5
        a = 25 + 230 * z; b = 1.5 + 10 * z
        cx = (x0 + sp * t * (0.3 + z)) % 1400 - 160
        br = (0.03 + 0.11 * z) * (0.55 + 0.45 * math.sin(t * 1.3 + ph))
        y0, y1 = int(max(0, cy - 3 * b)), int(min(hh, cy + 3 * b + 1))
        x0_, x1_ = int(max(0, cx - 2.5 * a)), int(min(W, cx + 2.5 * a + 1))
        if y1 <= y0 or x1_ <= x0_: continue
        gy = np.exp(-((np.arange(y0, y1) - cy) / b) ** 2)
        gx = np.exp(-((np.arange(x0_, x1_) - cx) / a) ** 2)
        out[y0:y1, x0_:x1_] += br * np.outer(gy, gx)
    return out

# ---------------------------------------------------------------- text
_FONTS = {}
def font(sz):
    if sz not in _FONTS: _FONTS[sz] = ImageFont.truetype(FONT, sz)
    return _FONTS[sz]

def text_w(s, sz, sp):
    f = font(sz)
    return sum(f.getlength(ch) for ch in s) + sp * (len(s) - 1)

def draw_text(d, s, cx, y, sz, fill, sp=4, anchor='c'):
    f = font(sz)
    wt = text_w(s, sz, sp)
    x = cx - wt / 2 if anchor == 'c' else cx
    for ch in s:
        d.text((x, y), ch, font=f, fill=fill)
        x += f.getlength(ch) + sp
    return wt

def overlay_text(t, rew_k=0.0):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    seg = segment_at(t)
    # --- headline
    if t < OPEN_END:
        draw_text(d, 'EVERYONE SAW', W / 2, 318, 64, (255, 255, 255, 255), 4)
        draw_text(d, 'THE CATCH.', W / 2, 404, 64, (255, 255, 255, 255), 4)
        head_bottom = 480
    elif t < QUIT_T:
        draw_text(d, 'EVERYONE SAW THE CATCH.', W / 2, 318, 34, (255, 255, 255, 235), 3)
        k = clamp((t - (OPEN_END + 0.15)) / 0.45)
        line2 = 'NOBODY SAW THE 14 BEFORE IT.'
        n = int(round(len(line2) * k))
        if n:
            draw_text(d, line2[:n], W / 2 - text_w(line2, 34, 3) / 2, 368, 34, (255, 255, 255, 235), 3, anchor='l')
        head_bottom = 420
    else:
        k = clamp((t - QUIT_T) / 0.3)
        a = int(255 * k)
        draw_text(d, 'WHICH FLIGHT', W / 2, 318, 58, (255, 255, 255, a), 4)
        draw_text(d, 'WOULD YOU', W / 2, 396, 58, (255, 255, 255, a), 4)
        draw_text(d, 'HAVE QUIT?', W / 2, 474, 58, (255, 255, 255, a), 4)
        head_bottom = None
    # --- counter
    if head_bottom is not None:
        if seg[0] == 'rewind':
            p = (t - OPEN_END) / (REW_END - OPEN_END)
            num = max(1, int(round(lerp(15, 1, ease_in(p, 0.8)))))
            lab = '<<'
        else:
            num = 15 if seg[0] in ('open', 'finale') else seg[1]
            lab = 'FLIGHT'
        y0 = head_bottom + 28
        lw = text_w(lab, 22, 4)
        nw = text_w(f'{num:02d}', 54, 3)
        tot = lw + 14 + nw
        x = W / 2 - tot / 2
        draw_text(d, lab, x, y0 + 26, 22, (200, 200, 205, 255), 4, anchor='l')
        draw_text(d, f'{num:02d}', x + lw + 14, y0, 54, (255, 255, 255, 255), 3, anchor='l')
        # --- tag
        tag = None
        if seg[0] in ('open', 'finale'):
            tc = CONTACT if seg[0] == 'finale' else OPEN_CATCH
            if t >= tc + 0.08: tag = ('CAUGHT', clamp((t - tc - 0.08) / 0.12))
        elif seg[0] not in ('rewind',):
            fate, fl, s, dd = seg
            fail_at = s + fail_time(fate, dd)
            if t >= fail_at: tag = ('NOT CAUGHT', clamp((t - fail_at) / 0.08))
        if tag:
            txt, k = tag
            ty = y0 + 84
            tw = text_w(txt, 24, 4)
            bx0, bx1 = W / 2 - tw / 2 - 16, W / 2 + tw / 2 + 16
            if txt == 'CAUGHT':
                d.rounded_rectangle([bx0, ty, bx1, ty + 48], 6, fill=(255, 255, 255, int(255 * k)))
                draw_text(d, txt, W / 2, ty + 9, 24, (20, 20, 24, int(255 * k)), 4)
            else:
                col = (255, 70, 85, int(255 * k))
                d.rounded_rectangle([bx0, ty, bx1, ty + 48], 6, outline=col, width=3)
                draw_text(d, txt, W / 2, ty + 9, 24, col, 4)
    # --- 15-cell progress bar (14 misses, then the catch)
    if t >= OPEN_END + 0.25:
        ka = clamp((t - OPEN_END - 0.25) / 0.3)
        by = 606 if head_bottom is not None else 582
        cw, gap, ch = 40, 8, 14
        x0 = W / 2 - (15 * cw + 14 * gap) / 2
        cur = seg[1] if seg[0] not in ('open', 'rewind') else None
        for i in range(15):
            fl = i + 1
            cx = x0 + i * (cw + gap)
            if fl < 15:
                s_, d_ = [(s, dd) for f_, fa, s, dd in SEGS if f_ == fl][0]
                fate_ = [fa for f_, fa, s, dd in SEGS if f_ == fl][0]
                filled = t >= s_ + fail_time(fate_, d_)
                col = (255, 70, 85, int(235 * ka)) if filled else (120, 120, 128, int(110 * ka))
            else:
                filled = t >= CONTACT + 0.08
                col = (255, 255, 255, int(255 * ka)) if filled else (120, 120, 128, int(110 * ka))
            d.rectangle([cx, by, cx + cw, by + ch], fill=col)
            if cur == fl and not filled:
                d.rectangle([cx - 2, by - 2, cx + cw + 2, by + ch + 2], outline=(255, 255, 255, int(220 * ka)), width=2)
    # --- payoff line under the caught ship
    if t >= CONTACT + 0.05:
        k = clamp((t - CONTACT - 0.05) / 0.2)
        draw_text(d, 'UNTIL THIS ONE.', W / 2, 1222, 54, (255, 255, 255, int(255 * k)), 4)
    return im

def fail_time(fate, d):
    return {'stack': 0.78, 'ascent': 0.5, 'breakup': 0.5, 'splash': 0.55, 'blur': 0.35}[fate] * d

OPEN_CATCH = 1.85   # contact time within the opening

# ---------------------------------------------------------------- explosions
def draw_explosion(glow, ctx, x, y, u, size=1.0, seed=1):
    """u = seconds since detonation"""
    if u < 0 or u > 1.6: return
    k = math.exp(-u * 3.2)
    R = size * (60 + 260 * ease_out(u / 0.5, 2))
    rg = cairo.RadialGradient(x, y, 0, x, y, R)
    rg.add_color_stop_rgba(0, 1, 1, 1, 1.0 * k)
    rg.add_color_stop_rgba(0.35, 1, 0.75, 0.8, 0.7 * k)
    rg.add_color_stop_rgba(1, 1, 0.3, 0.4, 0)
    glow.set_source(rg); glow.arc(x, y, R * 0.8, 0, 2 * math.pi); glow.fill()
    for j in range(7):
        aa = hrand(seed, j, 9) * 2 * math.pi
        dd = R * (0.35 + 0.4 * hrand(seed, j, 8))
        lx, ly = x + math.cos(aa) * dd, y + math.sin(aa) * dd - 40 * u
        lr = R * (0.35 + 0.3 * hrand(seed, j, 7))
        rg2 = cairo.RadialGradient(lx, ly, 0, lx, ly, lr)
        rg2.add_color_stop_rgba(0, 1, 0.85, 0.9, 0.75 * k); rg2.add_color_stop_rgba(1, 1, 0.3, 0.4, 0)
        glow.set_source(rg2); glow.arc(lx, ly, lr, 0, 2 * math.pi); glow.fill()
    # shock ring
    if u < 0.5:
        rr = size * 420 * ease_out(u / 0.5, 2)
        glow.set_line_width(3 * (1 - u / 0.5)); glow.set_source_rgba(1, 1, 1, 0.22 * (1 - u / 0.5))
        glow.arc(x, y, rr, 0, 2 * math.pi); glow.stroke()
    # debris sparks with trails
    for i in range(26):
        a = hrand(seed, i) * 2 * math.pi
        sp = size * (250 + 650 * hrand(seed, i, 2))
        g = 600
        def pos(tt):
            dd = (1 - math.exp(-1.8 * tt)) / 1.8
            return x + math.cos(a) * sp * dd, y + math.sin(a) * sp * dd + 0.5 * g * tt * tt
        if u > 1.2: continue
        p1 = pos(u); p0 = pos(max(0, u - 0.09))
        al = clamp(1 - u / 1.2)
        red = hrand(seed, i, 3) < 0.25
        glow.set_line_width(2.6 if i % 3 else 4)
        glow.set_source_rgba(1, 0.3 if red else 1, 0.35 if red else 1, al)
        glow.move_to(*p0); glow.line_to(*p1); glow.stroke()

# ---------------------------------------------------------------- per-segment scene state
def montage_scene(ctx, glow, fate, fl, u, d, t, smoke_events):
    """draw one failed flight; u local time [0,d]"""
    p = u / d
    ft = fail_time(fate, d)
    seed = fl * 17
    if fate == 'stack':
        # full stack climbing, starts to tumble, then explodes high
        ang = 0.25 + (0 if u < 0.3 else 2.4 * ease_in((u - 0.3) / (ft - 0.3), 1.6))
        x = lerp(300, 330, p); y = lerp(1180, 860, p)
        if u < ft:
            draw_booster(ctx, glow, x, y, ang, 0.55, 1.0, t)
        draw_explosion(glow, ctx, 330, 880, u - ft, 1.3, seed)
    elif fate == 'ascent':
        ang = 0.32
        x = lerp(150, 320, p); y = lerp(1200, 760, p)
        ex, ey = lerp(150, 320, ft / d), lerp(1200, 760, ft / d)
        if u < ft:
            draw_ship(ctx, glow, x, y, ang, 0.9, 1.0, 0, t)
        draw_explosion(glow, ctx, ex, ey - 60, u - ft, 1.0, seed)
    elif fate == 'breakup':
        # belly-first plasma pass left->right, breaks into pieces
        x = lerp(-200, 900, p); y = lerp(640, 900, p)
        ang = -math.pi / 2 + 0.12
        if u < ft:
            draw_ship(ctx, glow, x, y, ang, 0.8, 0, 1.0, t)
        else:
            q = u - ft
            bx, by = lerp(-200, 900, ft / d), lerp(640, 900, ft / d)
            for i, (dx, dy, dr) in enumerate(((-120, -60, -3), (0, 0, 2), (150, 80, 5))):
                px = bx + dx * 0.4 + (420 + dx) * q * 1.2
                py = by + dy * 0.4 + (160 + dy) * q + 300 * q * q
                glow.save(); glow.translate(px, py); glow.rotate(dr * q)
                for j in range(4):
                    rg = cairo.RadialGradient(-j * 30, 0, 0, -j * 30, 0, 40 - j * 6)
                    rg.add_color_stop_rgba(0, 1, 0.75, 0.85, 0.9 - j * 0.2); rg.add_color_stop_rgba(1, 1, 0.3, 0.5, 0)
                    glow.set_source(rg); glow.arc(-j * 30, 0, 40, 0, 2 * math.pi); glow.fill()
                glow.restore()
            draw_explosion(glow, ctx, bx, by, q, 0.7, seed)
    elif fate == 'splash':
        # flipped ship comes down into the water beside the open tower and tips over
        sx = 250
        touch = ft
        yb = YF - SHIP_L / 2 * 0.95
        if u < touch:
            q = u / touch
            y = lerp(yb - 520 * (d / 0.75), yb, ease_out(q, 1.6))
            draw_ship(ctx, glow, sx, y, 0.0, 0.95, 1.0, 0, t)
        else:
            q = u - touch
            ang = -ease_in(q / 0.35, 2) * math.pi / 2 * 0.9
            # pivot at the base
            px, py = sx, YF
            cx = px + math.sin(ang) * SHIP_L / 2 * 0.95; cy = py - math.cos(ang) * SHIP_L / 2 * 0.95
            if q < 0.3:
                draw_ship(ctx, glow, cx, cy, ang, 0.95, 0.3, 0, t)
            draw_explosion(glow, ctx, sx - 40, YF - 60, q - 0.12, 0.9, seed)
    elif fate == 'blur':
        y = lerp(300, 1200, p)
        for j in range(6):
            draw_ship(ctx, glow, 300, y - j * 60, 0.0, 0.95, 0.8, 0, t, alpha=0.5 / (j + 1))

def add_montage_smoke(sm):
    for fl, fate, s, d in SEGS:
        ft = s + fail_time(fate, d)
        if fate == 'stack':
            sm.burst(ft, 330, 880, 26, 300, 20, 30, 70, 1.4, 0.75, fl)
        elif fate == 'ascent':
            sm.burst(ft, 280, 860, 18, 260, 10, 26, 60, 1.0, 0.7, fl)
        elif fate == 'breakup':
            sm.burst(ft, 450, 700, 12, 200, 10, 22, 50, 0.8, 0.7, fl)
        elif fate == 'splash':
            sm.burst(ft + 0.08, 220, YF - 20, 30, 420, 60, 30, 90, 1.2, 0.8, fl, spread_x=1.6)
        # engine trail puffs at ground for early ascent
    # opening: base wash when the landing burn hits, and burst at contact
    for base, seed in ((0.0, 101), (FINALE_START + F_REENTRY + F_FLIP, 201)):
        if base == 0.0:
            t0 = 0.0; tc = OPEN_CATCH
        else:
            t0 = base; tc = CONTACT
        sm.burst(t0, SHIP_X, YF - 6, 60, 700, 30, 26, 85, 2.4, 0.85, seed, spread_x=1.8, dur=tc - t0)
        big = 1.0 if base == 0.0 else 1.6
        sm.burst(tc - 0.15, SHIP_X, YF - 10, int(70 * big), 900 * big, 60, 40, 120 * big, 3.5, 0.95, seed + 1, spread_x=2.0, dur=0.25)

SMOKE = Smoke()
add_montage_smoke(SMOKE)

# ---------------------------------------------------------------- frame
def scene_pose(t):
    """returns (kind, info) describing the main ship for open/finale/rewind"""
    seg = segment_at(t)
    kind = seg[0]
    if kind == 'open':
        u = t - OPEN_CATCH
        st = catch_state(u, 200)
        # first 0.5 s: finishing the flip
        if t < 0.55:
            q = t / 0.55
            st['ang'] = lerp(-1.05, 0.0, smooth(q))
            st['x'] = lerp(SHIP_X - 40, SHIP_X, smooth(q))
        return st
    if kind == 'rewind':
        p = (t - OPEN_END) / (REW_END - OPEN_END)
        tt = lerp(OPEN_END, -0.3, ease_in(p, 1.3))
        st = scene_pose(min(max(0.0, tt), OPEN_END - 0.01))
        if tt < 0: st['y'] -= (-tt) * 1800
        st['plume'] = 0.6
        return st
    return None

def finale_pose(t):
    u = t - FINALE_START
    if u < F_REENTRY:
        p = u / F_REENTRY
        x = lerp(-260, SHIP_X - 60, ease_out(p, 2.2))
        y = lerp(690, CATCH_Y - 280, ease_out(p, 2.0))
        return dict(x=x, y=y, ang=-math.pi / 2 + 0.05, plume=0.0, plasma=clamp(1.2 - p * 1.1), arms=1.0)
    u -= F_REENTRY
    if u < F_FLIP:
        st = flip_state(u); st['plasma'] = 0; return st
    st = catch_state(t - CONTACT); st['plasma'] = 0
    return st

def render_frame(fi):
    t = fi / FPS
    seg = segment_at(t)
    kind = seg[0]
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    gsurf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf); glow = cairo.Context(gsurf)
    glow.set_operator(cairo.OPERATOR_ADD)
    # camera: shake on contact, slow push on finale
    shake = 0.0
    for tc, amp in ((OPEN_CATCH, 7), (CONTACT, 12)):
        if 0 <= t - tc < 0.5: shake += amp * math.exp(-(t - tc) * 8)
    for fl, fate, s, d in SEGS:
        q = t - (s + fail_time(fate, d))
        if 0 <= q < 0.3: shake += 6 * math.exp(-q * 12)
    zoomk = 1.0
    if kind == 'finale':
        zoomk = 1.0 + 0.06 * smooth((t - FINALE_START) / (CONTACT - FINALE_START)) + 0.02 * smooth((t - CONTACT) / 2)
    if kind == 'open':
        zoomk = 1.06 - 0.06 * smooth(t / OPEN_END)
    cxz, cyz = 520, 900
    for c in (ctx, glow):
        c.translate(cxz, cyz); c.scale(zoomk, zoomk); c.translate(-cxz, -cyz)
        c.translate(shake * math.sin(t * 91), shake * math.cos(t * 77))

    # ---- arms state
    arms_open = 1.0
    st = None
    if kind in ('open', 'rewind'):
        st = scene_pose(t); arms_open = st['arms']
    elif kind == 'finale':
        st = finale_pose(t); arms_open = st['arms']

    draw_tower(ctx, glow)
    th_b, th_f = arm_angles(arms_open)
    draw_arm(ctx, glow, th_b, ARM_Y, front=False)

    if st is not None:
        draw_ship(ctx, glow, st['x'], st['y'], st['ang'], SS, st['plume'], st.get('plasma', 0), t)
        if st['plume'] > 0.05:
            # ground glow where the plume hits the water
            gy = YF
            k = st['plume'] * clamp(1 - (gy - st['y'] - SS * SHIP_L / 2) / 900)
            rg = cairo.RadialGradient(st['x'], gy, 0, st['x'], gy, 340)
            rg.add_color_stop_rgba(0, 1, 0.95, 0.97, 0.55 * k); rg.add_color_stop_rgba(1, 1, 0.9, 0.95, 0)
            glow.save(); glow.translate(st['x'], gy); glow.scale(1, 0.18); glow.translate(-st['x'], -gy)
            glow.set_source(rg); glow.arc(st['x'], gy, 340, 0, 2 * math.pi); glow.fill(); glow.restore()
    elif kind not in ('open', 'rewind', 'finale'):
        fate, fl, s, d = seg
        montage_scene(ctx, glow, fate, fl, t - s, d, t, None)

    draw_arm(ctx, glow, th_f, ARM_Y, front=True)

    # cheering figures at the base after the finale catch
    if kind == 'finale' and t > CONTACT + 0.5:
        k = clamp((t - CONTACT - 0.5) / 0.3)
        for i, fx in enumerate((880, 922, 964, 1020)):
            wave = math.sin((t - CONTACT) * 9 + i * 1.7)
            draw_figure(ctx, fx, YF - 20, k, wave, i)

    surf.flush(); gsurf.flush()
    A = np.ndarray((H, W, 4), np.uint8, surf.get_data()).astype(np.float32) / 255.0
    G = np.ndarray((H, W, 4), np.uint8, gsurf.get_data()).astype(np.float32) / 255.0
    img = background().copy()
    img[YF:] += sea_glints(t)[:, :, None]
    # subtle drifting haze
    img = img * (1 - A[:, :, 3:4]) + A[:, :, 2::-1][:, :, :3]
    img = render_smoke(img, SMOKE.state(t))
    img = img + G[:, :, 2::-1][:, :, :3] * 0.85

    # reflections on the water
    above = img[2 * YF - H:YF][::-1]
    rows = np.arange(H - YF)
    shift = (np.sin(rows * 0.09 + t * 5.0) * 4 + np.sin(rows * 0.023 - t * 2.1) * 3).astype(int)
    refl = np.empty_like(above)
    for i in range(0, H - YF, 2):
        refl[i:i + 2] = np.roll(above[i:i + 2], shift[i], axis=1)
    fade = (0.42 * np.exp(-rows / 380.0))[:, None, None]
    refl = gaussian_filter(refl, (2.5, 1.2, 0))
    img[YF:] = img[YF:] + np.maximum(refl - background()[2 * YF - H:YF][::-1], 0) * fade

    # rewind glitch
    if kind == 'rewind':
        p = (t - OPEN_END) / (REW_END - OPEN_END)
        rng = np.random.default_rng(fi)
        for _ in range(9):
            y0 = rng.integers(0, H - 80); hh = rng.integers(8, 60)
            img[y0:y0 + hh] = np.roll(img[y0:y0 + hh], rng.integers(-90, 90), axis=1)
        img[::4] *= 0.85
        img = img * 0.92 + 0.04

    # montage cut flashes
    for fl, fate, s, d in SEGS + [(15, 'f', FINALE_START, 0)]:
        q = t - s
        if 0 <= q < 0.07: img = img + 0.12 * (1 - q / 0.07)

    # bloom
    br = np.clip(img - 0.85, 0, None)
    small = br[::4, ::4]
    b1 = gaussian_filter(small, (5, 5, 0)); b2 = gaussian_filter(small, (22, 22, 0))
    bloom = zoom(b1 * 0.5 + b2 * 0.7, (4, 4, 1), order=1)[:H, :W]
    img = img + bloom
    # tone map
    img = 1 - np.exp(-img * 1.35)
    img = img / (1 - math.exp(-1.35))
    # grain
    rng = np.random.default_rng(fi * 31 + 5)
    img = img + rng.normal(0, 0.012, (H // 2, W // 2, 1)).repeat(2, 0).repeat(2, 1)
    out = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    im = Image.fromarray(out, 'RGB')
    txt = overlay_text(t)
    glowt = txt.filter(ImageFilter.GaussianBlur(10))
    im = Image.alpha_composite(im.convert('RGBA'), Image.eval(glowt, lambda v: v // 2))
    im = Image.alpha_composite(im, txt).convert('RGB')
    return np.asarray(im)

def draw_figure(ctx, x, y, k, wave, i):
    """tiny stick person, arms up, lit from the catch."""
    ctx.save(); ctx.translate(x, y); ctx.scale(1.35, 1.35)
    ctx.set_source_rgba(0.85, 0.85, 0.9, k); ctx.set_line_width(4); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.arc(0, -46, 8, 0, 2 * math.pi); ctx.fill()
    ctx.move_to(0, -36); ctx.line_to(0, -6); ctx.stroke()
    ctx.move_to(0, -6); ctx.line_to(-8, 18); ctx.stroke(); ctx.move_to(0, -6); ctx.line_to(8, 18); ctx.stroke()
    a = 0.25 * wave
    ctx.move_to(0, -30); ctx.line_to(-14 + 4 * a, -58 - 4 * a); ctx.stroke()
    ctx.move_to(0, -30); ctx.line_to(14 - 4 * a, -58 + 4 * a); ctx.stroke()
    ctx.restore()

# ---------------------------------------------------------------- main
if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('--still', default=None)
    ap.add_argument('--frames', default=None)
    ap.add_argument('-j', type=int, default=4)
    a = ap.parse_args()
    if a.still:
        ts = [float(x) for x in a.still.split(',')]
        ims = [Image.fromarray(render_frame(int(round(x * FPS)))) for x in ts]
        sw = 360
        sh = int(sw * H / W)
        sheet = Image.new('RGB', (sw * len(ims), sh))
        for i, im in enumerate(ims):
            sheet.paste(im.resize((sw, sh), Image.LANCZOS), (i * sw, 0))
        sheet.save(a.out, quality=90)
        if len(ims) == 1: ims[0].save(a.out.replace('.jpg', '_full.png'))
        sys.exit()
    f0, f1 = 0, NFRAMES
    if a.frames:
        f0, f1 = map(int, a.frames.split(':'))
    from multiprocessing import Pool
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                           '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
                           '-pix_fmt', 'yuv420p', a.out], stdin=subprocess.PIPE)
    with Pool(a.j) as pool:
        for i, fr in enumerate(pool.imap(render_frame, range(f0, f1), chunksize=2)):
            ff.stdin.write(fr.tobytes())
            if i % 30 == 0: print('frame', f0 + i, '/', f1, flush=True)
    ff.stdin.close(); ff.wait()
    print('done', NFRAMES, 'frames', END, 's')
