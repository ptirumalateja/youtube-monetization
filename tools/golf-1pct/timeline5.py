# v6: one side view from frame 0, 1% lane is the hero. Balls drop in (0-0.4 s), all three lift together, impact 0.7 s,
# 93% freezes, 6% misses once and drops the club, 1% sprints, then slows into near-misses (lip-outs) that build tension,
# then the final putt drops. Bigger balls, lane pulled in from the frame edges.
import json, math, random, sys
OUT=sys.argv[1]
FPS=30
CX,HX,BR,CUP=-1.22,1.22,0.072,0.15
TEE=(CX+0.17,0.0)
ROWS={'r93':(0,940,805),'r6':(940,1270,200),'r1':(1270,1920,195)}
CAM={'pos':[0,0.6,3.95],'look':[0,0.5,0],'fov':38}
def cl(x,a=0,b=1): return max(a,min(b,x))
def ss(a,b,x): u=cl((x-a)/(b-a)); return u*u*(3-2*u)
def lerp(a,b,u): return a+(b-a)*u

# 34 miss spots: far/wide early, hugging the cup at the end
random.seed(11); far=[]
while len(far)<26:
    a=random.uniform(0,2*math.pi); r=0.45+abs(random.gauss(0,0.4))
    x=HX+r*math.cos(a)*1.2; z=r*math.sin(a)*0.75
    if x>HX+0.75 or x<HX-1.15 or abs(z)>0.6: continue
    if all((x-p[0])**2+(z-p[1])**2>(2.0*BR)**2 for p in far): far.append((x,z))
far.sort(key=lambda p:-math.hypot(p[0]-HX,p[1]))
near=[]   # lip-outs: stop just past the cup, closer each time
for k in range(8):
    r=CUP+BR*1.1+0.30*(1-k/7)**1.3+0.02; a=[0.5,-0.6,0.35,-0.4,0.75,-0.25,0.15,-0.1][k]
    p=(HX+r*math.cos(a),r*math.sin(a))
    near.append(p)
pts=far+near
MISS6=(0.55,0.2)

def swing(t,ti,s=1.0):
    a0=ti-0.45*s; top=ti-0.13*s
    if t<a0 or t>ti+0.6*s: return 0.0
    if t<top: return 0.8*ss(a0,top,t)
    if t<ti: u=(t-top)/(ti-top); return 0.8*(1-u*u)
    if t<ti+0.13*s: u=(t-ti)/(0.13*s); return -0.75*math.sin(u*math.pi/2)
    return -0.75*(1-ss(ti+0.13*s,ti+0.6*s,t))
def path(t,ti,T,target,lip=False):
    u=cl((t-ti)/T); e=1-(1-u)**2
    if not lip: return (lerp(TEE[0],target[0],e),lerp(TEE[1],target[1],e)), u>=1
    # lip-out: quadratic Bezier that runs over the cup's edge and out the other side
    side=1 if target[1]>=0 else -1; P1=(HX-0.05,side*(CUP*0.55))
    x=(1-e)**2*TEE[0]+2*(1-e)*e*P1[0]+e*e*target[0]; z=(1-e)**2*TEE[1]+2*(1-e)*e*P1[1]+e*e*target[1]
    return (x,z),u>=1

DROPS={'r93':0.0,'r6':0.05,'r1':0.10}; H0=0.34; G=14.0
def ball_y(t,t0):
    if t<t0: return None
    T=math.sqrt(2*H0/G); u=t-t0
    if u<T: return BR+H0-0.5*G*u*u
    u-=T; v=G*T*0.15; tb=2*v/G
    return BR+v*u-0.5*G*u*u if u<tb else BR

IMP0=0.70
# schedule: miss 1 at IMP0, misses 2-26 sprint (accelerating), misses 27-34 lip-outs (slower, tense), final putt
imp=[IMP0]; tt=2.3; d=0.55
for k in range(25): imp.append(tt); tt+=max(0.1,d); d*=0.85
sc=(5.7-2.3)/(imp[-1]-2.3); imp=[imp[0]]+[2.3+(x-2.3)*sc for x in imp[1:]]
lipT=[6.25+0.62*k for k in range(8)]           # 6.25 ... 10.59
imp+=lipT
T1=[1.25]+[max(0.42,1.1*0.92**k) for k in range(1,26)]+[1.0]*8
FINAL_IMP=11.45; RIM_T=12.6; DROP_T=12.95; DUR=15.6
NF=int(round(DUR*FPS))

