#!/usr/bin/env python3
"""'Mom's hotspot' (12 s, 1080x1920): 2 AM, Mom wakes the kid ("NO INTERNET!"), he turns on his hotspot, the signal crosses the city and the planet, Mom's video starts BUFFERING, his battery hits 1%.
Navy + gold theme, glowing cream stick figures, safe zones (15% top / 20% bottom). SFX only. Own characters, own wording.
usage: render_mom.py sheet OUT.png t... | frames OUTDIR | video OUT.mp4 AUDIO.wav FRAMESDIR"""
import sys, os, math, random, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_bridge3 as RB
from render_bridge3 import font, spaced, MONO, INTER_XB, INTER_B, sm, lerp, GOLD, CREAM

W, H = 1080, 1920; FPS = 30; DUR = 12.0; SS = 2
HAND = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "PatrickHand-Regular.ttf")
CUTS = [1.8, 4.4, 5.6, 6.4, 8.4]
GOLDC = (255, 196, 84); NAVY = (20, 24, 42); SLATE = (60, 68, 98); BLUE = (84, 112, 190)

class Cam:
    def __init__(s, z=1.0, cx=540, cy=980): s.z, s.cx, s.cy = z, cx, cy
class Pen:
    """drawing helper with a per-scene zoom"""
    def __init__(s, d, cam): s.d, s.c = d, cam
    def p(s, x, y): return ((s.c.cx + (x - s.c.cx) * s.c.z) * SS, (s.c.cy + (y - s.c.cy) * s.c.z) * SS)
    def w(s, v): return max(1, int(v * s.c.z * SS))
    def line(s, pts, w=8, col=CREAM + (255,)):
        P = [s.p(*q) for q in pts]; s.d.line(P, fill=col, width=s.w(w), joint="curve"); r = s.w(w) / 2
        for a, b in (P[0], P[-1]): s.d.ellipse([a - r, b - r, a + r, b + r], fill=col)
    def circ(s, x, y, r, fill=CREAM + (255,), outline=None, ow=3):
        a, b = s.p(x, y); rr = r * s.c.z * SS; s.d.ellipse([a - rr, b - rr, a + rr, b + rr], fill=fill, outline=outline, width=s.w(ow) if outline else 0)
    def poly(s, pts, fill, outline=None, ow=3): s.d.polygon([s.p(*q) for q in pts], fill=fill, outline=None); s.line(list(pts) + [pts[0]], ow, outline) if outline else None
    def rrect(s, x0, y0, x1, y1, r, fill, outline=None, ow=3):
        a, b = s.p(x0, y0); c, d_ = s.p(x1, y1); s.d.rounded_rectangle([a, b, c, d_], radius=int(r * s.c.z * SS), fill=fill, outline=outline, width=s.w(ow) if outline else 0)
    def text(s, xy, t, path, size, fill, anchor="mm"):
        s.d.text(s.p(*xy), t, font=ImageFont.truetype(path, int(size * s.c.z * SS)), fill=fill, anchor=anchor)

