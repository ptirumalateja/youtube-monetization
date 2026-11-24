#!/usr/bin/env python3
"""SIMULTANEOUS cut of 'What success looks like:' (10 s): Expectation (top) and Reality (bottom) run at the same time. White theme, black stickman.
(older docstring:) sketch-style replica (15 s, 1080x1920). White paper, wobbly hand-drawn panels, kid in a green #5 jersey,
EXPECTATION (1 post -> 1,000,000 followers) vs REALITY (stack posts into a staircase, followers crawl, then it happens).
Plain black stickman on pure white. Own drawing code; the credit line is our channel handle. Coordinates are in the reference's 720x1280 space (K=1.5 to final).
usage: render_exact.py sheet OUT.png t... | frames OUTDIR | video OUT.mp4 AUDIO.wav FRAMESDIR"""
import sys, os, math, random, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920; FPS = 30; DUR = 10.0; K = 1.5; SS = 2
HERE = os.path.dirname(os.path.abspath(__file__))
HAND = os.path.join(HERE, "fonts", "PatrickHand-Regular.ttf")
INTER_B = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"; INTER_SB = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
INK = (22, 22, 22); GREEN = (22, 88, 68); PAPER = (255, 255, 255)
CREDIT = "@SLOWLIGHTTV"
def sm(x): x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t
def interp(keys, t):
    if t <= keys[0][0]: return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t0 <= t < t1: return v0 + (v1 - v0) * sm((t - t0) / (t1 - t0))
    return keys[-1][1]

# ------------------------------------------------------------------ timeline (read from the reference)
EXP_KEYS = [(0.9, 0), (1.15, 97538), (1.6, 821362), (1.9, 1000000)]
POST_KEYS = [(2.6, 0), (3.0, 2), (3.5, 6), (4.0, 15), (4.5, 29), (5.0, 46), (5.5, 82), (6.0, 138), (6.5, 246), (7.0, 395), (7.5, 557), (8.0, 699), (8.5, 809), (9.0, 902), (9.5, 935), (10.0, 1000)]
FOL_KEYS = [(2.6, 0), (3.0, 7), (3.5, 18), (4.0, 38), (4.5, 60), (5.0, 84), (5.5, 129), (6.0, 187), (6.5, 283), (7.0, 399), (7.5, 510), (8.0, 601), (8.5, 669), (9.0, 723), (9.5, 765), (10.0, 774),
            (10.5, 8620), (11.0, 199120), (11.5, 906968), (12.0, 1000000)]
def linear_interp(keys, t):
    if t <= keys[0][0]: return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t0 <= t < t1: return v0 + (v1 - v0) * (t - t0) / (t1 - t0)
    return keys[-1][1]
def exp_followers(t): return int(interp(EXP_KEYS, t))
def real_posts(t): return int(round(linear_interp(POST_KEYS, t)))
def real_followers(t): return int(round(linear_interp(FOL_KEYS, t)))
def fmt(n): return f"{n:,}"

# ------------------------------------------------------------------ hand-drawn helpers
def wob(p0, p1, amp, seed, step=18.0):
    """a wobbly line from p0 to p1 (reference px)"""
    r = random.Random(seed); dx, dy = p1[0] - p0[0], p1[1] - p0[1]; L = math.hypot(dx, dy); n = max(2, int(L / step)); nx, ny = -dy / L, dx / L
    ph1, ph2 = r.uniform(0, 6), r.uniform(0, 6); pts = []
    for i in range(n + 1):
        u = i / n; o = amp * (math.sin(u * 9 + ph1) * 0.6 + math.sin(u * 23 + ph2) * 0.4)
        pts.append((p0[0] + dx * u + nx * o, p0[1] + dy * u + ny * o))
    return pts
class Ink:
    def __init__(self):
        self.im = Image.new("RGBA", (W * SS, H * SS), PAPER + (255,)); self.d = ImageDraw.Draw(self.im)
    def px(self, p): return (p[0] * K * SS, p[1] * K * SS)
    def line(self, pts, w=2.4, col=INK):
        P = [self.px(p) for p in pts]; self.d.line(P, fill=col, width=max(1, int(w * K * SS)), joint="curve")
        r = w * K * SS / 2
        for a, b in (P[0], P[-1]): self.d.ellipse([a - r, b - r, a + r, b + r], fill=col)
    def poly(self, pts, fill, outline=INK, w=1.6):
        P = [self.px(p) for p in pts]; self.d.polygon(P, fill=fill)
        if outline: self.d.line(P + [P[0]], fill=outline, width=max(1, int(w * K * SS)), joint="curve")
    def rect(self, x0, y0, x1, y1, fill=None, outline=INK, w=1.6):
        self.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], fill, outline, w) if fill is not None else self.line([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], w)
    def circle(self, cx, cy, r, fill=PAPER, outline=INK, w=1.8):
        a, b = self.px((cx, cy)); rr = r * K * SS; self.d.ellipse([a - rr, b - rr, a + rr, b + rr], fill=fill, outline=outline, width=max(1, int(w * K * SS)))
    def text(self, xy, s, path, size, fill=INK, anchor="la"):
        f = ImageFont.truetype(path, int(size * K * SS)); self.d.text(self.px(xy), s, font=f, fill=fill, anchor=anchor)
    def textlen(self, s, path, size): return ImageFont.truetype(path, int(size * K * SS)).getlength(s) / (K * SS)
    def out(self): return self.im.resize((W, H), Image.LANCZOS).convert("RGB")

