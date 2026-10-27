#version 300 es
// Moon -> Earth -> Jupiter -> Sun: ONE world, ONE camera.
// Units are Earth radii. Earth bowl at the origin, Jupiter bowl around it (Earth is one of its units),
// Sun bowl around that (Jupiter is one of its units). Every container is a hollow shell with a cut; units are FCC lattice spheres.
precision highp float;
uniform vec2 R;
uniform vec3 uCamP, uCamT;
uniform float uFov, uRoll, uT;
uniform vec3 uF;     // fill 0..1 for Earth / Jupiter / Sun bowls
uniform vec3 uCut;   // cut height (fraction of radius above centre); >=1 -> closed
uniform vec3 uWave;  // ignition-wave radius for Jupiter and Sun shells (0 = hidden), z unused
uniform vec3 uM0;    // hero Moon centre
uniform float uExpo;
uniform vec4 uSP[96];  // Earth-bowl unit slots: xyz, landing time (-1 = unused)
uniform vec3 uHeap;  // heap scale above the rim of each bowl (shrinks away as the bowl closes)
uniform sampler2D tEarth, tSpec, tCloud, tLights, tMoon;
out vec4 o;

const float RM = 0.2727, RJ = 10.97, RS = 109.1;
const float TE = 0.05, TJ = 0.15, TS = 0.6;
const vec3 J = vec3(0., 9.82, 0.);
const vec3 S = vec3(0., 107.35, 0.);
const float CUT0 = 0.42, CUT0J = 0.42, CUT0S = 0.42;
const vec3 LD = normalize(vec3(0.86, 0.34, 0.38));   // sun direction (far away light)
const float PI = 3.14159265;

// ---------- noise ----------
float h31(vec3 p) { p = fract(p * .3183099 + .1); p *= 17.; return fract(p.x * p.y * p.z * (p.x + p.y + p.z)); }
vec3 h33(vec3 p) { p = vec3(dot(p, vec3(127.1, 311.7, 74.7)), dot(p, vec3(269.5, 183.3, 246.1)), dot(p, vec3(113.5, 271.9, 124.6))); return fract(sin(p) * 43758.5453); }
float vn(vec3 p) {
  vec3 i = floor(p), f = fract(p); f = f * f * (3. - 2. * f);
  return mix(mix(mix(h31(i), h31(i + vec3(1, 0, 0)), f.x), mix(h31(i + vec3(0, 1, 0)), h31(i + vec3(1, 1, 0)), f.x), f.y),
             mix(mix(h31(i + vec3(0, 0, 1)), h31(i + vec3(1, 0, 1)), f.x), mix(h31(i + vec3(0, 1, 1)), h31(i + vec3(1, 1, 1)), f.x), f.y), f.z);
}
float fbm(vec3 p) { float a = .5, s = 0.; for (int i = 0; i < 5; i++) { s += a * vn(p); p = p * 2.03 + 11.7; a *= .5; } return s; }
float fbm3(vec3 p) { float a = .5, s = 0.; for (int i = 0; i < 3; i++) { s += a * vn(p); p = p * 2.03 + 11.7; a *= .5; } return s; }
mat3 rotY(float a) { float c = cos(a), s = sin(a); return mat3(c, 0, -s, 0, 1, 0, s, 0, c); }
mat3 rotAxis(vec3 k, float a) { float c = cos(a), s = sin(a); return mat3(
  c + k.x*k.x*(1.-c), k.x*k.y*(1.-c) + k.z*s, k.x*k.z*(1.-c) - k.y*s,
  k.x*k.y*(1.-c) - k.z*s, c + k.y*k.y*(1.-c), k.y*k.z*(1.-c) + k.x*s,
  k.x*k.z*(1.-c) + k.y*s, k.y*k.z*(1.-c) - k.x*s, c + k.z*k.z*(1.-c)); }

// ---------- geometry ----------
float sdShell(vec3 q, float Rr, float t, float cutY) {
  float s = abs(length(q) - (Rr - .5 * t)) - .5 * t;
  return max(s, q.y - cutY);
}
vec3 fccNearest(vec3 q) {
  vec3 f = floor(q + .5);
  if (mod(f.x + f.y + f.z, 2.) > .5) {
    vec3 r = q - f, a = abs(r);
    if (a.x > a.y && a.x > a.z) f.x += r.x >= 0. ? 1. : -1.;
    else if (a.y > a.z) f.y += r.y >= 0. ? 1. : -1.;
    else f.z += r.z >= 0. ? 1. : -1.;
  }
  return f;
}
float eob(float x) { float c1 = 1.2, c3 = c1 + 1.; return 1. + c3 * pow(x - 1., 3.) + c1 * pow(x - 1., 2.); }

// globals set by map()
int gid; vec3 gC; float gR; float gH; float gPop; vec3 gG, gGl;

