#!/usr/bin/env python3
"""How Much of You Is Actually You? Perspective-shock reel (18 s, 1080x1920, PIL + numpy + ffmpeg).

Hook structure: QUESTION -> next-second PUNCHLINE that reopens the question -> second hook -> escalation -> twist -> payoff
(loops to frame 0) -> tease for the next reel.
Data: Sender, Fuchs & Milo (2016), PLoS Biology 14(8): ~30T human cells, ~38T bacterial cells, 70 kg reference man,
bacteria ~0.2 kg. (Estimates, not exact counts.)

usage: render.py sheet OUT.png t1 t2 ...   |   render.py video OUT.mp4
"""
import math, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from multiprocessing import Pool

W, H, FPS, DUR = 1080, 1920, 30, 18.0
N = int(round(FPS * DUR))
FONT_B = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
FONT_S = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
FONT_M = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
CREAM = (243, 234, 215); GOLD = (255, 191, 77); TEAL = (52, 214, 196)
COL = {"cream": CREAM, "gold": GOLD, "teal": TEAL}
def cc(nm, k): return tuple(int(c * k) for c in COL[nm])
FIG_C = (540, 960)            # figure centre on screen at zoom 1
FOCUS = np.array([0.0, -120.0])

def sm(x):
    x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)

def key(t, ks, lin=False):
    if t <= ks[0][0]: return ks[0][1]
    for (t0, v0), (t1, v1) in zip(ks, ks[1:]):
        if t <= t1:
            u = (t - t0) / (t1 - t0); return v0 + (v1 - v0) * (u if lin else sm(u))
    return ks[-1][1]

# ------------------------------------------------------------------ static data
def build():
    rng = np.random.RandomState(7)
    m = Image.new("L", (540, 1000), 0); d = ImageDraw.Draw(m)
    d.ellipse([190, 18, 350, 178], fill=255)
    d.polygon([(165, 205), (375, 205), (398, 262), (382, 560), (158, 560), (142, 262)], fill=255)
    d.polygon([(78, 224), (130, 236), (142, 604), (92, 608)], fill=255)
    d.polygon([(462, 224), (410, 236), (398, 604), (448, 608)], fill=255)
    d.polygon([(166, 552), (264, 552), (252, 975), (170, 975)], fill=255)
    d.polygon([(276, 552), (374, 552), (370, 975), (288, 975)], fill=255)
    a = np.asarray(m) > 128
    ys, xs = np.nonzero(a)
    idx = rng.choice(len(xs), 15000, replace=False)
    px = (xs[idx] - 270) * 0.88 + rng.randn(15000) * 0.5
    py = (ys[idx] - 500) * 0.88 + rng.randn(15000) * 0.5
    P = dict(x=px.astype(np.float32), y=py.astype(np.float32), r=(1.5 + rng.rand(15000) * 1.7).astype(np.float32),
             ph=(rng.rand(15000) * 6.28).astype(np.float32), fx=(0.6 + rng.rand(15000) * 1.4).astype(np.float32),
             fy=(0.6 + rng.rand(15000) * 1.4).astype(np.float32), teal=(rng.rand(15000) < 0.56),
             jit=rng.rand(15000).astype(np.float32), ang=(rng.rand(15000) * 6.28).astype(np.float32))
    P["yn"] = ((P["y"] + 480) / 960).clip(0, 1)
    # micro world
    rr = np.random.RandomState(21)
    nr, nc = 230, 34
    M = dict(rx=rr.rand(nr) * 1500, ry=rr.rand(nr) * 2300, rd=0.45 + rr.rand(nr) * 1.25, ra=rr.rand(nr) * 6.28, rl=60 + rr.rand(nr) * 55,
             rw=14 + rr.rand(nr) * 12, rph=rr.rand(nr) * 6.28, rsp=0.8 + rr.rand(nr) * 1.5, rs=(rr.rand(nr) < 0.18),
             cx=rr.rand(nc) * 1500, cy=rr.rand(nc) * 2300, cd=0.55 + rr.rand(nc) * 1.05, cr=70 + rr.rand(nc) * 60, cph=rr.rand(nc) * 6.28)
    return P, M

_DATA = None
_TX = {}

# ------------------------------------------------------------------ text helpers
def font(path, size): return ImageFont.truetype(path, size)

