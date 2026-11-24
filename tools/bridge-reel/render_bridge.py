#!/usr/bin/env python3
"""'Love is a bridge' replica (14 s, 1080x1920). Two stacked panels on black: BOTH BUILD (white glowing stickmen meet in the middle, red heart) vs ONE BUILDS (she scrolls, he builds alone).
Same layout, palette and beats as the reference; drawn procedurally.   usage: render_bridge.py sheet OUT.png t... | frames OUTDIR | video OUT.mp4 AUDIO.wav FRAMESDIR"""
import sys, os, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920; FPS = 30; DUR = 14.0
K = 1.5                       # reference is 720x1280; everything scaled x1.5
SS = 2                        # panel supersampling
PW, PH = 612, 358             # panel size in reference pixels
PX, PY1, PY2 = 55, 273, 672   # panel origins in reference pixels
HZ = 252                      # horizon / bridge deck y inside the panel
LE, RE = 95, 517              # inner cliff edges (where bridges start)
MID = (LE + RE) / 2
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
def sm(x): x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t

# ------------------------------------------------------------------ stick figure (FK)
LT, LTH, LSH, LUA, LFA = 62.0, 38.0, 38.0, 28.0, 27.0
HEAD_R = 17.0
POSES = {
    "stand": dict(lean=4, thF=6, shF=3, thB=-5, shB=-6, uaF=8, faF=12, uaB=2, faB=8, tilt=0),
    "kneel": dict(lean=38, thF=82, shF=4, thB=-8, shB=-88, uaF=62, faF=18, uaB=40, faB=10, tilt=10),
    "reach": dict(lean=12, thF=10, shF=4, thB=-8, shB=-8, uaF=92, faF=92, uaB=6, faB=10, tilt=-4),
    "phone": dict(lean=8, thF=5, shF=2, thB=-6, shB=-6, uaF=48, faF=132, uaB=6, faB=10, tilt=18),
    "hug": dict(lean=2, thF=4, shF=2, thB=-4, shB=-4, uaF=118, faF=170, uaB=100, faB=165, tilt=-8),
    "slump": dict(lean=64, thF=88, shF=6, thB=-8, shB=-88, uaF=70, faF=40, uaB=60, faB=30, tilt=28),
}
def walk_pose(ph, amp=1.0):
    s, c = math.sin(ph), math.cos(ph)
    return dict(lean=5, thF=30 * s * amp, shF=30 * s * amp - 24 * max(0, c) * amp, thB=-30 * s * amp, shB=-30 * s * amp - 24 * max(0, -c) * amp,
                uaF=-22 * s, faF=-22 * s + 10, uaB=22 * s, faB=22 * s + 10, tilt=0)
def mix(a, b, u): return {k: lerp(a[k], b[k], u) for k in a}
def figure_points(x, ground, f, p):
    """returns joint dict in panel coords; ground = y of the floor under the figure"""
    def seg(origin, L, ang_down): return (origin[0] + f * L * math.sin(math.radians(ang_down)), origin[1] + L * math.cos(math.radians(ang_down)))
    hip = (x, 0.0)
    kF = seg(hip, LTH, p["thF"]); aF = seg(kF, LSH, p["shF"]); kB = seg(hip, LTH, p["thB"]); aB = seg(kB, LSH, p["shB"])
    low = max(aF[1] + 3, aB[1] + 3, kF[1] + 5 if p["thF"] > 60 else -1e9, kB[1] + 5 if p["thB"] > 60 or p["shB"] < -70 else -1e9)
    dy = ground - low; hip = (x, dy)
    kF = (kF[0], kF[1] + dy); aF = (aF[0], aF[1] + dy); kB = (kB[0], kB[1] + dy); aB = (aB[0], aB[1] + dy)
    neck = (hip[0] + f * LT * math.sin(math.radians(p["lean"])), hip[1] - LT * math.cos(math.radians(p["lean"])))
    sh = (hip[0] + 0.9 * (neck[0] - hip[0]), hip[1] + 0.9 * (neck[1] - hip[1]))
    hd = math.radians(p["lean"] + p["tilt"]); head = (neck[0] + f * (HEAD_R + 1) * math.sin(hd), neck[1] - (HEAD_R + 1) * math.cos(hd))
    eF = seg(sh, LUA, p["uaF"]); wF = seg(eF, LFA, p["faF"]); eB = seg(sh, LUA, p["uaB"]); wB = seg(eB, LFA, p["faB"])
    return dict(hip=hip, neck=neck, sh=sh, head=head, kF=kF, aF=aF, kB=kB, aB=aB, eF=eF, wF=wF, eB=eB, wB=wB)
