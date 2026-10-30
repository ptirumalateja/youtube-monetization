"""V5 assembly (V2 timing, stripped ending): every scene frame through overlay.compose, silent mp4, mux with output/mix5.wav.

  python3 build_v5.py            (scene frames in output/v5/frames, 588 of them)
"""
import os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import overlay
from PIL import Image
OUT = os.path.join(HERE, 'output', 'v5'); FR = os.path.join(OUT, 'frames'); CP = os.path.join(OUT, 'comp'); os.makedirs(CP, exist_ok=True)
N = 588
for i in range(N):
    o = os.path.join(CP, f'c{i:05d}.jpg')
    if not os.path.exists(o): overlay.compose(Image.open(os.path.join(FR, f'f{i:05d}.jpg')), i / 30).save(o, quality=93)
sil = os.path.join(OUT, 'silent.mp4')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', '30', '-i', os.path.join(CP, 'c%05d.jpg'), '-c:v', 'libx264', '-crf', '17', '-pix_fmt', 'yuv420p', '-preset', 'slow', sil], check=True)
sys.path.insert(0, HERE)
import sld_sound as S
print(S.master_to_mp4(sil, os.path.join(HERE, 'output', 'mix5.wav'), os.path.join(OUT, 'normal-people-vs-me-sleep.mp4')))
