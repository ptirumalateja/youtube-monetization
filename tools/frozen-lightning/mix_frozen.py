# Frozen Lightning sound design: fully synthesised in numpy (no sample files, no licences to track).
# Family: "storm and glass" - thunder cracks, electric crackle, heat roar, glass/crystal partials.
# Cue times follow the scene timeline in index.html. Output: frozen_mix.wav (48 kHz stereo, about -15 LUFS).
import numpy as np, sys
from scipy.signal import butter, sosfilt, fftconvolve
import pyloudnorm as pyln
SR=48000; T=20.0; N=int(SR*T)
rng=np.random.default_rng(7)
def t_(d): return np.arange(int(d*SR))/SR
def filt(x,kind,f,order=4):
    if kind=='bp': sos=butter(order,[f[0]/(SR/2),f[1]/(SR/2)],'band',output='sos')
    else: sos=butter(order,f/(SR/2),kind,output='sos')
    return sosfilt(sos,x)
def pink(n):
    w=rng.standard_normal(n); X=np.fft.rfft(w); f=np.arange(len(X)); f[0]=1; X/=np.sqrt(f); y=np.fft.irfft(X,n); return y/np.abs(y).max()
def brown(n):
    y=np.cumsum(rng.standard_normal(n)); y=filt(y,'high',20,2); return y/np.abs(y).max()
def env_ad(n,a,d):  # attack seconds, exponential decay time constant
    t=np.arange(n)/SR; e=np.minimum(1,t/max(a,1e-4))*np.exp(-np.maximum(0,t-a)/d); return e
def place(bus,x,t0,g=1.0):
    i=int(round(t0*SR));
    if i<0: x=x[-i:]; i=0
    j=min(len(bus),i+len(x)); bus[i:j]+=g*x[:j-i]
def sweep(f0,f1,d,curve='exp'):
    t=t_(d); k=t/d
    f=f0*(f1/f0)**k if curve=='exp' else f0+(f1-f0)*k
    return np.sin(2*np.pi*np.cumsum(f)/SR)
HIT=np.zeros(N); SFX=np.zeros(N); BED=np.zeros(N); TONE=np.zeros(N); SUB=np.zeros(N)

# ---------------------------------------------------------------- building blocks
def crack(size=1.0):
    n=int(0.5*SR); x=np.zeros(n)
    b=filt(rng.standard_normal(n),'high',1800)*env_ad(n,0.0005,0.018); x+=b*1.0
    for k in range(int(10*size)):  # micro crackles over the first 150 ms
        t0=abs(rng.normal(0,0.05)); m=int(0.02*SR); c=filt(rng.standard_normal(m),'bp',(2500,9000))*env_ad(m,0.0002,0.004); place(x,c,t0,0.5*rng.random())
    return x*size
def body(f0,f1,d,dec,drive=2.5):
    s=sweep(f0,f1,d)*env_ad(int(d*SR),0.004,dec); return np.tanh(s*drive)/np.tanh(drive)
def rumble(d,lp=260,dec=1.6):
    n=int(d*SR); r=filt(brown(n),'low',lp)*env_ad(n,0.05,dec)
    mod=filt(rng.standard_normal(n),'low',3); mod=1+1.2*mod/np.abs(mod).max(); return r*np.clip(mod,0.2,2.2)
def subhit(f=44,dec=0.7): n=int(3*dec*SR); return np.sin(2*np.pi*f*t_(3*dec))*env_ad(n,0.006,dec)
def sparks(d,rate,lo=2500,hi=8000):
    n=int(d*SR); x=np.zeros(n)
    for _ in range(int(d*rate)):
        m=int(rng.uniform(0.002,0.012)*SR); c=filt(rng.standard_normal(m),'bp',(lo,hi))*env_ad(m,0.0002,m/SR/4); place(x,c,rng.uniform(0,d),rng.uniform(0.2,1))
    return x
