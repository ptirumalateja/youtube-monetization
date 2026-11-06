#!/bin/bash
set -e
L=$1; W=/tmp/claude-0/rk/dub; R=/home/user/youtube-monetization; T=$R/tools/roopkund-v4
if [ $L = hi ]; then F="Noto Sans Devanagari ExtraBold"; MF=$T/fonts/NotoSansDevanagari-ExtraBold.ttf; ROOP="रूपकुंड"; GC="ग्रीस और क्रीट"; KM="कि.मी."; fi
if [ $L = te ]; then F="Noto Sans Telugu ExtraBold"; MF=$T/fonts/NotoSansTelugu-ExtraBold.ttf; ROOP="రూప్‌కుండ్"; GC="గ్రీస్, క్రీట్"; KM="కి.మీ."; fi
DUR=$(python3 -c "
import sys;sys.path.insert(0,'$W');import importlib.util as u;s=u.spec_from_file_location('c','$W/cut_$L.py');m=u.module_from_spec(s);s.loader.exec_module(m);print(round((m.MAPT(34.85)-m.MAPT(31.9))/1.08,3))")
cd $W && MAP_FONT=$MF MAP_ROOP="$ROOP" MAP_GC="$GC" MAP_KM="$KM" python3 $T/mapflash.py /tmp/claude-0/rk/ne/land.geojson $W/map_$L.mp4 $DUR
cd $R && CUTMOD=$W/cut_$L.py MAP=$W/map_$L.mp4 TEMPO=1.08 python3 $T/build4.py media/roopkund-src $W/b_$L | tail -1
CUTMOD=$W/cut_$L.py TEMPO=1.08 FONT="$F" python3 $T/captions4.py $W/caps_$L.ass
CUTMOD=$W/cut_$L.py TEMPO=1.08 python3 $T/mix4.py $W/b_$L/picture.mp4 $W/vo_$L.wav /tmp/claude-0/rk/sfx $W/caps_$L.ass $W/v5-$L.mp4
rm -f $W/b_$L/s*.mp4 $W/b_$L/raw.mp4
echo done $L
