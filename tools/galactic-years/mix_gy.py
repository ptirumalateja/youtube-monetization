# Sound for "Earth Is 20 Years Old": "orbital clockwork" family (new for this reel).
# A lap tick per orbit (pitch climbs), a glass bell per milestone, a slow drone that opens as the laps speed up,
# held breath, one big hit on the twist, a soft bell for humans, a dive whoosh and a loop-link tone.
# Everything is synthesized here except the wind bed (22331 sleepCircle, CC0).  python3 mix_gy.py -> gy_mix.wav
import subprocess, numpy as np, wave, json
SR=48000; HERE=__import__('os').path.dirname(__import__('os').path.abspath(__file__)); TL=json.load(open(HERE+'/timeline.json')); T=TL['T']; N=int(SR*T); B=TL['beats']; LK=TL['lapKeys']
LIB=HERE+"/../sfxlib/"
t=np.arange(N)/SR; rng=np.random.default_rng(20)
def db(g): return 10**(g/20)
def load(f):
    raw=subprocess.run(["ffmpeg","-v","error","-i",LIB+f,"-f","f32le","-ac","2","-ar",str(SR),"-"],capture_output=True).stdout
    return np.frombuffer(raw,np.float32).reshape(-1,2).copy()
def filt(x,kind,fc,order=2):
    n=len(x); X=np.fft.rfft(x,axis=0); fr=np.fft.rfftfreq(n,1/SR); r=fr/fc+1e-9
    mag=1/np.sqrt(1+r**(2*order)) if kind=='lp' else (1-1/np.sqrt(1+r**(2*order)))
    if x.ndim==2: mag=mag[:,None]
    return np.fft.irfft(X*mag,n=n,axis=0)
buses={k:np.zeros((N,2)) for k in ['hit','tick','bell','bed','fx']}
def add(bus,x,at,gain=0.0,pan=0.0):
    a=int(at*SR); x=np.asarray(x)
    if x.ndim==1: x=np.stack([x*(1-max(0,pan)),x*(1+min(0,pan))],1)
    if a<0: x=x[-a:]; a=0
    n=min(len(x),N-a)
    if n>0: buses[bus][a:a+n]+=x[:n]*db(gain)
# lap(t) exactly as the scene computes it
def lap_at(tt):
    if tt<=LK[0][0]: return LK[0][1]
    if tt>=LK[-1][0]: return LK[-1][1]
    for i in range(len(LK)-1):
        t0,a=LK[i]; t1,b=LK[i+1]
        if tt<=t1:
            u=(tt-t0)/(t1-t0)
            if i==0: e=u
            elif i==len(LK)-2: e=0.5*u+0.5*u*u
            else: s=u*u*(3-2*u); e=0.22*u+0.78*s
            return a+(b-a)*e
# ---------------------------------------------------------------- instruments
def env_exp(n,dec): return np.exp(-np.arange(n)/SR/dec)
def tick(f):
    n=int(0.32*SR); tt=np.arange(n)/SR
    click=rng.standard_normal(n)*np.exp(-tt/0.004); click=filt(click,'hp',2500)
    body=np.sin(2*np.pi*f*tt+2.0*np.sin(2*np.pi*f*1.5*tt)*np.exp(-tt/0.03))*np.exp(-tt/0.09)
    wood=np.sin(2*np.pi*f*2.76*tt)*np.exp(-tt/0.03)*0.4
    return 0.5*click+0.8*body+wood
def bell(f,dur,ratio=1.4,idx=2.2):
    n=int(dur*SR); tt=np.arange(n)/SR; e=np.exp(-tt/(dur*0.28))
    s=np.sin(2*np.pi*f*tt+idx*e*np.sin(2*np.pi*f*ratio*tt))+0.35*np.sin(2*np.pi*f*2.0*tt)*np.exp(-tt/(dur*0.12))
    return s*e*np.minimum(1,tt/0.003)
def boom(dur,f0,f1,k=9.0):
    n=int(dur*SR); tt=np.arange(n)/SR; f=f1+(f0-f1)*np.exp(-tt*k); ph=2*np.pi*np.cumsum(f)/SR
    return np.tanh(1.6*np.sin(ph))*np.exp(-tt*(3.0/dur))*np.minimum(1,tt/0.002)
def noise_burst(dur,hp,lp=None,dec=0.25):
    n=int(dur*SR); x=rng.standard_normal(n); x=filt(x,'hp',hp)
    if lp: x=filt(x,'lp',lp)
    return x*np.exp(-np.arange(n)/(n*dec))
