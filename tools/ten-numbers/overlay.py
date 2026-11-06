"""Text layer for Ten Numbers (Slow Light logo palette: cream text, amber for the one number that matters).

0 - hookOut        "AT 10, YOU KNEW / 10 PHONE NUMBERS." (cream, frame 0), "HOW MANY DID YOU LOSE?" (amber) pops at hookQ
counterIn - counterOut   AGE n (cream) over "n NUMBERS" (amber)
payoffIn - end     "NOW YOU KNOW" (cream) over "ONE." (amber, bigger)
Series kit ../slow-light-dark-common/sld_text.py supplies font, tracking, halo and the SLOW LIGHT watermark.
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


def draw(img, t, m, end_k=1.0, hook_k=None):
    """end_k scales the payoff (fades it out in the loop dissolve); hook_k (0..1) forces the hook on at that alpha (fades it in)."""
    blocks = []
    a = 1 - sstep(TL['hookOut'] - 0.25, TL['hookOut'], t)
    if hook_k is not None: a = hook_k
    blocks.append((['AT 10, YOU KNEW', '10 PHONE NUMBERS.'], 60, 9, 170, a))
    c = sstep(TL['counterIn'], TL['counterIn'] + 0.3, t) * (1 - sstep(TL['counterOut'] - 0.25, TL['counterOut'], t))
    blocks.append(([f"AGE {m['age']}"], 56, 14, 236, c))
    p = sstep(TL['payoffIn'], TL['payoffIn'] + 0.35, t) * end_k
    blocks.append((['NOW YOU KNOW'], 64, 9, 236, p))
    img = sld_text.draw(img, blocks)
    n = m['count']
    hit = 0.0
    if len(TL['depart']) >= 5:                      # rehook: the count crosses 5 (half gone) - the amber line punches
        t5 = TL['depart'][4][1] + TL['fly']; x = (t - t5) / 0.5; hit = (1 - x) ** 2 if 0 <= x < 1 else 0.0
    img = amber_line(img, f"{n} NUMBER" + ('S' if n != 1 else ''), int(44 + 26 * hit), 12, 326 - int(8 * hit), c)
    img = amber_line(img, 'HOW MANY DID YOU LOSE?', 52, 8, 170 + 2 * int(60 * 1.45), (a * sstep(TL['hookQ'], TL['hookQ'] + 0.3, t) if hook_k is None else 0))
    return amber_line(img, 'ONE.', 110, 14, 330, p)
