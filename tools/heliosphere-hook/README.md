# Heliosphere hook v17 (5 s)

Opening hook for the heliosphere reel, built on the Not a Vortex engine (tools/not-a-vortex on branch claude/project-thread-k71kjg):
galaxy plate + plate-sampled stars, white-gold Sun with corona, Kepler planets and true stretched paths, canvas bloom.
Added here: Earth's magnetosphere (shield + dipole field lines), the heliosphere (termination shock + heliopause on the same sqrt map), solar wind sparks,
and the hook captions in Playfair. The hook code is the HELIOSPHERE HOOK section at the end of scene.js.

```sh
ln -s ../heliosphere-v16/node_modules node_modules   # three 0.170
RENDER_W=1080 TIMES=0,1.2,3 node render.cjs --stills
RENDER_W=1080 FROM=0 TO=150 OUT_DIR=output/frames node render.cjs   # ~1.5 s/frame, split into 4 ranges
```
Assets (planet maps, galaxy plate) are copied from Not a Vortex and are our own generated textures.

## v19/v20 full reel (25 s)
- v19: blocks 3-4 (13-25 s) added to scene.js: Voyager 1 model, plasma, chase and crossing at 17.0, wide bubble, "Would you go? YES or NO", dive home into frame 0 (clocks ease from 19 s so Earth matches frame 0; build blends the last 8 frames into frame 0).
- v20: reel time is remapped onto the v19 picture time (`RMAP`/`srcT` in scene.js, smooth monotone map), so pacing changes without re-animating:
  117 billion line 2.8 s, galaxy round trip 3.2 s with the speed line held, wind line cut, "Outside, dead stars are shooting at you.",
  rehook at 11.75, Voyager chase in slow motion to the crossing at 16.8, question held 3 s. Captions that must sit in reel time use `TN`.
- Sound: `mix.sh` is in v19 picture time; `python3 retime_mix.py` writes `mix_v20.sh` (maps every adelay/between through the inverse map, fixed landings, hole fills).
```sh
RENDER_W=1080 FROM=0 TO=188 OUT_DIR=output/frames20 node render.cjs   # x4 ranges, ~6 s/frame/worker
python3 retime_mix.py && bash mix_v20.sh output/sound20.wav
```
