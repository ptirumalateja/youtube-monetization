# Shot library for the Galwan reel. Each shot: fn(C, T, D) draws into Canvas C at local time T of duration D.
import math
import numpy as np
from lino import *


def shake(T, amp, f=23):
    return amp * math.sin(T * f) * math.cos(T * f * 0.7), amp * math.cos(T * f * 1.3)


def hook_text(C, T, top="ఒక్క బుల్లెట్ కూడా", bot="పేలలేదు"):
    # frame-0 hook line, second line slams at ~0.33 s
    text_layer(C, top, 540, 400, 112, col="paper", path=FONT_TE, maxw=880, outline="deep")
    u = (T - 0.30) / 0.14
    sc = 1.0 if u >= 1 else (1.0 if u < 0 else 1.0 + 0.35 * (1 - eout(u)))
    text_layer(C, bot, 540, 560, 150, col="saff", path=FONT_TE, scale=sc, maxw=820, outline="deep")


def s_standoff(C, T, D):
    u = T / D
    cam = Cam(540, 1000, 1.0 + 0.10 * ease(u))
    sky(C, cam, T)
    flare = 1 + 0.6 * max(0, 1 - abs(T - 0.4) / 0.25)
    moon(C, cam, 760, 860, 150, T, ring=flare, glow=min(1, flare))
    mountains(C, cam, 11, 1080, 260, t=T)
    # enemy wall on snow ridge
    d = C.L("paper", rough=0.8)
    poly(d, cam, [(-400, 1270), (300, 1235), (800, 1250), (1480, 1225), (1480, 4000), (-400, 4000)])
    d = C.L("deep", rough=0.9)
    r = np.random.default_rng(4)
    for i in range(16):
        x = -60 + i * 78 + r.random() * 30
        hh = 300 + r.random() * 60
        raise_ = (i % 3 == 0)
        pose = dict(ra=170 + 10 * math.sin(T * 6 + i), re=10) if raise_ else dict(ra=-20, re=-30)
        soldier(d, cam, x, 1265 + r.random() * 12, hh, pose, facing=-1, club=True, pack=False)
    # gouge snow hatch on ground
    d = C.L("ink", rough=0.6, alpha=0.5)
    for k in range(18):
        y = 1300 + k * 34
        line(d, cam, [(-200 + (k * 97) % 300, y), (300 + (k * 131) % 500, y + 8)], 4)
    # our officer, from behind, huge, saffron rim
    x0 = 330 - 20 * ease(u)
    d = C.L("saff", rough=0.8)
    figure_front(d, cam.off(-12, 6), x0, 2560, 1700, arms=(10, 10, 4))
    d = C.L("ink", rough=0.8)
    figure_front(d, cam, x0, 2560, 1700, arms=(10, 10, 4))
    snow(C, cam, T + 0.5, n=90, wind=1.0 + 1.6 * max(0, 1 - abs(T - 0.45) / 0.3), size=1.2)
    hook_text(C, T)


def s_front_of_men(C, T, D):
    u = T / D
    cam = Cam(540 - 60 * ease(u), 1000, 1.06)
    sky(C, cam, T)
    moon(C, cam, 300, 700, 120, T)
    mountains(C, cam, 21, 1000, 220)
    d = C.L("paper", rough=0.8)
    poly(d, cam, [(-400, 1330), (1480, 1300), (1480, 4000), (-400, 4000)])
    d = C.L("ink", rough=0.8)
    for i, (x, hh) in enumerate([(70, 560), (190, 600), (300, 640), (120, 520), (250, 560)]):
        soldier(d, cam, x, 1360 + i * 6, hh, dict(la=5, ra=-5), facing=1, rifle=True)
    d = C.L("saff", rough=0.8)
    figure_front(d, cam.off(-10), 680, 1520, 1000, arms=(40, 8, 20), legs=8)
    d = C.L("ink", rough=0.8)
    figure_front(d, cam, 680, 1520, 1000, arms=(40, 8, 20), legs=8)
    snow(C, cam, T + 2, n=80)
    hook_text(C, 5)


