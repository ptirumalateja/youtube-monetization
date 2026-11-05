"""Shot 03: Padmanabhaswamy east gopuram at dawn over the Padma Theertham tank (Cycles).
python3 gopuram.py OUT.png [W H SAMPLES]      still
ANIM=a0,n,total python3 gopuram.py OUTDIR W H SAMPLES   frames f%04d.png (crane up off the water)

Stylised, not a survey model: seven tapering tiers with cornices, miniature-shrine parapets,
pilasters and figure niches, a barrel-vault crown with seven gold kalasams, Kerala tiled walls,
coconut palms, stepped tank. The east face catches the rising sun behind the camera.
"""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
from mathutils import Vector, Matrix, Euler
import lib

out = sys.argv[1] if len(sys.argv) > 1 else '/tmp/gopuram.png'
W = int(sys.argv[2]) if len(sys.argv) > 2 else 1080
H = int(sys.argv[3]) if len(sys.argv) > 3 else 1920
S = int(sys.argv[4]) if len(sys.argv) > 4 else 64
sc = lib.reset(W, H, S)
sc.cycles.max_bounces = 6
random.seed(3)

def grime(m, amount=0.75, dist=0.6):
    """Darken recesses with AO so carved tiers read at distance."""
    N = m.node_tree.nodes; L = m.node_tree.links; b = N['Principled BSDF']
    src = b.inputs['Base Color'].links[0].from_socket
    ao = N.new('ShaderNodeAmbientOcclusion'); ao.inputs['Distance'].default_value = dist; ao.samples = 8
    mr = N.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = 1 - amount; L.new(ao.outputs['AO'], mr.inputs['Value'])
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs['Factor'].default_value = 1.0
    L.new(src, mx.inputs['A']); cc = N.new('ShaderNodeCombineColor')
    for i in range(3): L.new(mr.outputs[0], cc.inputs[i])
    L.new(cc.outputs[0], mx.inputs['B']); L.new(mx.outputs['Result'], b.inputs['Base Color'])
    return m
stone = grime(lib.stone_mat('gstone', base=(0.5, 0.42, 0.33), scale=0.35, bump=0.35))
dark = lib.stone_mat('gdark', base=(0.2, 0.15, 0.11), scale=0.5, bump=0.2)
kgold = lib.gold_mat('kalasam', 0.2, (1.0, 0.72, 0.32), 0.1)

def box(name, c, s, m, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=c); o = bpy.context.object; o.name = name; o.scale = s
    bpy.ops.object.transform_apply(scale=True); o.data.materials.append(m)
    if bevel:
        b = o.modifiers.new('bev', 'BEVEL'); b.width = bevel; b.segments = 2
    return o

def proto(name, build):
    """Build a mesh once; return the mesh for linked-duplicate instancing."""
    bm = bmesh.new(); build(bm); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); return me

def inst(me, loc, rot=(0, 0, 0), scale=(1, 1, 1)):
    o = bpy.data.objects.new(me.name, me); lib.link(o); o.location = loc; o.rotation_euler = rot; o.scale = scale; return o

# ---------- miniature shrine (kudu / shala) for the parapets ----------
def b_shrine(bm):
    bmesh.ops.create_cube(bm, size=1, matrix=Matrix.Translation((0, 0, 0.3)) @ Matrix.Diagonal((0.8, 0.55, 0.6, 1)))
    # barrel roof: half cylinder along x
    seg = 10; r = 0.32
    ring = []
    for i in range(seg + 1):
        a = math.pi * i / seg
        ring.append((math.cos(a) * r, math.sin(a) * r * 1.15))
    for sx in (-0.42, 0.42):
        pass
    vs0 = [bm.verts.new((-0.44, y, 0.6 + z)) for y, z in ring]
    vs1 = [bm.verts.new((0.44, y, 0.6 + z)) for y, z in ring]
    for i in range(seg):
        bm.faces.new((vs0[i], vs0[i + 1], vs1[i + 1], vs1[i]))
    bm.faces.new(vs0[::-1]); bm.faces.new(vs1)
    # finial
    bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.07, radius2=0.0, depth=0.22, matrix=Matrix.Translation((0, 0, 0.6 + r * 1.15 + 0.1)))
