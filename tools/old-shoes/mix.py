# Foley mix for the look test: room tone, a hard sole slap on every landing (first at ~0.33 s), rewind whoosh.
import json, subprocess
EV=[e['t'] for e in json.load(open('output/hook/meta.json'))['events']]
DUR=3.0; RW=2.55
ins=['-i','sfx/room.mp3']; fl=['[0:a]atrim=0:%g,volume=0.35[r]'%DUR]; mixl=['[r]']; n=1
for i,t in enumerate(EV):
    ins+=['-i','sfx/slap.mp3']; v=1.6 if i==0 else 1.1
    fl.append(f'[{n}:a]volume={v},adelay={int(t*1000)}|{int(t*1000)}[s{n}]'); mixl.append(f'[s{n}]'); n+=1
ins+=['-i','sfx/rewind.mp3']; fl.append(f'[{n}:a]volume=0.9,adelay={int(RW*1000)}|{int(RW*1000)}[w]'); mixl.append('[w]')
fl.append(''.join(mixl)+f'amix=inputs={len(mixl)}:normalize=0,atrim=0:{DUR},loudnorm=I=-15:TP=-1.5:LRA=11[o]')
subprocess.run(['ffmpeg','-v','error','-y',*ins,'-filter_complex',';'.join(fl),'-map','[o]','-ar','48000','output/mix.wav'],check=True); print('mix ok',EV)