def hesitate(t):
    a=0.0
    for t0,peak,hold in ((0.25,0.6,0.6),(3.4,0.32,0.6),(7.6,0.16,0.5)):
        up=t0+0.3; dn=up+hold
        if t0<=t<up: a=peak*ss(t0,up,t)
        elif up<=t<dn: a=peak+0.025*math.sin(t*55)*(1-(t-up)/hold)
        elif dn<=t<dn+0.5: a=peak*(1-ss(dn,dn+0.5,t))
    return a

def lane1(t):
    whites=[]; misses=[]; n=0; lastlip=None
    for k in range(34):
        ti=imp[k]
        if t<ti: break
        p,done=path(t,ti,T1[k],pts[k],lip=k>=26)
        if done: n+=1; age=t-(ti+T1[k]); misses.append([p[0],p[1],1+0.45*math.exp(-age*8)*(age<0.5)])
        else: whites.append([p[0],p[1]])
    ang=swing(t,IMP0,1.0)
    for k in range(1,34):
        s=min(1.0,(imp[k+1]-imp[k] if k<33 else 0.6)/0.95) if k<26 else 0.62
        ang=ang or swing(t,imp[k],s)
    ang=ang or swing(t,FINAL_IMP,1.25)
    ball=None; gold=0; y=BR
    if t>=FINAL_IMP:
        if t<RIM_T:
            u=cl((t-FINAL_IMP)/(RIM_T-FINAL_IMP)); e=1-(1-u)**1.7; rim=(HX-CUP-0.004,0.03)
            ball=(lerp(TEE[0],rim[0],e),lerp(TEE[1],rim[1],e))
        elif t<DROP_T:
            u=(t-RIM_T)/(DROP_T-RIM_T); a=math.pi+0.25+u*1.9*(1-0.3*u)
            ball=(HX+(CUP+0.004)*math.cos(a),-(CUP+0.004)*math.sin(a))
        else:
            u=cl((t-DROP_T)/0.14); ball=(lerp(HX-0.05,HX,u),0); y=BR-0.24*u*u; gold=ss(DROP_T,DROP_T+0.25,t)
    elif not whites: ball=TEE
    st={'club':{'angle':ang},'misses':misses,'gold':gold,'flag':1+1.2*math.exp(-max(0,t-DROP_T)*3)*(t>DROP_T),'seed':3,'whites':whites}
    if ball is None: st['noBall']=True
    else: st['ball']=[ball[0],ball[1],y]
    return st,n
def lane6(t):
    st={'club':{'angle':swing(t,IMP0,1.0)},'seed':2,'flag':0.6}
    if t>=IMP0:
        p,done=path(t,IMP0,T1[0],MISS6)
        if done: st['noBall']=True; age=t-IMP0-T1[0]; st['misses']=[[p[0],p[1],1+0.45*math.exp(-age*8)*(age<0.5)]]
        else: st['ball']=[p[0],p[1]]
    else: st['ball']=list(TEE)
    if t>=2.4: st['club']={'fall':ss(2.4,2.75,t)**1.6 if t<2.75 else 1}
    return st
def lane93(t): return {'club':{'angle':hesitate(t)},'ball':list(TEE),'seed':1,'flag':0.45}

frames=[]; jobs=[]
for fi in range(NF):
    t=fi/FPS; l1,n=lane1(t); F={'t':t,'i':fi,'rows':{},'n':n}
    for k,st in (('r93',lane93(t)),('r6',lane6(t)),('r1',l1)):
        y=ball_y(t,DROPS[k])
        if t<0.5:
            if y is None: st['noBall']=True; st.pop('ball',None)
            elif 'ball' in st and t<IMP0: st['ball']=[TEE[0],TEE[1],y]
        y0,y1,yc=ROWS[k]; st['cam']={**CAM,'yc':yc}
        name=f'k{fi:04d}_{k}'; jobs.append({'name':name,'lane':st,'t':t,'w':1080,'h':y1-y0}); F['rows'][k]=name
    frames.append(F)
json.dump(jobs,open(f'{OUT}/jobs.json','w')); json.dump(frames,open(f'{OUT}/frames.json','w'))
json.dump({'imp0':IMP0,'imp1':imp,'T1':T1,'lips':lipT,'final_imp':FINAL_IMP,'rim':RIM_T,'drop':DROP_T,'miss6_stop':IMP0+T1[0],'fall':2.75,
  'hes':[0.25,3.4,7.6],'drops':[DROPS[k]+math.sqrt(2*H0/G) for k in ('r93','r6','r1')],'dur':DUR},open(f'{OUT}/cues.json','w'))
print(NF,'frames',len(jobs),'renders; sprint ends',round(imp[25],2),'lips',[round(x,2) for x in lipT])
