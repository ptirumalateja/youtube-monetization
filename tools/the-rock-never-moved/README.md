# The Rock Never Moved (Slow Light Dark)

12.0 s, 1080x1920, 30 fps. Copy: `publish-copy/the-rock-never-moved.md`. Look: `storyboards/slow-light-dark/style-sheet.md` (dark void, one gold lamp, cream stickman). `sld.js` is the kit file plus one addition: `F.thick`, a muscle scale for limb and torso radius. Python imports `sld_text` and `sld_sound` from `../slow-light-dark-common/`.

```
cd tools/the-rock-never-moved && npm install                    # three@0.170.0 (playwright comes from the global install)
OUT=/path/to/render node render.cjs meta                          # meta.json: shot/cut/day per frame + the mockers' screen positions
for w in 0 1 2 3; do OUT=/path/to/render node render.cjs frames $w 4 & done   # 360 frames
OUT=/path/to/render W=360 H=640 SUB=1 node render.cjs stills      # the review times in timeline.json
python3 mix.py /path/to/render/meta.json /path/to/render/mix.wav
python3 compose.py /path/to/render /path/to/deliver               # master (-15 LUFS, true peak checked after AAC) + _music-ready (silent)
```

- `timeline.json`: the nine push cuts (`[start, day]`; each opens on the impact at start + `impactLag`), the mocking cuts, the stop, the lift beats, the boom and the text times. `scene.js`, `overlay.py` and `mix.py` all read it.
- `scene.js`:
  - The rock sits at the origin. He pushes from +x, leaning in hard on a diagonal, with his feet sliding back.
  - Every cut has its own camera, and the camera shakes on the impact.
  - His muscle grows with the day count: `thickOf(day)` goes from 1.0 on day 1 to about 2.15 on day 365.
  - Two dim figures laugh at the edge of the light in cuts 3 and 5.
  - Day 365: he steps back and looks at his arms.
  - The lift is one shot. He crouches and grips, brings the rock to his chest, then presses it overhead. A warm front light comes in, because the rock blocks the lamp. The dust ring and the lamp flare land on the boom.
- `overlay.py`:
  - The hook "HE PUSHED IT / EVERY DAY."
  - The DAY counter, which punches in on every impact.
  - The mockers' words in orange-yellow ("IT WON'T MOVE", "GIVE UP", "WASTE OF TIME", "HAHAHA").
  - "IT NEVER MOVED." through the stop.
  - The end lines "THE ROCK WAS / NEVER THE POINT." and "IT WAS BUILDING YOU."
- `mix.py`:
  - Montage: a thud, a sub kick, a breath and a counter clack on every impact, with off-beat kicks between the slow early cuts, over a drone that climbs.
  - The mockers' dry laughs.
  - The stop drops to near silence.
  - The lift: a rising rumble and strained breaths into the boom, then a warm open chord.
  - No whooshes.