// lattice of unit spheres. returns distance; sets gC, gR, gH, gPop if it is the sphere
float lattice(vec3 p, vec3 C, vec3 off, float sp, float r, float Ri, float yb, float yRim, float hs, float f, out vec3 c_, out float sid, out float pop) {
  float yt = yRim + .7 * Ri;
  vec3 g = fccNearest((p - off) / sp);
  gGl = g;
  vec3 c = off + g * sp;
  sid = h31(g + 7.3);
  bool hero = dot(g, g) < .01;
  float yr = yRim - C.y; float xzMax = sqrt(max(Ri * Ri - yr * yr, 0.)) - .1 * r;
  vec2 hq = vec2(length(c.xz - C.xz) / xzMax, (c.y - yRim) / (.7 * Ri));
  bool inBowl = length(c - C) <= Ri - r * .98 && c.y <= yRim;
  bool inHeap = c.y > yRim && dot(hq, hq) <= 1.;
  float ok = (!hero && (inBowl || (inHeap && hs > .01))) ? 1. : 0.;
  float qy = clamp((c.y - yb) / (yt - yb), 0., 1.);
  bool isHeap = c.y > yRim;
  float qq = qy * .72 + sid * .28;
  pop = clamp((f - qq) * 9., 0., 1.);
  float sc = pop > 0. ? mix(.35, 1., pop * pop * (3. - 2. * pop)) : 0.;
  if (isHeap) sc *= hs;
  c_ = c;
  float rr = r * sc;
  float len = length(p - c);
  float nn = sp * 1.41421356;
  float bound = max(max(len, nn - len) - r, .03 * r);   // nearest any neighbouring unit can be
  float d = (ok < .5 || sc <= 0.) ? bound : min(len - rr, bound);
  float dSph = length(p - C) - (Ri + r * .06);
  vec2 eq = vec2(length(p.xz - C.xz) / (xzMax + r * 1.1), (p.y - yRim) / (.7 * Ri + r * 1.1));
  float dEll = (length(eq) - 1.) * min(xzMax + r * 1.1, .7 * Ri + r * 1.1);
  float dreg = min(dSph, dEll);   // every unit lives inside the bowl sphere or the heap ellipsoid
  return max(d, dreg);
}


// units rain into each bowl: sphere j lands at its slot on the rising fill front, so the pile is built by what you see fall
float fillFrac(float tt, vec2 w) { float x = clamp((tt - w.x) / (w.y - w.x), 0., 1.); return 1. - pow(1. - x, 1.6); }
const float TAUF = .85;
float rain(vec3 p, vec3 C, float Ri, float r, float yb, float yRim, vec2 w, float Nr, out vec3 pc, out float jid) {
  float yt = yRim + .7 * Ri; float Hd = 4.5 * Ri;
  vec3 Cb = vec3(C.x, yRim + 2.7 * Ri, C.z); float Rb = 3.2 * Ri;
  float db = length(p - Cb) - Rb; pc = vec3(0.); jid = 0.;
  if (db > r * 2.) return db;
  float fr0 = fillFrac(uT, w), fr1 = fillFrac(uT + TAUF, w);
  if (fr0 >= .999 || fr1 <= 0.) return max(db, 0.) + r;
  float d = 1e9; int jlo = int(ceil(Nr * fr0 - .5));
  for (int k = 0; k < 32; k++) {
    float j = float(jlo + k);
    if (j + .5 > Nr * fr1 || j >= Nr) break;
    float frac = (j + .5) / Nr; float x = 1. - pow(1. - frac, 1. / 1.6);
    float tau = w.x + (w.y - w.x) * x - uT;                 // seconds until it lands
    float fL = 1.06 * frac; float qy = clamp((fL - .19) / .72, 0., 1.);
    float yl = yb + qy * (yt - yb);
    vec3 hj = h33(vec3(j, 3.7, 1.3) + 11.);
    float yc = clamp(yl, yb, yt);
    float inb = min(yc, yRim) - C.y;
    float rad = .55 * sqrt(max(Ri * Ri - inb * inb, 0.)) * sqrt(max(1. - pow(max(yc - yRim, 0.) / (.7 * Ri), 2.), .05));
    float an = 6.2831853 * hj.x; float rr = sqrt(hj.y) * rad;
    vec3 land = vec3(C.x + cos(an) * rr, yl + .8 * r, C.z + sin(an) * rr);
    float u = tau / TAUF;
    vec3 ps = land + vec3(0., Hd * u * u, 0.) + vec3(.35 * r * sin(j * 1.7 + u * 3.), 0., .35 * r * cos(j * 2.3 + u * 3.)) * u;
    float rs = r * mix(.22, 1., 1. - pow(clamp(u, 0., 1.), .7));   // far = small, near = full size
    float dd = length(p - ps) - rs;
    if (dd < d) { d = dd; pc = ps; jid = j; }
  }
  return min(d, max(db, 0.) + r);
}

