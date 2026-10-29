#version 300 es
// The Moon Shouldn't Fit: every shot of the eclipse reel in one shader, picked by uShot.
//  0 telephoto Sun/Moon (2D, units = solar radii)   1 Earth + Moon shadow (3D, units = Earth radii)
//  2 hill crowd at totality (2D)                    3 back of a head looking up (2D)
//  4 Earth limb -> Moon, the gap opening (3D)
precision highp float;
uniform vec2 R;
uniform float uT, uShot, uZoom, uMR, uExp, uDark, uFov, uA, uB, uSky, uPhot;
uniform vec3 uMoonC, uBead, uCamP, uCamT, uSun, uCen;
uniform sampler2D tEarth, tSpec, tCloud, tLights, tMoon;
out vec4 o;
const float PI = 3.14159265;

// ---------- noise ----------
float h21(vec2 p) { p = fract(p * vec2(123.34, 456.21)); p += dot(p, p + 45.32); return fract(p.x * p.y); }
float h31(vec3 p) { p = fract(p * .3183099 + .1); p *= 17.; return fract(p.x * p.y * p.z * (p.x + p.y + p.z)); }
vec3 h33(vec3 p) { p = vec3(dot(p, vec3(127.1, 311.7, 74.7)), dot(p, vec3(269.5, 183.3, 246.1)), dot(p, vec3(113.5, 271.9, 124.6))); return fract(sin(p) * 43758.5453); }
float vn(vec3 p) {
  vec3 i = floor(p), f = fract(p); f = f * f * (3. - 2. * f);
  return mix(mix(mix(h31(i), h31(i + vec3(1, 0, 0)), f.x), mix(h31(i + vec3(0, 1, 0)), h31(i + vec3(1, 1, 0)), f.x), f.y),
             mix(mix(h31(i + vec3(0, 0, 1)), h31(i + vec3(1, 0, 1)), f.x), mix(h31(i + vec3(0, 1, 1)), h31(i + vec3(1, 1, 1)), f.x), f.y), f.z);
}
float fbm(vec3 p) { float a = .5, s = 0.; for (int i = 0; i < 5; i++) { s += a * vn(p); p = p * 2.03 + 11.7; a *= .5; } return s; }
float fbm3(vec3 p) { float a = .5, s = 0.; for (int i = 0; i < 3; i++) { s += a * vn(p); p = p * 2.03 + 11.7; a *= .5; } return s; }

vec3 stars(vec2 p, float dens) {  // p in pixels-ish units
  vec3 c = vec3(0.);
  for (int k = 0; k < 2; k++) {
    float sc = k == 0 ? 90. : 34.;
    vec2 g = floor(p / sc), f = fract(p / sc);
    float r = h21(g + float(k) * 7.1);
    if (r < dens * (k == 0 ? 1. : .25)) {
      vec2 sp = vec2(h21(g + 1.3), h21(g + 2.9)) * .8 + .1;
      float d = length(f - sp) * sc;
      float b = pow(h21(g + 5.5), 3.) * (k == 0 ? 1. : 2.5);
      c += mix(vec3(.75, .85, 1.), vec3(1., .85, .7), h21(g + 9.)) * b * exp(-d * d / (k == 0 ? .9 : 1.6));
    }
  }
  return c;
}

