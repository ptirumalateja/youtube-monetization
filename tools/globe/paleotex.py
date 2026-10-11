"""Paleo-texture generator: for time t, every pixel of an equirectangular map is assigned to the
plate under it (reconstructed static polygons), rotated back to its present-day position, and
coloured from NASA Blue Marble. Ocean = flat colour; mask image R=land, G=India (plate 501)."""
import sys,json,numpy as np,pygplates
from PIL import Image,ImageDraw
Image.MAX_IMAGE_PIXELS=None
D="data/muller2019/"
R=pygplates.RotationModel(D+"Rotations/Muller_etal_2019_CombinedRotations.rot")
STATIC=pygplates.FeatureCollection(D+"StaticPolygons/Muller_etal_2019_Global_StaticPlatePolygons.gpmlz")
COAST=pygplates.FeatureCollection(D+"Coastlines/Muller_etal_2019_Global_Coastlines.gpmlz")
W=int(sys.argv[1]) if len(sys.argv)>1 else 4096; H=W//2
OCEAN=np.array([5,19,42],np.uint8)
wrapper=pygplates.DateLineWrapper()
def raster(polys_vals,mode,fill0=0):
    im=Image.new(mode,(W,H),fill0); dr=ImageDraw.Draw(im)
    for geom,val in polys_vals:
        for wp in wrapper.wrap(geom):
            pts=[((p.get_longitude()+180)/360*W,(90-p.get_latitude())/180*H) for p in wp.get_exterior_points()]
            if len(pts)>2: dr.polygon(pts,fill=val)
    return np.array(im)
# present-day sources, resampled to working resolution
BM=np.array(Image.open("bm_8k.png").convert("RGB").resize((W,H),Image.LANCZOS))
# land mask from Blue Marble colours: ocean pixels are blue-dominant (works at full resolution and handles Antarctica)
_b=BM.astype(np.int16); _ocean=((_b[...,2]>_b[...,0]+25)&(_b[...,2]>=_b[...,1]-5))|((_b.max(-1)<70)&(_b[...,2]>=_b[...,0]))
LAND=(~_ocean).astype(np.uint8)
lon=(np.arange(W)+0.5)/W*360-180; lat=90-(np.arange(H)+0.5)/H*180
LON,LAT=np.meshgrid(np.radians(lon),np.radians(lat))
XYZ=np.stack([np.cos(LAT)*np.cos(LON),np.cos(LAT)*np.sin(LON),np.sin(LAT)],-1).reshape(-1,3)
def rotmat(fr):
    if fr.represents_identity_rotation(): return np.eye(3)
    plat,plon,ang=fr.get_lat_lon_euler_pole_and_angle_degrees()
    a,b=np.radians(plat),np.radians(plon); k=np.array([np.cos(a)*np.cos(b),np.cos(a)*np.sin(b),np.sin(a)]); th=np.radians(ang)
    K=np.array([[0,-k[2],k[1]],[k[2],0,-k[0]],[-k[1],k[0],0]]); return np.eye(3)+np.sin(th)*K+(1-np.cos(th))*K@K
def frame(t):
    rec=[]; pygplates.reconstruct(STATIC,R,rec,t)
    vals=[(r.get_reconstructed_geometry(),r.get_feature().get_reconstruction_plate_id()) for r in rec]
    pid=raster(vals,"I",-1).reshape(-1)
    out=np.empty((H*W,3),np.uint8); out[:]=OCEAN; land=np.zeros(H*W,bool); india=np.zeros(H*W,bool)
    for p in np.unique(pid):
        if p<0: continue
        idx=np.nonzero(pid==p)[0]; M=rotmat(R.get_rotation(0.0,int(p),t))
        v=XYZ[idx]@M.T
        plat=np.degrees(np.arcsin(np.clip(v[:,2],-1,1))); plon=np.degrees(np.arctan2(v[:,1],v[:,0]))
        px=np.clip(((plon+180)/360*W).astype(int),0,W-1); py=np.clip(((90-plat)/180*H).astype(int),0,H-1)
        isl=LAND[py,px]>0; li=idx[isl]
        out[li]=BM[py[isl],px[isl]]; land[li]=True
        if p==501:
            india[li]=True
            # no Himalaya before the collision: replace present-day snow/ice on the Indian plate with nearby land tones
            c=out[li].astype(np.int16); snow=(plat[isl]>26.5)&(c.min(1)>110)  # only the Himalayan rim (present-day lat > 26.5N)
            if snow.any() and (~snow).any(): out[li[snow]]=np.median(c[~snow],0).astype(np.uint8)
    mask=np.zeros((H*W,3),np.uint8); mask[land,0]=255; mask[india,1]=255
    # India centroid (lat, lon) for the camera
    c=XYZ[india].mean(0); c/=np.linalg.norm(c)
    return out.reshape(H,W,3),mask.reshape(H,W,3),(float(np.degrees(np.arcsin(c[2]))),float(np.degrees(np.arctan2(c[1],c[0]))))
if __name__=="__main__":
    import os,time
    times=json.loads(sys.argv[2]); os.makedirs("tex",exist_ok=True); meta={}
    for i,t in enumerate(times):
        t0=time.time(); col,mask,cen=frame(float(t))
        Image.fromarray(col).save(f"tex/color_{i:04d}.png"); Image.fromarray(mask).save(f"tex/mask_{i:04d}.png")
        meta[i]={"t":t,"india_lat":cen[0],"india_lon":cen[1]}; print(i,t,cen,f"{time.time()-t0:.1f}s",flush=True)
    json.dump(meta,open("tex/meta.json","w"),indent=1)
