#!/usr/bin/env python3
"""Skeleton Lake V4: picture cut to our own ElevenLabs VO (tight VO played at TEMPO).
Cut points are written in tight-VO seconds (vo_tight_words.json) and divided by TEMPO.
Usage: build4.py SRC_DIR OUT_DIR   -> OUT_DIR/picture.mp4   (ONLY=i,j rebuilds selected shots)"""
import subprocess, sys, os
SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
TEMPO = float(os.environ.get('TEMPO', '1.08'))
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
 'peaks':  '14848134_3840_2160_60fps.mp4',
 'face':   '16327650_1920_1080_30fps.mp4',
 'drone':  '12786328_1920_1080_60fps.mp4',
 'valley': '13322002_1080_1920_60fps.mp4',
 'heap':   'Human_Skeletons_in_Roopkund_Lake.jpg',
 'lake':   'Roopkund_Lake.jpg',
 'map':    os.environ.get('MAP', '/tmp/claude-0/rk/mapflash.mp4'),
}
for k, v in list(C.items()):          # optional Commons stills dropped next to the clips
    pass
FLOW = {'skull', 'shore', 'sandal', 'rise', 'ice'}
STILL = lambda n: C[n].lower().endswith('.jpg')
# (name, source_in, END on tight-VO timeline, z0, z1, cx, speed, fx)
# fx: P punch-in  F flash  S shake  B whip blur  G rgb glitch  L lightning  D darker  M hue morph from blue
#     K black dip at end  R speed ramp  V reversed (in = source end)  N night (very dark, cold)  X long slow push
CUT = [
 # HOOK  "Every summer, when the ice melts... this lake gives back its dead."
 ('skull',   0.00, 1.35, 1.00, 1.20, .46, 1.0, 'PF'),   # stronger push on the hook
 ('ice',     1.20, 2.62, 1.00, 1.10, .50, 1.0, 'BS'),     # ice crack at "melts"
 ('rise',    0.00, 3.85, 1.12, 1.00, .50, 1.0, 'B'),
 ('heap',    0.00, 5.30, 1.06, 1.22, .47, 1.0, 'FS'),     # boom on "dead"
 # LOCK-IN "Roopkund. Five thousand metres up in the Himalayas. Hundreds of skeletons."
 ('drone',   0.40, 6.40, 1.00, 1.05, .58, 1.0, 'BR'),
 ('peaks',   1.00, 8.15, 1.00, 1.10, .55, 1.0, 'P'),
 ('face',    1.00, 9.20, 1.00, 1.08, .36, 1.0, 'B'),
 ('lake',    0.00, 11.10, 1.00, 1.14, .45, 1.0, 'FS'),    # bones clatter
 # BODY 1 "For decades, everyone believed they died together. In one terrible night."
 ('shore',   0.20, 13.30, 1.08, 1.00, .50, 0.8, 'B'),
 ('drone',   6.50, 14.50, 1.00, 1.06, .55, 1.0, 'D'),     # V5: no repeat skull
 ('valley',  4.00, 16.55, 1.00, 1.08, .50, 0.7, 'NLK'),   # thunder; dip to black before "They didn't"
 # REHOOK  "They didn't."
 ('ice',     5.00, 18.00, 1.10, 1.22, .50, 1.0, 'PFS'),
 # BODY 2  DNA
 ('pipette', 0.60, 19.60, 1.05, 1.15, .50, 1.0, 'G'),
 ('helixB',  5.30, 22.45, 1.00, 1.12, .50, 1.0, 'GF'),    # 800 AD
 ('helixR',  4.00, 25.10, 1.12, 1.00, .50, 1.0, 'MS'),    # 1800
 ('drone',   10.0, 26.80, 1.00, 1.08, .55, 1.0, 'B'),     # a thousand years apart
 ('rise',    4.20, 28.90, 1.00, 1.10, .50, 1.0, 'D'),     # same frozen lake
 # BODY 3  "And the second group? Their closest match... is people from Greece and Crete."
 ('sandal',  6.00, 30.40, 1.00, 1.10, .50, 1.0, 'GS'),    # V5: lake from above, not a 2nd bone pile
 ('valley',  8.00, 31.90, 1.00, 1.10, .50, 1.0, 'BD'),   # far from home
 ('map',     0.00, 34.85, 1.00, 1.00, .50, 1.0, 'G'),     # V5: map flash Roopkund -> Greece & Crete
 # REHOOK 2 "Some skulls are cracked. From above."
 ('heap',    0.00, 37.20, 1.55, 1.75, .60, 1.0, 'XD'),    # V5: real skulls, tight on the top of the pile    # slow push, skull crack at "cracked"
 ('face',    4.50, 38.40, 1.12, 1.00, .30, 1.0, 'PL'),    # look up: from above
 # BODY 4  legend
 ('shore',   3.80, 40.50, 1.00, 1.06, .50, 0.8, 'D'),
 ('peaks',   3.50, 41.60, 1.05, 1.15, .55, 1.0, 'PL'),    # a goddess
 ('valley',  11.0, 43.10, 1.08, 1.00, .50, 1.0, 'NLS'),   # hail: storm-dark valley, lightning
 ('sandal',  2.40, 44.20, 1.00, 1.10, .50, 1.0, 'DFS'),   # iron
 # CLOSE   "And every summer... the ice gives back a little more."
 ('ice',     0.00, 46.30, 1.00, 1.18, .50, 0.7, 'X'),
 ('sandal',  0.00, 48.45, 1.04, 1.12, .50, 0.8, 'D'),     # bones under ice, slow
 # CTA     "Who were they?"  reversed into the opening skull = loop
 ('skull',   2.60, 50.30, 1.00, 1.22, .50, 1.2, 'FV'),
]

