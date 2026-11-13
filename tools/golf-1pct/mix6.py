# Foley mix for the golf reel. python3 mix.py <fulldir> <out.wav>
# Sounds: our earlier ElevenLabs foley (sfx/*.mp3) + CC0 wind (sleepCircle 22331) + synthesized ball roll and sub.
import sys, json, subprocess, numpy as np
D=sys.argv[1]; OUT=sys.argv[2]; SR=48000; DUR=json.load(open(sys.argv[1]+'/cues.json'))['dur']; N=int(SR*DUR)
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

# ambience: night wind under everything, gone for the held breath before the drop
w=np.tile(wind,int(N/len(wind))+2)[:N]
env=np.full(N,db(-16),np.float32)
def seg(a,b,v): env[int(a*SR):int(b*SR)]=db(v)
seg(cues['lips'][0],cues['final_imp'],-22); seg(cues['final_imp']+0.4,cues['drop'],-48)
env=np.convolve(env,np.ones(int(0.25*SR))/int(0.25*SR),'same').astype(np.float32)
bus['amb']+=w*env
# 0.3 s: the 6% and the 1% hit together (one big double strike) while the 93% freezes
strike(cues['imp0'],2); place('hit',S['hit3'],cues['imp0'],-9,True); sub(cues['imp0'],100,0.25,-10)
roll(cues['imp0'],cues['T1'][0],-12); roll(cues['imp0']+0.01,cues['T1'][0],-14)
place('fol',S['thump'][:int(0.2*SR)],cues['miss6_stop'],-20,True)
# 6% drops the club
place('hit',S['thud'],cues['fall'],2,True); place('fol',S['coin'],cues['fall']+0.02,-16,True)
# 93% hesitations: a small grip creak/tick each time it freezes
for t in cues['hes'][1:]: place('fol',S['click'][:int(0.06*SR)],t+0.3,-24,True)
# 1% sprint: accelerating strikes and rolls, then lip-outs: rim rattle, louder each time, wind drops away
for k,(t,T) in enumerate(zip(cues['imp1'][1:],cues['T1'][1:])):
    lip=k+1>=26
    strike(t,-2 if lip else -3-min(5,k*0.2)); roll(t,T,-11 if lip else -15-min(5,k*0.15))
    if lip:
        j=k+1-26; place('fol',S['coin'],t+T*0.55,-10+j*0.8,True); place('fol',S['thump'][:int(0.15*SR)],t+T*0.55,-16+j,True)
        place('hit',S['thud'][:int(0.4*SR)],t+T,-14+j*0.9,True)
# final putt, held breath, drop = biggest hit
strike(cues['final_imp'],0); roll(cues['final_imp'],cues['rim']-cues['final_imp'],-10)
roll(cues['rim'],cues['drop']-cues['rim'],-12,decel=False)
clunk(cues['drop'],2); place('hit',S['hit1'],cues['drop'],-2,True); sub(cues['drop'],85,0.6,-3)
# ball drops onto the tees
for t in cues['drops']: place('fol',S['thump'][:int(0.18*SR)],t,-6,True); place('fol',S['click'][:int(0.05*SR)],t,-14,True)
place('fol',S['coin'][:int(0.12*SR)],cues['drop']+1.5,-16,True)
# master: duck ambience under hits, sum, soft clip, normalise
hitenv=np.convolve(np.abs(bus['hit']),np.ones(2400)/2400,'same'); duck=1/(1+4*hitenv)
mix=bus['hit']+bus['fol']+bus['amb']*duck
mix=np.tanh(mix*1.4)/np.tanh(1.4); mix*=0.89/np.abs(mix).max()
st=np.stack([mix,mix],1)
subprocess.run(['ffmpeg','-y','-v','error','-f','f32le','-ar',str(SR),'-ac','2','-i','-','-c:a','pcm_s16le',OUT],input=st.astype(np.float32).tobytes())
def rms(a,b): x=mix[int(a*SR):int(b*SR)]; return 20*np.log10(np.sqrt((x**2).mean())+1e-9)
d=cues['drop']; print(f'0-0.5 {rms(0,0.5):.1f} | sprint {rms(3,5.5):.1f} | lips {rms(6.3,11):.1f} | held breath {rms(d-0.6,d-0.05):.1f} | drop {rms(d,d+0.4):.1f} dB')
