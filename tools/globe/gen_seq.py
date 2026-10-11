# usage: gen_seq.py <width> <t_start> <t_end> <n_frames> <outdir>
import sys,os,json,numpy as np
from multiprocessing import Pool
W,t0,t1,n,out=int(sys.argv[1]),float(sys.argv[2]),float(sys.argv[3]),int(sys.argv[4]),sys.argv[5]
sys.argv=[sys.argv[0],str(W)]
import paleotex as P
from PIL import Image
os.makedirs(out,exist_ok=True)
times=np.linspace(t0,t1,n)
def work(i):
    col,mask,cen=P.frame(float(times[i]))
    Image.fromarray(col).save(f"{out}/color_{i:04d}.jpg",quality=93); Image.fromarray(mask).save(f"{out}/mask_{i:04d}.png")
    return i,float(times[i]),cen
if __name__=="__main__":
    with Pool(24) as p: res=p.map(work,range(n))
    json.dump({i:{"t":t,"india_lat":c[0],"india_lon":c[1]} for i,t,c in res},open(f"{out}/meta.json","w"),indent=1)
    print("done",n)
