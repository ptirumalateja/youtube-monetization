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
    vo = N.new('ShaderNodeTexVoronoi'); vo.feature = 'F1'; vo.inputs['Scale'].default_value = 115; vo.inputs['Randomness'].default_value = 0.35
    L.new(tc.outputs['Object'], vo.inputs['Vector'])
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 6; nz.inputs['Detail'].default_value = 10; L.new(tc.outputs['Object'], nz.inputs['Vector'])
    ramp = N.new('ShaderNodeValToRGB'); L.new(nz.outputs['Fac'], ramp.inputs['Fac'])
    e = ramp.color_ramp.elements; e[0].position = 0.3; e[0].color = (0.2, 0.12, 0.055, 1); e[1].position = 0.7; e[1].color = (0.62, 0.4, 0.17, 1)
    ao = N.new('ShaderNodeAmbientOcclusion'); ao.inputs['Distance'].default_value = 0.03
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs['Factor'].default_value = 0.85
    L.new(ramp.outputs[0], mx.inputs['A']); L.new(ao.outputs['AO'], mx.inputs['B']); L.new(mx.outputs['Result'], b.inputs['Base Color'])
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
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -3.4, 3.45)); c = bpy.context.object; c.scale = (3.4, 7.6, 1); bpy.ops.object.transform_apply(scale=True); c.data.materials.append(stone)

# door frame: two jambs + lintel, carved granite
for sx in (-1, 1):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(sx * (DW / 2 + 0.15), 0.05, DH / 2 + 0.2)); j = bpy.context.object; j.scale = (0.3, 0.42, DH + 0.4); bpy.ops.object.transform_apply(scale=True); j.data.materials.append(stone)
    bv = j.modifiers.new('bev', 'BEVEL'); bv.width = 0.02; bv.segments = 3
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.05, DH + 0.2)); li = bpy.context.object; li.scale = (DW + 0.9, 0.46, 0.4); bpy.ops.object.transform_apply(scale=True); li.data.materials.append(stone); bv = li.modifiers.new('bev', 'BEVEL'); bv.width = 0.02; bv.segments = 3

