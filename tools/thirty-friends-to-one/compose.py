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
import re

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
# the kit's master_to_mp4 limits at -2.5 dBFS; the toast clink still read -0.1 dBTP after AAC, so limit at -3.3 dBFS
# (same fix as I'm Fine) and verify after encoding
def meas(path, af=None):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', (af + ',' if af else '') + 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    s = r[r.rindex('Summary:'):]; return float(re.search(r'I:\s+(\S+) LUFS', s).group(1)), float(re.search(r'Peak:\s+(\S+) dBFS', s).group(1))
wav = os.path.join(src, 'mix.wav'); master = os.path.join(out, 'thirty-friends-to-one.mp4')
g = -15.0 - meas(wav)[0]
for _ in range(3):
    af = f"volume={g:.2f}dB,alimiter=limit=0.684:attack=3:release=80:level=false,aresample=48000"; g += -15.0 - meas(wav, af)[0]
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', silent, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-af', af,
                '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', master], check=True)
i, tp = meas(master)
print(f'master after AAC: {i:.1f} LUFS, true peak {tp:.1f} dBTP')
assert tp <= -1.0, 'true peak over -1 dBTP after AAC'
