# v3 = v2 with a 0.4 s opening: the three balls drop onto their tees one by one (top, middle, bottom), clubs start lifting,
# then the v2 reel plays unchanged. New frames 0-11 are rendered (h*), frames 12+ reuse v2's renders (g*).
import json, math, sys, importlib.util
OUT=sys.argv[1]; V2=sys.argv[2]
sys.argv=[sys.argv[0],V2]
spec=importlib.util.spec_from_file_location('t2','timeline2.py'); t2=importlib.util.module_from_spec(spec); spec.loader.exec_module(t2)
SHIFT=12; FPS=30
v2f=json.load(open(f'{V2}/frames.json')); cues=json.load(open(f'{V2}/cues.json'))
DROPS={'r93':0.0,'r6':0.05,'r1':0.10}   # new-time start of each ball's fall
H0=0.34; G=14.0
def ball_y(tn,t0):
    """fall from H0 with one small bounce; None before it appears"""
    if tn<t0: return None
    T=math.sqrt(2*H0/G); u=tn-t0
    if u<T: return t2.BR+H0-0.5*G*u*u
    u-=T; v=G*T*0.15; tb=2*v/G
    if u<tb: return t2.BR+v*u-0.5*G*u*u
    return t2.BR
jobs=[]; frames=[]
for fi in range(SHIFT):
    tn=fi/FPS; told=tn-SHIFT/FPS; F={'t':told,'i':fi,'rows':{},'n':0}
    for k,st in (('r93',t2.lane93(told)),('r6',t2.lane6(told)),('r1',t2.lane1(told)[0])):
        y=ball_y(tn,DROPS[k])
        st.pop('whites',None)
        if y is None: st['noBall']=True; st.pop('ball',None)
        else: st.pop('noBall',None); st['ball']=[t2.TEE[0],t2.TEE[1],y]
        y0,y1,yc=t2.ROWS[k]; st['cam']={**t2.CAM,'yc':yc}
        name=f'h{fi:04d}_{k}'; jobs.append({'name':name,'lane':st,'t':told,'w':1080,'h':y1-y0}); F['rows'][k]=name
    frames.append(F)
for F in v2f: frames.append({**F,'i':F['i']+SHIFT})
json.dump(jobs,open(f'{OUT}/jobs.json','w')); json.dump(frames,open(f'{OUT}/frames.json','w'))
c=dict(cues); c['shift']=SHIFT/FPS; c['drops']=[SHIFT/FPS*0+DROPS[k]+math.sqrt(2*H0/G) for k in ('r93','r6','r1')]
json.dump(c,open(f'{OUT}/cues.json','w')); print(len(frames),'frames; new renders',len(jobs),'landings',c['drops'])
