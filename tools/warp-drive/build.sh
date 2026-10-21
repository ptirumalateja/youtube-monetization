#!/bin/bash
# Full build: frames -> overlay -> sound -> mux.  Usage: ./build.sh <workdir>
# Needs: node_modules (three@0.170.0, playwright-core) next to index.html, Chromium at /opt/pw-browsers, ffmpeg, python3 + numpy + PIL.
# Render first (4 interleaved workers):  python3 -m http.server 8790 &  then  for w in 0 1 2 3; do node render.js 1080 1920 $WD/frames 8790 $w 660 4 & done
# and the marker projections:            node proj.js 8790 $WD/proj.json
set -e; WD=$1
python3 overlay.py $WD/frames $WD/proj.json $WD/video.mp4
python3 mix_warp.py $WD/mix.wav
# about -15 LUFS integrated, true peak under -1 dBTP after AAC (measure after encoding, playbook 4.3)
ffmpeg -loglevel error -y -i $WD/video.mp4 -i $WD/mix.wav -map 0:v -map 1:a -c:v copy \
  -af "loudnorm=I=-15:TP=-1.5:LRA=11,alimiter=limit=0.84,aresample=48000" -c:a aac -b:a 192k -shortest -movflags +faststart $WD/the-ship-never-moves.mp4
ffmpeg -hide_banner -i $WD/the-ship-never-moves.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
