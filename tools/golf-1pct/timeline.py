# Full-reel timeline -> render jobs (jobs.json) and compose spec (frames.json).
import json, math, random, sys
OUT=sys.argv[1]
FPS=30; DUR=23.5; NF=int(DUR*FPS)
CX,HX,BR,CUP=-1.42,1.42,0.048,0.115
TEE=(CX+0.11,0.0)
ROWS={'r93':(0,720),'r6':(720,1310),'r1':(1310,1920)}
CAM93={'pos':[0,0.6,4.25],'look':[0,0.82,0],'fov':33}
CAMROW={'pos':[0,0.6,3.95],'look':[0,0.5,0],'fov':30}
HOOKCAM={'pos':[HX-1.45,0.78,1.55],'look':[HX,0.06,0],'fov':24}
WIDE={'pos':[0,1.3,5.6],'look':[0,0.3,0],'fov':50}
LANE1CAM={'pos':[CX-1.05,0.62,0.32],'look':[HX-0.2,0.0,0.0],'fov':40}

def cl(x,a=0,b=1): return max(a,min(b,x))
def ss(a,b,x): u=cl((x-a)/(b-a)); return u*u*(3-2*u)
def lerp(a,b,u): return a+(b-a)*u
def lv(a,b,u): return [lerp(x,y,u) for x,y in zip(a,b)]
def lcam(A,B,u): return {'pos':lv(A['pos'],B['pos'],u),'look':lv(A['look'],B['look'],u),'fov':lerp(A['fov'],B['fov'],u)}
def push(C,k,dz=0.35):
    c=json.loads(json.dumps(C)); d=[c['pos'][i]-c['look'][i] for i in range(3)]; L=math.sqrt(sum(x*x for x in d))
    c['pos']=[c['pos'][i]-d[i]/L*dz*k for i in range(3)]; return c

# miss spots for the 1% row: far/wide first, closer to the hole later (they get better)
random.seed(7)
pts=[]
while len(pts)<34:
    a=random.uniform(0,2*math.pi); r=0.3+abs(random.gauss(0,0.45))
    x=HX+r*math.cos(a)*1.25; z=r*math.sin(a)*0.8
    if x>HX+0.9 or x<HX-1.25 or abs(z)>0.9: continue
    if all((x-p[0])**2+(z-p[1])**2>(2.1*BR)**2 for p in pts): pts.append((x,z))
pts.sort(key=lambda p:-math.hypot(p[0]-HX,p[1]))
MISS6=(0.82,0.2)

def swing(t,ti,s=1.0):
    """club angle for a swing with impact at ti; s scales the tempo"""
    a0=ti-0.45*s; top=ti-0.13*s
    if t<a0 or t>ti+0.6*s: return 0.0
    if t<top: return 0.8*ss(a0,top,t)
    if t<ti: u=(t-top)/(ti-top); return 0.8*(1-u*u)
    if t<ti+0.13*s: u=(t-ti)/(0.13*s); return -0.75*math.sin(u*math.pi/2)
    return -0.75*(1-ss(ti+0.13*s,ti+0.6*s,t))
def roll(t,ti,T,target):
    u=cl((t-ti)/T); e=1-(1-u)**2
    return (lerp(TEE[0],target[0],e),lerp(TEE[1],target[1],e)), u>=1

# 1% schedule
imp=[]; tt=11.35; d=0.95
for k in range(34):
    imp.append(tt); tt+=max(0.11,d); d*=0.84
scale=(16.15-11.35)/(imp[-1]-11.35); imp=[11.35+(x-11.35)*scale for x in imp]
ints=[imp[k+1]-imp[k] for k in range(33)]+[0.5]
T1=[max(0.38,1.35*0.9**k) for k in range(34)]
FINAL_IMP=16.75; RIM_T=17.75; DROP_T=17.98

def lane1(t,final=True):
    """state of the 1% lane at time t (segment D/E)"""
    whites=[]; misses=[]; n=0
    for k in range(34):
        ti=imp[k]
        if t<ti: break
        p,done=roll(t,ti,T1[k],pts[k])
        if done:
            n+=1; age=t-(ti+T1[k]); misses.append([p[0],p[1],1+0.35*math.exp(-age*9)*(age<0.4)])
        else: whites.append([p[0],p[1]])
    ang=0.0
    for k in range(34):
        s=min(1.0,ints[k]/0.95) if k<33 else 0.6
        ang=ang or swing(t,imp[k],s)
    ang=ang or swing(t,FINAL_IMP,1.25)
    ball=None; gold=0; y=BR
    if t>=FINAL_IMP:
        if t<RIM_T:
            u=cl((t-FINAL_IMP)/(RIM_T-FINAL_IMP)); e=1-(1-u)**1.7
            rim=(HX-CUP-0.004,0.03)
            ball=(lerp(TEE[0],rim[0],e),lerp(TEE[1],rim[1],e))
        elif t<DROP_T:
            u=(t-RIM_T)/(DROP_T-RIM_T); a=math.pi+0.25+u*1.9*(1-0.3*u)
            ball=(HX+(CUP+0.004)*math.cos(a),(CUP+0.004)*math.sin(a)*-1)
        else:
            u=cl((t-DROP_T)/0.14); ball=(lerp(HX-0.05,HX,u),0); y=BR-0.16*u*u
            gold=ss(DROP_T,DROP_T+0.25,t)
    elif not whites and (n<34): ball=TEE  # waiting on the tee
    st={'club':{'angle':ang},'misses':misses,'gold':gold,'flag':1+1.2*math.exp(-max(0,t-DROP_T)*3)*(t>DROP_T),'seed':3}
    if ball is None: st['noBall']=True
    else: st['ball']=[ball[0],ball[1],y]
    st['whites']=whites; return st,n

