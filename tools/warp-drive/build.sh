#!/bin/bash
# Full build: frames -> overlay -> sound -> mux.  Usage: ./build.sh <workdir>
# Needs: node_modules (three@0.170.0, playwright-core) next to index.html, Chromium at /opt/pw-browsers, ffmpeg, python3 + numpy + PIL.
# Render first (4 interleaved workers):  python3 -m http.server 8790 &  then  for w in 0 1 2 3; do node render.js 1080 1920 $WD/frames 8790 $w 660 4 & done
# and the marker projections:            node proj.js 8790 $WD/proj.json
set -e; WD=$1
python3 overlay.py $WD/frames $WD/proj.json $WD/video.mp4
python3 mix_warp.py $WD/mix.wav
# mix_warp.py already lands near -15 LUFS and keeps true peak under -2 dBTP after AAC (measured after encoding, playbook 4.3)
# master: high bitrate for uploads; share: under 30 MB for chat delivery
ffmpeg -loglevel error -y -i $WD/video.mp4 -i $WD/mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -crf 19 -maxrate 28M -bufsize 56M -pix_fmt yuv420p \
  -c:a aac -b:a 192k -shortest -movflags +faststart $WD/the-ship-never-moves_master.mp4
ffmpeg -loglevel error -y -i $WD/video.mp4 -i $WD/mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 9M -maxrate 10M -bufsize 20M -pix_fmt yuv420p \
  -c:a aac -b:a 192k -shortest -movflags +faststart $WD/the-ship-never-moves.mp4
for f in the-ship-never-moves_master.mp4 the-ship-never-moves.mp4; do ls -la $WD/$f; ffmpeg -hide_banner -i $WD/$f -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"; done
