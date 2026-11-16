import math, sys, os, time, numpy as np, cv2
sys.path.insert(0, os.environ['JBDIR'])
from assets import load_all
from kernel import render
from scene import *
T = load_all()
out, W, H, ss = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
jy = float(os.environ.get('JY', 9)); jz = float(os.environ.get('JZ', -75)); ty = float(os.environ.get('TY', 6))
fov = float(os.environ.get('FOV', 34)); cy = float(os.environ.get('CY', 1.25)); cz = float(os.environ.get('CZ', 2.2))
jx = float(os.environ.get('JX', 0)); erot = float(os.environ.get('EROT', 0.10)); grs = float(os.environ.get('GRS', -0.43))
L = norm([float(v) for v in os.environ.get('L', '-0.55,0.35,0.75').split(',')])
J = [jx, jy, jz]
cam = camera([0, cy, cz], [0, ty, jz], fov)
objs = [obj(JUPITER, J, 11.2, 0.935, 0.05), obj(EARTH, [0, 0, 0], 1.0, 1.0, 0.41)]
p = prm(earth_rot=erot, jup_rot=grs, shear=0.002, sky=float(os.environ.get('SKY', 0.55)), pix=math.radians(fov)/1350, sky_roll=0.8, sky_yaw=2.2, jpos=tuple(J), jfill=0.15)
t = time.time()
img = render(W, H, cam, np.array(objs), len(objs), L, T['earth_day'], T['earth_night'], T['earth_cloud'], T['jup'], T['sat'], T['ring'], T['sky'], T['neb'], p, ss)
np.save(out + '.npy', img.astype(np.float32))
cv2.imwrite(out, (tonemap(img, float(os.environ.get('EX', 1.0)))[..., ::-1] * 255).astype(np.uint8))
print('done', time.time() - t)
