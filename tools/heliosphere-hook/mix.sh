#!/usr/bin/env bash
# Hook v18 sound (6.5 s): library hits from tools/sfxlib cut to the picture (credits in /audio-attribution.md). No music.
# 0.1 braam on frame 0 | 1.8 woosh peak as the camera lifts past the Sun | 2.55 riser-hit + deep boom + portal shimmer as the Sun's bubble lands
# 3.4 air swish on the caption change | 5.05 subby whoosh on the speed line | wind, sparks, plasma and jet texture underneath
set -euo pipefail
L=../sfxlib; OUT=${1:-output/hook.wav}
ffmpeg -y -v error \
 -i $L/722633__chakong__cinematic-braaam.wav -i $L/649445__audiopapkin__cinematic-woosh-sfx-015.wav -i $L/822420__audiopapkin__riser-hit-sfx-120.wav \
 -i $L/814046__qubodup__explosion-from-another-dimension.wav -i $L/768664__berkup__portal-gate-opening.wav -i $L/276871__lucabia__sword-in-air.wav \
 -i $L/238375__stewdio2003__cp_subby_whoosh.aiff -i $L/115555__vartioh__synth_jet.wav -i $L/849772__mikiko850__electric-sparks.wav \
 -i $L/850262__cvltiv8r__orbiting-plasma-burst-and-trail-fx.wav -i $L/22331__sleepcircle__wind.ogg \
 -filter_complex "
[0]aformat=sample_rates=48000:channel_layouts=stereo,atrim=1.95,asetpts=N/SR/TB,atrim=0:2.6,afade=t=out:st=1.6:d=1.0,volume=0.95[braam];
[1]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0.74,asetpts=N/SR/TB,volume=0.8[woosh];
[2]aformat=sample_rates=48000:channel_layouts=stereo,atrim=3.65,asetpts=N/SR/TB,atrim=0:4.6,afade=t=in:d=1.2,afade=t=out:st=3.6:d=1.0,volume=0.85[rhit];
[3]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:3.5,afade=t=out:st=2.4:d=1.1,volume=0.75,adelay=2200|2200[boom];
[4]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:3.0,afade=t=out:st=2.0:d=1.0,volume=0.35,adelay=1150|1150[shim];
[5]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.45,adelay=1370|1370[swish];
[6]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.65,adelay=3540|3540[sub];
[7]aformat=sample_rates=48000:channel_layouts=stereo,atrim=1.2,asetpts=N/SR/TB,afade=t=in:d=1.0,volume=0.28,adelay=3300|3300[jet];
[8]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:3.7,afade=t=in:d=0.5,afade=t=out:st=3.2:d=0.5,volume=0.3,adelay=2800|2800[spark];
[9]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:2.3,afade=t=out:st=1.6:d=0.7,volume=0.38,adelay=4200|4200[plasma];
[10]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:6.5,afade=t=in:d=0.2,volume=1.0[bed];
[braam][woosh][rhit][boom][shim][swish][sub][jet][spark][plasma][bed]amix=inputs=11:normalize=0:duration=longest,
atrim=0:6.5,highpass=f=35,equalizer=f=2200:t=q:w=1.2:g=3,extrastereo=m=0.55,afade=t=out:st=6.15:d=0.35,loudnorm=I=-14:TP=-1.5:LRA=11,volume=1.6dB,alimiter=limit=0.80:level=false,aresample=48000[o]" \
 -map "[o]" -ar 48000 "$OUT"
echo wrote $OUT
