"""Shared helpers for the Vault B Cycles scenes (bpy 5.x)."""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, Euler, Quaternion


def reset(w=1080, h=1920, samples=96):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = samples
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.02
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 8
    sc.cycles.glossy_bounces = 6
    sc.cycles.transmission_bounces = 8
    sc.cycles.volume_bounces = 1
    sc.cycles.caustics_reflective = True
    sc.cycles.caustics_refractive = True
    sc.cycles.blur_glossy = 0.6
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Khronos PBR Neutral'
    sc.view_settings.exposure = -0.4
    sc.render.image_settings.file_format = 'PNG'
    world = bpy.data.worlds.new('W'); sc.world = world
    world.use_nodes = True
    return sc


def mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes, m.node_tree.links, m.node_tree.nodes['Principled BSDF']


def gold_mat(name='gold', rough=0.17, tint=(1.0, 0.71, 0.29), scratch=0.25):
    m, N, L, b = mat(name)
    b.inputs['Base Color'].default_value = (*tint, 1)
    b.inputs['Metallic'].default_value = 1.0
    # roughness variation + fine scratches
    tc = N.new('ShaderNodeTexCoord'); nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 40; nz.inputs['Detail'].default_value = 8
    L.new(tc.outputs['Object'], nz.inputs['Vector'])
    mr = N.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = rough * 0.6; mr.inputs['To Max'].default_value = rough * 1.6
    L.new(nz.outputs['Fac'], mr.inputs['Value']); L.new(mr.outputs['Result'], b.inputs['Roughness'])
    # subtle colour variation (worn high points brighter)
    cr = N.new('ShaderNodeMix'); cr.data_type = 'RGBA'; cr.inputs['A'].default_value = (*tint, 1); cr.inputs['B'].default_value = (tint[0], tint[1] * 0.86, tint[2] * 0.7, 1)
    L.new(nz.outputs['Fac'], cr.inputs['Factor']); L.new(cr.outputs['Result'], b.inputs['Base Color'])
    if scratch:
        wv = N.new('ShaderNodeTexWave'); wv.inputs['Scale'].default_value = 60; wv.inputs['Distortion'].default_value = 30; wv.inputs['Detail'].default_value = 4
        L.new(tc.outputs['Object'], wv.inputs['Vector'])
        bm = N.new('ShaderNodeBump'); bm.inputs['Strength'].default_value = 0.04 * scratch
        L.new(wv.outputs['Fac'], bm.inputs['Height']); L.new(bm.outputs['Normal'], b.inputs['Normal'])
    return m


def gem_mat(name, color):
    m, N, L, b = mat(name)
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Transmission Weight'].default_value = 1.0
    b.inputs['Roughness'].default_value = 0.0
    b.inputs['IOR'].default_value = 1.77
    return m


def emit_mat(name, color, strength):
    m = bpy.data.materials.new(name); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links
    N.remove(N['Principled BSDF']); e = N.new('ShaderNodeEmission'); e.inputs['Color'].default_value = (*color, 1); e.inputs['Strength'].default_value = strength
    L.new(e.outputs[0], N['Material Output'].inputs['Surface']); return m


def flame_mat():
    """Candle flame: emission graded by height, transparent edges."""
    m = bpy.data.materials.new('flame'); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links
    N.remove(N['Principled BSDF'])
    tc = N.new('ShaderNodeTexCoord'); sep = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Generated'], sep.inputs[0])
    ramp = N.new('ShaderNodeValToRGB'); L.new(sep.outputs['Z'], ramp.inputs['Fac'])
    ramp.color_ramp.elements[0].color = (1.0, 0.95, 0.75, 1); ramp.color_ramp.elements[1].position = 1.0; ramp.color_ramp.elements[1].color = (1.0, 0.35, 0.05, 1)
    e = N.new('ShaderNodeEmission'); e.inputs['Strength'].default_value = 60; L.new(ramp.outputs[0], e.inputs['Color'])
    lw = N.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.35
    tr = N.new('ShaderNodeBsdfTransparent'); mix = N.new('ShaderNodeMixShader')
    L.new(lw.outputs['Facing'], mix.inputs['Fac']); L.new(e.outputs[0], mix.inputs[1]); L.new(tr.outputs[0], mix.inputs[2])
    L.new(mix.outputs[0], N['Material Output'].inputs['Surface'])
    return m


