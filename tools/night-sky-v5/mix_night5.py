import subprocess, numpy as np, wave, os
SR=48000; T=24.0; N=int(SR*T)
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
# ===================== NIGHT SKY v5 (22.45 s) cue sheet
def ping(t0,f,dec,gain,pan=0.0):
    n=int((dec+0.2)*SR); tt_=np.arange(n)/SR; fb=f*(1-0.012*(1-np.exp(-tt_*3)))
    ph=2*np.pi*np.cumsum(fb)/SR; sig=(np.sin(ph)+0.22*np.sin(2.76*ph)*np.exp(-tt_*4)+0.1*np.sin(5.4*ph)*np.exp(-tt_*8))*np.exp(-tt_/(dec*0.35))*(1-np.exp(-tt_/0.012))
    add('air',sig.astype(np.float32),t0,gain,pan)
ROOT=106.0
# ---- hook 0-2.1: frame-0 hit, typing ticks, wind, spark-stutter charge-up, rising shepard + suck into the snap
hit_v3(0.0,0.6,gain=-1); place('hit',seg(DARK,4.95,6.4),0.0,-8,fi=0.002,fo=0.4); place('hit',seg(EXP,0.12,1.6),0.0,-12,fi=0.002,fo=0.6)
place('bed',wd[int(6*SR):int(9*SR)],0.0,-16,fi=0.05,fo=0.3,length=2.1)
for t0 in np.arange(0.35,1.0,0.025): burst(t0,0.008,-21,hp=3200,bus='tick')
for k,t0 in enumerate((0.55,0.78,0.95,1.10,1.23,1.34,1.44,1.53,1.61,1.68,1.74,1.80,1.85,1.90,1.94,1.98)): spark(t0,-12+0.35*k,k,length=0.12,pan=(-0.4 if k%2 else 0.4))
shepard(0.5,1.55,-15,f_lo=90,octs=5); suck(1.62,2.095,gain=-9)
# ---- 2.1 the snap into the sky
hit_v3(2.1,1.0,gain=1); pass; place('hit',seg(IMP,0.08,1.6),2.1,-9,fi=0.003,fo=0.5); place('hit',seg(EXP,0.12,2.6),2.1,-9,fi=0.002,fo=0.9)
whoosh_syn(2.1,0.8,-12,pan0=0.8,pan1=-0.8,peak=0.2)
# ---- depth gates: whoosh into each gate + a shape-specific shimmer at the crossing (Moon circle, Sun double, Proxima hex, Betelgeuse deep, Andromeda blue)
for tg,kind in ((2.85,'moon'),(4.65,'sun'),(6.65,'prox'),(8.35,'bet'),(13.45,'and')):
    whoosh_syn(tg-0.35,0.7,-12,peak=0.6,pan0=-0.5,pan1=0.5)
    if kind=='moon': ping(tg,1568,1.4,-22,pan=-0.3); ping(tg+0.08,2349,1.0,-28,pan=0.3)
    if kind=='sun': ping(tg,880,1.6,-20); ping(tg+0.06,1319,1.3,-24,pan=0.3); crackle(tg,tg+0.7,60,-18)
    if kind=='prox': ping(tg,277,2.0,-19,pan=0.3); ping(tg+0.05,415,1.6,-25,pan=-0.3)
    if kind=='bet': ping(tg,110,3.0,-15); ping(tg,220,2.4,-21); hit_v3(tg,0.3,gain=-7)
    if kind=='and': ping(tg,1760,2.4,-21,pan=-0.3); ping(tg+0.1,2637,2.0,-27,pan=0.3)