def s_milestone(C, T, D):
    u = T / D
    cam = Cam(540, 1050, 1.0 + 0.18 * eout(u))
    sky(C, cam, T, density=0.7)
    moon(C, cam, 800, 640, 90, T)
    d = C.L("ink", rough=0.8)
    poly(d, cam, ridge(31, 1180, 120) + [(1480, 4000), (-400, 4000)])
    # road
    d = C.L("paper", rough=0.8, alpha=0.9)
    poly(d, cam, [(470, 1190), (610, 1190), (1400, 2400), (-300, 2400)])
    d = C.L("ink", rough=0.6)
    for k in range(6):
        y0 = 1230 + k * k * 30 + 40 * k
        poly(d, cam, [(535, y0), (545, y0), (550 + k * 4, y0 + 30 + k * 12), (530 - k * 4, y0 + 30 + k * 12)])
    # milestone
    mx, my, mw, mh = 300, 1520, 380, 520
    d = C.L("ink", rough=0.7)
    poly(d, cam, [(mx - mw / 2 - 16, my + 16), (mx + mw / 2 + 16, my + 16), (mx + mw / 2 + 16, my - mh + 120), (mx - mw / 2 - 16, my - mh + 120)])
    circ(d, cam, mx, my - mh + 120, mw / 2 + 16)
    d = C.L("paper", rough=0.6)
    poly(d, cam, [(mx - mw / 2, my), (mx + mw / 2, my), (mx + mw / 2, my - mh + 120), (mx - mw / 2, my - mh + 120)])
    d = C.L("saff", rough=0.6)
    circ(d, cam, mx, my - mh + 120, mw / 2)
    poly(d, cam, [(mx - mw / 2, my - mh + 120), (mx + mw / 2, my - mh + 120), (mx + mw / 2, my - mh + 200), (mx - mw / 2, my - mh + 200)])
    # text on stone (screen space via cam)
    X, Y = cam.p(mx, my - mh + 90)
    text_layer(C, "సూర్యాపేట", X, Y, int(66 * cam.s), col="ink", maxw=int(330 * cam.s))
    X, Y = cam.p(mx, my - 210)
    text_layer(C, "తెలంగాణ", X, Y, int(52 * cam.s), col="ink", maxw=int(300 * cam.s))
    X, Y = cam.p(mx, my - 110)
    text_layer(C, "0", X, Y, int(110 * cam.s), col="saff", path=FONT_NUM)
    snow(C, cam, T, n=40, size=0.8)


def s_date(C, T, D):
    u = T / D
    d = C.L("saff", rough=0.9, alpha=0.95)
    d.rectangle((0, 0, W, H), fill=255)
    d = C.L("paper", rough=0.6, alpha=0.5)
    for k in range(40):
        y = k * 52 + (k % 3) * 9
        d.line([(0, y), (W, y + 24)], fill=255, width=3 + (k % 4))
    s = 1.0 + 0.4 * (1 - eout(T / 0.13))
    sx, sy = shake(T, 10 * max(0, 1 - T / 0.3))
    d = C.L("ink", rough=0.9)
    bw, bh = 820 * s, 560 * s
    d.rectangle((540 - bw / 2 + sx, 900 - bh / 2 + sy, 540 + bw / 2 + sx, 900 + bh / 2 + sy), fill=255)
    text_layer(C, "15", 540 + sx, 760 + sy, 260, col="paper", path=FONT_NUM, scale=s)
    text_layer(C, "జూన్ 2020", 540 + sx, 1020 + sy, 130, col="paper", scale=s, maxw=700)


