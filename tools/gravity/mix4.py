#!/usr/bin/env python3
"""Gravity reel v4 sound (23.5 s), fully synthesised (no samples, no credits needed). usage: mix4.py <out.wav> [impact_time_s=18.70]
0-2.2 street bed | 1.7-2.2 suck | 2.2 switch boom | 2.6-5.4 riser + pulse | 5.4 chime | 5.4-15 float pad + whooshes | 15.0 gravity-back whomp + falling wind | 19.05 impact | 20.6-23 tail."""
import sys, wave, numpy as np
from numpy.fft import rfft, irfft, rfftfreq
SR=44100; T=23.5; N=int(T*SR); rng=np.random.default_rng(11); t=np.arange(N)/SR
SW, TF = 2.2, 15.0; TI = float(sys.argv[2]) if len(sys.argv)>2 else 18.70
def noise(n=N): return rng.standard_normal(n)
def lp(x,fc,o=2): X=rfft(x); f=rfftfreq(len(x),1/SR); return irfft(X/(1+(f/fc)**(2*o)),len(x))
def hp(x,fc,o=2): return x-lp(x,fc,o)
def bp(x,a,b): return hp(lp(x,b),a)
def win(a,b,fi,fo): return np.clip((t-a)/max(fi,1e-6),0,1)*np.clip((b-t)/max(fo,1e-6),0,1)
def at(sig,t0):   # place a short signal at time t0 into a full-length buffer
    o=np.zeros(N); i=int(t0*SR); n=min(len(sig),N-i); o[i:i+n]=sig[:n]; return o
def env(n,tau): return np.exp(-np.arange(n)/SR/tau)
def reverb(x,rt=1.8,wet=1.0):
    n=int(rt*SR*1.3); ir=noise(n)*np.exp(-np.arange(n)/SR/(rt/3)); ir=lp(ir,5000)*0.02
    X=rfft(x,N+n); Y=rfft(ir,N+n); return irfft(X*Y,N+n)[:N]*wet
L=np.zeros(N); R=np.zeros(N)
def add(x,p=0.0,g=1.0):   # p: -1 left .. +1 right
    global L,R; L+=x*g*(0.5-p*0.5)*1.4; R+=x*g*(0.5+p*0.5)*1.4
# 1. street bed 0-2.2 (traffic rumble, city hiss, two horns, footsteps)
bed=lp(noise(),220)*0.9+bp(noise(),400,2200)*0.05*(0.7+0.3*np.sin(2*np.pi*0.6*t))
bed/=np.abs(bed).max(); bed*=0.28*win(0,SW,0.15,0.04)
add(bed,0)
def horn(f,d): n=int(d*SR); x=np.arange(n)/SR; s=(np.sign(np.sin(2*np.pi*f*x))*0.4+np.sin(2*np.pi*f*x)+np.sin(2*np.pi*f*1.26*x)); return lp(s,1800)*np.minimum(1,x/0.02)*np.minimum(1,(d-x)/0.05)*0.05
add(at(horn(400,0.35),0.5),-0.5); add(at(horn(480,0.22),1.25),0.5)
for k in range(5): add(at(lp(noise(2000),700)*env(2000,0.018)*0.10,0.25+k*0.5),0.0)
# 2. pre-hit suck 1.55-2.2 (rising noise + sub swell)
sk=hp(noise(),200)*win(1.55,SW,0.65,0.0)**2*0.2; add(sk,0); add(np.sin(2*np.pi*38*t)*win(1.7,SW+0.05,0.5,0.05)*0.25,0)
# 3. the switch: boom + thump + glass shimmer, with a long tail
n=int(2.0*SR); tt=np.arange(n)/SR
boom=np.sin(2*np.pi*np.cumsum(28+70*np.exp(-tt/0.14))/SR)*np.exp(-tt/0.7)
boom=np.tanh(1.8*boom)*0.8+lp(noise(n),350)*np.exp(-tt/0.22)*0.5
hit=at(boom,SW); add(hit,0); add(reverb(hit,2.2,0.45),0)
sh=bp(noise(int(1.6*SR)),2500,9000)*np.exp(-np.arange(int(1.6*SR))/SR/0.5)*0.12; add(at(sh,SW),0.3)
# tinnitus ring after the hit
ring=np.sin(2*np.pi*3150*t)*win(SW+0.15,SW+2.3,0.2,2.0)*0.012; add(ring,0)
# 4. rising riser 2.6-5.4 with an accelerating pulse
sw=np.clip((t-2.6)/2.8,0,1); rn=noise()
ris=(bp(rn,150,600)*(1-sw)+bp(rn,300,2800)*sw*0.9+bp(rn,1500,9000)*sw**2*0.6)*sw**1.4*win(2.6,5.45,0.2,0.06)
ris/=np.abs(ris).max()+1e-9; add(ris*0.40,0)
f0=110*(2.0**(2*np.clip((t-2.6)/2.8,0,1))); add(np.sin(2*np.pi*np.cumsum(f0)/SR)*win(2.6,5.45,0.4,0.06)*0.08,0)
tp=2.7; k=0
while tp<5.3:
    nn=int(0.22*SR); x=np.arange(nn)/SR; add(at(np.sin(2*np.pi*55*x)*np.exp(-x/0.07)*0.35*(0.5+0.5*(tp-2.7)/2.6),tp),0); tp+=0.95-0.55*(tp-2.7)/2.6
