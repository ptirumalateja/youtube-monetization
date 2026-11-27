# First Short (9:16) cut from the long-form VO. Visual/overlay cues are given in SOURCE time
# (seconds in narration-kabir-full.mp3) and mapped onto the short's timeline.
GAP=0.12
PIECES=[(0.0,10.8),(65.0,75.35),(117.35,125.38),(360.1,368.6),(272.95,289.75)]
HOLD=0.9
VIS=[  # (src_t, kind, src, opts)
(0.0,'I','I02b',dict(m='in')),(1.9,'I','I04',dict(m='out')),(3.9,'I','I01',dict(m='in')),(4.8,'I','I02',dict(m='in')),
(5.8,'I','I03',dict(m='in')),(6.8,'I','I04',dict(m='in',fx=.3)),(7.9,'GRID','',{}),
(65.1,'I','I14',dict(m='in',fx=.3)),(67.5,'I','I15',dict(m='R')),(69.8,'I','I34',dict(m='in')),(73.0,'I','I43',dict(m='L',fx=.65)),
(117.4,'I','I19',dict(m='up',fx=.6)),(119.8,'I','I21',dict(m='in',fx=.3)),(122.6,'I','I20',dict(m='in',fx=.68)),
(360.2,'I','I47',dict(m='in',fx=.45)),(365.5,'I','I60',dict(m='in',fx=.72)),
(273.0,'I','I38',dict(m='in',fx=.3)),(276.1,'I','I10',dict(m='in')),(285.9,'I','I32',dict(m='in')),(288.3,'I','I39',dict(m='in',fx=.6)),
]
# overlay cues: (src_t, type, text)  type: slam | sub | title | list | x
CUES=[
(0.0,'title','4 WORDS'),(0.0,'title2','NOT THE SAME'),
(3.9,'slam','ASURA'),(4.8,'slam','RAKSHASA'),(5.8,'slam','DAITYA'),(6.8,'slam','DANAVA'),(7.9,'grid',''),
(66.6,'slam','DAITYAS'),(66.6,'sub','sons of Diti'),(68.8,'slam','DANAVAS'),(68.8,'sub','sons of Danu'),
(69.8,'sub','Daityas + Danavas ='),(72.1,'slam','ASURAS'),(73.9,'sub','rivals of the gods'),
(117.9,'slam','RAKSHAMA'),(119.0,'sub','“we will protect”'),(120.4,'slam','YAKSHAMA'),(121.5,'sub','“we will worship”'),(124.6,'slam','RAKSHASAS'),(124.6,'sub','the protectors'),
(361.2,'sub','same father · same mother'),(366.4,'slam','BOTH'),(367.4,'slam','RAKSHASAS'),
(273.1,'subtop','Ravana’s boon from Brahma'),(276.1,'subtop','never to be killed by…'),
(277.7,'list','YAKSHAS'),(278.7,'list','DAITYAS'),(279.7,'list','DANAVAS'),(280.7,'list','RAKSHASAS'),(281.8,'list','SERPENTS'),(282.4,'list','GODS'),
(286.6,'x','HUMANS'),(288.3,'slam','RAMA WAS'),(288.9,'slam2','HUMAN'),
]
def build():
    m=[];t=0.0
    for a,b in PIECES: m.append((a,b,t)); t+=b-a+GAP
    end=t-GAP+HOLD
    def S(src):
        for a,b,o in m:
            if a-1e-6<=src<=b+1e-6: return round(o+src-a,3)
        raise ValueError(src)
    shots=sorted([(S(s),k,f,o) for s,k,f,o in VIS]); cues=sorted([(S(s),ty,tx) for s,ty,tx in CUES]+[(round(o,3),'cut','') for a,b,o in m[1:]])
    return m,shots,cues,round(end,3)