def s_valley(C, T, D):
    u = T / D
    cam = Cam(540, 1060 - 140 * ease(u), 1.0 + 0.08 * u)
    sky(C, cam, T)
    moon(C, cam, 300, 520, 110, T)
    for i, (b, a, col) in enumerate([(820, 320, "deep"), (1000, 300, "ink"), (1250, 260, "ink")]):
        c2 = cam.off(0, (i - 1) * 40 * u); c2.s = cam.s * (1 + i * 0.04 * u)
        mountains(C, c2, 50 + i, b, a, col=col)
    # river ribbon
    d = C.L("paper", rough=0.7)
    pts = []
    for k in range(60):
        v = k / 59
        y = 1100 + v ** 1.6 * 1200
        x = 540 + math.sin(v * 7 + 1) * (60 + 380 * v)
        w = 6 + 220 * v ** 1.5
        pts.append((x, y, w))
    left = [(x - w / 2, y) for x, y, w in pts]
    right = [(x + w / 2, y) for x, y, w in pts][::-1]
    poly(d, cam, left + right)
    d = C.L("ink", rough=0.4, alpha=0.6)
    for k in range(8, 60, 3):
        x, y, w = pts[k]
        line(d, cam, [(x - w * 0.3, y), (x + w * 0.25, y + 4)], 2 + w * 0.03)
    snow(C, cam, T, n=70)
    text_layer(C, "గల్వాన్ లోయ, లద్దాఖ్", 540, 430, 92, col="paper", maxw=840, outline="deep")


def s_cold(C, T, D):
    u = T / D
    cam = Cam(540, 960, 1.0 + 0.07 * u)
    d = C.L("paper", rough=0)
    d.rectangle((0, 0, W, H), fill=255)
    # blizzard streaks
    d = C.L("ink", rough=0.6, alpha=0.35)
    r = np.random.default_rng(8)
    for k in range(70):
        y = r.random() * 2000
        x = (r.random() * 1600 + T * 1400 * (0.6 + r.random())) % 1800 - 400
        line(d, Cam(), [(x, y), (x + 120 + r.random() * 260, y + 30)], 3 + r.random() * 5)
    hx, hy = 400, 1120
    for col, off in (("saff", 12), ("ink", 0)):
        d = C.L(col, rough=0.8)
        c2 = cam.off(-off, off * 0.3)
        circ(d, c2, hx, hy, 230)
        poly(d, c2, [(hx + 180, hy - 40), (hx + 285, hy + 50), (hx + 200, hy + 80)])
        poly(d, c2, [(hx + 150, hy + 120), (hx + 225, hy + 150), (hx + 160, hy + 210)])
        poly(d, c2, [(hx - 120, hy + 160), (hx + 120, hy + 170), (hx + 200, hy + 520), (hx + 420, hy + 640), (hx + 420, 2200), (-300, 2200), (-300, hy + 600), (hx - 260, hy + 480)])
        q = [(hx + 300 * math.cos(a) - 20, hy - 70 - 280 * math.sin(a)) for a in np.linspace(0, math.pi, 20)]
        poly(d, c2, q + [(hx - 330, hy - 40), (hx + 300, hy - 40)])
    # scarf band
    d = C.L("paper", rough=0.6, alpha=0.6)
    for k in range(5):
        line(d, cam, [(hx - 200, hy + 330 + k * 26), (hx + 230, hy + 300 + k * 22)], 6)
    # breath puffs (ink outlined paper)
    for k in range(3):
        ph = (T * 1.4 + k * 0.33) % 1.0
        x = hx + 310 + ph * 380
        y = hy + 120 - ph * 120 + 20 * math.sin(ph * 6)
        rr = (30 + ph * 140) * (1 - ph * 0.4)
        d = C.L("ink", rough=1.0, alpha=0.5 * (1 - ph))
        circ(d, cam, x, y, rr + 8)
        d = C.L("paper", rough=1.0)
        circ(d, cam, x, y, rr)
    snow(C, cam, T, n=120, wind=2.6, size=1.0, col="ink")
    text_layer(C, "ఎముకలు కొరికే చలి", 540, 420, 100, col="ink", maxw=860)


