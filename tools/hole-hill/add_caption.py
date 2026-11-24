#!/usr/bin/env python3
"""Burn a persistent top caption (with gold highlight words) onto a frame folder, then build the video.
usage: add_caption.py FRAMES_DIR OUT_FRAMES_DIR AUDIO.wav OUT.mp4 [FPS=30] [DUR=14]"""
import sys, os, glob, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
fr, outd, audio, out = sys.argv[1:5]; FPS = int(sys.argv[5]) if len(sys.argv) > 5 else 30; DUR = float(sys.argv[6]) if len(sys.argv) > 6 else 14.0
os.makedirs(outd, exist_ok=True)
FONT = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf", 62)
LINES = [[("when you ", False), ("lie", True), (" to an ", False), ("overthinker", True)], [("in a relationship", False)]]
GOLD, WHITE = (255, 200, 84), (246, 244, 238)
def make_overlay(W, H):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); y = 232
    for ln in LINES:
        tot = sum(d.textlength(s, font=FONT) for s, _ in ln); x = (W - tot) / 2
        for s, hi in ln:
            col = GOLD if hi else WHITE
            d.text((x + 3, y + 4), s, font=FONT, fill=(0, 0, 0, 170)); d.text((x, y), s, font=FONT, fill=col + (255,), stroke_width=1, stroke_fill=col + (255,)); x += d.textlength(s, font=FONT)
        y += 80
    return lay
files = sorted(glob.glob(fr + "/f*.png")); im0 = Image.open(files[0]); W, H = im0.size; ov = make_overlay(W, H)
yy = np.arange(H, dtype=np.float32)[:, None, None]; grad = 0.62 + 0.38 * np.clip(yy / 460.0, 0, 1)
for f in files:
    o = os.path.join(outd, os.path.basename(f))
    if os.path.exists(o): continue
    a = np.asarray(Image.open(f).convert("RGB"), np.float32) * grad
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA"); img.alpha_composite(ov); img.convert("RGB").save(o, compress_level=1)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", outd + "/f%04d.png", "-i", audio, "-t", str(DUR), "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True); print("wrote", out)
