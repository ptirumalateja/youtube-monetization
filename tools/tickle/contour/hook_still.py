#!/usr/bin/env python3
"""Style-C test frame: contour-line hand (cream) with a teal predicted ghost leading it, flat red target, dark navy ground.
usage: python3 hook_still.py <contours.json> <out.png>"""
import json, sys
from PIL import Image, ImageDraw, ImageFilter
W, H = 1080, 1920
data = json.load(open(sys.argv[1])); S = 1.45
def layer(dx, dy, color, width, alpha, glow=0):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for p in data["polys"]:
        pts = [(x * S + dx, y * S + dy) for x, y in p["pts"]]
        d.line(pts, fill=color + (alpha,), width=width, joint="curve")
    if glow:
        g = im.filter(ImageFilter.GaussianBlur(glow)); out = Image.alpha_composite(g, im); return out
    return im
bg = Image.new("RGBA", (W, H), (9, 13, 19, 255)); d = ImageDraw.Draw(bg)
for x in range(0, W, 60): d.line([(x, 300), (x, 1120)], fill=(232, 228, 208, 10), width=1)
for y in range(300, 1121, 60): d.line([(0, y), (W, y)], fill=(232, 228, 208, 10), width=1)
# real hand low-left, predicted ghost already ahead near the target
hand = layer(-150, 380, (232, 228, 208), 2, 235, glow=3)
ghost = layer(150, 70, (111, 214, 203), 2, 210, glow=5)
img = Image.alpha_composite(bg, ghost); img = Image.alpha_composite(img, hand)
# flat target (not a portal): two offset ellipses
tx, ty = 870, 560; t = Image.new("RGBA", (W, H), (0, 0, 0, 0)); td = ImageDraw.Draw(t)
td.ellipse((tx - 62, ty - 100, tx + 62, ty + 100), outline=(214, 62, 48, 255), width=14)
td.ellipse((tx - 30, ty - 56, tx + 30, ty + 56), fill=(214, 62, 48, 255))
img = Image.alpha_composite(img, t.filter(ImageFilter.GaussianBlur(10)))
img = Image.alpha_composite(img, t)
vg = Image.radial_gradient("L").resize((W, H)); vg = vg.point(lambda v: int(v * 0.7)); black = Image.new("RGBA", (W, H), (0, 0, 0, 255)); img = Image.composite(black, img, vg)
img.convert("RGB").save(sys.argv[2]); print("saved")
