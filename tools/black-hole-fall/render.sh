#!/bin/bash
# render.sh OUTDIR W H SS FIRST LAST  (frame indices; frame f is at t = f/30 s, negatives are the loop pre-roll)
OUT=$1; W=$2; H=$3; SS=$4; A=$5; B=$6
mkdir -p "$OUT"
cd "$(dirname "$0")"
for f in $(seq $A $B); do
  name=$(printf "f%05d" $((f + 100)))
  [ -f "$OUT/$name.png" ] && continue
  t=$(python3 -c "print($f/30)")
  ./bh $W $H $SS $t "$OUT/$name.raw" 2>/dev/null && python3 post.py "$OUT/$name.raw" "$OUT/$name.png" $W $H $f 0.8 && rm "$OUT/$name.raw"
done
