"""Text + HUD layer for The Salary Loop (Slow Light Dark series look; JetBrains Mono via ../slow-light-dark-common/sld_text.py).

Plain statements, big numbers: SALARY CREDITED +₹50,000 / balance counter / one flash line per bill / DAY n / 30-day calendar /
the work lines. All times come from timeline.json. balance() is asserted monotonic within each direction; DAY only increases.

  python3 overlay.py still IN.jpg T OUT.jpg      overlay one rendered frame at time T
  python3 overlay.py check                        assert the counters and the loop over every frame
"""
import json, os, sys, math
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
import sld_text
from sld_text import sstep, font, CREAM, W, H

# JetBrains Mono (as installed here) has no U+20B9: draw the rupee sign from DejaVu Sans Mono Bold, everything else unchanged.
_RS = {}
def _tracked(d, text, f, cx, y, track, fill):
    def fo(c):
        if c != '₹': return f
        if f.size not in _RS: _RS[f.size] = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', f.size)
        return _RS[f.size]
    widths = [d.textlength(c, font=fo(c)) for c in text]
    x = cx - (sum(widths) + track * (len(text) - 1)) / 2
    for c, w in zip(text, widths):
        d.text((x, y), c, font=fo(c), fill=fill); x += w + track
sld_text.tracked = _tracked
tracked = _tracked

TL = json.load(open(os.path.join(HERE, 'timeline.json')))
FPS = TL['fps']; DUR = TL['duration']; ITEMS = TL['items']
RS = '₹'; MINUS = '−'
def money(v): return f'{RS}{int(round(v)):,}'


def coin_land(k): return 1.0 + k * 0.02 + 0.0          # coin k lands in the wallet (scene.js coinState)


def balance(t):
    """Rupees: +1,000 per coin as the 50 coins pour into the wallet, then each bill takes its amount."""
    v = 0.0
    for k in range(50): v += 1000 * sstep(coin_land(k) - 0.06, coin_land(k) + 0.06, t)
    for it in ITEMS: v -= it['amt'] * sstep(it['t'] + 0.08, it['t'] + 0.08 + TL['countDur'], t)
    return v


def day_at(t):
    """DAY 1..6 for the six bills (one per day), then the grind runs 6 -> 30 and speeds up."""
    if t < ITEMS[0]['t']: return 0
    if t < TL['morning']: return sum(1 for it in ITEMS if t >= it['t'])
    u = min(1.0, max(0.0, (t - TL['morning'] - 0.4) / (16.6 - TL['morning'] - 0.4)))
    return min(30, 6 + int(24.99 * u ** 1.7))


_CROSS = None
def cross_time(i):
    global _CROSS
    if _CROSS is None:
        _CROSS = {}
        for f in range(round(DUR * FPS)):
            for k in range(1, day_at(f / FPS) + 1): _CROSS.setdefault(k - 1, f / FPS)
    return _CROSS.get(i, 1e9)


def blocks(t):
    out = []
    a = (1 - sstep(2.3, 2.6, t)) + sstep(18.25, 18.5, t)
    if a > 0: out.append((['SALARY CREDITED', f'+{money(TL["salary"])}'], 46, 9, 262, min(1.0, a)))
    d = day_at(t)
    if d and 3.2 <= t < TL['zero'] + 0.05: out.append(([f'DAY {d}'], 60, 14, 262, sstep(3.2, 3.5, t)))
    z = sstep(TL['zero'] + 0.1, TL['zero'] + 0.4, t) * (1 - sstep(8.3, 8.6, t))
    if z > 0: out.append(([f'DAY 6: {money(0)} LEFT.'], 50, 9, 262, z))
    w = sstep(8.9, 9.2, t) * (1 - sstep(9.7, 9.85, t))
    if w > 0: out.append((['TODAY: 6TH'], 56, 12, 262, w))
    al = sstep(9.9, 10.1, t) * (1 - sstep(10.4, 10.6, t))
    if al > 0: out.append((['07:00 AM', 'OFFICE'], 56, 12, 262, al))
    g = sstep(10.7, 11.0, t) * (1 - sstep(12.6, 12.9, t))
    if g > 0: out.append((["BUT THE WORK", "DOESN'T STOP."], 46, 9, 262, g))
    l1 = sstep(13.0, 13.3, t) * (1 - sstep(16.4, 16.7, t)); l2 = sstep(14.4, 14.7, t) * (1 - sstep(16.4, 16.7, t))
    if l1 > 0: out.append((['SALARY LASTED 6 DAYS.'], 46, 9, 262, l1))
    if l2 > 0: out.append((['WORK LASTS ALL 30.'], 46, 9, 329, l2))
    n = sstep(17.0, 17.25, t) * (1 - sstep(18.0, 18.25, t))
    if n > 0: out.append((['1ST OF NEXT MONTH'], 56, 12, 262, n))
    bal = sstep(1.5, 1.8, t) * (1 - sstep(16.8, 17.1, t))
    if bal > 0:
        out.append((['BALANCE'], 26, 10, 396, 0.75 * bal)); out.append(([money(balance(t))], 96, 8, 426, bal))
    if 10.9 <= t < 16.8 and d: out.append(([f'DAY {d}'], 44, 10, 548, sstep(10.9, 11.2, t) * (1 - sstep(16.4, 16.8, t))))
    for it in ITEMS:
        u = t - it['t']
        if -0.05 <= u <= 0.95:
            al2 = sstep(-0.05, 0.1, u) * (1 - sstep(0.7, 0.95, u)); sz = 40 if len(it['label']) > 12 else 52
            out.append(([f'{it["label"]}  {MINUS}{money(it["amt"])}'], sz, 5 if sz == 40 else 6, 700, al2))
    return out