// ---------- Sun ----------
vec3 photosphere(vec2 p, float r) {     // p inside unit disc
  vec3 n = vec3(p, sqrt(max(1. - r * r, 0.)));
  float mu = n.z, tm = uT * .45;
  vec3 wv = n + .025 * vec3(fbm3(n * 6. + tm * .1), fbm3(n * 6. + 7. - tm * .1), 0.);
  vec3 q = wv * 70.;
  vec3 ip = floor(q), fp = fract(q); float d1 = 9., d2 = 9.;
  for (int x = -1; x <= 1; x++) for (int y = -1; y <= 1; y++) for (int z = -1; z <= 1; z++) {
    vec3 g = vec3(x, y, z); vec3 rr = h33(ip + g);
    rr = .5 + .45 * sin(tm * (.6 + rr) + 6.2831 * rr);
    float dd = length(g + rr - fp);
    if (dd < d1) { d2 = d1; d1 = dd; } else if (dd < d2) d2 = dd;
  }
  float lane = smoothstep(0., .32, d2 - d1);
  float sup = fbm(n * 9. + tm * .05);
  float act = smoothstep(.55, .85, fbm(n * 3.5 + 3.));
  float b = .45 + .5 * pow(lane, 1.3) + .22 * (sup - .5) + .12 * act;
  // sunspot groups
  float sn = vn(n * 6.3 + vec3(3.7, 1.2, .4)) * .65 + vn(n * 17. + 2.) * .35;
  float band = smoothstep(.55, .2, abs(abs(n.y) - .28));
  float pen = smoothstep(.72, .76, sn) * band, um = smoothstep(.77, .8, sn) * band;
  b = mix(b, .38 + .1 * vn(n * 160.), pen); b = mix(b, .06, um);
  b += .2 * smoothstep(.6, .72, sn) * (1. - pen) * band;   // faculae
  float ld = .3 + .7 * pow(mu, .55);
  b *= ld;
  // filtered gold: hotter centre, deep orange limb
  vec3 col = mix(vec3(.85, .16, .01), vec3(1., .6, .16), smoothstep(.15, 1., b));
  col = mix(col, vec3(1., .86, .55), smoothstep(.8, 1.1, b) * .6);
  return col * b * 1.25;
}

// tiny angle helper for streamers
float adist(float a, float b) { float d = mod(a - b + PI, 2. * PI) - PI; return abs(d); }

vec3 corona(vec2 p, float r) {
  float h = max(r - 1., 0.);
  float a = atan(p.y, p.x);
  float tilt = .35;
  // helmet streamers near the solar equator, tapering with height
  float st = 0.;
  for (int i = 0; i < 6; i++) {
    float fi = float(i);
    float ai = tilt + (i < 3 ? 0. : PI) + (fi - (i < 3 ? 1. : 4.)) * .42 + .15 * sin(fi * 3.1);
    float w = (.22 + .12 * fract(fi * .61)) / (1. + h * 1.4);
    st += exp(-pow(adist(a, ai) / w, 2.)) * (.6 + .5 * fract(fi * .37));
  }
  // polar plumes: fine straight rays near the poles
  float pol = pow(abs(sin(a - tilt)), 3.);
  vec2 cs = vec2(cos(a), sin(a));
  float fil = vn(vec3(cs * 26., log(r) * 1.1 + uT * .01)) * .55 + vn(vec3(cs * 70., log(r) * 2.2)) * .3 + vn(vec3(cs * 160., log(r) * 3.)) * .15;
  float fil2 = vn(vec3(cs * 18., log(r) * .6 + 3.));
  float I = exp(-h * 14.) * 1.1 + exp(-h * 3.5) * .45 * (.3 + st) + pow(r, -2.5) * .13 * (.12 + st * 1.7) + pow(r, -4.) * .12;
  I *= .8 + .4 * fil * (.7 + .6 * fil2);
  I += pol * exp(-h * 2.5) * .2 * pow(fil, 4.) * 3.;
  vec3 c = mix(vec3(1., .93, .84), vec3(.82, .88, 1.), smoothstep(0., 1.5, h)) * I;
  // chromosphere + prominences (pink-red), only just above the limb
  float ch = exp(-h * 160.) * 1.8;
  float pr = 0.;
  for (int i = 0; i < 5; i++) {
    float fi = float(i);
    float ai = fi * 1.37 + .9;
    float hh = .025 + .05 * fract(fi * .53);
    float da = adist(a, ai) * r;
    float blob = exp(-pow(da / (.025 + .02 * fract(fi * .71)), 2.)) * exp(-h / hh) * smoothstep(0., .004, h + .002);
    blob *= .5 + .8 * vn(vec3(p * 90., fi));
    pr += blob;
  }
  c += vec3(1., .16, .3) * (ch + pr * 2.2);
  return c;
}

