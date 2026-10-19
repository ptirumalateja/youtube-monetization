#!/usr/bin/env python3
"""Mosquito reel acts 2-8 sound (screen 10-26 s, written as a 16 s file), fully synthesised. usage: mix_acts.py <out.wav>
local time u = screen time - 10:
0-1 transmission hum + marker pings | 1.0 the wave: suck, thump, outward whoosh, then silence | 2.3-3.5 'But...' key ticks + low drone | 3-3.9 iris hush |
3.5-6 Arctic wind, pad, hoof thumps | 5.45-6.1 dive into the pool | 6-7.5 wetland: water, bird chirps, a fish bloop | 7.5-9.7 orchid: faint whine, dust shimmer |
9.7-10.7 zoom-through | 10-13 Earth: uncertain pad, edge pings, question-mark glides | 12.55-13.5 descent | 13.4-16 the lone mosquito whine rising to the end."""
import sys, wave, numpy as np
from numpy.fft import rfft, irfft, rfftfreq
SR=44100; T=16.0; N=int(T*SR); rng=np.random.default_rng(33); t=np.arange(N)/SR
def noise(n=N): return rng.standard_normal(n)
def lp(x,fc,o=2): X=rfft(x); f=rfftfreq(len(x),1/SR); return irfft(X/(1+(f/fc)**(2*o)),len(x))
def hp(x,fc,o=2): return x-lp(x,fc,o)
def bp(x,a,b): return hp(lp(x,b),a)
def win(a,b,fi,fo): return np.clip((t-a)/max(fi,1e-6),0,1)*np.clip((b-t)/max(fo,1e-6),0,1)
def at(sig,t0): o=np.zeros(N); i=int(t0*SR); n=max(0,min(len(sig),N-i)); o[i:i+n]=sig[:n]; return o
def reverb(x,rt=1.8,wet=1.0):
    n=int(rt*SR*1.3); ir=noise(n)*np.exp(-np.arange(n)/SR/(rt/3)); ir=lp(ir,5000)*0.02; X=rfft(x,N+n); Y=rfft(ir,N+n); return irfft(X*Y,N+n)[:N]*wet
L=np.zeros(N); R=np.zeros(N)
def add(x,p=0.0,g=1.0):
    global L,R; L+=x*g*(0.5-p*0.5)*1.4; R+=x*g*(0.5+p*0.5)*1.4
def ping(f,d=0.9,g=0.12):
    n=int(d*SR); x=np.arange(n)/SR; return (np.sin(2*np.pi*f*x)+0.35*np.sin(2*np.pi*f*2.76*x))*np.exp(-x/(d/4))*g
# 1. transmission: warm hum, pulse, marker pings; then the wave cuts everything at u=1.0
act=win(0,1.0,0.05,0.0)
add((np.sin(2*np.pi*196*t)*.5+np.sin(2*np.pi*293.7*t)*.3+np.sin(2*np.pi*98*t)*.5)*act*0.10,0)
for k in range(8):
    tp=0.05+k*0.125; n=int(0.2*SR); x=np.arange(n)/SR; add(at(np.sin(2*np.pi*(50+25*np.exp(-x/.03))*x)*np.exp(-x/.07)*0.35,tp)*1.0,0)
    if tp<1.0: add(at(ping(rng.choice([1319,1568,1760,2093]),0.6,0.08),tp+0.05),rng.uniform(-.7,.7))
suck=hp(noise(),400)*win(0.55,1.0,0.45,0.0)**2*0.22; add(suck,0)
n=int(2.2*SR); x=np.arange(n)/SR; th=np.sin(2*np.pi*(52+60*np.exp(-x/.12))*x)*np.exp(-x/.8)*0.9+lp(noise(n),300)*np.exp(-x/.25)*0.5
b=at(th,1.0); add(b,0); add(reverb(b,2.0,0.45),0)
wh=bp(noise(),500,6000)*win(1.0,1.9,0.0,0.9)*0.25; add(wh,0)
# 2. "But...": near silence, a low drone swelling, soft key ticks for each letter
for k in range(6): n=int(0.02*SR); add(at(hp(noise(n),1500)*np.exp(-np.arange(n)/SR/0.004)*0.12,2.55+k*0.12),0)
dr=np.sin(2*np.pi*40*t)*win(2.4,4.2,1.0,0.5)*0.22; add(dr,0)
# 3. iris reveal and the cold Arctic: wind, pad, hooves
iris=bp(noise(),300,4000)*win(3.0,3.9,0.5,0.4)*0.16; add(iris,0)
wind=(bp(noise(),120,900)*(0.7+0.3*np.sin(2*np.pi*0.23*t))+bp(noise(),900,2500)*0.2*(0.5+0.5*np.sin(2*np.pi*0.17*t+1)))*win(3.5,6.2,0.8,0.3)*0.20; add(wind,-0.1)
pad=(np.sin(2*np.pi*146.8*t)*.5+np.sin(2*np.pi*220*t)*.4+np.sin(2*np.pi*329.6*t)*.15)*win(3.6,6.1,1.0,0.4)*(0.8+0.2*np.sin(2*np.pi*.2*t))*0.05; add(pad,0); add(reverb(pad,2.4,0.6),0.1)
tp=3.7
while tp<5.5: n=int(0.05*SR); add(at(lp(noise(n),500)*np.exp(-np.arange(n)/SR/0.012)*rng.uniform(.04,.12),tp),rng.uniform(-.8,.8)); tp+=rng.uniform(.28,.55)
# 4. the dive into the pool, then the wetland: water, a few bird chirps, a bloop as the fish rises
dv=lp(noise(),3000)*win(5.45,6.15,0.6,0.1)**1.3*0.30; add(dv,0); n=int(0.25*SR); x=np.arange(n)/SR; add(at(np.sin(2*np.pi*(260-120*x*4)*x)*np.exp(-x/.07)*0.25,6.05),0)
water=lp(noise(),700)*win(6.05,7.7,0.15,0.4)*(0.6+0.4*np.sin(2*np.pi*.6*t))*0.14; add(water,0)
for tc in (6.3,6.45,6.85,7.05):
    n=int(0.09*SR); x=np.arange(n)/SR; add(at(np.sin(2*np.pi*(3400-1200*x/0.09)*x)*np.sin(np.pi*x/0.09)*0.08,tc),rng.uniform(-.8,.8))
