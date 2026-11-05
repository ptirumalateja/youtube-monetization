"""Slow a rendered shot to a new frame count with motion-compensated interpolation.
python3 retime.py SRC_DIR DST_DIR NEW_COUNT     (SRC frames f%04d.png at 24 fps)
"""
import sys, os, subprocess, glob
src, dst, m = sys.argv[1], sys.argv[2], int(sys.argv[3])
n = len(glob.glob(os.path.join(src, 'f*.png')))
os.makedirs(dst, exist_ok=True)
for f in glob.glob(os.path.join(dst, '*.png')): os.remove(f)
if m == n:
    for i in range(n): os.symlink(os.path.abspath(os.path.join(src, f'f{i:04d}.png')), os.path.join(dst, f'f{i:04d}.png'))
else:
    rate = 24.0 * n / m
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', f'{rate:.6f}', '-i', os.path.join(src, 'f%04d.png'),
                    '-vf', 'minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1', '-frames:v', str(m),
                    '-start_number', '0', os.path.join(dst, 'f%04d.png')], check=True)
print(src, n, '->', len(glob.glob(os.path.join(dst, 'f*.png'))))
