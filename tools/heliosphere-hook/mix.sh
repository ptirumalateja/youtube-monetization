#!/usr/bin/env bash
# Heliosphere v18 sound, 0-13 s: library hits from tools/sfxlib cut to the picture (credits in /audio-attribution.md). No music.
# Hook: 0.1 braam on frame 0 | 1.8 woosh as the camera lifts past the Sun | 2.55 riser-hit + deep boom + shimmer as the Sun's bubble lands
#       3.4 swish on the caption change | 5.05 subby whoosh on the speed line | wind, sparks, plasma, jet texture
# Block 3: 13.15 braam + dark accent on ONLY 2 MACHINES (bed dips to near silence just before) | 13.55 woosh on the dive to Voyager | 14.6 jet + riser into the wall
#       16.75 bed drops, reversed implosion sucks in, 17.0 boom + zap + sparks + plasma as Voyager 1 crosses
# Block 4: 19.15 swell + 19.3 swish rising out to the bubble | 21.9 swish, dip, 22.55 dark accent on WOULD YOU GO? | 22.5 riser, 23.8 woosh + warp + implosion on the dive home into frame 0 (loops into the 0.1 braam)
# Block 2: 6.45 warp + 7.0 whoosh out to the galaxy | 7.3 gateway swell + jet as the bubble sweeps its orbit | 7.8 braam on Sgr A*
#       10.0 woosh back into the bubble + swish on the wind line, 10.5 portal swell as it inflates | 10.25 boom, 10.65 zap, 10.7 plasma, crackle to 13 s on the cosmic rays
set -euo pipefail
L=../sfxlib; OUT=${1:-output/hook.wav}; D=${DUR:-25}
ffmpeg -y -v error \
 -i $L/722633__chakong__cinematic-braaam.wav -i $L/649445__audiopapkin__cinematic-woosh-sfx-015.wav -i $L/822420__audiopapkin__riser-hit-sfx-120.wav \
 -i $L/814046__qubodup__explosion-from-another-dimension.wav -i $L/768664__berkup__portal-gate-opening.wav -i $L/276871__lucabia__sword-in-air.wav \
 -i $L/238375__stewdio2003__cp_subby_whoosh.aiff -i $L/115555__vartioh__synth_jet.wav -i $L/849772__mikiko850__electric-sparks.wav \
 -i $L/850262__cvltiv8r__orbiting-plasma-burst-and-trail-fx.wav -i $L/22331__sleepcircle__wind.ogg -i $L/735062__gammagool__fast-warp-in.wav \
 -i $L/752034__bachsambora__sci-fi-gateway.wav -i $L/19487__halleck__jacobsladdersingle2.flac \
 -i $L/869757__mikiko850__dark-suspense-accent.wav -i $L/814047__qubodup__fantasy-implosion.wav \
 -filter_complex "
