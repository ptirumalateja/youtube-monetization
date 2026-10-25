"""Assemble 30 Friends to 1.

  python3 compose.py RENDER_DIR OUT_DIR

RENDER_DIR holds frames/f00000.jpg.. (render.cjs frames), meta.json (render.cjs meta) and mix.wav (mix.py). Writes to OUT_DIR:
  thirty-friends-to-one.mp4               master, 1080x1920 30 fps, -15 LUFS, true peak checked after AAC
  thirty-friends-to-one_music-ready.mp4   same picture, silent (the toast clink lands at TL['clink'] = 16.20 s)
"""
import glob, json, os, subprocess, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
import overlay
from sld_sound import master_to_mp4

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
fps = overlay.TL['fps']; total = round(overlay.TL['duration'] * fps)
meta = json.load(open(os.path.join(src, 'meta.json')))['frames']
frames = sorted(glob.glob(os.path.join(src, 'frames', 'f*.jpg')))
assert len(frames) == total == len(meta), f'{len(frames)} frames, {len(meta)} meta rows, expected {total}'

silent = os.path.join(out, 'thirty-friends-to-one_music-ready.mp4')
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', str(fps), '-i', '-',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', silent], stdin=subprocess.PIPE)
for f, path in enumerate(frames):
    enc.stdin.write(overlay.draw(Image.open(path).convert('RGB'), f / fps, meta[f]).tobytes())
enc.stdin.close(); assert enc.wait() == 0
print('video ok')
i, tp = master_to_mp4(silent, os.path.join(src, 'mix.wav'), os.path.join(out, 'thirty-friends-to-one.mp4'))
print(f'master after AAC: {i:.1f} LUFS, true peak {tp:.1f} dBFS')
