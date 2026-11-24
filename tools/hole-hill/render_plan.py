#!/usr/bin/env python3
"""'The plan' (14 s): gold vinyl hero pins notes on a wall, crawls over maps, pins one more, lies on the floor planning, then the strings light up into one gold route.
Original scene (no third-party footage). The hero is rendered through the SAME pinhole camera as the room (perfect perspective match, real top-down/low/close shots).
usage: render_plan.py sheet OUT.png t... | frames OUTDIR [k] | video OUT.mp4 AUDIO.wav FRAMESDIR"""
import sys, os, math, random, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vinyl as V, hh_poses as HP

W, H = 1080, 1920; FPS = 30; DUR = 14.0; FO = 1400.0
TINT = (1.0, 0.74, 0.34)
FONT = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
def sm(x): x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t
def lv(a, b, t): return np.array([lerp(a[i], b[i], t) for i in range(3)], np.float32)
def nrm(v): v = np.array(v, np.float32); return v / (np.linalg.norm(v) + 1e-9)

# ------------------------------------------------------------------ shots / camera
CUTS = [3.0, 5.2, 6.6, 10.0, 11.4, 12.6]
SHOTS = [  # (t0, t1, C0, C1, T0, T1)
    (0.0, 3.0, (1000, 780, -1500), (720, 800, -1300), (-80, 820, 0), (120, 830, 0)),
    (3.0, 5.2, (-420, 1550, -1250), (380, 1450, -1000), (0, 0, -300), (0, 0, -300)),
    (5.2, 6.6, (430, 905, -760), (190, 905, -420), (30, 868, 0), (50, 868, 0)),
    (6.6, 10.0, (1500, 790, -1000), (1050, 810, -1250), (-250, 780, 0), (300, 800, 0)),
    (10.0, 11.4, (-950, 200, -1200), (-600, 170, -950), (0, 190, -300), (0, 210, -250)),
    (11.4, 12.6, (0, 930, -2650), (0, 880, -2150), (0, 860, 0), (0, 840, 0)),
    (12.6, 14.0, (0, 830, -2150), (0, 800, -1650), (0, 780, -100), (0, 770, -100)),
]
def shot_of(t):
    for i, s in enumerate(SHOTS):
        if s[0] <= t < s[1]: return i
    return len(SHOTS) - 1
def cam_state(t):
    s = SHOTS[shot_of(t)]; u = (t - s[0]) / (s[1] - s[0]); u = min(max(u, 0), 1)
    C = lv(s[2], s[3], u * (0.6 + 0.4 * u)); T = lv(s[4], s[5], u)
    C = C + np.array([3 * math.sin(t * 1.9), 2 * math.sin(t * 2.7), 0], np.float32)
    return C, T
CAM = {}
def set_cam(t):
    C, T = cam_state(t); r, u, f = V.lookat(C, T); CAM.update(C=C, T=T, r=r, u=u, f=f)
def to_cam(p):
    d = np.asarray(p, np.float32) - CAM["C"]; return np.array([d @ CAM["r"], d @ CAM["u"], d @ CAM["f"]], np.float32)
def scr(pc): return (W / 2 + FO * pc[0] / pc[2], H / 2 - FO * pc[1] / pc[2])
def proj_poly(pts):
    """project a 3D polygon, clipped against the near plane; returns screen points or None"""
    pc = [to_cam(p) for p in pts]; out = []; NEAR = 60.0
    for i in range(len(pc)):
        a, b = pc[i], pc[(i + 1) % len(pc)]; ina, inb = a[2] >= NEAR, b[2] >= NEAR
        if ina: out.append(a)
        if ina != inb:
            k = (NEAR - a[2]) / (b[2] - a[2]); out.append(a + (b - a) * k)
    return [scr(p) for p in out] if len(out) >= 3 else None
def P2(p):
    pc = to_cam(p); return scr(pc) if pc[2] > 60 else None

