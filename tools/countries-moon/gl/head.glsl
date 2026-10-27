#version 300 es
// How many countries fit on the Moon: one Moon, one camera. India (11.5 packed tiles) then Pakistan, Bangladesh,
// Nepal, Sri Lanka, Bhutan tile the surface at true scale (equal-area decals). Each new country wipes the last one off.
precision highp float;
uniform vec2 R;
uniform vec3 uCamP, uCamT;
uniform float uFov, uRoll, uT, uExpo;
uniform vec3 uCM;                    // Moon centre
uniform float uSpinM;                // Moon spin (rad)
uniform vec4 uMC[12];                // India tiles: body-local centre, appear time
uniform vec4 uMR[3];                 // India tile rotations
uniform vec4 uSheet;                 // flat hero India: height above surface (Moon radii), alpha, flash, -
uniform vec4 uInd;                   // India: opacity, clear-front angle, -, -
uniform vec3 uIndO;                  // India clear origin (body-local)
uniform vec4 uGA, uGA2, uGB, uGB2;   // grid sets A (outgoing) / B (incoming): (IA, IB, asp, wave) (clear, popw, opacity, -)
uniform vec3 uGAo, uGBo, uGAc, uGBc; // wave origins (body-local) and tints
uniform sampler2D tMoon, tIndia, tA, tB;
uniform sampler2D tEarth, tSpec, tCloud, tLights;
out vec4 o;

const float RM = 0.27270, RJ = 10.9733, RS = 109.198;
const vec3 LD = normalize(vec3(0.86, 0.34, 0.38));
const float PI = 3.14159265;
const float IB = 0.31364560;         // India SDF half-box (Earth radii, LAEA plane)
const float IA = 0.0806590;          // India area on the unit Earth sphere
const float YSPLIT = -0.0045944;     // LAEA y that halves India's area
vec3 S = vec3(0., -1e4, 0.);