n=int(0.2*SR); x=np.arange(n)/SR; add(at(np.sin(2*np.pi*(320-140*x/.2)*x)*np.exp(-x/.08)*0.3,6.62),0.3)
# 5. orchid: the mosquito's faint whine, then it dissolves into dust with a glassy shimmer
wn=win(7.55,8.62,0.5,0.03); add(np.sin(2*np.pi*np.cumsum(520+60*np.sin(2*np.pi*6*t))/SR)*wn*0.07,0.3)
od=(np.sin(2*np.pi*164.8*t)*.5+np.sin(2*np.pi*246.9*t)*.35)*win(7.5,10.0,0.8,0.4)*0.06; add(od,0); add(reverb(od,2.4,0.5),0)
for k in range(14): add(at(ping(rng.choice([2093,2637,3136,3951]),1.0,0.045),8.62+k*0.07+rng.uniform(0,.05)),rng.uniform(-.8,.8))
# 6. zoom-through to the planet, then the web: uncertain pad, edge pings, question-mark glides
zt=(bp(noise(),300,5000)*win(9.7,10.7,0.6,0.1)**1.2*0.25); add(zt,0); add(np.sin(2*np.pi*np.cumsum(40+55*np.clip((t-9.7)/1.0,0,1)**1.5)/SR)*win(9.7,10.8,0.6,0.2)*0.3,0)
cl=(np.sin(2*np.pi*110*t)*.5+np.sin(2*np.pi*116.5*t)*.4+np.sin(2*np.pi*164.8*t)*.3+np.sin(2*np.pi*174.6*t)*.25)*win(10.2,13.2,1.0,0.6)*(0.6+0.4*np.sin(2*np.pi*.25*t))*0.08; add(cl,0); add(reverb(cl,2.6,0.6),0.1)
for k in range(24): pg=at(ping(rng.choice([440,523,587,659,784,880]),1.1,0.05),10.35+rng.uniform(0,2.1)); add(pg,rng.uniform(-.8,.8)); add(reverb(pg,1.6,0.3),0)
for i in range(7):
    tq=10.9+i*0.33; n=int(0.3*SR); x=np.arange(n)/SR; add(at(np.sin(2*np.pi*(600+400*x/.3)*x)*np.sin(np.pi*x/.3)*0.05,tq),rng.uniform(-.6,.6))
# 7. descent to the marsh and the lone mosquito
ds=bp(noise(),200,4000)*win(12.55,13.55,0.5,0.15)*0.22; add(ds,0); add(np.sin(2*np.pi*np.cumsum(90-50*np.clip((t-12.6)/.9,0,1))/SR)*win(12.6,13.5,0.2,0.3)*0.25,0)
mw=win(13.4,16.0,1.2,0.0)*(0.10+0.9*np.clip((t-13.4)/2.6,0,1)**1.4); f=380+360*np.clip((t-13.4)/2.6,0,1)
mos=(np.sin(2*np.pi*np.cumsum(f*(1+0.012*np.sin(2*np.pi*6.5*t)))/SR)*0.42+np.sin(2*np.pi*np.cumsum(f*2.01*(1+0.012*np.sin(2*np.pi*6.5*t)))/SR)*0.15)*mw
add(mos,0.15)
mar=lp(noise(),600)*win(13.0,16.0,0.8,0.0)*0.08; add(mar,0)
M=np.stack([L,R]); M=np.tanh(M*1.15)/1.15; M*=0.92/np.abs(M).max()
M[:,:int(.01*SR)]*=np.linspace(0,1,int(.01*SR))
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((M.T*32767).astype('<i2').tobytes()); w.close()
