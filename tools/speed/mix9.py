#!/usr/bin/env python3
"""Speed Ladder v8 sound: the vortex and the aura ARE the sound (no pings, no drum machine, no sine arpeggios).
All synthesised from noise and filtered harmonics (no samples, no licences). usage: mix9.py <out.wav>
Timeline (s): jet 0-0.9 | bullet 0.9-1.8 | Earth 1.8-3.6 | Parker 3.6-5.4 | held breath 5.4-5.85 | light 5.85-8.1 | laps 8.1-10.8 | twist 10.8-12.6 | loop 12.6-13.05
Each tier is about +3 dB louder than the last (jet quiet and curious, probe at full).  Phones: sub only on the impact bus, everything else high-passed at 90 Hz."""
import sys, wave
import numpy as np
SR=44100; T=13.05; N=int(T*SR); rng=np.random.default_rng(31)
def tt(n): return np.arange(n)/SR
def noise(n): return rng.standard_normal(n)
def fftf(x,lo,hi,soft=0.15):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); m=np.ones_like(f)
    if lo>0: m*=np.clip((f-lo*(1-soft))/(lo*soft*2),0,1)
    if hi<SR/2: m*=np.clip((hi*(1+soft)-f)/(hi*soft*2),0,1)
    return np.fft.irfft(X*m,len(x))
def kf(keys,n=N):
    """keyframes [(t,value)...] -> per-sample array (linear)"""
    ts=[k[0] for k in keys]; vs=[k[1] for k in keys]; return np.interp(tt(n),ts,vs)
def sweep_bp(x,fc,bw=0.28,blk=2048):
    """band-pass noise whose centre frequency follows fc (per-sample array); overlap-add"""
    n=len(x); hop=blk//2; win=np.hanning(blk); out=np.zeros(n+blk); f=np.fft.rfftfreq(blk,1/SR); lf=np.log2(f+1)
    for s in range(0,n-blk,hop):
        c=max(30.0,fc[min(s+hop,n-1)]); m=np.exp(-0.5*((lf-np.log2(c))/bw)**2)
        out[s:s+blk]+=np.fft.irfft(np.fft.rfft(x[s:s+blk]*win)*m,blk)*win
    return out[:n]/0.75
def reverb(x,rt=1.1,wet=0.35,tail=1.6):
    n=int(tail*SR); t=tt(n); ir=fftf(noise(n),180,7000)*np.exp(-t/(rt/6.9)); ir[:int(0.01*SR)]=0; ir/=np.sqrt((ir**2).sum())+1e-9
    L=len(x)+n; y=np.fft.irfft(np.fft.rfft(x,L)*np.fft.rfft(ir,L),L)[:len(x)]
    return x*(1-wet)+y*wet*2.0
buses={k:np.zeros((2,N)) for k in ('imp','bed','tex','hf')}
def place(bus,x,t0,g=1.0,pan=0.0):
    i=int(t0*SR); j=min(N,i+len(x))
    if i>=N or j<=i: return
    x=x[:j-i]*g; l=np.cos((pan+1)*np.pi/4); r=np.sin((pan+1)*np.pi/4); buses[bus][0,i:j]+=x*l; buses[bus][1,i:j]+=x*r
def stereo(x,pan_hz=0.0,depth=0.0,ph=0.0):
    """slow rotating pan"""
    p=depth*np.sin(2*np.pi*pan_hz*tt(len(x))+ph); l=np.cos((p+1)*np.pi/4); r=np.sin((p+1)*np.pi/4); return np.stack([x*l,x*r])