shrine_me = proto('shrine', b_shrine); shrine_me.materials.append(stone)

def b_figure(bm):
    # a standing carved figure read at distance: body, head, arms - no face detail
    bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=8, radius=0.5, matrix=Matrix.Translation((0, 0, 0.55)) @ Matrix.Diagonal((0.32, 0.22, 0.62, 1)))
    bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=8, radius=0.14, matrix=Matrix.Translation((0, 0, 1.25)))
    bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=6, radius=0.5, matrix=Matrix.Translation((0, 0, 1.45)) @ Matrix.Diagonal((0.16, 0.14, 0.16, 1)))
    for sx in (-1, 1):
        bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=6, radius=0.5, matrix=Matrix.Translation((sx * 0.26, 0, 0.78)) @ Matrix.Diagonal((0.1, 0.1, 0.34, 1)))
fig_me = proto('figure', b_figure); fig_me.materials.append(stone)
for p in fig_me.polygons: p.use_smooth = True

# ---------- the gopuram ----------
BASE_W, BASE_D, BASE_H = 24.0, 13.0, 8.0
# plinth mouldings (adhishthana)
z = 0
for h, grow in [(0.5, 0.7), (0.35, 0.45), (0.6, 0.2), (0.3, 0.5), (0.4, 0.3)]:
    box('mould', (0, BASE_D / 2, z + h / 2), (BASE_W + grow * 2, BASE_D + grow * 2, h), stone, 0.04); z += h
box('wall', (0, BASE_D / 2, z + (BASE_H - z) / 2), (BASE_W, BASE_D, BASE_H - z), stone)
for zb in (3.2, 5.6):
    box('band', (0, BASE_D / 2, zb), (BASE_W + 0.3, BASE_D + 0.3, 0.28), stone, 0.04)
# pilasters on the base wall
for i in range(11):
    x = -BASE_W / 2 + 1.0 + i * (BASE_W - 2) / 10
    if abs(x) < 3.0: continue
    box('pil', (x, -0.12, z + (BASE_H - z) / 2), (0.55, 0.3, BASE_H - z), stone, 0.03)
# gateway: deep dark opening with lamp glow inside
GW, GH = 3.4, 6.6
box('gate', (0, 1.2, GH / 2 + 0.2), (GW, 2.6, GH), lib.emit_mat('gatelit', (1, 0.5, 0.2), 3.2))
box('gateframe_l', (-GW / 2 - 0.35, -0.15, GH / 2 + 0.2), (0.7, 0.4, GH + 0.4), stone, 0.05)
box('gateframe_r', (GW / 2 + 0.35, -0.15, GH / 2 + 0.2), (0.7, 0.4, GH + 0.4), stone, 0.05)
box('gatelintel', (0, -0.15, GH + 0.6), (GW + 1.8, 0.45, 0.6), stone, 0.05)
gl = lib.emit_mat('gateglow', (1, 0.55, 0.22), 2.2)
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 2.4, GH / 2)); g = bpy.context.object; g.scale = (GW * 0.9, GH * 0.9, 1); g.rotation_euler = (math.pi / 2, 0, 0); g.data.materials.append(gl)
for sx in (-1, 1):
    lib.point((sx * 1.2, 1.5, 1.6), 60, (1, 0.6, 0.3), 0.2)
# base cornice
box('bcorn', (0, BASE_D / 2, BASE_H + 0.2), (BASE_W + 1.2, BASE_D + 1.2, 0.45), stone, 0.06)
for i in range(13):
    x = -BASE_W / 2 + 0.6 + i * (BASE_W - 1.2) / 12
    inst(shrine_me, (x, -0.35, BASE_H + 0.42), scale=(1.5, 1.5, 1.5))

