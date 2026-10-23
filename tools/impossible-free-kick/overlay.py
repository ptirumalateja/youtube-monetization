"""Text layer for the free-kick reel. python3 overlay.py frames_dir meta.json out_dir
Cream text with a heavy black stroke, red chips (playbook 3.7), typed hooks, countdown."""
import json, os, sys, math
from PIL import Image, ImageDraw, ImageFont

src, metaf, out = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True)
meta = json.load(open(metaf))
CREAM = (255, 244, 224); RED = (214, 62, 48); EMER = (70, 255, 180); BLACK = (0, 0, 0)
FD = '/usr/share/fonts/truetype/'
HOOK = FD + 'liberation/LiberationSans-BoldItalic.ttf'
MONO = FD + 'liberation/LiberationMono-Bold.ttf'
_fc = {}
def F(path, size):
    k = (path, size)
    if k not in _fc: _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]
def ss(a, b, x):
    u = min(1, max(0, (x - a) / (b - a))); return u * u * (3 - 2 * u)

def text(d, xy, s, font, fill=CREAM, alpha=1.0, stroke=None, anchor='mm', spacing=0):
    if alpha <= 0.01 or not s: return
    sw = stroke if stroke is not None else max(3, font.size // 9)
    col = tuple(fill) + (int(255 * alpha),)
    d.text(xy, s, font=font, fill=col, stroke_width=sw, stroke_fill=(0, 0, 0, int(230 * alpha)), anchor=anchor)
def typed(s, t0, t, cps=26):
    n = int(max(0, (t - t0) * cps)); return s[:n]
def chip(d, xy, s, font, alpha=1.0, color=RED, fg=CREAM):
    if alpha <= 0.01: return
    x, y = xy; w = d.textlength(s, font=font); h = font.size
    pad = int(h * 0.45)
    d.rounded_rectangle([x - w / 2 - pad, y - h * 0.62 - pad * 0.4, x + w / 2 + pad, y + h * 0.62 + pad * 0.4], radius=int(h * 0.25), fill=tuple(color) + (int(235 * alpha),))
    d.text((x, y), s, font=font, fill=tuple(fg) + (int(255 * alpha),), anchor='mm')

def frame(f, img):
    t = f / 30
    Wr = img.width; k = Wr / 1080
    m = meta.get(str(f), {})
    sc = lambda p: (p[0] * img.width / m['_w'], p[1] * img.height / m['_h']) if p else None
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    X = lambda v: v * k
    cx = img.width / 2
    # ---- hook 0-2.7
    a = 1 - ss(2.45, 2.75, t)
    if t < 2.8:
        text(d, (cx, X(330)), typed('THIS BALL WAS', 0.0, t, 30), F(HOOK, int(X(92))), alpha=a)
        text(d, (cx, X(445)), typed('GOING OUT.', 0.45, t, 30), F(HOOK, int(X(118))), alpha=a)
        chip(d, (cx, X(560)), 'ROBERTO CARLOS · 1997', F(MONO, int(X(36))), alpha=a * ss(0.9, 1.15, t))
    # ---- freeze question + countdown 4.95-8.3
    if 4.95 < t < 8.45:
        a = ss(4.95, 5.15, t) * (1 - ss(8.15, 8.45, t))
        text(d, (cx, X(330)), 'IN OR OUT?', F(HOOK, int(X(120))), alpha=a)
        text(d, (cx, X(430)), 'DECIDE BEFORE IT MOVES', F(MONO, int(X(38))), alpha=a * ss(5.3, 5.6, t))
        for i, t0 in enumerate([5.0, 6.0, 7.0]):
            if t0 <= t < t0 + 1.0:
                u = t - t0; s = 1.25 - 0.25 * ss(0, 0.18, u); al = a * (1 - ss(0.75, 0.98, u))
                text(d, (cx, X(1440)), str(3 - i), F(HOOK, int(X(210) * s)), alpha=al)
        if m.get('head') and m['head'][2]:
            hx, hy = sc(m['head'])
            al = a * ss(5.9, 6.2, t)
            text(d, (min(max(hx, X(200)), img.width - X(200)), hy - X(60)), 'HEADING HERE', F(MONO, int(X(30))), fill=(255, 140, 120), alpha=al)
    # ---- bullet time 8.7-12.2
    if 8.7 < t < 12.3:
        a1 = ss(8.75, 9.0, t) * (1 - ss(9.95, 10.15, t))
        text(d, (cx, X(300)), 'HIT WITH THE OUTSIDE', F(MONO, int(X(50))), alpha=a1)
        text(d, (cx, X(370)), 'OF HIS LEFT FOOT', F(MONO, int(X(50))), alpha=a1)
        text(d, (cx, X(460)), '= HUGE SIDESPIN', F(MONO, int(X(50))), fill=(255, 205, 110), alpha=a1 * ss(9.25, 9.45, t))
        a2 = ss(10.1, 10.3, t) * (1 - ss(12.0, 12.3, t))
        text(d, (cx, X(300)), 'SPIN DRAGS THE AIR', F(MONO, int(X(52))), alpha=a2)
        text(d, (cx, X(370)), 'ONE WAY...', F(MONO, int(X(52))), alpha=a2)
        text(d, (cx, X(470)), '...THE BALL GETS', F(MONO, int(X(52))), fill=EMER, alpha=a2 * ss(10.7, 10.9, t))
        text(d, (cx, X(540)), 'PUSHED THE OTHER.', F(MONO, int(X(52))), fill=EMER, alpha=a2 * ss(10.7, 10.9, t))
    if 9.9 < t < 14.4 and m.get('forceTip') and m['forceTip'][2]:
        fx, fy = sc(m['forceTip']); a = ss(9.9, 10.2, t) * (1 - ss(14.0, 14.4, t))
        fx = min(max(fx, X(230)), img.width - X(230)); fy = min(max(fy, X(640)), X(1500))
        chip(d, (fx, fy - X(40)), 'MAGNUS EFFECT', F(MONO, int(X(34))), alpha=a, color=(20, 120, 90))
    # ---- the spiral 12.6-14.3
    if 12.6 < t < 14.4:
        a = ss(12.7, 12.95, t) * (1 - ss(14.05, 14.3, t))
        text(d, (cx, X(300)), 'AND AS IT SLOWS DOWN,', F(MONO, int(X(50))), alpha=a)
        text(d, (cx, X(375)), 'IT BENDS HARDER.', F(MONO, int(X(62))), fill=EMER, alpha=a * ss(13.2, 13.4, t))
    # ---- reveal 15.1-17.2: red line = what your eyes said, green = what happened
    if 15.15 < t < 17.3:
        a = ss(15.2, 15.45, t) * (1 - ss(17.05, 17.3, t))
        chip(d, (cx - X(200), X(300)), 'YOUR EYES', F(MONO, int(X(34))), alpha=a)
        chip(d, (cx + X(200), X(300)), 'THE BALL', F(MONO, int(X(34))), alpha=a, color=(20, 140, 100))
    # ---- in off the post, thesis
    if 17.24 < t < 18.6:
        a = ss(17.25, 17.4, t) * (1 - ss(18.3, 18.6, t)); s = 1.2 - 0.2 * ss(17.25, 17.45, t)
        text(d, (cx, X(330)), 'IN. OFF THE POST.', F(HOOK, int(X(96) * s)), alpha=a)
    if 17.8 < t < 19.3:
        a = ss(17.85, 18.05, t) * (1 - ss(19.0, 19.3, t))
        text(d, (cx, X(460)), typed('PHYSICS, NOT LUCK.', 17.85, t, 34), F(HOOK, int(X(84))), fill=EMER, alpha=a)
    # ---- footer (from the strike on; off for the hook and the rewind)
    af = ss(3.0, 3.4, t) * (1 - ss(18.4, 18.7, t))
    text(d, (cx, X(1545)), 'RECREATION · SIMULATED BALL FLIGHT', F(MONO, int(X(26))), fill=(200, 210, 220), alpha=af * 0.85)
    if t > 18.55 and t < 19.85:
        a = ss(18.55, 18.7, t) * (1 - ss(19.6, 19.85, t))
        text(d, (cx, X(1545)), 'REWIND · WATCH IT AGAIN', F(MONO, int(X(34))), fill=(255, 210, 120), alpha=a)
    return Image.alpha_composite(img.convert('RGBA'), lay).convert('RGB')

fs = sorted(x for x in os.listdir(src) if x.startswith('f') and x.endswith('.jpg'))
W0 = Image.open(os.path.join(src, fs[0])).size
for k in meta: meta[k]['_w'], meta[k]['_h'] = W0
for fn in fs:
    f = int(fn[1:5])
    im = frame(f, Image.open(os.path.join(src, fn)))
    im.save(os.path.join(out, fn), quality=95)
print('overlaid', len(fs))
