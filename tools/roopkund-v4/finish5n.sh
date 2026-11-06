#!/bin/bash
# V5 visuals + 45 s natural hi/te VO: headroom, mobile, contact, copy.  finish5n.sh LANG
set -e
L=$1; W=/tmp/claude-0/rk/dub; F=/mnt/project-files/final-reels/skeleton-lake; N=skeleton-lake-v5-$L-45s
ffmpeg -v error -y -i $W/v5n-$L.mp4 -c:v copy -af "volume=-1.2dB,alimiter=limit=0.80:level=false" -c:a aac -b:a 192k -movflags +faststart $W/$N.mp4
ffmpeg -v error -y -i $W/$N.mp4 -c:v libx264 -crf 26 -preset medium -maxrate 4M -bufsize 8M -c:a aac -b:a 128k -movflags +faststart $W/${N}_mobile.mp4
ffmpeg -v error -y -i $W/$N.mp4 -vf "fps=1,scale=180:-1,tile=9x5" -frames:v 1 $W/${N}_contact.jpg
cp $W/$N.mp4 $W/${N}_mobile.mp4 $W/${N}_contact.jpg $F/
cp $W/srt/skeleton-lake-v5-$L.$L.srt $F/subtitles/$N.$L.srt
ffmpeg -i $F/$N.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+Peak:" | tail -1
echo $N copied
