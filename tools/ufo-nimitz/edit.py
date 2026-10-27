"""Edit + render of the Tic Tac film. python3 edit.py [start end]  -> out/film_video.mp4 (silent)
Timeline is in seconds at 30 fps. Picture only; audio is mixed by audio.py and muxed by build.sh."""
import subprocess, sys, json, math, os, numpy as np
from PIL import Image, ImageFilter, ImageDraw
import gfx
from gfx import W, H, clamp, ease, eout
FPS = 30
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)

# ------------------------------------------------------------- sources
CROP = {'flir1': (56, 8, 292, 250), 'flir1_rev': (56, 8, 292, 250), 'gofast': (108, 30, 528, 452), 'gimbal': (108, 30, 528, 452)}
class Reader:
    """Sequential frame reader for one shot (ffmpeg pipe, native size, 30 fps)."""
    def __init__(self, path, t0, speed=1.0):
        info = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height',
                               '-of', 'csv=p=0', path], capture_output=True, text=True).stdout.strip().split(',')
        self.w, self.h = int(info[0]), int(info[1])
        vf = f'setpts=PTS/{speed},fps={FPS}' if speed != 1 else f'fps={FPS}'
        self.p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{max(t0, 0.):.3f}', '-i', path, '-vf', vf, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                                  stdout=subprocess.PIPE)
        self.last = None
    def next(self):
        b = self.p.stdout.read(self.w * self.h * 3)
        if len(b) == self.w * self.h * 3:
            self.last = Image.fromarray(np.frombuffer(b, np.uint8).reshape(self.h, self.w, 3))
        return self.last  # holds last frame at the end of a source
    def close(self):
        self.p.kill()

def fill(img, box, zoom=1.0, cx=.5, cy=.5, sharpen=True):
    if box: img = img.crop(box)
    iw, ih = img.size
    cw = iw / zoom; ch = cw * H / W
    if ch > ih / zoom: ch = ih / zoom; cw = ch * W / H
    x0 = min(max(cx * iw - cw / 2, 0), iw - cw); y0 = min(max(cy * ih - ch / 2, 0), ih - ch)
    out = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))
    return out.filter(ImageFilter.UnsharpMask(3, 60, 2)) if sharpen else out

