"""V2 text layer (goal-first edit). python3 overlay2.py frames_dir meta.json out_dir
Very little text: one line per beat, gone before the action it would cover."""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

src, metaf, out = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True)
meta = json.load(open(metaf))
CREAM = (255, 244, 224); RED = (214, 62, 48); EMER = (70, 255, 180); GOLD = (255, 205, 110)
HOOK = '/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf'
MONO = '/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf'
_fc = {}
def F(p, s):
    if (p, s) not in _fc: _fc[(p, s)] = ImageFont.truetype(p, s)
    return _fc[(p, s)]
def ss(a, b, x):
    u = min(1, max(0, (x - a) / (b - a))); return u * u * (3 - 2 * u)
def text(d, xy, s, font, fill=CREAM, alpha=1.0, anchor='mm'):
    if alpha <= 0.01 or not s: return
    d.text(xy, s, font=font, fill=tuple(fill) + (int(255 * alpha),), stroke_width=max(3, font.size // 9), stroke_fill=(0, 0, 0, int(230 * alpha)), anchor=anchor)
def typed(s, t0, t, cps=34): return s[:int(max(0, (t - t0) * cps))]
def chip(d, xy, s, font, alpha=1.0, color=RED):
    if alpha <= 0.01: return
    x, y = xy; w = d.textlength(s, font=font); h = font.size; pad = int(h * 0.45)
    d.rounded_rectangle([x - w / 2 - pad, y - h * 0.62 - pad * 0.4, x + w / 2 + pad, y + h * 0.62 + pad * 0.4], radius=int(h * 0.25), fill=tuple(color) + (int(235 * alpha),))
    d.text((x, y), s, font=font, fill=CREAM + (int(255 * alpha),), anchor='mm')

def frame(f, img):
    t = f / 30; k = img.width / 1080; X = lambda v: v * k; cx = img.width / 2
    m = meta.get(str(f), {}); sc = lambda p: (p[0] * img.width / m['_w'], p[1] * img.height / m['_h'])
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    # 0.1-1.0: the eye's verdict, cut the instant the ball starts bending back
    if 0.08 < t < 1.0:
        text(d, (cx, X(330)), typed("THAT'S GOING WIDE—", 0.08, t, 40), F(HOOK, int(X(100))))
    # rewind
    if 2.52 < t < 4.0:
        a = 1 - ss(3.8, 4.0, t); s = 1.15 - 0.15 * ss(2.52, 2.7, t)
        text(d, (cx, X(330)), 'HOW DID THAT', F(HOOK, int(X(104) * s)), alpha=a)
        text(d, (cx, X(450)), 'GO IN?!', F(HOOK, int(X(132) * s)), alpha=a)
    # the setup
    if 4.05 < t < 7.0:
        a = ss(4.05, 4.2, t) * (1 - ss(6.75, 7.0, t))
        text(d, (cx, X(330)), "THIS SHOULD'VE", F(HOOK, int(X(96))), alpha=a)
        text(d, (cx, X(440)), 'MISSED.', F(HOOK, int(X(120))), fill=(255, 120, 100), alpha=a)
        chip(d, (cx, X(545)), 'ROBERTO CARLOS · 1997 · 35 M', F(MONO, int(X(34))), alpha=a * ss(4.4, 4.6, t))
    # bullet time
    if 7.2 < t < 11.8:
        a = ss(7.25, 7.5, t) * (1 - ss(11.4, 11.75, t))
        text(d, (cx, X(330)), 'THE SPIN', F(HOOK, int(X(104))), alpha=a)
        text(d, (cx, X(445)), 'CHANGED EVERYTHING.', F(HOOK, int(X(80))), fill=EMER, alpha=a * ss(7.7, 7.9, t))
        if m.get('forceTip') and m['forceTip'][2]:
            fx, fy = sc(m['forceTip']); al = ss(8.8, 9.1, t) * (1 - ss(11.3, 11.7, t))
            fx = min(max(fx, X(220)), img.width - X(220)); fy = min(max(fy, X(640)), X(1450))
            chip(d, (fx, fy - X(40)), 'MAGNUS EFFECT', F(MONO, int(X(34))), alpha=al, color=(20, 120, 90))
    # overhead: expected vs actual, then the thesis
    # lands with the second goal and carries over the cut to the overhead
    if 13.8 < t < 17.1:
        a = ss(13.8, 13.9, t) * (1 - ss(16.9, 17.1, t)); s = 1.2 - 0.2 * ss(13.8, 14.0, t)
        text(d, (cx, X(330)), 'IT BENT BACK IN.', F(HOOK, int(X(100) * s)), alpha=a)
    if t >= 15.0:
        al = ss(15.4, 15.7, t)
        if m.get('expEnd') and m['expEnd'][2]:
            ex, ey = sc(m['expEnd']); chip(d, (min(ex, img.width - X(170)), ey - X(55)), 'EXPECTED', F(MONO, int(X(32))), alpha=al)
        if m.get('entry') and m['entry'][2]:
            nx, ny = sc(m['entry']); chip(d, (max(nx - X(30), X(150)), ny - X(55)), 'ACTUAL', F(MONO, int(X(32))), alpha=al, color=(20, 140, 100))
        a2 = ss(17.1, 17.3, t)
        text(d, (cx, X(225)), typed('PHYSICS.', 17.1, t, 30), F(HOOK, int(X(112))), alpha=a2)
        text(d, (cx, X(340)), typed('NOT LUCK.', 17.45, t, 30), F(HOOK, int(X(112))), fill=EMER, alpha=a2)
    af = ss(4.1, 4.4, t)
    text(d, (cx, X(1545)), 'RECREATION · SIMULATED BALL FLIGHT', F(MONO, int(X(26))), fill=(200, 210, 220), alpha=af * 0.8)
    return Image.alpha_composite(img.convert('RGBA'), lay).convert('RGB')

fs = sorted(x for x in os.listdir(src) if x.startswith('f') and x.endswith('.jpg'))
W0 = Image.open(os.path.join(src, fs[0])).size
for kk in meta: meta[kk]['_w'], meta[kk]['_h'] = W0
for fn in fs: frame(int(fn[1:5]), Image.open(os.path.join(src, fn))).save(os.path.join(out, fn), quality=95)
print('overlaid', len(fs))
