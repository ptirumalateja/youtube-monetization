#!/usr/bin/env python3
"""V6 stills: turn Teja's uploads (paper figures, Commons photos, Flow stills) into 1080x1920 frames for build4.
Landscape photos/figures sit sharp on a blurred, darkened copy of themselves; figures get a small source line.
Usage: prep6.py UPLOAD_DIR OUT_DIR"""
import os, sys
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageEnhance
U, OUT = sys.argv[1:3]; os.makedirs(OUT, exist_ok=True)
W, H = 1080, 1920
FONT = '/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf'
SRC = 'Harney et al. 2019, Nature Communications · CC BY 4.0'

def card(im, out, box=(1080, 1300), cy=820, label=None, border=0, ar=None, ax=.5):
    im = im.convert('RGB')
    if ar:                                   # crop to width/height = ar first (bigger on screen)
        w = int(im.height * ar); x0 = int((im.width - w) * ax); im = im.crop((x0, 0, x0 + w, im.height))
    bg = im.copy(); s = max(W / bg.width, H / bg.height); bg = bg.resize((int(bg.width * s) + 1, int(bg.height * s) + 1))
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(38))).enhance(0.55)
    s = min(box[0] / im.width, box[1] / im.height); fg = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    x, y = (W - fg.width) // 2, int(cy - fg.height / 2)
    if border:
        d = ImageDraw.Draw(bg); d.rectangle([x - border, y - border, x + fg.width + border, y + fg.height + border], fill=(250, 250, 250))
    bg.paste(fg, (x, y))
    if label:
        d = ImageDraw.Draw(bg); f = ImageFont.truetype(FONT, 26)
        d.text((W // 2, y + fg.height + border + 30), label, font=f, fill=(235, 235, 235), anchor='mt', stroke_width=3, stroke_fill=(20, 20, 20))
    bg.save(f'{OUT}/{out}.jpg', quality=94)

f = lambda n: Image.open(os.path.join(U, n))
fig1, fig2, fig3 = f('4f52c76d-image.webp'), f('aa6164b3-image.webp'), f('7fe147fe-image.webp')
card(fig1.crop((1100, 60, 2045, 675)), 'bones_field', box=(1080, 1400), label=SRC, ar=.8, ax=.45)              # Fig 1b: real bones in snow
card(fig1.crop((1090, 740, 2045, 1381)), 'lake_pano', box=(1080, 1400), label=SRC, ar=.8, ax=.55)              # Fig 1c: Roopkund lake
card(fig2.crop((175, 633, 861, 1040)), 'pca_greek', box=(1050, 1200), label=SRC, border=14)   # Fig 2b: Roopkund_B beside Greek/Cretan
card(fig3.crop((20, 20, 800, 900)), 'dates_full', box=(1000, 1250), label=SRC, border=14)     # Fig 3a: two date clusters
card(fig3.crop((20, 60, 440, 860)), 'dates_800', box=(1000, 1350), label=SRC, border=14)
card(fig3.crop((420, 60, 800, 860)), 'dates_1800', box=(1000, 1350), label=SRC, border=14)
card(f('5d88d5b7-image.jpg'), 'rajjat', box=(1080, 1400), ar=.8, ax=.5)                                       # Nanda Devi Raj Jat crowd
for n, o in (('0bc54773-image.jpg', 'skull_ice'), ('4496f99a-image.jpg', 'travellers'), ('91c369d7-image.jpg', 'temple')):
    im = f(n).convert('RGB'); s = max(W / im.width, H / im.height); im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    im.crop(((im.width - W) // 2, (im.height - H) // 2, (im.width - W) // 2 + W, (im.height - H) // 2 + H)).save(f'{OUT}/{o}.jpg', quality=94)
print('ok')
