# v3 compositor: grade, post camera (punch-ins, impact shake/flash), split-screen wipe + whips, captions, clock, CLICK/JINGLE tags, CTA, watermark.
# python3 compose.py [out.mp4] [audio.wav|none]     stills: python3 compose.py out.jpg none 0.5,3.2
import json, sys, subprocess, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FPS=30; DUR=13.0; COLD=0.5; OUTDUR=11.65; N=round(OUTDUR*FPS); NB=round(DUR*FPS); W,H=1080,1920   # COLD: payoff-first cold open before the story
FB='fonts/JetBrainsMono-Bold.ttf'
F=lambda s: ImageFont.truetype(FB,s)
fT=F(84); fTH=F(100); fCap=F(54); fLab=F(30); fClk=F(46); fJ=F(46); fJ2=F(78); fCTA=F(38); fWm=F(22)
CREAM=(240,233,216); RUST=(170,62,38); GOLD=(240,190,92); INK=(12,14,24)
SPLIT=(1.6,5.0); CROP=760
meta=json.load(open('output/dog/meta.json'))['frames']
TITLES=[(0.0,0.30,'HE WAITS',None),(0.30,1.6,'HE WAITS','ALL DAY.'),(5.0,6.4,'HE HAS','THE DOOR.'),(8.0,8.6,'YOU HAVE LOTS.',None),(8.6,13.01,"YOU'RE HIS",'ENTIRE WORLD.')]
SPLITCAP=[(1.6,2.7,'YOU HAVE A JOB,'),(2.7,3.8,'FRIENDS,'),(3.8,5.0,'A LIFE.')]
sm=lambda u: (lambda v: v*v*(3-2*v))(min(max(u,0.0),1.0))
# ---------------------------------------------------------------- grade (numpy, linear-ish on display values)
def grade(im,hl=0.0,pop=0.0):
    a=np.asarray(im.convert('RGB'),np.float32)/255.0
    if hl>0:                                                    # de-haze bright cream-on-cream shots: midtone gamma + saturation
        a=a**(1+0.28*hl); l0=(a@np.array([0.2126,0.7152,0.0722],np.float32))[...,None]; a=l0+(a-l0)*(1+0.18*hl)
    a=np.clip((a-0.03)/(0.965-0.03),0,1)                       # black point / white point (peaks reach ~250)
    c=0.35+pop
    a=a*(1-c)+c*(a*a*(3-2*a))                                   # S-curve; pop>0 = impact contrast punch
    l=(a@np.array([0.2126,0.7152,0.0722],np.float32))[...,None]
    a+=((1-l)**2)*np.array([-0.012,0.004,0.022],np.float32)     # cool slate shadows
    a+=(l**2)*np.array([0.014,0.004,-0.012],np.float32)         # warm amber highlights
    # edge lift: frame top/bottom never go near-black (FB "black border" read)
    yy=np.linspace(0,1,a.shape[0],dtype=np.float32)[:,None,None]
    xx=np.linspace(0,1,a.shape[1],dtype=np.float32)[None,:,None]
    m=np.maximum(np.clip(1-yy/0.13,0,1)**1.5+np.clip((yy-0.9)/0.1,0,1)**1.5, 0.8*(np.clip(1-xx/0.07,0,1)+np.clip((xx-0.93)/0.07,0,1))**1.5)
    a=np.maximum(a,m*np.array([0.19,0.18,0.215],np.float32))
    return Image.fromarray((np.clip(a,0,1)*255+0.5).astype(np.uint8))
# ---------------------------------------------------------------- post camera
def zoom_at(t):
    z=1.0
    if t<0.30: z=1.0+0.02*t/0.30
    elif t<0.55: z=1.02+0.07*sm((t-0.30)/0.07)                # latch punch-in
    elif 1.0<=t<1.6: z=1.0+0.12*sm((t-1.0)/0.6)                # push in on the sigh while the clock spins
    elif t<0.8: z=1.12-0.12*sm((t-0.55)/0.25)
    elif 10.68<=t<11.1: u=(t-10.68)*FPS; z=1.0+0.05*(sm(u/3) if u<3 else 1-sm((u-3)/8))   # micro-punch on the piano note + heart burst
    elif t>=12.4: z=1.0+(CZ-1.0)*sm((t-12.4)/0.6)                  # end on the cold-open crop -> seamless loop               # snap zoom-out on the cut to wide
    elif 5.0<=t<5.7: z=1.0+0.06*(t-5.0)/0.7
    elif 5.7<=t<6.4: z=1.0+0.12*sm((t-5.7)/0.7)                  # push toward the door
    elif 6.4<=t<7.4: z=1.0+0.05*max(0,1-abs(t-6.6)/0.35) if t>6.5 else 1.0
    elif 8.05<=t<8.6: z=1.0+0.08*math.exp(-(t-8.08)/0.18) if t>=8.08 else 1.0
    return z
