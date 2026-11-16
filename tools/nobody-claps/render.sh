#!/bin/bash
# Full render: frames (4 workers) -> events -> mix -> mp4.  OUT dir default ./output
set -e; cd "$(dirname "$0")"; OUT=${OUT:-$PWD/output}; export OUT; N=${N:-4}
rm -rf "$OUT/frames"; mkdir -p "$OUT/frames"
for w in $(seq 0 $((N-1))); do node render.cjs frames $w $N & done; wait
node render.cjs events
python3 mix.py "$OUT/events.json" "$OUT/mix.wav"
ffmpeg -v error -y -framerate 30 -i "$OUT/frames/f%05d.jpg" -i "$OUT/mix.wav" -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -af loudnorm=I=-14:TP=-1.5:LRA=11 -ar 48000 -c:a aac -b:a 256k -shortest -movflags +faststart "$OUT/nobody-claps.mp4"
echo done "$OUT/nobody-claps.mp4"
