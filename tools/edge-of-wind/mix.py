# Sound for The Edge of the Wind: a fully synthesized "plasma wind" family (no samples, so no licence questions).
# Cue sheet follows the scene: frame-0 flare hit, snap at 2.0, solar-wind roar that rises with speed, Voyager telemetry pings,
# termination-shock hit at 9.6 (wind collapses to a slow turbulent rumble), held breath 13.4-14.0, heliopause hit at 14.05
# (biggest), interstellar bed (plasma whistle + low drone), bell on the end line, plunge back into frame 0.
# usage: python3 mix.py out.wav
import numpy as np, wave, sys
SR=48000; T=22.0; N=int(SR*T); t=np.arange(N)/SR
rng=np.random.default_rng(1977)
def db(g): return 10**(g/20)
def sstep(a,b,x): k=np.clip((x-a)/(b-a),0,1); return k*k*(3-2*k)
def band(x,lo,hi,order=2):
    n=len(x); X=np.fft.rfft(x,axis=0); f=np.fft.rfftfreq(n,1/SR)
    m=np.ones_like(f)
    if lo: m*=1-1/np.sqrt(1+(f/lo)**(2*order))
    if hi: m*=1/np.sqrt(1+(f/hi)**(2*order))
    return np.fft.irfft(X*(m[:,None] if x.ndim==2 else m),n=n,axis=0)
def noise(n=N,st=True): return rng.standard_normal((n,2) if st else n)
def pink(n=N):
    X=np.fft.rfft(rng.standard_normal((n,2)),axis=0); f=np.fft.rfftfreq(n,1/SR); f[0]=1; X/=np.sqrt(f)[:,None]; y=np.fft.irfft(X,n=n,axis=0); return y/np.abs(y).max()
buses={k:np.zeros((N,2)) for k in ['hit','wind','pad','ping','air','sub']}
def add(bus,sig,t0,gain=0.0,pan=0.0):
    if sig.ndim==1: sig=np.stack([sig,sig],1)
    a=int(round(t0*SR)); sig=sig*db(gain)
    if a<0: sig=sig[-a:]; a=0
    n=min(len(sig),N-a)
    if n<=0: return
    l=1-max(0,pan); r=1+min(0,pan); buses[bus][a:a+n,0]+=sig[:n,0]*l; buses[bus][a:a+n,1]+=sig[:n,1]*r
def env_exp(n,tau,att=0.002):
    tt=np.arange(n)/SR; return np.minimum(1,tt/att)*np.exp(-tt/tau)
def sat(x,d): return np.tanh(x*d)/np.tanh(d)
# ---------------------------------------------------------------- hit anatomy: suck swell + vacuum, crack, pitch-drop body, partials, sub
def hit(t0,size,f0,f1,partials=None,ptau=1.6,g=0.0):
    dur=0.5+1.4*size; n=int(dur*SR); tt=np.arange(n)/SR
    crack=band(noise(int(0.06*SR)),2200,11000)*env_exp(int(0.06*SR),0.012)[:,None]; add('hit',crack/np.abs(crack).max(),t0,-4+4*size+g)
    f=f1+(f0-f1)*np.exp(-tt*7.5); ph=2*np.pi*np.cumsum(f)/SR; body=sat(np.sin(ph)+0.35*np.sin(2*ph),2.4)*env_exp(n,0.18+0.35*size,0.003); add('hit',body,t0,-6+5*size+g)
    sub=np.sin(2*np.pi*np.cumsum(46+20*np.exp(-tt*5))/SR)*env_exp(n,0.25+0.5*size,0.006); add('sub',sub,t0,-10+6*size+g)
    if partials:
        m=int((ptau*3)*SR); tm=np.arange(m)/SR; gp=np.zeros(m)
        for k,(fr,amp) in enumerate(partials): gp+=amp*np.sin(2*np.pi*fr*tm+k)*np.exp(-tm/(ptau*(1-0.12*k)))
        gp*=np.minimum(1,tm/0.004); add('hit',np.stack([gp,np.roll(gp,90)],1),t0,-12+5*size+g-(4 if size<0.9 else 0))
    # duck everything else around the hit
    return t0
def suck(t_hit,length,gain,vac=0.06):
    n=int(length*SR); x=band(noise(n),500,7000); e=np.linspace(0,1,n)**2.6; x=x*e[:,None]; x/=np.abs(x).max()+1e-9
    add('air',x,t_hit-vac-length,gain)
def vacuum(t_hit,vac):
    a=int((t_hit-vac)*SR); b=int(t_hit*SR)
    for k in ['wind','pad','ping','air']: buses[k][a:b]*=0.03
