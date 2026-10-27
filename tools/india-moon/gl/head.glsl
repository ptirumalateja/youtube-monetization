#version 300 es
// How many Indias fit on the Moon / Earth / Jupiter / the Sun: ONE world, ONE camera, analytic spheres.
// Units are Earth radii. Each smaller body hangs above the next one, drops onto its upper-left limb, and India
// re-tiles the bigger body from that contact point. India copies are true-scale equal-area decals (LAEA).
precision highp float;
uniform vec2 R;
uniform vec3 uCamP, uCamT;
uniform float uFov, uRoll, uT, uExpo;
uniform vec3 uCM, uCE, uCJ, uCS;     // body centres
uniform float uSpinM, uGlow;         // Moon spin (rad), Sun corona strength
uniform vec4 uMC[12];                // Moon tiles: body-local centre, appear time (-1 = never)
uniform vec4 uMR[3];                 // Moon tile rotations (rad), 12 packed
uniform vec4 uTile;                  // tile opacity per body (M, E, J, S)
uniform vec3 uWave;                  // wave front angle on E, J, S (rad)
uniform vec3 uPopW;                  // angular width of the pop-in at the wave front
uniform vec3 uWoE, uWoJ, uWoS;       // wave origins (body-local unit vectors) = contact points
uniform vec4 uSheet;                 // flat hero sheet: height above surface (Moon radii), alpha, flash, unused
uniform vec4 uImp;                   // impact flashes: x = Earth contact, y = Jupiter contact, z = Sun contact (0..1)
uniform sampler2D tEarth, tSpec, tCloud, tLights, tMoon, tIndia;
out vec4 o;

const float RM = 0.27270, RJ = 10.9733, RS = 109.198;
const vec3 LD = normalize(vec3(0.86, 0.34, 0.38));
const float PI = 3.14159265;
const float IB = 0.31364560;         // half-size of the India SDF box (Earth radii, LAEA plane)
const float IA = 0.0806590;          // India area on the unit Earth sphere
const float YSPLIT = -0.0045944;     // LAEA y that halves India's area
vec3 S;
