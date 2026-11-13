# Ramappa temple Telugu reel: EDL -> ffmpeg render.
import json,subprocess,glob,os,sys
C="/tmp/claude-0/ram/clips/ramappa/"
def clip(k): return glob.glob(C+k+"*.mp4")[0]
W="/tmp/claude-0/ram/work/"
TOTAL=26.6
# (out_start,out_end,clip,src_start, native_audio_gain)
EDL=[
 (0.00,0.36,"Craftsman_drops",9.0,0.5),       # payoff: brick floating
 (0.36,2.22,"Craftsman_drops",3.0,1.0),       # drop + splash (impact ~0.56)
 (2.22,4.36,"Visitors_viewing",7.0,0.35),     # temple, Telangana
 (4.36,5.76,"Ramappa_Temple_entrance",7.0,0.35), # madanika bracket
 (5.76,6.80,"Builders_constructing",0.6,0.35),
 (6.80,7.92,"Shiva_lingam",7.0,0.35),
 (7.92,9.70,"Builders_constructing",6.0,0.35),
 (9.70,11.00,"Craftsman_holding",0.8,0.35),
 (11.00,12.40,"Craftsman_holding",7.6,0.45),
 (12.40,14.66,"Workers_pouring",3.0,0.45),
 (14.66,15.92,"Stone_temple_sand",1.5,0.35),
 (15.92,17.94,"Ramappa_Temple_during",2.4,0.9),
 (17.94,19.44,"Ramappa_Temple_during",8.0,0.4),
 (19.44,21.86,"Visitors_viewing",0.5,0.35),
 (21.86,TOTAL,"Shiva_lingam",0.0,0.35),
]
if os.environ.get('EDL'):
    J=json.load(open(os.environ['EDL'])); EDL=[tuple(e) for e in J['edl']]; TOTAL=J['total']; ECT=J['endcard']; VOF=J['vo']
else: ECT=23.44; VOF=W+"vo.wav"; J={}
SB,S1,S2=J.get('sfx',[480,2050,15700])
inputs=[];fc=[]
for i,(a,b,k,s,g) in enumerate(EDL):
    d=b-a
    inputs+=["-ss",f"{s}","-t",f"{d+0.05}","-i",clip(k)]
    # zoom 1.16 top-anchored: drops Veo sparkle (y~1740) out of frame
    z="crop=931:1655:74:0,scale=1080:1920:flags=lanczos"
    if k=="Shiva_lingam": z+=",eq=gamma=1.18:saturation=1.05"
    fc.append(f"[{i}:v]{z},setsar=1,fps=30,trim=0:{d},setpts=PTS-STARTPTS,format=yuv420p[v{i}]")
    fc.append(f"[{i}:a]atrim=0:{d},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,volume={g},afade=t=in:d=0.03,afade=t=out:st={max(0,d-0.04)}:d=0.04[a{i}]")
n=len(EDL)
fc.append("".join(f"[v{i}]" for i in range(n))+f"concat=n={n}:v=1:a=0[vc]")
fc.append("".join(f"[a{i}]" for i in range(n))+f"concat=n={n}:v=0:a=1[nat]")
# caption overlays
caps=json.load(open(W+"caps/caps.json"))
k=n; last="vc"
for j,(a,b,p) in enumerate(caps):
    inputs+=["-i",p]; b=min(b,TOTAL)
    fc.append(f"[{last}][{k}:v]overlay=0:0:enable='between(t,{a},{b-0.001})'[o{j}]"); last=f"o{j}"; k+=1
inputs+=["-loop","1","-t",str(TOTAL),"-i",W+"caps/endcard.png"]
fc.append(f"[{k}:v]format=rgba,fade=t=in:st={ECT}:d=0.25:alpha=1[ec]")
fc.append(f"[{last}][ec]overlay=0:0:enable='gte(t,{ECT})'[vout]"); k+=1
# audio
SFX="/tmp/claude-0/ram/repo/tools/sfxlib/"
inputs+=["-i",VOF]; vo=k; k+=1
inputs+=["-i",W+"music.mp3"]; mu=k; k+=1
inputs+=["-i",SFX+"722633__chakong__cinematic-braaam.wav"]; br=k; k+=1
inputs+=["-i",SFX+"649445__audiopapkin__cinematic-woosh-sfx-015.wav"]; wo=k; k+=1
fc.append(f"[{vo}:a]aresample=48000,aformat=channel_layouts=stereo,adelay=0|0,volume=1.0,apad=whole_dur={TOTAL}[vo]")
fc.append(f"[vo]asplit[vo1][vo2]")
fc.append(f"[{mu}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{TOTAL},volume={os.environ.get("MUSIC","0.30")},afade=t=out:st={TOTAL-1.2}:d=1.2[mu]")
fc.append(f"[nat][mu]amix=inputs=2:normalize=0[bed]")
fc.append(f"[bed][vo1]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=300[bedd]")
fc.append(f"[{br}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:3,volume=0.55,afade=t=out:st=2.2:d=0.8,adelay={SB}|{SB}[br]")
fc.append(f"[{wo}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:1.2,volume=0.35,asplit=2[w1][w2]")
fc.append(f"[w1]adelay={S1}|{S1}[w1d];[w2]adelay={S2}|{S2}[w2d]")
fc.append(f"[bedd][vo2][br][w1d][w2d]amix=inputs=5:normalize=0:duration=first,atrim=0:{TOTAL},loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
out=sys.argv[1] if len(sys.argv)>1 else W+"ramappa_te.mp4"
cmd=["ffmpeg","-v","error","-y",*inputs,"-filter_complex",";".join(fc),"-map","[vout]","-map","[aout]","-t",str(TOTAL),
     "-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p","-r","30","-c:a","aac","-b:a","192k","-movflags","+faststart",out]
subprocess.run(cmd,check=True); print("done",out)
