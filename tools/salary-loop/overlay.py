"""Text + HUD layer for The Salary Loop v3 (Slow Light Dark series look; JetBrains Mono via ../slow-light-dark-common/sld_text.py).

The salary arrives as an on-screen message box (not a phone screen in the scene). Plain statements and big numbers: balance counter,
a HAPPINESS bar that drains over days 1-6 and comes back on the 1st, DAY n with a sun/moon, one flash line per bill, a 30-day calendar
with a gold NEXT SALARY square, the work lines. All times come from timeline.json. balance() is asserted monotonic within each
direction; DAY only increases; the end of the file equals the start (the message box, the bell, the happiness).

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
def keys(K, t):
    for (t0, v0), (t1, v1) in zip(K, K[1:]):
        if t <= t1: return v0 if t <= t0 else v0 + (v1 - v0) * sstep(t0, t1, t)
    return K[-1][1]
def hap_at(t): return keys(TL['hap'], t)
def light_at(t): return keys(TL['light'], t)


def coin_land(k): return TL['coinsIn'][0] + 0.45 + k * 0.02          # coin k lands in the wallet (scene.js coinState)


def balance(t):
    """Rupees: +1,000 per coin as the 50 coins pour into the wallet, then each bill takes its amount."""
    v = 0.0
    for k in range(50): v += 1000 * sstep(coin_land(k) - 0.06, coin_land(k) + 0.06, t)
    for it in ITEMS: v -= it['amt'] * sstep(it['t'] + 0.08, it['t'] + 0.08 + TL['countDur'], t)
    return v


def day_at(t):
    """DAY 1..6 for the six mornings (one bill each), then the grind runs 6 -> 30 and speeds up."""
    if t < TL['dayStart'][0]: return 0
    if t < TL['morning']: return sum(1 for d in TL['dayStart'] if t >= d)
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


def card_alpha(t):
    """The salary message box: slides in at 18.95 s and is still there when the file wraps to 0 s (it leaves by ~1.0 s)."""
    a = sstep(TL['notify'][0], TL['notify'][0] + 0.25, t) + (1 - sstep(0.8, 1.0, t)) * (1 if t < TL['notify'][1] else 0)
    return min(1.0, a)


def blocks(t):
    out = []
    d = day_at(t)
    if d and TL['dayStart'][0] - 0.1 <= t < TL['zero'] + 0.05: out.append(([f'DAY {d}'], 60, 14, 262, sstep(TL['dayStart'][0] - 0.1, TL['dayStart'][0] + 0.15, t)))
    z = sstep(TL['zero'] + 0.1, TL['zero'] + 0.4, t) * (1 - sstep(8.2, 8.5, t))
    if z > 0: out.append(([f'DAY 6: {money(0)} LEFT.'], 50, 9, 262, z))
    w = sstep(8.35, 8.6, t) * (1 - sstep(9.25, 9.4, t))
    if w > 0: out.append((['TODAY: 6TH'], 56, 12, 262, w))
    g = sstep(10.7, 11.0, t) * (1 - sstep(12.6, 12.9, t))
    if g > 0: out.append((["BUT THE WORK", "DOESN'T STOP."], 46, 9, 262, g))
    l1 = sstep(13.0, 13.3, t) * (1 - sstep(16.4, 16.7, t)); l2 = sstep(14.4, 14.7, t) * (1 - sstep(16.4, 16.7, t))
    if l1 > 0: out.append((['SALARY LASTED 6 DAYS.'], 46, 9, 262, l1))
    if l2 > 0: out.append((['WORK LASTS ALL 30.'], 46, 9, 329, l2))
    n = sstep(17.2, 17.5, t) * (1 - sstep(18.7, 18.9, t))
    if n > 0: out.append((['1ST OF NEXT MONTH'], 56, 12, 262, n))
    bal = sstep(0.9, 1.2, t) * (1 - sstep(16.8, 17.1, t)) if t > 5 or t < 3 else 1.0
    bal = sstep(0.9, 1.2, t) * (1 - sstep(16.8, 17.1, t))
    if bal > 0 and t > 0.5:
        out.append((['BALANCE'], 26, 10, 346, 0.75 * bal)); out.append(([money(balance(t))], 96, 8, 376, bal))
    if 10.9 <= t < 16.8 and d: out.append(([f'DAY {d}'], 44, 10, 590, sstep(10.9, 11.2, t) * (1 - sstep(16.4, 16.8, t))))
    for it in ITEMS:
        u = t - it['t']
        if -0.05 <= u <= 0.95:
            al2 = sstep(-0.05, 0.1, u) * (1 - sstep(0.7, 0.95, u)); sz = 40 if len(it['label']) > 12 else 52
            out.append(([f'{it["label"]}  {MINUS}{money(it["amt"])}'], sz, 5 if sz == 40 else 6, 600, al2))
    return out


def card(img, t):
    """Message box overlay: the salary notification (gold) and the 7:00 alarm (teal)."""
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer); drew = False
    def box(a, kind, slide):
        nonlocal drew
        if a <= 0: return
        drew = True; y = int(150 - 260 * (1 - slide)); x0, x1 = 90, W - 90; h = 270
        gold = kind == 'salary'; edge = (232, 184, 90) if gold else (143, 199, 232); tcol = (255, 243, 214) if gold else (191, 232, 234)
        d.rounded_rectangle([x0, y, x1, y + h], radius=34, fill=(13, 14, 18, int(225 * a)), outline=edge + (int(255 * a),), width=4)
        d.rounded_rectangle([x0 + 22, y + 22, x0 + 76, y + 76], radius=14, fill=edge + (int(255 * a),))
        tracked(d, '₹' if gold else '⏰'.replace('⏰', '07'), font(30, 'Bold'), x0 + 49, y + 33, 0, (13, 14, 18, int(255 * a)))
        d.text((x0 + 96, y + 30), 'SLOW LIGHT BANK' if gold else 'ALARM', font=font(24, 'Medium'), fill=edge + (int(210 * a),))
        d.text((x1 - 150, y + 30), 'now', font=font(22, 'Medium'), fill=(237, 230, 214, int(150 * a)))
        if gold:
            tracked(d, 'SALARY CREDITED', font(34, 'Bold'), W / 2, y + 100, 7, tcol + (int(255 * a),)); tracked(d, f'+{money(TL["salary"])}', font(74, 'Bold'), W / 2, y + 150, 6, (255, 255, 255, int(255 * a)))
        else:
            tracked(d, '07:00 AM', font(64, 'Bold'), W / 2, y + 100, 6, tcol + (int(255 * a),)); tracked(d, 'OFFICE', font(40, 'Bold'), W / 2, y + 185, 12, edge + (int(255 * a),))
    ca = card_alpha(t); slide = sstep(TL['notify'][0], TL['notify'][0] + 0.25, t) if t > 5 else 1.0
    box(ca, 'salary', slide)
    aa = sstep(TL['alarm'], TL['alarm'] + 0.12, t) * (1 - sstep(TL['sitUp'][1] - 0.2, TL['sitUp'][1], t)); box(aa, 'alarm', sstep(TL['alarm'], TL['alarm'] + 0.2, t))
    if not drew: return img
    base = img.convert('RGBA'); base.alpha_composite(layer); return base.convert('RGB')


def bars(img, t):
    """HAPPINESS bar (drains over days 1-6, small and hopeful in the grind, full again on the 1st), sun/moon icon, calendar."""
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    show = (1 - sstep(17.0, 17.3, t)) + sstep(18.95, 19.3, t); show = min(1.0, show); h = hap_at(t)
    if show > 0:
        bw, bh, bx, by = 380, 16, (W - 380) / 2, 532
        tracked(d, 'HAPPINESS', font(22, 'Medium'), W / 2, by - 30, 9, CREAM + (int(190 * show),))
        d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, outline=CREAM + (int(170 * show),), width=2)
        if h > 0.01: d.rounded_rectangle([bx + 3, by + 3, bx + 3 + (bw - 6) * h, by + bh - 3], radius=5, fill=(232, 184, 90, int(235 * show)) if h > 0.5 else CREAM + (int(220 * show),))
    # sun / moon next to the day counter
    a = sstep(TL['dayStart'][0] - 0.1, TL['dayStart'][0] + 0.2, t) * (1 - sstep(16.6, 16.9, t))
    if a > 0:
        L = light_at(t); day = sstep(0.35, 0.65, L); cx, cy, r = 900, 292, 24
        sun = (232, 184, 90, int(255 * a * day)); moon = (237, 230, 214, int(255 * a * (1 - day)))
        if day > 0.02:
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=sun)
            for k in range(8): ang = k * math.pi / 4; d.line([(cx + math.cos(ang) * (r + 8), cy + math.sin(ang) * (r + 8)), (cx + math.cos(ang) * (r + 18), cy + math.sin(ang) * (r + 18))], fill=sun, width=4)
        if day < 0.98:
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=moon); cut = Image.new('L', (W, H), 0); ImageDraw.Draw(cut).ellipse([cx - r + 14, cy - r - 6, cx + r + 14, cy + r - 6], fill=255)
            la = layer.getchannel('A'); la.paste(0, mask=cut); layer.putalpha(la)
    # calendar: 30 squares + a gold NEXT SALARY square that pulses once he starts going to work
    on = sstep(TL['dayStart'][0] - 0.1, TL['dayStart'][0] + 0.2, t) * (1 - sstep(TL['zero'] + 0.3, TL['zero'] + 0.6, t)) + sstep(10.9, 11.2, t) * (1 - sstep(18.7, 18.95, t))
    if on > 0:
        cw, gap, cols = 50, 10, 10; x0 = (W - (cols * cw + (cols - 1) * gap)) / 2; y0 = 680
        for i in range(30):
            c, r_ = i % cols, i // cols; x = x0 + c * (cw + gap); y = y0 + r_ * (cw + gap); ct = cross_time(i); crossed = t >= ct
            if crossed:
                u = sstep(ct, ct + 0.2, t); L_ = int(cw * 0.8 * u); m = cw / 2
                d.rectangle([x, y, x + cw, y + cw], fill=(237, 230, 214, int(40 * on)), outline=(237, 230, 214, int(150 * on)), width=2)
                d.line([(m + x - L_ / 2, y + m - L_ / 2), (m + x + L_ / 2, y + m + L_ / 2)], fill=(237, 230, 214, int(235 * on)), width=4); d.line([(m + x - L_ / 2, y + m + L_ / 2), (m + x + L_ / 2, y + m - L_ / 2)], fill=(237, 230, 214, int(235 * on)), width=4)
            else: d.rectangle([x, y, x + cw, y + cw], outline=(237, 230, 214, int(120 * on)), width=2)
            d.text((x + 6, y + 4), str(i + 1), font=font(20, 'Medium'), fill=(237, 230, 214, int((70 if crossed else 110) * on)))
        pul = 0.55 + 0.45 * math.sin(t * 5) if t > 10.5 else 0.5; ga = on * sstep(10.8, 11.2, t)
        x, y = x0, y0 + 3 * (cw + gap); d.rectangle([x, y, x + cw, y + cw], fill=(232, 184, 90, int(60 * ga * pul)), outline=(232, 184, 90, int(255 * ga)), width=3); d.text((x + 6, y + 4), '1', font=font(20, 'Bold'), fill=(232, 184, 90, int(255 * ga)))
        tracked(d, 'NEXT SALARY', font(24, 'Bold'), x + cw + 190, y + 12, 8, (232, 184, 90, int(255 * ga * (0.7 + 0.3 * pul))))
    base = img.convert('RGBA'); base.alpha_composite(layer); return base.convert('RGB')


def draw(img, t):
    if img.size != (W, H): img = img.resize((W, H), Image.LANCZOS)
    return sld_text.draw(card(bars(img, t), t), blocks(t))


def check():
    prev, ph = 0, 'up'
    for f in range(round(DUR * FPS)):
        t = f / FPS; b = round(balance(t))
        if ph == 'up' and b < prev:
            ph = 'down'; assert t >= 1.9, f'balance fell while the salary was still landing at {t:.2f}'
        assert (b >= prev) if ph == 'up' else (b <= prev), f'balance not monotonic ({ph}) at frame {f}'
        prev = b
    assert round(balance(2.05)) == TL['salary'] and round(balance(7.4)) == 0 and round(balance(DUR)) == 0
    assert sum(i['amt'] for i in ITEMS) == TL['salary'] == 1000 * sum(i['coins'] for i in ITEMS)
    run = TL['salary']; exp = [32000, 20000, 13000, 9000, 5000, 0]
    for it, e in zip(ITEMS, exp): run -= it['amt']; assert run == e, (it['key'], run, e)
    days = [day_at(f / FPS) for f in range(round(DUR * FPS))]
    assert days == sorted(days) and max(days) == 30 and [days.index(k) for k in range(1, 7)] == sorted(days.index(k) for k in range(1, 7))
    assert abs(card_alpha(0) - card_alpha(DUR - 1 / FPS)) < 0.01 and card_alpha(0) > 0.99, 'message box does not wrap'
    assert abs(hap_at(0) - hap_at(DUR)) < 1e-6 and abs(light_at(0) - light_at(DUR)) < 1e-6
    hs = [hap_at(t / FPS) for t in range(int(1.5 * FPS), int(6.9 * FPS))]; assert all(b <= a + 1e-9 for a, b in zip(hs, hs[1:])), 'happiness must only drain over days 1-6'
    print('counters ok: 50,000 in, six bills, balance 0 at', TL['zero'], 's, DAY max', max(days), '| happiness drains 1.0 ->', round(hap_at(6.9), 2), 'then rises to', round(hap_at(19.5), 2), 'on the 1st')


if __name__ == '__main__':
    if sys.argv[1] == 'check': check()
    elif sys.argv[1] == 'still': draw(Image.open(sys.argv[2]).convert('RGB'), float(sys.argv[3])).save(sys.argv[4], quality=94)
