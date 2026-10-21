#!/usr/bin/env bash
# usage: FRAMES=/path/to/frames OUT=/path/to/one_more_shovel.mp4 ./build.sh   (frames f0000.jpg..f0419.jpg at 30 fps, 720x1280)
# needs `python3 -m http.server 8790` running in this directory (proj.js reads the scene's camera)
set -euo pipefail
FRAMES=${FRAMES:?}; OUT=${OUT:?}; W=$(mktemp -d)
node proj.js "$W/proj.json"; python3 overlay.py "$W/proj.json" "$W/overlay.mov"; python3 mix.py "$W/audio.wav"
ffmpeg -y -v error -framerate 30 -i "$FRAMES/f%04d.jpg" -i "$W/overlay.mov" -i "$W/audio.wav" \
  -filter_complex "[0:v]scale=1080:1920:flags=lanczos,format=yuv420p[b];[b][1:v]overlay=format=auto,format=yuv420p[v]" \
  -map "[v]" -map 2:a -c:v libx264 -crf 20 -preset slow -pix_fmt yuv420p -c:a aac -b:a 192k -af "volume=-2.2dB,asoftclip=type=tanh,alimiter=limit=0.8:level=disabled" \
  -t 14.0 -movflags +faststart "$OUT"
ffmpeg -hide_banner -i "$OUT" -af ebur128=peak=true -vn -f null - 2>&1 | grep -E "^\s+(I|Peak):"
