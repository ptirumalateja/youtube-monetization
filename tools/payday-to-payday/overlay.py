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
    """DAY 1..5 for the five deductions, then the routine runs on to DAY 30 (it speeds up)."""
    if t < TL['dayStart'][0]: return 0
    if t < TL['routine0']: return sum(1 for s in TL['dayStart'] if t >= s)
    u = min(1.0, max(0.0, (t - TL['routine0']) / (TL['routine1'] - TL['routine0'])))
    return min(30, 5 + int(25.99 * u ** 1.6))


def light_at(t):
    K = TL['light']
    for (t0, v0), (t1, v1) in zip(K, K[1:]):
        if t <= t1: return v0 if t <= t0 else v0 + (v1 - v0) * sstep(t0, t1, t)
    return K[-1][1]


_CROSS = None
def cross_time(i):
    """Time at which calendar square i (0-based) gets crossed out = when DAY i+1 starts."""
    global _CROSS
    if _CROSS is None:
        _CROSS = {}
        for f in range(round(DUR * FPS)):
            d = day_at(f / FPS)
            for k in range(1, d + 1): _CROSS.setdefault(k - 1, f / FPS)
    return _CROSS.get(i, 1e9)


def blocks(t):
    out = []
    a = 1 - sstep(TL['hookOut'], TL['hookOut'] + 0.2, t)
    a = max(a, sstep(TL['salaryAgain'], TL['salaryAgain'] + 0.5, t))        # the loop: the same line is back before the cut
    if a > 0: out.append(([f'SALARY DAY: {money(TL["salary"])} IN.'], 46, 9, 262, a))
    d = day_at(t); show_day = (TL['hookOut'] + 0.1 <= t < TL['zeroText']) or (TL['dayCounterFrom'] <= t < TL['salaryAgain'] + 0.5)
    if show_day and d:
        al = sstep(TL['hookOut'] + 0.1, TL['hookOut'] + 0.3, t) if t < TL['zeroText'] else sstep(TL['dayCounterFrom'], TL['dayCounterFrom'] + 0.25, t) * (1 - sstep(TL['salaryAgain'], TL['salaryAgain'] + 0.4, t))
        out.append(([f'DAY {d}'], 60, 14, 262, al))
    z = sstep(TL['zeroText'], TL['zeroText'] + 0.3, t) * (1 - sstep(TL['daysText'] - 0.25, TL['daysText'], t))
    if z > 0: out.append(([f'DAY 5: {money(0)} LEFT.'], 50, 9, 262, z))
    e = sstep(TL['daysText'], TL['daysText'] + 0.35, t) * (1 - sstep(TL['dayCounterFrom'] - 0.25, TL['dayCounterFrom'], t))
    if e > 0: out.append(([f'{30 - 5} DAYS TO GO.'], 50, 9, 262, e))
    out.append((['BALANCE'], 26, 10, 346, 0.75))
    out.append(([money(balance(t))], 96, 8, 376, 1.0))
    for it in TL['items']:
        u = t - it['grab']
        if -0.05 <= u <= 1.35:
            al = sstep(-0.05, 0.12, u) * (1 - sstep(1.0, 1.35, u))
            out.append(([f'{it["key"]}  {MINUS}{money(it["amt"])}'], 52, 6, 690, al))
    w = sstep(TL['cycles'][0] + 0.5, TL['cycles'][0] + 0.8, t) * (1 - sstep(TL['cycles'][0] + 1.7, TL['cycles'][0] + 2.0, t))
    if w > 0: out.append((['BACK TO WORK.'], 52, 6, 690, w))
    return out


