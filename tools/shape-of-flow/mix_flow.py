import numpy as np, sys, wave
SR=44100; T=25.0; n=int(SR*T); rng=np.random.default_rng(5)
t=np.arange(n)/SR
def env(a,b,c,d,lo=0,hi=1): return np.interp(t,[a,b,c,d],[lo,hi,hi,lo])
def lp(x,fc): 
    k=np.exp(-2*np.pi*fc/SR); y=np.zeros_like(x); 
    from itertools import accumulate
    # one-pole via scipy-less recursion in chunks
    s=0.0
    out=np.empty_like(x)
    for i in range(len(x)): s=k*s+(1-k)*x[i]; out[i]=s
    return out
def noise(): return rng.standard_normal(n)
def fft_filter(x,lo,hi):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); X[(f<lo)|(f>hi)]=0; return np.fft.irfft(X,len(x))
def whoosh(a,b,f0,f1,amp):
    d=int((b-a)*SR); x=rng.standard_normal(d); 
    fc=np.geomspace(f0,f1,d); ph=np.cumsum(fc)/SR
    # swept band: noise modulated by swept sines (cheap sweep)
    y=x*(0.5+0.5*np.sin(2*np.pi*ph))*np.hanning(d); y=fft_filter(y,120,9000)
    out=np.zeros(n); i=int(a*SR); out[i:i+d]=y[:n-i]*amp/ (np.abs(y).max()+1e-9); return out
def hit(a,amp,f0=240,f1=55,dur=1.6,crack=1.0):
    d=int(dur*SR); tt=np.arange(d)/SR; ph=2*np.pi*np.cumsum(f1+(f0-f1)*np.exp(-tt*9))/SR
    body=np.tanh(2.2*np.sin(ph))*np.exp(-tt*2.6)
    sub=np.sin(2*np.pi*48*tt)*np.exp(-tt*2.0)*0.6
    cr=fft_filter(rng.standard_normal(d),2000,9000)*np.exp(-tt*38)*0.8*crack
    gong=sum(np.sin(2*np.pi*f*tt+i)*np.exp(-tt*(1.5+i*0.6))*0.12 for i,f in enumerate([180,271,402,617]))
    y=body+sub+cr+gong; out=np.zeros(n); i=int(a*SR); L=min(d,n-i); out[i:i+L]=y[:L]*amp; return out
def tone(f,a,b,amp,harm=(1,.5,.3,.15)):
    y=sum(h*np.sin(2*np.pi*f*(i+1)*t) for i,h in enumerate(harm)); return y*amp*env(a,a+0.8,b-0.8,b)
mix=np.zeros(n)
# beds
drone=tone(110,0,25,0.10)*(1+0.25*np.sin(2*np.pi*0.2*t)); mix+=drone
mix+=tone(164.8,5.5,10.6,0.05)+tone(220,10.6,17.0,0.05)+tone(55*2**(7/12),17.6,22,0.07,(1,.6,.4,.3,.2))
buzz=np.sin(2*np.pi*100*t)*np.sign(np.sin(2*np.pi*50*t))*0.5; mix+=buzz*env(10.8,11.6,14.0,14.8)*0.035
air=fft_filter(noise(),400,6000); mix+=air*env(13.9,14.8,17.0,17.4)*0.05+air*env(17.6,18.6,21.0,22.4)*0.09
# solar-wind shimmer in Earth shot
sh=fft_filter(noise(),2500,8000)*(0.6+0.4*np.sin(2*np.pi*3.1*t)); mix+=sh*env(6.4,7.2,10.0,11.0)*0.04
# current pulses (ticks) 11.2-14.2
for k in np.arange(11.2,14.2,0.25):
    i=int(k*SR); d=int(0.05*SR); tt=np.arange(d)/SR; mix[i:i+d]+=np.sin(2*np.pi*1400*tt)*np.exp(-tt*80)*0.05
# shells bloom up: glass shimmer 1.3-2.8
for f in (1320,1760,2093,2637): mix+=np.sin(2*np.pi*f*t)*env(2.4,3.0,3.4,4.4)*0.012
# hits and whooshes
mix+=hit(0.0,0.95,300,60,1.8)
mix+=whoosh(0.15,2.7,160,3200,0.5)
mix+=hit(5.9,0.35,160,50,1.3,0.3)+whoosh(4.4,6.0,200,2500,0.3)
mix+=hit(7.1,0.4,200,50,1.2,0.4)
mix+=whoosh(10.5,12.8,250,2800,0.4)
mix+=hit(14.5,0.3,420,90,1.0,0.2)+whoosh(14.0,15.2,2000,400,0.25)
# held breath 17.0-17.4 then the reveal
duck=np.ones(n); duck*=1-0.97*env(16.9,17.0,17.38,17.42); mix*=np.minimum(1,duck+0.0)
mix+=whoosh(15.9,17.0,300,4500,0.45)*1.0*(t<17.05)
mix+=hit(17.4,1.2,260,45,2.6,1.0)
mix+=whoosh(21.8,23.6,400,3200,0.4)
mix+=hit(22.5,0.5,180,52,1.4,0.5)
# loop link: rising tone + crackle into 0.0
mix+=np.sin(2*np.pi*np.cumsum(np.geomspace(180,900,n))/SR)*env(23.9,24.9,24.97,25.0)*0.08
mix+=fft_filter(noise(),3000,9000)*env(24.4,24.95,24.97,25.0)*0.05
mix/=np.abs(mix).max()*1.03; mix=np.tanh(mix*1.5)/np.tanh(1.5)
# short fades
mix[:50]*=np.linspace(0.3,1,50); 
L=mix; R=np.roll(mix,60)*0.97
st=np.stack([L,R],1); pcm=(st*0.89*32767).astype('<i2')
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes()); w.close()
