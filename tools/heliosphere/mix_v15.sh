#!/usr/bin/env bash
# Heliosphere reel (v15 FINAL): build the 26.15 s sound mix and mux it onto the sped-up picture.
# Usage: SND=/path/to/freesound/files ./mix_v15.sh raw_render.mp4 out.mp4
#   raw_render.mp4 = HyperFrames render of tools/heliosphere (34 s, 1080x1920, 30 fps)
# Expected files in $SND (Freesound names as downloaded; the globs match the id):
#   856173 braam (brktkrgll), 251462 sick dance bass (staticpony1), 648534 transition hit (audiopapkin),
#   321723 deep space ambience loop (rhodesmas), 758584 distorted unnerve (magnuswaker),
#   32424 hypnotic heartbeat (hello_flowers), 494981 riser (original_sound)
set -euo pipefail
RAW="$1"; OUT="$2"; : "${SND:?set SND}"
f() { ls "$SND"/*"$1"*; }
ffmpeg -y \
 -i "$(f 856173)" -i "$(f 251462)" -i "$(f 648534)" -i "$(f 321723)" -i "$(f 758584)" -i "$(f 32424)" -i "$(f 494981)" \
 -filter_complex "
[0]aformat=sample_rates=44100:channel_layouts=stereo,volume=0.85[braam];
[1]aformat=sample_rates=44100:channel_layouts=stereo,atrim=0:3.0,afade=t=in:d=0.2,afade=t=out:st=2.5:d=0.5,volume=0.5[bass];
[2]aformat=sample_rates=44100:channel_layouts=stereo,volume=0.8,asplit[h1][h2];
[h1]adelay=600|600[hit1];[h2]adelay=13000|13000,volume=0.8[hit2];
[3]aformat=sample_rates=44100:channel_layouts=stereo,atrim=0:26.15,afade=t=in:d=0.8,afade=t=out:st=24:d=2.1,volume=1.1[bed];
[4]aformat=sample_rates=44100:channel_layouts=stereo,adelay=20600|20600,volume=0.55[un];
[5]aformat=sample_rates=44100:channel_layouts=stereo,atrim=0:9,afade=t=in:d=2.5,afade=t=out:st=7:d=2,volume=0.28,adelay=17300|17300[hb];
[6]aformat=sample_rates=44100:channel_layouts=stereo,adelay=11200|11200,volume=0.45[ris];
[braam][bass][hit1][bed][hit2][un][hb][ris]amix=inputs=8:normalize=0:duration=longest,atrim=0:26.15,afade=t=out:st=24.4:d=1.7,loudnorm=I=-15:TP=-1.5:LRA=9[o]" \
 -map "[o]" -ar 44100 mix.wav
# picture: 34 s render sped up 1.3x -> 26.15 s
ffmpeg -y -i "$RAW" -i mix.wav -filter_complex "[0:v]setpts=PTS/1.3,fps=30[v]" -map "[v]" -map 1:a \
 -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest "$OUT"