def glass_ping(f,dec=0.6,amp=1.0):
    d=dec*4; t=t_(d); y=np.zeros(len(t))
    for r,a in [(1,1),(2.76,0.5),(5.40,0.28),(8.93,0.14)]:
        y+=a*np.sin(2*np.pi*f*r*t+rng.random()*6)*np.exp(-t/(dec/(0.6+0.4*r)))
    return y*amp*np.minimum(1,t/0.0015)
def shatter(d=1.2,count=46):
    n=int(d*SR); x=np.zeros(n)
    for _ in range(count):
        f=rng.uniform(1800,9000); g=glass_ping(f,rng.uniform(0.08,0.45),rng.uniform(0.15,0.6)); place(x,g,abs(rng.normal(0,0.04)))
    return x[:n]
def whoosh(d,f0,f1,peak=0.6):
    n=int(d*SR); w=rng.standard_normal(n); out=np.zeros(n); B=32; seg=n//B
    for b in range(B):
        k=b/B; fc=f0*(f1/f0)**k; s=filt(w,'bp',(fc*0.6,min(fc*1.6,20000)),2)[b*seg:(b+1)*seg]; out[b*seg:(b+1)*seg]=s
    t=np.arange(n)/n; e=np.where(t<peak,(t/peak)**2,((1-t)/(1-peak))**1.5); return out*e
def revswell(d): n=int(d*SR); x=filt(rng.standard_normal(n),'bp',(300,6000))*np.exp(-np.arange(n)/SR/0.35); return x[::-1]
def reverb(x,dec=1.8,mix=0.25):
    n=int(dec*SR*1.5); ir=rng.standard_normal(n)*np.exp(-np.arange(n)/SR/(dec/6.9)); ir=filt(ir,'low',5000,2); ir/=np.sqrt((ir**2).sum())
    return x+mix*fftconvolve(x,ir)[:len(x)]

# ---------------------------------------------------------------- storm opening (0 - 2.7)
place(HIT,crack(1.0),0.0,0.9); place(HIT,body(240,62,0.55,0.35),0.0,0.8); place(SUB,subhit(42,0.6),0.0,0.8)
place(SFX,rumble(4.0,240,1.8),0.03,1.0)
for ts,a in [(0.10,0.45),(0.27,0.6),(0.58,0.35)]: place(HIT,crack(0.5),ts,a)
rain=filt(pink(N),'bp',(900,9000))*0.22; wind=filt(pink(N),'bp',(120,900))*0.5
storm_env=np.ones(N); tt=np.arange(N)/SR
storm_env=np.clip(1-np.clip((tt-2.4)/0.4,0,1),0,1)+np.clip((tt-16.8)/1.2,0,1)*0.9
BED+=(rain+wind*(0.6+0.4*np.sin(tt*0.9)))*storm_env
place(SFX,rumble(3.0,320,1.0),0.85,0.9); place(SFX,sparks(1.4,40,2000,6000),0.4,0.5)
place(SFX,revswell(0.45),1.92-0.45,0.35)
place(HIT,crack(0.8),1.92,0.85); place(HIT,body(320,90,0.35,0.22,3),1.92,0.55); place(SUB,subhit(50,0.35),1.92,0.5)
place(SFX,whoosh(0.9,300,4000,0.75),1.9,0.9)
# ---------------------------------------------------------------- grains (2.6 - 4.8): sand hiss, crackling arcs, hum
n=int(2.4*SR); sand=sparks(2.4,900,3000,11000)*0.40; place(SFX,sand*np.linspace(0.3,1,n),2.5)
for k in range(int(2.2*14)):
    ts=2.6+k/14
    if rng.random()<0.75: place(SFX,sparks(0.07,120,2000,7000),ts,0.9)
