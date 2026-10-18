"""Paradox / mind-bending background concepts (stills). usage: bg_concepts.py <out.png>"""
import sys, math
import numpy as np, cv2
sys.argv_out=sys.argv[1]; sys.argv=['x']
import render as R
from PIL import Image
W,H=R.W,R.H
CXY=(540,960)
def glow(img,r=9,k=0.9):
    b=cv2.GaussianBlur(img,(0,0),r); return np.clip(img.astype(float)+b*k*1.6,0,255).astype('uint8')
def rot(x,y,a): c,s=math.cos(a),math.sin(a); return x*c-y*s,x*s+y*c
def twist_tunnel(t,twist=0.16,roll=0.0):
    """square corridor receding to the centre; every ring is rotated a little more than the one before it (a spiral staircase for the eye)"""
    img=np.zeros((H,W,3),np.uint8); F=620.0; cx,cy=CXY
    for k in range(40):
        z=((k*0.34-t*1.3)%13.6)+0.35; a=roll+twist*(13.6-z)*0.55; s=F/z
        pts=[rot(sx*s,sy*s,a) for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1))]; p=np.array([(cx+x,cy+y*1.28) for x,y in pts],np.int32)
        al=max(0.0,min(1.0,max(0.0,1-z/13.6)**0.8*min(1,z/0.9)))
        col=(int(150+80*al),int(200*al+30),int(255*al*0.6+20)) if k%2 else (int(120*al),int(190*al),int(240*al))
        cv2.polylines(img,[p],True,(int(col[0]*al),int(col[1]*al),int(col[2]*al)),2,cv2.LINE_AA)
    for j in range(4*2):   # lines along the corridor (corners and mid-edges)
        ang=j*math.pi/4+math.pi/4; pts=[]
        for z in np.linspace(0.35,13.9,40):
            a=roll+twist*(13.6-z)*0.55; r_=(1.0 if j%2==0 else 1.0)*F/z; ex=math.cos(ang); ey=math.sin(ang)
            m=1/max(abs(ex),abs(ey)); x,y=rot(ex*m*r_,ey*m*r_,a); pts.append((cx+x,cy+y*1.28))
        pts=np.array(pts,np.int32); cv2.polylines(img,[pts],False,(120,170,220),2,cv2.LINE_AA)
    return glow(img,10,0.8)
def topo(t):
    img=np.zeros((H,W,3),np.uint8); gw,gh=108,192
    ys,xs=np.mgrid[0:gh,0:gw].astype(float); u=xs/gw*3.2; v=ys/gh*5.6
    f=(np.sin(u*1.7+t*0.9+np.sin(v*1.3+t*0.5)*1.6)+np.sin(v*1.1-t*0.7+np.sin(u*1.9-t*0.4)*1.4)+0.6*np.sin((u+v)*2.3+t*0.8))/2.6
    f=cv2.GaussianBlur(f,(0,0),1.2)
    for lv in np.linspace(-0.85,0.85,13):
        m=(f>lv).astype('uint8')*255; cs,_=cv2.findContours(m,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
        for c in cs:
            if len(c)<8: continue
            p=(c[:,0,:].astype(float)*np.array([W/gw,H/gh])).astype(np.int32)
            tone=int(110+110*(1-abs(lv)))
            cv2.polylines(img,[p],True,(tone,int(tone*0.95),int(tone*0.8)),2,cv2.LINE_AA)
    return glow(img,7,0.6)
def dots(t):
    img=np.zeros((H,W,3),np.uint8); cx,cy=540,900; n=70; m=130
    for i in range(m):
        for j in range(n):
            u=(j/(n-1)-0.5)*2; v=(i/(m-1))
            ang=v*5.0+t*0.7+u*1.4; r=0.15+v*1.3
            x=math.cos(ang)*r*(1+0.35*math.sin(u*3+t)); y=math.sin(ang)*r*0.55+u*0.7; z=0.4+v*2.2+0.4*math.sin(u*2.5+t*0.8)
            sx=cx+x/z*520; sy=cy+y/z*520
            if not(0<sx<W and 0<sy<H): continue
            br=max(0.0,min(1.0,1.3-z*0.45)); rad=1+int(3*br)
            col=(int(140*br),int(235*br),int(90*br)) if (i+j)%7 else (int(120*br),int(210*br),int(255*br))
            cv2.circle(img,(int(sx),int(sy)),rad,col,-1,cv2.LINE_AA)
    img=glow(img,8,0.9); cv2.circle(img,(cx,cy-380),160,(255,230,200),-1,cv2.LINE_AA); img=cv2.GaussianBlur(img,(0,0),2)
    return img
def compose(bg_bgr,t,label):
    fr=Image.fromarray(cv2.cvtColor(bg_bgr,cv2.COLOR_BGR2RGB)).convert('RGBA')
    ov=Image.new('RGBA',(W,H),(0,0,0,0)); R.put(ov,R.txt('HOW FAST',112),540,250,1); R.put(ov,R.row(['IS','#FAST','?'],112,0.3),540,400,1)
    R.paste(ov,R.SPR['bullet'],570,980,0.9); fr.alpha_composite(ov)
    R.put(fr,R.txt(label,40,R.GOLD),540,1500,1)
    return fr.convert('RGB')
tiles=[]
for t in (0.0,1.2):
    tiles.append(compose(twist_tunnel(t),t,'A  TWISTED CORRIDOR'))
    tiles.append(compose(topo(t),t,'B  MORPHING CONTOURS'))
    tiles.append(compose(dots(t),t,'C  DOT-LATTICE VORTEX'))
sheet=Image.new('RGB',(3*320,2*569))
for i,im in enumerate(tiles): sheet.paste(im.resize((320,569)),((i%3)*320,(i//3)*569))
sheet.save(sys.argv_out)