float map(vec3 p) {
  float d = 1e9; gid = 0;
  float dm0 = length(p - uM0) - RM;
  d = dm0; gid = 7; gC = uM0; gR = RM;
  // Sun
  vec3 qs = p - S; float rs = length(qs);
  if (uWave.y > 0.) {
    float ds = sdShell(qs, RS, TS, uCut.z * RS);
    ds = max(ds, length(p) - uWave.y);
    if (ds < d) { d = ds; gid = 1; gC = S; gR = RS; }
  }
  if (uF.z > 0. && rs >= 1.4 * RS) d = min(d, max(rs - 1.4 * RS, .05 * RS));
  if (rs < 1.4 * RS && uF.z > 0.) {
    vec3 c; float sid, pop;
    float dj = lattice(p, S, J, 2.12 * RJ / 1.41421356, RJ, RS - TS, J.y - RJ, S.y + CUT0S * RS, uHeap.z, uF.z, c, sid, pop);
    if (dj < d) { d = dj; gid = 2; gC = c; gR = RJ; gH = sid; gPop = pop; gG = gGl; }
  }
  if (uF.z > 0.) {
    vec3 pc; float jid; float dr = rain(p, S, RS - TS, RJ, J.y - RJ, S.y + CUT0S * RS, vec2(13.4, 16.4), 56., pc, jid);
    if (dr < d) { d = dr; gid = 2; gC = pc; gR = RJ; gH = h31(vec3(jid, 5., 2.)); gPop = 1.; gG = vec3(jid, 3., 9.); }
  }
  // Jupiter hero
  vec3 qj = p - J; float rj = length(qj);
  if (rj < RJ + 2.) {
    float dhj = 1e9;
    if (uWave.x > 0.) { dhj = max(sdShell(qj, RJ, TJ, uCut.y * RJ), length(p) - uWave.x); if (rj > RJ + 1.) dhj = rj - RJ; }
    if (dhj < d) { d = dhj; gid = 3; gC = J; gR = RJ; }
  } else { float dd = rj - RJ - 1.; if (dd < d && uWave.x > 0.) { d = dd; gid = 0; } }
  if (uF.y > 0. && rj >= 1.4 * RJ) d = min(d, max(rj - 1.4 * RJ, .05 * RJ));
  if (rj < 1.4 * RJ && uF.y > 0.) {
    vec3 c; float sid, pop;
    float de = lattice(p, J, vec3(0.), 2.12 / 1.41421356, 1., RJ - TJ, J.y - RJ, J.y + CUT0J * RJ, uHeap.y, uF.y, c, sid, pop);
    if (de < d) { d = de; gid = 4; gC = c; gR = 1.; gH = sid; gPop = pop; gG = gGl; }
  }
  if (uF.y > 0.) {
    vec3 pc; float jid; float dr = rain(p, J, RJ - TJ, 1., J.y - RJ, J.y + CUT0J * RJ, vec2(7.8, 10.7), 56., pc, jid);
    if (dr < d) { d = dr; gid = 4; gC = pc; gR = 1.; gH = h31(vec3(jid, 5., 2.)); gPop = 1.; gG = vec3(jid, 3., 9.); }
  }
  if (rj < RJ - TJ) {
    vec3 c; float sid, pop;
    float re = length(p);
    float dhe = re > 1.5 ? re - 1. : sdShell(p, 1., TE, uCut.x);
    if (dhe < d) { d = dhe; gid = 5; gC = vec3(0.); gR = 1.; }
    if (false) {
      float dmm = lattice(p, vec3(0.), vec3(0., -1. + TE + RM + .01, 0.), 2.12 * RM / 1.41421356, RM, 1. - TE, -1. + TE, .5, uHeap.x, uF.x, c, sid, pop);
      if (dmm < d) { d = dmm; gid = 6; gC = c; gR = RM; gH = sid; gPop = pop; gG = gGl; }
    }
  }
  if (uF.x > 0.) {
    // Moons: every one falls to its own slot and stays there
    vec3 Cb = vec3(0., 2.7, 0.); float db = length(p - Cb) - 3.4;
    if (db > .6) { d = min(d, db); }
    else {
      float dm = 1e9; vec3 pcm = vec3(0.); float jm = 0.;
      for (int i = 0; i < 96; i++) {
        vec4 s = uSP[i]; if (s.w < -.5) break;
        float tau = s.w - uT; if (tau > TAUF) continue;
        float u = clamp(tau / TAUF, 0., 1.); bool hp = s.y > .5;
        vec3 ps = s.xyz + vec3(0., 4.275 * u * u, 0.) + vec3(.35 * RM * sin(float(i) * 1.7 + u * 3.), 0., .35 * RM * cos(float(i) * 2.3 + u * 3.)) * u;
        float rs = RM * mix(.22, 1., 1. - pow(u, .7)) * (hp ? uHeap.x : 1.);
        float dd = length(p - ps) - rs;
        if (dd < dm) { dm = dd; pcm = ps; jm = float(i); }
      }
      if (dm < d) { d = dm; gid = 6; gC = pcm; gR = RM; gH = h31(vec3(jm, 5., 2.)); gPop = 1.; gG = vec3(jm, 3., 9.); }
    }
  }
  return d;
}

vec3 nrm(vec3 p, float e) {
  vec2 k = vec2(1., -1.);
  return normalize(k.xyy * map(p + k.xyy * e) + k.yyx * map(p + k.yyx * e) + k.yxy * map(p + k.yxy * e) + k.xxx * map(p + k.xxx * e));
}

// ---------- surfaces ----------
float lodFor(float t, float rad, float texW) {
  float fp = t * (2. * tan(uFov * .5)) / R.y;
  return max(0., log2(max(fp * texW / (6.2831853 * rad), 1e-4)));
}
vec2 sph(vec3 n) { return vec2(atan(n.z, n.x) / 6.2831853 + .5, acos(clamp(n.y, -1., 1.)) / PI); }

