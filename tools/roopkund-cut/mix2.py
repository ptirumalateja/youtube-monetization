#!/usr/bin/env python3
"""V2 mix: pre-normalised VO (no in-graph loudnorm, which dropped the last line), real wind, sfxlib hits.
Usage: mix2.py picture.mp4 vo.wav caps.ass out.mp4"""
import subprocess, sys, os
PIC, VO, ASS, OUT = sys.argv[1:5]
L = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sfxlib')
S = lambda n: os.path.join(L, n)
D = float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',PIC],capture_output=True,text=True).stdout)
vo_n = OUT + '.vo.wav'
subprocess.run(['ffmpeg','-v','error','-y','-i',VO,'-af','highpass=f=70,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,loudnorm=I=-15:TP=-2:LRA=7,aresample=48000',
                '-ac','1',vo_n],check=True)
BRAAAM='722633__chakong__cinematic-braaam.wav'; WOOSH='649445__audiopapkin__cinematic-woosh-sfx-015.wav'
SUB='238375__stewdio2003__cp_subby_whoosh.aiff'; ACC='869757__mikiko850__dark-suspense-accent.wav'
RISER='822420__audiopapkin__riser-hit-sfx-120.wav'; ZAP='19487__halleck__jacobsladdersingle2.flac'
IMPL='814047__qubodup__fantasy-implosion.wav'
# (file, trim_start, place_at, gain_dB)
FX = [
 (BRAAAM, 0.25, 0.00, -6),     # hook: skull
 (WOOSH,  1.90, 0.90-0.62, -12),  # whip into ice (peak 2.52)
 (SUB,    0.00, 1.70, -10),    # heap slam
 (WOOSH,  1.90, 2.45-0.62, -13),  # into drone reveal
 (WOOSH,  1.90, 7.60-0.62, -14),
 (ZAP,    0.00, 8.88, -18),    # glitch into blue helix
 (ZAP,    0.00, 10.95, -16),   # glitch into red helix
 (SUB,    0.00, 10.95, -9),
 (RISER,  0.00, 17.90-6.2, -14),  # builds under Greece/Crete, hits on the cracked skull
 (ZAP,    0.00, 19.90, -20),   # lightning flicker
 (ACC,    0.00, 22.90-5.03, -10), # iron hail
 (SUB,    0.00, 21.85, -11),
 (IMPL,   0.00, 23.94, -16),
 (BRAAAM, 0.25, 23.94, -11),   # who were they
]
inp = ['-i', PIC, '-i', vo_n, '-stream_loop', '-1', '-i', S('22331__sleepcircle__wind.ogg')]
fc = [f"[1:a]aformat=channel_layouts=stereo,apad=whole_dur={D}[vo]",
      f"[2:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{D},highpass=f=120,volume=-20dB,"
      f"volume='1-0.85*between(t,17.55,17.95)':eval=frame[wind]"]   # wind drops out for the beat before the skull clue
mix = ['[vo]', '[wind]']
for i,(f,ts,at,g) in enumerate(FX):
    inp += ['-i', S(f)]; k = i+3
    fc.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=start={ts},asetpts=PTS-STARTPTS,volume={g}dB,adelay={int(max(0,at)*1000)}:all=1[f{i}]")
    mix.append(f'[f{i}]')
fc.append(f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0:duration=first,atrim=0:{D},afade=t=out:st={D-0.35}:d=0.35,alimiter=limit=0.89[a]")
fc.append(f"[0:v]ass={ASS}[v]")
subprocess.run(['ffmpeg','-v','error','-y',*inp,'-filter_complex',';'.join(fc),'-map','[v]','-map','[a]',
                '-c:v','libx264','-preset','slow','-b:v','14M','-maxrate','18M','-bufsize','28M','-pix_fmt','yuv420p','-movflags','+faststart',
                '-c:a','aac','-b:a','192k','-t',f'{D}',OUT],check=True)
os.remove(vo_n)
