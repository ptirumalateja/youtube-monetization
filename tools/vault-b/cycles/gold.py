"""Shot 01: inside a mountain of temple gold (Cycles). python3 gold.py OUT.png [W H SAMPLES]"""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
from mathutils import Vector, Matrix, Euler, Quaternion
from PIL import Image, ImageDraw, ImageFilter
import lib

out = sys.argv[1] if len(sys.argv) > 1 else '/tmp/gold.png'
W = int(sys.argv[2]) if len(sys.argv) > 2 else 1080
H = int(sys.argv[3]) if len(sys.argv) > 3 else 1920
S = int(sys.argv[4]) if len(sys.argv) > 4 else 96
sc = lib.reset(W, H, S)
HERE = os.path.dirname(os.path.abspath(__file__))

# ---------- coin relief heightmap ----------
hm_path = os.path.join(HERE, 'coin_height.png')
if not os.path.exists(hm_path):
    im = Image.new('L', (512, 512), 90); d = ImageDraw.Draw(im)
    d.ellipse((14, 14, 498, 498), outline=230, width=22)
    d.ellipse((60, 60, 452, 452), outline=170, width=6)
    for i in range(56):
        a = i / 56 * math.tau; x, y = 256 + math.cos(a) * 214, 256 + math.sin(a) * 214; d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=200)
    # conch (Travancore coins carry a sankha)
    d.ellipse((170, 140, 330, 380), fill=200); d.ellipse((205, 170, 300, 340), fill=120); d.ellipse((222, 190, 290, 320), fill=210)
    d.polygon([(200, 360), (310, 360), (256, 430)], fill=200)
    for k in range(4): d.arc((180 + k * 12, 150 + k * 14, 320 - k * 12, 360 - k * 14), 200, 340, fill=240, width=5)
    im = im.filter(ImageFilter.GaussianBlur(2.2)); im.save(hm_path)
hm = bpy.data.images.load(hm_path); hm.colorspace_settings.name = 'Non-Color'

def coin_material(name, rough, tint):
    m = lib.gold_mat(name, rough, tint, scratch=0.4)
    N = m.node_tree.nodes; L = m.node_tree.links; b = N['Principled BSDF']
    tc = N.new('ShaderNodeTexCoord'); tex = N.new('ShaderNodeTexImage'); tex.image = hm; tex.extension = 'CLIP'
    L.new(tc.outputs['UV'], tex.inputs['Vector'])
    bm = N.new('ShaderNodeBump'); bm.inputs['Strength'].default_value = 0.9; bm.inputs['Distance'].default_value = 0.0006
    L.new(tex.outputs['Color'], bm.inputs['Height']); L.new(bm.outputs['Normal'], b.inputs['Normal'])
    return m

R = 0.012; T = 0.0019
def coin_mesh(name, material):
    bm = bmesh.new()
    prof = [(0, T / 2), (R * 0.86, T / 2), (R * 0.93, T * 0.62), (R * 0.995, T * 0.55), (R, 0), (R * 0.995, -T * 0.55), (R * 0.93, -T * 0.62), (R * 0.86, -T / 2), (0, -T / 2)]
    verts = [bm.verts.new((r, 0, z)) for r, z in prof]
    edges = [bm.edges.new((verts[i], verts[i + 1])) for i in range(len(verts) - 1)]
    bmesh.ops.spin(bm, geom=verts + edges, cent=(0, 0, 0), axis=(0, 0, 1), angle=math.tau, steps=48, use_merge=True)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)
    uv = bm.loops.layers.uv.new()
    for f in bm.faces:
        for l in f.loops:
            x, y = l.vert.co.x, l.vert.co.y
            l[uv].uv = (x / (2 * R) + 0.5, (y if l.vert.co.z > 0 else -y) / (2 * R) + 0.5)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    me.materials.append(material)
    return me

coinA = coin_mesh('coinA', coin_material('coinA', 0.14, (1.0, 0.72, 0.30)))
coinB = coin_mesh('coinB', coin_material('coinB', 0.22, (1.0, 0.66, 0.26)))
coinC = coin_mesh('coinC', coin_material('coinC', 0.12, (1.0, 0.78, 0.40)))
coins = [coinA, coinB, coinC]

