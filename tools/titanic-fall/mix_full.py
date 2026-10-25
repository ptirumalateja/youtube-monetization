# TEMPORARY sound for the full "It Fell" reel (24 s). Synth only: no samples, no licences. Replace with the real "iron and pressure" mix.
# usage: python3 mix_full.py <out.wav> <frames_dir_with_meta_json>
import numpy as np, wave, sys, json, glob, os
SR=44100; T=24.0; N=int(SR*T); t=np.arange(N)/SR; rng=np.random.default_rng(7)
def lp(x,fc):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); return np.fft.irfft(X*np.exp(-(f/fc)**2),len(x))
def hp(x,fc): return x-lp(x,fc)
def bp(x,f0,f1): return lp(hp(x,f0),f1)
def env(t0,t1,att=0.01,rel=0.2):
    e=np.zeros(N); i0,i1=int(t0*SR),min(N,int(t1*SR)); k=np.arange(i1-i0)/SR; e[i0:i1]=np.minimum(1,k/att)*np.exp(-k/rel); return e
def sweep(f0,f1,t0,dur,rel,amp=1.0):
    i0=int(t0*SR); L=min(int(dur*SR),N-i0); k=np.arange(L)/SR; f=f0*(f1/f0)**(k/dur); ph=2*np.pi*np.cumsum(f)/SR; y=np.zeros(N); y[i0:i0+L]=np.sin(ph)*np.exp(-k/rel)*amp; return y
def tone(f,t0,dur,rel,att=0.01,amp=1.0): return sweep(f,f,t0,dur,rel,amp)*np.minimum(1,np.clip((t-t0)/att,0,1))
noise=rng.standard_normal(N); out=np.zeros(N)
# ---- 0-5.6 s (same cues as the opening review cut)
out+=0.9*sweep(88,36,0.0,1.4,0.55)+0.4*sweep(176,70,0.0,1.0,0.3)+0.5*lp(noise,1400)*env(0,0.4,0.004,0.12)
out+=lp(noise,700)*0.05*(1-np.clip((t-1.95)/0.15,0,1))+0.07*np.sin(2*np.pi*46*t)*np.clip(t/1.9,0,1)*(t<2.0)
for tr in (1.15,1.5): out+=0.12*lp(noise,2500)*env(tr,tr+0.5,0.02,0.18)
out+=0.8*hp(noise,2200)*env(1.93,2.0,0.001,0.012)+1.0*sweep(95,45,1.95,0.8,0.22)+0.55*bp(noise,500,3500)*env(2.0,2.8,0.005,0.22)
for k in range(260): out+=0.05*sweep(rng.uniform(500,2400),rng.uniform(800,3800),2.0+abs(rng.normal(0,0.55)),0.05,0.02)
sw=np.zeros(N); i0,i1=int(2.42*SR),int(2.72*SR); sw[i0:i1]=rng.standard_normal(i1-i0)*np.sin(np.linspace(0,np.pi,i1-i0))**2; out+=0.25*lp(sw,1800)
uw=np.clip((t-2.05)/0.2,0,1); out=out*(1-uw)+lp(out,420)*uw
# ---- underwater bed 2.1-21.4: rumble, drone swell, falling tone
bed=uw*(1-np.clip((t-21.2)/0.5,0,1)); out+=lp(noise,260)*0.28*bed
swell=np.clip((t-2.4)/3.0,0,1); out+=bed*swell*(0.16*np.sin(2*np.pi*55*t)+0.11*np.sin(2*np.pi*82.5*t+1.1))
f=420*(200/420)**(np.clip((t-2.3)/3.2,0,1)); out+=np.sin(2*np.pi*np.cumsum(f)/SR)*0.035*bed*(t<8.0)
for tc in (2.9,3.8,4.7,6.3,7.4,8.6,9.5,10.4): 
    L=int(0.7*SR); i0=int(tc*SR); k=np.arange(L)/SR; out[i0:i0+L]+=0.35*bp(rng.standard_normal(L),130,260)*np.sin(np.pi*k/0.7)**2*(1+0.5*np.sin(2*np.pi*7*k))
