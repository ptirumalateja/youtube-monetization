"""Text layer for Tug of War (Slow Light Dark series look; blocks drawn by ../slow-light-dark-common style sld_text.py).

  python3 overlay.py still IN.jpg T OUT.jpg     overlay one rendered frame at time T (seconds)
  (compose.py imports blocks()/draw for the full video)
"""
import json, os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sld_text import draw as draw_blocks, sstep

HERE = os.path.dirname(os.path.abspath(__file__))
TL = json.load(open(os.path.join(HERE, 'timeline.json')))


def blocks(t):
    """Text blocks visible at t: (lines, size, track, y, alpha)."""
    out = []
    # hook: on from frame 0, gone as the camera leaves him
    a = sstep(-0.01, 0.12, t) * (1 - sstep(TL['hookOut'] - 0.3, TL['hookOut'], t))
    if a > 0:
        out.append((['WHY IS IT SO HARD', 'TO MOVE FORWARD?'], 46, 9, 262, a))
    # the reveal question
    a = sstep(TL['revealText'], TL['revealText'] + 0.35, t) * (1 - sstep(TL['revealTextOut'] - 0.3, TL['revealTextOut'], t))
    if a > 0:
        out.append((["WHO'S ON THE", 'OTHER END?'], 46, 9, 262, a))
    # the line after he lets go
    a = sstep(TL['endText'], TL['endText'] + 0.4, t)
    if a > 0:
        out.append((['LET GO OF', 'ONE END.'], 50, 9, 262, a))
    return out


def draw(img, t):
    return draw_blocks(img, blocks(t))


if __name__ == '__main__':
    if sys.argv[1] == 'still':
        draw(Image.open(sys.argv[2]).convert('RGB'), float(sys.argv[3])).save(sys.argv[4], quality=94)