vec3 moonDisc(vec2 q, float mr, float lit) {   // q relative to the Moon centre, in solar radii
  vec2 u = q / mr; float rr = dot(u, u);
  vec3 n = vec3(u, sqrt(max(1. - rr, 0.)));
  float lon = atan(n.x, n.z) + 1.2, lat = asin(clamp(n.y, -1., 1.));
  vec3 t = texture(tMoon, vec2(lon / (2. * PI) + .5, .5 - lat / PI)).rgb;
  float es = .25 + .75 * n.z;
  return t * es * lit;
}

vec3 sky(vec2 px) {
  return stars(px, .22);
}

// ---------- shot 0: telephoto Sun + Moon ----------
vec3 shotSun(vec2 frag) {
  vec2 p = (frag - .5 * R) / R.y * 2. * uZoom + uCen.xy;
  float r = length(p);
  vec3 c = vec3(0.);
  // sky: deep blue during totality on the ground (uSky), black in space
  vec3 skyc = mix(vec3(0.), vec3(.004, .009, .028) + vec3(.006, .012, .03) * smoothstep(-1., 1., -p.y / uZoom), uSky);
  c += skyc + stars(frag, .25) * .015 * (1. - .7 * uSky);
  vec2 q = p - uMoonC.xy; float dm = length(q);
  float mrD = max(uMR, 5. * uZoom / R.y);   // keep the far Moon a visible dot
  float inMoon = smoothstep(mrD + .0015 * uZoom, mrD - .0015 * uZoom, dm);
  c += corona(p, max(r, 1.)) * step(1., r) * .9 * uDark;
  // photosphere (+ limb antialias)
  float sdisc = smoothstep(1. + .002 * uZoom, 1. - .002 * uZoom, r);
  if (sdisc > 0.) c = mix(c, photosphere(p, min(r, .999)) * uPhot, sdisc);
  // Moon: black, with the faintest earthshine, occluding everything behind
  if (inMoon > 0.) c = mix(c, moonDisc(q, mrD, .006 + .02 * uA), inMoon);
  // diamond ring / Baily's bead: glare and starburst
  if (uBead.z > 0.) {
    vec2 d = p - uBead.xy; float dd = length(d) / uZoom;
    float th = atan(d.y, d.x);
    float spikes = pow(abs(cos(th * 3. + .4)), 160.) * exp(-dd * 9.) + pow(abs(cos(th * 3. + 1.45)), 300.) * exp(-dd * 14.) * .6;
    float core = .0012 / (dd * dd + .00007);
    float halo = exp(-dd * 10.) * .35 + exp(-dd * 3.5) * .035;
    c += vec3(1., .96, .9) * uBead.z * (core + halo + spikes * .9);
  }
  return c;
}

