# Foley mix for the golf reel. python3 mix.py <fulldir> <out.wav>
# Sounds: our earlier ElevenLabs foley (sfx/*.mp3) + CC0 wind (sleepCircle 22331) + synthesized ball roll and sub.
import sys, json, subprocess, numpy as np
D=sys.argv[1]; OUT=sys.argv[2]; SR=48000; DUR=23.5; N=int(SR*DUR)
cues=json.load(open(f'{D}/cues.json'))
def load(p,start=0.0,dur=None):
    a=['ffmpeg','-v','error','-ss',str(start),'-i',p]+(['-t',str(dur)] if dur else [])+['-ac','1','-ar',str(SR),'-f','f32le','-']
    return np.frombuffer(subprocess.run(a,capture_output=True).stdout,np.float32).copy()
S={k:load(f'sfx/{k}.mp3') for k in ['click','thud','rewind','coin','hit1','hit3','thump','swish','whoosh']}
wind=load('../sfxlib/22331__sleepcircle__wind.ogg')
bus={k:np.zeros(N,np.float32) for k in ('hit','fol','amb')}
def db(x): return 10**(x/20)
def place(b,x,t,g_db,align_peak=False):
    i=int(t*SR)
    if align_peak: i-=int(np.argmax(np.abs(x)))
    if i<0: x=x[-i:]; i=0
    n=min(len(x),N-i)
    if n>0: bus[b][i:i+n]+=x[:n]*db(g_db)
rng=np.random.default_rng(3)
def lp(x,fc):  # one-pole low-pass
    a=np.exp(-2*np.pi*fc/SR); y=np.empty_like(x); s=0.0
    for i in range(len(x)): s=(1-a)*x[i]+a*s; y[i]=s
    return y
def roll(t0,T,g_db,decel=True):
    """ball rolling on short grass: band-limited noise with a slow flutter, fading as it slows"""
    n=int(T*SR); u=np.linspace(0,1,n); x=rng.standard_normal(n).astype(np.float32)
    x=lp(x,1400)-lp(x,180)
    env=(1-u)**1.4 if decel else np.ones(n); env*=np.minimum(1,u*40)
    flutter=1+0.25*np.sin(2*np.pi*np.cumsum(14*(1-0.7*u))/SR*1.0)
    place('fol',(x*env*flutter).astype(np.float32),t0,g_db)
def sub(t0,f0=90,dec=0.35,g_db=-6):
    n=int(1.2*SR); tt=np.arange(n)/SR; f=f0*np.exp(-tt*1.2); ph=2*np.pi*np.cumsum(f)/SR
    place('hit',(np.sin(ph)*np.exp(-tt/dec)).astype(np.float32),t0,g_db)
def strike(t,g=-4): place('hit',S['click'][:int(0.35*SR)],t,g,True); place('hit',lp(S['thump'],2500)[:int(0.25*SR)],t,g-12,True)
def clunk(t,g=0):  # ball into the cup: hollow thump + plastic clink
    place('hit',S['thump'],t,g,True); place('fol',S['coin'],t+0.05,g-10,True)

# ambience: night wind, louder while the 93% row waits, gone for the held breath
w=np.tile(wind,int(N/len(wind))+2)[:N]
env=np.full(N,db(-18),np.float32)
def seg(a,b,v): env[int(a*SR):int(b*SR)]=db(v)
seg(5.6,8.0,-8); seg(17.25,17.98,-48)
env=np.convolve(env,np.ones(int(0.25*SR))/int(0.25*SR),'same').astype(np.float32)
bus['amb']+=w*env

# A hook: last roll, cup at 0.33, weight on frame 0
roll(0.0,0.3,-14,decel=False); place('hit',S['hit3'],0.0,-10,True); clunk(0.33,0); sub(0.33,95,0.3,-8)
# B rewind
place('fol',S['rewind'],2.48,-5); place('fol',S['swish'],3.08,-8,True)
# C lock-in ticks on labels and lines
for t in (3.3,3.55,3.8): place('fol',S['coin'][:int(0.12*SR)],t,-20,True)
for t in (3.95,4.35,4.75): place('fol',S['click'][:int(0.08*SR)],t,-20,True)
place('fol',S['click'][:int(0.08*SR)],5.8,-16,True)
# 6%: strike, roll, stop, club falls
strike(8.45,-3); roll(8.45,1.5,-12); place('fol',S['thump'][:int(0.2*SR)],9.95,-22,True)
place('hit',S['thud'],10.55,2,True); place('fol',S['coin'],10.57,-16,True)
# D 1%: accelerating strikes and rolls
place('fol',S['swish'],10.98,-8,True)
for k,(t,T) in enumerate(zip(cues['imp1'],cues['T1'])):
    strike(t,-4-min(6,k*0.25)); roll(t,T,-15-min(6,k*0.2))
# final putt: louder strike, long roll, rim, held breath, drop = biggest hit
strike(cues['final_imp'],-1); roll(cues['final_imp'],cues['rim']-cues['final_imp'],-10)
place('fol',S['swish'],17.33,-12,True)
roll(cues['rim'],cues['drop']-cues['rim'],-12,decel=False)
clunk(cues['drop'],2); place('hit',S['hit1'],cues['drop'],-2,True); sub(cues['drop'],85,0.6,-3)
# F closing and CTA
place('fol',S['swish'],18.88,-8,True)
place('hit',S['thud'],20.05,-2,True); sub(20.05,70,0.4,-12)
place('fol',S['coin'][:int(0.12*SR)],21.9,-16,True)
# H dive back into frame 0 (loop)
place('fol',S['whoosh'],22.9,-2)

# master: duck ambience under hits, sum, soft clip, normalise
hitenv=np.convolve(np.abs(bus['hit']),np.ones(2400)/2400,'same'); duck=1/(1+4*hitenv)
mix=bus['hit']+bus['fol']+bus['amb']*duck
mix=np.tanh(mix*1.4)/np.tanh(1.4); mix*=0.89/np.abs(mix).max()
st=np.stack([mix,mix],1)
subprocess.run(['ffmpeg','-y','-v','error','-f','f32le','-ar',str(SR),'-ac','2','-i','-','-c:a','pcm_s16le',OUT],input=st.astype(np.float32).tobytes())
def rms(a,b): x=mix[int(a*SR):int(b*SR)]; return 20*np.log10(np.sqrt((x**2).mean())+1e-9)
print(f'0-0.5 {rms(0,0.5):.1f} | 93% wait {rms(6,8):.1f} | held breath {rms(17.4,17.95):.1f} | drop {rms(17.98,18.4):.1f} dB')
