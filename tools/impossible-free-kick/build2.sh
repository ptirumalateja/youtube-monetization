#!/bin/bash
# V2 (goal-first edit) build: physics -> 3D frames -> sound -> text -> encodes. Needs node_modules (three@0.170.0, playwright-core@1.56.1)
# and a static server on :8771 serving this folder (npx http-server -p 8771 -c-1 .).
set -e
OUT=${1:-out2}; mkdir -p $OUT
python3 physics.py
node shot.js index2.html 1080 1920 $OUT/frames --range 0 300 & node shot.js index2.html 1080 1920 $OUT/frames --range 300 600 & wait
python3 -c "import json;a=json.load(open('$OUT/frames/meta_0_300.json'));a.update(json.load(open('$OUT/frames/meta_300_600.json')));json.dump(a,open('$OUT/meta.json','w'))"
python3 sound2.py $OUT/meta.json $OUT/sound.wav
python3 overlay2.py $OUT/frames $OUT/meta.json $OUT/text
AF="volume=+2.5dB,alimiter=limit=0.7:level=false"
ffmpeg -y -loglevel error -framerate 30 -i $OUT/text/f%04d.jpg -i $OUT/sound.wav -af $AF -c:v libx264 -preset slow -crf 18 -maxrate 10M -bufsize 10M -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 256k -shortest $OUT/roberto-carlos-free-kick_v2.mp4
ffmpeg -y -loglevel error -framerate 30 -i $OUT/text/f%04d.jpg -i $OUT/sound.wav -af $AF -c:v libx264 -preset slow -crf 18 -maxrate 24M -bufsize 24M -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 256k -shortest $OUT/roberto-carlos-free-kick_v2_master.mp4
ffmpeg -y -loglevel error -i $OUT/roberto-carlos-free-kick_v2.mp4 -an -c:v copy $OUT/roberto-carlos-free-kick_v2_music-ready.mp4