// ---------- 3D helpers ----------
vec2 isph(vec3 ro, vec3 rd, vec3 c, float r) {
  vec3 oc = ro - c; float b = dot(oc, rd), q = dot(oc, oc) - r * r, h = b * b - q;
  if (h < 0.) return vec2(-1.); h = sqrt(h); return vec2(-b - h, -b + h);
}
// fraction of the solar disc hidden by a disc of angular radius rm at angular separation s (rs = Sun angular radius)
float overlap(float rs, float rm, float s) {
  if (s >= rs + rm) return 0.;
  if (s <= abs(rm - rs)) return rm >= rs ? 1. : (rm * rm) / (rs * rs);
  float a = rs * rs * acos(clamp((s * s + rs * rs - rm * rm) / (2. * s * rs), -1., 1.));
  float b = rm * rm * acos(clamp((s * s + rm * rm - rs * rs) / (2. * s * rm), -1., 1.));
  float k = .5 * sqrt(max((-s + rs + rm) * (s + rs - rm) * (s - rs + rm) * (s + rs + rm), 0.));
  return (a + b - k) / (PI * rs * rs);
}
vec3 camRay(vec2 frag, out vec3 ro) {
  vec2 uv = (frag - .5 * R) / R.y;
  vec3 fw = normalize(uCamT - uCamP), rt = normalize(cross(fw, vec3(0, 1, 0))), up = cross(rt, fw);
  ro = uCamP;
  return normalize(fw + (uv.x * rt + uv.y * up) * 2. * tan(uFov * .5));
}
vec3 earthShade(vec3 p, vec3 rd, vec3 L, float occl) {
  vec3 n = normalize(p);
  vec3 nr = n; float rot = 2.4 + uT * .01;
  float lon = atan(nr.x * cos(rot) - nr.z * sin(rot), nr.x * sin(rot) + nr.z * cos(rot)), lat = asin(clamp(nr.y, -1., 1.));
  vec2 uv = vec2(lon / (2. * PI) + .5, .5 - lat / PI);
  vec3 day = pow(texture(tEarth, uv).rgb, vec3(1.25));
  float cl = texture(tCloud, uv + vec2(uT * .0004, 0.)).r;
  float spec = texture(tSpec, uv).r;
  float ndl = dot(n, L);
  float lit = smoothstep(-.05, .25, ndl) * (1. - occl);
  vec3 V = -rd;
  float sl = pow(1. - occl, 2.6);
  vec3 col = mix(day, vec3(1.), cl * .9) * max(ndl, 0.) * sl * .95;
  vec3 hlf = normalize(L + V);
  col += vec3(1., .85, .7) * pow(max(dot(n, hlf), 0.), 90.) * spec * (1. - cl) * .3 * (1. - occl);
  // city lights where it is dark (night side and the umbra core)
  float dark = 1. - smoothstep(-.1, .1, ndl);
  col += texture(tLights, uv).rgb * vec3(1., .75, .45) * dark * 1.1 * (1. - cl * .8) * uB;
  // atmosphere rim
  float fres = pow(1. - max(dot(n, V), 0.), 3.);
  col += vec3(.25, .5, 1.) * fres * smoothstep(-.2, .4, ndl) * .9 * (1. - .6 * occl);
  col += vec3(.3, .55, 1.) * .04 * max(ndl, 0.);
  return col;
}
vec3 moonShade(vec3 p, vec3 c, float r, vec3 L) {
  vec3 n = normalize(p - c);
  float lon = atan(n.x, n.z) + 2.5, lat = asin(clamp(n.y, -1., 1.));
  vec3 t = pow(texture(tMoon, vec2(lon / (2. * PI) + .5, .5 - lat / PI)).rgb, vec3(1.15));
  float ndl = dot(n, L);
  return t * (max(ndl, 0.) * 1.35 + .004);
}

// ---------- shot 1: Earth with the Moon's shadow, shot 4: Earth limb looking out to the Moon ----------
vec3 shotSpace(vec2 frag) {
  vec3 ro; vec3 rd = camRay(frag, ro);
  vec3 L = normalize(uSun);
  vec3 M = uMoonC; float mr = .2727;
  vec3 c = stars(frag, .35) * .9;
  // Sun glare if in view
  float sd = max(dot(rd, L), 0.);
  c += vec3(1., .9, .75) * (pow(sd, 2000.) * 6. + pow(sd, 120.) * .15);
  float tb = 1e9;
  vec2 he = isph(ro, rd, vec3(0.), 1.);
  vec2 hm = isph(ro, rd, M, mr);
  // atmosphere halo just off the limb
  vec3 oc = ro; float bb = dot(oc, rd); float tc = max(-bb, 0.); float rmin = length(oc + rd * tc);
  if (he.x < 0.) {
    float hh = max(rmin - 1., 0.);
    float side = max(dot(normalize(oc + rd * tc), L) + .25, 0.);
    c += vec3(.3, .55, 1.) * exp(-hh * 55.) * .9 * side;
  }
  if (he.x > 0.) {
    vec3 p = ro + rd * he.x; tb = he.x;
    vec3 d = M - p; float dl = length(d);
    float s = asin(min(length(cross(d / dl, L)), 1.));
    float occl = overlap(.00465 * uA, asin(mr / dl), s);
    c = earthShade(p, rd, L, occl);
  }
  if (hm.x > 0. && hm.x < tb) c = moonShade(ro + rd * hm.x, M, mr, L);
  return c;
}

