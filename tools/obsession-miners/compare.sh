#!/bin/bash
# compare.sh <ref.mp4> <stilldir> <out.jpg> t1 t2 ... : ref | ours pairs, 4 pairs per row
REF=$1; D=$2; OUT=$3; shift 3
TMP=$(mktemp -d); i=0
for t in "$@"; do
  tt=$(printf "%.2f" $t)
  ffmpeg -v error -y -ss $t -i "$REF" -frames:v 1 -vf "scale=270:480,drawtext=text='REF $tt':x=4:y=4:fontsize=18:fontcolor=yellow:box=1:boxcolor=black" $TMP/r.png
  ffmpeg -v error -y -i "$D/t$tt.png" -vf "scale=270:480,drawtext=text='OURS':x=4:y=4:fontsize=18:fontcolor=cyan:box=1:boxcolor=black" $TMP/o.png
  ffmpeg -v error -y -i $TMP/r.png -i $TMP/o.png -filter_complex "hstack,pad=iw+10:ih:0:0:white" $TMP/p$(printf %03d $i).png
  i=$((i+1))
done
ffmpeg -v error -y -i $TMP/p%03d.png -vf "tile=4x$(( (i+3)/4 ))" -frames:v 1 "$OUT"
rm -rf $TMP
