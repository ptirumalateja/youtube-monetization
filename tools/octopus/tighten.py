# Cut VO into phrases at long gaps, rejoin with capped pauses, then tempo.
import json,subprocess,sys
import os
src=os.environ.get("VOSRC","/tmp/claude-0/oct/vo/a.mp3")
d=json.load(open(src+".stt.json"))
ws=[w for w in d["words"] if w["type"]=="word"]
# pause cap after the word ending a phrase (index-based on word text match)
CAP={"గుండెలు,":0.18,"రక్తం.":0.26,"octopus.":0.26,"ఉంటే,":0.14,"అంటారు.":0.22,"మాయమవుతుంది.":0.34,"సులభం.":0.26,"లేదు.":0.28,"గ్రహిస్తుంది.":0.26,"ఉంటుంది.":0.24}
segs=[];start=max(0,ws[0]["start"]-0.06)
for i,w in enumerate(ws):
    last=i==len(ws)-1
    if last or (ws[i+1]["start"]-w["end"]>0.3):
        end=w["end"]+0.08
        pause=CAP.get(w["text"],0.12) if not last else 0
        segs.append((start,end,pause,w["text"]))
        if not last: start=ws[i+1]["start"]-0.06
fl=[];t=0;out=[]
for i,(a,b,p,txt) in enumerate(segs):
    out.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={b-a-0.03}:d=0.03,apad=pad_dur={p}[s{i}]")
    print(f"{t:6.2f} {txt}"); t+=b-a+p
fc=";".join(out)+";"+"".join(f"[s{i}]" for i in range(len(segs)))+f"concat=n={len(segs)}:v=0:a=1,rubberband=tempo={sys.argv[1]}:pitchq=quality:transients=crisp,aresample=48000[o]"
subprocess.run(["ffmpeg","-v","error","-y","-i",src,"-filter_complex",fc,"-map","[o]","-ac","1","-c:a","pcm_s16le",os.environ.get("VOOUT","/tmp/claude-0/oct/vo.wav")],check=True)
print("tight",t,"final",t/float(sys.argv[1]))
