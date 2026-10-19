#!/usr/bin/env python3
"""Mosquito reel acts 2-6 sound (screen 10-25 s, written as a 15 s file), fully synthesised. usage: mix_acts.py <out.wav>
local time u = screen time - 10:
0-2.5 bite -> glass body -> interrupted (close whine, skin tick, flow, heartbeat, second whine, dissolve shimmer, sting) | 2.5-5 the night goes quiet (near silence, breathing) |
5-8 the pond: water, fish splash, swallow whoosh | 8-11.5 the orchid: glass pad, opening chimes, a drooping sigh | 11.2-12.2 zoom-through | 12-15 Earth half lit: cold pad, slow heartbeat, ghost ping, lone whine rising."""
import sys, wave, numpy as np
from numpy.fft import rfft, irfft, rfftfreq
SR=44100; T=15.0; N=int(T*SR); rng=np.random.default_rng(44); t=np.arange(N)/SR
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
def bell(f,d=1.5,g=0.1):
    n=int(d*SR); x=np.arange(n)/SR; return sum(np.sin(2*np.pi*f*m*x)*a*np.exp(-x/(d/3.2)/(1+0.4*i)) for i,(m,a) in enumerate([(1,1),(2.76,0.5),(5.4,0.25)]))*g
def thump(t0,f=50,g=0.5,d=0.2):
    n=int(d*SR); x=np.arange(n)/SR; return at(np.sin(2*np.pi*(f+30*np.exp(-x/.03))*x)*np.exp(-x/(d/3))*g,t0)
