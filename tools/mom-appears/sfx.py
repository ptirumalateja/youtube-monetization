# Code SFX for "Mom appears" (no music). Usage: python3 sfx.py out.wav
import sys, wave
import numpy as np
SR=48000; DUR=9.8; CUT=6.45
rng=np.random.default_rng(8); out=np.zeros(int(SR*DUR))
def add(sig,t,g=1.0):
    i=int(t*SR); n=min(len(sig),len(out)-i)
    if n>0: out[i:i+n]+=sig[:n]*g
def tt(d): return np.arange(int(d*SR))/SR
def bp(x,lo,hi):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); X[(f<lo)|(f>hi)]=0; return np.fft.irfft(X,len(x))
# muffled reel audio from the phone, a new "reel" every 0.7 s (tinny chatter / music blips)
for k in range(int(CUT/0.7)+1):
    t0=k*0.7; d=min(0.7,CUT-t0)
    if d<=0: break
    t=tt(d); f0=rng.choice([220,262,330,392,440,523])
    voice=np.sin(2*np.pi*f0*t+3*np.sin(2*np.pi*5*t))*(0.5+0.5*np.sin(2*np.pi*(4+rng.random()*4)*t))
    beat=(np.sin(2*np.pi*2*t*(1+k%3))>0.9)*bp(rng.standard_normal(len(t)),100,800)*2
    sig=bp(voice+beat+0.3*rng.standard_normal(len(t)),500,3200)
    e=np.ones(len(t)); e[:200]=np.linspace(0,1,200); e[-200:]=np.linspace(1,0,200)
    add(sig*e,t0,0.12)
    # thumb swipe tick
    tc=tt(0.05); add(bp(rng.standard_normal(len(tc)),3000,9000)*np.exp(-tc*200),t0+0.02,0.15)
# hard cut: door bang/creak + horror hit + high string sting
t=tt(1.8); add(np.sin(2*np.pi*(60*np.exp(-t*1.5)+28)*t)*np.exp(-t*1.6),CUT,0.9)
t=tt(0.25); add(bp(rng.standard_normal(len(t)),80,2500)*np.exp(-t*14),CUT,0.6)
t=tt(2.6); s=sum(np.sin(2*np.pi*f*t) for f in (1480,1568,1661))
add(s*np.minimum(1,t/0.05)*np.exp(-t*0.9)*(1+0.3*np.sin(2*np.pi*7*t)),CUT,0.06)
t=tt(0.4); f=420+150*np.sin(2*np.pi*2.5*t)
add(bp(np.sign(np.sin(2*np.pi*np.cumsum(f)/SR)),300,2500)*np.exp(-t*5),CUT+0.05,0.08)
# low tense drone after
t=tt(DUR-CUT); add((np.sin(2*np.pi*55*t)+0.5*np.sin(2*np.pi*58*t))*np.minimum(1,t/0.6),CUT,0.12)
# gulp
t=tt(0.18); add(np.sin(2*np.pi*(180+500*t)*t)*np.sin(np.pi*t/0.18)**2,7.3,0.4)
out/=np.abs(out).max()/0.89
with wave.open(sys.argv[1],'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype(np.int16).tobytes())
