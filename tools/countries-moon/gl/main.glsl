
// ---------- country grids: equal-area latitude rows, cells shaped like the country's bounding box ----------
// painter order = angle from the wave origin; tiles closer than `clr` to the origin have been wiped off
Tile gridSet(sampler2D tx, vec3 n, float k, vec4 g, vec4 g2, vec3 wo, vec3 co, float lwU) {
  Tile b; b.key = -1.; b.sdf = 1e3; b.pop = 0.; b.half_ = 0.; b.q = vec2(0.); b.id = 0.;
  if (g2.z <= 0. || g.w <= 0.) return b;
  float ia = g.x, B = g.y, asp = g.z, wave = g.w, clr = g2.x, popw = g2.y;
  float Dlat = k * sqrt(ia / asp), Dlon = k * sqrt(ia * asp);
  float lat = asin(clamp(n.y, -1., 1.)), lon = atan(n.z, n.x);
  float nb = floor(PI / Dlat + .5), dl = PI / nb;
  float bi0 = floor((lat + PI * .5) / dl);
  for (int di = -1; di <= 1; di++) {
    float bi = bi0 + float(di); if (bi < 0. || bi > nb - 1.) continue;
    float latc = -PI * .5 + (bi + .5) * dl;
    float m = max(1., floor(2. * PI * cos(latc) / Dlon + .5));
    float off = mod(bi, 2.) * .5;
    float jc0 = floor((lon + PI) / (2. * PI) * m - off);
    for (int dj = -1; dj <= 1; dj++) {
      float jc = mod(jc0 + float(dj), m);
      float lonc = -PI + (jc + .5 + off) * 2. * PI / m;
      vec3 c = vec3(cos(latc) * cos(lonc), sin(latc), cos(latc) * sin(lonc));
      float th = acos(clamp(dot(c, wo), -1., 1.));
      if (th > wave || acos(clamp(dot(c, co), -1., 1.)) < clr) continue;
      float pop = clamp((wave - th) / popw, 0., 1.); float ps = mix(1.25, 1., 1. - pow(1. - pop, 3.));
      vec2 q = laeaAt(n, c) / (k * ps);
      float d = sdfAt(tx, B, q);
      if (d < lwU && th > b.key) { b.key = th; b.sdf = d; b.q = q; b.pop = pop; b.id = bi * 977. + jc; }
    }
  }
  return b;
}

vec3 drawGrid(vec3 col, Tile b, float kpx, float lit, float op, vec3 tint) {
  if (op <= 0. || b.pop <= 0.) return col;
  float sp = b.sdf * kpx;
  float lw = clamp(.0045 * kpx * .6, .8, 3.);
  float line = 1. - smoothstep(lw - .8, lw + .8, abs(sp));
  float fill = 1. - smoothstep(-.8, .8, sp);
  float halo = exp(-abs(sp) / (lw * 4. + 2.)) * .3;
  float flash = b.pop * (1. - b.pop) * 4.;
  vec3 fc = tint * (.85 + .3 * fract(sin(b.id * 91.7) * 4375.5));
  col = mix(col, fc * (.35 + .65 * lit), fill * .38 * b.pop * op);
  vec3 lc = mix(vec3(1., .86, .6), tint, .45);
  return col + lc * (line * 1.2 + halo * .5 + flash * (fill * .5 + line * 2.)) * b.pop * op;
}

// ---------- Moon ----------
float isec(vec3 ro, vec3 rd, vec3 C, float r) {
  vec3 oc = ro - C; float b = dot(oc, rd); float c = dot(oc, oc) - r * r; float h = b * b - c;
  if (h < 0.) return -1.; h = sqrt(h); float t = -b - h; return t > 0. ? t : -1.;
}
float fpAt(float t) { return t * (2. * tan(uFov * .5)) / R.y; }
mat3 spinM() { return rotAxis(normalize(vec3(.12, 1., 0.)), uSpinM); }

vec3 shadeMoon(vec3 p, vec3 V, float t) {
  vec3 nw = normalize(p - uCM);
  vec3 nl = transpose(spinM()) * nw;
  vec3 N; vec3 alb = moonSurf(nl, nw, t, 3.1, N);
  float dif = max(dot(N, LD), 0.);
  vec3 col = alb * (dif * 2.1 + .04) + alb * vec3(.3, .5, .9) * .12;
  float lit = dif * 1.6 + .22;
  float k = 1. / RM;                                   // Earth radius / Moon radius: true scale
  float kpx = k * RM / fpAt(t);                        // LAEA Earth-units -> px
  if (uInd.x > 0.) {
    Tile b = moonTiles(nl, k, LWU(kpx));
    if (b.pop > 0.) { vec3 fc; vec4 tl = drawTile(b, kpx, 1., 1., fc); col = mix(col, fc * lit, tl.a * .5 * uInd.x); col += tl.rgb * uInd.x; }
  }
  Tile a = gridSet(tA, nl, k, uGA, uGA2, uGAo, uGBo, LWU(kpx));
  Tile bb = gridSet(tB, nl, k, uGB, uGB2, uGBo, uGBo, LWU(kpx));
  if (bb.pop > 0. && bb.key >= 0.) col = drawGrid(col, bb, kpx, lit, uGB2.z, uGBc);
  else col = drawGrid(col, a, kpx, lit, uGA2.z, uGAc);
  return col;
}

// the flat hero India that lands on the Moon and wraps onto it
vec4 sheet(vec3 ro, vec3 rd, float tHit) {
  if (uSheet.y <= 0.) return vec4(0.);
  vec3 c = spinM() * uMC[0].xyz;
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
  vec2 uv = (gl_FragCoord.xy - .5 * R) / R.y;
  float cr = cos(uRoll), sr = sin(uRoll); uv = mat2(cr, -sr, sr, cr) * uv;
  vec3 ro = uCamP; vec3 fw = normalize(uCamT - ro);
  vec3 rt = normalize(cross(fw, vec3(0., 1., 0.))); vec3 up = cross(rt, fw);
  float fl = 1. / tan(uFov * .5) * .5;
  vec3 rd = normalize(uv.x * rt + uv.y * up + fw * fl);
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
  float t = isec(ro, rd, uCM, RM);
  vec3 col = bg;
  if (t > 0.) col = shadeMoon(ro + rd * t, -rd, t);
  // thin warm rim light around the Moon
  { vec3 oc = ro - uCM; float b = dot(oc, rd); float rmin = length(oc - rd * b);
    if (t < 0.) col += vec3(1., .85, .6) * exp(-max(rmin - RM, 0.) / (RM * .03)) * .12; }
  vec4 sh = sheet(ro, rd, t > 0. ? t : 1e9);
  col = col * (1. - sh.a * .5) + sh.rgb;
  col *= uExpo;
  col = col * (2.51 * col + .03) / (col * (2.43 * col + .59) + .14);
  col = pow(clamp(col, 0., 1.), vec3(1. / 2.2));
  o = vec4(col, t > 0. ? clamp(log2(t + 1.) / 11.5, 0., 1.) * .98 + .02 : 0.);
}