def swell(n,pk=0.7,pw=2.0): t=np.linspace(0,1,n); return np.where(t<pk,(t/pk)**pw,((1-t)/(1-pk))**pw)
# ------------------------------------------------------------------ tier curve: +3 dB per tier (jet -12, bullet -9, Earth -6, probe 0)
TIER=kf([(0,0.40),(0.88,0.40),(0.92,0.48),(1.78,0.48),(1.82,0.62),(3.58,0.62),(3.62,1.0),(5.38,1.0),(5.4,0.0),(5.85,0.0),(5.88,0.5),(8.1,0.25),(8.2,0.5),(10.8,0.5),(10.9,0.30),(12.6,0.30),(13.05,0.25)])
SNAP=[0.9,1.8,3.6,5.85]
def duck_curve():
    d=np.ones(N)
    for s in (0.9,):   # 0.1 s of near-silence right before the bullet crack makes it hit harder
        a,b=int((s-0.1)*SR),int(s*SR); d[a:b]=0.08
    a,b=int(5.4*SR),int(5.85*SR); d[a:b]=0.0     # held breath
    return d
# ------------------------------------------------------------------ aura hum (magnetic hum): harmonics, pitch jumps up an octave at the bullet, slight detune shimmer
f0=kf([(0,98),(0.88,98),(0.92,196),(1.78,196),(1.82,147),(3.58,147),(3.62,262),(5.4,262),(5.85,98),(8.1,98),(10.8,82),(13.05,98)])
ph=2*np.pi*np.cumsum(f0)/SR; hum=np.zeros(N)
for h,a in ((1,1.0),(2,0.6),(3,0.45),(4,0.3),(5,0.22),(7,0.12)):
    hum+=a*np.sin(h*ph*(1+0.0012*h)+0.4*np.sin(2*np.pi*(0.3+0.1*h)*tt(N)))
hum=fftf(hum*(1+0.12*np.sin(2*np.pi*0.7*tt(N))),90,2600)*0.10
buses['bed']+=stereo(hum*TIER,0.35,0.5)
# ------------------------------------------------------------------ sub rumble (felt): 44 Hz with audible harmonics so phones can show it
sub=np.sin(2*np.pi*np.cumsum(kf([(0,44),(5.4,52),(13.05,44)]))/SR); sub=np.tanh(2.2*sub)*(0.8+0.2*np.sin(2*np.pi*0.5*tt(N)))
buses['imp']+=stereo(sub*TIER*0.18)
# ------------------------------------------------------------------ vortex: wind/whistle that follows the spin (centre frequency steps up with every tier), rotating pan
fc=kf([(0,420),(0.88,520),(0.92,1500),(1.78,1700),(1.82,1050),(3.58,1250),(3.62,2600),(5.38,3600),(5.85,900),(8.1,800),(10.8,300),(12.6,300),(13.05,420)])
wh=sweep_bp(noise(N),fc,0.22)*TIER*kf([(0,0.9),(5.4,1.0),(5.85,0.0),(5.88,0.6),(8.1,0.2),(13.05,0.3)])*1.4
wh*=1+0.25*np.sin(2*np.pi*kf([(0,1.5),(0.9,3.5),(1.8,2.0),(3.6,6.0),(5.4,6.0),(13.05,1.5)])*tt(N))
buses['tex']+=stereo(fftf(wh,150,9000)*0.5,0.6,0.7,1.0)
# ------------------------------------------------------------------ bullet: aura buzz (sparse electric zaps, density grows with tier) and the snap
def zaps(t0,t1,dens,g):
    t=t0
    while t<t1:
        t+=rng.exponential(1.0/dens); d=int(rng.uniform(0.006,0.03)*SR); x=fftf(noise(d),1500,9000)*np.exp(-tt(d)/0.01)
        place('hf',x,t,g*rng.uniform(0.4,1.0),rng.uniform(-0.8,0.8))