hum_t=t_(10.5); f=110+70*np.clip((hum_t-1.5)/8,0,1)**1.5
hum=np.tanh(1.8*sum(np.sin(2*np.pi*np.cumsum(f*h)/SR)/h for h in range(1,7)))
hum=filt(hum,'bp',(150,2400))*np.clip(hum_t/2.0,0,1)
place(TONE,hum*0.16,2.6)
# ---------------------------------------------------------------- crystal (4.8 - 7.3): glass partial chord + ticks that speed up
for fq,dl in [(587.3,0.0),(880,0.35),(1174.7,0.7),(1318.5,1.05)]: place(TONE,glass_ping(fq,1.4,0.22),4.85+dl)
place(TONE,reverb(np.concatenate([np.zeros(10),glass_ping(1760,0.9,0.12)])),4.85)
t=4.9;
while t<10.4:
    rate=3+40*((t-4.9)/5.5)**2; place(SFX,glass_ping(rng.uniform(3200,5200),0.03,0.18+0.25*min(1,(t-4.9)/4)),t); t+=1/rate
# heat roar (5.5 - 10.45): detuned saws sweeping up + noise riser
d=4.95; tr=t_(d); k=tr/d; f=60*(4.5)**(k**1.3)
saw=sum(np.sin(2*np.pi*np.cumsum(f*(1+dt))/SR*h)/h for dt in (-0.012,0,0.009) for h in range(1,8))
roar=np.tanh(1.5*saw)*k**1.6; roar=filt(roar,'bp',(90,3500))
nr=filt(rng.standard_normal(len(tr)),'bp',(400,7000))*k**2.2
place(TONE,(roar*0.20+nr*0.09),5.5)
# melt crunch at 7.3
place(SFX,filt(rng.standard_normal(int(0.5*SR)),'bp',(200,3000))*env_ad(int(0.5*SR),0.005,0.12),7.3,0.55); place(SFX,sparks(0.4,300,1500,6000),7.3,0.7)
place(HIT,body(180,80,0.3,0.18,2),7.3,0.35)
# electric bursts in the bolt phase
for k in range(14):
    place(SFX,sparks(0.12,500,2500,9000),8.6+k*0.13+rng.uniform(0,0.05),0.5+0.4*k/14)
# ---------------------------------------------------------------- held breath 10.45-11.0, freeze hit at 11.0
place(SFX,revswell(0.5),11.0-0.5-0.06,0.5)
place(HIT,shatter(1.6,60),11.0,0.24); place(HIT,body(300,95,0.45,0.28,3),11.0,0.32); place(HIT,crack(0.6),11.0,0.3); place(SUB,subhit(48,0.45),11.0,0.4)
for k in range(9): place(SFX,glass_ping(rng.uniform(2200,5200),0.18,0.12),11.35+k*0.14+rng.uniform(0,0.08))
pad_t=t_(3.0); pad=sum(np.sin(2*np.pi*f0*pad_t+np.sin(pad_t*0.7+i)*0.6) for i,f0 in enumerate([1174.7,1318.5,1760,2349.3]))*np.exp(-pad_t/0.9)*np.minimum(1,pad_t/0.05)
place(TONE,pad*0.035,11.0)
# ---------------------------------------------------------------- pull-out 12.6-13.6, REVEAL hit 13.6 (biggest)
place(SFX,whoosh(1.0,5000,250,0.8),12.55,1.0); place(SFX,revswell(0.7),13.6-0.7-0.07,0.7)
place(HIT,crack(1.2),13.6,0.8); place(HIT,body(170,52,0.9,0.6,3.2),13.6,1.25)
gt=t_(4.5); gong=sum(a*np.sin(2*np.pi*f0*gt+i)*np.exp(-gt/dd) for i,(f0,a,dd) in enumerate([(98,1,2.4),(153.5,0.7,1.9),(231,0.5,1.4),(318,0.35,1.0),(447,0.25,0.7)]))*np.minimum(1,gt/0.004)
place(HIT,np.tanh(gong*1.4)*0.8,13.6); place(HIT,shatter(1.8,26)*0.5,13.62); place(SUB,subhit(40,1.1),13.6,1.0)
place(SFX,rumble(5.0,200,2.2),13.65,0.6)
# warm drone under the reveal (13.6-17.6)
dt_=t_(4.6); ch=sum(np.sin(2*np.pi*np.cumsum(np.full(len(dt_),f0*(1+0.002*np.sin(dt_*0.5+f0))))/SR*h)/h for f0 in (73.42,110.0,146.83,220.0) for h in (1,2,3,4))
ch=filt(np.tanh(ch*0.6),'low',1100)*np.minimum(1,dt_/0.8)*np.minimum(1,(4.6-dt_)/1.2)
place(TONE,ch*0.11,13.6)
# ghost bolt 14.9-16.6: distant roll
place(SFX,rumble(3.0,180,1.2),15.0,0.5); place(SFX,sparks(0.6,150,2000,6000),14.95,0.25)
# ---------------------------------------------------------------- rise and end line (17.2-19.4)
place(SFX,whoosh(1.8,200,2500,0.7),17.2,0.8)
place(TONE,reverb(np.concatenate([glass_ping(880,1.2,0.25),np.zeros(SR)]),2.5,0.5),17.75)
place(TONE,reverb(np.concatenate([glass_ping(1318.5,1.0,0.18),np.zeros(SR)]),2.5,0.5),18.35)
# loop link: crackle and rising leader tone into frame 0
lt=t_(0.55); lead=np.sin(2*np.pi*np.cumsum(200*(3.5)**(lt/0.55))/SR)*(lt/0.55)**2
place(TONE,lead*0.08,19.45); place(SFX,sparks(0.55,260,2500,9000)*np.linspace(0.1,1,int(0.55*SR)),19.45,0.6)
place(SFX,revswell(0.5)*0.5,19.5)

