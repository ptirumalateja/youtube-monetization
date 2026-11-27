# usage: python3 render_film.py REPO OUT_DIR GFX_DIR [i0 i1]
import sys,os,subprocess,math,random,numpy as np
from PIL import Image,ImageFilter
sys.path.insert(0,os.path.dirname(__file__)); from edl import SHOTS,END
REPO,OUT,GFX=sys.argv[1:4]; os.makedirs(OUT,exist_ok=True)
FPS=30;W,H=1920,1080
rng=range(len(SHOTS)) if len(sys.argv)<6 else range(int(sys.argv[4]),int(sys.argv[5]))
def fr(t): return round(t*FPS)
def enc_cmd(path,extra_in=None):
    return ['ffmpeg','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-']
def x264(path): return ['-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p','-r',str(FPS),path]
_cache={}
def load(kind,src):
    if (kind,src) in _cache: return _cache[(kind,src)]
    if kind=='I':
        p=f'{REPO}/media/asura-flow/{src}.jpg'
        if not os.path.exists(p): p=p[:-4]+'.png'
    else: p=f'{REPO}/media/asura-src/{src}'
    im=Image.open(p).convert('RGB')
    if im.width>3000: im=im.resize((3000,round(im.height*3000/im.width)),Image.LANCZOS)
    _cache[(kind,src)]=im; return im
def ease(u): return u*u*(3-2*u)
def boxes(im,o,flow):
    iw,ih=im.size; ar=W/H
    m=o.get('m','in'); fx,fy=o.get('fx',.5),o.get('fy',.45)
    if iw/ih>ar: bw,bh=ih*ar,ih
    else: bw,bh=iw,iw/ar
    tall=bh<ih*0.8
    if tall and m in('up','down'):
        z0=z1=1.05; ys=(.15,.45) if m=='down' else (.45,.15)
        a,b=(fx,ys[0]),(fx,ys[1])
    else:
        z0,z1={'in':(1.15,1.3),'out':(1.3,1.15)}.get(m,(1.3,1.3))
        d={'L':(-.07,0),'R':(.07,0),'up':(0,.07),'down':(0,-.07)}.get(m,(0,0))
        if tall: fy=.3
        a,b=(fx+d[0],fy+d[1]),(fx-d[0],fy-d[1])
    def box(u):
        z=z0+(z1-z0)*u; cw,ch=bw/z,bh/z
        if tall and m in('up','down'):
            x0=(iw-cw)/2; y0=(ih-ch)*(a[1]+(b[1]-a[1])*u)
        else:
            cx=(a[0]+(b[0]-a[0])*u)*iw; cy=(a[1]+(b[1]-a[1])*u)*ih
            x0=min(max(cx-cw/2,0),iw-cw); y0=min(max(cy-ch/2,0),ih-ch)
        if flow and x0+cw>0.875*iw and y0+ch>0.78*ih:
            dx=(x0+cw-0.875*iw)/iw; dy=(y0+ch-0.78*ih)/ih
            if (dy<dx or x0-dx*iw<0) and y0-dy*ih>=0: y0-=dy*ih
            else: x0=max(0.0,0.875*iw-cw)
        return (x0,y0,x0+cw,y0+ch)
    return box
class FX:
    def __init__(s,kind,n,seed):
        r=random.Random(seed); s.kind=kind
        cnt={'embers':70,'dust':90}.get(kind,0)
        s.p=[(r.random()*W,r.random()*H,r.uniform(.5,1.6),r.uniform(20,90) if kind=='embers' else r.uniform(4,18),r.random()*6.28,r.uniform(1.2,3.5) if kind=='embers' else r.uniform(1,2.6)) for _ in range(cnt)]
    def apply(s,f,t):
        if s.kind=='flicker':
            k=1+0.045*math.sin(t*9.1)+0.03*math.sin(t*23.7+1)+0.02*math.sin(t*3.3)
            return np.clip(f.astype(np.float32)*k,0,255).astype(np.uint8)
        if not s.p: return f
        g=f.astype(np.float32)
        col=np.array([255,140,50] if s.kind=='embers' else [255,220,160],np.float32)
        for (x,y,sz,v,ph,rad) in s.p:
            yy=(y-v*t)%H; xx=(x+math.sin(t*.7+ph)*30)%W
            a=(.55+.45*math.sin(t*3+ph))*(.9 if s.kind=='embers' else .35)
            R=int(rad*3)+1; xi,yi=int(xx),int(yy)
            x0,x1,y0,y1=max(0,xi-R),min(W,xi+R+1),max(0,yi-R),min(H,yi+R+1)
            if x1<=x0 or y1<=y0: continue
            gx=np.arange(x0,x1)-xx; gy=np.arange(y0,y1)-yy
            d=np.exp(-(gy[:,None]**2+gx[None,:]**2)/(2*rad*rad))*a*sz
            g[y0:y1,x0:x1]+=d[...,None]*col
        return np.clip(g,0,255).astype(np.uint8)
