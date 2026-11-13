# v7 (~13 s): v6's rows time-warped (sprint 1.5x, lip-outs 1.5x), then a new finale: the lane goes dark,
# the camera pushes in on the 1% hole, one final putt rolls in, gold, "THE ONLY DIFFERENCE? THEY KEPT GOING."
import json, math, sys, importlib.util
OUT,V6=sys.argv[1],sys.argv[2]
sys.argv=[sys.argv[0],OUT+'/_t5']
import os; os.makedirs(OUT+'/_t5',exist_ok=True)
spec=importlib.util.spec_from_file_location('t5','timeline5.py'); t5=importlib.util.module_from_spec(spec); spec.loader.exec_module(t5)
FPS=30; DUR=13.0; NF=int(round(DUR*FPS)); FIN=8.0
v6=json.load(open(f'{V6}/frames.json')); c6=json.load(open(f'{V6}/cues.json'))
WARP=[(0,0),(2.3,2.3),(4.7,5.9),(FIN,10.85)]       # (new, old)
def warp(tn):
    for (a,A),(b,B) in zip(WARP,WARP[1:]):
        if tn<=b: return A+(B-A)*(tn-a)/(b-a)
    return WARP[-1][1]
def unwarp(to):
    for (a,A),(b,B) in zip(WARP,WARP[1:]):
        if to<=B: return a+(b-a)*(to-A)/(B-A)
    return None
def rate(to):
    for (a,A),(b,B) in zip(WARP,WARP[1:]):
        if to<=B: return (b-a)/(B-A)
    return 1
IMP=8.45; RIM=9.55; DROP=9.85
CA={'pos':[0,0.75,4.3],'look':[0,0.35,0],'fov':42}; CB={'pos':[t5.HX-0.95,0.36,1.05],'look':[t5.HX,0.04,0],'fov':32}
def cam(t):
    u=t5.ss(FIN,DROP,t)*0.92+0.08*t5.cl((t-DROP)/3.2)
    return {k:([CA[k][i]+(CB[k][i]-CA[k][i])*u for i in range(3)] if k!='fov' else CA[k]+(CB[k]-CA[k])*u) for k in CA}
frames=[]; jobs=[]
for fi in range(NF):
    t=fi/FPS
    if t<FIN:
        to=warp(t); src=v6[min(len(v6)-1,int(round(to*FPS)))]
        frames.append({**src,'i':fi,'t':to,'tn':t,'mode':'rows'})
    else:
        st,_=t5.lane1(10.85); st['whites']=[]
        st['misses']=[[p[0],p[1],1] for p in t5.pts]
        st['club']={'angle':t5.swing(t,IMP,1.15)}
        if t<IMP: st['ball']=[t5.TEE[0],t5.TEE[1],t5.BR]
        elif t<RIM:
            u=t5.cl((t-IMP)/(RIM-IMP)); e=1-(1-u)**1.8; rim=(t5.HX-t5.CUP-0.004,0.03)
            st['ball']=[t5.lerp(t5.TEE[0],rim[0],e),t5.lerp(t5.TEE[1],rim[1],e),t5.BR]
        elif t<DROP:
            u=(t-RIM)/(DROP-RIM); a=math.pi+0.25+u*1.9*(1-0.3*u)
            st['ball']=[t5.HX+(t5.CUP+0.004)*math.cos(a),-(t5.CUP+0.004)*math.sin(a),t5.BR]
        else:
            u=t5.cl((t-DROP)/0.14); st['ball']=[t5.lerp(t5.HX-0.05,t5.HX,u),0,t5.BR-0.24*u*u]
        st.pop('noBall',None)
        st['gold']=t5.ss(DROP,DROP+0.3,t); st['flag']=1+1.2*math.exp(-max(0,t-DROP)*3)*(t>DROP)
        st['dark']=t5.ss(FIN,FIN+0.45,t)*(1-0.3*t5.ss(DROP,DROP+0.6,t)); st['cam']=cam(t)
        name=f'z{fi:04d}_full'; jobs.append({'name':name,'lane':st,'t':t,'w':1080,'h':1920})
        frames.append({'i':fi,'t':t,'tn':t,'mode':'fin','full':name,'n':34})
json.dump(jobs,open(f'{OUT}/jobs.json','w')); json.dump(frames,open(f'{OUT}/frames.json','w'))
# audio cues on the new clock
imp=[]; T1=[]
for x,T in zip(c6['imp1'],c6['T1']):
    if x<10.85: imp.append(unwarp(x)); T1.append(T*rate(x))
lips=[unwarp(x) for x in c6['lips'] if x<10.85]
cues={**c6,'imp1':imp,'T1':T1,'lips':lips,'final_imp':IMP,'rim':RIM,'drop':DROP,'dur':DUR,'fin':FIN,
      'hes':[unwarp(x) for x in c6['hes']],'fall':unwarp(c6['fall']),'miss6_stop':unwarp(c6['miss6_stop'])}
json.dump(cues,open(f'{OUT}/cues.json','w'))
print(NF,'frames',len(jobs),'new renders; strikes',len(imp),'lips',[round(x,2) for x in lips])
