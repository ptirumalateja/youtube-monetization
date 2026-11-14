"""Numba ray tracer for the Jupiter bodyguard reel.

One function renders a frame of up to three planets (Earth, Saturn with
rings, Jupiter) over a lensed Milky Way + nebula sky. Everything is in
linear float RGB; the caller tonemaps.
"""
import math
import numpy as np
from numba import njit, prange

# object kinds
EARTH, SATURN, JUPITER = 0, 1, 2


@njit(fastmath=True, inline="always")
def samp(tex, u, v):
    """Bilinear sample uint8 HxWxC texture; u wraps, v clamps. Returns 0-1."""
    h, w, c = tex.shape
    x = (u - math.floor(u)) * w - 0.5
    y = min(max(v, 0.0), 1.0) * (h - 1)
    x0 = int(math.floor(x)); fx = x - x0
    y0 = int(math.floor(y)); fy = y - y0
    x0 %= w; x1 = (x0 + 1) % w
    y1 = min(y0 + 1, h - 1)
    r = np.empty(3, np.float32)
    for k in range(3):
        kk = min(k, c - 1)
        a = tex[y0, x0, kk] * (1 - fx) + tex[y0, x1, kk] * fx
        b = tex[y1, x0, kk] * (1 - fx) + tex[y1, x1, kk] * fx
        r[k] = (a * (1 - fy) + b * fy) / 255.0
    return r


@njit(fastmath=True, inline="always")
def samp1(tex, u, v, ch):
    h, w, c = tex.shape
    x = (u - math.floor(u)) * w - 0.5
    y = min(max(v, 0.0), 1.0) * (h - 1)
    x0 = int(math.floor(x)); fx = x - x0
    y0 = int(math.floor(y)); fy = y - y0
    x0 %= w; x1 = (x0 + 1) % w
    y1 = min(y0 + 1, h - 1)
    a = tex[y0, x0, ch] * (1 - fx) + tex[y0, x1, ch] * fx
    b = tex[y1, x0, ch] * (1 - fx) + tex[y1, x1, ch] * fx
    return (a * (1 - fy) + b * fy) / 255.0


@njit(fastmath=True, inline="always")
def srgb2lin(c):
    return c ** 2.2


@njit(fastmath=True, inline="always")
def hash2(i, j):
    h = (i * 374761393 + j * 668265263) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return (h ^ (h >> 16)) / 4294967295.0


@njit(fastmath=True, inline="always")
def vnoise(x, y):
    xi = math.floor(x); yi = math.floor(y)
    fx = x - xi; fy = y - yi
    fx = fx * fx * (3 - 2 * fx); fy = fy * fy * (3 - 2 * fy)
    i = int(xi); j = int(yi)
    a = hash2(i, j); b = hash2(i + 1, j); c = hash2(i, j + 1); d = hash2(i + 1, j + 1)
    return (a + (b - a) * fx) * (1 - fy) + (c + (d - c) * fx) * fy


@njit(fastmath=True, inline="always")
def jdetail(u, v, edge):
    """Fine zonal turbulence: domain-warped value noise stretched along the bands, +-1."""
    x = u * 330.0; y = v * 330.0
    wx = vnoise(x * 0.3 + 17.0, y * 0.3) - 0.5
    wy = vnoise(x * 0.3, y * 0.3 + 31.0) - 0.5
    ws = 3.0 + 5.0 * edge
    x += wx * ws; y += wy * ws * 0.9
    n = vnoise(x, y) * 0.55 + vnoise(x * 2.1 + 5.0, y * 2.1) * 0.3 + vnoise(x * 4.3, y * 4.3 + 9.0) * 0.15
    return (n - 0.5) * 2.0


