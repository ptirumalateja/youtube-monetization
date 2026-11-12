#!/bin/bash
# Full render: room shot (3 workers) + owner's-day panel (1 worker), then meta for compose.
cd "$(dirname "$0")"
for w in 0 1 2; do OUT=output/dog SHOT=dog node render.cjs frames $w 3 > output/log_dog$w.txt 2>&1 & done
OUT=output/day SHOT=day H=960 F0=48 F1=150 node render.cjs frames 0 1 > output/log_day.txt 2>&1 &
wait
OUT=output/dog SHOT=dog node render.cjs meta
echo done
