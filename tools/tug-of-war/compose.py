"""Assemble Tug of War.

  python3 compose.py RENDER_DIR OUT_DIR

RENDER_DIR holds frames/f00000.jpg.. (render.cjs frames) and mix.wav (mix.py). Writes to OUT_DIR:
  tug-of-war.mp4               master, 1080x1920 30 fps, -15 LUFS, true peak checked after AAC
  tug-of-war_music-ready.mp4   same picture, silent (sub-boom / reveal hit at 10.00 s)
"""
import glob, json, os, subprocess, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import overlay
from sld_sound import master_to_mp4

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
fps = overlay.TL['fps']; total = round(overlay.TL['duration'] * fps)
frames = sorted(glob.glob(os.path.join(src, 'frames', 'f*.jpg')))
assert len(frames) == total, f'{len(frames)} frames, expected {total}'
silent = os.path.join(out, 'tug-of-war_music-ready.mp4')
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', str(fps), '-i', '-',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', silent], stdin=subprocess.PIPE)
for f, path in enumerate(frames):
    enc.stdin.write(overlay.draw(Image.open(path).convert('RGB'), f / fps).tobytes())
enc.stdin.close(); assert enc.wait() == 0
print('video ok')
print('master after AAC (LUFS, true peak dBFS):', master_to_mp4(silent, os.path.join(src, 'mix.wav'), os.path.join(out, 'tug-of-war.mp4')))
