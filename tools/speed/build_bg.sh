#!/bin/bash
# Builds the Speed Ladder background timeline (432 frames, 30 fps) from the seven Google Flow clips (stop1_jet ... stop7_twist, 1080x1920, 24 fps, 4 s each).
# usage: build_bg.sh <dir with the Flow clips> ; writes <dir>/bgtl2.mp4. Windows are cut on the beat grid; the bottom of the frame is faded to black in render12.py.
cd "$1"; DL="scale=1080:1920:flags=lanczos,fps=30,format=yuv420p"
seg(){ ffmpeg -v error -y -ss $2 -i $1.mp4 -an -vf "$DL" -frames:v $3 -c:v libx264 -crf 12 -preset medium s_$4.mp4; }
seg stop1_jet 1.0 27 1; seg stop2_bullet 1.0 27 2; seg stop3_earth 0.8 54 3; seg stop4_parker 1.0 54 4; seg stop5_light 0.0 68 6; seg stop6_laps 0.5 81 7; seg stop7_twist 0.3 108 8
ffmpeg -v error -y -f lavfi -i "color=c=black:s=1080x1920:r=30,format=yuv420p" -frames:v 13 -c:v libx264 -crf 12 s_5.mp4
printf "file 's_%s.mp4'\n" 1 2 3 4 5 6 7 8 > list2.txt
ffmpeg -v error -y -f concat -safe 0 -i list2.txt -c:v libx264 -crf 12 -preset medium -r 30 bgtl2.mp4
