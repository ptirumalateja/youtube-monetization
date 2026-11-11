"""Text layer for the umbrella reel.
- Title from frame 0 that stays the whole time (Teja, 11 Nov): SOME PEOPLE PLAY CHECKERS. / OTHERS PLAY CHESS.
- The grey man's HA HA near his head while he laughs (like the reference).
- The last 0.55 s of the picture fades into a 3 s end card over the blurred, darkened last frame:
  ONE FOCUSES ON THE NEXT MOVE. / THE OTHER THINKS THREE MOVES AHEAD. / FOLLOW @SLOWLIGHTTV"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
import sld_text
from sld_text import sstep, font, tracked, CREAM

W, H = 1080, 1920
GOLD = (240, 196, 120)
RED = (226, 74, 52)
HAS = [(0.05, 0.85, -95, -150), (0.3, 1.1, -150, -95), (1.15, 1.9, -110, -165), (1.45, 2.25, -165, -105), (1.9, 2.75, -100, -150)]


def text_block(img, lines, alpha_watermark=True):
    """lines: [(text, size, track, y, rgb, alpha, weight)] with the soft dark halo of sld_text."""
    mask = Image.new('L', (W, H), 0); md = ImageDraw.Draw(mask)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
    for text, size, track, y, rgb, a, wt in lines:
        if a <= 0: continue
        f = font(size, wt)
        tracked(md, text, f, W / 2, y, track, int(255 * a)); tracked(ld, text, f, W / 2, y, track, rgb + (int(255 * a),))
    halo = mask.filter(ImageFilter.GaussianBlur(12)).point(lambda v: min(255, int(v * 0.8)))
    base = img.convert('RGBA')
    base.alpha_composite(Image.merge('RGBA', (Image.new('L', (W, H), 0),) * 3 + (halo,)))
    base.alpha_composite(layer); return base.convert('RGB')


def title(img, a=1.0):
    return text_block(img, [('SOME PEOPLE PLAY CHECKERS.', 50, 6, 150, CREAM, a, 'Bold'),
                            ('OTHERS PLAY CHESS.', 50, 6, 222, GOLD, a, 'Bold')])


def draw(img, t, m, card=0.0):
    img = sld_text.draw(img, [])
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    hx, hy = m['greyHeadC'][0] * W, m['greyHeadC'][1] * H
    for a, b, dx, dy in HAS:
        al = sstep(a, a + 0.08, t) * (1 - sstep(b - 0.15, b, t))
        if al <= 0: continue
        pop = 1 + 0.25 * (1 - sstep(a, a + 0.12, t))
        d.text((hx + dx, hy + dy - 8 * sstep(a, b, t)), 'HA', font=font(int(38 * pop), 'Bold'), fill=(225, 228, 236, int(240 * al)), anchor='mm')
    base = img.convert('RGBA'); base.alpha_composite(layer); img = base.convert('RGB')
    if card > 0: img = Image.blend(img, card_bg(img), card)
    return title(img)


_bg = {}
def card_bg(last):
    k = id(last)
    if k not in _bg:
        _bg.clear(); _bg[k] = ImageEnhance.Brightness(last.filter(ImageFilter.GaussianBlur(28))).enhance(0.28)
    return _bg[k]


def end_card(last, u):
    """u: seconds into the end card."""
    img = card_bg(last).copy()
    img = text_block(img, [
        ('ONE FOCUSES ON', 58, 6, 760, CREAM, sstep(0.05, 0.4, u), 'Bold'),
        ('THE NEXT MOVE.', 58, 6, 840, CREAM, sstep(0.05, 0.4, u), 'Bold'),
        ('THE OTHER THINKS', 58, 6, 980, GOLD, sstep(0.75, 1.1, u), 'Bold'),
        ('THREE MOVES AHEAD.', 58, 6, 1060, GOLD, sstep(0.75, 1.1, u), 'Bold'),
        ('FOLLOW @SLOWLIGHTTV', 34, 8, 1290, CREAM, 0.85 * sstep(1.5, 1.85, u), 'SemiBold')])
    img = sld_text.draw(img, [])
    return title(img)