def stone_mat(name='granite', base=(0.42, 0.33, 0.25), scale=3.0, bump=0.6):
    m, N, L, b = mat(name)
    tc = N.new('ShaderNodeTexCoord')
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = scale; nz.inputs['Detail'].default_value = 12; nz.inputs['Roughness'].default_value = 0.62
    vo = N.new('ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value = scale * 18
    L.new(tc.outputs['Object'], nz.inputs['Vector']); L.new(tc.outputs['Object'], vo.inputs['Vector'])
    ramp = N.new('ShaderNodeValToRGB'); L.new(nz.outputs['Fac'], ramp.inputs['Fac'])
    ramp.color_ramp.elements[0].position = 0.3; ramp.color_ramp.elements[0].color = (base[0] * 0.55, base[1] * 0.52, base[2] * 0.5, 1)
    ramp.color_ramp.elements[1].position = 0.75; ramp.color_ramp.elements[1].color = (base[0] * 1.25, base[1] * 1.2, base[2] * 1.15, 1)
    speck = N.new('ShaderNodeMix'); speck.data_type = 'RGBA'; speck.blend_type = 'MULTIPLY'
    vr = N.new('ShaderNodeMapRange'); vr.inputs['From Min'].default_value = 0.0; vr.inputs['From Max'].default_value = 0.15; vr.inputs['To Min'].default_value = 0.55; vr.inputs['To Max'].default_value = 1.0
    L.new(vo.outputs['Distance'], vr.inputs['Value'])
    L.new(ramp.outputs[0], speck.inputs['A']); L.new(vr.outputs[0], speck.inputs['B']); speck.inputs['Factor'].default_value = 1.0
    # mix in a greyscale Value -> as color
    cv = N.new('ShaderNodeCombineColor'); L.new(vr.outputs[0], cv.inputs[0]); L.new(vr.outputs[0], cv.inputs[1]); L.new(vr.outputs[0], cv.inputs[2])
    L.new(cv.outputs[0], speck.inputs['B'])
    L.new(speck.outputs['Result'], b.inputs['Base Color'])
    rr = N.new('ShaderNodeMapRange'); rr.inputs['To Min'].default_value = 0.55; rr.inputs['To Max'].default_value = 0.95; L.new(nz.outputs['Fac'], rr.inputs['Value']); L.new(rr.outputs[0], b.inputs['Roughness'])
    bm = N.new('ShaderNodeBump'); bm.inputs['Strength'].default_value = bump; bm.inputs['Distance'].default_value = 0.02
    add = N.new('ShaderNodeMath'); add.operation = 'ADD'; L.new(nz.outputs['Fac'], add.inputs[0]); L.new(vo.outputs['Distance'], add.inputs[1])
    L.new(add.outputs[0], bm.inputs['Height']); L.new(bm.outputs['Normal'], b.inputs['Normal'])
    return m


def iron_mat(name='iron'):
    m, N, L, b = mat(name)
    tc = N.new('ShaderNodeTexCoord')
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 4; nz.inputs['Detail'].default_value = 14; nz.inputs['Roughness'].default_value = 0.65
    L.new(tc.outputs['Object'], nz.inputs['Vector'])
    fine = N.new('ShaderNodeTexNoise'); fine.inputs['Scale'].default_value = 90; fine.inputs['Detail'].default_value = 6; L.new(tc.outputs['Object'], fine.inputs['Vector'])
    ramp = N.new('ShaderNodeValToRGB'); L.new(nz.outputs['Fac'], ramp.inputs['Fac'])
    e = ramp.color_ramp.elements; e[0].position = 0.5; e[0].color = (0.03, 0.028, 0.027, 1); e[1].position = 0.78; e[1].color = (0.16, 0.065, 0.025, 1)
    L.new(ramp.outputs[0], b.inputs['Base Color'])
    mt = N.new('ShaderNodeMapRange'); mt.inputs['From Min'].default_value = 0.5; mt.inputs['From Max'].default_value = 0.7; mt.inputs['To Min'].default_value = 0.92; mt.inputs['To Max'].default_value = 0.2
    L.new(nz.outputs['Fac'], mt.inputs['Value']); L.new(mt.outputs[0], b.inputs['Metallic'])
    rr = N.new('ShaderNodeMapRange'); rr.inputs['From Min'].default_value = 0.45; rr.inputs['From Max'].default_value = 0.72; rr.inputs['To Min'].default_value = 0.32; rr.inputs['To Max'].default_value = 0.9
    L.new(nz.outputs['Fac'], rr.inputs['Value']); L.new(rr.outputs[0], b.inputs['Roughness'])
    bm = N.new('ShaderNodeBump'); bm.inputs['Strength'].default_value = 0.35; bm.inputs['Distance'].default_value = 0.01
    add = N.new('ShaderNodeMath'); add.operation = 'MULTIPLY_ADD'; L.new(fine.outputs['Fac'], add.inputs[0]); add.inputs[1].default_value = 0.4; L.new(nz.outputs['Fac'], add.inputs[2])
    L.new(add.outputs[0], bm.inputs['Height']); L.new(bm.outputs['Normal'], b.inputs['Normal'])
    return m


def brass_mat():
    return gold_mat('brass', rough=0.24, tint=(0.82, 0.56, 0.26), scratch=0.6)


def link(obj):
    bpy.context.scene.collection.objects.link(obj); return obj


def mesh_obj(name, bm, material=None, smooth=True):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); link(o)
    if smooth:
        for p in me.polygons: p.use_smooth = True
    if material: me.materials.append(material)
    return o


def lathe(name, prof, material=None, seg=64):
    """prof: list of (r, z). Returns revolved object around Z."""
    bm = bmesh.new()
    verts = [bm.verts.new((r, 0, z)) for r, z in prof]
    edges = [bm.edges.new((verts[i], verts[i + 1])) for i in range(len(verts) - 1)]
    bmesh.ops.spin(bm, geom=verts + edges, cent=(0, 0, 0), axis=(0, 0, 1), angle=math.tau, steps=seg, use_merge=True)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = mesh_obj(name, bm, material)
    return o


