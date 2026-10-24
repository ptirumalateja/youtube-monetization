# The Invisible Backpack: shared style sheet (Part 1 → Part 2)

Locked by the Part 1 session on 24 Oct 2026. Part 2 ("Check Your Friend's Bag") starts on Part 1's last frame, so match everything here exactly. **The source of truth is the code:** `tools/invisible-backpack/scene.js` (+ `timeline.json`, `render.cjs`). If a number here and the code disagree, the code wins. Tell the Part 1 session if you need something changed.

## Reuse the scene directly

```
cd tools/invisible-backpack && npm install          # three@0.170.0 + playwright-core 1.56.1
TIMES=17.9667 node render.cjs stills                # Part 1's last frame (frame 539), clean (no text), 1080x1920 -> output/still-17.97.jpg
TIMES=17.9667 node render.cjs probe                 # screen positions of hero head, bag, crowd heads at that frame
```
- `scene.js` exposes `window.renderAt(t, subframes)` (pure, no state between frames) and `window.metaAt(t)`. Copy the folder to `tools/<part-2>/` and extend the timeline past 18 s, or import the rig/rock/bag/sky sections; the sections are labelled with `// ---` banners.
- Render: three.js r0.170, headless Chromium + SwiftShader (`--use-angle=swiftshader`), PCF soft shadows, 3 motion-blur sub-frames (shutter 1/60 s, never across a cut), JPEG 0.95, native 1080x1920, 30 fps.

## Final frame of Part 1 (t = 17.9667 s, frame 539; the shot is locked from 16.8 s)

| | Value |
|---|---|
| Camera position | (8.6, 0.32, 6.65) m |
| Camera look-at | (2.45, 2.55, -0.7) |
| Up / FOV / clip | +y, **60°** vertical, near 0.05, far 3000, aspect 9:16 |
| Hero | stands on the top step at root (4.27, 3.15, 0), facing +x (yaw 0), pose `tall` (p -0.03, head tilt -0.16: looking slightly up and forward), slow breath sway |
| Lamp | small lantern on the top step at (4.71, 3.15, 0.24), flame `#ffe0a8`, warm point light `#ffc27a` 1.5, glow sprite opacity 0.5, flicker `0.92+0.08·sin(17t)·sin(5.3t)` |
| Empty backpack | on the ground at (-0.8, 0, -0.05), yaw 1.45 rad, height squashed to 0.7 (slumped, empty), slight tilt |
| Crowd (3 blue) | stopped beyond the stair's top end at (5.15, -0.85), (5.65, -1.6), (6.2, -1.05); facing the hero, heads tilted up. Only the first is in frame (screen x≈0.93, y≈0.56) |
| Moon | thin crescent, direction (-0.66, 0.5, -0.56) normalised, upper left of frame |
| Wind | dust motes drift +x at ~1.1 m/s from 15.6 s (`WIND(t)` in the code) |
| Screen positions | hero head (0.66, 0.24), top of the stair + 2.2 m (0.67, 0.19), bag (0.09, 0.70), crowd head (0.93, 0.56), as fractions of width/height |

Units are metres. Path runs along +x (he walked toward +x); the side cameras live on +z; ground is y = 0.

## Characters (shared stickman rig)

- Proportions: thigh 0.46, shin 0.46, torso 0.56, neck gap 0.07, head radius 0.125, upper arm 0.31, forearm 0.29; single-point shoulders (±0.035) and hips (±0.06); small nose sphere (r 0.032) shows look direction.
- **Hero (white):** colour `#efe6d4`, emissive `#2a241a` (intensity 1), roughness 0.55, bone radius 0.045. Same look as One Step a Day's ivory stickman.
- **Crowd (muted blue):** colour `#5872ad`, emissive `#121d3c`, bone radius 0.04. 3 figures. Walk speed 0.72 m/s, stride cycle 1.3 m.
- Pose library (`POSES` in the code): `stand`, `heavy` (bent 0.6 rad, head down), `crouch`, `carry`, `place`, `sit`, `tall`. Arms can use two-bone IK to world targets (`tL/tR`, weights `wL/wR`).

## The rocks

