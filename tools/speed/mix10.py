#!/usr/bin/env python3
"""Speed Ladder v9 sound: cinematic hits + risers (no tones, no zaps, no pings, nothing above ~6 kHz). usage: mix10.py <out.wav>
Hit on every cut (sized up each tier), a noise riser into each cut, a warm low pad that opens with each tier, a soft low pulse on the 133 BPM beat that gives it rhythm,
held-breath silence, the biggest hit on light, then a hollow tail. All synthesised (no licences). Phones: sub only on the hit bus; the rest is high-passed at 90 Hz."""
import sys, wave
import numpy as np
SR=44100; T=13.05; N=int(T*SR); rng=np.random.default_rng(5); BEAT=0.45
def tt(n): return np.arange(n)/SR
def noise(n): return rng.standard_normal(n)
def fftf(x,lo,hi,soft=0.2):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); m=np.ones_like(f)
    if lo>0: m*=np.clip((f-lo*(1-soft))/(lo*soft*2),0,1)
    if hi<SR/2: m*=np.clip((hi*(1+soft)-f)/(hi*soft*2),0,1)
    return np.fft.irfft(X*m,len(x))
def swell(n,pk=0.8,pw=2.0): t=np.linspace(0,1,n); return np.where(t<pk,(t/pk)**pw,((1-t)/(1-pk))**pw)
def reverb(x,rt=1.2,wet=0.3,tail=1.8):
    n=int(tail*SR); t=tt(n); ir=fftf(noise(n),160,5000)*np.exp(-t/(rt/6.9)); ir[:int(0.012*SR)]=0; ir/=np.sqrt((ir**2).sum())+1e-9
    L=len(x)+n; y=np.fft.irfft(np.fft.rfft(x,L)*np.fft.rfft(ir,L),L)[:len(x)]; return x*(1-wet)+y*wet*2.0
B={k:np.zeros((2,N)) for k in ('hit','bed','air','pulse')}
def place(b,x,t0,g=1.0,pan=0.0):
    i=int(t0*SR); j=min(N,i+len(x))
    if i>=N or j<=i: return
    x=x[:j-i]*g; l=np.cos((pan+1)*np.pi/4); r=np.sin((pan+1)*np.pi/4); B[b][0,i:j]+=x*l; B[b][1,i:j]+=x*r
def hit(t0,size,tail=1.8):
    """warm cinematic impact: pitch-dropping sine body, a soft mid thud, a short low-passed noise burst, hollow room tail; no click above 5 kHz"""
    n=int(tail*SR); t=tt(n); f=30+88*np.exp(-t/0.16); body=np.tanh(1.8*np.sin(2*np.pi*np.cumsum(f)/SR))*np.exp(-t/0.85)
    mid=np.sin(2*np.pi*(118-50*np.minimum(t/0.14,1))*t)*np.exp(-t/0.22)
    burst=fftf(noise(n),120,4200)*np.exp(-t/0.10)*0.5
    place('hit',reverb(body*0.9+mid*0.55+burst,1.1,0.24,min(tail,1.6)),t0,size)
def riser(t0,dur,size,lo0=120,hi0=700,hi1=4500):
    """noise riser: low-passed, the cutoff and level sweeping up into the cut"""
    n=int(dur*SR); x=noise(n); out=np.zeros(n); k=6
    for i in range(k):
        a=int(n*i/k); b=int(n*(i+1)/k) if i<k-1 else n; c=hi0*(hi1/hi0)**((i+0.5)/k)
        seg=fftf(x[a:b],lo0,c); out[a:b]=seg
    out*=swell(n,0.97,2.4); place('air',out,t0,size)
def downlift(t0,dur,size):
    n=int(dur*SR); x=fftf(noise(n),140,3600)*np.exp(-tt(n)/(dur*0.5)); place('air',x,t0,size)
def pad(t0,dur,notes,size,open_=2200):
    n=int(dur*SR); t=tt(n); y=np.zeros(n)
    for f in notes:
        for dt in (-0.0025,0,0.0025): y+=np.sin(2*np.pi*f*(1+dt)*t+rng.uniform(0,6.28))
        y+=0.35*np.sin(2*np.pi*2*f*t+rng.uniform(0,6.28))
    y=fftf(y,70,open_)*swell(n,0.5,1.3); place('bed',reverb(y,1.8,0.4,2.0),t0,size)
