#!/bin/sh
# renders frames 168..719 of the reel in chunks (resumable: existing frames are skipped), W H outdir
cd "$(dirname "$0")"; W=${1:-720}; H=${2:-1280}; OUT=$3
for a in 168 258 348 438 528 618; do b=$((a+90)); [ $b -gt 720 ] && b=720; SKIP=1 SUB=3 node render.js $W $H $OUT $a $b >> $OUT/render_full.log 2>&1; done
echo ALLDONE >> $OUT/render_full.log
