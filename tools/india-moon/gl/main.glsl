
// ---------- India tiles ----------
float indiaSdf(vec2 q) {   // q in Earth radii on the LAEA plane; returns signed distance (Earth radii)
  vec2 uv = q / (2. * IB) + .5;
  vec2 cl = clamp(uv, vec2(.5 / 1024.), vec2(1. - .5 / 1024.));
  float d = texture(tIndia, cl).r;
  return d + length(uv - cl) * 2. * IB;
}
vec2 laeaAt(vec3 n, vec3 c) {   // equal-area plane coordinates of n around centre c (unit sphere), x east, y north
  vec3 e = cross(vec3(0., 1., 0.), c); float el = length(e); e = el > 1e-5 ? e / el : vec3(1., 0., 0.);
  vec3 nn = cross(c, e);
  float cs = dot(n, c); vec3 tv = n - c * cs; float tl = length(tv);
  float rho = sqrt(max(2. * (1. - cs), 0.));
  return tl > 1e-7 ? rho * vec2(dot(tv, e), dot(tv, nn)) / tl : vec2(0.);
}
vec3 tricolor(float y) {
  vec3 saf = vec3(1., .52, .12), wht = vec3(1., .96, .9), grn = vec3(.12, .62, .18);
  return mix(mix(grn, wht, smoothstep(-.1, -.07, y)), saf, smoothstep(.07, .1, y));
}

float LWU(float kpx) { return (clamp(.0045 * kpx * .6, .9, 3.2) + 1.2) / kpx; }
struct Tile { float key; float sdf; vec2 q; float pop; float half_; float id; };

// result: rgb = additive glow, a = fill alpha; fillCol = tile tint
vec4 drawTile(Tile b, float kpx, float detail, float solid, out vec3 fillCol) {
  // kpx: pixels per Earth-radius unit of the LAEA plane at this point
  float sp = b.sdf * kpx;
  float lw = clamp(.0045 * kpx * .6, .9, 3.2);
  float line = 1. - smoothstep(lw - .8, lw + .8, abs(sp));
  float fill = 1. - smoothstep(-.8, .8, sp);
  if (b.half_ > .5) { float north = smoothstep(-.001, .001, b.q.y - YSPLIT); fill *= north; line *= mix(.28, 1., north); }
  float tilePx = sqrt(IA) * kpx;
  float halo = exp(-abs(sp) / (lw * 4. + 2.)) * .35 * smoothstep(10., 30., tilePx);
  float pop = b.pop; float flash = pop * (1. - pop) * 4.;
  fillCol = tricolor(b.q.y) * (.88 + .24 * fract(sin(b.id * 91.7) * 4375.5));
  if (solid > .5 && b.id > .5) { float m3 = mod(b.id, 3.); fillCol = m3 < .5 ? vec3(1., .52, .12) : m3 < 1.5 ? vec3(.12, .62, .18) : vec3(1., .93, .82); }
  vec3 lc = vec3(1., .86, .6);
  vec3 g = lc * (line * 1.25 + halo * .6) * detail + lc * flash * (fill * .6 + line * 2.) * mix(.2, 1., detail);
  return vec4(g * pop, fill * pop);
}

// Moon tiles: 12 explicit centres (index 11 is the half India)
Tile moonTiles(vec3 n, float k, float lwU) {
  Tile b; b.key = -1.; b.sdf = 1e3; b.pop = 0.; b.half_ = 0.; b.q = vec2(0.); b.id = 0.;
  float best = -1.;
  for (int i = 0; i < 12; i++) {
    vec4 c = uMC[i]; if (c.w < 0. || uT < c.w) continue;
    float pop = clamp((uT - c.w) / .32, 0., 1.); float ps = mix(1.22, 1., 1. - pow(1. - pop, 3.));
    float ra = uMR[i / 4][i % 4]; float ca = cos(ra), sa = sin(ra);
    vec2 q0 = laeaAt(n, c.xyz) / (k * ps); vec2 q = vec2(ca * q0.x + sa * q0.y, -sa * q0.x + ca * q0.y);
    float d = indiaSdf(q);
    if (d < lwU && c.w > best) { best = c.w; b.key = c.w; b.sdf = d; b.q = q; b.pop = pop; b.half_ = i == 11 ? 1. : 0.; b.id = float(i); }
    if (best < 0. && d < b.sdf) { b.sdf = d; b.q = q; b.pop = pop; b.id = float(i); }
  }
  return b;
}