def draw_figure(d, S, x, ground, f, p, fill, outline, bun=False, glow_d=None):
    J = figure_points(x, ground, f, p)
    def L(pts, w, col):
        d.line([(a * S, b * S) for a, b in pts], fill=col, width=int(w * S), joint="curve")
        for a, b in pts: d.ellipse([a * S - w * S / 2, b * S - w * S / 2, a * S + w * S / 2, b * S + w * S / 2], fill=col)
    layers = [([J["sh"], J["eB"], J["wB"]], 11), ([J["hip"], J["kB"], J["aB"], (J["aB"][0] + f * 11, J["aB"][1])], 11), ([J["hip"], J["sh"]], 13),
              ([J["hip"], J["kF"], J["aF"], (J["aF"][0] + f * 11, J["aF"][1])], 11), ([J["sh"], J["eF"], J["wF"]], 11)]
    for pts, w in layers:
        L(pts, w + 6, outline); L(pts, w, fill)
        if glow_d is not None: L(pts, w + 4, (255, 255, 255, 255))
    hx, hy = J["head"]
    if bun:
        bx, by = hx - f * 14, hy - 8; d.ellipse([(bx - 8) * S, (by - 8) * S, (bx + 8) * S, (by + 8) * S], fill=fill, outline=outline, width=int(3 * S))
    d.ellipse([(hx - HEAD_R) * S, (hy - HEAD_R) * S, (hx + HEAD_R) * S, (hy + HEAD_R) * S], fill=fill, outline=outline, width=int(3 * S))
    if glow_d is not None:
        glow_d.ellipse([(hx - HEAD_R - 2) * S, (hy - HEAD_R - 2) * S, (hx + HEAD_R + 2) * S, (hy + HEAD_R + 2) * S], fill=(255, 255, 255, 255))
        for pts, w in layers: glow_d.line([(a * S, b * S) for a, b in pts], fill=(255, 255, 255, 255), width=int((w + 6) * S), joint="curve")
    return J