[0]aformat=sample_rates=48000:channel_layouts=stereo,asplit=3[br1][br2][br3];
[br3]atrim=1.95,asetpts=N/SR/TB,atrim=0:2.8,afade=t=out:st=1.8:d=1.0,volume=0.85,adelay=13150|13150[rehook];
[br1]atrim=1.95,asetpts=N/SR/TB,atrim=0:2.6,afade=t=out:st=1.6:d=1.0,volume=0.95[braam];
[br2]atrim=1.95,asetpts=N/SR/TB,atrim=0:2.4,afade=t=out:st=1.4:d=1.0,volume=0.55,adelay=7800|7800[sgra];
[1]aformat=sample_rates=48000:channel_layouts=stereo,asplit=4[w1a][w1b][w1c][w1d];
[w1d]volume=0.8,adelay=23780|23780[dive2];
[w1c]volume=0.75,adelay=13550|13550[dive];
[w1a]atrim=0.74,asetpts=N/SR/TB,volume=0.8[woosh];
[w1b]volume=0.7,adelay=7480|7480[woosh2];
[2]aformat=sample_rates=48000:channel_layouts=stereo,asplit=3[rh1][rh2][rh3];
[rh3]atrim=3.65,asetpts=N/SR/TB,atrim=0:2.5,afade=t=in:d=1.2,afade=t=out:st=2.35:d=0.15,volume=0.8,adelay=22500|22500[rise3];
[rh1]atrim=3.65,asetpts=N/SR/TB,atrim=0:4.6,afade=t=in:d=1.2,afade=t=out:st=3.6:d=1.0,volume=0.85[rhit];
[rh2]atrim=3.65,asetpts=N/SR/TB,atrim=0:4.2,afade=t=in:d=1.4,afade=t=out:st=3.2:d=1.0,volume=0.8,adelay=14450|14450[rhit2];
[3]aformat=sample_rates=48000:channel_layouts=stereo,asplit=3[x1][x2][x3];
[x3]atrim=0:2.0,afade=t=out:st=1.2:d=0.8,volume=0.8,adelay=17000|17000[boom3];
[x1]atrim=0:3.5,afade=t=out:st=2.4:d=1.1,volume=0.75,adelay=2200|2200[boom];
[x2]atrim=0:3.0,afade=t=out:st=2.0:d=1.0,volume=0.55,adelay=10250|10250[boom2];
[4]aformat=sample_rates=48000:channel_layouts=stereo,asplit=3[g1][g2][g3];
[g3]atrim=0:2.8,afade=t=out:st=1.8:d=1.0,volume=0.35,adelay=19150|19150[rise4];
[g1]atrim=0:3.0,afade=t=out:st=2.0:d=1.0,volume=0.35,adelay=1150|1150[shim];
[g2]atrim=0:2.6,afade=t=out:st=1.8:d=0.8,volume=0.4,adelay=9030|9030[inflate];
[5]aformat=sample_rates=48000:channel_layouts=stereo,asplit=4[s1][s2][s3][s4];
[s3]volume=0.4,adelay=19300|19300[swish3];
[s4]volume=0.4,adelay=21900|21900[swish4];
[s1]volume=0.45,adelay=1370|1370[swish];
[s2]volume=0.4,adelay=7970|7970[swish2];
[6]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[u1][u2];
[u1]volume=0.65,adelay=3540|3540[sub];
[u2]volume=0.6,adelay=5490|5490[sub2];
[7]aformat=sample_rates=48000:channel_layouts=stereo,asplit=3[j1][j2][j3];
[j3]atrim=0.5,asetpts=N/SR/TB,atrim=0:2.5,afade=t=in:d=1.6,afade=t=out:st=2.3:d=0.2,volume=0.34,adelay=14500|14500[jet3];
[j1]atrim=1.2,asetpts=N/SR/TB,atrim=0:3.6,afade=t=in:d=1.0,afade=t=out:st=2.8:d=0.8,volume=0.32,adelay=3300|3300[jet];
[j2]atrim=0.5,asetpts=N/SR/TB,atrim=0:2.6,afade=t=in:d=0.6,afade=t=out:st=1.8:d=0.8,volume=0.3,adelay=7300|7300[jet2];
[8]aformat=sample_rates=48000:channel_layouts=stereo,asplit=4[p1][p2][p3][p4];
[p4]atrim=0.4,asetpts=N/SR/TB,atrim=0:2.0,afade=t=in:d=0.05,afade=t=out:st=1.4:d=0.6,volume=0.45,adelay=17020|17020[spark4];
[p1]atrim=0:3.7,afade=t=in:d=0.5,afade=t=out:st=3.2:d=0.5,volume=0.3,adelay=2800|2800[spark];
[p2]atrim=0:1.6,afade=t=in:d=0.3,afade=t=out:st=1.1:d=0.5,volume=0.38,adelay=9950|9950[spark2];
[p3]atrim=1.0,asetpts=N/SR/TB,atrim=0:2.9,afade=t=in:d=0.2,afade=t=out:st=2.6:d=0.3,volume=0.5,adelay=10150|10150[spark3];
[9]aformat=sample_rates=48000:channel_layouts=stereo,asplit=3[q1][q2][q3];
[q3]atrim=0:2.0,afade=t=out:st=1.4:d=0.6,volume=0.35,adelay=17100|17100[plasma3];
[q1]atrim=0:2.3,afade=t=out:st=1.6:d=0.7,volume=0.38,adelay=4200|4200[plasma];
[q2]atrim=0:2.5,afade=t=out:st=1.8:d=0.7,volume=0.4,adelay=10700|10700[plasma2];
[10]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:$D,afade=t=in:d=0.2,volume='if(between(t,7.0,9.6),0.55,if(between(t,12.95,13.15),0.12,if(between(t,16.75,17.0),0.2,1)))':eval=frame[bed];
[11]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[wp1][wp2];
[wp1]volume=0.6,adelay=6450|6450[warp];
[wp2]volume=0.55,adelay=23950|23950[warp2];
[12]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.45,adelay=7300|7300[gate];
[13]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[z1][z2];
[z1]volume=0.5,adelay=10650|10650[zap];
[z2]volume=0.4,adelay=17000|17000[zap2];
[14]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[ac1][ac2];
[ac1]atrim=0:2.6,afade=t=out:st=1.8:d=0.8,volume=0.6,adelay=13150|13150[accent];
[ac2]atrim=0:2.4,afade=t=out:st=1.6:d=0.8,volume=0.7,adelay=22550|22550[accent2];
[15]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[im1][im2];
[im2]atrim=0:1.0,afade=t=in:d=0.3,afade=t=out:st=0.85:d=0.15,volume=0.45,adelay=24000|24000[suck2];
[im1]atrim=0:1.4,afade=t=in:d=0.4,afade=t=out:st=1.25:d=0.15,volume=0.5,adelay=15600|15600[suck];
[braam][woosh][woosh2][rhit][boom][boom2][shim][swish][swish2][sub][sub2][jet][spark][spark2][spark3][plasma][plasma2][bed][warp][gate][zap][inflate][sgra][jet2][rehook][dive][rhit2][boom3][jet3][spark4][plasma3][zap2][accent][suck][dive2][rise3][rise4][swish3][swish4][warp2][accent2][suck2]amix=inputs=42:normalize=0:duration=longest,asetpts=N/SR/TB,volume='if(between(t,16.88,17.0),0.12,if(between(t,22.42,22.55),0.12,1))':eval=frame,
atrim=0:$D,highpass=f=35,equalizer=f=2200:t=q:w=1.2:g=3,extrastereo=m=0.55,afade=t=out:st=$(echo "$D-0.2"|bc):d=0.2,loudnorm=I=-14:TP=-1.5:LRA=11,volume=1.6dB,alimiter=limit=0.72:level=false,aresample=48000[o]" \
 -map "[o]" -ar 48000 "$OUT"
echo wrote $OUT
