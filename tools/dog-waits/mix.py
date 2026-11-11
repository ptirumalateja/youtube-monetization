# Foley + piano mix. Output: output/mix.wav (loudness-normalised for social, -14 LUFS)
import numpy as np, subprocess
SR=48000; DUR=13.0
def load(n):
    raw=subprocess.run(['ffmpeg','-v','error','-i',f'sfx/{n}.mp3','-ac','2','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout
    return np.frombuffer(raw,np.float32).reshape(-1,2).copy()
out=np.zeros((int(SR*DUR)+SR*12,2),np.float32)
def put(n,t,g=1.0,fade_out=None,maxlen=None):
    a=load(n)*g
    if maxlen: a=a[:int(maxlen*SR)]
    if fade_out: k=int(fade_out*SR); a[-k:]*=np.linspace(1,0,k)[:,None]
    i=int(t*SR); out[i:i+len(a)]+=a
room=load('room'); out[:len(room)]+=room*3.0
put('door_close',0.12,4.0); put('sigh',1.02,1.1)
for t in (1.6,2.2,3.0,3.9,5.0,5.7,6.4): put('swish',t-0.06,0.55)
put('ticks',1.62,0.35,fade_out=0.5,maxlen=3.3)
put('piano',5.0,0.55)
put('jingle',6.4,1.2); put('whine',6.98,0.75); put('door_open',7.36,4.0)
put('barks',7.72,0.75); put('laugh',8.12,0.65); put('nuzzle',9.1,3.5)
out=out[:int(SR*DUR)]
k=int(0.6*SR); out[-k:]*=np.linspace(1,0.25,k)[:,None]**1.5
out=out/np.abs(out).max()*0.8
out.astype(np.float32).tofile('output/mix.f32')
subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(SR),'-ac','2','-i','output/mix.f32','-af','loudnorm=I=-14:TP=-1.5:LRA=11','-ar',str(SR),'output/mix.wav'],check=True)
print('mix ok')
