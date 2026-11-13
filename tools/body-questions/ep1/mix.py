#!/usr/bin/env python3
"""mix.py SFX_DIR VO_WAV OUT_WAV  -> 23 s mix, VO on top, loudnorm -14 LUFS"""
import sys, subprocess
SFX, VO, OUT = sys.argv[1:4]
DUR = 23.0
# (file, start s, gain dB)
CUES = [
    ('drop_hit', 0.00, -4), ('punch', 0.26, -6), ('cut_tick', 1.50, -9),
    ('nerve_zap', 2.90, -6), ('heartbeat', 3.80, -5), ('heartbeat', 5.30, -8),
    ('squeeze', 6.25, -6), ('cut_tick', 7.34, -10), ('skin_crinkle', 7.60, -9),
    ('proof_hit', 11.00, -4), ('whoosh', 13.84, -8), ('cut_tick', 15.63, -9),
    ('water_drain', 15.65, -8), ('whoosh', 19.00, -9), ('splash_soft', 19.15, -9),
    ('pop', 21.75, -8),
]
ins = ['-i', VO, '-i', f'{SFX}/bath_amb.mp3']
fil = [f'[0:a]aresample=48000,apad=whole_dur={DUR},adelay=0|0[vo]',
       f'[1:a]aresample=48000,aloop=loop=2:size=480000,atrim=0:{DUR},volume=-27dB,afade=t=in:d=0.3,afade=t=out:st={DUR-1}:d=1[amb]']
labels = ['[vo]', '[amb]']
for k, (f, st, g) in enumerate(CUES):
    ins += ['-i', f'{SFX}/{f}.mp3']; ms = int(st * 1000)
    fil.append(f'[{k+2}:a]aresample=48000,volume={g}dB,adelay={ms}|{ms}[s{k}]'); labels.append(f'[s{k}]')
# duck sfx+amb slightly under VO via sidechain
fil.append(''.join(labels[1:]) + f'amix=inputs={len(labels)-1}:normalize=0[fx]')
fil.append('[vo]asplit[vo1][vo2]')
fil.append('[fx][vo2]sidechaincompress=threshold=0.05:ratio=4:attack=5:release=250[fxd]')
fil.append(f'[vo1][fxd]amix=inputs=2:normalize=0,atrim=0:{DUR},loudnorm=I=-14:TP=-1.0:LRA=11[out]')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *ins, '-filter_complex', ';'.join(fil), '-map', '[out]', '-ar', '48000', OUT], check=True)
print('ok', OUT)