if os.environ.get('AB'):
    from ab_cut import CUT

if os.environ.get('CUTMOD'):
    import importlib.util as _u; _sp = _u.spec_from_file_location('cm', os.environ['CUTMOD']); _m = _u.module_from_spec(_sp); _sp.loader.exec_module(_m)
    CUT = [(c[0], c[1], _m.MAPT(c[2])) + tuple(c[3:]) for c in CUT]

def shot(i, s, t0):
    name, ss, tend, z0, z1, cx, sp, fx = s
    n = round(tend / TEMPO * FPS) - round(t0 / TEMPO * FPS); dur = n / FPS
    src = os.path.join(SRC, C[name]); out = f'{OUT}/s{i:02d}.mp4'
    if STILL(name):
        inp = ['-loop', '1', '-t', f'{dur+.2:.3f}', '-i', src]
        pre = f"crop=ih*9/16:ih:(iw-ih*9/16)*{cx}:0,scale={W*2}:{H*2},fps={FPS},"
    else:
        if 'R' in fx:
            srclen = 0.9 + (dur - 0.3) * 0.6 + .3
            speed = "setpts='(if(lt(T,0.9),T/3,0.3+(T-0.9)/0.6))/TB'"
        else:
            srclen = dur * sp + .3; speed = f"setpts=PTS/{sp}"
        if 'V' in fx:
            inp = ['-ss', '0', '-t', str(ss), '-i', src]; speed = f"reverse,setpts=(PTS-STARTPTS)/{sp}"
        else:
            inp = ['-ss', str(ss), '-t', f'{srclen:.3f}', '-i', src]
        pre = (f"{speed},fps={FPS},scale={W*2}:{H*2}:force_original_aspect_ratio=increase:flags=lanczos,"
               f"crop={W*2}:{H*2}:(iw-{W*2})*{cx}:(ih-{H*2})/2,tpad=stop_mode=clone:stop_duration=3,")
    z = f"({z0}+({z1}-{z0})*on/{n})"
    if 'P' in fx: z = f"{z}*(1+0.22*exp(-on/3))"
    if name in FLOW: z = f"1.16*{z}"; y = "0.875*ih-ih/zoom"
    else: y = "ih/2-ih/zoom/2"
    x = "iw/2-iw/zoom/2"
    if 'S' in fx:
        x += "+38*exp(-on/5)*sin(on*2.7)"; y += "+30*exp(-on/5)*cos(on*3.3)"
    vf = pre + f"zoompan=z='{z}':x='{x}':y='{y}':d=1:s={W}x{H}:fps={FPS}"
    if 'B' in fx: vf += ",dblur=angle=0:radius=60:enable='lt(n,3)'"
    if 'G' in fx: vf += ",rgbashift=rh=-28:bh=28:gv=6:enable='lt(n,4)',rgbashift=rh=14:bh=-14:enable='between(n,6,7)'"
    if 'F' in fx: vf += ",eq=brightness='0.55*eq(n,0)+0.28*eq(n,1)+0.1*eq(n,2)':eval=frame"
    if 'L' in fx: vf += ",eq=brightness='0.34*gt(sin(n*0.9)*sin(n*0.37),0.80)':eval=frame"
    if 'D' in fx: vf += ",eq=brightness=-0.10:gamma=0.85:saturation=0.8"
    if 'N' in fx: vf += ",eq=brightness=-0.16:gamma=0.75:saturation=0.45,colorbalance=bs=0.2:bm=0.1"
    if 'M' in fx: vf += ",hue=h='-125*max(0,1-n/12)'"
    if 'K' in fx: vf += f",eq=brightness='-1*gte(n,{n-6})':eval=frame"
    vf += f",trim=end_frame={n},setsar=1,format=yuv420p"
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *inp, '-vf', vf, '-an', '-c:v', 'libx264', '-crf', '15', '-preset', 'fast', out], check=True)
    return out

