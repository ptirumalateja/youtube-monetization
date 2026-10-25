"""Slow Light Dark: shared text layer (PIL). Lifted from the pilot's overlay (tools/chain-never-locked/overlay.py).

Top centre, wide-tracked caps in cream (JetBrains Mono SemiBold, OFL), soft dark halo for legibility over the beam.
Counters use the same font. "SLOW LIGHT" watermark bottom centre at 35% opacity.

Sizes at 1080x1920 (pilot): hook 46 px / track 9 / two lines at y 262 and 329; counter 60 px / track 14 at y 262;
end line 50 px / track 9 at y 262; watermark 24 px Medium / track 10 at y 1548. Keep text below y 150 and above y 1574
(the platform UI covers the rest).

  from sld_text import draw, sstep
  blocks = [(['HE STOPPED PULLING', 'IN YEAR ONE.'], 46, 9, 262, alpha)]   # (lines, size px, tracking px, top y, alpha 0..1)
  frame = draw(frame, blocks)
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT_DIR = '/usr/share/fonts/truetype/jetbrains-mono'
CREAM = (237, 230, 214)
W, H = 1080, 1920
_fonts = {}


def font(size, weight='SemiBold'):
    k = (size, weight)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(os.path.join(FONT_DIR, f'JetBrainsMono-{weight}.ttf'), size)
    return _fonts[k]


def sstep(a, b, x):
    u = min(1.0, max(0.0, (x - a) / (b - a)))
    return u * u * (3 - 2 * u)


def tracked(d, text, f, cx, y, track, fill):
    """Draw text centred on cx with extra letter spacing (track, px)."""
    widths = [d.textlength(c, font=f) for c in text]
    x = cx - (sum(widths) + track * (len(text) - 1)) / 2
    for c, w in zip(text, widths):
        d.text((x, y), c, font=f, fill=fill)
        x += w + track


def draw(img, blocks, watermark=True):
    """img: RGB frame (resized to 1080x1920 if needed). blocks: [(lines, size, track, y, alpha)]."""
    if img.size != (W, H):
        img = img.resize((W, H), Image.LANCZOS)
    mask = Image.new('L', (W, H), 0); md = ImageDraw.Draw(mask)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
    for lines, size, track, y0, a in blocks:
        if a <= 0: continue
        f = font(size)
        for i, line in enumerate(lines):
            y = y0 + i * int(size * 1.45)
            tracked(md, line, f, W / 2, y, track, int(255 * a))
            tracked(ld, line, f, W / 2, y, track, CREAM + (int(255 * a),))
    if watermark:
        wf = font(24, 'Medium')
        tracked(md, 'SLOW LIGHT', wf, W / 2, 1548, 10, 90)
        tracked(ld, 'SLOW LIGHT', wf, W / 2, 1548, 10, CREAM + (int(255 * 0.35),))
    halo = mask.filter(ImageFilter.GaussianBlur(9)).point(lambda v: min(255, int(v * 1.1 * 0.55)))
    base = img.convert('RGBA')
    base.alpha_composite(Image.merge('RGBA', (Image.new('L', (W, H), 0),) * 3 + (halo,)))
    base.alpha_composite(layer)
    return base.convert('RGB')
