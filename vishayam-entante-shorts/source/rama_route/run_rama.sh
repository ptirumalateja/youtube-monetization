#!/bin/bash
cd "$(dirname "$0")"
W=("0 3.8" "5.85 11.9" "14.05 18.15" "22.15 29.15" "30.45 34.45" "39.05 42.75" "44.75 51.6")
run(){ i=$1; set -- ${W[$i]}; ENGINE=engine_rama.html node render.js rama_map.json rframes/w$i 24 $1 $2 > rlog_w$i.txt 2>&1; ffmpeg -v error -y -framerate 24 -i rframes/w$i/f%05d.jpg -c:v libx264 -crf 14 -pix_fmt yuv420p ../rama/src/map_w$i.mp4; echo done w$i >> rlog_done.txt; }
rm -f rlog_done.txt
(run 6; run 2; run 4) & (run 3; run 0) & (run 1; run 5) & wait
echo ALLDONE >> rlog_done.txt
