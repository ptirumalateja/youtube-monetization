# Born Rich climb reel

Remake of the V-Visuals "Perfectionist vs Action Taker" ladder reel in a golden-hour cut-paper look.

- `scene.html`: 2D canvas, `renderAt(t)`; all timings are constants at the top.
- `node render.js stills <dir> t1 t2 ...` or `node render.js video out.mp4 30 4` (~50 s on 4 CPUs).
- `python3 sfx.py bed.wav`: SFX-only bed from `sfx/` (ElevenLabs foley via `sfx/gen.sh`; hammer/step/plank_grab reused from tools/climb). Loudnorm -16 LUFS.
- Mux: `ffmpeg -i silent.mp4 -i bed.wav -c:v copy -c:a aac -b:a 192k -shortest out.mp4`.
