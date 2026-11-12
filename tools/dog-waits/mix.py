# v5 foley + piano mix -> output/mix.wav, laid out on the timeline.py output clock: one-shots at natural speed at T(body),
# beds (room tone, waiting piano) built in body time and time-warped per segment (rubberband for slow motion). Two-pass linear loudnorm at -14 LUFS (keeps the dynamics arc).
import numpy as np, subprocess, json, os
NOMUSIC=os.environ.get('NOMUSIC')=='1'   # music-ready version: foley only, piano left out for an in-app track
from timeline import T, SEGS, OUT, OUTDUR, COLD
SR=48000; DUR=13.0; LIB='../sfxlib/'
def load(path,a0=0.0,a1=None,flt=None):
    af=[]
    if path.startswith('sfx/'): af.append('equalizer=f=15600:t=q:w=30:g=-30')   # ElevenLabs stems carry a 15.6 kHz whistle
    if flt: af.append(flt)
    cmd=['ffmpeg','-v','error','-ss',str(a0)]+(['-to',str(a1)] if a1 else [])+['-i',path]+(['-af',','.join(af)] if af else [])+['-ac','2','-ar',str(SR),'-f','f32le','-']
    return np.frombuffer(subprocess.run(cmd,capture_output=True).stdout,np.float32).reshape(-1,2).copy()
out=np.zeros((int(SR*OUTDUR)+SR*12,2),np.float32)   # events, output time
bed=np.zeros((int(SR*DUR)+SR*12,2),np.float32)   # beds, body time
def I(b): return int(round(T(b)*SR))
def db(x): return 10**(x/20)
def put(a,t,g_db=0.0,fade_in=0.0,fade_out=0.0,peak_norm=True,bus=None,at=None):
    a=a.copy()
    if peak_norm: a/=np.abs(a).max()+1e-9
    a*=db(g_db)
    if fade_in: k=int(fade_in*SR); a[:k]*=np.linspace(0,1,k)[:,None]
    if fade_out: k=min(len(a),int(fade_out*SR)); a[-k:]*=np.linspace(1,0,k)[:,None]
    o=out if bus is None else bus
    i=int(round(t*SR)) if bus is not None else (int(round(at*SR)) if at is not None else I(t))
    if i<0: a=a[-i:]; i=0
    o[i:i+len(a)]+=a[:len(o)-i]
W5=LIB+'175183__tomlija__5-everyday-whooshes.wav'; WC=LIB+'649445__audiopapkin__cinematic-woosh-sfx-015.wav'
PK=[3.65,7.9,12.6,17.4,21.4]
def whoosh(i,cut,g,semi=0):
    a=load(W5,PK[i]-0.45,PK[i]+0.55,f'asetrate={SR}*{2**(semi/12):.4f},aresample={SR}' if semi else None); put(a,0,g,fade_in=0.05,fade_out=0.25,at=T(cut)-0.45)
# room tone: high-passed, quiet, with a true-silence dip before the door beat
room=load('sfx/room.mp3',flt='highpass=f=120'); room/=np.abs(room).max()+1e-9; room*=db(-34)
env=np.ones(len(room)); a,b=int(4.62*SR),int(5.0*SR); env[a:b]=db(-26); room*=env[:,None]; bed[:len(room)]+=room
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
    a=load(f'sfx/life_{nm}.mp3',flt='alimiter=limit=0.8'); o0,o1=T(t0),T(t1); n=int((o1-o0+0.15)*SR)
    if len(a)<n: a=np.concatenate([a,a[::-1]])            # mirror-extend so the layer holds past its cut
    put(a[:n],0,g,fade_in=0.08,fade_out=0.15,at=o0)
    b=a[:int((o1-o0-0.45)*SR)]; put(b,0,g-4,fade_in=0.1,fade_out=0.2,at=o0+0.6)   # second staggered pass fills the panel's tail            # clock through the split; hard stop 4.6

