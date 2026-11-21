# Code SFX for bent nails: clang per hit, nail giggles, sob, tear plinks. Usage: python3 sfx.py out.wav
import sys, wave
import numpy as np
SR=48000; DUR=10.0; HITS=[0.84,2.2,3.87,5.83,7.47,9.4]
rng=np.random.default_rng(12); out=np.zeros(int(SR*DUR))
def add(sig,t,g=1.0):
    i=int(t*SR); n=min(len(sig),len(out)-i)
    if n>0: out[i:i+n]+=sig[:n]*g
def tt(d): return np.arange(int(d*SR))/SR
def bp(x,lo,hi):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); X[(f<lo)|(f>hi)]=0; return np.fft.irfft(X,len(x))
def clang():
    t=tt(1.2); s=sum(a*np.sin(2*np.pi*f*t)*np.exp(-t*d) for f,a,d in ((1180,1,5),(2710,.6,7),(4230,.4,9),(5960,.25,12),(830,.5,4)))
    s+=bp(rng.standard_normal(len(t)),1500,10000)*np.exp(-t*60)*2
    s+=np.sin(2*np.pi*90*t)*np.exp(-t*20)*1.5
    return s
def giggle(f0,n):
    parts=[]
    for k in range(n):
        d=0.09; t=tt(d); f=f0*(1+0.15*np.sin(np.pi*t/d))*(1-0.04*k)
        src=np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))*0.5+0.6*rng.standard_normal(len(t))
        v=bp(src,f0*2,f0*9)*np.sin(np.pi*t/d)**2
        parts.append(v); parts.append(np.zeros(int(0.045*SR)))
    return np.concatenate(parts)
def sob():
    d=0.7; t=tt(d); f=330+60*np.sin(2*np.pi*6*t)-80*t
    src=np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))
    v=bp(src,400,2600)*(0.6+0.4*np.sin(2*np.pi*7*t))*np.sin(np.pi*t/d)
    return v
for i,h in enumerate(HITS):
    add(clang(),h,0.9)
    add(sob(),h+0.08,0.10)
    for j,f0 in enumerate((520,640,760)):
        add(giggle(f0,4),h+0.18+j*0.07,0.05)
    for k in range(3):
        t=tt(0.12); add(np.sin(2*np.pi*(1800-3000*t)*t)*np.exp(-t*40),h+0.45+k*0.18+rng.random()*0.05,0.08)
out/=np.abs(out).max()/0.89
with wave.open(sys.argv[1],'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype(np.int16).tobytes())
