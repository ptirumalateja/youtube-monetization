#!/bin/bash
# cut.sh OUTDIR BLADE GALAXY RING VORTEX  (Google Flow clips, 1080x1920 24 fps)
# Four 2.8 s beats with hard cuts: blade (hook) -> galaxy reveal -> ring -> vortex, loops to the blade.
O=$1; B=$2; G=$3; R=$4; V=$5
FONT=/usr/share/fonts/opentype/inter/InterDisplay-SemiBold.otf
D=2.8
seg() { echo "[$1:v]trim=start=$2:duration=$D,setpts=PTS-STARTPTS,fps=24,scale=1080:1920,setsar=1[$3]"; }
GRADE="eq=contrast=1.06:saturation=1.05:gamma=0.97,noise=alls=5:allf=t,format=yuv420p"
HOOK="drawtext=fontfile=$FONT:text='NOTHING ESCAPES THIS.':fontsize=70:fontcolor=0xF6ECD6:shadowcolor=black@0.7:shadowx=0:shadowy=3:x=(w-text_w)/2:y=1440:alpha='if(lt(t,0.25),t/0.25,if(lt(t,2.2),1,max(0,1-(t-2.2)/0.4)))'"
FC="$(seg 0 0.4 a);$(seg 1 0.0 b);$(seg 2 0.0 c);$(seg 3 4.2 d);[a][b][c][d]concat=n=4:v=1:a=0[cat]"
ffmpeg -hide_banner -loglevel error -y -i "$B" -i "$G" -i "$R" -i "$V" -filter_complex "$FC;[cat]$GRADE,split[v1][v2];[v1]$HOOK[txt]" \
  -map "[txt]" -c:v libx264 -preset slow -crf 14 -r 24 "$O/flow_text_v.mp4" -map "[v2]" -c:v libx264 -preset slow -crf 14 -r 24 "$O/flow_notext_v.mp4"