def gong(f,dur):
    n=int(dur*SR); tt=np.arange(n)/SR; s=np.zeros(n)
    for r,a,dk in [(1,1,1),(1.47,0.6,0.7),(2.09,0.45,0.5),(2.56,0.3,0.4),(3.37,0.2,0.3)]: s+=a*np.sin(2*np.pi*f*r*tt+rng.uniform(0,6))*np.exp(-tt/(dur*0.3*dk))
    return s*np.minimum(1,tt/0.004)
def swell(dur,f0,f1,hp=400):
    n=int(dur*SR); x=filt(rng.standard_normal(n),'hp',hp); x=filt(x,'lp',3000); e=(np.arange(n)/n)**2.2
    tt=np.arange(n)/SR; tone=np.sin(2*np.pi*np.cumsum(np.linspace(f0,f1,n))/SR)*0.3
    return (x*0.6+tone)*e
def whoosh(dur,peak=0.6,hp=300,lp=2500):
    n=int(dur*SR); x=filt(rng.standard_normal(n),'hp',hp); x=filt(x,'lp',lp); u=np.arange(n)/n
    e=np.where(u<peak,(u/peak)**2,np.exp(-(u-peak)/(1-peak)*4)); return x*e
def pan_sweep(m,p0,p1):
    pan=np.linspace(p0,p1,len(m)); ang=(pan+1)*np.pi/4; return np.stack([m*np.cos(ang),m*np.sin(ang)],1)
# ---------------------------------------------------------------- cue sheet
# frame 0: hit + rush (we are already riding with the Sun)
add('hit',boom(1.6,260,62),0.0,-4); add('hit',noise_burst(0.25,2200,dec=0.2),0.0,-8); add('hit',gong(98,2.2),0.0,-16)
add('fx',pan_sweep(whoosh(2.2,0.35,500,4000),0.7,-0.7),0.0,-10)
# hook type ticks (quiet keys)
for i in range(22): add('tick',noise_burst(0.02,3500,dec=0.3),0.05+i*0.033,-28,pan=rng.uniform(-0.3,0.3))
# snap: reverse swell into a soft hit as the galaxy opens
add('fx',swell(0.9,200,900),B['snap']-0.9,-12); add('hit',boom(1.2,200,70),B['snap'],-11); add('bell',bell(587,2.4),B['snap']+0.05,-18)
# lap ticks: one per completed orbit, pitch climbs a pentatonic scale
scale=[0,2,4,7,9]; lap_times=[]; tt_=np.arange(0,B['now']+0.01,1/1000); laps=np.array([lap_at(x) for x in tt_])
for k in range(1,20):
    idx=np.argmax(laps>=k); lap_times.append(tt_[idx])
