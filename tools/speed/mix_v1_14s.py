#!/usr/bin/env python3
"""Speed Ladder sound (synthesised, no licences). usage: mix.py <out.wav>
Hit budget: frame 0 (small), the flash/vanish at 1.55 s (second), the malaria number at 10.0 s (biggest). Held-breath silence 8.8-9.2 s.
Phones: sub only on the hit bus; everything else is high-passed at 90 Hz."""
import sys, wave
import numpy as np
SR=44100; T=14.05; N=int(T*SR); rng=np.random.default_rng(7)
def tt(n): return np.arange(n)/SR
def fftf(x,lo,hi,soft=0.15):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR)
    m=np.ones_like(f)
    if lo>0: m*=np.clip((f-lo*(1-soft))/(lo*soft*2),0,1)
    if hi<SR/2: m*=np.clip((hi*(1+soft)-f)/(hi*soft*2),0,1)
    return np.fft.irfft(X*m,len(x))
def noise(n): return rng.standard_normal(n)
def env(n,a,d,pw=2.0):  # attack a s, decay d s
    t=tt(n); e=np.where(t<a,t/max(a,1e-6),np.exp(-(t-a)/max(d,1e-6))); return e
def place(buf,x,t0,g=1.0,pan=0.0):
    i=int(t0*SR); j=min(N,i+len(x)); 
    if i>=N or j<=0: return
    x=x[:j-i]*g; l=np.cos((pan+1)*np.pi/4); r=np.sin((pan+1)*np.pi/4)
    buf[0,i:j]+=x*l; buf[1,i:j]+=x*r
def stereo_noise(n,lo,hi,g):
    return np.stack([fftf(noise(n),lo,hi),fftf(noise(n),lo,hi)])*g
def swell(n,peak,pw=2.0):
    t=np.linspace(0,1,n); return np.where(t<peak,(t/peak)**pw,((1-t)/(1-peak))**pw)
hit=np.zeros((2,N)); sfx=np.zeros((2,N)); bed=np.zeros((2,N)); air=np.zeros((2,N))
def boom(t0,size):
    n=int(2.6*SR); t=tt(n)
    crack=fftf(noise(n),2500,12000)*np.exp(-t/0.018)*0.9
    f=90+230*np.exp(-t/0.09); ph=2*np.pi*np.cumsum(f)/SR
    body=np.tanh(2.2*np.sin(ph))*np.exp(-t/0.55)*0.9
    gong=sum(np.sin(2*np.pi*fq*t)*np.exp(-t/dd)*a for fq,dd,a in ((181,1.3,.35),(271,1.0,.3),(412,0.7,.25),(533,.5,.18)))
    sub=np.sin(2*np.pi*(48+30*np.exp(-t/0.2))*t)*np.exp(-t/0.9)*0.9
    x=(crack*0.7+body+gong*0.45)*size
    place(hit,x,t0,1.0); place(hit,sub*size,t0,0.55)
    # reverse suck before the hit, vacuum 60 ms
    m=int(0.42*SR); s=fftf(noise(m),300,5000)*np.linspace(0,1,m)**2.5; s[-int(0.06*SR):]=0
    place(sfx,s,t0-0.42,0.32*size)
def whine(t0,t1,f0,f1,g,swarm=10):
    n=int((t1-t0)*SR); t=tt(n); out=np.zeros(n)
    for k in range(swarm):
        fk=(f0+(f1-f0)*t/(t1-t0))*(1+rng.uniform(-0.07,0.07)); vib=1+0.012*np.sin(2*np.pi*rng.uniform(5,9)*t+rng.uniform(0,6.28))
        ph=2*np.pi*np.cumsum(fk*vib)/SR
        out+=(np.sin(ph)+0.45*np.sin(2*ph)+0.2*np.sin(3*ph))*rng.uniform(0.5,1)
    return out/swarm
def pings(t0,t1,count,gain,lo=2200,hi=6500,decay=0.12):
    for _ in range(count):
        ts=rng.uniform(t0,t1); f=rng.uniform(lo,hi); d=int(0.5*SR); t=tt(d)
        x=np.sin(2*np.pi*f*t)*np.exp(-t/decay)*np.exp(-5*t)**0.0
        place(sfx,x*gain*rng.uniform(0.4,1),ts,1.0,rng.uniform(-0.9,0.9))
# ---- Speed Ladder cues. Stops land at 1.6 / 3.4 / 5.0 / 6.8, held breath 8.6-9.1, hero hit 9.1, twist 11.2, loop 13.5
def rush(t0,dur,f0,f1,g,pan=0.0):
    n=int(dur*SR); t=tt(n); x=noise(n)
    # sweep a band by crossfading three static bands (cheap, stable)
    lo=fftf(x,f0*0.6,f0*1.4); hi=fftf(x,f1*0.6,f1*1.4); p=np.linspace(0,1,n)
    y=(lo*(1-p)+hi*p)*swell(n,0.5,1.6); place(sfx,y,t0,g,pan)
