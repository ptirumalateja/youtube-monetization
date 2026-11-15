#!/bin/bash
# full render: 4 workers -> frames -> mp4 with mix, loudness -14 LUFS
cd "$(dirname "$0")"; N=${N:-4}
for w in $(seq 0 $((N-1))); do SUB=${SUB:-2} OUT=output node render.cjs frames $w $N > output/w$w.log 2>&1 & done; wait
OUT=output node render.cjs events && python3 mix.py output/events.json output/mix.wav
ffmpeg -v error -y -framerate 30 -i output/frames/f%05d.jpg -i output/mix.wav -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -af loudnorm=I=-14:TP=-1.5:LRA=11 -ar 48000 -movflags +faststart -shortest output/hall-of-mirrors.mp4
echo done
