#!/usr/bin/env python3
"""'What success looks like' (12 s, 1080x1920): EXPECTATION (1 post -> 1,000,000 followers, instantly) vs REALITY (he stacks 1,000 posts into a staircase, followers crawl, then it happens).
Our navy + gold theme, glowing stickman, safe zones (15% top / 20% bottom). Own wording. SFX only.
usage: render_success.py sheet OUT.png t... | frames OUTDIR | video OUT.mp4 AUDIO.wav FRAMESDIR"""
import sys, os, math, random, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_bridge3 as RB
from render_bridge3 import POSES, mix, walk_pose, draw_fig, font, spaced, MONO, INTER_XB, INTER_B, sm, lerp, GOLD, CREAM

W, H = 1080, 1920; FPS = 30; DUR = 12.0; SS = 2
TOP_Y, BOT_Y = 860, 1430
KT, KB = 1.5, 1.0
POSES["cheer"] = dict(lean=-2, thF=8, shF=3, thB=-8, shB=-5, uaF=158, faF=168, uaB=-158, faB=-168, tilt=-6)
POSES["cheer2"] = dict(lean=-4, thF=10, shF=4, thB=-10, shB=-6, uaF=140, faF=150, uaB=-140, faB=-150, tilt=-8)
POSES["carry"] = dict(lean=14, thF=8, shF=3, thB=-8, shB=-8, uaF=62, faF=96, uaB=50, faB=90, tilt=6)
POSES["place"] = dict(lean=30, thF=40, shF=6, thB=-12, shB=-14, uaF=72, faF=40, uaB=60, faB=34, tilt=12)
GOLD2 = (214, 130, 34)

# ------------------------------------------------------------------ timeline
def top_followers(t):
    keys = [(1.0, 0), (1.35, 97538), (1.9, 821362), (2.5, 1000000)]
    if t < keys[0][0]: return 0
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t0 <= t < t1: return int(v0 + (v1 - v0) * sm((t - t0) / (t1 - t0)))
    return 1000000
PT0, PT1 = 0.8, 8.0    # posting window
def post_p(t): return min(1.0, max(0.0, (t - PT0) / (PT1 - PT0)))
def posts_n(t): p = post_p(t); return int(1000 * (p * p * (3 - 2 * p) * 0.85 + p * 0.15))
def real_followers(t):
    if t < PT1 + 0.4:
        p = post_p(t); return int(810 * p ** 1.6)
    q = sm((t - (PT1 + 0.4)) / 1.5); return int(810 * (1000000 / 810) ** q)
def fmt(n): return f"{n:,}"
def stairs_state(t):
    n = posts_n(t); cols = []
    for k in range(10):
        comp = min(1.0, max(0.0, n / 100.0 - k)); cols.append(comp)
    cur = min(9, int(n / 100.0)) if n < 1000 else 9
    return n, cols, cur

# ------------------------------------------------------------------ drawing
def bg():
    if not hasattr(bg, "_b"): bg._b = RB.bg()
    return bg._b.copy()
def block(d, x, y, w, h, S=SS, alt=0):
    c1, c2 = ((255, 196, 84), (214, 130, 34)) if alt % 2 == 0 else ((248, 180, 66), (200, 120, 30))
    d.rounded_rectangle([x * S, y * S, (x + w) * S, (y + h) * S], radius=int(4 * S), fill=c1 + (255,))
    d.rounded_rectangle([x * S, (y + h * 0.55) * S, (x + w) * S, (y + h) * S], radius=int(4 * S), fill=c2 + (255,))
    d.line([((x + 4) * S, (y + 3) * S), ((x + w - 4) * S, (y + 3) * S)], fill=(255, 232, 160, 220), width=int(2 * S))
