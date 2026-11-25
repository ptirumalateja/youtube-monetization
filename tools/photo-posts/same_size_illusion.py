"""Photo post: Same Size (corridor illusion). Two identical stick figures in a dark corridor drawn in perspective: the far
one ("tomorrow") looks huge, the near one ("today") looks small. They are the same sprite, pixel for pixel.

  python3 same_size_illusion.py OUT.png

1080x1350 (4:5), drawn at 2x and downsampled. Slow Light look: deep charcoal-navy (never pure black), thin cream lines,
a warm gold glow at the end of the corridor. Text: Inter Medium + Lora Italic (fonts/, OFL).
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
S = 2; W, H = 1080 * S, 1350 * S
INTER = '/usr/share/fonts/opentype/inter/'
CREAM, GOLD, WHITE = (237, 230, 214), (240, 196, 120), (248, 244, 236)
F = lambda f, s: ImageFont.truetype(f, s * S)
sans = lambda s: F(INTER + 'Inter-Medium.otf', s)
ital = lambda s: F(os.path.join(HERE, 'fonts', 'Lora_500Medium_Italic.ttf'), s)

# ---- background: charcoal-navy with a soft gold glow at the vanishing point
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VP = (W * 0.5, H * 0.43)
d = np.hypot(xx - VP[0], (yy - VP[1]) * 1.1) / W
bg = np.zeros((H, W, 3), np.float32) + np.array([18, 20, 27], np.float32)
bg += np.array([120, 88, 40], np.float32)[None, None] * np.exp(-(d / 0.16) ** 2)[..., None] * 0.55
bg += np.array([40, 30, 18], np.float32)[None, None] * np.exp(-(d / 0.45) ** 2)[..., None] * 0.6
img = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert('RGBA')

# ---- the corridor: receding door frames, floor tiles and wall lines converging on VP
lines = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lines)
X0, X1, Y0, Y1 = -W * 0.08, W * 1.08, H * 0.13, H * 1.02          # the nearest frame (slightly off-frame)
def frame(k):                                                        # perspective scale for depth k (0 = near)
    s = 1 / (1 + 0.55 * k); return [VP[0] + (X0 - VP[0]) * s, VP[1] + (Y0 - VP[1]) * s, VP[0] + (X1 - VP[0]) * s, VP[1] + (Y1 - VP[1]) * s], s
ks = [k * 1.0 for k in range(0, 24)]
for k in ks:
    (a, b, c, e), s = frame(k)
    al = int(200 * min(1, 0.25 + 0.6 * s))
    ld.rectangle([a, b, c, e], outline=CREAM + (al // 2,), width=max(1, int(3 * S * s)))
for t in np.linspace(0, 1, 9):                                       # floor and ceiling rails
    for y_edge in (Y1, Y0):
        x = X0 + (X1 - X0) * t; ld.line([(x, y_edge), VP], fill=CREAM + (42,), width=2 * S)
for t in np.linspace(0, 1, 7):                                       # wall rails
    for x_edge in (X0, X1):
        y = Y0 + (Y1 - Y0) * t; ld.line([(x_edge, y), VP], fill=CREAM + (30,), width=2 * S)
# fade the lines into the glow near the vanishing point
fade = np.clip((np.hypot(xx - VP[0], yy - VP[1]) / W - 0.02) / 0.12, 0, 1)
la = np.asarray(lines).copy(); la[..., 3] = (la[..., 3] * fade).astype(np.uint8); img.alpha_composite(Image.fromarray(la))

# ---- one stick figure sprite, used twice at exactly the same size
FH = 300 * S
def figure():
    sp = Image.new('RGBA', (int(FH * 0.62), FH + 20 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(sp); w = sp.width
    lw = int(FH * 0.05); hx = w / 2; r = FH * 0.1
    d.ellipse([hx - r, 0, hx + r, 2 * r], fill=CREAM)
    neck, hip = (hx, 2 * r + FH * 0.02), (hx, FH * 0.58)
    d.line([neck, hip], fill=CREAM, width=lw)
    for sx in (-1, 1):
        d.line([(hx, FH * 0.3), (hx + sx * w * 0.36, FH * 0.5)], fill=CREAM, width=lw)    # arms
        d.line([hip, (hx + sx * w * 0.26, FH * 0.99)], fill=CREAM, width=lw)              # legs
    for p in [neck, hip, (hx, FH * 0.3)]:
        d.ellipse([p[0] - lw / 2, p[1] - lw / 2, p[0] + lw / 2, p[1] + lw / 2], fill=CREAM)
    for sx in (-1, 1):
        for p in [(hx + sx * w * 0.36, FH * 0.5), (hx + sx * w * 0.26, FH * 0.99)]:
            d.ellipse([p[0] - lw / 2, p[1] - lw / 2, p[0] + lw / 2, p[1] + lw / 2], fill=CREAM)
    return sp
fig = figure()
def place(cx, foot_y, glow):
    x, y = int(cx - fig.width / 2), int(foot_y - FH)
    pad = 60 * S; a = np.zeros((fig.height + 2 * pad, fig.width + 2 * pad), np.uint8); a[pad:-pad, pad:-pad] = np.asarray(fig)[..., 3]
    halo = Image.fromarray((np.asarray(Image.fromarray(a).filter(ImageFilter.GaussianBlur(18 * S))) * glow).astype(np.uint8))
    gl = Image.new('RGBA', halo.size, GOLD + (0,)); gl.putalpha(halo); img.alpha_composite(gl, (x - pad, y - pad)); img.alpha_composite(fig, (x, y))
    # contact shadow
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse([cx - fig.width * 0.42, foot_y - 10 * S, cx + fig.width * 0.42, foot_y + 12 * S], fill=(0, 0, 0, 140))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8 * S)))
    return x, y
# far figure: feet on the corridor floor deep in, head reaching toward the ceiling line there -> reads as a giant
kf = 4.2; (a, b, c, e), s = frame(kf); far = place(W * 0.56, e - 4 * S, 0.6)   # deep in: the figure nearly fills the corridor there
# near figure: feet on the floor in the foreground, small against the big near frame
near = place(W * 0.24, H * 0.79, 0.35)

# ---- text
txt = Image.new('RGBA', (W, H), (0, 0, 0, 0)); td = ImageDraw.Draw(txt); mask = Image.new('L', (W, H), 0); md = ImageDraw.Draw(mask)
def put(s_, f, col, x, y, anchor='ma', a=255):
    td.text((x, y), s_, font=f, fill=col + (a,), anchor=anchor); md.text((x, y), s_, font=f, fill=a, anchor=anchor)
put('Which one is bigger?', sans(66), WHITE, W / 2, 92 * S)
put('tomorrow', ital(40), GOLD, far[0] + fig.width + 22 * S, far[1] + FH * 0.42, 'lm', 230)
put('today', ital(40), CREAM, near[0] + fig.width + 18 * S, near[1] + FH * 0.45, 'lm', 230)
put('Same size.', sans(46), WHITE, W / 2, H - 256 * S)
put("Tomorrow's problems just look", ital(46), GOLD, W / 2, H - 198 * S)
put('bigger from here.', ital(46), GOLD, W / 2, H - 142 * S)
halo = mask.filter(ImageFilter.GaussianBlur(14 * S)).point(lambda v: int(v * 0.75))
img.alpha_composite(Image.merge('RGBA', (Image.new('L', (W, H), 8), Image.new('L', (W, H), 9), Image.new('L', (W, H), 14), halo)))
img.alpha_composite(txt)
# watermark
wm = Image.new('RGBA', (W, H), (0, 0, 0, 0)); wd = ImageDraw.Draw(wm); wf = sans(22)
x = W / 2 - (sum(wd.textlength(c, font=wf) for c in 'SLOW LIGHT') + 9 * 9 * S) / 2
for c in 'SLOW LIGHT':
    wd.text((x, H - 56 * S), c, font=wf, fill=(255, 255, 255, 140)); x += wd.textlength(c, font=wf) + 9 * S
img.alpha_composite(wm)
out = img.convert('RGB').resize((W // S, H // S), Image.LANCZOS); out.save(sys.argv[1])
print('figure height px (both):', FH // S, '| far top-left', (far[0] // S, far[1] // S), '| near top-left', (near[0] // S, near[1] // S))
a = np.asarray(out.convert('L')).astype(float)
for n, b in [('top', a[:150]), ('bot', a[-200:]), ('left', a[:, :80]), ('right', a[:, -80:])]: print(n, round(b.mean(), 1), round(b.std(), 1))
