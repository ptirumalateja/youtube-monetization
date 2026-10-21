# Photon Rain v2 sound: fully synthesised (no samples, no credits). Every cue is tied to an on-screen event;
# photon and drop times come from the scene itself (events.json, exported by ev.js).
import numpy as np, wave, json, sys
SR=48000; T=32.0; N=int(SR*T); rng=np.random.default_rng(11); t=np.arange(N)/SR
EV=json.load(open('events.json'))
def sm(a,b,x): k=np.clip((x-a)/(b-a),0,1); return k*k*(3-2*k)
def place(bus,sig,ts):
    i=int(ts*SR); j=min(N,i+len(sig))
    if 0<=i<N and j>i: bus[i:j]+=sig[:j-i]
def band(x,lo,hi):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); m=np.clip(((f>=lo)&(f<=hi))+np.exp(-((f-lo)/(0.2*lo+1))**2)*(f<lo)+np.exp(-((f-hi)/(0.2*hi+1))**2)*(f>hi),0,1); return np.fft.irfft(X*m,len(x))
def tone(f,dur,dec,amp=1.0,harm=((1,1.0),)):
    n=int(dur*SR); x=np.arange(n)/SR; s=sum(a*np.sin(2*np.pi*f*h*x) for h,a in harm); return s*np.exp(-x/dec)*amp*np.minimum(1,x/0.002)
def pluck(f,amp=1.0,dec=0.35): return tone(f,dec*5,dec,amp,((1,1),(2,0.35),(3,0.12)))
def click(amp=1.0,lo=2000,hi=9000,dec=0.004):
    n=int(0.05*SR); x=np.arange(n)/SR; return band(rng.standard_normal(n),lo,min(hi,7000))*np.exp(-x/dec)*amp*np.minimum(1,x/0.0006)*0.6
def whoosh(a,b,peak,lvl,lo=200,hi=5000):
    n=int((b-a)*SR); x=np.arange(n)/SR; e=np.where(x<peak-a,(x/(peak-a))**2,np.exp(-(x-(peak-a))/((b-peak)/3)))
    return band(rng.standard_normal(n),lo,hi)/3.0*e*lvl
def thump(f0=150,f1=55,dur=0.6,amp=1.0):
    n=int(dur*SR); x=np.arange(n)/SR; f=f1+(f0-f1)*np.exp(-x/0.05); return np.tanh(1.8*np.sin(2*np.pi*np.cumsum(f)/SR))*np.exp(-x/(dur/4))*amp
def shutter(amp=1.0):
    s=np.zeros(int(0.12*SR)); c1=click(1.0,1500,8000,0.005); c2=click(0.7,1200,6000,0.006)
    s[:len(c1)]+=c1; i=int(0.035*SR); s[i:i+len(c2)]+=c2[:len(s)-i]; return s*amp
sfx=np.zeros(N); mus=np.zeros(N); hit=np.zeros(N)
# ---- music bed: soft pad (D major 9) + quiet eighth-note pluck pulse at 100 bpm that builds toward the end
for f,a in [(146.8,1),(220,0.7),(293.7,0.5),(370,0.35),(440,0.25)]:
    mus+=a*np.sin(2*np.pi*f*t+0.3*np.sin(2*np.pi*0.11*t*f/146.8))
mus*=0.035*(sm(0,1.5,t))*(1-0.6*sm(17.9,18.2,t)*(1-sm(20.6,21.0,t)))
beat=60/100/2; notes=[293.7,370,440,370, 293.7,440,554.4,440]
for k in range(int(T/beat)):
    ts=k*beat;
    if ts<2.9 or ts>31.6: continue
    lvl=0.10+0.10*(ts>29.1)
    place(mus,pluck(notes[k%8],lvl,0.18),ts)
# ---- S1 hook: frame-0 hit, counter ticks while 12 -> 200 rolls (ticks slow down as it eases), lock ping, camera in, 24 ticks
place(hit,thump(170,60,0.7,0.9),0.025); place(hit,click(0.9,1500,9000,0.008),0.025)
v=lambda u:12+188*(1-(1-u)**3)
last=12
for i in range(1,int(1.0*SR/240)):
    ts=i*240/SR; val=v(ts/1.0)
    if int(val/8)!=int(last/8): place(sfx,click(0.35,3000,9000,0.002),ts)
    last=val
place(sfx,tone(1318.5,1.2,0.35,0.30,((1,1),(2.01,0.3))),0.98); place(sfx,tone(659.3,1.2,0.4,0.25),0.98)
place(sfx,whoosh(1.0,1.9,1.45,0.5,300,6000),1.0)
for k in range(1,25): place(sfx,click(0.25,2500,8000,0.002),1.4+0.6*(1-(1-k/24)**0.5))
place(sfx,tone(987.8,1.0,0.3,0.22),2.0)
# ---- S2: transition whoosh, sensor glow shimmer, zoom riser into the grid + impact
place(sfx,whoosh(2.95,3.9,3.3,0.45),2.95)
shim=np.sin(2*np.pi*1760*t)*0.5+np.sin(2*np.pi*2637*t)*0.3; sfx+=shim*0.025*sm(3.8,4.4,t)*(1-sm(5.6,6.2,t))*(0.6+0.4*np.sin(2*np.pi*5*t/6.283*6.283))
rz=np.zeros(N); fr=200*np.exp(np.clip((t-5.2)/1.0,0,1)*2.2); rz+=np.sin(2*np.pi*np.cumsum(fr)/SR)*0.10*sm(5.2,6.15,t)*(t<6.2)
sfx+=rz+band(rng.standard_normal(N),800,9000)*0.08*sm(5.3,6.18,t)*(t<6.2)
place(hit,thump(140,50,0.8,0.8),6.2); place(hit,click(0.6,1200,7000,0.01),6.2)
# grid lines draw out: a soft glassy sweep
for k in range(11): place(sfx,tone(880*2**(k/12),0.5,0.12,0.06),6.25+k*0.07)
# ---- S4 rain: one glass tick per landed photon (+ small pitch spread)
for ts in EV['rain']:
    place(sfx,tone(rng.uniform(2200,4200),0.25,0.035,rng.uniform(0.08,0.18),((1,1),(2.7,0.2))),ts)
