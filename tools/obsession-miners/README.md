# Obsession miners reel

Faithful remake of ref #1 ("Obsession pays off", 4 labelled miners). Ref breakdown: `concepts/viral-ref-five-breakdown.md` in project files.

- `scene.html`: 2D canvas world, `renderAt(t)`. Camera keys (`CAM`) and miner tracks (`OBS`, `EGO`, `TAL`, `MOT`) were matched shot by shot against frame-accurate ref stills.
- `render.js`: `node render.js video out.mp4 30 3` (about 1 minute) or `node render.js stills dir t1 t2 ...`.
- `compare.sh <ref.mp4> <stilldir> <out.jpg> t...`: ref vs ours pairs.
- `sfx.py out.wav`: action-synced SFX (needs numpy, soundfile), uses `../sfxlib/`.
- Mux: `ffmpeg -i silent.mp4 -i sfx.wav -c:v copy -c:a aac -b:a 192k -shortest out.mp4`.
