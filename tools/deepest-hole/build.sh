#!/usr/bin/env bash
# usage: FRAMES=/path/to/frames OUT=/path/to/the_deepest_hole.mp4 [HOOK="..."] ./build.sh   (frames f0000.jpg..f0659.jpg, 30 fps, 720x1280)
# needs `python3 -m http.server 8791` running in this directory (proj.js reads the scene's camera)
set -euo pipefail
FRAMES=${FRAMES:?}; OUT=${OUT:?}; W=$(mktemp -d)
node proj.js "$W/proj.json"; python3 overlay.py "$W/proj.json" "$W/overlay.mov" ${HOOK:+"$HOOK"}; python3 mix.py "$W/audio.wav"
ffmpeg -y -v error -framerate 30 -i "$FRAMES/f%04d.jpg" -i "$W/overlay.mov" -i "$W/audio.wav" \
  -filter_complex "[0:v]scale=1080:1920:flags=lanczos,format=yuv420p[b];[b][1:v]overlay=format=auto,format=yuv420p[v]" \
  -map "[v]" -map 2:a -c:v libx264 -crf 20 -preset slow -pix_fmt yuv420p -c:a aac -b:a 192k -af "volume=${GAIN:--1dB}" \
  -t 22.0 -movflags +faststart "$OUT"
ffmpeg -hide_banner -i "$OUT" -af ebur128=peak=true -vn -f null - 2>&1 | grep -E "^\s+(I|Peak):"
