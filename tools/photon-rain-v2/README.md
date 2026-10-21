# Photon Rain v2: build (reference-style line art)

32 s, 1080x1920, 30 fps, wordless (headlines carry the story). The record is in `final-reels/photon-rain.md`.

| File | What it does |
|---|---|
| `index.html` | 2D canvas scene, drawn by `window.renderAt(t)`: flat navy blueprint, draw-on line-art phone and camera, Space Grotesk headlines with a per-character rise, JetBrains Mono numbers, and photon-noise tiles made from a Poisson model of our own night scene. |
| `shot.js` | Test stills: `node shot.js out 0 1.4 14.3 23` |
| `render.js` | All 960 frames (about 2 min, CPU only). |
| `ev.js` | Exports the photon and drop times from the scene to `events.json`, so the sound lands on the exact frames. |
| `mix_v2.py` | Fully synthesised sound (no samples, no credits). |

Setup: `npm i @fontsource/space-grotesk@5.1.0 @fontsource/jetbrains-mono@5.1.0 playwright-core@1.56.0`, then serve this folder with `python3 -m http.server 8778`.

Assemble:
```
ffmpeg -framerate 30 -i fr/f%04d.jpg -i mix_v2.wav \
  -af "volume=3dB,alimiter=limit=0.62:attack=0.5:release=50:level=false,asoftclip=type=tanh" \
  -c:v libx264 -preset slow -crf 18 -maxrate 8M -bufsize 16M -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart photon-rain-v2.mp4
```
