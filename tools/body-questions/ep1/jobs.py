import json,math
def ease(x): x=max(0,min(1,x)); return x*x*(3-2*x)
def lerp(a,b,f): return [a[i]+(b[i]-a[i])*f for i in range(len(a))] if isinstance(a,list) else a+(b-a)*f
J=[]
P=lambda n,p:J.append({"name":n,"log":1,"params":p})
P("H1",{"T":0.3,"SS":2})
P("H2",{"T":1.2,"SS":2,"CAMP":[0.35,0.0,2.4],"TGT":[0.05,-0.25,0],"ROLL":0.1})
P("P",{"SS":2,"TWO":1,"WR0":0,"WR1":1,"XRAY":0.6,"NERVE":1.3,"CUT0":1,"DROPS":0,"VES":0.2,"CAMP":[0,-0.6,4.6],"TGT":[0,-0.7,0],"ROT":[-0.15,0,0.0],"T":0.2})
P("H3",{"SS":2,"T":2.0,"ROT":[-0.2,0.0,0.05],"CAMP":[0,-0.1,3.2],"TGT":[0,-0.3,0]})
P("C",{"SS":2,"T":3.0,"CAMP":[0,-0.4,6.5],"TGT":[0,-0.6,0]})
F=15
# S2 nerves 2.92-3.78, S3 vessels 3.78-7.36 : one continuous camera
t0,t1=2.92,7.36
n=int(round((t1-t0)*F))+1
for i in range(n):
    t=t0+i/F; f=(t-t0)/(t1-t0)
    cam=lerp([0.2,-0.3,3.6],[0.12,-0.5,2.85],ease(f)); 
    nerve=1.3*ease((t-2.95)/0.35) if t<3.78 else lerp(1.3,0.25,ease((t-3.78)/0.4))
    ves=0 if t<3.78 else 1.9*ease((t-3.78)/0.35)
    con=1-0.65*ease((t-6.3)/0.9)
    P(f"X{i:03d}",{"SS":1,"XRAY":1,"WR0":0,"DROPS":0,"CAMP":cam,"TGT":[0,-0.6,0],"NERVE":nerve,"VES":ves,"CON":con,"T":t})
t0,t1=7.36,11.02
n=int(round((t1-t0)*F))+1
for i in range(n):
    t=t0+i/F; f=(t-t0)/(t1-t0); a=-0.5+0.9*ease(f)
    cam=[2.9*math.sin(a*0.35)+0.0,0.1-0.1*f,3.3-0.4*ease(f)]
    P(f"G{i:03d}",{"SS":1,"WR0":ease((t-7.5)/3.3),"DROPS":0,"CAMP":cam,"TGT":[0,-0.2,0],"T":t})
t0,t1=15.65,19.05
n=int(round((t1-t0)*30))+1
for i in range(n):
    t=t0+i/30
    P(f"R{i:03d}",{"SHOT":1,"T":t,"PRESS":ease((t-15.65)/0.7),"FOV":1.0+0.12*ease((t-15.65)/3.4)})
json.dump(J,open('/home/user/ep1/jobs.json','w'))
print(len(J))
