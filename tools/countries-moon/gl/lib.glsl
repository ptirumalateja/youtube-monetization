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

