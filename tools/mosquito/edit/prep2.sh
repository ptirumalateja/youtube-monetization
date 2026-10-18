#!/bin/bash
# v2 (anime look). usage: prep2.sh <dir with anime clips + globe2.mp4> <out dir>
# Cuts each chosen window, removes the Gemini sparkle (bottom right, same spot on every anime clip), conforms to 1080x1920 / 30 fps, silent.
SRC=$1; OUT=$2; mkdir -p "$OUT"
DL="delogo=x=855:y=1695:w=90:h=90"
DLG="delogo=x=852:y=1692:w=96:h=96,delogo=x=904:y=1748:w=84:h=84,delogo=x=940:y=1795:w=90:h=90"   # globe2 clip had a second sparkle position
seg(){ # name file ss dur filter
  ffmpeg -v error -y -ss "$3" -t "$4" -i "$SRC/$2" -an -vf "$5,scale=1080:1920:flags=lanczos,fps=30,format=yuv420p" -c:v libx264 -crf 14 -preset medium "$OUT/$1.mp4"; }
seg O open.mp4    0.0 8.0 "$DL"      # hook: swarm vanishes, clouds, Earth with aura
seg D globe2.mp4  0.8 4.2 "$DLG"     # malaria globe (Africa red)
seg T tundra.mp4  1.0 5.5 "$DL"      # arctic calm, then ten years on
seg H heron2.mp4  0.4 3.2 "$DL"      # heron strikes, finds nothing
seg R orchid.mp4  3.6 3.8 "$DL"      # orchid, mosquito dissolves
seg M meadow.mp4  0.2 7.3 "$DL"      # Earth sunrise, descent, one mosquito (loop)
ls -la "$OUT" | awk '{print $5,$9}'