# ------------------------------------------------------------------ room content
rnd = random.Random(21)
NOTE_COLS = [(238, 232, 214), (206, 224, 236), (238, 214, 158), (226, 198, 196), (214, 232, 208)]
NOTES = []
for i in range(120):
    NOTES.append(dict(x=rnd.uniform(-1500, 1500), y=rnd.uniform(260, 1900), w=rnd.uniform(70, 150), h=rnd.uniform(90, 190), rot=rnd.uniform(-0.25, 0.25),
                      col=rnd.choice(NOTE_COLS) if rnd.random() < 0.8 else (60, 56, 62), lines=rnd.randint(2, 5), seed=i))
KP = [(-380, 930), (-120, 945), (180, 925), (420, 940), (60, 935)]       # key pins placed by the hero
KP_T = [0.62, 1.32, 2.02, 2.72, 6.0]                                     # when each appears
KP_THREADS = [(0, 1, 0.9, 0.4), (1, 2, 1.6, 0.4), (2, 3, 2.3, 0.4), (4, 1, 6.15, 0.35), (4, 2, 6.3, 0.35)]   # (a, b, start, dur)
EXIT = (800, 1180)
GOLD = [(0, 1), (1, 4), (4, 2), (2, 3)]
GOLD_T0 = 11.5
EV = [(-520, 650), (-250, 730), (60, 650), (330, 740), (600, 660)]    # evidence-board notes he links with red string
EV_LINKS = [(0, 1), (1, 2), (2, 3), (3, 4), (1, 3), (2, 4)]
EV_T0, EV_DT, EV_DUR = 6.8, 0.5, 0.42
def ev_pin_time(i): return 6.7 if i == 0 else min(EV_T0 + k * EV_DT + EV_DUR for k, (a, b) in enumerate(EV_LINKS) if b == i)
MAPS = [(-380, -300, 900, 620, 0.15, (214, 224, 232)), (330, -380, 860, 600, -0.2, (232, 222, 196)), (-60, -620, 940, 560, 0.05, (210, 226, 214)),
        (500, -700, 640, 480, 0.3, (228, 214, 214)), (-640, -640, 600, 460, -0.35, (222, 226, 238))]

def wall_light(x, y):
    g = 0.0
    for xs in (-460, 460): g += math.exp(-(((x - xs) / 520) ** 2 + ((y - 1000) / 760) ** 2) * 0.5)
    return 0.20 + 0.95 * min(g, 1.0)
def floor_light(x, z):
    return 0.14 + 0.95 * math.exp(-((x / 900) ** 2 + ((z + 420) / 760) ** 2) * 0.5)
def tint(col, k, warm=1.0):
    return (int(min(255, col[0] * k * (1.0 + 0.10 * warm))), int(min(255, col[1] * k)), int(min(255, col[2] * k * (1.0 - 0.18 * warm))))


def hash_np(a): return (np.sin(a * 12.9898) * 43758.5453) % 1.0
def wall_light_np(x, y):
    g = 0.0
    for xs in (-460, 460): g = g + np.exp(-(((x - xs) / 520) ** 2 + ((y - 1000) / 760) ** 2) * 0.5)
    return 0.10 + 1.0 * np.minimum(g, 1.0)
