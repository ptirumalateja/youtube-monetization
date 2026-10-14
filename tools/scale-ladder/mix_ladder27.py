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



# ============================ SCALE LADDER v3 sound: heavier, brighter-transient hits, size hierarchy
def sat(x,d): return np.tanh(x*d)/np.tanh(d)
def add(bus,sig,t0,gain=0.0,pan=0.0):
    a=int(t0*SR)
    if sig.ndim==1: sig=np.stack([sig,sig],1)
    sig=sig.astype(np.float32)*db(gain)
    l=1-max(0,pan); r=1+min(0,pan)
    if a<0: sig=sig[-a:]; a=0
    n=min(len(sig),N-a)
    if n<=0: return
    buses[bus][a:a+n,0]+=sig[:n,0]*l; buses[bus][a:a+n,1]+=sig[:n,1]*r
def nz1(n): return rng.standard_normal(n).astype(np.float32)
def bandpass(x,lo,hi):
    return fft_filter(fft_filter(x if x.ndim>1 else np.stack([x,x],1),'hp',lo),'lp',hi)
def hit_v3(t0,size,gain=0.0,bus='hit'):
    """transient crack + saturated pitch-drop body (audible on phone speakers) + sub + gong partials + pre-hit suck"""
    n=int(4.0*SR); tt=np.arange(n)/SR
    f=88+(320-88)*np.exp(-tt*(16-4*size)); ph=2*np.pi*np.cumsum(f)/SR
    body=sat(np.sin(ph)*np.exp(-tt/(0.28+0.40*size))*(1-np.exp(-tt/0.0015)),2.8+2.2*size)*0.85
    sub=np.sin(2*np.pi*(36+6*size)*tt)*np.exp(-tt/(0.5+0.6*size))*0.22*size
    crack=bandpass(nz1(n),1800,9500)[:,0]*np.exp(-tt/0.012)*1.4
    crack2=bandpass(nz1(n),300,2400)[:,0]*np.exp(-tt/0.09)*0.55
    gong=np.zeros(n,np.float32)
    for i,(fp,ap) in enumerate(((137,1.0),(211,0.8),(293,0.7),(379,0.55),(521,0.4),(667,0.3),(843,0.2))):
        gong+=np.sin(2*np.pi*fp*tt+i*1.3)*ap*np.exp(-tt/(1.2+0.8*size))
    gong*=0.17*size**0.8*(1-np.exp(-tt/0.004))
    sig=(body+sub+crack*0.95+crack2*0.65+gong*1.3).astype(np.float32)
    add(bus,sig,t0,gain)
def suck(t0,t1,gain=-8,lo=500,hi=7000):
    n=int((t1-t0)*SR); tt=np.arange(n)/SR; env=(tt/(t1-t0))**3*np.clip((t1-t0-tt)/0.03,0,1)
    x=bandpass(nz1(n),lo,hi)*env[:,None]; add('riser',x,t0,gain)
def braaam(t0,dur,f0,gain,bus='synth',bright=1500):
    n=int(dur*SR); tt=np.arange(n)/SR; out=np.zeros(n,np.float32)
    for dt,mult in ((-14,1.0),(-6,1.0),(0,1.0),(7,1.0),(15,1.0),(-8,1.5),(9,1.5),(0,2.0)):
        fv=f0*mult*2**(dt/1200)
        for h in range(1,15): out+=np.sin(2*np.pi*fv*h*tt+h*0.7)/h*(1.0 if mult==1 else 0.6)
    env=np.minimum(1,tt/0.10)*np.exp(-np.clip(tt-0.15,0,None)/(dur*0.38)); out*=env
    o2=fft_filter(np.stack([out,out],1),'lp',bright); o2=sat(o2*0.55,2.2)
    add(bus,o2,t0,gain)
