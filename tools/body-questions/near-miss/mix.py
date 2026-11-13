import json,subprocess,sys
V=sys.argv[1]  # mark|jessica
DUR=23.4
SLOTS=[0.15,1.0,3.0,4.95,6.05,7.4,9.3,10.85,13.15,14.1,15.65,16.7,19.0,21.25]
w=json.load(open(f'/home/user/nm/vo/{V}11_words.json'))
lines=[];cur=[]
for x in w:
    cur.append(x)
    if x[0][-1] in '.?': lines.append((cur[0][1],cur[-1][2]));cur=[]
assert len(lines)==14,len(lines)
src=f'/home/user/nm/vo/{V}11_tight.wav'
SFX='/home/user/nm/sfx'
CUES=[('brain_zap',3.0,-7),('whip',4.88,-10),('foot_scrape',5.0,-6),
('heart_slam',7.4,-3),('whip',8.98,-8),('iris_open',9.45,-6),('sugar_rush',10.8,-7),('whip',12.58,-8),('tunnel',12.85,-6),('bullet_time',13.95,-5),('glitch_snap',15.58,-7),
('memory_frames',16.6,-9),('screech_stop',19.05,-3),('rain_start',19.08,-6)]
ins=[];fil=[];lab=[]
for i,((a,b),st) in enumerate(zip(lines,SLOTS)):
    ins+=['-i',src];ms=int(st*1000)
    fil.append(f'[{i}:a]atrim={max(0,a-0.03):.3f}:{b+0.12:.3f},asetpts=PTS-STARTPTS,afade=t=out:st={b-a+0.07:.3f}:d=0.05,adelay={ms}|{ms}[v{i}]');lab.append(f'[v{i}]')
n=len(lines)
fil.append(''.join(lab)+f'amix=inputs={n}:normalize=0,apad=whole_dur={DUR}[vo]')
ins+=['-i',f'{SFX}/rain_amb.mp3','-i',f'{SFX}/rain_amb.mp3']
fil.append(f'[{n}:a]aresample=48000,aloop=loop=2:size=480000,atrim=0:{DUR},volume=-60dB,afade=t=in:d=0.2,afade=t=out:st={DUR-1.2}:d=1.2[dr]')
fil.append(f'[{n+1}:a]aresample=48000,atrim=0:4.3,volume=-22dB,afade=t=in:d=0.2,afade=t=out:st=3.3:d=1,adelay=19100|19100[rn]')
fl=['[dr]','[rn]']
for k,(f,st,g) in enumerate(CUES):
    ins+=['-i',f'{SFX}/{f}.mp3'];ms=int(st*1000);j=n+2+k
    fil.append(f'[{j}:a]aresample=48000,volume={g}dB,adelay={ms}|{ms}[s{k}]');fl.append(f'[s{k}]')
fil.append(''.join(fl)+f'amix=inputs={len(fl)}:normalize=0[fx]')
fil.append('[vo]asplit[vo1][vo2]')
fil.append('[fx][vo2]sidechaincompress=threshold=0.05:ratio=4:attack=5:release=250[fxd]')
fil.append(f'[vo1][fxd]amix=inputs=2:normalize=0,atrim=0:{DUR},loudnorm=I=-14:TP=-1.0:LRA=11[out]')
subprocess.run(['ffmpeg','-y','-loglevel','error',*ins,'-filter_complex',';'.join(fil),'-map','[out]','-ar','48000',f'{V}_mix.wav'],check=True)
print('ok',V)
