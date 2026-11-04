"""Shot 02: the sealed cobra door of Vault B (Cycles). python3 door.py OUT.png [W H SAMPLES SHOT]
SHOT: wide (default) | heads | lamp
"""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
from mathutils import Vector, Matrix, Euler
import lib

out = sys.argv[1] if len(sys.argv) > 1 else '/tmp/door.png'
W = int(sys.argv[2]) if len(sys.argv) > 2 else 1080
H = int(sys.argv[3]) if len(sys.argv) > 3 else 1920
S = int(sys.argv[4]) if len(sys.argv) > 4 else 96
SHOT = sys.argv[5] if len(sys.argv) > 5 else 'wide'
sc = lib.reset(W, H, S)

stone = lib.stone_mat('granite', (0.26, 0.19, 0.14), scale=1.6, bump=0.5)
iron = lib.iron_mat()
brass = lib.brass_mat()

def bronze_mat():
    """Dark patinated bronze; scales via voronoi bump; polished where hands have touched (front highs)."""
    m, N, L, b = lib.mat('bronze')
    tc = N.new('ShaderNodeTexCoord')
    vo = N.new('ShaderNodeTexVoronoi'); vo.feature = 'F1'; vo.inputs['Scale'].default_value = 70; vo.inputs['Randomness'].default_value = 0.35
    L.new(tc.outputs['Object'], vo.inputs['Vector'])
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 6; nz.inputs['Detail'].default_value = 10; L.new(tc.outputs['Object'], nz.inputs['Vector'])
    ramp = N.new('ShaderNodeValToRGB'); L.new(nz.outputs['Fac'], ramp.inputs['Fac'])
    e = ramp.color_ramp.elements; e[0].position = 0.42; e[0].color = (0.05, 0.035, 0.022, 1); e[1].position = 0.66; e[1].color = (0.62, 0.38, 0.16, 1)
    L.new(ramp.outputs[0], b.inputs['Base Color'])
    b.inputs['Metallic'].default_value = 0.95
    rr = N.new('ShaderNodeMapRange'); rr.inputs['From Min'].default_value = 0.4; rr.inputs['From Max'].default_value = 0.7; rr.inputs['To Min'].default_value = 0.6; rr.inputs['To Max'].default_value = 0.22
    L.new(nz.outputs['Fac'], rr.inputs['Value']); L.new(rr.outputs[0], b.inputs['Roughness'])
    # scale relief: distance to cell centre gives domed scales
    pw = N.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = 0.6; L.new(vo.outputs['Distance'], pw.inputs[0])
    bm = N.new('ShaderNodeBump'); bm.inputs['Strength'].default_value = 0.55; bm.inputs['Distance'].default_value = 0.004; bm.invert = True
    L.new(pw.outputs[0], bm.inputs['Height']); L.new(bm.outputs['Normal'], b.inputs['Normal'])
    return m
bronze = bronze_mat()

def block_wall(x0, x1, z0, z1, y, bw=0.9, bh=0.45, depth=0.25, facing=1, along='x', seed=1):
    """Wall of bevelled granite blocks in the plane y (along x) or x (along y)."""
    random.seed(seed); bm = bmesh.new()
    row = 0; z = z0
    while z < z1:
        off = (row % 2) * bw * 0.5; x = x0 - off
        while x < x1:
            xa, xb = max(x, x0), min(x + bw, x1)
            if xb - xa > 0.06:
                w = xb - xa - 0.012; hgt = bh - 0.012; d = depth * random.uniform(0.85, 1.1)
                m = Matrix.Translation(((xa + xb) / 2, random.uniform(-0.008, 0.008) * facing, z + bh / 2)) @ Matrix.Diagonal((w, d, hgt, 1))
                bmesh.ops.create_cube(bm, size=1, matrix=m)
            x += bw
        z += bh; row += 1
    o = lib.mesh_obj('wall', bm, stone, smooth=False)
    bv = o.modifiers.new('bev', 'BEVEL'); bv.width = 0.018; bv.segments = 3; bv.limit_method = 'ANGLE'
    if along == 'x': o.location.y = y
    else: o.rotation_euler.z = math.pi / 2; o.location.x = y
    return o

def floor(x0, x1, y0, y1, s=0.8):
    random.seed(3); bm = bmesh.new(); x = x0
    while x < x1:
        yy = y0
        while yy < y1:
            m = Matrix.Translation((x + s / 2, yy + s / 2, -0.05 + random.uniform(-0.004, 0.004))) @ Matrix.Diagonal((s - 0.01, s - 0.01, 0.1, 1))
            bmesh.ops.create_cube(bm, size=1, matrix=m); yy += s
        x += s
    o = lib.mesh_obj('floor', bm, stone, smooth=False)
    bv = o.modifiers.new('bev', 'BEVEL'); bv.width = 0.012; bv.segments = 2; bv.limit_method = 'ANGLE'
    return o