def confetti(img, cx, cy, t0, t):
    if t < t0 or t > t0 + 1.8: return
    d = ImageDraw.Draw(img, "RGBA"); rnd = random.Random(int(t0 * 10)); tau = t - t0
    for i in range(90):
        a = rnd.uniform(0, 2 * math.pi); sp = rnd.uniform(140, 520); x = cx + math.cos(a) * sp * tau * 0.7; y = cy + math.sin(a) * sp * tau * 0.5 + 140 * tau * tau
        col = rnd.choice([(255, 196, 84), (255, 232, 160), (255, 120, 90), (140, 190, 255), (250, 246, 232)]); al = int(255 * max(0, 1 - tau / 1.8))
        w, h_ = rnd.uniform(6, 12), rnd.uniform(14, 24); ang = rnd.uniform(0, math.pi) + tau * rnd.uniform(-8, 8)
        pts = [(x + (px * math.cos(ang) - py * math.sin(ang)), y + (px * math.sin(ang) + py * math.cos(ang))) for px, py in ((-w / 2, -h_ / 2), (w / 2, -h_ / 2), (w / 2, h_ / 2), (-w / 2, h_ / 2))]
        d.polygon(pts, fill=col + (al,))

def frame(t):
    S = SS; base = bg(); big = (W * S, H * S)
    lay = Image.new("RGBA", big, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    fig = Image.new("RGBA", big, (0, 0, 0, 0)); fd = ImageDraw.Draw(fig)
    # ground lines
    for y in (TOP_Y, BOT_Y):
        ld.line([(110 * S, y * S), (970 * S, y * S)], fill=(130, 138, 168, 200), width=int(3 * S))
    # ---- EXPECTATION: one post, instant success
    post_t = 0.7
    pose = POSES["stand"]; x_top = 250.0
    if t < 0.7: pose = POSES["stand"]
    elif t < 1.0: pose = mix(POSES["stand"], POSES["place"], sm((t - 0.7) / 0.15)) if t < 0.85 else mix(POSES["place"], POSES["stand"], sm((t - 0.85) / 0.15))
    elif t < 2.5: pose = POSES["stand"]
    else: pose = mix(POSES["cheer"], POSES["cheer2"], 0.5 + 0.5 * math.sin((t - 2.5) * 9)) if t > 2.7 else mix(POSES["stand"], POSES["cheer"], sm((t - 2.5) / 0.2))
    draw_fig(fd, x_top, TOP_Y + 2, 1, pose, KT, CREAM + (255,))
    # the single post flies out to the right (gold block)
    if 0.85 <= t < 1.4:
        u = sm((t - 0.85) / 0.55); bx = lerp(x_top + 70, 560, u); by = lerp(TOP_Y - 150, TOP_Y - 330, math.sin(u * math.pi * 0.5)) - 40 * math.sin(u * math.pi)
        block(ld, bx - 20, by - 10, 40, 22, S)
    # ---- REALITY: stack the posts
    n, cols, cur = stairs_state(t)
    stepx, stepw, x0, hstep = 58, 52, 340, 18
    for k, comp in enumerate(cols):
        hh = (k + 1) * hstep * comp; nb = int(math.ceil(hh / hstep - 1e-6)) if comp > 0 else 0
        for b in range(nb):
            top = BOT_Y - (b + 1) * hstep
            if (b + 1) * hstep <= hh + 0.1: block(ld, x0 + k * stepx, top, stepw, hstep - 2, S, alt=k + b)
    # figure on the current column
    ccomp = cols[cur]; ytop = BOT_Y - (cur + 1) * hstep * max(ccomp, 0.0) if n < 1000 else BOT_Y - 10 * hstep
    fx = x0 + cur * stepx + stepw / 2
    if t < PT0: fx, ytop = 250.0, BOT_Y
    if t < PT0: pose2 = POSES["stand"]
    elif n < 1000:
        ph = (t - PT0) * 2 * math.pi * 2.2; pose2 = mix(POSES["carry"], POSES["place"], 0.5 + 0.5 * math.sin(ph))
    else: pose2 = mix(POSES["cheer"], POSES["cheer2"], 0.5 + 0.5 * math.sin((t - PT1) * 9)) if t > PT1 + 1.9 else POSES["stand"]
    if t < PT0 + 0.9 and t >= PT0:   # walk from the left to the first column
        u = sm((t - PT0) / 0.9); fx = lerp(250.0, x0 + stepw / 2, u); ytop = BOT_Y; pose2 = walk_pose(u * 2 * math.pi * 1.5, 1.2)
    draw_fig(fd, fx, ytop + 2, 1, pose2, KB, CREAM + (255,))
    lay1 = lay.resize((W, H), Image.LANCZOS); fig1 = fig.resize((W, H), Image.LANCZOS)
    A = fig1.split()[3]; aw = np.asarray(A.filter(ImageFilter.GaussianBlur(20)), np.float32)
    gl = Image.new("RGBA", (W, H), (255, 214, 150, 0)); gl.putalpha(Image.fromarray((aw * 0.5).astype(np.uint8), "L")); base.alpha_composite(gl)
    base.alpha_composite(lay1); base.alpha_composite(fig1)
    confetti(base, 780, 690, 2.5, t); confetti(base, 700, 1180, PT1 + 1.9, t)
    # ---- text
    img = base.convert("RGB"); d = ImageDraw.Draw(img)
    def title_block(gold, white, al):
        if al < 0.01: return
        lay_t = Image.new("RGBA", (W, H), (0, 0, 0, 0)); tl = Image.new("L", (W, 150), 0); td = ImageDraw.Draw(tl); sz = 72
        while td.textlength(gold, font=font(INTER_XB, sz)) > 840 and sz > 40: sz -= 2
        td.text((W / 2, 75), gold, font=font(INTER_XB, sz), fill=255, anchor="mm")
        gc = np.zeros((150, W, 3), np.float32); gg = np.linspace(0, 1, 150, dtype=np.float32)[:, None, None]
        gc[:] = np.array([255, 214, 130], np.float32) * (1 - gg) + np.array([246, 164, 56], np.float32) * gg
        g_img = Image.fromarray(gc.astype(np.uint8), "RGB").convert("RGBA"); g_img.putalpha(tl); lay_t.alpha_composite(g_img, (0, 255))
        w2 = 50
        while ImageDraw.Draw(lay_t).textlength(white, font=font(INTER_XB, w2)) > 840 and w2 > 28: w2 -= 2
        ImageDraw.Draw(lay_t).text((W / 2, 415), white, font=font(INTER_XB, w2), fill=(246, 244, 240, 255), anchor="mm")
        la = np.asarray(lay_t, np.float32).copy(); la[..., 3] *= al; return Image.fromarray(la.astype(np.uint8), "RGBA")
    a1 = 1.0 if t < 9.3 else max(0.0, 1 - (t - 9.3) / 0.25); a2 = 0.0 if t < 9.55 else min(1.0, (t - 9.55) / 0.3)
    bi = img.convert("RGBA")
    for g_, w_, al in (("WHAT SUCCESS LOOKS LIKE", "ONE POST vs. WHAT IT TAKES", a1), ("KEEP POSTING.", "THE 1,000TH POST IS THE ONE THEY SEE.", a2)):
        lt = title_block(g_, w_, al)
        if lt is not None: bi.alpha_composite(lt)
    img = bi.convert("RGB"); d = ImageDraw.Draw(img)
    spaced(d, (130, 520), "EXPECTATION", font(MONO, 26), (186, 188, 202), 7)
    d.text((620, 700), fmt(top_followers(t)), font=font(INTER_B, 96), fill=(244, 242, 236) if top_followers(t) < 1000000 else GOLD, anchor="mm")
    d.text((620, 640), "followers", font=font(MONO, 26), fill=(130, 134, 158), anchor="mm")
    d.text((x_top + 215, TOP_Y - 120), "1 post", font=font(MONO, 26), fill=(176, 180, 204), anchor="mm")
    d.line([(x_top + 170, TOP_Y - 118), (x_top + 112, TOP_Y - 118)], fill=(150, 156, 184), width=3)
    d.line([(110, 985 - 20), (970, 985 - 20)], fill=(40, 44, 64), width=2)
    spaced(d, (130, 1040), "REALITY", font(MONO, 26), (124, 128, 148), 7)
    spaced(d, (400, 1040), f"followers: {fmt(real_followers(t))}", font(MONO, 26), (176, 182, 214) if real_followers(t) < 1000000 else GOLD, 3)
    if t > PT0 + 0.9:
        pn = fmt(n) + (" post" if n == 1 else " posts"); d.text((640, 1215), pn, font=font(MONO, 26), fill=(176, 180, 204), anchor="mm")
        d.line([(690, 1228), (740, 1262)], fill=(150, 156, 184), width=3)
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
