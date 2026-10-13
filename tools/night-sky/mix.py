import subprocess, numpy as np, wave, os
SR=48000; T=18.0; N=int(SR*T)
LIB="../sfxlib/"
def load(f):
    raw=subprocess.run(["ffmpeg","-v","error","-i",LIB+f,"-f","f32le","-ac","2","-ar",str(SR),"-"],capture_output=True).stdout
    return np.frombuffer(raw,np.float32).reshape(-1,2).copy()
cache={}
def L(f):
    if f not in cache: cache[f]=load(f)
    return cache[f]
def peak_t(x,win=0.02):
    h=int(win*SR); m=x.mean(1); n=len(m)//h; e=np.array([(m[i*h:(i+1)*h]**2).mean() for i in range(n)]); return e.argmax()*win
def db(g): return 10**(g/20)
def fft_filter(x,kind,fc,order=2):
    n=len(x); X=np.fft.rfft(x,axis=0); f=np.fft.rfftfreq(n,1/SR)[:,None]
    r=(f/fc+1e-9)
    mag=1/np.sqrt(1+r**(2*order)) if kind=='lp' else (1-1/np.sqrt(1+r**(2*order)))
    return np.fft.irfft(X*mag,n=n,axis=0)
buses={k:np.zeros((N,2),np.float32) for k in ['hit','sfx','bed','synth','tick','riser','punch']}
def place(bus,x,at,gain=0,fi=0.005,fo=0.03,pan=0.0,length=None):
    x=x.copy()
    if length is not None: x=x[:int(length*SR)]
    n=len(x); a=int(at*SR)
    if a<0: x=x[-a:]; n=len(x); a=0
    if a>=N: return
    if a+n>N: x=x[:N-a]; n=len(x)
    env=np.ones(n,np.float32); fi_n=int(fi*SR); fo_n=int(fo*SR)
    if fi_n>0: env[:min(fi_n,n)]=np.linspace(0,1,min(fi_n,n))
    if fo_n>0: env[-min(fo_n,n):]*=np.linspace(1,0,min(fo_n,n))
    g=db(gain)*env
    l=g*(1-max(0,pan)); r=g*(1+min(0,pan))
    buses[bus][a:a+n,0]+=x[:,0]*l; buses[bus][a:a+n,1]+=x[:,1]*r
def seg(f,s0,s1): x=L(f); return x[int(s0*SR):int(s1*SR)]
def at_peak(bus,f,s0,s1,t_peak,gain,**kw):
    x=seg(f,s0,s1); p=peak_t(x); place(bus,x,t_peak-p,gain,**kw)
# ---------------------------------------------------------------- hits & transitions
# frame 0 hit: dark suspense accent (peak at 5.0 src) aligned to 0.0..0.05
place('hit',seg("869757__mikiko850__dark-suspense-accent.wav",4.95,6.9),0.0,-4,fi=0.002,fo=0.25)
# charge flicker 0.30 .. 1.55: jacobs ladder + sparks bursts (stutter w/ gaps)
jl=L("19487__halleck__jacobsladdersingle2.flac")
for t0,d in ((0.30,0.28),(0.82,0.30),(1.26,0.26)):
    place('sfx',jl[int(0.15*SR):int((0.15+d)*SR)],t0,-4,fi=0.003,fo=0.04)
