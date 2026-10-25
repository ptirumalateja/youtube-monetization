# Tug of War (Slow Light Dark)

16 s, 1080x1920, 30 fps. Copy: `publish-copy/tug-of-war.md`. Series look: `storyboards/slow-light-dark/style-sheet.md` (on branch `claude/chain-never-locked`); `sld.js`, `sld_text.py`, `sld_sound.py`, `render.cjs` are copies of `tools/slow-light-dark-common/`.

Local changes to the shared kit (no look value changed): `sld.js` exports `addBeam()` (the beam + motes code, unchanged, extracted so a second lamp can reuse it); `render.cjs` has a `meta` mode. Per-reel stage options: `spot: 50` (series 60, the close-lit standing figure clips otherwise) and both lamps sit 1.1 m toward the camera (tilted 14 degrees) so upright figures catch light on their front.

```
cd tools/tug-of-war && npm install && python3 make_doubt.py        # make_doubt.py writes doubt.png / doubt_hi.png (the etched word)
OUT=/path/r W=540 H=960 SUB=1 TIMES=0.4,5.2,10.3,15.2 node render.cjs stills
OUT=/path/r node render.cjs meta 16 30                              # meta.json for the mix
for w in 0 1 2 3; do OUT=/path/r/final node render.cjs frames $w 4 16 30 & done    # 480 frames, about 25 min on 4 CPU cores
python3 mix.py /path/r/meta.json /path/r/final/mix.wav
python3 compose.py /path/r/final /path/deliver                      # master + _music-ready (silent)
```
- `timeline.json`: heaves, yanks, camera and lamp times, reveal (10.00), let-go (13.25), stumble. Scene, overlay and mix read it.
- `scene.js`: pure `renderAt(t)`. The rope is analytic while taut; from 12.85 a verlet rope is simulated once at page load (deterministic) so parallel workers agree.
