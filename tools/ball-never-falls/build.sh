#!/usr/bin/env bash
# Assemble the reel. Needs: frames in $FRAMES (f0000.jpg...), python3 + Pillow + numpy, ffmpeg.
# usage: FRAMES=/path/to/frames OUT=/path/to/ball_never_falls.mp4 ./build.sh
set -euo pipefail
FRAMES=${FRAMES:?}; OUT=${OUT:?}; W=$(mktemp -d)
python3 overlay.py "$W/overlay.mov"
python3 mix.py "$W/audio.wav"
ffmpeg -y -v error -framerate 30 -i "$FRAMES/f%04d.jpg" -i "$W/overlay.mov" -i "$W/audio.wav" \
  -filter_complex "[0:v]scale=1080:1920:flags=lanczos,format=yuv420p[b];[b][1:v]overlay=format=auto,format=yuv420p[v]" \
  -map "[v]" -map 2:a -c:v libx264 -crf 23 -preset slow -pix_fmt yuv420p -c:a aac -b:a 192k -af "asoftclip=type=tanh,volume=-1.2dB,alimiter=limit=0.8" \
  -t 20 -movflags +faststart "$OUT"
ffmpeg -hide_banner -i "$OUT" -af ebur128=peak=true -vn -f null - 2>&1 | grep -E "^\s+(I|Peak):"