@njit(fastmath=True)
def stars(dx, dy, dz, pix):
    """Procedural point stars on a cube-ish lat/lon grid. pix = angular pixel size."""
    r = g = b = 0.0
    lat = math.asin(max(-1.0, min(1.0, dy)))
    lon = math.atan2(dx, -dz)
    for layer in range(2):
        cell = 0.004 if layer == 0 else 0.0125
        cl = math.cos(lat)
        j = int(math.floor(lat / cell))
        ncol = max(int(2 * math.pi * cl / cell), 1)
        i = int(math.floor((lon + math.pi) / (2 * math.pi) * ncol))
        for dj in range(-1, 2):
            for di in range(-1, 2):
                jj = j + dj; ii = (i + di) % ncol
                h1 = hash2(ii + layer * 7919, jj)
                if h1 > (0.22 if layer == 0 else 0.10):
                    continue
                slat = (jj + hash2(ii, jj + 99)) * cell
                slon = (ii + hash2(ii + 31, jj)) / ncol * 2 * math.pi - math.pi
                # angular distance (small-angle)
                dlat = lat - slat
                dlon = (lon - slon + math.pi) % (2 * math.pi) - math.pi
                d2 = dlat * dlat + (dlon * cl) ** 2
                m = hash2(ii + 5, jj + 17)
                s = max(pix * (0.9 + 1.6 * m ** 6), 1e-5)    # bright stars get a wider soft PSF
                mag = (m ** 9.0) * (4.0 if layer == 1 else 1.2) + 0.015
                w = math.exp(-d2 / (s * s)) * mag
                tcol = hash2(ii + 77, jj + 3)
                if tcol < 0.25:
                    r += w * 1.0; g += w * 0.75; b += w * 0.55
                elif tcol < 0.6:
                    r += w * 0.75; g += w * 0.85; b += w * 1.0
                else:
                    r += w; g += w; b += w
    return r, g, b


@njit(fastmath=True)
def hit_ellipsoid(ox, oy, oz, dx, dy, dz, P):
    """P: [cx,cy,cz,R,flat, m00..m22 (rows = local x,y,z axes)].
    Returns t (or -1) and local unit-sphere point."""
    cx, cy, cz, R, f = P[0], P[1], P[2], P[3], P[4]
    px, py, pz = ox - cx, oy - cy, oz - cz
    lx = (P[5] * px + P[6] * py + P[7] * pz) / R
    ly = (P[8] * px + P[9] * py + P[10] * pz) / (R * f)
    lz = (P[11] * px + P[12] * py + P[13] * pz) / R
    ex = (P[5] * dx + P[6] * dy + P[7] * dz) / R
    ey = (P[8] * dx + P[9] * dy + P[10] * dz) / (R * f)
    ez = (P[11] * dx + P[12] * dy + P[13] * dz) / R
    a = ex * ex + ey * ey + ez * ez
    b = lx * ex + ly * ey + lz * ez
    c = lx * lx + ly * ly + lz * lz - 1.0
    disc = b * b - a * c
    if disc < 0:
        return -1.0, 0.0, 0.0, 0.0
    t = (-b - math.sqrt(disc)) / a
    if t < 1e-4:
        return -1.0, 0.0, 0.0, 0.0
    return t, lx + ex * t, ly + ey * t, lz + ez * t


@njit(fastmath=True, inline="always")
def to_world(P, x, y, z):
    # local normal (ellipsoid: divide y by f) -> world
    f = P[4]
    ny = y / f
    wx = P[5] * x + P[8] * ny + P[11] * z
    wy = P[6] * x + P[9] * ny + P[12] * z
    wz = P[7] * x + P[10] * ny + P[13] * z
    n = math.sqrt(wx * wx + wy * wy + wz * wz)
    return wx / n, wy / n, wz / n


@njit(fastmath=True, inline="always")
def smooth(a, b, x):
    t = min(max((x - a) / (b - a), 0.0), 1.0)
    return t * t * (3 - 2 * t)


@njit(fastmath=True)
def ring_hit(ox, oy, oz, dx, dy, dz, P, rin, rout):
    """Ring plane = local y=0 of Saturn. Returns t and radius/R."""
    cx, cy, cz, R = P[0], P[1], P[2], P[3]
    ny0, ny1, ny2 = P[8], P[9], P[10]
    den = dx * ny0 + dy * ny1 + dz * ny2
    if abs(den) < 1e-7:
        return -1.0, 0.0
    t = ((cx - ox) * ny0 + (cy - oy) * ny1 + (cz - oz) * ny2) / den
    if t < 1e-4:
        return -1.0, 0.0
    hx, hy, hz = ox + dx * t - cx, oy + dy * t - cy, oz + dz * t - cz
    r = math.sqrt(hx * hx + hy * hy + hz * hz) / R
    if r < rin or r > rout:
        return -1.0, r
    return t, r


