#!/usr/bin/env bash
# Point a HyperFrames project at a local gsap copy (cdn.jsdelivr.net is blocked in the cloud).
set -e; dir=${1:-.}; cd "$dir"
[ -f gsap.min.js ] || { npm i -q --no-save gsap@3.15.0 && cp node_modules/gsap/dist/gsap.min.js .; }
sed -i.bak 's#https://cdn.jsdelivr.net/npm/gsap@[0-9.]*/dist/gsap.min.js#gsap.min.js#' *.html && rm -f *.html.bak
echo "gsap now local in $dir"