HITS=[(0.0,0.75),(2.0,0.35),(9.6,0.6),(14.05,1.0)]
# ---------------------------------------------------------------- 0-2.0: corona: crackle + hiss + warm low drone
cr=np.zeros((N,2)); idx=rng.integers(0,int(2.1*SR),900)
for i in idx: cr[i,rng.integers(0,2)]+=rng.uniform(0.2,1.0)*rng.choice([-1,1])
cr=band(cr,1800,9000); cr/=np.abs(cr).max(); add('air',cr*(1-sstep(1.7,2.2,t))[:,None],0,-15)
hiss=band(noise(),3500,9000); hiss/=np.abs(hiss).max(); add('air',hiss*(sstep(0,0.3,t)*(1-sstep(1.8,2.3,t)))[:,None]*0.6,0,-20)
# ---------------------------------------------------------------- 2.0-9.6: solar wind roar, centre frequency rising with speed
P=pink(); centres=[220,360,600,1000,1600]; bands=[]
for c in centres: b=band(P,c/1.6,c*1.6); bands.append(b/np.abs(b).max())
curve=np.interp(t,[2.0,4.0,6.6,8.6,9.55],[0.6,1.6,2.6,3.6,4.0])   # index into centres
wind=np.zeros((N,2))
for i,b in enumerate(bands): w=np.clip(1-np.abs(curve-i),0,1); wind+=b*w[:,None]
lvl=sstep(1.8,2.3,t)*(1-sstep(9.5,9.6,t))*np.interp(t,[2,6,9.5],[0.75,0.9,1.0])
gust=1+0.25*np.sin(2*np.pi*0.7*t)+0.15*np.sin(2*np.pi*1.9*t+1)
add('wind',wind*(lvl*gust)[:,None],0,-12)
# streak grains: short filtered whooshes flying past, random pans, denser as the wind speeds up
for k in range(70):
    tg=rng.uniform(2.1,9.4); L=rng.uniform(0.12,0.3); n=int(L*SR); x=band(noise(n,False),900,5000)
    e=np.sin(np.linspace(0,np.pi,n))**2; x=x*e; x/=np.abs(x).max(); pan=rng.uniform(-0.8,0.8)
    if rng.random()<0.35+0.5*(tg-2)/7.5: add('air',x,tg,-27,pan)
# ---------------------------------------------------------------- 9.6-13.4: heliosheath: slow, churning low rumble + teal plinks
rum=band(P,70,420); rum/=np.abs(rum).max(); xp=np.arange(0,22.2,0.11); am=np.interp(t,xp,rng.uniform(0.45,1.0,len(xp))); am=np.convolve(am,np.ones(2400)/2400,'same')
lv2=sstep(9.6,9.75,t)*(1-sstep(13.2,13.45,t)); add('wind',rum*(lv2*am)[:,None],0,-9)
PENT=[1046.5,1174.7,1318.5,1568.0,1760.0,2093.0,2349.3]
for k in range(26):
    tg=rng.uniform(9.9,13.2); fr=rng.choice(PENT); n=int(0.5*SR); tt=np.arange(n)/SR; x=np.sin(2*np.pi*fr*tt)*np.exp(-tt/0.12)*np.minimum(1,tt/0.004)
    add('air',x,tg,-30,rng.uniform(-0.7,0.7))
# riser into the held breath
n=int(1.0*SR); tt=np.arange(n)/SR; fr=180*2**(tt*2.2); rs=np.sin(2*np.pi*np.cumsum(fr)/SR)*(tt/1.0)**2; add('pad',rs,12.45,-20)
rn=band(noise(n),1200,8000)*((tt/1.0)**3)[:,None]; rn/=np.abs(rn).max(); add('air',rn,12.45,-22)
# ---------------------------------------------------------------- pads: warm solar chord early, interstellar drone after the heliopause
def pad(freqs,t0,t1,gain,fi=0.6,fo=0.8,bright=1800):
    n=int((t1-t0)*SR); tt=np.arange(n)/SR; x=np.zeros(n)
    for fr in freqs:
        for det in (-0.35,0.0,0.4):
            ph=(fr+det)*tt; x+=2*(ph-np.floor(ph+0.5))   # saw
    x=band(x,60,bright); x/=np.abs(x).max(); e=sstep(0,fi,tt)*(1-sstep(t1-t0-fo,t1-t0,tt)); add('pad',np.stack([x*e,np.roll(x,240)*e],1),t0,gain)