// ---------- shot 2: crowd on a hill at totality ----------
float sdCapsule(vec2 p, vec2 a, vec2 b, float r) { vec2 pa = p - a, ba = b - a; float h = clamp(dot(pa, ba) / dot(ba, ba), 0., 1.); return length(pa - ba * h) - r; }
float smin(float a, float b, float k) { float h = clamp(.5 + .5 * (b - a) / k, 0., 1.); return mix(b, a, h) - k * h * (1. - h); }
float person(vec2 p, float s, float pose, float lean) {   // p relative to feet, height ~ s
  p /= s; p.x -= lean * max(p.y - .5, 0.) * .12;
  float d = length((p - vec2(-.015 * lean - .012, .905)) * vec2(1., .88)) - .068;   // head, tipped back
  d = min(d, sdCapsule(p, vec2(0., .8), vec2(-.005, .84), .03));                  // neck
  // torso: shoulders taper to the waist
  float tor = sdCapsule(p, vec2(0., .55), vec2(0., .72), .072);
  tor = smin(tor, sdCapsule(p, vec2(-.085, .745), vec2(.085, .745), .04), .06);
  d = smin(d, tor, .02);
  d = min(d, sdCapsule(p, vec2(-.07, .02), vec2(-.045, .5), .034 + .01 * smoothstep(.2, .5, p.y)));   // legs
  d = min(d, sdCapsule(p, vec2(.065, .02), vec2(.045, .5), .034 + .01 * smoothstep(.2, .5, p.y)));
  d = min(d, sdCapsule(p, vec2(-.09, .015), vec2(-.04, .015), .02));            // feet
  d = min(d, sdCapsule(p, vec2(.04, .015), vec2(.09, .015), .02));
  if (pose < .33) {           // arm raised pointing at the sky
    d = min(d, sdCapsule(p, vec2(.1, .76), vec2(.2, .93), .026));
    d = min(d, sdCapsule(p, vec2(.2, .93), vec2(.3, 1.1), .022));
    d = min(d, sdCapsule(p, vec2(-.11, .75), vec2(-.13, .5), .026));
  } else if (pose < .66) {    // holding a phone up
    d = min(d, sdCapsule(p, vec2(.1, .76), vec2(.16, .62), .026));
    d = min(d, sdCapsule(p, vec2(.16, .62), vec2(.12, .95), .022));
    d = min(d, sdCapsule(p, vec2(-.1, .76), vec2(-.03, .64), .026));
    d = min(d, sdCapsule(p, vec2(-.03, .64), vec2(.1, .96), .022));
  } else {                    // hands in pockets / at sides
    d = min(d, sdCapsule(p, vec2(.11, .75), vec2(.13, .52), .026));
    d = min(d, sdCapsule(p, vec2(-.11, .75), vec2(-.13, .52), .026));
  }
  return d * s;
}
float hill(float x) { return .2 + .045 * sin(x * 2.1 + .5) + .02 * sin(x * 5.3) + .006 * (fbm3(vec3(x * 18., 0., 0.)) - .5); }
vec3 coronaAt(vec3 bg, vec2 uv, vec2 c, float rad, float bright) {
  vec2 p = (uv - c) / rad; float r = length(p);
  vec3 col = bg;
  if (r > 1.) col += corona(p, r) * bright;
  col += vec3(.5, .6, 1.) * .03 * exp(-(r - 1.) * .25) * bright;   // scattered glow in the air
  float inm = smoothstep(1.03 + 1.5 / (rad * R.y), 1.03 - 1.5 / (rad * R.y), length(p - uMoonC.xy));
  return mix(col, moonDisc(p - uMoonC.xy, 1.03, .003), inm);
}
vec3 shotHill(vec2 frag) {
  vec2 uv = frag / R.y; float ax = R.x / R.y;
  float y = uv.y;
  // totality sky: indigo zenith, 360-degree sunset ring low down
  vec3 zen = vec3(.008, .016, .05), mid = vec3(.03, .05, .13), hor = vec3(1., .45, .16);
  vec3 c = mix(mid, zen, smoothstep(.25, 1., y));
  float hb = exp(-max(y - .19, 0.) * 14.);
  c += hor * hb * .55 * uDark + vec3(1., .75, .4) * exp(-max(y - .19, 0.) * 40.) * .4 * uDark;
  c += vec3(.02, .03, .06) * (1. - uDark) * 6.;        // brighter before totality
  c += stars(frag, .3) * .25 * uDark;
  // Venus, low and bright
  vec2 vp = vec2(ax * .22, .63); float dv = length(uv - vp) * R.y;
  c += vec3(1., .97, .9) * (exp(-dv * dv / 3.) * 1.2 + exp(-dv / 6.) * .05) * uDark;
  // the eclipse
  c = coronaAt(c, uv, uCen.xy * vec2(ax, 1.), uZoom, uExp);
  // far ridges with aerial perspective, glowing from the horizon ring
  float r1 = .175 + .015 * sin(uv.x * 4. + 1.) + .01 * fbm3(vec3(uv.x * 6., 1., 0.));
  float r2 = .16 + .02 * sin(uv.x * 3. + 2.5) + .012 * fbm3(vec3(uv.x * 9., 3., 0.));
  if (y < r1) c = mix(c, vec3(.32, .13, .07) * uDark + vec3(.05, .05, .08), .85);
  if (y < r2) c = mix(c, vec3(.13, .05, .04) * uDark + vec3(.025, .025, .04), .9);
  // our hill and the crowd, pure silhouette with a warm rim from the horizon
  float hx = uv.x / ax + uA;
  float hy = hill(hx);
  float d = y - hy;
  for (int i = 0; i < 8; i++) {
    float fi = float(i);
    float px = (fi + .45 * h21(vec2(fi, 2.))) / 7.6 * 1.15 - .08;
    float sc = .12 + .04 * h21(vec2(fi, 5.)) + (i == 4 ? .02 : 0.);
    vec2 fp = vec2((px - uA) * ax, hill(px) - .004);
    d = min(d, person(uv - fp, sc, h21(vec2(fi, 9.)), h21(vec2(fi, 11.)) - .5));
  }
  float sil = smoothstep(.0012, -.0012, d);
  vec3 rim = vec3(1., .5, .2) * exp(-abs(d) * 1500.) * .12 * uDark * smoothstep(.0, .2, uv.y);
  c = mix(c, vec3(.004, .004, .008), sil) + rim * sil;
  // a few phone screens glowing
  for (int i = 0; i < 8; i++) {
    float fi = float(i); float pose = h21(vec2(fi, 9.));
    if (pose < .33 || pose > .66) continue;
    float px = (fi + .45 * h21(vec2(fi, 2.))) / 7.6 * 1.15 - .08;
    float sc = .12 + .04 * h21(vec2(fi, 5.)) + (i == 4 ? .02 : 0.);
    vec2 fp = vec2((px - uA) * ax, hill(px) - .004) + vec2(.115, .97) * sc;
    vec2 q = abs(uv - fp) - vec2(.012, .02) * sc;
    float sd = max(q.x, q.y);
    c += vec3(.7, .85, 1.) * (smoothstep(.001, 0., sd) * .5 + exp(-max(sd, 0.) * 300.) * .04) * uB;
  }
  // foreground grass
  float gx = uv.x * 260.; float gi = floor(gx);
  float gh = .045 + .05 * h21(vec2(gi, 1.)); float gf = fract(gx) - .5 + sin(uT * 1.3 + gi) * .06 * (uv.y / .1);
  if (uv.y < gh && abs(gf) < .25 * (1. - uv.y / gh)) c = vec3(.002);
  if (uv.y < .03) c = vec3(.002);
  return c;
}