def floor_light_np(x, z): return 0.08 + 1.0 * np.exp(-((x / 900) ** 2 + ((z + 420) / 760) ** 2) * 0.5)
def base_bg():
    C, r, u, f = CAM["C"], CAM["r"], CAM["u"], CAM["f"]
    px = (np.arange(W, dtype=np.float32) - W / 2) / FO; py = -(np.arange(H, dtype=np.float32) - H / 2) / FO
    D = f[None, None, :] + px[None, :, None] * r[None, None, :] + py[:, None, None] * u[None, None, :]
    dx, dy, dz = D[..., 0], D[..., 1], D[..., 2]
    big = np.float32(1e9)
    with np.errstate(divide="ignore", invalid="ignore"):
        tw = np.where(dz > 1e-4, (0 - C[2]) / dz, big); xw = C[0] + tw * dx; yw = C[1] + tw * dy
        okw = (tw > 0) & (tw < big) & (yw >= 0) & (yw <= 2300) & (np.abs(xw) < 1800)
        tf = np.where(dy < -1e-4, (0 - C[1]) / dy, big); xf = C[0] + tf * dx; zf = C[2] + tf * dz
        okf = (tf > 0) & (tf < big) & (zf <= 0) & (zf > -3600) & (np.abs(xf) < 2000)
    use_w = okw & (~okf | (tw < tf)); use_f = okf & ~use_w
    out = np.zeros((H, W, 3), np.float32); out[:] = np.array([10, 8, 9], np.float32)
    lw = wall_light_np(xw, yw); panel = 1.0 + 0.10 * (hash_np(np.floor(xw / 120.0)) - 0.5) + 0.05 * np.sin(yw * 0.02 + xw * 0.004)
    wc = np.array([96, 78, 64], np.float32)[None, None, :] * (lw * panel)[..., None] * np.array([1.08, 1.0, 0.86], np.float32)
    lf = floor_light_np(xf, zf); pl = np.floor(xf / 170.0); joint = ((xf % 170.0) < 5.0).astype(np.float32); shade = 1.0 + 0.12 * (hash_np(pl) - 0.5)
    cross = (((zf + 5000) % 850.0) < 4.0).astype(np.float32) * (hash_np(pl + 3) > 0.5)
    fc = np.array([128, 88, 58], np.float32)[None, None, :] * (lf * shade * (1 - 0.65 * np.maximum(joint, cross)))[..., None] * np.array([1.08, 1.0, 0.86], np.float32)
    out = np.where(use_w[..., None], wc, out); out = np.where(use_f[..., None], fc, out)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB").convert("RGBA")

def draw_quad3(d, pts, fill, outline=None):
    q = proj_poly(pts)
    if q: d.polygon(q, fill=fill, outline=outline)
def note_pts(x, y, w, h, rot, z):
    c, s = math.cos(rot), math.sin(rot)
    return [(x + (a * c - b * s), y + (a * s + b * c), z) for a, b in ((-w / 2, h / 2), (w / 2, h / 2), (w / 2, -h / 2), (-w / 2, -h / 2))]
def draw_note(d, n, z=-5, pop=1.0, warm=1.0):
    k = float(wall_light_np(n["x"], n["y"])) * 1.05 + 0.05; col = tint(n["col"], min(k, 1.1), warm)
    pts = note_pts(n["x"], n["y"], n["w"] * pop, n["h"] * pop, n["rot"], z); draw_quad3(d, pts, col + (255,))
    r_ = random.Random(n["seed"]); c, s = math.cos(n["rot"]), math.sin(n["rot"])
    if n["col"] != (60, 56, 62):
        for j in range(n["lines"]):
            ly = n["h"] * (0.30 - 0.18 * j) * pop; lw = n["w"] * r_.uniform(0.4, 0.8) * pop; a = (-lw / 2, ly); b = (lw / 2, ly)
            p1 = (n["x"] + a[0] * c - a[1] * s, n["y"] + a[0] * s + a[1] * c, z - 0.5); p2 = (n["x"] + b[0] * c - b[1] * s, n["y"] + b[0] * s + b[1] * c, z - 0.5)
            q1, q2 = P2(p1), P2(p2)
            if q1 and q2: d.line([q1, q2], fill=(60, 52, 48, 255), width=max(1, int(2.2 * FO / max(to_cam(p1)[2], 60) * 0.6)))
def pin_dot(d, x, y, z=-9, col=(200, 36, 36)):
    p = P2((x, y, z))
    if p: r_ = max(3, 16 * FO / to_cam((x, y, z))[2]); d.ellipse([p[0] - r_, p[1] - r_, p[0] + r_, p[1] + r_], fill=col + (255,), outline=(70, 10, 10, 255))
def thread(d, a, b, prog, col=(190, 40, 40), wpx=3.0, z=-9):
    if prog <= 0: return
    x = lerp(a[0], b[0], prog); y = lerp(a[1], b[1], prog); p1, p2 = P2((a[0], a[1], z)), P2((x, y, z))
    if p1 and p2: d.line([p1, p2], fill=col + (255,), width=max(1, int(wpx * FO / to_cam((a[0], a[1], z))[2])))

