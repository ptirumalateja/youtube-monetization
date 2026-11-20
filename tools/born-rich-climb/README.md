# Born Rich climb reel

Shot-for-shot remake of the V-Visuals "Perfectionist vs Action Taker" ladder reel (15.2 s, locked camera, ref-measured layout).

- `scene.html` (v3): 2D canvas, `renderAt(t)`; layout and timings are constants at the top, measured from the ref (720-space x1.5). `?theme=A` painted night look, `?theme=B` Slow Light look (navy/teal grade, red label chips, gold figure glow).
- Older looks: `scene_v1.html` (cut-paper golden hour, own camera moves), `scene_v2.html` (painted night, own camera).
- `THEME=A node render.js stills <dir> t1 t2 ...` or `THEME=B node render.js video out.mp4 30 4` (~1 min on 4 CPUs).
- `python3 sfx.py bed.wav`: SFX-only bed from `sfx/` (ElevenLabs foley via `sfx/gen.sh`; hammer/step/plank_grab reused from tools/climb). Loudnorm -16 LUFS. Timings mirror scene.html.
- Mux: `ffmpeg -i silent.mp4 -i bed.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out.mp4`.
