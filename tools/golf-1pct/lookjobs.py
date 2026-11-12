import json, random, math
CX,HX,BR=-1.42,1.42,0.048
random.seed(7)
def scatter(n):
    pts=[]
    while len(pts)<n:
        a=random.uniform(0,2*math.pi); r=0.3+abs(random.gauss(0,0.45))
        x=HX+r*math.cos(a)*1.25; z=r*math.sin(a)*0.8
        if x>HX+0.9 or x<HX-1.25 or abs(z)>0.9: continue
        if all((x-p[0])**2+(z-p[1])**2>(2.1*BR)**2 for p in pts): pts.append([round(x,3),round(z,3)])
    return pts
CAM={'pos':[0,0.6,3.95],'look':[0,0.5,0],'fov':30}
lanes={
 'row93':{'club':{'angle':0},'ball':[CX+0.11,0],'flag':0.35,'cam':CAM,'seed':1},
 'row6':{'club':{'lying':True},'noBall':True,'misses':[[0.82,0.2]],'flag':0.6,'cam':CAM,'seed':2},
 'row1':{'club':{'angle':-0.85},'noBall':True,'misses':scatter(34),'gold':1,'flag':1,'cam':CAM,'seed':3},
}
import copy
# safe zone: all text between y 300 and 1440 (IG/FB account info sits above, caption below)
PANELS={'row93':(0,720),'row6':(720,1310),'row1':(1310,1920)}
lanes['row93']=copy.deepcopy(lanes['row93']); lanes['row93']['cam']={'pos':[0,0.6,4.25],'look':[0,0.82,0],'fov':33}
jobs=[{'name':k,'lane':v,'t':1.3,'w':1080,'h':PANELS[k][1]-PANELS[k][0]} for k,v in lanes.items()]
hook=dict(lanes['row1']); hook.update({'noBall':False,'ball':[HX+0.035,0,BR*0.15],'gold':0.8,
  'cam':{'pos':[HX-1.45,0.78,1.55],'look':[HX+0.0,0.06,0],'fov':24}})
jobs.append({'name':'hook','lane':hook,'t':1.3,'w':1080,'h':1920})
json.dump(jobs,open('/tmp/claude-0/-home-user/d9a00831-620e-5323-a35f-20367efeb7b9/scratchpad/lookjobs.json','w'))
