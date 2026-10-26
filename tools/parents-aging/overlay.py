"""Text layer for Your Parents Are Aging (Slow Light Dark look, shared kit ../slow-light-dark-common/sld_text.py).

Hook "YOUR PARENTS / CALLED YOU / 10 TIMES A DAY." from frame 0; it hands over to the counter "AGE 8 / PARENTS 38"
(both only go up; render.cjs meta asserts it); tiny call labels over his far lamp (DAILY, LATER, BUSY, ONCE A WEEK);
the payoff "NOW YOU CALL / ONCE A WEEK." over the parents waiting; "CALL NOW." at the ring, held through the silence.

  python3 overlay.py still IN.jpg T META.json OUT.jpg [TIMELINE]     overlay one rendered frame at time T (seconds)
  (compose.py imports draw() for the full video)
"""
import json, os, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
import sld_text
from sld_text import sstep, font, tracked, CREAM

TL = json.load(open(os.path.join(HERE, os.environ.get('TL', 'timeline.json'))))
FPS = TL['fps']; LN = TL['lines']


def blocks(t, m):
    out = []
    a = 1 - sstep(TL['hookOut'] - 0.25, TL['hookOut'], t)
    out.append((LN['hook'], 66, 10, 230, a))
    a = sstep(TL['counterIn'], TL['counterIn'] + 0.3, t) * (1 - sstep(TL['counterOut'] - 0.3, TL['counterOut'], t))
    if a > 0:
        out.append(([f"AGE {m['age']}"], 60, 14, 262, a))
        out.append(([f"PARENTS {m['page']}"], 34, 10, 352, a * 0.85))
    a = sstep(TL['line'], TL['line'] + 0.45, t) * (1 - sstep(TL['lineOut'] - 0.35, TL['lineOut'], t))
    out.append((LN['payoff'], 56, 10, 262, a))
    if LN.get('sub'):
        a = sstep(TL['subIn'], TL['subIn'] + 0.45, t) * (1 - sstep(TL['lineOut'] - 0.35, TL['lineOut'], t))
        out.append((LN['sub'], 32, 8, 262 + 2 * int(56 * 1.45) + 30, a * 0.85))
    a = sstep(TL['callNow'], TL['callNow'] + 0.18, t)
    out.append((LN['end'], 92, 16, 262, a))
    return out


def labels(img, m):
    """Tiny call labels over his lamp (cream, wide tracking, same font as the counter)."""
    if not m['labels']:
        return img
    base = img.convert('RGBA'); layer = Image.new('RGBA', base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    f = font(26, 'Medium')
    for l in m['labels']:
        x = min(max(l['x'], 160), 920); y = min(max(l['y'], 470), 1500)
        tracked(d, l['text'], f, x, y - 11, 6, (8, 9, 12, int(180 * l['a'])))
        tracked(d, l['text'], f, x, y - 12, 6, CREAM + (int(225 * l['a']),))
    base.alpha_composite(layer)
    return base.convert('RGB')


def draw(img, t, m):
    img = sld_text.draw(img, blocks(t, m))
    return labels(img, m)


if __name__ == '__main__':
    if sys.argv[1] == 'still':
        t = float(sys.argv[3]); meta = json.load(open(sys.argv[4]))
        m = meta['frames'][min(round(t * FPS), len(meta['frames']) - 1)]
        draw(Image.open(sys.argv[2]).convert('RGB'), t, m).save(sys.argv[5], quality=94)
