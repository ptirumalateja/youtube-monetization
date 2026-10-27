"""Text + HUD layer for The Salary Loop (warm). The salary arrives as an on-screen message box (white card, bell, amount), every bill pops up as a
card with its amount, a balance pill counts 50,000 -> 0, a HAPPINESS bar follows his face, DAY n runs 1 -> 30. All times come from timeline.json.
balance() is asserted monotonic within each direction; DAY only increases; the file's end equals its start (message box, bar, mood).

  python3 overlay.py still IN.jpg T OUT.jpg      overlay one rendered frame at time T
  python3 overlay.py check                        assert the counters and the loop over every frame
"""
import json, os, sys, math
from PIL import Image, ImageDraw, ImageFilter, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = '/usr/share/fonts/truetype/jetbrains-mono'
W, H = 1080, 1920
CREAM = (250, 240, 222); INK = (50, 34, 24); GREEN = (28, 128, 66); GOLD = (232, 160, 40); RED = (200, 60, 46)
_f = {}
def font(size, weight='Bold'):
    k = (size, weight)
    if k not in _f: _f[k] = ImageFont.truetype(os.path.join(FONT_DIR, f'JetBrainsMono-{weight}.ttf'), size)
    return _f[k]
_RS = {}
def rfont(size):
    if size not in _RS: _RS[size] = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', size)
    return _RS[size]
def sstep(a, b, x):
    u = min(1.0, max(0.0, (x - a) / (b - a))); return u * u * (3 - 2 * u)
def tracked(d, text, size, cx, y, track, fill, weight='Bold', anchor='c'):
    """Centred text with letter spacing; the rupee sign is drawn from DejaVu Sans Mono Bold (JetBrains Mono has no U+20B9 here)."""
    fs = [rfont(size) if c == '₹' else font(size, weight) for c in text]; ws = [d.textlength(c, font=f) for c, f in zip(text, fs)]
    tot = sum(ws) + track * (len(text) - 1); x = cx - tot / 2 if anchor == 'c' else cx
    for c, f, w in zip(text, fs, ws): d.text((x, y), c, font=f, fill=fill); x += w + track
    return tot

TL = json.load(open(os.path.join(HERE, 'timeline.json')))
FPS = TL['fps']; DUR = TL['duration']; ITEMS = TL['items']; RS = '₹'; MINUS = '−'
def money(v): return f'{RS}{int(round(v)):,}'
def keys(K, t):
    for (t0, v0), (t1, v1) in zip(K, K[1:]):
        if t <= t1: return v0 if t <= t0 else v0 + (v1 - v0) * sstep(t0, t1, t)
    return K[-1][1]
def hap_at(t): return keys(TL['hap'], t)


def balance(t):
    """Rupees: +50,000 lands with the notification, then each bill takes its amount."""
    v = TL['salary'] * sstep(TL['notify'][1] - 0.2 if False else 0.45, 0.85, t)
    for it in ITEMS: v -= it['amt'] * sstep(it['t'] + 0.15, it['t'] + 0.15 + TL['countDur'], t)
    return v


def day_at(t):
    """DAY 1..6 as the six bills hit; then DAY 6 -> 30 along the office time-lapse (the same number the wall calendar shows)."""
    d = sum(1 for it in ITEMS if t >= it['t'] - 0.25)
    o0, o1 = TL['office']
    if t < o0: return d
    u = min(1.0, max(0.0, (t - o0) / (o1 - o0))); return min(30, 6 + int(24.99 * u))


CARDS = [(TL['notify'][0], TL['notify'][1]), (19.1, 20.5)]   # the salary card in the hook, and again when next month's salary lands


def card_alpha(t):
    return max(sstep(a, a + 0.25, t) * (1 - sstep(b, b + 0.3, t)) for a, b in CARDS)


def card_slide(t):
    return max(sstep(a, a + 0.25, t) if t >= a else 0.0 for a, b in CARDS)


def rr(d, box, r, fill, outline=None, width=0): d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def bell(d, cx, cy, s, col):
    d.pieslice([cx - s, cy - s * 1.1, cx + s, cy + s * 0.9], 180, 360, fill=col); d.rectangle([cx - s, cy - s * 0.15, cx + s, cy + s * 0.55], fill=col); d.rectangle([cx - s * 1.25, cy + s * 0.45, cx + s * 1.25, cy + s * 0.7], fill=col); d.ellipse([cx - s * 0.3, cy + s * 0.7, cx + s * 0.3, cy + s * 1.1], fill=col)


