# They Laughed reel

Ref remake (crowd mocks a climber on the SUCCESS pillar, then claps when he reaches the top). Ours ends with him throwing the summit boulder at them instead of the ref's urinating gag. Look = Born Rich v4 Slow Light (tools/born-rich-climb).

- `scene.html` (v3): side-on climb up the pillar's left edge like the ref (`drawProfile`: near limbs bright, far limbs dimmed), rock lumps along the edge (`HOLDS`), grit falls on every hand/foot landing (`EVENTS`), one lump snaps at 5.75 s, ref-style mantle over the lip. Hook = crowd laughing close-up. v1/v2 kept as `scene_v1.html`, `scene_v2.html` (v2 = front-face climb, rejected).
- `node render.js stills <dir> t1 t2 ...` or `node render.js video out.mp4 30 4` (~50 s on 4 CPUs).
- `node render.js events events.json` then `python3 sfx.py bed.wav events.json`: SFX-only bed from `sfx/` (ElevenLabs via `sfx/gen.sh`; dizzy/thud/tumble/step reused from born-rich-climb). Loudnorm -16 LUFS.
- Mux: `ffmpeg -i silent.mp4 -i bed.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out.mp4`.

## v4 (current scene.html): pee ending, ref-exact shots
- Ending switched to the ref's pee (stylised gold stream, crowd cowers). Boulder ending kept in scene_v3.html.
- Shots/cuts copy the ref: 0 wide, 2.2 crowd two-shot, 3.9 climb close, 5.8 pullback, 7.3 summit mantle, 9.6 wide, 12.2 two-shot, 12.75 crowd close.
- All figures side-on (drawProfile); knees bend forward, climber elbows bend down (elbow -1).
- Build: `node render.js events events.json && python3 sfx.py bed.wav events.json && node render.js video silent.mp4 30 4`, then mux bed.wav.
