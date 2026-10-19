#!/usr/bin/env python3
"""Retime the rendered v8 frames into the v9 sequence (24.77 s) without re-rendering: freeze, speed-ups, and the slow hold frames.
usage: build_reel2.py <old_frames_dir> <slow_frames_dir> <out_dir>"""
import os, sys, shutil
old, slow, out = sys.argv[1:4]
os.makedirs(out, exist_ok=True)
seq = []
seq += [f'{old}/f{i:04d}.jpg' for i in range(0, 90)]                                   # 0-3.0 s as is
seq += [f'{old}/f0090.jpg'] * 18                                                        # freeze on the empty sky (0.6 s)
seq += [f'{old}/f{int(99 + k*1.2):04d}.jpg' for k in range(79)]                        # old 3.3-6.45 s, x1.2
seq += [f'{old}/f{i:04d}.jpg' for i in range(194, 360)]                                 # old 6.45-12.0 s as is
seq += [f'{slow}/f{i:04d}.jpg' for i in range(1680, 1722)]                              # old 12.0-12.3 s rendered slowly (1.4 s hold)
seq += [f'{old}/f{i:04d}.jpg' for i in range(369, 540)]                                 # old 12.3-18.0 s as is
seq += [f'{old}/f{int(540 + k*1.129):04d}.jpg' for k in range(93)]                      # old 18.0-21.5 s, x1.129
seq += [f'{old}/f{int(645 + k*1.25):04d}.jpg' for k in range(84)]                       # old 21.5-25.0 s, x1.25
for n, p in enumerate(seq):
    assert os.path.exists(p), p
    d = f'{out}/g{n:04d}.jpg'
    if os.path.lexists(d): os.remove(d)
    os.symlink(p, d)
print(len(seq), 'frames', round(len(seq)/30, 3), 's')