for k in range(150): out+=0.025*sweep(rng.uniform(700,1700),rng.uniform(1000,2600),2.8+rng.uniform(0,2.7),0.05,0.022)*(1-0.5*rng.uniform(0,1))
# ---- 5.6-11.2 twilight to midnight: bioluminescent pings, lamp click, descending shepard, accelerating pulses
for k in range(14): out+=0.05*tone(rng.uniform(900,2600),5.8+rng.uniform(0,2.2),0.6,0.18,0.004)
out+=0.5*hp(noise,1800)*env(7.6,7.64,0.001,0.01)+0.5*sweep(140,90,7.62,0.3,0.1)
shep=np.zeros(N); 
for i in range(6):
    ph=((t-7.8)/3.4*0.5+i/6.0)%1.0; fr=1200*(0.5**(ph*3)); amp=np.sin(np.pi*ph)**2; shep+=np.sin(2*np.pi*np.cumsum(fr)/SR)*amp
out+=0.035*shep*((t>7.8)&(t<11.15)).astype(float)
tp=7.9; 
while tp<11.1:
    out+=0.45*sweep(78,48,tp,0.22,0.07); tp+=1.0/np.interp(tp,[7.9,11.1],[1.6,7.5])
# ---- held breath 11.15-11.88 (near silence), then the impact
gate=1-np.clip((t-11.12)/0.08,0,1)*(1-np.clip((t-11.86)/0.04,0,1)); out*=np.where((t>=11.12)&(t<11.88),0.012+0.0*gate,1.0); out+=0.03*tone(1800,11.5,0.05,0.02)
out+=1.15*sweep(72,26,11.9,2.2,0.75)+0.7*lp(noise,500)*env(11.9,12.6,0.003,0.30)+0.55*lp(noise,110)*env(11.9,14.4,0.02,1.1)
for fq,rl,am in ((143,1.4,0.28),(211,1.1,0.22),(337,0.9,0.16),(521,0.6,0.1),(777,0.4,0.06)): out+=am*sweep(fq,fq*0.985,11.9,1.8,rl)
out+=0.35*bp(noise,150,420)*env(12.05,12.7,0.05,0.25)*(1+0.6*np.sin(2*np.pi*13*t))+0.7*sweep(110,55,12.7,0.5,0.14)+0.4*lp(noise,900)*env(12.7,13.0,0.003,0.1)
# ---- 14.2-18.6 pull-up: one tone per outline, accelerating, rising air
meta={}
for fn in glob.glob(os.path.join(sys.argv[2],'meta_*.json')):
    for fr,dp in json.load(open(fn)): meta[int(fr)]=dp
last=-1
for fr in sorted(meta):
    tt=fr/30.0
    if 14.2<=tt<19.0:
        n=min(14,max(0,int((3800-meta[fr])/269)))
        if n>last and n>=1: out+=0.16*tone(220*2**((n-1)/7.0),tt,0.9,0.35,0.01)*(1+0.0)+0.05*tone(440*2**((n-1)/7.0),tt,0.6,0.2,0.01); last=n
ri=(t>14.2)&(t<18.7); sweepn=np.interp(t,[14.2,18.6],[300,3200]); out+=0.22*lp(hp(noise,300),2200)*np.where(ri,np.clip((t-14.2)/4.4,0,1)**1.5,0)
out*=np.where((t>18.55)&(t<19.0),1-0.0,1.0)
# ---- 18.7 sonar ping with echoes, hush, then the surface
for dl,am in ((0,0.22),(0.42,0.10),(0.86,0.05)): out+=am*tone(1100,18.75+dl,1.6,0.45,0.004)
surf=np.clip((t-21.4)/0.4,0,1); out+=surf*0.18*bp(noise,350,1300)*np.clip((t-21.4)/1.6,0,1)
for k in range(40): out+=0.04*sweep(rng.uniform(300,700),rng.uniform(200,500),21.8+rng.uniform(0,2.0),0.08,0.04)*surf
rise=np.clip((t-22.6)/1.4,0,1); out+=0.28*np.sin(2*np.pi*np.cumsum(40+50*rise)/SR)*rise**1.4+0.25*lp(noise,900)*rise**2
out*=np.clip((T-t)/0.05,0,1)
out=np.tanh(out*0.9); out*=0.7/np.max(np.abs(out))
st=np.stack([out,np.roll(out,int(0.0006*SR))],1); pcm=(st*32767).astype(np.int16)
with wave.open(sys.argv[1],'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('wrote',sys.argv[1])
