"""Assemble The Chain Was Never Locked.

  python3 compose.py RENDER_DIR OUT_DIR

RENDER_DIR holds frames/f00000.jpg.. (render.cjs frames) and mix.wav (mix.py). Writes to OUT_DIR:
  chain-never-locked.mp4               master, 1080x1920 30 fps, sound normalised to -15 LUFS / -1.5 dBTP (checked after AAC)
  chain-never-locked_music-ready.mp4   same picture, silent (sub-boom / reveal hit at 13.00 s)
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

silent = os.path.join(out, 'chain-never-locked_music-ready.mp4')
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', str(fps), '-i', '-',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', silent], stdin=subprocess.PIPE)
for f, path in enumerate(frames):
    enc.stdin.write(overlay.draw(Image.open(path).convert('RGB'), f / fps).tobytes())
enc.stdin.close(); assert enc.wait() == 0
print('video ok')

# two-pass linear loudnorm, then verify true peak after AAC
wav = os.path.join(src, 'mix.wav')
m = subprocess.run(['ffmpeg', '-hide_banner', '-i', wav, '-af', 'loudnorm=I=-15:TP=-1.5:LRA=14:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
j = json.loads(m[m.rindex('{'):m.rindex('}') + 1])
af = (f"loudnorm=I=-15:TP=-1.5:LRA=14:linear=true:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
      f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']},aresample=48000")
master = os.path.join(out, 'chain-never-locked.mp4')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', silent, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-af', af,
                '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', master], check=True)
r = subprocess.run(['ffmpeg', '-hide_banner', '-i', master, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
summ = r[r.rindex('Summary:'):]
print('master after AAC:', ' '.join(re.findall(r'(I:\s+\S+ LUFS|Peak:\s+\S+ dBFS)', summ)))