def text_mask(lines, size, path=FONT_B, spacing=1.14):
    kx = (tuple(lines), size, path)
    if kx in _TX: return _TX[kx]
    f = font(path, size)
    lh = int(size * spacing); hbox = lh * len(lines) + 30
    m = Image.new("L", (W, hbox), 0); d = ImageDraw.Draw(m)
    for i, ln in enumerate(lines):
        w = d.textlength(ln, font=f); d.text(((W - w) / 2, 6 + i * lh), ln, font=f, fill=255)
    if len(_TX) > 400: _TX.clear()
    _TX[kx] = m
    return m

def put_text(ov, lines, size, y, color, alpha=1.0, path=FONT_B, scale=1.0, glow=True):
    if alpha <= 0.01: return
    m = text_mask(lines, size, path)
    if abs(scale - 1) > 0.005:
        m = m.resize((int(W * scale), int(m.height * scale)), Image.BICUBIC)
        canvas = Image.new("L", (W, m.height), 0); canvas.paste(m, ((W - m.width) // 2, 0)); m = canvas
    a = m.point(lambda v: int(v * alpha))
    if glow:
        sh = Image.new("L", m.size, 0); sh.paste(a.filter(ImageFilter.GaussianBlur(14)).point(lambda v: min(255, int(v * 1.6))), (0, 0))
        ov.paste(Image.new("RGBA", m.size, (4, 6, 14, 255)), (0, int(y)), sh.point(lambda v: int(v * 0.8)))
    ov.paste(Image.new("RGBA", m.size, color + (255,)), (0, int(y)), a)

def typed(lines, n):
    out, left = [], n
    for ln in lines:
        out.append(ln[:max(0, left)]); left -= len(ln)
    return out

# ------------------------------------------------------------------ scenes
def zoom_fig(t):
    if t < 3.0: return 1.0 + 0.07 * sm(t / 3.0)
    if t < 7.4:
        u = sm((t - 3.0) / 4.4); return 1.07 * math.exp(math.log(46 / 1.07) * u)
    if t < 12.4: return 46.0
    if t < 14.5:
        u = sm((t - 12.4) / 2.1); return 46.0 * math.exp(math.log(1.0 / 46.0) * u)
    return 1.0

def particles(t, layers, a):
    """layers: dict name -> ImageDraw on full-res L. a: scene alpha 0..1."""
    P = _DATA[0]; z = zoom_fig(t)
    amp = key(t, [(0, 0.6), (3.0, 1.0), (7.0, 7.0), (12.4, 7.0), (14.5, 1.0), (15.5, 0.4)])
    x = P["x"] + amp * np.sin(t * P["fx"] + P["ph"]); y = P["y"] + amp * np.cos(t * P["fy"] + P["ph"] * 1.3)
    tr = 1.40 + 0.45 * (1 - P["yn"]) + 0.05 * P["jit"]
    rec_f = 14.45 + 0.6 * P["jit"]                                   # recolour back to cream at the end
    after = t >= tr
    since = np.where(after, t - tr, -1.0)
    pop = np.where(after, 1 + 1.0 * np.exp(-since / 0.13), 1.0)
    sx = (x - FOCUS[0]) * z + FOCUS[0] + FIG_C[0]; sy = (y - FOCUS[1]) * z + FOCUS[1] + FIG_C[1]
    sep = np.where(after & P["teal"], 12 * (1 - np.exp(-since / 0.9)), 0.0)
    sx = sx + np.cos(P["ang"]) * sep * min(z, 3); sy = sy + np.sin(P["ang"]) * sep * min(z, 3)
    rad = P["r"] * (z ** 0.52) * pop * (1 + 0.12 * np.sin(t * 3 + P["ph"]))
    vis = (sx > -60) & (sx < W + 60) & (sy > -60) & (sy < H + 60)
    cream_phase = (t < tr) | (t >= rec_f)
    fade_end = np.clip((t - rec_f) / 0.4, 0, 1)
    for i in np.nonzero(vis)[0]:
        r = float(rad[i]); cx, cy = float(sx[i]), float(sy[i])
        if cream_phase[i]:
            nm = "cream"
        else:
            nm = "teal" if P["teal"][i] else "gold"
        if nm == "gold": r *= 1.35
        k = a * (0.82 if nm == "teal" else 1.0)
        layers.ellipse([cx - r, cy - r, cx + r, cy + r], fill=tuple(int(c * k) for c in COL[nm]))

def micro(t, dc, gd, a):
    M = _DATA[1]
    zm = 1.0 + 0.045 * (t - 6.4)
    camx = 70 * t; camy = 40 * math.sin(t * 0.7) + 55 * t
    def pos(px, py, d):
        x = ((px - camx * d + 750) % 1500) - 750; y = ((py - camy * d + 1150) % 2300) - 1150
        return 540 + x * zm * (0.9 + 0.1 * d), 960 + y * zm * (0.9 + 0.1 * d)
    for i in range(len(M["rx"])):
        d = M["rd"][i]; x, y = pos(M["rx"][i], M["ry"][i], d)
        if x < -150 or x > W + 150 or y < -150 or y > H + 150: continue
        ang = M["ra"][i] + 0.35 * math.sin(t * M["rsp"][i] + M["rph"][i])
        L = M["rl"][i] * d * zm; w = M["rw"][i] * d * zm
        dx, dy = math.cos(ang) * L / 2, math.sin(ang) * L / 2
        far = d < 0.7 or d > 1.35
        if M["rs"][i]:
            rr = w * 0.9
            if far:
                k = 0.25; gd.ellipse([(x - rr) * k, (y - rr) * k, (x + rr) * k, (y + rr) * k], fill=cc("teal", a * 0.8))
            else:
                dc.ellipse([x - rr, y - rr, x + rr, y + rr], fill=cc("teal", a))
            continue
        if far:
            k = 0.25
            gd.line([((x - dx) * k, (y - dy) * k), ((x + dx) * k, (y + dy) * k)], fill=cc("teal", a * (0.5 if d < 0.7 else 0.9)), width=max(1, int(w * k)))
        else:
            dc.line([(x - dx, y - dy), (x + dx, y + dy)], fill=cc("teal", a), width=max(2, int(w)))
            dc.ellipse([x - dx - w / 2, y - dy - w / 2, x - dx + w / 2, y - dy + w / 2], fill=cc("teal", a))
            dc.ellipse([x + dx - w / 2, y + dy - w / 2, x + dx + w / 2, y + dy + w / 2], fill=cc("teal", a))
            dc.line([(x - dx * 0.5, y - dy * 0.5), (x + dx * 0.5, y + dy * 0.5)], fill=cc("cream", a * 0.3), width=max(1, int(w * 0.25)))
    for i in range(len(M["cx"])):
        d = M["cd"][i]; x, y = pos(M["cx"][i], M["cy"][i], d)
        R = M["cr"][i] * d * zm * (1 + 0.03 * math.sin(t * 1.3 + M["cph"][i]))
        if x < -R - 20 or x > W + R + 20 or y < -R - 20 or y > H + R + 20: continue
        if d < 0.7 or d > 1.35:
            k = 0.25; gd.ellipse([(x - R) * k, (y - R) * k, (x + R) * k, (y + R) * k], outline=cc("gold", a * 0.55), width=max(2, int(R * 0.18 * k)))
        else:
            dc.ellipse([x - R, y - R, x + R, y + R], outline=cc("gold", a), width=max(3, int(R * 0.09)))
            dc.ellipse([x - R * 0.36, y - R * 0.36 + 4, x + R * 0.36, y + R * 0.36 + 4], fill=cc("gold", a * 0.85))
            dc.ellipse([x - R * 0.82, y - R * 0.82, x + R * 0.82, y + R * 0.82], outline=cc("gold", a * 0.3), width=2)

def bars(t, ov, a):
    t0 = 9.3
    gx = {"n": 290, "w": 800}; base = 1260; hmax = 500
    ease = sm((t - t0 - 0.2) / 1.2)
    f = font(FONT_B, 50); fs = font(FONT_S, 34); fsm = font(FONT_M, 30)
    d = ImageDraw.Draw(ov)
    def ca(c, al=1.0): return c + (int(255 * a * al),)
    d.text((gx["n"], 560), "HOW MANY", font=f, fill=ca(CREAM), anchor="mm")
    d.text((gx["w"], 560), "HOW HEAVY", font=f, fill=ca(CREAM), anchor="mm")
    items = [("n", -80, 38, 38, TEAL, "38T"), ("n", 80, 30, 38, GOLD, "30T"), ("w", -80, 70, 70, GOLD, "70 kg"), ("w", 80, 0.2, 70, TEAL, "0.2 kg")]
    bw = 120
    for g, off, v, mx, col, lab in items:
        x = gx[g] + off
        h = max(hmax * v / mx * ease, 0)
        if v == 0.2: h = max(h, 8 * ease)
        d.rounded_rectangle([x - bw / 2, base - h, x + bw / 2, base], radius=10, fill=ca(col))
        if ease > 0.05:
            vv = v * ease
            txt = (f"{vv:.0f}T" if g == "n" else ("%.0f kg" % vv if v == 70 else ""))
            if txt: d.text((x, base - h - 38), txt, font=fs, fill=ca(col), anchor="mm")
    d.line([(gx["n"] - 160, base + 6), (gx["n"] + 160, base + 6)], fill=ca(CREAM, 0.6), width=4)
    d.line([(gx["w"] - 160, base + 6), (gx["w"] + 160, base + 6)], fill=ca(CREAM, 0.6), width=4)
    d.text((gx["n"] - 80, base + 46), "bacteria", font=fsm, fill=ca(TEAL), anchor="mm"); d.text((gx["n"] + 80, base + 46), "you", font=fsm, fill=ca(GOLD), anchor="mm")
    d.text((gx["w"] - 80, base + 46), "you", font=fsm, fill=ca(GOLD), anchor="mm"); d.text((gx["w"] + 80, base + 46), "bacteria", font=fsm, fill=ca(TEAL), anchor="mm")
    # apple callout for the tiny teal bar
    ap = sm((t - 10.5) / 0.6)
    if ap > 0.02:
        cx, cy = gx["w"] + 80, base - 330
        al = int(255 * ap * a)
        d.line([(cx, base - 24), (cx, cy + 84)], fill=TEAL + (al,), width=5)
        d.ellipse([cx - 74, cy - 62, cx + 74, cy + 78], outline=CREAM + (al,), width=10)
        d.line([(cx, cy - 58), (cx + 10, cy - 102)], fill=CREAM + (al,), width=9)
        d.ellipse([cx + 10, cy - 114, cx + 62, cy - 84], fill=GOLD + (al,))
        d.text((cx, cy + 128), "0.2 kg", font=fs, fill=TEAL + (al,), anchor="mm")
        d.text((cx, cy + 168), "≈ an apple", font=fsm, fill=CREAM + (al,), anchor="mm")
    d.text((W / 2, 1530), "By cell count, 70 kg adult · Sender, Fuchs & Milo, PLoS Biology 2016", font=font(FONT_M, 26),
           fill=CREAM + (int(150 * a),), anchor="mm")

# ------------------------------------------------------------------ frame
def glow_from(layer_img, blur=5, scale=4):
    s = layer_img.resize((W // scale, H // scale), Image.BILINEAR).filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(s.resize((W, H), Image.BILINEAR), np.float32) / 255

_BGC = None
def bg():
    global _BGC
    if _BGC is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.47) / (H * 0.65)) ** 2)
        g = np.clip(1 - r, 0, 1) ** 1.6
        c0 = np.array([5, 8, 17], np.float32) / 255; c1 = np.array([17, 27, 54], np.float32) / 255
        _BGC = c0 + (c1 - c0) * g[..., None]
    return _BGC

def render(t):
    global _DATA
    if _DATA is None: _DATA = build()
    img = bg().copy()
    # scene alphas
    a_part = 1.0 if t < 6.6 else (1 - sm((t - 6.6) / 0.8) if t < 7.6 else 0.0)
    if t >= 12.3: a_part = sm((t - 12.3) / 0.7)
    a_micro = sm((t - 6.7) / 0.9) * (1 - sm((t - 9.0) / 0.6)) if t > 6.6 else 0.0
    a_bars = sm((t - 9.2) / 0.5) * (1 - sm((t - 12.3) / 0.5)) if t > 9.1 else 0.0
    C = Image.new("RGB", (W, H), (0, 0, 0)); DC = ImageDraw.Draw(C)
    GC = Image.new("RGB", (W // 4, H // 4), (0, 0, 0)); GD = ImageDraw.Draw(GC)
    if a_part > 0.01: particles(t, DC, a_part)
    if a_micro > 0.01: micro(t, DC, GD, a_micro)
    sharp = np.asarray(C, np.float32) / 255
    glow = np.asarray(C.resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(4)).resize((W, H), Image.BILINEAR), np.float32) / 255
    far = np.asarray(GC.filter(ImageFilter.GaussianBlur(3)).resize((W, H), Image.BILINEAR), np.float32) / 255
    img = img + sharp * 0.95 + glow * 0.55 + far * 0.9
    # punch flash at the recolour
    fl = np.exp(-((t - 1.5) / 0.09) ** 2) * 0.18 + np.exp(-((t - 9.25) / 0.09) ** 2) * 0.12 + np.exp(-((t - 12.9) / 0.09) ** 2) * 0.14
    img = img + fl
    base = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # ---- text / counters
    q = ["HOW MUCH OF YOU", "IS ACTUALLY YOU?"]
    n = int(t * 40)
    if t < 1.55:
        al = 1 - sm((t - 1.36) / 0.16)
        put_text(ov, typed(q, n), 82, 270, CREAM, al)
    if 1.4 < t < 3.1:
        sc = 1.0 + 0.45 * math.exp(-(t - 1.42) / 0.09) * (t > 1.42)
        put_text(ov, ["LESS THAN", "HALF."], 128, 140, GOLD, sm((t - 1.42) / 0.05) * (1 - sm((t - 2.85) / 0.25)), scale=min(1.3, sc))
    if 3.0 < t < 5.8:
        h2 = ["SO WHO ELSE", "IS IN THERE?"]
        put_text(ov, typed(h2, int((t - 3.0) * 34)), 92, 230, CREAM, sm((t - 3.0) / 0.1) * (1 - sm((t - 5.35) / 0.35)))
    if 5.9 < t < 9.4:
        e = sm((t - 6.1) / 2.3)
        fa = sm((t - 5.9) / 0.35) * (1 - sm((t - 9.0) / 0.4))
        d = ImageDraw.Draw(ov)
        pulse = 1 + 0.08 * math.exp(-max(0, t - 8.5) / 0.15) * (t > 8.5)
        d.text((300, 250), f"{30 * e:.1f}T", font=font(FONT_B, int(104)), fill=GOLD + (int(255 * fa),), anchor="mm")
        d.text((300, 330), "HUMAN CELLS", font=font(FONT_S, 36), fill=GOLD + (int(255 * fa),), anchor="mm")
        d.text((780, 250), f"{38 * e:.1f}T", font=font(FONT_B, int(104 * pulse)), fill=TEAL + (int(255 * fa),), anchor="mm")
        d.text((780, 330), "BACTERIA", font=font(FONT_S, 36), fill=TEAL + (int(255 * fa),), anchor="mm")
    if 8.5 < t < 9.5:
        put_text(ov, ["THEY OUTNUMBER YOU."], 80, 1340, CREAM, sm((t - 8.5) / 0.2) * (1 - sm((t - 9.2) / 0.3)))
    if a_bars > 0.01:
        bars(t, ov, a_bars)
        put_text(ov, ["...BUT THEY WEIGH ABOUT", "AS MUCH AS AN APPLE."], 66, 250, CREAM, a_bars * sm((t - 10.0) / 0.4) * (1 - sm((t - 12.2) / 0.4)))
    if 12.8 < t < 15.2:
        sc = 1.0 + 0.4 * math.exp(-(t - 12.85) / 0.1)
        put_text(ov, ["YOU HAVE NEVER", "BEEN ALONE."], 116, 150, CREAM, sm((t - 12.85) / 0.06) * (1 - sm((t - 14.9) / 0.3)), scale=min(1.25, sc))
    if t > 15.2:
        put_text(ov, ["NEXT: THE OLDEST THING IN YOU", "IS OLDER THAN THE SUN."], 60, 1470, GOLD, sm((t - 15.2) / 0.4))
        put_text(ov, ["FOLLOW"], 42, 1650, CREAM, 0.7 * sm((t - 15.9) / 0.4), path=FONT_S, glow=False)
    out = Image.alpha_composite(base, ov).convert("RGB")
    arr = np.asarray(out, np.float32) / 255
    rng = np.random.RandomState(int(t * 24) % 5)
    arr = arr + (rng.randn(H // 2, W // 2).astype(np.float32).repeat(2, 0).repeat(2, 1) * 0.012)[..., None]
    return (np.clip(arr, 0, 1) * 255).astype(np.uint8)

def render_bytes(i): return render(i / FPS).tobytes()

def main():
    mode = sys.argv[1]
    if mode == "sheet":
        out = sys.argv[2]; ts = [float(x) for x in sys.argv[3:]]
        with Pool(4) as p: fr = p.map(render, ts)
        cols = 4; rows = math.ceil(len(fr) / cols); sw, sh = 270, 480
        sheet = Image.new("RGB", (cols * sw, rows * sh))
        for k, f in enumerate(fr): sheet.paste(Image.fromarray(f).resize((sw, sh), Image.LANCZOS), ((k % cols) * sw, (k // cols) * sh))
        sheet.save(out)
    elif mode == "video":
        out = sys.argv[2]
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
               "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", f"{DUR}", "-c:v", "libx264", "-crf", "17", "-preset", "medium",
               "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out]
        pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        with Pool(4) as p:
            for k, b in enumerate(p.imap(render_bytes, range(N), chunksize=3)):
                pr.stdin.write(b)
                if k % 90 == 0: print("frame", k, "/", N, flush=True)
        pr.stdin.close(); pr.wait()

if __name__ == "__main__":
    main()