def thump(t0,size,f=58):
    n=int(0.28*SR); t=tt(n); y=np.sin(2*np.pi*(f+36*np.exp(-t/0.04))*t)*np.exp(-t/0.09); y+=0.18*fftf(noise(n),90,700)*np.exp(-t/0.03); place('pulse',np.tanh(1.3*y),t0,size)
# ---- timeline: jet 0-0.9 | bullet 0.9-1.8 | Earth 1.8-3.6 | probe 3.6-5.4 | held 5.4-5.85 | light 5.85-8.1 | laps 8.1-10.8 | twist 10.8-12.6 | loop 12.6-13.05
hit(0.0,0.28,1.0)                                       # frame-0 hit, small
pad(0.0,1.2,(55,82.5),0.10,900)                         # jet: barely there, curious
riser(0.50,0.40,0.16)                                   # into the bullet cut
hit(0.9,0.42,1.3); pad(0.9,1.1,(55,82.5,110),0.12,1300) # bullet
riser(1.40,0.40,0.18)
hit(1.8,0.58,1.6); pad(1.8,2.0,(55,82.5,110,165),0.15,1800)   # Earth: wider, warmer
riser(2.4,1.2,0.14,100,500,3200)                       # long swell inside the Earth stop
riser(3.15,0.45,0.22)
hit(3.6,0.78,1.8); pad(3.6,2.0,(55,82.5,110,165,220),0.18,2400)   # probe: biggest of the ladder
riser(4.0,1.4,0.30,100,700,5200)                       # the long climb into the held breath
# soft low pulse on the beat gives the rhythm; it starts at the bullet cut and rises in level until the probe, then stops for the held breath
b=0.9; k=0
while b<5.38:
    thump(b+0.0,0.10+0.20*min(1.0,(b-0.9)/4.0),f=56+3*k); b+=BEAT; k+=1
# held breath 5.4-5.85: silence (a quiet suck would sit here, left out on purpose)
# ---- drop on light
hit(5.85,1.0,2.8)
n=int(1.8*SR); t=tt(n); place('air',reverb(fftf(noise(n),400,5200)*np.exp(-t/0.45),1.4,0.4,1.6),5.85,0.20)
downlift(5.9,2.0,0.10)                                  # everything falls away: "light has no sound"
n=int(2.2*SR); t=tt(n); place('bed',np.sin(2*np.pi*41*t)*swell(n,0.2,1.0)*0.7+0.4*np.sin(2*np.pi*82*t)*swell(n,0.2,1.0),5.95,0.10)
# ---- laps 8.1-10.8: a soft low thump per lap (7.5 per second, as one fast roll), one weight at 7.5
for k in range(7): thump(8.1+0.3+(k+1)/7.5,0.13+0.015*k,f=62+4*k)
riser(8.1,0.45,0.12,100,600,2600)
hit(9.4,0.46,1.4)
pad(8.1,2.7,(55,82.5,110,165),0.14,1800)
# ---- twist 10.8-12.6: low unresolved pad, a slow stretching swell, nothing else
pad(10.8,2.0,(49,73.5,98,147),0.15,1400)
riser(10.9,1.6,0.10,100,300,2200)
# ---- loop: rising air into frame 0
riser(12.45,0.60,0.16,100,500,2400)
# ---- mix
duck=np.ones(N); a,b_=int(5.40*SR),int(5.85*SR); duck[a:b_]=0.0
def hp(x): return np.stack([fftf(x[0],90,SR/2),fftf(x[1],90,SR/2)])
mix=B['hit']*0.95+B['pulse']*0.9*duck+(hp(B['bed'])+hp(B['air']))*duck
mix=np.tanh(1.05*mix)/np.tanh(1.05); mix*=0.72/np.max(np.abs(mix))
fade=np.ones(N); fade[:int(0.004*SR)]=np.linspace(0,1,int(0.004*SR)); fade[-int(0.02*SR):]=np.linspace(1,0,int(0.02*SR)); mix*=fade
pcm=(mix.T*32767).astype('<i2')
with wave.open(sys.argv[1],'wb') as wf: wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(pcm.tobytes())
print('wrote',sys.argv[1],round(N/SR,2),'s peak',np.max(np.abs(mix)).round(3))
