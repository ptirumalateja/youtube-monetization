"""python3 compose.py RENDER_DIR OUT_DIR  ->  salary-dark-warm.mp4 (master, -15 LUFS) and salary-dark-warm_music-ready.mp4 (silent).
RENDER_DIR holds frames/f00000.jpg.. (render.cjs frames) and mix.wav (mix.py)."""
import glob, os, subprocess, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
import overlay
from sld_sound import master_to_mp4
src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True); fps = overlay.TL['fps']; total = round(overlay.TL['duration'] * fps)
frames = sorted(glob.glob(os.path.join(src, 'frames', 'f*.jpg'))); assert len(frames) == total, (len(frames), total)
silent = os.path.join(out, 'salary-dark-warm_music-ready.mp4')
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', str(fps), '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', silent], stdin=subprocess.PIPE)
for f, p in enumerate(frames): enc.stdin.write(overlay.draw(Image.open(p).convert('RGB'), f / fps).tobytes())
enc.stdin.close(); assert enc.wait() == 0; print('video ok')
lufs, peak = master_to_mp4(silent, os.path.join(src, 'mix.wav'), os.path.join(out, 'salary-dark-warm.mp4')); print(f'master: {lufs} LUFS, true peak {peak} dBTP')
