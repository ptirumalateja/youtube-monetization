# Foley mix for both panels (they play at once). Output: output/mix.wav
import numpy as np, subprocess
SR=48000; DUR=11.2
def load(n):
    raw=subprocess.run(['ffmpeg','-v','error','-i',f'sfx/{n}.mp3','-ac','2','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout
    return np.frombuffer(raw,np.float32).reshape(-1,2)
out=np.zeros((int(SR*DUR)+SR,2),np.float32)
def put(n,t,g=1.0,pan=0.0):
    a=load(n)*g; a=a*np.array([1-max(0,pan),1+min(0,pan)],np.float32); i=int(t*SR); out[i:i+len(a)]+=a[:len(out)-i]
room=load('room'); n=min(len(room),len(out)); out[:n]+=room[:n]*0.55
CLOCK=[2.4,3.0,3.55,4.3,4.8,5.3,5.9,7.0,8.6]
for t in CLOCK: put('tick',t,0.35)
# strict (top)
put('pop',0.15,0.5); put('pop',0.7,0.5); put('door_close',1.5,0.8,0.3); put('steps',2.0,0.7,-0.2); put('sash',2.85,0.8,-0.4); put('climb',3.05,0.7,-0.4)
put('door_open',3.55,0.8,0.3); put('steps',3.85,0.6); put('pop',4.05,0.4); put('door_close',4.9,0.5,0.3); put('bed',4.95,0.6)
put('climb',6.15,0.8,-0.4); put('lamp',6.42,1.0); put('pop',6.85,0.5); put('pop',6.95,0.4); put('pop',7.95,0.5)
# chill (bottom)
put('pop',1.0,0.45); put('steps',1.25,0.55,0.2); put('door_close',2.55,0.6,0.3); put('door_open',4.15,0.7,0.3); put('steps',4.45,0.55)
put('pop',4.65,0.45); put('bed',5.65,0.6); put('lamp',5.95,0.8); put('steps',8.6,0.5,0.2)
out=out[:int(SR*DUR)]
env=np.ones(len(out)); fs=int(10.0*SR); env[fs:]=np.linspace(1,0,len(out)-fs); env[:int(0.05*SR)]=np.linspace(0,1,int(0.05*SR))
out*=env[:,None].astype(np.float32)
pk=np.abs(out).max(); out=out/pk*0.7
out.astype(np.float32).tofile('output/mix.f32')
subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(SR),'-ac','2','-i','output/mix.f32','-af','loudnorm=I=-16:TP=-1.5:LRA=11','-ar',str(SR),'output/mix.wav'],check=True)
print('mix ok')