def shepard(t0,dur,gain,f_lo=70,octs=6,rate=1.4,bus='riser',shape=2.0):
    n=int(dur*SR); tt=np.arange(n)/SR; u=tt/dur; out=np.zeros(n,np.float32)
    for k in range(7):
        pos=((k+u*rate*octs/octs*0+ (u**1.3)*rate*3)%octs)/octs
        fq=f_lo*2**(pos*octs); a=np.exp(-0.5*((pos-0.5)/0.22)**2); ph=2*np.pi*np.cumsum(fq)/SR
        out+=(np.sin(ph)+0.35*np.sin(2*ph))*a
    env=(u**shape)*np.clip((dur-tt)/0.02,0,1); add(bus,(out*env/3.0).astype(np.float32),t0,gain)
def whoosh_syn(t0,dur,gain,pan0=-0.7,pan1=0.7,peak=0.5,rev=False,bus='sfx'):
    n=int(dur*SR); tt=np.arange(n)/SR; u=tt/dur; base=nz1(n)
    bands=((150,500),(500,1500),(1500,4000),(4000,10000)); out=np.zeros((n,2),np.float32)
    for i,(lo,hi) in enumerate(bands):
        b=bandpass(base,lo,hi); w=np.exp(-0.5*((u-(0.15+0.7*i/3.0))/0.2)**2); out+=b*w[:,None]
    env=np.sin(np.pi*np.clip(u**(np.log(0.5)/np.log(peak)),0,1))**1.5
    out*=env[:,None]
    if rev: out=out[::-1].copy()
    pan=np.linspace(pan0,pan1,n); ang=(pan+1)*np.pi/4; m=out.mean(1)
    add(bus,np.stack([m*np.cos(ang),m*np.sin(ang)],1),t0,gain)
def crackle(t0,t1,rate,gain,bus='sfx'):
    n=int((t1-t0)*SR); sig=np.zeros((n,2),np.float32)
    for _ in range(int(rate*(t1-t0))):
        i=int(rng.random()*(n-400)); L_=int(rng.uniform(40,320)); a=rng.uniform(0.2,1.0)*(rng.random()**2)
        pop=bandpass(nz1(L_),1500,9000)*np.exp(-np.arange(L_)/(L_*0.25))[:,None]*a; sig[i:i+L_]+=pop
    add(bus,sig,t0,gain)
def choir(t0,t1,f0,gain,bus='bed'):
    n=int((t1-t0)*SR); tt=np.arange(n)/SR; u=tt/(t1-t0); out=np.zeros(n,np.float32)
    for mult,vol in ((1,1.0),(1.5,0.8),(2,0.9),(3,0.5),(4,0.35)):
        for dt in (-9,0,8):
            fv=f0*mult*2**(dt/1200)*(1+0.004*np.sin(2*np.pi*5.1*tt+mult))
            ph=2*np.pi*np.cumsum(fv)/SR
            for h in range(1,10): out+=np.sin(ph*h)/h*vol
    X=np.fft.rfft(out); f=np.fft.rfftfreq(n,1/SR); form=sum(g*np.exp(-0.5*((f-c)/b)**2) for c,b,g in ((700,160,1.0),(1150,200,0.7),(2700,350,0.35)))
    out=np.fft.irfft(X*(0.15+form),n=n); env=np.clip(u/0.7,0,1)**1.4*np.clip((1-u)/0.04,0,1); out*=env*(0.85+0.15*np.sin(2*np.pi*0.5*tt))
    add(bus,(out/np.abs(out).max()*0.5).astype(np.float32),t0,gain)

