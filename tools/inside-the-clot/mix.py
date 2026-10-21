# python3 mix.py out.wav  — "pulse & pressure" sound family for Inside the Clot. Every sound is synthesized here (numpy), no samples, no licences.
import numpy as np, wave, sys
SR=48000; T=24.0; N=int(SR*T); t=np.arange(N)/SR
rng=np.random.default_rng(66)
def db(g): return 10**(g/20)
def sm(a,b,x): k=np.clip((x-a)/(b-a),0,1); return k*k*(3-2*k)
def fft_filter(x,kind,fc,order=2,fc2=None):
    n=len(x); X=np.fft.rfft(x,axis=0); f=np.fft.rfftfreq(n,1/SR)
    if x.ndim==2: f=f[:,None]
    lp=lambda fc_:1/np.sqrt(1+(f/fc_+1e-9)**(2*order))
    if kind=='lp': mag=lp(fc)
    elif kind=='hp': mag=1-lp(fc)
    else: mag=(1-lp(fc))*lp(fc2)
    return np.fft.irfft(X*mag,n=n,axis=0)
B={k:np.zeros((N,2)) for k in ['beat','hit','bed','tex','tone']}
def add(bus,sig,t0,gain=0.0,pan=0.0):
    if sig.ndim==1: sig=np.stack([sig,sig],1)
    a=int(round(t0*SR)); sig=sig*db(gain)
    if a<0: sig=sig[-a:]; a=0
    n=min(len(sig),N-a)
    if n<=0: return
    B[bus][a:a+n,0]+=sig[:n,0]*(1-max(0,pan)); B[bus][a:a+n,1]+=sig[:n,1]*(1+min(0,pan))
def env_exp(n,tau): return np.exp(-np.arange(n)/(tau*SR))
def thump(f0,f1,dur,body=1.0,click=0.15):
    n=int(dur*SR); tt=np.arange(n)/SR; f=f1+(f0-f1)*np.exp(-tt*28); ph=2*np.pi*np.cumsum(f)/SR
    e=np.minimum(1,tt/0.004)*np.exp(-tt/(dur*0.28))
    s=np.sin(ph)*e+0.55*body*np.sin(2*ph+0.4)*e*np.exp(-tt/0.05)+0.3*body*np.tanh(3*np.sin(ph*1.5))*e*np.exp(-tt/0.04)
    nz=rng.standard_normal(n)*np.exp(-tt/0.006)*click; nz=fft_filter(nz,'bp',300,2,2500)
    return s+nz
def heartbeat(t0,g=0.0,muffle=False,weak=1.0):
    lub=thump(120,52,0.30,1.0)*weak; dub=thump(150,64,0.22,0.8)*0.62*weak
    x=np.zeros(int(0.7*SR)); x[:len(lub)]+=lub; o=int(0.27*SR); x[o:o+len(dub)]+=dub
    if muffle: x=fft_filter(x,'lp',420,2)*1.4
    add('beat',x,t0,g)
def noise(n): return rng.standard_normal(n)
def boom(t0,f0,f1,dur,g,bus='hit'):
    n=int(dur*SR); tt=np.arange(n)/SR; f=f1+(f0-f1)*np.exp(-tt*9); ph=2*np.pi*np.cumsum(f)/SR
    e=np.minimum(1,tt/0.003)*np.exp(-tt*(3.2/dur)); s=np.tanh(1.8*np.sin(ph))*e; add(bus,s,t0,g)
def crack(t0,g,dur=0.5):
    n=int(dur*SR); tt=np.arange(n)/SR; x=np.zeros(n)
    for k in range(38):  # brittle micro-fractures cascading
        at=int(SR*0.09*(k/38)**1.7+rng.integers(0,200)); ln=int(SR*0.004)
        if at+ln<n: x[at:at+ln]+=noise(ln)*np.exp(-np.arange(ln)/(0.0009*SR))*(1-k/45)
    x=fft_filter(x,'hp',2200,2)*3; x+=fft_filter(noise(n),'bp',1800,2,7000)*np.exp(-tt/0.035)*0.8
    add('hit',np.stack([x,np.roll(x,37)],1),t0,g)
def swell(t_end,dur,g,f_lo=300,f_hi=5000,bus='tex'):
    n=int(dur*SR); x=noise(n); x=fft_filter(x,'bp',f_lo,2,f_hi); e=(np.arange(n)/n)**3; add(bus,x*e,t_end-dur,g)
