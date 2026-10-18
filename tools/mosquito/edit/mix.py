#!/usr/bin/env python3
"""Synthesised sound design for the mosquito Reel (no samples, so no licences). usage: mix.py <out.wav>
Hit budget: frame 0 (small), the flash/vanish at 1.55 s (second), the malaria number at 10.0 s (biggest). Held-breath silence 8.8-9.2 s.
Phones: sub only on the hit bus; everything else is high-passed at 90 Hz."""
import sys, wave
import numpy as np
SR=44100; T=32.4; N=int(T*SR); rng=np.random.default_rng(7)
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
# ---- 0-3.2 hook
w=whine(0,1.55,470,560,1.0); w*=np.linspace(0.55,1,len(w))**1.2
place(bed,fftf(w,200,3500),0.0,0.20,-0.1)
glow=fftf(noise(int(0.5*SR)),1500,9000)*swell(int(0.5*SR),0.95,2.5); place(sfx,glow,1.05,0.10)   # glow swell
boom(0.0,0.35); boom(1.55,0.8)
pings(1.7,3.2,140,0.045)   # glowing particles
# ---- 3.2-5.8 Earth pulse
n=int(2.6*SR); t=tt(n)
place(bed,np.sin(2*np.pi*44*t)*0.5*swell(n,0.45)+fftf(noise(n),400,2500)*0.03*swell(n,0.5),3.2,0.35)
p=int(1.4*SR); tp=tt(p); pulse=np.sin(2*np.pi*(78-30*tp/1.4)*tp)*swell(p,0.35,1.6)
place(sfx,fftf(pulse,90,400),3.5,0.55)
# ---- 5.3-8.8 cloud wipe then tundra wind
n=int(1.1*SR); place(sfx,fftf(noise(n),350,2200)*swell(n,0.35,1.5),5.25,0.22)
n=int(3.6*SR); wind=fftf(noise(n),120,900)*(0.6+0.4*np.sin(2*np.pi*0.23*tt(n)))*swell(n,0.3,0.8); place(bed,wind,5.4,0.10)
# ---- 8.8-9.2 held breath: bed ducked later; 9.2-13.7 malaria hit
boom(10.0,1.0)
n=int(3.0*SR); t=tt(n); place(bed,fftf(noise(n),70,320)*np.exp(-t/1.2),10.05,0.22)
# ---- 13.7-16.2 dusk water + wind
n=int(2.6*SR); place(bed,fftf(noise(n),150,700)*(0.7+0.3*np.sin(2*np.pi*0.4*tt(n)))*swell(n,0.4,0.9),13.7,0.09)
place(air,fftf(noise(n),3000,9000)*0.015*swell(n,0.5),13.7,1.0)
# ---- 16.2-18.7 underwater
n=int(2.6*SR); t=tt(n); place(bed,fftf(noise(n),80,420)*0.5*swell(n,0.4,0.9),16.2,0.20)
for _ in range(9):
    ts=rng.uniform(16.3,18.5); d=int(0.18*SR); tb=tt(d); f=rng.uniform(380,900)*(1+2*tb/0.18)
    place(sfx,np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tb/0.05)*0.12,ts,1.0,rng.uniform(-0.8,0.8))
# ---- 18.7-22.3 orchid dissolve + chime on SAFE
n=int(2.4*SR); place(sfx,fftf(noise(n),1800,7000)*swell(n,0.4,1.4),19.8,0.07)
pings(20.0,21.6,26,0.07,1200,3200,0.25)
for f,dl in ((880,0),(1320,0.09)):
    d=int(1.1*SR); tb=tt(d); place(sfx,np.sin(2*np.pi*f*tb)*np.exp(-tb/0.35)*0.16,20.95+dl,1.0,0.2)
# ---- 22.3-25.8 year 10: thin insect hum rising
for _ in range(260):
    ts=rng.uniform(22.3,25.8); dens=(ts-22.3)/3.5
    if rng.uniform()>0.25+0.75*dens: continue
    d=int(rng.uniform(0.05,0.14)*SR); tb=tt(d); f=rng.uniform(1000,2600)
    place(sfx,np.sin(2*np.pi*f*tb*(1+0.03*np.sin(40*tb)))*np.sin(np.pi*tb/(d/SR))*0.05,ts,1.0,rng.uniform(-0.9,0.9))
n=int(3.5*SR); place(bed,np.sin(2*np.pi*55*tt(n))*0.4*swell(n,0.7,1.0),22.3,0.12)
# ---- 25.8-29.8 closing pad
n=int(4.4*SR); t=tt(n); pad=sum(np.sin(2*np.pi*f*t+rng.uniform(0,6))*a for f,a in ((110,.5),(165,.4),(220,.35),(277.2,.22),(440,.1)))
pad*=swell(n,0.55,1.4)*(1+0.12*np.sin(2*np.pi*0.35*t)); place(bed,pad,25.7,0.20)
place(air,fftf(noise(n),2500,9000)*swell(n,0.6)*0.012,25.8,1.0)
# ---- 29.8-32.3 whine returns and rises into frame 0 (same level as t=0 start)
n=int(2.5*SR); w2=whine(0,2.5,430,470,1.0)[:n]*np.linspace(0,0.55,n)**1.2*1.0
place(bed,fftf(w2,200,3500),29.8,0.20,0.1)
# ---- held-breath duck: pull everything except hit to near silence 8.7-9.2
duck=np.ones(N); a,b=int(8.55*SR),int(9.25*SR); duck[a:b]=0.01
duck[int(8.45*SR):a]=np.linspace(1,0.01,a-int(8.45*SR)); duck[b:int(9.35*SR)]=np.linspace(0.01,1,int(9.35*SR)-b)
# hit bus: small side-chain duck of beds 0.25 s after each hit
for th,dep in ((1.55,0.45),(10.0,0.35)):
    i=int(th*SR); j=int((th+0.9)*SR); duck[i:j]*=np.linspace(1-dep,1,j-i)
# ---- bass management: HPF everything but the hit bus at 90 Hz, mix, soft clip
def hp(x): return np.stack([fftf(x[0],90,SR/2),fftf(x[1],90,SR/2)])
mix=hit*0.95+(hp(sfx)+hp(bed)*duck+hp(air))
mix=np.tanh(1.15*mix)/np.tanh(1.15)
mix*=0.88/np.max(np.abs(mix))
fade=np.ones(N); fade[:int(0.005*SR)]=np.linspace(0,1,int(0.005*SR)); fade[-int(0.02*SR):]=np.linspace(1,0,int(0.02*SR)); mix*=fade
pcm=(mix.T*32767).astype('<i2')
with wave.open(sys.argv[1],'wb') as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(pcm.tobytes())
print('wrote',sys.argv[1],round(N/SR,2),'s peak',np.max(np.abs(mix)).round(3))
