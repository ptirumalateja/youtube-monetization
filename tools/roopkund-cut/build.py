#!/usr/bin/env python3
"""Skeleton Lake (Roopkund) 24 s 9:16 cut. Hard cuts, dark steel-teal grade.
Usage: build.py SRC_DIR OUT_DIR [vo.wav]   (timings in SHOTS / CAPS)"""
import subprocess, sys, os, json
SRC, OUT = sys.argv[1], sys.argv[2]
VO = sys.argv[3] if len(sys.argv) > 3 else None
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30

C = {
 'skull':  'Archaeological_reconstruction_of…_b750b9e6_1080p.mp4',      # 17
 'shore':  'Camera_panning_across_lake_ac6a0ce2_1080p.mp4',             # 18
 'sandal': 'Camera_revealing_glacial_lake_an…_698672c3_1080p.mp4',      # 19
 'rise':   'Camera_reveals_high_altitude_lake_38eb7135_1080p.mp4',      # 20
 'ice':    'Sunlight_refracting_through_glac…_c888df92_1080p.mp4',      # 21
 'pipette':'8540611-uhd_2160_4096_25fps.mp4',                           # 15
 'helixB': '14774644_1080_1920_30fps.mp4',                              # blue helix
 'helixR': '14776784_1080_1920_30fps.mp4',                              # red helix
 'peaks':  '14848134_3840_2160_60fps.mp4',                              # 4K peaks 16:9
 'scope':  '8533270-uhd_2160_3840_30fps.mp4',                           # 14
 'heap':   'Human_Skeletons_in_Roopkund_Lake.jpg',                      # real photo
}
FLOW = {'skull','shore','sandal','rise','ice'}
# (name, src_in, dur, zoom_from, zoom_to, cx (0-1 crop centre for wide), flash)
# cut points follow the tightened VO (vo.py): each cut lands 0.08 s before its phrase
SHOTS = [
 ('skull',   0.00, 1.20, 1.00, 1.08, .5, False),
 ('ice',     3.20, 1.25, 1.10, 1.00, .5, True),
 ('rise',    5.40, 2.28, 1.00, 1.06, .5, False),
 ('heap',    0.00, 1.85, 1.00, 1.12, .47, True),
 ('pipette', 0.60, 2.30, 1.05, 1.15, .5, False),
 ('helixB',  5.50, 2.07, 1.00, 1.10, .5, True),
 ('helixR',  4.00, 1.97, 1.10, 1.00, .5, True),
 ('peaks',   2.00, 1.61, 1.00, 1.08, .55, False),
 ('scope',   2.00, 1.21, 1.00, 1.06, .5, False),
 ('shore',   0.30, 2.06, 1.05, 1.00, .5, False),
 ('skull',   3.40, 2.10, 1.00, 1.10, .5, True),
 ('shore',   3.80, 2.00, 1.00, 1.08, .5, False),
 ('sandal',  2.60, 2.04, 1.00, 1.10, .5, True),
 ('sandal',  5.90, 1.73, 1.00, 1.04, .5, False),
]
GRADE = ("eq=contrast=1.10:brightness=-0.035:saturation=0.72:gamma=0.96,"
         "colorbalance=rs=-0.06:bs=0.07:rm=-0.03:bm=0.04:rh=-0.02:bh=0.02,"
         "vignette=angle=0.32,noise=alls=7:allf=t")

def shot(i, s):
    name, ss, dur, z0, z1, cx, flash = s
    src = os.path.join(SRC, C[name]); out = f'{OUT}/s{i:02d}.mp4'
    n = round(dur * FPS)
    zexpr = f"{z0}+({z1}-{z0})*on/{n}"
    if name == 'heap':
        inp = ['-loop', '1', '-t', str(dur), '-i', src]
        pre = f"crop=ih*9/16:ih:(iw-ih*9/16)*{cx}:0,scale={W*2}:{H*2},"
    else:
        inp = ['-ss', str(ss), '-t', str(dur + .2), '-i', src]
        pre = (f"fps={FPS},scale={W*2}:{H*2}:force_original_aspect_ratio=increase:flags=lanczos,"
               f"crop={W*2}:{H*2}:(iw-{W*2})*{cx}:(ih-{H*2})/2,")
    if name in FLOW:   # Veo sparkle sits bottom-right: zoom past it and keep the window's bottom above y=0.875
        zexpr = f"1.16*({zexpr})"
        yexpr = "0.875*ih-ih/zoom"
    else:
        yexpr = "ih/2-ih/zoom/2"
    zp = f"zoompan=z='{zexpr}':x='iw/2-iw/zoom/2':y='{yexpr}':d=1:s={W}x{H}:fps={FPS}"
    fl = ",eq=brightness='0.35*between(n,0,1)':eval=frame" if flash else ""
    vf = pre + zp + "," + GRADE + fl + f",trim=end_frame={n},setsar=1,format=yuv420p"
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *inp, '-vf', vf, '-an',
                    '-c:v', 'libx264', '-crf', '14', '-preset', 'medium', out], check=True)
    return out

files = [shot(i, s) for i, s in enumerate(SHOTS)]
with open(f'{OUT}/list.txt', 'w') as f:
    f.writelines(f"file '{os.path.abspath(p)}'\n" for p in files)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{OUT}/list.txt',
                '-c', 'copy', f'{OUT}/picture.mp4'], check=True)
t = 0
for s in SHOTS: t += s[2]
print('total', round(t, 2), 's')