# ------------------------------------------------------------------ panel background
_BG = {}
def panel_bg():
    if "bg" in _BG: return _BG["bg"].copy()
    w, h = PW * SS, PH * SS
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    top = np.array([15, 16, 25], np.float32); base = np.array([13, 15, 26], np.float32)
    img = np.repeat(top * (1 - yy) + base * yy, w, axis=1)
    void = np.array([[12, 14, 24], [28, 38, 68]], np.float32)
    ys = int(HZ * SS); vv = np.linspace(0, 1, h - ys, dtype=np.float32)[:, None, None]
    img[ys:] = np.repeat(void[0] * (1 - vv) + void[1] * vv, w, axis=1)
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB").convert("RGBA"); d = ImageDraw.Draw(im)
    # cream cliffs
    def cliff(poly, flip):
        c = Image.new("RGBA", (w, h), (0, 0, 0, 0)); cd = ImageDraw.Draw(c); cd.polygon([(x * SS, y * SS) for x, y in poly], fill=(255, 255, 255, 255))
        g = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
        col = np.array([220, 210, 194], np.float32) * (1 - g) + np.array([168, 158, 144], np.float32) * g
        col = np.repeat(col, w, axis=1); a = np.asarray(c.split()[3], np.float32)[..., None] / 255
        base_ = np.asarray(im, np.float32)[..., :3]; return Image.fromarray(np.clip(base_ * (1 - a) + col * a, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    im = cliff([(0, HZ), (LE, HZ), (LE + 5, HZ + 32), (LE - 3, HZ + 70), (LE - 7, PH), (0, PH)], False)
    im = cliff([(PW, HZ), (RE, HZ), (RE - 4, HZ + 34), (RE + 3, HZ + 72), (RE + 8, PH), (PW, PH)], True)
    _BG["bg"] = im; return im.copy()
def spots(im, red=0.0, red_x=MID):
    w, h = PW * SS, PH * SS; lay = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for cx, a in ((196, 26), (565, 30)):
        d.polygon([((cx - 14) * SS, 0), ((cx + 14) * SS, 0), ((cx + 58) * SS, HZ * SS), ((cx - 58) * SS, HZ * SS)], fill=(210, 214, 230, a))
    lay = lay.filter(ImageFilter.GaussianBlur(22 * SS / 2)); im.alpha_composite(lay)
    if red > 0.01:
        r = Image.new("RGBA", (w, h), (0, 0, 0, 0)); rd = ImageDraw.Draw(r)
        rd.polygon([((red_x - 24) * SS, 0), ((red_x + 24) * SS, 0), ((red_x + 62) * SS, HZ * SS), ((red_x - 62) * SS, HZ * SS)], fill=(235, 40, 40, int(80 * red)))
        im.alpha_composite(r.filter(ImageFilter.GaussianBlur(12 * SS / 2)))
def bridge(d, S, x0, x1, direction):
    """planks + rope rail from edge x0 to x1"""
    if abs(x1 - x0) < 2: return
    lo, hi = min(x0, x1), max(x0, x1); n = int((hi - lo) // 17.6)
    for i in range(n + 1):
        px = lo + i * 17.6; d.rectangle([px * S, (HZ - 1.5) * S, (px + 13.5) * S, (HZ + 3.5) * S], fill=(150, 100, 58, 255))
    for xp in (lo, hi):
        d.line([(xp * S, HZ * S), (xp * S, (HZ - 36) * S)], fill=(150, 108, 76, 255), width=int(2 * S))
    pts = [(lo + (hi - lo) * i / 20, HZ - 36 + 7 * math.sin(math.pi * i / 20)) for i in range(21)]
    d.line([(a * S, b * S) for a, b in pts], fill=(150, 108, 76, 255), width=int(1.6 * S))

# ------------------------------------------------------------------ timelines
TP = 7.0 / 12.0
def build_state(t, side):
    """returns (end_x, pose, f) for a builder who starts at the cliff edge; side=+1 left builder (faces right), -1 right builder"""
    n = int(t / TP); f = (t / TP) % 1.0
    placed = n + (1 if f > 0.45 else 0)
    start = LE if side > 0 else RE
    end = lambda k: start + side * 17.6 * k
    return end, n, f, placed
def top_panel(t):
    S = SS; im = panel_bg(); spots(im, red=sm((t - 8.0) / 0.6)); d = ImageDraw.Draw(im); glow = Image.new("RGBA", im.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    figs = []
    if t < 7.0:
        for side, bun in ((1, True), (-1, False)):
            endf, n, f, placed = build_state(t + (0.0 if side > 0 else 0.07), side)
            bridge(d, S, LE if side > 0 else RE, endf(placed), side)
            if f < 0.5:
                p = mix(POSES["stand"], POSES["kneel"], sm(f / 0.18)) if f < 0.4 else mix(POSES["kneel"], POSES["stand"], sm((f - 0.4) / 0.1)); x = endf(n)
            else:
                u = (f - 0.5) / 0.5; p = walk_pose(u * 2 * math.pi, 0.9); x = lerp(endf(n), endf(n + 1), sm(u))
            figs.append((x + side * 4, HZ + 2, side, p, bun))
    else:
        bridge(d, S, LE, MID, 1); bridge(d, S, RE, MID, -1)
        u = sm((t - 7.0) / 0.9); hugu = sm((t - 7.8) / 0.6)
        xl, xr = lerp(MID - 62, MID - 8, u), lerp(MID + 62, MID + 10, u)
        pl = mix(POSES["stand"], POSES["hug"], hugu) if t > 7.8 else mix(POSES["stand"], POSES["reach"], u)
        figs.append((xl, HZ + 2, 1, pl, True)); figs.append((xr, HZ + 2, -1, pl if t > 7.8 else mix(POSES["stand"], POSES["reach"], u), False))
        if t > 8.1:   # heart
            hb = 1 + 0.07 * math.sin(t * 7); hx, hy = MID - 2, 52 + 3 * math.sin(t * 2)
            pts = [(hx + 14 * hb * math.sin(a) ** 3 / 1.0, hy - hb * (11 * math.cos(a) - 4.4 * math.cos(2 * a) - 1.7 * math.cos(3 * a) - 0.7 * math.cos(4 * a)) * 1.1) for a in np.linspace(0, 2 * math.pi, 40)]
            gh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(gh).polygon([(a * S, b * S) for a, b in pts], fill=(255, 60, 60, int(255 * sm((t - 8.1) / 0.4))))
            im.alpha_composite(gh.filter(ImageFilter.GaussianBlur(6 * S))); gh2 = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(gh2).polygon([(a * S, b * S) for a, b in pts], fill=(232, 36, 40, int(255 * sm((t - 8.1) / 0.4))), outline=(120, 10, 14, 255)); im.alpha_composite(gh2)
    for (x, g, f, p, bun) in figs: draw_figure(d, S, x, g, f, p, (255, 255, 255, 255), (12, 12, 16, 255), bun=bun, glow_d=gd)
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(7 * S)).point(lambda v: int(v * 0.55)))
    d = ImageDraw.Draw(im)
    for (x, g, f, p, bun) in figs: draw_figure(d, S, x, g, f, p, (255, 255, 255, 255), (12, 12, 16, 255), bun=bun)
    return im
def bottom_panel(t):
    S = SS; im = panel_bg(); spots(im); d = ImageDraw.Draw(im)
    # builder (right figure) slows, stops, reaches, slumps
    TP2 = 0.9; stop = 9.0
    tt = min(t, stop); n = int(tt / TP2); f = (tt / TP2) % 1.0; placed = n + (1 if f > 0.45 else 0)
    endf = lambda k: RE - 17.6 * k
    if t >= stop: placed = int(stop / TP2) + (1 if (stop / TP2) % 1 > 0.45 else 0)
    bridge(d, S, RE, endf(placed), -1)
    gcol, ocol = (128, 128, 130, 255), (22, 22, 26, 255)
    if t < stop:
        if f < 0.5: p = mix(POSES["stand"], POSES["kneel"], sm(f / 0.18)) if f < 0.4 else mix(POSES["kneel"], POSES["stand"], sm((f - 0.4) / 0.1)); x = endf(n)
        else: u = (f - 0.5) / 0.5; p = walk_pose(u * 2 * math.pi, 0.9); x = lerp(endf(n), endf(n + 1), sm(u))
    else:
        x = endf(placed)
        if t < 10.9: p = mix(POSES["stand"], POSES["reach"], sm((t - stop) / 0.5))
        else: p = mix(POSES["reach"], POSES["slump"], sm((t - 10.9) / 0.9))
    # she scrolls (phone glow)
    ps = mix(POSES["stand"], POSES["phone"], sm((t - 0.3) / 0.4))
    Js = draw_figure(d, S, 75, HZ + 2, 1, ps, gcol, ocol, bun=True)
    draw_figure(d, S, x + (-4), HZ + 2, -1, p, gcol, ocol)
    if t > 0.5:
        a = sm((t - 0.5) / 0.4); pw_ = (Js["wF"][0] + 5, Js["wF"][1] - 6); gl = Image.new("RGBA", im.size, (0, 0, 0, 0)); gd2 = ImageDraw.Draw(gl)
        fl = 0.85 + 0.15 * math.sin(t * 6)
        gd2.ellipse([(pw_[0] - 22) * S, (pw_[1] - 22) * S, (pw_[0] + 22) * S, (pw_[1] + 22) * S], fill=(70, 120, 255, int(120 * a * fl)))
        im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(9 * S))); d = ImageDraw.Draw(im)
        d.rounded_rectangle([(pw_[0] - 3.5) * S, (pw_[1] - 6) * S, (pw_[0] + 3.5) * S, (pw_[1] + 6) * S], radius=int(1.5 * S), fill=(235, 242, 255, 255), outline=(40, 70, 150, 255))
    return im