def heap(cx, cy, rad, height, n, seed):
    random.seed(seed)
    def h(x, y):
        r2 = ((x - cx) ** 2 + (y - cy) ** 2) / (rad * rad)
        return height * math.exp(-r2 * 2.2)
    # gold mound underneath (so gaps read as gold)
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=120, y_segments=120, size=rad * 1.7)
    for v in bm.verts: v.co.x += cx; v.co.y += cy; v.co.z = h(v.co.x, v.co.y) - T * 2.5
    lib.mesh_obj('mound', bm, lib.gold_mat('mound', 0.4, (0.75, 0.5, 0.2), 0))
    col = bpy.data.collections.new('heap%d' % seed); sc.collection.children.link(col)
    for i in range(n):
        a = random.random() * math.tau; r = rad * 1.3 * math.sqrt(random.random())
        x, y = cx + math.cos(a) * r, cy + math.sin(a) * r
        e = 0.002; nrm = Vector((h(x - e, y) - h(x + e, y), h(x, y - e) - h(x, y + e), 2 * e)).normalized()
        q = Vector((0, 0, 1)).rotation_difference(nrm) @ Euler((random.uniform(-0.6, 0.6), random.uniform(-0.6, 0.6), random.uniform(0, 6.28))).to_quaternion()
        o = bpy.data.objects.new('c', random.choice(coins)); col.objects.link(o)
        o.location = (x, y, h(x, y) + random.uniform(-0.3, 1.0) * T)
        o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = q
        s = random.uniform(0.92, 1.08); o.scale = (s, s, s)
    return h

h0 = heap(0.0, 0.0, 0.24, 0.13, 4400, 1)
heap(-0.34, 0.32, 0.26, 0.2, 4200, 2)
heap(0.36, 0.42, 0.3, 0.24, 4200, 3)
heap(0.05, 0.8, 0.4, 0.3, 3000, 4)

# ---------- treasures ----------
gold = lib.gold_mat('gold', 0.12, (1.0, 0.74, 0.32))
ruby = lib.gem_mat('ruby', (0.8, 0.02, 0.05)); emer = lib.gem_mat('emerald', (0.03, 0.6, 0.18)); dia = lib.gem_mat('diamond', (1, 1, 1))

def crown(loc, s, rot):
    parts = []
    band = lib.lathe('band', [(0.5, 0), (0.53, 0.02), (0.53, 0.06), (0.51, 0.08), (0.52, 0.22), (0.56, 0.26), (0.56, 0.31), (0.5, 0.31)], gold, 96); parts.append(band)
    for i in range(12):
        a = i / 12 * math.tau
        sp = lib.lathe('sp', [(0, 0), (0.08, 0), (0.06, 0.1), (0.1, 0.18), (0.05, 0.3), (0.06, 0.36), (0.02, 0.48), (0, 0.52)], gold, 24)
        sp.location = (math.cos(a) * 0.52, math.sin(a) * 0.52, 0.29); sp.rotation_euler = (-math.sin(a) * 0.18, math.cos(a) * 0.18, 0); parts.append(sp)
        g = bpy.data.objects.new('gem', bpy.data.meshes.new('g')); lib.link(g)
        bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.05); bm.to_mesh(g.data); bm.free(); g.data.materials.append([ruby, emer, dia][i % 3])
        g.location = (math.cos(a + 0.26) * 0.545, math.sin(a + 0.26) * 0.545, 0.15); g.scale = (0.5, 0.5, 0.75) if i % 3 else (0.6, 0.6, 0.6); parts.append(g)
    top = lib.lathe('top', [(0, 0), (0.2, 0), (0.14, 0.12), (0.18, 0.24), (0.1, 0.38), (0.12, 0.44), (0.04, 0.6), (0, 0.66)], gold, 48); top.location = (0, 0, 0.55); parts.append(top)
    for i in range(4):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.5, minor_radius=0.022, major_segments=64, minor_segments=12, location=(0, 0, 0.3), rotation=(math.pi / 2, 0, i * math.pi / 4))
        t = bpy.context.object; t.scale = (1, 0.75, 1); t.data.materials.append(gold)
        bpy.ops.object.shade_smooth(); parts.append(t)
    root = bpy.data.objects.new('crown', None); lib.link(root)
    for p in parts: p.parent = root
    root.location = loc; root.scale = (s, s, s); root.rotation_euler = rot
    return root

