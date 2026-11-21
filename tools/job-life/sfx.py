# Code SFX for "POV: Life with a Job". Usage: python3 sfx.py out.wav
import sys, wave
import numpy as np
SR=48000; DUR=10.2
rng=np.random.default_rng(21); out=np.zeros(int(SR*DUR))
def add(sig,t,g=1.0):
    i=int(t*SR); n=min(len(sig),len(out)-i)
    if n>0: out[i:i+n]+=sig[:n]*g
def tt(d): return np.arange(int(d*SR))/SR
def bp(x,lo,hi):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); X[(f<lo)|(f>hi)]=0; return np.fft.irfft(X,len(x))
def step():
    t=tt(0.12); return bp(rng.standard_normal(len(t)),80,1500)*np.exp(-t*45)+np.sin(2*np.pi*70*t)*np.exp(-t*35)
for s in (0.22,0.66,1.1,1.54): add(step(),s,0.35)
# bag drop + bed flop
t=tt(0.6); add(bp(rng.standard_normal(len(t)),60,900)*np.exp(-t*9)+np.sin(2*np.pi*55*t)*np.exp(-t*7),1.98,0.9)
t=tt(0.3); add(bp(rng.standard_normal(len(t)),200,3000)*np.exp(-t*12),2.02,0.3)
# snores 3.3-4.3
for s0 in (3.3,):
    d=0.9;t=tt(d);buzz=np.sign(np.sin(2*np.pi*36*t))*0.5+bp(rng.standard_normal(len(t)),80,500)*3
    add(buzz*np.sin(np.pi*t/d)**2,s0,0.18)
# whoosh 4.25
t=tt(0.5); add(bp(rng.standard_normal(len(t)),300,6000)*np.sin(np.pi*t/0.5)**2,4.2,0.6)
# alarm bell 4.6-6.75: hammer striking two bells ~16 Hz
d=2.15;t=tt(d);bell=np.sin(2*np.pi*2350*t)+0.7*np.sin(2*np.pi*3120*t)+0.4*np.sin(2*np.pi*4700*t)
gate=(np.sin(2*np.pi*16*t)>0).astype(float); gate=np.convolve(gate,np.ones(200)/200,'same')
burst=((t%0.9)<0.7).astype(float)
add(bell*gate*burst*np.exp(-0.0*t),4.6,0.35)
# groan-ish push up 6.4 (low filtered noise)
t=tt(0.5); add(bp(rng.standard_normal(len(t)),90,500)*np.sin(np.pi*t/0.5),6.4,0.25)
# footsteps out + door close
for s in (8.15,8.6,9.05,9.5): add(step(),s,0.35)
t=tt(0.5); add(bp(rng.standard_normal(len(t)),60,2000)*np.exp(-t*14)+np.sin(2*np.pi*80*t)*np.exp(-t*12),9.92,0.9)
out/=np.abs(out).max()/0.89
with wave.open(sys.argv[1],'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype(np.int16).tobytes())
