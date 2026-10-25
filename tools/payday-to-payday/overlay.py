"""Text + HUD layer for Payday to Payday (Slow Light Dark series look; JetBrains Mono via ../slow-light-dark-common/sld_text.py).

Plain statements, big numbers: PAYDAY: ₹50,000 IN. / balance counter / flash line per deduction / DAY n / 30-day calendar.
All times come from timeline.json. balance() is asserted monotonic within each direction (up while salary lands, down after).

  python3 overlay.py still IN.jpg T OUT.jpg      overlay one rendered frame at time T
  python3 overlay.py check                        assert the counters over every frame
"""
import json, os, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
import sld_text
from sld_text import sstep, font, tracked, CREAM, W, H

# JetBrains Mono (as installed here) has no U+20B9: draw the rupee sign from DejaVu Sans Mono Bold, everything else unchanged.
from PIL import ImageFont
_RS = {}
def _tracked(d, text, f, cx, y, track, fill):
    def fo(c):
        if c != '\u20B9': return f
        if f.size not in _RS: _RS[f.size] = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', f.size)
        return _RS[f.size]
    widths = [d.textlength(c, font=fo(c)) for c in text]
    x = cx - (sum(widths) + track * (len(text) - 1)) / 2
    for c, w in zip(text, widths):
        d.text((x, y), c, font=fo(c), fill=fill); x += w + track
sld_text.tracked = _tracked
tracked = _tracked

TL = json.load(open(os.path.join(HERE, 'timeline.json')))
FPS = TL['fps']; DUR = TL['duration']
RS = '₹'; MINUS = '−'


def money(v): return f'{RS}{int(round(v)):,}'


def balance(t):
    """Rupees in the wallet. Rises as the five bundles land (sum 50,000), falls as each is taken."""
    v = 0.0
    for it in TL['items']:
        v += it['amt'] * sstep(TL['land'][it['key']], TL['land'][it['key']] + 0.25, t)
        v -= it['amt'] * sstep(it['grab'], it['grab'] + TL['countDur'], t)
    return v


def day_at(t):
    d = 0
    for s in TL['dayStart']:
        if t >= s: d += 1
    return d


def blocks(t):
    out = []
    a = (1 - sstep(TL['hookOut'], TL['hookOut'] + 0.2, t))
    if a > 0: out.append(([f'PAYDAY: {money(TL["salary"])} IN.'], 46, 9, 262, a))
    d = day_at(t)
    if d and t < TL['zeroText']:
        out.append(([f'DAY {d}'], 60, 14, 262, sstep(TL['hookOut'] + 0.1, TL['hookOut'] + 0.3, t)))
    z = sstep(TL['zeroText'], TL['zeroText'] + 0.3, t) * (1 - sstep(TL['daysText'] - 0.25, TL['daysText'], t))
    if z > 0: out.append(([f'DAY 3: {money(0)} LEFT.'], 50, 9, 262, z))
    e = sstep(TL['daysText'], TL['daysText'] + 0.35, t) * (1 - sstep(TL['endFade'], DUR - 0.02, t))
    if e > 0: out.append(([f'{30 - 3} DAYS TO PAYDAY.'], 50, 9, 262, e))
    # balance counter, big, under the headline
    out.append((['BALANCE'], 26, 10, 346, 0.75))
    out.append(([money(balance(t))], 96, 8, 376, 1.0))
    # flash line for each deduction
    for it in TL['items']:
        u = t - it['grab']
        if -0.05 <= u <= 1.35:
            a = sstep(-0.05, 0.12, u) * (1 - sstep(1.0, 1.35, u))
            out.append(([f'{it["key"]}  {MINUS}{money(it["amt"])}'], 52, 6, 690, a))
    return out


def calendar(img, t):
    """30 day squares (10 x 3). Day n is crossed out when it starts; the 27 left pulse once the month is clearly lost."""
    if t < TL['dayStart'][0] - 0.1: return img
    a_all = sstep(TL['dayStart'][0] - 0.1, TL['dayStart'][0] + 0.25, t) * (1 - sstep(TL['endFade'], DUR - 0.02, t))
    cw, gap, cols = 50, 10, 10
    x0 = (W - (cols * cw + (cols - 1) * gap)) / 2; y0 = 506
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    pulse = sstep(TL['daysText'], TL['daysText'] + 0.5, t) * (1 - sstep(TL['endFade'], DUR - 0.02, t)) * (0.5 + 0.5 * __import__('math').sin(t * 2.2))
    for i in range(30):
        c, r = i % cols, i // cols; x = x0 + c * (cw + gap); y = y0 + r * (cw + gap)
        crossed = i < 3 and t >= TL['dayStart'][i]
        if crossed:
            u = sstep(TL['dayStart'][i], TL['dayStart'][i] + 0.3, t)
            d.rectangle([x, y, x + cw, y + cw], fill=(237, 230, 214, int(40 * a_all)), outline=(237, 230, 214, int(150 * a_all)), width=2)
            L = int(cw * 0.8 * u); m = cw / 2
            d.line([(m + x - L / 2, y + m - L / 2), (m + x + L / 2, y + m + L / 2)], fill=(237, 230, 214, int(235 * a_all)), width=4)
            d.line([(m + x - L / 2, y + m + L / 2), (m + x + L / 2, y + m - L / 2)], fill=(237, 230, 214, int(235 * a_all)), width=4)
        else:
            d.rectangle([x, y, x + cw, y + cw], outline=(237, 230, 214, int((120 + 90 * pulse) * a_all)), width=2)
        f = font(20, 'Medium'); s = str(i + 1)
        d.text((x + 6, y + 4), s, font=f, fill=(237, 230, 214, int((110 if not crossed else 70) * a_all)))
    base = img.convert('RGBA'); base.alpha_composite(layer)
    lab = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lab)
    tracked(ld, 'ONE MONTH', font(24, 'Medium'), W / 2, y0 + 3 * (cw + gap) + 4, 10, (237, 230, 214, int(150 * a_all)))
    base.alpha_composite(lab)
    return base.convert('RGB')


def draw(img, t):
    if img.size != (W, H): img = img.resize((W, H), Image.LANCZOS)
    return sld_text.draw(calendar(img, t), blocks(t))


def check():
    prev, ph = 0, 'up'
    for f in range(round(DUR * FPS)):
        t = f / FPS; b = round(balance(t))
        if ph == 'up' and b < prev:
            ph = 'down'; assert t >= TL['land']['RENT'] + 0.25 - 1e-6, f'balance fell while salary still landing at {t:.2f}'
        if ph == 'up': assert b >= prev, f'balance not monotonic (up) at frame {f}'
        else: assert b <= prev, f'balance not monotonic (down) at frame {f}'
        prev = b
    assert round(balance(DUR)) == 0 and round(balance(TL['land']['RENT'] + 0.3)) == TL['salary']
    assert sum(i['amt'] for i in TL['items']) == TL['salary']
    days = [day_at(f / FPS) for f in range(round(DUR * FPS))]; assert days == sorted(days) and max(days) == 3
    print('counters ok: peak', money(TL['salary']), 'final', money(0), 'days', max(days))


if __name__ == '__main__':
    if sys.argv[1] == 'check': check()
    elif sys.argv[1] == 'still': draw(Image.open(sys.argv[2]).convert('RGB'), float(sys.argv[3])).save(sys.argv[4], quality=94)
