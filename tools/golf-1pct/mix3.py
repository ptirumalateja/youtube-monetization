# v3 audio = v2 mix delayed by the 0.4 s opening + three ball-landing tocks (one per row) and a light wind lead-in
import sys, json, subprocess, numpy as np
D3,V2WAV,OUT=sys.argv[1:4]; SR=48000
c=json.load(open(f'{D3}/cues.json'))
def load(p,ch=2):
    return np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',p,'-ac',str(ch),'-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout,np.float32).reshape(-1,ch).copy()
v2=load(V2WAV); pad=int(c['shift']*SR)
mix=np.concatenate([np.zeros((pad,2),np.float32),v2])
wind=load('../sfxlib/22331__sleepcircle__wind.ogg'); mix[:pad]+=wind[:pad]*10**(-16/20)
thump=load('sfx/thump.mp3'); click=load('sfx/click.mp3')
for k,t in enumerate(c['drops']):
    for x,g in ((thump[:int(0.18*SR)],-6+k), (click[:int(0.05*SR)],-14)):
        i=int(t*SR)-int(np.argmax(np.abs(x[:,0]))); n=min(len(x),len(mix)-i); mix[i:i+n]+=x[:n]*10**(g/20)
mix=np.tanh(mix*1.2)/np.tanh(1.2); mix*=0.89/np.abs(mix).max()
subprocess.run(['ffmpeg','-y','-v','error','-f','f32le','-ar',str(SR),'-ac','2','-i','-','-c:a','pcm_s16le',OUT],input=mix.astype(np.float32).tobytes())