sfx+=band(rng.standard_normal(N),4000,12000)*0.012*sm(9.0,9.5,t)*(1-sm(11.5,12.0,t))
# ---- S5 buckets: drops plink with a pitch per bucket; a fill tone rises with the level
bp=[523.3,659.3,784.0,987.8]
for ts,b,fine in EV['drops']:
    if fine: place(sfx,tone(bp[b]*2,0.15,0.02,0.03),ts)
    else: place(sfx,tone(bp[b],0.4,0.07,0.12,((1,1),(2,0.25))),ts)
k1=np.clip((t-12.6)/2.0,0,1); k2=np.clip((t-15.0)/2.2,0,1)
ff=220+260*k1+300*k2; fl=np.sin(2*np.pi*np.cumsum(ff)/SR)
sfx+=fl*0.035*(sm(12.6,13.0,t)*(1-sm(14.6,14.9,t))+sm(15.0,15.3,t)*(1-sm(17.3,17.8,t)))
place(sfx,whoosh(11.8,12.6,12.1,0.35),11.8); place(sfx,tone(587.3,1.0,0.3,0.15),14.6); place(sfx,tone(880,1.2,0.35,0.15),17.2)
# ---- S6 shot noise: grainy hiss on the noisy tile, clean bell on the clean one
sfx+=band(rng.standard_normal(N),1500,10000)*0.05*sm(18.0,18.3,t)*(1-sm(19.2,19.7,t))
place(sfx,tone(1174.7,1.5,0.5,0.18,((1,1),(2.0,0.3),(3.0,0.1))),18.15)
place(sfx,whoosh(17.6,18.4,17.95,0.35),17.6)
# ---- S7 sizes: phone sensor pop, frame draw sweep, twelve tile pops in a rising scale, photon sprinkle
place(sfx,whoosh(20.6,21.5,20.95,0.35),20.6); place(sfx,tone(392,0.6,0.15,0.18),21.0)
scale=[261.6,293.7,329.6,349.2,392,440,493.9,523.3,587.3,659.3,698.5,784.0]
for i in range(12): place(sfx,pluck(scale[i],0.13,0.12),22.3+i*0.11)
place(hit,thump(160,60,0.5,0.45),23.62)
for i in range(160):
    ts=23.6+1.6*rng.random(); place(sfx,tone(rng.uniform(2500,5000),0.12,0.02,0.05),ts)
# ---- S8 phones fight back: 8 rapid shutter clicks as frames slide out, merge whoosh + chime
place(sfx,whoosh(25.5,26.3,25.85,0.35),25.5)
for i in range(8): place(sfx,shutter(0.35),26.2+i*0.09)
place(sfx,whoosh(27.3,28.4,28.2,0.4,300,7000),27.3); place(sfx,tone(1318.5,1.4,0.45,0.18,((1,1),(1.5,0.3))),28.3)
# ---- S9 the difference: the big hit, end-line chord, loop link back into the frame-0 hit
place(hit,thump(190,52,1.2,1.0),29.1); place(hit,shutter(0.9),29.1)
for f,a in [(587.3,0.16),(880,0.12),(1174.7,0.08),(1480,0.05)]: place(hit,tone(f,2.6,0.9,a),29.1)
lk=np.sin(2*np.pi*np.cumsum(500+700*sm(31.3,32.0,t))/SR)*0.05*sm(31.3,31.95,t); sfx+=lk
# ---- mix: high-pass non-hit buses at 90 Hz, duck under hits, soft clip
from numpy.fft import rfft,irfft,rfftfreq
def hp(x,fc=90): X=rfft(x); f=rfftfreq(len(x),1/SR); return irfft(X*(1/(1+(fc/np.maximum(f,1))**4)),len(x))
sfx=hp(sfx); mus=hp(mus)
env=np.zeros(N)
for ts in (0.0,6.2,23.62,29.1): env=np.maximum(env,np.exp(-np.clip(t-ts,0,None)/0.35)*(t>=ts))
mix=sfx+mus*(1-0.5*env)+hit
mix=np.tanh(mix*1.2)/np.tanh(1.2)
f=int(0.004*SR); mix[:f]*=np.linspace(0,1,f); mix[-f:]*=np.linspace(1,0,f)
mix/=np.abs(mix).max()*1.1
st=np.stack([mix,mix],1); d=int(0.0008*SR); st[d:,1]=0.85*st[d:,1]+0.15*st[:-d,0]
with wave.open(sys.argv[1] if len(sys.argv)>1 else 'mix_v2.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(st,-1,1)*32767).astype(np.int16).tobytes())
print('ok')