# time-lapse acceleration: a rising airy sweep as the rate climbs, 5.6-9.0
ac=np.clip((t-5.6)/3.4,0,1); an=noise(); acc=(bp(an,400,1800)*(1-ac)+bp(an,1500,8000)*ac)*ac**1.2*win(5.6,9.2,0.3,0.5); acc/=np.abs(acc).max()+1e-9; add(acc*0.22,0)
# 5. "one metre" marker at 5.4 (a single cold bell)
def bell(f,d=2.0,g=0.12):
    n=int(d*SR); x=np.arange(n)/SR; return sum(np.sin(2*np.pi*f*m*x)*a*np.exp(-x/(d/3.2)/(1+0.4*i)) for i,(m,a) in enumerate([(1,1),(2.76,0.5),(5.4,0.25)]))*g
b=at(bell(622.3,2.4,0.10),5.4); add(b,-0.2); add(reverb(b,2.0,0.5),0)
# 6. the float 5.4-15: TENSION. Dissonant string-like cluster that tightens upward, a racing heartbeat, a Shepard-style endless rise,
#    ticking that accelerates with the time-lapse, distorted whooshes, then a 0.2 s hole of silence before gravity returns.
fl=win(5.4,TF-0.2,1.2,0.03); u=np.clip((t-5.4)/(TF-5.4),0,1)
def saw(f,vib=0.0):
    ph=np.cumsum(f*(1+vib*np.sin(2*np.pi*5.5*t)))/SR; return 2*(ph%1)-1
# minor-second / tritone cluster on a low drone, slowly creeping up in pitch and getting brighter and louder
base=82.4*(1+0.22*u**1.3)
clu=(saw(base,0.004)+saw(base*1.0595,0.004)*0.9+saw(base*1.4142,0.005)*0.6+saw(base*2.0*1.01,0.006)*0.5)
clu=(lp(clu,600)*(1-u)+lp(clu,2200)*u*0.8+lp(clu,5000)*u**2*0.5)*fl*(0.12+0.55*u**1.4)*(0.75+0.25*np.sin(2*np.pi*(5+9*u)*t))   # tremolo speeds up
add(clu*0.30,-0.15); add(reverb(clu*0.12,1.8,1.0),0.15)
# high strained "screech" glissando, entering around 9 s
hi=np.sin(2*np.pi*np.cumsum(1100+1900*u**2+30*np.sin(2*np.pi*7*t))/SR)*win(9.0,TF-0.2,2.0,0.03)*0.05*u; add(hi,0.3)
# Shepard-like rising tone: octave-spaced partials gliding up together under a bell-shaped weighting
sh=np.zeros(N); 
for k in range(6):
    f=55*(2.0**((k+ (u*2.0))%6)); wgt=np.exp(-0.5*((np.log2(f/700))/1.2)**2); sh+=np.sin(2*np.pi*np.cumsum(f)/SR)*wgt
add(sh*fl*0.05*(0.3+u),0)
# heartbeat: lub-dub, 70 -> 160 bpm
tp=5.5
while tp<TF-0.25:
    bpm=70+90*((tp-5.4)/(TF-5.4))**1.2; per=60/bpm
    for off,g in((0,1.0),(0.17*per/0.85*0.85,0.65)):
        nn=int(0.20*SR); x=np.arange(nn)/SR; add(at(np.sin(2*np.pi*(48+30*np.exp(-x/0.03))*x)*np.exp(-x/0.07)*g*(0.35+0.65*((tp-5.4)/(TF-5.4))),tp+off),0)
    tp+=per