# ---- act 2 (0-2.5): the bite
add(bp(noise(),300,5000)*win(0.0,0.45,0.05,0.12)**1.2*0.28,0); add(np.sin(2*np.pi*np.cumsum(50+60*np.clip(t/0.4,0,1))/SR)*win(0,0.45,0.1,0.1)*0.3,0)   # zoom in
mw=win(0.35,1.05,0.15,0.1); add(np.sin(2*np.pi*np.cumsum(620-90*np.clip((t-.35)/.5,0,1)+9*np.sin(2*np.pi*7*t))/SR)*mw*0.30,-0.2)   # the close whine settling onto the skin
n=int(0.03*SR); add(at(hp(noise(n),1500)*np.exp(-np.arange(n)/SR/0.006)*0.35,0.64),0)   # skin touch
add(lp(noise(),500)*win(0.7,1.15,0.1,0.15)*(0.6+0.4*np.sin(2*np.pi*9*t))*0.10,0)   # liquid flow
add(bp(noise(),250,3500)*win(0.95,1.45,0.2,0.2)*0.25,0); add(np.sin(2*np.pi*np.cumsum(120-70*np.clip((t-.95)/.5,0,1))/SR)*win(0.95,1.5,0.1,0.2)*0.3,0)   # pull back
tp=1.4
while tp<2.1: add(thump(tp,48,0.38,0.2),0); add(thump(tp+0.17,44,0.26,0.18),0); tp+=0.56
tk=1.42
while tk<2.1: n=int(0.008*SR); add(at(hp(noise(n),3500)*np.exp(-np.arange(n)/SR/0.002)*0.07,tk),rng.uniform(-.6,.6)); tk+=0.075
w2=win(1.7,2.12,0.25,0.02); add(np.sin(2*np.pi*np.cumsum(440+90*np.clip((t-1.7)/.4,0,1)+7*np.sin(2*np.pi*6*t))/SR)*w2*0.20,0.5)   # the second mosquito approaching
for k in range(16): add(at(bell(rng.choice([2093,2637,3136,3951]),1.0,0.045),2.12+k*0.03+rng.uniform(0,.04)),rng.uniform(-.8,.8))   # it dissolves
n=int(0.3*SR); x=np.arange(n)/SR; add(at(np.sin(2*np.pi*(1400*np.exp(-x*7))*x)*np.exp(-x/.12)*0.25,2.14),0); add(thump(2.14,46,0.55,0.35),0)   # the interruption sting
# ---- act 3 (2.5-5): the night goes quiet
q=win(2.5,5.1,0.8,0.1); qp=(np.sin(2*np.pi*55*t)*.5+np.sin(2*np.pi*82.4*t)*.3)*q*0.06; add(qp,0); add(reverb(qp,2.4,0.5),0)
add(lp(noise(),400)*win(2.6,5.1,0.8,0.1)*0.035,0)
add(bp(noise(),200,2500)*win(3.1,3.9,0.4,0.3)*0.08,0)   # the push through the window
br=(0.5+0.5*np.sin(2*np.pi*0.28*t-1.2)); add(bp(noise(),250,1400)*win(3.6,5.0,0.5,0.4)*br*0.05,0.1)   # the child breathing
for k in range(5): n=int(0.02*SR); add(at(lp(noise(n),2500)*np.exp(-np.arange(n)/SR/0.004)*0.04,3.7+rng.uniform(0,1.2)),-0.4)   # lamp ticks
# ---- act 4 (5-8): the pond
add(lp(noise(),700)*win(5.0,8.2,0.5,0.4)*(0.6+0.4*np.sin(2*np.pi*.5*t))*0.07,0)
n=int(0.25*SR); x=np.arange(n)/SR; add(at(np.sin(2*np.pi*(320-140*x/.25)*x)*np.exp(-x/.09)*0.32,5.95),0.2)   # the fish leaves the water
add(at(lp(noise(int(0.35*SR)),1800)*np.exp(-np.arange(int(0.35*SR))/SR/0.1)*0.18,6.78),0.3)   # and lands, finding nothing
sw=bp(noise(),700,4500)*win(6.15,7.15,0.4,0.4)**1.2*0.20; pp=np.clip((t-6.15)/1.0,0,1)*2-1; L+=sw*(0.5-pp*0.5)*1.4; R+=sw*(0.5+pp*0.5)*1.4   # the swallow's dive
# ---- act 5 (8-11.5): the orchid opens, waits, no one comes; a petal droops
op=(np.sin(2*np.pi*329.6*t)*.4+np.sin(2*np.pi*493.9*t)*.25)*win(8.0,11.6,0.8,0.5)*0.05; add(op,0); add(reverb(op,2.6,0.6),0.1)
for k,f in enumerate([659.3,830.6,987.8,1318.5,1661.2]): bb=at(bell(f,1.8,0.07),8.3+k*0.27); add(bb,-0.4+k*0.2); add(reverb(bb,2.0,0.4),0)
n=int(0.7*SR); x=np.arange(n)/SR; add(at(np.sin(2*np.pi*(700-220*x/.7)*x)*np.sin(np.pi*x/.7)*0.07,10.35),0)   # the petal droops
# ---- act 6 (11.5-15): open grassland, golden hour; wind, grass, and one mosquito crossing then hovering towards us
add(bp(noise(),150,1100)*win(11.2,15.0,0.6,0.0)*(0.5+0.5*np.clip((t-11.2)/3.5,0,1))*(0.7+0.3*np.sin(2*np.pi*.21*t))*0.16,-0.1)
add(hp(noise(),2500)*win(11.4,15.0,0.8,0.0)*(0.5+0.5*np.sin(2*np.pi*.35*t+1))*0.03,0.1)
add(bp(noise(),300,4500)*win(11.2,11.9,0.3,0.3)*0.12,0)   # the soft rack-focus into the field
fm=win(11.5,15.0,0.5,0.0)*(0.25+0.75*np.clip((t-11.5)/3.5,0,1)**1.3); f=420+300*np.clip((t-11.5)/3.5,0,1)+60*np.exp(-np.clip(t-11.5,0,3)*1.1)*(t>11.5)
vib=1+0.012*np.sin(2*np.pi*6.5*t); mos=(np.sin(2*np.pi*np.cumsum(f*vib)/SR)*0.40+np.sin(2*np.pi*np.cumsum(f*2.01*vib)/SR)*0.14)*fm
pp=np.clip((t-11.5)/2.1,0,1)*1.2-0.8; L+=mos*(0.5-pp*0.5)*1.4; R+=mos*(0.5+pp*0.5)*1.4
M=np.stack([L,R]); M=np.tanh(M*1.15)/1.15; M*=0.92/np.abs(M).max()
M[:,:int(.01*SR)]*=np.linspace(0,1,int(.01*SR))
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((M.T*32767).astype('<i2').tobytes()); w.close()
