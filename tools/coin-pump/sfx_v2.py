# Code SFX for coin pump v2 (struggle strokes, coin growth, hook/CTA thuds). Usage: python3 sfx_v2.py out.wav
import sys, wave
import numpy as np
SR=48000; DUR=13.0; T_PUMP_END=6.4; T_END=10.2
rng=np.random.default_rng(9); out=np.zeros(int(SR*DUR))
def add(sig,t,g=1.0):
    i=int(t*SR); n=min(len(sig),len(out)-i)
    if n>0 and i>=0: out[i:i+n]+=sig[:n]*g
def tt(d): return np.arange(int(d*SR))/SR
def bp(x,lo,hi):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); X[(f<lo)|(f>hi)]=0; return np.fft.irfft(X,len(x))
def clink(f=3200,d=0.35):
    t=tt(d); return sum(a*np.sin(2*np.pi*f*m*t)*np.exp(-t*k) for m,a,k in ((1,1,14),(1.48,.6,18),(2.1,.35,24)))
def thud():
    t=tt(0.5); return np.sin(2*np.pi*(70*np.exp(-t*4)+40)*t)*np.exp(-t*7)+bp(rng.standard_normal(len(t)),60,400)*np.exp(-t*20)
# replicate stroke timing from the scene
active=lambda x: x<T_PUMP_END or x>8.7
ph=0; x=0; dt=0.001; last=-1; starts=[]
while x<DUR:
    if active(x):
        per=0.95 if x>8.7 else 0.62+0.33*min(1,x/T_PUMP_END); ph+=dt/per
        if int(ph)!=last: starts.append((x,per)); last=int(ph)
    x+=dt
for s,per in starts:
    g_start=s+0.32*per; grind=0.68*0.62*per
    t=tt(grind); f=180+40*np.sin(2*np.pi*3*t)
    squeak=bp(np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))+0.4*rng.standard_normal(len(t)),300,2200)*np.sin(np.pi*t/grind)
    add(squeak,g_start,0.10)                                   # pump grinding under strain
    t=tt(0.3); add(bp(rng.standard_normal(len(t)),150,900)*np.sin(np.pi*t/0.3)**2,g_start+0.05,0.22)  # effort breath "hnn"
    t=tt(0.25); add(bp(rng.standard_normal(len(t)),900,5000)*np.sin(np.pi*t/0.25)**2,s+per*0.82,0.3)  # air pssh
    if s<T_PUMP_END or s>8.7: add(clink(2500+rng.random()*900,0.3),s+per*0.97,0.2)
# hook / text thuds
for tt0 in (0.0,1.1,T_END): add(thud(),tt0,0.9)
for i,t0 in enumerate((T_PUMP_END,T_PUMP_END+0.12,T_PUMP_END+0.24)):
    add(clink(3400+i*150,0.4),t0+0.6,0.4)
tm=T_PUMP_END+1.05
add(clink(3000,0.5),tm+0.6,0.5)
for i,f in enumerate((1568,2093,2637)):
    t=tt(0.6); add(np.sin(2*np.pi*f*t)*np.exp(-t*6),tm+0.95+i*0.07,0.18)
out[int(T_END*SR):]*=np.linspace(1,0.25,len(out)-int(T_END*SR))**0.5
add(thud(),T_END,0.9)
out/=np.abs(out).max()/0.89
with wave.open(sys.argv[1],'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype(np.int16).tobytes())
