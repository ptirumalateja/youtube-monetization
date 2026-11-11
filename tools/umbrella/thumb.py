"""Cover for the umbrella reel: last shot (f00300) + big CHECKERS OR CHESS? in the sky, inside the IG 4:5 grid crop.
  python3 thumb.py FRAME.jpg OUT.jpg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'slow-light-dark-common'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageEnhance
from overlay import text_block, CREAM, GOLD
im = Image.open(sys.argv[1]).convert('RGB')
im = ImageEnhance.Contrast(ImageEnhance.Brightness(im).enhance(1.12)).enhance(1.08)
W, H = im.size; z = 1.08; cw, ch = int(W / z), int(H / z); cx, cy = W // 2 + 20, int(H * 0.53)
im = im.crop((cx - cw // 2, cy - ch // 2, cx + cw // 2, cy + ch // 2)).resize((W, H), Image.LANCZOS)
im = text_block(im, [('CHECKERS', 112, 10, 300, CREAM, 1, 'ExtraBold'), ('OR CHESS?', 112, 10, 425, GOLD, 1, 'ExtraBold')])
im.save(sys.argv[2], quality=94)