float crater(vec3 n, float scale, float seed) {
  vec3 p = n * scale; vec3 ip = floor(p), fp = fract(p);
  float h = 0.;
  for (int x = -1; x <= 1; x++) for (int y = -1; y <= 1; y++) for (int z = -1; z <= 1; z++) {
    vec3 g = vec3(x, y, z); vec3 r = h33(ip + g + seed);
    if (r.z < .45) continue;
    vec3 c = g + r * .8 + .1; float rad = .16 + .26 * r.x * r.x;
    float dd = length(fp - c) / rad;
    if (dd < 1.6) h += -(1. - dd * dd) * .55 * step(dd, 1.) + .32 * exp(-pow((dd - 1.05) / .16, 2.)) * (r.y * .5 + .5) * (1. - step(1.35, dd));
  }
  return h;
}
float moonH(vec3 n, float fp) {
  float h = 0.;
  h += crater(n, 7., 1.) * .8;
  if (fp < .03) h += crater(n, 17., 2.) * .5;
  if (fp < .012) h += crater(n, 41., 3.) * .3;
  if (fp < .004) h += crater(n, 97., 4.) * .2;
  return h + (fp < .004 ? (fbm3(n * 60.) - .5) * .12 : 0.);
}
vec3 moonSurf(vec3 nl, vec3 nw, float t, float seedRot, out vec3 N) {
  float fp = t * (2. * tan(uFov * .5)) / R.y / RM;
  vec2 uv = sph(nl);
  vec3 alb = textureLod(tMoon, vec2(uv.x, uv.y), lodFor(t, RM, 1024.) + log2(1. / max(sqrt(1. - nl.y * nl.y), .1))).rgb;
  float g = dot(alb, vec3(.333));
  float hh = moonH(nl, fp);
  // finite-difference bump
  vec3 tu = normalize(cross(nl, vec3(0., 1., 0.) + 1e-3)), tv = cross(nl, tu);
  float e = max(.004, fp * .5);
  float hu = moonH(normalize(nl + tu * e), fp), hv = moonH(normalize(nl + tv * e), fp);
  vec3 bump = (tu * (hu - hh) + tv * (hv - hh)) / e * .018 * smoothstep(.01, .002, fp);
  N = normalize(nw - bump * 1.);
  // young bright rayed craters: Tycho, Copernicus, Kepler (lat/lon on near side)
  float ray = 0.;
  vec2 ll = vec2((uv.x - .5) * 360., 90. - uv.y * 180.);
  vec3 cs[3] = vec3[3](vec3(-11., -43.3, .9), vec3(-20., 9.7, .55), vec3(-38., 8.1, .35));
  for (int i = 0; i < 3; i++) {
    float lo = radians(cs[i].x), la = radians(cs[i].y);
    vec3 cn = vec3(cos(la) * cos(lo), sin(la), -cos(la) * sin(lo));
    float ang = acos(clamp(dot(nl, cn), -1., 1.));
    vec3 pr = normalize(nl - cn * dot(nl, cn)); float az = atan(dot(pr, cross(vec3(0, 1, 0), cn)), dot(pr, vec3(0, 1, 0)));
    float rays = pow(abs(sin(az * 11. + fbm3(vec3(az * 3., i, 1.)) * 6.)), 4.) * (.4 + .6 * vn(vec3(az * 7., i, 5.)));
    ray += cs[i].z * (smoothstep(.06, .015, ang) * 1.2 + smoothstep(.55, .03, ang) * rays * .45) * smoothstep(.05, .012, fp * 8.);
  }
  vec3 col = vec3(g * 1.15) * vec3(1., .98, .94);
  col *= .8 + .5 * (fbm3(nl * 14.) - .45) * 1.3;
  col *= 1. + hh * .35 * smoothstep(.01, .002, fp);
  col = mix(col, vec3(.92, .9, .86), clamp(ray, 0., 1.) * .8);
  return col;
}

vec3 earthSurf(vec3 nl, vec3 nw, float t, vec3 V, float rad, out vec3 emis, out float spec, out float atm) {
  vec2 uv = sph(nl); float lod = lodFor(t, rad, 2048.) + log2(1. / max(sqrt(1. - nl.y * nl.y), .08));
  vec3 alb = textureLod(tEarth, uv, lod).rgb;
  float sp = textureLod(tSpec, uv, lod).r;
  float cl = smoothstep(.04, .75, textureLod(tCloud, vec2(fract(uv.x + uT * .004), uv.y), lodFor(t, rad, 2048.)).r);
  vec3 lights = textureLod(tLights, uv, lod).rgb;
  float ndl = dot(nw, LD);
  float day = smoothstep(-.12, .22, ndl);
  alb = pow(alb, vec3(1.08)) * 1.25;
  vec3 ocean = vec3(.03, .14, .36); alb = mix(alb, ocean, sp * .7);
  alb = mix(alb, vec3(.95, .96, 1.), cl * .9);
  spec = sp * (1. - cl) * smoothstep(.02, .004, t * .0015 / rad);
  emis = lights * (1. - day) * (1. - cl * .8) * vec3(1.3, .85, .45) * 1.6;
  float fres = pow(1. - max(dot(nw, V), 0.), 3.);
  atm = fres * (.25 + .75 * smoothstep(-.3, .5, ndl));
  return alb;
}

