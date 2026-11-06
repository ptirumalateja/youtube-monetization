"""Text layer for The Rock Never Moved (Slow Light Dark text kit, plus orange-yellow mocking words).

- Hook "HE PUSHED IT" / "EVERY DAY." over the first two cuts.
- The counter "DAY 1" ... "DAY 365" slams in on every cut (scale punch on the impact).
- In the mocking cuts the two figures' words pop beside them ("IT WON'T MOVE", "GIVE UP").
- "IT NEVER MOVED." through the stop; after the lift "THE ROCK WAS" / "NEVER THE POINT." then "IT WAS BUILDING YOU."

  python3 overlay.py still IN.jpg T META.json OUT.jpg
  (compose.py imports draw() for the full video)
"""
import json, math, os, sys
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
import sld_text
from sld_text import sstep, font, tracked

TL = json.load(open(os.path.join(HERE, 'timeline.json')))
FPS = TL['fps']; W, H = 1080, 1920
WORD = (246, 178, 52)          # the orange-yellow of the series' word reels
MOCKS = {3: ["IT WON'T MOVE", 'GIVE UP'], 5: ['WASTE OF TIME', 'HAHAHA']}
TX = TL['text']


def blocks(t, m):
    out = []
    if t < TX['hook1']:
        out.append((['HE PUSHED IT', 'EVERY DAY.'], 64, 12, 230, 1 - sstep(TX['hook1'] - 0.15, TX['hook1'], t)))
    if m['shot'] == 'push':
        t0 = TL['cuts'][m['cut']][0] + TL['impactLag']
        punch = 1 + 0.35 * math.exp(-max(0.0, t - t0) * 12) * (t >= t0)
        y = 430 if t < TX['hook1'] else 300
        a = 1 - sstep(TX['never'] - 0.1, TX['never'] + 0.1, t)
        out.append(([f"DAY {m['day']}"], int(96 * punch), 14, y, a))
    if TX['never'] <= t < TX['never1']:
        out.append((['IT NEVER MOVED.'], 62, 12, 300, sstep(TX['never'], TX['never'] + 0.12, t)))
    if t >= TX['end1']:
        out.append((['THE ROCK WAS', 'NEVER THE POINT.'], 62, 11, 220, sstep(TX['end1'], TX['end1'] + 0.2, t)))
    if t >= TX['end2']:
        out.append((['IT WAS BUILDING YOU.'], 50, 10, 410, sstep(TX['end2'], TX['end2'] + 0.25, t)))
    return out


def words(img, t, m):
    """The mockers' words: pop in beside them, a soft dark halo for legibility."""
    if m['shot'] != 'push' or m['cut'] not in MOCKS: return img
    t0 = TL['cuts'][m['cut']][0]
    base = img.convert('RGBA'); halo = Image.new('L', (W, H), 0); hd = ImageDraw.Draw(halo)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    for j, ((x, y, on), text) in enumerate(zip(m['mockers'], MOCKS[m['cut']])):
        if not on: continue
        k = sstep(t0 + 0.12 + 0.15 * j, t0 + 0.22 + 0.15 * j, t)
        if k <= 0: continue
        s = int(58 * (1 + 0.3 * (1 - k)))
        f = font(s, 'Bold'); x = min(max(x + 40, 260), W - 260); y = max(y - 120 - 70 * j, 600)
        tracked(hd, text, f, x, y, 4, int(255 * k)); tracked(d, text, f, x, y, 4, WORD + (int(255 * k),))
    base.alpha_composite(Image.merge('RGBA', (Image.new('L', (W, H), 0),) * 3 + (halo.filter(ImageFilter.GaussianBlur(8)).point(lambda v: int(v * 0.7)),)))
    base.alpha_composite(layer)
    return base.convert('RGB')


def draw(img, t, m):
    return sld_text.draw(words(img, t, m), blocks(t, m))


if __name__ == '__main__':
    if sys.argv[1] == 'still':
        t = float(sys.argv[3]); meta = json.load(open(sys.argv[4]))
        m = meta['frames'][min(round(t * FPS), len(meta['frames']) - 1)]
        draw(Image.open(sys.argv[2]).convert('RGB'), t, m).save(sys.argv[5], quality=94)
