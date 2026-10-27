"""Text layer for the dark-warm Salary reference frame. python3 overlay.py IN.jpg OUT.png after|before"""
import os, sys
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
import sld_text
from sld_text import font, tracked, W, H
GOLD = (255, 190, 110)
COPY = {'after': dict(tag='DAY 24  |  BALANCE ₹0', small='SALARY LASTED 6 DAYS.', big=['WORK LASTS', 'ALL 30.']),
        'before': dict(tag='DAY 1  |  +₹50,000', small='MY SALARY', big=['BEFORE', 'PAYDAY.'])}
def run(inp, out, v):
    c = COPY[v]; img = Image.open(inp).convert('RGB').resize((W, H), Image.LANCZOS)
    img = sld_text.draw(img, [([c['small']], 40, 8, 170, 0.95), (c['big'], 92, 14, 240, 1.0)])
    base = img.convert('RGBA'); lay = Image.new('RGBA', base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', 32); tw = sum(d.textlength(ch, font=f) for ch in c['tag']) + 4 * (len(c['tag']) - 1); w = tw + 80; x0 = (W - w) / 2; y0 = 505
    d.rounded_rectangle([x0, y0, x0 + w, y0 + 64], 32, fill=(22, 24, 30, 215)); tracked(d, c['tag'], f, W / 2, y0 + 14, 4, GOLD + (255,))
    base.alpha_composite(lay); base.convert('RGB').save(out, quality=95)
run(*sys.argv[1:4])
