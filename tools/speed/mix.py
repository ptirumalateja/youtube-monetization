#!/usr/bin/env python3
"""Speed Ladder sound (synthesised, no licences). usage: mix.py <out.wav>
Hit budget: frame 0 (small), the flash/vanish at 1.55 s (second), the malaria number at 10.0 s (biggest). Held-breath silence 8.8-9.2 s.
Phones: sub only on the hit bus; everything else is high-passed at 90 Hz."""
import sys, wave
import numpy as np
SR=44100; T=17.2; N=int(T*SR); rng=np.random.default_rng(7)
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
# ---- Speed Ladder v2 (17.1 s) on a 133 BPM grid (BEAT=0.45 s). Stops land at 1.8/3.6/5.4/7.2, held breath 9.0-9.45,
# DROP at 9.45, lap beat 11.7-14.4 (laps at 12.0 + k/7.5), atmospheric twist 14.4-16.65, loop rush into frame 0.
BEAT=0.45; kick_t=[]
def kick(t0,g):
    n=int(0.42*SR); t=tt(n); f=48+135*np.exp(-t/0.035); ph=2*np.pi*np.cumsum(f)/SR
    body=np.tanh(2.4*np.sin(ph))*np.exp(-t/0.17); sub=np.sin(2*np.pi*50*t)*np.exp(-t/0.22)*0.8
    click=fftf(noise(n),2500,9000)*np.exp(-t/0.004)*0.5
    place(hit,body+sub+click,t0,g); kick_t.append(t0)
def hat(t0,g,open_=False):
    n=int((0.16 if open_ else 0.05)*SR); t=tt(n); place(sfx,fftf(noise(n),6500,13000)*np.exp(-t/(0.05 if open_ else 0.014)),t0,g,rng.uniform(-0.3,0.3))
def clap(t0,g):
    n=int(0.28*SR); t=tt(n); x=np.zeros(n)
    for dl in (0,0.011,0.022): i=int(dl*SR); x[i:]+=fftf(noise(n-i),900,5500)*np.exp(-t[:n-i]/0.012)
    x+=fftf(noise(n),900,4500)*np.exp(-t/0.09)*0.6; place(sfx,x,t0,g)
def bassnote(t0,f,dur,g):
    n=int(dur*SR); t=tt(n); ph=2*np.pi*np.cumsum(f*(1+0.5*np.exp(-t/0.03)))/SR
    saw=sum(np.sin(h*ph)/h for h in range(1,7)); y=np.tanh(3.2*saw)*np.minimum(1,t/0.006)*np.exp(-t/(dur*0.8)); place(bed,y,t0,g)
def rush(t0,dur,f0,f1,g,pan=0.0):
    n=int(dur*SR); x=noise(n); p=np.linspace(0,1,n)
    y=(fftf(x,f0*0.6,f0*1.4)*(1-p)+fftf(x,f1*0.6,f1*1.4)*p)*swell(n,0.5,1.6); place(sfx,y,t0,g,pan)
def ping(t0,f,g=0.12,dec=0.35):
    d=int(1.2*SR); t=tt(d); place(sfx,(np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*2*f*t))*np.exp(-t/dec),t0,g,0.1)
def ticks(t0,t1,n,g=0.05):
    for k in range(n):
        ts=t0+(t1-t0)*(k/n)**0.8; d=int(0.02*SR); tb=tt(d); place(sfx,fftf(noise(d),2500,9000)*np.exp(-tb/0.006),ts,g)
