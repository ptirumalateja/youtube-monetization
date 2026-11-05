"""Shot 04: the vault corridor. Five lettered doors (A C D E F) swing open one after another,
gold light spilling out, while the camera dollies toward the far end where door B waits, shut,
two red eyes in the dark. python3 vaults.py OUT.png [W H SAMPLES]   (still: FRAME env picks the moment)
ANIM=a0,n,total python3 vaults.py OUTDIR W H SAMPLES
"""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
from mathutils import Vector, Matrix, Euler
import lib

out = sys.argv[1] if len(sys.argv) > 1 else '/tmp/vaults.png'
W = int(sys.argv[2]) if len(sys.argv) > 2 else 1080
H = int(sys.argv[3]) if len(sys.argv) > 3 else 1920
S = int(sys.argv[4]) if len(sys.argv) > 4 else 64
sc = lib.reset(W, H, S)
random.seed(5)

stone = lib.stone_mat('vstone', base=(0.5, 0.4, 0.3), scale=2.2, bump=0.5)
floor_m = lib.stone_mat('vfloor', base=(0.3, 0.24, 0.18), scale=1.4, bump=0.3)
iron = lib.iron_mat()
vdark = lib.stone_mat('vdark', base=(0.16, 0.12, 0.09), scale=2.2, bump=0.5)
brass = lib.brass_mat()
gold = lib.gold_mat('vgold', 0.22, (1.0, 0.7, 0.3), 0.2)

def box(name, c, s, m, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=c); o = bpy.context.object; o.name = name; o.scale = s
    bpy.ops.object.transform_apply(scale=True); o.data.materials.append(m)
    if bevel:
        b = o.modifiers.new('bev', 'BEVEL'); b.width = bevel; b.segments = 2
    return o

CW, CH = 4.0, 3.8            # corridor width, height
Y0, Y1 = -8.0, 19.0          # corridor extent
DW, DH = 1.8, 2.6           # vault door size
DOORS = [('A', -1, 2.0), ('C', 1, 5.0), ('D', -1, 8.0), ('E', 1, 11.0), ('F', -1, 14.0)]
FPS = 24

# ---------- corridor shell: walls built from ashlar blocks with door gaps ----------
def wall_x(sx, gaps):
    x = sx * (CW / 2 + 0.2)
    row_h = 0.45; rows = int(CH / row_h) + 1
    for r in range(rows):
        z = r * row_h + row_h / 2
        y = Y0 + (random.uniform(0, 0.6) if r % 2 else 0)
        while y < Y1:
            L_ = random.uniform(0.7, 1.3); yc = y + L_ / 2
            y_end = min(Y1, y + L_)
            # clip around door gaps
            segs = [(y, y_end)]
            for gy in gaps:
                a, b = gy - DW / 2 - 0.08, gy + DW / 2 + 0.08
                if z < DH + 0.05:
                    nsegs = []
                    for s0, s1 in segs:
                        if s1 <= a or s0 >= b: nsegs.append((s0, s1))
                        else:
                            if s0 < a: nsegs.append((s0, a))
                            if s1 > b: nsegs.append((b, s1))
                    segs = nsegs
            for s0, s1 in segs:
                if s1 - s0 > 0.05:
                    box('blk', (x, (s0 + s1) / 2, z), (0.4, s1 - s0 - 0.012, row_h - 0.012), stone, 0.012)
            y = y_end
for sx in (-1, 1):
    wall_x(sx, [d[2] for d in DOORS if d[1] == sx])
box('floor', (0, (Y0 + Y1) / 2, -0.05), (CW + 0.8, Y1 - Y0, 0.1), floor_m)
# floor slab seams
seam, _, _, sb = lib.mat('seam'); sb.inputs['Base Color'].default_value = (0.03, 0.025, 0.02, 1); sb.inputs['Roughness'].default_value = 1
y = Y0
while y < Y1:
    box('fs', (0, y, 0.001), (CW, 0.015, 0.004), seam); y += 1.1
