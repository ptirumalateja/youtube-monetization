#!/usr/bin/env python3
"""Mosquito reel opening v7 sound (10 s), fully synthesised (no samples). usage: mix_open.py <out.wav> [fly_buzz.wav]  (the owner's real fly-buzz recording, if given, is the swarm bed)
0-1.9 rising swarm whine | 1.9-3.45 complete silence while they fall | 3.45-4.95 lift riser + settle boom | 5-6.5 space pad + sonar ping |
6.5-7.45 dive whoosh + grid ticks | 7.7-8.8 marker pings | 8.15-9.6 counter ticks | 9.6 hit."""
import sys, wave, subprocess, numpy as np
from numpy.fft import rfft, irfft, rfftfreq
SR=44100; T=10.0; N=int(T*SR); rng=np.random.default_rng(21); t=np.arange(N)/SR
def noise(n=N): return rng.standard_normal(n)
def lp(x,fc,o=2): X=rfft(x); f=rfftfreq(len(x),1/SR); return irfft(X/(1+(f/fc)**(2*o)),len(x))
def hp(x,fc,o=2): return x-lp(x,fc,o)
def bp(x,a,b): return hp(lp(x,b),a)
def win(a,b,fi,fo): return np.clip((t-a)/max(fi,1e-6),0,1)*np.clip((b-t)/max(fo,1e-6),0,1)
def at(sig,t0): o=np.zeros(N); i=int(t0*SR); n=min(len(sig),N-i); o[i:i+n]=sig[:n]; return o
def reverb(x,rt=1.8,wet=1.0):
    n=int(rt*SR*1.3); ir=noise(n)*np.exp(-np.arange(n)/SR/(rt/3)); ir=lp(ir,5000)*0.02; X=rfft(x,N+n); Y=rfft(ir,N+n); return irfft(X*Y,N+n)[:N]*wet
L=np.zeros(N); R=np.zeros(N)
def add(x,p=0.0,g=1.0):
    global L,R; L+=x*g*(0.5-p*0.5)*1.4; R+=x*g*(0.5+p*0.5)*1.4
# 1. swarm: many detuned partials rising in pitch and level, plus close hero flybys (Doppler-like pitch dip as they pass)
sw=win(0,1.9,0.05,0.0)*(0.25+0.75*np.clip(t/1.9,0,1)**1.3); pit=1+0.30*np.clip(t/1.9,0,1)
sw_sig=np.zeros(N)
for k in range(46):
    f=rng.uniform(330,980); am=0.5+0.5*np.sin(2*np.pi*rng.uniform(80,200)*t+rng.uniform(0,6)); sw_sig+=np.sin(2*np.pi*np.cumsum(f*pit*(1+0.006*np.sin(2*np.pi*rng.uniform(.5,3)*t)))/SR)*am*0.05
add(sw_sig*sw*(0.55 if len(sys.argv)>2 else 1.0),0)
for (t0,t1,f0,p0,p1) in [(0.2,1.5,540,-.8,.8),(0.9,1.9,470,.7,-.7)]:
    w=win(t0,t1,0.25,0.15); fr=f0*(1+0.18*np.cos(np.pi*np.clip((t-t0)/(t1-t0),0,1)))*pit; vib=1+0.01*np.sin(2*np.pi*7*t)
    hero=np.sin(2*np.pi*np.cumsum(fr*vib)/SR)*0.22+np.sin(2*np.pi*np.cumsum(fr*2.01*vib)/SR)*0.08; hero*=w*(0.6+0.4*np.sin(2*np.pi*110*t))
    pp=np.clip((t-t0)/(t1-t0),0,1)*(p1-p0)+p0; L+=hero*(0.5-pp*0.5)*1.4; R+=hero*(0.5+pp*0.5)*1.4
