# Build stars.json for the Dipper reel from the HYG v4.1 catalogue (Hipparcos-based).
# Each star is propagated in 3D (x,y,z + v*t, parsecs) so perspective and radial motion are included.
# usage: python3 stars.py hygdata_v41.csv stars.json
import csv, json, math, sys
import numpy as np
SRC, OUT = sys.argv[1], sys.argv[2]
DIPPER = ['54061','53910','58001','59774','62956','65378','67301']   # Dubhe Merak Phecda Megrez Alioth Mizar Alkaid
UMAG = {'53910','58001','59774','62956','65378','65477'}            # Ursa Major Moving Group nucleus (Merak..Mizar + Alcor)
YEARS = np.linspace(0, 100000, 101)
C_RA, C_DEC = math.radians(12.35*15), math.radians(55.5)            # view centre (between bowl and handle)
MAGLIM, RADIUS = 6.8, 52.0
def unit(ra, dec): return np.array([math.cos(dec)*math.cos(ra), math.cos(dec)*math.sin(ra), math.sin(dec)])
cvec = unit(C_RA, C_DEC)
east = np.array([-math.sin(C_RA), math.cos(C_RA), 0.0]); north = np.cross(cvec, east)
def tangent(p):  # gnomonic projection, degrees (xi east, eta north)
    p = p/np.linalg.norm(p, axis=-1, keepdims=True); d = p@cvec
    return np.degrees(np.stack([(p@east)/d, (p@north)/d], -1))
out = []
for r in csv.DictReader(open(SRC)):
    if not r['hip'] or not r['mag'] or float(r['dist']) <= 0 or float(r['dist']) >= 100000: continue
    hip, mag = r['hip'], float(r['mag'])
    if mag > MAGLIM and hip not in DIPPER: continue
    ra, dec = float(r['rarad']), float(r['decrad'])
    if math.degrees(math.acos(max(-1, min(1, unit(ra, dec)@cvec)))) > RADIUS: continue
    x0 = np.array([float(r['x']), float(r['y']), float(r['z'])]); v = np.array([float(r['vx']), float(r['vy']), float(r['vz'])])
    path = tangent(x0[None, :] + YEARS[:, None]*v[None, :])
    if hip not in DIPPER and (np.abs(path).max() > 70 or not np.isfinite(path).all()): continue   # leaves the projectable field
    ci = float(r['ci']) if r['ci'] else 0.6
    out.append(dict(hip=hip, name=r['proper'], mag=mag, ci=ci, dist_ly=round(float(r['dist'])*3.26156, 1),
                    pm=[float(r['pmra']), float(r['pmdec'])], rv=float(r['rv'] or 0),
                    dipper=DIPPER.index(hip) if hip in DIPPER else -1, umag=hip in UMAG,
                    path=np.round(path, 4).tolist()))
out.sort(key=lambda s: s['mag'])
json.dump(dict(years=YEARS.tolist(), stars=out), open(OUT, 'w'))
for s in out:
    if s['dipper'] >= 0 or s['hip'] == '65477':
        p = np.array(s['path']); print(f"{s['name']:7s} {s['dist_ly']:6.1f} ly  pm {s['pm']}  moves {np.hypot(*(p[-1]-p[0])):.2f} deg in 100k yr")
print(len(out), 'stars')
