#!/bin/bash
# usage: base.sh <segs dir> <out.mp4>   (silent picture edit, 32.3 s, 30 fps; B->C crossfade 0.5 s, 0.4 s black before D)
S=$1; O=$2
ffmpeg -v error -y -i $S/A.mp4 -i $S/B.mp4 -i $S/C.mp4 -f lavfi -t 0.4 -i "color=c=black:s=1080x1920:r=30,format=yuv420p" -i $S/D.mp4 -i $S/E.mp4 -i $S/F.mp4 -i $S/G.mp4 -i $S/H.mp4 -i $S/I.mp4 -i $S/J.mp4 \
 -filter_complex "[1:v][2:v]xfade=transition=fade:duration=0.5:offset=2.1[bc];[0:v][bc][3:v][4:v][5:v][6:v][7:v][8:v][9:v][10:v]concat=n=10:v=1:a=0,format=yuv420p[v]" \
 -map "[v]" -c:v libx264 -crf 14 -preset medium -r 30 $O
