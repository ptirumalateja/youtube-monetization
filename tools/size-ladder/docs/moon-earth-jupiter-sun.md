# Moon, Earth, Jupiter, Sun: the size ladder (v1)

Teja's brief (27 Oct 2026): under 20 s, 9:16, "nothing short of spectacular". Show the Moon, make Earth an open bowl and fill it with Moons, then Earths fill Jupiter, then Jupiters fill the Sun. Continuity, clean motion, solid depth and parallax, every surface detail considered.

Length 19.6 s, 1080x1920, 30 fps, with sound. Wordless except the short on-screen lines below.

## Counts, checked by volume

Mean radii (NASA fact sheets, volumetric for Jupiter): Moon 1,737.4 km, Earth 6,371.0 km, Jupiter 69,911 km, Sun 695,700 km.

| Step | Radius ratio | Volume ratio (what is shown) | Say |
|---|---|---|---|
| Earth / Moon | 3.667 (Moon is 0.273 of Earth's width) | **49.3** | "49 Moons" |
| Jupiter / Earth | 10.973 | **1,321** | "about 1,300 Earths" |
| Sun / Jupiter | 9.951 | **985** | "about 1,000 Jupiters" |

These are volume ratios, i.e. how many would fit if they could be poured in with no gaps. Whole spheres leave gaps (a packing of equal spheres fills about 74% at best), so the pile on screen shows fewer whole balls than the counter. The counter says "49" without a tilde because 49.3 is the figure; the other two carry "≈". Do not add "about 50" or "1,000 exactly" to the copy. The Sun/Jupiter figure is 985, so "about 1,000" is the honest rounding.

## Format map (reel-script-structure)

| Slot | Time | Picture | Line | Sound |
|---|---|---|---|---|
| Hook (payoff first) | 0.1-2.4 | Moon filling the frame, real maria and rayed craters, terminator light | **49 MOONS / FIT INSIDE EARTH.** | hard sub-hit on frame 1, thin shimmer |
| Lock-in | 2.7-5.4 | Camera pulls out; the Earth bowl opens under the falling Moon | EARTH IS ABOUT / 4 MOONS WIDE. | whoosh, soft drop thud |
| Body 1 | 3.0-5.5 | Moons pour in and heap over the rim; counter runs 0 to 49 | counter "MOONS IN EARTH" | glassy pops at the fill density |
| Rehook 1 | 5.65-7.3 | The heap is absorbed, Earth closes with a seam of light and becomes one unit; the camera climbs out of a Jupiter-sized cavern that ignites around it | **NOW EARTH / IS THE MOON.** | 0.3 s hard silence, boom, riser |
| Body 2 | 7.8-10.7 | Earths pour into the Jupiter bowl; counter to 1,300 | JUPITER IS 11x / WIDER THAN EARTH. then counter "EARTHS IN JUPITER" | woody taps |
| Rehook 2 | 10.85-12.5 | Jupiter closes, the camera is pulled out as the Sun's bowl ignites | **NOW JUPITER / IS THE MOON.** | silence, boom, riser |
| Body 3 | 13.4-16.4 | Jupiters pour into the Sun bowl; counter to 1,000 | THE SUN IS 10x / WIDER THAN JUPITER. then counter "JUPITERS IN THE SUN" | deep thumps |
| Close + CTA | 16.7-19.6 | The Sun closes into a full star with prominences | **1,000 JUPITERS. / IN ONE STAR. / STARS GET MUCH BIGGER.** then "Follow @slowlighttv" | biggest hit, 0.3 s silence before it, warm chord |

Edit layers: raw GPU render, then parallax dust motes in the same camera, bloom, text, counter, vignette, grain, sound. The test from sports-reel-edit-feedback holds: every beat reads with the text off.

## Continuity (the rule from the photon reel)

One world and one camera, never a 2D zoom or a crossfade. Units are Earth radii: the Earth bowl sits at the origin, the Jupiter bowl is built around it with Earth as the first unit at its floor, the Sun bowl is built around Jupiter with Jupiter as its first unit. The camera is a single log-distance path from 0.95 to 640 Earth radii, so the whole reel is a 700x pull-back. The Moon that opens the reel is the first Moon to fall into the bowl. Each next bowl appears as an expanding ring of light (an ignition wave) around the previous one, not as a cut.

## Detail

- Moon: the real albedo map (maria in the right places) plus procedural craters at four scales, rim brightening, and ray systems for Tycho, Copernicus and Kepler.
- Earth: NASA Blue Marble colour, ocean mask for specular, a real cloud layer that drifts, city lights on the night side, a blue atmosphere limb. Cut section shows a thin crust over a glowing mantle.
- Jupiter: zones and belts warped by noise, turbulent band edges, the Great Red Spot at 22 degrees south with its pale collar, white ovals, a cut section of cloud deck over deep amber, and a swirling interior.
- Sun: boiling granulation cells with dark lanes, supergranule brightness, limb darkening and reddening, sunspots, faculae, a corona, prominence loops standing on the limb, glowing plasma interior.
- Units are packed in an FCC lattice (the densest sphere packing), heaped above the rim like an overflowing bowl, and shrink away into the planet as it closes.
- Textures (three.js example planets, from the Solar System Scope / NASA public-domain maps) are in `tools/size-ladder/tex`.

## Build

`tools/size-ladder/`: `gl/scene.glsl` (the whole world as one fragment shader, ray-marched, headless Chromium + SwiftShader), `gl/render.mjs` (batch renderer; depth in the alpha channel), `cam.py` (timeline: camera, fills, closings, waves), `comp.py` (dust, bloom, text, counter; `plates`, `frames`, `events`), `sound.py`, `run_plates.sh` (parallel plate render, resumable). About 6 s per 1080x1920 plate per core.

## v2: extended cut (21.0 s, loop), 27 Oct 2026

Built in `cam2.py` + `comp2.py` + `sound2.py` on top of the 19.6 s cut.

| Time | Beat |
|---|---|
| 0.0-1.5 | Hook, "49 MOONS FIT INSIDE EARTH." (full text on frame 0) |
| 1.5-4.5 | Moons fall into Earth, counter to 49 |
| 4.5-7.5 | Earth becomes the unit, Earths into Jupiter, counter to 1,321 |
| 7.5-10.3 | Jupiter becomes the unit, Jupiters into the Sun, counter to 985 |
| 10.3-14.0 | Sun shrinks to a marble and a bead, count runs 985 to 10,000,000,000 SUNS (hits 12.6 s), whip back to Stephenson 2-18, hard cut |
| 14.0-16.6 | "YOU ARE SMALLER THAN ONE PIXEL." on the starfield |
| 16.6-19.2 | "WHAT SHOULD WE SQUEEZE NEXT?" while the camera starts its zoom home |
| 19.2-21.0 | One-world zoom back to the opening Moon, hook text re-forms; last frame matches frame 0 |

- The original timeline is time-warped into 0-10.3 s (`cam2.KN`), so the first 10.3 s reuse the existing plates (no re-render); only 320 new frames were rendered (`plates2/`).
- No handle card or platform icons: the handle goes in the caption.
- Stephenson 2-18: radius 2,150 solar radii (estimate, varies between studies), ~9.9 billion Suns by volume, so "about 10 billion" and the caveat in the description. Drawn as a giant sphere in the same world (id 8 in `scene.glsl`), revealed by a fast log-distance pull-back; the Sun is a glowing bead against it.
- Moons: each of the ~14 whole Moons that physically fit falls to its own slot and stays; counter keeps the volume count of 49.
- Sound: falling whistle and thud per landing, ticking counter riser into a big hit at 12.6 s, whip, hard silence at the 14.0 s cut, quiet payoff, riser into the loop.