def s_tent(C, T, D):
    u = T / D
    cam = Cam(540 + 60 * u, 1060, 1.08 + 0.1 * u)
    sky(C, cam, T)
    mountains(C, cam, 61, 980, 240)
    d = C.L("paper", rough=0.8)
    poly(d, cam, [(-400, 1240), (1480, 1200), (1480, 4000), (-400, 4000)])
    # river in front
    d = C.L("ink", rough=0.6, alpha=0.75)
    poly(d, cam, [(-400, 1500), (1480, 1440), (1480, 1600), (-400, 1680)])
    d = C.L("paper", rough=0.5)
    for k in range(10):
        x = -200 + ((k * 173 + T * 220) % 1600)
        line(d, cam, [(x, 1540 - x * 0.04), (x + 90, 1538 - x * 0.04)], 5)
    # tent
    d = C.L("deep", rough=0.8)
    poly(d, cam, [(560, 1230), (760, 1000), (960, 1230)])
    line(d, cam, [(760, 1000), (760, 960)], 10)
    d = C.L("saff", rough=0.6)
    glow = 0.8 + 0.2 * math.sin(T * 13)
    poly(d, cam, [(720, 1230), (760, 1110), (800, 1230)])
    d = C.L("saff", rough=1.2, alpha=0.35 * glow)
    circ(d, cam, 760, 1190, 120)
    d = C.L("deep", rough=0.8)
    for i, x in enumerate([500, 1000, 1080]):
        soldier(d, cam, x, 1235, 260, dict(ra=-15, la=15), facing=-1, pack=False)
    snow(C, cam, T, n=70)
    text_layer(C, "మన భూభాగంలో టెంట్", 540, 420, 96, col="paper", maxw=860, outline="deep")


def s_walk(C, T, D):
    u = T / D
    cam = Cam(400 + 260 * u, 1000, 1.05)
    sky(C, cam, T)
    moon(C, cam, 900, 620, 130, T)
    mountains(C, cam, 71, 1020, 230)
    d = C.L("paper", rough=0.8)
    poly(d, cam, [(-400, 1360), (2000, 1330), (2000, 4000), (-400, 4000)])
    ph = T * 2 * math.pi * 1.6
    x = 330 + 320 * u
    sw = 26 * math.sin(ph)
    pose = dict(lt=sw, ls=max(0, -sw) * 0.8, rt=-sw, rs=max(0, sw) * 0.8, la=-sw * 0.8, le=10, ra=sw * 0.8, re=10, lean=4)
    d = C.L("saff", rough=0.8)
    soldier(d, cam.off(-9), x, 1520 - abs(math.sin(ph)) * 10, 900, pose)
    d = C.L("ink", rough=0.8)
    soldier(d, cam, x, 1520 - abs(math.sin(ph)) * 10, 900, pose)
    for i, (dx, hh) in enumerate([(-300, 600), (-420, 560), (-520, 520)]):
        p2 = dict(lt=sw * -0.9, rt=sw * 0.9, la=sw * 0.7, ra=-sw * 0.7)
        soldier(d, cam, x + dx, 1420 + i * 4, hh, p2, rifle=True)
    snow(C, cam, T, n=60)


def s_name(C, T, D):
    u = T / D
    d = C.L("saff", rough=0.9)
    d.rectangle((0, 0, W, H), fill=255)
    d = C.L("paper", rough=0.5, alpha=0.55)
    for k in range(60):
        a = k / 60 * math.pi * 2 + T * 0.15
        d.polygon([(540, 980), (540 + 2000 * math.cos(a), 980 + 2000 * math.sin(a)), (540 + 2000 * math.cos(a + 0.035), 980 + 2000 * math.sin(a + 0.035))], fill=255)
    cam = Cam(540, 960, 1.0 + 0.05 * u)
    # saluting officer silhouette
    pose = dict(ra=-150, re=-115, la=6, le=0, lt=3, rt=-3)
    d = C.L("ink", rough=0.8)
    soldier(d, cam, 540, 1060, 600, pose, facing=1, pack=False)
    s = 1 + 0.3 * (1 - eout((T - 0.15) / 0.14)) if T > 0.15 else 0
    if s:
        d = C.L("ink", rough=0.9)
        d.rectangle((70, 1080, 1010, 1370), fill=255)
        text_layer(C, "కల్నల్ సంతోష్ బాబు", 540, 1170, 108, col="paper", scale=s, maxw=880)
        text_layer(C, "కమాండింగ్ ఆఫీసర్ · 16 బిహార్", 540, 1300, 58, col="saff", maxw=820)


