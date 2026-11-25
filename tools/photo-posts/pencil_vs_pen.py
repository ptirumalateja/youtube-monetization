"""Photo post: Pencil vs Pen. A notebook page: "What people remember about you... 50 years later".
"your money" is pencil, almost fully erased (smudge + eraser crumbs); "your job title" pencil, half erased;
"how you made them feel" is blue ballpoint, pressed hard, circled in red. Punchline: "Some things are written in
pencil. Kindness is written in pen."

  python3 pencil_vs_pen.py OUT.png

1080x1350 (4:5), drawn at 2x. Handwriting: Caveat (fonts/, OFL). Same paper as same_size_sketch.py.
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
S = 2; W, H = 1080 * S, 1350 * S
R = np.random.default_rng(11)
hand = lambda s, b=False: ImageFont.truetype(os.path.join(HERE, 'fonts', 'Caveat_700Bold.ttf' if b else 'Caveat_600SemiBold.ttf'), int(s * S))
INK, BLUE, RED, GRAPHITE = (28, 27, 30), (28, 52, 140), (196, 44, 40), (88, 88, 92)

# ---- paper (as in same_size_sketch.py)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
paper = np.zeros((H, W, 3), np.float32) + np.array([236, 231, 219], np.float32)
paper += R.normal(0, 4.5, (H, W, 1)).astype(np.float32)
blot = Image.fromarray((R.random((H // 40, W // 40)) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
paper += (np.asarray(blot, np.float32)[..., None] - 128) * 0.05
paper *= (1 - 0.16 * ((xx / W - 0.45) ** 2 + (yy / H - 0.4) ** 2) * 2.2)[..., None]
img = Image.fromarray(np.clip(paper, 0, 255).astype(np.uint8)).convert('RGBA')
d = ImageDraw.Draw(img)
for y in range(int(150 * S), H, int(54 * S)): d.line([(0, y), (W, y + R.normal(0, 1))], fill=(150, 175, 205, 60), width=S)
d.line([(96 * S, 0), (97 * S, H)], fill=(215, 120, 120, 70), width=S)

def text_layer(text, f, x, y, col, rot=0.0, anchor='mm', alpha=255):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(lay).text((x, y), text, font=f, fill=col + (alpha,), anchor=anchor)
    return lay.rotate(rot, center=(x, y), resample=Image.BICUBIC) if rot else lay

def pencil(lay):
    """Graphite: grainy, a bit light, slightly broken strokes."""
    a = np.asarray(lay).astype(np.float32); grain = R.random(a.shape[:2]).astype(np.float32)
    a[..., 3] *= 0.55 + 0.45 * (grain > 0.18); a[..., 3] *= 0.85
    return Image.fromarray(a.astype(np.uint8))

def erase(lay, keep, seed):
    """Rub it out: eraser strokes take the graphite down to `keep`, leave a grey smudge and crumbs around it."""
    rr = np.random.default_rng(seed); a = np.asarray(lay).astype(np.float32); al = a[..., 3]
    ys, xs = np.nonzero(al > 10); x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    m = Image.new('L', (W, H), 0); md = ImageDraw.Draw(m)
    for _ in range(26):   # back-and-forth eraser strokes across the word
        cx = rr.uniform(x0, x1); cy = rr.uniform(y0, y1); L = rr.uniform(60, 160) * S; ang = rr.normal(-0.25, 0.15)
        md.line([(cx - L * math.cos(ang), cy - L * math.sin(ang)), (cx + L * math.cos(ang), cy + L * math.sin(ang))], fill=255, width=int(rr.uniform(26, 44) * S))
    m = np.asarray(m.filter(ImageFilter.GaussianBlur(10 * S))).astype(np.float32) / 255
    a[..., 3] = al * (1 - m * (1 - keep)) * (0.75 + 0.25 * rr.random(al.shape))
    out = Image.fromarray(a.astype(np.uint8))
    smudge = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(smudge)
    sd.rounded_rectangle([x0 - 30 * S, y0 - 10 * S, x1 + 40 * S, y1 + 12 * S], radius=30 * S, fill=GRAPHITE + (22,))
    smudge = smudge.filter(ImageFilter.GaussianBlur(30 * S))
    crumbs = Image.new('RGBA', (W, H), (0, 0, 0, 0)); cd = ImageDraw.Draw(crumbs)
    for _ in range(14):   # a few rolled eraser crumbs: small, irregular, grey-pink
        cx = rr.uniform(x0 - 40 * S, x1 + 90 * S); cy = rr.uniform(y1 + 4 * S, y1 + 60 * S); r = rr.uniform(1.5, 3.5) * S
        pts = [(cx + r * rr.uniform(1.5, 3.5) * math.cos(a), cy + r * rr.uniform(0.7, 1.3) * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 9)[:-1]]
        cd.polygon(pts, fill=(170, 140, 140, 170))
    return smudge, out, crumbs.filter(ImageFilter.GaussianBlur(0.6 * S))

def wob_ellipse(dr, cx, cy, rx, ry, col, w, turns=1.9, seed=0):
    rr = np.random.default_rng(seed); pts = []; ph = rr.uniform(0, 6, 3)
    for t in np.linspace(0, 2 * math.pi * turns, 260):
        k = 1 + 0.035 * math.sin(2 * t + ph[0]) + 0.02 * math.sin(5 * t + ph[1]) + 0.025 * t
        pts.append((cx + rx * k * math.cos(t - 0.4), cy + ry * k * math.sin(t - 0.4)))
    dr.line(pts, fill=col + (215,), width=int(w * S), joint='curve')

layers = []
# title
layers.append(text_layer('What people remember', hand(86, True), W / 2, 150 * S, INK, rot=0.8))
layers.append(text_layer('about you...', hand(86, True), W / 2, 238 * S, INK, rot=0.6))
layers.append(text_layer('50 years later', hand(60), W / 2 + 150 * S, 322 * S, RED, rot=-4))
for l in layers: img.alpha_composite(l)
# 1. your money: pencil, almost gone
sm, t, cr = erase(pencil(text_layer('your money', hand(96, True), W / 2, 520 * S, GRAPHITE, rot=-1.5)), 0.12, 3)
img.alpha_composite(sm); img.alpha_composite(t); img.alpha_composite(cr)
# 2. your job title: pencil, half gone
sm, t, cr = erase(pencil(text_layer('your job title', hand(96, True), W / 2, 740 * S, GRAPHITE, rot=1.0)), 0.45, 5)
img.alpha_composite(sm); img.alpha_composite(t); img.alpha_composite(cr)
# 3. how you made them feel: ballpoint, pressed hard (drawn twice, offset), circled in red pen
pen = text_layer('how you made', hand(104, True), W / 2, 948 * S, BLUE, rot=-1.0)
pen.alpha_composite(text_layer('them feel', hand(104, True), W / 2, 1052 * S, BLUE, rot=-1.0))
img.alpha_composite(pen.transform(pen.size, Image.AFFINE, (1, 0, -1.2 * S, 0, 1, -0.8 * S)))
img.alpha_composite(pen)
circ = Image.new('RGBA', (W, H), (0, 0, 0, 0)); wob_ellipse(ImageDraw.Draw(circ), W / 2, 1000 * S, 360 * S, 128 * S, RED, 4.5, turns=1.85, seed=2)
img.alpha_composite(circ.filter(ImageFilter.GaussianBlur(0.5 * S)))
# punchline, with a highlighter stroke on "pen"
img.alpha_composite(text_layer('Some things are written in pencil.', hand(62), W / 2, 1196 * S, INK, rot=-0.5))
pl = 'Kindness is written in pen.'; f = hand(70, True); x0 = W / 2; y0 = 1272 * S
bb = ImageDraw.Draw(Image.new('L', (1, 1))).textbbox((x0, y0), pl, font=f, anchor='mm'); pw = ImageDraw.Draw(Image.new('L', (1, 1))).textlength('pen.', font=f)
hl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(hl).polygon([(bb[2] - pw - 10 * S, bb[1] + 18 * S), (bb[2] + 8 * S, bb[1] + 12 * S), (bb[2] + 4 * S, bb[3] + 4 * S), (bb[2] - pw - 14 * S, bb[3] + 8 * S)], fill=(255, 224, 70, 130))
img.alpha_composite(hl.filter(ImageFilter.GaussianBlur(1.5 * S)))
img.alpha_composite(text_layer(pl, f, x0, y0, INK, rot=-0.4))
ImageDraw.Draw(img).text((W - 50 * S, H - 30 * S), '— slow light', font=hand(34), fill=(90, 88, 92, 200), anchor='rm')
out = img.convert('RGB').filter(ImageFilter.GaussianBlur(0.35 * S)).resize((W // S, H // S), Image.LANCZOS); out.save(sys.argv[1])
print('ok')