def calendar(img, t):
    on = sstep(3.2, 3.5, t) * (1 - sstep(TL['zero'] + 0.3, TL['zero'] + 0.6, t)) + sstep(10.9, 11.2, t) * (1 - sstep(16.4, 16.8, t))
    if on <= 0: return img
    cw, gap, cols = 50, 10, 10; x0 = (W - (cols * cw + (cols - 1) * gap)) / 2; y0 = 604
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    for i in range(30):
        c, r = i % cols, i // cols; x = x0 + c * (cw + gap); y = y0 + r * (cw + gap); ct = cross_time(i); crossed = t >= ct
        if crossed:
            u = sstep(ct, ct + 0.2, t); L = int(cw * 0.8 * u); m = cw / 2
            d.rectangle([x, y, x + cw, y + cw], fill=(237, 230, 214, int(40 * on)), outline=(237, 230, 214, int(150 * on)), width=2)
            d.line([(m + x - L / 2, y + m - L / 2), (m + x + L / 2, y + m + L / 2)], fill=(237, 230, 214, int(235 * on)), width=4)
            d.line([(m + x - L / 2, y + m + L / 2), (m + x + L / 2, y + m - L / 2)], fill=(237, 230, 214, int(235 * on)), width=4)
        else: d.rectangle([x, y, x + cw, y + cw], outline=(237, 230, 214, int(120 * on)), width=2)
        d.text((x + 6, y + 4), str(i + 1), font=font(20, 'Medium'), fill=(237, 230, 214, int((70 if crossed else 110) * on)))
    base = img.convert('RGBA'); base.alpha_composite(layer); return base.convert('RGB')


def draw(img, t):
    if img.size != (W, H): img = img.resize((W, H), Image.LANCZOS)
    return sld_text.draw(calendar(img, t), blocks(t))


def check():
    prev, ph = 0, 'up'
    for f in range(round(DUR * FPS)):
        t = f / FPS; b = round(balance(t))
        if ph == 'up' and b < prev:
            ph = 'down'; assert t >= 2.0, f'balance fell while the salary was still landing at {t:.2f}'
        assert (b >= prev) if ph == 'up' else (b <= prev), f'balance not monotonic ({ph}) at frame {f}'
        prev = b
    assert round(balance(2.05)) == TL['salary'] and round(balance(7.3)) == 0 and round(balance(DUR)) == 0
    assert sum(i['amt'] for i in ITEMS) == TL['salary'] == 1000 * sum(i['coins'] for i in ITEMS)
    run = TL['salary']; exp = [32000, 20000, 13000, 9000, 5000, 0]
    for it, e in zip(ITEMS, exp): run -= it['amt']; assert run == e, (it['key'], run, e)
    days = [day_at(f / FPS) for f in range(round(DUR * FPS))]
    assert days == sorted(days) and max(days) == 30 and [days.index(k) for k in range(1, 7)] == sorted(days.index(k) for k in range(1, 7))
    assert blocks(0)[0][0] == blocks(DUR - 1 / FPS)[0][0] and abs(blocks(0)[0][4] - blocks(DUR - 1 / FPS)[0][4]) < 0.01, 'loop text mismatch'
    print('counters ok: 50,000 in, six bills, balance 0 at', TL['zero'], 's, DAY max', max(days))


if __name__ == '__main__':
    if sys.argv[1] == 'check': check()
    elif sys.argv[1] == 'still': draw(Image.open(sys.argv[2]).convert('RGB'), float(sys.argv[3])).save(sys.argv[4], quality=94)
