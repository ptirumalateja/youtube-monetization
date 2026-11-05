"""Chief-editor VO cut: keep chosen phrases from the two takes, re-space the silences, write vo_cut.wav + vo_timeline.json."""
import json, subprocess, numpy as np, soundfile as sf, os
D = os.path.dirname(os.path.abspath(__file__)); SR = 48000
def load(take):
    wav = f"{D}/take_{take}.wav"
    if not os.path.exists(wav):
        subprocess.run(["ffmpeg","-y","-v","error","-i",f"{D}/take_{take}.mp3","-ar",str(SR),"-ac","1",wav],check=True)
    a,_ = sf.read(wav); return a
A = {t: load(t) for t in ("natural","creative")}
W = {t: [w for w in json.load(open(f"{D}/stt_{t}.json"))["words"] if w["type"]=="word"] for t in A}
def span(take, first, last, nth=0):
    """time span from the nth occurrence of word `first` to the next `last` after it"""
    ws = W[take]; hits=[i for i,w in enumerate(ws) if w["text"].strip(".,—?").lower()==first.strip(".,—?").lower()]
    i = hits[nth]; j = next(k for k in range(i,len(ws)) if ws[k]["text"].strip(".,—?").lower()==last.strip(".,—?").lower())
    return ws[i]["start"], ws[j]["end"]
# (key, take, first word, last word, nth, gap AFTER in s)
CUT = [
 ("warned",  "natural","They","warned",0, 0.30),
 ("notopen", "natural","not","it.",0, 0.55),
 ("six",     "natural","six","vaults",0, 0.30),
 ("five",    "natural","In","five",1, 0.25),
 ("idols",   "natural","Gold","idols",0, 0.15),
 ("chain",   "natural","An","gold",0, 0.15),
 ("sacks",   "natural","Sacks","coins",0, 0.15),
 ("diamonds","natural","Diamonds","Diamonds",0, 0.12),
 ("crowns",  "natural","Crowns","Crowns",0, 0.45),
 ("lakh",    "natural","More","rupees",0, 0.40),
 ("temple",  "natural","Padmanabhaswamy","Temple",0, 0.85),
 ("then",    "natural","Then","B.",0, 0.45),
 ("handle",  "natural","No","handle",0, 0.30),
 ("lock",    "natural","No","lock",1, 0.30),
 ("keyhole", "natural","No","keyhole",2, 0.40),
 ("legend",  "natural","Legend","Bandham",0, 0.35),
 ("chant",   "natural","Only","it.",0, 0.55),
 ("wrong",   "creative","Get","wrong",0, 1.10),
 ("weeks",   "natural","Weeks","dead",0, 0.50),
 ("warning", "natural","Believers","warning",0, 0.60),
 ("never",   "natural","Vault","since",1, 1.00),
 ("would",   "natural","Would","you",0, 0.80),
]
PRE, POST = 0.05, 0.12
out=[]; tl=[]; t=0.35   # tiny lead-in so the first frame isn't mid-breath
out.append(np.zeros(int(t*SR)))
for key,take,a,b,nth,gap in CUT:
    s,e = span(take,a,b,nth); s=max(0,s-PRE); e=e+POST
    seg = A[take][int(s*SR):int(e*SR)].copy()
    f=int(0.012*SR); seg[:f]*=np.linspace(0,1,f); seg[-f*3:]*=np.linspace(1,0,f*3)
    tl.append({"key":key,"start":round(t,3),"end":round(t+len(seg)/SR,3)})
    out.append(seg); t+=len(seg)/SR
    out.append(np.zeros(int(gap*SR))); t+=gap
y=np.concatenate(out); y/=max(1e-6,np.abs(y).max()/0.89)
TEMPO=1.12
sf.write(f"{D}/vo_raw.wav", y, SR, subtype="PCM_24")
subprocess.run(["ffmpeg","-y","-v","error","-i",f"{D}/vo_raw.wav","-af",f"rubberband=tempo={TEMPO}:pitch=0.985:formant=preserved","-c:a","pcm_s24le",f"{D}/vo_cut.wav"],check=True)
y,_=sf.read(f"{D}/vo_cut.wav")
for x in tl: x["start"]=round(x["start"]/TEMPO,3); x["end"]=round(x["end"]/TEMPO,3)
json.dump(tl, open(f"{D}/vo_timeline.json","w"), indent=1)
print("total", round(len(y)/SR,2)); [print(f"{x['start']:6.2f} {x['end']:6.2f} {x['key']}") for x in tl]
