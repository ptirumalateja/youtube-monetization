#!/usr/bin/env python3
"""Gravity reel sound, fully synthesised (no third-party samples, so no credits needed). usage: mix.py <out.wav>
0-1.8 city murmur + soft pad | 1.8 one low hit, then near silence | 2.2-5.2 slow swell | 5-14 airy float pad with slow shimmer | 14.2-16 hollow tail."""
import sys, wave, numpy as np
SR=44100; T=20.0; N=int(T*SR); rng=np.random.default_rng(5); t=np.arange(N)/SR
def lp(x,fc,order=2):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); return np.fft.irfft(X/(1+(f/fc)**(2*order)),len(x))
def hp(x,fc): return x-lp(x,fc)
def win(a,b,fi,fo): return np.clip((t-a)/fi,0,1)*np.clip((b-t)/fo,0,1)
n1=rng.standard_normal(N); n2=rng.standard_normal(N)
# city murmur: low-passed noise with slow wobble
mur=lp(n1,500)*(0.6+0.4*np.sin(2*np.pi*0.7*t)); mur/=np.abs(mur).max()
L=mur*0.22*win(0,2.8,0.3,0.6); R=lp(n2,500)*0.22/np.abs(lp(n2,500)).max()*win(0,2.8,0.3,0.6)
pad=lambda f,a:np.sin(2*np.pi*f*t)*a
# soft pad (A2 + E3), present while gravity is on, then returns as the float pad
env=win(0,20,0.5,2.6)
base=(pad(110,.5)+pad(164.8,.3)+pad(110.6,.4))*env*0.10
# the switch: low drop + thump + air
h0=2.2; th=np.clip(t-h0,0,None); hit=np.sin(2*np.pi*(34+60*np.exp(-th/0.12))*th)*np.exp(-th/0.55)*(t>=h0)
hit=np.tanh(1.4*hit)*0.55+lp(n1,300)*np.exp(-th/0.25)*(t>=h0)*0.25
# swell 2.2-5.2: noise brightens and rises
sw=np.clip((t-2.6)/3.2,0,1); sn=(hp(lp(n2,500),200)*(1-sw)+hp(lp(n2,2500),200)*sw*0.7+hp(lp(n2,6000),800)*sw**2*0.5)*(sw**1.6)*win(2.6,6.0,0.2,0.5)
sn=sn/np.abs(sn).max()*0.28
rise=np.sin(2*np.pi*np.cumsum(110+220*np.clip((t-2.6)/3.2,0,1)**2)/SR)*win(2.6,5.8,0.4,0.3)*0.07
# float pad 5-14: higher, wide, slow shimmer
fl=win(5.4,17.4,1.5,2.0)
fp=sum(np.sin(2*np.pi*f*t+k)*a for k,(f,a) in enumerate([(220,.5),(329.6,.4),(440,.25),(659.3,.12)]))*fl*(0.8+0.2*np.sin(2*np.pi*0.25*t))*0.07
air=hp(lp(rng.standard_normal(N),3000),500)*fl*0.07
airR=hp(lp(rng.standard_normal(N),3000),500)*fl*0.07
# soft glassy ticks as things lift (sparse, quiet)
tick=np.zeros(N)
for k in range(26):
    c=int((5.8+k*0.42+rng.uniform(0,.12))*SR); d=np.arange(int(.35*SR))/SR; f=rng.choice([1320,1760,1975,2637]); s=np.sin(2*np.pi*f*d)*np.exp(-d/0.09)*0.02*(0.4+0.6*(k/26))
    if c+len(s)<N: tick[c:c+len(s)]+=s
# tail: hollow low tone
tl=win(17.0,20,0.3,1.6); tail=(pad(82.4,.5)+pad(123.5,.3))*tl*0.12
Lc=L+base+hit+sn+rise+fp+air+tick+tail; Rc=R+base*0.95+hit+sn*0.95+rise+fp*0.95+airR+np.roll(tick,300)+tail
M=np.stack([Lc,Rc]); M=np.tanh(M*1.2)/1.2
M*=0.9/np.abs(M).max()
M[:, :int(.01*SR)]*=np.linspace(0,1,int(.01*SR)); M[:,-int(.4*SR):]*=np.linspace(1,0,int(.4*SR))
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((M.T*32767).astype('<i2').tobytes()); w.close()
