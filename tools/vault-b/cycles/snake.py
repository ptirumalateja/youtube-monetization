"""Living cobra for the Vault B Cycles scenes. A spine (list of points, tail -> snout) is lofted into one mesh:
round body, flattened hood, head with a hinged lower jaw, plus eyes, fangs, pink mouth and a forked tongue.
Call Cobra(...).update(points, hood=0..1, jaw=0..1, tongue=0..1) once per frame."""
import bpy, bmesh, math
from mathutils import Vector, Matrix, Quaternion
import lib


def skin_mat(name='cobra_skin', dorsal=(0.035, 0.028, 0.02), belly=(0.55, 0.45, 0.3), band=(0.05, 0.035, 0.025), scale_n=60.0):
    """Glossy dark dorsal scales, cream ventral plates with dark throat bands. Uses UV: u around (0..1, 0.25 = belly), v along length."""
    m, N, L, b = lib.mat(name)
    uv = N.new('ShaderNodeUVMap'); sep = N.new('ShaderNodeSeparateXYZ'); L.new(uv.outputs['UV'], sep.inputs[0])
    # belly mask from u: cos(2pi(u-0.25)) > 0.55
    m1 = N.new('ShaderNodeMath'); m1.operation = 'SUBTRACT'; L.new(sep.outputs['X'], m1.inputs[0]); m1.inputs[1].default_value = 0.25
    m2 = N.new('ShaderNodeMath'); m2.operation = 'MULTIPLY'; L.new(m1.outputs[0], m2.inputs[0]); m2.inputs[1].default_value = math.tau
    m3 = N.new('ShaderNodeMath'); m3.operation = 'COSINE'; L.new(m2.outputs[0], m3.inputs[0])
    bm_ = N.new('ShaderNodeMapRange'); bm_.inputs['From Min'].default_value = 0.45; bm_.inputs['From Max'].default_value = 0.7; L.new(m3.outputs[0], bm_.inputs['Value'])
    # scale pattern: voronoi on (u*scale_n, v*scale_n*?) -> v is already in 'circumference units'
    cmb = N.new('ShaderNodeCombineXYZ'); mu = N.new('ShaderNodeMath'); mu.operation = 'MULTIPLY'; L.new(sep.outputs['X'], mu.inputs[0]); mu.inputs[1].default_value = scale_n
    mv = N.new('ShaderNodeMath'); mv.operation = 'MULTIPLY'; L.new(sep.outputs['Y'], mv.inputs[0]); mv.inputs[1].default_value = scale_n
    L.new(mu.outputs[0], cmb.inputs['X']); L.new(mv.outputs[0], cmb.inputs['Y'])
    vo = N.new('ShaderNodeTexVoronoi'); vo.feature = 'DISTANCE_TO_EDGE'; vo.inputs['Scale'].default_value = 1.0; vo.inputs['Randomness'].default_value = 0.25
    L.new(cmb.outputs[0], vo.inputs['Vector'])
    # ventral plates: bands along v on the belly
    wv = N.new('ShaderNodeTexWave'); wv.wave_type = 'BANDS'; wv.bands_direction = 'Y'; wv.inputs['Scale'].default_value = 1.0; wv.inputs['Distortion'].default_value = 0.0
    pv = N.new('ShaderNodeCombineXYZ'); pm = N.new('ShaderNodeMath'); pm.operation = 'MULTIPLY'; L.new(sep.outputs['Y'], pm.inputs[0]); pm.inputs[1].default_value = scale_n * 0.18
    L.new(pm.outputs[0], pv.inputs['Y']); L.new(pv.outputs[0], wv.inputs['Vector'])
    # colours
    dn = N.new('ShaderNodeTexNoise'); dn.inputs['Scale'].default_value = 3; L.new(uv.outputs['UV'], dn.inputs['Vector'])
    dr = N.new('ShaderNodeValToRGB'); L.new(dn.outputs['Fac'], dr.inputs['Fac']); e = dr.color_ramp.elements
    e[0].position = 0.35; e[0].color = (*dorsal, 1); e[1].position = 0.75; e[1].color = (dorsal[0] * 2.2, dorsal[1] * 1.9, dorsal[2] * 1.5, 1)
    # throat bands: dark rings on the belly at given v ranges (Z of attribute 'band' baked into vertex colour)
    attr = N.new('ShaderNodeAttribute'); attr.attribute_name = 'band'
    bel = N.new('ShaderNodeMix'); bel.data_type = 'RGBA'; bel.inputs['A'].default_value = (*belly, 1); bel.inputs['B'].default_value = (*band, 1)
    L.new(attr.outputs['Fac'], bel.inputs['Factor'])
    mix = N.new('ShaderNodeMix'); mix.data_type = 'RGBA'; L.new(bm_.outputs[0], mix.inputs['Factor']); L.new(dr.outputs[0], mix.inputs['A']); L.new(bel.outputs['Result'], mix.inputs['B'])
    # scale edges darker
    ed = N.new('ShaderNodeMapRange'); ed.inputs['From Min'].default_value = 0.0; ed.inputs['From Max'].default_value = 0.12; ed.inputs['To Min'].default_value = 0.45; ed.inputs['To Max'].default_value = 1.0
    L.new(vo.outputs['Distance'], ed.inputs['Value'])
    mul = N.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs['Factor'].default_value = 1.0
    L.new(mix.outputs['Result'], mul.inputs['A']); cc = N.new('ShaderNodeCombineColor'); [L.new(ed.outputs[0], cc.inputs[i]) for i in range(3)]; L.new(cc.outputs[0], mul.inputs['B'])
    L.new(mul.outputs['Result'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.32; b.inputs['Coat Weight'].default_value = 0.6; b.inputs['Coat Roughness'].default_value = 0.12
    b.inputs['Specular IOR Level'].default_value = 0.6
    # bump: domed scales (dorsal) / plates (belly)
    pw = N.new('ShaderNodeMath'); pw.operation = 'POWER'; L.new(vo.outputs['Distance'], pw.inputs[0]); pw.inputs[1].default_value = 0.5
    hb = N.new('ShaderNodeMix'); hb.data_type = 'FLOAT'; L.new(bm_.outputs[0], hb.inputs['Factor']); L.new(pw.outputs[0], hb.inputs['A']); L.new(wv.outputs['Fac'], hb.inputs['B'])
    bump = N.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.55; bump.inputs['Distance'].default_value = 0.002
    L.new(hb.outputs['Result'], bump.inputs['Height']); L.new(bump.outputs['Normal'], b.inputs['Normal'])
    return m


def _resample(pts, n):
    L = [0.0]
    for i in range(len(pts) - 1): L.append(L[-1] + (pts[i + 1] - pts[i]).length)
    tot = L[-1]; out = []; k = 0
    for i in range(n):
        d = tot * i / (n - 1)
        while k < len(L) - 2 and L[k + 1] < d: k += 1
        t = (d - L[k]) / max(1e-9, L[k + 1] - L[k]); out.append(pts[k].lerp(pts[k + 1], t))
    return out, tot


class Cobra:
    def __init__(self, name, R, material=None, NT=260, NS=40, belly_up=Vector((0, -1, 0)), bands=((0.80, 0.83), (0.85, 0.87))):
        """R = body radius at the thickest point (m). belly_up: where the belly faces at the tail start (sets the frame)."""
        self.R, self.NT, self.NS, self.bands, self.b0 = R, NT, NS, bands, belly_up
        self.mat = material or skin_mat()
        me = bpy.data.meshes.new(name); self.obj = bpy.data.objects.new(name, me); lib.link(self.obj); me.materials.append(self.mat)
        lib.add_mod_subsurf(self.obj, 1)
        self.obj.data.attributes.new('band', 'FLOAT', 'POINT') if 'band' not in me.attributes else None
        eye, _, _, eb = lib.mat(name + '_eye'); eb.inputs['Base Color'].default_value = (0.004, 0.003, 0.002, 1); eb.inputs['Roughness'].default_value = 0.03; eb.inputs['Coat Weight'].default_value = 1.0
        mouth, _, _, mb = lib.mat(name + '_mouth'); mb.inputs['Base Color'].default_value = (0.55, 0.16, 0.16, 1); mb.inputs['Roughness'].default_value = 0.25; mb.inputs['Subsurface Weight'].default_value = 0.3
        fang, _, _, fb = lib.mat(name + '_fang'); fb.inputs['Base Color'].default_value = (0.9, 0.86, 0.75, 1); fb.inputs['Roughness'].default_value = 0.2
        self.eye_m, self.mouth_m, self.fang_m = eye, mouth, fang
        self.parts = {}
        for k, mt in (('eyeL', eye), ('eyeR', eye), ('mouth', mouth), ('fangL', fang), ('fangR', fang), ('tongue', mouth)):
            o = bpy.data.objects.new(name + k, bpy.data.meshes.new(name + k)); lib.link(o); o.data.materials.append(mt); self.parts[k] = o

    # cross-section half sizes (lateral w, dorso-ventral d) as a function of s in [0,1], tail -> snout
    def section(self, s, hood):
        R = self.R
        if s < 0.62: r = R * (0.12 + 0.88 * min(1, s / 0.45) ** 0.6); return r, r
        if s < 0.9:   # neck + hood
            u = (s - 0.62) / 0.28; flare = math.sin(min(1, u / 0.85) * math.pi) ** 0.7 if u < 0.85 else 0.25 * (1 - (u - 0.85) / 0.15) + 0.0
            w = R * (1 + hood * 2.3 * flare); d = R * (1 - hood * 0.45 * flare); return w, d
        u = (s - 0.9) / 0.1  # head: broad jaws, tapering snout
        w = R * (0.95 + 0.25 * math.sin(min(1, u * 1.6) * math.pi * 0.5) - 0.75 * u ** 2.2); d = R * (0.62 - 0.32 * u ** 1.8)
        return max(w, R * 0.18), max(d, R * 0.14)

    def update(self, pts, hood=1.0, jaw=0.0, tongue=0.0, tongue_phase=0.0):
        pts, length = _resample([Vector(p) for p in pts], self.NT + 1)
        T = [(pts[min(i + 1, self.NT)] - pts[max(i - 1, 0)]).normalized() for i in range(self.NT + 1)]
        # parallel-transport frame; n = belly direction
        n = (self.b0 - T[0] * self.b0.dot(T[0])).normalized(); frames = []
        for i in range(self.NT + 1):
            if i: q = T[i - 1].rotation_difference(T[i]); n = (q @ n); n = (n - T[i] * n.dot(T[i])).normalized()
            frames.append((T[i], n, T[i].cross(n).normalized()))
        circ = 2 * math.pi * self.R
        s_h = 0.935; ih = int(s_h * self.NT); hinge = pts[ih]; side_h = frames[ih][2]
        jq = Quaternion(side_h, -jaw * 0.85)
        bm = bmesh.new(); uvl = bm.loops.layers.uv.new(); bl = bm.verts.layers.float.new('band'); rows = []
        for i in range(self.NT + 1):
            s = i / self.NT; t, nb, sd = frames[i]; w, d = self.section(s, hood); row = []
            for j in range(self.NS):
                th = j / self.NS * math.tau; c, sn = math.cos(th), math.sin(th)
                ex = 2.4 if 0.66 < s < 0.9 else 2.0
                sx = math.copysign(abs(c) ** (2 / ex), c); sy = math.copysign(abs(sn) ** (2 / ex), sn)
                off = sd * (sx * w) + nb * (sy * d)
                p = pts[i] + off
                if s > s_h and sn > 0.05 and jaw > 0:   # lower jaw: belly half of the head swings open about the hinge
                    k = min(1, (s - s_h) / 0.02) * min(1, sn / 0.4); p = hinge + Quaternion(side_h, -jaw * 0.85 * k) @ (p - hinge)
                v = bm.verts.new(p); inb = any(a < s < b_ for a, b_ in self.bands); v[bl] = 1.0 if inb else 0.0; row.append((v, j / self.NS, s * length / circ))
            rows.append(row)
        for i in range(self.NT):
            for j in range(self.NS):
                a, b_, c_, d_ = rows[i][j], rows[i][(j + 1) % self.NS], rows[i + 1][(j + 1) % self.NS], rows[i + 1][j]
                f = bm.faces.new((a[0], b_[0], c_[0], d_[0]))
                us = [a[1], b_[1] if j + 1 < self.NS else 1.0, b_[1] if j + 1 < self.NS else 1.0, a[1]]
                for l, uu, vv in zip(f.loops, us, (a[2], b_[2], c_[2], d_[2])): l[uvl].uv = (uu, vv)
        tip = bm.verts.new(pts[-1] + T[-1] * self.R * 0.12)
        for j in range(self.NS): bm.faces.new((rows[-1][j][0], rows[-1][(j + 1) % self.NS][0], tip))
        tail = bm.verts.new(pts[0] - T[0] * self.R * 0.2)
        for j in range(self.NS): bm.faces.new((rows[0][(j + 1) % self.NS][0], rows[0][j][0], tail))
        me = self.obj.data; me.clear_geometry(); bm.to_mesh(me); bm.free()
        for p in me.polygons: p.use_smooth = True
        # ---- eyes, mouth, fangs, tongue ----
        ie = int(0.965 * self.NT); t, nb, sd = frames[ie]; w, d = self.section(0.965, hood)
        for k, sg in (('eyeL', -1), ('eyeR', 1)):
            c = pts[ie] + sd * (sg * w * 0.86) - nb * (d * 0.35)
            self._sphere(self.parts[k], c, self.R * 0.13)
        # mouth cavity: a pink wedge between the jaws, only when open
        isn = self.NT; t_e, nb_e, sd_e = frames[ih]
        mo = self.parts['mouth']; bmm = bmesh.new()
        if jaw > 0.02:
            wj, dj = self.section(s_h, hood); up = [hinge + sd_e * (x * wj * 0.75) for x in (-1, 1)]
            front = pts[-1]; low = hinge + jq @ (front - hinge)
            vs = [bmm.verts.new(p) for p in (up[0], up[1], front + sd_e * wj * 0.3, front - sd_e * wj * 0.3)]
            vl = [bmm.verts.new(p) for p in (low + sd_e * wj * 0.3, low - sd_e * wj * 0.3)]
            bmm.faces.new((vs[0], vs[1], vs[2], vs[3])); bmm.faces.new((vs[1], vs[0], vl[1], vl[0])); bmm.faces.new((vs[3], vs[2], vl[0], vl[1]))
            # fangs hang from the upper jaw near the snout
            for k, sg in (('fangL', -1), ('fangR', 1)):
                base = pts[int(0.985 * self.NT)] + sd_e * (sg * wj * 0.32) + nb_e * (self.R * 0.05)
                self._cone(self.parts[k], base, nb_e, self.R * 0.05, self.R * 0.32 * min(1, jaw * 1.5))
        else:
            for k in ('fangL', 'fangR'): self.parts[k].data.clear_geometry()
        mo.data.clear_geometry(); bmm.to_mesh(mo.data); bmm.free()
        # forked tongue flicking out of the snout
        to = self.parts['tongue']; bt = bmesh.new()
        if tongue > 0.02:
            t_, nb_, sd_ = frames[-1]; L_ = self.R * 1.6 * tongue; base = pts[-1] + nb_ * self.R * 0.05
            wob = math.sin(tongue_phase * 40) * 0.25
            for sg in (-1, 1):
                pts_t = [base + t_ * (L_ * k / 6) + nb_ * (wob * L_ * (k / 6) ** 2) + sd_ * (sg * max(0, k - 4) / 2 * L_ * 0.12) for k in range(7)]
                for a_, b2 in zip(pts_t, pts_t[1:]):
                    bmesh.ops.create_cone(bt, cap_ends=True, segments=6, radius1=self.R * 0.035, radius2=self.R * 0.025, depth=(b2 - a_).length,
                                          matrix=Matrix.Translation((a_ + b2) / 2) @ (b2 - a_).to_track_quat('Z', 'Y').to_matrix().to_4x4())
        to.data.clear_geometry(); bt.to_mesh(to.data); bt.free()
        return pts, frames

    def _sphere(self, o, c, r):
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=12, radius=r, matrix=Matrix.Translation(c))
        o.data.clear_geometry(); bm.to_mesh(o.data); bm.free()
        for p in o.data.polygons: p.use_smooth = True

    def _cone(self, o, base, down, r, L):
        bm = bmesh.new(); m = Matrix.Translation(base + down * L / 2) @ down.to_track_quat('-Z', 'Y').to_matrix().to_4x4()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=r, radius2=r * 0.05, depth=L, matrix=m)
        o.data.clear_geometry(); bm.to_mesh(o.data); bm.free()
        for p in o.data.polygons: p.use_smooth = True
