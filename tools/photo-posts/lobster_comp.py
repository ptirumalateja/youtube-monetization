"""Lobster photo post: text and watermark over the OpenArt image (GPT Image 2, folder "Slow Light photo posts").

  python3 lobster_comp.py IN.png OUT.png

Resizes to 1080x1350 (4:5), lifts the deepest shadows so no edge reads as a black border, then the headline in the
What Are You Carrying v7 style: plain words in Inter Medium (white), the turn in Lora Italic (gold), a soft dark halo
for legibility. SLOW LIGHT watermark at the bottom. Prints edge brightness as a black-border check.
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1350
INTER = '/usr/share/fonts/opentype/inter/'
WHITE, GOLD = (248, 244, 236), (240, 196, 120)

src = Image.open(sys.argv[1]).convert('RGB')
r = max(W / src.width, H / src.height)
src = src.resize((round(src.width * r), round(src.height * r)), Image.LANCZOS)
x0, y0 = (src.width - W) // 2, (src.height - H) // 2
img = np.asarray(src.crop((x0, y0, x0 + W, y0 + H))).astype(np.float32) / 255
# warm the light a touch toward the series gold (highlights only; the deep water stays teal)
lum = img.mean(2, keepdims=True); w = np.clip((lum - 0.15) / 0.5, 0, 1)
img = img * (1 - w) + img * np.array([1.06, 1.0, 0.86], np.float32) * w
# lift the floor a little toward deep teal so no band is flat black (Facebook "black borders")
floor = np.array([0.035, 0.06, 0.075], np.float32)
img = 1 - (1 - img) * (1 - floor)
base = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).convert('RGBA')

lines = [('A lobster grows only', ImageFont.truetype(INTER + 'Inter-Medium.otf', 60), WHITE, 120),
         ('after its shell', ImageFont.truetype(INTER + 'Inter-Medium.otf', 60), WHITE, 200),
         ('gets too tight.', ImageFont.truetype(os.path.join(HERE, 'fonts', 'Lora_500Medium_Italic.ttf'), 78), GOLD, 276)]
mask = Image.new('L', (W, H), 0); lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
md, ld = ImageDraw.Draw(mask), ImageDraw.Draw(lay)
for text, f, col, y in lines:
    md.text((W / 2, y), text, font=f, fill=255, anchor='ma'); ld.text((W / 2, y), text, font=f, fill=col + (255,), anchor='ma')
halo = mask.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * 0.7))
base.alpha_composite(Image.merge('RGBA', (Image.new('L', (W, H), 4), Image.new('L', (W, H), 8), Image.new('L', (W, H), 12), halo)))
base.alpha_composite(lay)
# watermark
wm = Image.new('RGBA', (W, H), (0, 0, 0, 0)); wd = ImageDraw.Draw(wm); wf = ImageFont.truetype(INTER + 'Inter-SemiBold.otf', 22)
x = W / 2 - (sum(wd.textlength(c, font=wf) for c in 'SLOW LIGHT') + 9 * 9) / 2
for c in 'SLOW LIGHT':
    wd.text((x, H - 62), c, font=wf, fill=(255, 255, 255, 150)); x += wd.textlength(c, font=wf) + 9
base.alpha_composite(wm)
base.convert('RGB').save(sys.argv[2])
a = np.asarray(base.convert('L')).astype(float)
for n, b in [('top', a[:150]), ('bot', a[-200:]), ('left', a[:, :80]), ('right', a[:, -80:])]: print(n, round(b.mean(), 1), round(b.std(), 1))
