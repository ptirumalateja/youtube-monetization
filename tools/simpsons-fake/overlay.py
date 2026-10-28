"""Text layer for the Simpsons 'one is fake' look stills (1080x1920). One huge line per beat, inside the middle 70%.
  python3 overlay.py IN_DIR OUT_DIR
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H = 1080, 1920
CREAM = (255, 244, 224); GOLD = (255, 190, 110)
XB = '/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf'; MD = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
TEXT = {  # shot: [(text, size, colour, font)], y of first line
    'room':      (300, [('ONE OF THESE', 86, CREAM, XB), ('SIMPSONS PREDICTIONS', 70, CREAM, XB), ('IS FAKE.', 110, GOLD, XB)]),
    'tiger':     (300, [('1993 → 2003', 96, GOLD, XB), ('THE TIGER', 70, CREAM, XB)]),
    'gate':      (300, [('1998 → 2019', 96, GOLD, XB), ('DISNEY BUYS FOX', 70, CREAM, XB)]),
    'president': (300, [('2000 → 2017', 96, GOLD, XB), ('PRESIDENT TRUMP', 70, CREAM, XB)]),
    'chalk':     (300, [('1998 → 2012', 96, GOLD, XB), ('THE HIGGS BOSON', 70, CREAM, XB)]),
    'shelf':     (300, [('WHICH ONE', 100, CREAM, XB), ('IS FAKE?', 120, GOLD, XB), ('ANSWER PINNED · @slowlighttv', 40, CREAM, MD)]),
}
def fit(text, size, path, maxw):
    while True:
        f = ImageFont.truetype(path, size)
        if f.getlength(text) + 4 * len(text) <= maxw or size < 20: return f
        size -= 2
def draw(shot, src, dst):
    img = Image.open(src).convert('RGB').resize((W, H), Image.LANCZOS)
    y, lines = TEXT[shot]
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ds, dl = ImageDraw.Draw(sh), ImageDraw.Draw(lay)
    for text, size, col, path in lines:
        f = fit(text, size, path, W * 0.78); tw = f.getlength(text) + 4 * (len(text) - 1); x = (W - tw) / 2
        for c in text:
            ds.text((x, y + 4), c, font=f, fill=(0, 0, 0, 200)); dl.text((x, y), c, font=f, fill=col + (255,)); x += f.getlength(c) + 4
        y += int(f.size * 1.18)
    img = img.convert('RGBA'); img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10))); img.alpha_composite(lay)
    img.convert('RGB').save(dst, quality=92)
if __name__ == '__main__':
    i, o = sys.argv[1], sys.argv[2]; os.makedirs(o, exist_ok=True)
    for s in TEXT:
        if os.path.exists(os.path.join(i, s + '.jpg')): draw(s, os.path.join(i, s + '.jpg'), os.path.join(o, s + '.jpg'))
