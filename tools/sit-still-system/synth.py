import numpy as np, wave
SR=48000; D=12.6; N=int(SR*D)
rng=np.random.default_rng(3)
out=np.zeros((N,2))
def lp(x,a):  # one-pole lowpass
    y=np.empty_like(x);s=0.0
    for i,v in enumerate(x): s+=a*(v-s); y[i]=s
    return y
def place(sig,t,g=1.0,pan=0.0):
    i=int(t*SR); j=min(N,i+len(sig))
    if i>=N: return
    out[i:j,0]+=sig[:j-i]*g*(1-pan)*0.8+0*0
    out[i:j,1]+=sig[:j-i]*g*(1+pan)*0.8
t=lambda d: np.arange(int(SR*d))/SR
def glass():
    tt=t(0.9); s=np.zeros_like(tt)
    # crack transient
    s+=rng.normal(0,1,len(tt))*np.exp(-tt*60)*0.9
    # bright tinkles
    for k in range(40):
        t0=abs(rng.normal(0.02,0.12)); f=rng.uniform(3500,9000)
        m=tt>t0; d=tt[m]-t0
        s[m]+=np.sin(2*np.pi*f*d)*np.exp(-d*rng.uniform(25,60))*rng.uniform(0.08,0.25)
    hp=s-lp(s,0.25)
    return hp*0.9
def clank(f0=140,dec=9,dur=0.7):
    tt=t(dur); s=np.zeros_like(tt)
    for f,a in [(f0,1),(f0*2.76,0.5),(f0*5.4,0.3),(f0*8.9,0.15)]:
        s+=a*np.sin(2*np.pi*f*tt)*np.exp(-tt*dec*(1+f/f0*0.3))
    s+=rng.normal(0,1,len(tt))*np.exp(-tt*80)*0.5
    return s*0.6
def thud():
    tt=t(0.4); f=90*np.exp(-tt*6)+45
    s=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*14)
    s+=lp(rng.normal(0,1,len(tt)),0.05)*np.exp(-tt*25)*2
    return s*0.8
def servo(dur,f0,f1):
    tt=t(dur); f=np.linspace(f0,f1,len(tt))
    ph=np.cumsum(f)/SR
    s=(2*(ph%1)-1)*0.3+np.sin(2*np.pi*ph*2)*0.2
    env=np.minimum(1,tt/0.05)*np.minimum(1,(dur-tt)/0.08)
    s=lp(s,0.12)*env
    return s*0.35
def belt(dur=0.45):
    tt=t(dur); s=lp(rng.normal(0,1,len(tt)),0.08)*1.2
    # chain rattle
    for k in range(14):
        t0=k*dur/14; m=tt>t0; d=tt[m]-t0
        s[m]+=np.sin(2*np.pi*rng.uniform(600,1400)*d)*np.exp(-d*120)*0.35
    env=np.sin(np.pi*tt/dur)**0.5
    return s*env*0.5
# ambience hum
tt=np.arange(N)/SR
amb=0.05*np.sin(2*np.pi*55*tt)+0.03*np.sin(2*np.pi*110*tt+1)+0.02*np.sin(2*np.pi*165*tt)
amb+=lp(rng.normal(0,1,N),0.01)*0.35
amb*=1+0.15*np.sin(2*np.pi*0.3*tt)
out[:,0]+=amb; out[:,1]+=amb*0.97
T=2.1;S=1.65;T0=0.8;AH=1.1
for k in range(-1,7):
    base=k*T-T0
    hit=base+AH
    if hit>=0:
        place(glass(),hit,1.1,-0.25)
        place(clank(160,10),hit-0.005,0.7,-0.25)
        place(thud(),hit+0.02,0.8,0.3)
    # smasher windup whir
    if base+0.45>=-0.5: 
        if base+0.45>=0: place(servo(AH-0.09-0.45,220,160),base+0.45,0.6,-0.2)
        place(servo(0.5,150,240),hit+0.2,0.4,-0.2) if hit+0.2>=0 else None
    # capper descend
    if base+0.15>=0: place(servo(AH-0.15,300,180),base+0.15,0.45,0.35)
    # conveyor step
    ms=base+S
    if ms>=0:
        place(belt(T-S),ms,0.9)
        place(clank(70,7,0.8),ms+T-S-0.02,0.9)
m=np.max(np.abs(out)); out=out/m*0.89
# short fade out end to loop smoothly
fo=int(0.05*SR); out[-fo:]*=np.linspace(1,0,fo)[:,None]
w=wave.open('sfx.wav','wb');w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR)
w.writeframes((out*32767).astype('<i2').tobytes());w.close()