def fig_front(pn, x, gy, k=1.0, kind="kid", arms=((8, 8), (8, 8)), mood="flat", sit=False, col=CREAM + (255,), lids=0.0):
    """front-facing stick figure. arms=((L upper, lower),(R upper, lower)): degrees from 'down', outward positive, 180 = straight up"""
    s = k; hip = (x, gy - (62 * s if sit else 118 * s)); sh = (x, hip[1] - 96 * s); head = (x, sh[1] - 34 * s); w = 9 * s
    if not sit:
        pn.line([(x, hip[1]), (x - 22 * s, gy - 56 * s), (x - 26 * s, gy)], w, col); pn.line([(x, hip[1]), (x + 22 * s, gy - 56 * s), (x + 26 * s, gy)], w, col)
        pn.line([(x - 26 * s, gy), (x - 40 * s, gy)], w, col); pn.line([(x + 26 * s, gy), (x + 40 * s, gy)], w, col)
    if kind == "mom":
        pn.poly([(x - 20 * s, sh[1] + 6 * s), (x + 20 * s, sh[1] + 6 * s), (x + 36 * s, gy - 8 * s), (x - 36 * s, gy - 8 * s)], GOLDC + (46,), GOLDC + (230,), 4 * s)
        pn.line([(x - 18 * s, sh[1] + 8 * s), (x + 12 * s, hip[1] + 10 * s)], 9 * s, GOLDC + (255,))
    pn.line([sh, hip], w * 1.15, col)
    for sd, (a1, a2) in zip((-1, 1), arms):
        def seg(o, L, a): return (o[0] + sd * L * math.sin(math.radians(a)), o[1] + L * math.cos(math.radians(a)))
        e = seg((x + sd * 4 * s, sh[1] + 6 * s), 46 * s, a1); h = seg(e, 44 * s, a2); pn.line([(x + sd * 4 * s, sh[1] + 6 * s), e, h], w, col)
    pn.circ(head[0], head[1], 31 * s, col)
    if kind == "mom":
        pn.circ(head[0] - 20 * s, head[1] - 28 * s, 13 * s, col); pn.circ(head[0], head[1] - 12 * s, 3.4 * s, GOLDC + (255,))
    else:
        for i, off in enumerate((-12, 0, 12)): pn.line([(head[0] + off * s, head[1] - 26 * s), (head[0] + (off * 1.4 + 3) * s, head[1] - 40 * s)], 6 * s, col)
    ey = head[1] - 2 * s
    for sd in (-1, 1):
        pn.circ(head[0] + sd * 11 * s, ey, 3.8 * s, NAVY + (255,))
        if lids > 0: pn.rrect(head[0] + sd * 11 * s - 7 * s, ey - 6 * s, head[0] + sd * 11 * s + 7 * s, ey - 6 * s + 8 * s * lids + 1, 1, col)
    my = head[1] + 14 * s
    if mood == "o": pn.circ(head[0], my, 5.5 * s, NAVY + (255,))
    elif mood == "smile": pn.line([(head[0] - 9 * s, my - 2 * s), (head[0], my + 4 * s), (head[0] + 9 * s, my - 2 * s)], 3.4 * s, NAVY + (255,))
    elif mood == "grit": pn.rrect(head[0] - 12 * s, my - 4 * s, head[0] + 12 * s, my + 6 * s, 2, (240, 240, 240, 255), NAVY + (255,), 2)
    else: pn.line([(head[0] - 8 * s, my), (head[0] + 8 * s, my)], 3.4 * s, NAVY + (255,))
    return dict(head=head, sh=sh, hip=hip)

def bubble(pn, x, y, text, tail=(1, 60), size=44, w=None):
    f = ImageFont.truetype(HAND, int(size * pn.c.z * SS)); parts = text.split("\n"); ww = max(f.getlength(p) for p in parts) / (pn.c.z * SS) + 56; hh = len(parts) * size * 1.05 + 36
    pn.rrect(x - ww / 2, y - hh / 2, x + ww / 2, y + hh / 2, 34, (250, 246, 236, 255), (30, 30, 40, 255), 3)
    pn.poly([(x + tail[0] * 40 - 18, y + hh / 2 - 2), (x + tail[0] * 40 + 18, y + hh / 2 - 2), (x + tail[0] * 70, y + hh / 2 + tail[1])], (250, 246, 236, 255), None)
    for i, p in enumerate(parts): pn.text((x, y - hh / 2 + 18 + size * 0.52 + i * size * 1.05), p, HAND, size, (30, 30, 40, 255))

# ------------------------------------------------------------------ scenes (all inside y 330..1500)
FLOOR = 1300
def room(pn, t, door_open=0.0, kid_bed=True):
    pn.line([(80, FLOOR), (1000, FLOOR)], 5, (130, 138, 168, 200))
    # door (left)
    pn.rrect(110, 640, 270, FLOOR, 8, (36, 42, 66, 255), (110, 120, 156, 255), 4)
    if door_open > 0:
        pn.poly([(270, 660), (250 + 140 * door_open, 700), (250 + 140 * door_open, FLOOR + 8), (270, FLOOR)], (255, 214, 140, int(120 * door_open)))
    # window (right) with stars
    pn.rrect(760, 700, 960, 940, 6, (16, 22, 52, 255), (120, 130, 170, 255), 4)
    for sx, sy in ((800, 750), (900, 800), (850, 890), (930, 740)): pn.circ(sx, sy, 3, (240, 240, 255, 230))
def bed_front(pn, x, y, mound=True):
    pn.rrect(x - 190, y - 120, x + 205, y - 70, 10, (44, 50, 80, 255), (110, 120, 156, 255), 4)                       # headboard / back
    pn.rrect(x - 200, y - 30, x + 215, y + 28, 12, (70, 80, 128, 255), (130, 140, 190, 255), 4)                          # mattress edge
    pn.rrect(x + 90, y - 100, x + 205, y - 52, 22, (96, 108, 160, 255), None)                                           # pillow
    if mound: pn.poly([(x - 150, y - 4), (x - 70, y - 60), (x + 40, y - 56), (x + 120, y - 4)], BLUE + (255,), (150, 170, 240, 255), 4)