def hook_state(t):
    """frame-0 payoff: ball rolls the last bit and drops (0.25-0.4 s)"""
    misses=[[p[0],p[1],1] for p in pts]
    st={'club':{'angle':0},'misses':misses,'seed':3,'flag':1}
    start=(HX-0.26,0.05)
    if t<0.25: u=t/0.25; e=1-(1-u)**1.4; st['ball']=[lerp(start[0],HX-0.06,e),lerp(start[1],0.01,e),BR]
    else: u=cl((t-0.25)/0.15); st['ball']=[lerp(HX-0.06,HX,u),0,BR-0.16*u*u]
    st['gold']=ss(0.3,0.55,t)
    st['flag']=1+1.0*math.exp(-max(0,t-0.4)*3)*(t>0.4)
    return st

frames=[]; jobs=[]
def J(fi,slot,lane,t,w,h):
    name=f'f{fi:04d}_{slot}'; jobs.append({'name':name,'lane':lane,'t':t,'w':w,'h':h}); return name

for fi in range(NF):
    t=fi/FPS; F={'t':t,'i':fi}
    if t<2.5:   # A hook
        st=hook_state(t); st['cam']=lcam(HOOKCAM,{**HOOKCAM,'fov':21},ss(0,2.5,t))
        F['full']=J(fi,'full',st,t,1080,1920); F['mode']='hook'
    elif t<3.1: # B rewind
        u=ss(2.5,3.1,t); st=hook_state(0.5)
        st['misses']=[]
        for k,p in enumerate(pts):
            uk=cl((u-(33-k)/34*0.45)/0.55); e=uk*uk
            st['misses'].append([lerp(p[0],TEE[0],e),lerp(p[1],TEE[1],e),1-e])
        st['ball']=[HX,0,lerp(BR-0.16,BR+0.02,u)] if u<0.5 else [lerp(HX,TEE[0],(u-0.5)*2),0,BR]
        st['gold']=1-u; st['cam']=lcam(HOOKCAM,WIDE,u)
        F['full']=J(fi,'full',st,t,1080,1920); F['mode']='rewind'
    elif t<11.0 or t>=18.9 and t<23.0:  # C/F rows
        closing=t>=18.9
        r93={'club':{'angle':0},'ball':[TEE[0],TEE[1]],'seed':1,'flag':0.45}
        r6={'club':{'angle':0},'ball':[TEE[0],TEE[1]],'seed':2,'flag':0.6}
        r1={'club':{'angle':0},'ball':[TEE[0],TEE[1]],'seed':3,'flag':1}
        if not closing:
            if t>=8.0:
                ti=8.45; r6['club']['angle']=swing(t,ti,1.0)
                if t>=ti:
                    p,done=roll(t,ti,1.5,MISS6)
                    if done: r6.pop('ball'); r6['noBall']=True; age=t-ti-1.5; r6['misses']=[[p[0],p[1],1+0.35*math.exp(-age*9)]]
                    else: r6['ball']=[p[0],p[1]]
                if t>=10.2: r6['club']={'fall':ss(10.2,10.55,t)**1.6 if t<10.55 else 1}
        else:
            r6={'club':{'fall':1},'noBall':True,'misses':[[MISS6[0],MISS6[1],1]],'seed':2,'flag':0.6}
            r1={'club':{'angle':0},'noBall':True,'misses':[[p[0],p[1],1] for p in pts],'gold':1,'seed':3,'flag':1}
        act=None if closing else ('r93' if 5.6<=t<8.0 else 'r6' if t>=8.0 else None)
        k93=ss(5.6,8.0,t) if not closing else 0
        r93['cam']=push(CAM93,k93,0.4)
        r6['cam']=push(CAMROW,ss(8.0,11.0,t) if not closing else 0,0.35)
        r1['cam']=push(CAMROW,ss(18.9,23,t)*0.5 if closing else 0,0.35)
        F['rows']={k:J(fi,k,v,t,1080,ROWS[k][1]-ROWS[k][0]) for k,v in (('r93',r93),('r6',r6),('r1',r1))}
        F['mode']='closing' if closing else 'rows'; F['act']=act
    elif t<17.35: # D 1% full frame
        st,n=lane1(t); st['cam']=lcam(LANE1CAM,{**LANE1CAM,'pos':[CX-0.55,0.52,0.26]},ss(11,17.35,t))
        F['full']=J(fi,'full',st,t,1080,1920); F['mode']='one'; F['n']=n
    elif t<18.9: # E close-up on the final putt
        st,n=lane1(t); st['cam']=lcam(HOOKCAM,{**HOOKCAM,'fov':20},ss(17.35,18.9,t))
        F['full']=J(fi,'full',st,t,1080,1920); F['mode']='final'; F['n']=n
    else:       # H loop dive back to frame 0
        u=ss(23.0,23.5,t); st=hook_state(0); st['gold']=0
        st['cam']=lcam(WIDE,HOOKCAM,u)
        F['full']=J(fi,'full',st,t,1080,1920); F['mode']='dive'
    frames.append(F)
json.dump(jobs,open(f'{OUT}/jobs.json','w')); json.dump(frames,open(f'{OUT}/frames.json','w'))
print(len(frames),'frames',len(jobs),'renders; 1% impacts',[round(x,2) for x in imp[:5]],'...',round(imp[-1],2))
json.dump({'imp1':imp,'T1':T1,'final_imp':FINAL_IMP,'rim':RIM_T,'drop':DROP_T},open(f'{OUT}/cues.json','w'))
