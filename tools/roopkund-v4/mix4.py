#!/usr/bin/env python3
"""V4 mix: our ElevenLabs VO (rubberband TEMPO, pre-normalised to a file), ElevenLabs SFX + sfxlib hits.
Usage: mix4.py picture.mp4 vo_tight.wav sfx_dir caps.ass out.mp4   (SFX times are tight-VO seconds)"""
import subprocess, sys, os
PIC, VO, SFX, ASS, OUT = sys.argv[1:6]
TEMPO = float(os.environ.get('TEMPO', '1.08'))
LIB = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sfxlib')
E = lambda n: os.path.join(SFX, n + '.mp3'); L = lambda n: os.path.join(LIB, n)
D = float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',PIC],capture_output=True,text=True).stdout)
vo_n = OUT + '.vo.wav'
subprocess.run(['ffmpeg','-v','error','-y','-i',VO,'-af',f'rubberband=tempo={TEMPO}:pitchq=quality,highpass=f=70,'
                'equalizer=f=180:t=q:w=1:g=2,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,loudnorm=I=-15:TP=-2:LRA=7,aresample=48000',
                '-ac','1',vo_n],check=True)
BRAAAM = L('722633__chakong__cinematic-braaam.wav'); SUB = L('238375__stewdio2003__cp_subby_whoosh.aiff')
ACC = L('869757__mikiko850__dark-suspense-accent.wav'); IMPL = L('814047__qubodup__fantasy-implosion.wav')
# (file, trim_start, at (tight-VO s), gain dB)
FX = [
 (BRAAAM, 0.25, 0.00, -8), (E('drip'), 0, 0.05, -10),
 (E('icecrack'), 0.0, 1.30, -6),                 # "ice melts"
 (E('whoosh'), 0, 2.45, -12),
 (E('boom'), 0, 4.45, -5), (E('bones'), 0, 4.50, -9),   # "dead"
 (E('whoosh'), 0, 5.15, -11),                    # into drone / Roopkund
 (SUB, 0, 8.15, -12),
 (E('bones'), 0.2, 9.30, -8),                    # hundreds of skeletons
 (E('thunder'), 0, 14.70, -7),                   # one terrible night
 (E('boom'), 0, 16.95, -4),                      # THEY DIDN'T
 (E('glitch'), 0, 18.05, -12), (E('glitch'), 0, 19.60, -13),
 (E('glitch'), 0, 22.45, -12), (SUB, 0, 22.50, -10),
 (E('whoosh'), 0, 31.80, -10), (SUB, 0, 33.00, -11),   # map flash: whoosh in, sub on "Greece"
 (E('whoosh'), 0, 25.05, -12),
 (E('heartbeat'), 0, 28.90, -8),                 # under the Greece/Crete reveal
 (E('riser'), 0, 34.85 - 2.4, -10),
 (E('skullcrack'), 0, 36.10, -4), (E('boom'), 0, 36.15, -9),   # "cracked"
 (E('whoosh'), 0, 37.15, -12),                  # look up "from above"
 (E('breath'), 0, 38.45, -12),                  # villagers' song: ghostly air
 (ACC, 0, 40.45, -15),                          # goddess
 (E('hail'), 0, 41.55, -15), (E('thunder'), 0.3, 41.60, -17),   # V5: hail sits under the folklore line
 (SUB, 0, 43.40, -14), (E('boom'), 0, 44.05, -9),             # "iron": hit lands after the word
 (E('icecrack'), 0.1, 45.70, -10),              # "the ice gives back"
 (IMPL, 0, 48.45, -15), (BRAAAM, 0.25, 48.50, -12),           # who were they
]
DUCK = [(16.4, 17.0), (35.0, 36.1), (41.5, 44.2)]
if os.environ.get('AB'):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from ab_cut import FX_AB, DUCK_AB as DUCK
    FX = FX_AB(E, L, BRAAAM, SUB, ACC, IMPL)
inp = ['-i', PIC, '-i', vo_n, '-stream_loop', '-1', '-i', E('wind')]
duck = "+".join([f"between(t,{a/TEMPO:.2f},{b/TEMPO:.2f})" for a, b in DUCK])
fc = [f"[1:a]aformat=channel_layouts=stereo,apad=whole_dur={D}[vo]",
      f"[2:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{D},highpass=f=90,volume=-17dB,"
      f"volume='1-0.9*({duck})':eval=frame[wind]"]
mix = ['[vo]', '[wind]']
for i, (f, ts, at, g) in enumerate(FX):
    inp += ['-i', f]; k = i + 3
    fc.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=start={ts},asetpts=PTS-STARTPTS,volume={g}dB,adelay={int(max(0, at/TEMPO)*1000)}:all=1[f{i}]")
    mix.append(f'[f{i}]')
fc.append(f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0:duration=first,atrim=0:{D},afade=t=out:st={D-0.4}:d=0.4,alimiter=limit=0.79[a]")
fc.append(f"[0:v]ass={ASS}[v]")
subprocess.run(['ffmpeg','-v','error','-y',*inp,'-filter_complex',';'.join(fc),'-map','[v]','-map','[a]',
                '-c:v','libx264','-preset','slow','-b:v','14M','-maxrate','18M','-bufsize','28M','-pix_fmt','yuv420p','-movflags','+faststart',
                '-c:a','aac','-b:a','192k','-t',f'{D}',OUT],check=True)
os.remove(vo_n)
