# The Phone at Dinner (Slow Light Dark)

17.5 s, 1080x1920, 30 fps. Copy: `publish-copy/phone-at-dinner.md`. Look: `storyboards/slow-light-dark/style-sheet.md`; `sld.js` is a copy of `../slow-light-dark-common/sld.js` (the page server only serves this folder). The Python side imports `sld_text` / `sld_sound` from `../slow-light-dark-common/`.

```
cd tools/phone-at-dinner && npm install                         # three@0.170.0 (playwright comes from the global install)
OUT=/path/to/render node render.cjs meta                         # meta.json: per-frame DINNER (monotonic check), her alpha / talk, phone glow
for w in 0 1 2 3; do OUT=/path/to/render node render.cjs frames $w 4 & done   # 525 frames, 3 motion-blur sub-frames
OUT=/path/to/render W=540 H=960 SUB=1 TIMES=0.3,7.5,13.9 node render.cjs stills
python3 mix.py /path/to/render/meta.json /path/to/render/mix.wav
python3 compose.py /path/to/render /path/to/deliver              # master (-15 LUFS, true peak checked after AAC) + _music-ready (silent)
```

- `timeline.json`: hook out 2.75 s; DINNER 1 -> 1,825 (3.0-12.4 s, power 2.1 so the years speed up) with three story lines under it; her touch on his hand (4.0-5.2), she goes quiet (6.4), turns slate (8.2-10.4), fades (10.2-12.3); he looks up (12.75-13.45, the hit at 13.45) and turns the phone face down (13.35-13.9); "ONE NIGHT HE LOOKED UP." 13.0, "SHE WASN'T THERE." 14.7, held to the end.
- `scene.js`: pure `renderAt(t)`. Small table for two, two chairs, plates, two glasses (hers stays full), the red phone (the one red object: held out on the camera side so it reads from frame 0; its red light on him grows over the years; the halo and the phone are hidden from the floor mirror), the two cream figures (she: talk, laugh, reach, slump, cream -> slate -> gone), the lamp (drifts off her side of the table 4.5-12.4 s so her half sinks into shadow as she fades), the camera (both in frame, slow push toward him, slow pull back that keeps him and her empty chair in frame).
- `overlay.py`: hook, DINNER counter with story lines, the two end lines (series text kit).
- `mix.py`: her voice, his thumb ticks and blips (duller and echoing over the years), the quickening cutlery ticks, a low A-minor pad that swells as she fades and three falling low piano notes (A2, F2, E2), the held breath, the cold low hit and the phone face down; CC0 room tone from the kit.
