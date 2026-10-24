# The Chain Was Never Locked (Slow Light Dark pilot)

16 s, 1080x1920, 30 fps, loops. Copy: `publish-copy/chain-never-locked.md`.

```
cd tools/chain-never-locked && npm install                    # three@0.170.0 (playwright comes from the global install)
OUT=/path/to/render node render.cjs meta                      # meta.json: per-frame YEAR (monotonic check), walker phases, event times
for w in 0 1 2 3; do OUT=/path/to/render node render.cjs frames $w 4 & done   # 480 frames, 3 motion-blur sub-frames (7 on the jolts)
OUT=/path/to/render W=540 H=960 SUB=1 TIMES=0.6,3.56,12.6 node render.cjs stills   # quick look stills
python3 mix.py /path/to/render/meta.json /path/to/render/mix.wav
python3 compose.py /path/to/render /path/to/deliver           # master (-15 LUFS, -1.5 dBTP) + _music-ready (silent)
```

- `timeline.json`: every story time (grab, snaps 2.86/3.56, release, sit-down, YEAR 2..12 times, push-in, creak, glint, cut 13.00, look). Scene, overlay and mix all read it.
- `scene.js`: pure `renderAt(t)` (no state between frames). Sections: palette, years/slump/dust, stage, lights, rim + dust shader helpers, floor (soft Reflector under a 90% concrete skin), post/ring/cuff, padlock (shackle open: lifted 3 cm and swung 43° from the first frame), stickman rig (capsule limbs, sphere head, no face, two-bone IK), year-one pull (the chain stops his hands at `HMAX`, which makes the snap), chain (parabolic sag clamped to the floor + sideways slack, links every 5 cm), walkers, beam (ray-marched cone, kept out of the floor reflection), motes, dust puffs, camera, post (bloom, soft clamp, vignette, grain).
- `overlay.py`: text layer (JetBrains Mono, tracked caps, cream, soft halo; "SLOW LIGHT" watermark at 35%).
- `mix.py`: all sound synthesised in numpy plus two CC0 Freesound files from `../sfxlib/` (wind room tone; explosion pitched down two octaves under the boom).
