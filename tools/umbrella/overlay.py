"""Text layer for the umbrella reel: the grey man's HA HA (like the reference) near his head while he laughs, plus
the Slow Light watermark. No captions (the reference has none; the line lives in the post copy)."""
import json, os, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
import sld_text
from sld_text import sstep, font

W, H = 1080, 1920
# (start, end, dx, dy) in px relative to the grey man's head centre
HAS = [(0.05, 0.85, -95, -150), (0.3, 1.1, -150, -95), (1.15, 1.9, -110, -165), (1.45, 2.25, -165, -105), (1.9, 2.75, -100, -150)]


def draw(img, t, m):
    img = sld_text.draw(img, [])
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    hx, hy = m['greyHeadC'][0] * W, m['greyHeadC'][1] * H
    for a, b, dx, dy in HAS:
        al = sstep(a, a + 0.08, t) * (1 - sstep(b - 0.15, b, t))
        if al <= 0: continue
        pop = 1 + 0.25 * (1 - sstep(a, a + 0.12, t))
        f = font(int(38 * pop), 'Bold')
        d.text((hx + dx, hy + dy - 8 * sstep(a, b, t)), 'HA', font=f, fill=(225, 228, 236, int(240 * al)), anchor='mm')
    base = img.convert('RGBA'); base.alpha_composite(layer); return base.convert('RGB')