box('fsc', (0, (Y0 + Y1) / 2, 0.001), (0.015, Y1 - Y0, 0.004), seam)
box('ceil', (0, (Y0 + Y1) / 2, CH + 0.1), (CW + 0.8, Y1 - Y0, 0.2), stone)
# ceiling beams
for i in range(int((Y1 - Y0) / 1.8)):
    box('beam', (0, Y0 + 0.9 + i * 1.8, CH - 0.12), (CW, 0.32, 0.28), stone, 0.02)

# ---------- vault rooms, doors, lights ----------
def gold_room(sx, yc, seed):
    """Small chamber behind the wall: a heap of coins and pots under a hot light."""
    rnd = random.Random(seed)
    x_in = sx * (CW / 2 + 0.4); depth = 3.2
    xc = x_in + sx * depth / 2
    box('rwall', (x_in + sx * depth, yc, CH / 2), (0.3, 3.6, CH), vdark)
    box('rside1', (xc, yc - 1.8, CH / 2), (depth, 0.3, CH), vdark)
    box('rside2', (xc, yc + 1.8, CH / 2), (depth, 0.3, CH), vdark)
    box('rfloor', (xc, yc, -0.05), (depth, 3.6, 0.1), floor_m)
    box('rceil', (xc, yc, CH + 0.1), (depth, 3.6, 0.2), stone)
    # heap: displaced grid in gold, coins sprinkled on it
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=60, y_segments=60, size=1.5)
    hx, hy = x_in + sx * 0.6, yc + 0.35   # heap fills the doorway; its corridor-side spill is the animated coins
    for v in bm.verts:
        r2 = (v.co.x ** 2 + v.co.y ** 2) / 1.6
        v.co.z = 1.9 * math.exp(-r2 * 1.5) + 0.04 * math.sin(v.co.x * 23 + seed) * math.sin(v.co.y * 19)
        v.co.x += hx; v.co.y += hy
        if sx * v.co.x < CW / 2 + 0.27: v.co.z = -0.06   # nothing pokes through the wall into the corridor
    lib.mesh_obj('heap', bm, gold)
    for i in range(240):
        a = rnd.random() * math.tau; r = 1.4 * math.sqrt(rnd.random())
        x, y = hx + math.cos(a) * r, hy + math.sin(a) * r
        if sx * x < CW / 2 + 0.3: continue
        z = 1.9 * math.exp(-((x - hx) ** 2 + (y - hy) ** 2) / 1.6 * 1.5)
        o = bpy.data.objects.new('coin', coin_me); lib.link(o); o.location = (x, y, z + 0.01)
        o.rotation_euler = (rnd.uniform(-0.8, 0.8), rnd.uniform(-0.8, 0.8), rnd.uniform(0, 6.3))
    for i in range(3):
        o = lib.lathe('pot', [(0, 0), (0.12, 0), (0.2, 0.12), (0.22, 0.25), (0.14, 0.38), (0.09, 0.42), (0.11, 0.47), (0, 0.5)], gold, seg=40)
        o.location = (xc + sx * rnd.uniform(-0.9, 0.3), yc + rnd.uniform(-1.3, 1.3), 0); o.scale = (1.6, 1.6, 1.6)
    l = lib.point((x_in + sx * 0.9, yc, 2.4), 0.0, (1.0, 0.66, 0.3), 0.35)
    l2 = lib.point((x_in + sx * 1.6, yc, 0.9), 0.0, (1.0, 0.6, 0.25), 0.25)
    l.visible_camera = False; l2.visible_camera = False
    return [l, l2]

bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=24, radius1=0.05, radius2=0.05, depth=0.008)
coin_me = bpy.data.meshes.new('coin'); bm.to_mesh(coin_me); bm.free(); coin_me.materials.append(lib.gold_mat('coin', 0.1, (1.0, 0.76, 0.36), 0))

def letter(ch, loc, rot, size=0.3):
    cu = bpy.data.curves.new('L', 'FONT'); cu.body = ch; cu.size = size; cu.extrude = 0.015; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    o = bpy.data.objects.new('L', cu); lib.link(o); o.location = loc; o.rotation_euler = rot; cu.materials.append(brass); return o

