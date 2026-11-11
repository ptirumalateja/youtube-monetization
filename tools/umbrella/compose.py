"""Assemble the umbrella reel.  python3 compose.py RENDER_DIR OUT_DIR
Writes rain-or-shine.mp4 (1080x1920 30 fps, -15 LUFS) and rain-or-shine_music-ready.mp4 (silent). Ends on the
reference's fade to black (last 0.55 s)."""
import glob, json, os, subprocess, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
import overlay
from sld_sound import master_to_mp4
from sld_text import sstep
src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
TL = json.load(open(os.path.join(HERE, 'timeline.json'))); fps = TL['fps']; total = round(TL['duration'] * fps)
META = json.load(open(os.path.join(src, 'meta.json')))['frames']
frames = sorted(glob.glob(os.path.join(src, 'frames', 'f*.jpg'))); assert len(frames) == total, len(frames)
silent = os.path.join(out, 'rain-or-shine_music-ready.mp4')
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', str(fps), '-i', '-',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', silent], stdin=subprocess.PIPE)
VIS = TL['duration']; END = 3.0
for f, p in enumerate(frames):
    t = f / fps; im = overlay.draw(Image.open(p).convert('RGB'), t, META[f], card=sstep(VIS - 0.55, VIS - 0.05, t))
    enc.stdin.write(im.tobytes())
last = Image.open(frames[-1]).convert('RGB')
for f in range(round(END * fps)):
    t = VIS + f / fps; enc.stdin.write(overlay.end_card(last, t - VIS).tobytes())
enc.stdin.close(); assert enc.wait() == 0
lufs, tp = master_to_mp4(silent, os.path.join(src, 'mix.wav'), os.path.join(out, 'rain-or-shine.mp4'))
print(f'master: {lufs:.1f} LUFS, true peak {tp:.1f} dBTP')
