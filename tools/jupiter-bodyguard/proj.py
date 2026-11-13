import numpy as np, shots
def project(cam, p, W=1080, H=1920):
    o=cam[0:3]; r=cam[3:6]; u=cam[6:9]; f=cam[9:12]; th=cam[12]
    d=np.asarray(p)-o; z=d@f
    x=(d@r)/z/(th*W/H); y=(d@u)/z/th
    return (x+1)/2*W, (1-y)/2*H, z
if __name__=="__main__":
    import sys
    for t in [0,11.6,14,17.4]:
        cam,objs,p,L,n=shots.setup(t)
        J=objs[0][:3]; E=objs[1][:3]
        jx,jy,jz=project(cam,J); ex,ey,ez=project(cam,E)
        th=cam[12]
        print(t, 'J', int(jx),int(jy),'Rpx',int(objs[0][3]/jz/th*960), ' E',int(ex),int(ey),'Rpx',int(1/ez/th*960))
