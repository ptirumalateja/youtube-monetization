#!/usr/bin/env python3
"""Skeleton Lake V2: faster hard cuts with impact effects, eerie global grade.
Usage: build2.py SRC_DIR OUT_DIR  -> OUT_DIR/picture.mp4 (ungraded shots + global grade/fog/grain)"""
import subprocess, sys, os, math
SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
C = {
 'skull':  'Archaeological_reconstruction_of…_b750b9e6_1080p.mp4',
 'shore':  'Camera_panning_across_lake_ac6a0ce2_1080p.mp4',
 'sandal': 'Camera_revealing_glacial_lake_an…_698672c3_1080p.mp4',
 'rise':   'Camera_reveals_high_altitude_lake_38eb7135_1080p.mp4',
 'ice':    'Sunlight_refracting_through_glac…_c888df92_1080p.mp4',
 'pipette':'8540611-uhd_2160_4096_25fps.mp4',
 'plate':  '8381455-uhd_3840_2160_25fps.mp4',
 'helixB': '14774644_1080_1920_30fps.mp4',
 'helixR': '14776784_1080_1920_30fps.mp4',
 'peaks4k':'14848134_3840_2160_60fps.mp4',
 'face':   '16327650_1920_1080_30fps.mp4',     # Himalayan face + clouds
 'droneup':'12786328_1920_1080_60fps.mp4',     # drone rises over scree to the peaks
 'valley': '13322002_1080_1920_60fps.mp4',
 'heap':   'Human_Skeletons_in_Roopkund_Lake.jpg',
 'lake':   'Roopkund_Lake.jpg',
}
FLOW = {'skull','shore','sandal','rise','ice'}
# name, in, end_time_on_timeline, z0, z1, cx, speed, fx
# fx: P punch-zoom in, F flash, S shake, B whip blur in, G rgb glitch in, L lightning flicker, K black dip at end (frames)
CUT = [
 ('skull',   0.00, 0.95, 1.00, 1.12, .50, 1.0, 'PF'),
 ('ice',     3.40, 1.70, 1.12, 1.00, .50, 1.0, 'BS'),
 ('heap',    0.00, 2.45, 1.05, 1.20, .47, 1.0, 'FS'),
 ('droneup', 0.40, 3.60, 1.00, 1.06, .58, 0.8, 'B'),
 ('face',    1.00, 4.73, 1.00, 1.08, .36, 1.0, 'P'),
 ('shore',   0.30, 5.65, 1.06, 1.00, .50, 1.0, 'B'),
 ('lake',    0.00, 6.58, 1.00, 1.10, .45, 1.0, 'F'),
 ('pipette', 0.60, 7.60, 1.05, 1.15, .50, 1.0, 'P'),
 ('plate',   3.00, 8.88, 1.00, 1.10, .45, 1.0, 'B'),
 ('helixB',  5.30, 10.95, 1.00, 1.12, .50, 1.0, 'GF'),
 ('helixR',  4.00, 12.92, 1.12, 1.00, .50, 1.0, 'GSF'),
 ('peaks4k', 1.00, 14.53, 1.00, 1.10, .55, 0.6, 'PL'),
 ('valley',  4.00, 15.74, 1.00, 1.08, .50, 0.7, 'B'),
 ('droneup', 4.20, 17.80, 1.00, 1.05, .55, 0.7, 'K'),
 ('skull',   3.40, 18.90, 1.00, 1.12, .50, 1.0, 'PFS'),
 ('ice',     5.40, 19.90, 1.00, 1.08, .50, 1.0, 'B'),
 ('face',    4.50, 21.20, 1.06, 1.00, .30, 1.0, 'L'),
 ('shore',   3.80, 21.85, 1.00, 1.06, .50, 1.0, 'S'),
 ('sandal',  2.60, 22.90, 1.00, 1.12, .50, 1.0, 'PFS'),
 ('heap',    0.00, 23.94, 1.15, 1.00, .55, 1.0, 'LS'),
 ('rise',    5.20, 26.10, 1.00, 1.06, .50, 0.8, 'F'),
]

