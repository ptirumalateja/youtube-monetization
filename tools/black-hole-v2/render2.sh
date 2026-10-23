#!/bin/bash
# render2.sh OUTDIR W H SS SHOT FIRST LAST   (frame f of a shot is at t = f/30 s)
OUT=$1; W=$2; H=$3; SS=$4; SH=$5; A=$6; B=$7
mkdir -p "$OUT"
cd "$(dirname "$0")"
gcc -O3 -march=native -ffast-math -fopenmp bh2.c -o bh2 -lm || exit 1
for f in $(seq $A $B); do
  name=$(printf "s%d_%04d" $SH $f)
  [ -f "$OUT/$name.png" ] && continue
  t=$(python3 -c "print($f/30)")
  ./bh2 $W $H $SS $t "$OUT/$name.raw" $SH 2>/dev/null && python3 post2.py "$OUT/$name.raw" "$OUT/$name.png" $W $H $((f + SH * 150)) 0.9 && rm "$OUT/$name.raw"
done
