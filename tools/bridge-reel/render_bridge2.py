#!/usr/bin/env python3
"""'Who tries harder' (12 s, 1080x1920): the bridge story in the polished navy + gold theme (gold title, glowing cream stickmen, gold plank squares, DAY counter).
Top: BOTH BUILD with long strides, bridge meets, hug. Bottom: ONE BUILDS (she scrolls, he builds alone, too far, slumps). SFX only.
usage: render_bridge2.py sheet OUT.png t... | frames OUTDIR | video OUT.mp4 AUDIO.wav FRAMESDIR"""
import sys, os, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920; FPS = 30; DUR = 12.0; SS = 2
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
INTER_XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"; INTER_B = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
def sm(x): x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t
GOLD = (255, 196, 96); CREAM = (252, 246, 232)

# ------------------------------------------------------------------ layout (final pixels)
TOP_Y = 940          # top panel deck line
BOT_Y = 1640         # bottom panel deck line
LED_TOP = (270, 810) # inner ledge edges (top panel)
LED_BOT = (300, 780)
NPL = 18             # planks across the top gap (9 per side, 3 per stride)
KT, KB = 1.65, 1.12  # figure scale top / bottom

# ------------------------------------------------------------------ stick figure (FK, units)
LT, LTH, LSH, LUA, LFA = 62.0, 38.0, 38.0, 28.0, 27.0
HEAD_R = 17.0
POSES = {
    "stand": dict(lean=4, thF=6, shF=3, thB=-5, shB=-6, uaF=8, faF=12, uaB=2, faB=8, tilt=0),
    "kneel": dict(lean=38, thF=82, shF=4, thB=-8, shB=-88, uaF=62, faF=18, uaB=40, faB=10, tilt=10),
    "reach": dict(lean=12, thF=10, shF=4, thB=-8, shB=-8, uaF=92, faF=92, uaB=6, faB=10, tilt=-4),
    "phone": dict(lean=8, thF=5, shF=2, thB=-6, shB=-6, uaF=48, faF=132, uaB=6, faB=10, tilt=18),
    "hold": dict(lean=3, thF=5, shF=2, thB=-5, shB=-5, uaF=40, faF=86, uaB=6, faB=8, tilt=-6),
    "hug": dict(lean=2, thF=4, shF=2, thB=-4, shB=-4, uaF=118, faF=170, uaB=100, faB=165, tilt=-8),
    "slump": dict(lean=64, thF=88, shF=6, thB=-8, shB=-88, uaF=70, faF=40, uaB=60, faB=30, tilt=28),
}
def walk_pose(ph, amp=1.6):
    s, c = math.sin(ph), math.cos(ph)
    return dict(lean=7, thF=32 * s * amp, shF=32 * s * amp - 26 * max(0, c) * amp, thB=-32 * s * amp, shB=-32 * s * amp - 26 * max(0, -c) * amp,
                uaF=-30 * s, faF=-30 * s + 12, uaB=30 * s, faB=30 * s + 12, tilt=0)
def mix(a, b, u): return {k: lerp(a[k], b[k], u) for k in a}
def joints(p, f):
    def seg(o, L, a): return (o[0] + f * L * math.sin(math.radians(a)), o[1] + L * math.cos(math.radians(a)))
    hip = (0.0, 0.0); kF = seg(hip, LTH, p["thF"]); aF = seg(kF, LSH, p["shF"]); kB = seg(hip, LTH, p["thB"]); aB = seg(kB, LSH, p["shB"])
    low = max(aF[1], aB[1], kF[1] if p["thF"] > 60 else -1e9, kB[1] if (p["thB"] > 60 or p["shB"] < -70) else -1e9); dy = -low
    kF, aF, kB, aB, hip = [(a, b + dy) for a, b in (kF, aF, kB, aB, hip)]
    neck = (hip[0] + f * LT * math.sin(math.radians(p["lean"])), hip[1] - LT * math.cos(math.radians(p["lean"])))
    sh = (hip[0] + 0.9 * (neck[0] - hip[0]), hip[1] + 0.9 * (neck[1] - hip[1])); hd = math.radians(p["lean"] + p["tilt"])
    head = (neck[0] + f * (HEAD_R + 1) * math.sin(hd), neck[1] - (HEAD_R + 1) * math.cos(hd))
    eF = seg(sh, LUA, p["uaF"]); wF = seg(eF, LFA, p["faF"]); eB = seg(sh, LUA, p["uaB"]); wB = seg(eB, LFA, p["faB"])
    return dict(hip=hip, neck=neck, sh=sh, head=head, kF=kF, aF=aF, kB=kB, aB=aB, eF=eF, wF=wF, eB=eB, wB=wB)
