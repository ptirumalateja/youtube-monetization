# Heliosphere reel: build notes (v15 FINAL, 3 Nov 2026)

3D scene (three.js 0.187 inside HyperFrames 0.8.231) + HTML overlay. Rendered 34 s, sped up 1.3x to 26.15 s in `mix_v15.sh`.

Files here: `index.html` (overlay, captions c0-c4, labels, counters, timeline), `assets/scene.js` is `scene.js` (put it in `assets/`), `hyperframes.json`, `mix_v15.sh` (sound + speed-up).

Not committed (rebuild or fetch):
- `assets/three.module.js`, `assets/three.core.js`: `npm pack three@0.187.0`, copy `build/three.module.js` and `build/three.core.js`.
- `assets/gsap.min.js`: gsap 3.x (cdnjs).
- `assets/planets/*.jpg`: the three.js example planet textures (earth_atmos_2048, earthcloudmaptrans, moon_1024, mercurymap, venusmap, marsmap1k, jupitermap, saturnmap, saturnringcolor, saturnringpattern.gif, uranusmap, neptunemap), from `mrdoob/three.js` `examples/textures/planets/` (raw.githubusercontent works from the sandbox). Check the texture credits (Solar System Scope, CC BY 4.0) if the reel is monetised.
- The video (103 MB) and the Freesound files.

Render (from the folder that holds index.html):
```
HYPERFRAMES_BROWSER_PATH=/usr/bin/google-chrome npx --yes hyperframes@0.8.231 lint
HYPERFRAMES_BROWSER_PATH=/usr/bin/google-chrome npx --yes hyperframes@0.8.231 snapshot --at 0.2,2.5,6,12,26,33.5
HYPERFRAMES_BROWSER_PATH=/usr/bin/google-chrome npx --yes hyperframes@0.8.231 render -o ../heliosphere_raw.mp4   # about 7 min, run in the background
SND=/path/to/freesound ./mix_v15.sh ../heliosphere_raw.mp4 slowlight_heliosphere_FINAL_v15.mp4
```
Lint gives 0 errors and 6 benign `nested_structure_needs_subcomposition` warnings.

## Scene map (raw-render seconds; final = /1.3)
| Raw t | Shot |
|---|---|
| 0-3 | Hook: whole galaxy (golden spiral, 70k points) with Sagittarius A*, the Sun system scaled up 3.8x at the Sun's galactic path, labels MILKY WAY / SUN'S ORBIT / SAGITTARIUS A* |
| 3-8 | Zoom into the heliosphere (log distance + target blend); system scale eases 3.8x -> 1x; shells and planets labels fade in |
| 8-19 | Side-on camera, planet helices (OM = 3.8/sqrt(AU)), Sun's wavy path ribbon, termination shock / heliopause / hydrogen wall callouts, cosmic rays |
| 19.2-29.6 | Dive to Earth: magnetosphere cutaway (bow shock, magnetopause, magnetotail) |
| 29.6-34 | Pull back to the wide heliosphere, question "Does every star have a bubble like this?", tag |

## Key constants (scene.js)
- Galaxy: `GC = (-8,0,0) + 62*GP`, `GP = (0,0.09,-0.99)`, rings 10-110 units, Sun at radius 62 (about 0.56 of the disc, like the real 26,700 ly of about 50,000 ly).
- Hook zoom `zz = 1 - smoothstep(seg(t,3,8))`; camera hook distance 520; Sun-system group `SYSG` scale `1 + 2.8*zz`; anchors scaled to match.
- Orbit speeds: `OM = 3.8/sqrt(AU)`; trails `TRN=420`, `TRLEN=8`, `TS_=2.2`; ribbon speed 3.2; galaxy spin 0.3 rad/s.

## Lessons (add to the playbook lessons log)
- A camera-attached backdrop with fake parallax reads as a still image. Put the galaxy in the world and move the camera.
- To enlarge one object inside a much bigger scene without breaking either, move everything that belongs to it into one group and scale the group (and the label anchors) instead of rewriting the camera.
- Side-on camera + planets orbiting around the travel axis = long helices; from above they read as flat rings.
- Phones cannot play the sub-bass: the first mix with only synthetic pad and whooshes was "inaudible and irritating". Real hits plus a mid-range ambience bed worked.
- Check the AAC file's true peak and LUFS after encoding (v15: -17.1 LUFS integrated, -1.0 dBFS peak).