wd=L("22331__sleepcircle__wind.ogg"); PLASMA="850262__cvltiv8r__orbiting-plasma-burst-and-trail-fx.wav"
# ---- HOOK 0-2: big hit at frame 0, ticks, rising pull (shepard + suck) into the Sun slam at 2.0
hit_v3(0.0,0.75,gain=0)
place('hit',seg(EXP,0.12,1.6),0.0,-9,fi=0.002,fo=0.6); place('hit',seg(DARK,4.95,6.4),0.0,-8,fi=0.002,fo=0.4)
for t0 in np.arange(0.30,0.80,0.025): burst(t0,0.008,-20,hp=3200,bus='tick')
place('hit',seg(IMP,0.08,1.6),0.55,-10,fi=0.003,fo=0.5)
shepard(0.25,1.7,-14,f_lo=90,octs=5); whoosh_syn(0.9,1.05,-8,peak=0.8); suck(1.45,1.96,gain=-9)
# ---- 2.0 SUN SLAM: biggest early moment
hit_v3(2.0,1.0,gain=1); braaam(2.0,1.5,110,-12); place('hit',seg(EXP,0.12,2.6),2.0,-8,fi=0.002,fo=0.9)
whoosh_syn(2.0,0.7,-14,pan0=0.8,pan1=-0.8,peak=0.2)
# fire: roar + crackle + low rumble
nz=rng.standard_normal(N).astype(np.float32); roar=np.stack([nz,np.roll(nz,31)],1); roar=fft_filter(fft_filter(roar,'lp',2600),'hp',120)
renv=np.clip((t-2.0)/0.05,0,1)*(0.8+0.2*np.sin(2*np.pi*3.1*t)+0.1*np.sin(2*np.pi*7.3*t))*(t>=2.0)*(t<5.3)*np.clip((5.3-t)/0.4,0,1); buses['sfx']+=(roar*renv[:,None]*db(-10)).astype(np.float32)
rum=fft_filter(fft_filter(np.stack([nz,np.roll(nz,57)],1),'lp',260),'hp',70); buses['synth']+=(rum*(renv[:,None])*db(-17)).astype(np.float32)
place('sfx',seg(PLASMA,0.5,3.0),2.1,-8,fi=0.05,fo=0.5); crackle(2.1,5.2,70,-11)
# ---- PULL 1 (5.4) and arrival (7.6)
suck(5.0,5.395,gain=-8); hit_v3(5.4,0.6,gain=-1); whoosh_syn(5.4,2.2,-8,peak=0.35); hit_v3(7.6,0.35,gain=-4)
# ---- STOP 3 (v3): dark orbital drone + descending harmonic pings (no melody) + slow rotating whirr
def ping(t0,f,dec,gain,pan=0.0):
    n=int((dec+0.2)*SR); tt=np.arange(n)/SR; fb=f*(1-0.012*(1-np.exp(-tt*3)))
    ph=2*np.pi*np.cumsum(fb)/SR; sig=(np.sin(ph)+0.22*np.sin(2.76*ph)*np.exp(-tt*4)+0.1*np.sin(5.4*ph)*np.exp(-tt*8))*np.exp(-tt/(dec*0.35))*(1-np.exp(-tt/0.012))
    add('air',sig.astype(np.float32),t0,gain,pan)
ROOT=106.0
for i_,mult in enumerate((8,6,5,4,3,2.5,2,1.5)):
    ping(7.95+0.36*i_,ROOT*mult,0.8+0.22*i_,-17-0.3*i_,pan=np.sin(i_*0.9+0.4)*0.8)
ping(10.15,ROOT,2.6,-14); ping(10.15,ROOT*2,2.2,-20)
dn=(7.7<=t)&(t<10.9); dr=np.zeros(N,np.float32)
for mult,vol in ((1,1.0),(1.5,0.7),(2,0.8)):
    for dt in (-8,0,9): dr+=sum(np.sin(2*np.pi*ROOT*mult*2**(dt/1200)*h*t)/h for h in range(1,8))*vol
