"""Text layer for The Phone at Dinner (Slow Light Dark look, shared kit ../slow-light-dark-common/sld_text.py).

The text tells the story literally (series 3-second test): hook "EVERY DINNER, / HE CHECKED HIS PHONE." from frame 0;
the DINNER counter (only goes up; render.cjs meta asserts it) with one story line under it; then
"ONE NIGHT HE LOOKED UP." and "SHE WASN'T THERE." held to the end.

  python3 overlay.py still IN.jpg T META.json OUT.jpg     overlay one rendered frame at time T (seconds)
  (compose.py imports draw() for the full video)
"""
import json, os, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
import sld_text
from sld_text import sstep

TL = json.load(open(os.path.join(HERE, 'timeline.json')))
FPS = TL['fps']


def blocks(t, m):
    out = []
    a = 1 - sstep(TL['hookOut'] - 0.25, TL['hookOut'], t)      # on from frame 0, no fade-in
    out.append((['EVERY DINNER,', 'HE CHECKED HIS PHONE.'], 58, 8, 250, a))
    a = sstep(TL['counterIn'], TL['counterIn'] + 0.3, t) * (1 - sstep(TL['counterOut'] - 0.3, TL['counterOut'], t))
    if a > 0:
        out.append(([f"DINNER {m['dinner']:,}"], 60, 14, 262, a))
        for t0, t1, line in TL['lines']:
            b = sstep(t0, t0 + 0.3, t) * (1 - sstep(t1 - 0.25, t1, t))
            if b > 0: out.append(([line], 34, 10, 352, a * b * 0.9))
    out.append((['ONE NIGHT HE LOOKED UP.'], 52, 8, 262, sstep(TL['line1'], TL['line1'] + 0.4, t)))
    out.append((["SHE WASN'T THERE."], 52, 8, 345, sstep(TL['line2'], TL['line2'] + 0.5, t)))
    return out


def draw(img, t, m):
    return sld_text.draw(img, blocks(t, m))


if __name__ == '__main__':
    if sys.argv[1] == 'still':
        t = float(sys.argv[3]); meta = json.load(open(sys.argv[4]))
        m = meta['frames'][min(round(t * FPS), len(meta['frames']) - 1)]
        draw(Image.open(sys.argv[2]).convert('RGB'), t, m).save(sys.argv[5], quality=94)
