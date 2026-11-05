# The Phone at Dinner (Slow Light Dark)

14.0 s, 1080x1920, 30 fps. Copy: `publish-copy/phone-at-dinner.md`. Look: `storyboards/slow-light-dark/style-sheet.md`; `sld.js` is a copy of `../slow-light-dark-common/sld.js` (the page server only serves this folder). The Python side imports `sld_text` / `sld_sound` from `../slow-light-dark-common/`.

```
cd tools/phone-at-dinner && npm install                         # three@0.170.0 (playwright comes from the global install)
OUT=/path/to/render node render.cjs meta                         # meta.json: per-frame DINNER (monotonic check), her alpha / talk, phone glow
for w in 0 1 2 3; do OUT=/path/to/render node render.cjs frames $w 4 & done   # 420 frames, 3 motion-blur sub-frames
OUT=/path/to/render W=540 H=960 SUB=1 TIMES=0.3,7.5,13.9 node render.cjs stills
python3 mix.py /path/to/render/meta.json /path/to/render/mix.wav
python3 compose.py /path/to/render /path/to/deliver              # master (-15 LUFS, true peak checked after AAC) + _music-ready (silent)
```

- `timeline.json`: hook out 2.2 s; DINNER 1 -> 1,825 (2.3-9.6 s, power 2.1 so the years speed up) with three story lines under it; her touch on his hand (3.0-3.9), she goes quiet (4.8), turns slate (6.2-8.0), fades (7.9-9.5); he looks up (9.9-10.5, the hit at 10.5) and turns the phone face down (10.4-10.9); "ONE NIGHT HE LOOKED UP." 10.1, "SHE WASN'T THERE." 11.4, held to the end. Scene and mix times are all derived from these keys.
- `scene.js`: pure `renderAt(t)`. Small table for two, two chairs, plates, two glasses (hers stays full), the red phone (the one red object: held out on the camera side so it reads from frame 0; its red light on him grows over the years; the halo and the phone are hidden from the floor mirror), the two cream figures (she: talk, laugh, reach, slump, cream -> slate -> gone), the lamp (drifts off her side of the table 4.5-12.4 s so her half sinks into shadow as she fades), the camera (both in frame, slow push toward him, slow pull back that keeps him and her empty chair in frame).
- `overlay.py`: hook, DINNER counter with story lines, the two end lines (series text kit).
- `mix.py`: her voice, his thumb ticks and blips (duller and echoing over the years), the quickening cutlery ticks, a low A-minor pad that swells as she fades and three falling low piano notes (A2, F2, E2), the held breath, the cold low hit and the phone face down; CC0 room tone from the kit.
