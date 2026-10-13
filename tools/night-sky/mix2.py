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
# ---- 0.0 frame-0 hit + lighting-up of the sky
place('hit',seg(EXP,0.12,1.9),0.0,-8,fi=0.002,fo=0.6); place('hit',seg(DARK,4.95,6.4),0.0,-6,fi=0.002,fo=0.4)
synth_boom(0.0,0.9,95,34,-2); burst(0.0,0.06,-9,hp=1500)
for t0 in (0.10,0.24,0.38): place('sfx',jl[int(0.15*SR):int(0.27*SR)],t0,-7,fi=0.002,fo=0.04,pan=(-0.4 if t0>0.2 else 0.4))
# ---- 0.5 snap-pull
whoosh_at(4,0.5,-5,rev=True,p0=0.0,p1=0.0,fo=0.01)                      # reverse whoosh pre-roll into the pull
sw=L("276871__lucabia__sword-in-air.wav"); place('sfx',sw,0.5-peak_t(sw),-4,length=0.9,fo=0.1)
place('hit',seg(IMP,0.08,1.8),0.5,-5,fi=0.003,fo=0.5); synth_boom(0.5,0.8,88,34,-3)
# ---- 1.0 portal opens around the star
place('sfx',seg("768664__berkup__portal-gate-opening.wav",0.15,3.0),1.0,-11,fi=0.05,fo=0.4)
u=np.clip((t-1.0)/0.9,0,1)*(t<1.95); sh=np.sin(2*np.pi*np.cumsum(1800+3400*u**1.5)/SR)*u**2*db(-27)*(0.7+0.3*np.sin(2*np.pi*14*t)); buses['air']+=np.stack([sh,sh],1).astype(np.float32)
for k,t0 in enumerate((1.0,1.2,1.4,1.6)): spark(t0,-10,k+3,pan=(-0.5 if k%2 else 0.5))
# ---- 1.7..2.1 pull-through
place('riser',ris[int(4.9*SR):int(6.15*SR)],0.85,-9,fi=0.5,fo=0.01,length=1.25)
wp=L("735062__gammagool__fast-warp-in.wav"); place('sfx',wp,1.95-peak_t(wp),-7,length=0.6)
# ---- 2.1 entry into the tunnel
synth_boom(2.1,0.5,90,40,-8)
# ---- portal passes with distinct identities
# MOON 3.0 : airy glass
a=L("649445__audiopapkin__cinematic-woosh-sfx-015.wav"); x=a[int(1.0*SR):int(2.55*SR)]; place('sfx',pan_sweep(x,-0.6,0.6),3.0-peak_t(x),-7,fo=0.2)
bell(3.0,2093,1.5,-17); bell(3.0,3136,1.2,-22); synth_boom(3.0,0.4,80,44,-8); burst(3.0,0.05,-12,hp=2500)
# SUN 5.0 : fire
for k,t0 in enumerate(np.arange(4.98,5.75,0.11)): spark(t0,-7+(-0.8*k),k,pan=(-0.5 if k%2 else 0.5))
st=L("238375__stewdio2003__cp_subby_whoosh.aiff"); xs=st[int(0.3*SR):int(2.2*SR)]; place('sfx',pan_sweep(xs,-0.7,0.7),5.0-peak_t(xs),-6,fo=0.3)
place('sfx',seg("850262__cvltiv8r__orbiting-plasma-burst-and-trail-fx.wav",0.5,3.2),4.7,-9,fi=0.1,fo=0.5)
burst(5.0,0.8,-10,hp=250,lp=3000,bus='sfx'); synth_boom(5.0,0.6,90,38,-2); burst(5.0,0.05,-10,hp=2000)
# PROXIMA 7.0 : dark and low
gw=L("752034__bachsambora__sci-fi-gateway.wav"); place('sfx',gw,6.95-peak_t(gw),-6)
whoosh_at(2,7.0,-6,p0=0.7,p1=-0.7)
dk=fft_filter(seg(DARK,5.5,7.6),'lp',1200); place('hit',dk,7.0,-10,fi=0.02,fo=0.6); synth_boom(7.0,0.9,62,30,-2)
# ---- hyper acceleration 7.1..11.28
place('riser',ris[int(2.15*SR):int(6.15*SR)],7.28,-4,fi=0.3,fo=0.01,length=4.0)
a=L("649445__audiopapkin__cinematic-woosh-sfx-015.wav"); x=a[int(1.0*SR):int(2.55*SR)]; place('sfx',x,11.28-peak_t(x),-8,fo=0.02)
jet=mono(L("115555__vartioh__synth_jet.wav")); n=int(3.7*SR); rate=np.linspace(0.7,2.0,n); pos=np.cumsum(rate)[:n]%(len(jet)-2)
jr=np.interp(pos,np.arange(len(jet)),jet).astype(np.float32); place('riser',np.stack([jr,jr],1),7.6,-17,fi=0.5,fo=0.01)
tt_=7.15; k=0
while tt_<11.2:
    u=(tt_-7.15)/4.05; rate=2.0+12.0*u**1.4; synth_boom(tt_,0.16,72,44,-9-3*(1-u)); burst(tt_,0.012,-24,hp=6000,bus='tick'); tt_+=1.0/rate