def env(t, hero_floor):
    img = Image.new("RGBA", (W, H), (12, 10, 10, 255)); d = ImageDraw.Draw(img, "RGBA")
    img = base_bg(); d = ImageDraw.Draw(img, "RGBA")
    for n in NOTES: draw_note(d, n)
    # maps on the floor
    for (cx, cz, w, dd, rot, col) in MAPS:
        c, s = math.cos(rot), math.sin(rot)
        pts = [(cx + (a * c - b * s), 1.5, cz + (a * s + b * c)) for a, b in ((-w / 2, dd / 2), (w / 2, dd / 2), (w / 2, -dd / 2), (-w / 2, -dd / 2))]
        k = float(floor_light_np(cx, cz)) * 1.2 + 0.08; draw_quad3(d, pts, tint(col, min(k, 1.0)) + (255,), outline=(70, 60, 50, 255))
        rr = random.Random(int(abs(cx) + 7))
        for g in range(9):   # blueprint lines + route
            a1, b1 = rr.uniform(-w * .42, w * .42), rr.uniform(-dd * .42, dd * .42); a2, b2 = a1 + rr.uniform(-w * .3, w * .3), b1 + rr.uniform(-dd * .3, dd * .3)
            p1 = (cx + (a1 * c - b1 * s), 2, cz + (a1 * s + b1 * c)); p2 = (cx + (a2 * c - b2 * s), 2, cz + (a2 * s + b2 * c))
            q1, q2 = P2(p1), P2(p2)
            if q1 and q2: d.line([q1, q2], fill=(60, 80, 110, 255) if g % 3 else (190, 40, 40, 255), width=max(1, int(4 * FO / max(to_cam(p1)[2], 60))))
    # key notes + pins + threads
    for i, (px, py) in enumerate(KP):
        tp = KP_T[i]
        if t >= tp:
            pop = min(1.0, 0.6 + (t - tp) / 0.12 * 0.4) if t - tp < 0.12 else 1.0
            draw_note(d, dict(x=px, y=py, w=130, h=160, rot=(-0.1, 0.07, -0.05, 0.1, 0.03)[i], col=(246, 240, 220), lines=4, seed=300 + i), z=-8, pop=pop, warm=1.0)
            pin_dot(d, px, py + 54, z=-12)
    for (a, b, t0, dur) in KP_THREADS: thread(d, KP[a], KP[b], min(1.0, max(0.0, (t - t0) / dur)))
    # evidence board: notes + red strings pulled hand to hand
    for i, (px, py) in enumerate(EV):
        tp = ev_pin_time(i)
        if t >= tp:
            pop = min(1.0, 0.6 + (t - tp) / 0.12 * 0.4) if t - tp < 0.12 else 1.0
            draw_note(d, dict(x=px, y=py, w=120, h=150, rot=(0.08, -0.06, 0.1, -0.09, 0.05)[i], col=((246, 238, 200), (214, 232, 244), (246, 220, 214), (226, 240, 214), (246, 238, 200))[i], lines=4, seed=500 + i), z=-8, pop=pop)
            pin_dot(d, px, py + 50, z=-12)
    for k, (a, b) in enumerate(EV_LINKS):
        thread(d, EV[a], EV[b], min(1.0, max(0.0, (t - (EV_T0 + k * EV_DT)) / EV_DUR)), wpx=3.4)
    # exit door note (appears with the gold route)
    gp = GOLD_T0 + 0.35 * len(GOLD)
    if t > GOLD_T0 - 0.2:
        al = sm((t - (GOLD_T0 - 0.2)) / 0.5); ex, ey = EXIT
        pts = [(ex - 90, ey - 130, -8), (ex + 90, ey - 130, -8), (ex + 90, ey + 130, -8), (ex - 90, ey + 130, -8)]
        draw_quad3(d, pts, (250, 216, 130, int(255 * al)), outline=(120, 80, 20, int(255 * al)))
        draw_quad3(d, [(ex - 56, ey - 90, -9), (ex + 56, ey - 90, -9), (ex + 56, ey + 110, -9), (ex - 56, ey + 110, -9)], (255, 244, 200, int(255 * al)))
    # hero contact shadow on the floor
    if hero_floor is not None:
        hx, hz, rx, rz = hero_floor
        pts = [(hx + rx * math.cos(a), 1.0, hz + rz * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 28, endpoint=False)]
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh); q = proj_poly(pts)
        if q: sd.polygon(q, fill=(0, 0, 0, 95)); img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(22)))
    return img

