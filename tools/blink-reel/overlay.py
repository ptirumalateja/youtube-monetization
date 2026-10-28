"""Text layer for You Were Blind for 20 Minutes Today (V3, 22 s): the hook over the blinking eye, two one-line lock-in beats, the
DARKNESS TODAY counter (00:00 -> 20:00, asserted monotonic) with time-of-day chips, the 20:00 rehook, "~1 YEAR" in a lifetime, the eye
question, the brain line, the mirror dare and the follow CTA. V2's layer is kept in overlay_v2.py.

  python3 overlay.py still IN.jpg T OUT.jpg       overlay one rendered frame at time T
  python3 overlay.py frames IN_DIR OUT_DIR        overlay every fNNNNN.jpg (30 fps)
  python3 overlay.py check                        assert the counter is monotonic
"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
FONT_DIR = '/usr/share/fonts/truetype/jetbrains-mono'
W, H, FPS, DUR = 1080, 1920, 30, 22.0
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
    """Seconds of darkness counted so far: 0 at 5.4 s, 1200 (20:00) at 9.9 s, accelerating, then held."""
    u = min(1.0, max(0.0, (t - 5.4) / 4.5)); return 1200.0 * u ** 1.7

TOD = [(5.4, 6.4, '7 AM'), (6.4, 7.4, '1 PM'), (7.4, 8.4, '6 PM'), (8.4, 9.3, '11 PM')]
def layer(t):
    """Return (text RGBA layer, shadow RGBA layer) for time t. V3: payoff-first, one line per beat, nothing below y 1300."""
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    def lines(rows, size, y0, a, col=CREAM, gap=1.18, track=2, weight='Bold'):
        for i, r in enumerate(rows):
            c = col[i] if isinstance(col, list) else col
            tracked(d, r, size, W / 2, y0 + i * size * gap, track, c + (int(255 * a),), weight)
    # hook (frame 0, over the eye)
    a = win(t, 0, 2.35)
    if a: lines(['YOU WERE BLIND', 'FOR 20 MINUTES', 'TODAY.'], 96, 200, a, [CREAM, GOLD, CREAM])
    # lock-in: one beat per shot
    a = win(t, 2.45, 3.85, 0.1, 0.12)
    if a: lines(['YOU BLINK ~12,000', 'TIMES A DAY.'], 80, 230, a, [CREAM, CREAM])
    a = win(t, 3.95, 5.35, 0.1, 0.12)
    if a: lines(['EACH ONE:', '0.1 s OF DARKNESS.'], 80, 230, a, [CREAM, GOLD])
    # counter + time-of-day chips
    a = win(t, 5.4, 11.2, 0.1, 0.15)
    if a:
        s = int(dark_s(t)); tracked(d, 'DARKNESS TODAY', 46, W / 2, 240, 10, DIM + (int(235 * a),), 'Medium')
        tracked(d, f'{s // 60:02d}:{s % 60:02d}', 160, W / 2, 300, 6, (GOLD if t >= 9.9 else CREAM) + (int(255 * a),))
        for t0, t1, lab in TOD:
            b = win(t, t0, t1, 0.08, 0.1)
            if b: tracked(d, lab, 54, W / 2, 500, 6, CREAM + (int(230 * b),), 'Medium')
    a = win(t, 9.9, 11.2, 0.06, 0.15)
    if a: lines(['20 MINUTES.', 'EVERY DAY.'], 100, 1080, a, [CREAM, GOLD])
    # stakes: a lifetime
    a = win(t, 11.25, 13.0, 0.08, 0.15)
    if a:
        tracked(d, 'IN A LIFETIME', 46, W / 2, 240, 10, DIM + (int(235 * a),), 'Medium')
        b = win(t, 11.45, 13.0, 0.06, 0.15)
        if b: tracked(d, '~1 YEAR', 170, W / 2, 300, 6, GOLD + (int(255 * b),))
        c = win(t, 11.9, 13.0, 0.1, 0.15)
        if c: lines(['WITH YOUR', 'EYES SHUT.'], 96, 1080, c)
    # why
    a = win(t, 13.05, 14.5, 0.1, 0.12)
    if a: lines(["SO WHY DON'T", 'YOU NOTICE?'], 92, 210, a, [CREAM, GOLD])
    # brain
    a = win(t, 14.75, 16.95, 0.1, 0.15)
    if a: lines(['YOUR BRAIN', 'EDITS OUT', 'EVERY BLINK.'], 92, 200, a, [CREAM, CREAM, GOLD])
    # mirror dare + CTA
    a = win(t, 17.05, 20.45)
    if a: lines(['TRY IT IN A MIRROR.'], 64, 200, a)
    a = win(t, 17.9, 20.45, 0.08, 0.12)
    if a: lines(["YOU'LL NEVER", 'CATCH ONE.'], 100, 300, a, [CREAM, GOLD])
    a = win(t, 20.5, 21.85, 0.1, 0.06)
    if a:
        lines(['FOLLOW @SLOWLIGHTTV'], 64, 220, a, GOLD)
        lines(['MORE THINGS YOUR', 'BRAIN HIDES FROM YOU.'], 52, 320, a, CREAM, weight='Medium')
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