# ticking: a dry clock/geiger tick whose rate climbs with the time-lapse
tk=5.6
while tk<TF-0.22:
    rate=2+10*((tk-5.6)/(TF-5.6))**1.6; nn=int(0.012*SR); add(at(hp(noise(nn),3000)*np.exp(-np.arange(nn)/SR/0.0025)*0.12,tk),rng.uniform(-.6,.6)); tk+=1/rate
# distorted whooshes sweeping past, denser and louder as you climb
tw=5.9
while tw<TF-0.4:
    d=rng.uniform(0.5,1.0); n=int(d*SR); x=np.arange(n)/SR; c=rng.uniform(500,3000)
    w=np.tanh(2.5*bp(noise(n),c*0.5,c*2.4))*np.sin(np.pi*x/d)**2*0.20*(0.4+0.8*((tw-5.9)/(TF-5.9)))
    p=rng.choice([-0.8,0.8]); s=np.linspace(p,-p,n); i=int(tw*SR); Lp=np.zeros(N); Rp=np.zeros(N); m=min(n,N-i)
    Lp[i:i+m]=w[:m]*(0.5-s[:m]*0.5); Rp[i:i+m]=w[:m]*(0.5+s[:m]*0.5); L+=Lp*1.4; R+=Rp*1.4
    tw+=rng.uniform(0.35,0.8)*(1-0.55*((tw-5.9)/(TF-5.9)))
# sub dread, building
add(np.sin(2*np.pi*(40+8*u)*t)*fl*(0.10+0.25*u),0)

# 7. gravity back on at 15.0: whomp, then falling wind that grows with speed
n=int(1.2*SR); tt=np.arange(n)/SR; wh=np.sin(2*np.pi*np.cumsum(60+90*np.exp(-tt/0.09))/SR)*np.exp(-tt/0.4); wh=np.tanh(1.6*wh)*0.85+bp(noise(n),200,5000)*np.exp(-tt/0.12)*0.6
add(at(wh,TF),0); add(reverb(at(wh,TF),1.6,0.35),0)
fall=np.clip((t-TF)/(TI-TF),0,1); wind=(bp(noise(),300,4000)*fall**1.5+hp(noise(),2000)*fall**2*0.5)*win(TF+0.1,TI,0.4,0.01); wind/=np.abs(wind).max()+1e-9; add(wind*0.40,0)
wf=1900-1400*fall; add(np.sin(2*np.pi*np.cumsum(wf)/SR)*win(TF+0.5,TI,0.8,0.01)*0.035*fall,0)
add(lp(noise(),120)*win(TF,TI,1.0,0.01)*0.6*fall**1.3,0)
# 8. impact at TI: kick, crack, crash, debris, then silence with a ring
n=int(1.6*SR); tt=np.arange(n)/SR
kick=np.sin(2*np.pi*np.cumsum(46+90*np.exp(-tt/0.05))/SR)*np.exp(-tt/0.45); kick=np.tanh(2.2*kick)
crack=hp(noise(n),1500)*np.exp(-tt/0.05)*0.9; crash=bp(noise(n),200,3500)*np.exp(-tt/0.35)*0.7
imp=kick*1.0+crack+crash; add(at(imp*0.9,TI),0); add(reverb(at(imp,TI),2.4,0.4),0)
for k in range(10): add(at(bp(noise(int(0.5*SR)),700,4200)*env(int(0.5*SR),0.14)*rng.uniform(0.15,0.3),TI+0.02+k*0.03),rng.uniform(-.9,.9))   # car crumple
for k in range(60): add(at(lp(noise(900),rng.uniform(1500,5000))*env(900,0.01)*rng.uniform(0.08,0.2),TI+0.05+rng.exponential(0.6)),rng.uniform(-.9,.9))
add(np.sin(2*np.pi*3150*t)*win(TI+0.4,TI+3.0,0.1,2.4)*0.012,0)
# 9. tail pad and a bell for the question, soft fade out
tl=win(TI+1.3,T,0.9,1.3); tail=(np.sin(2*np.pi*82.4*t)*.5+np.sin(2*np.pi*123.5*t)*.3+np.sin(2*np.pi*164.8*t)*.15)*tl*0.12; add(tail,0); add(reverb(tail,2.0,0.5),0)
qb=at(bell(659.3,2.6,0.10),TI+2.7); add(qb,0); add(reverb(qb,2.0,0.5),0.1)
M=np.stack([L,R]); M=np.tanh(M*1.15)/1.15; M*=0.92/np.abs(M).max()
M[:,:int(.01*SR)]*=np.linspace(0,1,int(.01*SR)); M[:,-int(.5*SR):]*=np.linspace(1,0,int(.5*SR))
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((M.T*32767).astype('<i2').tobytes()); w.close()