door_objs = []
for ch, sx, yc in DOORS:
    x = sx * (CW / 2 + 0.2)
    # frame: jambs + lintel
    for dy in (-1, 1):
        box('jamb', (x - sx * 0.02, yc + dy * (DW / 2 + 0.09), DH / 2), (0.5, 0.18, DH), stone, 0.02)
    box('lint', (x - sx * 0.02, yc, DH + 0.16), (0.5, DW + 0.4, 0.32), stone, 0.02)
    plaque = box('plq', (x - sx * 0.27, yc, DH + 0.62), (0.03, 0.5, 0.42), lib.stone_mat('plq', base=(0.22, 0.16, 0.1), scale=3, bump=0.2))
    letter(ch, (x - sx * 0.29, yc, DH + 0.62), (math.pi / 2, 0, -sx * math.pi / 2), 0.32)
    # leaf hinged at its near (camera-side, -y) edge, swings into the vault
    piv = bpy.data.objects.new('pivot', None); lib.link(piv); piv.location = (x, yc - DW / 2, 0)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0)); leaf = bpy.context.object
    leaf.scale = (0.1, DW, DH); bpy.ops.object.transform_apply(scale=True); leaf.data.materials.append(iron)
    leaf.parent = piv; leaf.location = (0, DW / 2, DH / 2)
    for zb in (0.3, DH / 2, DH - 0.3):
        bpy.ops.mesh.primitive_cube_add(size=1); b = bpy.context.object; b.scale = (0.03, DW, 0.1); bpy.ops.object.transform_apply(scale=True)
        b.data.materials.append(iron); b.parent = piv; b.location = (-sx * 0.06, DW / 2, zb)
    lights = gold_room(sx, yc, ord(ch))
    # coins that slide out over the threshold as the door opens
    rnd = random.Random(ord(ch) * 7); spill = []
    for i in range(160):
        a0_ = Vector((x + sx * rnd.uniform(0.1, 0.5), yc + rnd.uniform(-DW / 2 + 0.1, DW / 2 - 0.1), 0.006))
        d_ = rnd.uniform(0.2, 1.3) ** 1.3; ang = rnd.uniform(-0.7, 0.7)
        b0_ = Vector((x - sx * (0.3 + d_ * math.cos(ang)), yc + d_ * math.sin(ang) * 1.2, 0.006))
        o = bpy.data.objects.new('sc', coin_me); lib.link(o); o.location = a0_
        o.rotation_euler = (rnd.uniform(-0.15, 0.15), rnd.uniform(-0.15, 0.15), rnd.uniform(0, 6.3))
        spill.append((o, a0_, b0_, rnd.uniform(0.0, 0.5)))
    door_objs.append((piv, sx, lights, spill))

# ---------- far end: door B, shut, eyes in the dark ----------
yb = Y1 - 0.25
box('endwall', (0, yb + 0.2, CH / 2), (CW + 0.8, 0.4, CH), stone)
box('bdoor', (0, yb - 0.05, 1.3), (1.5, 0.1, 2.5), iron, 0.01)
for dx in (-1, 1):
    box('bjamb', (dx * 0.92, yb - 0.12, 1.35), (0.3, 0.3, 2.7), stone, 0.02)
box('blint', (0, yb - 0.12, 2.78), (2.2, 0.32, 0.36), stone, 0.02)
box('bplq', (0, yb - 0.3, 3.2), (0.5, 0.03, 0.42), lib.stone_mat('plqb', base=(0.22, 0.16, 0.1), scale=3, bump=0.2))
letter('B', (0, yb - 0.32, 3.2), (math.pi / 2, 0, 0), 0.32)
eye = lib.emit_mat('beye', (1.0, 0.06, 0.03), 6.0)
for ex in (-0.34, 0.34):
    for dx in (-0.035, 0.035):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.016, location=(ex + dx, yb - 0.12, 2.12)); bpy.context.object.data.materials.append(eye)
