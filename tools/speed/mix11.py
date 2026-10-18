#!/usr/bin/env python3
"""Speed Ladder v12 sound, built from the owner's Freesound clips (CC0 and CC BY only; the four CC BY-NC files were removed, see audio-attribution.md). usage: mix11.py <sfx_dir> <out.wav>
Timeline (s): jet 0-0.9 | bullet 0.9-1.8 | Earth 1.8-3.6 | probe 3.6-5.4 | held breath 5.4-5.85 | light 5.85-8.1 | laps 8.1-10.8 | twist 10.8-12.6 | question 12.6-14.4 (holds, no loop)
Each stop adds a layer and about +3 dB over the last: jet quiet, bullet crack, Earth heartbeat, probe fire roar + big hit, light drop, then nearly silent."""
import sys, os, subprocess, wave
import numpy as np
D=sys.argv[1]; SR=44100; T=15.0; N=int(T*SR)
def clip(f,start,dur,db=0.0,lp=None,hp=None,rate=1.0,fi=0.01,fo=0.05):
    af=[]
    if rate!=1.0: af.append(f'asetrate={int(SR*rate)},aresample={SR}')
    if hp: af.append(f'highpass=f={hp}')
    if lp: af.append(f'lowpass=f={lp}')
    af.append(f'afade=t=in:st=0:d={fi}'); af.append(f'afade=t=out:st={max(0.0,dur-fo):.3f}:d={fo}'); af.append(f'volume={db}dB')
    p=subprocess.run(['ffmpeg','-v','error','-ss',str(start),'-t',str(dur/rate),'-i',os.path.join(D,f),'-af',','.join(af),'-ac','2','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout
    x=np.frombuffer(p,np.float32).reshape(-1,2).T.copy(); return x[:,:int(dur*SR)]
M=np.zeros((2,N),np.float32)
rng=np.random.default_rng(9)
def tt(n): return np.arange(n)/SR
def synth_beat(f=58,g=0.5):
    n=int(0.30*SR); t=tt(n); y=np.sin(2*np.pi*(f+34*np.exp(-t/0.045))*t)*np.exp(-t/0.10); return np.stack([np.tanh(1.3*y)*g]*2).astype(np.float32)
def synth_rotate(dur,f0,f1,g):
    """circling air: low-passed noise whose brightness and level swell and rotate (stereo, 3 Hz pan), no tones"""
    n=int(dur*SR); x=rng.standard_normal(n); X=np.fft.rfft(x); fr=np.fft.rfftfreq(n,1/SR); y=np.fft.irfft(X*(np.clip((fr-120)/60,0,1)*np.clip((f1-fr)/(f1*0.3),0,1)),n)
    env=np.sin(np.pi*np.linspace(0,1,n))**1.4; pan=np.sin(2*np.pi*2.4*tt(n)); return np.stack([y*env*g*(0.7+0.3*pan),y*env*g*(0.7-0.3*pan)]).astype(np.float32)
def shift(t): return 0.45*(t>=0.3)+0.45*(t>=1.2)   # the jet and bullet stops are one beat (0.45 s) longer each
def put(x,t0,anchor=None):
    t0=t0+shift(t0 if anchor is None else anchor)
    i=int(round(t0*SR))
    if i<0: x=x[:,-i:]; i=0
    j=min(N,i+x.shape[1])
    if j>i: M[:,i:j]+=x[:,:j-i]
# bed: dark drone under the whole ladder (low, steady), then fades before the held breath
put(clip('terror_ambience_155142.mp3',40.0,6.3,-22,lp=1500,hp=60,fi=0.4,fo=0.1),0.0)
put(clip('rarexport_4096.wav',8.0,6.3,+2,lp=1500,hp=40,fi=0.5,fo=0.1),0.0)
put(clip('tonal_wind_397092.wav',30.0,6.3,+14,lp=600,hp=45,fi=0.5,fo=0.1),0.0)
# frame-0 hit, small
put(clip('impact_376816.wav',0.0,1.6,-21,lp=2500,hp=40),0.0)
# riser into each cut
put(clip('riser_quick_376576.wav',3.0,0.5,-17,hp=200,fi=0.2,fo=0.01),0.4)
put(clip('riser_quick_376576.wav',3.0,0.5,-15,hp=200,rate=0.92,fi=0.2,fo=0.01),1.3)
put(clip('riser_quick_376576.wav',2.7,0.8,-13,hp=200,fi=0.4,fo=0.01),2.8)
# --- jet 0-0.9: distant airliner
put(clip('jet_overhead_352134.wav',8.4,2.0,-14,hp=60,lp=6000,fi=0.3,fo=0.6),0.0)
# --- bullet 0.9: dry crack (owner's clip, transient at 0.8 s in the file) + low impact under it
put(clip('bullet_whiz_123223.wav',0.0,2.6,-8,hp=60,fi=0.005,fo=0.6),0.1,anchor=0.9)
put(clip('impact_376816.wav',0.0,1.8,-14,lp=3500,hp=40),0.7)
put(clip('supersonic_250591.wav',1.0,1.5,-12,hp=300,lp=6000,fi=0.3,fo=0.4),1.1)
# --- Earth 1.8: heartbeat, wide low wind, a warm cinematic hit
put(clip('heartbeat_92036.mp3',0.5,1.8,+3,lp=500,hp=35,fi=0.05,fo=0.25),1.8)   # urupin, CC BY 4.0
put(clip('tonal_wind_397092.wav',30.0,1.8,+17,lp=900,hp=60,fi=0.4,fo=0.4),1.8)
put(clip('impact_cinematic_376817.wav',0.0,3.0,-9,lp=4000,hp=40),1.3)
# --- probe 3.6: fire roar building, suspense rising, the biggest hit of the ladder
put(clip('fire_roar_730704.wav',86.0,1.8,+16,lp=6000,hp=80,fi=1.2,fo=0.15),3.6)
put(clip('sitar_riser_403662.wav',12.3,1.8,-4,hp=120,fi=0.6,fo=0.05),3.6)
put(clip('horror_climax_235205.wav',3.0,1.8,+3,hp=120,lp=6000,fi=0.9,fo=0.05),3.6)
put(clip('impact_376816.wav',0.0,1.8,-7,lp=4500,hp=40),3.6)
# --- held breath 5.4-5.85: silence (the layers above end at 5.4); thin tone returns after the drop
# --- light drop 5.85: cinematic impact aligned so its peak (0.5 s into the file) lands on 5.85, plus the low impact; then it falls hollow
put(clip('impact_cinematic_376817.wav',0.4,3.0,0,lp=6000,hp=40,fi=0.02),5.75)
put(clip('impact_376816.wav',0.0,2.5,-3,lp=5000,hp=40),5.75)
put(clip('tonal_wind_397092.wav',33.0,2.4,+18,lp=700,hp=50,fi=0.2,fo=0.6),5.9)
put(clip('ringing_218050.wav',2.0,1.9,-34,lp=5000,fi=0.6,fo=0.8),6.2)
# --- laps 8.1-10.8: spinning noise as the circling bed (low-passed), a weight at 7.5 laps (9.4)
put(clip('wind_turbine_434098.wav',3.2,2.6,-6,hp=100,lp=4500,fi=0.4,fo=0.6),8.1)
put(clip('impact_376816.wav',0.0,1.6,-9,lp=3000,hp=40),9.35)
# --- twist 10.8-12.6: dark, unresolved
put(clip('terror_ambience_155142.mp3',43.0,3.6,-9,lp=3000,hp=80,fi=0.6,fo=1.4),10.8)
put(clip('tonal_wind_397092.wav',31.0,3.6,+14,lp=700,hp=45,fi=0.6,fo=1.4),10.8)
put(clip('rarexport_4096.wav',40.0,3.6,+2,lp=1500,hp=40,fi=0.6,fo=1.4),10.8)
# the question lands: one soft low hit and a hollow tail, then the drone hangs and fades out unresolved
put(clip('impact_376816.wav',0.0,1.8,-15,lp=2500,hp=40),12.7)
put(clip('tonal_wind_397092.wav',36.0,1.7,+16,lp=700,hp=50,fi=0.3,fo=1.0),12.7)
# a short riser into the question
put(clip('riser_quick_376576.wav',2.9,0.6,-15,hp=200,fi=0.3,fo=0.01),12.1)
gate=np.ones(N,np.float32); gate[int(6.30*SR):int(6.65*SR)]=0.0; gate[int(6.26*SR):int(6.30*SR)]=np.linspace(1,0,int(6.30*SR)-int(6.26*SR)); M*=gate
# ---- master: soft limit, then set the level
M=np.tanh(0.9*M)/np.tanh(0.9)
fade=np.ones(N,np.float32); fade[:int(0.004*SR)]=np.linspace(0,1,int(0.004*SR)); fade[-int(0.5*SR):]=np.linspace(1,0,int(0.5*SR)); M*=fade
pk=np.max(np.abs(M)); M*=0.80/pk
pcm=(M.T*32767).astype('<i2')
with wave.open(sys.argv[2],'wb') as wf: wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(pcm.tobytes())
print('wrote',sys.argv[2],round(N/SR,2),'s peak 0.80')
