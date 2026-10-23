# Sound for "Earth Is 20 Years Old" V3: the V2 "orbital clockwork" family retimed to the cutaways, plus a voice for each scene
# (lava rumble and impacts, underwater plunge and bubbles, footsteps / asteroid roar / impact, night air).
# Everything is synthesized except the wind bed (22331 sleepCircle, CC0).  python3 mix3.py -> gy3_mix.wav
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
# lap(t): the PCHIP curve used by index.html and overlay3.py
n_=len(LK); h_=[LK[i+1][0]-LK[i][0] for i in range(n_-1)]; d_=[(LK[i+1][1]-LK[i][1])/h_[i] for i in range(n_-1)]; m_=[0.0]*n_; m_[0]=d_[0]; m_[-1]=d_[-1]
for i in range(1,n_-1):
    if d_[i-1]*d_[i]<=0: m_[i]=0.0
    else: w1=2*h_[i]+h_[i-1]; w2=h_[i]+2*h_[i-1]; m_[i]=(w1+w2)/(w1/d_[i-1]+w2/d_[i])
def lap_at(tt):
    if tt<=LK[0][0]: return LK[0][1]
    if tt>=LK[-1][0]: return LK[-1][1]
    for i in range(n_-1):
        t0,a=LK[i]; t1,b=LK[i+1]
        if tt<=t1:
            hh=t1-t0; u=(tt-t0)/hh; u2=u*u; u3=u2*u
            return (2*u3-3*u2+1)*a+(u3-2*u2+u)*hh*m_[i]+(-2*u3+3*u2)*b+(u3-u2)*hh*m_[i+1]
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
def rumble(dur,lp=220,dec=None):
    n=int(dur*SR); x=filt(rng.standard_normal(n),'lp',lp); x=filt(x,'hp',45); x/=np.abs(x).max()+1e-9
    e=np.minimum(1,np.arange(n)/(0.08*SR)); return x*e*(np.exp(-np.arange(n)/SR/dec) if dec else 1)
def crackle(dur,rate=60):
    n=int(dur*SR); x=np.zeros(n); k=rng.poisson(rate*dur)
    for _ in range(k):
        i=rng.integers(0,n-400); L=int(rng.uniform(40,380)); x[i:i+L]+=rng.standard_normal(L)*np.exp(-np.arange(L)/(L*0.3))*rng.uniform(0.2,1)
    return filt(filt(x,'hp',900),'lp',7000)
def bubbles(dur,rate=40):
    n=int(dur*SR); x=np.zeros(n)
    for _ in range(int(rate*dur)):
        i=rng.integers(0,n-6000); f0=rng.uniform(500,1600); L=int(rng.uniform(1500,5000)); tt=np.arange(L)/SR
        x[i:i+L]+=np.sin(2*np.pi*np.cumsum(f0*(1+3*tt/ (L/SR)))/SR)*np.exp(-tt/0.02)*rng.uniform(0.2,1)
    return x