# hero: tall temple kalasam with a ring of rubies
kal = lib.lathe('kal', [(0, 0), (0.30, 0), (0.33, 0.03), (0.3, 0.06), (0.2, 0.1), (0.22, 0.14), (0.44, 0.3), (0.5, 0.45), (0.47, 0.6), (0.36, 0.74), (0.2, 0.82), (0.17, 0.86), (0.24, 0.9), (0.24, 0.94),
    (0.14, 0.97), (0.11, 1.1), (0.17, 1.16), (0.17, 1.2), (0.09, 1.24), (0.1, 1.36), (0.06, 1.5), (0.03, 1.66), (0, 1.72)], gold, 128)
kal.location = (0.1, 0.16, 0.035); kal.scale = (0.11, 0.11, 0.11); kal.rotation_euler = (0.1, -0.15, 0)
for i in range(14):
    a = i / 14 * math.tau
    g_ = bpy.data.objects.new('gem', bpy.data.meshes.new('g')); lib.link(g_)
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.028); bm.to_mesh(g_.data); bm.free(); g_.data.materials.append([ruby, ruby, emer][i % 3])
    for p in g_.data.polygons: p.use_smooth = False
    g_.parent = kal; g_.location = (math.cos(a) * 0.49, math.sin(a) * 0.49, 0.45); g_.scale = (0.8, 0.8, 1.1)
bpy.ops.mesh.primitive_torus_add(major_radius=0.5, minor_radius=0.025, major_segments=96, minor_segments=12, location=(0, 0, 0.45)); t = bpy.context.object; t.data.materials.append(gold); bpy.ops.object.shade_smooth(); t.parent = kal
for zz, rr_ in ((0.3, 0.44), (0.6, 0.47)):
    bpy.ops.mesh.primitive_torus_add(major_radius=rr_, minor_radius=0.012, major_segments=96, minor_segments=8, location=(0, 0, zz)); t = bpy.context.object; t.data.materials.append(gold); bpy.ops.object.shade_smooth(); t.parent = kal

def pot(loc, s, rot, mat_):
    o = lib.lathe('pot', [(0, 0), (0.28, 0), (0.3, 0.04), (0.5, 0.25), (0.58, 0.5), (0.52, 0.76), (0.32, 0.92), (0.26, 0.98), (0.34, 1.05), (0.37, 1.1), (0.33, 1.12), (0.26, 1.06), (0, 1.06)], mat_, 96)
    o.location = loc; o.scale = (s, s, s); o.rotation_euler = rot; return o

pot((-0.2, 0.18, 0.08), 0.09, (0.15, 0.25, 0), gold)
pot((0.3, 0.52, 0.16), 0.11, (-0.4, 0.5, 0), lib.gold_mat('gold2', 0.26, (1.0, 0.68, 0.28)))
pot((-0.45, 0.55, 0.15), 0.12, (0, 0, 0), gold)

# chain draped over the front heap
def chain(points, link_r=0.006, n=160):
    from mathutils import geometry
    curve = bpy.data.curves.new('ch', 'CURVE'); curve.dimensions = '3D'; sp = curve.splines.new('BEZIER'); sp.bezier_points.add(len(points) - 1)
    for bp, p in zip(sp.bezier_points, points): bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    co = bpy.data.objects.new('chcurve', curve); lib.link(co)
    dg = bpy.context.evaluated_depsgraph_get(); bpy.context.view_layer.update()
    me = co.evaluated_get(dg).to_mesh(); pts = [co.matrix_world @ v.co for v in me.vertices]
    # resample
    L = [0]; [L.append(L[-1] + (pts[i + 1] - pts[i]).length) for i in range(len(pts) - 1)]
    total = L[-1]; step = link_r * 2.3; k = 0; res = []
    d = 0
    while d < total:
        while L[k + 1] < d: k += 1
        t = (d - L[k]) / max(1e-9, L[k + 1] - L[k]); res.append((pts[k].lerp(pts[k + 1], t), (pts[k + 1] - pts[k]).normalized())); d += step
    bpy.data.objects.remove(co)
    bpy.ops.mesh.primitive_torus_add(major_radius=link_r, minor_radius=link_r * 0.3, major_segments=24, minor_segments=8)
    lk = bpy.context.object; lk.scale = (1.5, 1, 1); bpy.ops.object.transform_apply(scale=True); lk.data.materials.append(gold); bpy.ops.object.shade_smooth()
    lme = lk.data; bpy.data.objects.remove(lk)
    for i, (p, tdir) in enumerate(res):
        o = bpy.data.objects.new('lk', lme); lib.link(o); o.location = p
        q = Vector((1, 0, 0)).rotation_difference(tdir) @ Quaternion((1, 0, 0), (math.pi / 2) * (i % 2))
        o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = q

