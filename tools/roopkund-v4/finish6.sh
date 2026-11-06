#!/bin/bash
# finish V6: -1 dB audio headroom, mobile copy, contact sheet, copy to project files.  finish6.sh LANG
set -e
L=$1; W=/tmp/claude-0/rk/dub; F=/mnt/project-files/final-reels/skeleton-lake
N=skeleton-lake-v6-$L; [ $L = en ] && N=skeleton-lake-v6
ffmpeg -v error -y -i $W/v6-$L.mp4 -c:v copy -af volume=-1.2dB -c:a aac -b:a 192k -movflags +faststart $W/$N.mp4
ffmpeg -v error -y -i $W/$N.mp4 -c:v libx264 -crf 26 -preset medium -maxrate 4M -bufsize 8M -c:a aac -b:a 128k -movflags +faststart $W/${N}_mobile.mp4
ffmpeg -v error -y -i $W/$N.mp4 -vf "fps=1,scale=180:-1,tile=9x5" -frames:v 1 $W/${N}_contact.jpg
cp $W/$N.mp4 $W/${N}_mobile.mp4 $W/${N}_contact.jpg $F/
ffmpeg -i $F/$N.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):" | tail -2
echo $N copied
