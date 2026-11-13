import json,subprocess,re,sys
n=sys.argv[1];KEEP=float(sys.argv[2]);src=f'{n}_raw.mp3'
dur=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',src],capture_output=True,text=True).stdout)
out=subprocess.run(['ffmpeg','-hide_banner','-i',src,'-af','silencedetect=n=-40dB:d=0.25','-f','null','-'],capture_output=True,text=True).stderr
st=[float(x) for x in re.findall(r'silence_start: ([\d.]+)',out)];en=[float(x) for x in re.findall(r'silence_end: ([\d.]+)',out)]
segs=[];t=0.0
for s,e in zip(st,en):
    if s<0.05: t=max(0,e-0.05);continue
    if e>=dur-0.05: break
    segs.append((t,s+KEEP/2)); t=e-KEEP/2
segs.append((t,min(dur,(st[-1]+0.15) if st and st[-1]>dur-2 and len(en)<len(st) else dur)))
f=';'.join(f'[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS[s{i}]' for i,(a,b) in enumerate(segs))
f+=';'+''.join(f'[s{i}]' for i in range(len(segs)))+f'concat=n={len(segs)}:v=0:a=1[o]'
subprocess.run(['ffmpeg','-y','-loglevel','error','-i',src,'-filter_complex',f,'-map','[o]','-ar','48000',f'{n}_tight.wav'],check=True)
def mapt(x):
    acc=0
    for a,b in segs:
        if x<=b: return acc+max(0,x-a)
        acc+=b-a
    return acc
al=json.load(open(f'{n}_align.json'))
words=[];cur='';ws=None
for ch,a,b in zip(al['characters'],al['character_start_times_seconds'],al['character_end_times_seconds']):
    if ch.strip()=='':
        if cur: words.append((cur,round(mapt(ws),3),round(mapt(pb),3)));cur=''
        continue
    if not cur: ws=a
    cur+=ch;pb=b
if cur: words.append((cur,round(mapt(ws),3),round(mapt(pb),3)))
json.dump(words,open(f'{n}_words.json','w'))
print(n,round(sum(b-a for a,b in segs),2))