# seven tiers
z0 = BASE_H + 0.42
TIERS = 7
for k in range(TIERS):
    w = 21.0 - k * 1.9; d = 11.4 - k * 0.75; h = 2.55 - k * 0.08
    y0 = (BASE_D - d) / 2
    box('tier', (0, y0 + d / 2, z0 + h / 2), (w, d, h), stone)
    # central window column
    box('win', (0, y0 - 0.05, z0 + h * 0.48), (1.2 - k * 0.06, 0.3, h * 0.66), dark)
    box('winframe', (0, y0 - 0.25, z0 + h * 0.85), (1.8 - k * 0.06, 0.25, 0.22), stone, 0.03)
    # pilasters + figure niches across the face
    nb = max(4, int(w / 1.55))
    for i in range(nb + 1):
        x = -w / 2 + 0.35 + i * (w - 0.7) / nb
        box('tp', (x, y0 - 0.12, z0 + h / 2), (0.28, 0.28, h), stone)
        if i < nb:
            xm = x + (w - 0.7) / nb / 2
            if abs(xm) < 1.1: continue
            s_ = (h * 0.55) / 1.6
            inst(fig_me, (xm, y0 - 0.08, z0 + 0.12), rot=(0, 0, random.uniform(-0.25, 0.25)), scale=(s_, s_, s_))
    # side faces get pilasters too
    for sx in (-1, 1):
        for i in range(int(d / 1.6) + 1):
            yy = y0 + 0.3 + i * (d - 0.6) / max(1, int(d / 1.6))
            box('tps', (sx * (w / 2 + 0.1), yy, z0 + h / 2), (0.25, 0.28, h), stone)
    # cornice (kapota) with drip curve: two stacked slabs
    box('corn', (0, y0 + d / 2, z0 + h + 0.12), (w + 0.9, d + 0.9, 0.28), stone, 0.08)
    box('corn2', (0, y0 + d / 2, z0 + h + 0.32), (w + 0.5, d + 0.5, 0.14), stone, 0.04)
    # parapet of miniature shrines along front + sides
    ns = max(3, int((w + 0.4) / 1.35))
    sk = 1.15 - k * 0.04
    for i in range(ns):
        x = -w / 2 + 0.2 + i * (w - 0.4) / (ns - 1)
        inst(shrine_me, (x, y0 - 0.25, z0 + h + 0.39), scale=(sk, sk, sk))
    for sx in (-1, 1):
        for i in range(max(2, int(d / 1.5))):
            yy = y0 + 0.6 + i * (d - 1.2) / max(1, int(d / 1.5) - 1)
            inst(shrine_me, (sx * (w / 2 + 0.05), yy, z0 + h + 0.39), rot=(0, 0, math.pi / 2), scale=(sk, sk, sk))
    z0 += h + 0.39 + 0.05

# crown: barrel-vault shala roof with seven kalasams
CW = 21.0 - TIERS * 1.9 + 0.6; CD = 11.4 - TIERS * 0.75
yc = BASE_D / 2
box('crownbase', (0, yc, z0 + 0.4), (CW, CD * 0.55, 0.8), stone, 0.05)
bm = bmesh.new(); seg = 24; R = CD * 0.3
prof = []
for i in range(seg + 1):
    a = math.pi * i / seg
    prof.append((math.cos(a) * R, max(0, math.sin(a)) ** 0.8 * R * 1.35))
v0 = [bm.verts.new((-CW / 2, yc + y, z0 + 0.8 + zz)) for y, zz in prof]
v1 = [bm.verts.new((CW / 2, yc + y, z0 + 0.8 + zz)) for y, zz in prof]
for i in range(seg): bm.faces.new((v0[i], v0[i + 1], v1[i + 1], v1[i]))
bm.faces.new(v0[::-1]); bm.faces.new(v1)
crown = lib.mesh_obj('crown', bm, stone)
# horseshoe kudu gable on the front of the crown
bm = bmesh.new()
bmesh.ops.create_circle(bm, cap_ends=True, segments=32, radius=1.0, matrix=Matrix.Translation((0, yc - R - 0.05, z0 + 0.8 + R * 0.75)) @ Matrix.Rotation(math.pi / 2, 4, 'X'))
bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.25)
lib.mesh_obj('kudu', bm, dark)
ktop = z0 + 0.8 + R * 1.35
kprof = [(0, 0), (0.42, 0), (0.45, 0.08), (0.3, 0.16), (0.55, 0.5), (0.6, 0.75), (0.45, 1.0), (0.18, 1.1), (0.22, 1.25), (0.12, 1.35), (0.16, 1.5), (0.08, 1.8), (0.03, 2.3), (0, 2.45)]
for i in range(7):
    x = -CW / 2 + 0.9 + i * (CW - 1.8) / 6
    o = lib.lathe('kal', [(r * 0.75, zz * 0.75) for r, zz in kprof], kgold, seg=32); o.location = (x, yc, ktop - 0.15)

