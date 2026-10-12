"""Assemble India Episode 1 (30 s) from clips + voiceover.
usage: python3 assemble_ep1.py <assets_dir> <out.mp4>
Missing clips (seafloor fold, fossil) are replaced by labelled placeholder cards until they exist in <assets_dir>.
Timings are locked to the ElevenLabs v3 voiceover (india_ep1_vo_v3.mp3) word timestamps."""
import os,subprocess,sys,tempfile
A,OUT=sys.argv[1],sys.argv[2]; T=tempfile.mkdtemp(); FPS=24; W,H=1080,1920
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def ff(*a): subprocess.run(["ffmpeg","-v","error","-y",*a],check=True)
def dur(f): return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f]))
def esc(t): return t.replace("\\","\\\\").replace(":","\\:").replace("'","\u2019")
def text(t,y=330,size=74,start=0,end=99):
    return (f"drawtext=fontfile={FONT}:text='{esc(t)}':fontsize={size}:fontcolor=white:borderw=4:bordercolor=black@0.85:"
            f"x=(w-text_w)/2:y={y}:enable='between(t,{start},{end})'")
def seg(name,src,length,ss=0,speed=None,vf_extra="",reverse=False):
    """Cut/stretch a source clip to exactly `length` seconds."""
    out=f"{T}/{name}.mp4"
    if src is None or not os.path.exists(src):
        label={"fold":"SEAFLOOR FOLDS INTO|THE HIMALAYAS|(Blender shot - to build)","fossil":"FOSSIL CLOSE-UP|(stock / AI - to source)"}.get(name.split("_",1)[-1],name)
        lines=label.split("|"); vf=",".join(text(l,y=820+i*110,size=62 if i<2 else 44) for i,l in enumerate(lines))
        ff("-f","lavfi","-i",f"color=c=0x1b1f2a:s={W}x{H}:r={FPS}:d={length}","-vf",vf+(","+vf_extra if vf_extra else ""),"-c:v","libx264","-pix_fmt","yuv420p",out)
        return out
    d=dur(src)-ss; sp=speed or d/length
    chain=[f"trim=start={ss}",("reverse," if reverse else "")+f"setpts=(PTS-STARTPTS)*{1/sp:.5f}",f"fps={FPS}",f"scale={W}:{H}:flags=lanczos","setsar=1"]
    if vf_extra: chain.append(vf_extra)
    ff("-i",src,"-vf",",".join(c for c in chain if c)+f",trim=duration={length}","-an","-c:v","libx264","-crf","16","-pix_fmt","yuv420p",out)
    return out
P=lambda f:os.path.join(A,f)
segs=[
 seg("A_hook",P("race_preview.mp4"),4.60),                                                        # 0.00 India racing, title + counter
 seg("B_flash",P("shot7_clean.mp4"),0.25,ss=3.6,vf_extra="eq=brightness=0.35:contrast=1.3"),     # 4.60 impact flash
 seg("C_rewind",P("race_clean.mp4"),1.30,reverse=True,vf_extra=text("90 MILLION YEARS AGO",start=0.35)), # 4.85 rewind
 seg("D_madagascar",P("shot4_clean.mp4"),5.45,vf_extra=text("90 MILLION YEARS AGO",end=3.4)+","+text("20 CM A YEAR",start=3.5)),  # 6.15
 seg("E_collision",P("shot7_clean.mp4"),3.90,vf_extra=text("50 MILLION YEARS AGO")),               # 11.60
 seg("F_fold",P("fold.mp4"),4.30),                                                                 # 15.50
 seg("G_everest",P("everest.mp4"),3.40,vf_extra=text("EVEREST =")+","+text("ANCIENT SEAFLOOR",y=420)),       # 19.80
 seg("H_fossil",P("fossil.mp4"),2.00),                                                             # 23.20
 seg("I_today",P("shot10_clean.mp4"),3.75,vf_extra=text("STILL MOVING")+","+text("~4 CM A YEAR",y=420)), # 25.20
]
open(f"{T}/list.txt","w").write("".join(f"file '{s}'\n" for s in segs))
ff("-f","concat","-safe","0","-i",f"{T}/list.txt","-c","copy",f"{T}/video.mp4")
total=dur(f"{T}/video.mp4")
# --- placeholder sound design (swap for Pixabay / YouTube Audio Library effects in the final)
def boom(t): return f"sine=f=42:d=1.8,volume='exp(-2.2*t)':eval=frame,adelay={int(t*1000)}|{int(t*1000)}"
sfx=[
 f"anoisesrc=c=brown:d=4.6:a=0.6,lowpass=f=140,afade=t=in:d=4.4,volume=0.9",                       # rising rumble
 boom(4.60), boom(14.56),                                                                            # impact flash, collision
 f"anoisesrc=c=pink:d=1.2:a=0.5,highpass=f=600,lowpass=f=5000,afade=t=in:d=0.5,afade=t=out:st=0.6:d=0.6,adelay=4850|4850",  # rewind whoosh
 f"anoisesrc=c=brown:d=0.5:a=0.8,bandpass=f=260:w=200,afade=t=out:st=0.05:d=0.45,adelay=6150|6150", # breakaway crack
 f"anoisesrc=c=brown:d=4.3:a=0.5,lowpass=f=180,afade=t=in:d=2,adelay=15500|15500",                  # grinding rumble
 f"anoisesrc=c=pink:d=3.4:a=0.35,lowpass=f=900,tremolo=f=0.4:d=0.6,afade=t=in:d=0.4,adelay=19800|19800", # summit wind
 f"sine=f=55:d=3.75,tremolo=f=1.1:d=0.8,volume=0.5,adelay=25200|25200",                              # low pulse
]
inputs=[]; [inputs.extend(["-f","lavfi","-i",s]) for s in sfx]
n=len(sfx); mix="".join(f"[{i+2}:a]aformat=sample_rates=48000:channel_layouts=stereo[s{i}];" for i in range(n))
mix+="".join(f"[s{i}]" for i in range(n))+f"amix=inputs={n}:normalize=0,volume=0.30[sfx];"
mix+="[1:a]loudnorm=I=-16:TP=-1.5,aformat=sample_rates=48000:channel_layouts=stereo[vo];"
mix+=f"[vo][sfx]amix=inputs=2:normalize=0,atrim=duration={total},loudnorm=I=-14:TP=-1.0[a]"
ff("-i",f"{T}/video.mp4","-i",P("india_ep1_vo_v3.mp3"),*inputs,"-filter_complex",mix,"-map","0:v","-map","[a]","-c:v","copy","-c:a","aac","-b:a","192k","-shortest",OUT)
print(f"done: {OUT} ({dur(OUT):.2f}s)")
