# Draws the info layer (tag, NET WORTH counter, hook, captions, red marker) over the rendered frames and muxes the sound.
# python3 overlay.py [out.mp4]   reads output/frames/*.jpg, output/meta.json, output/sound.wav
import json, math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(ROOT, 'output')
TL = json.load(open(os.path.join(ROOT, 'timeline.json'))); META = json.load(open(os.path.join(OUT, 'meta.json')))
FR = META['frames']; FPS = TL['fps']; N = len(FR); W, H = 1080, 1920
BOLD = '/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf'; SANS = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
font = lambda p, s: ImageFont.truetype(p, s)
F_TAG, F_LBL, F_NUM, F_HOOK, F_CAP, F_END = font(SANS, 26), font(BOLD, 27), font(BOLD, 84), font(BOLD, 60), font(BOLD, 56), font(BOLD, 78)
CREAM = (240, 232, 214); RED = (214, 62, 48); BLACK = (0, 0, 0)
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

HOOK = ['EVERY COIN', 'LIFTED HIM HIGHER.']; CAP = ['HE COULD REACH', 'ANYTHING.']; END = 'EXCEPT HER.'
def draw(i):
    t = i / FPS; m = FR[i]
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    text(d, (W / 2, 168), 'SLOW LIGHT', F_TAG, 0.6, stroke=3, spacing=9)
    text(d, (W / 2, 222), 'NET WORTH', F_LBL, 0.9, stroke=4, spacing=6)
    text(d, (W / 2, 278), '${:,}'.format(m['worth']), F_NUM, 1.0, stroke=6)
    # hook: line one types from frame 0, line two follows; done by 1.3 s
    a = 1 - sstep(4.4, 4.8, t)
    text(d, (W / 2, 420), typed(HOOK[0], t, 0.0, 0.45), F_HOOK, a)
    text(d, (W / 2, 492), typed(HOOK[1], t, 0.45, 1.3), F_HOOK, a)
    # the gap: captions sit in the empty space between him and her in the wide shot
    a = fade(t, 13.4, 15.3, 0.15, 0.3)
    text(d, (W / 2, 880), typed(CAP[0], t, 13.4, 13.95), F_CAP, a)
    text(d, (W / 2, 948), typed(CAP[1], t, 13.95, 14.3), F_CAP, a)
    a = fade(t, 15.35, 18.0, 0.1, 0.18)
    text(d, (W / 2, 930), typed(END, t, 15.35, 15.8), F_END, a, stroke=7)
    # red marker ring on her in the wide shot
    a = fade(t, 13.9, 16.25, 0.25, 0.25)
    if a > 0.01:
        x, y = m['herHead'][0] * W, m['herHead'][1] * H + 30; r = 58 + 4 * math.sin(t * 6.0)
        d.ellipse((x - r, y - r, x + r, y + r), outline=RED + (int(235 * a),), width=6)
    return lay

def main():
    out = os.path.join(OUT, sys.argv[1] if len(sys.argv) > 1 else 'the-higher-he-got.mp4')
    ff = subprocess.Popen(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
        '-i', os.path.join(OUT, 'sound.wav'), '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p',
        '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
        '-t', str(TL['duration']), '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for i in range(N):
        base = Image.open(os.path.join(OUT, 'frames', f'f{i:05d}.jpg')).convert('RGB')
        if base.size != (W, H): base = base.resize((W, H), Image.LANCZOS)
        img = Image.alpha_composite(base.convert('RGBA'), draw(i)).convert('RGB')
        ff.stdin.write(img.tobytes())
    ff.stdin.close(); assert ff.wait() == 0; print('wrote', out)

if __name__ == '__main__': main()
