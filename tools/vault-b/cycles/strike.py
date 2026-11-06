"""Giant living cobra rears in front of the Vault B door and strikes at the camera (Cycles).
python3 strike.py OUTDIR [W H SAMPLES]   env FRAMES=a,b (default 0,48) ; STILL=frame -> OUTDIR/still.png"""
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
out = sys.argv[1]; W = int(sys.argv[2]) if len(sys.argv) > 2 else 1080; H = int(sys.argv[3]) if len(sys.argv) > 3 else 1920
S = int(sys.argv[4]) if len(sys.argv) > 4 else 32
# build the door scene (everything before its camera section)
src = open(os.path.join(HERE, 'door.py')).read().split('# ---------- cameras / animation ----------')[0]
sys.argv = ['door.py', '/tmp/unused.png', str(W), str(H), str(S), 'wide']
g = {'__file__': os.path.join(HERE, 'door.py'), '__name__': 'door'}; exec(compile(src, 'door.py', 'exec'), g)
import bpy
from mathutils import Vector
import lib, snake

sc = bpy.context.scene
R = 0.2
cob = snake.Cobra('giant', R, belly_up=Vector((0, -1, 0)))
CAM0 = Vector((0.15, -6.4, 0.55))
cam = lib.camera(CAM0, (0, -1.7, 2.1), lens=26, fstop=5.6, focus=4.5)
# rim lights behind the snake so the hood reads against the door, plus a low warm key from the lamps
lib.spot((0.0, -0.6, 3.6), (0, -2.0, 2.0), 900, angle=0.9, blend=0.6, color=(1, 0.7, 0.42), radius=0.2)
lib.spot((-2.0, -3.6, 0.4), (0, -1.9, 2.0), 500, angle=0.6, blend=0.7, color=(1, 0.6, 0.3), radius=0.05)
lib.spot((2.2, -4.2, 0.6), (0, -1.9, 2.2), 260, angle=0.6, blend=0.7, color=(1, 0.66, 0.38), radius=0.05)

def ss(t): t = min(1, max(0, t)); return t * t * (3 - 2 * t)
def bez(p0, p1, p2, p3, n):
    return [p0 * (1 - t) ** 3 + p1 * 3 * t * (1 - t) ** 2 + p2 * 3 * t * t * (1 - t) + p3 * t ** 3 for t in (i / (n - 1) for i in range(n))]

BASE = Vector((0, -1.9, 0))
def pose(f):
    sec = f / 24
    rise = ss(f / 14); hood = 0.25 + 0.75 * ss((f - 6) / 12)
    sway = 0.12 * math.sin(sec * 3.1) * (1 - ss((f - 24) / 4))
    Hh = 1.0 + 1.9 * rise
    head = Vector((sway, BASE.y - 0.15, Hh)); fwd = Vector((0, -1, -0.15)).normalized(); jaw = 0.0
    if f >= 24:   # draw back
        u = ss((f - 24) / 5); head = head + Vector((0, 0.35, 0.12)) * u; jaw = 0.55 * u
    if f >= 29:   # strike into the lens
        u = ss((f - 29) / 6) ** 0.8; tgt = CAM0 + Vector((-0.02, 0.55, 0.12))
        head = head.lerp(tgt, u); fwd = (CAM0 - head).normalized() if (CAM0 - head).length > 1e-3 else fwd; jaw = 0.55 + 0.45 * u
    # coil on the floor (1.4 turns, shrinking radius), then the neck rises to the head
    coil = []
    for i in range(70):
        t = i / 69; a = -t * math.tau * 1.4 + 0.6; r = 1.0 - 0.55 * t
        coil.append(Vector((BASE.x + math.cos(a) * r, BASE.y + math.sin(a) * r * 0.8, R * 0.95 + 0.02 * t)))
    c0 = coil[-1]; neck_top = head - fwd * 0.55
    neck = bez(c0, c0 + Vector((0, 0, Hh * 0.45)), neck_top - Vector((0, 0, 0.0)) + Vector((0, 0.25, -Hh * 0.25)), neck_top, 60)
    headpts = [neck_top + fwd * (0.55 * k / 10) for k in range(1, 11)]
    tongue = (0.5 + 0.5 * math.sin(sec * 22)) if 10 < f < 24 and (f // 4) % 2 == 0 else 0.0
    cob.update(coil + neck[1:] + headpts, hood=hood, jaw=jaw, tongue=tongue, tongue_phase=sec)
    # the camera shakes as it lands
    sh = 0.03 * ss((f - 31) / 3) * math.sin(f * 2.7) if f > 31 else 0.0
    cam.location = CAM0 + Vector((sh, 0, sh * 0.6))
    cam.data.dof.focus_distance = max(0.4, (head - cam.location).length)

os.makedirs(out, exist_ok=True)
if os.environ.get('STILL'):
    f = int(os.environ['STILL']); pose(f); sc.render.filepath = os.path.join(out, 'still_%02d.png' % f); bpy.ops.render.render(write_still=True)
else:
    a, b = [int(v) for v in os.environ.get('FRAMES', '0,40').split(',')]
    for f in range(a, b):
        fn = os.path.join(out, 'f%04d.png' % f)
        if os.path.exists(fn): continue
        pose(f); sc.render.filepath = fn; bpy.ops.render.render(write_still=True); print('frame', f, flush=True)
