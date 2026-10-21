#!/bin/bash
# build.sh SCRATCH : render frames, overlay, mix, composite -> SCRATCH/nine-minutes.mp4  (needs the http server on :8771)
set -e; S=${1:?scratch dir}; D=$(cd "$(dirname "$0")" && pwd); mkdir -p "$S/fr"
for w in 0 1 2; do node "$D/render.js" 1080 1920 "$S/fr" $w 660 3 2 > "$S/r$w.log" 2>&1 & done; wait
python3 "$D/overlay.py" "$S/overlay.mov"
python3 "$D/mix.py" "$S/mix.wav" ${GAIN:-1.1}
ffmpeg -v error -y -framerate 30 -i "$S/fr/f%04d.jpg" -i "$S/overlay.mov" -i "$S/mix.wav" \
  -filter_complex "[0:v]format=yuv444p,noise=alls=2:allf=t,vignette=PI/5[b];[b][1:v]overlay=format=auto,format=yuv420p[v]" \
  -map "[v]" -map 2:a -c:v libx264 -preset slow -b:v 9500k -maxrate 11M -bufsize 20M -profile:v high -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart "$S/nine-minutes.mp4"
ffmpeg -hide_banner -i "$S/nine-minutes.mp4" -af ebur128=peak=true -f null - 2>&1 | grep -A14 Summary | grep -E "I:|Peak:"
