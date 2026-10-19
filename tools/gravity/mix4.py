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
# 5. "one metre" chime at 5.4
def bell(f,d=2.0,g=0.12):
    n=int(d*SR); x=np.arange(n)/SR; return sum(np.sin(2*np.pi*f*m*x)*a*np.exp(-x/(d/3.2)/(1+0.4*i)) for i,(m,a) in enumerate([(1,1),(2.76,0.5),(5.4,0.25)]))*g
b=at(bell(880,2.4,0.14),5.4); add(b,-0.2); add(reverb(b,2.0,0.5),0)
# 6. the float 5.4-15: pad, air, whooshes, pings, sub drone
fl=win(5.4,TF+0.05,1.6,0.04)
pad=sum(np.sin(2*np.pi*f*t+k)*a for k,(f,a) in enumerate([(220,.5),(277.2,.35),(329.6,.4),(493.9,.22),(659.3,.12)]))*fl*(0.8+0.2*np.sin(2*np.pi*0.22*t))*0.07
add(pad,-0.1); add(reverb(pad,2.4,0.6),0.1)
add(np.sin(2*np.pi*55*t)*fl*0.10,0); add(bp(noise(),500,3500)*fl*0.05,-0.3); add(bp(noise(),500,3500)*fl*0.05,0.3)
tw=5.9
while tw<14.6:
    d=rng.uniform(0.7,1.3); n=int(d*SR); x=np.arange(n)/SR; w=noise(n); c=rng.uniform(600,2400)
    w=bp(w,c*0.5,c*2.2)*np.sin(np.pi*x/d)**2*0.25*(0.5+0.5*(tw-5.9)/8.7)
    p=rng.choice([-0.8,0.8]); s=np.linspace(p,-p,n); i=int(tw*SR)
    Lp=np.zeros(N); Rp=np.zeros(N); Lp[i:i+n]=w*(0.5-s*0.5); Rp[i:i+n]=w*(0.5+s*0.5); L+=Lp*1.4; R+=Rp*1.4
    tw+=rng.uniform(0.55,1.2)
for k in range(14):
    f=rng.choice([1319,1760,1976,2637,3136]); add(at(bell(f,1.4,0.035),6.3+k*0.62+rng.uniform(0,0.2)),rng.uniform(-.8,.8))
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
