#!/usr/bin/env python3
"""Retime the mixed sound to the trimmed cut: each anchor segment of the original 28.2 s mix is tempo-changed (pitch preserved)
so that hits stay locked to the picture. usage: warp_audio.py in.wav out.wav"""
import json, subprocess, sys, os, math
src, dst = sys.argv[1], sys.argv[2]
W = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'warp.json'))); A = W['anch']
parts = []; labels = []
for i, ((T0, t0), (T1, t1)) in enumerate(zip(A, A[1:])):
    f = (T1 - T0) / (t1 - t0)
    chain = f"atrim=start={T0}:end={T1},asetpts=PTS-STARTPTS"
    if f > 1.0005:
        k = max(1, math.ceil(math.log(f) / math.log(2.0))); each = f ** (1.0 / k)
        chain += "," + ",".join(f"atempo={each:.5f}" for _ in range(k))
    chain += ",atrim=end=%f,apad=whole_dur=%f" % (t1 - t0, t1 - t0)
    chain += ",afade=t=in:d=0.004,afade=t=out:st=%f:d=0.004" % max(0.0, (t1 - t0) - 0.004)
    parts.append(f"[0:a]{chain}[s{i}]"); labels.append(f"[s{i}]")
fg = ";".join(parts) + ";" + "".join(labels) + f"concat=n={len(labels)}:v=0:a=1[out]"
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-filter_complex", fg, "-map", "[out]", "-ar", "48000", dst], check=True)
print("warped audio ->", dst)
