"""Same Size, raw version: a hand-drawn ink sketch of the corridor illusion on notebook paper.

  python3 same_size_sketch.py OUT.png

Wobbly double-stroked ink lines (nothing ruler-straight), a slightly uneven paper with grain and a soft phone-photo
vignette, handwritten text (Caveat, fonts/, OFL), one yellow highlighter stroke. The two stick figures are ONE drawing
pasted twice at the same size: the far one only looks bigger because of the corridor around it.
1080x1350 (4:5), drawn at 2x.
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
S = 2; W, H = 1080 * S, 1350 * S
R = np.random.default_rng(7)
INK = (28, 27, 30)
hand = lambda s, b=False: ImageFont.truetype(os.path.join(HERE, 'fonts', 'Caveat_700Bold.ttf' if b else 'Caveat_600SemiBold.ttf'), int(s * S))

# ---- paper: warm off-white, fibre grain, faint ruled lines and margin, uneven light like a phone photo of a page
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
paper = np.zeros((H, W, 3), np.float32) + np.array([236, 231, 219], np.float32)
paper += R.normal(0, 4.5, (H, W, 1)).astype(np.float32)
blot = Image.fromarray((R.random((H // 40, W // 40)) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
paper += (np.asarray(blot, np.float32)[..., None] - 128) * 0.05
light = 1 - 0.16 * ((xx / W - 0.42) ** 2 + (yy / H - 0.38) ** 2) * 2.2          # the page is lit a little off-centre
paper *= light[..., None]
img = Image.fromarray(np.clip(paper, 0, 255).astype(np.uint8)).convert('RGBA')
d = ImageDraw.Draw(img)
for y in range(int(150 * S), H, int(54 * S)):                                     # faint blue ruled lines
    d.line([(0, y), (W, y + R.normal(0, 1))], fill=(150, 175, 205, 60), width=S)
d.line([(96 * S, 0), (97 * S, H)], fill=(215, 120, 120, 70), width=S)            # red margin

ink = Image.new('RGBA', (W, H), (0, 0, 0, 0)); di = ImageDraw.Draw(ink)
def wob(p0, p1, w=3.0, a=235, passes=2, amp=1.6):
    """A hand-drawn line: slightly curved, jittered, drawn twice with a small offset, uneven pressure."""
    (x0, y0), (x1, y1) = p0, p1; L = math.hypot(x1 - x0, y1 - y0); n = max(2, int(L / (14 * S)))
    nx, ny = -(y1 - y0) / (L + 1e-6), (x1 - x0) / (L + 1e-6)
    for k in range(passes):
        bow = R.normal(0, L * 0.006); off = R.normal(0, 1.2 * S, 2) * (k > 0)
        pts = []
        for i in range(n + 1):
            u = i / n; j = R.normal(0, amp * S * 0.35)
            pts.append((x0 + (x1 - x0) * u + nx * (bow * math.sin(math.pi * u) + j) + off[0], y0 + (y1 - y0) * u + ny * (bow * math.sin(math.pi * u) + j) + off[1]))
        di.line(pts, fill=INK + (int(a * (0.85 if k else 1)),), width=max(1, int(w * S * (0.75 if k else 1))), joint='curve')

# ---- corridor in one-point perspective
VP = (W * 0.52, H * 0.42)
X0, X1, Y0, Y1 = W * 0.04, W * 0.98, H * 0.155, H * 0.80
def at(k):  # frame rectangle at depth k
    s = 1 / (1 + 0.5 * k); return [VP[0] + (X0 - VP[0]) * s, VP[1] + (Y0 - VP[1]) * s, VP[0] + (X1 - VP[0]) * s, VP[1] + (Y1 - VP[1]) * s], s
for k in [0, 1, 2, 3, 4.2, 5.6, 7.4, 10, 14]:
    (a, b, c, e), s = at(k); w = 3.2 * max(0.45, s ** 0.5)
    for p, q in [((a, b), (c, b)), ((c, b), (c, e)), ((c, e), (a, e)), ((a, e), (a, b))]: wob(p, q, w)
for t in [0, 0.18, 0.36, 0.54, 0.72, 0.9, 1.0]:                                  # floor boards converging
    x = X0 + (X1 - X0) * t; (a, b, c, e), s = at(14); xe = VP[0] + (x - VP[0]) * s
    wob((x, Y1), (xe, e), 2.2, 200)
for t in [0.0, 1.0]:
    for (xa, ya) in [(X0, Y0), (X1, Y0)]:
        (a, b, c, e), s = at(14); wob((xa, ya), (VP[0] + (xa - VP[0]) * s, VP[1] + (ya - VP[1]) * s), 2.6)
# the far opening: a little crosshatched darkness at the end, a few rays of pencil light
(a, b, c, e), s = at(14)
for i in range(16):
    u = i / 15; wob((a + (c - a) * u, b), (a + (c - a) * u - 8 * S, e), 1.2, 120, 1, 1.0)

# ---- ONE stick figure, drawn once by hand, used twice
FH = 300 * S
def figure():
    sp = Image.new('RGBA', (int(FH * 0.7), int(FH * 1.04)), (0, 0, 0, 0)); g = ImageDraw.Draw(sp); w = sp.width; hx = w / 2
    global di; save = di; di = g
    r = FH * 0.1; c0 = (hx, r + 4 * S)
    pts = [(c0[0] + r * math.cos(t) * (1 + 0.04 * math.sin(3 * t)), c0[1] + r * math.sin(t) * (1 + 0.04 * math.sin(3 * t))) for t in np.linspace(-0.3, 2 * math.pi + 0.15, 40)]
    g.line(pts, fill=INK + (240,), width=int(5 * S), joint='curve')
    neck, hip = (hx, 2 * r + 6 * S), (hx + 2 * S, FH * 0.6)
    wob(neck, hip, 5.0, 240); wob((hx, FH * 0.32), (hx - w * 0.34, FH * 0.52), 4.6, 240); wob((hx, FH * 0.32), (hx + w * 0.33, FH * 0.5), 4.6, 240)
    wob(hip, (hx - w * 0.22, FH * 0.99), 5.0, 240); wob(hip, (hx + w * 0.25, FH * 0.99), 5.0, 240)
    di = save; return sp
fig = figure()
def place(cx, foot_y):
    x, y = int(cx - fig.width / 2), int(foot_y - FH)
    sh = ImageDraw.Draw(ink)                                                       # scribbled ground shadow
    for i in range(7):
        yy_ = foot_y + 2 * S + i * 2.2 * S; sh.line([(cx - fig.width * 0.42 + i * 6 * S, yy_), (cx + fig.width * 0.38 - i * 6 * S, yy_ + R.normal(0, S))], fill=INK + (90,), width=int(1.6 * S))
    ink.alpha_composite(fig, (x, y)); return x, y
(a, b, c, e), s = at(4.6); far = place(W * 0.56, e - 2 * S)
near = place(W * 0.25, H * 0.76)

# ---- handwriting, and one highlighter stroke
tl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); tdraw = ImageDraw.Draw(tl)
def hl(x0, y0, x1, y1):   # yellow highlighter behind a word
    m = Image.new('RGBA', (W, H), (0, 0, 0, 0)); md = ImageDraw.Draw(m)
    md.polygon([(x0 - 8 * S, y0 + 6 * S), (x1 + 10 * S, y0), (x1 + 6 * S, y1), (x0 - 10 * S, y1 + 5 * S)], fill=(255, 224, 70, 120))
    img.alpha_composite(m.filter(ImageFilter.GaussianBlur(1.5 * S)))
def write(text, f, x, y, anchor='ma', rot=0.0, col=INK):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(lay).text((x, y), text, font=f, fill=col + (235,), anchor=anchor)
    if rot: lay = lay.rotate(rot, center=(x, y), resample=Image.BICUBIC)
    tl.alpha_composite(lay); return ImageDraw.Draw(Image.new('L', (1, 1))).textbbox((x, y), text, font=f, anchor=anchor)
write('Which one is bigger?', hand(92, True), W / 2, 40 * S, rot=0.8)
write('tomorrow', hand(66, True), far[0] + fig.width + 4 * S, far[1] + FH * 0.3, 'lm', rot=4)
write('today', hand(66, True), near[0] + fig.width - 2 * S, near[1] + FH * 0.36, 'lm', rot=-3)
bb = write('Same size.', hand(78, True), W / 2, H - 262 * S, rot=-0.6)
hl(bb[0], bb[1] + 14 * S, bb[2], bb[3] + 4 * S)
write("Tomorrow's problems just look", hand(62), W / 2, H - 180 * S, rot=-0.4)
write('bigger from here.', hand(62), W / 2, H - 120 * S, rot=-0.3)
img.alpha_composite(ink.filter(ImageFilter.GaussianBlur(0.6 * S)))
img.alpha_composite(tl.filter(ImageFilter.GaussianBlur(0.4 * S)))
write_wm = ImageDraw.Draw(img); wf = hand(34)
write_wm.text((W - 50 * S, H - 40 * S), '— slow light', font=wf, fill=(90, 88, 92, 200), anchor='rm')
out = img.convert('RGB').resize((W // S, H // S), Image.LANCZOS); out.save(sys.argv[1])
print('both figures', fig.size[1] // S, 'px tall (same drawing)')