# ---- Moon pass 3.55: silver glass, soft
ping(3.0,1760,1.6,-24,pan=-0.5); ping(3.0,2637,1.0,-33,pan=-0.5)
whoosh_syn(3.05,1.0,-10,peak=0.5,pan0=-0.7,pan1=0.7); hit_v3(3.55,0.25,gain=-6)
# ---- Sun pass 5.30: fire flare
nzz=rng.standard_normal(N).astype(np.float32); roarf=fft_filter(fft_filter(np.stack([nzz,np.roll(nzz,29)],1),'lp',3200),'hp',140)
renv=np.exp(-0.5*((t-5.3)/0.75)**2)*(0.8+0.2*np.sin(2*np.pi*4.0*t)); buses['sfx']+=(roarf*renv[:,None]*db(-9)).astype(np.float32)
crackle(4.5,6.3,90,-11); place('sfx',seg(PLASMA,0.5,2.6),4.8,-9,fi=0.05,fo=0.6); whoosh_syn(4.7,1.2,-8,peak=0.5); hit_v3(5.3,0.55,gain=-3)
# ---- Proxima 7.20: cold thin red dwarf
ping(6.7,330,2.2,-18,pan=0.3); ping(6.7,495,1.6,-26,pan=0.3); whoosh_syn(6.7,1.0,-10,peak=0.55,pan0=0.7,pan1=-0.7); hit_v3(7.2,0.35,gain=-4)
for k in range(8): spark(7.0+k*0.07,-14,k+3,length=0.1,pan=0.5)
# ---- Betelgeuse 9.60: scale shock, giant low swell
braaam(8.9,2.8,73,-11,bright=1000); shepard(8.4,1.2,-16,f_lo=60,octs=4,shape=1.6); suck(9.2,9.595,gain=-9,lo=300,hi=4000)
hit_v3(9.6,0.8,gain=-1); whoosh_syn(9.2,1.6,-9,peak=0.45,pan0=0.6,pan1=-0.6)
# ---- hyperdrive 10.8-13.9: accelerating pulse, shepard, jet, stutter; cut at 13.45
shepard(10.8,2.7,-10,f_lo=80,octs=5,rate=2.0,shape=1.6)
jet=mono(L("115555__vartioh__synth_jet.wav")); n=int(2.8*SR); rate=np.linspace(0.7,2.0,n); pos=np.cumsum(rate)[:n]%(len(jet)-2)
jr=np.interp(pos,np.arange(len(jet)),jet).astype(np.float32); place('riser',np.stack([jr,jr],1),10.8,-18,fi=0.5,fo=0.01)
uu=np.clip((t-11.6)/1.8,0,1); fg=4+11*uu**1.5; phg=np.cumsum(fg)/SR
gate=np.where((t>=11.6)&(t<13.45),0.30+0.70*(np.sin(2*np.pi*phg)>0),1.0); buses['riser']=buses['riser']*gate[:,None]
for k in range(34): tk=10.9+3.0*(k/34)**0.8; burst(tk,0.01,-18,hp=2500,bus='tick')
suck(13.55,13.995,gain=-11,lo=400,hi=6000)
# ---- 14.0 ANDROMEDA: the big hit
hit_v3(14.0,1.5,gain=-1); pass  # real brass braaam (chakong) replaces the synthetic stack here
place('hit',seg(EXP,0.12,6.0),14.0,-15,fi=0.002,fo=1.2); place('hit',ris[int(6.15*SR):int(9.6*SR)],14.0,-14,fi=0.003,fo=1.5); whoosh_syn(14.0,1.2,-9,peak=0.15)
tt=t-14.0; m=(tt>=0)&(tt<3.4); env=np.zeros(N); env[m]=np.minimum(1,tt[m]/0.004)*np.exp(-tt[m]/0.9)
vib=1+0.004*np.sin(2*np.pi*5.2*t); ph_=lambda f: 2*np.pi*np.cumsum(f*vib)/SR
sub=np.sin(ph_(36*np.ones(N)))*0.7; bright=fft_filter(roarf,'lp',3500); dark=fft_filter(roarf,'lp',260); w_=np.clip(tt/2.5,0,1)[:,None]
rr=(bright*(1-w_)+dark*w_)*(0.38*np.exp(-np.clip(tt,0,None)/0.6)*m)[:,None]
buses['synth']+=(np.stack([sub*env,sub*env],1)*db(-20)+rr*db(-8)).astype(np.float32); burst(14.0,0.7,-12,hp=3000,bus='air')
choir(14.2,17.4,110,-17)
# ---- 16.2-17.3: the turn (reversed swell, low drone), then the look-back
whoosh_syn(16.2,1.3,-11,peak=0.7,pan0=-0.8,pan1=0.8,rev=True); suck(16.6,17.3,gain=-14,lo=300,hi=3000)
ping(17.7,ROOT*3,3.0,-15,pan=-0.2); ping(17.7,159,3.2,-21)
for k,tk in enumerate((17.75,18.25,18.75)): synth_boom(tk,0.5,70,38,-17)
choir(17.4,19.4,106,-22)
# ---- user-supplied files (Pixabay-style): real sub weight under the three biggest hits + electrical hum bed through Betelgeuse/hyperdrive
HUM="gregorquendel_circuits_hum.mp3"; DROP="braam_bass_drop.mp3"; LONG="braam_long_impact.mp3"; SCR="braam_screaming_echo.mp3"; CHK="722633__chakong__cinematic-braaam.wav"
# 14.0 burst: chakong brass braaam is the hero body (swell lands on the hit), screaming-echo adds the tail, bass-drop is the real sub
place('synth',seg(CHK,0.0,4.2),13.5,0,fi=0.01,fo=1.0); place('synth',seg(SCR,0.0,4.8),14.0,-9,fi=0.003,fo=1.6); place('synth',seg(DROP,0.5,4.6),14.0,-8,fi=0.003,fo=1.4)
# 2.1 snap: shorter braaam dose
place('synth',seg(CHK,0.0,2.4),1.65,-5,fi=0.01,fo=0.6); place('synth',seg(DROP,0.5,1.9),2.1,-13,fi=0.003,fo=0.5)
place('synth',seg(LONG,3.0,6.4),8.7,-19,fi=0.9,fo=0.8)   # Betelgeuse swell into the pass at 9.6
place('synth',seg(DROP,0.5,2.7),21.0,-18,fi=0.003,fo=0.9)
place('synth',seg(HUM,0.0,5.25),8.22,-20,fi=1.2,fo=0.02)
# ---- 19.2-21.0 the fall home: shepard riser, a whoosh as each realm streaks past (Betelgeuse, Proxima, Sun, Moon), suck into the star, hit as the star blazes
shepard(19.2,1.8,-10,f_lo=100,octs=5,rate=2.2,shape=1.7); whoosh_syn(19.2,1.0,-10,peak=0.3,pan0=0.0,pan1=0.0,rev=True)
for tw_,gn in ((19.85,-7),(20.06,-8),(20.25,-6),(20.57,-6)): whoosh_syn(tw_-0.28,0.6,gn,peak=0.6,pan0=0.9,pan1=-0.9)
suck(20.62,20.96,gain=-7,lo=600,hi=8000); hit_v3(21.0,0.9,gain=-1); place('bed',wd[int(8*SR):int(11*SR)],21.05,-14,fi=0.3,fo=0.04)
bell(21.5,1319,2.2,-17); bell(21.5,659,2.2,-23)
for k,t0 in enumerate((23.1,23.25,23.37,23.49,23.59,23.67)): spark(t0,-5,k+2,length=0.16,pan=(-0.3 if k%2 else 0.3))
u=np.clip((t-23.05)/0.95,0,1)*(t>=23.05); lk=np.sin(2*np.pi*np.cumsum(40+36*u**1.6)/SR)*u**1.5*db(-12); buses['synth']+=np.stack([lk,lk],1).astype(np.float32)
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
for h in (2.1,5.3,9.6,14.0,21.0,0.0):
    i0=max(0,int((h-0.08)*SR)); i1=int(h*SR); duck2[i0:i1]=np.minimum(duck2[i0:i1],0.10)
    rel=int(0.6*SR); duck2[i1:i1+rel]=np.minimum(duck2[i1:i1+rel],0.10+0.90*np.linspace(0,1,rel)**1.6)
for k in ('sfx','bed','tick','riser','air'): buses[k]=buses[k]*duck2[:,None]
mix=sum(buses.values())
duck=np.ones(N)
def vac(a,b,floor=0.0,ramp=0.012):
    i0,i1=int(a*SR),int(b*SR); duck[i0:i1]=np.minimum(duck[i0:i1],floor); r=int(ramp*SR); duck[i0-r:i0]=np.minimum(duck[i0-r:i0],np.linspace(1,floor,r))
vac(2.055,2.097); vac(13.45,13.995,floor=0.03,ramp=0.05); vac(20.96,20.998)
mix=mix*duck[:,None]
mix=fft_filter(mix,'hp',24); mix=np.tanh(mix*0.85)/np.tanh(0.85)
mix[-int(0.02*SR):]*=np.linspace(1,0,int(0.02*SR))[:,None]
pkv=np.abs(mix).max(); mix=mix/pkv*0.95
w_=wave.open("night_sfx_v5.wav","wb"); w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((mix*32767).astype(np.int16).tobytes()); w_.close()
print("night v5 mixed, peak scale",pkv)
