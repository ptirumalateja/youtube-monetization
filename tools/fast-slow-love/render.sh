#!/bin/bash
# render.sh <outdir> : 4 workers, frames 0..407 at 30 fps
OUT=$1; N=465; K=4; per=$(( (N + K - 1) / K ))
for w in $(seq 0 $((K-1))); do
  a=$((w*per)); b=$(( (w+1)*per - 1 )); [ $b -ge $N ] && b=$((N-1))
  ( node shoot.js $OUT/w$w $(python3 -c "print($a/30)") $(python3 -c "print($b/30)") 0.0333333333333 > $OUT/w$w.log 2>&1 ) &
done
wait
i=0; for w in $(seq 0 $((K-1))); do for f in $(ls $OUT/w$w/*.jpg | sort); do mv $f $OUT/$(printf "%04d" $i).jpg; i=$((i+1)); done; done
echo frames $i
