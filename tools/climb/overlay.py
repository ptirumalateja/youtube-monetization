"""Text layer for Build It As You Climb.

Like the reference: two lane labels over the lanes (PERFECTIONIST / ACTION TAKER) that ride with the camera, each with
a small rung counter under it (ours), fading as the camera climbs; then "BUILD IT AS YOU CLIMB." top centre from
`caption` to the end, and PERFECTIONIST under him from `endLabel`. Lane positions come from meta.json (render.cjs meta).

  python3 overlay.py still IN.jpg T META OUT.jpg
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
import sld_text
from sld_text import sstep, font, tracked, CREAM

TL = json.load(open(os.path.join(HERE, 'timeline.json')))
W, H = 1080, 1920
GOLD = (255, 196, 110)


def draw(img, t, m):
    img = sld_text.draw(img, [])
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    a0, a1 = TL['labelsOut']
    la = 1 - sstep(a0, a1, t)
    if la > 0:
        for key, name, n, col in (('perf', 'PERFECTIONIST', m['prung'], CREAM), ('act', 'ACTION TAKER', m['rungs'], CREAM)):
            x = min(max(m['lane'][key][0] * W, 210), W - 210)
            tracked(d, name, font(38), x, 232, 5, col + (int(255 * la),))
            tracked(d, f'RUNGS {n:02d}', font(28, 'Medium'), x, 288, 6, GOLD + (int(220 * la),))
    ca = sstep(TL['caption'], TL['caption'] + 0.5, t)
    if ca > 0:
        tracked(d, 'BUILD IT AS YOU CLIMB.', font(50), W / 2, 250, 7, CREAM + (int(255 * ca),))
    ea = sstep(TL['endLabel'], TL['endLabel'] + 0.5, t)
    if ea > 0:
        x = m['lane']['perfFeet'][0] * W; y = min(m['lane']['perfFeet'][1] * H + 30, 1470)
        tracked(d, 'PERFECTIONIST', font(34), x, y, 5, CREAM + (int(255 * ea),))
        tracked(d, f'RUNGS {m["prung"]:02d}', font(26, 'Medium'), x, y + 50, 6, GOLD + (int(220 * ea),))
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sh.putalpha(layer.getchannel('A').filter(ImageFilter.GaussianBlur(7)).point(lambda v: int(v * 0.6)))
    base = img.convert('RGBA'); base.alpha_composite(sh); base.alpha_composite(layer)
    return base.convert('RGB')


if __name__ == '__main__' and sys.argv[1] == 'still':
    meta = json.load(open(sys.argv[4]))['frames']; t = float(sys.argv[3])
    draw(Image.open(sys.argv[2]).convert('RGB'), t, meta[min(len(meta) - 1, round(t * TL['fps']))]).save(sys.argv[5], quality=94)
