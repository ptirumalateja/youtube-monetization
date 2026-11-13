import json,subprocess,re
src='liam.mp3'
out=subprocess.run(['ffmpeg','-hide_banner','-i',src,'-af','silencedetect=n=-40dB:d=0.25','-f','null','-'],capture_output=True,text=True).stderr
st=[float(x) for x in re.findall(r'silence_start: ([\d.]+)',out)];en=[float(x) for x in re.findall(r'silence_end: ([\d.]+)',out)]
KEEP=0.22
segs=[];t=0.0;remap=[]
for s,e in zip(st,en):
    if e>25.9: break
    mid=(s+e)/2; segs.append((t,s+KEEP/2)); t=e-KEEP/2
segs.append((t,26.0))
# build concat
f=';'.join(f'[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS[s{i}]' for i,(a,b) in enumerate(segs))
f+=';'+''.join(f'[s{i}]' for i in range(len(segs)))+f'concat=n={len(segs)}:v=0:a=1[o]'
subprocess.run(['ffmpeg','-y','-loglevel','error','-i',src,'-filter_complex',f,'-map','[o]','-ar','48000','vo_tight.wav'],check=True)
def mapt(x):
    acc=0
    for a,b in segs:
        if x<=b: return acc+max(0,x-a)
        acc+=b-a
    return acc
al=json.load(open('liam.json'))
chars=al['characters'];s0=al['character_start_times_seconds'];e0=al['character_end_times_seconds']
words=[];cur='';ws=None
for ch,a,b in zip(chars,s0,e0):
    if ch.strip()=='' :
        if cur: words.append((cur,mapt(ws),mapt(pb)));cur=''
        continue
    if not cur: ws=a
    cur+=ch;pb=b
if cur: words.append((cur,mapt(ws),mapt(pb)))
json.dump(words,open('words.json','w'))
for w in words: print(f'{w[1]:6.2f} {w[2]:6.2f} {w[0]}')
