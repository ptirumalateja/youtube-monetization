#!/usr/bin/env python3
"""v2 (anime look) sound for the mosquito Reel. Synthesised (no samples, so no licences). usage: mix.py <out.wav>
Hit budget: frame 0 (small), the flash/vanish at 1.55 s (second), the malaria number at 10.0 s (biggest). Held-breath silence 8.8-9.2 s.
Phones: sub only on the hit bus; everything else is high-passed at 90 Hz."""
import sys, wave
import numpy as np
SR=44100; T=31.95; N=int(T*SR); rng=np.random.default_rng(7)
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
# ---- v2 timeline: O 0-8 | D 7.7-11.9 | T 11.9-17.4 | H 17.4-20.6 | R 20.6-24.4 | M 24.4-31.9
# O 0-2.9 hook: wing whine, vanish between 1.8 and 2.7
w=whine(0,1.8,470,560,1.0); w*=np.linspace(0.55,1,len(w))**1.2
place(bed,fftf(w,200,3500),0.0,0.20,-0.1)
boom(0.0,0.30)
# the swarm goes quiet: soft breath-out at the vanish, particles
glow=fftf(noise(int(0.9*SR)),1500,9000)*swell(int(0.9*SR),0.5,2.0); place(sfx,glow,1.8,0.10)
boom(2.0,0.7)
pings(2.1,3.6,110,0.04)
# clouds whoosh 3.0-5.2 and rise
n=int(2.4*SR); place(sfx,fftf(noise(n),350,2400)*swell(n,0.45,1.5),3.0,0.20)
n=int(3.0*SR); wind=fftf(noise(n),120,900)*(0.6+0.4*np.sin(2*np.pi*0.23*tt(n)))*swell(n,0.4,0.8); place(bed,wind,3.0,0.09)
# Earth aura swell 5.2-7.8
n=int(2.6*SR); t=tt(n)
place(bed,np.sin(2*np.pi*44*t)*0.5*swell(n,0.5)+fftf(noise(n),400,2500)*0.03*swell(n,0.5),5.2,0.35)
p=int(1.5*SR); tp=tt(p); pulse=np.sin(2*np.pi*(78-30*tp/1.5)*tp)*swell(p,0.35,1.6)
place(sfx,fftf(pulse,90,400),5.4,0.55)
pings(5.3,7.6,26,0.03,1800,5200,0.2)
# D 7.7-11.9 malaria: held breath 7.65-8.5, biggest hit when the red lands (8.9)
boom(8.9,1.0)
n=int(2.8*SR); t=tt(n); place(bed,fftf(noise(n),70,320)*np.exp(-t/1.2),8.95,0.22)
# T 11.9-17.4 tundra: still air, then thin insect hum rising from 14.5
n=int(5.4*SR); place(bed,fftf(noise(n),120,800)*(0.6+0.4*np.sin(2*np.pi*0.2*tt(n)))*swell(n,0.3,0.9),11.9,0.09)
for _ in range(240):
    ts=rng.uniform(14.4,17.3); dens=(ts-14.4)/2.9
    if rng.uniform()>0.2+0.8*dens: continue
    d=int(rng.uniform(0.05,0.14)*SR); tb=tt(d); f=rng.uniform(1000,2600)
    place(sfx,np.sin(2*np.pi*f*tb*(1+0.03*np.sin(40*tb)))*np.sin(np.pi*tb/(d/SR))*0.045,ts,1.0,rng.uniform(-0.9,0.9))
# H 17.4-20.6 wetland: water, strike splash at ~18.1, ripples
n=int(3.2*SR); place(bed,fftf(noise(n),150,700)*(0.7+0.3*np.sin(2*np.pi*0.4*tt(n)))*swell(n,0.4,0.9),17.4,0.09)
place(air,fftf(noise(n),3000,9000)*0.015*swell(n,0.5),17.4,1.0)
m=int(0.35*SR); place(sfx,fftf(noise(m),600,4500)*np.exp(-tt(m)/0.09),18.15,0.22)
# R 20.6-24.4 orchid: soft ticks, shimmer as the mosquito dissolves (~23.2-24), chime on SAFE
n=int(2.4*SR); place(sfx,fftf(noise(n),1800,7000)*swell(n,0.5,1.4),22.4,0.07)
pings(22.6,24.2,26,0.07,1200,3200,0.25)
for f,dl in ((880,0),(1320,0.09)):
    d=int(1.1*SR); tb=tt(d); place(sfx,np.sin(2*np.pi*f*tb)*np.exp(-tb/0.35)*0.16,22.65+dl,1.0,0.2)
# M 24.4-31.9 closing: held tone over Earth, warm pad on the descent, whine returns into frame 0
n=int(4.4*SR); t=tt(n); pad=sum(np.sin(2*np.pi*f*t+rng.uniform(0,6))*a for f,a in ((110,.5),(165,.4),(220,.35),(277.2,.22),(440,.1)))
pad*=swell(n,0.55,1.4)*(1+0.12*np.sin(2*np.pi*0.35*t)); place(bed,pad,24.4,0.20)
place(air,fftf(noise(n),2500,9000)*swell(n,0.6)*0.012,24.6,1.0)
n=int(1.6*SR); place(sfx,fftf(noise(n),350,2200)*swell(n,0.4,1.5),27.4,0.18)
n=int(3.4*SR); w2=whine(0,3.4,430,470,1.0)[:n]*np.linspace(0,0.55,n)**1.2
place(bed,fftf(w2,200,3500),28.5,0.20,0.1)
# ---- held-breath duck 7.55-8.5 (everything but the hit bus)
duck=np.ones(N); a,b=int(7.65*SR),int(8.5*SR); duck[a:b]=0.02
duck[int(7.55*SR):a]=np.linspace(1,0.02,a-int(7.55*SR)); duck[b:int(8.8*SR)]=np.linspace(0.02,1,int(8.8*SR)-b)
for th,dep in ((2.0,0.45),(8.9,0.35)):
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
