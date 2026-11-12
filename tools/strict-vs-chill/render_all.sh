#!/bin/bash
# v2 renders: wide panels (top=strict, bot=chill) + tight cold-open of the strict payoff (hook, t 6.05-8.70)
set -e; cd "$(dirname "$0")"
for k in top bot; do P=0; [ $k = bot ] && P=1
  OUT=output/$k W=1080 H=558 PANEL=$P node render.cjs meta
  for w in 0 1 2 3; do OUT=output/$k W=1080 H=558 PANEL=$P node render.cjs frames $w 4 & done; wait; done
HOOKCAM=-0.5,1.7,8.6,-0.5,1.4,0,24
OUT=output/hook W=1080 H=1320 PANEL=0 CAM=$HOOKCAM node render.cjs meta
for w in 0 1 2 3; do OUT=output/hook W=1080 H=1320 PANEL=0 CAM=$HOOKCAM T0=6.05 T1=8.75 node render.cjs frames $w 4 & done; wait
echo ALLDONE
