import sys, time, numpy as np, cv2
from assets import load_all
from kernel import render
from scene import *
T = load_all()
OUT = sys.argv[1]
W, H = 540, 960
L = norm([-0.85, 0.3, 0.35])
def go(name, cam, objs, p, ex=1.0):
    t=time.time()
    img = render(W, H, cam, np.array(objs), len(objs), L, T['earth_day'], T['earth_night'], T['earth_cloud'], T['jup'], T['sat'], T['ring'], T['sky'], T['neb'], p, 2)
    print(name, time.time()-t)
    cv2.imwrite(f"{OUT}/{name}.jpg", (tonemap(img, ex)[..., ::-1]*255).astype(np.uint8))
# Earth close
go('earth', camera([0,0,4.2],[0,0,0],30), [obj(EARTH,[0,0,0],1,1,0.41)], prm(sky=0.55, pix=0.0009, earth_rot=0.15))
# Saturn
go('saturn', camera([0,1.5,16],[0,0,0],38), [obj(SATURN,[0,0,0],4,0.9,0.45,0.35)], prm(sky=0.55, pix=0.0009, sat_rot=0.1))
# Jupiter behind earth
go('jupiter', camera([0,0,6],[0,1.5,-30],40), [obj(EARTH,[-0.5,-1.2,0],1,1,0.41), obj(JUPITER,[2,6,-40],11.2,0.935,0.05)], prm(sky=0.55, pix=0.0009, earth_rot=0.15, lens=3.0))
