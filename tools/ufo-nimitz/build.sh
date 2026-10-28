#!/bin/bash
# join the rendered segments and mux the mixed audio -> out/the-tic-tac-is-still-unidentified.mp4
cd "$(dirname "$0")"
SEGS="0_80 80_160 160_240 240_320 320_400 400_478.28"
: > out/segs.txt; for s in $SEGS; do echo "file 'seg_$s.mp4'" >> out/segs.txt; done
ffmpeg -v error -y -f concat -safe 0 -i out/segs.txt -i out/film_audio.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -ar 48000 -shortest -movflags +faststart out/the-tic-tac-is-still-unidentified.mp4
ffprobe -v error -show_entries format=duration,size -of csv=p=0 out/the-tic-tac-is-still-unidentified.mp4