def panel(ink, y0, y1, seed):
    x0, x1 = 32, 688
    for (a, b, s) in (((x0, y0), (x1, y0), 1), ((x1, y0), (x1, y1), 2), ((x1, y1), (x0, y1), 3), ((x0, y1), (x0, y0), 4)):
        ext = lambda p, q, e: (p[0] - (q[0] - p[0]) * 0.012 * e, p[1] - (q[1] - p[1]) * 0.012 * e)
        ink.line(wob(ext(a, b, 1), ext(b, a, 1), 1.3, seed * 10 + s), w=2.8)
def ground(ink, y, seed): ink.line(wob((45, y), (675, y), 1.0, seed), w=2.4)

# ------------------------------------------------------------------ the kid
def draw_kid(ink, x, y0, pose="stand", walk=0.0, face=1):
    """plain black stickman. x = centre, y0 = floor; reference px. pose: stand (holding a phone), cheer, place"""
    s = lambda dx, dy: (x + face * dx, y0 + dy)
    sw = math.sin(walk * 2 * math.pi) * (7 if walk else 0)
    W_ = 3.2
    # legs
    ink.line([s(0, -50), s(-4 - sw * 0.5, -26), s(-7 - sw, -1)], w=W_); ink.line([s(0, -50), s(4 + sw * 0.5, -26), s(7 + sw, -1)], w=W_)
    # torso
    ink.line([s(0, -50), s(0, -88)], w=W_)
    # arms
    if pose == "cheer":
        ink.line([s(0, -85), s(-10, -102), s(-17, -118)], w=W_); ink.line([s(0, -85), s(10, -102), s(17, -118)], w=W_)
        ink.circle(x - face * 17, y0 - 121, 3.0, fill=PAPER, w=2.0); ink.circle(x + face * 17, y0 - 121, 3.0, fill=PAPER, w=2.0)
    elif pose == "place":
        ink.line([s(0, -85), s(18, -88), s(34, -90)], w=W_); ink.line([s(0, -85), s(-5, -70), s(-4, -56)], w=W_)
    else:
        ink.line([s(0, -85), s(12, -74), s(11, -94)], w=W_); ink.line([s(0, -85), s(-5, -70), s(-4, -56)], w=W_)
        ink.poly([s(9.5, -104), s(14.5, -104), s(14.5, -91), s(9.5, -91)], INK, INK, 1.0)
    # head
    ink.circle(x, y0 - 100, 10.5, fill=PAPER, w=3.0)

TAB = [(240, 150, 40), (52, 104, 214), (96, 160, 80), (232, 118, 160), (244, 196, 60), (222, 70, 60)]
def book(ink, x, y, w=38, h=9.2, i=0):
    ink.rect(x, y, x + w, y + h, fill=PAPER, outline=INK, w=1.1)
    ink.rect(x + 2, y + 2, x + 7.5, y + h - 2, fill=TAB[i % len(TAB)], outline=None)
    ink.line([(x + 11, y + h / 2), (x + w - 5, y + h / 2)], w=0.8, col=(150, 150, 150))
def confetti(ink, cx, cy, t0, t, spread=140):
    tau = t - t0
    if tau < 0 or tau > 1.5: return
    r = random.Random(int(t0 * 7) + 3)
    for i in range(70):
        a = r.uniform(0, 2 * math.pi); sp = r.uniform(30, spread); g = 60 * tau * tau
        x = cx + math.cos(a) * sp * min(1, tau * 2.2); y = cy + math.sin(a) * sp * 0.7 * min(1, tau * 2.2) + g
        ang = r.uniform(0, math.pi) + tau * r.uniform(-4, 4); L = r.uniform(4, 8); col = r.choice(TAB)
        if tau < 1.1 or r.random() > (tau - 1.1) / 0.4: ink.line([(x - math.cos(ang) * L / 2, y - math.sin(ang) * L / 2), (x + math.cos(ang) * L / 2, y + math.sin(ang) * L / 2)], w=1.9, col=col)

# stairs: 8 columns (heights in books)
COLS = [2, 3, 5, 7, 9, 11, 13, 15]; COLX = [178, 220, 262, 305, 347, 390, 432, 474]; BOOKS = sum(COLS)
def stair_state(posts):
    n = int(round(posts / 1000.0 * BOOKS)); cols = []
    for h in COLS: take = min(h, n); cols.append(take); n -= take
    return cols
