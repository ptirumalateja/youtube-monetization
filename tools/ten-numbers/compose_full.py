"""Assemble Ten Numbers.  python3 compose_full.py RENDER_DIR OUT_DIR
RENDER_DIR: frames/f00000.jpg.. (render.cjs frames), meta.json (render.cjs meta), mix.wav (mix.py).
The last loopFade seconds dissolve into frame 0 (picture + text), so the reel loops."""
import glob, json, os, re, subprocess, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import overlay
from warp import fwd
src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
fps = overlay.TL['fps']; total = round(overlay.TL['outDuration'] * fps); LF = overlay.TL['loopFade']
meta = json.load(open(os.path.join(src, 'meta.json')))['frames']
frames = sorted(glob.glob(os.path.join(src, 'frames', 'f*.jpg')))
assert len(frames) == total == len(meta), (len(frames), len(meta), total)
silent = os.path.join(out, 'ten-numbers_music-ready.mp4')
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', str(fps), '-i', '-',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', silent], stdin=subprocess.PIPE)
f0raw = Image.open(frames[0]).convert('RGB')
for f, path in enumerate(frames):
    t = f / fps
    raw = Image.open(path).convert('RGB')
    u = overlay.sstep(overlay.TL['outDuration'] - LF, overlay.TL['outDuration'], t); ts = fwd(t)
    if u > 0:                     # loop: picture dissolves into frame 0; the payoff text leaves first, the hook arrives after
        raw = Image.blend(raw, f0raw, u)
        img = overlay.draw(raw, ts, meta[f], end_k=1 - overlay.sstep(0.0, 0.5, u), hook_k=overlay.sstep(0.5, 1.0, u))
    else:
        img = overlay.draw(raw, ts, meta[f])
    enc.stdin.write(img.tobytes())
enc.stdin.close(); assert enc.wait() == 0
wav = os.path.join(src, 'mix.wav'); master = os.path.join(out, 'ten-numbers.mp4')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', silent, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-af',
                'loudnorm=I=-15:TP=-2.0:LRA=9,aresample=48000,alimiter=limit=0.66:level=false', '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', master], check=True)
r = subprocess.run(['ffmpeg', '-hide_banner', '-i', master, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
s = r[r.rindex('Summary:'):]; print('master', re.search(r'I:\s+(\S+) LUFS', s).group(1), 'LUFS, peak', re.search(r'Peak:\s+(\S+) dBFS', s).group(1))
