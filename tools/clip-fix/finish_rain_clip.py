#!/usr/bin/env python3
"""Finish the 'rain figure' clip: remove the moving/static corner sparkles per frame (detect + inpaint), add the caption in the earlier clip's own font, trim, fade out, loudness-normalise.
usage: finish_rain_clip.py IN.mp4 CAPTION_SOURCE_CLIP.mp4 OUT.mp4 [END=7.2] [CAPTION_Y=300] [SPEED=1.0]   (END is the output length; SPEED>1 plays the source faster)"""
import sys, os, subprocess, tempfile, glob
import numpy as np, cv2
src, capsrc, dst = sys.argv[1:4]; END = float(sys.argv[4]) if len(sys.argv) > 4 else 7.2; CY = int(sys.argv[5]) if len(sys.argv) > 5 else 300; SPEED = float(sys.argv[6]) if len(sys.argv) > 6 else 1.0
tmp = tempfile.mkdtemp(prefix="rainfix_"); fi = os.path.join(tmp, "in"); fo = os.path.join(tmp, "out"); os.makedirs(fi); os.makedirs(fo)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", f"setpts=PTS/{SPEED},fps=30", "-t", str(END), os.path.join(fi, "%04d.png")], check=True)
files = sorted(glob.glob(fi + "/*.png")); H, W = cv2.imread(files[0]).shape[:2]
# caption pixels taken from the earlier clip at full brightness (same typeface), scaled to this width
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "5", "-i", capsrc, "-frames:v", "1", os.path.join(tmp, "cap.png")], check=True)
cf = cv2.imread(os.path.join(tmp, "cap.png")); y0, y1, x0, x1 = 100, 156, 100, 650
g = cv2.cvtColor(cf[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY); th = cv2.morphologyEx(g, cv2.MORPH_TOPHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))).astype(np.float32)
cal = np.clip((th - 10) / max(np.percentile(th, 99.7) - 10, 1), 0, 1)
cal[cal < 0.12] = 0; n_, lab_, st_, _ = cv2.connectedComponentsWithStats((cal > 0).astype(np.uint8), connectivity=8)
keep = np.zeros_like(cal)
for i_ in range(1, n_):
    if st_[i_][4] >= 3: keep[lab_ == i_] = cal[lab_ == i_]
cal = keep; ys, xs = np.nonzero(cal > 0.05); cal = cal[max(0, ys.min() - 3):ys.max() + 4, max(0, xs.min() - 3):xs.max() + 4]
sc = 1.7; cal = np.clip(cv2.resize(cal, None, fx=sc, fy=sc, interpolation=cv2.INTER_CUBIC), 0, 1); ch, cw = cal.shape
# word spans (from empty-column gaps), then bolden the strokes and colour chosen words
cols = (cal.max(0) > 0.12).astype(np.uint8); spans = []; start = None; gap = 0
for x_ in range(cw):
    if cols[x_]:
        if start is None: start = x_
        gap = 0; last = x_
    elif start is not None:
        gap += 1
        if gap > 9: spans.append((start, last)); start = None
if start is not None: spans.append((start, last))
print("words found:", len(spans))
HIL = {3: (86, 196, 255), 8: (86, 196, 255)}      # BGR gold on "thoughts" and "anyone."
COL = np.tile(np.array([232, 228, 226], np.float32), (ch, cw, 1))
for wi, c in HIL.items():
    if wi < len(spans): COL[:, spans[wi][0]:spans[wi][1] + 1] = np.array(c, np.float32)
dil = cv2.GaussianBlur(cv2.dilate(cal, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))), (0, 0), 0.6)
cal = np.clip(0.5 * cal * 1.3 + 0.5 * dil * 1.2, 0, 1)   # a little bolder
SHAD = cv2.GaussianBlur(np.roll(np.roll(cal, 3, 0), 2, 1), (0, 0), 2.0) * 0.7
cx0 = (W - cw) // 2
def sparkle_mask(f):
    g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY); reg = g[1700:H, 880:W].astype(np.float32)
    lift = reg - cv2.medianBlur(reg.astype(np.uint8), 41).astype(np.float32)
    b = (lift > 22).astype(np.uint8); b = cv2.morphologyEx(b, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(b); m = np.zeros_like(b)
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if 60 <= a <= 2500 and 12 <= w <= 90 and 12 <= h <= 90 and 0.6 < w / h < 1.6: m[lab == i] = 1
    full = np.zeros((H, W), np.uint8); full[1700:H, 880:W] = cv2.dilate(m, np.ones((7, 7), np.uint8)); return full
cnt = 0
for i, fpath in enumerate(files):
    f = cv2.imread(fpath); t = i / 30.0
    m = sparkle_mask(f)
    if m.any(): f = cv2.inpaint(f, m * 255, 5, cv2.INPAINT_TELEA); cnt += 1
    a = 1.0   # caption fully visible from frame 0
    if a > 0:
        As_ = np.zeros((H, W), np.float32); As_[CY:CY + ch, cx0:cx0 + cw] = SHAD * a; ff = f.astype(np.float32) * (1 - As_[..., None])
        A = np.zeros((H, W), np.float32); A[CY:CY + ch, cx0:cx0 + cw] = cal * a; C_ = np.zeros((H, W, 3), np.float32); C_[CY:CY + ch, cx0:cx0 + cw] = COL
        f = (ff * (1 - A[..., None]) + C_ * A[..., None]).clip(0, 255).astype(np.uint8)
    cv2.imwrite(os.path.join(fo, os.path.basename(fpath)), f)
print("frames with sparkle removed:", cnt, "of", len(files))
af = f"atempo={SPEED},afade=t=out:st={END - 0.4:.2f}:d=0.4,loudnorm=I=-14:TP=-1.5:LRA=9"
vf = f"fade=t=out:st={END - 0.35:.2f}:d=0.35"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-i", os.path.join(fo, "%04d.png"), "-i", src, "-t", str(END), "-map", "0:v", "-map", "1:a?", "-vf", vf, "-af", af, "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", dst], check=True)
print("wrote", dst)