def whoosh(t0,dur,g,rise=True,pan0=-0.6,pan1=0.6):
    n=int(dur*SR); x=noise(n); out=np.zeros(n); step=n//24
    for i in range(24):  # sweeping band
        k=i/23; fc=(300+3500*k) if rise else (3800-3500*k); seg=fft_filter(x[i*step:(i+1)*step+1],'bp',fc*0.6,2,fc*1.6); out[i*step:i*step+len(seg)]=seg[:len(out[i*step:i*step+len(seg)])]
    e=np.sin(np.pi*np.arange(n)/n)**2; m=out*e; pan=np.linspace(pan0,pan1,n); a=(pan+1)*np.pi/4
    add('tex',np.stack([m*np.cos(a),m*np.sin(a)],1)*1.4,t0,g)
def bell(t0,f,dur,g,bus='tone'):
    n=int(dur*SR); tt=np.arange(n)/SR; s=sum(a*np.sin(2*np.pi*f*r*tt)*np.exp(-tt*(2.2+1.5*i)/dur) for i,(r,a) in enumerate([(1,1),(2.76,0.45),(5.4,0.22),(8.93,0.1)]))
    add(bus,s*np.minimum(1,tt/0.002),t0,g)
BEAT=60/66
# ---------------- heartbeat track
for k in range(40):
    tb=k*BEAT
    if tb>=23.9: break
    if 8.55<=tb<9.6: continue                       # held breath: the heart sound drops out
    if 2.25<=tb<13.55: heartbeat(tb,-11,muffle=True)  # inside: heard through the vessel
    elif tb<2.25: heartbeat(tb,-7 if k else 0)
    elif tb<21.0:                                    # outside, no blood to the front wall: weaker, uneven
        if k%5==3: continue
        heartbeat(tb+0.04*np.sin(k*2.1),-10-4*sm(13.5,18.6,tb),weak=0.8)
    else: heartbeat(tb,-9)
# frame-0 hit (loop target): big lub + crack + sub
boom(0.0,180,46,1.1,-4); crack(0.0,-16,0.3); swell(0.02,0.4,-30)
# ---------------- snap into the artery 2.25
swell(2.22,0.9,-12,400,6000); whoosh(1.7,0.9,-8); boom(2.25,140,50,0.8,-8)
# ---------------- flow bed inside (pulsatile, darkens as flow stops)
n=N; flow=fft_filter(noise(n),'lp',520,2); flow2=fft_filter(noise(n),'bp',900,2,2400)
puls=np.zeros(n)
for k in range(40):
    tb=k*BEAT; puls+=np.exp(-((t-tb-0.12)/0.16)**2)
puls=0.45+0.8*puls
inside=sm(2.15,2.4,t)*(1-sm(13.4,13.6,t)); stopf=1-sm(11.6,13.0,t); hold=1-0.8*sm(8.5,8.7,t)*(1-sm(9.25,9.4,t))
bed=flow*puls*inside*(0.15+0.85*stopf)*hold*0.75
bruit=flow2*puls*inside*sm(5.0,8.4,t)*stopf*hold*0.55          # turbulence over the narrowing
B['bed']+=np.stack([bed,bed*0.96+0.04*np.roll(bed,90)],1)+np.stack([np.roll(bruit,40),bruit],1)
# age ticks 4.6-8.4: one per year, pitch climbing
prev=None
for f in range(int(4.6*30),int(8.5*30)):
    tt_=f/30; a=25+int(np.floor(30*float(sm(2.6,8.4,tt_))+1e-6))
    if prev is not None and a!=prev:
        k=a-25; m=int(0.03*SR); s=np.sin(2*np.pi*(1300+18*k)*np.arange(m)/SR)*np.exp(-np.arange(m)/(0.006*SR)); add('tex',s,tt_,-24+0.12*k,pan=0.3*np.sin(k))
    prev=a
