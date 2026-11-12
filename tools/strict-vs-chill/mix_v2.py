# v2 audio: hook front (lamp snap + deep hit, bubble pops, tape rewind) then the v1 story mix (output/mix.wav from mix.py).
import numpy as np, subprocess
SR=48000; HOOK=2.58; RW=0.5; S0=HOOK+RW
def load(path):
    raw=subprocess.run(['ffmpeg','-v','error','-i',path,'-ac','2','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout
    return np.frombuffer(raw,np.float32).reshape(-1,2).copy()
story=load('output/mix.wav'); out=np.zeros((int(S0*SR)+len(story)+SR,2),np.float32)
def put(a,t,g=1.0): i=int(t*SR); n=min(len(a),len(out)-i); out[i:i+n]+=a[:n]*g
sfx=lambda n:load(f'sfx/{n}.mp3')
room=sfx('room'); put(room[int(6.15*SR):int(6.15*SR)+int(HOOK*SR)],0,0.35)
put(sfx('climb'),0.0,0.45)                         # kid landing back on the bed
put(sfx('lamp'),0.26,1.6); put(sfx('hit'),0.26,1.2)  # the light snaps on: biggest sound in the first second
put(sfx('pop'),0.8,0.5); put(sfx('pop'),1.8,0.6)
rw=sfx('rewind'); put(rw[:int(RW*SR)+int(0.15*SR)],HOOK-0.08,0.8)
f=int(S0*SR); fade=np.linspace(0,1,int(0.08*SR))[:,None]; st=story.copy(); st[:len(fade)]*=fade
out[f:f+len(st)]+=st*0.5                            # story mix was loudnormed; scale before final loudnorm
out=out[:f+len(st)]; out=out/np.abs(out).max()*0.8
out.astype(np.float32).tofile('output/mix_v2.f32')
subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(SR),'-ac','2','-i','output/mix_v2.f32','-af','loudnorm=I=-14:TP=-1.5:LRA=11','-ar',str(SR),'output/mix_v2.wav'],check=True)
print('mix_v2 ok')
