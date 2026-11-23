"""Text and screen layer for Don't Tell Your Dreams.

- The song's lines, at the exact frames the reference shows them (timeline.json lyrics), lower third, sentence case.
- Shot D: radial speed lines closing in on him (the reference's manga lines), faint cream on the dark.
- The burst: a white-gold full-frame flash at TL.F.burst.

  python3 overlay.py still IN.jpg T OUT.jpg
  (compose.py imports draw() for the full video)
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
import sld_text
from sld_text import sstep

TL = json.load(open(os.path.join(HERE, 'timeline.json')))
FPS = TL['fps']; W, H = 1080, 1920
SHOTS = TL['shots']


def shot_at(t):
    name = SHOTS[0][1]
    for t0, n in SHOTS:
        if t >= t0: name = n
    return name


def speed_lines(img, t):
    if shot_at(t) != 'D': return img
    a = sstep(TL['D']['lines0'], TL['D']['lines0'] + 0.15, t)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    rng = np.random.default_rng(int(t * 12))            # the lines flicker at 12 fps, like the drawn original
    cx, cy = W / 2, H * 0.42
    for k in range(70):
        ang = rng.uniform(0, 2 * math.pi); r0 = rng.uniform(430, 620); r1 = 1500
        w = rng.uniform(1.5, 5)
        d.line([(cx + r0 * math.cos(ang), cy + r0 * math.sin(ang)), (cx + r1 * math.cos(ang), cy + r1 * math.sin(ang))],
               fill=(237, 230, 214, int(70 * a * rng.uniform(0.4, 1))), width=int(w))
    base = img.convert('RGBA'); base.alpha_composite(layer); return base.convert('RGB')


def flash(img, t):
    b = TL['F']['burst']
    k = 0.0 if t < b - 0.05 else max(0.0, 1 - abs(t - (b + 0.03)) / 0.16)
    if k <= 0: return img
    base = img.convert('RGBA'); base.alpha_composite(Image.new('RGBA', (W, H), (255, 246, 226, int(235 * min(1, k * 1.3))))); return base.convert('RGB')


def blocks(t):
    out = []
    for t0, t1, lines in TL['lyrics']:
        if t0 <= t < t1:
            out.append((lines, 50, 3, 1440, 1.0))
    return out


def draw(img, t, m=None):
    return sld_text.draw(flash(speed_lines(img, t), t), blocks(t))


if __name__ == '__main__':
    if sys.argv[1] == 'still':
        t = float(sys.argv[3])
        draw(Image.open(sys.argv[2]).convert('RGB'), t).save(sys.argv[4], quality=94)
