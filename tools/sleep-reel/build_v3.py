"""V3 assembly: the opening swipe from NORMAL PEOPLE to ME is made here from two frames (the normal sleeper holds, ME slides in with
motion blur), then overlay.compose on every frame -> output/v3/comp, silent mp4, mux with the mix.

  python3 build_v3.py            (frames in output/v3/frames, mix in output/mix3.wav)
"""
import os, sys, subprocess
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import overlay
from overlay import W, H, sstep
OUT = os.path.join(HERE, 'output', 'v3'); FR = os.path.join(OUT, 'frames'); CP = os.path.join(OUT, 'comp'); os.makedirs(CP, exist_ok=True)
N = 597; I0, I1 = 66, 78; A_IDX, B_IDX = 71, 72
def sm5(u): u = min(1.0, max(0.0, u)); return u * u * u * (u * (u * 6 - 15) + 10)
def img(i): return Image.open(os.path.join(FR, f'f{i:05d}.jpg'))
A = np.asarray(overlay.compose(img(A_IDX), 2.30)).astype(np.float32); B = np.asarray(overlay.compose(img(B_IDX), 2.50)).astype(np.float32)
strip = np.concatenate([A, B], axis=1)
for i in range(N):
    o = os.path.join(CP, f'f{i:05d}.jpg')
    if I0 <= i < I1:
        p = sm5((i - I0) / (I1 - I0 - 1)); acc = np.zeros_like(A); ks = range(-4, 5)
        for k in ks:
            x = int(round(min(1.0, max(0.0, p + k * 0.012)) * W)); acc += strip[:, x:x + W]
        Image.fromarray((acc / len(ks)).clip(0, 255).astype(np.uint8)).save(o, quality=93)
    elif not os.path.exists(o) or i < 120 or 438 <= i < 483 or 186 <= i < 336:
        overlay.compose(img(i), i / 30).save(o, quality=93)
print('composed')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', '30', '-i', os.path.join(CP, 'f%05d.jpg'), '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', os.path.join(OUT, 'silent.mp4')], check=True)
import sld_sound as S
print(S.master_to_mp4(os.path.join(OUT, 'silent.mp4'), os.path.join(HERE, 'output', 'mix3.wav'), os.path.join(OUT, 'normal-people-vs-me-sleep.mp4')))
