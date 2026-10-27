#!/usr/bin/env bash
# parallel plate render, resumable (render.mjs skips existing PNGs)
cd "$(dirname "$0")"
O=$1; N=${2:-3}
for i in $(seq 0 $((N-1))); do python3 comp.py plates "$O" $i $N & done
wait
