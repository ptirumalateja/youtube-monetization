#!/bin/bash
cd "$(dirname "$0")"
mapfile -t W < wins3.txt
run(){ i=$1; set -- ${W[$i]}; rm -rf r3frames/w$i; ENGINE=engine_rama.html node render.js rama_map3.json r3frames/w$i 24 $1 $2 > r3log_w$i.txt 2>&1; ffmpeg -v error -y -framerate 24 -i r3frames/w$i/f%05d.jpg -c:v libx264 -crf 14 -pix_fmt yuv420p ../rama/src/map3_w$i.mp4; echo done w$i >> r3_done.txt; }
rm -f r3_done.txt
(run 3; run 0) & (run 6; run 2) & (run 1; run 4; run 5) & wait
echo ALLDONE >> r3_done.txt
