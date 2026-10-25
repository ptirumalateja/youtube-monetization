"""Assemble The Chain Was Never Locked v2.

  python3 compose.py RENDER_DIR OUT_DIR

RENDER_DIR holds frames/f00000.jpg.. (render.cjs frames) and mix.wav (mix.py). Writes to OUT_DIR:
  chain-never-locked_v2.mp4            master, 1080x1920 30 fps, sound normalised to -15 LUFS, true peak under -1 dBTP (checked after AAC)
  chain-never-locked_v2_music-ready.mp4   same picture, silent (chain hits the floor / sub-boom at 12.45 s)
"""
import glob, json, os, re, subprocess, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import overlay

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
fps = overlay.TL['fps']; total = round(overlay.TL['duration'] * fps)
frames = sorted(glob.glob(os.path.join(src, 'frames', 'f*.jpg')))
assert len(frames) == total, f'{len(frames)} frames, expected {total}'

silent = os.path.join(out, 'chain-never-locked_v2_music-ready.mp4')
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', str(fps), '-i', '-',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', silent], stdin=subprocess.PIPE)
for f, path in enumerate(frames):
    enc.stdin.write(overlay.draw(Image.open(path).convert('RGB'), f / fps).tobytes())
enc.stdin.close(); assert enc.wait() == 0
print('video ok')

# gain to -15 LUFS, then a look-ahead limiter at -2.5 dBFS (loudnorm alone overshot +1.8 dBTP after AAC); verify after AAC
wav = os.path.join(src, 'mix.wav')
def lufs(path, af=None):
    cmd = ['ffmpeg', '-hide_banner', '-i', path] + (['-af', af + ',ebur128=peak=true'] if af else ['-af', 'ebur128=peak=true']) + ['-f', 'null', '-']
    r = subprocess.run(cmd, capture_output=True, text=True).stderr; summ = r[r.rindex('Summary:'):]
    return float(re.search(r'I:\s+(\S+) LUFS', summ).group(1)), float(re.search(r'Peak:\s+(\S+) dBFS', summ).group(1))
g = -15.0 - lufs(wav)[0]
for _ in range(3):   # the limiter costs a little loudness: nudge the gain until the limited mix sits at -15
    af = f"volume={g:.2f}dB,alimiter=limit=0.75:attack=4:release=60:level=false,aresample=48000"
    i, _p = lufs(wav, af); g += -15.0 - i
master = os.path.join(out, 'chain-never-locked_v2.mp4')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', silent, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-af', af,
                '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', master], check=True)
r = subprocess.run(['ffmpeg', '-hide_banner', '-i', master, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
summ = r[r.rindex('Summary:'):]
print('master after AAC:', ' '.join(re.findall(r'(I:\s+\S+ LUFS|Peak:\s+\S+ dBFS)', summ)))