GRAIN = [np.random.RandomState(i).normal(0, 7, (H // 2, W // 2)).astype(np.float32) for i in range(6)]
def sensor_look(img, i):
    a = np.asarray(img, np.float32)
    g = GRAIN[i % 6].repeat(2, 0).repeat(2, 1)[:, :, None]
    return Image.fromarray(np.clip(a + g, 0, 255).astype(np.uint8))

LUT = None
def film_look(img, i):
    """Grade for the Navy b-roll: lifted contrast, teal shadows / warm highlights, soft vignette, fine grain."""
    global LUT
    if LUT is None:
        yy, xx = np.mgrid[0:H, 0:W]
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        LUT = (1 - .28 * np.clip(r - .45, 0, 1) ** 1.6)[:, :, None].astype(np.float32)
    a = np.asarray(img, np.float32) / 255.
    l = a.mean(2, keepdims=True)
    a = l + (a - l) * .82                                   # slight desaturation
    a = np.clip((a - .5) * 1.12 + .48, 0, 1)
    a = a + (1 - l) * np.array([-.012, .008, .022], np.float32) * 1.4 + l * np.array([.02, .006, -.018], np.float32)
    a = a * LUT * 255. + GRAIN[i % 6].repeat(2, 0).repeat(2, 1)[:, :, None] * .5
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

# ------------------------------------------------------------- timeline (v2, see timeline.py)
from timeline import T, D, VO, END, R, R_end, CARD_AT, CHAPTERS
SHOTS = []   # (start, dur, kind, params)
def S(start, dur, kind, **kw): SHOTS.append((start, dur, kind, kw))
OVL = []     # (start, dur, fn(layer, t, dur))
def O(start, dur, fn): OVL.append((start, dur, fn))
def LS(t, d, kind, **kw):
    """v1 shot, moved to its v2 place and trimmed where its section got shorter"""
    n = R(t); d = min(d, R_end(t) - n)
    if d > 0: S(n, d, kind, **kw)
def LO(t, d, fn):
    n = R(t); d = min(d, R_end(t) - n)
    if d > 0: O(n, d, fn)
def at(k, f): return T[k] + f * D[k]          # f = fraction of the way through narration beat k
def HL(k, f0, f1, text, **kw): O(at(k, f0), (f1 - f0) * D[k], lambda L, t, d: gfx.headline(L, text, t, d, **kw))
def TAG(t0, t1, text, color=gfx.CREAM): O(t0, t1 - t0, lambda L, t, d: gfx.tag(L, text, 1, color))

NAVY_TAG = 'REAL U.S. NAVY FOOTAGE'
REC_TAG = 'RECONSTRUCTION · BASED ON WITNESS TESTIMONY'
TRI_TAG = 'RECONSTRUCTION · BASED ON WITNESS DOCUMENTS · NO VIDEO EXISTS'
FILE_TAG = 'U.S. NAVY FILE FOOTAGE · NOT FROM THE 2004 INCIDENT'
def B(start, dur, src, t0, z0=1.0, z1=1.07, cx=.5, cy=.5, speed=1.0):
    S(start, dur, 'broll', src=src, t0=t0, z0=z0, z1=z1, cx=cx, cy=cy, speed=speed)
def LB(start, dur, src, t0, z0=1.0, z1=1.07, cx=.5, cy=.5, speed=1.0):
    LS(start, dur, 'broll', src=src, t0=t0, z0=z0, z1=z1, cx=cx, cy=cy, speed=speed)
for k, (num, title) in CHAPTERS.items():
    S(CARD_AT[k], T[k] - (.6 if k == 'b11' else 0) - CARD_AT[k], 'chapter', num=num, title=title)

# --- 0 · TWO DOCUMENTS: cold open on the 23 Oct 2026 release
S(0.0, T['c02'], 't_recon', clip='t1_triangle', t0=0, speed=14.0 / T['c02'], z0=1.0, z1=1.1)
TAG(0.0, at('c03', .24), TRI_TAG)
O(0.0, T['c02'], lambda L, t, d: gfx.source_line(L, 'As described in AARO memo DOW-UAP-D176 and FBI FD-302 FBI-UAP-D043 · released 23 Oct 2026'))
O(.15, 3.6, lambda L, t, d: gfx.headline(L, 'TWO GOVERNMENT REPORTS. ONE SIGHTING.', t, d, y=900, size=72))
O(at('c01', .2), .25 * D['c01'], lambda L, t, d: gfx.lower_third(L, 'FEDERAL AGENTS', 'SENSITIVE SITE · WESTERN UNITED STATES', t, d))
HL('c01', .47, .68, 'MATTE BLACK · UP TO 15 FT', y=980, size=64)
O(at('c01', .88), T['c02'] - at('c01', .88), lambda L, t, d: gfx.headline(L, 'NO SOUND. NO EXHAUST.', t, d, y=980, size=64))
S(T['c02'], T['c03'] - T['c02'], 'versus', bg=('clips/t1_triangle.mp4', 4.0, .5),
  a1=.45 * D['c02'], a2=.74 * D['c02'], a3=.84 * D['c02'], final='BOTH OFFICIAL. BOTH CAN’T BE RIGHT.', intro=None)
O(T['c02'] + .2, .3 * D['c02'], lambda L, t, d: gfx.lower_third(L, 'AARO MEMO DOW-UAP-D176', 'VS. FBI FD-302 · FBI-UAP-D043', t, d))
S(T['c03'], .24 * D['c03'], 't_recon', clip='t1_triangle', t0=9.5, speed=.5, z0=1.1, z1=1.2)
HL('c03', .13, .24, 'NO VIDEO EXISTS', size=110, color=gfx.RED)
S(at('c03', .24), .31 * D['c03'], 'files', n=7, bg=('src/DOD_111796027.mp4', 12.0, .38))
TAG(at('c03', .24), at('c03', .55), 'WAR.GOV/UFO · RELEASE 7 · 23 OCT 2026')
HL('c03', .26, .52, '23 OCT 2026', y=170, size=96)
B(at('c03', .55), .29 * D['c03'], 'DOD_111585732', 6.0, 1.0, 1.1)
TAG(at('c03', .55), at('c03', .84), 'U.S. NAVY FILE FOOTAGE · ILLUSTRATIVE')
HL('c03', .71, .84, '22 YEARS EARLIER', size=110)
# --- 1 · THE FOOTAGE THAT ISN'T THE ENCOUNTER (FLIR1 hook, then the honesty, in the first two minutes)
fs = at('c03', .84)
S(fs, T['b01'] - .4 + 8.9 - fs, 'video', src='flir1', t0=66.0 - (T['b01'] - .4 - fs), z0=1.3, z1=1.6, cy=.47)
LS(8.9, .25, 'black')
LS(9.15, 2.15, 'video', src='flir1_rev', t0=76.27 - 75.0, speed=35.0, z0=1.4, z1=1.2, cy=.47)
O(fs, T['b01'] + 10.9 - fs, lambda L, t, d: gfx.tag(L, NAVY_TAG + ' · 2004', clamp(t / .2)))
O(fs, R(8.9) - fs, lambda L, t, d: gfx.source_line(L, 'U.S. Navy · released by the Department of Defense, 27 Apr 2020'))
LO(5.6, 3.3, lambda L, t, d: gfx.headline(L, 'STILL “UNIDENTIFIED”', t, d, y=880, size=104, sub='U.S. DEPARTMENT OF DEFENSE'))
c4 = D['c04']
S(T['c04'], .6 * c4, 'video', src='flir1', t0=0.0, z0=1.0, z1=1.25, cy=.47)
S(at('c04', .6), .2 * c4, 'video', src='flir1', t0=74.5 - .03 * c4, speed=.5, z0=1.25, z1=1.45, cy=.47)
S(at('c04', .8), T['b02'] - at('c04', .8), 'video', src='flir1', t0=30.0, z0=1.5, z1=1.7, cy=.47)
O(T['c04'], T['b02'] - T['c04'], lambda L, t, d: gfx.tag(L, NAVY_TAG + ' · FLIR1 · 14 NOV 2004', 1))
O(T['c04'], T['b02'] - T['c04'], lambda L, t, d: gfx.source_line(L, 'U.S. Navy / DoD release, 27 Apr 2020'))
HL('c04', .2, .44, 'A LATER FLIGHT — NOT THE CLOSE ENCOUNTER', y=170, size=54)
O(at('c04', .23), .22 * c4, lambda L, t, d: gfx.lower_third(L, 'CHAD UNDERWOOD', 'WEAPONS SYSTEMS OFFICER · RECORDED FLIR1', t, d))
HL('c04', .5, .64, 'HIS CREW NEVER SAW IT BY EYE', y=960, size=60, color=gfx.RED)
O(at('c04', .7), .2 * c4, lambda L, t, d: gfx.headline(L, 'BURST OF SPEED — OR LOST LOCK?', t, d, y=1000, size=60))
HL('c04', .9, 1.02, 'THE FOOTAGE CAN’T SETTLE IT', y=1000, size=60)
b2 = D['b02']
S(T['b02'], .15 * b2, 'freeze', src='flir1', t0=4.0, z0=1.5, z1=1.35)
TAG(T['b02'], at('b02', .15), NAVY_TAG + ' · FLIR1', gfx.RED)
B(at('b02', .15), .33 * b2, 'DOD_111581586', 35.0, 1.0, 1.08)
B(at('b02', .48), .37 * b2, 'DOD_109335834', 0.6, 1.0, 1.08)
TAG(at('b02', .15), at('b02', .85), FILE_TAG)
HL('b02', .2, .32, '2 JETS', size=118)
HL('b02', .33, .46, '4 AVIATORS', size=118)
O(at('b02', .5), .35 * b2, lambda L, t, d: gfx.quote(L, 'far superior to anything that we had', 'DAVID FRAVOR · SWORN TESTIMONY TO CONGRESS · 26 JUL 2023', t, d, y=860))
S(at('b02', .85), CARD_AT['b03s'] - at('b02', .85), 'recon', clip='e4_close', t0=1.0, z0=1.0, z1=1.08)
TAG(at('b02', .85), CARD_AT['b03s'], REC_TAG)
# --- 2 · NOVEMBER 2004 (v1 sections, unchanged)
LB(29.2, 4.6, 'DOD_111802050', 80.6, 1.0, 1.12)
LO(29.2, 8.2, lambda L, t, d: gfx.tag(L, FILE_TAG, 1, gfx.CREAM))
LO(29.6, 3.6, lambda L, t, d: gfx.headline(L, 'NOVEMBER 2004', t, d, y=170, size=90))
LB(33.8, 3.6, 'DOD_107844340', 14.7, 1.0, 1.1)
LO(34.0, 3.4, lambda L, t, d: gfx.lower_third(L, 'USS PRINCETON (CG-59)', 'GUIDED-MISSILE CRUISER · NIMITZ STRIKE GROUP ESCORT', t, d))
LS(37.4, 14.9, 'radar', d0=.0, d1=1.0, lead=2.0)
LO(37.4, 14.9, lambda L, t, d: gfx.tag(L, 'ILLUSTRATIVE · USS PRINCETON RADAR CONTACTS, AS DESCRIBED', 1, gfx.CREAM))
LO(40.2, 3.0, lambda L, t, d: gfx.headline(L, '2+ WEEKS OF CONTACTS', t, d, y=1000, size=64))
# --- BODY 1b 52.3–74.8: the pilots
LB(52.3, 3.3, 'DOD_109335834', 0.6, 1.0, 1.08)
LB(55.6, 2.9, 'DOD_111579505', 51.3, 1.0, 1.06)
LO(52.3, 13.3, lambda L, t, d: gfx.tag(L, FILE_TAG, 1, gfx.CREAM))
LO(54.0, 4.3, lambda L, t, d: gfx.lower_third(L, 'CDR DAVID FRAVOR', 'COMMANDING OFFICER · VFA-41 “BLACK ACES”', t, d))
LB(58.5, 4.1, 'DOD_111581586', 35.0, 1.0, 1.08)
LO(58.7, 3.6, lambda L, t, d: gfx.headline(L, '2 × F/A-18F SUPER HORNETS', t, d, y=170, size=70))
LB(62.6, 3.0, 'DOD_112040853', 32.0, 1.0, 1.1)
LO(62.9, 3.4, lambda L, t, d: gfx.lower_third(L, 'LT ALEX DIETRICH', 'PILOT · SECOND F/A-18F', t, d))
LB(65.6, 4.8, 'DOD_111796027', 2.0, 1.0, 1.1)
LO(65.6, 4.8, lambda L, t, d: gfx.tag(L, 'U.S. NAVY FILE FOOTAGE · ILLUSTRATIVE', 1, gfx.CREAM))
LS(70.4, 4.4, 'radar', d0=1.0, d1=1.0, lead=0)
LO(70.4, 4.4, lambda L, t, d: gfx.tag(L, 'ILLUSTRATIVE', 1, gfx.CREAM))
LO(70.6, 4.0, lambda L, t, d: gfx.headline(L, 'EXERCISE CALLED OFF', t, d, y=1000, size=70, color=gfx.RED))
# --- BODY 2 74.8–99.0: encounter (reconstruction)
LB(74.8, 5.0, 'DOD_111585732', 0.0, 1.0, 1.1)
LO(74.8, 5.0, lambda L, t, d: gfx.tag(L, 'U.S. NAVY FILE FOOTAGE · ILLUSTRATIVE', 1, gfx.CREAM))
LS(79.8, 6.0, 'recon', clip='e2_lookdown', t0=0, z0=1.0, z1=1.1)
LS(85.8, 6.6, 'recon', clip='e3_mid', t0=0.3, z0=1.0, z1=1.12)
LS(92.4, 6.6, 'recon', clip='e4_close', t0=0.2, z0=1.0, z1=1.1)
LO(79.8, 19.2, lambda L, t, d: gfx.tag(L, REC_TAG, 1, gfx.CREAM))
LO(77.0, 2.6, lambda L, t, d: gfx.headline(L, 'CLEAR SKY · CALM SEA', t, d, y=1000, size=56))
LO(87.6, 4.6, lambda L, t, d: gfx.quote(L, 'a white Tic Tac object', 'DAVID FRAVOR · SWORN TESTIMONY · 2023', t, d, y=900))
LO(94.6, 4.0, lambda L, t, d: gfx.headline(L, 'NO WINGS. NO ROTORS.', t, d, y=980, size=78))
# --- BODY 2b 99.0–120.2
LS(99.0, 6.0, 'recon', clip='e5_spiral', t0=0, z0=1.0, z1=1.1)
LS(105.0, 4.0, 'recon', clip='e6_climb', t0=0, z0=1.0, z1=1.15)
LS(109.0, 3.0, 'recon', clip='e7_gone', t0=0, z0=1.0, z1=1.05)
LS(112.0, 6.0, 'recon', clip='e8_calm', t0=0, z0=1.0, z1=1.08)
LS(118.0, 2.2, 'black')
LO(99.0, 19.0, lambda L, t, d: gfx.tag(L, REC_TAG, 1, gfx.CREAM))
LO(100.6, 4.3, lambda L, t, d: gfx.quote(L, 'aligned it with my aircraft, and began to climb', 'DAVID FRAVOR · SWORN TESTIMONY · 2023', t, d, y=900))
LO(109.6, 2.3, lambda L, t, d: gfx.headline(L, 'GONE.', t, d, size=150))
LO(114.6, 3.2, lambda L, t, d: gfx.headline(L, 'THE WHITEWATER TOO.', t, d, y=980, size=64))
LS(120.2, 10.2, 'map', z0=2.4, z1=2.0, c0=(-118.05, 31.5), c1=(-118.45, 31.75), jets=(1, 1), cap=(R(121.8), R(123.0)))
LO(120.2, 10.2, lambda L, t, d: gfx.tag(L, 'ILLUSTRATIVE MAP', 1, gfx.CREAM))
LO(124.6, 5.6, lambda L, t, d: gfx.headline(L, '60 MILES. UNDER A MINUTE.', t, d, y=900, size=104))
# --- REHOOK 1 120.2–130.4
# --- 3 · 60 MILES IN UNDER A MINUTE: the arithmetic, and where the number comes from
c5 = D['c05']
S(T['c05'], .36 * c5, 'map', z0=2.0, z1=1.7, c0=(-118.45, 31.75), c1=(-118.55, 31.85), jets=(1, 1), cap=(0, .01))
TAG(T['c05'], at('c05', .36), 'ILLUSTRATIVE MAP')
HL('c05', .0, .11, '60 MILES ÷ 60 SECONDS', y=900, size=96)
HL('c05', .11, .21, '= 1 MILE EVERY SECOND', y=900, size=96)
O(at('c05', .21), .15 * c5, lambda L, t, d: gfx.headline(L, f'≥ {3600 * eout(t / 1.4):,.0f} MPH', t, d, y=880, size=150, color=gfx.RED))
S(at('c05', .36), CARD_AT['c06'] - at('c05', .36), 'radar', d0=1.0, d1=1.0, lead=0)
TAG(at('c05', .36), CARD_AT['c06'], 'ILLUSTRATIVE · USS PRINCETON RADAR')
HL('c05', .4, .56, 'SOURCE: THE SHIP’S RADAR, OVER THE RADIO', y=1000, size=52)
HL('c05', .57, .7, 'NO RECORDING YOU CAN WATCH', y=1000, size=64, color=gfx.RED)
O(at('c05', .78), CARD_AT['c06'] - at('c05', .78), lambda L, t, d: gfx.headline(L, 'BEST EVIDENCE — OR FIRST THING TO QUESTION?', t, d, y=1000, size=52))
# --- 4 · FOUR AVIATORS, TWO JETS, ONE RADAR
c6, c12 = D['c06'], D['c12']
B(T['c06'], .15 * c6, 'DOD_111581586', 40.0, 1.0, 1.1)
TAG(T['c06'], at('c06', .15), FILE_TAG)
S(at('c06', .15), .4 * c6, 'crew', seats=(at('c06', .17), at('c06', .24), at('c06', .27), at('c06', .36)), radar=None)
TAG(at('c06', .15), at('c06', .55), 'ILLUSTRATIVE · TWO F/A-18F SUPER HORNETS')
O(at('c06', .41), .15 * c6, lambda L, t, d: gfx.lower_third(L, 'JIM SLAIGHT', 'FRAVOR’S WEAPONS SYSTEMS OFFICER · HAS NOT SPOKEN PUBLICLY', t, d))
S(at('c06', .55), .25 * c6, 'recon', clip='e2_lookdown', t0=0, z0=1.0, z1=1.12)
TAG(at('c06', .55), at('c06', .8), REC_TAG)
HL('c06', .57, .78, '4 WITNESSES · ABOUT 5 MINUTES', y=980, size=64)
B(at('c06', .8), T['c12'] - at('c06', .8), 'DOD_111796027', 10.0, 1.0, 1.1)
TAG(at('c06', .8), T['c12'], 'U.S. NAVY FILE FOOTAGE · ILLUSTRATIVE')
B(T['c12'], .25 * c12, 'DOD_107844340', 5.0, 1.0, 1.1)
TAG(T['c12'], at('c12', .25), FILE_TAG)
O(T['c12'] + .2, .24 * c12, lambda L, t, d: gfx.lower_third(L, 'SENIOR CHIEF KEVIN DAY', 'RADAR OPERATOR · USS PRINCETON', t, d))
S(at('c12', .25), .4 * c12, 'radar', d0=0.0, d1=1.0, lead=.5)
TAG(at('c12', .25), at('c12', .65), 'ILLUSTRATIVE · AS DESCRIBED BY KEVIN DAY')
HL('c12', .28, .5, '5–10 OBJECTS AT A TIME', y=1000, size=60, sub='KEVIN DAY’S ACCOUNT')
S(at('c12', .65), .2 * c12, 'crew', seats=(0, 0, 0, 0), radar=at('c12', .66))
TAG(at('c12', .65), at('c12', .85), 'ILLUSTRATIVE')
HL('c12', .67, .85, '2 COCKPITS + 1 WARSHIP RADAR', y=980, size=60)
S(at('c12', .85), CARD_AT['c07'] - at('c12', .85), 'radar', d0=1.0, d1=1.0, lead=0)
TAG(at('c12', .85), CARD_AT['c07'], 'ILLUSTRATIVE')
O(at('c12', .86), CARD_AT['c07'] - at('c12', .86), lambda L, t, d: gfx.headline(L, 'RAW RADAR DATA · NEVER MADE PUBLIC', t, d, y=1000, size=60, color=gfx.RED))
# --- 5 · GO FAST, after the Nimitz case, as the test of what a video can prove
S(T['c07'], .5 * D['c07'], 'freeze', src='flir1', t0=40.0, z0=1.3, z1=1.5)
TAG(T['c07'], at('c07', .5), NAVY_TAG + ' · FLIR1', gfx.RED)
S(at('c07', .5), R(171.0) - at('c07', .5), 'freeze', src='gofast', t0=1.0, z0=1.0, z1=1.08)
TAG(at('c07', .5), R(171.0), NAVY_TAG + ' · GOFAST · JAN 2015', gfx.RED)
HL('c07', .05, .55, 'WHAT DOES A VIDEO PROVE?', y=980, size=70)
LS(171.0, 29.0, 'video', src='gofast', t0=0.0, z0=1.0, z1=1.2, cy=.5)
LS(200.0, 17.2, 'parallax')
LO(171.0, 29.0, lambda L, t, d: gfx.tag(L, NAVY_TAG + ' · GOFAST · JAN 2015', 1))
LO(171.0, 29.0, lambda L, t, d: gfx.source_line(L, 'U.S. Navy / DoD release, 27 Apr 2020'))
LO(185.0, 4.0, lambda L, t, d: gfx.headline(L, 'AARO · 2025', t, d, y=170, size=80, color=gfx.RED))
LO(190.4, 6.0, lambda L, t, d: gfx.headline(L, '≈ 13,000 FT UP', t, d, y=1000, size=88))
LO(200.0, 17.2, lambda L, t, d: gfx.tag(L, 'ILLUSTRATIVE · AFTER AARO GOFAST ANALYSIS, FEB 2025', 1, gfx.CREAM))
LO(206.0, 5.2, lambda L, t, d: gfx.headline(L, '5 – 92 MPH', t, d, y=170, size=110))
LO(211.2, 5.8, lambda L, t, d: gfx.quote(L, 'did not move at anomalous speeds', 'AARO GOFAST CASE RESOLUTION · FEB 2025', t, d, y=330))
c8 = D['c08']
S(T['c08'], .17 * c8, 'video', src='gofast', t0=20.0, z0=1.2, z1=1.3)
TAG(T['c08'], at('c08', .17), NAVY_TAG + ' · GOFAST', gfx.RED)
S(at('c08', .17), .23 * c8, 'recon', clip='e4_close', t0=3.0, z0=1.05, z1=1.15)
TAG(at('c08', .17), at('c08', .4), REC_TAG)
B(at('c08', .4), .12 * c8, 'DOD_111581586', 61.0, 1.0, 1.08)
TAG(at('c08', .4), at('c08', .52), FILE_TAG)
HL('c08', .4, .52, 'PEOPLE', size=130)
S(at('c08', .52), .11 * c8, 'radar', d0=1.0, d1=1.0, lead=0)
HL('c08', .52, .63, 'AND RADAR', size=130)
S(at('c08', .63), CARD_AT['b11'] - at('c08', .63), 'video', src='flir1', t0=10.0, z0=1.2, z1=1.35, cy=.47)
TAG(at('c08', .63), CARD_AT['b11'], NAVY_TAG + ' · FLIR1', gfx.RED)
HL('c08', .66, .98, 'THE VIDEO CAME LATER', y=1000, size=60)
# --- 6 · TWENTY-TWO YEARS OF FILES (v1 montage and file batches)
LB(233.0, 2.8, 'DOD_111579505', 32.4, 1.0, 1.1)
LB(235.8, 2.1, 'DOD_112040853', 9.9, 1.0, 1.08)
LB(237.9, 3.3, 'DOD_112040853', 18.3, 1.0, 1.08)
LB(241.2, 4.0, 'DOD_111796027', 41.8, 1.0, 1.08)
LB(245.2, 4.2, 'DOD_112040853', 56.3, 1.0, 1.1)
LO(233.0, 16.4, lambda L, t, d: gfx.tag(L, 'U.S. NAVY FILE FOOTAGE · ILLUSTRATIVE', 1, gfx.CREAM))
LO(236.0, 4.4, lambda L, t, d: gfx.headline(L, 'THE REPORTS NEVER STOPPED', t, d, y=980, size=72))
LO(241.6, 5.4, lambda L, t, d: gfx.headline(L, '757 NEW REPORTS IN 13 MONTHS', t, d, y=980, size=72, sub='AARO ANNUAL REPORT · NOV 2024'))
LS(249.4, 23.0, 'files', n=7, bg=('src/DOD_111796027.mp4', 0.5, .38))
LO(249.4, 23.0, lambda L, t, d: gfx.tag(L, 'WAR.GOV/UFO · 7 RELEASES · MAY–OCT 2026', 1, gfx.CREAM))
LO(262.0, 4.0, lambda L, t, d: gfx.headline(L, '23 OCT 2026', t, d, y=170, size=96))
LO(266.4, 5.8, lambda L, t, d: gfx.headline(L, 'DOCUMENTS ONLY. NO NEW VIDEO.', t, d, y=980, size=70))
c10 = D['c10']
S(T['c10'], CARD_AT['c11'] - T['c10'], 'versus', bg=('clips/t1_triangle.mp4', 0.0, .7),
  a1=.4 * c10, a2=.6 * c10, a3=.87 * c10, final='AND NO FOOTAGE TO CHECK.', intro='THE BLACK TRIANGLE')
TAG(T['c10'], CARD_AT['c11'], TRI_TAG)
# --- 7 · STILL UNIDENTIFIED
c11 = D['c11']
S(T['c11'], .22 * c11, 'recon', clip='e3_mid', t0=.3, z0=1.0, z1=1.1)
TAG(T['c11'], at('c11', .22), REC_TAG)
S(at('c11', .22), .24 * c11, 't_recon', clip='t1_triangle', t0=3.0, z0=1.0, z1=1.1)
TAG(at('c11', .22), at('c11', .46), TRI_TAG)
B(at('c11', .46), T['b14'] - at('c11', .46), 'DOD_111796027', 20.0, 1.0, 1.1, speed=.6)
TAG(at('c11', .46), T['b14'], 'U.S. NAVY FILE FOOTAGE · ILLUSTRATIVE')
HL('c11', .47, .69, '2004 · 2026', size=140)
O(at('c11', .7), T['b14'] - at('c11', .7), lambda L, t, d: gfx.headline(L, 'SERIOUS. NOT SOLVED.', t, d, size=110))
LB(306.2, 7.2, 'DOD_111796027', 46.4, 1.0, 1.12, speed=.6)
LS(313.4, 6.8, 'recon', clip='e4_close', t0=0.0, z0=1.12, z1=1.0)
LS(320.2, 8.0, 'freeze', src='flir1', t0=4.0, z0=1.5, z1=1.9, cy=.47)
LO(306.2, 7.2, lambda L, t, d: gfx.tag(L, 'U.S. NAVY FILE FOOTAGE · ILLUSTRATIVE', 1, gfx.CREAM))
LO(313.4, 6.8, lambda L, t, d: gfx.tag(L, REC_TAG, 1, gfx.CREAM))
LO(308.4, 5.6, lambda L, t, d: gfx.quote(L, 'We don’t know what it was.', 'ALEX DIETRICH · F/A-18F PILOT · 2021', t, d, y=900))
LO(314.4, 5.6, lambda L, t, d: gfx.headline(L, 'NOT PROOF. NOT EXPLAINED.', t, d, y=980, size=78))
LO(320.2, 8.0, lambda L, t, d: gfx.tag(L, NAVY_TAG + ' · FLIR1', 1))
S(R(328.2), END - R(328.2), 'endcard', bg=('src/DOD_111796027.mp4', 30.0, .4))


# ------------------------------------------------------------- special frames
def cards_frame(t, d, items):
    """Placeholder for the 2026 clip montage: file IDs slam in over a dark sensor field."""
    k = min(int(t / (d / len(items))), len(items) - 1); tt = t - k * d / len(items)
    rnd = np.random.RandomState(k)
    base = np.full((H // 4, W // 4), 40, np.float32) + rnd.normal(0, 9, (H // 4, W // 4))
    im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC).convert('RGB')
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    gfx.headline(L, items[k][0], tt, d / len(items), y=520, size=110)
    gfx.shadow_text(L, (W / 2, 620), items[k][1], gfx.font('monob', 34), gfx.CREAM + (255,))
    return Image.alpha_composite(im.convert('RGBA'), L).convert('RGB')

def backdrop(img, u, fi):
    """Moving, darkened, soft background so card sections never sit still."""
    im = fill(img, None, 1.05 + .12 * u, .5, .5, sharpen=False).filter(ImageFilter.GaussianBlur(6))
    a = np.asarray(im, np.float32) * .32
    return film_look(Image.fromarray(a.astype(np.uint8)), fi)

def files_frame(t, d, n, bg):
    im = bg.copy(); dr = ImageDraw.Draw(im)
    for i in range(n):
        u = clamp((t - i * .5) / .6)
        if u <= 0: continue
        x = 180 + i * 230 + (1 - eout(u)) * 300 - t * 6; y = 300 + (i % 2) * 60
        dr.rectangle([x, y, x + 200, y + 280], fill=(26, 30, 40), outline=(90, 100, 120), width=2)
        dr.text((x + 100, y + 120), f'{i + 1:02d}', font=gfx.font('black', 90), fill=gfx.CREAM, anchor='mm')
        dr.text((x + 100, y + 230), ['8 MAY', '22 MAY', '12 JUN', 'JUL', 'AUG', 'SEP', '23 OCT'][i], font=gfx.font('monob', 26), fill=(200, 190, 170), anchor='mm')
    return im

def versus_frame(t, d, bg, a1t=3.2, a2t=5.8, a3t=12.0, final='AND NO VIDEO AT ALL.', intro='HOW LONG DID IT LAST?'):
    im = bg; L = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    a1 = clamp((t - a1t) / .2); a2 = clamp((t - a2t) / .2)
    f = gfx.font('black', 170)
    if a1 > 0:
        gfx.shadow_text(L, (W * .27, 500), '30+ SEC', f, gfx.CREAM + (int(255 * a1),))
        gfx.shadow_text(L, (W * .27, 640), 'AARO MEMO', gfx.font('monob', 36), (210, 200, 180, int(255 * a1)))
    if a2 > 0:
        gfx.shadow_text(L, (W * .73, 500), '~3 SEC', f, gfx.RED + (int(255 * a2),))
        gfx.shadow_text(L, (W * .73, 640), 'FBI WRITE-UP', gfx.font('monob', 36), (210, 200, 180, int(255 * a2)))
    if a1 > 0 and a2 > 0:
        ImageDraw.Draw(L).line([(W / 2, 360), (W / 2, 700)], fill=(120, 120, 130, 200), width=3)
    if t > a3t:
        gfx.headline(L, final, t - a3t, d - a3t, y=880, size=72)
    if intro and t < a1t:
        gfx.headline(L, intro, t, a1t, y=540, size=96)
    return Image.alpha_composite(im.convert('RGBA'), L).convert('RGB')

def chapter_frame(t, d, num, title, fi):
    """Chapter title: number and name over a dark, slowly drifting field."""
    rnd = np.random.RandomState(int(num))
    base = np.full((H // 4, W // 4), 14, np.float32) + rnd.normal(0, 4, (H // 4, W // 4))
    im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC).convert('RGB')
    im = sensor_look(im, fi)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    a = clamp(t / .35) * clamp((d - t) / .35)
    x = W / 2 + 40 * (1 - eout(t / .8))
    gfx.shadow_text(L, (x, 470), f'CHAPTER {num}', gfx.font('monob', 34), gfx.RED + (int(255 * a),))
    gfx.shadow_text(L, (x, 560), title, gfx.font('black', 84), gfx.CREAM + (int(255 * a),), spread=16)
    dr = ImageDraw.Draw(L); w = 260 * eout(t / .9)
    dr.line([(W / 2 - w, 625), (W / 2 + w, 625)], fill=gfx.RED + (int(200 * a),), width=3)
    return Image.alpha_composite(im.convert('RGBA'), L).convert('RGB')

def _jet(cx, cy, s, ang):
    """F/A-18-like planform, top view, as a polygon (nose up at ang=0)."""
    pts = [(0, -1.0), (.07, -.75), (.09, -.25), (.55, .1), (.55, .2), (.12, .12), (.1, .45), (.3, .62), (.3, .7), (.06, .68),
           (0, .72)]
    pts = pts + [(-x, y) for x, y in reversed(pts[1:-1])]
    c, sn = math.cos(ang), math.sin(ang)
    return [(cx + s * (x * c - y * sn), cy + s * (x * sn + y * c)) for x, y in pts]

def crew_frame(t, u, seats, radar, fi):
    """Illustrative: two jets, four seats lighting up as each crew member is named; optional radar beam from the ship."""
    im = Image.new('RGB', (W, H), gfx.NAVY); d = ImageDraw.Draw(im)
    ox = -30 * u
    for y in range(0, H, 34):
        for x in range(int(ox) % 34, W, 34): d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(18, 28, 46))
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
    jets = [(720 + ox, 500, .35), (1300 + ox, 560, .35)]
    labels = []
    for j, (cx, cy, ang) in enumerate(jets):
        ld.polygon(_jet(cx, cy, 360, ang), outline=(235, 215, 180, 255), fill=(30, 36, 52, 255))
        for k, (dy, role) in enumerate(((-232, 'PILOT'), (-176, 'WSO'))):
            sx = cx - dy * math.sin(ang); sy = cy + dy * math.cos(ang)
            ts = seats[j * 2 + k]
            lit = clamp((t - ts) / .3) if ts else 1.0
            r = 17
            ld.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(int(60 + 166 * lit), int(70 + 128 * lit), int(80 + 2 * lit), 255))
            if lit > 0: labels.append((sx, sy, role, lit))
    if radar is not None:
        ra = clamp((t - radar) / .8)
        if ra > 0:
            shx, shy = 230 + ox, 820
            for (cx, cy, _) in jets:
                ld.line([(shx, shy), (cx, cy)], fill=gfx.TEAL + (int(150 * ra),), width=4)
            ld.polygon([(shx - 26, shy + 10), (shx + 26, shy + 10), (shx + 16, shy - 8), (shx - 16, shy - 8)], fill=gfx.TEAL + (int(255 * ra),))
            ld.text((shx + 40, shy), 'USS PRINCETON · SPY-1 RADAR', font=gfx.font('monob', 26), fill=gfx.TEAL + (int(255 * ra),), anchor='lm')
    L = gfx.glow(L, 10, .8)
    for sx, sy, role, lit in labels:
        gfx.shadow_text(L, (sx + 40, sy), role, gfx.font('monob', 32), gfx.CREAM + (int(255 * lit),), anchor='lm', spread=6)
    return Image.alpha_composite(im.convert('RGBA'), L).convert('RGB')

def endcard_frame(t, d, bg):
    """Last 16 s: title up top, the middle left clear for YouTube end-screen elements."""
    im = bg; L = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    a = clamp(t / .6)
    gfx.shadow_text(L, (W / 2, 150), 'SLOW LIGHT', gfx.font('black', 96), gfx.CREAM + (int(255 * a),))
    gfx.shadow_text(L, (W / 2, 225), 'stories worth slowing down for', gfx.font('serif', 44), (215, 205, 185, int(255 * a)))
    b = clamp((t - 1.2) / .5)
    gfx.shadow_text(L, (W / 2, 990), 'SUBSCRIBE FOR THE NEXT FILE', gfx.font('monob', 32), gfx.RED + (int(255 * b),))
    return Image.alpha_composite(im.convert('RGBA'), L).convert('RGB')

# ------------------------------------------------------------- render
def render(t_start=0., t_end=END, out='out/film_video.mp4'):
    os.makedirs('out', exist_ok=True)
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    cur = None; reader = None; frozen = {}
    n0, n1 = int(t_start * FPS), int(t_end * FPS)
    for fi in range(n0, n1):
        t = fi / FPS
        sh = None
        for s in SHOTS:
            if s[0] <= t < s[0] + s[1]: sh = s
        if sh is not cur:
            if reader: reader.close(); reader = None
            cur = sh
            if sh and 'bg' in sh[3]:
                bp, bt0, bsp = sh[3]['bg']; reader = Reader(bp, bt0 + (t - sh[0]) * bsp, bsp)
            elif sh and sh[2] in ('video', 'recon', 't_recon', 'broll'):
                p = sh[3]
                if sh[2] in ('video', 'broll'):
                    path = f"src/{p['src']}.mp4"
                else:
                    path = f"clips/{p['clip']}.mp4"
                lt0 = t - sh[0]
                spd = p.get('speed', 1.0) * p.get('slow', 1.0)
                reader = Reader(path, p.get('t0', 0) + lt0 * spd, spd)
        if sh is None:
            frame = Image.new('RGB', (W, H))
        else:
            st, d, kind, p = sh; lt = t - st; u = lt / d
            if kind == 'black':
                frame = Image.new('RGB', (W, H))
            elif kind in ('video', 'recon', 't_recon'):
                img = reader.next()
                z = p.get('z0', 1) + (p.get('z1', 1) - p.get('z0', 1)) * ease(u)
                if kind == 'video':
                    frame = sensor_look(fill(img, CROP[p['src']], z, .5, p.get('cy', .5)), fi)
                else:
                    frame = fill(img, None, z, .5, .5, sharpen=False) if z != 1 else img
            elif kind == 'broll':
                img = reader.next()
                z = p['z0'] + (p['z1'] - p['z0']) * ease(u)
                frame = film_look(fill(img, None, z, p['cx'], p['cy'], sharpen=False), fi)
            elif kind == 'freeze':
                key = (p['src'], p['t0'])
                if key not in frozen:
                    r = Reader(f"src/{p['src']}.mp4", p['t0']); frozen[key] = r.next(); r.close()
                z = p.get('z0', 1.4) + (p.get('z1', 1.4) - p.get('z0', 1.4)) * ease(u)
                frame = sensor_look(fill(frozen[key], CROP[p['src']], z, .5, p.get('cy', .47)), fi)
            elif kind == 'map':
                z = p['z0'] + (p['z1'] - p['z0']) * ease(u)
                c0, c1 = p['c0'], p['c1']
                c = (c0[0] + (c1[0] - c0[0]) * ease(u), c0[1] + (c1[1] - c0[1]) * ease(u))
                j = p.get('jets', (0, 0)); jets = j[0] + (j[1] - j[0]) * ease((lt - .5) / 6.0)
                cap = 0.
                if 'cap' in p: cap = clamp((t - p['cap'][0]) / (p['cap'][1] - p['cap'][0]))
                frame = gfx.map_frame(t, z, c, jets=jets, cap=cap)
            elif kind == 'radar':
                lead = p.get('lead', 0)
                dr = p['d0'] + (p['d1'] - p['d0']) * clamp((lt - lead) / max(d - lead - 2, 1))
                frame = gfx.radar_frame(t, dr, ping=clamp((lt - lead - 1) / .5) if p['d1'] > 0 else 0)
            elif kind == 'parallax':
                frame = gfx.parallax_frame(t, u)
            elif kind == 'cards':
                frame = cards_frame(lt, d, p['items'])
            elif kind == 'files':
                frame = files_frame(lt, d, p['n'], backdrop(reader.next(), u, fi))
            elif kind == 'versus':
                frame = versus_frame(lt, d, backdrop(reader.next(), u, fi), p.get('a1', 3.2), p.get('a2', 5.8), p.get('a3', 12.0),
                                     p.get('final', 'AND NO VIDEO AT ALL.'), p.get('intro', 'HOW LONG DID IT LAST?'))
            elif kind == 'endcard':
                frame = endcard_frame(lt, d, backdrop(reader.next(), u, fi))
            elif kind == 'chapter':
                frame = chapter_frame(lt, d, p['num'], p['title'], fi)
            elif kind == 'crew':
                frame = crew_frame(t, u, p['seats'], p['radar'], fi)
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        for (os_, od, fn) in OVL:
            if os_ <= t < os_ + od: fn(L, t - os_, od)
        frame = Image.alpha_composite(frame.convert('RGBA'), L).convert('RGB')
        enc.stdin.write(frame.tobytes())
        if fi % 150 == 0: print(f'{t:7.1f}s', flush=True)
    if reader: reader.close()
    enc.stdin.close(); enc.wait()

if __name__ == '__main__':
    a = float(sys.argv[1]) if len(sys.argv) > 1 else 0; b = float(sys.argv[2]) if len(sys.argv) > 2 else END
    out = sys.argv[3] if len(sys.argv) > 3 else 'out/film_video.mp4'
    render(a, b, out)