vec3 jupiterSurf(vec3 nl, float t, float spin) {
  float fpj = t * .89 / R.y / RJ; float hf = smoothstep(.02, .004, fpj);
  float lat = nl.y; float lon = atan(nl.z, nl.x);
  vec3 w = vec3(nl.x, nl.y * 3.2, nl.z) * 5.;
  float warp = fbm(w * 1.3 + vec3(0, lat * 18., 0)) - .5;
  float band = lat + .10 * warp * (1. - lat * lat) + .02 * sin(lat * 26.);
  float b = sin(band * 21. + 1.) * .5 + sin(band * 9. - .4) * .35 + sin(band * 47.) * .12 * hf;
  vec3 zone = vec3(.93, .86, .72), belt = vec3(.62, .38, .22), dark = vec3(.40, .22, .14);
  vec3 col = mix(belt, zone, smoothstep(-.5, .6, b));
  col = mix(col, dark, smoothstep(.65, 1., -b) * .55);
  float streak = fbm(vec3(lon * 7. + lat * 3., lat * 60., 2.)) ;
  col *= .82 + .36 * mix(.5, streak, hf);
  float edge = abs(fract(band * 4.5) - .5);                     // turbulence on band boundaries
  float turb = fbm(vec3(lon * 14. + warp * 10., lat * 38., 5.) * 1.2);
  col = mix(col, vec3(.96, .9, .8), smoothstep(.55, .85, turb) * smoothstep(.34, .5, edge) * .35 * hf);
  // Great Red Spot at 22 deg S, plus white ovals
  float gl = radians(-22.); vec2 gp = vec2(lon - (-1.0), lat - sin(gl));
  gp.x = mod(gp.x + PI, 2. * PI) - PI;
  vec2 q = vec2(gp.x / .24, gp.y / .085);
  float g = length(q);
  vec3 grs = mix(vec3(.72, .22, .12), vec3(.9, .5, .32), fbm(vec3(q * 3., 1.)));
  grs *= .8 + .3 * sin(atan(q.y, q.x) * 3. + g * 7. - uT * .3 + fbm(vec3(q * 5., 2.)) * 3.);
  col = mix(col, vec3(.74, .62, .5), smoothstep(1.55, 1.1, g) * .5);          // pale collar
  col = mix(col, grs, smoothstep(1.0, .8, g));
  for (int i = 0; i < 4; i++) {
    float fi = float(i); vec2 oq = vec2(mod(lon - (-.2 + fi * 1.6) + PI, 2. * PI) - PI, lat - (-.42 + fi * .03)) / vec2(.05, .02);
    col = mix(col, vec3(.97, .94, .88), smoothstep(1., .6, length(oq)) * .85);
  }
  return col * 1.05;
}

vec3 sunSurf(vec3 nl, vec3 nw, vec3 V, float t) {
  float mu = clamp(dot(nw, V), 0., 1.);
  float tm = uT * .5;
  // flow: domain-warped so the cells stream and boil instead of sitting still
  vec3 wv = nl + .06 * vec3(fbm3(nl * 5. + tm * .12), fbm3(nl * 5. + 7. - tm * .1), fbm3(nl * 5. + 13.));
  vec3 p = wv * 30.;
  vec3 ip = floor(p), fp = fract(p); float d1 = 9., d2 = 9.;
  for (int x = -1; x <= 1; x++) for (int y = -1; y <= 1; y++) for (int z = -1; z <= 1; z++) {
    vec3 g = vec3(x, y, z); vec3 r = h33(ip + g);
    r = .5 + .5 * sin(tm * (.7 + r) + 6.2831 * r);
    float dd = length(g + r - fp);
    if (dd < d1) { d2 = d1; d1 = dd; } else if (dd < d2) d2 = dd;
  }
  float lane = smoothstep(.0, .38, d2 - d1);           // 0 in the dark intergranular lanes, 1 at cell cores
  float core = smoothstep(.55, 1., 1. - d1 * .9);      // hotter cell centres
  float super_ = fbm(nl * 6. + tm * .08);
  float act = smoothstep(.5, .85, fbm(nl * 4. + 3.));  // active regions: brighter and more violent
  vec3 lane_c = vec3(.45, .035, .0), mid_c = vec3(1., .38, .05), hot_c = vec3(1., .86, .45), wht = vec3(1., .97, .85);
  vec3 col = mix(lane_c, mid_c, pow(lane, 1.7));
  col = mix(col, hot_c, core * lane * (.35 + .5 * super_));
  col = mix(col, wht, core * core * act * .7);
  col *= max(.3 + 1.6 * super_, .12);
  // big sunspot groups with umbra + penumbra
  float sn = vn(nl * 5. + 3.7);
  float spm = smoothstep(.60, .72, sn) * smoothstep(.2, .6, 1. - abs(nl.y - .1) * 2.2);
  float um = smoothstep(.72, .8, sn) * spm;
  col = mix(col, vec3(.35, .08, .01), spm * .75);
  col = mix(col, vec3(.02, .004, 0.), um);
  // bright plage around spots, arcs of magnetic brightening
  col += vec3(1., .7, .35) * smoothstep(.45, .7, sn) * (1. - spm) * .5;
  col += vec3(1., .6, .25) * pow(max(vn(nl * 14. + tm * .3), 0.), 6.) * 1.5;
  // limb darkening and reddening
  float ld = .14 + .86 * pow(mu, .9);
  col *= ld; col = mix(col, col * vec3(1., .42, .12), pow(1. - mu, 1.5) * .9);
  col = pow(max(col, 0.), vec3(1.35, 1.8, 2.6));
  return col * .75;
}

