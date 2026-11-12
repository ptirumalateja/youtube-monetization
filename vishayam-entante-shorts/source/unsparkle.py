import numpy as np
from PIL import Image, ImageFilter
import os
A = np.load(os.environ.get('ALPHA','alpha.npy'))
X0, Y0 = int(os.environ.get('AX','846')), int(os.environ.get('AY','1686')); N = A.shape[0]
C = float(os.environ.get('AC','235'))
a3 = A[..., None]
# thin band around the sparkle's outline, where edge residue remains
mask = Image.fromarray((A > 0.015).astype(np.uint8) * 255)
dil = np.asarray(mask.filter(ImageFilter.MaxFilter(5))) > 0
ero = np.asarray(mask.filter(ImageFilter.MinFilter(5))) > 0
band = (dil & ~ero).astype(float)
band = np.asarray(Image.fromarray((band * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))).astype(float)[..., None] / 255
def clean(frame):
    p = frame[Y0:Y0+N, X0:X0+N].astype(float)
    u = np.clip((p - a3 * C) / (1 - a3), 0, 255)
    blur = np.asarray(Image.fromarray(u.astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.2))).astype(float)
    out = u * (1 - band) + blur * band
    frame[Y0:Y0+N, X0:X0+N] = out.astype(np.uint8)
    return frame
if __name__ == '__main__':
    import sys, subprocess
    src, dst = sys.argv[1], sys.argv[2]
    W, H = 1080, 1920
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', src, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '24', '-i', '-',
                            '-c:v', 'libx264', '-crf', '12', '-preset', 'fast', '-pix_fmt', 'yuv420p', dst], stdin=subprocess.PIPE)
    sz = W * H * 3
    while True:
        buf = dec.stdout.read(sz)
        if len(buf) < sz: break
        f = np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy()
        enc.stdin.write(clean(f).tobytes())
    enc.stdin.close(); enc.wait(); dec.wait()
