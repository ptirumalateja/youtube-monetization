#!/usr/bin/env python3
"""Tighten the VO: keep each spoken phrase, speed it slightly, set short fixed gaps.
Usage: vo.py in.mp3 out.wav  -> prints phrase start times (JSON)"""
import subprocess, sys, json
SRC, OUT = sys.argv[1], sys.argv[2]
TEMPO = 1.16
# phrase spans from silencedetect (-38 dB, 0.12 s) on Teja's take, padded 0.06 s
P = [(0.00,2.60),(3.00,5.36),(5.92,7.78),(8.31,10.70),(11.28,13.40),(13.81,14.37),
     (14.51,15.76),(16.21,17.79),(18.22,19.35),(19.78,21.60),(22.16,24.32),(24.73,29.13),(29.65,30.91)]
GAP = [0.14]*len(P); GAP[5]=0.06; GAP[9]=0.38   # tight "The other, around 1800"; beat before the skull clue
LEAD, TAIL = 0.10, 0.45
parts, t, starts = [], LEAD, []
fc, ins = [], 0
for i,(a,b) in enumerate(P):
    a2, b2 = max(0,a-0.06), b+0.06
    starts.append(round(t,3))
    fc.append(f"[0:a]atrim={a2}:{b2},asetpts=PTS-STARTPTS,atempo={TEMPO},afade=t=in:d=0.02,areverse,afade=t=in:d=0.04,areverse[p{i}]")
    t += (b2-a2)/TEMPO
    if i < len(P)-1:
        fc.append(f"anullsrc=r=44100:cl=mono,atrim=0:{GAP[i]}[g{i}]"); t += GAP[i]
seq = ''.join(f"[p{i}]" + (f"[g{i}]" if i < len(P)-1 else '') for i in range(len(P)))
n = 2*len(P)-1
fc.append(f"anullsrc=r=44100:cl=mono,atrim=0:{LEAD}[lead];anullsrc=r=44100:cl=mono,atrim=0:{TAIL}[tail]")
fc.append(f"[lead]{seq}[tail]concat=n={n+2}:v=0:a=1,aformat=sample_rates=48000:channel_layouts=mono[out]")
subprocess.run(['ffmpeg','-v','error','-y','-i',SRC,'-filter_complex',';'.join(fc).replace('[0:a]atrim','[0:a]aformat=sample_rates=44100:channel_layouts=mono,atrim'),
                '-map','[out]',OUT],check=True)
print(json.dumps({'starts':starts,'end':round(t+TAIL,3)}))
