import sys, numpy as np, cv2, time
from assets import load_all
from kernel import render
from scene import tonemap
import shots
T = load_all()
def raw(t, W, H, ss):
    cam, objs, p, L, name = shots.setup(t)
    return render(W, H, cam, np.array(objs), len(objs), L, T['earth_day'], T['earth_night'], T['earth_cloud'], T['jup'], T['sat'], T['ring'], T['sky'], T['neb'], p, ss)
if __name__ == "__main__":
    out = sys.argv[1]; ts = [float(x) for x in sys.argv[2].split(',')]
    ims = []
    for t in ts:
        im = (tonemap(raw(t, 360, 640, 1))[..., ::-1] * 255).astype(np.uint8)
        cv2.putText(im, f"{t:.1f}", (10, 30), 0, 0.8, (0, 255, 255), 2); ims.append(im)
    rows = [np.hstack(ims[i:i+6] + [np.zeros_like(ims[0])] * (6 - len(ims[i:i+6]))) for i in range(0, len(ims), 6)]
    cv2.imwrite(out, np.vstack(rows))