# corridor: door wall at y=0, side walls at x=+-1.6, floor y from -6 to 0
DW, DH = 1.6, 2.5
block_wall(-2.2, -DW / 2 - 0.3, 0, 3.6, 0.12, seed=1)
block_wall(DW / 2 + 0.3, 2.2, 0, 3.6, 0.12, seed=2)
block_wall(-DW / 2 - 0.3, DW / 2 + 0.3, DH + 0.4, 3.6, 0.12, seed=3)
block_wall(-7, 0.3, 0, 3.6, -1.6, along='y', seed=4)
block_wall(-7, 0.3, 0, 3.6, 1.6, along='y', seed=5)
floor(-1.6, 1.6, -7, 0.3)
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -3.4, 3.45)); c = bpy.context.object; c.scale = (3.4, 7.6, 1); c.data.materials.append(stone)

# door frame: two jambs + lintel, carved granite
for sx in (-1, 1):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(sx * (DW / 2 + 0.15), 0.05, DH / 2 + 0.2)); j = bpy.context.object; j.scale = (0.3, 0.42, DH + 0.4); j.data.materials.append(stone)
    bv = j.modifiers.new('bev', 'BEVEL'); bv.width = 0.02; bv.segments = 3
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.05, DH + 0.2)); li = bpy.context.object; li.scale = (DW + 0.9, 0.46, 0.4); li.data.materials.append(stone); bv = li.modifiers.new('bev', 'BEVEL'); bv.width = 0.02; bv.segments = 3

# iron leaf with bands and rivets
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.1, DH / 2)); leaf = bpy.context.object; leaf.scale = (DW, 0.12, DH); leaf.data.materials.append(iron)
bv = leaf.modifiers.new('bev', 'BEVEL'); bv.width = 0.01; bv.segments = 2
riv = bpy.data.meshes.new('riv'); bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=8, radius=0.022); bm.to_mesh(riv); bm.free()
for p in riv.polygons: p.use_smooth = True
riv.materials.append(iron)
for zb in (0.28, DH * 0.42, DH - 0.28):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.035, zb)); b = bpy.context.object; b.scale = (DW, 0.035, 0.12); b.data.materials.append(iron)
    bv = b.modifiers.new('bev', 'BEVEL'); bv.width = 0.006; bv.segments = 2
    for i in range(15):
        o = bpy.data.objects.new('r', riv); lib.link(o); o.location = (-DW / 2 + 0.07 + i * (DW - 0.14) / 14, 0.012, zb); o.scale = (1, 0.6, 1)
for i in range(18):
    for sx in (-1, 1):
        o = bpy.data.objects.new('r', riv); lib.link(o); o.location = (sx * (DW / 2 - 0.06), 0.035, 0.12 + i * (DH - 0.24) / 17); o.scale = (1, 0.6, 1)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.035, DH / 2)); seam = bpy.context.object; seam.scale = (0.008, 0.02, DH - 0.05)
sm, _, _, sb = lib.mat('seam'); sb.inputs['Base Color'].default_value = (0.005, 0.004, 0.003, 1); sb.inputs['Roughness'].default_value = 1; seam.data.materials.append(sm)

