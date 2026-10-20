#!/usr/bin/env python3
"""Mosquito reel v10 audio (voice-over v2): retime the v8 sound bed to the new picture timing and add the Fraser voice-over.
usage: retime_audio2.py <bed.wav> <vo_dir> <out.wav>   (vo_dir holds full.mp3, the v2 voice-over take)
Picture timing (old reel time -> new): 0-3.0 as is | +0.6 s freeze | old 3.3-6.45 x1.2 | old 6.45-12.0 as is | old 12.0-12.3 stretched to 1.4 s (slow hold on TRANSMISSION INTERRUPTED) |
old 12.3-18.0 as is | old 18.0-21.5 x1.129 | old 21.5-25.0 x1.25. New length 24.77 s."""
import sys, subprocess, numpy as np, os, tempfile, wave
SR=44100
def load(p): raw=subprocess.run(['ffmpeg','-v','error','-i',p,'-ac','2','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout; return np.frombuffer(raw,np.float32).reshape(-1,2).T.copy()
def save(x,p): w=wave.open(p,'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(x.T,-1,1)*32767).astype('<i2').tobytes()); w.close()
def tempo(x,f):
    d=tempfile.mkdtemp(); a=os.path.join(d,'a.wav'); b=os.path.join(d,'b.wav'); save(x,a)
    subprocess.run(['ffmpeg','-v','error','-y','-i',a,'-af',f'atempo={f}','-ar',str(SR),b],check=True); return load(b)
bed=load(sys.argv[1]); sl=lambda a,b: bed[:,int(a*SR):int(b*SR)]
sil=lambda s: np.zeros((2,int(s*SR)),np.float32)
t=np.arange(int(0.65*SR))/SR
rms=np.sqrt((sl(11.85,12.0)**2).mean()); wh=np.sin(2*np.pi*np.cumsum(508+14*t/0.65+6*np.sin(2*np.pi*6*t))/SR); wh=wh*(rms*1.4)/np.sqrt((wh**2).mean())*np.minimum(1,(0.65-t)/0.05)
wh=np.stack([wh,wh]).astype(np.float32)
region=np.concatenate([wh, sl(12.12,12.3)],axis=1); region=np.concatenate([region, sil(1.4)],axis=1)[:,:int(1.4*SR)]
parts=[sl(0,3.0), sil(0.6), tempo(sl(3.3,6.45),1.2), sl(6.45,12.0), region, sl(12.3,18.0), tempo(sl(18.0,21.5),1.129), tempo(sl(21.5,25.0),1.25)]
out=np.concatenate(parts,axis=1); n=out.shape[1]
# voice-over v2: one recording (7 lines, 23.9 s); pauses are trimmed and lines placed on the picture beats
full=load(os.path.join(sys.argv[2],'full.mp3'))
def line(segs,start,rate=1.0):
    parts=[]
    for a,b,gap in segs:
        x=full[:,int(a*SR):int(b*SR)].copy(); f=int(0.008*SR); x[:,:f]*=np.linspace(0,1,f); x[:,-f:]*=np.linspace(1,0,f)
        parts.append(x); parts.append(np.zeros((2,int(gap*SR)),np.float32))
    x=np.concatenate(parts,axis=1)
    return start,(tempo(x,rate) if rate!=1.0 else x)
lines=[line([(0,0.52,0.12),(0.99,2.68,0.25),(3.37,4.11,0)],3.9,1.15),   # Tonight, every mosquito on Earth... is gone.
 line([(4.95,8.0,0)],7.2),                                              # Malaria kills six hundred thousand a year.
 line([(8.67,9.28,0.30),(9.98,11.1,0)],11.9,1.1),                       # And the bite... never happens.
 line([(11.83,13.12,0.15),(13.43,14.87,0)],13.8,1.12),                  # For the first time, the night is safe.
 line([(15.68,17.82,0)],16.6),                                          # But a fish loses a meal.
 line([(18.41,20.42,0)],19.0),                                          # And a few flowers lose a helper.
 line([(21.28,21.73,0.4),(22.57,23.88,0)],21.9)]                        # So... would you erase them?
voice=np.zeros_like(out); env=np.zeros(n,np.float32)
for st,x in lines:
    i=int(st*SR); j=min(n,i+x.shape[1]); voice[:,i:j]+=x[:,:j-i]; env[i:j]=1.0
from numpy.fft import rfft, irfft
k=np.ones(int(0.12*SR))/int(0.12*SR); env=np.convolve(env,k,mode='same')   # smooth the ducking envelope
duck=1.0-0.45*np.clip(env*1.3,0,1)
# voice level: about -15 LUFS speech on top of the ducked bed
vp=np.sqrt((voice[:,np.abs(voice).max(0)>0.02]**2).mean()); voice=voice*(0.16/vp)
mix=out*duck+voice
mix=np.tanh(mix*1.05)/1.05; mix*=0.93/np.abs(mix).max(); mix[:,-int(0.3*SR):]*=np.linspace(1,0,int(0.3*SR))
save(mix,sys.argv[3]); print('length',round(n/SR,3))
