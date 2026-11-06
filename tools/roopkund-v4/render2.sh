#!/bin/bash
set -e
W=/tmp/claude-0/rk/dub; R=/home/user/youtube-monetization; T=$R/tools/roopkund-v4
cd $W
# Hindi: picture is fine, re-mix with PIL captions
CUTMOD=$W/cut_hi.py TEMPO=1.08 python3 $T/capspng.py $T/fonts/NotoSansDevanagari-ExtraBold.ttf $W/capspng_hi
CAPPNG=$W/capspng_hi/list.json CUTMOD=$W/cut_hi.py TEMPO=1.08 python3 $T/mix4.py $W/b_hi/picture.mp4 $W/vo_hi.wav /tmp/claude-0/rk/sfx none $W/v5-hi.mp4
echo hi mixed
# Telugu: new map label, full rebuild
DUR=$(python3 -c "
import importlib.util as u;s=u.spec_from_file_location('c','$W/cut_te.py');m=u.module_from_spec(s);s.loader.exec_module(m);print(round((m.MAPT(34.85)-m.MAPT(31.9))/1.08,3))")
MAP_FONT=$T/fonts/NotoSansTelugu-ExtraBold.ttf MAP_ROOP="రూప్‌కుండ్" MAP_GC="గ్రీస్, క్రీట్" MAP_KM="కి.మీ." python3 $T/mapflash.py /tmp/claude-0/rk/ne/land.geojson $W/map_te.mp4 $DUR
cd $R && CUTMOD=$W/cut_te.py MAP=$W/map_te.mp4 TEMPO=1.08 python3 $T/build4.py media/roopkund-src $W/b_te | tail -1
CAPSIZE=76 CUTMOD=$W/cut_te.py TEMPO=1.08 python3 $T/capspng.py $T/fonts/NotoSansTelugu-ExtraBold.ttf $W/capspng_te
CAPPNG=$W/capspng_te/list.json CUTMOD=$W/cut_te.py TEMPO=1.08 python3 $T/mix4.py $W/b_te/picture.mp4 $W/vo_te.wav /tmp/claude-0/rk/sfx none $W/v5-te.mp4
rm -f $W/b_te/s*.mp4 $W/b_te/raw.mp4
echo te done
