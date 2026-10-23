# The Voice in Your Head V2 (20 s, 1080x1920, 60 fps)

Reach cut of the Voice in Your Head reel: white scribble-line figures on a blue paper ground, Canvas 2D, `window.renderAt(t)` in `scene.js` is a pure function of time (line "boil" at 10 fps, sub-frame motion blur on fast camera moves, no blur across the 9.0 s snap cut). Sound: `sfx.py` (numpy, fully synthesised). Notes, shot plan and copy: `final-reels/the-voice-in-your-head-v2.md`.

```sh
npm install                                   # playwright-core; Chromium from /opt/pw-browsers or CHROME_PATH
node render.mjs /tmp/st stills 0 5.3 9.4 11 13.8 16.5 19.95
for w in 0 1 2 3; do node render.mjs /tmp/f60 frames 60 $w 4 & done; wait   # 1200 frames, about 1 min on 4 CPUs
python3 sfx.py /tmp/sfx.wav
ffmpeg -i /tmp/sfx.wav -af "loudnorm=I=-15:TP=-2:LRA=14:linear=true" -ar 48000 /tmp/mix.wav
for p in 1 2; do ffmpeg -y -framerate 60 -i /tmp/f60/f%05d.jpg -i /tmp/mix.wav -c:v libx264 -b:v 10.5M -maxrate 16M -bufsize 20M \
  -pass $p -preset slow -pix_fmt yuv420p -c:a aac -b:a 192k -t 20 -movflags +faststart $([ $p = 1 ] && echo "-an -f null /dev/null" || echo out.mp4); done
ffmpeg -i out.mp4 -an -c:v copy out_silent.mp4
```