if __name__ == '__main__':
    files, t0 = [], 0.0
    ONLY = set(map(int, os.environ['ONLY'].split(','))) if os.environ.get('ONLY') else None
    for i, s in enumerate(CUT):
        files.append(shot(i, s, t0) if (ONLY is None or i in ONLY) else f'{OUT}/s{i:02d}.mp4'); t0 = s[2]
        print(i, s[0], f'{t0/TEMPO:.2f}', flush=True)
    with open(f'{OUT}/list.txt', 'w') as f: f.writelines(f"file '{os.path.abspath(p)}'\n" for p in files)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{OUT}/list.txt', '-c', 'copy', f'{OUT}/raw.mp4'], check=True)
    fog = f'{OUT}/fog.png'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'color=gray:s=120x200,noise=alls=100:allf=0,gblur=sigma=6,eq=contrast=2.2',
                    '-frames:v', '1', '-vf', 'scale=1600:2400:flags=bicubic,gblur=sigma=20', fog], check=True)
    # dark teal, cold; weak vignette (FB black-border rule)
    GRADE = ("eq=contrast=1.20:brightness=-0.05:saturation=0.62:gamma=0.88,"
             "colorbalance=rs=-0.15:gs=0.02:bs=0.16:rm=-0.05:bm=0.05:rh=-0.04:bh=0.03,"
             "curves=all='0/0.03 0.12/0.07 0.5/0.45 0.85/0.80 1/0.95',vignette=angle=0.42")
    fc = (f"[0:v]{GRADE},format=yuv420p[g];[1:v]format=gray,format=yuv420p,crop={W}:{H}:x='260+120*sin(t/5)':y='240+t*7'[fog];"
          f"[g][fog]blend=c0_mode=screen:c0_opacity=0.15:c1_mode=normal:c1_opacity=1:c2_mode=normal:c2_opacity=1,noise=alls=12:allf=t,format=yuv420p[v]")
    D = round(CUT[-1][2] / TEMPO * FPS) / FPS
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{OUT}/raw.mp4', '-loop', '1', '-t', f'{D}', '-i', fog, '-filter_complex', fc, '-map', '[v]',
                    '-t', f'{D}', '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', f'{OUT}/picture.mp4'], check=True)
    print('total', D)