// prominences, flares and corona around the Sun (additive, analytic)
vec3 sunGlow(vec3 ro, vec3 rd, float tmax) {
  vec3 oc = ro - S; float b = dot(oc, rd); float tc = clamp(-b, 0., tmax);
  vec3 pc = oc + rd * tc; float rmin = length(pc);
  float h = (rmin - RS) / RS;
  vec3 fwc = normalize(uCamT - uCamP); vec3 rtc = normalize(cross(fwc, vec3(0., 1., 0.))); vec3 upc = cross(rtc, fwc);
  float ang = atan(dot(pc, upc), dot(pc, rtc));
  float strm = .5 + .9 * pow(max(vn(vec3(ang * 3.2, uT * .1, 1.)),0.), 2.) + .6 * pow(max(vn(vec3(ang * 9., uT * .17, 5.)),0.), 3.);
  float cor = exp(-max(h, 0.) * 7.) * .9 + exp(-max(h, 0.) * 2.6) * .32 * strm + exp(-max(h, 0.) * .5) * .07;
  float rtrue = length(oc - rd * dot(oc, rd)); float offd = smoothstep(RS * .985, RS * 1.02, rtrue);
  cor *= smoothstep(RS * .98, RS * 1.01, rmin) * offd;
  vec3 g = vec3(1., .3, .05) * cor * 1.0;
  vec3 pp = ro + rd * tc;
  for (int i = 0; i < 9; i++) {
    float fi = float(i);
    float an = fi * 2.399 + uT * .035 + .7 * sin(fi * 1.7);
    vec3 ax = normalize(cos(an) * rtc + sin(an) * upc);
    vec3 side = rtc * -sin(an) + upc * cos(an);
    float life = .75 + .25 * sin(uT * .8 + fi * 2.1);
    float rad = RS * (.22 + .3 * fract(fi * .37 + .1)) * life;
    vec3 c = S + ax * (RS - rad * .12);
    vec2 pl = vec2(dot(pp - c, side), dot(pp - c, ax));
    float dist = abs(length(vec2(pl.x, pl.y * 1.25)) - rad); float inh = smoothstep(-.12 * rad, .25 * rad, pl.y);
    float depthT = abs(dot(pp - c, fwc));
    float tube = exp(-dist / (rad * .14)) * inh * exp(-depthT / (rad * .9));
    float strands = max(.55 + .6 * vn(vec3(pl * 14. / rad, uT * .3 + fi)), .05);
    tube *= strands * offd;
    g += vec3(1., .16, .02) * tube * 8. + vec3(1., .5, .2) * tube * tube * 3.;
  }
  // flares: bright jets lashing off the limb
  for (int i = 0; i < 3; i++) {
    float fi = float(i);
    float an = fi * 2.1 + 1.3 + uT * .07;
    vec3 ax = normalize(cos(an) * rtc + sin(an) * upc);
    vec3 d = pp - (S + ax * RS);
    float along = dot(d, ax), perp = length(d - ax * along);
    float len = RS * (.6 + .35 * sin(uT * .9 + fi * 3.));
    float jet = exp(-perp / (RS * .018 * (1. + max(along, 0.) / len * 2.))) * smoothstep(-.02 * RS, .05 * RS, along) * (1. - smoothstep(len * .3, len, along));
    g += vec3(1., .45, .15) * jet * 4.5 * offd;
  }
  return g;
}