@njit(fastmath=True)
def shade_ray(ox, oy, oz, dx, dy, dz, objs, nobj, Lx, Ly, Lz,
              earth_day, earth_night, earth_cloud, jup, sat, ring,
              sky, neb, prm):
    """prm: [earth_rot, cloud_rot, jup_rot, sat_rot, lens_k, sky_gain,
             neb_gain, ring_in, ring_out, jup_shear, time, jup_glow]"""
    # ---- nearest opaque hit
    best_t = 1e30
    best_i = -1
    bx = by = bz = 0.0
    for i in range(nobj):
        P = objs[i]
        t, lx, ly, lz = hit_ellipsoid(ox, oy, oz, dx, dy, dz, P)
        if t > 0 and t < best_t:
            best_t = t; best_i = i; bx = lx; by = ly; bz = lz

    cr = cg = cb = 0.0
    if best_i < 0:
        # ---- sky with gravitational lensing toward Jupiter
        sdx, sdy, sdz = dx, dy, dz
        for i in range(nobj):
            P = objs[i]
            if int(P[14]) == JUPITER and prm[4] > 0:
                px, py, pz = P[0] - ox, P[1] - oy, P[2] - oz
                tc = px * dx + py * dy + pz * dz
                if tc > 0:
                    qx, qy, qz = px - dx * tc, py - dy * tc, pz - dz * tc
                    b = math.sqrt(qx * qx + qy * qy + qz * qz)
                    ang = prm[4] * P[3] / max(b, P[3]) / max(tc, 1.0)
                    ang = min(ang, 0.6)
                    sdx += qx / b * ang; sdy += qy / b * ang; sdz += qz / b * ang
                    n = math.sqrt(sdx * sdx + sdy * sdy + sdz * sdz)
                    sdx /= n; sdy /= n; sdz /= n
        # fixed sky orientation: roll the galactic band diagonally
        ca, sa = math.cos(prm[14]), math.sin(prm[14])
        qx = ca * sdx - sa * sdy; qy = sa * sdx + ca * sdy; qz = sdz
        cy_, sy_ = math.cos(prm[15]), math.sin(prm[15])
        rx = cy_ * qx + sy_ * qz; rz = -sy_ * qx + cy_ * qz
        u = 0.5 + math.atan2(rx, -rz) / (2 * math.pi)
        v = 0.5 - math.asin(max(-1.0, min(1.0, qy))) / math.pi
        s = samp(sky, u, v)
        g = prm[5]
        cr = srgb2lin(s[0]) * g; cg = srgb2lin(s[1]) * g; cb = srgb2lin(s[2]) * g
        sr, sg, sb = stars(sdx, sdy, sdz, prm[12])
        cr += sr * prm[13]; cg += sg * prm[13]; cb += sb * prm[13]
    else:
        P = objs[best_i]
        kind = int(P[14])
        nx, ny, nz = to_world(P, bx, by, bz)
        hx, hy, hz = ox + dx * best_t, oy + dy * best_t, oz + dz * best_t
        ndl = nx * Lx + ny * Ly + nz * Lz
        ndv = -(nx * dx + ny * dy + nz * dz)
        lat = math.asin(max(-1.0, min(1.0, by)))
        lon = math.atan2(bz, bx)
        v = 0.5 - lat / math.pi
        if kind == EARTH:
            u = 0.5 + lon / (2 * math.pi) + prm[0]
            day = samp(earth_day, u, v)
            night = samp(earth_night, u, v)
            cl = samp1(earth_cloud, u + prm[1], v, 0)
            dr = srgb2lin(day[0]); dg = srgb2lin(day[1]); db = srgb2lin(day[2])
            # ocean mask -> specular glint
            ocean = smooth(0.02, 0.10, db - dr) * (1 - smooth(0.25, 0.45, day[1]))
            lit = smooth(-0.12, 0.25, ndl)
            diff = max(ndl, 0.0) ** 0.85
            # cloud shadow (offset sample toward the sun is costly; fake it)
            clc = smooth(0.15, 0.9, cl)
            dr2 = dr * (1 - ocean * 0.2); dg2 = dg * (1 - ocean * 0.15); db2 = db * (1 - ocean * 0.35)
            sr = dr2 * (1 - clc * 0.75); sg = dg2 * (1 - clc * 0.75); sb = db2 * (1 - clc * 0.75)
            sr += clc * 1.05; sg += clc * 1.07; sb += clc * 1.12
            cr = sr * diff * 1.0; cg = sg * diff * 1.0; cb = sb * diff * 1.0
            # specular sun glint on oceans
            hxv = Lx - dx; hyv = Ly - dy; hzv = Lz - dz
            hn = math.sqrt(hxv * hxv + hyv * hyv + hzv * hzv)
            ndh = max((nx * hxv + ny * hyv + nz * hzv) / hn, 0.0)
            spec = ocean * (1 - clc) * ((ndh ** 90) * 0.05) * lit * smooth(0.0, 0.3, ndv)
            cr += spec * 1.0; cg += spec * 0.9; cb += spec * 0.75
            # city lights on the night side
            nl = (1 - lit) * (1 - clc * 0.8)
            ln = srgb2lin(night[0]) * 0.5 + srgb2lin(night[1]) * 0.5
            lnb = max(ln - 0.015, 0.0) ** 0.8   # lights only, no brown land base
            cr += lnb * nl * 44.0; cg += lnb * nl * 24.0; cb += lnb * nl * 7.0
            # warm Jupiter-shine fill on the side facing Jupiter
            if prm[19] > 0:
                jx_, jy_, jz_ = prm[16] - hx, prm[17] - hy, prm[18] - hz
                jn = math.sqrt(jx_ * jx_ + jy_ * jy_ + jz_ * jz_)
                jf = max((nx * jx_ + ny * jy_ + nz * jz_) / jn, 0.0) * prm[19] * (1 - lit * 0.7)
                cr += jf * 0.11; cg += jf * 0.07; cb += jf * 0.035
            # atmosphere rim on disc
            rim = (1 - max(ndv, 0.0)) ** 3.0
            al = smooth(-0.3, 0.4, ndl)
            rim *= prm[20]
            cr += rim * 0.25 * (al + 0.06); cg += rim * 0.55 * (al + 0.08); cb += rim * 1.25 * (al + 0.1)
            # warm terminator band
            term = math.exp(-((ndl - 0.03) / 0.035) ** 2) * (0.3 + clc * 0.7)
            cr += term * 0.06; cg += term * 0.025
        elif kind == JUPITER:
            shear = prm[9] * math.sin(lat * 6.0) + prm[9] * 0.4 * math.sin(lat * 13.0 + 1.0)
            u = 0.5 + lon / (2 * math.pi) + prm[2] + shear + prm[10] * 0.0016 * math.sin(lat * 14.0)   # counter-flowing jets
            c = samp(jup, u, v)
            ca = samp(jup, u, v - 0.0015); cb_ = samp(jup, u, v + 0.0015)
            edge = min(abs((ca[0] + ca[1]) - (cb_[0] + cb_[1])) * 6.0, 1.0)
            dn = 1.0 + jdetail(u, v, edge) * (0.16 + 0.22 * edge)
            # extra contrast for the bands
            cr = srgb2lin(c[0]) ** 1.3 * 1.18 * dn
            cg = srgb2lin(c[1]) ** 1.3 * 1.06 * dn
            cb = srgb2lin(c[2]) ** 1.3 * 0.94 * dn
            diff = smooth(-0.08, 1.0, ndl) ** 1.2
            limb = 0.55 + 0.45 * max(ndv, 0.0) ** 0.6
            limb = limb * (1 - prm[21]) + (0.25 + 0.75 * max(ndv, 0.0) ** 0.75) * prm[21]
            cr *= diff * limb * 1.25; cg *= diff * limb * 1.2; cb *= diff * limb * 1.15
            rim = (1 - max(ndv, 0.0)) ** 4.0 * smooth(-0.2, 0.5, ndl)
            cr += rim * 0.35; cg += rim * 0.22; cb += rim * 0.12
            # night side faint airglow so the giant never goes pure black
            ng = (1 - smooth(-0.1, 0.2, ndl)) * prm[11]
            cr += ng * 0.035; cg += ng * 0.022; cb += ng * 0.022
        else:  # SATURN
            u = 0.5 + lon / (2 * math.pi) + prm[3]
            c = samp(sat, u, v)
            # polar cap: fade to a flat band colour (hides the map's pole pinch / decal)
            pw = smooth(1.0, 1.22, abs(lat))
            if pw > 0:
                c2 = samp(sat, 0.31, 0.5 - math.copysign(1.0, lat) / math.pi)
                for q in range(3):
                    c[q] = c[q] * (1 - pw) + c2[q] * pw
            cr = srgb2lin(c[0]) ** 1.9 * 1.45; cg = srgb2lin(c[1]) ** 1.9 * 1.33; cb = srgb2lin(c[2]) ** 1.9 * 1.08
            diff = smooth(-0.06, 1.0, ndl) ** 1.1
            limb = 0.6 + 0.4 * max(ndv, 0.0) ** 0.5
            cr *= diff * limb * 1.15; cg *= diff * limb * 1.1; cb *= diff * limb
            # ring shadow on the planet
            rt, rr = ring_hit(hx, hy, hz, Lx, Ly, Lz, P, prm[7], prm[8])
            if rt > 0:
                ra = samp1(ring, (rr - prm[7]) / (prm[8] - prm[7]), 0.5, 3)
                sh = 1 - ra * 0.85
                cr *= sh; cg *= sh; cb *= sh
            rim = (1 - max(ndv, 0.0)) ** 4.0 * smooth(-0.2, 0.5, ndl)
            cr += rim * 0.3; cg += rim * 0.25; cb += rim * 0.15

    # ---- rings (Saturn) blended over whatever is behind them
    ringa = 0.0
    for i in range(nobj):
        P = objs[i]
        if int(P[14]) != SATURN:
            continue
        rt, rr = ring_hit(ox, oy, oz, dx, dy, dz, P, prm[7], prm[8])
        if rt > 0 and rt < best_t:
            uu = (rr - prm[7]) / (prm[8] - prm[7])
            rc = samp(ring, uu, 0.5)
            ra = samp1(ring, uu, 0.5, 3)
            ra *= 1 - 0.85 * math.exp(-((uu - 0.69) / 0.012) ** 2)    # Cassini Division
            rx_ = srgb2lin(rc[0]) ** 1.25 * 1.6 + 0.02; ry_ = srgb2lin(rc[1]) ** 1.25 * 1.38 + 0.017; rz_ = srgb2lin(rc[2]) ** 1.25 * 1.05 + 0.01
            # planet shadow on rings
            hx, hy, hz = ox + dx * rt, oy + dy * rt, oz + dz * rt
            st, _a, _b, _c = hit_ellipsoid(hx, hy, hz, Lx, Ly, Lz, P)
            sh = 0.06 if st > 0 else 1.0
            # forward scatter makes back-lit rings glow a little
            ndl = abs(P[8] * Lx + P[9] * Ly + P[10] * Lz)
            lum = (0.35 + 0.9 * ndl) * sh * 1.6
            a = min((ra ** 1.35) * 1.25, 1.0)
            ringa = a
            cr = cr * (1 - a) + rx_ * lum * a
            cg = cg * (1 - a) + ry_ * lum * a
            cb = cb * (1 - a) + rz_ * lum * a

    # ---- atmospheres / glows for rays passing near a limb (in ellipsoid space)
    for i in range(nobj):
        P = objs[i]
        kind = int(P[14])
        R, f = P[3], P[4]
        px, py, pz = ox - P[0], oy - P[1], oz - P[2]
        lx = (P[5] * px + P[6] * py + P[7] * pz) / R
        ly = (P[8] * px + P[9] * py + P[10] * pz) / (R * f)
        lz = (P[11] * px + P[12] * py + P[13] * pz) / R
        ex = (P[5] * dx + P[6] * dy + P[7] * dz)
        ey = (P[8] * dx + P[9] * dy + P[10] * dz) / f
        ez = (P[11] * dx + P[12] * dy + P[13] * dz)
        en = math.sqrt(ex * ex + ey * ey + ez * ez)
        ex /= en; ey /= en; ez /= en
        tc = -(lx * ex + ly * ey + lz * ez)
        if tc <= 0:
            continue
        if best_i >= 0 and best_i != i:
            # occluded by a nearer planet?
            pcx, pcy, pcz = P[0] - ox, P[1] - oy, P[2] - oz
            if pcx * dx + pcy * dy + pcz * dz > best_t:
                continue
        qx, qy, qz = lx + ex * tc, ly + ey * tc, lz + ez * tc
        b = math.sqrt(qx * qx + qy * qy + qz * qz)
        if b < 0.995 and best_i == i:
            continue
        h = b - 1.0
        if h < -0.01:
            continue
        wx, wy, wz = to_world(P, qx / b, qy / b * f, qz / b)
        sl = smooth(-0.35, 0.5, wx * Lx + wy * Ly + wz * Lz)
        if kind != EARTH:
            sl = smooth(0.0, 0.7, wx * Lx + wy * Ly + wz * Lz)
        if kind == SATURN:
            sl *= (1 - ringa)
        hh = max(h, 0.0)
        if kind == EARTH:
            g = (math.exp(-hh / 0.018) * 1.4 + math.exp(-hh / 0.07) * 0.25) * prm[20]
            sl2 = sl + 0.05
            cr += g * 0.30 * sl2; cg += g * 0.62 * sl2; cb += g * 1.45 * sl2
        elif kind == JUPITER:
            g = math.exp(-hh / 0.008) * 0.45 + math.exp(-hh / 0.08) * 0.06 * prm[11]
            cr += g * 0.9 * sl; cg += g * 0.62 * sl; cb += g * 0.42 * sl
        else:
            g = math.exp(-hh / 0.008) * 0.3
            cr += g * 0.9 * sl; cg += g * 0.8 * sl; cb += g * 0.55 * sl
    return cr, cg, cb