def s_rifle(C, T, D):
    u = T / D
    d = C.L("paper", rough=0.5)
    d.rectangle((0, 0, W, H), fill=255)
    cam = Cam(540, 960, 1.0 + 0.06 * u)
    # rifle silhouette, diagonal
    import math as m
    ang = -0.5
    ca, sa = m.cos(ang), m.sin(ang)

    def R(P):
        return [(540 + (x * ca - y * sa), 960 + (x * sa + y * ca)) for x, y in P]
    d = C.L("ink", rough=0.8)
    poly(d, cam, R([(-470, -40), (-260, -60), (-250, -10), (-120, -20), (-100, 40), (-60, 40), (-60, -30), (260, -30), (260, -10), (480, -10), (480, 10), (260, 10), (240, 20), (120, 20), (100, 120), (60, 120), (70, 20), (-20, 20), (-40, 70), (-90, 80), (-120, 30), (-270, 40), (-470, 80)]))
    sl = 1 if T > 0.28 else 0
    if sl:
        k = eout((T - 0.28) / 0.12)
        s = 1.5 - 0.5 * k
        sx, sy = shake(T, 12 * max(0, 1 - (T - 0.28) / 0.3))
        d = C.L("saff", rough=1.0)
        for a in (0.78, -0.78):
            L = 430 * s
            line(d, Cam(540, 960, 1), [(540 - L * m.cos(a) + sx, 960 - L * m.sin(a) + sy), (540 + L * m.cos(a) + sx, 960 + L * m.sin(a) + sy)], 70)
    text_layer(C, "తుపాకీ వాడకూడదు", 540, 420, 110, col="ink", maxw=860)


def s_rocks(C, T, D):
    u = T / D
    sx, sy = shake(T, 9)
    cam = Cam(540, 960, 1.05, sx=sx, sy=sy)
    sky(C, cam, T, density=1.4)
    d = C.L("deep", rough=0.8)
    poly(d, cam, [(1480, -100), (1480, 1100), (900, 900), (500, 500), (300, -100)])
    d = C.L("paper", rough=0.8)
    poly(d, cam, [(-400, 1450), (1480, 1400), (1480, 4000), (-400, 4000)])
    d = C.L("ink", rough=0.8)
    for i, x in enumerate([120, 300, 470, 640]):
        soldier(d, cam, x, 1480 + i * 8, 560, dict(ra=-160, re=-60, la=-150, le=-60, lean=-6), facing=1)
    r = np.random.default_rng(9)
    d2 = C.L("paper", rough=0.7)
    for k in range(26):
        st = r.random() * 1.5
        tt = (T * 1.2 + st) % 1.0
        x0, y0 = 1000 + r.random() * 500, 200 + r.random() * 500
        x = x0 - tt * (700 + r.random() * 300)
        y = y0 + tt * 1100 + tt * tt * 300
        s = 30 + r.random() * 50
        P = [(x + s * math.cos(a) * (0.7 + 0.5 * r.random()), y + s * math.sin(a) * (0.7 + 0.5 * r.random())) for a in np.linspace(0, 6.28, 7)[:-1]]
        poly(d2, cam, P)
        line(d2, cam, [(x + 40, y - 60), (x + 160, y - 220)], 3)
    snow(C, cam, T, n=60, wind=1.5)
    text_layer(C, "రాళ్ల వర్షం", 540, 420, 130, col="paper", maxw=860, outline="deep")