# ---------- temple walls with Kerala tiled roofs ----------
tile = lib.stone_mat('tile', base=(0.42, 0.16, 0.08), scale=2.0, bump=0.5)
for sx in (-1, 1):
    x0 = sx * (BASE_W / 2 + 0.2); x1 = sx * 70
    cx = (x0 + x1) / 2; L_ = abs(x1 - x0)
    box('twall', (cx, 6, 2.8), (L_, 1.2, 5.6), lib.stone_mat('lime', base=(0.86, 0.8, 0.7), scale=0.6, bump=0.15))
    box('tplinth', (cx, 5.8, 0.4), (L_, 1.8, 0.8), stone)
    bm = bmesh.new()
    a = bm.verts.new((x0, 4.4, 5.6)); b = bm.verts.new((x1, 4.4, 5.6)); c = bm.verts.new((x1, 7.4, 7.2)); d_ = bm.verts.new((x0, 7.4, 7.2))
    bm.faces.new((a, b, c, d_)); bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.18)
    lib.mesh_obj('troof', bm, tile, smooth=False)

# ---------- coconut palms ----------
leafm, N, L, lb = lib.mat('leaf')
lb.inputs['Base Color'].default_value = (0.08, 0.16, 0.04, 1); lb.inputs['Roughness'].default_value = 0.6
lb.inputs['Subsurface Weight'].default_value = 0.0
lb.inputs['Transmission Weight'].default_value = 0.25
barkm = lib.stone_mat('bark', base=(0.35, 0.28, 0.2), scale=6, bump=0.6)