@njit(parallel=True, fastmath=True)
def render(W, H, cam, objs, nobj, L, earth_day, earth_night, earth_cloud,
           jup, sat, ring, sky, neb, prm, ss):
    """cam: [ox,oy,oz, rx,ry,rz, ux,uy,uz, fx,fy,fz, tan_half_fov_y]"""
    out = np.zeros((H, W, 3), np.float32)
    th = cam[12]
    asp = W / H
    for y in prange(H):
        for x in range(W):
            ar = ag = ab = 0.0
            for sy in range(ss):
                for sx in range(ss):
                    fx_ = (x + (sx + 0.5) / ss) / W * 2 - 1
                    fy_ = 1 - (y + (sy + 0.5) / ss) / H * 2
                    px = fx_ * th * asp; py = fy_ * th
                    dx = cam[9] + cam[3] * px + cam[6] * py
                    dy = cam[10] + cam[4] * px + cam[7] * py
                    dz = cam[11] + cam[5] * px + cam[8] * py
                    n = math.sqrt(dx * dx + dy * dy + dz * dz)
                    r, g, b = shade_ray(cam[0], cam[1], cam[2], dx / n, dy / n, dz / n,
                                        objs, nobj, L[0], L[1], L[2],
                                        earth_day, earth_night, earth_cloud, jup, sat,
                                        ring, sky, neb, prm)
                    ar += r; ag += g; ab += b
            k = 1.0 / (ss * ss)
            out[y, x, 0] = ar * k; out[y, x, 1] = ag * k; out[y, x, 2] = ab * k
    return out
