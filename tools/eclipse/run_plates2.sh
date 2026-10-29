#!/bin/sh
# usage: run_plates2.sh OUT [scale]   (helium cut)
O=$1; S=${2:-1}; cd "$(dirname "$0")"; mkdir -p "$O"
for k in 0 1 2; do python3 comp2.py plates "$O" "$S" $k 3 > "$O/plates$k.log" 2>&1 & done; wait
for k in 0 1 2 3; do python3 comp2.py frames "$O" "$S" $k 4 & done; wait
python3 comp2.py video "$O"
