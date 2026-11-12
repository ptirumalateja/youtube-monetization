#!/bin/bash
# Re-render only dog-shot frame ranges (FORCE overwrite), 3 workers each, then meta.
cd "$(dirname "$0")"
for r in "$@"; do F0=${r%-*}; F1=${r#*-}
  for w in 0 1 2; do FORCE=1 F0=$F0 F1=$F1 OUT=output/dog SHOT=dog node render.cjs frames $w 3 > output/log_r${F0}_$w.txt 2>&1 & done; wait
done
OUT=output/dog SHOT=dog node render.cjs meta; echo done
