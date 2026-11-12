# Foley mix (no music, no voice): room tone / market bed, sole slaps, the boy's new-shoe steps, coins, cardboard, gift paper, rewind.
# Silence under the last two lines. Out: output/mix_full.wav (-15 LUFS).
import json, subprocess
EV=json.load(open('output/full/meta.json'))['events']; DUR=28.0
ins=[]; fl=[]; lab=[]; n=0
def add(f,t,vol,trim=None):
    global n; ins.extend(['-i',f]); tr=f'atrim=0:{trim},' if trim else ''; d=int(t*1000)
    fl.append(f'[{n}:a]{tr}volume={vol},adelay={d}|{d}[a{n}]'); lab.append(f'[a{n}]'); n+=1
# beds: room tone for home shots, market for 3.0-9.0; fade out from 25.6 (silence before the last line)
add('sfx/room.mp3',0,0.32,3.0); add('sfx/market.mp3',3.0,0.42,6.0)
for t0 in (9.0,14.0,19.0): add('sfx/room.mp3',t0,0.3 if t0<19 else 0.22,5.0 if t0<19 else 6.6)
VOL={'slap':1.2,'kidstep':0.8,'coin':1.0,'card':1.0,'paper':0.8}
for e in EV:
    if e['t']>=DUR: continue
    f={'slap':'sfx/slap.mp3','kidstep':'sfx/kidstep.mp3','coin':'sfx/coin.mp3','card':'sfx/card.mp3','paper':'sfx/paper.mp3'}[e['type']]
    v=VOL[e['type']]*(1.4 if e['type']=='slap' and e['t']<1 else 1.0)*(0.8 if e['type']=='slap' and e['t']>19 else 1.0)
    add(f,e['t'],v)
add('sfx/rewind.mp3',2.55,0.9)
fl.append(''.join(lab)+f'amix=inputs={len(lab)}:normalize=0,apad,atrim=0:{DUR},afade=t=out:st=25.4:d=1.2,loudnorm=I=-14.5:TP=-2:LRA=11,alimiter=limit=0.83:level=false[o]')
subprocess.run(['ffmpeg','-v','error','-y',*ins,'-filter_complex',';'.join(fl),'-map','[o]','-ar','48000','output/mix_full.wav'],check=True); print('mix ok',len(EV),'events')
