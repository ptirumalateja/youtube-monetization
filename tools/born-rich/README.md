# Born Rich (Slow Light Dark)

14 s, 1080x1920, 30 fps. Copy: `publish-copy/born-rich.md`. Series look: `storyboards/slow-light-dark/style-sheet.md`.
`sld.js` is the shared kit (from the umbrella reel, with its `vig` option) plus one change: `moteSpan`/`moteCx` spread the
dust along the track so the moving lamp always finds motes.

```
cd tools/born-rich && npm install                        # three@0.170.0 (playwright from the global install)
sfx/gen.sh                                               # ElevenLabs sound effects (already committed)
OUT=/path/to/render node render.cjs meta                 # meta.json: screen positions for the labels, race numbers
for w in 0 1 2 3; do OUT=/path/to/render node render.cjs frames $w 4 & done   # 420 frames
OUT=/path/to/render W=540 H=960 SUB=1 TIMES=0.5,4.8,9.3 node render.cjs stills  # quick look
python3 mix.py /path/to/render/meta.json /path/to/render/mix.wav
python3 compose.py /path/to/render /path/to/deliver      # master (-15 LUFS) + _music-ready (silent)
```

- `timeline.json`: start (0.40), Motivation's burnout (1.6-3.0), Ego's push (3.8) and early celebration (6.2), engine (7.2), the car crossing (8.6) and stopping (9.1), the freeze (9.15), heads turn (9.45-10.4), end card (10.8), caption windows.
- `scene.js`: track along +x (start -5, finish +5), lanes z = +0.95 MOTIVATION / 0 DISCIPLINE / -0.95 EGO, car lane -2.3. Speeds are profiles integrated once, so `renderAt(t)` is pure. The lamp (6 m up, set 1.7 m toward the camera so it lights the runners' fronts) follows the pack, leaning to the leader, and swings onto the car after it crosses. Fixed high camera beyond the finish (FOV 30) looking back down the track; it tilts up during the race and down to the line as the car comes. Car = lofted superellipse body with a canopy (vertex-coloured glass), tyres, red tail bar, headlights, exhaust glow, tail-light streak, skid dust; the finish tape snaps and whips. Fog 0.05 (pilot 0.085) because the stage is longer.
- `overlay.py`: hook SAME GROUND. / SAME FINISH LINE., name tags over the heads, beat captions, the red BORN RICH tag on the car, end card WAS IT EVER A / FAIR RACE? + FOLLOW @SLOWLIGHTTV, watermark.
- `mix.py`: ElevenLabs foley (lamp clunk, start, sprint, jog, panting, whoop, engine pass aligned to the line, nitro, tape, skid, idle, boom) over the series bed (CC0 wind, lamp hum, drone); the freeze ducks everything but the idle.