zaps(0.92,1.8,40,0.20); zaps(3.62,5.38,70,0.26); zaps(1.8,3.58,14,0.08); zaps(0.0,0.88,6,0.04)
# snap 1 (0.9): reversed cymbal swell into a dry rifle crack with a short room tail
n=int(0.22*SR); rc=fftf(noise(n),3500,14000)*np.linspace(0,1,n)**2.2; place('hf',rc,0.68,0.55)
cr=int(0.35*SR); ct=tt(cr); crack=fftf(noise(cr),1200,12000)*np.exp(-ct/0.022)+0.7*np.sin(2*np.pi*(180-90*np.minimum(ct/0.08,1))*ct)*np.exp(-ct/0.06)
place('imp',reverb(crack,0.5,0.28,0.8),0.9,0.9)
# ------------------------------------------------------------------ Earth (1.8): orbital drone and a slowly blooming eight-voice pad, faint 60 bpm heartbeat
n=int(1.9*SR); t=tt(n); pad=np.zeros(n)
for k in range(8):
    f=[110,165,220,247,330,392,440,494][k]*(1+rng.uniform(-0.004,0.004)); pad+=np.sin(2*np.pi*f*t+rng.uniform(0,6.28))*(0.35+0.65*swell(n,0.6,1.3)*(k/7))
place('bed',reverb(fftf(pad,100,2200)*swell(n,0.55,1.6),1.6,0.5,1.8),1.7,0.16)
n=int(1.9*SR); t=tt(n); dr=np.sin(2*np.pi*(55+8*np.sin(2*np.pi*0.4*t))*t)+0.5*np.sin(2*np.pi*82.5*t); place('bed',fftf(np.tanh(1.5*dr),70,400)*swell(n,0.4,1.2),1.8,0.18)
for k in range(2):   # lub-dub heartbeat at 60 bpm, very low
    for off,gg in ((0.0,1.0),(0.28,0.6)):
        n=int(0.22*SR); t=tt(n); th=np.sin(2*np.pi*(78-22*t/0.22)*t)*np.exp(-t/0.06)+0.5*fftf(noise(n),60,260)*np.exp(-t/0.04); place('imp',np.tanh(1.4*th),2.0+k*1.0+off,0.30*gg)
# soft bloom at the Earth snap: reversed swell and a low boom, no crack
n=int(0.3*SR); place('tex',fftf(noise(n),200,4000)*np.linspace(0,1,n)**2,1.5,0.35)
def boom(t0,size,tail=2.0):
    n=int(tail*SR); t=tt(n); f=95*np.exp(-t/0.20)+34; body=np.tanh(2.0*np.sin(2*np.pi*np.cumsum(f)/SR))*np.exp(-t/0.9)
    hi=fftf(noise(n),150,9000)*np.exp(-t/0.12)*0.6; mid=np.sin(2*np.pi*(140-70*np.minimum(t/0.15,1))*t)*np.exp(-t/0.25)
    place('imp',reverb(body*0.9+mid*0.6+hi,1.0,0.22,1.4),t0,size)
boom(1.8,0.35,1.2)
# ------------------------------------------------------------------ Parker (3.6): whiteout wash, metallic screech that overloads, Shepard riser, wormhole spin
n=int(1.8*SR); t=tt(n); wash=fftf(noise(n),400,11000)*(0.25+0.75*swell(n,0.85,1.1)); place('tex',wash,3.6,0.42)
fs=kf([(0,2400),(1.8,5600)],n); scr=sweep_bp(noise(n),fs,0.10)*(1+0.5*np.sin(2*np.pi*(6+10*t/1.8)*t)); scr=np.tanh(3.2*scr/ (np.abs(scr).max()+1e-9))
place('hf',scr*swell(n,0.9,1.2),3.6,0.34)
sh=np.zeros(n)
for k in range(7):
    f=160*2**(k+(t/1.8)); amp=np.exp(-0.5*((np.log2(np.maximum(f,1))-np.log2(900))/1.4)**2); sh+=np.sin(2*np.pi*np.cumsum(f)/SR)*amp