def gold_layer(t):
    """glowing gold route over the wall: pin to pin, then to the exit door"""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay, "RGBA")
    if t < GOLD_T0: return lay
    pts = [KP[GOLD[0][0]]] + [KP[b] for (a, b) in GOLD] + [EXIT]
    n = len(pts) - 1; prog = (t - GOLD_T0) / 0.38
    for i in range(n):
        p = min(1.0, max(0.0, prog - i)); 
        if p <= 0: break
        a, b = pts[i], pts[i + 1]
        x, y = lerp(a[0], b[0], p), lerp(a[1], b[1], p); p1, p2 = P2((a[0], a[1], -14)), P2((x, y, -14))
        if p1 and p2: d.line([p1, p2], fill=(255, 205, 90, 255), width=max(8, int(24 * FO / to_cam((a[0], a[1], -14))[2])))
    return lay

# ------------------------------------------------------------------ hero
def loc_fn(pos, phi):
    c, s = math.cos(phi), math.sin(phi)
    def loc(p):
        d = np.asarray(p, np.float32) - np.asarray(pos, np.float32); return np.array([d[0] * c - d[2] * s, d[1], d[0] * s + d[2] * c], np.float32)
    return loc
def ik_arm(sh, tgt, l1, l2, pole):
    sd = tgt - sh; L = float(np.linalg.norm(sd)); d = sd / (L + 1e-9); L = min(L, l1 + l2 - 2)
    a = (l1 * l1 - l2 * l2 + L * L) / (2 * L); h = math.sqrt(max(l1 * l1 - a * a, 1.0))
    pv = nrm(pole); pv = nrm(pv - d * float(pv @ d)); el = sh + d * a + pv * h
    return nrm(el - sh), nrm(sh + d * L - el)
def set_arm(P, side, tgt_loc, amount=1.0):
    sk = V.skeleton(dict(P)); sh = sk["sh" + side]; sgn = -1 if side == "L" else 1
    ua, fa = ik_arm(sh, np.asarray(tgt_loc, np.float32), V.LEN["uarm"], V.LEN["farm"] + 34, (sgn * 0.6, -0.7, -0.3))
    cu, cf = np.array(P.get("ua" + side, HP.DEF["ua" + side]), np.float32), np.array(P.get("fa" + side, HP.DEF["fa" + side]), np.float32)
    P["ua" + side] = tuple(cu * (1 - amount) + ua * amount); P["fa" + side] = tuple(cf * (1 - amount) + fa * amount)
def bump(t, t0, w): return math.exp(-((t - t0) / w) ** 2)