def shot(i, s, t0):
    name, ss, tend, z0, z1, cx, sp, fx = s
    dur = tend - t0; n = round(tend*FPS) - round(t0*FPS)
    src = os.path.join(SRC, C[name]); out = f'{OUT}/s{i:02d}.mp4'
    still = name in ('heap', 'lake')
    if still:
        inp = ['-loop', '1', '-t', f'{dur+.2:.3f}', '-i', src]
        pre = f"crop=ih*9/16:ih:(iw-ih*9/16)*{cx}:0,scale={W*2}:{H*2},fps={FPS},"
    else:
        inp = ['-ss', str(ss), '-t', f'{dur/sp+.3:.3f}', '-i', src]
        pre = (f"setpts=PTS/{sp},fps={FPS},scale={W*2}:{H*2}:force_original_aspect_ratio=increase:flags=lanczos,"
               f"crop={W*2}:{H*2}:(iw-{W*2})*{cx}:(ih-{H*2})/2,")
    z = f"({z0}+({z1}-{z0})*on/{n})"
    if 'P' in fx: z = f"{z}*(1+0.22*exp(-on/3))"
    if name in FLOW: z = f"1.16*{z}"; y = "0.875*ih-ih/zoom"
    else: y = "ih/2-ih/zoom/2"
    x = "iw/2-iw/zoom/2"
    if 'S' in fx:  # decaying shake
        x += "+38*exp(-on/5)*sin(on*2.7)"; y += "+30*exp(-on/5)*cos(on*3.3)"
    vf = pre + f"zoompan=z='{z}':x='{x}':y='{y}':d=1:s={W}x{H}:fps={FPS}"
    if 'B' in fx: vf += ",dblur=angle=0:radius=60:enable='lt(n,3)'"
    if 'G' in fx: vf += ",rgbashift=rh=-28:bh=28:gv=6:enable='lt(n,4)',rgbashift=rh=14:bh=-14:enable='between(n,6,7)'"
    if 'F' in fx: vf += ",eq=brightness='0.55*eq(n,0)+0.28*eq(n,1)+0.1*eq(n,2)':eval=frame"
    if 'L' in fx: vf += ",eq=brightness='0.32*gt(sin(n*0.9)*sin(n*0.37),0.82)':eval=frame"
    if 'K' in fx: vf += f",eq=brightness='-1*gte(n,{n-4})':eval=frame"
    vf += f",trim=end_frame={n},setsar=1,format=yuv420p"
    subprocess.run(['ffmpeg','-v','error','-y',*inp,'-vf',vf,'-an','-c:v','libx264','-crf','15','-preset','fast',out],check=True)
    return out

files, t0 = [], 0.0
for i, s in enumerate(CUT):
    files.append(shot(i, s, t0)); t0 = s[2]
with open(f'{OUT}/list.txt','w') as f: f.writelines(f"file '{os.path.abspath(p)}'\n" for p in files)
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',f'{OUT}/list.txt','-c','copy',f'{OUT}/raw.mp4'],check=True)
# fog: one blurred noise plate, drifting
fog = f'{OUT}/fog.png'
subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','color=gray:s=120x200,noise=alls=100:allf=0,gblur=sigma=6,eq=contrast=2.2',
                '-frames:v','1','-vf',f'scale=1600:2400:flags=bicubic,gblur=sigma=20',fog],check=True)
GRADE = ("eq=contrast=1.22:brightness=-0.06:saturation=0.62:gamma=0.86,"
         "colorbalance=rs=-0.15:gs=0.02:bs=0.16:rm=-0.05:bm=0.05:rh=-0.04:bh=0.03,"
         "curves=all='0/0 0.12/0.05 0.5/0.44 0.85/0.80 1/0.94',vignette=angle=0.62")
fc = (f"[0:v]{GRADE},format=yuv420p[g];[1:v]format=gray,format=yuv420p,crop={W}:{H}:x='260+120*sin(t/5)':y='240+t*9'[fog];"
      f"[g][fog]blend=c0_mode=screen:c0_opacity=0.16:c1_mode=normal:c1_opacity=1:c2_mode=normal:c2_opacity=1,noise=alls=12:allf=t,format=yuv420p[v]")
D = float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f'{OUT}/raw.mp4'],capture_output=True,text=True).stdout)
subprocess.run(['ffmpeg','-v','error','-y','-i',f'{OUT}/raw.mp4','-loop','1','-t',f'{D}','-i',fog,'-filter_complex',fc,'-map','[v]',
                '-t',f'{D}','-c:v','libx264','-crf','16','-preset','medium',f'{OUT}/picture.mp4'],check=True)
print('total', t0)