for k,tk in enumerate(lap_times):
    semi=scale[k%5]+12*(k//5); f=196*2**(semi/12)
    add('tick',tick(f),tk,-13-0.15*k,pan=0.35*np.sin(k*1.3))
# milestone bells (glass), one pitch per stop
mb=[392,440,523,587,659,784,880]
for m,f in zip(TL['milestones'][:-1],mb): add('bell',bell(f,2.6,1.4+0.2*np.sin(f)),m['t']-0.05,-15)
add('bell',bell(988,3.0,2.0,1.4),TL['milestones'][-1]['t']-0.05,-17)
# drone: A minor-ish pad that opens as the laps accelerate, dips at the held breath
def pad():
    x=np.zeros(N)
    for f,a in [(110,1),(110.6,0.8),(164.8,0.6),(220.3,0.4),(261.6,0.25)]:
        ph=rng.uniform(0,6); x+=a*(2*((f*t+ph)%1)-1)
    return x
pd=pad(); speed=np.gradient(np.interp(t,tt_,laps,right=laps[-1]))*SR
lo=filt(pd,'lp',350); hi=filt(pd,'lp',1800); mix=np.clip(speed/3.0,0,1)
bed=(lo*(1-mix)+hi*mix)*0.12
ga=np.interp(t,[0,2.2,3.4,B['now']-0.1,B['now']+0.05,B['twistHit'],B['twistHit']+0.05,B['dive'],T-0.6,T],[0.15,0.35,0.8,1,0.02,0.02,0.85,0.6,0.25,0.15])
add('bed',np.stack([bed*ga,np.roll(bed,240)*ga],1),0,0)
# wind bed (CC0)
wd=load("22331__sleepcircle__wind.ogg"); wd=np.tile(wd,(int(np.ceil(N/len(wd)))+1,1))[:N]
wg=np.interp(t,[0,2.0,3.4,B['now']-0.1,B['now']+0.05,B['twistHit'],B['twistHit']+0.3,B['dive'],T],[1,0.9,0.35,0.3,0.0,0.0,0.3,0.5,1.0])
add('bed',filt(wd,'hp',120)*wg[:,None],0,-8)
# riser into "today", then held breath (near silence) and the twist hit (the biggest one)
r0=12.8; rl=B['now']-r0; n=int(rl*SR); u=np.arange(n)/n
shep=sum(np.sin(2*np.pi*np.cumsum(220*2**(o+1.2*u))/SR)*np.exp(-((o+1.2*u-1.0)**2)/0.5) for o in range(-1,3))
add('fx',(shep*u**1.5*0.25),r0,-6)
add('fx',swell(0.42,120,600,hp=200)[::1],B['twistHit']-0.46,-10)
h=B['twistHit']
add('hit',boom(3.2,300,58,k=7),h,-1); add('hit',noise_burst(0.35,1800,dec=0.18),h,-5); add('hit',gong(73.4,4.5),h,-9); add('hit',gong(146.8,3.0),h+0.01,-15)
sub=np.sin(2*np.pi*44*np.arange(int(2.6*SR))/SR)*np.exp(-np.arange(int(2.6*SR))/SR/0.9); add('hit',sub,h,-7)
add('bell',bell(523,3.2,1.5,2.6),h+0.9,-17)   # arc draws on
# humans: tiny high bell + soft tick
add('bell',bell(1318,2.4,2.0,1.0),B['humans']+0.3,-17); add('tick',tick(784),B['humans']+1.25,-17)
# dive home: whoosh sweep, rising loop-link tone into frame 0
add('fx',pan_sweep(whoosh(2.6,0.75,300,5000),-0.6,0.6),B['dive'],-9)
n=int(1.4*SR); u=np.arange(n)/n; tone=np.sin(2*np.pi*np.cumsum(180+220*u**2)/SR)*u**2; add('fx',tone,T-1.4,-14)
add('bell',bell(659,2.0,1.4,1.8),B['dive']+0.35,-19)
# ---------------------------------------------------------------- bus processing and master
def reverb(x,dec=1.6,wet=0.25):
    n=int(dec*SR); ir=rng.standard_normal((n,2))*np.exp(-np.arange(n)/SR/(dec/6.9))[:,None]; ir=filt(ir,'lp',4000); ir/=np.sqrt((ir**2).sum(0))
    L=len(x)+n; X=np.fft.rfft(x,L,axis=0); I=np.fft.rfft(ir,L,axis=0); y=np.fft.irfft(X*I,L,axis=0)[:len(x)]
    return x+wet*y*4
for k in ['tick','bell','bed','fx']: buses[k]=filt(buses[k],'hp',90)
buses['hit']=reverb(buses['hit'],2.4,0.22); buses['bell']=reverb(buses['bell'],2.0,0.35); buses['tick']=reverb(buses['tick'],1.2,0.2)
# side-chain duck the bed under the two main hits
duck=np.ones(N)
for ht,dd in [(0.0,0.5),(h,0.35)]:
    m=(t>=ht)&(t<ht+1.5); duck[m]=np.minimum(duck[m],1-(1-dd)*np.exp(-(t[m]-ht)/0.5))
# bus trims (hit bus carries the reverb tail, so it sits lowest)
for k,g in [('hit',-11),('tick',4),('bell',-6),('bed',3),('fx',4)]: buses[k]*=db(g)
for k,v in buses.items(): print(k,'rms dB',round(20*np.log10(np.sqrt((v**2).mean())+1e-9),1),'peak',round(np.abs(v).max(),2))
mixd=buses['hit']+buses['tick']+buses['bell']+(buses['bed']+buses['fx'])*duck[:,None]
mixd=np.tanh(mixd*1.1)/np.tanh(1.1); mixd/=np.abs(mixd).max()/0.89
# loop seam: short fades so the last sample meets the first
fn=int(0.01*SR); mixd[-fn:]*=np.linspace(1,0,fn)[:,None]
with wave.open('gy_mix.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(mixd,-1,1)*32767).astype(np.int16).tobytes())
print('lap ticks at',[round(x,2) for x in lap_times])
