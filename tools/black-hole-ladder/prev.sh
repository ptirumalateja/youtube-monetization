#!/bin/bash
# fast preview: all frames at 1/3 rate, low res, 2 workers
cd "$(dirname "$0")"; OUT=$1; rm -rf $OUT; mkdir -p $OUT
./with_server.sh 8767 bash -c "node render.js 270 480 $OUT 0 846 6 1 & node render.js 270 480 $OUT 3 846 6 1 & wait"
