# Lay the trimmed VO lines on a timeline, get word times (faster-whisper), write vo.json + vo.wav
import json, subprocess, numpy as np, os, wave
from faster_whisper import WhisperModel
H=os.path.dirname(os.path.abspath(__file__))+'/vo'; SR=48000
L=[l.strip() for l in open(H+'/lines.txt') if l.strip()]
GAP={1:0.45,2:0.2,3:0.25,4:0.25,5:0.2,6:0.25,7:0.75,8:0.6,9:0.3,10:0.45,11:0.5,12:0.25,13:0.3,14:0.35,15:0.5,16:0.45,17:0.5}
m=WhisperModel('base.en',device='cpu',compute_type='int8')
t=0.1; out=[]; bufs=[]
for i,txt in enumerate(L,1):
    raw=subprocess.run(['ffmpeg','-v','error','-i',f'{H}/t{i:02d}.wav','-af','atempo=1.08','-f','s16le','-ac','1','-ar',str(SR),'-'],capture_output=True).stdout
    a=np.frombuffer(raw,np.int16).astype(np.float32)/32768; d=len(a)/SR
    a16=a[::3]; segs,_=m.transcribe(a16,word_timestamps=True,initial_prompt=None)
    words=[{'w':w.word.strip(),'t':round(t+w.start,3),'e':round(t+w.end,3)} for s in segs for w in s.words]
    out.append({'i':i,'text':txt,'t':round(t,3),'e':round(t+d,3),'words':words}); bufs.append((t,a))
    t+=d+0.85*GAP.get(i,0.3)
DUR=round(t+1.2,2)
mix=np.zeros(int(DUR*SR))
for t0,a in bufs: k=int(t0*SR); mix[k:k+len(a)]+=a
with wave.open(H+'/vo.wav','wb') as f: f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((np.clip(mix,-1,1)*32767).astype('<i2').tobytes())
json.dump({'dur':DUR,'lines':out},open(H+'/vo.json','w'),indent=0)
for o in out: print(f"{o['i']:2d} {o['t']:6.2f}-{o['e']:6.2f} {o['text']}")
print('DUR',DUR)
