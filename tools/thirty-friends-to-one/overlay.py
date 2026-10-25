"""Text layer for 30 Friends to 1 (Slow Light Dark look, shared kit ../slow-light-dark-common/sld_text.py).

Hook "AT 20, YOU HAVE / 30 FRIENDS." from frame 0; it hands over to the counter "AGE 20 / 30 FRIENDS" (AGE only goes
up, the friend count only goes down; render.cjs meta asserts both); five tiny reason labels over friends as they stand
to leave (MOVED, MARRIED, BUSY, DRIFTED, GONE), placed through the real camera (meta.json); "AT 60, YOU NEED ONE." at the end.

  python3 overlay.py still IN.jpg T META.json OUT.jpg     overlay one rendered frame at time T (seconds)
  (compose.py imports draw() for the full video)
"""
import json, os, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
import sld_text
from sld_text import sstep, font, tracked, CREAM

TL = json.load(open(os.path.join(HERE, 'timeline.json')))
FPS = TL['fps']


def blocks(t, m):
    out = []
    a = sstep(-0.01, 0.1, t) * (1 - sstep(TL['hookOut'] - 0.25, TL['hookOut'], t))
    out.append((['AT 20, YOU HAVE', '30 FRIENDS.'], 46, 9, 262, a))
    a = sstep(TL['counterIn'], TL['counterIn'] + 0.3, t) * (1 - sstep(TL['counterOut'] - 0.3, TL['counterOut'], t))
    if a > 0:
        n = m['count']
        out.append(([f"AGE {m['age']}"], 60, 14, 262, a))
        out.append(([f"{n} FRIEND" + ('S' if n != 1 else '')], 34, 10, 352, a * 0.85))
    a = sstep(TL['line60'], TL['line60'] + 0.45, t)
    out.append((['AT 60, YOU NEED ONE.'], 50, 9, 262, a))
    return out


def labels(img, m):
    """Tiny reason labels over the friends who are leaving (cream, 60%, wide tracking, same font)."""
    if not m['labels']:
        return img
    base = img.convert('RGBA'); layer = Image.new('RGBA', base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    f = font(24, 'Medium')
    for l in m['labels']:
        x = min(max(l['x'], 90), 990); y = min(max(l['y'], 470), 1500)
        tracked(d, l['text'], f, x, y - 11, 6, (8, 9, 12, int(180 * l['a'])))   # faint dark underlay for the beam
        tracked(d, l['text'], f, x, y - 12, 6, CREAM + (int(215 * l['a']),))
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