# ---------- cobras ----------
def cobra(cx, flip):
    """Relief cobra rising from a coil; hood spread; head turned toward the other cobra. Door plane y=0.04, relief toward -y."""
    objs = []
    base_z = 0.42
    # body curve: coil then S-rise
    pts = []
    for i in range(36):
        t = i / 35; a = t * math.tau * 1.4
        pts.append((cx + flip * math.cos(a) * (0.2 - t * 0.06), -0.03 - 0.02 * math.sin(a), base_z + math.sin(a) * 0.05 + t * 0.06))
    for i in range(1, 26):
        t = i / 25
        pts.append((cx + flip * (0.12 * math.cos(t * math.pi * 1.5) - 0.02), -0.05 - t * 0.02, base_z + 0.1 + t * 0.95))
    cu = bpy.data.curves.new('body', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.042; cu.bevel_resolution = 6; cu.resolution_u = 24
    sp = cu.splines.new('NURBS'); sp.points.add(len(pts) - 1)
    for p, co in zip(sp.points, pts): p.co = (*co, 1)
    sp.use_endpoint_u = True; sp.order_u = 4
    # taper: thin tail -> thick neck
    tp = bpy.data.curves.new('taper', 'CURVE'); s2 = tp.splines.new('BEZIER'); s2.bezier_points.add(2)
    for bp, co in zip(s2.bezier_points, [(0, 0.15, 0), (0.5, 0.85, 0), (1, 1.05, 0)]): bp.co = co; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    to = bpy.data.objects.new('taperobj', tp); lib.link(to); cu.taper_object = to; to.hide_render = True
    bo = bpy.data.objects.new('body', cu); lib.link(bo); cu.materials.append(bronze)
    # hood
    outline = []
    for i in range(64):
        t = i / 64 * math.tau
        # wide hood: narrow at neck (bottom), widest 60% up, rounded top
        x = math.sin(t); y = -math.cos(t)
        k = 0.17 * (0.55 + 0.45 * (1 + y) / 2) if y < 0 else 0.17
        u = (y + 1) / 2; base = math.sin(min(1.0, u ** 1.15) * math.pi) ** 0.55; wid = 0.24 * max(0.22 if u < 0.5 else 0.36, base)
        outline.append((x * wid, y * 0.27))
    bm = bmesh.new(); vs = [bm.verts.new((x, 0, z)) for x, z in outline]; f = bm.faces.new(vs)
    bmesh.ops.triangulate(bm, faces=[f]); bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=6, use_grid_fill=True)
    for v in bm.verts:
        r = min(1, (v.co.x / 0.23) ** 2 + (v.co.z / 0.27) ** 2); v.co.y = -0.07 * (1 - r) ** 0.7
    ho = lib.mesh_obj('hood', bm, bronze)
    so = ho.modifiers.new('sol', 'SOLIDIFY'); so.thickness = 0.03; so.offset = 1
    lib.add_mod_subsurf(ho, 2)
    ho.location = (cx + flip * -0.02, -0.04, base_z + 1.12)
    # spectacle mark on the hood back is hidden; front shows ventral scutes: raised bars down the middle
    for i in range(9):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(cx + flip * -0.02, -0.15, base_z + 0.92 + i * 0.038)); sc_ = bpy.context.object
        sc_.scale = (0.075 * (1 - abs(i - 4) / 10), 0.02, 0.028); sc_.data.materials.append(bronze); bv = sc_.modifiers.new('bev', 'BEVEL'); bv.width = 0.005; bv.segments = 2
    # head: metaballs (skull + snout + brow), turned toward the other cobra
    hz = base_z + 1.42; hx = cx + flip * -0.02; d = -flip
    def blob(co, sz, rot=(0, 0, 0)):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=1, location=co); o = bpy.context.object; o.scale = sz; o.rotation_euler = rot
        bpy.ops.object.transform_apply(scale=True, rotation=False, location=False)
        o.data.materials.append(bronze); bpy.ops.object.shade_smooth(); return o
    # head faces out of the door, tilted down; eyes on the sides, snout toward the viewer
    blob((hx, -0.17, hz - 0.01), (0.062, 0.07, 0.03), (0.45, 0, 0))
    blob((hx, -0.215, hz - 0.03), (0.04, 0.045, 0.022), (0.5, 0, 0))
    blob((hx, -0.13, hz - 0.06), (0.05, 0.04, 0.07))
    # garnet eye on the visible (front) side
    eye = lib.gem_mat('eye', (0.6, 0.02, 0.03))
    [bpy.ops.mesh.primitive_uv_sphere_add(radius=0.011, location=(hx + sx_ * 0.05, -0.19, hz + 0.008)) or bpy.context.object.data.materials.append(eye) for sx_ in (-1, 1)]
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.011, location=(hx + 0.05, -0.19, hz + 0.008)); ey = bpy.context.object; ey.data.materials.append(eye); bpy.ops.object.shade_smooth()
    return (hx, -0.19, hz + 0.008)

eyeL = cobra(-0.34, 1)
eyeR = cobra(0.34, -1)

# lamps either side of the door
lean = {'wide': 0.0, 'heads': 0.0, 'lamp': 0.9}[SHOT]
for sx in (-1, 1):
    o, wicks = lib.nilavilakku((sx * 1.15, -0.55, 0), 1.0, brass)
    for w in wicks: lib.flame(w, 1.25, lean=(-sx * lean, 0))
# warm fill from the stairwell behind camera; keeps the frame lifted
lib.spot((0.2, -6.5, 3.0), (0, 0, 1.4), 380, angle=0.5, blend=0.9, color=(1, 0.72, 0.45), radius=0.6)
lib.point((0, -1.2, 2.9), 25, (1, 0.66, 0.36), 0.2)
wn = sc.world.node_tree.nodes; wn['Background'].inputs['Color'].default_value = (0.08, 0.045, 0.025, 1); wn['Background'].inputs['Strength'].default_value = 0.3
lib.volume_box((0, -3.2, 1.7), (3.1, 7.0, 3.4), density=0.03, color=(1, 0.82, 0.62), aniso=0.55)
lib.dust((0, -1.6, 1.5), (1.2, 1.4, 1.2), 260, radius=0.0022, strength=2.2, seed=7)

if SHOT == 'wide':
    lib.camera((0.1, -4.3, 1.05), (0, 0, 1.5), lens=30, fstop=8, focus=4.3)
elif SHOT == 'heads':
    m = Vector(eyeL).lerp(Vector(eyeR), 0.5)
    lib.camera((m.x + 0.1, -1.5, m.z - 0.2), (m.x, 0, m.z - 0.16), lens=38, fstop=2.8, focus=1.32)
elif SHOT == 'lamp':
    lib.camera((1.9, -3.2, 1.25), (0.5, 0, 1.15), lens=40, fstop=2.8, focus=3.0)
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
print('done', out)
