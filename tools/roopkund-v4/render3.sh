#!/bin/bash
# v2 natural-script dubs, ~45 s.  render3.sh LANG TEMPO
set -e
L=$1; TP=$2
W=/tmp/claude-0/rk/dub; R=/home/user/youtube-monetization; T=$R/tools/roopkund-v4
if [ $L = te ]; then F=$T/fonts/NotoSansTelugu-ExtraBold.ttf; ROOP="రూప్‌కుండ్"; GC="గ్రీస్, క్రీట్"; KM="కి.మీ."; CS=76
else F=$T/fonts/NotoSansDevanagari-ExtraBold.ttf; ROOP="रूपकुंड"; GC="ग्रीस और क्रीट"; KM="कि.मी."; CS=84; fi
cd $W
DUR=$(python3 -c "
import importlib.util as u;s=u.spec_from_file_location('c','$W/cut2_$L.py');m=u.module_from_spec(s);s.loader.exec_module(m);print(round((m.MAPT(34.85)-m.MAPT(31.9))/$TP,3))")
MAP_FONT=$F MAP_ROOP="$ROOP" MAP_GC="$GC" MAP_KM="$KM" python3 $T/mapflash.py /tmp/claude-0/rk/ne/land.geojson $W/map2_$L.mp4 $DUR
(cd $R && LAB=1 CUTMOD=$W/cut2_$L.py MAP=$W/map2_$L.mp4 TEMPO=$TP python3 $T/build4.py media/roopkund-src $W/b2_$L | tail -1)
CAPSIZE=$CS CUTMOD=$W/cut2_$L.py TEMPO=$TP python3 $T/capspng.py $F $W/caps2_$L
CAPPNG=$W/caps2_$L/list.json CUTMOD=$W/cut2_$L.py TEMPO=$TP python3 $T/mix4.py $W/b2_$L/picture.mp4 $W/vo2_$L.wav /tmp/claude-0/rk/sfx none $W/v5n-$L.mp4
rm -f $W/b2_$L/s*.mp4 $W/b2_$L/raw.mp4
echo $L done