def calendar(img, t):
    """30 day squares (10 x 3); square n is crossed out when DAY n starts."""
    if t < TL['dayStart'][0] - 0.1: return img
    import math
    a_all = sstep(TL['dayStart'][0] - 0.1, TL['dayStart'][0] + 0.25, t) * (1 - sstep(TL['salaryAgain'], TL['salaryAgain'] + 0.5, t))
    if a_all <= 0: return img
    cw, gap, cols = 50, 10, 10
    x0 = (W - (cols * cw + (cols - 1) * gap)) / 2; y0 = 506
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    for i in range(30):
        c, r = i % cols, i // cols; x = x0 + c * (cw + gap); y = y0 + r * (cw + gap)
        ct = cross_time(i); crossed = t >= ct
        if crossed:
            u = sstep(ct, ct + 0.2, t)
            d.rectangle([x, y, x + cw, y + cw], fill=(237, 230, 214, int(40 * a_all)), outline=(237, 230, 214, int(150 * a_all)), width=2)
            L = int(cw * 0.8 * u); m = cw / 2
            d.line([(m + x - L / 2, y + m - L / 2), (m + x + L / 2, y + m + L / 2)], fill=(237, 230, 214, int(235 * a_all)), width=4)
            d.line([(m + x - L / 2, y + m + L / 2), (m + x + L / 2, y + m - L / 2)], fill=(237, 230, 214, int(235 * a_all)), width=4)
        else:
            d.rectangle([x, y, x + cw, y + cw], outline=(237, 230, 214, int(120 * a_all)), width=2)
        d.text((x + 6, y + 4), str(i + 1), font=font(20, 'Medium'), fill=(237, 230, 214, int((110 if not crossed else 70) * a_all)))
    base = img.convert('RGBA'); base.alpha_composite(layer)
    lab = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lab)
    tracked(ld, 'ONE MONTH', font(24, 'Medium'), W / 2, y0 + 3 * (cw + gap) + 4, 10, (237, 230, 214, int(150 * a_all)))
    base.alpha_composite(lab)
    return base.convert('RGB')


def sun_moon(img, t):
    """Small sun / moon icon next to the day counter during the routine: bright lamp = sun, dim lamp = moon."""
    a = sstep(TL['routine0'] - 0.3, TL['routine0'] + 0.2, t) * (1 - sstep(TL['salaryAgain'] - 0.2, TL['salaryAgain'] + 0.3, t))
    if a <= 0: return img
    import math
    L = light_at(t); day = sstep(0.35, 0.65, L)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer); cx, cy, r = 900, 292, 24
    sun = (232, 184, 90, int(255 * a * day)); moon = (237, 230, 214, int(255 * a * (1 - day)))
    if day > 0.02:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=sun)
        for k in range(8):
            ang = k * math.pi / 4; d.line([(cx + math.cos(ang) * (r + 8), cy + math.sin(ang) * (r + 8)), (cx + math.cos(ang) * (r + 18), cy + math.sin(ang) * (r + 18))], fill=sun, width=4)
    if day < 0.98:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=moon); d.ellipse([cx - r + 14, cy - r - 6, cx + r + 14, cy + r - 6], fill=(0, 0, 0, 0))
        cut = Image.new('L', (W, H), 0); ImageDraw.Draw(cut).ellipse([cx - r + 14, cy - r - 6, cx + r + 14, cy + r - 6], fill=255)
        la = layer.getchannel('A'); la.paste(0, mask=cut); layer.putalpha(la)
    base = img.convert('RGBA'); base.alpha_composite(layer); return base.convert('RGB')


def draw(img, t):
    if img.size != (W, H): img = img.resize((W, H), Image.LANCZOS)
    return sld_text.draw(sun_moon(calendar(img, t), t), blocks(t))


def check():
    prev, ph = 0, 'up'
    for f in range(round(DUR * FPS)):
        t = f / FPS; b = round(balance(t))
        if ph == 'up' and b < prev:
            ph = 'down'; assert t >= TL['land']['RENT'] + 0.25 - 1e-6, f'balance fell while salary still landing at {t:.2f}'
        if ph == 'up': assert b >= prev, f'balance not monotonic (up) at frame {f}'
        else: assert b <= prev, f'balance not monotonic (down) at frame {f}'
        prev = b
    assert round(balance(DUR)) == 0 and round(balance(0)) == 0 and round(balance(TL['land']['RENT'] + 0.3)) == TL['salary']
    assert sum(i['amt'] for i in TL['items']) == TL['salary']
    days = [day_at(f / FPS) for f in range(round(DUR * FPS))]
    assert days == sorted(days), 'DAY counter not monotonic'; assert max(days) == 30 and days.index(5) < days.index(6)
    assert [days.index(k) for k in range(1, 6)] == sorted(days.index(k) for k in range(1, 6))
    assert abs(blocks(0)[0][4] - blocks(DUR - 1 / FPS)[0][4]) < 0.01 and blocks(0)[0][0] == blocks(DUR - 1 / FPS)[0][0], 'loop text mismatch'
    assert abs(light_at(0) - light_at(DUR - 1 / FPS)) < 0.01
    print('counters ok: peak', money(TL['salary']), 'final', money(0), 'DAY max', max(days), '| the balance is 0 on day 5 (', f"{TL['zero']:.2f}s)")


if __name__ == '__main__':
    if sys.argv[1] == 'check': check()
    elif sys.argv[1] == 'still': draw(Image.open(sys.argv[2]).convert('RGB'), float(sys.argv[3])).save(sys.argv[4], quality=94)
