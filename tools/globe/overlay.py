import subprocess,numpy as np
from PIL import Image,ImageDraw,ImageFont
W,H,N=1080,1920,72
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f_title=ImageFont.truetype(B,78); f_cnt=ImageFont.truetype(B,46); f_lbl=ImageFont.truetype(R,30)
dec=subprocess.Popen(["ffmpeg","-v","error","-i","hook_clean.mp4","-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r","24","-i","-","-c:v","libx264","-crf","16","-pix_fmt","yuv420p","hook_preview.mp4"],stdin=subprocess.PIPE)
for i in range(N):
    fr=Image.frombytes("RGB",(W,H),dec.stdout.read(W*H*3)); d=ImageDraw.Draw(fr)
    # title: centred in the black space above the globe, appears from frame 0
    for k,line in enumerate(["INDIA IS ABOUT","TO HIT ASIA"]):
        w=d.textlength(line,font=f_title); d.text(((W-w)/2,330+k*96),line,font=f_title,fill=(255,255,255),stroke_width=3,stroke_fill=(0,0,0))
    # rolling year counter
    yrs=74_000_000-round(i*16_000_000/(N-1)/10000)*10000
    c=f"{yrs:,}"; w=d.textlength(c,font=f_cnt); d.text(((W-w)/2,170),c,font=f_cnt,fill=(255,196,90))
    l="years ago"; w=d.textlength(l,font=f_lbl); d.text(((W-w)/2,225),l,font=f_lbl,fill=(220,220,220))
    enc.stdin.write(fr.tobytes())
enc.stdin.close(); enc.wait(); dec.wait()