def s_clubs(C, T, D):
    u = T / D
    d = C.L("saff", rough=0.9)
    d.rectangle((0, 0, W, H), fill=255)
    d = C.L("paper", rough=0.6, alpha=0.45)
    for k in range(30):
        y = k * 70
        line(d, Cam(), [(-50, y), (1130, y - 120)], 6 + (k % 3) * 4)
    sx, sy = shake(T, 6)
    cam = Cam(540, 960, 1.0 + 0.08 * u, sx=sx, sy=sy)
    d = C.L("ink", rough=0.9)
    for i, (bx, by, a0) in enumerate([(200, 1900, -0.35), (860, 1950, 0.4), (520, 2050, 0.05)]):
        a = a0 + 0.25 * math.sin(T * 7 + i * 2)
        L = 1150
        ex, ey = bx + math.sin(a) * L, by - math.cos(a) * L
        line(d, cam, [(bx, by), (ex, ey)], 46)
        # barbed wire wraps
        for k in range(14):
            v = 0.45 + k * 0.038
            px, py = bx + math.sin(a) * L * v, by - math.cos(a) * L * v
            nx, ny = math.cos(a), math.sin(a)
            line(d, cam, [(px - nx * 52, py - ny * 52 + 14), (px + nx * 52, py + ny * 52 - 14)], 7)
            line(d, cam, [(px + nx * 40, py + ny * 40), (px + nx * 70, py + ny * 40 - 22)], 5)
            line(d, cam, [(px - nx * 40, py - ny * 40), (px - nx * 70, py - ny * 40 + 22)], 5)
    text_layer(C, "ముళ్ల కర్రలు", 540, 420, 130, col="ink", maxw=860)


def s_wounded(C, T, D):
    u = T / D
    cam = Cam(540, 1000, 1.05 + 0.1 * ease(u))
    sky(C, cam, T, density=1.2)
    moon(C, cam, 760, 640, 120, T, ring=0.9)
    d = C.L("paper", rough=0.8)
    poly(d, cam, [(-400, 1400), (1480, 1380), (1480, 4000), (-400, 4000)])
    d = C.L("ink", rough=0.8, alpha=0.75)
    for i, x in enumerate([100, 210, 900, 1000]):
        soldier(d, cam, x, 1410, 480, dict(la=8, ra=-8), facing=1 if x < 540 else -1, rifle=True)
    ar = (70 + 6 * math.sin(T * 3), 12, -10)
    d = C.L("saff", rough=0.8)
    figure_front(d, cam.off(+10), 540, 1580, 1000, arms=ar, legs=10)
    d = C.L("ink", rough=0.8)
    figure_front(d, cam, 540, 1580, 1000, arms=ar, legs=10)
    r = np.random.default_rng(12)
    d = C.L("deep", rough=0.6)
    for k in range(10):
        tt = (T * 1.6 + r.random()) % 1
        x = 1300 - tt * 1500
        y = 500 + r.random() * 600 + tt * 300
        circ(d, cam, x, y, 14 + r.random() * 16)
        line(d, cam, [(x + 30, y - 6), (x + 200, y - 50)], 3)
    snow(C, cam, T, n=60)
    text_layer(C, "వెనక్కి తగ్గలేదు", 540, 420, 120, col="paper", maxw=860, outline="deep")


def s_moonhero(C, T, D, close=False):
    u = T / D
    s0 = 1.35 if close else 1.0
    cam = Cam(540, 1100 if not close else 1050, s0 + 0.08 * u)
    sky(C, cam, T, density=0.8)
    dim = 1 - 0.35 * u if close else 1
    moon(C, cam, 540, 1000, 420, T, ring=1.0, glow=dim)
    d = C.L("ink", rough=0.8)
    poly(d, cam, ridge(81, 1500, 80) + [(1480, 4000), (-400, 4000)])
    figure_front(d, cam, 540, 1540, 1050, arms=(9, 9, 5), legs=7)
    if close:
        d = C.L("paper", rough=1.0, alpha=0.8 * (1 - u))
        hx, hy = 560, 1540 - 0.92 * 1050
        ph = (T * 0.9) % 1
        circ(d, cam, hx + 80 + ph * 160, hy + 30 - ph * 60, 30 + ph * 60)
    snow(C, cam, T, n=60, size=0.9)
    if close:
        text_layer(C, "చివరి శ్వాస వరకు", 540, 1330, 112, col="paper", maxw=860, outline="deep")


