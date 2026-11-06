"""Assemble Build It As You Climb.

  python3 compose.py RENDER_DIR OUT_DIR

RENDER_DIR holds frames/f00000.jpg.. (render.cjs frames), meta.json (render.cjs meta) and mix.wav (mix.py). Writes:
  build-as-you-climb.mp4               master, 1080x1920 30 fps, -15 LUFS, true peak checked after AAC
  build-as-you-climb_music-ready.mp4   same picture, silent (red rung clicks home at pPlace in timeline.json)
"""
import glob, os, subprocess, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
import overlay, json
from sld_sound import master_to_mp4

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
fps = overlay.TL['fps']; total = round(overlay.TL['duration'] * fps)
XF = round(overlay.TL.get('loopXfade', 0) * fps) or 1
META = json.load(open(os.path.join(src, 'meta.json')))['frames']
frames = sorted(glob.glob(os.path.join(src, 'frames', 'f*.jpg')))
assert len(frames) == total, f'{len(frames)} frames, expected {total}'
silent = os.path.join(out, 'build-as-you-climb_music-ready.mp4')
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', str(fps), '-i', '-',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '15', '-tune', 'film', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', silent], stdin=subprocess.PIPE)
for f, path in enumerate(frames):
    im = Image.open(path).convert('RGB')
    u = (f - (total - XF)) / XF                       # seamless loop: dissolve the last frames into frame 0
    if u > 0: im = Image.blend(im, Image.open(frames[0]).convert('RGB'), min(1.0, u * u * (3 - 2 * u)))
    enc.stdin.write(overlay.draw(im, f / fps, META[f]).tobytes())
enc.stdin.close(); assert enc.wait() == 0
print('video ok')
lufs, tp = master_to_mp4(silent, os.path.join(src, 'mix.wav'), os.path.join(out, 'build-as-you-climb.mp4'), limit=0.4)
print(f'master after AAC: {lufs:.1f} LUFS, true peak {tp:.1f} dBTP')
