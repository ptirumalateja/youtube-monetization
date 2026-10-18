#!/bin/bash
# usage: prep.sh <src dir with the Drive clips> <out dir>
# Cuts each chosen window, removes the Gemini sparkle, conforms to 1080x1920 / 30 fps, silent.
SRC=$1; OUT=$2; mkdir -p "$OUT"
DL="delogo=x=852:y=1692:w=96:h=96,delogo=x=904:y=1748:w=84:h=84"
seg(){ # name file ss dur [extra vf]
  ffmpeg -v error -y -ss "$3" -t "$4" -i "$SRC/$2" -an -vf "$DL,scale=1080:1920:flags=lanczos,fps=30${5:+,$5},format=yuv420p" -c:v libx264 -crf 14 -preset medium "$OUT/$1.mp4"; }
# A: hook (pull-back: digital zoom 1.3 -> 1.0 over the first second)
seg A glowburst133707.mp4 0.0 3.2 "scale=w='trunc(1080*(1.3-0.3*min(n/30,1))/2)*2':h=-2:eval=frame:flags=bicubic,crop=1080:1920"
seg B earthpulse.mp4 0.7 2.6
seg C caribou114933.mp4 0.5 3.5
seg D globe2.mp4 0.8 4.5 "delogo=x=940:y=1795:w=90:h=90"
seg E bird.mp4 0.0 2.5
seg F fish.mp4 4.8 2.5
seg G dissolve123713.mp4 0.8 3.6
seg H caribou131204.mp4 3.5 3.5
seg I sunrise.mp4 0.8 4.0
seg J landing.mp4 0.0 2.5
ls -la "$OUT" | awk '{print $5,$9}'