def hero_state(t):
    P = {}; mood = "determined"; phi = 0.0; pos = np.array([0, 0, -150], np.float32); shadow = (0, -150, 170, 120)
    if t < 3.0:
        xs = [-280, -60, 130, 330]; hx = xs[0]
        for i in range(1, 4): hx = lerp(hx, xs[i], sm((t - (KP_T[i] - 0.5)) / 0.45))
        P = dict(V.POSES["stand"]); P["spine"] = (0, 1, 0.06); P["pelvis"] = (0, 470 - 6 * abs(math.sin(t * 6)), 0)
        pos = np.array([hx, 0, -110], np.float32); loc = loc_fn(pos, 0.0)
        for i in range(4):
            amt = bump(t, KP_T[i] - 0.05, 0.22)
            if amt > 0.02:
                tgt = np.array([KP[i][0], KP[i][1], -14], np.float32); side = "L" if KP[i][0] < hx else "R"
                set_arm(P, side, loc(tgt), min(1.0, amt * 1.2))
        shadow = (hx, -110, 170, 120)
    elif t < 5.2:
        u = (t - 3.0) / 2.2; pos = np.array([lerp(-60, 60, u), 0, -330], np.float32); phi = lerp(0.0, 0.35, u)
        P = dict(V.POSES["kneel_draw"]); loc = loc_fn(pos, phi)
        set_arm(P, "R", np.array([240 * math.sin((t - 3) * 3.4), 14, 400 + 90 * math.sin((t - 3) * 2.3)], np.float32), 1.0)
        set_arm(P, "L", np.array([-150, 14, 340 + 30 * math.sin((t - 3) * 2.0)], np.float32), 1.0)
        shadow = (pos[0], -330 - 100, 260, 230)
    elif t < 6.6:
        u = (t - 5.2) / 1.4; pos = np.array([-130, 0, -110], np.float32); P = dict(V.POSES["stand"]); P["spine"] = (0, 1, 0.1); loc = loc_fn(pos, 0.0)
        amt = sm(u / 0.5); tgt = np.array([KP[4][0] + 8 * math.sin(u * 14), KP[4][1] + 6 * math.cos(u * 11), -14], np.float32)
        set_arm(P, "R", loc(tgt), min(1.0, amt)); shadow = (-130, -110, 170, 120)
    elif t < 10.0:
        # evidence board: pull red string from note to note
        hand = np.array(EV[0], np.float32); side = "R"
        for k, (a, b) in enumerate(EV_LINKS):
            ts = EV_T0 + k * EV_DT
            if t >= ts + EV_DUR: hand = np.array(EV[b], np.float32)
            elif t >= ts:
                pa, pb = np.array(EV[a], np.float32), np.array(EV[b], np.float32); hand = pa + (pb - pa) * sm((t - ts) / EV_DUR); side = "R" if pb[0] >= pa[0] else "L"; break
            else:
                pa = np.array(EV[a], np.float32); hand = hand + (pa - hand) * sm((t - (ts - 0.1)) / 0.1); side = "R" if EV[b][0] >= EV[a][0] else "L"; break
        hx = float(hand[0]) * 0.88 + (60 if side == "L" else -60) * 0.0
        pos = np.array([hx, 0, -110], np.float32); P = dict(V.POSES["stand"]); P["spine"] = (0, 1, 0.08); P["pelvis"] = (0, 470 - 5 * abs(math.sin(t * 9)), 0); loc = loc_fn(pos, 0.0)
        set_arm(P, side, loc(np.array([hand[0], hand[1], -14], np.float32)), 1.0); shadow = (hx, -110, 170, 120)
    elif t < 11.4:
        u = (t - 10.0) / 1.4; P = dict(V.POSES["prone_write"]); pos = np.array([0, 0, -130], np.float32)
        set_arm(P, "R", np.array([210 + 45 * math.sin(t * 7.5), 8, 330 + 30 * math.cos(t * 7.5)], np.float32), 1.0)
        set_arm(P, "L", np.array([-180, 8, 300], np.float32), 1.0); shadow = (0, -420, 190, 380)
    elif t < 12.6:
        u = (t - 11.4) / 1.2; pos = np.array([0, 0, lerp(-240, -380, sm(u))], np.float32); P = dict(V.POSES["stand"]); mood = "determined"
        P["pelvis"] = (0, 470 - 3 * math.sin(t * 2.4), 0); shadow = (0, pos[2], 170, 120)
    else:
        u = (t - 12.6) / 1.4; pos = np.array([0, 0, -380], np.float32); phi = lerp(0.0, math.pi, sm(u / 0.65)); P = dict(V.POSES["stand"])
        mood = "determined" if u < 0.7 else "joy"; shadow = (0, -380, 170, 120)
    return P, mood, phi, pos, shadow

def render_hero(P, mood, phi, pos):
    loc = loc_fn(pos, phi); Cl, Tl = loc(CAM["C"]), loc(CAM["T"]); r, u, f = V.lookat(Cl, Tl)
    rgb, a = V.render(dict(P), mood, Cl, r, u, f, sprite=True, tint=TINT)
    return rgb, a

