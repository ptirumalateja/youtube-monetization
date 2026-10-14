import subprocess, numpy as np, wave, os
SR=48000; T=26.0; N=int(SR*T)
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
buses={k:np.zeros((N,2),np.float32) for k in ['hit','sfx','bed','synth','tick','riser','punch','air']}
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

t=np.arange(N)/SR
rng=np.random.default_rng(5)
def mono(x): return x.mean(1)
def pan_sweep(x,p0,p1):
    m=mono(x); pan=np.linspace(p0,p1,len(m)); ang=(pan+1)*np.pi/4
    return np.stack([m*np.cos(ang),m*np.sin(ang)],1).astype(np.float32)
def synth_boom(t0,dur,f0,f1,gain,bus='punch'):
    tt=np.clip(t-t0,0,None); m=(t>=t0)&(t<t0+dur)
    f=f1+(f0-f1)*np.exp(-tt*9); ph=2*np.pi*np.cumsum(f)/SR
    env=np.exp(-tt*(3.4/dur)); env[~m]=0; env[m]*=np.minimum(1,tt[m]/0.003)
    s_=np.sin(ph)*env*db(gain); buses[bus]+=np.stack([s_,s_],1).astype(np.float32)
def burst(t0,dur,gain,hp=1500,bus='punch',lp=None):
    a=int(t0*SR); Ln=int(dur*SR); nz=rng.standard_normal(Ln).astype(np.float32)
    nz=fft_filter(np.stack([nz,nz],1),'hp',hp)
    if lp: nz=fft_filter(nz,'lp',lp)
    nz*=np.exp(-np.arange(Ln)/(Ln*0.28))[:,None]*db(gain); buses[bus][a:a+Ln]+=nz[:max(0,min(Ln,N-a))]
def bell(t0,f,dur,gain,bus='air'):
    tt=np.clip(t-t0,0,None); m=(t>=t0)&(t<t0+dur); env=np.exp(-tt*(5.0/dur)); env[~m]=0
    s_=(np.sin(2*np.pi*f*t)+0.4*np.sin(2*np.pi*f*2.01*t)+0.2*np.sin(2*np.pi*f*3.02*t))*env*db(gain); buses[bus]+=np.stack([s_,s_],1).astype(np.float32)
pk="175183__tomlija__5-everyday-whooshes.wav"; wsegs=[(2.6,4.9),(7.0,9.6),(11.8,14.9),(16.5,19.3),(21.0,23.6)]
def whoosh_at(k,tp,gain,p0=-0.6,p1=0.6,rev=False,bus='sfx',fo=0.15):
    a,b=wsegs[k]; x=seg(pk,a,b); p=peak_t(x)
    if rev: x=x[::-1].copy(); p=len(x)/SR-p
    place(bus,pan_sweep(x,p0,p1),tp-p,gain,fo=fo)