# held breath 8.6-9.3: thin high tone only
m=int(0.75*SR); hz=np.sin(2*np.pi*2350*np.arange(m)/SR)*np.sin(np.pi*np.arange(m)/m)**2; add('tone',hz,8.55,-40)
# ---------------- the crack 9.3: the biggest hit (reverse suck, 60 ms vacuum, crack + pitch-drop body + sub + debris hiss)
swell(9.24,0.6,-10,200,7000)
crack(9.3,-4,0.6); boom(9.3,320,58,1.6,-1); boom(9.3,90,38,2.0,-9)
hiss=fft_filter(noise(int(1.4*SR)),'bp',2500,2,9000)*env_exp(int(1.4*SR),0.35); add('tex',np.stack([hiss,np.roll(hiss,60)],1),9.31,-17)
bell(9.32,196,2.5,-20)
# ---------------- clot forming 9.7-13.0: granular platelet clicks getting denser, sticky creak, seal thud
for i in range(520):
    u=(i/520)**0.6; tc=9.7+3.3*u+rng.uniform(-0.02,0.02)
    m=int(0.012*SR); fr=rng.uniform(2200,5200)*(0.8+0.3*u); s=np.sin(2*np.pi*fr*np.arange(m)/SR)*np.exp(-np.arange(m)/(0.0018*SR))
    add('tex',s,tc,-31+5*u,pan=rng.uniform(-0.8,0.8))
cr=np.zeros(int(3.3*SR)); tt=np.arange(len(cr))/SR; cr=np.sin(2*np.pi*(70+40*tt/3.3)*tt+3*np.sin(2*np.pi*7*tt))*sm(0,3.0,tt)*0.5; cr=fft_filter(cr,'lp',600)
add('tone',cr,9.7,-18)
boom(13.0,200,60,0.9,-8); swell(12.98,0.8,-22,150,2000)
# ---------------- back outside 13.55
whoosh(13.15,0.8,-10,rise=False,pan0=0.6,pan1=-0.6)
# minutes: tick every 5 min of the counter, dark two-note drone underneath
prev=None
for f in range(int(13.8*30),int(18.7*30)):
    tt_=f/30; u=min(1,max(0,(tt_-13.8)/4.6)); mn=int(np.floor(90*u**0.9+1e-6))//5
    if prev is not None and mn!=prev:
        m=int(0.05*SR); s=np.sin(2*np.pi*880*np.arange(m)/SR)*np.exp(-np.arange(m)/(0.01*SR))+0.5*np.sin(2*np.pi*1760*np.arange(m)/SR)*np.exp(-np.arange(m)/(0.004*SR)); add('tex',s,tt_,-22)
    prev=mn
dr=sum(np.sin(2*np.pi*f_*t+0.3*np.sin(2*np.pi*0.21*t*i))*a for i,(f_,a) in enumerate([(110,1),(110.6,0.8),(164.8,0.55),(220.4,0.25)]))
dr=fft_filter(np.tanh(1.3*dr),'lp',700)*sm(13.6,16.5,t)*(1-sm(20.6,21.6,t))*0.22
B['tone']+=np.stack([dr,np.roll(dr,120)],1)
# twist 18.8: low gong
bell(18.8,82.4,3.0,-8); boom(18.8,140,55,1.2,-12)
# end line 21.1 + loop riser into frame 0
bell(21.1,164.8,2.4,-14); boom(21.1,160,50,0.8,-14)
n=int(1.4*SR); tt=np.arange(n)/SR; fr_=220*2**(tt/1.4*1.0); ris=np.sin(2*np.pi*np.cumsum(fr_)/SR)*(tt/1.4)**2.5*0.5; add('tone',ris,22.6,-20); swell(24.0,1.0,-20,500,6000)
# ---------------- buses -> master
def hp(x,fc): return fft_filter(x,'hp',fc,2)
mix=B['hit']*1.0 + B['beat']*1.0 + hp(B['bed'],90)*0.9 + hp(B['tex'],120) + hp(B['tone'],70)*0.9
# side-chain: duck bed/tex under the big hits
duck=1-0.6*(np.exp(-np.clip(t-9.3,0,None)/0.5)*(t>=9.3))-0.4*(np.exp(-np.clip(t-0.0,0,None)/0.3))
mix=B['hit']+B['beat']+(mix-B['hit']-B['beat'])*duck[:,None]
# small room reverb on everything except the frame-0 window tail
ir_n=int(1.2*SR); ir=noise(ir_n)*np.exp(-np.arange(ir_n)/(0.28*SR)); ir=fft_filter(ir,'lp',3500)*0.012
rev=np.stack([np.fft.irfft(np.fft.rfft(mix[:,c],N+ir_n)*np.fft.rfft(ir,N+ir_n),N+ir_n)[:N] for c in range(2)],1)
mix=mix+rev*0.6
mix=np.tanh(mix*1.1)/np.tanh(1.1)
mix/=np.max(np.abs(mix))/0.89
with wave.open(sys.argv[1],'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(mix,-1,1)*32767).astype(np.int16).tobytes())
print("mix done")
