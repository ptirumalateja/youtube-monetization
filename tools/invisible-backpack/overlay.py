# Draws the info layer (tag, hook, reveal title, rock labels that sharpen into focus, the ROCK -> STEP counter, captions,
# end lines) over the rendered frames and muxes the sound.
# python3 overlay.py [out.mp4] [--silent]   reads output/frames/*.jpg, output/meta.json, output/sound.wav
#   --silent writes the _music-ready cut: same picture, a silent audio track
import json, math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(ROOT, 'output')
TL = json.load(open(os.path.join(ROOT, 'timeline.json'))); META = json.load(open(os.path.join(OUT, 'meta.json')))
FR = META['frames']; EV = META['events']; FPS = TL['fps']; N = len(FR); W, H = 1080, 1920
BOLD = '/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf'; SANS = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'; ARROW = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font = lambda p, s: ImageFont.truetype(p, s)
F_TAG, F_HOOK, F_TITLE, F_LBL, F_CNT, F_CAP, F_END, F_SUB, F_HANDLE = (font(SANS, 26), font(BOLD, 62), font(BOLD, 66), font(BOLD, 41), font(BOLD, 60),
                                                                      font(BOLD, 58), font(BOLD, 64), font(BOLD, 44), font(SANS, 30))
CREAM = (240, 232, 214); RED = (214, 62, 48); GOLD = (240, 186, 92); BLACK = (0, 0, 0)
LABELS = TL['labels']; FOCUS = EV['focus']
clamp = lambda x, a=0.0, b=1.0: max(a, min(b, x))
def sstep(a, b, x): t = clamp((x - a) / (b - a)); return t * t * (3 - 2 * t)
def fade(t, a, b, fin=0.2, fout=0.3): return sstep(a, a + fin, t) * (1 - sstep(b - fout, b, t))

def text(d, xy, s, f, a, fill=CREAM, stroke=5, spacing=0, anchor='mm'):
    if a <= 0.01 or not s: return
    col = fill + (int(255 * a),); sc = BLACK + (int(235 * a),)
    if spacing:
        widths = [f.getlength(ch) + spacing for ch in s]; x = xy[0] - (sum(widths) - spacing) / 2
        for ch, w in zip(s, widths): d.text((x, xy[1]), ch, font=f, fill=col, stroke_width=stroke, stroke_fill=sc, anchor='lm'); x += w
    else: d.text(xy, s, font=f, fill=col, stroke_width=stroke, stroke_fill=sc, anchor=anchor)

def typed(s, t, t0, t1):
    if t < t0: return ''
    n = max(1, math.ceil(len(s) * clamp((t - t0) / (t1 - t0))))     # never a negative or zero slice
    return s[:n]

def label(lay, xy, s, a, blur):
    # a rock label: drawn on its own small layer so it can be blurred until the rock turns into focus
    if a <= 0.01: return
    w = int(F_LBL.getlength(s)) + 60; h = 80; tile = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    text(ImageDraw.Draw(tile), (w / 2, h / 2), s, F_LBL, a, stroke=5)
    if blur > 0.3: tile = tile.filter(ImageFilter.GaussianBlur(blur))
    x, y = int(xy[0] - w / 2), int(xy[1] - h / 2); x = max(-20, min(W - w + 20, x))
    lay.alpha_composite(tile, (max(0, x), max(0, y)), (max(0, -x), max(0, -y)))

