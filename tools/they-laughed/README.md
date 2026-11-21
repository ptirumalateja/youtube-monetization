# They Laughed reel

Ref remake (crowd mocks a climber on the SUCCESS pillar, then claps when he reaches the top). Ours ends with him throwing the summit boulder at them instead of the ref's urinating gag. Look = Born Rich v4 Slow Light (tools/born-rich-climb).

- `scene.html`: 2D canvas, `renderAt(t)`, 17.5 s. World is one 1080x1920 frame; shots are camera framings (`SHOTS`, `camAt`). 0-0.8 s flash-forward hook (boulder overhead), then wide / crowd close-up / climb / summit / crowd clap / throw / impact / wide hold with end question. Rock is painted at 2x so close-ups stay crisp.
- `node render.js stills <dir> t1 t2 ...` or `node render.js video out.mp4 30 4` (~50 s on 4 CPUs).
- `python3 sfx.py bed.wav`: SFX-only bed from `sfx/` (ElevenLabs via `sfx/gen.sh`; dizzy/thud/tumble/step reused from born-rich-climb). Loudnorm -16 LUFS.
- Mux: `ffmpeg -i silent.mp4 -i bed.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out.mp4`.
