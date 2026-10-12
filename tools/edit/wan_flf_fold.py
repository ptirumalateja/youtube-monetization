import sys,os; sys.path.insert(0,".")
from build import wan; from cf import *
D="/tmp/claude-0/-home-user-youtube-monetization/96a43257-9cfd-5e8b-a4a4-3357705cc188/scratchpad/collide/"
MOT=("Locked-off camera, no camera movement. The ocean basin between the two continental plates slowly closes as the plates push together. "
     "The horizontal rock layers in the cross-section compress, bend and fold upward, the crust thickens, and young mountain ridges rise "
     "gradually on the surface where the sea was. Slow, heavy, continuous geological deformation. A little dust drifts only at the very end. "
     "No explosion, no fire, no lava, no glowing cracks.")
e1=upload(D+"E1.png","E1.png"); e2=upload(D+"E2.png","E2.png")
g=wan("flf_fast",e1,MOT,8101)
g["18"]={"class_type":"LoadImage","inputs":{"image":e2}}
g["12"]={"class_type":"WanFirstLastFrameToVideo","inputs":{"positive":["8",0],"negative":["9",0],"vae":["10",0],"start_image":["11",0],"end_image":["18",0],"width":720,"height":1280,"length":81,"batch_size":1}}
p=queue(g); print("queued",p,flush=True)
h=wait(p,3600); print("flf",h["status"].get("status_str"),flush=True)
if h["status"].get("status_str")=="success": download(outputs(h)[0],D+"flf_fast_raw.mp4"); print("saved",flush=True)
else: print(json.dumps(h["status"])[:1500])
