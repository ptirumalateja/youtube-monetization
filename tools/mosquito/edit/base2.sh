#!/bin/bash
# usage: base2.sh <segs dir> <out.mp4>  (silent picture edit, 31.7 s, 30 fps; 0.3 s cross-dissolve O->D, hard cuts elsewhere)
S=$1; O=$2
ffmpeg -v error -y -i $S/O.mp4 -i $S/D.mp4 -i $S/T.mp4 -i $S/H.mp4 -i $S/R.mp4 -i $S/M.mp4 \
 -filter_complex "[0:v][1:v]xfade=transition=fade:duration=0.3:offset=7.7[od];[od][2:v][3:v][4:v][5:v]concat=n=5:v=1:a=0,format=yuv420p[v]" \
 -map "[v]" -c:v libx264 -crf 14 -preset medium -r 30 $O
