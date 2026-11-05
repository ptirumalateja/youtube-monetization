"""Compose the 5 s hook test: frames + captions + popping tags + sound.
python3 compose_hook.py output/hook   ->  output/hook/ghosts-hook-test.mp4"""
import os, subprocess, sys
from PIL import Image
from overlay import caption, tags

D = sys.argv[1]
FPS = 30
N = 150
TAGS = [  # text, x, y, angle, pop time  (screen positions over the crowd after the turn)
    ('NEVER SENT', 640, 760, 4, 3.5),
    ('DRAFT, 2019', 840, 1000, -3, 3.85),
    ('STARTS MONDAY', 700, 1290, 3, 4.2),
    ('DAY 1 (OF 1)', 880, 1560, -4, 4.55),
]
os.makedirs(f'{D}/comp', exist_ok=True)


for f in range(N):
    t = f / FPS
    im = Image.open(f'{D}/frames/f{f:05d}.jpg').convert('RGB')
    if t < 2.45:
        im = caption(im, ["THESE ARE ALL THE YOU'S", 'YOU NEVER FINISHED.'], 0.08)
    if t >= 3.2:
        im = caption(im, ['THEY NEVER LEFT.'], 0.08)
    for s, x, y, a, t0 in TAGS:  # each tag pops in over 0.18 s with a small overshoot
        if t < t0: continue
        u = min(1, (t - t0) / 0.18)
        im = tags(im, [(s, x, y, a)], 0.04 * (0.6 + 0.4 * u + 0.5 * (1 - u) * u))
    im.save(f'{D}/comp/c{f:05d}.jpg', quality=94)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS), '-i', f'{D}/comp/c%05d.jpg', '-i', f'{D}/hook.wav',
                '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k',
                '-shortest', '-movflags', '+faststart', f'{D}/ghosts-hook-test.mp4'], check=True)
print('ok')
