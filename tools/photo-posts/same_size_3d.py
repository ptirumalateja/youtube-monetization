"""Same Size, 3D version: the corridor render plus one stickman sprite pasted twice at EXACTLY the same pixel height.

  python3 same_size_3d.py CORRIDOR.png FIGURE.png OUT.png

CORRIDOR.png (+ .json with the floor spots) and FIGURE.png (+ .json with feet/head) come from corridor/still.cjs:
  QS=mode=corridor node corridor/still.cjs CORRIDOR.png 2160 2700
  QS=mode=figure   node corridor/still.cjs FIGURE.png 1200 2400
Each copy gets a contact shadow and a faint floor reflection; the far one picks up a little of the corridor haze.
Text in Inter Medium + Lora Italic (fonts/, OFL). Output 1080x1350 (4:5).
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
cor = Image.open(sys.argv[1]).convert('RGBA'); W, H = cor.size; S = W / 1080
spots = json.load(open(sys.argv[1] + '.json'))
fig = Image.open(sys.argv[2]).convert('RGBA'); fb = json.load(open(sys.argv[2] + '.json'))
a = np.asarray(fig)[..., 3]; ys, xs = np.nonzero(a > 8)
foot_y = fb['foot'][1]; top = ys.min(); x0, x1 = xs.min(), xs.max()
spr = fig.crop((x0, top, x1 + 1, int(foot_y) + 1))           # tight crop, bottom = the soles
SPR_H = int(360 * S)                                # the one height both copies get (px, at render scale)
spr = spr.resize((round(spr.width * SPR_H / spr.height), SPR_H), Image.LANCZOS)
HAZE = np.array([26, 22, 18], np.float32)

def place(foot, haze=0.0, refl=0.22, back=0.0):
    fx, fy = foot; x, y = int(fx - spr.width / 2), int(fy - spr.height)
    # contact shadow
    sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).ellipse([fx - spr.width * 0.55, fy - 8 * S, fx + spr.width * 0.55, fy + 10 * S], fill=150)
    cor.alpha_composite(Image.merge('RGBA', (Image.new('L', (W, H), 0),) * 3 + (sh.filter(ImageFilter.GaussianBlur(7 * S)),)))
    s = np.asarray(spr).astype(np.float32).copy()
    if haze: s[..., :3] = s[..., :3] * (1 - haze) + HAZE * haze
    if back:   # backlit by the doorway: darker body, a gold rim where the light wraps the edges
        al = s[..., 3] / 255
        inner = np.asarray(Image.fromarray(s[..., 3].astype(np.uint8)).filter(ImageFilter.MinFilter(int(9 * S) | 1)).filter(ImageFilter.GaussianBlur(5 * S))).astype(np.float32) / 255
        rim = (np.clip(al - inner, 0, 1) ** 1.4 * 0.75)[..., None]                      # a soft wrap of light, not an outline
        s[..., :3] = s[..., :3] * (1 - 0.45 * back) * (1 - rim) + np.array([255, 205, 130], np.float32) * rim * back + s[..., :3] * rim * (1 - back)
    # floor reflection: flipped, darker, fading out
    r = s[::-1].copy(); fade = np.linspace(refl, 0, r.shape[0])[:, None] ** 1.4; r[..., 3] *= fade / max(refl, 1e-6) * refl; r[..., :3] *= 0.7
    rimg = Image.fromarray(np.clip(r, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5 * S))
    cor.alpha_composite(rimg, (x, int(fy)))
    cor.alpha_composite(Image.fromarray(np.clip(s, 0, 255).astype(np.uint8)), (x, y))
    return x, y

far = place(spots['far']['foot'], haze=0.1, refl=0.18, back=1.0)
near = place(spots['near']['foot'], haze=0.0, refl=0.25)
img = cor

INTER = '/usr/share/fonts/opentype/inter/'
sans = lambda s: ImageFont.truetype(INTER + 'Inter-Medium.otf', int(s * S))
ital = lambda s: ImageFont.truetype(os.path.join(HERE, 'fonts', 'Lora_500Medium_Italic.ttf'), int(s * S))
WHITE, GOLD, CREAM = (248, 244, 236), (240, 196, 120), (237, 230, 214)
txt = Image.new('RGBA', (W, H), (0, 0, 0, 0)); td = ImageDraw.Draw(txt); mask = Image.new('L', (W, H), 0); md = ImageDraw.Draw(mask)
def put(s_, f, col, x, y, anchor='ma', a=255):
    td.text((x, y), s_, font=f, fill=col + (a,), anchor=anchor); md.text((x, y), s_, font=f, fill=a, anchor=anchor)
put('Which one is bigger?', sans(64), WHITE, W / 2, 86 * S)
put('tomorrow', ital(36), GOLD, far[0] + spr.width + 14 * S, far[1] + spr.height * 0.4, 'lm', 235)
put('today', ital(36), CREAM, near[0] - 14 * S, near[1] + spr.height * 0.4, 'rm', 235)
put('Same size.', sans(46), WHITE, W / 2, H - 256 * S)
put("Tomorrow's problems just look", ital(46), GOLD, W / 2, H - 198 * S)
put('bigger from here.', ital(46), GOLD, W / 2, H - 142 * S)
halo = mask.filter(ImageFilter.GaussianBlur(16 * S)).point(lambda v: min(255, int(v * 1.0)))
img.alpha_composite(Image.merge('RGBA', (Image.new('L', (W, H), 8), Image.new('L', (W, H), 7), Image.new('L', (W, H), 6), halo)))
img.alpha_composite(txt)
wm = Image.new('RGBA', (W, H), (0, 0, 0, 0)); wd = ImageDraw.Draw(wm); wf = sans(22)
x = W / 2 - (sum(wd.textlength(c, font=wf) for c in 'SLOW LIGHT') + 9 * 9 * S) / 2
for c in 'SLOW LIGHT':
    wd.text((x, H - 56 * S), c, font=wf, fill=(255, 255, 255, 140)); x += wd.textlength(c, font=wf) + 9 * S
img.alpha_composite(wm)
out = img.convert('RGB').resize((1080, 1350), Image.LANCZOS); out.save(sys.argv[3])
print('both figures', spr.size, 'px at render scale ->', round(spr.height / S), 'px tall in the 1080x1350 post')
g = np.asarray(out.convert('L')).astype(float)
for n, b in [('top', g[:150]), ('bot', g[-200:]), ('left', g[:, :80]), ('right', g[:, -80:])]: print(n, round(b.mean(), 1), round(b.std(), 1))