# ---- 11.5 hero reveal
place('hit',seg(EXP,0.12,6.0),11.5,-2,fi=0.002,fo=1.2); place('hit',ris[int(6.15*SR):int(9.6*SR)],11.5,-9,fi=0.003,fo=1.5)
tt=t-11.5; m=(tt>=0)&(tt<3.0); env=np.zeros(N); env[m]=np.minimum(1,tt[m]/0.004)*np.exp(-tt[m]/0.9)
vib=1+0.004*np.sin(2*np.pi*5.2*t); ph=lambda f: 2*np.pi*np.cumsum(f*vib)/SR
sub=np.sin(ph(36*np.ones(N)))*0.9+np.sin(ph(72*np.ones(N)))*0.35
body=(np.sin(ph(212*np.ones(N)))+0.5*np.sin(ph(424*np.ones(N)))+0.25*np.sin(ph(636*np.ones(N))))*0.22*np.exp(-np.clip(tt,0,None)/1.4)*m
noise=rng.standard_normal(N).astype(np.float32); roar=np.stack([noise,np.roll(noise,40)],1)
bright=fft_filter(roar,'lp',3500); dark=fft_filter(roar,'lp',260); w=np.clip(tt/2.5,0,1)[:,None]
roar=(bright*(1-w)+dark*w)*(0.38*np.exp(-np.clip(tt,0,None)/0.6)*m)[:,None]
wall=np.stack([sub*env+body,sub*env+body],1)*db(-4)+roar*db(-4); buses['synth']+=wall.astype(np.float32)
burst(11.5,0.7,-13,hp=3000,bus='air')
# pad shimmer + trail under the hold
pad=(np.sin(2*np.pi*424*t)+0.6*np.sin(2*np.pi*636*t)+0.4*np.sin(2*np.pi*848*t))*(0.7+0.3*np.sin(2*np.pi*0.7*t))*np.clip((t-12.0)/1.2,0,1)*np.clip((16.0-t)/0.4,0,1)*(t<16)*db(-30)
buses['bed']+=np.stack([pad,pad],1).astype(np.float32)
place('bed',seg("850262__cvltiv8r__orbiting-plasma-burst-and-trail-fx.wav",4.9,6.0),13.2,-16,fi=0.3,fo=0.6)
# ---- ending + loop link
wd=L("22331__sleepcircle__wind.ogg"); place('bed',wd[int(8*SR):int(10*SR)],16.3,-15,fi=0.15,fo=0.04)
for k,t0 in enumerate((17.35,17.5,17.62,17.74,17.84,17.92)): spark(t0,-6,k+2,length=0.16,pan=(-0.3 if k%2 else 0.3))
u=np.clip((t-17.3)/0.68,0,1)*(t>=17.3); lk=np.sin(2*np.pi*np.cumsum(40+36*u**1.6)/SR)*u**1.5*db(-12); buses['synth']+=np.stack([lk,lk],1).astype(np.float32)
# ---- ticks
for t0 in np.arange(0.35,0.86,0.025): burst(t0,0.008,-22,hp=3200,bus='tick')
for t0 in np.arange(2.15,11.2,0.1):
    if any(abs(t0-p)<0.2 for p in (3.0,5.0,7.0)): continue
    a_=int(t0*SR); Ln=int(0.011*SR); tk=np.sin(2*np.pi*2600*np.arange(Ln)/SR)*np.exp(-np.arange(Ln)/(0.002*SR))*db(-27); buses['tick'][a_:a_+Ln]+=tk[:,None]
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
for h in (2.10,3.0,5.0,7.0):
    i0=int((h-0.08)*SR); i1=int(h*SR); duck2[i0:i1]=np.minimum(duck2[i0:i1],0.12)
    rel=int(0.45*SR); duck2[i1:i1+rel]=np.minimum(duck2[i1:i1+rel],0.12+0.88*np.linspace(0,1,rel)**1.5)
for k in ('sfx','bed','tick','riser','air'): buses[k]=buses[k]*duck2[:,None]
mix=sum(buses.values())
duck=np.ones(N)
def vac(a,b,floor=0.0,ramp=0.012):
    i0,i1=int(a*SR),int(b*SR); duck[i0:i1]=np.minimum(duck[i0:i1],floor); r=int(ramp*SR); duck[i0-r:i0]=np.minimum(duck[i0-r:i0],np.linspace(1,floor,r))
vac(0.40,0.495); vac(2.02,2.095); vac(2.92,2.995); vac(4.92,4.995); vac(6.92,6.995); vac(11.28,11.495,floor=0.02); vac(16.0,16.3)
mix=mix*duck[:,None]
mix=fft_filter(mix,'hp',24); mix=np.tanh(mix*0.9)/np.tanh(0.9)
mix[-int(0.02*SR):]*=np.linspace(1,0,int(0.02*SR))[:,None]
pkv=np.abs(mix).max(); mix=mix/pkv*0.89
w_=wave.open("night_sfx_raw2.wav","wb"); w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((mix*32767).astype(np.int16).tobytes()); w_.close()
print("mixed2, peak scale",pkv)