def notification(layer, t):
    a = card_alpha(t)
    if a <= 0: return
    d = ImageDraw.Draw(layer); slide = card_slide(t) if t >= CARDS[1][0] else sstep(TL['notify'][0], TL['notify'][0] + 0.25, t); y = int(160 - 300 * (1 - slide)); x0, x1, h = 110, W - 110, 250
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([x0 + 6, y + 14, x1 + 6, y + h + 14], radius=40, fill=(0, 0, 0, int(110 * a))); layer.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
    rr(d, [x0, y, x1, y + h], 40, (255, 252, 244, int(246 * a)), (232, 170, 60, int(255 * a)), 4)
    rr(d, [x0 + 28, y + 30, x0 + 108, y + 110], 22, (255, 190, 60, int(255 * a))); bell(d, x0 + 68, y + 66, 18, (255, 255, 255, int(255 * a)))
    d.text((x0 + 130, y + 36), 'SLOW LIGHT BANK', font=font(26, 'Medium'), fill=(110, 90, 70, int(255 * a))); d.text((x1 - 120, y + 38), 'now', font=font(24, 'Medium'), fill=(150, 130, 110, int(255 * a)))
    tracked(d, 'SALARY CREDITED', 40, W / 2, y + 104, 6, INK + (int(255 * a),)); tracked(d, f'+{money(TL["salary"])}', 84, W / 2, y + 152, 5, GREEN + (int(255 * a),))
    # sparkle ticks around the box, like the reference's notification
    for ang in (-2.6, -2.2, -0.9, -0.5): d.line([(W / 2 + math.cos(ang) * 470, y + 100 + math.sin(ang) * 140), (W / 2 + math.cos(ang) * 505, y + 100 + math.sin(ang) * 160)], fill=(255, 200, 70, int(255 * a * 0.9)), width=6)


def alarm(layer, t):
    a = sstep(TL['alarm'], TL['alarm'] + 0.12, t) * (1 - sstep(TL['wake'][1] - 0.3, TL['wake'][1], t))
    if a <= 0: return
    d = ImageDraw.Draw(layer); y = int(160 - 300 * (1 - sstep(TL['alarm'], TL['alarm'] + 0.2, t))); x0, x1, h = 110, W - 110, 250
    rr(d, [x0, y, x1, y + h], 40, (24, 36, 44, int(240 * a)), (143, 199, 232, int(255 * a)), 4); rr(d, [x0 + 28, y + 30, x0 + 108, y + 110], 22, (143, 199, 232, int(255 * a))); d.text((x0 + 40, y + 52), '07', font=font(38), fill=(24, 36, 44, int(255 * a)))
    d.text((x0 + 130, y + 36), 'ALARM', font=font(26, 'Medium'), fill=(180, 210, 230, int(255 * a))); tracked(d, '07:00 AM', 96, W / 2, y + 88, 6, (230, 245, 255, int(255 * a))); tracked(d, 'OFFICE', 44, W / 2, y + 190, 14, (143, 199, 232, int(255 * a)))


def bill_cards(layer, t):
    d = ImageDraw.Draw(layer)
    if t < TL['scenes'][1]['t0']: return
    for i, it in enumerate(ITEMS):
        u = t - it['t']
        if -0.15 <= u <= 0.95:
            a = sstep(-0.15, 0.1, u) * (1 - sstep(0.7, 0.95, u)); pop = 0.9 + 0.1 * sstep(-0.15, 0.15, u); lab = it['label']; amt = f'{MINUS}{money(it["amt"])}'
            fs = 40 if len(lab) < 12 else 30; wlab = d.textlength(lab, font=font(fs)); w = int(max(560, wlab + 330) * pop); h = int(150 * pop); cx = W / 2; y = 1330
            sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([cx - w / 2 + 4, y + 12, cx + w / 2 + 4, y + h + 12], radius=34, fill=(0, 0, 0, int(120 * a))); layer.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
            rr(d, [cx - w / 2, y, cx + w / 2, y + h], 34, (255, 252, 244, int(246 * a)))
            col = [(212, 70, 52), (52, 100, 190), (60, 150, 70), (230, 170, 40), (210, 110, 40), (60, 140, 200)][i]
            rr(d, [cx - w / 2 + 24, y + 24, cx - w / 2 + 24 + h - 48, y + h - 24], 20, col + (int(255 * a),)); d.text((cx - w / 2 + 38, y + h / 2 - 28), str(i + 1), font=font(50), fill=(255, 255, 255, int(255 * a)))
            d.text((cx - w / 2 + h, y + 30), lab, font=font(fs), fill=INK + (int(255 * a),)); tracked(d, amt, 62, cx - w / 2 + h, y + 76, 2, (190, 50, 40, int(255 * a)), anchor='l')