# ------------------------------------------------------------------ compose
_F = {}
def font(sz):
    if sz not in _F: _F[sz] = ImageFont.truetype(FONT, sz)
    return _F[sz]
def caption(img, t):
    """no captions (added by the user in the app); only the channel label"""
    d = ImageDraw.Draw(img, "RGBA"); lab = "S L O W   L I G H T"; w = d.textlength(lab, font=font(30))
    d.text(((W - w) / 2, 1822), lab, font=font(30), fill=(255, 255, 255, 215), stroke_width=3, stroke_fill=(10, 10, 14, 170))
def whip(arr, t):
    for c in CUTS[:-1]:
        for side, dt in ((-1, c - t), (1, t - c)):
            if 0 <= dt < 0.14:
                p = 1 - dt / 0.14; L = int(8 + 150 * p * p); k = np.zeros((1, L), np.float32); k[0, :] = 1.0 / L
                return cv2.filter2D(arr, -1, k, borderType=cv2.BORDER_REFLECT) * (1 + 0.25 * p)
    return arr
def frame(t):
    set_cam(t); si = shot_of(t)
    P, mood, phi, pos, sh = hero_state(t)
    e = env(t, sh)
    g = gold_layer(t); glow = g.filter(ImageFilter.GaussianBlur(22)); e.alpha_composite(glow); e.alpha_composite(glow); e.alpha_composite(glow); e.alpha_composite(g)
    blur = {0: 1.2, 1: 1.5, 2: 6.0, 3: 1.6, 4: 3.0, 5: 1.0, 6: 1.5}[si]
    if blur > 0.5: e = e.filter(ImageFilter.GaussianBlur(blur))
    rgb, a = render_hero(P, mood, phi, pos)
    hero = np.dstack([np.clip(rgb * 255, 0, 255), a[..., None] * 255]).astype(np.uint8)
    # warm rim behind the hero
    A = Image.fromarray(hero[..., 3], "L"); glow_l = Image.new("RGBA", (W, H), (255, 190, 110, 0)); glow_l.putalpha(A.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * 0.28)))
    e.alpha_composite(glow_l); e.alpha_composite(Image.fromarray(hero, "RGBA"))
    arr = np.asarray(e.convert("RGB"), np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vig = np.clip(1 - 0.5 * (((xx - W / 2) / (W * 0.72)) ** 2 + ((yy - H * 0.48) / (H * 0.7)) ** 2), 0.25, 1.0); arr = arr * vig[..., None]
    arr = arr + np.random.RandomState(int(t * 30)).randn(H, W, 1).astype(np.float32) * 4.0
    arr = whip(arr, t)
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB").convert("RGBA"); caption(img, t); return img.convert("RGB")

def _job(a):
    i, t, out, k = a; V.RES["k"] = k; frame(t).save(f"{out}/f{i:04d}.png", compress_level=1); return i
if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "sheet":
        V.RES["k"] = 2; ts = [float(a) for a in sys.argv[3:]]; cols = min(len(ts), 6); rows = math.ceil(len(ts) / cols); tw, th_ = 270, 480
        sheet = Image.new("RGB", (tw * cols, th_ * rows))
        for j, t in enumerate(ts): sheet.paste(frame(t).resize((tw, th_), Image.LANCZOS), ((j % cols) * tw, (j // cols) * th_))
        sheet.save(sys.argv[2]); print("wrote", sys.argv[2])
    elif cmd == "frames":
        from multiprocessing import Pool
        out = sys.argv[2]; k = int(sys.argv[3]) if len(sys.argv) > 3 else 1; os.makedirs(out, exist_ok=True)
        jobs = [(i, i / FPS, out, k) for i in range(int(DUR * FPS)) if not os.path.exists(f"{out}/f{i:04d}.png")]
        with Pool(4) as p:
            for n, i in enumerate(p.imap_unordered(_job, jobs)):
                if n % 20 == 0: print(n, "/", len(jobs), flush=True)
    elif cmd == "video":
        out, audio, fr = sys.argv[2:5]
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{fr}/f%04d.png", "-i", audio, "-t", str(DUR), "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True); print("wrote", out)