def draw_fig(d, x, ground, f, p, k, col, ponytail=False, S=SS, silhouette=False):
    J = joints(p, f); T = lambda q: ((x + q[0] * k) * S, (ground + q[1] * k) * S)
    wl = 12 * k * S
    def L(pts, w):
        P = [T(q) for q in pts]; d.line(P, fill=col, width=int(w), joint="curve")
        for a, b in P: d.ellipse([a - w / 2, b - w / 2, a + w / 2, b + w / 2], fill=col)
    L([J["sh"], J["eB"], J["wB"]], wl * 0.95); L([J["hip"], J["kB"], J["aB"]], wl * 0.95); L([J["hip"], J["sh"]], wl * 1.12)
    L([J["hip"], J["kF"], J["aF"]], wl); L([J["sh"], J["eF"], J["wF"]], wl)
    hx, hy = T(J["head"]); r_ = HEAD_R * k * S
    d.ellipse([hx - r_, hy - r_, hx + r_, hy + r_], fill=col)
    if ponytail:
        bx, by = hx - f * r_ * 0.95, hy - r_ * 0.55; r2 = r_ * 0.42; d.ellipse([bx - r2, by - r2, bx + r2, by + r2], fill=col)
        d.line([(bx, by), (bx - f * r_ * 0.5, by + r_ * 0.9)], fill=col, width=int(r_ * 0.4))
    return J

# ------------------------------------------------------------------ background
_BG = {}
def bg():
    if "a" in _BG: return _BG["a"].copy()
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    img = np.repeat(np.array([26, 28, 44], np.float32) * (1 - yy) + np.array([16, 18, 30], np.float32) * yy, W, axis=1)
    xx, y2 = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
    glow = np.exp(-(((xx - 540) / 520) ** 2 + ((y2 - 700) / 520) ** 2)); img = img + glow[..., None] * np.array([34, 26, 14], np.float32)
    rng = np.random.RandomState(4)
    for _ in range(90):
        x, y = rng.randint(0, W), rng.randint(0, H); img[y:y + 2, x:x + 2] += rng.randint(14, 30)
    _BG["a"] = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB").convert("RGBA"); return _BG["a"].copy()
def ledge(d, x0, x1, y, S=SS, inner="r"):
    d.rectangle([x0 * S, y * S, x1 * S, (y + 46) * S], fill=(72, 78, 98, 255)); d.rectangle([x0 * S, (y + 46) * S, x1 * S, (y + 300) * S], fill=(30, 34, 50, 255))
    d.line([(x0 * S, y * S), (x1 * S, y * S)], fill=(150, 158, 182, 255), width=int(3 * S)); d.line([(x0 * S, (y + 46) * S), (x1 * S, (y + 46) * S)], fill=(110, 118, 142, 160), width=int(2 * S))
    xi = x1 if inner == "r" else x0; d.line([(xi * S, y * S), (xi * S, (y + 300) * S)], fill=(120, 130, 160, 130), width=int(2 * S))
def planks(d, x0, n, step, y, direction, size=31, S=SS):
    for i in range(n):
        px = x0 + direction * step * i; xa, xb = (px, px + size) if direction > 0 else (px - size, px)
        d.rounded_rectangle([xa * S, (y + 2) * S, xb * S, (y + 2 + size) * S], radius=int(6 * S), fill=(255, 190, 78, 255))
        d.rounded_rectangle([xa * S, (y + 2 + size * 0.55) * S, xb * S, (y + 2 + size) * S], radius=int(6 * S), fill=(214, 130, 34, 255))
        d.rounded_rectangle([(xa + 3) * S, (y + 5) * S, (xb - 3) * S, (y + 11) * S], radius=int(3 * S), fill=(255, 228, 150, 220))

