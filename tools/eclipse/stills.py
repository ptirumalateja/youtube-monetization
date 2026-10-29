"""python3 stills.py OUTDIR [scale] -> key stills for sign-off."""
import json, os, subprocess, sys, numpy as np
O = sys.argv[1]; S = float(sys.argv[2]) if len(sys.argv) > 2 else 1
W, H = int(1080 * S), int(1920 * S)
os.makedirs(O, exist_ok=True)
def n(v): v = np.array(v, float); return (v / np.linalg.norm(v)).tolist()
L = np.array(n([1, .3, .55]))
side = np.cross(L, [0, 1, 0]); side /= np.linalg.norm(side)
M = (L * 57 + side * .12 + np.array([0, .25, 0]))
cam = M + L * 6 + side * -.42 + np.array([0, -.22, 0])
un = lambda v: v / np.linalg.norm(v)
tgt = cam + un(-cam) * .8 + un(M - cam) * .2
BASE = dict(uT=3., uShot=0, uZoom=1, uMR=1, uExp=1, uDark=0, uFov=.5, uA=0, uB=0, uSky=0, uPhot=1, uMoonC=[0, 0, 0], uBead=[0, 0, 0], uCamP=[0, 0, 5], uCamT=[0, 0, 0], uSun=[1, 0, 0], uCen=[0, 0, 0])
def sh(k, **kw):
  kw = {**BASE, **kw}
  return dict(out=f'{O}/{k}.png', w=W, h=H, f={a: b for a, b in kw.items() if not isinstance(b, list)}, v={a: b for a, b in kw.items() if isinstance(b, list)})
jobs = [
  sh('a_hook', uShot=0, uZoom=2.3, uMR=1.03, uExp=1., uSky=1., uPhot=1., uDark=1., uMoonC=[.04, -.03, 0], uBead=[-.8, .6, 1.4], uCen=[0, 0, 0]),
  sh('b_transit', uShot=0, uZoom=1.9, uMR=1 / 400, uExp=.55, uSky=0., uPhot=1., uMoonC=[.32, .35, 0], uBead=[0, 0, 0], uCen=[0, 0, 0]),
  sh('c_approach', uShot=0, uZoom=1.9, uMR=.45, uExp=.55, uSky=0., uPhot=1., uMoonC=[.12, .1, 0], uBead=[0, 0, 0], uCen=[0, 0, 0]),
  sh('d_earth', uShot=1, uA=1., uB=1., uFov=.1, uSun=L.tolist(), uMoonC=M.tolist(), uCamP=cam.tolist(), uCamT=tgt.tolist()),
  sh('e_hill', uShot=2, uDark=1., uZoom=.04, uCen=[.6, .74, 0], uExp=1., uMoonC=[.01, 0, 0], uB=1., uA=0.),
  sh('f_head', uShot=3, uZoom=.085, uCen=[.66, .74, 0], uExp=1., uMoonC=[.01, 0, 0], uA=0., uB=0.),
  sh('g_annular', uShot=0, uZoom=1.6, uMR=.935, uExp=.5, uPhot=2.5, uSky=0., uMoonC=[0, 0, 0], uBead=[0, 0, 0], uCen=[0, 0, 0]),
]
json.dump(jobs, open(f'{O}/jobs.json', 'w'))
subprocess.run(['node', os.path.dirname(os.path.abspath(__file__)) + '/gl/render.mjs', f'{O}/jobs.json'], check=True)
