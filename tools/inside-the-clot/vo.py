import sys, json, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
k=Kokoro("kokoro.onnx","voices.bin"); voice=sys.argv[1]; speed=float(sys.argv[2]); out=sys.argv[3]
L=["Every forty seconds, someone in the US has a heart attack.","It starts inside an artery, decades earlier.","Fatty plaque builds in the wall.","Then its cap cracks.","A clot seals the crack... and the artery.","Within twenty to forty minutes, the heart muscle starts to die.","The plaque didn't block it.","The clot did.","Time is muscle. Call emergency services."]
segs=[]
for l in L:
    a,sr=k.create(l,voice=voice,speed=speed,lang="en-us")
    a=np.asarray(a,np.float32); nz=np.where(np.abs(a)>0.01)[0]; a=a[max(0,nz[0]-200):nz[-1]+800]
    segs.append(a)
json.dump({"sr":sr,"lens":[len(s)/sr for s in segs]},open(out+".json","w"))
for i,s in enumerate(segs): sf.write(f"{out}_{i}.wav",s,sr)
print(voice,[round(len(s)/sr,2) for s in segs],round(sum(len(s) for s in segs)/sr,2))