int shellPart(float rr, float Rr, float tt, float yrel, float cutY, float t) {
  if (cutY < Rr && abs(yrel - cutY) < max(t * .003, Rr * .0012)) return 1;
  return rr > Rr - .5 * tt ? 0 : 2;
}
vec3 shade(vec3 ro, vec3 rd, float t, out float emisAdd) {
  vec3 p = ro + rd * t; vec3 n = nrm(p, max(1e-4, t * .0006));
  int id = gid; vec3 C = gC; float r = gR; float H0 = gH, P0 = gPop; vec3 G0 = gG; emisAdd = 0.;
  vec3 V = -rd; vec3 nw = n;
  vec3 col = vec3(0.); float amb = .05; float ndl = dot(n, LD);
  // soft shadow + AO
  float sh = 1., t2 = max(t * .002, .01);
  for (int i = 0; i < 18; i++) {
    vec3 sp = p + n * (t * .004 + .004) + LD * t2; float dd = map(sp);
    sh = min(sh, 7. * dd / t2); t2 += clamp(dd, .01 + t * .0004, .6 + t * .01);
    if (sh < .02 || t2 > 40.) break;
  }
  sh = mix(.3, 1., clamp(sh, 0., 1.));
  int id2 = gid; vec3 C2 = gC; float r2 = gR; // restore (map() overwritten by shadow march)
  gid = id; gC = C; gR = r; gH = H0; gPop = P0; gG = G0;
  float ao = 1.;
  for (int i = 1; i <= 3; i++) { float h = .06 * float(i) * (id == 4 || id == 3 || id == 5 ? 1. : r * 1.2) * (id == 2 || id == 1 ? 6. : 1.); ao -= (h - map(p + n * h)) * (.9 / float(i)) * (1. / (h * 3. + .2)) * h * 1.2; }
  ao = clamp(ao, .15, 1.);
  gid = id; gC = C; gR = r; gH = H0; gPop = P0; gG = G0;
  vec3 rel = p - C; vec3 nl;
  if (id == 6 || id == 7) {
    float sd = id == 7 ? 3.1 : gH;
    vec3 hm = id == 7 ? vec3(.3, .8, .5) : h33(gG * .171 + 1.7);
    mat3 rm = rotAxis(normalize(hm - .5 + 1e-3), hm.z * 6.28 + (id == 7 ? uT * .35 : 0.));
    nl = normalize(transpose(rm) * rel);
    vec3 N; vec3 alb = moonSurf(nl, nw, t, sd, N);
    float dif = max(dot(N, LD), 0.) * sh;
    // earthshine + warm bounce from the bowl
    col = alb * (dif * 2.1 + amb * .8) + alb * vec3(.3, .5, .9) * .22;
    col += alb * vec3(1., .55, .25) * .08 * ao * (id == 6 ? 1.3 : .1);
    col *= mix(.45, 1., ao);
    emisAdd = id == 6 ? (1. - gPop) * .8 : 0.;
    col += vec3(1., .85, .6) * emisAdd * .6;
  } else if (id == 5 || id == 4) {
    float rad = 1.;
    float spinA = uT * .12 + (id == 4 ? gH * 20. : 0.);
    nl = normalize(rotY(spinA) * rel);
    if (id == 4) { vec3 hr = h33(gG * .137 + 3.1); nl = normalize(rotAxis(normalize(hr - .5 + 1e-3), hr.z * 6.28) * nl); }
    float rr = length(rel);
    int part = id == 4 ? 0 : shellPart(rr, 1., TE, rel.y, uCut.x, t);
    if (part == 0) {
      vec3 em; float sp, atm; vec3 alb = earthSurf(nl, nw, t, V, rad, em, sp, atm);
      float dif = max(ndl, 0.) * sh;
      col = alb * (dif * 1.9 + amb + (id == 4 ? vec3(.22, .3, .45) + vec3(.35, .18, .08) : vec3(0.))) + em;
      vec3 hh = normalize(LD + V); col += vec3(1., .95, .85) * pow(max(dot(nw, hh), 0.), 90.) * sp * sh * 1.1 * (id == 5 ? 1. : 0.);
      col += vec3(.25, .55, 1.) * atm * (id == 5 ? 1.6 : .7);
      col *= mix(.5, 1., ao);
      if (id == 4) { col += vec3(1., .8, .55) * (1. - gPop) * .5; }
    } else if (part == 1) {
      // cut section: crust + glowing mantle
      float k = smoothstep(1., 1. - TE, rr);
      col = mix(vec3(.18, .1, .06), vec3(1., .42, .12), k * k) * (1.4 + .6 * fbm3(rel * 40.));
    } else {
      // inner wall: warm mantle glow
      float gl = fbm(rel * 5. + uT * .05);
      col = vec3(.9, .26, .06) * (.12 + .3 * gl) * (.4 + .8 * ao) + vec3(.03, .01, .005);
      col *= mix(.12, 1.1, smoothstep(-.95, .5, rel.y));   // deep: the floor sits in shadow
    }
    // closing seam glow
    float seam = exp(-abs(rel.y - uCut.x) / .02) * step(uCut.x, .99) * step(.3, uCut.x + .01);
    col += vec3(1., .7, .35) * seam * 2.0;
  } else if (id == 3 || id == 2) {
    vec3 cc = (id == 3) ? J : C; float rr = length(p - cc); float Rr = RJ; float tt = TJ;
    nl = normalize(rotY(uT * .18 + (id == 2 ? gH * 20. : 0.)) * (p - cc));
    int part = id == 2 ? 0 : shellPart(rr, Rr, tt, (p - cc).y, uCut.y * RJ, t);
    if (part == 0) {
      vec3 alb = jupiterSurf(nl, t, 0.);
      float dif = max(ndl, 0.) * sh;
      col = alb * (dif * 1.9 + amb + (id == 2 ? vec3(1., .5, .16) * .8 : vec3(0.)));
      float fres = pow(1. - max(dot(nw, V), 0.), 3.); col += vec3(.9, .65, .4) * fres * .5 * (.3 + .7 * smoothstep(-.3, .4, ndl));
      col *= mix(.5, 1., ao);
      if (id == 2) col += vec3(1., .8, .55) * (1. - gPop) * .6;
    } else if (part == 1) {
      float k = smoothstep(Rr, Rr - tt, rr);
      col = mix(vec3(.95, .8, .55), vec3(1., .35, .08), k) * 1.8;
    } else {
      vec3 q = (p - J) * .3; float swl = fbm(q + vec3(0., 0., uT * .03));
      float bnd = .5 + .5 * sin(q.y * 7. + 5. * swl); bnd *= bnd;
      col = mix(vec3(.22, .035, .01), vec3(1., .46, .1), bnd) * (.25 + .6 * ao);
      col *= mix(.1, 1.1, smoothstep(-RJ * .9, RJ * .5, (p - J).y));
    }
    if (id == 3) {
      float seam = exp(-abs((p - J).y - uCut.y * RJ) / .12) * step(uCut.y, .99);
      col += vec3(1., .75, .4) * seam * 2.;
      float edge = exp(-abs(length(p) - uWave.x) / (.012 * uWave.x + .05)) * step(.01, uWave.x);
      col += vec3(1., .85, .6) * edge * 3.;
    }
  } else if (id == 1) {
    float rr = length(p - S);
    nl = normalize(rotY(uT * .02) * (p - S));
    int part = shellPart(rr, RS, TS, (p - S).y, uCut.z * RS, t);
    if (part == 0) {
      col = sunSurf(nl, nw, V, t);
    } else if (part == 1) {
      float k = smoothstep(RS, RS - TS, rr); col = mix(vec3(1., .95, .8), vec3(1., .4, .08), k) * 4.5;
    } else {
      vec3 q = (p - S) * .012; float swl = fbm(q + vec3(0., 0., uT * .03)); float gl = fbm(q * 3. + swl * 2. + uT * .04);
      col = mix(vec3(.45, .05, .005), vec3(1., .5, .1), smoothstep(.25, .75, gl)) * 1.9;
      col *= mix(.15, 1.1, smoothstep(-RS * .9, RS * .5, (p - S).y));
    }
    float edge = exp(-abs(length(p) - uWave.y) / (.012 * uWave.y + .3)) * step(.01, uWave.y);
    col += vec3(1., .85, .6) * edge * 2.5;
    emisAdd = 1.;
  }
  return col;
}