def blanket(fg, x, y): fg.poly([(x - 170, y + 6), (x - 90, y - 66), (x + 70, y - 70), (x + 150, y + 6)], BLUE + (255,), (150, 170, 240, 255), 4)

def scene_a(pn, fg, t):    # asleep
    room(pn, t, 0.0)
    x, y = 540, FLOOR - 40
    pn.rrect(250, y - 10, 830, y + 40, 10, (60, 68, 108, 255), (130, 140, 190, 255), 4)
    pn.rrect(250, y + 40, 830, y + 120, 6, (40, 46, 74, 255), None); pn.rrect(250, y - 70, 300, y + 110, 6, (44, 50, 80, 255), (110, 120, 156, 255), 4)
    pn.rrect(310, y - 52, 440, y - 6, 22, (96, 108, 160, 255), None)
    pn.rrect(430, y - 46, 830, y - 4, 16, BLUE + (255,), (150, 170, 240, 255), 4)
    ph = math.sin(t * 2.4) * 3; fg.circ(380, y - 62 + ph, 40, CREAM + (255,))
    for sd in (-1, 1): pass
    fg.line([(366, y - 66 + ph), (378, y - 62 + ph)], 4, NAVY + (255,)); fg.line([(386, y - 62 + ph), (398, y - 66 + ph)], 4, NAVY + (255,))
    fg.circ(392, y - 40 + ph, 5, NAVY + (255,))
    for i in range(3):
        u = (t * 0.7 + i / 3.0) % 1.0; fg.text((470 + 40 * u, y - 140 - 150 * u), "z", HAND, 40 + 20 * u, (206, 214, 255, int(255 * (1 - u))))
def scene_b(pn, fg, t):    # mom enters: NO INTERNET!
    u = t - 1.8; room(pn, t, sm(u / 0.5))
    bed_front(pn, 720, FLOOR - 4, mound=False)
    wake = sm((u - 0.9) / 0.4)
    mx = 190 + 150 * sm((u - 0.25) / 0.9)
    if u > 0.25: fig_front(fg, mx, FLOOR, 1.18, "mom", arms=((8, 8), (96, 120) if u > 1.3 else (8, 8)), mood="o" if u > 1.4 else "flat")
    kid = fig_front(fg, 735, FLOOR - 52, 1.1, "kid", arms=((18, 40), (18, 40)), sit=True, mood="o" if u > 1.4 else "flat", lids=0.8 * (1 - wake) + 0.1) if u > 0.9 else None
    if u > 0.9: blanket(fg, 735, FLOOR - 4)
    if u > 1.35: bubble(fg, 380, 835, "Beta... NO\nINTERNET!", tail=(-0.5, 105))
    if u > 1.3:   # her phone
        fg.rrect(mx + 108, 940, mx + 150, 1020, 8, (30, 36, 60, 255), (210, 216, 240, 255), 3)
def scene_c(pn, fg, t):    # phone close-up: hotspot on
    u = t - 4.4; pn.rrect(280, 560, 800, 1460, 50, (22, 28, 54, 255), (214, 220, 244, 255), 6)
    pn.text((540, 660), "Settings", INTER_B, 42, (230, 232, 244, 255))
    pn.rrect(310, 740, 770, 860, 26, (40, 48, 84, 255), None); pn.text((470, 800), "Personal Hotspot", INTER_B, 38, (236, 238, 248, 255))
    on = sm((u - 0.55) / 0.2); tx = lerp(668, 722, on)
    pn.rrect(640, 770, 750, 830, 30, tuple(int(lerp(a, b, on)) for a, b in zip((92, 98, 124), GOLDC)) + (255,), None)
    pn.circ(tx - (0 if on else 14) + 0, 800, 24, (252, 250, 244, 255))
    fx = 0.55 + 0.45 * math.sin(u * 5)
    for i, r in enumerate((60, 110, 160)):   # wifi arcs under the row
        if on > 0.5:
            a0 = (u - 0.75) * 3 - i * 0.18; al = int(255 * max(0, min(1, a0)));
            for dx in range(1): pn.d.arc([pn.p(540 - r, 1130 - r)[0], pn.p(540 - r, 1130 - r)[1], pn.p(540 + r, 1130 + r)[0], pn.p(540 + r, 1130 + r)[1]], 225, 315, fill=GOLDC + (al,), width=pn.w(12))
        pn.circ(540, 1130, 12, GOLDC + (255,) if on > 0.5 else (92, 98, 124, 255))
    # thumb
    ty = lerp(1500, 840, sm(u / 0.5)) if u < 0.7 else lerp(840, 1100, sm((u - 0.7) / 0.5))
    fg.rrect(tx - 42 + 20, ty, tx + 42 + 20, ty + 260, 40, CREAM + (255,), None)