drs=fft_filter(np.stack([dr,dr],1),'lp',420)*(np.clip((t-7.7)/1.0,0,1)*np.clip((10.9-t)/0.5,0,1)*dn)[:,None]; buses['synth']+=(drs/np.abs(drs).max()*db(-17)*0.5).astype(np.float32)
wh=bandpass(nz1(N),300,1400)*((0.5+0.5*np.sin(2*np.pi*(0.8+0.25*(t-7.7))*(t-7.7)))*np.clip((t-7.8)/0.8,0,1)*np.clip((10.9-t)/0.5,0,1)*dn)[:,None]
ang=(np.sin(2*np.pi*0.18*t)+1)*np.pi/4; wh=np.stack([wh[:,0]*np.cos(ang),wh[:,1]*np.sin(ang)],1); buses['air']+=(wh*db(-26)).astype(np.float32)
# ---- PULL 2 (11.0) and Milky Way arrival (13.0)
suck(10.6,10.995,gain=-8); hit_v3(11.0,0.6,gain=-1); whoosh_syn(11.0,2.2,-8,peak=0.35); hit_v3(13.0,0.45,gain=-3)
# ---- STOP 4: choir swell, shepard riser, stutter gate; cut at 17.0
choir(13.1,17.0,110,-16)
shepard(14.0,3.0,-13,f_lo=80,octs=5,shape=1.6)
jet=mono(L("115555__vartioh__synth_jet.wav")); n=int(3.0*SR); rate=np.linspace(0.7,2.0,n); pos=np.cumsum(rate)[:n]%(len(jet)-2)
jr=np.interp(pos,np.arange(len(jet)),jet).astype(np.float32); place('riser',np.stack([jr,jr],1),14.0,-18,fi=0.5,fo=0.01)
uu=np.clip((t-15.2)/1.8,0,1); fg=4+11*uu**1.5; phg=np.cumsum(fg)/SR
gate=np.where((t>=15.2)&(t<17.0),0.30+0.70*(np.sin(2*np.pi*phg)>0),1.0); buses['riser']=buses['riser']*gate[:,None]; buses['bed']=buses['bed']*gate[:,None]
suck(17.55,17.96,gain=-12,lo=400,hi=5000)
# ---- 18.0 THE BIG ONE
hit_v3(18.0,1.5,gain=2); braaam(18.0,3.2,82,-9,bright=1500); braaam(18.0,3.2,164,-12,bright=2400)
place('hit',seg(EXP,0.12,6.0),18.0,-4,fi=0.002,fo=1.2); place('hit',ris[int(6.15*SR):int(9.6*SR)],18.0,-10,fi=0.003,fo=1.5)
whoosh_syn(18.0,1.2,-9,peak=0.15)
tt=t-18.0; m=(tt>=0)&(tt<3.4); env=np.zeros(N); env[m]=np.minimum(1,tt[m]/0.004)*np.exp(-tt[m]/0.9)
vib=1+0.004*np.sin(2*np.pi*5.2*t); ph_=lambda f: 2*np.pi*np.cumsum(f*vib)/SR
sub=np.sin(ph_(36*np.ones(N)))*0.7
bright=fft_filter(roar,'lp',3500); dark=fft_filter(roar,'lp',260); w_=np.clip(tt/2.5,0,1)[:,None]
rr=(bright*(1-w_)+dark*w_)*(0.38*np.exp(-np.clip(tt,0,None)/0.6)*m)[:,None]
buses['synth']+=(np.stack([sub*env,sub*env],1)*db(-12)+rr*db(-6)).astype(np.float32); burst(18.0,0.7,-12,hp=3000,bus='air')
# ---- STOP 5: web shimmer
choir(19.6,22.5,165,-20)
for k,f_ in enumerate([1319,1568,1760,2093,1175,1568,1760]): bell(20.2+0.35*k,f_,1.8,-23); bell(20.2+0.35*k,f_*1.5,1.4,-31)
place('bed',seg(PLASMA,4.9,6.0),20.2,-16,fi=0.3,fo=0.8)
# ---- PLUNGE 22.5-24.1
hit_v3(22.5,0.5,gain=-2); shepard(22.5,1.55,-9,f_lo=110,octs=5,rate=2.2,shape=1.8); suck(23.7,24.02,gain=-6,lo=600,hi=8000)
for tw_,k_ in ((22.95,0.4),(23.4,0.5),(23.8,0.6)): whoosh_syn(tw_-0.35,0.7,-6,peak=0.6,pan0=0.9,pan1=-0.9)
# ---- 24.1 landing
hit_v3(24.1,0.85,gain=0); place('bed',wd[int(8*SR):int(11*SR)],24.1,-14,fi=0.3,fo=0.04)
bell(24.55,1319,2.2,-16); bell(24.55,659,2.2,-22)
for k,t0 in enumerate((25.35,25.5,25.62,25.74,25.84,25.92)): spark(t0,-5,k+2,length=0.16,pan=(-0.3 if k%2 else 0.3))
u=np.clip((t-25.3)/0.68,0,1)*(t>=25.3); lk=np.sin(2*np.pi*np.cumsum(40+36*u**1.6)/SR)*u**1.5*db(-12); buses['synth']+=np.stack([lk,lk],1).astype(np.float32)
# ---------------------------------------------------------------- reverb (longer, darker tail on hits)
def reverb(x,rt=2.4,wet=0.30):
    n=int(rt*SR); ir=rng.standard_normal((n,2)).astype(np.float32)*np.exp(-np.arange(n)/(0.45*SR))[:,None]; ir=fft_filter(ir,'lp',4200); ir/=np.abs(ir).max()
    out=np.zeros_like(x); L_=len(x)+n
    for ch in (0,1):
        X=np.fft.rfft(x[:,ch],L_); Y=np.fft.rfft(ir[:,ch],L_); out[:,ch]=np.fft.irfft(X*Y,L_)[:len(x)]*wet*0.05
    return out
