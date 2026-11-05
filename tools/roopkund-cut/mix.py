#!/usr/bin/env python3
"""Mix VO + wind/drone bed + sfx, burn captions, mux. Usage: mix.py picture.mp4 vo.wav caps.ass out.mp4"""
import subprocess, sys, os
PIC, VO, ASS, OUT = sys.argv[1:5]
L = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sfxlib')
D = float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',PIC],capture_output=True,text=True).stdout)
S = lambda n: os.path.join(L, n)
# (file, trim_start, place_at, gain_dB)
FX = [
 ('722633__chakong__cinematic-braaam.wav',          0.25,  0.00, -9),   # hook hit on the skull
 ('649445__audiopapkin__cinematic-woosh-sfx-015.wav',1.50,  0.18, -14),  # cut to bones under ice
 ('649445__audiopapkin__cinematic-woosh-sfx-015.wav',0.00,  6.36, -15),  # into blue helix
 ('649445__audiopapkin__cinematic-woosh-sfx-015.wav',0.00,  8.43, -13),  # into red helix
 ('822420__audiopapkin__riser-hit-sfx-120.wav',      0.00, 11.60, -15),  # builds under Greece/Crete, hits on skull
 ('869757__mikiko850__dark-suspense-accent.wav',     0.00, 16.82, -12),  # iron hail
 ('722633__chakong__cinematic-braaam.wav',          0.25, 23.88, -13),  # who were they
]
inp = ['-i', PIC, '-i', VO]
fc = [f"[1:a]aresample=48000,highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,loudnorm=I=-15:TP=-2:LRA=7,aformat=channel_layouts=stereo[vo]"]
mix = ['[vo]']
for i,(f,ts,at,g) in enumerate(FX):
    inp += ['-i', S(f)]; k = i+2
    fc.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=start={ts},asetpts=PTS-STARTPTS,volume={g}dB,adelay={int(at*1000)}:all=1[f{i}]")
    mix.append(f'[f{i}]')
# cold wind (brown noise, band-limited, slow gusts) + low drone
fc.append(f"anoisesrc=d={D}:c=brown:r=48000:a=0.5,bandpass=f=500:w=900,tremolo=f=0.18:d=0.55,volume=-24dB,aformat=channel_layouts=stereo[wind]")
fc.append(f"sine=f=55:d={D}:r=48000,volume=-30dB[s1];sine=f=82.4:d={D}:r=48000,volume=-34dB[s2];[s1][s2]amix=2:normalize=0,tremolo=f=0.1:d=0.3,aformat=channel_layouts=stereo[drone]")
mix += ['[wind]','[drone]']
fc.append(f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0:duration=longest,atrim=0:{D},afade=t=out:st={D-0.5}:d=0.5,alimiter=limit=0.89[a]")
fc.append(f"[0:v]ass={ASS}[v]")
subprocess.run(['ffmpeg','-v','error','-y',*inp,'-filter_complex',';'.join(fc),'-map','[v]','-map','[a]',
                '-c:v','libx264','-crf','17','-preset','slow','-pix_fmt','yuv420p','-movflags','+faststart',
                '-c:a','aac','-b:a','192k',OUT],check=True)
