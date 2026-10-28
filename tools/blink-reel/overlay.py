"""Text layer for You Were Blind for 20 Minutes Today: the hook, three lock-in lines, the DARKNESS TODAY counter (00:00 -> 20:00, asserted
monotonic), time-of-day chips, the rehook, the brain line and the mirror close. Frame 0 carries the hook on the shut lids, so the loop closes.

  python3 overlay.py still IN.jpg T OUT.jpg       overlay one rendered frame at time T
  python3 overlay.py frames IN_DIR OUT_DIR        overlay every fNNNNN.jpg (30 fps)
  python3 overlay.py check                        assert the counter is monotonic
"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
FONT_DIR = '/usr/share/fonts/truetype/jetbrains-mono'
W, H, FPS, DUR = 1080, 1920, 30, 19.0
CREAM = (250, 240, 222); GOLD = (240, 184, 92); DIM = (200, 190, 175)
_f = {}
def font(size, weight='Bold'):
    k = (size, weight)
    if k not in _f: _f[k] = ImageFont.truetype(os.path.join(FONT_DIR, f'JetBrainsMono-{weight}.ttf'), size)
    return _f[k]
def sstep(a, b, x):
    u = min(1.0, max(0.0, (x - a) / (b - a))); return u * u * (3 - 2 * u)
def win(t, a, b, fi=0.12, fo=0.15):
    """Opacity of an element shown on [a, b]; a=0 means already fully on at frame 0."""
    if t < a or t > b: return 0.0
    return (1.0 if a <= 0 else sstep(a, a + fi, t)) * (1 - sstep(b - fo, b, t))
def tracked(d, text, size, cx, y, track, fill, weight='Bold'):
    f = font(size, weight); ws = [d.textlength(c, font=f) for c in text]; tot = sum(ws) + track * (len(text) - 1); x = cx - tot / 2
    for c, w in zip(text, ws): d.text((x, y), c, font=f, fill=fill); x += w + track
    return tot

def dark_s(t):
    """Seconds of darkness counted so far: 0 at 6.0 s, 1200 (20:00) at 10.9 s, accelerating, then held."""
    u = min(1.0, max(0.0, (t - 6.0) / 4.9)); return 1200.0 * u ** 1.7

TOD = [(6.0, 7.0, '7 AM'), (7.0, 8.0, '1 PM'), (8.0, 9.0, '6 PM'), (9.0, 10.0, '11 PM')]
def layer(t):
    """Return (text RGBA layer, shadow RGBA layer) for time t."""
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    def lines(rows, size, y0, a, col=CREAM, gap=1.18, track=2):
        for i, r in enumerate(rows):
            c = col[i] if isinstance(col, list) else col
            tracked(d, r, size, W / 2, y0 + i * size * gap, track, c + (int(255 * a),))
    # hook (frame 0)
    a = win(t, 0, 2.45);
    if a: lines(['YOU WERE BLIND', 'FOR 20 MINUTES', 'TODAY.'], 92, 250, a, [CREAM, GOLD, CREAM])
    # lock-in
    for k, (t0, txt, size, col) in enumerate([(2.55, 'YOU BLINK 10,000+', 54, CREAM), (2.55, 'TIMES A DAY.', 54, CREAM), (3.6, 'EACH ONE = 0.1 s', 54, CREAM), (3.6, 'OF DARKNESS.', 54, CREAM), (4.65, "YOU'VE NEVER", 70, GOLD), (4.65, 'SEEN ONE.', 70, GOLD)]):
        a = win(t, t0, 5.95)
        if a: y = [1120, 1188, 1270, 1338, 1420, 1502][k]; tracked(d, txt, size, W / 2, y, 2, col + (int(255 * a),))
    # counter + time-of-day chips
    a = win(t, 6.0, 12.0, 0.1, 0.2)
    if a:
        s = int(dark_s(t)); tracked(d, 'DARKNESS TODAY', 36, W / 2, 300, 10, DIM + (int(235 * a),), 'Medium')
        tracked(d, f'{s // 60:02d}:{s % 60:02d}', 150, W / 2, 352, 6, (GOLD if t >= 10.9 else CREAM) + (int(255 * a),))
        for t0, t1, lab in TOD:
            b = win(t, t0, t1, 0.08, 0.1)
            if b: tracked(d, lab, 34, W / 2, 560, 6, CREAM + (int(220 * b),), 'Medium')
    a = win(t, 10.9, 12.0, 0.06, 0.15)
    if a: lines(['20 MINUTES.', 'EVERY DAY.'], 100, 1180, a, [CREAM, GOLD])
    # eye + brain
    a = win(t, 12.1, 13.75)
    if a: lines(["SO WHY DON'T", 'YOU NOTICE?'], 66, 1430, a)
    a = win(t, 13.95, 15.95)
    if a: tracked(d, 'YOUR VISUAL BRAIN', 34, W / 2, 320, 10, DIM + (int(230 * a),), 'Medium')
    a = win(t, 14.25, 15.95)
    if a: lines(['YOUR BRAIN', 'SWITCHES OFF', 'THE DARK.'], 92, 760, a, [CREAM, CREAM, GOLD])
    # mirror
    a = win(t, 16.05, 18.82)
    if a: lines(['TRY IT IN', 'A MIRROR.'], 66, 300, a)
    a = win(t, 16.95, 18.82, 0.08, 0.1)
    if a: lines(["YOU'LL NEVER", 'CATCH ONE.'], 96, 1300, a, [CREAM, GOLD])
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sh.putalpha(L.getchannel('A').point(lambda v: int(v * 0.75))); sh = sh.filter(ImageFilter.GaussianBlur(10))
    return L, sh

def apply(img, t):
    L, sh = layer(t); base = img.convert('RGBA'); base.alpha_composite(sh, (0, 6)); base.alpha_composite(L); return base.convert('RGB')

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'check':
        prev = -1
        for f in range(int(DUR * FPS)):
            v = int(dark_s(f / FPS)); assert v >= prev, (f, v, prev); prev = v
        assert prev == 1200; print('counter monotonic, ends at 20:00')
    elif cmd == 'still':
        apply(Image.open(sys.argv[2]), float(sys.argv[3])).save(sys.argv[4], quality=92)
    elif cmd == 'frames':
        src, dst = sys.argv[2], sys.argv[3]; os.makedirs(dst, exist_ok=True)
        for f in range(int(DUR * FPS)):
            p = os.path.join(src, f'f{f:05d}.jpg'); apply(Image.open(p), f / FPS).save(os.path.join(dst, f'f{f:05d}.jpg'), quality=94)
        print('overlaid', int(DUR * FPS))
