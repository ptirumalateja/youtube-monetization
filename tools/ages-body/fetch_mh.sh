#!/bin/sh
# Download the CC0 MakeHuman base mesh + macro age targets into mh_src/ (needed by build_body.py).
set -e
cd "$(dirname "$0")"; mkdir -p mh_src
R=https://raw.githubusercontent.com/makehumancommunity/makehuman/master/makehuman/data
curl -sf -o mh_src/base.obj $R/3dobjs/base.obj
for r in african asian caucasian; do for g in male female; do for a in baby child young old; do
  curl -sf -o mh_src/$r-$g-$a.target $R/targets/macrodetails/$r-$g-$a.target
done; done; done