buses['hit']=buses['hit']+reverb(buses['hit']); buses['synth']=buses['synth']+reverb(buses['synth'],2.0,0.18)
buses['air']=buses['air']+reverb(buses['air'],1.6,0.2)
# bass management: phones cannot play <90 Hz, keep real sub only on hit/synth, tidy rest
for k in ('sfx','riser','bed','air','tick','punch'): buses[k]=fft_filter(buses[k],'hp',90)
hsub=fft_filter(buses['hit'],'lp',70)*0.45; buses['hit']=fft_filter(buses['hit'],'hp',70)+hsub
duck2=np.ones(N)
for h in (2.0,5.4,11.0,18.0,24.1,0.0,13.0):
    i0=max(0,int((h-0.08)*SR)); i1=int(h*SR); duck2[i0:i1]=np.minimum(duck2[i0:i1],0.10)
    rel=int(0.6*SR); duck2[i1:i1+rel]=np.minimum(duck2[i1:i1+rel],0.10+0.90*np.linspace(0,1,rel)**1.6)
for k in ('sfx','bed','tick','riser','air'): buses[k]=buses[k]*duck2[:,None]
mix=sum(buses.values())
duck=np.ones(N)
def vac(a,b,floor=0.0,ramp=0.012):
    i0,i1=int(a*SR),int(b*SR); duck[i0:i1]=np.minimum(duck[i0:i1],floor); r=int(ramp*SR); duck[i0-r:i0]=np.minimum(duck[i0-r:i0],np.linspace(1,floor,r))
vac(1.955,1.997); vac(5.355,5.397); vac(10.955,10.997); vac(17.05,17.95,floor=0.03,ramp=0.05); vac(17.96,17.997); vac(24.06,24.098)
mix=mix*duck[:,None]
mix=fft_filter(mix,'hp',24); mix=np.tanh(mix*0.85)/np.tanh(0.85)
mix[-int(0.02*SR):]*=np.linspace(1,0,int(0.02*SR))[:,None]
pkv=np.abs(mix).max(); mix=mix/pkv*0.95
w_=wave.open("ladder_sfx_v3.wav","wb"); w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((mix*32767).astype(np.int16).tobytes()); w_.close()
print("v3 mixed, peak scale",pkv)