sp=L("849772__mikiko850__electric-sparks.wav"); m=sp.mean(1); hop=int(0.12*SR); en=np.array([(m[i*hop:(i+1)*hop]**2).mean() for i in range(len(m)//hop)]); top=np.argsort(en)[::-1]
chosen=[]; 
for i in top:
    if all(abs(i-c)>6 for c in chosen): chosen.append(i)
    if len(chosen)>=8: break
chosen=[int(i) for i in chosen]
burst_times=[0.42,0.62,0.95,1.12,1.38,1.50]
for k,t0 in enumerate(burst_times):
    i=chosen[k%len(chosen)]; place('sfx',sp[i*hop:i*hop+int(0.14*SR)],t0,-9,fi=0.002,fo=0.03,pan=(-0.4 if k%2 else 0.4))
# snap-zoom 1.70: swish pre-roll, implosion, sub hit
sw=L("276871__lucabia__sword-in-air.wav"); pt=peak_t(sw); place('sfx',sw,1.66-pt,-5,fo=0.1,length=1.0)
place('hit',seg("814047__qubodup__fantasy-implosion.wav",0.08,1.8),1.70,-6,fi=0.003,fo=0.5)
# portal open 2.0, warp 2.75
place('sfx',seg("768664__berkup__portal-gate-opening.wav",0.15,3.4),2.0,-9,fi=0.05,fo=0.4)
at_peak('sfx',"735062__gammagool__fast-warp-in.wav",0,1.2,2.95,-7)
# pass-by whooshes at 3.0 4.8 6.6 8.4 from the whoosh pack
pk="175183__tomlija__5-everyday-whooshes.wav"
segs=[(2.6,4.9),(7.0,9.6),(11.8,14.9),(16.5,19.3),(21.0,23.6)]
for k,t in enumerate((3.0,4.8,6.6,8.4)):
    a,b=segs[k]; at_peak('sfx',pk,a,b,t,-5-0.0*k,pan=(-0.25 if k%2==0 else 0.25),fo=0.12)
place('sfx',seg("850262__cvltiv8r__orbiting-plasma-burst-and-trail-fx.wav",0.5,3.6),4.55,-9,fi=0.1,fo=0.5)
place('sfx',seg("752034__bachsambora__sci-fi-gateway.wav",0,1.1),6.52,-8)
at_peak('sfx',"238375__stewdio2003__cp_subby_whoosh.aiff",0.3,2.2,8.4,-9,fo=0.3)
# hyper acceleration 8.4..11.3: riser (src 3.0..6.15 -> 8.35..11.5), cinematic woosh, synth jet pitched up
ris=L("822420__audiopapkin__riser-hit-sfx-120.wav")
place('riser',ris[int(3.1*SR):int(6.15*SR)],8.45,-5,fi=0.4,fo=0.02,length=2.85)   # cut at 11.30 by vacuum
at_peak('sfx',"649445__audiopapkin__cinematic-woosh-sfx-015.wav",1.0,2.55,11.28,-8,fo=0.02)
jet=L("115555__vartioh__synth_jet.wav").mean(1); 
dur=2.9; n=int(dur*SR); rate=np.linspace(0.7,2.0,n); pos=np.cumsum(rate)[:n]; pos=pos%(len(jet)-2)
jr=np.interp(pos,np.arange(len(jet)),jet).astype(np.float32); place('riser',np.stack([jr,jr],1),8.4,-16,fi=0.5,fo=0.02)
# 11.5 hero blast: explosion + riser hit tail + synth sub wall (below)
place('hit',seg("814046__qubodup__explosion-from-another-dimension.wav",0.12,6.0),11.5,-3,fi=0.002,fo=1.2)
place('hit',ris[int(6.15*SR):int(11.5*SR)],11.5,-9,fi=0.003,fo=2.0,length=3.2)
# plasma trail fade under hold
place('bed',seg("850262__cvltiv8r__orbiting-plasma-burst-and-trail-fx.wav",4.9,6.0),13.2,-16,fi=0.3,fo=0.6)
# wind bed: 0..1.7 and 16.3..18
wd=L("22331__sleepcircle__wind.ogg")
place('bed',wd[int(3*SR):int(4.9*SR)],0.0,-20,fi=0.01,fo=0.15)
place('bed',wd[int(8*SR):int(10*SR)],16.3,-15,fi=0.15,fo=0.04)
# re-ignition crackle at 17.40..18.0 (hard stop)
for k,t0 in enumerate((17.35,17.5,17.62,17.74,17.84)):
    i=chosen[(k+2)%len(chosen)]; place('sfx',sp[i*hop:i*hop+int(0.16*SR)],t0,-6,fi=0.002,fo=0.03,pan=(-0.3 if k%2 else 0.3))
# ---------------------------------------------------------------- synth layers
t=np.arange(N)/SR
def synth_boom(t0,dur,f0,f1,gain):
    tt=np.clip(t-t0,0,None); m=(t>=t0)&(t<t0+dur)
    f=f1+(f0-f1)*np.exp(-tt*8); ph=2*np.pi*np.cumsum(f)/SR
    env=np.exp(-tt*(3.2/dur)); env[~m]=0
    s=np.sin(ph)*env*db(gain); return s
for t0,dur,f0,f1,g in ((0.0,1.1,85,32,-3),(1.70,0.9,80,34,-4)):
    s=synth_boom(t0,dur,f0,f1,g); buses['synth']+=np.stack([s,s],1)
# sub wall 11.5..15.0 : sub 36 Hz + tonal body 212 Hz (+octave), darkening noise roar
tt=t-11.5; m=(tt>=0)&(tt<3.6); env=np.zeros(N); env[m]=np.minimum(1,tt[m]/0.04)*np.exp(-np.clip(tt[m],0,None)*0.55)
vib=1+0.004*np.sin(2*np.pi*5.2*t)
sub=np.sin(2*np.pi*np.cumsum(36*vib*np.ones(N))/SR)*0.9+np.sin(2*np.pi*np.cumsum(72*vib*np.ones(N))/SR)*0.35
body=(np.sin(2*np.pi*np.cumsum(212*vib*np.ones(N))/SR)+0.5*np.sin(2*np.pi*np.cumsum(424*vib*np.ones(N))/SR)+0.25*np.sin(2*np.pi*np.cumsum(636*vib*np.ones(N))/SR))*0.20*np.exp(-np.clip(tt,0,None)*0.9)
rng=np.random.default_rng(5); noise=rng.standard_normal(N).astype(np.float32)
roar=np.stack([noise,np.roll(noise,40)],1)
bright=fft_filter(roar,'lp',3500); dark=fft_filter(roar,'lp',260)
w=np.clip(tt/3.0,0,1)[:,None]; roar=(bright*(1-w)+dark*w)*(0.35*np.exp(-np.clip(tt,0,None)*0.7))[:,None]
wall=np.stack([sub+body,sub+body],1)*env[:,None]*db(-5)+roar*m[:,None]*db(-4)
buses['synth']+=wall.astype(np.float32)
# counter ticks every 0.1 s 2.1..11.2 (soft), accent ticks at label times
for k,t0 in enumerate(np.arange(2.1,11.2,0.1)):
    a=int(t0*SR); Ln=int(0.012*SR); tick=np.sin(2*np.pi*2600*np.arange(Ln)/SR)*np.exp(-np.arange(Ln)/(0.002*SR))*db(-24)
    buses['tick'][a:a+Ln,0]+=tick; buses['tick'][a:a+Ln,1]+=tick
for t0 in (3.0,4.8,6.6,8.4):
    a=int(t0*SR); Ln=int(0.09*SR); tk=np.sin(2*np.pi*1200*np.arange(Ln)/SR)*np.exp(-np.arange(Ln)/(0.02*SR))*db(-12)
    buses['tick'][a:a+Ln]+=tk[:,None]
# text-in ticks (typed hook 0.2..0.7)
for t0 in np.arange(0.2,0.72,0.03):
    a=int(t0*SR); Ln=int(0.008*SR); tk=np.sin(2*np.pi*3400*np.arange(Ln)/SR)*np.exp(-np.arange(Ln)/(0.0015*SR))*db(-20)
    buses['tick'][a:a+Ln]+=tk[:,None]
# per-portal punch hits (synth boom + bright transient)
rngp=np.random.default_rng(9)
for t0,g in ((2.10,-9),(2.75,-8),(3.0,-3),(4.8,-3),(6.6,-3),(8.4,-2)):
    sb=synth_boom(t0,0.45,95,40,g); buses['punch']+=np.stack([sb,sb],1)
    a_=int(t0*SR); Ln=int(0.14*SR); nz=rngp.standard_normal(Ln)
    nz=fft_filter(np.stack([nz,nz],1).astype(np.float32),'hp',900)*np.exp(-np.arange(Ln)/(0.03*SR))[:,None]*db(g-6)
    buses['punch'][a_:a_+Ln]+=nz
# stutter gate on the hyper-acceleration riser (4 Hz -> 15 Hz)
u=np.clip((t-8.4)/2.9,0,1); f_g=4+11*u**1.5; ph_g=np.cumsum(f_g)/SR
gate=np.where((t>=8.4)&(t<11.3), 0.30+0.70*(np.sin(2*np.pi*ph_g)>0), 1.0)
buses['riser']=buses['riser']*gate[:,None]
# sidechain-style ducking of everything except punch/hit before + after each punch
duck2=np.ones(N)
for h in (2.10,2.75,3.0,4.8,6.6,8.4):
    i0=int((h-0.08)*SR); i1=int(h*SR); duck2[i0:i1]=np.minimum(duck2[i0:i1],0.12)
    rel=int(0.45*SR); duck2[i1:i1+rel]=np.minimum(duck2[i1:i1+rel],0.12+0.88*np.linspace(0,1,rel)**1.5)
for k in ('sfx','bed','synth','tick','riser'): buses[k]=buses[k]*duck2[:,None]
mix=sum(buses.values())
duck=np.ones(N)
def vac(a,b,floor=0.0,ramp=0.012):
    i0,i1=int(a*SR),int(b*SR); duck[i0:i1]=np.minimum(duck[i0:i1],floor)
    r=int(ramp*SR); duck[i0-r:i0]=np.minimum(duck[i0-r:i0],np.linspace(1,floor,r)) 
vac(1.58,1.695); vac(11.28,11.495,floor=0.02); vac(16.0,16.3)
# hard cut at 16.0: everything stops (fast fade), wind returns at 16.3
mix=mix*duck[:,None]
mix=fft_filter(mix,'hp',24)
mix=np.tanh(mix*0.9)/np.tanh(0.9)
mix[-int(0.02*SR):]*=np.linspace(1,0,int(0.02*SR))[:,None]
pkv=np.abs(mix).max(); mix=mix/pkv*0.89
w=wave.open("night_sfx_raw.wav","wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype(np.int16).tobytes()); w.close()
print("mixed, peak scale",pkv)