def s_moonhero_close(C, T, D):
    s_moonhero(C, T, D, close=True)


def diya(d, cam, x, y, s):
    poly(d, cam, [(x - 60 * s, y), (x + 60 * s, y), (x + 30 * s, y + 38 * s), (x - 30 * s, y + 38 * s)])
    poly(d, cam, [(x + 55 * s, y), (x + 85 * s, y - 14 * s), (x + 62 * s, y + 10 * s)])


def s_diyas(C, T, D):
    u = T / D
    cam = Cam(540, 1000, 1.0 + 0.05 * u)
    sky(C, cam, T, density=0.6)
    n_lit = min(20, int(T / (D * 0.82) * 20) + 1)
    pos = []
    for row in range(4):
        for c in range(5):
            pos.append((180 + c * 180 + (row % 2) * 40 - 20, 760 + row * 190))
    d = C.L("saff", rough=1.3, alpha=0.4)
    for i in range(n_lit):
        x, y = pos[i]
        circ(d, cam, x + 10, y - 55, 70)
    d = C.L("paper", rough=0.7, alpha=0.9)
    for x, y in pos:
        diya(d, cam, x, y, 1.0)
    d = C.L("ink", rough=0.6, alpha=0.7)
    for x, y in pos:
        line(d, cam, [(x - 50, y + 10), (x + 50, y + 10)], 4)
    for i in range(n_lit):
        x, y = pos[i]
        fl = 1 + 0.12 * math.sin(T * 17 + i)
        dd = C.cur and None
    d = C.L("saff", rough=0.5)
    for i in range(n_lit):
        x, y = pos[i]
        fl = 1 + 0.12 * math.sin(T * 17 + i)
        poly(d, cam, [(x - 14, y - 6), (x + 14, y - 6), (x + 2, y - 70 * fl)])
    d = C.L("paper", rough=0.4)
    for i in range(n_lit):
        x, y = pos[i]
        poly(d, cam, [(x - 6, y - 8), (x + 6, y - 8), (x + 1, y - 34)])
    text_layer(C, str(n_lit), 540, 470, 230, col="saff", path=FONT_NUM)
    text_layer(C, "వీరులు", 540, 620, 80, col="paper")


def medal(C, cam, T, cx=540, cy=1020, R=300):
    # ribbon: half white half saffron (vertical split)
    d = C.L("ink", rough=0.7)
    poly(d, cam, [(cx - 170, 120), (cx + 170, 120), (cx + 170, cy - R - 20), (cx - 170, cy - R - 20)])
    d = C.L("saff", rough=0.6)
    poly(d, cam, [(cx - 156, 120), (cx, 120), (cx, cy - R - 32), (cx - 156, cy - R - 32)])
    d = C.L("paper", rough=0.6)
    poly(d, cam, [(cx, 120), (cx + 156, 120), (cx + 156, cy - R - 32), (cx, cy - R - 32)])
    d = C.L("ink", rough=0.7)
    line(d, cam, [(cx, cy - R - 20), (cx, cy - R + 30)], 26)
    star = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        rr = R if k % 2 == 0 else R * 0.45
        star.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    poly(d, cam, [(x + (x - cx) * 0.06, y + (y - cy) * 0.06) for x, y in star])
    d = C.L("paper", rough=0.5)
    poly(d, cam, star)
    # engraved facets
    d = C.L("ink", rough=0.4, alpha=0.55)
    for k in range(0, 10, 2):
        line(d, cam, [(cx, cy), star[k]], 6)
    # glint sweep
    d = C.L("saff", rough=0.4)
    for k, (px, py) in enumerate([(cx - R * 0.55, cy - R * 0.2), (cx + R * 0.6, cy + R * 0.35), (cx + R * 0.1, cy - R * 0.75)]):
        sz = 30 + 25 * abs(math.sin(T * 4 + k * 2))
        poly(d, cam, [(px, py - sz), (px + sz * 0.18, py), (px, py + sz), (px - sz * 0.18, py)])
        poly(d, cam, [(px - sz, py), (px, py + sz * 0.18), (px + sz, py), (px, py - sz * 0.18)])
    d = C.L("saff", rough=0.4)
    circ(d, cam, cx, cy, R * 0.26)
    d = C.L("paper", rough=0.4)
    circ(d, cam, cx, cy, R * 0.19)
    d = C.L("ink", rough=0.4)
    # tiny lion-capital emblem hint
    poly(d, cam, [(cx - 22, cy + 34), (cx + 22, cy + 34), (cx + 14, cy - 10), (cx - 14, cy - 10)])
    circ(d, cam, cx, cy - 22, 18)


