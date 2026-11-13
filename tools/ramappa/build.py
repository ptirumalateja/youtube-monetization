# v2: word-indexed timeline from the tightened VO's Scribe word times.
import json,os,sys
W="/tmp/claude-0/ram/work/"
d=json.load(open(sys.argv[1]+".stt.json")); ws=[w for w in d["words"] if w["type"]=="word"]
assert len(ws)==54,len(ws)
def t(i): return 0.0 if i==0 else round((ws[i-1]["end"]+ws[i]["start"])/2,2)
voend=ws[-1]["end"]; TOTAL=round(voend+1.2,2)
CB=[0,3,5,7,10,13,15,17,20,22,25,27,31,35,38,42,44,46,50]
times=[t(i) for i in CB]+[99]
json.dump(times,open(W+"times_v2.json","w"))
S=1.30  # splash shot length
E=[(0,"Craftsman_drops",3.45,1.0),(S,"Craftsman_drops",7.6,0.5),
   (t(5),"Visitors_viewing",7.0,.35),(t(10),"Ramappa_Temple_entrance",7.0,.35),(t(13),"Builders_constructing",0.6,.35),
   (t(15),"Shiva_lingam",7.0,.35),(t(17),"Builders_constructing",6.0,.35),(t(20),"Craftsman_holding",0.8,.35),
   (t(22),"Craftsman_holding",7.6,.45),(t(25),"Workers_pouring",3.0,.45),(t(31),"Stone_temple_sand",1.5,.35),
   (t(35),"Ramappa_Temple_during",2.4,.9),(t(38),"Ramappa_Temple_during",8.0,.4),(t(42),"Visitors_viewing",0.5,.35),
   (t(46),"Shiva_lingam",0.0,.35)]
edl=[(a,(E[i+1][0] if i+1<len(E) else TOTAL),k,s,g) for i,(a,k,s,g) in enumerate(E)]
for e in edl: assert e[1]-e[0]>0.5 and e[3]+e[1]-e[0]<=10, e
json.dump({"edl":edl,"total":TOTAL,"endcard":t(50),"vo":sys.argv[1],"sfx":[0,int(t(5)*1000)-150,int(t(35)*1000)-150]},open(W+"edl_v2.json","w"),indent=0)
print(TOTAL,times)