def scene_d(pn, fg, t):    # rage burst
    u = t - 5.6; rot = u * 0.9
    for i in range(30):
        a0 = rot + i * 2 * math.pi / 30; a1 = a0 + math.pi / 30 * (0.9 + 0.3 * math.sin(i + u * 14))
        R = 1500; pn.poly([(540, 940), (540 + R * math.cos(a0), 940 + R * math.sin(a0)), (540 + R * math.cos(a1), 940 + R * math.sin(a1))], GOLDC + (110 if i % 2 else 40,))
    k = 1.0 + 0.1 * math.sin(u * 22) * (1 - u); fg.circ(540, 940, 190 * k, CREAM + (255,))
    for sd in (-1, 1):
        fg.line([(540 + sd * 40, 900), (540 + sd * 120, 880 - 0 * sd)], 14, NAVY + (255,)); fg.line([(540 + sd * 52, 930), (540 + sd * 98, 960)], 12, NAVY + (255,))
    fg.rrect(460, 1010, 620, 1070, 12, (246, 246, 246, 255), NAVY + (255,), 6)
    for xx in range(480, 620, 26): fg.line([(xx, 1012), (xx, 1068)], 3, NAVY + (255,))
    fg.line([(420, 770), (520, 810)], 18, NAVY + (255,)); fg.line([(660, 770), (560, 810)], 18, NAVY + (255,))
CITY = [(90, 760, 150, 600), (230, 640, 120, 720), (370, 700, 150, 660), (530, 560, 190, 800), (740, 680, 140, 680), (890, 600, 160, 760)]
def scene_e(pn, fg, t):    # signal crosses the city, then the planet
    u = t - 6.4
    if u < 1.2:
        for (x, y, w, h) in CITY:
            pn.rrect(x, y + 1300 - 640 - 0 * h, x + w, FLOOR + 160, 4, (30, 38, 68, 255), (70, 80, 120, 255), 3)
            for wy in range(y + 1300 - 640 + 22, FLOOR + 130, 54):
                for wx in range(int(x) + 22, int(x + w) - 14, 34): pn.rrect(wx, wy, wx + 16, wy + 22, 2, (54, 66, 112, 255) if (wx + wy) % 5 else (250, 230, 160, 255), None)
        wx_, wy_ = 560, 900; pn.rrect(wx_ - 8, wy_ - 12, wx_ + 22, wy_ + 20, 2, GOLDC + (255,), None)
        L = min(1.0, u / 0.45); R = 1100 * L
        pn.poly([(wx_ + 6, wy_ + 4), (wx_ + 6 + R, wy_ - 170 * L - 40), (wx_ + 6 + R, wy_ + 190 * L + 40)], (255, 232, 170, int(120 * min(1, u * 3))))
        for i in range(5):
            r = ((u * 520) - i * 120) % 600 + 20; al = int(255 * max(0, 1 - r / 640))
            pn.d.arc([pn.p(wx_ - r, wy_ - r)[0], pn.p(wx_ - r, wy_ - r)[1], pn.p(wx_ + r, wy_ + r)[0], pn.p(wx_ + r, wy_ + r)[1]], -45, 45, fill=GOLDC + (al,), width=pn.w(10))
    else:
        v = u - 1.2; pn.circ(540, 1900, 1050, (14, 22, 52, 255), GOLDC + (190,), 8)
        rr = random.Random(5)
        for i in range(70): a = rr.uniform(-1.25, 1.25); r_ = rr.uniform(120, 760); pn.circ(540 + math.sin(a) * r_, 1900 - math.cos(a) * r_ * 0.95 + 150, rr.uniform(2, 5), (250, 226, 150, 230))
        s = sm(v / 0.4) * 80; pn.circ(560, 1330, 10 + s * 0.5, (255, 244, 210, 255))
        pn.line([(560 - s * 2.4, 1330), (560 + s * 2.4, 1330)], 8, (255, 244, 210, 255)); pn.line([(560, 1330 - s * 2.4), (560, 1330 + s * 2.4)], 8, (255, 244, 210, 255))
        for i in range(3):
            r = ((v * 420) - i * 130) % 420; pn.d.ellipse([pn.p(560 - r, 1330 - r)[0], pn.p(560 - r, 1330 - r)[1], pn.p(560 + r, 1330 + r)[0], pn.p(560 + r, 1330 + r)[1]], outline=GOLDC + (int(220 * max(0, 1 - r / 420)),), width=pn.w(6))