// ---------- shot 3: one face in profile, looking up at the corona ----------
const int NP = 145;
const vec2 PF[NP] = vec2[NP](vec2(-1.9000, -2.6000), vec2(-1.9848, -2.4332), vec2(-1.9504, -2.2076), vec2(-1.8436, -1.9604), vec2(-1.7112, -1.7288), vec2(-1.6000, -1.5500),
  vec2(-1.5052, -1.4336), vec2(-1.3956, -1.3548), vec2(-1.2784, -1.2992), vec2(-1.1608, -1.2524), vec2(-1.0500, -1.2000), vec2(-0.9409, -1.1433),
  vec2(-0.8286, -1.0918), vec2(-0.7210, -1.0438), vec2(-0.6255, -0.9971), vec2(-0.5500, -0.9500), vec2(-0.4960, -0.9034), vec2(-0.4584, -0.8585),
  vec2(-0.4348, -0.8139), vec2(-0.4228, -0.7682), vec2(-0.4200, -0.7200), vec2(-0.4317, -0.6698), vec2(-0.4594, -0.6187), vec2(-0.4954, -0.5657),
  vec2(-0.5315, -0.5098), vec2(-0.5600, -0.4500), vec2(-0.5814, -0.3846), vec2(-0.6011, -0.3143), vec2(-0.6181, -0.2417), vec2(-0.6314, -0.1694),
  vec2(-0.6400, -0.1000), vec2(-0.6440, -0.0331), vec2(-0.6440, 0.0330), vec2(-0.6400, 0.0978), vec2(-0.6320, 0.1603), vec2(-0.6200, 0.2200),
  vec2(-0.6040, 0.2774), vec2(-0.5840, 0.3331), vec2(-0.5600, 0.3861), vec2(-0.5320, 0.4354), vec2(-0.5000, 0.4800), vec2(-0.4634, 0.5202),
  vec2(-0.4221, 0.5565), vec2(-0.3771, 0.5887), vec2(-0.3294, 0.6166), vec2(-0.2800, 0.6400), vec2(-0.2269, 0.6590), vec2(-0.1694, 0.6737),
  vec2(-0.1106, 0.6839), vec2(-0.0531, 0.6894), vec2(0.0000, 0.6900), vec2(0.0490, 0.6853), vec2(0.0957, 0.6754), vec2(0.1399, 0.6610),
  vec2(0.1814, 0.6423), vec2(0.2200, 0.6200), vec2(0.2559, 0.5934), vec2(0.2894, 0.5621), vec2(0.3198, 0.5271), vec2(0.3469, 0.4894),
  vec2(0.3700, 0.4500), vec2(0.3894, 0.4061), vec2(0.4053, 0.3570), vec2(0.4175, 0.3070), vec2(0.4258, 0.2599), vec2(0.4300, 0.2200),
  vec2(0.4266, 0.1893), vec2(0.4159, 0.1650), vec2(0.4029, 0.1442), vec2(0.3926, 0.1235), vec2(0.3900, 0.1000), vec2(0.3961, 0.0739),
  vec2(0.4074, 0.0474), vec2(0.4228, 0.0198), vec2(0.4407, -0.0091), vec2(0.4600, -0.0400), vec2(0.4852, -0.0753), vec2(0.5173, -0.1146),
  vec2(0.5493, -0.1544), vec2(0.5742, -0.1907), vec2(0.5850, -0.2200), vec2(0.5762, -0.2404), vec2(0.5524, -0.2543), vec2(0.5220, -0.2645),
  vec2(0.4934, -0.2738), vec2(0.4750, -0.2850), vec2(0.4693, -0.2985), vec2(0.4706, -0.3124), vec2(0.4754, -0.3262), vec2(0.4797, -0.3389),
  vec2(0.4800, -0.3500), vec2(0.4745, -0.3586), vec2(0.4658, -0.3652), vec2(0.4562, -0.3710), vec2(0.4485, -0.3772), vec2(0.4450, -0.3850),
  vec2(0.4483, -0.3943), vec2(0.4566, -0.4044), vec2(0.4664, -0.4152), vec2(0.4737, -0.4271), vec2(0.4750, -0.4400), vec2(0.4679, -0.4539),
  vec2(0.4548, -0.4688), vec2(0.4394, -0.4846), vec2(0.4249, -0.5017), vec2(0.4150, -0.5200), vec2(0.4128, -0.5407), vec2(0.4160, -0.5638),
  vec2(0.4198, -0.5874), vec2(0.4194, -0.6101), vec2(0.4100, -0.6300), vec2(0.3894, -0.6467), vec2(0.3609, -0.6614), vec2(0.3277, -0.6746),
  vec2(0.2930, -0.6873), vec2(0.2600, -0.7000), vec2(0.2254, -0.7098), vec2(0.1871, -0.7161), vec2(0.1501, -0.7235), vec2(0.1194, -0.7366),
  vec2(0.1000, -0.7600), vec2(0.0909, -0.7947), vec2(0.0886, -0.8378), vec2(0.0950, -0.8874), vec2(0.1115, -0.9421), vec2(0.1400, -1.0000),
  vec2(0.1849, -1.0486), vec2(0.2450, -1.0889), vec2(0.3138, -1.1399), vec2(0.3843, -1.2206), vec2(0.4500, -1.3500), vec2(0.5274, -1.5592),
  vec2(0.6211, -1.8356), vec2(0.7061, -2.1324), vec2(0.7574, -2.4028), vec2(0.7500, -2.6000), vec2(0.6856, -2.7136), vec2(0.5808, -2.7748),
  vec2(0.4332, -2.7992), vec2(0.2404, -2.8024), vec2(0.0000, -2.8000), vec2(-0.3416, -2.7992), vec2(-0.7828, -2.7896), vec2(-1.2432, -2.7604),
  vec2(-1.6424, -2.7008));
