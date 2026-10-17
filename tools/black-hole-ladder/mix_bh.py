import subprocess, numpy as np, wave, os
SR=48000; T=28.2; N=int(SR*T)
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
sp=L("849772__mikiko850__electric-sparks.wav"); m_=mono(sp); hop=int(0.12*SR); en=np.array([(m_[i*hop:(i+1)*hop]**2).mean() for i in range(len(m_)//hop)]); top=np.argsort(en)[::-1]
chosen=[]
for i in top:
    if all(abs(i-c)>6 for c in chosen): chosen.append(int(i))
    if len(chosen)>=10: break
def spark(t0,gain,k,length=0.14,pan=0.0): i=chosen[k%len(chosen)]; place('sfx',sp[i*hop:i*hop+int(length*SR)],t0,gain,fi=0.002,fo=0.03,pan=pan)
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


ris=L("822420__audiopapkin__riser-hit-sfx-120.wav")
EXP="814046__qubodup__explosion-from-another-dimension.wav"; IMP="814047__qubodup__fantasy-implosion.wav"; DARK="869757__mikiko850__dark-suspense-accent.wav"
wd=L("22331__sleepcircle__wind.ogg"); PLASMA="850262__cvltiv8r__orbiting-plasma-burst-and-trail-fx.wav"
def ping(t0,f,dec,gain,pan=0.0):
    n=int((dec+0.2)*SR); tt=np.arange(n)/SR; fb=f*(1-0.012*(1-np.exp(-tt*3)))
    ph=2*np.pi*np.cumsum(fb)/SR; sig=(np.sin(ph)+0.22*np.sin(2.76*ph)*np.exp(-tt*4)+0.1*np.sin(5.4*ph)*np.exp(-tt*8))*np.exp(-tt/(dec*0.35))*(1-np.exp(-tt/0.012))
    add('air',sig.astype(np.float32),t0,gain,pan)
def drone(t0,t1,f0,gain,bus='synth',f1=None,harm=7,lp=420):
    n=N; f1=f0 if f1 is None else f1; fr=np.interp(t,[t0,t1],[f0,f1]); ph=2*np.pi*np.cumsum(fr)/SR; out=np.zeros(N,np.float32)
    for mult,vol in ((1,1.0),(1.5,0.7),(2,0.8)):
        for dt in (-8,0,9): out+=sum(np.sin(ph*mult*2**(dt/1200)*h)/h for h in range(1,harm+1))*vol
    env=np.clip((t-t0)/1.0,0,1)*np.clip((t1-t)/0.6,0,1)*((t>=t0)&(t<t1)); o=fft_filter(np.stack([out,out],1),'lp',lp)*env[:,None]
    buses[bus]+=(o/max(np.abs(o).max(),1e-6)*db(gain)*0.5).astype(np.float32)
CUT=6.4
# ================= 0 - 6.4  SOLAR SYSTEM + the plunge into the speck
hit_v3(0.0,0.75,gain=0); place('hit',seg(EXP,0.12,1.6),0.0,-9,fi=0.002,fo=0.6); place('hit',seg(DARK,4.95,6.4),0.0,-8,fi=0.002,fo=0.4)
for t0 in np.arange(0.30,0.85,0.025): burst(t0,0.008,-20,hp=3200,bus='tick')
shepard(0.2,1.5,-15,f_lo=90,octs=5); whoosh_syn(0.2,1.5,-11,peak=0.7)
choir(1.4,5.2,110,-24)                                   # soft pad: the calm orrery
crackle(1.5,5.0,26,-24)                                  # asteroid glitter
for k_,tc in enumerate((1.9,2.6,3.1)): ping(tc,106*[8,5,6][k_],1.4,-24,pan=[-0.7,0.5,0.1][k_])   # planets / comet passing
drone(3.2,6.35,55,-15,f1=70)                             # the dark thing is coming
for tt_ in np.arange(3.35,5.2,0.95): hit_v3(tt_,0.12,gain=-12)   # pulse = ring pulse around the speck
suck(5.0,5.9,gain=-9,lo=400,hi=6000); shepard(4.9,1.45,-11,f_lo=80,octs=5,rate=2.0,shape=1.8); whoosh_syn(5.2,1.1,-8,peak=0.85)
# ================= 6.4  CUT: flash into the stellar-mass black hole
suck(6.0,6.395,gain=-6); hit_v3(CUT,1.0,gain=1); braaam(CUT,1.4,98,-14); place('hit',seg(EXP,0.12,2.6),CUT,-8,fi=0.002,fo=0.9)
# ---- STOP 1 stellar (6.5-8.6): X-ray flicker, spiral hiss, whine
crackle(6.5,8.4,140,-15)
whine_f=np.interp(t,[6.4,8.6],[2100,3600]); wp_=2*np.pi*np.cumsum(whine_f)/SR; wm=((t>=6.5)&(t<8.6))*np.clip((8.6-t)/0.3,0,1); buses['air']+=(np.stack([np.sin(wp_)*wm,np.sin(wp_+0.4)*wm],1)*db(-31)).astype(np.float32)
whoosh_syn(7.0,1.6,-8,peak=0.4,pan0=-0.8,pan1=0.8); suck(8.2,8.595,gain=-9)
# ---- STOP 2 Sgr A* (8.6-12.4): dark drone + orbiting star pings + the hot-spot heartbeat
hit_v3(8.6,0.5,gain=-3); drone(8.6,12.4,52,-14)
for i_,mult in enumerate((8,6,5,4,3,2.5,2,1.5,6,4)): ping(9.0+0.30*i_,106.0*mult,0.9+0.12*i_,-19-0.3*i_,pan=np.sin(i_*0.9+0.4)*0.85)
for tt_ in np.arange(9.2,12.2,1.1): hit_v3(tt_,0.10,gain=-14)
crackle(8.8,12.2,45,-24)
# ---- pull-back 2 (12.4 - 14.6)
suck(12.0,12.395,gain=-8); hit_v3(12.4,0.6,gain=-1); whoosh_syn(12.4,2.2,-8,peak=0.35); hit_v3(14.6,0.45,gain=-3)
# ---- STOP 3 M87* (14.6-18.4): choir + jet sweep + knots
choir(14.7,18.3,106,-17)
jet=mono(L("115555__vartioh__synth_jet.wav")); n=int(3.2*SR); rate=np.linspace(0.6,1.8,n); pos=np.cumsum(rate)[:n]%(len(jet)-2)
jr=np.interp(pos,np.arange(len(jet)),jet).astype(np.float32); place('riser',np.stack([jr,jr],1),15.0,-20,fi=0.6,fo=0.02)
for k_ in range(6): ping(15.1+0.5*k_,106*[3,4,5,6,5,4][k_],1.6,-22,pan=[-0.6,0.4,-0.2,0.7,-0.5,0.2][k_])   # jet knots passing
place('bed',seg(PLASMA,0.5,3.2),15.0,-15,fi=0.1,fo=0.6)
# ---- pull-back 3 (18.4 - 20.8)
suck(18.0,18.395,gain=-8); hit_v3(18.4,0.6,gain=-1); whoosh_syn(18.4,2.3,-8,peak=0.35); hit_v3(20.8,0.55,gain=-2)
# ---- STOP 4 TON 618 (20.8-25.0): heavy sub drone, shepard riser, distorted braaam, stutter gate into the held breath
drone(20.8,25.0,41,-9,f1=46,lp=520); choir(21.0,24.0,82,-17)
shepard(21.6,2.4,-12,f_lo=70,octs=5,shape=1.6); braaam(20.8,2.8,82,-16,bright=1800)
uu=np.clip((t-22.8)/1.3,0,1); fg=4+11*uu**1.5; phg=np.cumsum(fg)/SR
gate=np.where((t>=22.8)&(t<24.1),0.30+0.70*(np.sin(2*np.pi*phg)>0),1.0); buses['riser']=buses['riser']*gate[:,None]; buses['synth']=buses['synth']*np.where((t>=22.8)&(t<24.1),gate,1.0)[:,None]
suck(24.55,24.95,gain=-10,lo=400,hi=5000)
# ================= 25.0  THE BIG ONE: the dive back toward the Solar System
hit_v3(25.0,1.5,gain=2); braaam(25.0,3.2,82,-9,bright=1500); braaam(25.0,3.2,164,-12,bright=2400)
place('hit',seg(EXP,0.12,6.0),25.0,-4,fi=0.002,fo=1.2); place('hit',ris[int(6.15*SR):int(9.6*SR)],25.0,-10,fi=0.003,fo=1.5); whoosh_syn(25.0,1.8,-9,peak=0.15)
tt=t-25.0; m=(tt>=0)&(tt<3.0); env=np.zeros(N); env[m]=np.minimum(1,tt[m]/0.004)*np.exp(-tt[m]/0.9); sub=np.sin(2*np.pi*np.cumsum(36*np.ones(N))/SR)*0.7
buses['synth']+=(np.stack([sub*env,sub*env],1)*db(-12)).astype(np.float32); burst(25.0,0.7,-12,hp=3000,bus='air')
whoosh_syn(26.0,1.1,-9,peak=0.5,pan0=0.9,pan1=-0.9)
# ---- 27 - 28.2 landing in the Solar System, loop link
place('bed',wd[int(8*SR):int(11*SR)],27.0,-14,fi=0.3,fo=0.04); bell(27.35,1319,2.0,-16); bell(27.35,659,2.0,-22)
for k,t0 in enumerate((27.7,27.82,27.93,28.02,28.1)): spark(t0,-6,k+2,length=0.16,pan=(-0.3 if k%2 else 0.3))
u=np.clip((t-27.6)/0.6,0,1)*(t>=27.6); lk=np.sin(2*np.pi*np.cumsum(40+36*u**1.6)/SR)*u**1.5*db(-12); buses['synth']+=np.stack([lk,lk],1).astype(np.float32)

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
for h in (0.0,CUT,8.6,12.4,14.6,18.4,20.8,25.0):
    i0=max(0,int((h-0.08)*SR)); i1=int(h*SR); duck2[i0:i1]=np.minimum(duck2[i0:i1],0.10)
    rel=int(0.6*SR); duck2[i1:i1+rel]=np.minimum(duck2[i1:i1+rel],0.10+0.90*np.linspace(0,1,rel)**1.6)
for k in ('sfx','bed','tick','riser','air'): buses[k]=buses[k]*duck2[:,None]
mix=sum(buses.values())
duck=np.ones(N)
def vac(a,b,floor=0.0,ramp=0.012):
    i0,i1=int(a*SR),int(b*SR); duck[i0:i1]=np.minimum(duck[i0:i1],floor); r=int(ramp*SR); duck[i0-r:i0]=np.minimum(duck[i0-r:i0],np.linspace(1,floor,r))
vac(6.36,6.397); vac(12.36,12.397); vac(18.36,18.397); vac(24.1,24.95,floor=0.03,ramp=0.05); vac(24.96,24.997)
mix=mix*duck[:,None]
mix=fft_filter(mix,'hp',24); mix=np.tanh(mix*0.85)/np.tanh(0.85)
mix[-int(0.02*SR):]*=np.linspace(1,0,int(0.02*SR))[:,None]
pkv=np.abs(mix).max(); mix=mix/pkv*0.95
w_=wave.open("bh_ladder_sfx.wav","wb"); w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((mix*32767).astype(np.int16).tobytes()); w_.close()
print("bh mixed, peak scale",pkv)