def hud(layer, t):
    d = ImageDraw.Draw(layer)
    # balance pill
    bal = sstep(ITEMS[0]['t'] - 0.7, ITEMS[0]['t'] - 0.4, t) * (1 - sstep(18.4, 18.8, t))
    if bal > 0 and t > TL['scenes'][1]['t0']:
        b = balance(t); w = 600; x0 = (W - w) / 2; y = 330
        rr(d, [x0, y, x0 + w, y + 104], 52, (20, 14, 12, int(210 * bal)), (255, 255, 255, int(70 * bal)), 2)
        tracked(d, 'BALANCE', 26, x0 + 40, y + 38, 8, (230, 215, 190, int(220 * bal)), 'Medium', anchor='l'); tracked(d, money(b), 60, x0 + w - 40 - 310, y + 22, 3, ((255, 120, 100) if b < 1 else (255, 255, 255)) + (int(255 * bal),), anchor='l')


def strike_strip(layer, t):
    """Days 1-6 of the month in a row: each bill strikes its day through, like a calendar."""
    a = sstep(TL['scenes'][1]['t0'] - 0.05, TL['scenes'][1]['t0'] + 0.2, t) * (1 - sstep(TL['alarm'] - 0.25, TL['alarm'] - 0.05, t))
    if a <= 0: return
    d = ImageDraw.Draw(layer); bw, gap = 92, 14; x0 = (W - (6 * bw + 5 * gap)) / 2; y = 452
    rr(d, [x0 - 24, y - 16, W - x0 + 24, y + bw + 16], 30, (20, 14, 12, int(170 * a)))
    for i, it in enumerate(ITEMS):
        x = x0 + i * (bw + gap); rr(d, [x, y, x + bw, y + bw], 18, (250, 240, 222, int(240 * a)), None)
        tracked(d, str(i + 1), 46, x + bw / 2, y + 22, 0, INK + (int(255 * a),))
        k = sstep(it['t'] + 0.05, it['t'] + 0.3, t)
        if k > 0:
            d.line([(x + 10, y + 10), (x + 10 + (bw - 20) * k, y + 10 + (bw - 20) * k)], fill=RED + (int(255 * a),), width=9)
            d.line([(x + bw - 10, y + 10), (x + bw - 10 - (bw - 20) * k, y + 10 + (bw - 20) * k)], fill=RED + (int(255 * a),), width=9)


def end_card(layer, t):
    a = sstep(19.35, 19.75, t)
    if a <= 0: return
    d = ImageDraw.Draw(layer); d.rectangle([0, 0, W, H], fill=(10, 6, 4, int(150 * a)))
    ta = sstep(19.5, 19.85, t); y = 800 - int(20 * (1 - ta))
    tracked(d, 'LIFE GOES ON.', 92, W / 2, y, 8, (255, 244, 224, int(255 * ta)))
    tb = sstep(19.7, 20.0, t); tracked(d, 'UNTIL THE NEXT 1ST.', 40, W / 2, y + 150, 10, (255, 200, 110, int(255 * tb)), 'Medium')