// grid tiles: equal-area latitude bands, cell side D (rad); painter order = angle from the wave origin
Tile gridTiles(vec3 n, float k, float D, vec3 wo, float wave, float popw, float lwU) {
  Tile b; b.key = -1.; b.sdf = 1e3; b.pop = 0.; b.half_ = 0.; b.q = vec2(0.); b.id = 0.;
  float lat = asin(clamp(n.y, -1., 1.)), lon = atan(n.z, n.x);
  float nb = floor(PI / D + .5), dl = PI / nb;
  float bi0 = floor((lat + PI * .5) / dl);
  for (int di = -1; di <= 1; di++) {
    float bi = bi0 + float(di); if (bi < 0. || bi > nb - 1.) continue;
    float latc = -PI * .5 + (bi + .5) * dl;
    float m = max(1., floor(2. * PI * cos(latc) / D + .5));
    float off = fract(bi * .618034);
    float jc0 = floor((lon + PI) / (2. * PI) * m - off);
    for (int dj = -1; dj <= 1; dj++) {
      float jc = mod(jc0 + float(dj), m);
      float lonc = -PI + (jc + .5 + off) * 2. * PI / m;
      vec3 c = vec3(cos(latc) * cos(lonc), sin(latc), cos(latc) * sin(lonc));
      float th = acos(clamp(dot(c, wo), -1., 1.));
      if (th > wave) continue;
      float pop = clamp((wave - th) / popw, 0., 1.); float ps = mix(1.22, 1., 1. - pow(1. - pop, 3.));
      vec2 q = laeaAt(n, c) / (k * ps);
      float d = indiaSdf(q);
      if (d < lwU && th > b.key) { b.key = th; b.sdf = d; b.q = q; b.pop = pop; b.id = bi * 977. + jc; }
    }
  }
  return b;
}

// ---------- bodies ----------
float isec(vec3 ro, vec3 rd, vec3 C, float r) {
  vec3 oc = ro - C; float b = dot(oc, rd); float c = dot(oc, oc) - r * r; float h = b * b - c;
  if (h < 0.) return -1.; h = sqrt(h); float t = -b - h; return t > 0. ? t : -1.;
}
float fpAt(float t) { return t * (2. * tan(uFov * .5)) / R.y; }   // pixel footprint (world units) at distance t

vec3 applyTiles(vec3 col, Tile b, float kpx, float detail, float lit, float op, float avgA, float fs, float solid) {
  if (op <= 0.) return col;
  vec3 fc; vec4 tl = drawTile(b, kpx, detail, solid, fc);
  float fa = mix(avgA * b.pop, tl.a, detail) * fs * op;
  col = mix(col, fc * lit, fa);
  return col + tl.rgb * op;
}

vec3 shadeMoon(vec3 p, vec3 V, float t) {
  vec3 nw = normalize(p - uCM);
  mat3 sp = rotAxis(normalize(vec3(.12, 1., 0.)), uSpinM);
  vec3 nl = transpose(sp) * nw;      // body-local
  vec3 N; vec3 alb = moonSurf(nl, nw, t, 3.1, N);
  float dif = max(dot(N, LD), 0.);
  vec3 col = alb * (dif * 2.1 + .04) + alb * vec3(.3, .5, .9) * .12;
  float k = 1. / RM;                                   // Earth radius / Moon radius
  float kpx = k * RM / fpAt(t);                        // LAEA Earth-units -> px
  Tile b = moonTiles(nl, k, LWU(kpx));
  float lit = dif * 1.6 + .22;
  col = applyTiles(col, b, kpx, 1., lit, uTile.x, .8, .5, 1.);
  return col;
}

vec3 shadeEarth(vec3 p, vec3 V, float t) {
  vec3 nw = normalize(p - uCE);
  vec3 nl = rotY(uT * .02) * nw;
  vec3 em; float spc, atm; vec3 alb = earthSurf(nl, nw, t, V, 1., em, spc, atm);
  float ndl = dot(nw, LD); float dif = max(ndl, 0.);
  vec3 col = alb * (dif * 1.9 + .04) + em;
  vec3 hh = normalize(LD + V); col += vec3(1., .95, .85) * pow(max(dot(nw, hh), 0.), 90.) * spc * 1.1;
  col += vec3(.25, .55, 1.) * atm * 1.6;
  float k = 1.; float D = k * sqrt(IA);   // cell side so cell area = tile area
  float kpx = k / fpAt(t);
  Tile b = gridTiles(nw, k, D, uWoE, uWave.x, uPopW.x, LWU(kpx));
  float tilePx = sqrt(IA) * kpx;
  col = applyTiles(col, b, kpx, smoothstep(2., 6., tilePx), dif * 1.6 + .22, uTile.y, .8, .42, 0.);
  // impact flash at the contact point
  col += vec3(1., .8, .55) * exp(-acos(clamp(dot(nw, uWoE), -1., 1.)) * 9.) * uImp.x * 3.;
  return col;
}

