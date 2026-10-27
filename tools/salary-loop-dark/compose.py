"""Assemble The Salary Loop.

  python3 compose.py RENDER_DIR OUT_DIR

RENDER_DIR holds frames/f00000.jpg.. (render.cjs frames) and mix.wav (mix.py). Writes to OUT_DIR:
  salary-loop.mp4               master, 1080x1920 30 fps, -15 LUFS, true peak checked after AAC
  salary-loop_music-ready.mp4   same picture, silent (the sub-boom hit is at 6.40 s)
"""
import glob, os, subprocess, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
import overlay
from sld_sound import master_to_mp4

src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
overlay.check()
fps = overlay.FPS; total = round(overlay.DUR * fps)
frames = sorted(glob.glob(os.path.join(src, 'frames', 'f*.jpg'))); assert len(frames) == total, f'{len(frames)} frames, expected {total}'
silent = os.path.join(out, 'salary-loop_music-ready.mp4')
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', str(fps), '-i', '-',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', silent], stdin=subprocess.PIPE)
for f, path in enumerate(frames): enc.stdin.write(overlay.draw(Image.open(path).convert('RGB'), f / fps).tobytes())
enc.stdin.close(); assert enc.wait() == 0; print('video ok')
lufs, peak = master_to_mp4(silent, os.path.join(src, 'mix.wav'), os.path.join(out, 'salary-loop.mp4'))
print(f'master after AAC: {lufs} LUFS, true peak {peak} dBTP')
