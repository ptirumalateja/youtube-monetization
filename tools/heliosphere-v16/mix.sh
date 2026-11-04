#!/usr/bin/env bash
# Heliosphere v16 sound: recorded/library hits from tools/sfxlib (credits in /audio-attribution.md), wind bed, no music. -> mix.wav (23 s)
set -euo pipefail
L=../sfxlib; OUT=${1:-mix.wav}
ffmpeg -y -v error \
 -i $L/722633__chakong__cinematic-braaam.wav -i $L/649445__audiopapkin__cinematic-woosh-sfx-015.wav -i $L/752034__bachsambora__sci-fi-gateway.wav \
 -i $L/735062__gammagool__fast-warp-in.wav -i $L/238375__stewdio2003__cp_subby_whoosh.aiff -i $L/869757__mikiko850__dark-suspense-accent.wav \
 -i $L/849772__mikiko850__electric-sparks.wav -i $L/814046__qubodup__explosion-from-another-dimension.wav -i $L/850262__cvltiv8r__orbiting-plasma-burst-and-trail-fx.wav \
 -i $L/19487__halleck__jacobsladdersingle2.flac -i $L/822420__audiopapkin__riser-hit-sfx-120.wav -i $L/814047__qubodup__fantasy-implosion.wav -i $L/22331__sleepcircle__wind.ogg \
 -filter_complex "
[0]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[b0][b1];
[b0]atrim=0.2,asetpts=N/SR/TB,volume=0.95[hit0];
[b1]atrim=0.6,asetpts=N/SR/TB,atrim=0:2.5,afade=t=out:st=1.6:d=0.9,volume=0.55,adelay=14650|14650[hitX];
[1]aformat=sample_rates=48000:channel_layouts=stereo,asplit=3[w0][w1][w2];
[w0]atrim=0.9,asetpts=N/SR/TB,volume=0.7[rip];
[w1]volume=0.55,adelay=5500|5500[zin];
[w2]volume=0.6,adelay=19000|19000[dive];
[2]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.35,adelay=2700|2700[l1];
[3]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.6,adelay=3200|3200[warp];
[4]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.7,adelay=3400|3400[sub];
[5]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:3.4,afade=t=out:st=2.6:d=0.8,volume=0.55,adelay=4300|4300[susp];
[6]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:3.0,afade=t=in:d=0.4,afade=t=out:st=2.4:d=0.6,volume=0.32,adelay=8300|8300[spark];
[7]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.95,adelay=11250|11250[boom];
[8]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:3.6,afade=t=out:st=2.8:d=0.8,volume=0.42,adelay=12300|12300[plasma];
[9]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.5,adelay=13600|13600[zap];
[10]aformat=sample_rates=48000:channel_layouts=stereo,atrim=5.0,asetpts=N/SR/TB,atrim=0:3.5,afade=t=out:st=2.5:d=1.0,volume=0.75,adelay=15350|15350[rhit];
[11]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:3.5,afade=t=out:st=2.6:d=0.9,volume=0.7,adelay=18300|18300[imp];
[12]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:23,afade=t=in:d=0.3,volume='if(between(t,11.15,11.5),0.02,if(between(t,15.0,16.4),0.35,1.0))':eval=frame,volume=1.1[bed];
[hit0][rip][zin][dive][l1][warp][sub][susp][spark][boom][plasma][zap][hitX][rhit][imp][bed]amix=inputs=16:normalize=0:duration=longest,
volume='if(between(t,11.18,11.24),0.15,1)':eval=frame,atrim=0:23,highpass=f=35,equalizer=f=2200:t=q:w=1.2:g=3,afade=t=out:st=22.6:d=0.4,loudnorm=I=-14:TP=-1.5:LRA=11,volume=1.6dB,alimiter=limit=0.80:level=false,aresample=48000[o]" \
 -map "[o]" -ar 48000 "$OUT"
echo wrote $OUT