def shake_at(t):
    if 0.30<=t<0.40: a=6*(1-(t-0.30)/0.10); return (a*math.sin(t*251),a*math.cos(t*197))
    if 8.08<=t<8.2: k=(t-8.08)/0.12; a=14*(1-k); return (a*math.sin(t*173),a*math.cos(t*211))
    return (0,0)
def cam(im,t,cy=0.5,cx=0.5):
    z=zoom_at(t); dx,dy=shake_at(t)
    if z==1.0 and dx==0 and dy==0: return im
    w,h=im.size; cw,ch=w/z,h/z; x0=(w-cw)*cx-dx/z; y0=(h-ch)*cy-dy/z
    return im.transform((w,h),Image.EXTENT,(x0,y0,x0+cw,y0+ch),resample=Image.BICUBIC)
# ---------------------------------------------------------------- text helpers
def sw(d,txt,font,sp): return sum(d.textlength(c,font=font)+sp for c in txt)-sp
def spaced(d,x,y,txt,font,fill,sp,heavy=0):
    for ch in txt: d.text((x,y),ch,font=font,fill=fill,stroke_width=heavy,stroke_fill=fill); x+=d.textlength(ch,font=font)+sp
def ease_back(u): u=min(max(u,0),1); c=1.7; return 1+(c+1)*(u-1)**3+c*(u-1)**2
def pop_layer(lay,t,t0,cx,cy,dur=0.14):
    if t0<=0.0: return lay                                  # frame-0 text is simply there
    s=0.82+0.18*ease_back((t-t0)/dur)
    if abs(s-1)>1e-3: lay=lay.transform((W,H),Image.AFFINE,(1/s,0,cx-cx/s,0,1/s,cy-cy/s),resample=Image.BICUBIC)
    return lay
def with_shadow(base,lay,r=16,k=0.55):
    sh=lay.getchannel('A').filter(ImageFilter.GaussianBlur(r)).point(lambda v:int(v*k)); blk=Image.new('RGBA',(W,H),INK+(0,)); blk.putalpha(sh); base.alpha_composite(blk); base.alpha_composite(lay)
def pill(d,cx,cy,txt,font,sp,fg,bg=INK+(225,),padx=30,h=None,outline=None):
    w=sw(d,txt,font,sp); h=h or font.size+30; x0=cx-w/2-padx
    d.rounded_rectangle([x0,cy-h/2,cx+w/2+padx,cy+h/2],radius=h/2,fill=bg,outline=outline,width=3 if outline else 0)
    spaced(d,cx-w/2,cy-font.size*0.62,txt,font,fg,sp)
def title(base,t):
    for t0,t1,a,b in TITLES:
        if not (t0<=t<t1): continue
        hook=t1<=1.6; fnt=fTH if hook else fT; lh=fnt.size+28; y=215 if hook else 175
        lays=[Image.new('RGBA',(W,H),(0,0,0,0)) for _ in range(2)]
        for i,(txt,col) in enumerate([(a,CREAM),(b,GOLD)]):
            if not txt: continue
            d=ImageDraw.Draw(lays[i]); w=sw(d,txt,fnt,6); yy=y+i*lh
            if hook: bg,fg=((RUST+(242,),CREAM) if i==0 else (GOLD+(250,),INK))      # hook: brand rust/gold slabs, max contrast
            else: bg,fg=INK+(185,),col
            d.rounded_rectangle([540-w/2-28,yy-10,540+w/2+28,yy+fnt.size+20],radius=18,fill=bg,outline=(CREAM+(255,)) if hook else None,width=4 if hook else 0)
            spaced(d,540-w/2,yy+2,txt,fnt,fg+(255,),6,heavy=2 if hook else 0)
        if hook:   # line 1 is simply there from frame 0; line 2 stamps on the latch with a bigger overshoot
            with_shadow(base,lays[0])
            if b: with_shadow(base,pop_layer(lays[1],t,t0,540,y+lh*1.5,0.12) if t0>0 else lays[1])
        else:
            lays[0].alpha_composite(lays[1]); with_shadow(base,pop_layer(lays[0],t,t0,540,250))