float sdPoly(vec2 p) {
  float d = dot(p - PF[0], p - PF[0]); float s = 1.;
  for (int i = 0, j = NP - 1; i < NP; j = i, i++) {
    vec2 e = PF[j] - PF[i], w = p - PF[i];
    vec2 b = w - e * clamp(dot(w, e) / dot(e, e), 0., 1.);
    d = min(d, dot(b, b));
    bvec3 cnd = bvec3(p.y >= PF[i].y, p.y < PF[j].y, e.x * w.y > e.y * w.x);
    if (all(cnd) || all(not(cnd))) s *= -1.;
  }
  return s * sqrt(d);
}
vec3 shotHead(vec2 frag) {
  vec2 uv = frag / R.y; float ax = R.x / R.y;
  vec3 c = mix(vec3(.03, .05, .13), vec3(.006, .012, .04), smoothstep(.2, 1., uv.y));
  c += vec3(1., .45, .16) * exp(-max(uv.y - .05, 0.) * 9.) * .35;
  c += stars(frag, .3) * .25;
  c = coronaAt(c, uv, uCen.xy * vec2(ax, 1.), uZoom, uExp);
  // profile, tipped back ~32 degrees, lower left of frame
  float an = -.5; mat2 rot = mat2(cos(an), sin(an), -sin(an), cos(an));
  float sc = .2;
  vec2 hp = rot * ((uv - vec2(ax * .3 + uA, .3 + uB)) / sc);
  float d = sdPoly(hp) * sc;
  float sil = smoothstep(.0015, -.0015, d);
  // rim light from the corona on the face edge (the side facing up/right)
  vec2 toC = normalize(uCen.xy * vec2(ax, 1.) - uv);
  vec3 rim = vec3(0.);
  if (abs(d) < .01) {
    vec2 gq = vec2(sdPoly(hp + vec2(.004, 0.)), sdPoly(hp + vec2(0., .004))) - d / sc;
    vec2 nn = normalize(transpose(rot) * gq + 1e-6);
    float e = max(dot(nn, toC), 0.);
    rim = vec3(.85, .9, 1.) * exp(-max(-d, 0.) * 900.) * .6 * pow(e, 3.) * uExp;
  }
  c = mix(c, vec3(.003, .003, .006), sil) + rim * sil;
  return c;
}

void main() {
  vec2 f = gl_FragCoord.xy;
  vec3 c;
  if (uShot < .5) c = shotSun(f);
  else if (uShot < 1.5 || (uShot > 3.5 && uShot < 4.5)) c = shotSpace(f);
  else if (uShot < 2.5) c = shotHill(f);
  else c = shotHead(f);
  c *= uExp > 0. && uShot < .5 ? uExp : 1.;
  c = (c * (2.51 * c + .03)) / (c * (2.43 * c + .59) + .14);   // ACES fit
  c = pow(clamp(c, 0., 1.), vec3(1. / 2.2));
  o = vec4(c, 1.);
}