chain([(-0.16, -0.1, h0(-0.16, -0.1) + 0.004), (-0.05, -0.05, h0(-0.05, -0.05) + 0.004), (0.06, -0.03, h0(0.06, -0.03) + 0.005), (0.15, -0.09, h0(0.15, -0.09) + 0.004), (0.22, -0.18, h0(0.22, -0.18) + 0.003)])

# loose rubies scattered on the heap in front of the kalasam
random.seed(5)
for i in range(18):
    x, y = random.uniform(-0.08, 0.2), random.uniform(0.0, 0.14)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=random.uniform(0.006, 0.01), location=(x, y, h0(x, y) + 0.004)); gm_ = bpy.context.object
    gm_.data.materials.append([ruby, ruby, emer, dia][i % 4]); gm_.rotation_euler = (random.random() * 3, random.random() * 3, 0)
# tumbling coins in the air (frozen mid-fall)
random.seed(9)
for i in range(30):
    o = bpy.data.objects.new('fall', random.choice(coins)); lib.link(o)
    o.location = (random.uniform(-0.15, 0.22), random.uniform(-0.05, 0.3), random.uniform(0.16, 0.36)); o.rotation_euler = (random.uniform(0, 6), random.uniform(0, 6), random.uniform(0, 6))

# ---------- vault: granite walls, lamps ----------
stone = lib.stone_mat('granite', (0.2, 0.14, 0.1), scale=2.5)
bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0, -0.02)); bpy.context.object.data.materials.append(stone)
bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 2.2, 1.0), rotation=(math.pi / 2, 0, 0)); bpy.context.object.data.materials.append(stone)
brass = lib.brass_mat()
for (x, y, s) in [(-0.55, 1.15, 0.8), (0.65, 1.25, 0.9), (0.05, 1.45, 0.8), (-1.0, 0.7, 0.9), (1.0, 0.8, 0.8)]:
    o, wicks = lib.nilavilakku((x, y, 0), s * 0.75, brass)
    for w in wicks: lib.flame(w, 0.9)

# key + fill
lib.spot((-0.7, 0.9, 0.9), (0.08, 0.15, 0.12), 160, angle=0.45, blend=0.7, color=(1, 0.78, 0.5), radius=0.08)
lib.spot((0.4, -0.9, 0.9), (0.08, 0.15, 0.12), 45, angle=0.4, blend=0.9, color=(1, 0.82, 0.62), radius=0.3)
lib.point((0.6, -0.4, 0.25), 9, (1, 0.6, 0.3), 0.02)
lib.point((-0.5, -0.3, 0.2), 6, (1, 0.6, 0.3), 0.02)
lib.point((0.0, 0.5, 0.6), 14, (1, 0.62, 0.32), 0.05)
# warm world bounce, never black
wn = sc.world.node_tree.nodes; wn['Background'].inputs['Color'].default_value = (0.09, 0.05, 0.025, 1); wn['Background'].inputs['Strength'].default_value = 0.2
lib.volume_box((0, 0.5, 0.6), (4, 4, 1.4), density=0.012, color=(1, 0.8, 0.6), aniso=0.6)
lib.dust((0.05, 0.25, 0.3), (0.4, 0.4, 0.25), 500, radius=0.0012, strength=6, seed=4)

lib.camera((-0.02, -0.34, 0.25), (0.08, 0.16, 0.1), lens=40, fstop=4.0, focus=0.56)
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
print('done', out)
