# v3 foley + piano mix -> output/mix.wav. Two-pass linear loudnorm at -14 LUFS (keeps the dynamics arc).
import numpy as np, subprocess, json
SR=48000; DUR=13.0; LIB='../sfxlib/'
def load(path,a0=0.0,a1=None,flt=None):
    af=[]
    if path.startswith('sfx/'): af.append('equalizer=f=15600:t=q:w=30:g=-30')   # ElevenLabs stems carry a 15.6 kHz whistle
    if flt: af.append(flt)
    cmd=['ffmpeg','-v','error','-ss',str(a0)]+(['-to',str(a1)] if a1 else [])+['-i',path]+(['-af',','.join(af)] if af else [])+['-ac','2','-ar',str(SR),'-f','f32le','-']
    return np.frombuffer(subprocess.run(cmd,capture_output=True).stdout,np.float32).reshape(-1,2).copy()
out=np.zeros((int(SR*DUR)+SR*12,2),np.float32)
def db(x): return 10**(x/20)
def put(a,t,g_db=0.0,fade_in=0.0,fade_out=0.0,peak_norm=True):
    a=a.copy()
    if peak_norm: a/=np.abs(a).max()+1e-9
    a*=db(g_db)
    if fade_in: k=int(fade_in*SR); a[:k]*=np.linspace(0,1,k)[:,None]
    if fade_out: k=min(len(a),int(fade_out*SR)); a[-k:]*=np.linspace(1,0,k)[:,None]
    i=int(round(t*SR))
    if i<0: a=a[-i:]; i=0
    out[i:i+len(a)]+=a[:len(out)-i]
W5=LIB+'175183__tomlija__5-everyday-whooshes.wav'; WC=LIB+'649445__audiopapkin__cinematic-woosh-sfx-015.wav'
PK=[3.65,7.9,12.6,17.4,21.4]
def whoosh(i,cut,g,semi=0):
    a=load(W5,PK[i]-0.45,PK[i]+0.55,f'asetrate={SR}*{2**(semi/12):.4f},aresample={SR}' if semi else None); put(a,cut-0.45,g,fade_in=0.05,fade_out=0.25)
# room tone: high-passed, quiet, with a true-silence dip before the door beat
room=load('sfx/room.mp3',flt='highpass=f=120'); room/=np.abs(room).max()+1e-9; room*=db(-34)
env=np.ones(len(room)); a,b=int(4.62*SR),int(5.0*SR); env[a:b]=db(-26); room*=env[:,None]; out[:len(room)]+=room
# 0.0 hook: air whoosh of the swinging door, latch on the visual shut (0.30)
put(load(WC,2.3,3.0),-0.12,-9,fade_out=0.3)
put(load('sfx/doorswing.mp3',flt='alimiter=limit=0.7:attack=1:release=30,lowpass=f=9000'),0.30-0.15,-2)
put(load('sfx/door_close.mp3',0,0.4),0.29,-10)
put(load('sfx/ticks.mp3',0,0.55),0.0,-30,fade_out=0.2)
# cuts
whoosh(0,0.55,-16,+1); whoosh(1,1.6,-15,-1); whoosh(2,2.7,-15,+2); whoosh(3,3.8,-15,0); whoosh(4,5.0,-13,-2)
whoosh(1,5.7,-18,+2); whoosh(2,6.4,-20,-1)
put(load('sfx/sigh.mp3'),0.55,-18)
put(load('sfx/ticks.mp3',0,1.1),0.5,-12,fade_in=0.05,fade_out=0.1)          # keep the hook window alive after the rewind
put(load('sfx/jingle.mp3',0.0,0.35),0.95,-22,fade_out=0.1)
put(load('sfx/swish.mp3'),0.7,-13,fade_in=0.05,fade_out=0.2)                    # body settling onto the rug                     # collar tag as he lies down
put(load('sfx/ticks.mp3'),1.6,-15,fade_out=0.05)
# the owner's day gets its own life underneath the ticks (office, cafe, bike), each cut on the whip
for nm,t0,t1,g in (('office',1.75,2.7,-12),('cafe',2.62,3.8,-12),('bike',3.72,4.6,-16)):
    a=load(f'sfx/life_{nm}.mp3',flt='alimiter=limit=0.8'); n=int((t1-t0+0.15)*SR)
    if len(a)<n: a=np.concatenate([a,a[::-1]])            # mirror-extend so the layer holds past its cut
    put(a[:n],t0,g,fade_in=0.08,fade_out=0.15)
    b=a[:int((t1-t0-0.45)*SR)]; put(b,t0+0.6,g-4,fade_in=0.1,fade_out=0.2)   # second staggered pass fills the panel's tail            # clock through the split; hard stop 4.6
i0=int(4.6*SR); n0=int(0.02*SR); out[i0:i0+n0]*=np.linspace(1,0.4,n0)[:,None]; out[i0+n0:int(5.0*SR)]*=0.4

