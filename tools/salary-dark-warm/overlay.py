"""Text layer for the dark-warm Salary Loop (1080x1920). One sentence split across the loop, like the 30 Friends reel:
hook "YOUR SALARY / LASTS 6 DAYS." with the salary-credited chip (frame 0 and the last 1.2 s), DAY n + balance and one bill chip per bill,
"DAY 6. / ₹0 LEFT." on the zero hit, then "YOUR WORK / LASTS ALL 30." held over the slow calendar. Everything comes from timeline.json.
  python3 overlay.py still IN.jpg T OUT.jpg
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
TL = json.load(open(os.path.join(HERE, 'timeline.json')))
W, H = 1080, 1920
CREAM = (255, 244, 224); GOLD = (255, 190, 110); RED = (255, 110, 90); GREEN = (110, 225, 150)
JB = '/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-%s.ttf'; DJ = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
_f = {}
def font(size, text='', weight='SemiBold'):
    k = (size, '₹' in text, weight)
    if k not in _f: _f[k] = ImageFont.truetype(DJ if k[1] else JB % weight, size)
    return _f[k]
def sstep(a, b, x):
    u = min(1.0, max(0.0, (x - a) / (b - a))); return u * u * (3 - 2 * u)
def win(t, a, b, f=0.2):
    return sstep(a, a + f, t) * (1 - sstep(b - f, b, t))
def tw(d, text, f, tr): return sum(d.textlength(c, font=f) for c in text) + tr * (len(text) - 1)
def tracked(d, text, f, cx, y, tr, fill):
    x = cx - tw(d, text, f, tr) / 2
    for c in text: d.text((x, y), c, font=f, fill=fill); x += d.textlength(c, font=f) + tr
def line(layer, shadow, text, size, cx, y, tr, fill, a):
    if a <= 0: return
    f = font(size, text); tracked(ImageDraw.Draw(shadow), text, f, cx, y, tr, (0, 0, 0, int(255 * a)))
    tracked(ImageDraw.Draw(layer), text, f, cx, y, tr, fill + (int(255 * a),))
def chip(layer, text, y, a, col=GOLD, size=36, minw=0):
    if a <= 0: return
    d = ImageDraw.Draw(layer); f = font(size, text, 'Bold'); w = max(minw, tw(d, text, f, 4) + 90); x0 = (W - w) / 2; yy = y + 24 * (1 - a)
    d.rounded_rectangle([x0, yy, x0 + w, yy + 84], 42, fill=(20, 22, 28, int(225 * a))); d.rounded_rectangle([x0, yy, x0 + w, yy + 84], 42, outline=col + (int(200 * a),), width=2)
    tracked(d, text, f, W / 2, yy + 19, 4, col + (int(255 * a),))
def money(n): return '₹' + f'{n:,}'
def balance(t):
    from math import floor
    if t >= TL['next'] or t < TL['bills'][0]['t']: return TL['salary']
    if t >= TL['zero']: return 0
    b = TL['salary']
    for x in TL['bills']: b -= x['amt'] * sstep(x['t'], x['t'] + 0.4, t)
    return int(round(b / 100) * 100)
def day(t):
    if t < TL['bills'][0]['t']: return 1
    d = 0
    for i, x in enumerate(TL['bills']):
        if t >= x['t']: d = i + 1
    return d
def draw(img, t):
    img = img.convert('RGB')
    if img.size != (W, H): img = img.resize((W, H), Image.LANCZOS)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    B = TL['bills']; Z = TL['zero']; W0, W1 = TL['work']; N = TL['next']; D = TL['duration']
    # hook (frame 0, and again after the next-month notification: the loop seam)
    ha = (1 - sstep(TL['hookOut'] - 0.25, TL['hookOut'], t)) + sstep(N - 0.1, N + 0.3, t)
    ha = min(1.0, ha)
    line(layer, sh, 'YOUR SALARY', 92, W / 2, 190, 12, CREAM, ha); line(layer, sh, 'LASTS 6 DAYS.', 92, W / 2, 310, 12, GOLD, ha)
    chip(layer, 'SALARY CREDITED  +' + money(TL['salary']), 1380, ha, GREEN, 36)
    # the spine: DAY n + balance, then a chip per bill
    sa = sstep(TL['hookOut'] - 0.05, TL['hookOut'] + 0.2, t) * (1 - sstep(Z - 0.35, Z - 0.3, t))
    if sa > 0:
        line(layer, sh, f'DAY {max(1, day(t))}', 110, W / 2, 170, 14, CREAM, sa); line(layer, sh, money(balance(t)), 64, W / 2, 322, 8, GOLD, sa)
    for x in B:
        a = win(t, x['t'], x['t'] + 1.1, 0.2)
        chip(layer, f"{x['label']}  −{money(x['amt'])}", 1380, a, RED, 34)
    # zero hit
    za = win(t, Z, W0 + 0.2, 0.2)
    if za > 0:
        line(layer, sh, 'DAY 6.', 120, W / 2, 170, 14, CREAM, za); line(layer, sh, '₹0 LEFT.', 120, W / 2, 300, 14, RED, za)
    # payoff, held over the work
    pa = win(t, W0 + 0.15, TL['flipPage'][1] + 0.3, 0.35)
    line(layer, sh, 'YOUR WORK', 100, W / 2, 190, 12, CREAM, pa); line(layer, sh, 'LASTS ALL 30.', 100, W / 2, 318, 12, GOLD, pa)
    wu = min(1, max(0, (t - W0) / (W1 - W0))); dd = min(30, 7 + int(23.99 * (wu * wu * (3 - 2 * wu)))) if t < TL['flipPage'][0] else 30
    chip(layer, f'DAY {dd}  |  BALANCE ₹0', 1380, pa, RED, 34)
    # watermark (kit style)
    wf = font(24, '', 'Medium'); tracked(ImageDraw.Draw(sh), 'SLOW LIGHT', wf, W / 2, 1548, 10, (0, 0, 0, 90)); tracked(ImageDraw.Draw(layer), 'SLOW LIGHT', wf, W / 2, 1548, 10, CREAM + (90,))
    halo = sh.getchannel('A').filter(ImageFilter.GaussianBlur(10)).point(lambda v: min(255, int(v * 0.8)))
    base = img.convert('RGBA'); base.alpha_composite(Image.merge('RGBA', (Image.new('L', (W, H), 0),) * 3 + (halo,))); base.alpha_composite(layer)
    return base.convert('RGB')
if __name__ == '__main__' and sys.argv[1] == 'still':
    draw(Image.open(sys.argv[2]), float(sys.argv[3])).save(sys.argv[4], quality=94)