pad([110,164.8,220],0.0,9.6,-23,fi=0.4,fo=0.12,bright=1400)
pad([82.4,123.5,164.8],9.6,13.4,-24,fi=0.2,fo=0.3,bright=700)
pad([73.4,110,146.8,220,293.7],14.05,21.0,-20,fi=0.25,fo=1.2,bright=2200)
# plasma whistle: Voyager's plasma-wave instrument heard ~2-3 kHz oscillations in interstellar gas; a faint narrow band there
pw=band(noise(),2450,2800,order=4); pw/=np.abs(pw).max(); wob=1+0.4*np.sin(2*np.pi*0.23*t); add('air',pw*(sstep(14.2,15.2,t)*(1-sstep(20.4,21.0,t))*wob)[:,None],0,-25)
# interstellar head-wind: wide low whoosh
iw=band(P,140,900); iw/=np.abs(iw).max(); add('wind',iw*(sstep(14.05,14.6,t)*(1-sstep(20.6,21.1,t))*np.interp(t,[14,16,19,21],[1,0.8,0.55,0.4]))[:,None],0,-16)
# pull-out swell
n=int(1.6*SR); tt=np.arange(n)/SR; sw=band(noise(n),300,4000)*(np.sin(np.pi*tt/1.6)**2)[:,None]; sw/=np.abs(sw).max(); add('air',sw,15.0,-21)
# ---------------------------------------------------------------- Voyager telemetry pings (a heartbeat; farther and fainter after the heliopause)
for k,tp in enumerate(np.arange(2.45,19.0,1.6)):
    if 13.3<tp<14.3: continue
    far=tp>14.05; n=int(0.9*SR); tt=np.arange(n)/SR; fr=2200
    x=(np.sin(2*np.pi*fr*tt)+0.25*np.sin(2*np.pi*fr*2*tt))*np.exp(-tt/(0.09 if not far else 0.22))*np.minimum(1,tt/0.003)
    if far: x=x+0.5*np.roll(x,int(0.11*SR))+0.25*np.roll(x,int(0.23*SR))
    add('ping',np.stack([x,np.roll(x,60)],1),tp,-27 if not far else -31,0.25)
# ---------------------------------------------------------------- hits
suck(2.0,0.5,-20,0.045); suck(9.6,0.7,-18,0.06); suck(14.05,0.9,-15,0.08)
hit(0.0,0.75,280,62,[(196,1.0),(311,0.5),(523,0.3)],1.0,g=-1.5)
hit(2.0,0.35,230,80,g=-3.0)
hit(9.6,0.6,200,58,[(420,1.0),(1130,0.6),(1870,0.4)],0.9,g=-5.0)
hit(14.05,1.0,320,52,[(98,1.0),(147,0.7),(262,0.45),(415,0.3),(619,0.2)],2.4)
# end-line bell, then the plunge: reverse whoosh + rising tone into frame 0
for fr,a in [(587.3,1.0),(880,0.45),(1174.7,0.3),(1763,0.15)]:
    n=int(2.5*SR); tt=np.arange(n)/SR; x=a*np.sin(2*np.pi*fr*tt)*np.exp(-tt/0.8)*np.minimum(1,tt/0.003); add('air',np.stack([x,np.roll(x,180)],1),19.28,-17)
n=int(1.0*SR); tt=np.arange(n)/SR; pl=band(noise(n),400,9000)*((tt/1.0)**3)[:,None]; pl/=np.abs(pl).max(); add('air',pl,20.9,-11)
fr=140*2**(tt*1.6); ri=np.sin(2*np.pi*np.cumsum(fr)/SR)*(tt/1.0)**2; add('pad',ri,20.9,-19)
# ---------------------------------------------------------------- held breath and loop gap
def gate(a,b,g,ramp=0.05):
    m=1-(1-g)*sstep(a,a+ramp,t)*(1-sstep(b-ramp,b,t))
    for k in ['wind','pad','ping','air']: buses[k]*=m[:,None]
gate(13.4,14.0,0.02,0.18); vacuum(9.6,0.06); vacuum(14.05,0.08); vacuum(2.0,0.045)
gate(21.93,22.0,0.05,0.02)
# ---------------------------------------------------------------- bus processing and master
for k in ['wind','pad','ping','air']: buses[k]=band(buses[k],90,None)   # phones cannot play below ~90 Hz; keep the sub on the hit/sub buses
buses['sub']=band(buses['sub'],30,140)
hitenv=np.zeros(N)
for th,sz in HITS: hitenv=np.maximum(hitenv,sz*np.exp(-np.clip(t-th,0,None)/0.35)*(t>=th))
duck=1-0.55*hitenv
for k in ['wind','pad','air']: buses[k]*=duck[:,None]
# small reverb on the hit bus (feedback comb + allpass-ish diffusion)
h=buses['hit']; rv=np.zeros_like(h)
for dly,g in [(0.031,0.5),(0.047,0.45),(0.071,0.4),(0.113,0.35),(0.167,0.3)]:
    d=int(dly*SR); y=np.zeros_like(h); y[d:]=h[:-d]*g; rv+=y
rv=band(rv,200,6000); buses['hit']=h+0.6*rv
mix=buses['hit']*1.0+buses['sub']*0.8+(buses['wind']+buses['pad']+buses['air'])*db(5.5)+buses['ping']*db(3)
mix=np.tanh(mix*1.6)/1.6; mix/=np.abs(mix).max(); mix*=0.89
fi=int(0.003*SR); mix[:fi]*=np.linspace(0,1,fi)[:,None]
with wave.open(sys.argv[1],'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(mix,-1,1)*32767).astype('<i2').tobytes())
print('mix written')