def add_mod_subsurf(o, lvl=2):
    m = o.modifiers.new('sub', 'SUBSURF'); m.levels = lvl; m.render_levels = lvl; return m


def camera(loc, look, lens=50, fstop=None, focus=None, sensor=24):
    cd = bpy.data.cameras.new('cam'); cd.lens = lens; cd.sensor_fit = 'HORIZONTAL'; cd.sensor_width = sensor
    c = bpy.data.objects.new('cam', cd); link(c); c.location = loc
    d = Vector(look) - Vector(loc); c.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    if fstop:
        cd.dof.use_dof = True; cd.dof.aperture_fstop = fstop; cd.dof.focus_distance = focus if focus else d.length
    bpy.context.scene.camera = c; return c


def point(loc, energy, color=(1, 0.62, 0.32), radius=0.05):
    ld = bpy.data.lights.new('pt', 'POINT'); ld.energy = energy; ld.color = color; ld.shadow_soft_size = radius
    o = bpy.data.objects.new('pt', ld); link(o); o.location = loc; return o


def spot(loc, look, energy, angle=0.6, blend=0.6, color=(1, 0.78, 0.55), radius=0.1):
    ld = bpy.data.lights.new('sp', 'SPOT'); ld.energy = energy; ld.color = color; ld.spot_size = angle; ld.spot_blend = blend; ld.shadow_soft_size = radius
    o = bpy.data.objects.new('sp', ld); link(o); o.location = loc
    o.rotation_euler = (Vector(look) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); return o


def volume_box(center, size, density=0.02, color=(1, 0.85, 0.7), aniso=0.6):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center); o = bpy.context.object; o.scale = size
    m = bpy.data.materials.new('vol'); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links; N.remove(N['Principled BSDF'])
    v = N.new('ShaderNodeVolumePrincipled'); v.inputs['Density'].default_value = density; v.inputs['Color'].default_value = (*color, 1); v.inputs['Anisotropy'].default_value = aniso
    L.new(v.outputs[0], N['Material Output'].inputs['Volume']); o.data.materials.append(m)
    o.visible_shadow = False
    return o


def dust(center, size, n, radius=0.004, strength=3.0, seed=1):
    random.seed(seed)
    bm = bmesh.new()
    for i in range(n):
        p = Vector((center[0] + random.uniform(-1, 1) * size[0], center[1] + random.uniform(-1, 1) * size[1], center[2] + random.uniform(-1, 1) * size[2]))
        r = radius * random.uniform(0.5, 1.4)
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r, matrix=Matrix.Translation(p))
    o = mesh_obj('dust', bm, emit_mat('dustm', (1, 0.8, 0.55), strength))
    o.visible_shadow = False
    return o


def flame(loc, scale=1.0, lean=(0, 0)):
    """Teardrop flame + small point light. lean = (dx, dy) tip offset per unit height."""
    prof = []
    for i in range(25):
        t = i / 24
        prof.append((0.012 * scale * math.sin(math.pi * t ** 0.55) * (1 - 0.3 * t) + 1e-4, t * 0.07 * scale))
    o = lathe('flame', prof, flame_mat(), seg=24)
    for v in o.data.vertices:
        z = v.co.z / (0.07 * scale)
        v.co.x += lean[0] * z * z * 0.07 * scale
        v.co.y += lean[1] * z * z * 0.07 * scale
    o.location = loc; o.visible_shadow = False
    l = point((loc[0] + lean[0] * 0.02, loc[1] + lean[1] * 0.02, loc[2] + 0.035 * scale), 12 * scale, radius=0.012)
    return o, l


def nilavilakku(loc, s=1.0, material=None):
    """Kerala brass oil lamp, ~0.6 m tall at s=1, five wicks on a rim."""
    material = material or brass_mat()
    k = 0.4 * s
    prof = [(0, 0), (0.5, 0), (0.52, 0.03), (0.44, 0.07), (0.3, 0.11), (0.14, 0.18), (0.1, 0.27), (0.15, 0.31), (0.09, 0.36), (0.075, 0.6), (0.11, 0.63),
            (0.08, 0.67), (0.07, 0.95), (0.12, 0.99), (0.08, 1.03), (0.075, 1.2), (0.13, 1.24), (0.12, 1.26), (0.42, 1.31), (0.47, 1.36), (0.44, 1.37), (0.12, 1.3), (0.09, 1.38),
            (0.13, 1.45), (0.07, 1.6), (0.03, 1.72), (0, 1.76)]
    o = lathe('lamp', [(r * k, z * k) for r, z in prof], material, seg=96)
    o.location = loc
    wicks = []
    for i in range(5):
        a = i / 5 * math.tau + 0.3
        p = (loc[0] + math.cos(a) * 0.42 * k, loc[1] + math.sin(a) * 0.42 * k, loc[2] + 1.37 * k)
        wicks.append(p)
    return o, wicks