def ping(t0,f,g=0.12,dec=0.35):
    d=int(1.2*SR); t=tt(d); place(sfx,(np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*2*f*t))*np.exp(-t/dec),t0,g,0.1)
def ticks(t0,t1,n,g=0.05):
    for k in range(n):
        ts=t0+(t1-t0)*(k/n)**0.8; d=int(0.02*SR); tb=tt(d); place(sfx,fftf(noise(d),2500,9000)*np.exp(-tb/0.006),ts,g)
# hook: frame-0 hit + wind rush building
boom(0.0,0.35); rush(0.0,1.7,500,1100,0.30)
# stops: pass-by whoosh, ring ping on the pentatonic ladder, counter ticks
rush(1.45,1.5,400,900,0.30);  ping(1.95,660);  ticks(1.9,2.3,10)
rush(3.25,1.3,900,2200,0.34); ping(3.75,784);  ticks(3.7,4.1,10)
m=int(0.012*SR); place(sfx,fftf(noise(m),3000,11000)*np.exp(-tt(m)/0.003),3.5,0.45)                 # bullet crack
rush(4.85,1.7,120,700,0.36);  ping(5.35,988);  ticks(5.3,5.7,10)
n=int(1.6*SR); t=tt(n); place(bed,np.sin(2*np.pi*(70+30*t)*t)*swell(n,0.6,1.2)*0.5,5.0,0.12)        # deep, long: you
# parker: shepard riser 6.8-8.6
n=int(1.8*SR); t=tt(n); sh=np.zeros(n)
for k in range(6):
    f=200*2**(k+ (t/1.8)*1.0); fw=np.where(f>8000,0,f); amp=np.exp(-0.5*((np.log2(np.maximum(f,1))-np.log2(900))/1.3)**2)
    sh+=np.sin(2*np.pi*np.cumsum(f)/SR)*amp
place(sfx,sh*swell(n,0.85,1.3)*0.16,6.8,1.0); ping(7.35,1175); ticks(7.3,7.7,10)
# held breath 8.6-9.1: a reversed suck into the hit
m=int(0.38*SR); s=fftf(noise(m),300,6000)*np.linspace(0,1,m)**2.4; place(sfx,s,8.72,0.4)
# hero hit: light
boom(9.1,1.0); n=int(2.6*SR); t=tt(n); place(bed,fftf(noise(n),70,320)*np.exp(-t/1.2),9.15,0.22)
pings_=[1500,2200,3300,4400]
for k,f in enumerate(pings_): ping(9.15+0.1*k,f,0.05,0.5)
ticks(9.6,10.0,12,0.045)
# twist: thin stretching tone, no hits
n=int(2.3*SR); t=tt(n); f=300*2**(2.0*t/2.3); tone=np.sin(2*np.pi*np.cumsum(f)/SR)*(1+0.2*np.sin(2*np.pi*5*t))
place(bed,fftf(tone,200,3000)*swell(n,0.7,1.4),11.2,0.16)
for ts in (12.0,12.3,12.55,12.8,13.0): ping(ts,rng.uniform(1800,3200),0.04,0.15)
# loop: rising rush into frame 0
rush(13.35,0.7,500,1400,0.34)
# ---- held-breath duck 8.55-9.1 (everything except the hit bus), then side-chain dip after the hero hit
duck=np.ones(N); a,b=int(8.62*SR),int(9.05*SR); duck[a:b]=0.02
duck[int(8.52*SR):a]=np.linspace(1,0.02,a-int(8.52*SR)); duck[b:int(9.1*SR)]=np.linspace(0.02,1,int(9.1*SR)-b)
i=int(9.1*SR); j=int(10.0*SR); duck[i:j]*=np.linspace(0.6,1,j-i)
# ---- bass management: HPF everything but the hit bus at 90 Hz, mix, soft clip
def hp(x): return np.stack([fftf(x[0],90,SR/2),fftf(x[1],90,SR/2)])
mix=hit*0.95+(hp(sfx)*duck+hp(bed)*duck+hp(air))
mix=np.tanh(1.15*mix)/np.tanh(1.15)
mix*=0.88/np.max(np.abs(mix))
fade=np.ones(N); fade[:int(0.005*SR)]=np.linspace(0,1,int(0.005*SR)); fade[-int(0.02*SR):]=np.linspace(1,0,int(0.02*SR)); mix*=fade
pcm=(mix.T*32767).astype('<i2')
with wave.open(sys.argv[1],'wb') as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(pcm.tobytes())
print('wrote',sys.argv[1],round(N/SR,2),'s peak',np.max(np.abs(mix)).round(3))
