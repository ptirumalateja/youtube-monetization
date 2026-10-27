"""Text layer for The Salary Loop V2. One sentence carries the reel, split across the loop like the 30 Friends reel:
"YOUR SALARY LASTS 6 DAYS." (hook, from frame 0, and again over the last frames so the loop seam is invisible)
"YOUR WORK LASTS ALL 30." (payoff, held from the street through the office).
In between, one spine: DAY n and the balance; bill cards, the ₹0 hit and the alarm come from the V1 overlay at source time.

  python3 overlay_v2.py still SRC_FRAME.jpg OUT_T OUT.jpg     overlay one rendered source frame at output time OUT_T
"""
import json, os, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import overlay as V1
from overlay import W, H, sstep, tracked, rr, money, ITEMS, TL
ED = json.load(open(os.path.join(HERE, 'edit.json'))); FPS = ED['fps']
MAP = [s for a, b in ED['segments'] for s in range(a, b)]           # output frame -> source frame
TOTAL = len(MAP); DUR = TOTAL / FPS
CREAM = (255, 244, 224); GOLD = (255, 200, 110); RED = (255, 110, 90)


def src_t(f): return MAP[min(f, TOTAL - 1)] / FPS


def out_t(ts):
    """First output time showing source time ts (or the nearest one after it)."""
    s = round(ts * FPS)
    for f, m in enumerate(MAP):
        if m >= s: return f / FPS
    return DUR


T_RENT = out_t(TL['scenes'][1]['t0']); T_ZERO = out_t(TL['zero']); T_ALARM = out_t(TL['alarm']); T_STREET = out_t(12.2)
T_OFF0 = out_t(TL['office'][0]); T_OFF1 = out_t(TL['office'][1] - 0.01); T_BED3 = out_t(18.2); T_CARD2 = out_t(19.1)


def top_shade(layer, a):
    """A soft dark band behind the top lines so they read on the bright street and office windows."""
    sh = Image.new('RGBA', (W, 700), (0, 0, 0, 0)); d = ImageDraw.Draw(sh)
    for y in range(700): d.line([(0, y), (W, y)], fill=(8, 5, 4, int(165 * a * (1 - y / 700) ** 1.4)))
    layer.alpha_composite(sh, (0, 0))


def big(d, lines, y0, a, size=96, gap=118, cols=(CREAM, GOLD)):
    if a <= 0: return
    for i, ln in enumerate(lines):
        y = y0 + i * gap; c = cols[min(i, len(cols) - 1)]
        tracked(d, ln, size, W / 2 + 3, y + 5, 6, (0, 0, 0, int(170 * a))); tracked(d, ln, size, W / 2, y, 6, c + (int(255 * a),))


def card(layer, a, y=420):
    """The SALARY CREDITED box, parked under the hook line (V1 drew it at the very top)."""
    if a <= 0: return
    tmp = Image.new('RGBA', (W, H), (0, 0, 0, 0)); V1.notification(tmp, V1.CARDS[0][0] + 1.0)   # fully in
    if a < 1: tmp.putalpha(tmp.getchannel('A').point(lambda v: int(v * a)))
    layer.alpha_composite(tmp, (0, y - 160))


def spine(d, t, ts):
    """DAY n huge, the balance right under it: the only counter on screen during the bills."""
    a = sstep(T_RENT, T_RENT + 0.12, t) * (1 - sstep(T_ZERO - 0.02, T_ZERO + 0.05, t))
    if a <= 0: return
    tracked(d, f'DAY {max(1, V1.day_at(ts))}', 120, W / 2 + 3, 145, 14, (0, 0, 0, int(170 * a))); tracked(d, f'DAY {max(1, V1.day_at(ts))}', 120, W / 2, 140, 14, CREAM + (int(255 * a),))
    b = V1.balance(ts); w = 660; x0 = (W - w) / 2; y = 310
    rr(d, [x0, y, x0 + w, y + 120], 60, (20, 14, 12, int(215 * a)), (255, 255, 255, int(70 * a)), 2)
    tracked(d, 'BALANCE', 28, x0 + 44, y + 46, 8, (230, 215, 190, int(220 * a)), 'Medium', anchor='l')
    tracked(d, money(b), 72, x0 + w - 44 - 360, y + 22, 3, (RED if b < 1 else (255, 255, 255)) + (int(255 * a),), anchor='l')


def draw(img, f):
    t = f / FPS; ts = src_t(f)
    if img.size != (W, H): img = img.resize((W, H), Image.LANCZOS)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    hook_in = 1 - sstep(T_RENT - 0.2, T_RENT - 0.02, t); hook_end = sstep(DUR - 0.75, DUR - 0.45, t)
    pay = sstep(T_STREET, T_STREET + 0.15, t) * (1 - sstep(T_BED3 - 0.15, T_BED3, t))
    top_shade(layer, max(hook_in, hook_end, pay, sstep(T_RENT, T_RENT + 0.1, t) * (1 - sstep(T_STREET, T_STREET + 0.1, t)) * 0.8))
    d = ImageDraw.Draw(layer)
    V1.bill_cards(layer, ts)
    spine(d, t, ts)
    # the hit: DAY 6, ₹0, until the alarm
    z = sstep(T_ZERO, T_ZERO + 0.08, t) * (1 - sstep(T_ALARM - 0.1, T_ALARM, t))
    big(d, ['DAY 6.', f'{money(0)} LEFT.'], 150, z, 120, 150, (CREAM, RED))
    V1.alarm(layer, ts)
    # the payoff, held from the street to the end of the office
    big(d, ['YOUR WORK', 'LASTS ALL 30.'], 130, pay)
    if T_OFF0 <= t < T_BED3:
        u = (t - T_OFF0) / (T_OFF1 - T_OFF0); dd = min(30, 7 + int(23.99 * max(0.0, min(1.0, u)))); a = sstep(T_OFF0, T_OFF0 + 0.15, t) * pay
        tracked(d, f'DAY {dd}  ·  BALANCE {money(0)}', 40, W / 2, 400, 6, (255, 214, 160, int(240 * a)), 'Medium')
    nm = sstep(T_BED3, T_BED3 + 0.12, t) * (1 - sstep(T_CARD2 - 0.15, T_CARD2, t))
    big(d, ['1ST OF', 'NEXT MONTH.'], 150, nm, 96, 118, (CREAM, CREAM))
    # the hook, from frame 0, and back over the last frames so the replay is seamless
    big(d, ['YOUR SALARY', 'LASTS 6 DAYS.'], 130, max(hook_in, hook_end))
    card(layer, max(1 - sstep(T_RENT - 0.6, T_RENT - 0.3, t), sstep(T_CARD2, T_CARD2 + 0.2, t)))
    tracked(d, 'SLOW LIGHT', 24, W / 2, 1548, 10, CREAM + (90,), 'Medium')
    base = img.convert('RGBA'); base.alpha_composite(layer); return base.convert('RGB')


if __name__ == '__main__':
    if sys.argv[1] == 'still':
        t = float(sys.argv[3]); draw(Image.open(sys.argv[2]).convert('RGB'), round(t * FPS)).save(sys.argv[4], quality=94)
    elif sys.argv[1] == 'times':
        print(f'{TOTAL} frames, {DUR:.2f} s; rent {T_RENT:.2f}, zero {T_ZERO:.2f}, alarm {T_ALARM:.2f}, street {T_STREET:.2f}, office {T_OFF0:.2f}-{T_OFF1:.2f}, bed3 {T_BED3:.2f}, card {T_CARD2:.2f}')