sp=L("849772__mikiko850__electric-sparks.wav"); m_=mono(sp); hop=int(0.12*SR); en=np.array([(m_[i*hop:(i+1)*hop]**2).mean() for i in range(len(m_)//hop)]); top=np.argsort(en)[::-1]
chosen=[]
for i in top:
    if all(abs(i-c)>6 for c in chosen): chosen.append(int(i))
    if len(chosen)>=10: break
def spark(t0,gain,k,length=0.14,pan=0.0): i=chosen[k%len(chosen)]; place('sfx',sp[i*hop:i*hop+int(length*SR)],t0,gain,fi=0.002,fo=0.03,pan=pan)
jl=L("19487__halleck__jacobsladdersingle2.flac"); ris=L("822420__audiopapkin__riser-hit-sfx-120.wav")
EXP="814046__qubodup__explosion-from-another-dimension.wav"; IMP="814047__qubodup__fantasy-implosion.wav"; DARK="869757__mikiko850__dark-suspense-accent.wav"


# ============================ SCALE LADDER (26 s, 3D fly-back) cue sheet
wd=L("22331__sleepcircle__wind.ogg"); PLASMA="850262__cvltiv8r__orbiting-plasma-burst-and-trail-fx.wav"
# 0.0 hit + depth-hook: implosion pull + rising reverse whoosh, slam as the Sun limb arrives (2.0)
place('hit',seg(EXP,0.12,1.6),0.0,-8,fi=0.002,fo=0.6); place('hit',seg(DARK,4.95,6.4),0.0,-7,fi=0.002,fo=0.4)
synth_boom(0.0,0.9,95,34,-2); burst(0.0,0.06,-10,hp=1500)
for t0 in np.arange(0.30,0.80,0.025): burst(t0,0.008,-22,hp=3200,bus='tick')
place('hit',seg(IMP,0.08,1.6),0.55,-9,fi=0.003,fo=0.5)
whoosh_at(4,1.95,-5,rev=True,p0=-0.3,p1=0.3,fo=0.01); whoosh_at(1,1.2,-9,p0=0.6,p1=-0.6)
place('hit',seg(EXP,0.12,2.6),2.0,-9,fi=0.002,fo=0.9); synth_boom(2.0,0.9,90,34,-3); burst(2.0,0.05,-10,hp=2200)
def pullback(ts,te,k):
    whoosh_at(4,ts,-5,rev=True,p0=0,p1=0,fo=0.01)
    place('hit',seg(IMP,0.08,1.6),ts,-7,fi=0.003,fo=0.5)
    whoosh_at(k,(ts+te)/2+0.05,-6,p0=0.7,p1=-0.7)
    synth_boom(ts,0.6,88,36,-4); synth_boom(te,0.5,85,40,-5); burst(te,0.05,-11,hp=2000)
pullback(5.4,7.6,2); pullback(11.0,13.0,3)
# ---- stop 2: the Sun (2.0-5.4) fire roar + crackle
nz=rng.standard_normal(N).astype(np.float32); roar=np.stack([nz,np.roll(nz,31)],1); roar=fft_filter(fft_filter(roar,'lp',2600),'hp',120)
renv=np.clip((t-2.0)/0.05,0,1)*(0.85+0.15*np.sin(2*np.pi*3.1*t))*(t>=2.0)*(t<5.3)*np.clip((5.3-t)/0.4,0,1); buses['sfx']+=(roar*renv[:,None]*db(-12)).astype(np.float32)
place('sfx',seg(PLASMA,0.5,3.0),2.1,-9,fi=0.05,fo=0.5)
for k in range(16): spark(2.2+k*0.2,-11-0.2*k,k,pan=(-0.5 if k%2 else 0.5))
# ---- stop 3: solar system (7.6-11.0): glass bells, one per orbit
for i,f_ in enumerate([523,587,659,784,880,1047,1175,1319]): bell(7.9+0.36*i,f_,1.7,-21)
pad3=(np.sin(2*np.pi*424*t)+0.6*np.sin(2*np.pi*636*t))*np.clip((t-7.7)/0.8,0,1)*np.clip((10.9-t)/0.4,0,1)*(t>=7.7)*db(-32); buses['bed']+=np.stack([pad3,pad3],1).astype(np.float32)
# ---- stop 4: Milky Way (13.0-17.0): choir-like pad swell, riser, stutter gate; held breath 17.0-18.0
padm=sum(np.sin(2*np.pi*f_*t) for f_ in (212,318,424,530))*(0.75+0.25*np.sin(2*np.pi*0.6*t))*np.clip((t-13.1)/1.4,0,1)*((t>=13.1)&(t<17.0))*db(-26)*np.clip((17.0-t)/0.05,0,1)
buses['bed']+=np.stack([padm,padm],1).astype(np.float32)
place('riser',ris[int(3.15*SR):int(6.15*SR)],14.0,-5,fi=0.3,fo=0.01,length=3.0)
jet=mono(L("115555__vartioh__synth_jet.wav")); n=int(3.0*SR); rate=np.linspace(0.7,2.0,n); pos=np.cumsum(rate)[:n]%(len(jet)-2)
jr=np.interp(pos,np.arange(len(jet)),jet).astype(np.float32); place('riser',np.stack([jr,jr],1),14.0,-18,fi=0.5,fo=0.01)
uu=np.clip((t-15.2)/1.8,0,1); fg=4+11*uu**1.5; phg=np.cumsum(fg)/SR
gate=np.where((t>=15.2)&(t<17.0),0.30+0.70*(np.sin(2*np.pi*phg)>0),1.0); buses['riser']=buses['riser']*gate[:,None]
# ---- 18.0 the burst into the observable universe: big hit, controlled-decay sub wall
place('hit',seg(EXP,0.12,6.0),18.0,-3,fi=0.002,fo=1.2); place('hit',ris[int(6.15*SR):int(9.6*SR)],18.0,-9,fi=0.003,fo=1.5)
whoosh_at(3,18.25,-6,p0=-0.6,p1=0.6)
tt=t-18.0; m=(tt>=0)&(tt<3.4); env=np.zeros(N); env[m]=np.minimum(1,tt[m]/0.004)*np.exp(-tt[m]/0.9)
vib=1+0.004*np.sin(2*np.pi*5.2*t); ph=lambda f: 2*np.pi*np.cumsum(f*vib)/SR
sub=np.sin(ph(36*np.ones(N)))*0.9+np.sin(ph(72*np.ones(N)))*0.35
body=(np.sin(ph(212*np.ones(N)))+0.5*np.sin(ph(424*np.ones(N)))+0.25*np.sin(ph(636*np.ones(N))))*0.22*np.exp(-np.clip(tt,0,None)/1.4)*m
bright=fft_filter(roar,'lp',3500); dark=fft_filter(roar,'lp',260); w_=np.clip(tt/2.5,0,1)[:,None]
rr=(bright*(1-w_)+dark*w_)*(0.38*np.exp(-np.clip(tt,0,None)/0.6)*m)[:,None]
buses['synth']+=(np.stack([sub*env+body,sub*env+body],1)*db(-4)+rr*db(-4)).astype(np.float32); burst(18.0,0.7,-13,hp=3000,bus='air')
# ---- stop 5: web shimmer 20.0-23.0
padw=(np.sin(2*np.pi*424*t)+0.6*np.sin(2*np.pi*636*t)+0.4*np.sin(2*np.pi*848*t))*(0.7+0.3*np.sin(2*np.pi*0.7*t))*np.clip((t-19.6)/1.2,0,1)*np.clip((22.5-t)/0.4,0,1)*((t>=19.6)&(t<22.5))*db(-30); buses['bed']+=np.stack([padw,padw],1).astype(np.float32)
place('bed',seg(PLASMA,4.9,6.0),20.2,-16,fi=0.3,fo=0.8)
for k,f_ in enumerate([1319,1568,1760,2093,1175]): bell(20.4+0.45*k,f_,1.6,-27)
# ---- 22.5-24.1 the plunge back down the ladder: rising sweep, riser, pass-by whooshes per scale, then Earth lands
fsw=180*np.exp(np.clip((t-22.5)/1.55,0,1)*np.log(3400/180)); phs=2*np.pi*np.cumsum(fsw)/SR
sw=np.sin(phs)*np.clip((t-22.5)/0.3,0,1)*((t>=22.5)&(t<24.05))*(np.clip((t-22.5)/1.55,0,1)**1.6)*np.clip((24.05-t)/0.02,0,1)*db(-20); buses['riser']+=np.stack([sw,sw],1).astype(np.float32)
place('riser',ris[int(3.15*SR):int(5.0*SR)],22.4,-7,fi=0.2,fo=0.01,length=1.65)
whoosh_at(4,24.0,-4,rev=True,p0=0,p1=0,fo=0.01)
for tw_,k_ in ((22.95,1),(23.4,2),(23.8,3)): whoosh_at(k_,tw_,-8,p0=0.8,p1=-0.8)
place('hit',seg(IMP,0.08,1.6),22.5,-9,fi=0.003,fo=0.5); synth_boom(22.5,0.6,88,36,-5)
synth_boom(24.1,0.9,85,34,-3); burst(24.1,0.05,-10,hp=2200)
place('bed',wd[int(8*SR):int(11*SR)],24.1,-15,fi=0.3,fo=0.04)
bell(24.55,1319,2.0,-18); bell(24.55,659,2.0,-24)
for k,t0 in enumerate((25.35,25.5,25.62,25.74,25.84,25.92)): spark(t0,-6,k+2,length=0.16,pan=(-0.3 if k%2 else 0.3))
u=np.clip((t-25.3)/0.68,0,1)*(t>=25.3); lk=np.sin(2*np.pi*np.cumsum(40+36*u**1.6)/SR)*u**1.5*db(-12); buses['synth']+=np.stack([lk,lk],1).astype(np.float32)
# ---------------------------------------------------------------- reverb on hit/punch
def reverb(x,rt=1.7,wet=0.16):
    n=int(rt*SR); ir=rng.standard_normal((n,2)).astype(np.float32)*np.exp(-np.arange(n)/(0.28*SR))[:,None]; ir=fft_filter(ir,'lp',5500); ir/=np.abs(ir).max()
    out=np.zeros_like(x); L_=len(x)+n; 
    for ch in (0,1):
        X=np.fft.rfft(x[:,ch],L_); Y=np.fft.rfft(ir[:,ch],L_); out[:,ch]=np.fft.irfft(X*Y,L_)[:len(x)]*wet*0.05
    return out
buses['hit']=buses['hit']+reverb(buses['hit']); buses['punch']=buses['punch']+reverb(buses['punch'],1.2,0.10)
# ---------------------------------------------------------------- bass management, sidechain, vacuum
for k in ('sfx','riser','bed','air'): buses[k]=fft_filter(buses[k],'hp',90)
buses['hit']=fft_filter(buses['hit'],'hp',28)
duck2=np.ones(N)
for h in (2.0,5.4,11.0,18.0,24.1):
    i0=int((h-0.08)*SR); i1=int(h*SR); duck2[i0:i1]=np.minimum(duck2[i0:i1],0.12)
    rel=int(0.45*SR); duck2[i1:i1+rel]=np.minimum(duck2[i1:i1+rel],0.12+0.88*np.linspace(0,1,rel)**1.5)
for k in ('sfx','bed','tick','riser','air'): buses[k]=buses[k]*duck2[:,None]
mix=sum(buses.values())
duck=np.ones(N)
def vac(a,b,floor=0.0,ramp=0.012):
    i0,i1=int(a*SR),int(b*SR); duck[i0:i1]=np.minimum(duck[i0:i1],floor); r=int(ramp*SR); duck[i0-r:i0]=np.minimum(duck[i0-r:i0],np.linspace(1,floor,r))
vac(1.92,2.0); vac(5.30,5.395); vac(10.90,10.995); vac(17.05,17.95,floor=0.02,ramp=0.05); vac(24.02,24.1)
mix=mix*duck[:,None]
mix=fft_filter(mix,'hp',24); mix=np.tanh(mix*0.9)/np.tanh(0.9)
mix[-int(0.02*SR):]*=np.linspace(1,0,int(0.02*SR))[:,None]
pkv=np.abs(mix).max(); mix=mix/pkv*0.89
w_=wave.open("ladder_sfx_raw.wav","wb"); w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((mix*32767).astype(np.int16).tobytes()); w_.close()
print("mixed2, peak scale",pkv)