vec3 shadeJupiter(vec3 p, vec3 V, float t) {
  vec3 nw = normalize(p - uCJ);
  vec3 nl = rotY(uT * .05) * nw;
  vec3 alb = jupiterSurf(nl, t, 0.);
  float ndl = dot(nw, LD); float dif = max(ndl, 0.);
  vec3 col = alb * (dif * 1.9 + .04);
  float fres = pow(1. - max(dot(nw, V), 0.), 3.); col += vec3(.9, .65, .4) * fres * .5 * (.3 + .7 * smoothstep(-.3, .4, ndl));
  float k = 1. / RJ; float D = k * sqrt(IA);
  float kpx = k * RJ / fpAt(t);
  Tile b = gridTiles(nw, k, D, uWoJ, uWave.y, uPopW.y, LWU(kpx));
  float tilePx = sqrt(IA) * kpx;
  float detail = smoothstep(3.5, 9., tilePx);
  col = applyTiles(col, b, kpx, detail, dif * 1.6 + .22, uTile.z, .8, mix(.04, .22, detail), 0.);
  float front = exp(-abs(acos(clamp(dot(nw, uWoJ), -1., 1.)) - uWave.y) / max(uPopW.y * .3, .004)) * step(.001, uWave.y) * step(uWave.y, 3.1);
  col += vec3(1., .8, .5) * front * (1. - detail * .7) * uTile.z * .8;
  col += vec3(1., .8, .55) * exp(-acos(clamp(dot(nw, uWoJ), -1., 1.)) * 60.) * uImp.y * 3.;
  return col;
}

vec3 shadeSun(vec3 p, vec3 V, float t) {
  vec3 nw = normalize(p - uCS);
  vec3 nl = rotY(uT * .02) * nw;
  vec3 col = sunSurf(nl, nw, V, t) * 1.0;
  float k = 1. / RS; float D = k * sqrt(IA);
  float kpx = k * RS / fpAt(t);
  Tile b = gridTiles(nw, k, D, uWoS, uWave.z, uPopW.z, LWU(kpx));
  float tilePx = sqrt(IA) * kpx;
  float detail = smoothstep(3.5, 9., tilePx);
  float mu = clamp(dot(nw, V), 0., 1.);
  col = applyTiles(col, b, kpx, detail, (.35 + .65 * mu) * 1.1, uTile.w * 1.6, .75, 0., 0.);
  float front = exp(-abs(acos(clamp(dot(nw, uWoS), -1., 1.)) - uWave.z) / max(uPopW.z * .3, .002)) * step(.001, uWave.z) * step(uWave.z, 3.1);

  col += vec3(1., .9, .7) * exp(-acos(clamp(dot(nw, uWoS), -1., 1.)) * 400.) * uImp.z * 4.;
  return col;
}

// the flat hero sheet that lands on the Moon and wraps onto it
vec4 sheet(vec3 ro, vec3 rd, float tHit) {
  if (uSheet.y <= 0.) return vec4(0.);
  mat3 sp = rotAxis(normalize(vec3(.12, 1., 0.)), uSpinM);
  vec3 c = sp * uMC[0].xyz;                            // hero centre in world
  vec3 P0 = uCM + c * RM * (1. + uSheet.x);
  float dn = dot(rd, c); if (abs(dn) < 1e-4) return vec4(0.);
  float ts = dot(P0 - ro, c) / dn; if (ts < 0. || ts > tHit) return vec4(0.);
  vec3 x = ro + rd * ts - P0;
  vec3 e = normalize(cross(vec3(0., 1., 0.), c)), nn = cross(c, e);
  float k = 1. / RM;
  vec2 q = vec2(dot(x, e), dot(x, nn)) / RM / k;
  float d = indiaSdf(q);
  float kpx = k * RM / fpAt(ts);
  float sp_ = d * kpx; float lw = clamp(.0045 * kpx * .6, .9, 3.2);
  float line = 1. - smoothstep(lw - .8, lw + .8, abs(sp_));
  float fill = 1. - smoothstep(-.8, .8, sp_);
  float halo = exp(-abs(sp_) / (lw * 6. + 3.)) * .5;
  vec3 g = tricolor(q.y) * fill * .55 + vec3(1., .86, .6) * (line * 1.4 + halo * .7 + uSheet.z * (fill * .8 + line * 2.));
  return vec4(g * uSheet.y, clamp(fill * .55 + line, 0., 1.) * uSheet.y);
}

