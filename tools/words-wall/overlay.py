"""Text layer for Their Words Became His Wall.

One caption for the whole reel, unchanged from frame 0 to the end (Teja, 3 Nov):
"Let their words become / the bricks of your success", sentence case, clean light sans (Inter), centred above the scene.
"SLOW LIGHT" watermark bottom centre at 35%.

  python3 overlay.py still IN.jpg T OUT.jpg     overlay one rendered frame at time T (compose.py imports draw())
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
import sld_text

TL = json.load(open(os.path.join(HERE, 'timeline.json')))
W, H = 1080, 1920
LINES = ['Let their words become', 'the bricks of your success']
F = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Regular.otf', 54)
Y0, LH = 470, 72


def draw(img, t):
    img = sld_text.draw(img, [])                       # resize + the SLOW LIGHT watermark only
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    for i, line in enumerate(LINES):
        d.text((W / 2, Y0 + i * LH), line, font=F, fill=(244, 240, 232, 255), anchor='mm')
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sh.putalpha(layer.getchannel('A').filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * 0.55)))
    base = img.convert('RGBA'); base.alpha_composite(sh); base.alpha_composite(layer)
    return base.convert('RGB')


if __name__ == '__main__' and sys.argv[1] == 'still':
    draw(Image.open(sys.argv[2]).convert('RGB'), float(sys.argv[3])).save(sys.argv[4], quality=94)
