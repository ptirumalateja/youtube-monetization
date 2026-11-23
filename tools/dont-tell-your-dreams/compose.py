"""Assemble Don't Tell Your Dreams.

  python3 compose.py RENDER_DIR OUT_DIR [SONG.mp3]

RENDER_DIR holds frames/f00000.jpg.. (render.cjs frames). Writes to OUT_DIR:
  dont-tell-your-dreams_music-ready.mp4   1080x1920 30 fps, silent: the upload file. Add "Don't Tell Your Dreams"
                                          (LOVIXX & STOSLIV) from the platform's own music library, starting at 0:00.
  dont-tell-your-dreams_song-preview.mp4  same picture with the owner's copy of the song laid in at TL["songOffset"]
                                          (only when SONG is given): a sync check, NOT for upload (the song is
                                          commercial and not licensed to this channel; Content ID would claim it).
The song file itself never goes into git.
"""
import glob, os, subprocess, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
import overlay

src, out = sys.argv[1], sys.argv[2]; song = sys.argv[3] if len(sys.argv) > 3 else None
os.makedirs(out, exist_ok=True)
fps = overlay.TL['fps']; dur = overlay.TL['duration']; total = round(dur * fps)
frames = sorted(glob.glob(os.path.join(src, 'frames', 'f*.jpg')))
assert len(frames) == total, f'{len(frames)} frames, expected {total}'
silent = os.path.join(out, 'dont-tell-your-dreams_music-ready.mp4')
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', str(fps), '-i', '-',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', silent], stdin=subprocess.PIPE)
for f, path in enumerate(frames):
    enc.stdin.write(overlay.draw(Image.open(path).convert('RGB'), f / fps).tobytes())
enc.stdin.close(); assert enc.wait() == 0
print('video ok:', silent)
if song:
    ms = int(round(overlay.TL['songOffset'] * 1000))
    prev = os.path.join(out, 'dont-tell-your-dreams_song-preview.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', silent, '-i', song, '-filter_complex',
                    f'[1:a]adelay={ms}|{ms},apad,atrim=0:{dur},afade=t=out:st={dur - 0.4}:d=0.4[a]',
                    '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', prev], check=True)
    print('preview ok:', prev)
