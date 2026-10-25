# TEMPORARY sound for the "It Fell" opening (0-5.6 s): synth only, no samples, no licences. Replace with the real "iron and pressure" mix later.
import numpy as np, wave, sys
SR=44100; T=5.6; N=int(SR*T); t=np.arange(N)/SR; rng=np.random.default_rng(7)
def lp(x,fc):
    a=np.exp(-2*np.pi*fc/SR); y=np.zeros_like(x); s=0.0
    for i in range(len(x)): s=(1-a)*x[i]+a*s; y[i]=s
    return y
def hp(x,fc): return x-lp(x,fc)
def env(t0,t1,att=0.01,rel=0.2,N=N):
    e=np.zeros(N); i0,i1=int(t0*SR),int(t1*SR); L=i1-i0; k=np.arange(L)/SR; e[i0:i1]=np.minimum(1,k/att)*np.exp(-k/rel); return e
def sine_sweep(f0,f1,t0,dur,rel):
    i0=int(t0*SR); L=int(dur*SR); k=np.arange(L)/SR; f=f0*(f1/f0)**(k/dur); ph=2*np.pi*np.cumsum(f)/SR; y=np.zeros(N); y[i0:i0+L]=np.sin(ph)*np.exp(-k/rel); return y[:N]
noise=rng.standard_normal(N)
out=np.zeros(N)
# frame-0 hit: hull groan + water hit
out+=0.9*sine_sweep(88,36,0.0,1.4,0.55)+0.4*sine_sweep(176,70,0.0,1.0,0.3)+0.5*lp(noise,1400)*env(0,0.4,0.004,0.12)
# above-water bed: sea hush + rising pressure tone
hush=lp(noise,700)*0.05*(1-np.clip((t-1.95)/0.15,0,1)); out+=hush+0.07*np.sin(2*np.pi*46*t)*np.clip(t/1.9,0,1)*(t<2.0)
for tr in (1.15,1.5): out+=0.12*lp(noise,2500)*env(tr,tr+0.5,0.02,0.18)       # ripples
# snap: crack + thump + splash + bubble burst
out+=0.8*hp(noise,2200)*env(1.93,2.0,0.001,0.012)+1.0*sine_sweep(95,45,1.95,0.8,0.22)+0.55*lp(hp(noise,500),3500)*env(2.0,2.8,0.005,0.22)
for k in range(260):
    tb=2.0+abs(rng.normal(0,0.55)); f=rng.uniform(500,2400); fm=sine_sweep(f,f*1.6,tb,0.05,0.02); out+=0.05*fm
# whip whoosh
sw=np.zeros(N); i0,i1=int(2.42*SR),int(2.72*SR); seg=rng.standard_normal(i1-i0); cut=np.linspace(300,3000,i1-i0); sw[i0:i1]=seg*np.sin(np.linspace(0,np.pi,i1-i0))**2; out+=0.25*lp(sw,1800)
# underwater: everything muffled; low rumble and drone swell; falling tone; hull creaks; bubble stream
uw=np.clip((t-2.05)/0.2,0,1)
out=out*(1-uw)+lp(out,420)*uw
rum=lp(noise,260)*0.28*uw; out+=rum
swell=np.clip((t-2.4)/3.0,0,1); out+=uw*swell*(0.16*np.sin(2*np.pi*55*t)+0.11*np.sin(2*np.pi*82.5*t+1.1))
fall=np.zeros(N); f=420*(200/420)**(np.clip((t-2.3)/3.2,0,1)); fall=np.sin(2*np.pi*np.cumsum(f)/SR)*0.035*uw; out+=fall
for tc in (2.9,3.8,4.7):
    L=int(0.7*SR); i0=int(tc*SR); k=np.arange(L)/SR; bp=lp(hp(rng.standard_normal(L),130),260); out[i0:i0+L]+=0.35*bp*np.sin(np.pi*k/0.7)**2*(1+0.5*np.sin(2*np.pi*7*k))
for k in range(150):
    tb=2.8+rng.uniform(0,2.7); f=rng.uniform(700,1700); out+=0.025*sine_sweep(f,f*1.5,tb,0.05,0.022)*(1-0.5*(tb-2.8)/2.7)
out*=np.clip((T-t)/0.12,0,1)
out=np.tanh(out*0.9); out*=0.7/np.max(np.abs(out))
st=np.stack([out,np.roll(out,int(0.0006*SR))],1); pcm=(st*32767).astype(np.int16)
with wave.open(sys.argv[1],'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('wrote',sys.argv[1])
