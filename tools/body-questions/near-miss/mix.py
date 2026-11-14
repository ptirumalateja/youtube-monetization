import json,subprocess,sys
V=sys.argv[1]  # mark|jessica
DUR=22.4
SLOTS=[0.47, 1.35, 2.5, 4.45, 5.55, 6.8, 8.8, 10.35, 12.45, 13.15, 14.65, 15.7, 18.0, 20.25]
w=json.load(open(f'/home/user/nm/vo/{V}11_words.json'))
lines=[];cur=[]
for x in w:
    cur.append(x)
    if x[0][-1] in '.?': lines.append((cur[0][1],cur[-1][2]));cur=[]
assert len(lines)==14,len(lines)
src=f'/home/user/nm/vo/{V}11_tight.wav'
SFX='/home/user/nm/sfx'
CUES=[('brain_zap',2.50,-7),('whip',4.38,-10),('foot_scrape',4.50,-6),
('heart_slam',7.29,-3),('whip',8.48,-8),('iris_open',8.95,-6),('sugar_rush',10.30,-7),('whip',12.08,-8),('tunnel',12.35,-6),('bullet_time',12.95,-5),('glitch_snap',14.58,-7),
('memory_frames',15.60,-9),('screech_stop',18.05,-3),('rain_start',18.08,-6)]
ins=[];fil=[];lab=[]
for i,((a,b),st) in enumerate(zip(lines,SLOTS)):
    ins+=['-i',src];ms=int(st*1000)
    fil.append(f'[{i}:a]atrim={max(0,a-0.03):.3f}:{b+0.12:.3f},asetpts=PTS-STARTPTS,afade=t=out:st={b-a+0.07:.3f}:d=0.05,adelay={ms}|{ms}[v{i}]');lab.append(f'[v{i}]')
n=len(lines)
fil.append(''.join(lab)+f'amix=inputs={n}:normalize=0,apad=whole_dur={DUR}[vo]')
ins+=['-i',f'{SFX}/rain_amb.mp3','-i',f'{SFX}/rain_amb.mp3']
fil.append(f'[{n}:a]aresample=48000,aloop=loop=2:size=480000,atrim=0:{DUR},volume=-60dB,afade=t=in:d=0.2,afade=t=out:st={DUR-1.2}:d=1.2[dr]')
fil.append(f'[{n+1}:a]aresample=48000,atrim=0:4.3,volume=-22dB,afade=t=in:d=0.2,afade=t=out:st=3.3:d=1,adelay=18100|18100[rn]')
fl=['[dr]','[rn]']
for k,(f,st,g) in enumerate(CUES):
    ins+=['-i',f'{SFX}/{f}.wav' if f.endswith('_cut') else f'{SFX}/{f}.mp3'];ms=int(st*1000);j=n+2+k
    fil.append(f'[{j}:a]aresample=48000,volume={g}dB,adelay={ms}|{ms}[s{k}]');fl.append(f'[s{k}]')
fil.append(''.join(fl)+f'amix=inputs={len(fl)}:normalize=0[fx]')
fil.append('[vo]asplit[vo1][vo2]')
fil.append('[fx][vo2]sidechaincompress=threshold=0.05:ratio=4:attack=5:release=250[fxd]')
fil.append(f'[vo1][fxd]amix=inputs=2:normalize=0,atrim=0:{DUR},loudnorm=I=-14:TP=-1.0:LRA=11[out]')
subprocess.run(['ffmpeg','-y','-loglevel','error',*ins,'-filter_complex',';'.join(fil),'-map','[out]','-ar','48000',f'{V}_mix.wav'],check=True)
print('ok',V)