def scene_f(pn, fg, t):    # buffering + 1%
    u = t - 8.4; room(pn, t, 0.0); bed_front(pn, 720, FLOOR - 4, mound=False)
    mood = "smile" if u < 0.9 else "o"
    fig_front(fg, 340, FLOOR, 1.18, "mom", arms=((8, 8), (96, 120)), mood=mood)
    fg.rrect(448, 940, 490, 1020, 8, (30, 36, 60, 255), (210, 216, 240, 255), 3)
    if u > 0.4 and u < 1.6:   # full bars
        for i in range(4): fg.rrect(458 + i * 7, 1000 - 6 - i * 6, 462 + i * 7, 1000, 1, GOLDC + (255,), None)
    if u > 0.9:
        bubble(fg, 400, 835, "Beta... it's\nBUFFERING!", tail=(-0.5, 105))
        a = (u * 3) % 1.0; fg.d.arc([fg.p(442, 980)[0], fg.p(442, 980)[1], fg.p(498, 1036)[0], fg.p(498, 1036)[1]], 0, 270 * a + 30, fill=(255, 255, 255, 255), width=fg.w(5))
    # kid: tired, phone glowing, battery 1%
    fig_front(fg, 735, FLOOR - 52, 1.1, "kid", arms=((30, 58), (30, 58)), sit=True, mood="flat", lids=0.55 + 0.1 * math.sin(u * 3))
    blanket(fg, 735, FLOOR - 4); fg.rrect(702, 1108, 768, 1186, 8, (30, 36, 60, 255), (210, 216, 240, 255), 3)
    if u > 1.3:
        bx, by = 760, 880; fg.rrect(bx - 54, by - 24, bx + 46, by + 24, 7, None, (255, 120, 110, 255), 4); fg.rrect(bx + 46, by - 9, bx + 56, by + 9, 2, (255, 120, 110, 255), None)
        fg.rrect(bx - 49, by - 19, bx - 38, by + 19, 3, (255, 120, 110, 255), None); fg.text((bx - 120, by), "1%", INTER_B, 44, (255, 150, 140, 255))

SCENES = [(0.0, scene_a, Cam(1.32, 560, 1090)), (1.8, scene_b, Cam(1.3, 560, 1060)), (4.4, scene_c, Cam(1.0, 540, 1000)), (5.6, scene_d, Cam(1.0, 540, 940)), (6.4, scene_e, Cam(1.15, 540, 1040)), (8.4, scene_f, Cam(1.3, 560, 1060))]
def cam_for(t, i):
    t0, c = SCENES[i][0], SCENES[i][2]; p = min(1.0, (t - t0) / 1.8)
    if i == 5:
        q = sm((t - 9.9) / 1.8); return Cam(c.z * (1 + 0.28 * q), lerp(c.cx, 735, q), lerp(c.cy, 1110, q))
    return Cam(c.z * (1 + 0.08 * p), c.cx, c.cy)

def whip(arr, t):
    for c in CUTS:
        dt = abs(t - c)
        if dt < 0.1:
            p = 1 - dt / 0.1; L = int(8 + 120 * p * p); k = np.zeros((1, L), np.float32); k[0, :] = 1.0 / L
            return cv2.filter2D(arr, -1, k, borderType=cv2.BORDER_REFLECT) * (1 + 0.3 * p)
    return arr
