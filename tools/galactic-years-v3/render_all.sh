#!/bin/bash
# Renders every V3 frame: galaxy shots (index.html) then the cutaways (scenes.html), 4 workers each, into $1.
OUT=$1; N=780
for PG in index.html scenes.html; do
  for w in 0 1 2 3; do PAGE=$PG SS=${SS:-1.25} node render.js ${RW:-1080} ${RH:-1920} $OUT $w $N 4 > $OUT.$PG.$w.log 2>&1 & done; wait
done
ls $OUT/*.jpg | wc -l
