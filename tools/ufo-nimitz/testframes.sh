#!/bin/bash
# render one frame at each time in out/tt.txt and tile them into out/tf/sheet.png (4 at a time)
cd "$(dirname "$0")"
mkdir -p out/tf && rm -f out/tf/*
i=0
for t in $(cat out/tt.txt); do
  i=$((i+1)); n=$(printf %02d $i)
  ( python3 edit.py $t $(python3 -c "print($t+0.04)") out/tf/f$n.mp4 > out/tf/e$n.txt 2>&1
    ffmpeg -nostdin -v error -y -i out/tf/f$n.mp4 -frames:v 1 -vf scale=640:-1 out/tf/f$n.png ) &
  if (( i % 4 == 0 )); then wait; fi
done
wait
grep -h -v "^ *[0-9.]*s$" out/tf/e*.txt | head
python3 -c "
from PIL import Image;import glob
fs=sorted(glob.glob('out/tf/f*.png'));W=Image.new('RGB',(640*3,360*((len(fs)+2)//3)))
for i,f in enumerate(fs): W.paste(Image.open(f),(640*(i%3),360*(i//3)))
W.save('out/tf/sheet.png')"
