#!/bin/bash
# parallel render in 4 chunks, concat, mux with the mix, make a light preview copy
cd "$(dirname "$0")"; mkdir -p output/parts
N=$(python3 -c "import edit; print(int(edit.DUR*edit.FPS))"); C=$(( (N+3)/4 ))
for k in 0 1 2 3; do python3 edit.py --frames $((k*C)) $(((k+1)*C)) --out output/parts/p$k.mp4 > output/parts/p$k.log 2>&1 & done; wait
printf "file 'parts/p%d.mp4'\n" 0 1 2 3 > output/list.txt
ffmpeg -y -v error -f concat -safe 0 -i output/list.txt -i audio/vault-b-v3-mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest -movflags +faststart output/vault-b-v3.mp4
ffmpeg -y -v error -i output/vault-b-v3.mp4 -c:v libx264 -profile:v main -level 4.0 -crf 21 -maxrate 8M -bufsize 16M -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart output/vault-b-v3-preview.mp4
echo RENDER_DONE