def palm(base, height, lean, seed):
    random.seed(seed)
    pts = []
    for i in range(12):
        t = i / 11
        pts.append((base[0] + lean[0] * t * t * height, base[1] + lean[1] * t * t * height, base[2] + t * height))
    cu = bpy.data.curves.new('trunk', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.22; cu.bevel_resolution = 3
    sp = cu.splines.new('NURBS'); sp.points.add(len(pts) - 1)
    for p, co in zip(sp.points, pts): p.co = (*co, 1)
    sp.use_endpoint_u = True
    o = bpy.data.objects.new('trunk', cu); lib.link(o); cu.materials.append(barkm)
    top = Vector(pts[-1])
    bm = bmesh.new()
    for f in range(22):
        az = f / 22 * math.tau + random.uniform(-0.15, 0.15)
        el = random.uniform(-0.2, 0.9) if f % 2 else random.uniform(0.2, 1.1)
        Lf = random.uniform(3.6, 4.6)
        dirv = Vector((math.cos(az), math.sin(az), 0))
        side = Vector((-math.sin(az), math.cos(az), 0))
        prev = None
        for i in range(26):
            t = i / 25
            # drooping arc
            p = top + dirv * (Lf * t) + Vector((0, 0, Lf * (math.sin(el) * t - 0.55 * t * t)))
            nxt = top + dirv * (Lf * (t + 0.04)) + Vector((0, 0, Lf * (math.sin(el) * (t + 0.04) - 0.55 * (t + 0.04) ** 2)))
            tg = (nxt - p).normalized()
            ll = 0.95 * math.sin(math.pi * min(1, t * 1.15 + 0.05)) + 0.1
            for s_ in (-1, 1):
                tipp = p + side * s_ * ll + Vector((0, 0, -0.45 * ll)) + tg * 0.25
                v1 = bm.verts.new(p); v2 = bm.verts.new(p + tg * 0.12); v3 = bm.verts.new(tipp)
                bm.faces.new((v1, v2, v3))
    lib.mesh_obj('crown', bm, leafm, smooth=False)

palm((-17, 9, 0), 15, (0.06, 0.02), 1)
palm((-24, 12, 0), 18, (-0.08, 0.0), 2)
palm((-31, 8, 0), 13, (0.04, -0.03), 3)
palm((18, 10, 0), 16, (-0.05, 0.02), 4)
palm((26, 13, 0), 19, (0.07, 0.0), 5)
palm((33, 9, 0), 14, (-0.03, -0.02), 6)
# back rows: a dense Kerala tree line behind the walls
_r = random.Random(21)
for i in range(18):
    sx = -1 if i % 2 else 1
    x = sx * _r.uniform(13, 62); y = _r.uniform(16, 45)
    palm((x, y, 0), _r.uniform(12, 21), (_r.uniform(-0.08, 0.08), _r.uniform(-0.05, 0.05)), 100 + i)

# ---------- ground, tank steps, water ----------
box('ground', (0, 30, -0.05), (220, 50, 0.1), lib.stone_mat('earth', base=(0.45, 0.36, 0.26), scale=0.2, bump=0.2))
TANK_Y0, TANK_Y1, WZ = -5.0, -90.0, -0.55
# side steps (left/right) and far steps (nearest the gopuram)
for i in range(3):
    zz = -i * 0.2
    inset = i * 0.45
    box('stepF', (0, TANK_Y0 - inset - 0.25, zz - 0.1), (60, 0.5 + 0.0, 0.2), stone)
    for sx in (-1, 1):
        box('stepS', (sx * (22 - inset), (TANK_Y0 + TANK_Y1) / 2, zz - 0.1), (0.5, abs(TANK_Y1 - TANK_Y0), 0.2), stone)
for sx in (-1, 1):
    box('deck', (sx * 45, (TANK_Y0 + TANK_Y1) / 2, -0.1), (46, abs(TANK_Y1 - TANK_Y0), 0.2), stone)
wm, N, L, wb = lib.mat('water')
wb.inputs['Base Color'].default_value = (0.02, 0.035, 0.035, 1); wb.inputs['Roughness'].default_value = 0.02
wb.inputs['IOR'].default_value = 1.33; wb.inputs['Specular IOR Level'].default_value = 0.5
tc = N.new('ShaderNodeTexCoord'); wv = N.new('ShaderNodeTexWave'); wv.inputs['Scale'].default_value = 0.35; wv.inputs['Distortion'].default_value = 6; wv.inputs['Detail'].default_value = 6
wv.bands_direction = 'Y'
L.new(tc.outputs['Object'], wv.inputs['Vector'])
nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 1.2; nz.inputs['Detail'].default_value = 6; L.new(tc.outputs['Object'], nz.inputs['Vector'])
add = N.new('ShaderNodeMath'); add.operation = 'MULTIPLY_ADD'; L.new(wv.outputs['Fac'], add.inputs[0]); add.inputs[1].default_value = 0.6; L.new(nz.outputs['Fac'], add.inputs[2])
bmp = N.new('ShaderNodeBump'); bmp.inputs['Strength'].default_value = 0.06; bmp.inputs['Distance'].default_value = 0.05
L.new(add.outputs[0], bmp.inputs['Height']); L.new(bmp.outputs['Normal'], wb.inputs['Normal'])
WAVE = wv  # animated phase
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, (TANK_Y0 + TANK_Y1) / 2 - 3, WZ)); wp = bpy.context.object; wp.scale = (44, abs(TANK_Y1 - TANK_Y0) + 6, 1); wp.data.materials.append(wm)
# floating lotus pads near the camera side
padm, _, _, pb = lib.mat('pad'); pb.inputs['Base Color'].default_value = (0.06, 0.12, 0.03, 1); pb.inputs['Roughness'].default_value = 0.35
random.seed(11)
for i in range(26):
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=random.uniform(0.25, 0.5), depth=0.02, location=(random.uniform(-14, 10), random.uniform(-60, -40), WZ + 0.01))
    bpy.context.object.data.materials.append(padm)

