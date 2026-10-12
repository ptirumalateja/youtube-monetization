import subprocess,sys,numpy as np
# overlay.py <in.mp4> <out.mp4> <t_start_Ma|-> <t_end_Ma|-> ["TITLE LINE 1|TITLE LINE 2"]   ('-' = no year counter)
IN,OUTF=sys.argv[1],sys.argv[2]; T0=None if sys.argv[3]=="-" else float(sys.argv[3]); T1=None if sys.argv[4]=="-" else float(sys.argv[4])
TITLE=(sys.argv[5] if len(sys.argv)>5 else "INDIA IS ABOUT|TO HIT ASIA").split("|")
from PIL import Image,ImageDraw,ImageFont
W,H=1080,1920
N=int(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=nb_read_frames','-of','csv=p=0',sys.argv[1]]).decode().strip())
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f_title=ImageFont.truetype(B,78); f_cnt=ImageFont.truetype(B,46); f_lbl=ImageFont.truetype(R,30)
dec=subprocess.Popen(["ffmpeg","-v","error","-i",IN,"-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r","24","-i","-","-c:v","libx264","-crf","16","-pix_fmt","yuv420p",OUTF],stdin=subprocess.PIPE)
for i in range(N):
    fr=Image.frombytes("RGB",(W,H),dec.stdout.read(W*H*3)); d=ImageDraw.Draw(fr)
    # title: centred in the black space above the globe, appears from frame 0
    for k,line in enumerate(TITLE):
        w=d.textlength(line,font=f_title); d.text(((W-w)/2,330+k*96),line,font=f_title,fill=(255,255,255),stroke_width=3,stroke_fill=(0,0,0))
    # rolling year counter
    if T0 is None: enc.stdin.write(fr.tobytes()); continue
    yrs=int(round((T0-(T0-T1)*i/(N-1))*1e6/1e5)*1e5)
    c=f"{yrs:,}"; w=d.textlength(c,font=f_cnt); d.text(((W-w)/2,170),c,font=f_cnt,fill=(255,196,90))
    l="years ago"; w=d.textlength(l,font=f_lbl); d.text(((W-w)/2,225),l,font=f_lbl,fill=(220,220,220))
    enc.stdin.write(fr.tobytes())
enc.stdin.close(); enc.wait(); dec.wait()
