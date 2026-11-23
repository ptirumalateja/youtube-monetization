import sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/user/youtube-monetization/tools/hole-hill")
import vinyl as V
cases = [("guard", "determined", "GRIT", 0.25), ("dig", "strain", "DIGGING", 0.95), ("fall", "shocked", "FALLING IN", 0.0), ("triumph", "joy", "ON THE HILL", 0.0)]
T = np.array([0, 470, 0], np.float32)
pw, ph = 360, 640
sheet = Image.new("RGB", (pw * 4, ph + 56), (244, 244, 246)); d = ImageDraw.Draw(sheet)
fnt = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf", 22)
for i, (pose, mood, label, th) in enumerate(cases):
    D_ = 1500.0; C = np.array([D_ * math.sin(th), 520, D_ * math.cos(th)], np.float32); r, u, f = V.lookat(C, T)
    img, mask = V.render(V.POSES[pose], mood, C, r, u, f)
    pil = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).resize((pw, ph), Image.LANCZOS)
    sheet.paste(pil, (i * pw, 56)); d.text((i * pw + 14, 16), label, font=fnt, fill=(30, 30, 40))
sheet.save(sys.argv[1]); print("wrote", sys.argv[1])
