#!/bin/zsh
# mux.sh <base.mp4> <mix_raw.wav> <out.mp4>: two-pass loudnorm to about -15 LUFS, AAC, then report loudness/true peak AFTER encoding.
set -e
B=$1; A=$2; O=$3
J=$(ffmpeg -hide_banner -nostats -i $A -af loudnorm=I=-15:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
mi=$(echo $J | grep input_i | grep -oE '[-0-9.]+'); mtp=$(echo $J | grep input_tp | grep -oE '[-0-9.]+'); mlra=$(echo $J | grep input_lra | grep -oE '[-0-9.]+'); mth=$(echo $J | grep input_thresh | grep -oE '[-0-9.]+'); off=$(echo $J | grep target_offset | grep -oE '[-0-9.]+')
ffmpeg -y -hide_banner -loglevel error -i $B -i $A -map 0:v -map 1:a -c:v copy -af "loudnorm=I=-15:TP=-1.5:LRA=11:measured_I=${mi}:measured_TP=${mtp}:measured_LRA=${mlra}:measured_thresh=${mth}:offset=${off}:linear=true,aresample=48000" -c:a aac -b:a 192k -shortest -movflags +faststart $O
ffmpeg -hide_banner -nostats -i $O -map 0:a -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
