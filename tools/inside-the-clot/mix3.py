# python3 mix3.py out.wav <vo prefix>  — v3 mix: crowd opening, voiceover, scene events through the video->scene warp. All FX synthesized.
import numpy as np, wave, sys
SR=48000; T=24.9; N=int(SR*T); t=np.arange(N)/SR
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

# ---------------- v3: crowd opening + voiceover; scene events placed through the video->scene warp
WK=[(3.2,0.4),(4.4,2.25),(9.75,8.6),(10.75,9.3),(14.4,13.55),(19.0,18.7),(21.6,21.0),(24.9,24.0)]
_d=[(WK[i+1][1]-WK[i][1])/(WK[i+1][0]-WK[i][0]) for i in range(len(WK)-1)]
_m=[_d[0]]+[0 if _d[i-1]*_d[i]<=0 else 2/(1/_d[i-1]+1/_d[i]) for i in range(1,len(_d))]+[_d[-1]]
def warp(x):
    x=np.atleast_1d(np.asarray(x,float)); out=np.empty_like(x)
    for j,tv in enumerate(x):
        if tv<=WK[0][0]: out[j]=WK[0][1]-(WK[0][0]-tv); continue
        if tv>=WK[-1][0]: out[j]=WK[-1][1]; continue
        i=0
        while tv>WK[i+1][0]: i+=1
        h=WK[i+1][0]-WK[i][0]; u=(tv-WK[i][0])/h
        out[j]=(2*u**3-3*u**2+1)*WK[i][1]+(u**3-2*u**2+u)*h*_m[i]+(-2*u**3+3*u**2)*WK[i+1][1]+(u**3-u**2)*h*_m[i+1]
    return out
grid=np.linspace(0,T,int(T*1000)+1); gw=warp(grid)
def V(ts): return float(np.interp(ts,gw,grid))           # scene -> video
TS=np.interp(t,grid,gw)                                    # scene time of every sample
BEAT=60/66
# heartbeat (video time): faint under the crowd, rising as we close on him, then the v2 behaviour
for k in range(40):
    tb=k*BEAT
    if tb>=24.8: break
    ts=float(warp(tb)[0])
    if tb<3.2: heartbeat(tb,-20+16*float(sm(0.6,2.8,tb)),muffle=tb<1.0); continue
    if 8.55<=ts<9.6: continue
    if 2.25<=ts<13.55: heartbeat(tb,-11,muffle=True)
    elif ts<2.25: heartbeat(tb,-6)
    elif ts<21.0:
        if k%5==3: continue
        heartbeat(tb+0.04*np.sin(k*2.1),-10-4*float(sm(13.5,18.6,ts)),weak=0.8)
    else: heartbeat(tb,-9)
# crowd: city murmur bed + soft footsteps, fading as we push into his chest
mur=fft_filter(noise(N),'bp',250,2,1800); am=1+0.5*fft_filter(noise(N),'lp',4)*30
crowd=mur*am*0.35*(1-sm(2.4,3.2,t))
B['bed']+=np.stack([crowd,np.roll(crowd,300)],1)
for i in range(70):
    ft=rng.uniform(0,3.0); m=int(0.05*SR); s_=fft_filter(noise(m)*np.exp(-np.arange(m)/(0.008*SR)),'bp',300,2,3000); add('tex',s_,ft,-30+rng.uniform(-4,3),pan=rng.uniform(-0.9,0.9))
# frame-0 hit, his stop (heartbeat swell), the dive into the chest
boom(0.0,150,46,1.0,-6); swell(0.02,0.35,-30)
swell(1.55,0.6,-22,200,3000); boom(1.6,120,48,0.9,-12)
swell(3.18,1.0,-12,300,6000); whoosh(2.55,0.75,-9); boom(3.2,160,48,1.0,-6)
# snap into the artery
swell(V(2.22),0.7,-14,400,6000); whoosh(V(2.22)-0.5,0.7,-10); boom(V(2.25),140,50,0.8,-10)
# flow bed (scene-time masks)
flow=fft_filter(noise(N),'lp',520,2); flow2=fft_filter(noise(N),'bp',900,2,2400)
puls=np.zeros(N)
for k in range(40): puls+=np.exp(-((t-k*BEAT-0.12)/0.16)**2)
puls=0.45+0.8*puls
inside=sm(2.15,2.4,TS)*(1-sm(13.4,13.6,TS))*(t>=3.2); stopf=1-sm(11.6,13.0,TS); hold=1-0.8*sm(8.5,8.7,TS)*(1-sm(9.25,9.4,TS))
bed=flow*puls*inside*(0.15+0.85*stopf)*hold*0.75; bruit=flow2*puls*inside*sm(5.0,8.4,TS)*stopf*hold*0.55
B['bed']+=np.stack([bed,bed*0.96+0.04*np.roll(bed,90)],1)+np.stack([np.roll(bruit,40),bruit],1)
# age ticks
prev=None
for f in range(int(3.2*30),int(10*30)):
    tv=f/30; ts=float(warp(tv)[0])
    if not (4.6<=ts<8.5): continue
    a=25+int(np.floor(30*float(sm(2.6,8.4,ts))+1e-6))
    if prev is not None and a!=prev:
        kk=a-25; m=int(0.03*SR); s_=np.sin(2*np.pi*(1300+18*kk)*np.arange(m)/SR)*np.exp(-np.arange(m)/(0.006*SR)); add('tex',s_,tv,-26+0.12*kk,pan=0.3*np.sin(kk))
    prev=a
