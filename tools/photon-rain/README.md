# Photon Rain: build

22 s, 1080x1920, 30 fps, wordless, loops. Record and publish copy: `final-reels/photon-rain.md`.

| File | What it does |
|---|---|
| `index.html` | three.js r0.170 scene. `window.renderAt(t, sub)` renders one frame (sub-frames averaged over a 1/60 s shutter) and returns `{img, info}`; `info` holds the screen positions and photon counts the overlay needs. |
| `shot.js` | Test stills: `node shot.js 540 960 out 0.1 9.6 14.5 18` |
| `render.js` | Frames + per-frame JSON: `node render.js 1080 1920 frames <start> 660 <step>` (run 4 workers with start 0..3, step 4). |
| `overlay_photon.py` | Hook, labels, zoom counter, the two photon counters (asserted monotonic), red pixel markers, end line. Writes `photon_overlay.mov`. |
| `mix_photon.py` | Fully synthesised sound (no samples). Writes `photon_mix.wav`. |

Setup (in a scratch folder next to these files):
```
npm i three@0.170.0 playwright-core@1.56.0
python3 -m http.server 8777 &
```
The scripts expect Chromium at `/opt/pw-browsers/chromium-1194/chrome-linux/chrome` (SwiftShader, CPU only). A native 1080x1920 render takes about 1.5-2 h on 4 cores.

Assemble:
```
ffmpeg -framerate 30 -i frames/f%04d.jpg -i photon_overlay.mov -i photon_mix.wav \
  -filter_complex "[0][1]overlay=format=auto,format=yuv420p[v];[2]volume=2.5dB,alimiter=limit=0.70:attack=1:release=60:level=false,asoftclip=type=tanh[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset slow -crf 19 -maxrate 9M -bufsize 18M -c:a aac -b:a 192k -movflags +faststart photon-rain.mp4
```
