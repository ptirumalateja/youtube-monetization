# Photon Rain sound: fully synthesised (no samples, no credits needed).
# Family: "glass rain + filling bottle + shutter". Every sound has a visual cause:
#   photon landings -> glass ticks, bucket fill -> rising resonance, frame 0 and the photo reveal -> shutter hits.
import numpy as np, wave, sys
SR=48000; T=22.0; N=int(SR*T); rng=np.random.default_rng(7)
t=np.arange(N)/SR
def env_ad(n,a,d):
    e=np.ones(n); na=max(1,int(a*SR)); e[:na]=np.linspace(0,1,na); m=np.arange(n-na)/SR; e[na:]=np.exp(-m/d); return e
def sm(a,b,x): k=np.clip((x-a)/(b-a),0,1); return k*k*(3-2*k)
def place(bus,sig,ts):
    i=int(ts*SR); j=min(N,i+len(sig));
    if i<N and j>i: bus[i:j]+=sig[:j-i]
def onepole_lp(x,fc):
    a=np.exp(-2*np.pi*fc/SR); y=np.empty_like(x); s=0.0
    for i in range(len(x)): s=(1-a)*x[i]+a*s; y[i]=s
    return y
def fft_filter(x,lo,hi):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); m=((f>=lo)&(f<=hi)).astype(float)
    # soft edges
    m=np.clip(m+np.exp(-((f-lo)/(0.15*lo+1))**2)*(f<lo)+np.exp(-((f-hi)/(0.15*hi+1))**2)*(f>hi),0,1); return np.fft.irfft(X*m,len(x))
def hp(x,fc): return fft_filter(x,fc,20000)
tick=np.zeros(N); bed=np.zeros(N); fill=np.zeros(N); hit=np.zeros(N); whoosh=np.zeros(N); pad=np.zeros(N)
# ---------------- photon ticks: rate follows the visible landings
def rate(tt):
    r=np.zeros_like(tt)
    r+= 900*np.exp(-((tt-0.30)/0.22)**2)                     # first wave just after frame 0
    r+= 160*sm(0.3,0.8,tt)*(1-sm(6.8,8.2,tt))                 # overview rain
    r+= 110*sm(8.6,9.3,tt)*(1-sm(14.45,14.6,tt))              # macro rain over the buckets
    r+= 900*np.exp(-((tt-22.30)/0.22)**2)                     # next loop's first wave
    return r
dt=1/200; grid=np.arange(0,T,dt)
for g0 in grid:
    k=rng.poisson(rate(np.array([g0]))[0]*dt)
    for _ in range(k):
        ts=g0+rng.random()*dt; f=rng.uniform(2400,6200) if ts<8.4 else rng.uniform(1500,4200)
        n=int(0.035*SR); x=np.arange(n)/SR; a=rng.uniform(0.15,1.0)
        s=np.sin(2*np.pi*f*x+rng.random()*6.28)*np.exp(-x/rng.uniform(0.004,0.012))*a
        place(tick,s,ts)
# ---------------- rain hiss bed
nz=rng.standard_normal(N); hiss=fft_filter(nz,3000,12000); hiss/=np.abs(hiss).max()
bed+=hiss*(0.10*rate(t)/160).clip(0,1.4)
air=fft_filter(rng.standard_normal(N),400,2500); air/=np.abs(air).max(); bed+=air*0.03*(sm(0,1.0,t)*(1-sm(20.8,21.8,t)))
# ---------------- drone pad (A, E, A, C#) slow beating; dims during the held breath
pf=[110,164.8,220,277.2,330]; pd=np.zeros(N)
for i,f in enumerate(pf): pd+=np.sin(2*np.pi*f*t+0.4*np.sin(2*np.pi*0.13*(i+1)*t))*(1/(1+i*0.6))
lv=0.05*sm(0.2,2.0,t)*(1-0.9*sm(14.4,14.65,t))+0.07*sm(15.2,17.4,t)*(1-sm(20.6,21.9,t)) ; lv=lv*(1-sm(14.4,14.65,t)*(1-sm(15.1,15.3,t)))
pad+=pd*lv
# ---------------- bucket fill: resonance rising like a filling bottle (9.0 -> 14.55)
k=np.clip((t-9.0)/(14.55-9.0),0,1); fc=260*(1+3.2*k**1.1); ph=2*np.pi*np.cumsum(fc)/SR
fl=(np.sin(ph)+0.35*np.sin(2*ph)+0.15*np.sin(3*ph))*(0.75+0.25*np.sin(2*np.pi*7*t))
fill+=fl*0.075*sm(9.0,9.8,t)*(1-sm(14.45,14.6,t))
# second, smaller bucket voice an octave above with noisy flutter (the phone field)
ph2=2*np.pi*np.cumsum(fc*2.0*(1+0.012*np.sin(2*np.pi*13*t)))/SR
fill+=np.sin(ph2)*0.035*sm(9.3,10.2,t)*(1-sm(14.45,14.6,t))*(0.6+0.4*np.abs(np.sin(2*np.pi*3.1*t+np.sin(t*11))))
# ---------------- whooshes: dive (6.6-9.2) and pull-out (15.3-17.6, reversed swell into the reveal)
wn=fft_filter(rng.standard_normal(N),150,6000); wn/=np.abs(wn).max()
def sweep(a,b,peak,lvl,rev=False):
    e=np.where(t<peak,sm(a,peak,t),1-sm(peak,b,t)) if not rev else sm(a,b,t)*(t<b)
    return e*lvl