# ---------- sky, sun, haze ----------
wn = sc.world.node_tree.nodes; wl = sc.world.node_tree.links
# hand-graded dawn sky looking west: peach horizon, pink Belt of Venus, soft blue above, faint cloud streaks
sun_dir = Vector((1.1, -0.75, 0.2)).normalized()   # sun low in the south-east: cornices throw shadows across the face
tcw = wn.new('ShaderNodeTexCoord'); sep = wn.new('ShaderNodeSeparateXYZ'); wl.new(tcw.outputs['Generated'], sep.inputs[0])
ramp = wn.new('ShaderNodeValToRGB'); wl.new(sep.outputs['Z'], ramp.inputs['Fac'])
el = ramp.color_ramp.elements
el[0].position = 0.0; el[0].color = (1.0, 0.74, 0.52, 1)
el[1].position = 0.45; el[1].color = (0.42, 0.56, 0.82, 1)
for pos, col in [(0.05, (1.0, 0.7, 0.6, 1)), (0.14, (0.86, 0.66, 0.72, 1)), (0.26, (0.6, 0.66, 0.85, 1))]:
    e_ = el.new(pos); e_.color = col
cl = wn.new('ShaderNodeTexNoise'); cl.inputs['Scale'].default_value = 2.2; cl.inputs['Detail'].default_value = 6
mp = wn.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1.0, 1.0, 7.0); wl.new(tcw.outputs['Generated'], mp.inputs['Vector']); wl.new(mp.outputs[0], cl.inputs['Vector'])
cr = wn.new('ShaderNodeMapRange'); cr.inputs['From Min'].default_value = 0.55; cr.inputs['From Max'].default_value = 0.75; wl.new(cl.outputs['Fac'], cr.inputs['Value'])
band = wn.new('ShaderNodeMapRange'); band.inputs['From Min'].default_value = 0.02; band.inputs['From Max'].default_value = 0.2; band.inputs['To Min'].default_value = 0.0; band.inputs['To Max'].default_value = 1.0
wl.new(sep.outputs['Z'], band.inputs['Value'])
bmul = wn.new('ShaderNodeMath'); bmul.operation = 'MULTIPLY'; wl.new(cr.outputs[0], bmul.inputs[0]); wl.new(band.outputs[0], bmul.inputs[1])
bmul2 = wn.new('ShaderNodeMath'); bmul2.operation = 'MULTIPLY'; wl.new(bmul.outputs[0], bmul2.inputs[0]); bmul2.inputs[1].default_value = 0.55
cmix = wn.new('ShaderNodeMix'); cmix.data_type = 'RGBA'; wl.new(bmul2.outputs[0], cmix.inputs['Factor']); wl.new(ramp.outputs[0], cmix.inputs['A']); cmix.inputs['B'].default_value = (1.0, 0.82, 0.72, 1)
wl.new(cmix.outputs['Result'], wn['Background'].inputs['Color']); wn['Background'].inputs['Strength'].default_value = 1.05
ld = bpy.data.lights.new('sun', 'SUN'); ld.energy = 13.0; ld.color = (1.0, 0.58, 0.3); ld.angle = math.radians(1.2)
so = bpy.data.objects.new('sun', ld); lib.link(so)
so.rotation_euler = (-sun_dir).to_track_quat('-Z', 'Y').to_euler()
lib.volume_box((0, -20, 8), (140, 120, 40), density=0.0016, color=(1, 0.86, 0.72), aniso=0.55)
lib.volume_box((0, -36, WZ + 0.5), (46, 66, 1.0), density=0.008, color=(1, 0.86, 0.7), aniso=0.4)

# ---------- camera ----------
P0 = Vector((-2.0, -64.0, WZ + 0.5)); P1 = Vector((-1.4, -55.0, WZ + 1.6))
LOOK0 = Vector((0, 4, 7.5)); LOOK1 = Vector((0, 4, 10.5))
cam = lib.camera(P0, LOOK0, lens=34, fstop=None)
sc.view_settings.exposure = -0.75

ANIM = os.environ.get('ANIM')
if not ANIM:
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
    print('done', out)
else:
    a0, n, total = [int(v) for v in ANIM.split(',')]
    os.makedirs(out, exist_ok=True)
    for f in range(a0, min(total, a0 + n)):
        fn = os.path.join(out, 'f%04d.png' % f)
        if os.path.exists(fn): continue
        t = f / max(1, total - 1); e = t * t * (3 - 2 * t)
        cam.location = P0.lerp(P1, e); look = LOOK0.lerp(LOOK1, e)
        cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
        WAVE.inputs['Phase Offset'].default_value = f / 24 * 1.4
        sc.render.filepath = fn
        bpy.ops.render.render(write_still=True)
        print('frame', f, flush=True)