def clock_txt(m): return f'{m//60:02d}:{m%60:02d}'
HUG=8.6; HUG_SKIP=4
_yy,_xx=np.mgrid[0:H,0:W].astype(np.float32); VIG=(1-0.17*np.clip(1-np.hypot(_xx/W,(H-_yy)/H)/0.75,0,1)**1.6)[...,None]*np.array([1.0,0.97,0.94],np.float32)**0
def src(f):
    t=f/FPS
    if t<HUG: return f
    return round(HUG*FPS+HUG_SKIP+(f-HUG*FPS)*(NB-1-HUG*FPS-HUG_SKIP)/(NB-1-HUG*FPS))
fCold=ImageFont.truetype('fonts/JetBrainsMono-ExtraBold.ttf',76); CZ,CX,CY=1.0,0.5,0.5   # v4: wide hug, full room; loop ends on the same framing
def cold(f):
    # 0-0.47 s: the payoff first: the leap into the owner's arms (tight, moving, impact punch); 0.47-0.6 rewind smear into the morning
    t=f/FPS; TR=0.40
    def jump(tt):
        sf=round((10.6+tt)*FPS); room=grade(Image.open(f'output/dog/frames/f{sf:05d}.jpg'),1.6)
        room=Image.fromarray((np.asarray(room,np.float32)*VIG).clip(0,255).astype(np.uint8))
        z=CZ+0.10*(tt/TR)**0.8; cx,cy=CX*W,CY*H; cw,ch=W/z,H/z; sx=sy=0
        return room.transform((W,H),Image.EXTENT,(cx-cw/2+sx,cy-ch/2+sy,cx+cw/2+sx,cy+ch/2+sy),resample=Image.BICUBIC)
    if t<TR: im=jump(t).convert('RGBA')
    else:
        u=(t-TR)/(COLD-TR); k=math.sin(math.pi*min(u,1))
        a=np.asarray(jump(TR-1/FPS),np.float32); b=np.asarray(grade(Image.open('output/dog/frames/f00000.jpg')),np.float32); m=a*(1-sm(u))+b*sm(u)
        pass
        m=m*(1+0.12*k); m=np.where(m>220,220+(m-220)/(1+(m-220)/60),m)            # capped flash with highlight roll-off
        im=Image.fromarray(m.clip(0,255).astype(np.uint8)).filter(ImageFilter.BoxBlur(int(14*k)+1)).convert('RGBA')
    if t<TR+0.04:
        lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay); txt="10 HOURS FOR THIS?"; w=d.textlength(txt,font=fCold); y=150
        d.rounded_rectangle([540-w/2-24,y-14,540+w/2+24,y+fCold.size+18],radius=20,fill=RUST+(245,),outline=CREAM+(255,),width=4)
        d.text((540-w/2,y-4),txt,font=fCold,fill=CREAM+(255,))
        with_shadow(im,lay)
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); g=ImageDraw.Draw(lay); wm='SLOW LIGHT'; ww=sw(g,wm,fWm,10); spaced(g,540-ww/2,1852,wm,fWm,(230,220,200,150),10); im.alpha_composite(lay)
    return im.convert('RGB')
LIE=(0.95,1.40)
def body_t(to):
    if to<0.62: return to-0.32                   # door slam enters mid-swing; latch (body 0.30) lands at 0.62
    if to<LIE[0]: return 0.30+(to-0.62)*0.72     # ears drop, stays on the close-up until the lie-down
    if to<LIE[1]: return 0.63+(to-LIE[0])*2.0    # lie-down + sigh at 2x
    for o0,b0 in PANELS:                         # split panels trimmed to 0.75 s each (bike keeps its silence tail)
        if o0<=to<o0+0.75: return b0+(to-o0)
    return to+1.35                               # story after the split
