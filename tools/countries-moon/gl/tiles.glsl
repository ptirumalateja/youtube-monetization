// ---------- India tiles ----------
float sdfAt(sampler2D tx, float B, vec2 q) {   // q in Earth radii on the LAEA plane; signed distance (Earth radii)
  vec2 uv = q / (2. * B) + .5;
  vec2 cl = clamp(uv, vec2(.5 / 1024.), vec2(1. - .5 / 1024.));
  return texture(tx, cl).r + length(uv - cl) * 2. * B;
}
float indiaSdf(vec2 q) { return sdfAt(tIndia, IB, q); }
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
    if (acos(clamp(dot(c.xyz, uIndO), -1., 1.)) < uInd.y) continue;
    float pop = clamp((uT - c.w) / .32, 0., 1.); float ps = mix(1.22, 1., 1. - pow(1. - pop, 3.));
    float ra = uMR[i / 4][i % 4]; float ca = cos(ra), sa = sin(ra);
    vec2 q0 = laeaAt(n, c.xyz) / (k * ps); vec2 q = vec2(ca * q0.x + sa * q0.y, -sa * q0.x + ca * q0.y);
    float d = indiaSdf(q);
    if (d < lwU && c.w > best) { best = c.w; b.key = c.w; b.sdf = d; b.q = q; b.pop = pop; b.half_ = i == 11 ? 1. : 0.; b.id = float(i); }
    if (best < 0. && d < b.sdf) { b.sdf = d; b.q = q; b.pop = pop; b.id = float(i); }
  }
  return b;
}