void main() {
  S = uCS;
  vec2 uv = (gl_FragCoord.xy - .5 * R) / R.y;
  float cr = cos(uRoll), sr = sin(uRoll); uv = mat2(cr, -sr, sr, cr) * uv;
  vec3 ro = uCamP; vec3 fw = normalize(uCamT - ro);
  vec3 rt = normalize(cross(fw, vec3(0., 1., 0.))); vec3 up = cross(rt, fw);
  float fl = 1. / tan(uFov * .5) * .5;
  vec3 rd = normalize(uv.x * rt + uv.y * up + fw * fl);
  // sky: deep navy, stars of varied brightness, a faint milky band and a violet nebula wash (same as the size-ladder reel)
  float sky = .5 + .5 * rd.y;
  vec3 bg = mix(vec3(.012, .016, .034), vec3(.03, .035, .07), sky);
  vec3 stars = vec3(0.); {
    vec3 sp = rd * 220.; vec3 ip = floor(sp); vec3 fr = fract(sp) - .5;
    float h = h31(ip); if (h > .985) { float d = length(fr - (h33(ip) - .5) * .6); stars = vec3(.9, .95, 1.) * smoothstep(.12, 0., d) * (h - .985) * 60.; }
  }
  { vec3 sp2 = rd * 140.; vec3 ip2 = floor(sp2); vec3 fr2 = fract(sp2) - .5; float h2 = h31(ip2 + 3.1);
    if (h2 > .93) { float d2 = length(fr2 - (h33(ip2 + 1.) - .5) * .6); stars += mix(vec3(1., .85, .7), vec3(.7, .85, 1.), h33(ip2).x) * smoothstep(.15, 0., d2) * (h2 - .93) * 18.; } }
  float band = exp(-pow(dot(rd, normalize(vec3(.3, .8, -.5))) * 3.2, 2.));
  float neb = fbm(rd * 2.2 + 4.);
  bg += (vec3(.05, .035, .11) * neb + vec3(.04, .05, .09) * band * (.4 + fbm(rd * 7.))) * .9;
  bg += stars * .8;

  float tm = isec(ro, rd, uCM, RM), te = isec(ro, rd, uCE, 1.), tj = isec(ro, rd, uCJ, RJ), ts = isec(ro, rd, uCS, RS);
  float t = 1e9; int id = 0;
  if (tm > 0. && tm < t) { t = tm; id = 1; }
  if (te > 0. && te < t) { t = te; id = 2; }
  if (tj > 0. && tj < t) { t = tj; id = 3; }
  if (ts > 0. && ts < t) { t = ts; id = 4; }
  vec3 col = bg; vec3 V = -rd;
  if (id > 0) {
    vec3 p = ro + rd * t;
    if (id == 1) col = shadeMoon(p, V, t);
    else if (id == 2) col = shadeEarth(p, V, t);
    else if (id == 3) col = shadeJupiter(p, V, t);
    else col = shadeSun(p, V, t);
  }
  // Sun corona, prominences, flares (only near the Sun)
  { vec3 oc = ro - S; float b = dot(oc, rd); float rmin = length(oc - rd * b);
    if (rmin < RS * 2.6 && uGlow > 0.) col += sunGlow(ro, rd, id > 0 ? t : 1e5) * uGlow * .6 * smoothstep(2.6 * RS, 1.5 * RS, rmin); }
  // Earth atmosphere halo for rays that pass close to Earth
  { vec3 oc = ro - uCE; float b = dot(oc, rd); float tc = clamp(-b, 0., id > 0 ? t : 1e5); float rmin = length(oc + rd * tc);
    if (id != 2) col += vec3(.2, .45, 1.) * exp(-max(rmin - 1., 0.) * 13.) * .45; }
  // hero sheet
  vec4 sh = sheet(ro, rd, id > 0 ? t : 1e9);
  col = col * (1. - sh.a * .5) + sh.rgb;
  col *= uExpo;
  col = col * (2.51 * col + .03) / (col * (2.43 * col + .59) + .14);
  col = pow(clamp(col, 0., 1.), vec3(1. / 2.2));
  o = vec4(col, id > 0 ? clamp(log2(t + 1.) / 11.5, 0., 1.) * .98 + .02 : 0.);
}