PANELS=((1.40,1.6),(2.15,2.7),(2.90,4.25)); WHIPS=(2.15,2.90)
def frame(fo):
    if fo<round(COLD*FPS): return cold(fo)
    to=fo/FPS; f=min(NB-1,max(0,round(body_t(to)*FPS))); lie=LIE[0]<=to<LIE[1]
    t=f/FPS; sf=src(f); m=meta[min(sf,len(meta)-1)]
    hl=1.6*sm((t-8.45)/0.3) + (0.9 if 5.7<=t<6.4 else 0.0)
    pop=0.32*math.exp(-max(t-8.08,0)/0.1) if 8.06<=t<8.4 else 0.0
    room=grade(Image.open(f'output/dog/frames/f{sf:05d}.jpg'),hl,pop)
    if t>=8.6: room=Image.fromarray((np.asarray(room,np.float32)*VIG).clip(0,255).astype(np.uint8))
    split=SPLIT[0]<=t<SPLIT[1]
    if split:
        im=Image.new('RGB',(W,H),INK)
        day=grade(Image.open(f'output/day/frames/f{f:05d}.jpg'))
        day=day.point(lambda v:int(30+v*0.88))                    # lift the crushed shadows in the owner's-day sets
        ps=max(o for o,_ in PANELS if o<=to+1e-6); u=(to-ps)/0.75
        if True:
            z=1.0+0.12*u; ox=(u-0.5)*W*(1-1/z)*0.9 if ps==2.90 else 0; day=day.transform((W,960),Image.EXTENT,(W*(1-1/z)/2+ox,960*(1-1/z)/2,W*(1+1/z)/2+ox,960*(1+1/z)/2),resample=Image.BICUBIC)
        # whip between the owner's-day sets (4 frames each side of 2.7 / 3.8)
        for c in WHIPS:
            u=(to-c)*FPS
            if -4<=u<4:
                off=int(110*(1-abs(u+0.5)/4.5))*(1 if u<0 else -1); a=np.pad(np.asarray(day.filter(ImageFilter.BoxBlur(10))),((0,0),(120,120),(0,0)),mode='reflect'); day=Image.fromarray(np.ascontiguousarray(a[:,120+off:120+off+W]))
        wipe=sm((t-SPLIT[0])/0.2)
        zb=1.1; bw,bh=W/zb,960/zb; bx=min(max(918-bw/2,0),W-bw); by=min(max(1300-bh/2,0),H-bh)
        im.paste(room.transform((W,960),Image.EXTENT,(bx,by,bx+bw,by+bh),resample=Image.BICUBIC),(0,960))
        top=room.crop((0,0,W,960)); y=int(-960*(1-wipe))
        im.paste(top,(0,0)); im.paste(day,(0,y))
        im=im.convert('RGBA')
    else:
        if lie:
            z=1.15+0.12*sm((to-1.15)/0.06)*(to>=1.15); cw,ch=W/z,H/z
            k=sm((t-0.63)/0.5); hx,hy=0.78,0.52+0.1*k     # follow the head down through the sit -> lie
            x0=min(max(hx*W-cw/2,0),W-cw); y0=min(max(hy*H-ch/2,0),H-ch)
            im=room.transform((W,H),Image.EXTENT,(x0,y0,x0+cw,y0+ch),resample=Image.BICUBIC).convert('RGBA')
        elif 5.7<=t<6.4:
            u=sm((t-5.7)/0.7); z=1.0+0.08*u; w,h=room.size; cw,ch=w/z,h/z; x0=(w-cw)*0.8; y0=(h-ch)*0.75
            im=room.transform((w,h),Image.EXTENT,(x0,y0,x0+cw,y0+ch),resample=Image.BICUBIC)
            a=np.asarray(im,np.float32); xx=np.linspace(0,1,W,dtype=np.float32)[None,:,None]; a=a+25*np.clip((xx-0.86)/0.14,0,1); im=Image.fromarray(a.clip(0,255).astype(np.uint8)).convert('RGBA')
        elif t>=12.4 and zoom_at(t)>1.0001:
            z=zoom_at(t); k=(z-1)/0.25; cw,ch=W/z,H/z                      # centre glides from frame centre to the cold-open crop
            x0=min(max((0.5+(CX-0.5)*k)*W-cw/2,0),W-cw); y0=min(max((0.5+(CY-0.5)*k)*H-ch/2,0),H-ch)
            im=room.transform((W,H),Image.EXTENT,(x0,y0,x0+cw,y0+ch),resample=Image.BICUBIC).convert('RGBA')
        else: im=cam(room,t,0.45).convert('RGBA')
    d=ImageDraw.Draw(im)
    if split:
        d.rectangle([0,955,W,965],fill=GOLD+(255,))
        lay=Image.new('RGBA',(W,H),(0,0,0,0)); g=ImageDraw.Draw(lay)
        pill(g,158,72,'YOUR DAY',fLab,5,CREAM+(255,)); pill(g,146,1036,'HIS DAY',fLab,5,GOLD+(255,))
        im.alpha_composite(lay)
        for t0,t1,txt in SPLITCAP:
            if t0<=t<t1:
                lay=Image.new('RGBA',(W,H),(0,0,0,0)); g=ImageDraw.Draw(lay); pill(g,540,960,txt,fCap,5,CREAM+(255,),outline=GOLD+(255,),h=100)
                with_shadow(im,pop_layer(lay,t,t0,540,960),12,0.5)
    else: title(im,t)
    # story clock
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); g=ImageDraw.Draw(lay)
    cx,cy=(928,1036) if split else (928,1760)
    pill(g,cx,cy,clock_txt(m['min']),fClk,3,GOLD+(255,),bg=INK+(205,),padx=22,h=74); im.alpha_composite(lay)
    # CLICK as the door latches, JINGLE at the handle
    for t0,t1,txt,dx,dy,rot,fnt in ((0.28,0.75,'CLICK',40,-150,7,fJ2),(6.38,7.35,'JINGLE',40,-100,-6,fJ)):
        if t0<=t<t1 and not lie:
            kx,ky=m['knob']; jx=min(max(kx+dx,150),900); jy=min(max(ky+dy,520),1500)
            lay=Image.new('RGBA',(W,H),(0,0,0,0)); g=ImageDraw.Draw(lay); pill(g,jx,jy,txt,fnt,6,INK+(255,),bg=GOLD+(250,),h=fnt.size+30)
            lay=lay.rotate(rot,center=(jx,jy),resample=Image.BICUBIC); with_shadow(im,pop_layer(lay,t,t0,jx,jy,0.12),10,0.5)
    # CTA
    if t>=9.8:
        lay=Image.new('RGBA',(W,H),(0,0,0,0)); g=ImageDraw.Draw(lay); pill(g,540,1630,'TAG THE PERSON YOUR DOG WAITS FOR',fCTA,1,CREAM+(255,),bg=INK+(235,),outline=GOLD+(255,),h=92,padx=26)
        with_shadow(im,pop_layer(lay,t,9.8,540,1630),12,0.5)
    # impact = contrast punch in grade() + zoom/shake
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); g=ImageDraw.Draw(lay); wm='SLOW LIGHT'; ww=sw(g,wm,fWm,10); spaced(g,540-ww/2,1852,wm,fWm,(230,220,200,150),10); im.alpha_composite(lay)
    return im.convert('RGB')
if __name__=='__main__':
    out=sys.argv[1] if len(sys.argv)>1 else 'output/he-waits-all-day.mp4'; aud=sys.argv[2] if len(sys.argv)>2 else 'output/mix.wav'
    if len(sys.argv)>3:
        for t in sys.argv[3].split(','): frame(round(float(t)*FPS)).save(out.replace('.jpg',f'_{t}.jpg'),quality=92)
        sys.exit()
    ain=[] if aud=='none' else ['-i',aud]; aopt=[] if aud=='none' else ['-c:a','aac','-b:a','192k','-shortest']
    ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',*ain,
        '-c:v','libx264','-preset','slow','-crf','19','-pix_fmt','yuv420p','-profile:v','high','-maxrate','9M','-bufsize','18M',*aopt,'-movflags','+faststart',out],stdin=subprocess.PIPE)
    for f in range(N): ff.stdin.write(frame(f).tobytes())
    ff.stdin.close(); ff.wait(); print('wrote',out)
