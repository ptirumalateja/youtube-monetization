"""Look-test assembly: python3 compose_test.py RENDER_DIR OUT.mp4  (frames + overlay + sfx mix, -15 LUFS)."""
import glob, os, subprocess, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import overlay
src, out = sys.argv[1], sys.argv[2]; fps = overlay.TL['fps']
frames = sorted(glob.glob(os.path.join(src, 'frames', 'f*.jpg')))
sil = out.replace('.mp4', '_silent.mp4')
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', str(fps), '-i', '-',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', sil], stdin=subprocess.PIPE)
for f, p in enumerate(frames):
    enc.stdin.write(overlay.draw(Image.open(p).convert('RGB'), f / fps, {'age': 10, 'count': 10}).tobytes())
enc.stdin.close(); assert enc.wait() == 0
S = os.path.join(HERE, 'sfx'); d = overlay.TL['duration']; lift = int(overlay.TL['lift'] * 1000)
fc = (f"[1]volume=-20dB,atrim=0:{d}[r];[2]adelay=0|0,volume=0dB[a];[3]adelay={lift}|{lift},volume=-2dB[b];"
      f"[r][a][b]amix=inputs=3:normalize=0,apad,atrim=0:{d},loudnorm=I=-15:TP=-1.5:LRA=11[m]")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', sil, '-i', f'{S}/room.mp3', '-i', f'{S}/dial.mp3', '-i', f'{S}/pickup.mp3',
                '-filter_complex', fc, '-map', '0:v', '-map', '[m]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-shortest', '-movflags', '+faststart', out], check=True)
print('ok', out)
