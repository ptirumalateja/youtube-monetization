import sys, math
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/user/youtube-monetization/tools/hole-hill")
import vinyl as V
out = sys.argv[1]; pose = sys.argv[2] if len(sys.argv) > 2 else "guard"; mood = sys.argv[3] if len(sys.argv) > 3 else "determined"
C = np.array([0, 500, 2000], np.float32); T = np.array([0, 470, 0], np.float32)
r, u, f = V.lookat(C, T)
img, mask = V.render(V.POSES[pose], mood, C, r, u, f)
ys, xs = np.nonzero(mask); b = (max(0, xs.min() - 150), max(0, ys.min() - 120), min(V.W, xs.max() + 150), min(V.H, ys.max() + 120))
ours = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).crop(b)
ref = Image.open("/tmp/claude-0/-home-user-youtube-monetization/a23e2797-2c3e-5eef-b6ce-d7544fada057/images/1.png").convert("RGB")
hh = 1000
ref = ref.resize((int(ref.width * hh / ref.height), hh), Image.LANCZOS); ours = ours.resize((int(ours.width * hh / ours.height), hh), Image.LANCZOS)
s = Image.new("RGB", (ref.width + ours.width + 20, hh), (200, 200, 205)); s.paste(ref, (0, 0)); s.paste(ours, (ref.width + 20, 0)); s.save(out); print("wrote", out)
