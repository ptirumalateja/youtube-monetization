#!/bin/bash
# Renders every V4 frame (one continuous shot, index.html) into $1 with 4 workers. Server: python3 -m http.server 8779 in this folder.
OUT=$1; N=750
for w in 0 1 2 3; do SS=${SS:-1.25} node render.js ${RW:-1080} ${RH:-1920} $OUT $w $N 4 > $OUT.$w.log 2>&1 & done; wait
ls $OUT/*.jpg | wc -l
