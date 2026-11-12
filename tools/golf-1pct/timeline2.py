# v2: one side view from frame 0. Three rows always on screen; all three swing together; 1% sprints in the same view.
import json, math, random, sys
OUT=sys.argv[1]
FPS=30; DUR=12.8; NF=int(round(DUR*FPS))
CX,HX,BR,CUP=-1.42,1.42,0.048,0.115
TEE=(CX+0.11,0.0)
# panels (global y): row1 holds the title in its sky; text stays inside y 300-1440
ROWS={'r93':(0,790,655),'r6':(790,1120,200),'r1':(1120,1920,195)}   # (y0, y1, yc = where the look point lands)
CAM={'pos':[0,0.6,3.95],'look':[0,0.5,0],'fov':38}
def cl(x,a=0,b=1): return max(a,min(b,x))
def ss(a,b,x): u=cl((x-a)/(b-a)); return u*u*(3-2*u)
def lerp(a,b,u): return a+(b-a)*u

random.seed(7); pts=[]
while len(pts)<34:
    a=random.uniform(0,2*math.pi); r=0.3+abs(random.gauss(0,0.45))
    x=HX+r*math.cos(a)*1.25; z=r*math.sin(a)*0.8
    if x>HX+0.9 or x<HX-1.25 or abs(z)>0.75: continue
    if all((x-p[0])**2+(z-p[1])**2>(2.1*BR)**2 for p in pts): pts.append((x,z))
pts.sort(key=lambda p:-math.hypot(p[0]-HX,p[1]))
MISS6=(0.78,0.22)

def swing(t,ti,s=1.0):
    a0=ti-0.45*s; top=ti-0.13*s
    if t<a0 or t>ti+0.6*s: return 0.0
    if t<top: return 0.8*ss(a0,top,t)
    if t<ti: u=(t-top)/(ti-top); return 0.8*(1-u*u)
    if t<ti+0.13*s: u=(t-ti)/(0.13*s); return -0.75*math.sin(u*math.pi/2)
    return -0.75*(1-ss(ti+0.13*s,ti+0.6*s,t))
def roll(t,ti,T,target):
    u=cl((t-ti)/T); e=1-(1-u)**2
    return (lerp(TEE[0],target[0],e),lerp(TEE[1],target[1],e)), u>=1

IMP0=0.30   # all three start together: frame 0 is already in the backswing (swing began at -0.15 s)
def swing0(t): return swing(t+0.0,IMP0,1.0) if t>=0 else 0
def hesitate(t):
    """93%: lifts the club like the others, freezes, trembles, puts it back down. Three tries, each smaller."""
    a=0.0
    for t0,peak,hold in ((-0.15,0.8*ss(0,0.3,0.3)*0+0.62,0.55),(3.2,0.32,0.6),(6.9,0.16,0.5)):
        up=t0+0.3; dn=up+hold
        if t0<=t<up: a=peak*ss(t0,up,t) if t0>=0 else peak*ss(-0.15,up,t)
        elif up<=t<dn: a=peak+0.025*math.sin(t*55)*(1-(t-up)/hold)
        elif dn<=t<dn+0.5: a=peak*(1-ss(dn,dn+0.5,t))
    return a

# 1% sprint: 33 more misses after the first, accelerating, then the final putt
imp=[IMP0]; tt=2.05; d=0.62
for k in range(33): imp.append(tt); tt+=max(0.1,d); d*=0.86
sc=(7.9-2.05)/(imp[-1]-2.05); imp=[imp[0]]+[2.05+(x-2.05)*sc for x in imp[1:]]
ints=[imp[k+1]-imp[k] for k in range(33)]+[0.6]
T1=[1.3]+[max(0.42,1.15*0.92**k) for k in range(1,34)]
FINAL_IMP=8.55; RIM_T=9.75; DROP_T=10.0

def lane1(t):
    whites=[]; misses=[]; n=0
    for k in range(34):
        ti=imp[k]
        if t<ti: break
        p,done=roll(t,ti,T1[k],pts[k])
        if done: n+=1; age=t-(ti+T1[k]); misses.append([p[0],p[1],1+0.35*math.exp(-age*9)*(age<0.4)])
        else: whites.append([p[0],p[1]])
    ang=swing0(t)
    for k in range(1,34):
        s=min(1.0,ints[k]/0.95) if k<33 else 0.6
        ang=ang or swing(t,imp[k],s)
    ang=ang or swing(t,FINAL_IMP,1.2)
    ball=None; gold=0; y=BR
    if t>=FINAL_IMP:
        if t<RIM_T:
            u=cl((t-FINAL_IMP)/(RIM_T-FINAL_IMP)); e=1-(1-u)**1.7; rim=(HX-CUP-0.004,0.03)
            ball=(lerp(TEE[0],rim[0],e),lerp(TEE[1],rim[1],e))
        elif t<DROP_T:
            u=(t-RIM_T)/(DROP_T-RIM_T); a=math.pi+0.25+u*1.9*(1-0.3*u)
            ball=(HX+(CUP+0.004)*math.cos(a),-(CUP+0.004)*math.sin(a))
        else:
            u=cl((t-DROP_T)/0.14); ball=(lerp(HX-0.05,HX,u),0); y=BR-0.16*u*u; gold=ss(DROP_T,DROP_T+0.25,t)
    elif not whites and t<FINAL_IMP: ball=TEE
    st={'club':{'angle':ang},'misses':misses,'gold':gold,'flag':1+1.2*math.exp(-max(0,t-DROP_T)*3)*(t>DROP_T),'seed':3,'whites':whites}
    if ball is None: st['noBall']=True
    else: st['ball']=[ball[0],ball[1],y]
    return st,n

def lane6(t):
    st={'club':{'angle':swing0(t)},'seed':2,'flag':0.6}
    if t>=IMP0:
        p,done=roll(t,IMP0,T1[0],MISS6)
        if done: st['noBall']=True; age=t-IMP0-T1[0]; st['misses']=[[p[0],p[1],1+0.35*math.exp(-age*9)*(age<0.4)]]
        else: st['ball']=[p[0],p[1]]
    else: st['ball']=list(TEE)
    if t>=2.0: st['club']={'fall':ss(2.0,2.35,t)**1.6 if t<2.35 else 1}
    return st
def lane93(t): return {'club':{'angle':hesitate(t)},'ball':list(TEE),'seed':1,'flag':0.45}

frames=[]; jobs=[]
for fi in range(NF):
    t=fi/FPS; F={'t':t,'i':fi,'rows':{}}
    l1,n=lane1(t); F['n']=n
    for k,st in (('r93',lane93(t)),('r6',lane6(t)),('r1',l1)):
        y0,y1,yc=ROWS[k]; st['cam']={**CAM,'yc':yc}
        name=f'g{fi:04d}_{k}'; jobs.append({'name':name,'lane':st,'t':t,'w':1080,'h':y1-y0}); F['rows'][k]=name
    frames.append(F)
json.dump(jobs,open(f'{OUT}/jobs.json','w')); json.dump(frames,open(f'{OUT}/frames.json','w'))
json.dump({'imp0':IMP0,'imp1':imp,'T1':T1,'final_imp':FINAL_IMP,'rim':RIM_T,'drop':DROP_T,'miss6_stop':IMP0+T1[0],'fall':2.35,'hes':[-0.15,3.2,6.9]},open(f'{OUT}/cues.json','w'))
print(NF,'frames',len(jobs),'renders; sprint',[round(x,2) for x in imp[:4]],'...',round(imp[-1],2))
