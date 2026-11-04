#!/usr/bin/env bash
# Heliosphere v18 sound, 0-13 s: library hits from tools/sfxlib cut to the picture (credits in /audio-attribution.md). No music.
# Hook: 0.1 braam on frame 0 | 1.8 woosh as the camera lifts past the Sun | 2.55 riser-hit + deep boom + shimmer as the Sun's bubble lands
#       3.4 swish on the caption change | 5.05 subby whoosh on the speed line | wind, sparks, plasma, jet texture
# Block 2: 6.6 warp + 7.0 whoosh out to the galaxy | 7.3 gateway swell on the spiral | 8.8 woosh back into the bubble + swish on the caption
#       8.8-10.6 sparks for the solar wind | 10.5 boom + zap + plasma as the cosmic rays hit, crackle to 13 s
set -euo pipefail
L=../sfxlib; OUT=${1:-output/hook.wav}; D=${DUR:-13}
ffmpeg -y -v error \
 -i $L/722633__chakong__cinematic-braaam.wav -i $L/649445__audiopapkin__cinematic-woosh-sfx-015.wav -i $L/822420__audiopapkin__riser-hit-sfx-120.wav \
 -i $L/814046__qubodup__explosion-from-another-dimension.wav -i $L/768664__berkup__portal-gate-opening.wav -i $L/276871__lucabia__sword-in-air.wav \
 -i $L/238375__stewdio2003__cp_subby_whoosh.aiff -i $L/115555__vartioh__synth_jet.wav -i $L/849772__mikiko850__electric-sparks.wav \
 -i $L/850262__cvltiv8r__orbiting-plasma-burst-and-trail-fx.wav -i $L/22331__sleepcircle__wind.ogg -i $L/735062__gammagool__fast-warp-in.wav \
 -i $L/752034__bachsambora__sci-fi-gateway.wav -i $L/19487__halleck__jacobsladdersingle2.flac \
 -filter_complex "
[0]aformat=sample_rates=48000:channel_layouts=stereo,atrim=1.95,asetpts=N/SR/TB,atrim=0:2.6,afade=t=out:st=1.6:d=1.0,volume=0.95[braam];
[1]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[w1a][w1b];
[w1a]atrim=0.74,asetpts=N/SR/TB,volume=0.8[woosh];
[w1b]volume=0.7,adelay=6280|6280[woosh2];
[2]aformat=sample_rates=48000:channel_layouts=stereo,atrim=3.65,asetpts=N/SR/TB,atrim=0:4.6,afade=t=in:d=1.2,afade=t=out:st=3.6:d=1.0,volume=0.85[rhit];
[3]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[x1][x2];
[x1]atrim=0:3.5,afade=t=out:st=2.4:d=1.1,volume=0.75,adelay=2200|2200[boom];
[x2]atrim=0:3.0,afade=t=out:st=2.0:d=1.0,volume=0.55,adelay=10150|10150[boom2];
[4]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:3.0,afade=t=out:st=2.0:d=1.0,volume=0.35,adelay=1150|1150[shim];
[5]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[s1][s2];
[s1]volume=0.45,adelay=1370|1370[swish];
[s2]volume=0.4,adelay=6850|6850[swish2];
[6]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[u1][u2];
[u1]volume=0.65,adelay=3540|3540[sub];
[u2]volume=0.6,adelay=5490|5490[sub2];
[7]aformat=sample_rates=48000:channel_layouts=stereo,atrim=1.2,asetpts=N/SR/TB,atrim=0:3.6,afade=t=in:d=1.0,afade=t=out:st=2.8:d=0.8,volume=0.28,adelay=3300|3300[jet];
[8]aformat=sample_rates=48000:channel_layouts=stereo,asplit=3[p1][p2][p3];
[p1]atrim=0:3.7,afade=t=in:d=0.5,afade=t=out:st=3.2:d=0.5,volume=0.3,adelay=2800|2800[spark];
[p2]atrim=0:1.9,afade=t=in:d=0.3,afade=t=out:st=1.4:d=0.5,volume=0.38,adelay=8800|8800[spark2];
[p3]atrim=1.0,asetpts=N/SR/TB,atrim=0:2.6,afade=t=in:d=0.2,afade=t=out:st=2.3:d=0.3,volume=0.45,adelay=10450|10450[spark3];
[9]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[q1][q2];
[q1]atrim=0:2.3,afade=t=out:st=1.6:d=0.7,volume=0.38,adelay=4200|4200[plasma];
[q2]atrim=0:2.5,afade=t=out:st=1.8:d=0.7,volume=0.4,adelay=10600|10600[plasma2];
[10]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:$D,afade=t=in:d=0.2,volume='if(between(t,6.9,8.1),0.55,1)':eval=frame[bed];
[11]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.6,adelay=6450|6450[warp];
[12]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.45,adelay=7300|7300[gate];
[13]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.5,adelay=10500|10500[zap];
[braam][woosh][woosh2][rhit][boom][boom2][shim][swish][swish2][sub][sub2][jet][spark][spark2][spark3][plasma][plasma2][bed][warp][gate][zap]amix=inputs=21:normalize=0:duration=longest,
atrim=0:$D,highpass=f=35,equalizer=f=2200:t=q:w=1.2:g=3,extrastereo=m=0.55,afade=t=out:st=$(echo "$D-0.2"|bc):d=0.2,loudnorm=I=-14:TP=-1.5:LRA=11,volume=1.6dB,alimiter=limit=0.80:level=false,aresample=48000[o]" \
 -map "[o]" -ar 48000 "$OUT"
echo wrote $OUT