# ---- hook 0-1.8: frame-0 hit + rising wind rush, groove not started yet
# hook (new coords 0-1.35): line-up with the frame-0 hit, warp tunnel punch at 0.45 (riser + tone sweep + ring pings), jet pulls out into the groove
import os
if os.environ.get('HOOK','A') in ('B','C'):
    # B: the warp is already running at frame 0 (boom + continuous brightening whoosh), the bullet punches out at 0.9 (small boom + air burst), reverse suck into the first beat
    boom(0.0,0.55)
    n=int(1.1*SR); t=tt(n); p=np.linspace(0,1,n)
    place(sfx,(fftf(noise(n),250,1000)*(1-p)+fftf(noise(n),2500,10000)*p)*swell(n,0.85,1.3),0.0,0.34)
    f=180*2**(3.4*t/1.1); place(sfx,np.sin(2*np.pi*np.cumsum(f)/SR)*swell(n,0.9,1.3)*0.12,0.0,1.0)
    for ts,fp in ((0.15,440),(0.45,554),(0.75,659)): ping(ts,fp,0.08,0.4)
    if os.environ.get('HOOK')=='C':   # line-up flash: three quick pops, then the probe, Earth and bullet are pulled into the tunnel
        for ts,fp in ((0.92,880),(1.0,1175),(1.08,1568)): ping(ts,fp,0.09,0.2)
        rush(1.05,0.3,500,3200,0.30)
    boom(0.9,0.45); m_=int(0.35*SR); place(sfx,fftf(noise(m_),1500,12000)*np.exp(-tt(m_)/0.09),0.9,0.3)
else:
    boom(0.0,0.5)
    n=int(0.95*SR); t=tt(n); p=np.linspace(0,1,n)
    place(sfx,(fftf(noise(n),300,1200)*(1-p)+fftf(noise(n),2500,9000)*p)*swell(n,0.8,1.5),0.4,0.34)           # tunnel whoosh, brightening
    f=200*2**(3.2*t/0.95); place(sfx,np.sin(2*np.pi*np.cumsum(f)/SR)*swell(n,0.85,1.3)*0.12,0.4,1.0)           # warp tone sweep
    for ts,fp in ((0.45,440),(0.67,554),(0.89,659)): ping(ts,fp,0.09,0.4)
    m_=int(0.3*SR); place(sfx,fftf(noise(m_),300,6000)*np.linspace(0,1,m_)**2.2,1.0,0.3)                      # reverse suck into the first beat
# ---- groove 1.8-9.0: kick on every beat (rising level), hats from 3.6 (8ths) and 7.2 (16ths), claps on beats 2 and 4 from 5.4
b=1.8; i=0
while b<8.99:
    kick(b,0.34+0.30*(b-1.8)/7.2); 
    if b>=3.6: hat(b+BEAT/2,0.05+0.05*(b-3.6)/5.4)
    if b>=7.2:
        hat(b+BEAT/4,0.06); hat(b+3*BEAT/4,0.06)
    if b>=5.4 and (round((b-5.4)/BEAT)%2==1): clap(b,0.20)
    b+=BEAT
# stop identity: pass-by whoosh + ring ping (pentatonic climb) + counter ticks
for a,fr_,to,pf in ((1.8,400,900,660),(3.6,900,2200,784),(5.4,120,700,988),(7.2,300,1800,1175)):
    rush(a-0.15 if a>1.8 else a,1.4,fr_,to,0.26); ping(a+0.35,pf,0.10); ticks(a+0.3,a+0.7,10,0.04)
m=int(0.012*SR); place(sfx,fftf(noise(m),3000,11000)*np.exp(-tt(m)/0.003),3.75,0.4)                 # bullet crack
n=int(1.8*SR); t=tt(n); place(bed,np.sin(2*np.pi*(70+30*t)*t)*swell(n,0.6,1.2)*0.5,5.4,0.12)        # earth: deep pad
# riser into the drop 7.2-9.0: shepard + rising noise + 16th-note snare roll accelerating, then reverse suck
n=int(1.8*SR); t=tt(n); sh=np.zeros(n)
for k in range(6):
    f=200*2**(k+(t/1.8)); amp=np.exp(-0.5*((np.log2(np.maximum(f,1))-np.log2(900))/1.3)**2); sh+=np.sin(2*np.pi*np.cumsum(f)/SR)*amp
place(sfx,sh*swell(n,0.9,1.3)*0.15,7.2,1.0)
for k in range(24):
    ts=7.65+1.35*(k/24)**0.75; clap(ts,0.05+0.12*k/24)
