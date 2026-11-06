"""Text layer for Ten Numbers (Slow Light logo palette: cream text, amber for the one number that matters).

Hook "YOU KNEW 10 PHONE / NUMBERS BY HEART." on from frame 0; then the counter "AGE 10" (cream) over "10 NUMBERS" (amber).
Uses the series kit ../slow-light-dark-common/sld_text.py for font, tracking, halo and the SLOW LIGHT watermark.
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
import sld_text
from sld_text import sstep, font, tracked, W, H

TL = json.load(open(os.path.join(HERE, 'timeline.json')))
AMBER = (255, 178, 77)


def amber_line(img, text, size, track, y, a):
    if a <= 0:
        return img
    f = font(size, 'Bold')
    mask = Image.new('L', (W, H), 0); tracked(ImageDraw.Draw(mask), text, f, W / 2, y, track, int(255 * a))
    glow = mask.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.6))
    base = img.convert('RGBA')
    base.alpha_composite(Image.merge('RGBA', (Image.new('L', (W, H), AMBER[0]), Image.new('L', (W, H), 120), Image.new('L', (W, H), 30), glow)))
    halo = mask.filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * 0.5))
    base.alpha_composite(Image.merge('RGBA', (Image.new('L', (W, H), 0),) * 3 + (halo,)))
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); tracked(ImageDraw.Draw(layer), text, f, W / 2, y, track, AMBER + (int(255 * a),))
    base.alpha_composite(layer)
    return base.convert('RGB')


def draw(img, t, m):
    blocks = []
    a = 1 - sstep(TL['hookOut'] - 0.25, TL['hookOut'], t)
    blocks.append((['YOU KNEW 10 PHONE', 'NUMBERS BY HEART.'], 64, 9, 230, a))
    c = sstep(TL['counterIn'], TL['counterIn'] + 0.3, t)
    blocks.append(([f"AGE {m['age']}"], 56, 14, 236, c))
    img = sld_text.draw(img, blocks)
    n = m['count']
    return amber_line(img, f"{n} NUMBER" + ('S' if n != 1 else ''), 44, 12, 326, c)
