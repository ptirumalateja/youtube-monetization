#!/usr/bin/env python3
"""Remove a static semi-transparent corner sparkle (inverse alpha + inpaint on the edge) and move a burned-in caption lower (inpaint it out, redraw the same pixels lower).
usage: fix_clip.py IN.mp4 OUT.mp4 [DY=88]      (tuned for the 720x1280 'sitting with thoughts' clip; sparkle at (600,1160), caption band y 105-152)"""
import sys, os, subprocess, tempfile, glob
import numpy as np, cv2
src, dst = sys.argv[1], sys.argv[2]; DY = int(sys.argv[3]) if len(sys.argv) > 3 else 88
tmp = tempfile.mkdtemp(prefix="clipfix_"); fi = os.path.join(tmp, "in"); fo = os.path.join(tmp, "out"); os.makedirs(fi); os.makedirs(fo)
fps = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate", "-of", "csv=p=0", src]).decode().strip()
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, os.path.join(fi, "%04d.png")], check=True)
files = sorted(glob.glob(fi + "/*.png")); frames = [cv2.imread(f) for f in files]; H, W = frames[0].shape[:2]
# sparkle: measure its exact shape and opacity from the clip itself (static, semi-transparent white), then undo the alpha composite
cx, cy = 600, 1160; bx0, by0 = cx - 50, cy - 50
gs = np.mean([cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32) for f in frames[:min(60, len(frames))]], 0)
med = cv2.medianBlur(np.clip(gs, 0, 255).astype(np.uint8), 61).astype(np.float32); lift = (gs - med)[by0:by0 + 100, bx0:bx0 + 100]
m = (lift > 14).astype(np.uint8); m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
_, lab = cv2.connectedComponents(m); m = (lab == lab[50, 50]).astype(np.uint8)
inv = (m * 255).copy(); cv2.floodFill(inv, np.zeros((102, 102), np.uint8), (0, 0), 255); m = (m | (cv2.bitwise_not(inv) > 0)).astype(np.uint8)
alpha = float(np.clip(lift[m > 0].mean() / (255 - med[by0:by0 + 100, bx0:bx0 + 100][m > 0].mean()), 0.1, 0.7)); print("sparkle alpha ~", round(alpha, 3), "area", int(m.sum()))
star = np.zeros((H, W), np.uint8); star[by0:by0 + 100, bx0:bx0 + 100] = m
core = cv2.erode(star, np.ones((5, 5), np.uint8)); rim = ((cv2.dilate(star, np.ones((5, 5), np.uint8)) - core) > 0).astype(np.uint8) * 255
W_ = core.astype(np.float32)[..., None]
# caption: band + top-hat to extract thin bright strokes
x0, x1, y0, y1 = 100, 650, 100, 156
k_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
def tophat(f):
    g = cv2.cvtColor(f[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY); return cv2.morphologyEx(g, cv2.MORPH_TOPHAT, k_open).astype(np.float32)
peak = np.percentile(np.max(np.stack([tophat(f) for f in frames[len(frames) // 2:len(frames) // 2 + 4]]), 0), 99.5); print("caption peak", round(float(peak), 1))
TXT = np.array([226, 228, 232], np.float32)   # BGR-ish near-white
for i, f in enumerate(frames):
    o = f.copy()
    # 1) sparkle: invert the alpha composite
    o32 = o.astype(np.float32); rec = np.clip((o32 - alpha * 255) / (1 - alpha), 0, 255)
    o = np.clip(o32 * (1 - W_) + rec * W_, 0, 255).astype(np.uint8)
    o = cv2.inpaint(o, rim, 3, cv2.INPAINT_TELEA)   # antialiased rim: fill from the surroundings
    # 2) caption: alpha from top-hat, remove, redraw lower
    th = tophat(f); al = np.clip((th - 10) / max(peak - 10, 1), 0, 1)
    mask = np.zeros((H, W), np.uint8); mm = (al > 0.05).astype(np.uint8) * 255; mm = cv2.dilate(mm, np.ones((5, 5), np.uint8)); mask[y0:y1, x0:x1] = mm
    cl = cv2.inpaint(o, mask, 4, cv2.INPAINT_TELEA).astype(np.float32)
    A = np.zeros((H, W), np.float32); A[y0:y1, x0:x1] = cv2.GaussianBlur(al, (0, 0), 0.6)
    As = np.zeros_like(A); As[y0 + DY:y1 + DY] = A[y0:y1]
    cl = cl * (1 - As[..., None]) + TXT * As[..., None]
    cv2.imwrite(os.path.join(fo, os.path.basename(files[i])), np.clip(cl, 0, 255).astype(np.uint8))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", fps, "-i", os.path.join(fo, "%04d.png"), "-i", src, "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", dst], check=True)
print("wrote", dst)
