# python3 vo_fit.py el.mp3 outdir  — fit Teja's ElevenLabs take into ~23 s: cut each spoken chunk (silencedetect), speed up slightly, tighten pauses.
import subprocess, json, sys, numpy as np, wave
SRC,OUT=sys.argv[1],sys.argv[2]
segs=[(0,3.97),(4.88,6.80),(7.04,8.15),(9.01,10.97),(11.44,12.95),(13.27,15.10),(15.56,16.48),(17.26,20.90),(21.73,23.12),(23.53,24.53),(25.38,25.91),(26.32,27.13),(27.94,29.65)]
line=[0,1,1,2,3,4,4,5,6,7,8,8,8]   # script line of each chunk
TEMPO=1.10; PAD=0.04; gap_in={1:0.10,4:0.28,8:0.18}; gap_between=0.26
t=0.06; starts={}; parts=[]; chunk_t=[]
for i,(a,b) in enumerate(segs):
    if i>0: t+= gap_in.get(line[i],0.15) if line[i]==line[i-1] else gap_between
    a0=max(0,a-PAD); b0=b+PAD; out=f"{OUT}/c{i}.wav"
    subprocess.run(["ffmpeg","-v","error","-y","-ss",str(a0),"-to",str(b0),"-i",SRC,"-af",f"atempo={TEMPO},afade=t=in:d=0.02,afade=t=out:st={(b0-a0)/TEMPO-0.03:.3f}:d=0.03","-ar","48000","-ac","1",out],check=True)
    d=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",out],capture_output=True,text=True).stdout)
    starts.setdefault(line[i],t); chunk_t.append((t,d)); parts.append((t,out)); t+=d
end=t; cracks=chunk_t[4][0]+0.70*chunk_t[4][1]
SR=48000; buf=np.zeros(int((end+0.6)*SR))
for (st,f) in parts:
    w=wave.open(f); x=np.frombuffer(w.readframes(w.getnframes()),np.int16)/32768.; j=int(st*SR); buf[j:j+len(x)]+=x
w=wave.open(f"{OUT}/vo_el.wav","wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(buf,-1,1)*32767).astype(np.int16).tobytes()); w.close()
json.dump({"starts":starts,"end":end,"cracks":cracks,"chunks":chunk_t},open(f"{OUT}/el_layout.json","w"),indent=1)
print("end",round(end,2),{k:round(v,2) for k,v in starts.items()},"cracks",round(cracks,2))