# ------------------------------------------------------------------ timeline
def top_state(t):
    """both builders: cycles of 3 planks (kneel + long stride)"""
    CY, KN = 1.4, 0.8; t0 = 0.6
    gap = LED_TOP[1] - LED_TOP[0]; step = gap / NPL; per_side = NPL // 2
    tt = max(0.0, t - t0); n = int(tt / CY); f = (tt % CY) / CY
    out = []
    for side in (1, -1):
        stride = 3 * step; base = LED_TOP[0] if side > 0 else LED_TOP[1]
        if n >= 3:   # done: stand at the middle
            planted = per_side; pose = POSES["stand"]; x = base + side * (per_side * step) - side * 40
        else:
            kn = KN / CY
            if f < kn:
                u = f / kn; planted = n * 3 + int(u * 3.4); pose = mix(POSES["stand"], POSES["kneel"], sm(u / 0.2)) if u < 0.9 else mix(POSES["kneel"], POSES["stand"], sm((u - 0.9) / 0.1)); x = base + side * stride * n
            else:
                u = (f - kn) / (1 - kn); planted = n * 3 + 3; pose = walk_pose(u * 2 * math.pi, 1.6); x = base + side * stride * (n + sm(u))
            planted = min(planted, per_side)
        out.append((side, base, planted, x, pose))
    return out
def bottom_state(t):
    CY, KN = 1.9, 1.15; t0 = 0.8; gap = LED_BOT[1] - LED_BOT[0]; step = (gap / NPL) * 0.9
    tt = max(0.0, t - t0); n = int(tt / CY); f = (tt % CY) / CY; stride = 3 * step; base = LED_BOT[1]
    if n >= 3:
        planted = 9; x = base - stride * 3
        pose = mix(POSES["stand"], POSES["reach"], sm((t - (t0 + 3 * CY)) / 0.6)) if t < 8.4 else mix(POSES["reach"], POSES["slump"], sm((t - 8.4) / 0.9))
    else:
        kn = KN / CY
        if f < kn:
            u = f / kn; planted = n * 3 + int(u * 3.4); pose = mix(POSES["stand"], POSES["kneel"], sm(u / 0.2)) if u < 0.9 else mix(POSES["kneel"], POSES["stand"], sm((u - 0.9) / 0.1)); x = base - stride * n
        else:
            u = (f - kn) / (1 - kn); planted = n * 3 + 3; pose = walk_pose(u * 2 * math.pi, 1.5); x = base - stride * (n + sm(u))
        planted = min(planted, 9)
    return planted, step, x, pose

# ------------------------------------------------------------------ text helpers
_F = {}
def font(path, sz):
    k = (path, int(sz))
    if k not in _F: _F[k] = ImageFont.truetype(path, int(sz))
    return _F[k]
def spaced(d, xy, s, f, fill, ls, anchor="l"):
    w = sum(d.textlength(c, font=f) + ls for c in s) - ls; x, y = xy
    if anchor == "c": x -= w / 2
    for c in s: d.text((x, y), c, font=f, fill=fill); x += d.textlength(c, font=f) + ls
def typed(s, t0, cps, t): return s[:max(0, min(len(s), int((t - t0) * cps)))]
def day_n(t): return 1 + int(364 * sm((t - 0.5) / 4.7)) if t < 5.2 else 365

