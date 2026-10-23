#!/usr/bin/env bash
# Full build: shader plates -> composited frames -> sound -> encodes. Usage: ./build.sh OUTDIR  (ANIM=anim.py for v1)
set -euo pipefail
cd "$(dirname "$0")"
O=${1:?outdir}
A=${ANIM:-anim2.py}
python3 "$A" events "$O"
python3 "$A" plates "$O"          # skips plates that already exist
python3 "$A" frames "$O"          # skips frames that already exist
python3 sound.py "$O/events.json" "$O/mix.wav"
V="-framerate 30 -i $O/frames/f%04d.png"
ffmpeg -y -loglevel error $V -i "$O/mix.wav" -af "loudnorm=I=-15:TP=-2:LRA=11" -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p \
  -c:a aac -b:a 192k -shortest -movflags +faststart "$O/the-photon-that-made-your-eye.mp4"
ffmpeg -y -loglevel error $V -i "$O/mix.wav" -af "loudnorm=I=-15:TP=-2:LRA=11" -c:v libx264 -crf 15 -preset slow -pix_fmt yuv420p \
  -c:a aac -b:a 256k -shortest -movflags +faststart "$O/the-photon-that-made-your-eye_master.mp4"
ffmpeg -y -loglevel error $V -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p -an -movflags +faststart \
  "$O/the-photon-that-made-your-eye_music-ready.mp4"
ffmpeg -y -loglevel error -i "$O/the-photon-that-made-your-eye.mp4" -vf "fps=2,scale=216:384,tile=8x3" -frames:v 1 \
  "$O/the-photon-that-made-your-eye_contact_2fps.jpg"