place('bed',fftf(sh,150,8000)*swell(n,0.92,1.2),3.6,0.20)
boom(3.6,0.55,1.6)
# reverse suck into the held breath (5.0-5.4)
n=int(0.4*SR); place('tex',fftf(noise(n),300,7000)*np.linspace(0,1,n)**2.4,5.0,0.38)
# ------------------------------------------------------------------ held breath 5.4-5.85: silence, with a thin high tone creeping in (light has no sound)
n=int(0.45*SR); tin=np.sin(2*np.pi*11000*tt(n))*np.linspace(0,1,n)**2; place('hf',tin,5.4,0.045)
# ------------------------------------------------------------------ the light drop 5.85: cinematic impact, then everything falls away to a thin ringing tone and a faint sub
boom(5.85,1.0,2.6)
n=int(1.4*SR); t=tt(n); place('hf',reverb(fftf(noise(n),3000,14000)*np.exp(-t/0.35),1.2,0.4,1.4),5.85,0.30)
n=int((8.1-6.2)*SR); tin=np.sin(2*np.pi*11000*tt(n))*swell(n,0.15,0.6)*0.5+np.sin(2*np.pi*12500*tt(n))*0.25; place('hf',tin,6.2,0.05)
n=int(2.0*SR); place('bed',np.sin(2*np.pi*40*tt(n))*swell(n,0.3,1.0),6.1,0.06)
# ------------------------------------------------------------------ laps 8.1-10.8: one whip of air per lap (7.5 per second, pitch climbing), locked by a low thump at 7.5
for k in range(7):
    ts=8.1+0.3+(k+1)/7.5; n=int(0.11*SR); c=700*2**(k*0.42); w=sweep_bp(noise(n+4096),kf([(0,c*0.6),(0.11,c*1.5)],n+4096),0.3,1024)[:n]
    place('tex',w*np.hanning(n),ts-0.09,0.5,-0.7 if k%2 else 0.7)
n=int(1.6*SR); place('tex',fftf(noise(n),200,6000)*swell(n,0.5,1.6),8.35,0.12)
boom(9.4,0.45,1.4)
n=int(1.4*SR); t=tt(n); place('hf',reverb(fftf(noise(n),4000,13000)*np.exp(-t/0.3),1.2,0.4,1.2),9.4,0.16)
# ------------------------------------------------------------------ twist 10.8-12.6: low drone and a slow stretching swell; quiet and unresolved
n=int(1.9*SR); t=tt(n); dr=sum(np.sin(2*np.pi*f*t+rng.uniform(0,6.28))*a for f,a in ((55,.7),(82.5,.5),(110,.4),(165,.25))); place('bed',reverb(fftf(dr,70,1200)*swell(n,0.5,1.5),1.8,0.45,2.0),10.8,0.17)
n=int(1.8*SR); st=sweep_bp(noise(n+4096),kf([(0,250),(1.8,3200)],n+4096),0.3,2048)[:n]*swell(n,0.85,1.4); place('tex',st,10.8,0.20,0.3)
# loop: rising rush into frame 0
n=int(0.5*SR); lr=sweep_bp(noise(n+4096),kf([(0,420),(0.5,900)],n+4096),0.3,1024)[:n]*swell(n,0.9,1.5); place('tex',lr,12.55,0.3)
# ------------------------------------------------------------------ mix: duck for the pre-crack silence and the held breath, high-pass everything but the impact bus, soft clip
duck=duck_curve()
def hp(x): return np.stack([fftf(x[0],90,SR/2),fftf(x[1],90,SR/2)])
mix=buses['imp']*0.95+(hp(buses['bed'])+hp(buses['tex'])+hp(buses['hf']))*duck
mix=np.tanh(1.1*mix)/np.tanh(1.1); mix*=0.88/np.max(np.abs(mix))*0.80   # leave headroom for the AAC true peak
fade=np.ones(N); fade[:int(0.004*SR)]=np.linspace(0,1,int(0.004*SR)); fade[-int(0.02*SR):]=np.linspace(1,0,int(0.02*SR)); mix*=fade
pcm=(mix.T*32767).astype('<i2')
with wave.open(sys.argv[1],'wb') as wf: wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(pcm.tobytes())
print('wrote',sys.argv[1],round(N/SR,2),'s peak',np.max(np.abs(mix)).round(3))
