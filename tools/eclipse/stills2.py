"""FRAG=scene2.glsl python3 stills2.py OUTDIR [scale] -> stills of the 1868 / helium cut."""
import json, os, subprocess, sys, math
import numpy as np
O = sys.argv[1]; S = float(sys.argv[2]) if len(sys.argv) > 2 else 1
W, H = int(1080 * S), int(1920 * S)
os.makedirs(O, exist_ok=True)
un = lambda v: np.asarray(v, float) / np.linalg.norm(v)
def ll2p(lon, lat, rot):
    la, lo = math.radians(lat), math.radians(lon)
    X, Z = math.cos(la) * math.sin(lo), math.cos(la) * math.cos(lo)
    return np.array([X * math.cos(rot) + Z * math.sin(rot), math.sin(la), -X * math.sin(rot) + Z * math.cos(rot)])
BASE = dict(uT=3., uShot=0, uZoom=1, uMR=1, uExp=1, uDark=0, uFov=.5, uA=0, uB=0, uC=0, uD=0, uE=0, uSky=0, uPhot=1,
            uMoonC=[0, 0, 0], uBead=[0, 0, 0], uCamP=[0, 0, 5], uCamT=[0, 0, 0], uSun=[1, 0, 0], uCen=[0, 0, 0])
def sh(k, **kw):
    kw = {**BASE, **kw}
    return dict(out=f'{O}/{k}.png', w=W, h=H, f={a: b for a, b in kw.items() if not isinstance(b, list)}, v={a: b for a, b in kw.items() if isinstance(b, list)})
rot = 2.4 + 3. * .01
cam = ll2p(42, 30, rot) * 5.4
sun = ll2p(-130, 10, rot)
jobs = [
  sh('a_spec_wide', uShot=10, uZoom=330., uA=545., uB=1., uC=1., uD=0.),
  sh('b_spec_zoom', uShot=10, uZoom=42., uA=588., uB=1., uC=0., uD=1.),
  sh('c_obs', uShot=11, uZoom=1.5, uExp=1., uMoonC=[0, 0, 0]),
  sh('d_prom', uShot=12, uZoom=.5, uCen=[.18, .93, 0], uPhot=1.3, uA=1.38, uB=.2, uC=.15, uE=620.),
  sh('e_letters', uShot=13, uFov=.62, uA=.8, uB=1., uSun=sun.tolist(), uCamP=cam.tolist(), uCamT=[0, 0, 0]),
]
json.dump(jobs, open(f'{O}/jobs.json', 'w'))
subprocess.run(['node', os.path.dirname(os.path.abspath(__file__)) + '/gl/render.mjs', f'{O}/jobs.json'], check=True, env={**os.environ, 'FRAG': 'scene2.glsl'})