# 1b. the owner's real fly-buzz recording as the swarm bed: pitch and level rise to 1.9 s, then the pitch collapses as they lose flight
if len(sys.argv)>2:
    raw=subprocess.run(['ffmpeg','-v','error','-i',sys.argv[2],'-ac','2','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout
    fly=np.frombuffer(raw,np.float32).reshape(-1,2).T.copy(); fly=fly-fly.mean(axis=1,keepdims=True); nf=fly.shape[1]
    rate=np.where(t<1.9,1.0+0.28*(t/1.9),np.maximum(0.25,1.28*np.exp(-(t-1.9)*1.5))); pos=(np.cumsum(rate)/1.0)%(nf-2)   # source position, looped
    i0=pos.astype(int); fr=pos-i0; src=fly[:,i0]*(1-fr)+fly[:,i0+1]*fr
    xf=np.clip(np.minimum(pos,nf-pos)/(0.05*SR),0,1)   # soften the loop seam
    g=win(0,1.9,0.04,0.0)*(0.35+0.65*np.clip(t/1.9,0,1)**1.2)*np.where(t<1.9,1,np.clip(1-(t-1.9)/1.05,0,1)**1.2)
    for ch,(pp) in enumerate((-0.2,0.2)): add(hp(src[ch]*xf,110)*g*3.2,pp)
# 2. they all lose flight at 1.9 s: hard cut to silence: pitch collapses and decays, then water plinks, then a hard cut at 3.05
# complete silence from the instant they lose flight (no falling tone, no plinks)
cut=np.ones(N); cut[t>1.9]=0.0; cut[(t>1.88)&(t<=1.9)]=np.linspace(1,0,int((((t>1.88)&(t<=1.9)).sum())))
L*=cut; R*=cut
# 3. lift to orbit: sub riser, airy whoosh, settle boom at 4.95
riser=np.sin(2*np.pi*np.cumsum(38+60*np.clip((t-3.45)/1.5,0,1)**1.6)/SR)*win(3.45,4.95,0.5,0.03)*0.35; add(riser,0)
air=bp(noise(),300,5000)*win(3.45,4.95,0.9,0.1)**1.3*0.30; add(air,0.0)
n=int(2.4*SR); x=np.arange(n)/SR; boom=np.sin(2*np.pi*(46+40*np.exp(-x/0.18))*x)*np.exp(-x/0.9)*0.8+lp(noise(n),200)*np.exp(-x/0.3)*0.4
b=at(boom,4.95); add(b,0); add(reverb(b,2.0,0.4),0)
# 4. space: low pad and a sonar ping when the ring pulses
pad=(np.sin(2*np.pi*55*t)*.5+np.sin(2*np.pi*82.4*t)*.35+np.sin(2*np.pi*123.5*t)*.18)*win(4.9,6.9,0.8,0.5)*(0.8+0.2*np.sin(2*np.pi*.3*t))*0.10; add(pad,0); add(reverb(pad,2.5,0.6),0)
def ping(f,d=0.9,g=0.12):
    n=int(d*SR); x=np.arange(n)/SR; return (np.sin(2*np.pi*f*x)+0.35*np.sin(2*np.pi*f*2.76*x))*np.exp(-x/(d/4))*g
pg=at(ping(784,1.6,0.12),5.3); add(pg,0); add(reverb(pg,2.0,0.5),0); n=int(0.9*SR); xx=np.arange(n)/SR; add(at(np.sin(2*np.pi*np.cumsum(60+380*(xx/0.9)**2)/SR)*np.sin(np.pi*xx/0.9)**1.5*0.22,5.25),0)   # single white pulse
# 5. dive into Africa: rising whoosh, grid ticks
dv=win(6.5,7.5,0.5,0.15); sweep=(bp(noise(),400,2500)*(1-np.clip((t-6.5)/1.0,0,1))+bp(noise(),1200,9000)*np.clip((t-6.5)/1.0,0,1)*0.8)*dv*0.28; add(sweep,0)
tk=6.7
while tk<7.45: nn=int(0.012*SR); add(at(hp(noise(nn),3000)*np.exp(-np.arange(nn)/SR/0.003)*0.09,tk),rng.uniform(-.5,.5)); tk+=0.075
# 6. marker pings and the counter roll
for i in range(8): pg=at(ping(rng.choice([1319,1568,1760,2093]),0.7,0.07),7.7+i*0.17+0.1); add(pg,rng.uniform(-.6,.6)); add(reverb(pg,1.4,0.3),0)
def eo(x): return 1-(1-np.clip(x,0,1))**3
prev=0
for fr in np.arange(8.15,9.62,1/120):
    v=int(60*eo((fr-8.15)/1.45))
    if v!=prev: nn=int(0.02*SR); add(at(np.sin(2*np.pi*(1800-600*(fr-8.15))*np.arange(nn)/SR)*np.exp(-np.arange(nn)/SR/0.005)*0.10,fr),0); prev=v
# 7. the number lands: low hit, ring, soft tail
n=int(2.4*SR); x=np.arange(n)/SR; hit=np.sin(2*np.pi*(44+60*np.exp(-x/0.12))*x)*np.exp(-x/0.7)*0.9+lp(noise(n),300)*np.exp(-x/0.2)*0.4
hh=at(hit,9.55); add(hh,0); add(reverb(hh,1.8,0.4),0)
M=np.stack([L,R]); M=np.tanh(M*1.15)/1.15; M*=0.92/np.abs(M).max()
M[:,:int(.01*SR)]*=np.linspace(0,1,int(.01*SR)); M[:,-int(.3*SR):]*=np.linspace(1,0,int(.3*SR))
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((M.T*32767).astype('<i2').tobytes()); w.close()