m=int(0.42*SR); s_=fftf(noise(m),300,6500)*np.linspace(0,1,m)**2.4; place(sfx,s_,8.58,0.42)
# ---- held breath 9.0-9.45: near-silence, one soft heartbeat tick at 9.225
d_=int(0.12*SR); place(sfx,np.sin(2*np.pi*70*tt(d_))*np.exp(-tt(d_)/0.04),9.225,0.18)
# ---- DROP 9.45: hero hit + crash + bass groove + kicks every beat at full level
boom(9.45,1.0); n=int(2.2*SR); t=tt(n); place(sfx,fftf(noise(n),5000,14000)*np.exp(-t/0.7),9.45,0.20)
place(bed,fftf(noise(n),70,320)*np.exp(-t/1.1),9.5,0.22)
for k in range(4): ping(9.5+0.1*k,[1500,2200,3300,4400][k],0.05,0.5)
b=9.45
while b<14.39:
    kick(b,0.78 if b<11.7 else 0.70)
    hat(b+BEAT/2,0.10); hat(b+BEAT/4,0.05); hat(b+3*BEAT/4,0.05)
    if round((b-9.45)/BEAT)%2==1: clap(b,0.30)
    bassnote(b+BEAT/2,55 if round((b-9.45)/BEAT)%4<2 else 49,0.24,0.30)    # off-beat sub bass, A1 then G1
    b+=BEAT
# ---- lap beat 11.7-14.4: one ping per lap, rising scale, lock-in hit at 7.5 laps (12.95)
for k,f in enumerate([523,587,659,784,880,1047,1175]): ping(12.0+(k+1)/7.5,f,0.12,0.22)
boom(12.95,0.45); ping(12.95,1568,0.14,0.8); ping(12.95,2093,0.08,0.8)
# ---- twist 14.4-16.65: groove drops out, quiet atmosphere (pad + slow stretching tone)
n=int(2.4*SR); t=tt(n); pad=sum(np.sin(2*np.pi*f*t+rng.uniform(0,6))*a for f,a in ((110,.5),(165,.4),(220,.35),(262,.2),(330,.12)))
place(bed,fftf(pad,90,1500)*swell(n,0.45,1.4),14.4,0.20)
f=300*2**(2.0*t/2.4); tone=np.sin(2*np.pi*np.cumsum(f)/SR)*(1+0.2*np.sin(2*np.pi*5*t)); place(bed,fftf(tone,200,3000)*swell(n,0.7,1.4),14.5,0.10)
for ts in (15.2,15.5,15.75,16.0,16.2): ping(ts,rng.uniform(1800,3200),0.035,0.15)
# ---- loop: rising rush into frame 0
rush(16.5,0.6,500,1400,0.34)
# ---- ducks: held breath, side-chain pump on every kick
duck=np.ones(N); a_,b_=int(8.9*SR),int(9.43*SR); duck[a_:b_]=0.02
duck[int(8.55*SR):a_]=np.linspace(1,0.02,a_-int(8.55*SR)) if False else duck[int(8.55*SR):a_]
for tk in kick_t:
    i=int(tk*SR); j=min(N,i+int(0.2*SR))
    if j>i: duck[i:j]=np.minimum(duck[i:j],np.linspace(0.45,1,j-i))
# ---- 15 s cut: remove whole beats from the 17.1 s grid so the groove stays aligned (hook 2 beats, jet 1, bullet 1, twist 1)
CUTS=[(1.35,1.8),(2.7,3.15),(4.5,4.95),(15.75,16.2)]
def cutbus(x):
    keep=[]; p=0.0; X=int(0.01*SR)
    for a,b in CUTS: keep.append((p,a)); p=b
    keep.append((p,N/SR)); out=None
    for (a,b) in keep:
        seg=x[...,int(a*SR):int(b*SR)].copy(); L=seg.shape[-1]
        if L>2*X:
            seg[...,:X]*=np.linspace(0,1,X); seg[...,-X:]*=np.linspace(1,0,X)
        out=seg if out is None else np.concatenate([out,seg],axis=-1)
    return out
hit,sfx,bed,air,duck=[cutbus(x) for x in (hit,sfx,bed,air,duck)]
N=int(15.3*SR); hit,sfx,bed,air,duck=[x[...,:N] for x in (hit,sfx,bed,air,duck)]
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