# bronze cobra silhouettes in low relief (simple: hood ellipsoids + S-curve body)
bronze = lib.gold_mat('vbronze', 0.38, (0.55, 0.34, 0.16), 0.5)
for ex in (-0.34, 0.34):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(ex, yb - 0.12, 1.85)); h_ = bpy.context.object; h_.scale = (0.17, 0.05, 0.3); h_.data.materials.append(bronze); bpy.ops.object.shade_smooth()
    pts = [(ex + 0.1 * math.sin(t * 5) * (1 - t), yb - 0.13, 0.35 + t * 1.25) for t in [i / 14 for i in range(15)]]
    cu = bpy.data.curves.new('b', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.04; sp = cu.splines.new('NURBS'); sp.points.add(len(pts) - 1)
    for p, co in zip(sp.points, pts): p.co = (*co, 1)
    sp.use_endpoint_u = True; o = bpy.data.objects.new('bb', cu); lib.link(o); cu.materials.append(bronze)

# ---------- corridor lamps, haze, dust ----------
for i, yy in enumerate([0.5, 3.5, 6.5, 9.5, 12.5, 16.5]):
    sx = 1 if i % 2 == 0 else -1
    o, wicks = lib.nilavilakku((sx * (CW / 2 - 0.35), yy, 0), 0.9, brass)
    for w in wicks[::2]: lib.flame(w, 1.1)
lib.point((0, Y1 - 2.0, 2.2), 6, (1, 0.5, 0.25), 0.3)   # faint warm pool before B
wn = sc.world.node_tree.nodes; wn['Background'].inputs['Color'].default_value = (0.05, 0.03, 0.02, 1); wn['Background'].inputs['Strength'].default_value = 0.05
lib.volume_box((0, (Y0 + Y1) / 2, CH / 2), (CW + 0.2, Y1 - Y0, CH), density=0.028, color=(1, 0.82, 0.62), aniso=0.55)
lib.dust((0, 4, 1.6), (1.4, 8, 1.4), 500, radius=0.003, strength=2.0, seed=9)
lib.point((0, -6.5, 3.0), 5, (1, 0.7, 0.45), 0.6)       # soft fill from behind camera

# ---------- animation ----------
TOTAL = 60
STARTS = [3, 13, 22, 31, 40]       # door opening start frames (~0.4 s apart)
OPEN_LEN = 11
P0 = Vector((0.15, -5.0, 1.5)); P1 = Vector((0.05, 3.0, 1.55))
cam = lib.camera(P0, (0, Y1, 1.6), lens=24, fstop=5.6, focus=10)

def pose(f):
    t = f / (TOTAL - 1); e = 1 - (1 - t) ** 1.6
    cam.location = P0.lerp(P1, e)
    look = Vector((0.0, Y1, 1.55))
    cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.data.dof.focus_distance = 7.0
    for (piv, sx, lights, spill), st in zip(door_objs, STARTS):
        u = min(1.0, max(0.0, (f - st) / OPEN_LEN)); k = 1 - (1 - u) ** 3
        piv.rotation_euler = (0, 0, -sx * k * math.radians(105))
        lights[0].data.energy = 420 * k ** 0.7
        lights[1].data.energy = 160 * k ** 0.7
        for o, a_, b_, dl in spill:
            v = min(1.0, max(0.0, (f - st - 2 - dl * 8) / 10.0)); v = 1 - (1 - v) ** 2
            o.location = a_.lerp(b_, v)

ANIM = os.environ.get('ANIM')
if not ANIM:
    pose(int(os.environ.get('FRAME', '45')))
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
    print('done', out)
else:
    a0, n, total = [int(v) for v in ANIM.split(',')]
    os.makedirs(out, exist_ok=True)
    for f in range(a0, min(total, a0 + n)):
        fn = os.path.join(out, 'f%04d.png' % f)
        if os.path.exists(fn): continue
        pose(f)
        sc.render.filepath = fn
        bpy.ops.render.render(write_still=True)
        print('frame', f, flush=True)
