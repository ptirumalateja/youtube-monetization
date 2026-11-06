"""Text and UI layer for Friends in Every Group v6 (warm cafe). English only.

- Selfie shots: a phone-camera frame (corner brackets, shutter button), a white flash on the shutter, and the hook
  "FRIENDS IN / EVERY GROUP" (on from frame 0, punches on the flash).
- One caption per friend, in their own words, plus their counter: "5 MIN AWAY" ticking to "47 MIN LATE";
  "PHOTO #1" to "#47" in step with the flashes.
- Their number pops over their head (placed through the real camera, render.cjs meta); the end selfie shows all four
  with "WHICH ONE ARE YOU?" / "COMMENT 1-4".

  python3 overlay.py still IN.jpg T META.json OUT.jpg     overlay one rendered frame at time T (seconds)
  (compose.py imports draw() for the full video)
"""
import json, math, os, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
import sld_text
from sld_text import sstep, font, tracked, CREAM

TL = json.load(open(os.path.join(HERE, 'timeline.json')))
FPS = TL['fps']
W, H = 1080, 1920
RED = (216, 58, 46)
WHITE = (255, 255, 255)
SHOT = {name: (t0, (TL['shots'][i + 1][0] if i + 1 < len(TL['shots']) else TL['duration'])) for i, (t0, name) in enumerate(TL['shots'])}
SEAT_OF = {1: 'LATE', 2: 'PHOTO', 3: 'HUNGRY', 4: 'PAYS'}


def flash_k(t, times, decay=9.0):
    k = 0.0
    for ft in times:
        if t >= ft: k = max(k, math.exp(-(t - ft) * decay))
    return k


def blocks(t, m):
    out = []
    in_shot = lambda n: SHOT[n][0] <= t < SHOT[n][1]
    if in_shot('selfie'):
        punch = 1 + 0.18 * math.exp(-max(0, t - TL['flash0']) * 12) * (t >= TL['flash0'])
        out.append((['FRIENDS IN', 'EVERY GROUP'], int(80 * punch), 12, 230, 1.0))
    for t0, t1, lines in TL['captions']:
        if t0 <= t < t1:
            out.append((lines, 52, 7, 210, sstep(t0, t0 + 0.08, t)))
    if in_shot('late'):
        L = TL['late']; u = min(1.0, max(0.0, (t - L['min0']) / (L['min1'] - L['min0'])))
        mins = int(round(5 + 42 * u ** 1.6))
        out.append(([f'{mins} MIN AWAY' if mins < 47 else '47 MIN LATE'], 66, 10, 380, sstep(L['min0'] - 0.1, L['min0'], t)))
    if in_shot('photo'):
        fl = TL['photoFlashes']; k = sum(1 for f in fl if t >= f)
        if k:
            n = int(round(1 + 46 * ((k - 1) / (len(fl) - 1)) ** 1.6))
            out.append(([f'PHOTO #{n}'], 66, 10, 380, 1.0))
    if t >= TL['endCard']:
        out.append((['WHICH ONE', 'ARE YOU?'], 80, 12, 210, sstep(TL['endCard'], TL['endCard'] + 0.15, t)))
        out.append((['COMMENT 1-4'], 46, 10, 420, sstep(TL['endCard'] + 0.4, TL['endCard'] + 0.6, t)))
    return out


def ui(img, m, t):
    base = img.convert('RGBA'); layer = Image.new('RGBA', base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    selfie = m['shot'] in ('selfie', 'selfieEnd')
    if selfie:   # phone camera frame: corner brackets + shutter button
        a = 200; L = 90; pad = 60; w = 7
        for (x, y, sx, sy) in [(pad, 520, 1, 1), (W - pad, 520, -1, 1), (pad, 1640, 1, -1), (W - pad, 1640, -1, -1)]:
            d.line([(x, y), (x + sx * L, y)], fill=WHITE + (a,), width=w); d.line([(x, y), (x, y + sy * L)], fill=WHITE + (a,), width=w)
        d.ellipse((W / 2 - 55, 1700 - 55, W / 2 + 55, 1700 + 55), outline=WHITE + (220,), width=8)
        d.ellipse((W / 2 - 40, 1700 - 40, W / 2 + 40, 1700 + 40), fill=WHITE + (200,))
    # numbers: the friend being named gets theirs (big, red ring); the end selfie shows all four
    for n, seat in SEAT_OF.items():
        h = m['heads'][seat]
        if not h['on']: continue
        beat = TL['captions'][n - 1]
        active = beat[0] <= t < beat[1]
        show_end = m['shot'] == 'selfieEnd' and t >= TL['endCard'] + 0.15 * n
        if not (active or show_end): continue
        t_on = beat[0] + 0.25 if active else TL['endCard'] + 0.15 * n
        pop = 1 + 0.35 * math.exp(-max(0, t - t_on) * 10)
        r = (48 if active else 42) * pop
        # beside the head (upper right), never on the face
        x = h['x'] + h['r'] * 1.45 + r * 0.6; y = h['y'] - h['r'] * 0.9
        x, y = min(max(x, 70), W - 70), min(max(y, 520), 1560)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(18, 12, 10, 225), outline=(RED if active else CREAM) + (255,), width=7)
        f = font(int(r * 1.15), 'Bold'); s = str(n); tw = d.textlength(s, font=f)
        d.text((x - tw / 2, y - r * 0.78), s, font=f, fill=CREAM + (255,))
    base.alpha_composite(layer)
    # the shutter flash: a white frame flash on the selfies, a softer one on the photographer's burst
    k = max(flash_k(t, [TL['flash0'], TL['flashEnd']]) * 0.75, flash_k(t, TL['photoFlashes'], 14) * 0.3 * (m['shot'] == 'photo'))
    if k > 0.01:
        base.alpha_composite(Image.new('RGBA', base.size, WHITE + (int(255 * k),)))
    return base.convert('RGB')


def draw(img, t, m):
    return sld_text.draw(ui(img, m, t), blocks(t, m))


if __name__ == '__main__':
    if sys.argv[1] == 'still':
        t = float(sys.argv[3]); meta = json.load(open(sys.argv[4]))
        m = meta['frames'][min(round(t * FPS), len(meta['frames']) - 1)]
        draw(Image.open(sys.argv[2]).convert('RGB'), t, m).save(sys.argv[5], quality=94)
