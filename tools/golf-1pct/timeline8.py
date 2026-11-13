# v8 (13 s): Teja's pacing. Miss 1 lands with the other lanes, then the 1% fires with no pause, each swing
# quicker than the last up to miss 32; misses 33 and 34 slow right down as lip-outs; then v7's dark finale.
# Only the 1% lane is re-rendered; the 93%/6% lanes reuse v6 renders; the finale reuses v7's z-renders.
import json, math, sys, importlib.util, os
OUT,V6,V7=sys.argv[1],sys.argv[2],sys.argv[3]
sys.argv=[sys.argv[0],OUT+'/_t5']; os.makedirs(OUT+'/_t5',exist_ok=True)
spec=importlib.util.spec_from_file_location('t5','timeline5.py'); t5=importlib.util.module_from_spec(spec); spec.loader.exec_module(t5)
FPS=30; FIN=8.0
v7f=json.load(open(f'{V7}/frames.json')); c7=json.load(open(f'{V7}/cues.json')); c6=json.load(open(f'{V6}/cues.json'))
# schedule
imp=[t5.IMP0]; t=1.22
for k in range(31): imp.append(t); t+=0.062+0.40*math.exp(-k/4.2)
imp+=[imp[-1]+0.7, imp[-1]+0.7+0.95]
T1=[1.25]+[max(0.40,1.0*0.9**k) for k in range(1,32)]+[1.0,1.1]
print("last lands",imp[33]+T1[33])
def lane1(t):
    whites=[]; misses=[]; n=0
    for k in range(34):
        ti=imp[k]
        if t<ti: break
        p,done=t5.path(t,ti,T1[k],t5.pts[k],lip=k>=26)
        if done: n+=1; age=t-(ti+T1[k]); misses.append([p[0],p[1],1+0.45*math.exp(-age*8)*(age<0.5)])
        else: whites.append([p[0],p[1]])
    ang=t5.swing(t,imp[0],1.0)
    for k in range(1,34):
        gap=imp[k]-imp[k-1]; ang=ang or t5.swing(t,imp[k],min(1.0,gap/0.95) if k<32 else 0.9)
    st={'club':{'angle':ang},'misses':misses,'gold':0,'flag':1,'seed':3,'whites':whites}
    if not whites: st['ball']=[t5.TEE[0],t5.TEE[1],t5.BR]
    else: st['noBall']=True
    return st,n
# 93%/6% lanes: v6 clock unchanged to 2.8 s, then stretched slightly so the last 93% flinch lands
def old(t): return t if t<2.8 else 2.8+(t-2.8)*(8.2-2.8)/(FIN-2.8)
def new(o): return o if o<2.8 else 2.8+(o-2.8)*(FIN-2.8)/(8.2-2.8)
frames=[]; jobs=[]
for fi,F7 in enumerate(v7f):
    t=fi/FPS
    if t>=FIN: frames.append(F7); continue
    st,n=t5.lane1(0); st,n=lane1(t)
    y=t5.ball_y(t,t5.DROPS['r1'])
    if t<0.5 and t<imp[0]:
        if y is None: st['noBall']=True; st.pop('ball',None)
        else: st['ball']=[t5.TEE[0],t5.TEE[1],y]; st.pop('noBall',None)
    y0,y1,yc=t5.ROWS['r1']; st['cam']={**t5.CAM,'yc':yc}
    name=f'p{fi:04d}_r1'; jobs.append({'name':name,'lane':st,'t':t,'w':1080,'h':y1-y0})
    of=min(int(round(old(t)*FPS)),len(v7f)*3)
    frames.append({'i':fi,'t':t,'tn':t,'mode':'rows','n':n,'rows':{'r93':f'k{of:04d}_r93','r6':f'k{of:04d}_r6','r1':name}})
json.dump(jobs,open(f'{OUT}/jobs.json','w')); json.dump(frames,open(f'{OUT}/frames.json','w'))
cues={**c7,'imp0':imp[0],'imp1':imp,'T1':T1,'lips':imp[32:],'hes':[new(x) for x in c6['hes']],
      'fall':c6['fall'],'miss6_stop':c6['miss6_stop']}
json.dump(cues,open(f'{OUT}/cues.json','w'))
print(len(frames),'frames',len(jobs),'renders; miss32 at',round(imp[31],2),'lips',[round(x,2) for x in imp[32:]],'last lands',round(imp[33]+T1[33],2))
print('gaps',[round(b-a,2) for a,b in zip(imp,imp[1:])])
