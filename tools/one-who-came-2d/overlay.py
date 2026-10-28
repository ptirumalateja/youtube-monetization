"""Text layer for the 2D One Came stills (1080x1920): JetBrains Mono, tracked, cream + gold, inside the middle 70%.
The message cards are drawn in the scene itself, so there are no UI chips here.
  python3 overlay.py IN_DIR OUT_DIR
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H = 1080, 1920
CREAM = (255, 244, 224); GOLD = (255, 190, 110)
JB = '/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-%s.ttf'
def font(size, w='SemiBold'): return ImageFont.truetype(JB % w, size)
def tw(d, text, f, tr): return sum(d.textlength(c, font=f) for c in text) + tr * (len(text) - 1)
def tracked(d, text, f, cx, y, tr, fill):
    x = cx - tw(d, text, f, tr) / 2
    for c in text: d.text((x, y), c, font=f, fill=fill); x += d.textlength(c, font=f) + tr
LINES = {
    'hook':     [('WHO WOULD COME', 80, CREAM, 230), ('FOR YOU AT 2 AM?', 70, GOLD, 340)],
    'count':    [('30 PEOPLE SAID', 70, CREAM, 230), ('"I\'M HERE FOR YOU."', 56, GOLD, 330)],
    'knock':    [('THEN,', 78, CREAM, 230), ('A KNOCK.', 96, GOLD, 340)],
    'facedown': [],
    'payoff':   [('ONE PERSON', 92, CREAM, 230), ('CAME.', 110, GOLD, 360), ('TAG YOUR ONE.', 40, CREAM, 1700)],
}
def draw(shot, src, dst):
    img = Image.open(src).convert('RGBA').resize((W, H), Image.LANCZOS)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    scrim = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(scrim)
    for y in range(0, 640): sd.line([(0, y), (W, y)], fill=(14, 17, 26, int(170 * (1 - y / 640) ** 1.2)))
    img.alpha_composite(scrim)
    for text, size, col, y in LINES[shot]:
        f = font(size); tracked(ImageDraw.Draw(sh), text, f, W / 2, y + 4, 10, (0, 0, 0, 210)); tracked(ImageDraw.Draw(lay), text, f, W / 2, y, 10, col + (255,))
    tracked(ImageDraw.Draw(lay), 'SLOW LIGHT', font(22, 'Medium'), W / 2, 1830, 8, (200, 200, 205, 90))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12))); img.alpha_composite(lay); img.convert('RGB').save(dst, quality=92)
if __name__ == '__main__':
    i, o = sys.argv[1], sys.argv[2]; os.makedirs(o, exist_ok=True)
    for s in LINES:
        if os.path.exists(os.path.join(i, s + '.jpg')): draw(s, os.path.join(i, s + '.jpg'), os.path.join(o, s + '.jpg'))