# the waiting piano (first note lands on the 5.0 cut), ducked under the jingle
pia=load('sfx/piano.mp3'); pia/=np.abs(pia).max(); pia*=db(-8)
d=np.ones(len(pia)); s0,s1=int((6.15-4.75)*SR),int((7.3-4.75)*SR); d[s0:s1]=db(-6); pia*=d[:,None]
k=int(3.5*SR); seg=int((8.6-4.75)*SR); pia[seg-k//8:seg]*=np.linspace(1,0.35,k//8)[:,None]; pia[seg:]*=0.35
p0,p1=int((5.0-4.75)*SR),int((5.8-4.75)*SR); pf=int(0.15*SR); e=np.full(p1-p0,db(-3)); e[-pf:]=np.linspace(db(-3),1,pf); pia[p0:p1]*=e[:,None]   # first 0.8 s of the waiting piano under the reunion
put(pia,4.75,0,peak_norm=False)
put(load('sfx/jingle.mp3'),6.32,-7)
put(load('sfx/whine.mp3'),6.95,-9)
put(load('sfx/door_open.mp3',0.45,1.2),7.36,-5)
put(load('sfx/barks.mp3'),7.72,-4)
i0,i1=int(7.95*SR),int(8.08*SR); out[i0:i1]*=np.linspace(1,db(-5),i1-i0)[:,None]   # pre-duck so the hit has room
put(load('sfx/thump2.mp3',flt='alimiter=limit=0.7:attack=1:release=40'),8.06,-5)
put(load('sfx/thump2.mp3',flt='highpass=f=150,lowpass=f=1800,alimiter=limit=0.7:attack=1:release=40'),8.015,-4)
kt=np.arange(int(0.22*SR))/SR; kick=np.sin(2*np.pi*(58*kt+40*(1-np.exp(-kt/0.03))*0.03))*np.exp(-kt/0.07); put(np.stack([kick,kick],1).astype(np.float32),8.07,-7)
put(load('sfx/laugh.mp3'),8.22,-8)
# reunion: warm G major chord on the cut, with a room tail so it rings to the end
put(load('sfx/reunion_piano.mp3',0,4.6),8.58,2,fade_out=1.0)
nz=load('sfx/nuzzle.mp3',flt='acompressor=threshold=-30dB:ratio=4:attack=5:release=80'); nz=np.concatenate([nz[:int(2.3*SR)],nz[int(2.7*SR):]])
put(nz,9.05,-12,fade_in=0.1,fade_out=0.4)
put(load('sfx/jingle.mp3',0.0,0.4),9.8,-24,fade_out=0.15)
put(load('sfx/whine.mp3'),10.6,-14)
put(load('sfx/nuzzle.mp3',0.2,1.6),11.6,-16,fade_in=0.1,fade_out=0.3)
r0,r1=int(8.6*SR),int(9.8*SR); rf=int(0.3*SR); env=np.full(r1-r0,db(6.0)); env[-rf:]=np.linspace(db(6.0),1,rf); out[r0:r1]*=env[:,None]   # reunion bus lift
g0,g1=int(4.62*SR),int(4.98*SR); nf=int(0.02*SR)
out[g0:g0+nf]*=np.linspace(1,db(-26),nf)[:,None]; out[g0+nf:g1]*=db(-26)       # the silence beat before the door close-up
mix=out[:int(SR*DUR)]
j0,j1=int(6.1*SR),int(6.5*SR); jf=int(0.05*SR); e=np.full(j1-j0,db(-3)); e[:jf]=np.linspace(1,db(-3),jf); e[-jf:]=np.linspace(db(-3),1,jf); mix[j0:j1]*=e[:,None]   # jingle beat under the reunion
k=int(0.4*SR); mix[-k:]*=np.linspace(1,0.75,k)[:,None]
# payoff-first cold open (0.6 s): the leap itself (bark, impact) lifted from the story mix, piano downbeat, rewind whoosh
COLD=0.6; nc=int(COLD*SR); pre=np.zeros((nc,2),np.float32)
def pput(x,t,g,fo=0.0,norm=True):
    x=(x/(np.abs(x).max()+1e-9) if norm else x)*db(g); i=int(t*SR); x=x[:nc-i].copy()
    if fo: k=min(len(x),int(fo*SR)); x[-k:]*=np.linspace(1,0,k)[:,None]
    pre[i:i+len(x)]+=x
pput(load('sfx/barks.mp3',0,0.35),0.0,-9,0.1)
pput(load('sfx/reunion_piano.mp3',0.0,0.6),0.0,-4,0.15)
pput(load('sfx/laugh.mp3',0,0.5),0.05,-11,0.12)
rw=load(WC,2.3,3.0)[::-1]; pput(rw[-int(0.3*SR):],0.3,-9)
mix=np.concatenate([pre,mix]); DUR=DUR+COLD
mix.astype(np.float32).tofile('output/mix.f32')
# two-pass linear loudnorm
m=subprocess.run(['ffmpeg','-hide_banner','-f','f32le','-ar',str(SR),'-ac','2','-i','output/mix.f32','-af','acompressor=threshold=-18dB:ratio=2:attack=10:release=150,loudnorm=I=-14:TP=-2.5:LRA=20:print_format=json','-f','null','-'],capture_output=True,text=True).stderr
j=json.loads(m[m.rindex('{'):m.rindex('}')+1])
af=(f"acompressor=threshold=-18dB:ratio=2:attack=10:release=150,loudnorm=I=-14:TP=-2.5:LRA=20:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(SR),'-ac','2','-i','output/mix.f32','-af',af,'-ar',str(SR),'output/mix.wav'],check=True)
print('mix ok', j['input_i'], j['normalization_type'] if 'normalization_type' in j else '')
# post-normalisation emphasis (after the bus compressor): reunion is the loudest beat, the head-lift sits under it
subprocess.run(['ffmpeg','-v','error','-y','-i','output/mix.wav','-af',
  "volume='if(between(t,9.15,10.5),1.4,if(between(t,6.6,7.0),0.79,1))':eval=frame,alimiter=limit=0.8:attack=2:release=60:level=false",
  '-ar',str(SR),'output/mix_post.wav'],check=True)
import os; os.replace('output/mix_post.wav','output/mix.wav')