# hook (0-1.9): the V2 hook sound, unchanged
add('hit',boom(1.6,260,62),0.0,-4); add('hit',noise_burst(0.25,2200,dec=0.2),0.0,-8); add('hit',gong(98,2.2),0.0,-16)
add('fx',pan_sweep(whoosh(2.2,0.35,500,4000),0.7,-0.7),0.0,-10)
for i in range(22): add('tick',noise_burst(0.02,3500,dec=0.3),0.05+i*0.033,-28,pan=rng.uniform(-0.3,0.3))
add('fx',swell(0.9,200,900),B['snap']-0.9,-12); add('hit',boom(1.2,200,70),B['snap'],-11); add('bell',bell(587,2.4),B['snap']+0.05,-18)
# A. molten Earth 3.3-4.9: rumble + crackle, two small impacts, one big one that bursts into the galaxy
add('fx',pan_sweep(whoosh(0.5,0.85,300,3000),-0.4,0.4),2.85,-14)
add('bed',rumble(1.7,260)*1.0,3.3,-9); add('fx',crackle(1.6,90),3.3,-16)
for ti,g in [(0.42,-12),(0.80,-12)]: add('hit',boom(0.7,180,60,k=12),3.3+ti,g); add('hit',noise_burst(0.12,1500,dec=0.2),3.3+ti,g-6)
add('fx',swell(0.35,150,500,hp=200),3.3+1.36-0.35,-13); add('hit',boom(1.8,240,55,k=8),3.3+1.36,-5); add('hit',noise_burst(0.4,900,dec=0.25),3.3+1.36,-8); add('hit',gong(82,2.0),3.3+1.36,-17)
# lap ticks on every completed orbit (pitch climbs), each with a short shimmer for the ripple
scale=[0,2,4,7,9]; lap_times=[]; tt_=np.arange(0,T,1/1000); laps=np.array([lap_at(x) for x in tt_])
for k in range(1,20): lap_times.append(tt_[np.argmax(laps>=k)])
for k,tk in enumerate(lap_times):
    semi=scale[k%5]+12*(k//5); f=196*2**(semi/12)
    add('tick',tick(f),tk,-12-0.12*k,pan=0.35*np.sin(k*1.3)); add('bell',bell(f*4,0.6,2.0,0.8),tk+0.01,-27)
# B. life 7.4-9.2: dive whoosh, underwater bed, bubbles, a glassy bell as the cells appear
add('fx',whoosh(0.7,0.4,200,1800),7.25,-10); add('fx',bubbles(1.2,55),7.45,-20); add('bed',rumble(1.8,500)*0.6,7.4,-15); add('bell',bell(880,2.0,1.5,1.6),8.3,-18); add('bell',bell(1319,1.6,2.0,1.0),8.75,-22)
# back to the galaxy 9.2: whoosh; milestone bells
add('fx',pan_sweep(whoosh(0.6,0.7,400,4000),0.5,-0.5),8.85,-13)
for tm,f in [(5.0,440),(9.75,587),(11.05,659),(14.5,523)]: add('bell',bell(f,2.2,1.4+0.2*np.sin(f)),tm,-16)
# C. dinosaurs 11.8-14.4: wind, heavy footsteps, asteroid roar, impact (second-largest hit)
for i in range(7): add('hit',boom(0.5,95,48,k=14),11.95+i*0.37,-17-2*(i%2))
add('fx',swell(0.6,90,320,hp=150)*1.0,13.25,-9); add('fx',pan_sweep(whoosh(0.65,0.9,200,6000),-0.7,0.3),13.2,-8)
add('hit',boom(2.4,220,50,k=6),13.85,-3); add('hit',noise_burst(0.5,700,dec=0.3),13.85,-7); add('bed',rumble(1.6,180,dec=0.9),13.9,-6)
# 14.4 out of the impact into the galaxy
add('fx',whoosh(0.5,0.3,300,3000),14.35,-14)
# D. human 16.0-17.6: quiet; one high bell; stars streak into the final shot
add('bell',bell(1047,2.6,2.0,1.2),16.1,-18); add('fx',swell(0.5,300,1200),17.1,-13)
# final 17.6: shimmer, type ticks, held breath, the biggest hit on "...BARELY MOVES THE CLOCK."
add('bell',bell(659,3.0,1.4,1.8),17.65,-17)
for i in range(23): add('tick',noise_burst(0.02,3500,dec=0.3),B['cap1']+i/26,-29,pan=rng.uniform(-0.3,0.3))
h=B['cap2']; add('fx',swell(0.45,120,600,hp=200),h-0.47,-10)
add('hit',boom(3.2,300,58,k=7),h,-1); add('hit',noise_burst(0.35,1800,dec=0.18),h,-5); add('hit',gong(73.4,4.5),h,-9); add('hit',gong(146.8,3.0),h+0.01,-15)
sub=np.sin(2*np.pi*44*np.arange(int(2.6*SR))/SR)*np.exp(-np.arange(int(2.6*SR))/SR/0.9); add('hit',sub,h,-7)
add('bell',bell(1318,2.4,2.0,1.0),h+0.8,-18)
# dive home 22.6-26: whoosh, end bell, rising loop-link tone into frame 0
add('fx',pan_sweep(whoosh(2.8,0.75,300,5000),-0.6,0.6),B['dive'],-9)
n=int(1.4*SR); u=np.arange(n)/n; tone=np.sin(2*np.pi*np.cumsum(180+220*u**2)/SR)*u**2; add('fx',tone,T-1.4,-14)
add('bell',bell(659,2.0,1.4,1.8),B['dive']+0.45,-19)
# drone: opens with lap speed; dips under the cutaway beds and to near silence for the held breath
def pad():
    x=np.zeros(N)
    for f,a in [(110,1),(110.6,0.8),(164.8,0.6),(220.3,0.4),(261.6,0.25)]:
        ph=rng.uniform(0,6); x+=a*(2*((f*t+ph)%1)-1)
    return x
pd=pad(); speed=np.gradient(np.interp(t,tt_,laps,right=laps[-1]))*SR
lo=filt(pd,'lp',350); hi=filt(pd,'lp',1800); mix=np.clip(speed/3.0,0,1); bed=(lo*(1-mix)+hi*mix)*0.12
ga=np.interp(t,[0,2.2,3.3,3.35,4.85,4.95,7.35,7.45,9.15,9.25,11.75,11.85,14.35,14.45,15.95,16.05,17.55,17.7,19.4,19.5,h,h+0.05,B['dive'],T-0.6,T],
               [0.15,0.35,0.8,0.25,0.25,0.9,0.9,0.3,0.3,1.0,1.0,0.25,0.25,0.8,0.8,0.35,0.35,0.7,0.7,0.02,0.02,0.85,0.6,0.25,0.15])
add('bed',np.stack([bed*ga,np.roll(bed,240)*ga],1),0,0)
wd=load("22331__sleepcircle__wind.ogg"); wd=np.tile(wd,(int(np.ceil(N/len(wd)))+1,1))[:N]
wg=np.interp(t,[0,2.0,3.3,11.7,11.9,14.3,14.5,15.9,16.1,17.5,17.7,19.4,19.5,h,h+0.3,B['dive'],T],[1,0.9,0.3,0.3,1.0,1.0,0.3,0.3,0.7,0.7,0.25,0.25,0.0,0.0,0.3,0.5,1.0])
add('bed',filt(wd,'hp',120)*wg[:,None],0,-8)
# ---------------------------------------------------------------- bus processing and master
def reverb(x,dec=1.6,wet=0.25):
    n=int(dec*SR); ir=rng.standard_normal((n,2))*np.exp(-np.arange(n)/SR/(dec/6.9))[:,None]; ir=filt(ir,'lp',4000); ir/=np.sqrt((ir**2).sum(0))
    L=len(x)+n; X=np.fft.rfft(x,L,axis=0); I=np.fft.rfft(ir,L,axis=0); y=np.fft.irfft(X*I,L,axis=0)[:len(x)]
    return x+wet*y*4
for k in ['tick','bell','bed','fx']: buses[k]=filt(buses[k],'hp',90)
buses['hit']=reverb(buses['hit'],2.4,0.22); buses['bell']=reverb(buses['bell'],2.0,0.35); buses['tick']=reverb(buses['tick'],1.2,0.2)
for k,g in [('hit',-11),('tick',4),('bell',-6),('bed',3),('fx',4)]: buses[k]*=db(g)
duck=np.ones(N)
for ht,dd in [(0.0,0.5),(13.85,0.45),(h,0.35)]:
    m=(t>=ht)&(t<ht+1.5); duck[m]=np.minimum(duck[m],1-(1-dd)*np.exp(-(t[m]-ht)/0.5))
mixd=buses['hit']+buses['tick']+buses['bell']+(buses['bed']+buses['fx'])*duck[:,None]
mixd=np.tanh(mixd*1.1)/np.tanh(1.1); mixd/=np.abs(mixd).max()/0.89
fn=int(0.01*SR); mixd[-fn:]*=np.linspace(1,0,fn)[:,None]
with wave.open('gy3_mix.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(mixd,-1,1)*32767).astype(np.int16).tobytes())
print('lap ticks at',[round(float(x),2) for x in lap_times])