# ------------------------------------------------------------------ text
_F = {}
def font(sz):
    if sz not in _F: _F[sz] = ImageFont.truetype(MONO, int(sz))
    return _F[sz]
def spaced(d, xy, s, f, fill, ls, anchor="l"):
    w = sum(d.textlength(c, font=f) + ls for c in s) - ls; x, y = xy
    if anchor == "c": x -= w / 2
    for c in s: d.text((x, y), c, font=f, fill=fill); x += d.textlength(c, font=f) + ls
def typed(s, t0, cps, t): return s[:max(0, min(len(s), int((t - t0) * cps)))]
def top_sub(t):
    if t < 0.5: return ""
    if t < 7.0: return typed("PLANK BY PLANK", 0.5, 9, t)
    if t < 8.2: return typed("THEY MEET", 7.0, 12, t)
    return typed("HOLD ON", 8.2, 10, t)
def bottom_sub(t):
    if t < 0.9: return "", None
    if t < 2.7: return typed("HE BUILDS", 0.9, 8, t), None
    if t < 9.0: return typed("SHE SCROLLS", 2.7, 9, t), None
    if t < 10.3: return typed("TOO FAR", 9.0, 8, t), (232, 48, 48)
    return typed("ALONE", 10.3, 7, t), (232, 48, 48)