# the waiting piano (first note lands on the 5.0 cut), ducked under the jingle
pia=load('sfx/piano.mp3'); pia/=np.abs(pia).max(); pia*=db(-8)
d=np.ones(len(pia)); s0,s1=int((6.15-4.75)*SR),int((7.3-4.75)*SR); d[s0:s1]=db(-6); pia*=d[:,None]
k=int(3.5*SR); seg=int((8.6-4.75)*SR); pia[seg-k//8:seg]*=np.linspace(1,0.35,k//8)[:,None]; pia[seg:]*=0.35
p0,p1=int((5.0-4.75)*SR),int((5.8-4.75)*SR); pf=int(0.15*SR); e=np.full(p1-p0,db(-3)); e[-pf:]=np.linspace(db(-3),1,pf); pia[p0:p1]*=e[:,None]   # first 0.8 s of the waiting piano under the reunion
put(pia*(0 if NOMUSIC else 1),4.75,0,peak_norm=False,bus=bed)
put(load('sfx/jingle.mp3'),6.32,-7)
put(load('sfx/whine.mp3'),6.95,-9)
put(load('sfx/door_open.mp3',0.45,1.2),7.36,-5)
put(load('sfx/barks.mp3'),7.72,-4)
POST=[]   # whole-bus envelopes, applied after the beds are warped onto the output clock
i0,i1=I(7.95),I(8.08); out[i0:i1]*=np.linspace(1,db(-5),i1-i0)[:,None]   # pre-duck so the hit has room
put(load('sfx/thump2.mp3',flt='alimiter=limit=0.7:attack=1:release=40'),8.06,-5)
put(load('sfx/thump2.mp3',flt='highpass=f=150,lowpass=f=1800,alimiter=limit=0.7:attack=1:release=40'),8.015,-4)
kt=np.arange(int(0.22*SR))/SR; kick=np.sin(2*np.pi*(58*kt+40*(1-np.exp(-kt/0.03))*0.03))*np.exp(-kt/0.07); put(np.stack([kick,kick],1).astype(np.float32),8.07,-7)
put(load('sfx/laugh.mp3'),8.22,-8)
# reunion: warm G major chord on the cut, with a room tail so it rings to the end
put(load('sfx/reunion_piano.mp3',0,4.6),8.58,-90 if NOMUSIC else 2,fade_out=1.0)
nz=load('sfx/nuzzle.mp3',flt='acompressor=threshold=-30dB:ratio=4:attack=5:release=80'); nz=np.concatenate([nz[:int(2.3*SR)],nz[int(2.7*SR):]])
put(nz,9.05,-12,fade_in=0.1,fade_out=0.4)
put(load('sfx/jingle.mp3',0.0,0.4),9.8,-24,fade_out=0.15)
put(load('sfx/whine.mp3'),10.6,-14)
put(load('sfx/nuzzle.mp3',0.2,1.6),11.6,-16,fade_in=0.1,fade_out=0.3)
# ---- warp the beds onto the output clock and sum
def stretch(x,s_):
    if s_>=0.999: return x
    x.astype(np.float32).tofile('output/_st.f32')
    r=subprocess.run(['ffmpeg','-v','error','-f','f32le','-ar',str(SR),'-ac','2','-i','output/_st.f32','-af',f'rubberband=tempo={s_}:transients=smooth:window=long','-f','f32le','-'],capture_output=True,check=True).stdout
    return np.frombuffer(r,np.float32).reshape(-1,2).copy()
PAD=int(0.012*SR)
for (b0,b1,s_),o0 in zip(SEGS,OUT):
    x=stretch(bed[max(0,int(b0*SR)-PAD):int(b1*SR)+PAD],s_); r_=np.linspace(0,1,PAD)[:,None]; x[:PAD]*=r_; x[-PAD:]*=r_[::-1]
    i=int(round(o0*SR))-PAD; i0_=max(i,0); out[i0_:i+len(x)]+=x[i0_-i:len(out)-i]
DUR=OUTDUR
i0=I(4.6); n0=int(0.02*SR); out[i0:i0+n0]*=np.linspace(1,0.4,n0)[:,None]; out[i0+n0:I(5.0)]*=0.4      # clock through the split; hard stop under the bike
r0,r1=I(8.6),I(9.8); rf=int(0.3*SR); env=np.full(r1-r0,db(6.0)); env[-rf:]=np.linspace(db(6.0),1,rf); out[r0:r1]*=env[:,None]   # reunion bus lift
g0,g1=I(4.62),I(4.98); nf=int(0.02*SR)
out[g0:g0+nf]*=np.linspace(1,db(-26),nf)[:,None]; out[g0+nf:g1-nf]*=db(-26); out[g1-nf:g1]*=np.linspace(db(-26),1,nf)[:,None]       # the silence beat before the door close-up
mix=out[:int(SR*DUR)]
j0,j1=I(6.1),I(6.5); jf=int(0.05*SR); e=np.full(j1-j0,db(-3)); e[:jf]=np.linspace(1,db(-3),jf); e[-jf:]=np.linspace(db(-3),1,jf); mix[j0:j1]*=e[:,None]   # jingle beat under the reunion
k=int(0.4*SR); mix[-k:]*=np.linspace(1,0.75,k)[:,None]
# payoff-first cold open (0.6 s): the leap itself (bark, impact) lifted from the story mix, piano downbeat, rewind whoosh
COLD=0.5; nc=int(COLD*SR); pre=np.zeros((nc,2),np.float32)
def pput(x,t,g,fo=0.0,norm=True):
    x=(x/(np.abs(x).max()+1e-9) if norm else x)*db(g); i=int(t*SR); x=x[:nc-i].copy()
    if fo: k=min(len(x),int(fo*SR)); x[-k:]*=np.linspace(1,0,k)[:,None]
    pre[i:i+len(x)]+=x
pput(load('sfx/barks.mp3',0,0.35),0.0,-9,0.1)
pput(load('sfx/reunion_piano.mp3',0.0,0.6),0.0,-90 if NOMUSIC else -4,0.15)
pput(load('sfx/laugh.mp3',0,0.5),0.05,-11,0.12)
rw=load(WC,2.3,3.0)[::-1]; pput(rw[-int(0.3*SR):],0.22,-9)
nx=int(0.012*SR); body=mix[nc-nx:].copy(); r_=np.linspace(0,1,nx)[:,None]
mix=np.concatenate([pre[:-nx],pre[-nx:]*(1-r_)+body[:nx]*r_,body[nx:]])[:int(SR*DUR)]
j=load('sfx/jingle.mp3',0.0,0.3); j=j/(np.abs(j).max()+1e-9)*db(-8); i=int((T(1.03)-0.09)*SR); mix[i:i+len(j)]+=j[:len(mix)-i]   # tag jingle on the lie-down punch-in
mix.astype(np.float32).tofile('output/mix.f32')
# two-pass linear loudnorm
m=subprocess.run(['ffmpeg','-hide_banner','-f','f32le','-ar',str(SR),'-ac','2','-i','output/mix.f32','-af','acompressor=threshold=-18dB:ratio=2:attack=10:release=150,loudnorm=I=-14:TP=-2.5:LRA=20:print_format=json','-f','null','-'],capture_output=True,text=True).stderr
j=json.loads(m[m.rindex('{'):m.rindex('}')+1])
af=(f"acompressor=threshold=-18dB:ratio=2:attack=10:release=150,loudnorm=I=-14:TP=-2.5:LRA=20:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(SR),'-ac','2','-i','output/mix.f32','-af',af,'-ar',str(SR),'output/mix.wav'],check=True)
print('mix ok', j['input_i'], j['normalization_type'] if 'normalization_type' in j else '')
# post-normalisation emphasis (after the bus compressor): reunion is the loudest beat, the head-lift sits under it
subprocess.run(['ffmpeg','-v','error','-y','-i','output/mix.wav','-af',
  f"volume='if(between(t,{T(8.55):.3f},{T(9.9):.3f}),1.4,if(between(t,{T(6.0):.3f},{T(6.4):.3f}),0.79,1))':eval=frame,alimiter=limit=0.8:attack=2:release=60:level=false",
  '-ar',str(SR),'output/mix_post.wav'],check=True)
import os; os.replace('output/mix_post.wav','output/mix.wav')
