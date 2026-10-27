"""Camera/object choreography for every reconstruction shot. Writes shots/<name>.jsonl (30 fps)."""
import json, math, os, random
FPS=30
def n(v): l=math.sqrt(sum(x*x for x in v)); return [x/l for x in v]
def lerp(a,b,t): return [x+(y-x)*t for x,y in zip(a,b)] if isinstance(a,list) else a+(b-a)*t
def ease(t): t=min(max(t,0),1); return t*t*(3-2*t)
def eio(t): t=min(max(t,0),1); return 4*t*t*t if t<.5 else 1-(-2*t+2)**3/2
SUN=n([0.35,0.16,1.0]); SUN2=n([0.5,0.35,1.0])
def shake(t,amp,seed=0):
    return [amp*(math.sin(t*7.1+seed)*.6+math.sin(t*13.3+seed*2)*.4), amp*(math.sin(t*5.3+seed*3)*.6+math.sin(t*11.7+seed)*.4),0]
def darting(t,seed=1,step=1.1,rad=35):
    """Tic Tac abrupt hops: holds, then snaps to a new point in ~0.25 s."""
    rnd=random.Random(seed); pts=[[0,15,0]]
    for i in range(60): pts.append([rnd.uniform(-rad,rad),15+rnd.uniform(-6,10),rnd.uniform(-rad,rad)])
    k=int(t//step); f=(t%step)/0.25
    a,b=pts[k],pts[k+1]; e=eio(f)
    p=lerp(a,b,e); d=[b[0]-a[0],0.001,b[2]-a[2]]
    return p,n(d) if f<1.5 else n([math.cos(k),0,math.sin(k)])
def write(name,dur,fn):
    os.makedirs('shots',exist_ok=True)
    with open(f'shots/{name}.jsonl','w') as f:
        for i in range(int(round(dur*FPS))):
            t=i/FPS; P=dict(S=0,T=3+t,sunD=SUN,expo=1.0,ca=1,foam=1,tA=1,tGlow=.6,fov=.8,roll=0,tp=[0,15,0],ta=[0,0,1])
            P.update(fn(t,t/dur)); f.write(json.dumps(P)+'\n')
SHOTS={}
def shot(name,dur):
    def deco(fn): SHOTS[name]=(dur,fn); return fn
    return deco

@shot('e1_cruise',7)
def _(t,u):   # canopy POV at 20k ft, horizon + glint, slow bank
    s=shake(t,6)
    cp=[-300+u*900+s[0],6000+s[1],-9000+u*2500]
    return dict(cp=cp,ct=[cp[0]+300,cp[1]-4500,cp[2]+16000],fov=1.0,roll=.12+.08*math.sin(t*.5),canopy=1,flare=1,tGlow=.5)
@shot('e2_lookdown',6)
def _(t,u):   # over the rail, zooming toward the whitewater far below
    s=shake(t,8,2)
    cp=[-2600+u*400+s[0],6000+s[1],-3800+u*300]
    return dict(cp=cp,ct=[0,0,0],fov=lerp(.9,.35,ease(u)),roll=.35,canopy=1,flare=.4,tGlow=.8)
@shot('e3_mid',7)
def _(t,u):   # 1,500 m: churn + darting object
    p,d=darting(t+2,3,1.15,30)
    a=t*.06
    cp=[-900*math.cos(a)+u*200,1500-u*300,-900*math.sin(a)-600]
    return dict(cp=cp,ct=[0,10,0],fov=.3,roll=.15,tp=p,ta=d,tGlow=.25,sunD=SUN2)
@shot('e4_close',7)
def _(t,u):   # low and close: reflections, hops
    p,d=darting(t+5,7,1.3,22)
    cp=[-120+u*60,45+u*10,-200+u*30]
    s=shake(t,1.2,4)
    return dict(cp=[cp[0]+s[0],cp[1]+s[1],cp[2]],ct=[p[0]*.5,14,p[2]*.5],fov=.5,roll=.05,tp=p,ta=d,tGlow=.45,sunD=SUN2)
@shot('e5_spiral',6)
def _(t,u):   # Fravor's descending circle; object turns to face him and starts to climb
    a=-1.2+u*1.6; r=lerp(1400,700,u); h=lerp(3000,1200,ease(u))
    cp=[r*math.cos(a),h,r*math.sin(a)]
    turn=ease((u-.35)/.4)
    toward=n([cp[0],0,cp[2]]); base=[1,0,0]
    ta=n(lerp(base,toward,turn)); ty=15+ease((u-.65)/.35)*220
    s=shake(t,5,6)
    return dict(cp=[cp[0]+s[0],cp[1]+s[1],cp[2]],ct=[0,ty*.6,0],fov=.5,roll=.4,canopy=1,flare=.3,tp=[0,ty,0],ta=ta,tGlow=.6,sunD=SUN2)
@shot('e6_climb',4)
def _(t,u):   # object climbs toward the jet, closing fast
    ty=235+u*900; tz=u*700
    cp=[-700,1500-u*100,-400]
    s=shake(t,4,8)
    return dict(cp=[cp[0]+s[0],cp[1]+s[1],cp[2]],ct=[0,ty,tz],fov=.55,roll=.2,tp=[0,ty,tz],ta=n([0,.6,1]),tGlow=.8,sunD=SUN2,flare=.4)
@shot('e7_gone',3)
def _(t,u):   # hold, then it accelerates out of frame with a streak
    go=max(0,(u-.35)/.65); acc=go**3*9000
    tp=[acc*.8,1200+acc*.3,800+acc*.5]
    s=shake(t,3+go*20,9)
    return dict(cp=[-500+s[0],1700+s[1],-200],ct=[0,1200,800],fov=.55,roll=.2,tp=tp,ta=n([.8,.3,.5]),tGlow=.9+go,streak=min(go*600,600),tA=1 if u<.95 else 0,sunD=SUN2,flare=.5)
@shot('e8_calm',6)
def _(t,u):   # whitewater fades to calm sea
    cp=[-1600+u*300,3000,-2000]
    return dict(cp=cp,ct=[0,0,0],fov=.45,roll=.25,tA=0,foam=1-ease(u*1.4),sunD=SUN2)
@shot('c1_close_far',8)
def _(t,u):   # closing shot: slow pull-back from altitude, calm sea
    cp=[-1000-u*2000,4000+u*2000,-6000-u*3000]
    return dict(cp=cp,ct=[0,0,2000],fov=.9,roll=.1,tA=0,foam=0,flare=1,canopy=0)
@shot('n1_topdown',6)
def _(t,u):   # v2: from altitude, looking into the sun glitter: the object hopping over the whitewater, in silhouette
    p,d=darting(t+11,5,1.2,40)
    cp=[-200+u*250,700-u*120,-1500+u*200]
    return dict(cp=cp,ct=[0,0,0],fov=.36,roll=.1,tp=p,ta=d,tGlow=.5,sunD=SUN)
@shot('n2_skim',7)
def _(t,u):   # v2: low tracking shot, the object skimming across the whitewater
    x=-170+u*340; p=[x,15+3*math.sin(t*1.7),8*math.sin(t*.9)]
    s=shake(t,.8,12)
    cp=[x-55+s[0],24+s[1],-95]
    return dict(cp=cp,ct=[x+6,15,0],fov=.55,roll=.02,tp=p,ta=[1,0,0],tGlow=.4,sunD=SUN2)
@shot('n3_rise',6)
def _(t,u):   # v2: rising reveal from beside the object up to altitude
    e=ease(u)
    cp=[lerp(-160,-260,e),lerp(40,650,e),lerp(-260,-1500,e)]
    return dict(cp=cp,ct=[0,lerp(14,4,e),0],fov=lerp(.5,.32,e),roll=.08,tp=[0,15,0],ta=n([1,0,.3]),tGlow=.45,sunD=SUN2)
@shot('t1_triangle',14)
def _(t,u):   # dusk ridge: rise, hover, drop into canyon (based on AARO memo description)
    rise=ease(u/.3); drop=ease((u-.75)/.12)
    y=lerp(-8,36,rise)-drop*60; x=60+drop*12
    s=shake(t,.02,3)
    cp=[s[0],1.6+s[1],0]
    fovv=lerp(.9,.35,ease(u/.6))
    return dict(S=1,cp=cp,ct=[60,1.6+lerp(30,36,u),300],fov=fovv,dusk=1,sunD=n([.6,-.04,1]),trP=[x,y,300],trA=1 if u<.9 else 0,trYaw=.05+.03*math.sin(t),expo=1.15,ca=1)

if __name__=='__main__':
    import sys
    names=sys.argv[1:] or list(SHOTS)
    for k in names:
        d,fn=SHOTS[k]; write(k,d,fn); print(k,d)
