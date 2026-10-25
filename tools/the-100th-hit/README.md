# The 100th Hit (Slow Light Dark)

18.5 s, 1080x1920, 30 fps, split screen (top / bottom), clean end hold. Copy: `publish-copy/the-100th-hit.md`.
Series look: `storyboards/slow-light-dark/style-sheet.md`; `sld.js` is a copy of `../slow-light-dark-common/sld.js` (the page server only serves this folder).

```
cd tools/the-100th-hit && npm install                          # three@0.170.0 (playwright comes from the global install)
OUT=/path/to/render node render.cjs meta                       # meta.json: hit times + per-frame counters (asserts monotonic, ends 99 / 100)
for w in 0 1 2 3; do OUT=/path/to/render node render.cjs frames $w 4 & done   # 555 frames
OUT=/path/to/render W=540 H=960 SUB=1 TIMES=5,13.9,16.9 node render.cjs stills  # quick look stills
python3 mix.py /path/to/render/meta.json /path/to/render/mix.wav
python3 compose.py /path/to/render /path/to/deliver            # master (-15 LUFS) + _music-ready (silent)
```

- `timeline.json`: story times (hit 1 at 2.0 s, hit 99 at 14.0 s, release / land / turn / walk / fade of the quitter, breath / lift / strike of the other, hit 100 at 16.45 s, cool-down, final glow, end tilt, text times).
- Hit pace: interval `0.06 + 0.84 e^(-k/tau)` s, tau solved so hit 99 lands at 14.0 s (tau about 6.8): 0.9 s for the first swing, under 0.1 s from about hit 25. `scene.js hitTimes()`; exported in `meta.json` and read by the overlay and the mix.
- `scene.js`: one stage (series lamp, beam, motes, soft-mirror floor, grade from `sld.js`) rendered twice per frame, top half then bottom half (both 1080x960), identical state until hit 99. Boulder = faceted displaced sphere; cracks are a shader (warped 3D Voronoi edges, only some edges open, a front that spreads from the impact point with each hit; red emission rises with the count, plus a per-hit heat pulse and a red point light). Hammer contact angle is solved against the boulder surface. Hit 100: 80 instanced fragments drifting out, gold point light, core, halo and rays. Sparks, dust and gold motes are one GPU particle system keyed to the hit times.
- `overlay.py`: gold divider, hook and end line on the divider, per-half counters that turn into QUITS AT 99 / HITS 100, watermark (helpers from `../slow-light-dark-common/sld_text.py`).
- `mix.py`: synthesised stone hits, ember crackle, rising drone, hard-stop gate after 99, breaths/footsteps/clunk, hit-100 boom; CC0 wind (22331) and CC0 explosion (814046) from `../sfxlib/`.
