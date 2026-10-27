#!/bin/bash
# render every recon shot, 4 at a time
cd "$(dirname "$0")"
ls shots/*.jsonl | xargs -P 4 -I{} sh -c 'n=$(basename {} .jsonl); [ -f clips/$n.mp4 ] || node render_recon.js {} clips/$n.mp4 > logs_$n.txt 2>&1'
echo done