dive=sweep(6.5,9.4,8.0,0.32); pull=sweep(15.25,17.42,0,0.30,rev=True)
whoosh+=wn*dive
lo=onepole_lp(rng.standard_normal(N),900); lo/=np.abs(lo).max(); whoosh+=lo*pull*0.9+wn*pull*0.25
# vacuum before the reveal hit
whoosh*=1-0.95*(sm(17.36,17.40,t)*(1-sm(17.44,17.46,t)))
# ---------------- shutter hits
def shutter(big):
    n=int((1.6 if big else 0.7)*SR); x=np.arange(n)/SR; s=np.zeros(n)
    for c0,amp in [(0.0,1.0),(0.045 if big else 0.038,0.8)]:
        i=int(c0*SR); m=n-i; xx=np.arange(m)/SR
        cl=fft_filter(rng.standard_normal(m),1800,9000)*np.exp(-xx/0.006)*amp*2.2
        s[i:]+=cl
    body_f=np.where(x<0.25,220*np.exp(-x/0.12)+90,90) if big else 160*np.exp(-x/0.08)+110
    body=np.sin(2*np.pi*np.cumsum(body_f)/SR)*np.exp(-x/(0.45 if big else 0.12))*(1.1 if big else 0.55)
    s+=np.tanh(body*1.6)
    if big:
        for f,a,d in [(392,0.22,1.2),(587,0.14,0.9),(784,0.10,0.7),(1175,0.06,0.5)]: s+=np.sin(2*np.pi*f*x)*np.exp(-x/d)*a
        s+=np.sin(2*np.pi*55*x)*np.exp(-x/0.5)*0.45  # small real sub
    return s
place(hit,shutter(False),0.0); place(hit,shutter(True),17.40)
# loop-link: a rising tone into frame 0
lk=(t>21.2); ff=600+900*sm(21.2,22.0,t); lt=np.sin(2*np.pi*np.cumsum(ff)/SR)*0.05*sm(21.2,21.9,t)*lk; fill+=lt
# ---------------- mix: bass management on everything but the hit bus, side-chain duck under hits
for name in ['tick','bed','fill','whoosh','pad']:
    globals()[name]=hp(globals()[name],90)
duck=1-0.5*np.exp(-np.clip(t-17.40,0,None)/0.6)*(t>=17.40)
mix=tick*0.13+bed*0.8+fill+whoosh*duck+pad*duck+hit*0.9
import os
if os.environ.get("DBG"):
    for nm,b in [("tick",tick*0.13),("bed",bed),("fill",fill),("whoosh",whoosh),("pad",pad),("hit",hit*0.9)]:
        print(nm," ".join(f"{20*np.log10(np.sqrt(np.mean(b[int(a*SR):int((a+1)*SR)]**2))+1e-9):6.1f}" for a in range(0,22,2)))
# held breath: near silence 14.6 -> 15.25 (only a trace of the pad)
hb=1-0.97*sm(14.55,14.65,t)*(1-sm(15.2,15.3,t)); mix*=hb
mix=np.tanh(mix*1.25)/np.tanh(1.25)
# short fades at the ends keep the loop click-free
f=int(0.004*SR); mix[:f]*=np.linspace(0,1,f); mix[-f:]*=np.linspace(1,0,f)
mix/=np.abs(mix).max()*1.12
st=np.stack([mix,mix],1)
# subtle width: delay right channel of the tick/bed buses
d=int(0.0007*SR); st[d:,1]=0.85*st[d:,1]+0.15*st[:-d,0]
out=sys.argv[1] if len(sys.argv)>1 else 'photon_mix.wav'
with wave.open(out,'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(st,-1,1)*32767).astype(np.int16).tobytes())
print('wrote',out)
