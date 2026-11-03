"""Text layer for Their Words Became His Wall (V2 of They Threw Words) (Slow Light Dark look; helpers in ../slow-light-dark-common/sld_text.py).

Three lines only, top centre, tracked cream caps: hook on frame 0, one rehook, and the payoff held to the end.
"SLOW LIGHT" watermark bottom centre at 35%.

  python3 overlay.py still IN.jpg T OUT.jpg     overlay one rendered frame at time T (compose.py imports draw())
"""
import json, os, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
import sld_text
from sld_text import sstep

TL = json.load(open(os.path.join(HERE, 'timeline.json')))


def blocks(t):
    out = []
    a = 1 - sstep(TL['hookOut'], TL['hookOut'] + 0.3, t)                      # on from frame 0, no fade-in
    if a > 0: out.append((['THEY THREW WORDS', 'AT HIM.'], 50, 9, 230, a))
    a = sstep(TL['rehook0'], TL['rehook0'] + 0.25, t) * (1 - sstep(TL['rehook1'], TL['rehook1'] + 0.3, t))
    if a > 0: out.append((['HE KEPT', 'EVERY ONE.'], 46, 9, 230, a))
    a = sstep(TL['endText'], TL['endText'] + 0.45, t)
    if a > 0: out.append((['THEIR WORDS', 'BECAME HIS WALL.'], 54, 10, 230, a))
    return out


def draw(img, t):
    return sld_text.draw(img, blocks(t))


if __name__ == '__main__' and sys.argv[1] == 'still':
    draw(Image.open(sys.argv[2]).convert('RGB'), float(sys.argv[3])).save(sys.argv[4], quality=94)
