# v2: payoff-first hook. 0-2.65 s cold open on the strict payoff (tight camera, output/hook), 2.65-3.15 s rewind,
# then the full split-screen story (compose.py, bigger text) with a headline in the top padding.
# python3 compose_v2.py [out.mp4] [audio.wav]      stills: python3 compose_v2.py out.jpg 0,0.5,1
import sys, json, math, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import compose as C
FPS=30; W,H=1080,1920
HOOK_T0=6.15; HOOK_LEN=2.58; RW_LEN=0.5; STORY0=HOOK_LEN+RW_LEN; DUR=STORY0+C.DUR; N=round(DUR*FPS)
HY=300; HH=1320                                   # hook frame placement (1080x1320)
FB=C.FB; f=lambda s:ImageFont.truetype(FB,s)
fHead=f(74); fClkBig=f(150); fPMBig=f(54); fTop=f(62); fHB=f(44); fX=f(96)
hookMeta=json.load(open('output/hook/meta.json'))['frames']
# hook lines in strict time (same as v1 payoff)
HLINES=[('kid','!',6.82,8.8,'C','x'),('par',"YOU COULD'VE JUST ASKED.",6.95,8.8,'R','b'),('kid','I DID.',7.95,8.8,'C','b')]

def glow_text(im,xy,txt,font,col,blur=14,anchor='la'):
    gl=Image.new('RGBA',im.size,(0,0,0,0)); g=ImageDraw.Draw(gl); g.text(xy,txt,font=font,fill=col+(255,),anchor=anchor)
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(blur))); im.alpha_composite(gl)

def centered(im,y,txt,font,col,sp=4,alpha=255):
    d=ImageDraw.Draw(im); w=C.spaced_w(d,txt,font,sp); C.spaced(d,(540-w/2,y),txt,font,col+(alpha,),sp)

def hook_frame(t):
    st=HOOK_T0+t; fi=min(round(st*FPS),C.N-1)
    im=Image.new('RGBA',(W,H),(0,0,0,255))
    p=Image.open(f'output/hook/frames/f{fi:05d}.jpg').convert('RGBA')
    z=1.0+0.05*(t/HOOK_LEN)                        # slow push-in
    pz=p.resize((round(W*z),round(HH*z)),Image.BICUBIC); ox=(pz.width-W)//2; oy=(pz.height-HH)//2
    im.paste(pz.crop((ox,oy,ox+W,oy+HH)),(0,HY))
    # bubbles (bigger font, head positions from the hook camera)
    oldB,oldM,oldX,oldL=C.fBub,C.meta,C.fBig,C.BUB_LIFT; C.fBub,C.fBig,C.BUB_LIFT=fHB,fX,80
    hm=[{k:([round((v[0]-W/2)*z+W/2),round((v[1]-(100 if k=='kid' else 0)-HH/2)*z+HH/2)] if k in('kid','par') else v) for k,v in fr.items()} for fr in hookMeta]
    C.meta={'hook':hm}
    for who,txt,t0,t1,side,kind in HLINES: C.bubble(im,st,HY,('hook',who,txt,t0,t1,side,kind))
    C.fBub,C.meta,C.fBig,C.BUB_LIFT=oldB,oldM,oldX,oldL
    # headline: CAUGHT AT / 1:42 AM
    centered(im,58,'CAUGHT AT',fHead,C.CREAM,8)
    d=ImageDraw.Draw(im); tw=d.textlength('1:42',font=fClkBig); pw=d.textlength('AM',font=fPMBig); x0=540-(tw+14+pw)/2
    glow_text(im,(x0,128),'1:42',fClkBig,C.RED,16); glow_text(im,(x0+tw+14,128+84),'AM',fPMBig,C.RED,10)
    # white flash when the lamp snaps on
    fl=max(0.0,1-abs(st-6.43)/0.07)*0.35
    out=im.convert('RGB')
    if fl>0:
        box=(0,HY,W,HY+HH); out.paste(Image.blend(out.crop(box),Image.new('RGB',(W,HH),(255,236,200)),fl),box[:2])
    return out

def rewind_frame(t):
    u=t/RW_LEN; st=(HOOK_T0+HOOK_LEN)*(1-u)**1.4      # strict/chill time racing back to 0
    im=C.frame(min(round(st*FPS),C.N-1)).convert('RGBA')
    bands=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(bands)
    for i in range(5):                                # VHS tracking bands, inside the panels only
        y=C.PT+int((u*1900+i*263)%(C.PB+C.PH-C.PT)); d.rectangle([0,y,W,y+6+i%3*5],fill=(210,210,225,55))
    im.alpha_composite(bands)
    centered(im,150,'◀◀ REWIND',fTop,C.CREAM,6)
    return im.convert('RGB')

def story_frame(t):
    im=C.frame(min(round(t*FPS),C.N-1)).convert('RGBA')
    fa=max(0.0,min(1.0,(11.15-t)/1.15)) if t>10.0 else 1.0
    txt='SAME KID. SAME QUESTION.' if t<8.6 else 'WHICH ONE WAS YOURS?'
    t_in=0.0 if t<8.6 else 8.6; a=min(1,(t-t_in)/0.15)*fa
    centered(im,150,txt,fTop,C.CREAM,3,int(255*a))
    return im.convert('RGB')

def frame(i):
    t=i/FPS
    if t<HOOK_LEN: return hook_frame(t)
    if t<STORY0: return rewind_frame(t-HOOK_LEN)
    return story_frame(t-STORY0)

if __name__=='__main__':
    out=sys.argv[1] if len(sys.argv)>1 else 'output/strict-vs-chill_v2.mp4'
    if out.endswith('.jpg'):
        for t in sys.argv[2].split(','): frame(round(float(t)*FPS)).save(out.replace('.jpg',f'_{t}.jpg'),quality=90)
        sys.exit()
    aud=sys.argv[2] if len(sys.argv)>2 else 'output/mix_v2.wav'
    ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',aud,
        '-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-profile:v','high','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',out],stdin=subprocess.PIPE)
    for i in range(N): ff.stdin.write(frame(i).tobytes())
    ff.stdin.close(); ff.wait(); print('wrote',out,N/FPS,'s')