def frame(t):
    base = bg()
    S = SS; big = (W * S, H * S)
    plk = Image.new("RGBA", big, (0, 0, 0, 0)); pd = ImageDraw.Draw(plk)
    fig = Image.new("RGBA", big, (0, 0, 0, 0)); fd = ImageDraw.Draw(fig)
    # ---- top panel
    ledge(pd, 0, LED_TOP[0], TOP_Y, inner="r"); ledge(pd, LED_TOP[1], W, TOP_Y, inner="l")
    gap = LED_TOP[1] - LED_TOP[0]; step = gap / NPL
    st = top_state(t); met = t > 0.6 + 3 * 1.4 + 0.05
    figs_top = []
    for (side, b, planted, x, pose) in st:
        planks(pd, b if side > 0 else b, planted, step, TOP_Y, side, size=step - 3)
    if met:
        u = sm((t - 5.0) / 0.9); hugu = sm((t - 5.7) / 0.6); mid = (LED_TOP[0] + LED_TOP[1]) / 2
        xl, xr = lerp(st[0][3], mid - 36, u), lerp(st[1][3], mid + 36, u)
        pl = mix(POSES["stand"], POSES["hold"], hugu) if t > 5.7 else mix(POSES["stand"], POSES["reach"], u * 0.5)
        figs_top = [(xl, 1, pl, True), (xr, -1, pl, False)]
    else:
        figs_top = [(st[0][3], 1, st[0][4], True), (st[1][3], -1, st[1][4], False)]
    for (x, f, p, pt) in figs_top: draw_fig(fd, x, TOP_Y + 2, f, p, KT, CREAM + (255,), ponytail=pt)
    # ---- bottom panel
    ledge(pd, 0, LED_BOT[0], BOT_Y, inner="r"); ledge(pd, LED_BOT[1], W, BOT_Y, inner="l")
    planted, bstep, bx, bpose = bottom_state(t); gapb = LED_BOT[1] - LED_BOT[0]
    planks(pd, LED_BOT[1], planted, bstep, BOT_Y, -1, size=bstep - 3)
    dim = (214, 216, 232, 255)
    ps = mix(POSES["stand"], POSES["phone"], sm((t - 0.3) / 0.5)); Js = draw_fig(fd, 205, BOT_Y + 2, 1, ps, KB, (214, 218, 236, 255), ponytail=True)
    draw_fig(fd, bx, BOT_Y + 2, -1, bpose, KB, (214, 218, 236, 255))
    # downscale layers
    plk1 = plk.resize((W, H), Image.LANCZOS); fig1 = fig.resize((W, H), Image.LANCZOS)
    # glow behind the figures (warm on top, cool on bottom)
    A = fig1.split()[3]
    wk = 0.55 + 0.35 * sm((t - 5.7) / 0.6)
    aw = np.asarray(A.filter(ImageFilter.GaussianBlur(22)), np.float32).copy(); aw[1180:] = 0
    gl_w = Image.new("RGBA", (W, H), (255, 214, 150, 0)); gl_w.putalpha(Image.fromarray((aw * wk).astype(np.uint8), "L")); base.alpha_composite(gl_w)
    ac = np.asarray(A.filter(ImageFilter.GaussianBlur(16)), np.float32).copy(); ac[:1200] = 0
    gl_c = Image.new("RGBA", (W, H), (190, 205, 255, 0)); gl_c.putalpha(Image.fromarray((ac * 0.30).astype(np.uint8), "L")); base.alpha_composite(gl_c)
    if t > 5.6:   # gold bloom behind the hug
        bl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); mid = (LED_TOP[0] + LED_TOP[1]) // 2; a = sm((t - 5.6) / 0.8) * (0.8 + 0.2 * math.sin(t * 3))
        ImageDraw.Draw(bl).ellipse([mid - 260, 520, mid + 260, 1000], fill=(255, 190, 90, int(70 * a))); base.alpha_composite(bl.filter(ImageFilter.GaussianBlur(70)))
    base.alpha_composite(plk1)
    # reflections of the figures on the ledge slabs
    for (yl, hh) in ((TOP_Y, 120), (BOT_Y, 90)):
        strip = fig1.crop((0, yl - hh, W, yl + 2)).transpose(Image.FLIP_TOP_BOTTOM); a = np.asarray(strip, np.float32).copy()
        a[..., 3] *= np.linspace(0.22, 0.0, a.shape[0], dtype=np.float32)[:, None]; base.alpha_composite(Image.fromarray(a.astype(np.uint8), "RGBA"), (0, yl + 4))
    base.alpha_composite(fig1)
    # phone glow (bottom)
    if t > 0.45:
        pw_ = (205 + Js["wF"][0] * KB + 6, BOT_Y + 2 + Js["wF"][1] * KB - 4); a = sm((t - 0.45) / 0.4) * (0.85 + 0.15 * math.sin(t * 6)); gp = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(gp)
        gd.ellipse([pw_[0] - 40, pw_[1] - 40, pw_[0] + 40, pw_[1] + 40], fill=(80, 130, 255, int(130 * a))); base.alpha_composite(gp.filter(ImageFilter.GaussianBlur(14)))
        ImageDraw.Draw(base).rounded_rectangle([pw_[0] - 6, pw_[1] - 10, pw_[0] + 6, pw_[1] + 10], radius=3, fill=(240, 246, 255, 255), outline=(60, 90, 170, 255))
    # ---- text
    img = base.convert("RGB"); d = ImageDraw.Draw(img)
    # gold gradient title
    tl = Image.new("L", (W, 140), 0); ImageDraw.Draw(tl).text((W / 2, 70), "WHO TRIES HARDER", font=font(INTER_XB, 80), fill=255, anchor="mm")
    gcol = np.zeros((140, W, 3), np.float32); gg = np.linspace(0, 1, 140, dtype=np.float32)[:, None, None]
    gcol[:] = np.array([255, 214, 130], np.float32) * (1 - gg) + np.array([246, 164, 56], np.float32) * gg
    img.paste(Image.fromarray(gcol.astype(np.uint8), "RGB"), (0, 235), tl)
    d.text((W / 2, 395), "IN YOUR RELATIONSHIP?", font=font(INTER_XB, 58), fill=(246, 244, 240), anchor="mm")
    # panel labels
    spaced(d, (130, 535), "BOTH BUILD", font(MONO, 42), (232, 232, 238), 9)
    s = typed("PLANK BY PLANK", 0.4, 12, t) if t < 5.0 else (typed("THEY MEET", 5.0, 14, t) if t < 5.7 else typed("HOLD ON", 5.7, 12, t))
    if s: spaced(d, (132, 590), s, font(MONO, 26), (170, 174, 196), 5)
    # DAY counter between the panels
    n = day_n(t); col = GOLD if n >= 365 else (236, 236, 242)
    d.line([(0, 1170), (W, 1170)], fill=(40, 44, 64), width=2); d.line([(0, 1262), (W, 1262)], fill=(40, 44, 64), width=2)
    d.text((540 - 78, 1216), "DAY", font=font(MONO, 30), fill=(150, 154, 176), anchor="mm"); d.text((540 + 52, 1216), str(n), font=font(INTER_B, 58), fill=col, anchor="mm")
    spaced(d, (130, 1300), "ONE BUILDS", font(MONO, 42), (140, 144, 164), 9)
    if t < 0.8: s2, c2 = "", None
    elif t < 2.4: s2, c2 = typed("HE BUILDS", 0.8, 10, t), None
    elif t < 7.2: s2, c2 = typed("SHE SCROLLS", 2.4, 11, t), None
    elif t < 8.4: s2, c2 = typed("TOO FAR", 7.2, 9, t), (240, 90, 90)
    else: s2, c2 = typed("ALONE", 8.4, 8, t), (240, 90, 90)
    if s2: spaced(d, (132, 1355), s2, font(MONO, 26), c2 or (130, 134, 154), 5)
    # dimension line + final message
    if t < 9.2:
        yy = 1760; d.line([(LED_BOT[0] + 14, yy), (LED_BOT[1] - 14, yy)], fill=(110, 120, 170), width=2)
        for x_ in range(LED_BOT[0] + 14, LED_BOT[1] - 14, 22): d.line([(x_, yy), (x_ + 10, yy)], fill=(18, 20, 34), width=3)
        d.polygon([(LED_BOT[0] + 14, yy), (LED_BOT[0] + 30, yy - 8), (LED_BOT[0] + 30, yy + 8)], fill=(120, 130, 180)); d.polygon([(LED_BOT[1] - 14, yy), (LED_BOT[1] - 30, yy - 8), (LED_BOT[1] - 30, yy + 8)], fill=(120, 130, 180))
        spaced(d, (540, 1790), (f"{n} DAY OF TRYING" if n == 1 else f"{n} DAYS OF TRYING"), font(MONO, 28), (150, 160, 215), 4, "c")
    else:
        m = typed("ONE PERSON CAN'T BUILD A BRIDGE FOR TWO.", 9.2, 18, t)
        spaced(d, (540, 1775), m, font(MONO, 26), GOLD, 3, "c")
    spaced(d, (540, 1884), "S L O W   L I G H T", font(MONO, 22), (92, 96, 118), 2, "c")
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
