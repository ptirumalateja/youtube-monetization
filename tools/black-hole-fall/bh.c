// Black hole fall: CPU ray tracer for one Schwarzschild black hole (M = 1, horizon r = 2).
// Light rays are bent with the exact Schwarzschild photon orbit equation in Cartesian form,
// x'' = -3 M h^2 x / r^5 (h = |x cross x'|), integrated with RK4.
// The disk is a volumetric, turbulent, Doppler-beamed gas slab; the sky is a procedural
// blue-violet galaxy band and multi-layer star field, so lensing distorts all of it.
// Output: linear HDR float32 RGB, row-major, top row first.
//
// usage: bh W H SS t out.raw
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct { float x, y, z; } v3;
static inline v3 V(float x, float y, float z) { v3 r = {x, y, z}; return r; }
static inline v3 add(v3 a, v3 b) { return V(a.x + b.x, a.y + b.y, a.z + b.z); }
static inline v3 sub(v3 a, v3 b) { return V(a.x - b.x, a.y - b.y, a.z - b.z); }
static inline v3 mul(v3 a, float s) { return V(a.x * s, a.y * s, a.z * s); }
static inline v3 vm(v3 a, v3 b) { return V(a.x * b.x, a.y * b.y, a.z * b.z); }
static inline float dot(v3 a, v3 b) { return a.x * b.x + a.y * b.y + a.z * b.z; }
static inline v3 cross(v3 a, v3 b) { return V(a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z, a.x * b.y - a.y * b.x); }
static inline float len(v3 a) { return sqrtf(dot(a, a)); }
static inline v3 norm(v3 a) { return mul(a, 1.0f / len(a)); }
static inline float clampf(float x, float a, float b) { return x < a ? a : (x > b ? b : x); }
static inline float smooth(float a, float b, float x) { float t = clampf((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); }
static inline float mixf(float a, float b, float t) { return a + (b - a) * t; }
static inline v3 mixv(v3 a, v3 b, float t) { return add(a, mul(sub(b, a), t)); }

// ---------- noise ----------
static int P[512];
static void init_perm(void) {
    int p[256];
    for (int i = 0; i < 256; i++) p[i] = i;
    uint32_t s = 1234567u;
    for (int i = 255; i > 0; i--) { s = s * 1664525u + 1013904223u; int j = (s >> 8) % (i + 1); int t = p[i]; p[i] = p[j]; p[j] = t; }
    for (int i = 0; i < 512; i++) P[i] = p[i & 255];
}
static inline float fade(float t) { return t * t * t * (t * (t * 6 - 15) + 10); }
static inline float grad(int h, float x, float y, float z) {
    h &= 15; float u = h < 8 ? x : y, v = h < 4 ? y : (h == 12 || h == 14 ? x : z);
    return ((h & 1) ? -u : u) + ((h & 2) ? -v : v);
}
static float noise3(float x, float y, float z) {
    float fx = floorf(x), fy = floorf(y), fz = floorf(z);
    int X = (int)fx & 255, Y = (int)fy & 255, Z = (int)fz & 255;
    x -= fx; y -= fy; z -= fz;
    float u = fade(x), v = fade(y), w = fade(z);
    int A = P[X] + Y, AA = P[A] + Z, AB = P[A + 1] + Z, B = P[X + 1] + Y, BA = P[B] + Z, BB = P[B + 1] + Z;
    return mixf(mixf(mixf(grad(P[AA], x, y, z), grad(P[BA], x - 1, y, z), u),
                     mixf(grad(P[AB], x, y - 1, z), grad(P[BB], x - 1, y - 1, z), u), v),
                mixf(mixf(grad(P[AA + 1], x, y, z - 1), grad(P[BA + 1], x - 1, y, z - 1), u),
                     mixf(grad(P[AB + 1], x, y - 1, z - 1), grad(P[BB + 1], x - 1, y - 1, z - 1), u), v), w);
}
static float fbm(v3 p, int oct, float lac, float gain) {
    float s = 0, a = 0.5f, n = 0;
    for (int i = 0; i < oct; i++) {
        s += a * noise3(p.x, p.y, p.z); n += a;
        p = V(p.x * lac + 17.3f, p.y * lac - 9.1f, p.z * lac + 4.7f); a *= gain;
    }
    return s / n;
}
static inline uint32_t hash3(uint32_t a, uint32_t b, uint32_t c) {
    uint32_t h = a * 0x9E3779B1u ^ b * 0x85EBCA77u ^ c * 0xC2B2AE3Du;
    h ^= h >> 15; h *= 0x2C1B3C6Du; h ^= h >> 12; h *= 0x297A2D39u; h ^= h >> 15;
    return h;
}
static inline float hf(uint32_t h) { return (h & 0xFFFFFF) / 16777216.0f; }

// ---------- scene parameters ----------
static float T;               // scene time (s)
static v3 GAL_N;              // galaxy band normal
static float PIXANG;          // angular size of one pixel (rad)
static const float RIN = 3.4f, ROUT = 24.0f;
static const float SPIN = 1.35f; // scales Keplerian angular speed into screen time

// disk scale height
static inline float diskH(float r) { return 0.014f * r + 0.035f; }

// Disk sample: returns emission colour (pre-Doppler) and extinction coefficient.
static void disk_sample(v3 p, v3 raydir, v3 *em, float *ext) {
    float r = sqrtf(p.x * p.x + p.z * p.z);
    float H = diskH(r);
    float zq = p.y / H;
    float vert = expf(-0.5f * zq * zq);
    float inner = smooth(RIN - 0.4f, RIN + 1.6f, r);
    float outer = 1.0f - smooth(ROUT * 0.30f, ROUT, r);
    float prof = vert * inner * outer;
    if (prof < 2e-3f) { *em = V(0, 0, 0); *ext = 0; return; }

    float phi = atan2f(p.z, p.x);
    float om = powf(r, -1.5f);
    float rot = phi - SPIN * om * T;          // co-rotating angle (differential rotation)
    float c = cosf(rot), s = sinf(rot);
    float lr = logf(r);

    // low-frequency warp so streaks wander instead of forming perfect rings
    float w = fbm(V(c * 1.3f, s * 1.3f, lr * 2.2f + 3.1f), 3, 2.1f, 0.5f);
    float u = lr * 22.0f + w * 4.0f + zq * 0.25f;
    // anisotropic turbulence: fine radially, long azimuthally -> streaked filaments
    float n1 = fbm(V(u, c * 2.6f, s * 2.6f), 8, 2.03f, 0.60f);
    float ridge = 1.0f - fabsf(fbm(V(u * 1.7f + 7.0f, c * 4.5f, s * 4.5f), 6, 2.1f, 0.55f) * 2.4f);
    ridge = clampf(ridge, 0, 1); ridge = ridge * ridge * ridge;
    float clump = fbm(V(lr * 4.0f + 11.0f, c * 2.6f + zq * 0.25f, s * 2.6f), 4, 2.0f, 0.55f);

    float dens = 0.03f + 2.0f * powf(clampf(0.5f + 2.6f * n1, 0, 1), 2.2f) + 0.9f * ridge * smooth(-0.1f, 0.35f, clump);
    dens *= prof;

    // absorbing dust lanes (cooler gas) mostly in the outer disk
    float lane = fbm(V(lr * 6.5f + w * 1.4f + 40.0f, c * 2.0f, s * 2.0f), 4, 2.0f, 0.5f);
    float dust = smooth(0.02f, 0.28f, lane) * smooth(RIN + 2.0f, 12.0f, r) * prof;

    // temperature-ish colour ramp: white-gold inside, gold, amber, deep rust outside
    float tr = clampf((r - RIN) / (ROUT - RIN), 0, 1);
    tr = powf(tr, 0.55f);
    v3 c0 = V(1.00f, 0.88f, 0.66f), c1 = V(1.00f, 0.68f, 0.28f), c2 = V(0.95f, 0.46f, 0.12f), c3 = V(0.62f, 0.22f, 0.06f);
    v3 col = tr < 0.25f ? mixv(c0, c1, tr / 0.25f) : (tr < 0.6f ? mixv(c1, c2, (tr - 0.25f) / 0.35f) : mixv(c2, c3, (tr - 0.6f) / 0.4f));
    float bright = powf(RIN / r, 1.75f) * 14.0f;

    // Doppler beaming: gas moves counter-clockwise seen from +y
    float beta = fminf(0.55f, sqrtf(1.0f / fmaxf(r - 2.0f, 0.5f)));
    v3 vdir = V(-sinf(phi), 0, cosf(phi));
    float cth = dot(vdir, mul(raydir, -1.0f)); // toward the camera
    float gam = 1.0f / sqrtf(1 - beta * beta);
    float D = 1.0f / (gam * (1 - beta * cth));
    float grav = sqrtf(fmaxf(1 - 2.0f / r, 0.0f));
    float g = D * grav;
    float boost = powf(g, 2.6f);
    boost = boost / (1.0f + 0.25f * boost); // soften the extremes a touch
    // shift colour a little with g: approaching side whiter, receding side deeper amber
    v3 shift = g > 1 ? mixv(col, V(1.0f, 0.95f, 0.88f), clampf((g - 1) * 0.6f, 0, 0.5f))
                     : vm(col, V(1.0f, mixf(0.7f, 1.0f, g), mixf(0.45f, 1.0f, g)));

    // fine emission streaks (thin filaments riding the flow), emission only
    float fs = fbm(V(u * 2.8f + 31.0f, c * 9.0f, s * 9.0f), 4, 2.2f, 0.6f);
    float fine = 0.45f + 1.1f * smooth(-0.25f, 0.35f, fs);
    float e = powf(dens, 1.35f) * bright * boost * fine;
    *em = mul(shift, e);
    *ext = dens * 2.6f * (0.35f + 0.65f * smooth(RIN, RIN + 6.0f, r)) + dust * 2.8f;
}

// ---------- sky ----------
static v3 star_layer(v3 d, int layer, int N, float prob, float bmul) {
    float ax = fabsf(d.x), ay = fabsf(d.y), az = fabsf(d.z);
    int face; float u, v, m;
    if (ax >= ay && ax >= az) { face = d.x > 0 ? 0 : 1; m = ax; u = d.y / m; v = d.z / m; }
    else if (ay >= az) { face = d.y > 0 ? 2 : 3; m = ay; u = d.x / m; v = d.z / m; }
    else { face = d.z > 0 ? 4 : 5; m = az; u = d.x / m; v = d.y / m; }
    float fu = (u * 0.5f + 0.5f) * N, fv = (v * 0.5f + 0.5f) * N;
    int cu = (int)floorf(fu), cv = (int)floorf(fv);
    float sc = 2.0f / N;                       // uv per cell
    float ang_per_uv = 1.0f / (1.0f + u * u + v * v); // rough d(angle)/d(uv)
    float sig = PIXANG * 0.62f;
    v3 acc = V(0, 0, 0);
    for (int dj = -1; dj <= 1; dj++)
        for (int di = -1; di <= 1; di++) {
            int iu = cu + di, iv = cv + dj;
            uint32_t h = hash3((uint32_t)(face * 7919 + layer * 104729), (uint32_t)iu, (uint32_t)iv);
            if (hf(h) > prob) continue;
            uint32_t h2 = hash3(h, 77u, 3u), h3 = hash3(h2, 11u, 5u);
            float su = iu + hf(h2), sv = iv + hf(h2 >> 7 ^ h3);
            float du = (fu - su) * sc * ang_per_uv, dv = (fv - sv) * sc * ang_per_uv;
            float a2 = du * du + dv * dv;
            float x = hf(h3);
            float b = bmul * 0.02f * powf(x + 0.02f, -1.35f);   // power law: few bright, many faint
            float k = expf(-0.5f * a2 / (sig * sig));
            if (k < 1e-4f) continue;
            float tc = hf(hash3(h3, 5u, 9u));
            v3 c = tc < 0.30f ? V(0.70f, 0.82f, 1.0f) : tc < 0.70f ? V(1.0f, 0.97f, 0.92f) : tc < 0.90f ? V(1.0f, 0.84f, 0.60f) : V(1.0f, 0.65f, 0.40f);
            acc = add(acc, mul(c, b * k));
        }
    return acc;
}

static v3 sky(v3 d) {
    float lat = dot(d, GAL_N);
    float band = expf(-0.5f * lat * lat / (0.20f * 0.20f));
    float wide = expf(-0.5f * lat * lat / (0.55f * 0.55f));
    v3 q = mul(d, 2.6f);
    float n1 = fbm(q, 8, 2.05f, 0.58f);
    float n2 = fbm(add(mul(d, 6.5f), V(5.2f, 1.3f, 8.8f)), 5, 2.1f, 0.5f);
    float cloud = clampf(0.55f + 1.4f * n1 + 0.5f * n2, 0, 2);
    // dark dust lanes threading the band
    float lane = fbm(add(mul(d, 4.2f), V(-3.0f, 7.0f, 1.0f)), 8, 2.0f, 0.58f);
    float lanes = smooth(-0.02f, 0.22f, lane + lat * 0.6f);
    v3 deep = V(0.010f, 0.016f, 0.045f);
    v3 blue = V(0.035f, 0.075f, 0.20f);
    v3 violet = V(0.10f, 0.055f, 0.20f);
    v3 pinkish = V(0.20f, 0.09f, 0.16f);
    float hue = smooth(-0.25f, 0.35f, n2);
    v3 neb = mixv(blue, violet, hue);
    neb = mixv(neb, pinkish, smooth(0.25f, 0.6f, n1) * 0.5f);
    v3 c = add(mul(deep, 0.4f + 0.6f * cloud),
               mul(neb, (0.10f * wide + 0.75f * band) * cloud * cloud * (1.0f - 0.92f * lanes)));
    // warm core glow in the band (distant galactic bulge)
    float coreAng = dot(d, norm(V(-0.35f, 0.08f, -1.0f)));
    c = add(c, mul(V(0.10f, 0.06f, 0.08f), powf(fmaxf(coreAng, 0), 60.0f) * band * (1.0f - 0.7f * lanes)));

    float dens = 0.5f + 1.3f * band;             // more stars along the band
    v3 st = star_layer(d, 0, 260, 0.30f, 0.9f);
    st = add(st, star_layer(d, 1, 700, 0.30f * dens, 0.45f));
    st = add(st, star_layer(d, 2, 1600, 0.30f * dens, 0.16f));
    st = add(st, star_layer(d, 3, 3200, 0.28f * dens, 0.07f));
    st = mul(st, 1.0f - 0.75f * lanes * band);
    return add(c, st);
}

// ---------- geodesic ----------
static inline void deriv(v3 x, v3 v, float h2, v3 *dx, v3 *dv) {
    float r2 = dot(x, x);
    float r5 = r2 * r2 * sqrtf(r2);
    *dx = v;
    *dv = mul(x, -3.0f * h2 / r5);   // -3 M h^2 x / r^5 with M = 1
}

// Photon ring: rays skimming the photon sphere (r = 3) cross the inner disk many times,
// so the ring at the shadow edge is the brightest, thinnest feature. This adds that
// pile-up as a thin glow keyed on the ray's closest approach.
static inline v3 ring_glow(float rmin, float trans) {
    float d = (rmin - 3.0f) / 0.12f;
    float k = expf(-d * d) + 0.18f * expf(-fabsf(rmin - 3.0f) / 0.25f);
    return mul(V(1.0f, 0.80f, 0.52f), 1.8f * k * trans);
}

static v3 trace(v3 o, v3 d, float rcam) {
    v3 x = o, v = d;
    float h2 = dot(cross(x, v), cross(x, v));
    float rmin = 1e9f;
    v3 acc = V(0, 0, 0);
    float trans = 1.0f;
    float resc = fmaxf(rcam * 1.3f, 70.0f);
    for (int it = 0; it < 6000; it++) {
        float r = len(x);
        if (r < rmin) rmin = r;
        if (r < 2.02f) return add(acc, ring_glow(rmin, trans));   // captured: horizon is black
        if (r > resc && dot(x, v) > 0) break;     // escaped
        float rc = sqrtf(x.x * x.x + x.z * x.z);
        float H = diskH(rc);
        int indisk = fabsf(x.y) < 3.4f * H && rc > RIN - 0.6f && rc < ROUT * 1.02f;
        float ds = 0.06f * r;
        if (r < 6) ds = fminf(ds, 0.05f + 0.03f * (r - 2.0f));
        if (indisk) ds = fminf(ds, fmaxf(0.45f * H, 0.045f));
        else if (fabsf(x.y) > 3.4f * H) {
            // approach the slab quickly but do not overshoot it
            float gap = fabsf(x.y) - 3.4f * H;
            if (rc < ROUT * 1.1f) ds = fminf(ds, fmaxf(gap * 0.9f, 0.04f) + 0.02f);
        }
        // RK4
        v3 k1x, k1v, k2x, k2v, k3x, k3v, k4x, k4v;
        deriv(x, v, h2, &k1x, &k1v);
        deriv(add(x, mul(k1x, ds * 0.5f)), add(v, mul(k1v, ds * 0.5f)), h2, &k2x, &k2v);
        deriv(add(x, mul(k2x, ds * 0.5f)), add(v, mul(k2v, ds * 0.5f)), h2, &k3x, &k3v);
        deriv(add(x, mul(k3x, ds)), add(v, mul(k3v, ds)), h2, &k4x, &k4v);
        v3 xn = add(x, mul(add(add(k1x, mul(k2x, 2)), add(mul(k3x, 2), k4x)), ds / 6.0f));
        v3 vn = add(v, mul(add(add(k1v, mul(k2v, 2)), add(mul(k3v, 2), k4v)), ds / 6.0f));
        if (indisk) {
            v3 mid = mul(add(x, xn), 0.5f);
            v3 em; float ext;
            disk_sample(mid, norm(v), &em, &ext);
            if (ext > 0 || em.x > 0) {
                float a = expf(-ext * ds);
                // emission integrated over the step with the step's attenuation
                float wgt = ext > 1e-4f ? (1 - a) / ext : ds;
                acc = add(acc, mul(em, trans * wgt));
                trans *= a;
                if (trans < 0.01f) return add(acc, ring_glow(rmin, trans));
            }
        }
        x = xn; v = vn;
    }
    v3 dir = norm(v);
    return add(add(acc, ring_glow(rmin, trans)), mul(sky(dir), trans));
}

// ---------- camera path ----------
typedef struct { v3 pos, fwd, right, up; float r; } Cam;
static float DUR = 18.0f;
static Cam camera_at(float t) {
    float u = t / DUR;                    // may be < 0 for the loop pre-roll
    // falling: log-distance with gentle acceleration, already moving at frame 0
    float e = 0.42f * u + 0.58f * u * fabsf(u);
    float r = 90.0f * powf(33.0f / 90.0f, e);
    float elev = (18.0f - 10.0f * e) * (float)M_PI / 180.0f;
    float az = (-28.0f + 40.0f * e) * (float)M_PI / 180.0f;
    v3 pos = V(r * cosf(elev) * sinf(az), r * sinf(elev), r * cosf(elev) * cosf(az));
    // aim a little below the hole so it sits in the upper-middle of the frame
    v3 target = V(0, -0.075f * r, 0);
    v3 fwd = norm(sub(target, pos));
    v3 wup = V(0, 1, 0);
    float roll = (5.0f - 7.0f * e) * (float)M_PI / 180.0f;
    v3 right = norm(cross(fwd, wup));
    v3 up = cross(right, fwd);
    v3 r2 = add(mul(right, cosf(roll)), mul(up, sinf(roll)));
    v3 u2 = add(mul(up, cosf(roll)), mul(right, -sinf(roll)));
    Cam c = {pos, fwd, r2, u2, r};
    return c;
}

int main(int argc, char **argv) {
    if (argc < 6) { fprintf(stderr, "usage: bh W H SS t out.raw [dur]\n"); return 1; }
    int W = atoi(argv[1]), Hh = atoi(argv[2]), SS = atoi(argv[3]);
    T = atof(argv[4]);
    if (argc > 6) DUR = atof(argv[6]);
    init_perm();
    GAL_N = norm(V(0.55f, 0.80f, -0.10f));
    Cam cam = camera_at(T);
    float vfov = 46.0f * (float)M_PI / 180.0f;
    float th = tanf(vfov * 0.5f);
    PIXANG = 2 * th / Hh;
    float *img = malloc(sizeof(float) * 3 * W * Hh);
    // pass 1: one ray per pixel centre
    float *lum = malloc(sizeof(float) * W * Hh);
#pragma omp parallel for schedule(dynamic, 1)
    for (int j = 0; j < Hh; j++)
        for (int i = 0; i < W; i++) {
            float px = ((i + 0.5f) / W * 2 - 1) * th * W / Hh, py = (1 - (j + 0.5f) / Hh * 2) * th;
            v3 d = norm(add(cam.fwd, add(mul(cam.right, px), mul(cam.up, py))));
            v3 c = trace(cam.pos, d, cam.r);
            float *o = img + 3 * (j * W + i);
            o[0] = c.x; o[1] = c.y; o[2] = c.z;
            lum[j * W + i] = logf(1e-3f + 0.3f * c.x + 0.6f * c.y + 0.1f * c.z);
        }
    // pass 2: supersample SSxSS where the pixel differs from a neighbour (edges, stars, ring)
    int nref = 0;
#pragma omp parallel for schedule(dynamic, 1) reduction(+ : nref)
    for (int j = 0; j < Hh; j++) {
        for (int i = 0; i < W; i++) {
            float l0 = lum[j * W + i], dmax = 0;
            for (int dj = -1; dj <= 1; dj++)
                for (int di = -1; di <= 1; di++) {
                    int a = i + di, b = j + dj;
                    if (a < 0 || b < 0 || a >= W || b >= Hh) continue;
                    float dd = fabsf(lum[b * W + a] - l0);
                    if (dd > dmax) dmax = dd;
                }
            if (SS <= 1 || dmax < 0.30f) continue;
            nref++;
            v3 sum = V(0, 0, 0);
            for (int sj = 0; sj < SS; sj++)
                for (int si = 0; si < SS; si++) {
                    uint32_t h = hash3((uint32_t)i, (uint32_t)j, (uint32_t)(sj * SS + si));
                    float ox = (si + 0.25f + 0.5f * hf(h)) / SS, oy = (sj + 0.25f + 0.5f * hf(h >> 5)) / SS;
                    float px = ((i + ox) / W * 2 - 1) * th * W / Hh;
                    float py = (1 - (j + oy) / Hh * 2) * th;
                    v3 d = norm(add(cam.fwd, add(mul(cam.right, px), mul(cam.up, py))));
                    sum = add(sum, trace(cam.pos, d, cam.r));
                }
            sum = mul(sum, 1.0f / (SS * SS));
            float *o = img + 3 * (j * W + i);
            o[0] = sum.x; o[1] = sum.y; o[2] = sum.z;
        }
    }
    fprintf(stderr, "refined %.1f%%\n", 100.0 * nref / (W * Hh));
    FILE *f = fopen(argv[5], "wb");
    fwrite(img, sizeof(float), 3 * W * Hh, f);
    fclose(f);
    return 0;
}
