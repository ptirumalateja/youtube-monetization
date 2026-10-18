#!/usr/bin/env python3
"""v2 (anime look) text and chip overlay. usage: overlay2.py <out.mov> [t0 t1]. Reuses the v1 text style; only the timings and lines differ.
Timeline (s): O 0-8 | D 7.7-11.9 | T 11.9-17.4 | H 17.4-20.6 | R 20.6-24.4 | M 24.4-31.87"""
import sys, subprocess
import overlay as o
b=o.block
HOOK12=b(['WHAT IF',['EVERY','#MOSQUITO']],112)
o.CAPS=[
 ('hook12', 0.0, 2.9, 250, HOOK12, 'type', 1.1),
 ('hook3',  1.3, 2.9, 250+HOOK12.height+4, b(['VANISHED?'],112), 'pop', 0),
 ('allgone',5.30,6.60,260, b(['OVERNIGHT.','ALL GONE.'],118), 'fade', 0),
 ('everywhere',6.60,7.70,260, b(['EVERYWHERE','ON EARTH.'],104), 'fade', 0),
 ('num',   8.90,10.40,230, b([(['#~610,000'],150),('DEATHS FROM MALARIA,',60),('2024 (WHO)',60)],60), 'pop', 0),
 ('sec',  10.40,11.85,290, b([('ONE EVERY ~52 SECONDS.',64),('MOSTLY CHILDREN UNDER 5.',64)],64), 'fade', 0),
 ('illus', 9.20,11.85,1470, b(['RED = WHO AFRICAN REGION (ILLUSTRATIVE)'],36), 'fade', 0),
 ('arctic',12.10,14.30,260, b(['ARCTIC SWARMS:',['#GONE']],104), 'fade', 0),
 ('y10',   14.50,17.30,260, b([(['#YEAR 10'],88),('SOMETHING ELSE',98),('MOVES IN.',98)],98), 'fade', 0),
 ('nature',17.45,18.60,260, b(['BUT NATURE','NOTICES.'],104), 'fade', 0),
 ('switch',18.60,20.55,260, b(['SOME PREDATORS LOSE A MEAL.','MOST WOULD SWITCH.','FOOD WEBS MIGHT SHIFT.'],64), 'fade', 0),
 ('orchid',20.70,22.55,260, b(['ONE ORCHID','DEPENDS ON THEM.'],98), 'fade', 0),
 ('choc',  22.60,24.30,260, b([(['#CHOCOLATE? SAFE.'],64),('MIDGES POLLINATE IT.',60)],60), 'fade', 0),
 ('q',     24.60,28.30,240, b(['WOULD EARTH BE',['#BETTER'],'WITHOUT THEM?'],100), 'fade', 0),
 ('tag',   24.80,28.30,1470, b(['THOUGHT EXPERIMENT  -  AI-ASSISTED VISUALS'],38), 'fade', 0),
]
if __name__=='__main__':
    out=sys.argv[1]; T=31.87; n=int(T*o.FPS)
    a,bb=(int(float(sys.argv[2])*o.FPS),int(float(sys.argv[3])*o.FPS)) if len(sys.argv)>3 else (0,n)
    p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgba','-s',f'{o.W}x{o.H}','-r',str(o.FPS),'-i','-','-c:v','png','-pix_fmt','rgba',out],stdin=subprocess.PIPE)
    for i in range(a,bb): p.stdin.write(o.frame(i/o.FPS).tobytes())
    p.stdin.close(); p.wait()
