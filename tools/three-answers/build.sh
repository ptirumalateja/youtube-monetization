#!/usr/bin/env bash
# Build "Three Answers to One Fall" end to end. Usage: ./build.sh <workdir>   (needs node_modules with three@0.170.0 + playwright-core, ffmpeg, python3 numpy scipy pillow)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; WD="${1:?workdir}"; mkdir -p "$WD/frames"
cd "$HERE"
python3 -m http.server 8777 >/dev/null 2>&1 & SRV=$!; trap 'kill $SRV' EXIT; sleep 1
for k in 0 1 2 3; do SUB=3 node render.js 1080 1920 "$WD/frames" $k 660 4 > "$WD/render_$k.log" 2>&1 & done; wait
python3 overlay.py "$WD/overlay.mov"
python3 mix.py "$WD/mix.wav"
ffmpeg -v error -y -framerate 30 -i "$WD/frames/f%04d.jpg" -i "$WD/overlay.mov" -i "$WD/mix.wav" \
  -filter_complex "[0:v]format=rgba[b];[b][1:v]overlay=0:0:format=auto,format=yuv420p[v];[2:a]loudnorm=I=-15:TP=-3:LRA=11,asoftclip=type=tanh:threshold=0.6,alimiter=limit=0.6:attack=1:release=50:level=false,aresample=48000[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset slow -crf 18 -profile:v high -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -ar 48000 -movflags +faststart -t 22 "$WD/master_crf18.mp4"
# share size (~28 MB): two-pass 9.8 Mbps (the film grain makes CRF 18 about 200 MB)
for p in 1 2; do
  if [ $p = 1 ]; then ffmpeg -v error -y -i "$WD/master_crf18.mp4" -c:v libx264 -preset slow -b:v 9800k -maxrate 14M -bufsize 20M -pass 1 -passlogfile "$WD/x264" -an -f null /dev/null
  else ffmpeg -v error -y -i "$WD/master_crf18.mp4" -c:v libx264 -preset slow -b:v 9800k -maxrate 14M -bufsize 20M -pass 2 -passlogfile "$WD/x264" -pix_fmt yuv420p -c:a copy -movflags +faststart "$WD/three-answers-to-one-fall.mp4"; fi
done
ffmpeg -hide_banner -i "$WD/three-answers-to-one-fall.mp4" -af ebur128=peak=true -f null - 2>&1 | grep -A12 Summary | grep -E "^\s+(I|Peak):"