def tmap(t):
    """real time -> the original reality timeline (walk 2.6-3.2, stack 3.2-10, followers jump 10-12, confetti 12, ending 13)"""
    if t < 0.25: return 0.0
    if t < 0.7: return 2.6 + (t - 0.25) / 0.45 * 0.6
    return 3.2 + (t - 0.7) * 1.31
def frame(t):
    ink = Ink(); tr = tmap(t)
    tw = ink.textlen("What success looks like:", INTER_B, 50); size = 50 * 570 / tw
    ink.text((360, 221), "What success looks like:", INTER_B, size, INK, "mm")
    panel(ink, 287, 621, 1); panel(ink, 640, 975, 2); ground(ink, 579, 5); ground(ink, 933, 6)
    ink.text((50, 325), "Expectation", HAND, 34, INK, "lm"); ink.text((50, 678), "Reality", HAND, 36, INK, "lm")
    # ---- expectation: one post, instant million, then it keeps celebrating while reality is still grinding
    bounce = abs(math.sin(t * 7.5)) * 7 if t >= 1.4 else 0
    pose = ("cheer" if int(t * 5) % 2 == 0 else "cheer") if t >= 1.3 else ("place" if 0.25 <= t < 0.6 else "stand")
    draw_kid(ink, 135, 579 - bounce, pose)
    ink.text((262, 386), "1 post", HAND, 28, INK, "mm"); ink.line([(231, 400), (164, 474)], w=1.4)
    ink.line([(164, 474), (176, 471)], w=1.4); ink.line([(164, 474), (168, 462)], w=1.4)
    if 0.25 <= t < 0.8:
        u = sm((t - 0.25) / 0.55); px_, py_ = lerp(172, 305, u), lerp(486, 421, u)
        ink.rect(px_ - 19, py_ - 4, px_ + 19, py_ + 4, fill=PAPER, outline=INK, w=1.0); ink.rect(px_ - 17, py_ - 2.5, px_ - 12, py_ + 2.5, fill=TAB[0], outline=None)
    nf = int(interp([(0.7, 0), (0.85, 97538), (1.1, 821362), (1.3, 1000000)], t)); pulse = 1.0 + 0.05 * math.sin(t * 9) if nf >= 1000000 else 1.0
    ink.text((433, 458), "followers", HAND, 22, (140, 140, 140), "mm"); ink.text((433, 497), fmt(nf), HAND, 58 * pulse, INK, "mm")
    for t0 in (1.3, 3.1, 4.9, 6.7): confetti(ink, 433, 497, t0, t)
    # ---- reality: starts at the same moment
    posts = real_posts(tr); fol = real_followers(tr)
    ink.text((240, 679), f"followers: {fmt(fol)}", HAND, 31, INK, "lm")
    cols = stair_state(posts)
    for k, nb in enumerate(cols):
        for b in range(nb): book(ink, COLX[k], 933 - (b + 1) * 9.7, i=k * 3 + b)
    done = posts >= 1000
    if tr < 2.6: kx, ky, kpose, walk = 115, 933, "stand", 0.0
    else:
        active = max([k for k, nb in enumerate(cols) if nb > 0] or [0]); top = 933 - cols[active] * 9.7
        if done: kx, ky = COLX[7] + 19, 933 - COLS[7] * 9.7
        else: kx, ky = COLX[active] + 19 - 6, top
        kpose = "cheer" if (done and tr >= 11.95) else ("place" if int(t * 4.2) % 2 == 0 else "stand"); walk = 0.0
        if tr < 3.2: kx = lerp(115, COLX[0] + 13, sm((tr - 2.6) / 0.6)); ky = 933; walk = (tr - 2.6) * 1.6
        if done and tr < 11.95: kpose = "stand"
    draw_kid(ink, kx, ky, kpose, walk)
    if tr >= 2.9:
        pn = f"{fmt(posts)} post" + ("" if posts == 1 else "s"); ink.text((612, 800), pn, HAND, 28, INK, "mm")
        ink.line([(580, 816), (528, 866)], w=1.4); ink.line([(528, 866), (541, 860)], w=1.4); ink.line([(528, 866), (532, 852)], w=1.4)
    confetti(ink, 560, 700, 12.0, tr, spread=170)
    a = sm((t - 8.3) / 0.45)
    if a > 0.01:
        c = int(255 - (255 - 22) * a); ink.text((360, 1045), "Post anyway.", INTER_B, 31, (c, c, c), "mm")
        c2 = int(255 - (255 - 105) * a); ink.text((360, 1076), CREDIT, INTER_SB, 14, (c2, c2, c2), "mm")
    return ink.out()

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
                if n % 90 == 0: print(n, "/", len(jobs), flush=True)
    elif cmd == "video":
        out, audio, fr = sys.argv[2:5]
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{fr}/f%04d.png", "-i", audio, "-t", str(DUR), "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True); print("wrote", out)