void main() {
  vec2 uv = (gl_FragCoord.xy - .5 * R) / R.y;
  uv.y -= .07;   // lens shift: subject rides high, counter sits below
  float cr = cos(uRoll), sr = sin(uRoll); uv = mat2(cr, -sr, sr, cr) * uv;
  vec3 ro = uCamP; vec3 fw = normalize(uCamT - ro);
  vec3 rt = normalize(cross(fw, vec3(0., 1., 0.))); vec3 up = cross(rt, fw);
  float fl = 1. / tan(uFov * .5) * .5;
  vec3 rd = normalize(uv.x * rt + uv.y * up + fw * fl);
  // space backdrop: deep navy gradient with faint stars (parallax stars are added in comp)
  float sky = .5 + .5 * rd.y;
  vec3 bg = mix(vec3(.012, .016, .034), vec3(.03, .035, .07), sky);
  bg += vec3(.25, .12, .08) * pow(max(dot(rd, LD), 0.), 6.) * .05;
  vec3 stars = vec3(0.); {
    vec3 sp = rd * 220.; vec3 ip = floor(sp); vec3 fr = fract(sp) - .5;
    float h = h31(ip); if (h > .985) { float d = length(fr - (h33(ip) - .5) * .6); stars = vec3(.9, .95, 1.) * smoothstep(.12, 0., d) * (h - .985) * 60.; }
  }
  // deeper sky: denser stars of varied brightness, a faint milky band and a violet nebula wash
  { vec3 sp2 = rd * 140.; vec3 ip2 = floor(sp2); vec3 fr2 = fract(sp2) - .5; float h2 = h31(ip2 + 3.1);
    if (h2 > .93) { float d2 = length(fr2 - (h33(ip2 + 1.) - .5) * .6); stars += mix(vec3(1., .85, .7), vec3(.7, .85, 1.), h33(ip2).x) * smoothstep(.15, 0., d2) * (h2 - .93) * 18.; } }
  float band = exp(-pow(dot(rd, normalize(vec3(.3, .8, -.5))) * 3.2, 2.));
  float neb = fbm(rd * 2.2 + 4.);
  bg += (vec3(.05, .035, .11) * neb + vec3(.04, .05, .09) * band * (.4 + fbm(rd * 7.))) * .9;
  bg += stars * .8;
  float t = 0.; float dist; bool hit = false; vec3 glow = vec3(0.);
  float tmax = 2500.;
  for (int i = 0; i < 200; i++) {
    vec3 p = ro + rd * t; dist = map(p);
    if (dist < max(.0004, t * .0003)) { hit = true; break; }
    t += dist * .95; if (t > tmax) break;
  }
  vec3 col = bg; float ea = 0.;
  if (hit) { col = shade(ro, rd, t, ea); }
  // volumetric-ish glow of the Sun bowl (corona, prominences) when its shell is lit
  if (uWave.y > 0.) col += sunGlow(ro, rd, hit ? t : tmax) * smoothstep(0., 40., uWave.y);
  // Earth atmosphere halo + Jupiter haze for rays that miss
  {
    vec3 oc = ro; float b = dot(oc, rd); float tc = clamp(-b, 0., hit ? t : tmax); float rmin = length(oc + rd * tc);
    if (!hit) col += vec3(.2, .45, 1.) * exp(-max(rmin - 1., 0.) * 13.) * .55 * (.9 + .25 * sin(uT * 2.1));
  }
  // exposure + filmic tonemap
  col *= uExpo;
  col = col * (2.51 * col + .03) / (col * (2.43 * col + .59) + .14);
  col = pow(clamp(col, 0., 1.), vec3(1. / 2.2));
  o = vec4(col, hit ? clamp(log2(t + 1.) / 11.5, 0., 1.) * .98 + .02 : 0.);
}
