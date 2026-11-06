"""Text layer for Friends in Every Group (Slow Light Dark look, shared kit ../slow-light-dark-common/sld_text.py).

Hook "FRIENDS IN EVERY GROUP" big from frame 0; then one caption per friend (two lines) while a numbered tag pops above
their head (placed through the real camera, render.cjs meta); the tags stay, so the end card shows all six numbered:
"WHICH ONE ARE YOU?" / "COMMENT YOUR NUMBER".

  python3 overlay.py still IN.jpg T META.json OUT.jpg     overlay one rendered frame at time T (seconds)
  (compose.py imports draw() for the full video)
"""
import json, os, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
import sld_text
from sld_text import sstep, font, CREAM

TL = json.load(open(os.path.join(HERE, 'timeline.json')))
FPS = TL['fps']
RED = (216, 58, 46)


def blocks(t):
    out = []
    a = 1 - sstep(TL['hookOut'] - 0.2, TL['hookOut'], t)          # on from frame 0, no fade-in
    out.append((['FRIENDS IN', 'EVERY GROUP'], 76, 12, 230, a))
    for t0, seat, lines in TL['beats']:
        b = sstep(t0, t0 + 0.12, t) * (1 - sstep(t0 + TL['beatLen'] - 0.12, t0 + TL['beatLen'], t))
        if b > 0: out.append((lines, 54, 8, 250, b))
    e = sstep(TL['endCard'], TL['endCard'] + 0.3, t)
    out.append((['WHICH ONE', 'ARE YOU?'], 76, 12, 230, e))
    out.append((['COMMENT YOUR NUMBER'], 38, 8, 470, sstep(TL['endCard'] + 0.5, TL['endCard'] + 0.8, t)))
    return out


def tags(img, m, t):
    """Numbered discs above heads: cream ring, dark fill; the one being named is bigger and red-ringed."""
    base = img.convert('RGBA'); layer = Image.new('RGBA', base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    for g in m['tags']:
        if g['a'] <= 0: continue
        r = 34 + 10 * g['active'] + 8 * sstep(TL['endCard'], TL['endCard'] + 0.4, t)
        x, y = min(max(g['x'], 60), 1020), min(max(g['y'], 560), 1500)
        al = int(255 * g['a'])
        ring = tuple(int(CREAM[i] + (RED[i] - CREAM[i]) * g['active']) for i in range(3))
        d.ellipse((x - r, y - r, x + r, y + r), fill=(10, 11, 14, int(al * 0.82)), outline=ring + (al,), width=5)
        f = font(int(r * 1.15)); s = str(g['n']); w = d.textlength(s, font=f)
        d.text((x - w / 2, y - r * 0.78), s, font=f, fill=CREAM + (al,))
    base.alpha_composite(layer)
    return base.convert('RGB')


BEAT = {seat: t0 for t0, seat, _ in TL['beats']}


def bump(t, a, d):
    x = (t - a) / d
    return 0.0 if x <= 0 or x >= 1 else __import__('math').sin(__import__('math').pi * x) ** 2


def fx(img, m, t):
    """Cartoon accents: shake lines around the laugher, Z z z drifting up from the sleeper."""
    import math
    base = img.convert('RGBA'); layer = Image.new('RGBA', base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    pos = {g['seat']: (g['x'], g['y']) for g in m['tags']}
    u = t - BEAT['R2']
    k = max(bump(u, -0.05, 1.45), bump(u, 1.9, 1.2) * 0.6, bump(u, 4.2, 1.1) * 0.45)
    if k > 0.05 and 'R2' in pos:
        x, y = pos['R2']; y += 70                       # tag sits 0.3 m above the head
        for side in (-1, 1):
            for j, rr in enumerate((62, 84)):
                a0 = 200 if side < 0 else -20; wob = 6 * math.sin(t * 40 + j)
                box = (x - rr + wob, y - rr, x + rr + wob, y + rr)
                d.arc(box, a0 - 22, a0 + 22, fill=CREAM + (int(230 * k),), width=6)
    u = t - BEAT['L1'] - 0.6
    if u > 0 and 'L1' in pos:
        x, y = pos['L1']; y += 60
        for j in range(3):
            ph = (u * 0.55 + j / 3) % 1
            f = font(int(30 + 26 * ph), 'Bold')
            d.text((x + 30 + 60 * ph, y - 40 - 150 * ph), 'Z', font=f, fill=CREAM + (int(255 * math.sin(math.pi * ph) * min(1, u * 2)),))
    base.alpha_composite(layer)
    return base.convert('RGB')


def draw(img, t, m):
    return tags(fx(sld_text.draw(img, blocks(t)), m, t), m, t)


if __name__ == '__main__':
    if sys.argv[1] == 'still':
        t = float(sys.argv[3]); meta = json.load(open(sys.argv[4]))
        m = meta['frames'][min(round(t * FPS), len(meta['frames']) - 1)]
        draw(Image.open(sys.argv[2]).convert('RGB'), t, m).save(sys.argv[5], quality=94)
