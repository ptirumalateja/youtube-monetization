import re,subprocess,sys
src,out,cap,tempo=sys.argv[1],sys.argv[2],float(sys.argv[3]),float(sys.argv[4])
log=subprocess.run(["ffmpeg","-hide_banner","-i",src,"-af","silencedetect=noise=-38dB:d=0.12","-f","null","-"],capture_output=True,text=True).stderr
st=[float(x) for x in re.findall(r"silence_start: ([0-9.]+)",log)];en=[float(x) for x in re.findall(r"silence_end: ([0-9.]+)",log)]
dur=float(re.search(r"Duration: (\d+):(\d+):([0-9.]+)",log).groups()[2])+60*float(re.search(r"Duration: (\d+):(\d+)",log).groups()[1])
keep=[];p=0.0
for a,b in zip(st,en):
    if a<0.05: p=max(0,b-0.03); continue
    if b>=dur-0.05: keep.append((p,a+0.1)); p=None; break
    keep.append((p,a+cap/2)); p=b-cap/2
if p is not None: keep.append((p,dur))
fc="".join(f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS[s{i}];" for i,(a,b) in enumerate(keep))
fc+="".join(f"[s{i}]" for i in range(len(keep)))+f"concat=n={len(keep)}:v=0:a=1,rubberband=tempo={tempo}:pitchq=quality[o]"
subprocess.run(["ffmpeg","-y","-loglevel","error","-i",src,"-filter_complex",fc,"-map","[o]","-ar","48000",out],check=True)
