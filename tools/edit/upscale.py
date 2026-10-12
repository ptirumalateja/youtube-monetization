"""Real-ESRGAN x4 upscale (CPU, tiled) -> resize to a target width. usage: upscale.py <weights.pth> <out_width> <in.png> [...]
Writes <in>_up.png next to each input."""
import sys, numpy as np, torch
from PIL import Image
from spandrel import ModelLoader
torch.set_num_threads(4)
model = ModelLoader().load_from_file(sys.argv[1]).eval()
OW = int(sys.argv[2]); T, P = 192, 16
for path in sys.argv[3:]:
    im = np.asarray(Image.open(path).convert("RGB"), np.float32) / 255
    h, w = im.shape[:2]; s = model.scale
    out = np.zeros((h * s, w * s, 3), np.float32)
    x = torch.from_numpy(im).permute(2, 0, 1)[None]
    with torch.inference_mode():
        for y0 in range(0, h, T):
            for x0 in range(0, w, T):
                ya, xa = max(y0 - P, 0), max(x0 - P, 0); yb, xb = min(y0 + T + P, h), min(x0 + T + P, w)
                o = model(x[:, :, ya:yb, xa:xb])[0].permute(1, 2, 0).clamp(0, 1).numpy()
                ty, tx = (y0 - ya) * s, (x0 - xa) * s
                th, tw = (min(y0 + T, h) - y0) * s, (min(x0 + T, w) - x0) * s
                out[y0 * s:y0 * s + th, x0 * s:x0 * s + tw] = o[ty:ty + th, tx:tx + tw]
    img = Image.fromarray((out * 255).astype(np.uint8))
    img = img.resize((OW, round(OW * h / w)), Image.LANCZOS)
    img.save(path.rsplit(".", 1)[0] + "_up.png"); print("done", path, img.size, flush=True)
