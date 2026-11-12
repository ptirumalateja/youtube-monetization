#!/bin/bash
# Full render (4 workers, ~25-35 min on 4 CPUs) + meta for compose/mix. Re-running skips finished frames.
cd "$(dirname "$0")"
for w in 0 1 2 3; do OUT=output/full node render.cjs frames $w 4 > output/full/log$w.txt 2>&1 & done
wait
OUT=output/full node render.cjs meta
echo done
