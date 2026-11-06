#!/bin/bash
# timeline -> mix -> 4-chunk parallel render -> concat + mux -> app preview
cd "$(dirname "$0")"; mkdir -p output/parts
python3 edit.py --timeline && python3 audio/mix.py || exit 1
N=$(python3 -c "import edit; print(int(edit.DUR*edit.FPS))"); C=$(( (N+3)/4 ))
for k in 0 1 2 3; do python3 edit.py --frames $((k*C)) $(((k+1)*C)) --out output/parts/p$k.mp4 > output/parts/p$k.log 2>&1 & done; wait
printf "file 'parts/p%d.mp4'\n" 0 1 2 3 > output/list.txt
ffmpeg -y -v error -f concat -safe 0 -i output/list.txt -i audio/vault-b-v4-mix.wav -map 0:v -map 1:a -c:v libx264 -crf 19 -preset medium -pix_fmt yuv420p -c:a aac -b:a 256k -shortest -movflags +faststart output/vault-b-v4.mp4
ffmpeg -y -v error -i output/vault-b-v4.mp4 -c:v libx264 -profile:v main -level 4.0 -crf 24 -maxrate 2.5M -bufsize 5M -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart output/vault-b-v4-preview.mp4
echo RENDER_DONE