def top_text(layer, t):
    d = ImageDraw.Draw(layer); sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh); items = []
    dd = day_at(t)
    if dd and TL['scenes'][1]['t0'] + 0.3 <= t < TL['zero'] + 0.1: items.append((f'DAY {dd}', 64, 14, 250, sstep(2.7, 3.0, t)))
    z = sstep(TL['zero'] + 0.1, TL['zero'] + 0.4, t) * (1 - sstep(TL['alarm'] - 0.25, TL['alarm'] - 0.05, t))
    if z > 0: items.append((f'DAY 6: {money(0)} LEFT.', 52, 9, 250, z))
    al = sstep(9.05, 9.3, t) * (1 - sstep(10.3, 10.5, t))
    if al > 0: items.append(('TODAY: 6TH', 56, 12, 175, al * 0))
    g = sstep(12.3, 12.55, t) * (1 - sstep(13.0, 13.2, t))
    if g > 0: items.append(("BUT THE WORK DOESN'T STOP.", 44, 8, 250, g))
    if t >= 13.2 and t < 18.2:
        a1 = sstep(13.5, 13.8, t) * (1 - sstep(17.8, 18.1, t)); a2 = sstep(14.9, 15.2, t) * (1 - sstep(17.8, 18.1, t))
        items.append(('SALARY LASTED 6 DAYS.', 44, 8, 200, a1)); items.append(('WORK LASTS ALL 30.', 44, 8, 262, a2))
        items.append((f'DAY {dd}', 50, 12, 556, sstep(13.5, 13.8, t) * (1 - sstep(17.8, 18.1, t))))
    n = sstep(18.25, 18.45, t) * (1 - sstep(18.7, 18.9, t))
    if n > 0: items.append(('1ST OF NEXT MONTH', 56, 12, 250, n))
    for text, size, tr, y, a in items:
        if a <= 0: continue
        tracked(sd, text, size, W / 2, y, tr, (0, 0, 0, int(200 * a))); tracked(d, text, size, W / 2, y, tr, (255, 244, 224, int(255 * a)))
    layer.alpha_composite(sh.filter(ImageFilter.GaussianBlur(7))); 
    d2 = ImageDraw.Draw(layer)
    for text, size, tr, y, a in items:
        if a > 0: tracked(d2, text, size, W / 2, y, tr, (255, 244, 224, int(255 * a)))
    # a gold NEXT SALARY chip while he works: the hope
    h = sstep(13.7, 14.0, t) * (1 - sstep(17.9, 18.2, t))
    if h > 0:
        pul = 0.6 + 0.4 * math.sin(t * 5); rr(d2, [W / 2 - 260, 700, W / 2 + 260, 776], 38, (255, 196, 70, int(70 * h * pul)), (255, 196, 70, int(255 * h)), 3); tracked(d2, 'NEXT SALARY: 1ST', 34, W / 2, 720, 6, (255, 214, 120, int(255 * h)))


def draw(img, t):
    if img.size != (W, H): img = img.resize((W, H), Image.LANCZOS)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); hud(layer, t); bill_cards(layer, t); strike_strip(layer, t); top_text(layer, t); notification(layer, t); end_card(layer, t); alarm(layer, t)
    wm = ImageDraw.Draw(layer); tracked(wm, 'SLOW LIGHT', 24, W / 2, 1548, 10, (255, 244, 224, int(255 * 0.35)), 'Medium')
    base = img.convert('RGBA'); base.alpha_composite(layer); return base.convert('RGB')


def check():
    prev, ph = 0, 'up'
    for f in range(round(DUR * FPS)):
        t = f / FPS; b = round(balance(t))
        if ph == 'up' and b < prev: ph = 'down'
        assert (b >= prev) if ph == 'up' else (b <= prev), f'balance not monotonic ({ph}) at frame {f}'
        prev = b
    assert round(balance(1.0)) == TL['salary'] and round(balance(10.4)) == 0 and round(balance(DUR)) == 0
    assert sum(i['amt'] for i in ITEMS) == TL['salary']
    run = TL['salary']; exp = [32000, 20000, 13000, 8000, 4000, 0]
    for it, e in zip(ITEMS, exp): run -= it['amt']; assert run == e, (it['key'], run, e)
    days = [day_at(f / FPS) for f in range(round(DUR * FPS))]
    assert days == sorted(days) and max(days) == 30 and days[0] == 0 and [days.index(k) for k in range(1, 7)] == sorted(days.index(k) for k in range(1, 7))
    print('counters ok: 50,000 in, six bills, balance 0 at', TL['zero'], 's, DAY max', max(days))


if __name__ == '__main__':
    if sys.argv[1] == 'check': check()
    elif sys.argv[1] == 'still': draw(Image.open(sys.argv[2]).convert('RGB'), float(sys.argv[3])).save(sys.argv[4], quality=94)