# ---------------------------------------------------------------- held-breath window: duck everything but the swell
def duck(bus,a,b,floor=0.012,ramp=0.04):
    g=np.ones(N); i0,i1=int(a*SR),int(b*SR); r=int(ramp*SR)
    g[i0:i1]=floor; g[max(0,i0-r):i0]=np.linspace(1,floor,min(r,i0)); return bus*g
for nm in ('BED','TONE','SFX'):
    globals()[nm]=duck(globals()[nm],10.45,10.94)
BED=duck(BED,13.52,13.6,0.05,0.01); TONE=duck(TONE,13.52,13.6,0.05,0.01)
# bus processing: phones cannot play below ~90 Hz, keep sub on the hit bus only
for nm in ('SFX','BED','TONE'): globals()[nm]=filt(globals()[nm],'high',90,2)
HITB=reverb(HIT,1.6,0.30)+filt(SUB,'low',120,2)*0.8
# side-chain: duck beds under the hits
env=np.abs(HITB); env=filt(env,'low',8,1); env/=env.max()+1e-9; sc=1-0.55*np.clip(env*2,0,1)
mix=HITB*1.0+SFX*0.9*sc+BED*1.8*sc+TONE*0.9*sc
# stereo: slight decorrelation of beds
L=mix+0.15*filt(BED,'low',4000)*sc; R=mix-0.15*filt(BED,'low',4000)*sc
st=np.stack([L,R],1); st=np.tanh(st*1.1)/np.tanh(1.1)
meter=pyln.Meter(SR); lu=meter.integrated_loudness(st); st*=10**((-15.0-lu)/20)
pk=np.abs(st).max(); lim=10**(-1.5/20)
if pk>lim: st=np.tanh(st/lim)*lim
lu2=meter.integrated_loudness(st); print('LUFS',round(lu,2),'->',round(lu2,2),'peak',round(20*np.log10(np.abs(st).max()),2))
# 10 ms fades at both ends are NOT applied: the end leads into frame 0's crack for the loop
import wave
out=(np.clip(st,-1,1)*32767).astype(np.int16)
with wave.open(sys.argv[1] if len(sys.argv)>1 else 'frozen_mix.wav','wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())
