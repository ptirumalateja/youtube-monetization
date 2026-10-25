#!/bin/sh
# CC0 PBR sets from ambientCG (https://ambientcg.com, licence CC0 1.0): rusted iron, painted plaster, seabed ground, deck planks.
cd "$(dirname "$0")" && mkdir -p tex/_zip && cd tex/_zip || exit 1
for id in Metal021 Metal022 Metal055B PaintedPlaster007 Ground054 Planks037A; do
  curl -sSL -o ${id}_2K-JPG.zip "https://ambientcg.com/get?file=${id}_2K-JPG.zip" && mkdir -p ../$id && unzip -oq ${id}_2K-JPG.zip -d ../$id
done
