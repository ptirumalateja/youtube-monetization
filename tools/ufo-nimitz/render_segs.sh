#!/bin/bash
# render the edit in parallel segments: ./render_segs.sh "a b" "c d" ...
cd "$(dirname "$0")"
for seg in "$@"; do set -- $seg; python3 edit.py $1 $2 out/seg_$1_$2.mp4 > logs_edit_$1.txt 2>&1 & done; wait; echo segs done