def still_frames(kind,src,o,n,t0):
    im=load(kind,src); box=boxes(im,o,kind=='I'); fx=FX(o.get('fxs',''),n,hash(src)%1000)
    for i in range(n):
        u=ease(i/max(1,n-1)) if o.get('m','in') in('in','out') else i/max(1,n-1)
        f=np.asarray(im.transform((W,H),Image.EXTENT,box(u),Image.BICUBIC))
        yield fx.apply(f,i/FPS)
def grid_frames(n):
    ims=[load('I',k) for k in ('I01','I02','I03','I04')]
    for i in range(n):
        u=i/max(1,n-1); canvas=Image.new('RGB',(W,H))
        for k,im in enumerate(ims):
            iw,ih=im.size; z=1.2+0.08*u; cw,ch=iw/z*0.95,iw/z*0.95*9/16
            x0=0.03*iw; y0=max(0,(ih-ch)*0.4)
            t=im.transform((W//2,H//2),Image.EXTENT,(x0,y0,x0+cw,y0+ch),Image.BICUBIC)
            canvas.paste(t,((k%2)*W//2,(k//2)*H//2))
        yield np.asarray(canvas)
def run(idx):
    t0,kind,src,o=SHOTS[idx]; t1=SHOTS[idx+1][0] if idx+1<len(SHOTS) else END
    n=fr(t1)-fr(t0); out=f'{OUT}/k_{t0:07.2f}_{t1:07.2f}.mp4'
    if os.path.exists(out): return
    if os.environ.get('NOGFX') and (kind=='G' or o.get('ov')): return
    tmp=out+'.tmp.mp4'
    if kind in('I','R','GRID'):
        ov=o.get('ov')
        cmd=enc_cmd(out)
        if ov:
            g,gt=ov; off=t0-gt if g=='G01' else 0
            cmd+=['-ss',f'{max(0,off):.3f}','-i',f'{GFX}/{g}.mov','-filter_complex','[0][1]overlay=0:0:eof_action=pass[v]','-map','[v]']
        p=subprocess.Popen(cmd+['-frames:v',str(n)]+x264(tmp),stdin=subprocess.PIPE)
        gen=grid_frames(n) if kind=='GRID' else still_frames(kind,src,o,n,t0)
        for f in gen: p.stdin.write(np.ascontiguousarray(f).tobytes())
        p.stdin.close(); p.wait()
    elif kind=='C':
        p=f'{REPO}/media/asura-flow/flow-clips/{src}.mp4'
        dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',p]))
        ss=o.get('ss',0); need=n/FPS; avail=dur-ss-0.05; sp=min(1,avail/need)
        zw=2400 if src=='C08' else 2208
        vf=f"setpts=PTS/{sp:.4f},fps={FPS},scale={zw}:-2:flags=lanczos,crop={W}:{H}:0:(ih-{H})/2,setsar=1"
        subprocess.run(['ffmpeg','-loglevel','error','-y','-ss',f'{ss}','-i',p,'-vf',vf,'-frames:v',str(n),'-an']+x264(tmp),check=True)
    elif kind=='G':
        gss=o.get('gss',0)
        subprocess.run(['ffmpeg','-loglevel','error','-y','-ss',f'{gss}','-i',f'{GFX}/{src}.mp4','-vf',f'fps={FPS},tpad=stop_mode=clone:stop_duration=30','-frames:v',str(n),'-an']+x264(tmp),check=True)
    got=int(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v','-show_entries','stream=nb_read_frames','-of','csv=p=0',tmp]))
    if got!=n: print('FRAMES',idx,src,got,n,flush=True)
    os.rename(tmp,out); print('done',idx,kind,src,n,flush=True)
for i in rng: run(i)