- 7 rough boulders: superellipsoid icosahedron (detail 3) with low-frequency noise, flat-ish top, **flat-shaded facets**. Colour `#5a4e46` with a noise map, roughness 0.92.
- **Glowing amber cracks:** emissive `#ffa24a` through a procedural crack texture (orange glow `rgba(255,120,30)`, core `rgba(255,236,190)`). Glow sprite `#ff9a40`, point light `#ff9a48`.
- In the bag: about 0.33 × 0.19 × 0.29 m. As steps: about 1.16-1.22 × 0.47-0.49 × 0.90-0.98 m (they grow with a small pop when set down).
- **Stair geometry:** rock k (1..7) spans x [0.45+0.55(k-1), 0.45+0.55(k+1)], y [0.45(k-1), 0.45k]; each rock rests on the back half of the one below (a stacked, leaning cairn, not cut blocks). Rise 0.45, tread 0.55, top surface y 3.15. Steps keep a soft glow (emissive ~0.55-0.7).
- Labels in order (rock 1 = top of the bag = step 1): WHAT WILL THEY SAY / FAILED IN 2021 / I'M BEHIND / NOT READY / COMPARE / TOO LATE / NOT ENOUGH.

## The backpack (x-ray glass)

- Rounded box 0.78 × 1.05 × 0.5 m, corner radius 0.2, top tapered (width ×0.83, depth ×0.88 at the top), two tube shoulder straps (r 0.036), half-torus grab handle on top.
- Material: fresnel glass, average opacity about 30%. Rim `rgb(0.80,0.93,0.92)`, body tint amber `rgb(1.0,0.62,0.28)`, inner back-face glow amber (additive), glow sprite and point light `#ffa050` scaled by how full it is.
- X-ray cut (Part 1, 2.0-2.95 s): 16% flash, then the frame goes cyan monochrome (`0.45,0.9,1.0`) with faint scanlines for 0.45 s and dissolves back to colour by 2.95 s.

## World

- Dusk over a dust plain. Sky shader: horizon `rgb(0.060,0.105,0.150)` to `rgb(0.018,0.030,0.068)` to zenith `rgb(0.006,0.010,0.026)`; teal band `rgb(0.08,0.22,0.24)` at the horizon; **gold afterglow** `rgb(1.0,0.56,0.24)` low on the horizon toward +x (sun direction (1, 0, -0.28)); stars above 7° elevation; crescent moon.
- Ground `#2f3442` with a noise map, a lighter packed path `#3d4150` (z ≈ -0.45, 1.9 m wide), scattered dark pebbles. Two rings of low dunes (`#0f1826` at 700 m, `#0b121d` at 420 m). Fog `#0c1422`, FogExp2 0.011.
- Lights: hemisphere `#5a70a0`/`#15171e` 0.95; cool moon key `#a9bce6` 0.95 from (-5, 11, 8) relative to the action, casting shadows; warm rim `#ffb470` 0.5→0.85 from the afterglow side.
- Dust: world-fixed camera-wrapped motes (warm `rgb(1.0,0.86,0.66)`), dust puffs on footsteps, the thud and every rock set down.
- Grade (post): soft clamp `1-exp(-1.25c)`, teal shadows / warm highlights, vignette, fine grain, slight chromatic fringe; Unreal bloom 0.5 / radius 0.55 / threshold 0.8.

## Text, palette, fonts (overlay layer, drawn in PIL)

- Palette: charcoal/navy world, **cream text** `(240,232,214)` with a thick black stroke, **gold accent** `(240,186,92)`, teal accent, **red only for chips/markers** `(214,62,48)`.
- Fonts: Liberation Mono Bold (hook, captions, counters, end line), DejaVu Sans Mono (small tag), Liberation Mono Bold for labels.
- Sizes at 1080×1920: tag "SLOW LIGHT" 26 px spaced; hook 62 px; reveal title 66 px; rock labels 38 px; counter 60 px with a red "STEP n" chip; captions 58 px; end line 64 px; sign-off 40 px / 30 px. Safe zone: no text in the bottom 18% (y > 1574) or the top 150 px.
- Part 1's final frame carries the end text: "YOUR BAGGAGE IS / YOUR FOUNDATION." (y≈330-400), "One rock a day." and "slowlighttv" below it. The clean frame (no text) is the render above; start Part 2 on the clean frame and fade Part 1's text out in the first ~0.3 s if you want a seamless join.

## Sound at the join

Part 1 ends on a single warm piano chord (D major add9, struck at 15.0 s and decaying) over a wind bed and a soft lamp hum. Everything is synthesised in numpy (no samples, no credits). Continue the wind bed into Part 2 for a seamless join.
