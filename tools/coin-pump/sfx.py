# Code SFX for the 9-5 coin pump reel. Usage: python3 sfx.py out.wav
import sys, wave
import numpy as np
SR=48000; DUR=8.2; PERIOD=0.54; PUMP_END=3.8
rng=np.random.default_rng(5); out=np.zeros(int(SR*DUR))
def add(sig,t,g=1.0):
    i=int(t*SR); n=min(len(sig),len(out)-i)
    if n>0: out[i:i+n]+=sig[:n]*g
def tt(d): return np.arange(int(d*SR))/SR
def bp(x,lo,hi):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); X[(f<lo)|(f>hi)]=0; return np.fft.irfft(X,len(x))
def clink(f=3200,d=0.35):
    t=tt(d); return sum(a*np.sin(2*np.pi*f*m*t)*np.exp(-t*k) for m,a,k in ((1,1,14),(1.48,.6,18),(2.1,.35,24)))
k=0
while k*PERIOD<PUMP_END:
    t0=k*PERIOD
    t=tt(0.22); add(bp(rng.standard_normal(len(t)),900,5000)*np.sin(np.pi*t/0.22)**2,t0+PERIOD*0.5,0.35)  # pssh down-stroke
    add(clink(2600+rng.random()*900,0.3),t0+PERIOD*0.62,0.25)  # stack grows a coin
    k+=1
for i,t0 in enumerate((4.0,4.12,4.24)):
    t=tt(0.15); add(bp(rng.standard_normal(len(t)),3000,9000)*np.exp(-t*30),t0,0.15)
    add(clink(3400+i*150,0.4),t0+0.6,0.4)
add(clink(3000,0.5),5.6,0.5)
# pickup sparkle
for i,f in enumerate((1568,2093,2637)):
    t=tt(0.6); add(np.sin(2*np.pi*f*t)*np.exp(-t*6),5.9+i*0.07,0.18)
# deflate
t=tt(0.6); add(bp(rng.standard_normal(len(t)),200,3000)*np.sin(np.pi*t/0.6)*np.linspace(1,0.3,len(t)),7.0,0.6)
t=tt(0.6); add(np.sin(2*np.pi*(500-350*t)*t)*np.sin(np.pi*t/0.6),7.0,0.2)
out/=np.abs(out).max()/0.89
with wave.open(sys.argv[1],'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype(np.int16).tobytes())