m=int(0.9*SR); hz=np.sin(2*np.pi*2350*np.arange(m)/SR)*np.sin(np.pi*np.arange(m)/m)**2; add('tone',hz,V(8.55),-40)
# crack (biggest hit)
c=V(9.3); swell(c-0.06,0.6,-10,200,7000); crack(c,-4,0.6); boom(c,320,58,1.6,-1); boom(c,90,38,2.0,-9)
hiss=fft_filter(noise(int(1.4*SR)),'bp',2500,2,9000)*env_exp(int(1.4*SR),0.35); add('tex',np.stack([hiss,np.roll(hiss,60)],1),c+0.01,-17); bell(c+0.02,196,2.5,-20)
# clot
a0,a1=V(9.7),V(13.0)
for i in range(520):
    u=(i/520)**0.6; tc=a0+(a1-a0)*u+rng.uniform(-0.02,0.02); m=int(0.012*SR); fr=rng.uniform(2200,5200)*(0.8+0.3*u)
    add('tex',np.sin(2*np.pi*fr*np.arange(m)/SR)*np.exp(-np.arange(m)/(0.0018*SR)),tc,-32+5*u,pan=rng.uniform(-0.8,0.8))
L_=a1-a0; tt=np.arange(int(L_*SR))/SR; cr=np.sin(2*np.pi*(70+40*tt/L_)*tt+3*np.sin(2*np.pi*7*tt))*sm(0,L_*0.9,tt)*0.5; add('tone',fft_filter(cr,'lp',600),a0,-18)
boom(a1,200,60,0.9,-8); swell(a1-0.02,0.8,-22,150,2000)
whoosh(V(13.55)-0.4,0.8,-10,rise=False,pan0=0.6,pan1=-0.6)
prev=None
for f in range(int(13*30),int(20*30)):
    tv=f/30; ts=float(warp(tv)[0])
    if not (13.8<=ts<18.7): continue
    u=min(1,max(0,(ts-13.8)/4.6)); mn=int(np.floor(90*u**0.9+1e-6))//5
    if prev is not None and mn!=prev:
        m=int(0.05*SR); s_=np.sin(2*np.pi*880*np.arange(m)/SR)*np.exp(-np.arange(m)/(0.01*SR))+0.5*np.sin(2*np.pi*1760*np.arange(m)/SR)*np.exp(-np.arange(m)/(0.004*SR)); add('tex',s_,tv,-24)
    prev=mn
dr=sum(np.sin(2*np.pi*f_*t+0.3*np.sin(2*np.pi*0.21*t*i))*a for i,(f_,a) in enumerate([(110,1),(110.6,0.8),(164.8,0.55),(220.4,0.25)]))
dr=fft_filter(np.tanh(1.3*dr),'lp',700)*sm(13.6,16.5,TS)*(1-sm(20.6,21.6,TS))*0.22; B['tone']+=np.stack([dr,np.roll(dr,120)],1)
bell(V(18.8),82.4,3.0,-8); boom(V(18.8),140,55,1.2,-12)
bell(V(21.1),164.8,2.4,-14); boom(V(21.1),160,50,0.8,-14)
n=int(1.4*SR); tt=np.arange(n)/SR; fr_=220*2**(tt/1.4); add('tone',np.sin(2*np.pi*np.cumsum(fr_)/SR)*(tt/1.4)**2.5*0.5,T-1.45,-22); swell(T,1.0,-22,500,6000)
# ---------------- voiceover (stand-in TTS lines placed at the frozen starts)
import soundfile as sf
VO_DIR=sys.argv[2]; STARTS=[0.15,4.3,7.3,9.9,11.6,14.9,19.0,20.45,21.7]
vo=np.zeros(N)
for i,st in enumerate(STARTS):
    a,sr=sf.read(f"{VO_DIR}_{i}.wav"); a=np.asarray(a,float)
    if a.ndim>1: a=a.mean(1)
    if sr!=SR: a=np.interp(np.arange(int(len(a)*SR/sr))/SR,np.arange(len(a))/sr,a)
    j=int(st*SR); n=min(len(a),N-j); vo[j:j+n]+=a[:n]
vo=fft_filter(vo,'hp',90,2); vo=vo/np.max(np.abs(vo))*0.9
# light presence + warmth on the voice: tiny room, gentle saturation
vo=np.tanh(vo*1.3)/np.tanh(1.3)
env=np.convolve(np.abs(vo),np.ones(int(0.12*SR))/int(0.12*SR),'same'); duck=1-0.55*np.clip(env/0.12,0,1)
def hp(x,fc): return fft_filter(x,'hp',fc,2)
fx=B['hit']+B['beat']*0.9+hp(B['bed'],90)*0.9+hp(B['tex'],120)+hp(B['tone'],70)*0.9
fx=np.tanh(fx*1.1)/np.tanh(1.1); fx=fx/np.max(np.abs(fx))*0.85
mix=fx*duck[:,None]*0.55+np.stack([vo,vo],1)*0.75
ir_n=int(1.0*SR); ir=noise(ir_n)*np.exp(-np.arange(ir_n)/(0.22*SR)); ir=fft_filter(ir,'lp',3500)*0.010
rev=np.stack([np.fft.irfft(np.fft.rfft(mix[:,c],N+ir_n)*np.fft.rfft(ir,N+ir_n),N+ir_n)[:N] for c in range(2)],1)
mix=mix+rev*0.4; mix=np.tanh(mix*1.05)/np.tanh(1.05); mix/=np.max(np.abs(mix))/0.89
with wave.open(sys.argv[1],'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(mix,-1,1)*32767).astype(np.int16).tobytes())
print("mix3 done")