# iron leaf with bands and rivets
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.1, DH / 2)); leaf = bpy.context.object; leaf.scale = (DW, 0.12, DH); bpy.ops.object.transform_apply(scale=True); leaf.data.materials.append(iron)
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
    # ---- hood + head: one lofted surface along a spine that rises, then bends forward out of the door ----
    nx0 = cx - 0.02 * flip; z0 = base_z + 0.96
    def spine(t):
        if t <= 0.78:
            u = t / 0.78; return Vector((nx0, -0.07 - 0.03 * math.sin(u * math.pi), z0 + u * 0.72))
        u = (t - 0.78) / 0.22; ang = u * 1.25  # bend from up toward the viewer (-y)
        R_ = 0.1; return Vector((nx0, -0.07 - R_ * (1 - math.cos(ang)) - u * 0.06, z0 + 0.72 + R_ * math.sin(ang) * 0.75))
    def half_w(t):  # sideways half-width
        if t < 0.08: return 0.045 + 0.01 * t / 0.08
        if t <= 0.78:
            u = (t - 0.08) / 0.7
            return 0.05 + 0.15 * math.sin(min(1, u ** 1.35) * math.pi) ** 0.8 if u < 0.94 else 0.07 + 0.08 * (1 - (u - 0.94) / 0.06) * 0
        u = (t - 0.78) / 0.22
        return 0.088 + 0.02 * math.sin(u * math.pi) - 0.066 * u ** 2.2
    def half_d(t):  # front-back half-thickness
        if t < 0.08: return 0.045
        if t <= 0.78:
            u = (t - 0.08) / 0.7; return 0.045 - 0.022 * math.sin(min(1, u) * math.pi) ** 0.5
        u = (t - 0.78) / 0.22; return 0.034 - 0.016 * u ** 1.6
    NT, NS = 140, 48
    bm = bmesh.new(); rows = []
    for i in range(NT + 1):
        t = i / NT; p = spine(t); tg = (spine(min(1, t + 1e-3)) - spine(max(0, t - 1e-3))).normalized()
        side = Vector((1, 0, 0)); nrm = side.cross(tg).normalized()  # 'front' axis of the section
        aw, ad = half_w(t), half_d(t)
        row = []
        for j in range(NS):
            th = j / NS * math.tau; cx_, cy_ = math.cos(th), math.sin(th)
            # superellipse: flatter edges on the hood
            ex = 2.6 if 0.15 < t < 0.75 else 2.0
            sx = math.copysign(abs(cx_) ** (2 / ex), cx_); sy = math.copysign(abs(cy_) ** (2 / ex), cy_)
            off = side * (sx * aw) + nrm * (sy * ad)
            # belly scutes: ridges down the front centre of the hood and neck
            if t < 0.76 and sy > 0.6 and abs(sx) < 0.35:
                off += nrm * (0.007 * max(0.0, math.sin(t * 170)) ** 0.5 * (1 - abs(sx) / 0.35))
            row.append(bm.verts.new(p + off))
        rows.append(row)
    for i in range(NT):
        for j in range(NS):
            bm.faces.new((rows[i][j], rows[i][(j + 1) % NS], rows[i + 1][(j + 1) % NS], rows[i + 1][j]))
    tip = bm.verts.new(spine(1.0) + (spine(1.0) - spine(0.99)).normalized() * 0.012)
    for j in range(NS): bm.faces.new((rows[NT][j], rows[NT][(j + 1) % NS], tip))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ho = lib.mesh_obj('hoodhead', bm, bronze); lib.add_mod_subsurf(ho, 1)
    # front of the body is -y: make the section 'front' face the viewer (nrm points -y when the spine is vertical)
    # eyes on both sides of the head, with brow ridges
    eye = lib.gem_mat('eye', (0.55, 0.02, 0.03)); _b = eye.node_tree.nodes['Principled BSDF']; _b.inputs['Emission Color'].default_value = (1, 0.05, 0.03, 1); _b.inputs['Emission Strength'].default_value = 1.5
    te = 0.9; pe = spine(te); tge = (spine(te + 0.01) - spine(te - 0.01)).normalized(); up = tge.cross(Vector((1, 0, 0))).normalized()
    eyes = []
    for sx_ in (-1, 1):
        ep = pe + Vector((sx_ * (half_w(te) * 0.9 + 0.004), 0, 0)) + Vector((0, -0.004, 0.016))
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0115, location=ep); e_ = bpy.context.object; e_.data.materials.append(eye); bpy.ops.object.shade_smooth()
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=ep + Vector((0, 0.002, 0.009))); br = bpy.context.object; br.scale = (0.016, 0.014, 0.006); br.data.materials.append(bronze); bpy.ops.object.shade_smooth()
        eyes.append(ep)
    return tuple(eyes[0 if flip < 0 else 1])

eyeL = cobra(-0.34, 1)
eyeR = cobra(0.34, -1)

# lamps either side of the door
lean = {'wide': 0.0, 'heads': 0.0, 'lamp': 0.9}[SHOT]
for sx in (-1, 1):
    o, wicks = lib.nilavilakku((sx * 1.15, -0.55, 0), 1.0, brass)
    for w in wicks: lib.flame(w, 1.25, lean=(-sx * lean, 0))
# warm fill from the stairwell behind camera; keeps the frame lifted
lib.spot((0.2, -6.5, 3.0), (0, 0, 1.4), 230, angle=0.5, blend=0.9, color=(1, 0.72, 0.45), radius=0.6)
lib.point((0, -1.2, 2.9), 25, (1, 0.66, 0.36), 0.2)
wn = sc.world.node_tree.nodes; wn['Background'].inputs['Color'].default_value = (0.08, 0.045, 0.025, 1); wn['Background'].inputs['Strength'].default_value = 0.3
lib.volume_box((0, -3.2, 1.7), (3.1, 7.0, 3.4), density=0.03, color=(1, 0.82, 0.62), aniso=0.55)
lib.dust((0, -1.6, 1.5), (1.2, 1.4, 1.2), 260, radius=0.0022, strength=2.2, seed=7)

if SHOT == 'wide':
    lib.camera((0.1, -4.3, 1.05), (0, 0, 1.5), lens=30, fstop=8, focus=4.3)
elif SHOT == 'heads':
    m = Vector(eyeL).lerp(Vector(eyeR), 0.5)
    lib.camera((m.x + 0.1, -1.5, m.z - 0.2), (m.x, 0, m.z - 0.16), lens=30, fstop=2.8, focus=1.32)
elif SHOT == 'lamp':
    lib.camera((1.9, -3.2, 1.25), (0.5, 0, 1.15), lens=40, fstop=2.8, focus=3.0)
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
print('done', out)