def frame(t):
    img = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(img)
    f1, f2 = font(22 * K), font(21 * K)
    spaced(d, (W / 2, 171 * K - 12), "LOVE IS A BRIDGE.", f1, (245, 245, 245), 3, "c")
    l2 = typed("ONE PERSON CAN'T BUILD", 11.0, 16, t); l3 = typed("A BRIDGE FOR TWO.", 12.4, 14, t)
    if l2: spaced(d, (W / 2, 203 * K - 12), l2, f1, (245, 245, 245), 3, "c")
    if l3: spaced(d, (W / 2, 235 * K - 12), l3, f1, (245, 245, 245), 3, "c")
    for py, pn in ((PY1, "top"), (PY2, "bot")):
        pim = (top_panel(t) if pn == "top" else bottom_panel(t)).convert("RGB").resize((int(PW * K), int(PH * K)), Image.LANCZOS)
        img.paste(pim, (int(PX * K), int(py * K))); d.rectangle([PX * K - 1, py * K - 1, (PX + PW) * K, (py + PH) * K], outline=(42, 42, 52), width=3)
    d.text((int((PX + 28) * K), int((PY1 + 18) * K)), "", font=f2)
    spaced(d, ((PX + 28) * K, (PY1 + 18) * K), "BOTH BUILD", font(18 * K), (240, 240, 240), 4)
    s = top_sub(t)
    if s: spaced(d, ((PX + 28) * K, (PY1 + 43) * K), s, font(11 * K), (210, 210, 214), 3)
    spaced(d, ((PX + 28) * K, (PY2 + 18) * K), "ONE BUILDS", font(18 * K), (150, 150, 156), 4)
    s, col = bottom_sub(t)
    if s: spaced(d, ((PX + 28) * K, (PY2 + 43) * K), s, font(11 * K), col or (170, 170, 176), 3)
    lab = "S L O W   L I G H T"; w = d.textlength(lab, font=font(28)); d.text(((W - w) / 2, 1822), lab, font=font(28), fill=(150, 150, 156))
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