HOOK = ['WHY DOES IT FEEL', 'SO HEAVY?']; TITLE = ['THE INVISIBLE', 'BACKPACK']; DEC = ["YOU DON'T HAVE TO", 'THROW IT AWAY.']
END = ['YOUR BAGGAGE IS', 'YOUR FOUNDATION.']
P1 = [c['p1'] for c in EV['cycles']]
def draw(i):
    t = i / FPS; m = FR[i]
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    text(d, (W / 2, 168), 'SLOW LIGHT', F_TAG, 0.6, stroke=3, spacing=9)
    # hook: typed from frame 0, done by 1.3 s, gone in the flash
    a = 1 - sstep(1.92, 2.02, t)
    text(d, (W / 2, 300), typed(HOOK[0], t, 0.0, 0.75), F_HOOK, a)
    text(d, (W / 2, 374), typed(HOOK[1], t, 0.75, 1.3), F_HOOK, a)
    # reveal title
    a = fade(t, 2.15, 4.0, 0.1, 0.25)
    text(d, (W / 2, 272), typed(TITLE[0], t, 2.15, 2.6), F_TITLE, a, fill=CREAM)
    text(d, (W / 2, 348), typed(TITLE[1], t, 2.6, 2.95), F_TITLE, a, fill=GOLD)
    # rock labels: on the rocks, blurred until each rock turns into focus (4.15 s + 0.4 s each), gone at the decision
    a = fade(t, 2.45, 7.0, 0.3, 0.2)
    if a > 0.01:
        for k, (s, r) in enumerate(zip(LABELS, m['rocks'])):
            if not r[2]: continue
            f = FOCUS[k]; blur = 9.0 * (1 - sstep(f - 0.12, f + 0.12, t))
            x, y = r[0] * W, r[1] * H - (14 if m['shot'] == 1 else 0)
            label(lay, (x, y), s, a * (0.5 + 0.5 * sstep(f - 0.12, f + 0.12, t)), blur)
    # the decision
    a = fade(t, 7.25, 9.0, 0.1, 0.25)
    text(d, (W / 2, 300), typed(DEC[0], t, 7.25, 7.75), F_CAP, a)
    text(d, (W / 2, 372), typed(DEC[1], t, 7.75, 8.1), F_CAP, a)
    # monotonic counter: ROCK k -> [STEP k]
    k = m['counter']; a = fade(t, P1[0], 14.95, 0.08, 0.3)
    if k >= 1 and a > 0.01:
        pop = 1 + 0.12 * math.exp(-max(0.0, t - P1[k - 1]) / 0.12)
        fC = font(BOLD, int(60 * pop)); left = f'ROCK {k} →'; right = f'STEP {k}'
        wl, wr = fC.getlength(left), fC.getlength(right); pad = 18; total = wl + 22 + wr + 2 * pad; x0 = W / 2 - total / 2; y = 290
        text(d, (x0, y), left, fC, a, anchor='lm')
        cx0 = x0 + wl + 22; d.rounded_rectangle((cx0, y - 42 * pop, cx0 + wr + 2 * pad, y + 42 * pop), radius=10, fill=RED + (int(235 * a),))
        text(d, (cx0 + pad, y), right, fC, a, stroke=3, anchor='lm')
    a = fade(t, 12.35, 14.95, 0.1, 0.3)
    text(d, (W / 2, 392), typed('BUILD WITH IT.', t, 12.35, 12.75), F_CAP, a, fill=GOLD)
    # payoff
    a = sstep(15.3, 15.4, t)
    text(d, (W / 2, 250), typed(END[0], t, 15.3, 15.75), F_END, a)
    text(d, (W / 2, 326), typed(END[1], t, 15.75, 16.2), F_END, a, fill=GOLD)
    text(d, (W / 2, 1440), typed('One rock a day.', t, 16.35, 16.8), F_SUB, sstep(16.35, 16.45, t))
    text(d, (W / 2, 1506), 'slowlighttv', F_HANDLE, 0.85 * sstep(16.85, 17.15, t), stroke=3, spacing=4)
    return lay

def main():
    args = [x for x in sys.argv[1:] if not x.startswith('--')]; silent = '--silent' in sys.argv
    prev = -1
    for f, m in enumerate(FR):
        if m['counter'] < prev: raise SystemExit(f'counter goes backwards at frame {f}')
        prev = m['counter']
    out = os.path.join(OUT, args[0] if args else 'invisible-backpack.mp4')
    audio = ['-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo'] if silent else ['-i', os.path.join(OUT, 'sound.wav')]
    ff = subprocess.Popen(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
        *audio, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p',
        '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
        '-t', str(TL['duration']), '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for i in range(N):
        base = Image.open(os.path.join(OUT, 'frames', f'f{i:05d}.jpg')).convert('RGB')
        if base.size != (W, H): base = base.resize((W, H), Image.LANCZOS)
        img = Image.alpha_composite(base.convert('RGBA'), draw(i)).convert('RGB')
        ff.stdin.write(img.tobytes())
    ff.stdin.close(); assert ff.wait() == 0; print('wrote', out)

if __name__ == '__main__': main()
