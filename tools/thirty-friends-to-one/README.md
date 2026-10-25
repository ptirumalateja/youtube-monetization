# 30 Friends to 1 (Slow Light Dark)

20 s, 1080x1920, 30 fps. Copy: `publish-copy/thirty-friends-to-one.md`. Look: `storyboards/slow-light-dark/style-sheet.md`; `sld.js` is a copy of `../slow-light-dark-common/sld.js` (the page server only serves this folder). The Python side imports `sld_text` / `sld_sound` straight from `../slow-light-dark-common/`.

```
cd tools/thirty-friends-to-one && npm install                  # three@0.170.0 (playwright comes from the global install)
OUT=/path/to/render node render.cjs meta                        # meta.json: per-frame AGE / friend count (monotonic check), reason labels, departure times
for w in 0 1 2 3; do OUT=/path/to/render node render.cjs frames $w 4 & done   # 540 frames, 3 motion-blur sub-frames
OUT=/path/to/render W=540 H=960 SUB=1 TIMES=0.4,7,13,16.2 node render.cjs stills   # quick look stills
python3 mix.py /path/to/render/meta.json /path/to/render/mix.wav
python3 compose.py /path/to/render /path/to/deliver             # master (-15 LUFS, true peak checked after AAC) + _music-ready (silent)
```

- `timeline.json`: story times. Hook (68 px, larger than the series default, on from frame 0) out at 2.75 s; AGE 20 at 3.1 s to 35 at 9.2 s; 30 -> 14 in four `waves` (3.3-5.6 s, several friends stand at once) and the lamp closes in a step with every exit; the last 13 leave one at a time (`singles` 5.9-8.75 s, five with reason labels); a 0.6 s hold on AGE 35 / 1 FRIEND; 35 to 60 by 12.6 s with only the two left; the slide 13.95-14.95, take 15.05, raise 15.45, clink 16.20; "AT 60, YOU NEED ONE." stays up from 13.55 s to the end of a 20.0 s cut (about 3.8 s of hold after the clink).
- `scene.js`: pure `renderAt(t)`. Table frame (u along the table, v across; side A = the hero's right), the lamp over the head end (wide and aimed down the table at 20, narrowed onto the two by 13.4 s; the beam mesh is lengthened and its ray-march dithered for the wide cone), table/chairs/glasses, the red candle (burns down, flame steadies after the clink), the 30 friends (seated motion: talk, lean, laugh, toast, sip; departure: stand, step beside the chair, push it in, walk into the dark and fade), the two heroes (stoop with age; the glass slide and the toast), the camera (side three-quarter wide, near-static while the table is full, then a push-in that orbits to the front-left of the hero so the toast is in view), and `metaAt` for the overlay and mix. Departures go roughly from the far end toward the two; the five labelled exits are pinned to lit side-A seats (`PIN`) so each label sits over a friend you can see stand up (`labelVis()` in the page reports how much of each label window is in frame).
- `overlay.py`: hook, AGE / FRIENDS counter, reason labels, end line, watermark (series text kit).
- `mix.py`: synthesised crowd (30 voices murmuring and laughing, thinning as each friend leaves), toast clinks, chair scrapes, footsteps, clock, the glass slide, the toast clink + warm low tone; CC0 room tone from the kit.
