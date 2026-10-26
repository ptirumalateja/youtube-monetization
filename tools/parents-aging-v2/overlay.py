"""Text layer for Parents V2 (Slow Light Dark text kit ../slow-light-dark-common/sld_text.py).

Three age lines (AT 8 / AT 18 / AT 25), the gold sub "THEY STILL WAIT EVERY DAY.", "THEY WAITED 20 YEARS FOR YOU TO GROW UP.",
then a big "CALL NOW." held to the end. A small wall-calendar tag top right (YEAR | PARENTS N) and two small phone
notifications at the bottom (MOM CALLING... DAILY in green, MISSED CALL - MOM in red). Everything comes from timeline.json.

  python3 overlay.py still IN.jpg T OUT.jpg       overlay one rendered frame at time T (seconds)
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
import sld_text
from sld_text import sstep, font, tracked, CREAM, W, H

TL = json.load(open(os.path.join(HERE, 'timeline.json')))
FPS = TL['fps']
GOLD = (232, 184, 90)
PILL = {'green': (52, 199, 89), 'red': (255, 69, 58)}


def fade(t, a, b, f=0.3):
    return sstep(a, a + f, t) * (1 - sstep(b - f, b, t)) if a > 0 else 1 - sstep(b - f, b, t)


def draw(img, t, m=None):
    blocks, gold = [], []
    for it in TL['text']:
        a = fade(t, it['in'], it['out'], 0.25)
        if a <= 0: continue
        (gold if it.get('gold') else blocks).append((it['lines'], it['size'], 16 if it['size'] > 90 else 10, it.get('y', 262), a))
    img = sld_text.draw(img, blocks)
    base = img.convert('RGBA'); layer = Image.new('RGBA', base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    for lines, size, tr, y, a in gold:
        for i, ln in enumerate(lines):
            tracked(d, ln, font(size), W / 2, y + 1 + i * int(size * 1.45), tr, (8, 9, 12, int(200 * a)))
            tracked(d, ln, font(size), W / 2, y + i * int(size * 1.45), tr, GOLD + (int(255 * a),))
    # wall-calendar tag, top right (scenes 1-3)
    if t < TL['scenes'][3]:
        cal = [c for c in TL['calendar'] if c[0] <= t][-1]
        a = (1 - sstep(TL['scenes'][3] - 0.2, TL['scenes'][3], t)) * sstep(TL['hookOut'], TL['hookOut'] + 0.25, t)  # hidden under the hook
        k = sstep(cal[0], cal[0] + 0.25, t) if cal[0] > 0 else 1
        f = font(26, 'Medium'); txt = f"{cal[1]}  |  PARENTS {cal[2]}"
        x1 = W - 70; tw = sum(d.textlength(c, font=f) for c in txt) + 3 * (len(txt) - 1)
        d.rounded_rectangle([x1 - tw - 28, 168, x1, 214], 8, fill=(244, 239, 230, int(200 * a * k)))
        d.rectangle([x1 - tw - 28, 168, x1, 176], fill=(196, 69, 47, int(220 * a * k)))
        tracked(d, txt, f, x1 - 14 - tw / 2, 180, 3, (40, 34, 30, int(255 * a * k)))
    # phone notification pill, bottom (above the watermark)
    for p in TL['phoneUI']:
        a = fade(t, p['in'], p['out'], 0.2)
        if a <= 0: continue
        f = font(30, 'SemiBold'); tw = sum(d.textlength(c, font=f) for c in p['text']) + 4 * (len(p['text']) - 1)
        w = tw + 110; x0 = (W - w) / 2; y0 = 1400 + 30 * (1 - sstep(p['in'], p['in'] + 0.2, t))
        d.rounded_rectangle([x0, y0, x0 + w, y0 + 70], 35, fill=(18, 20, 24, int(225 * a)))
        d.ellipse([x0 + 22, y0 + 20, x0 + 52, y0 + 50], fill=PILL[p['col']] + (int(255 * a),))
        tracked(d, p['text'], f, x0 + 70 + tw / 2, y0 + 17, 4, PILL[p['col']] + (int(255 * a),))
    base.alpha_composite(layer)
    return base.convert('RGB')


if __name__ == '__main__':
    if sys.argv[1] == 'still':
        draw(Image.open(sys.argv[2]).convert('RGB'), float(sys.argv[3])).save(sys.argv[4], quality=94)