def s_medal(C, T, D):
    u = T / D
    s = 0.8 + 0.2 * eout(T / 0.25)
    cam = Cam(540, 960, s + 0.06 * u)
    sky(C, cam, T, density=0.6)
    medal(C, cam, T)
    d = C.L("ink", rough=0.9)
    d.rectangle((60, 1250, 1020, 1430), fill=255)
    text_layer(C, "మహావీర్ చక్ర", 540, 1340, 120, col="saff", maxw=860)


def s_medal2(C, T, D):
    u = T / D
    cam = Cam(540, 860, 1.25 + 0.1 * u)
    sky(C, cam, T, density=0.6)
    medal(C, cam, T + 1)
    d = C.L("ink", rough=0.9)
    d.rectangle((60, 1230, 1020, 1440), fill=255)
    text_layer(C, "యుద్ధంలో 2వ", 540, 1290, 76, col="paper", maxw=860)
    text_layer(C, "అత్యున్నత పురస్కారం", 540, 1385, 76, col="saff", maxw=860)


def s_flag(C, T, D):
    u = T / D
    sky(C, Cam(), T, density=0.6)
    cam = Cam(540, 900, 1.0 + 0.05 * u)
    x0, x1, y0, h = 120, 1040, 470, 600
    bands = [("saff", 0), ("paper", 1), ("green", 2)]
    d = C.L("ink", rough=0.7)
    line(d, cam, [(100, 480), (100, 2000)], 22)
    for col, i in bands:
        d = C.L(col, rough=0.7)
        top, bot = [], []
        for k in range(40):
            v = k / 39
            x = x0 + (x1 - x0) * v
            wv = math.sin(v * 5 - T * 5) * 40 * v
            top.append((x, y0 + i * h / 3 + wv))
            bot.append((x, y0 + (i + 1) * h / 3 + wv))
        poly(d, cam, top + bot[::-1])
    # chakra
    d = C.L("ink", rough=0.4)
    v = 0.5
    wv = math.sin(v * 5 - T * 5) * 40 * v
    cx, cy = x0 + (x1 - x0) * v, y0 + h / 2 + wv
    circ(d, cam, cx, cy, 82, fill=None, outline=255, width=11)
    for k in range(24):
        a = k * math.pi / 12 + T * 0.3
        line(d, cam, [(cx, cy), (cx + 78 * math.cos(a), cy + 78 * math.sin(a))], 4)
    s = 1 + 0.25 * (1 - eout(T / 0.15))
    text_layer(C, "జై హింద్", 540, 1240, 170, col="paper", scale=s, maxw=860)
    if T > 0.9:
        text_layer(C, "కామెంట్‌లో చెప్పండి", 540, 1395, 72, col="saff", maxw=820)


SHOTS = {
    "standoff": s_standoff, "front": s_front_of_men, "milestone": s_milestone,
    "date": s_date, "valley": s_valley, "cold": s_cold,
    "tent": s_tent, "walk": s_walk, "name": s_name,
    "rifle": s_rifle, "rocks": s_rocks, "clubs": s_clubs,
    "wounded": s_wounded, "moonhero": s_moonhero, "moonclose": s_moonhero_close,
    "diyas": s_diyas, "medal": s_medal, "medal2": s_medal2, "flag": s_flag,
}
