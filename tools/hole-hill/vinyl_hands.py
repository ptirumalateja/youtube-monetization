import sys, math
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/user/youtube-monetization/tools/hole-hill")
import vinyl as V
out = sys.argv[1]
V.RES["k"] = 1
C = np.array([0, 560, 1000], np.float32); T = np.array([0, 560, 0], np.float32)
r, u, f = V.lookat(C, T)
img, mask = V.render(V.POSES["guard"], "determined", C, r, u, f)
pil = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
ys, xs = np.nonzero(mask)
cx, cy = int(xs.mean()), int(ys.mean())
ours = pil.crop((cx - 330, cy - 320, cx + 330, cy + 380)).resize((660, 700), Image.LANCZOS)
ref = Image.open("/tmp/claude-0/-home-user-youtube-monetization/a23e2797-2c3e-5eef-b6ce-d7544fada057/images/1.png").convert("RGBA")
bgw = Image.new("RGBA", ref.size, (255, 255, 255, 255)); bgw.alpha_composite(ref); ref = bgw.convert("RGB")
refh = ref.crop((420, 700, 900, 1230)).resize((660, 700 * 1), Image.LANCZOS)
s = Image.new("RGB", (660 * 2 + 20, 700), (200, 200, 205)); s.paste(refh, (0, 0)); s.paste(ours, (680, 0)); s.save(out); print("wrote", out)
