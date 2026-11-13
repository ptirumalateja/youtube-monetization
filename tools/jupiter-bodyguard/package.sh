#!/bin/bash
# package.sh FRAMES_DIR MIX.wav OUT_DIR NAME
set -e
F=$1; A=$2; O=$3; N=$4
mkdir -p $O
ffmpeg -y -loglevel error -framerate 30 -i $F/f%04d.jpg -i $A -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -c:a aac -b:a 256k -shortest -movflags +faststart $O/$N.mp4
python3 - "$F" "$O" "$N" <<'PY'
import sys, cv2, numpy as np
F, O, N = sys.argv[1:4]
def sheet(frames, cols, w, path):
    ims = []
    for f in frames:
        im = cv2.imread(f"{F}/f{f:04d}.jpg"); im = cv2.resize(im, (w, int(w * 16 / 9)))
        cv2.putText(im, f"{f/30:.2f}s", (8, 28), 0, 0.8, (0, 255, 255), 2); ims.append(im)
    while len(ims) % cols: ims.append(np.zeros_like(ims[0]))
    cv2.imwrite(path, np.vstack([np.hstack(ims[i:i + cols]) for i in range(0, len(ims), cols)]), [cv2.IMWRITE_JPEG_QUALITY, 88])
sheet([0, 4, 8, 12, 18, 30, 45, 60, 75, 90], 5, 360, f"{O}/{N}_hook_0-3s.jpg")
sheet(list(range(0, len(__import__("glob").glob(F + "/f*.jpg")), 30)), 6, 300, f"{O}/{N}_contact_1fps.jpg")
PY
echo packaged
