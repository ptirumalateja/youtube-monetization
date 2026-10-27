#!/usr/bin/env bash
# parallel plate render + composite, resumable (render.mjs and do_frame skip existing PNGs)
cd "$(dirname "$0")"
O=$1; N=${2:-3}
for i in $(seq 0 $((N-1))); do python3 comp.py plates "$O" $i $N & done
wait
for i in $(seq 0 $((N-1))); do python3 comp.py frames "$O" $i $N & done
wait
python3 comp.py events "$O"
