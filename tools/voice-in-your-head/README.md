# The Voice in Your Head (20 s, 1080x1920, 60 fps)

Chalk stickman on a navy board, drawn in Canvas 2D; `window.renderAt(t)` in `scene.js` is a pure function of time (chalk "boil" at 10 fps, motion blur by sub-frame averaging when the camera moves fast). Fonts: Permanent Marker (Apache 2.0) in `fonts/`, Liberation Mono for the timer. Sound: `sfx.py` (numpy, fully synthesised, no credits). Notes, shot plan and copy: `final-reels/the-voice-in-your-head.md`.

```sh
npm install                                   # playwright-core; Chromium from /opt/pw-browsers or CHROME_PATH
node render.mjs /tmp/st stills 0.4 5.3 8.5 10.1 13.8 16.5     # test stills
for w in 0 1 2 3; do node render.mjs /tmp/f60 frames 60 $w 4 & done; wait   # 1200 frames, about 1.5 min on 4 CPUs
python3 sfx.py /tmp/sfx.wav
ffmpeg -i /tmp/sfx.wav -af "loudnorm=I=-15:TP=-2:LRA=14:linear=true" -ar 48000 /tmp/mix.wav
for p in 1 2; do ffmpeg -y -framerate 60 -i /tmp/f60/f%05d.jpg -i /tmp/mix.wav -c:v libx264 -b:v 10.5M -maxrate 16M -bufsize 20M \
  -pass $p -preset slow -pix_fmt yuv420p -c:a aac -b:a 192k -t 20 -movflags +faststart $([ $p = 1 ] && echo "-an -f null /dev/null" || echo out.mp4); done
```
CRF 18 gives a 38 MB master; the two-pass 10.5 Mbps encode keeps it at 27 MB for chat delivery (the film grain is what costs bits).
