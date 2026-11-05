#!/bin/bash
# Render Vault B blocks 3+4 (10-20 s) at full quality; resumable (skips existing frames).
cd "$(dirname "$0")/cycles"
O=../output/anim
for spec in lamp:36 heads:42 seam:42 hand:42 eyes:78; do
  s=${spec%%:*}; n=${spec##*:}
  ANIM=0,$n,$n python3 door.py $O/$s 720 1280 20 $s >> $O/$s.log 2>&1
done
echo ALLDONE >> $O/b34.done
