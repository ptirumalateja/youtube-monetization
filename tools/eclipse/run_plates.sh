#!/bin/sh
# usage: run_plates.sh OUT [scale]
O=$1; S=${2:-1}; cd "$(dirname "$0")"
for k in 0 1 2; do python3 comp.py plates "$O" "$S" $k 3 > "$O/plates$k.log" 2>&1 & done; wait
for k in 0 1 2 3; do python3 comp.py frames "$O" "$S" $k 4 & done; wait
python3 comp.py video "$O"