def frame(t):
    i = max(j for j, s in enumerate(SCENES) if t >= s[0]); cam = cam_for(t, i)
    base = RB.bg() if True else None
    if i in (2, 3): base = Image.new("RGBA", (W, H), (14, 18, 36, 255))
    big = (W * SS, H * SS); lay = Image.new("RGBA", big, (0, 0, 0, 0)); fgl = Image.new("RGBA", big, (0, 0, 0, 0))
    SCENES[i][1](Pen(ImageDraw.Draw(lay), cam), Pen(ImageDraw.Draw(fgl), cam), t)
    lay1 = lay.resize((W, H), Image.LANCZOS); fg1 = fgl.resize((W, H), Image.LANCZOS)
    A = np.asarray(fg1.split()[3], np.float32); gl = Image.new("RGBA", (W, H), (255, 214, 150, 0)); gl.putalpha(Image.fromarray((np.asarray(Image.fromarray(A.astype(np.uint8)).filter(ImageFilter.GaussianBlur(20)), np.float32) * 0.34).astype(np.uint8), "L"))
    base.alpha_composite(lay1); base.alpha_composite(gl); base.alpha_composite(fg1)
    arr = np.asarray(base.convert("RGB"), np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); vig = np.clip(1 - 0.45 * (((xx - W / 2) / (W * 0.8)) ** 2 + ((yy - H * 0.5) / (H * 0.75)) ** 2), 0.3, 1.0); arr = arr * vig[..., None]
    arr = whip(arr, t)
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB"); d = ImageDraw.Draw(img)
    # title (gold + white); closing line replaces it
    def title(gold, white, al):
        lt = Image.new("RGBA", (W, H), (0, 0, 0, 0)); tl = Image.new("L", (W, 150), 0); td = ImageDraw.Draw(tl); sz = 70
        while td.textlength(gold, font=font(INTER_XB, sz)) > 840 and sz > 36: sz -= 2
        td.text((W / 2, 75), gold, font=font(INTER_XB, sz), fill=255, anchor="mm")
        gc = np.zeros((150, W, 3), np.float32); gg = np.linspace(0, 1, 150, dtype=np.float32)[:, None, None]
        gc[:] = np.array([255, 214, 130], np.float32) * (1 - gg) + np.array([246, 164, 56], np.float32) * gg
        g = Image.fromarray(gc.astype(np.uint8), "RGB").convert("RGBA"); g.putalpha(tl); lt.alpha_composite(g, (0, 300))
        w2 = 52
        while ImageDraw.Draw(lt).textlength(white, font=font(INTER_XB, w2)) > 840 and w2 > 28: w2 -= 2
        ImageDraw.Draw(lt).text((W / 2, 462), white, font=font(INTER_XB, w2), fill=(246, 244, 240, 255), anchor="mm")
        a = np.asarray(lt, np.float32).copy(); a[..., 3] *= al; return Image.fromarray(a.astype(np.uint8), "RGBA")
    a1 = 1.0 if t < 10.2 else max(0.0, 1 - (t - 10.2) / 0.25); a2 = 0.0 if t < 10.45 else min(1.0, (t - 10.45) / 0.3)
    bi = img.convert("RGBA")
    for g_, w_, al in (("WHEN MOM'S INTERNET DIES", "AT 2 AM, YOU BECOME THE ROUTER", a1), ("EVERY KID IS MOM'S HOTSPOT", "NO SLEEP INCLUDED.", a2)):
        if al > 0.01: bi.alpha_composite(title(g_, w_, al))
    img = bi.convert("RGB"); d = ImageDraw.Draw(img)
    spaced(d, (540, 1610), "S L O W   L I G H T", font(MONO, 20), (96, 100, 124), 2, "c")
    return img

def _job(a):
    i, t, out = a; frame(t).save(f"{out}/f{i:04d}.png", compress_level=1); return i
if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "sheet":
        ts = [float(a) for a in sys.argv[3:]]; cols = min(len(ts), 6); rows = math.ceil(len(ts) / cols); tw, th_ = 270, 480
        sheet = Image.new("RGB", (tw * cols, th_ * rows))
        for j, t in enumerate(ts): sheet.paste(frame(t).resize((tw, th_), Image.LANCZOS), ((j % cols) * tw, (j // cols) * th_))
        sheet.save(sys.argv[2]); print("wrote", sys.argv[2])
    elif cmd == "frames":
        from multiprocessing import Pool
        out = sys.argv[2]; os.makedirs(out, exist_ok=True)
        jobs = [(i, i / FPS, out) for i in range(int(DUR * FPS))]
        with Pool(4) as p:
            for n, i in enumerate(p.imap_unordered(_job, jobs)):
                if n % 60 == 0: print(n, "/", len(jobs), flush=True)
    elif cmd == "video":
        out, audio, fr = sys.argv[2:5]
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{fr}/f%04d.png", "-i", audio, "-t", str(DUR), "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True); print("wrote", out)
