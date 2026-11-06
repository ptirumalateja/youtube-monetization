#!/bin/bash
# V6 (new visuals, <=45 s).  render6.sh LANG TEMPO   (LANG en | te | hi)
set -e
L=$1; TP=$2
W=/tmp/claude-0/rk/dub; R=/home/user/youtube-monetization; T=$R/tools/roopkund-v4; O=$W/v6_$L; mkdir -p $O
cd $W
if [ $L = en ]; then
  CM=""; VO=/tmp/claude-0/rk/vo_tight.wav
  DUR=$(python3 -c "print(round((34.85-31.9)/$TP,3))")
  python3 $T/mapflash.py /tmp/claude-0/rk/ne/land.geojson $O/map.mp4 $DUR
else
  CM=$W/cut2_$L.py; VO=$W/vo2_$L.wav
  if [ $L = te ]; then F=$T/fonts/NotoSansTelugu-ExtraBold.ttf; ROOP="రూప్‌కుండ్"; GC="గ్రీస్, క్రీట్"; KM="కి.మీ."; CS=76
  else F=$T/fonts/NotoSansDevanagari-ExtraBold.ttf; ROOP="रूपकुंड"; GC="ग्रीस और क्रीट"; KM="कि.मी."; CS=84; fi
  DUR=$(python3 -c "
import importlib.util as u;s=u.spec_from_file_location('c','$CM');m=u.module_from_spec(s);s.loader.exec_module(m);print(round((m.MAPT(34.85)-m.MAPT(31.9))/$TP,3))")
  MAP_FONT=$F MAP_ROOP="$ROOP" MAP_GC="$GC" MAP_KM="$KM" python3 $T/mapflash.py /tmp/claude-0/rk/ne/land.geojson $O/map.mp4 $DUR
fi
(cd $R && V6=1 CUTMOD=$CM MAP=$O/map.mp4 TEMPO=$TP python3 $T/build4.py media/roopkund-src $O | tail -1)
if [ $L = en ]; then
  TEMPO=$TP python3 $T/captions4.py $O/caps.ass
  TEMPO=$TP python3 $T/mix4.py $O/picture.mp4 $VO /tmp/claude-0/rk/sfx $O/caps.ass $W/v6-en.mp4
else
  CAPSIZE=$CS CUTMOD=$CM TEMPO=$TP python3 $T/capspng.py $F $O/caps
  CAPPNG=$O/caps/list.json CUTMOD=$CM TEMPO=$TP python3 $T/mix4.py $O/picture.mp4 $VO /tmp/claude-0/rk/sfx none $W/v6-$L.mp4
fi
rm -f $O/raw.mp4
echo $L done
