# They Laughed reel

Ref remake (crowd mocks a climber on the SUCCESS pillar, then claps when he reaches the top). Ours ends with him throwing the summit boulder at them instead of the ref's urinating gag. Look = Born Rich v4 Slow Light (tools/born-rich-climb).

- `scene.html` (v2): flowing curved-limb figures; he climbs the pillar face on rock holds (`HOLDS`), grit falls on every hand/foot landing (`EVENTS`), one hold snaps at 5.75 s. Hook = crowd laughing close-up (no summit flash-forward). v1 kept as `scene_v1.html`.
- `node render.js stills <dir> t1 t2 ...` or `node render.js video out.mp4 30 4` (~50 s on 4 CPUs).
- `node render.js events events.json` then `python3 sfx.py bed.wav events.json`: SFX-only bed from `sfx/` (ElevenLabs via `sfx/gen.sh`; dizzy/thud/tumble/step reused from born-rich-climb). Loudnorm -16 LUFS.
- Mux: `ffmpeg -i silent.mp4 -i bed.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out.mp4`.
