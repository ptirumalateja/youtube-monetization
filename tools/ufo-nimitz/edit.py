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
        self.p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', str(t0), '-i', path, '-vf', vf, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
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

# ------------------------------------------------------------- timeline
# VO placement (seconds) — matches audio.py
VO = {'b01': .4, 'b02': 11.3, 'b03': 29.2, 'b04': 52.3, 'b05': 74.8, 'b06': 99.0, 'b07': 120.2, 'b08a': 130.4,
      'b08b': 155.4, 'b09': 174.0, 'b10': 217.2, 'b11': 233.6, 'b12': 249.4, 'b13': 272.4, 'b14': 306.2}
END = 336.0
SHOTS = []   # (start, dur, kind, params)
def S(start, dur, kind, **kw): SHOTS.append((start, dur, kind, kw))
OVL = []     # (start, dur, fn(layer, t, dur))
def O(start, dur, fn): OVL.append((start, dur, fn))

NAVY_TAG = 'REAL U.S. NAVY FOOTAGE'
REC_TAG = 'RECONSTRUCTION · BASED ON WITNESS TESTIMONY'
FILE_TAG = 'U.S. NAVY FILE FOOTAGE · NOT FROM THE 2004 INCIDENT'
def B(start, dur, src, t0, z0=1.0, z1=1.07, cx=.5, cy=.5, speed=1.0):
    S(start, dur, 'broll', src=src, t0=t0, z0=z0, z1=z1, cx=cx, cy=cy, speed=speed)
# --- HOOK 0–11.3: FLIR1 tail, object slips out, hit, rewind
S(0.0, 8.9, 'video', src='flir1', t0=66.0, z0=1.35, z1=1.6, cy=.47)
S(8.9, .25, 'black')
S(9.15, 2.15, 'video', src='flir1_rev', t0=76.27 - 75.0, speed=35.0, z0=1.4, z1=1.2, cy=.47)
O(0.0, 11.3, lambda L, t, d: gfx.tag(L, NAVY_TAG + ' · 2004', clamp(t / .2)))
O(0.0, 8.9, lambda L, t, d: gfx.source_line(L, 'U.S. Navy · released by the Department of Defense, 27 Apr 2020'))
O(5.6, 3.3, lambda L, t, d: gfx.headline(L, 'STILL “UNIDENTIFIED”', t, d, y=880, size=104, sub='U.S. DEPARTMENT OF DEFENSE'))
# --- LOCK-IN 11.3–29.2
S(11.3, 15.3, 'video', src='flir1', t0=1.0, z0=1.15, z1=1.55, cy=.47)
O(11.3, 15.3, lambda L, t, d: gfx.tag(L, NAVY_TAG + ' · FLIR1', 1))
O(13.9, 2.0, lambda L, t, d: gfx.headline(L, '2 JETS', t, d))
O(15.9, 2.0, lambda L, t, d: gfx.headline(L, '4 AVIATORS', t, d))
O(19.6, 6.4, lambda L, t, d: gfx.quote(L, 'far superior to anything that we had', 'DAVID FRAVOR · SWORN TESTIMONY TO CONGRESS · 26 JUL 2023', t, d, y=860))
S(26.6, 2.6, 'recon', clip='e4_close', t0=1.0, z0=1.0, z1=1.08)
O(26.6, 2.6, lambda L, t, d: gfx.tag(L, REC_TAG, 1, gfx.CREAM))
# --- BODY 1 29.2–52.3: map + radar
B(29.2, 4.6, 'DOD_111802050', 80.6, 1.0, 1.12)
O(29.2, 8.2, lambda L, t, d: gfx.tag(L, FILE_TAG, 1, gfx.CREAM))
O(29.6, 3.6, lambda L, t, d: gfx.headline(L, 'NOVEMBER 2004', t, d, y=170, size=90))
B(33.8, 3.6, 'DOD_107844340', 14.7, 1.0, 1.1)
O(34.0, 3.4, lambda L, t, d: gfx.lower_third(L, 'USS PRINCETON (CG-59)', 'GUIDED-MISSILE CRUISER · NIMITZ STRIKE GROUP ESCORT', t, d))
S(37.4, 14.9, 'radar', d0=.0, d1=1.0, lead=2.0)
O(37.4, 14.9, lambda L, t, d: gfx.tag(L, 'ILLUSTRATIVE · USS PRINCETON RADAR CONTACTS, AS DESCRIBED', 1, gfx.CREAM))
O(40.2, 3.0, lambda L, t, d: gfx.headline(L, '2+ WEEKS OF CONTACTS', t, d, y=1000, size=64))
# --- BODY 1b 52.3–74.8: the pilots
B(52.3, 3.3, 'DOD_109335834', 0.6, 1.0, 1.08)
B(55.6, 2.9, 'DOD_111579505', 51.3, 1.0, 1.06)
O(52.3, 13.3, lambda L, t, d: gfx.tag(L, FILE_TAG, 1, gfx.CREAM))
O(54.0, 4.3, lambda L, t, d: gfx.lower_third(L, 'CDR DAVID FRAVOR', 'COMMANDING OFFICER · VFA-41 “BLACK ACES”', t, d))
B(58.5, 4.1, 'DOD_111581586', 35.0, 1.0, 1.08)
O(58.7, 3.6, lambda L, t, d: gfx.headline(L, '2 × F/A-18F SUPER HORNETS', t, d, y=170, size=70))
B(62.6, 3.0, 'DOD_112040853', 32.0, 1.0, 1.1)
O(62.9, 3.4, lambda L, t, d: gfx.lower_third(L, 'LT ALEX DIETRICH', 'PILOT · SECOND F/A-18F', t, d))
B(65.6, 4.8, 'DOD_111796027', 2.0, 1.0, 1.1)
O(65.6, 4.8, lambda L, t, d: gfx.tag(L, 'U.S. NAVY FILE FOOTAGE · ILLUSTRATIVE', 1, gfx.CREAM))
S(70.4, 4.4, 'radar', d0=1.0, d1=1.0, lead=0)
O(70.4, 4.4, lambda L, t, d: gfx.tag(L, 'ILLUSTRATIVE', 1, gfx.CREAM))
O(70.6, 4.0, lambda L, t, d: gfx.headline(L, 'EXERCISE CALLED OFF', t, d, y=1000, size=70, color=gfx.RED))
# --- BODY 2 74.8–99.0: encounter (reconstruction)
B(74.8, 5.0, 'DOD_111585732', 0.0, 1.0, 1.1)
O(74.8, 5.0, lambda L, t, d: gfx.tag(L, 'U.S. NAVY FILE FOOTAGE · ILLUSTRATIVE', 1, gfx.CREAM))
S(79.8, 6.0, 'recon', clip='e2_lookdown', t0=0, z0=1.0, z1=1.1)
S(85.8, 6.6, 'recon', clip='e3_mid', t0=0.3, z0=1.0, z1=1.12)
S(92.4, 6.6, 'recon', clip='e4_close', t0=0.2, z0=1.0, z1=1.1)
O(79.8, 19.2, lambda L, t, d: gfx.tag(L, REC_TAG, 1, gfx.CREAM))
O(77.0, 2.6, lambda L, t, d: gfx.headline(L, 'CLEAR SKY · CALM SEA', t, d, y=1000, size=56))
O(87.6, 4.6, lambda L, t, d: gfx.quote(L, 'a white Tic Tac object', 'DAVID FRAVOR · SWORN TESTIMONY · 2023', t, d, y=900))
O(94.6, 4.0, lambda L, t, d: gfx.headline(L, 'NO WINGS. NO ROTORS.', t, d, y=980, size=78))
# --- BODY 2b 99.0–120.2
S(99.0, 6.0, 'recon', clip='e5_spiral', t0=0, z0=1.0, z1=1.1)
S(105.0, 4.0, 'recon', clip='e6_climb', t0=0, z0=1.0, z1=1.15)
S(109.0, 3.0, 'recon', clip='e7_gone', t0=0, z0=1.0, z1=1.05)
S(112.0, 6.0, 'recon', clip='e8_calm', t0=0, z0=1.0, z1=1.08)
S(118.0, 2.2, 'black')
O(99.0, 19.0, lambda L, t, d: gfx.tag(L, REC_TAG, 1, gfx.CREAM))
O(100.6, 4.3, lambda L, t, d: gfx.quote(L, 'aligned it with my aircraft, and began to climb', 'DAVID FRAVOR · SWORN TESTIMONY · 2023', t, d, y=900))
O(109.6, 2.3, lambda L, t, d: gfx.headline(L, 'GONE.', t, d, size=150))
O(114.6, 3.2, lambda L, t, d: gfx.headline(L, 'THE WHITEWATER TOO.', t, d, y=980, size=64))
# --- REHOOK 1 120.2–130.4
S(120.2, 10.2, 'map', z0=2.4, z1=2.0, c0=(-118.05, 31.5), c1=(-118.45, 31.75), jets=(1, 1), cap=(121.8, 123.0))
O(120.2, 10.2, lambda L, t, d: gfx.tag(L, 'ILLUSTRATIVE MAP', 1, gfx.CREAM))
O(124.6, 5.6, lambda L, t, d: gfx.headline(L, '60 MILES. UNDER A MINUTE.', t, d, y=900, size=104))
# --- BODY 3 130.4–174: FLIR1 explained
B(130.4, 4.2, 'DOD_111579505', 51.2, 1.0, 1.08)
O(130.4, 4.2, lambda L, t, d: gfx.tag(L, FILE_TAG, 1, gfx.CREAM))
S(134.6, 20.4, 'video', src='flir1', t0=0.0, z0=1.0, z1=1.22, cy=.47)
S(155.0, 14.4, 'video', src='flir1', t0=61.8, z0=1.25, z1=1.6, cy=.47)
S(169.4, 1.6, 'freeze', src='flir1', t0=75.5)
O(134.6, 36.4, lambda L, t, d: gfx.tag(L, NAVY_TAG + ' · FLIR1 · 14 NOV 2004', 1))
O(134.6, 36.4, lambda L, t, d: gfx.source_line(L, 'U.S. Navy / DoD release, 27 Apr 2020'))
O(136.0, 4.5, lambda L, t, d: gfx.headline(L, '≈ 90 SECONDS OF INFRARED', t, d, y=1000, size=60))
O(144.0, 4.0, lambda L, t, d: gfx.headline(L, 'THIS CREW NEVER SAW IT BY EYE', t, d, y=1000, size=60, color=gfx.RED))
O(148.6, 5.6, lambda L, t, d: gfx.headline(L, 'A LATER FLIGHT — NOT THE CLOSE ENCOUNTER', t, d, y=1000, size=54))
O(160.8, 6.5, lambda L, t, d: gfx.callout_box(L, 820, 520, 330, 180, 'BURST OF SPEED — OR LOST LOCK?', t, d))
# --- BODY 4 171–217: GOFAST + reversal
S(171.0, 29.0, 'video', src='gofast', t0=0.0, z0=1.0, z1=1.2, cy=.5)
S(200.0, 17.2, 'parallax')
O(171.0, 29.0, lambda L, t, d: gfx.tag(L, NAVY_TAG + ' · GOFAST · JAN 2015', 1))
O(171.0, 29.0, lambda L, t, d: gfx.source_line(L, 'U.S. Navy / DoD release, 27 Apr 2020'))
O(185.0, 4.0, lambda L, t, d: gfx.headline(L, 'AARO · 2025', t, d, y=170, size=80, color=gfx.RED))
O(190.4, 6.0, lambda L, t, d: gfx.headline(L, '≈ 13,000 FT UP', t, d, y=1000, size=88))
O(200.0, 17.2, lambda L, t, d: gfx.tag(L, 'ILLUSTRATIVE · AFTER AARO GOFAST ANALYSIS, FEB 2025', 1, gfx.CREAM))
O(206.0, 5.2, lambda L, t, d: gfx.headline(L, '5 – 92 MPH', t, d, y=170, size=110))
O(211.2, 5.8, lambda L, t, d: gfx.quote(L, 'did not move at anomalous speeds', 'AARO GOFAST CASE RESOLUTION · FEB 2025', t, d, y=330))
# --- PIVOT 217.2–233
S(217.2, 2.6, 'video', src='gofast', t0=20.0, z0=1.2, z1=1.3)
S(219.8, 2.7, 'recon', clip='e4_close', t0=3.0, z0=1.05, z1=1.15)
S(222.5, 2.9, 'recon', clip='e5_spiral', t0=3.0, z0=1.0, z1=1.1)
O(219.8, 5.6, lambda L, t, d: gfx.tag(L, REC_TAG, 1, gfx.CREAM))
B(225.4, 3.0, 'DOD_111581586', 61.0, 1.0, 1.08)
B(228.4, 2.0, 'DOD_111581586', 4.6, 1.0, 1.1)
B(230.4, 2.6, 'DOD_107844340', 24.0, 1.0, 1.1)
O(225.4, 7.6, lambda L, t, d: gfx.tag(L, FILE_TAG, 1, gfx.CREAM))
O(225.4, 3.0, lambda L, t, d: gfx.headline(L, '4 AVIATORS', t, d))
O(228.4, 2.0, lambda L, t, d: gfx.headline(L, '2 JETS', t, d))
O(230.4, 2.6, lambda L, t, d: gfx.headline(L, '1 WARSHIP’S RADAR', t, d))
# --- MONTAGE + 2026 FILES 233–272.4  (montage clips added when available)
B(233.0, 2.8, 'DOD_111579505', 32.4, 1.0, 1.1)
B(235.8, 2.1, 'DOD_112040853', 9.9, 1.0, 1.08)
B(237.9, 3.3, 'DOD_112040853', 18.3, 1.0, 1.08)
B(241.2, 4.0, 'DOD_111796027', 41.8, 1.0, 1.08)
B(245.2, 4.2, 'DOD_112040853', 56.3, 1.0, 1.1)
O(233.0, 16.4, lambda L, t, d: gfx.tag(L, 'U.S. NAVY FILE FOOTAGE · ILLUSTRATIVE', 1, gfx.CREAM))
O(236.0, 4.4, lambda L, t, d: gfx.headline(L, 'THE REPORTS NEVER STOPPED', t, d, y=980, size=72))
O(241.6, 5.4, lambda L, t, d: gfx.headline(L, '757 NEW REPORTS IN 13 MONTHS', t, d, y=980, size=72, sub='AARO ANNUAL REPORT · NOV 2024'))
S(249.4, 23.0, 'files', n=7, bg=('src/DOD_111796027.mp4', 0.5, .38))
O(249.4, 23.0, lambda L, t, d: gfx.tag(L, 'WAR.GOV/UFO · 7 RELEASES · MAY–OCT 2026', 1, gfx.CREAM))
O(262.0, 4.0, lambda L, t, d: gfx.headline(L, '23 OCT 2026', t, d, y=170, size=96))
O(266.4, 5.8, lambda L, t, d: gfx.headline(L, 'DOCUMENTS ONLY. NO NEW VIDEO.', t, d, y=980, size=70))
# --- BODY 5 272.4–306: triangle
S(272.4, 14.0, 't_recon', clip='t1_triangle', t0=0)
O(272.4, 14.0, lambda L, t, d: gfx.tag(L, 'RECONSTRUCTION · BASED ON WITNESS DOCUMENTS · NO VIDEO EXISTS', 1, gfx.CREAM))
O(272.6, 4.6, lambda L, t, d: gfx.lower_third(L, 'AARO MEMO DOW-UAP-D176', 'FBI FD-302 · FBI-UAP-D043', t, d))
O(279.2, 3.2, lambda L, t, d: gfx.headline(L, 'MATTE BLACK · ~15 FT', t, d, y=980, size=64))
O(282.6, 3.6, lambda L, t, d: gfx.headline(L, 'NO SOUND. NO EXHAUST.', t, d, y=980, size=64))
S(286.4, 19.8, 'versus', bg=('clips/t1_triangle.mp4', 0.0, .7))
# --- CLOSE 306.2–336
B(306.2, 7.2, 'DOD_111796027', 46.4, 1.0, 1.12, speed=.6)
S(313.4, 6.8, 'recon', clip='e4_close', t0=0.0, z0=1.12, z1=1.0)
S(320.2, 8.0, 'freeze', src='flir1', t0=4.0, z0=1.5, z1=1.9, cy=.47)
S(328.2, 7.8, 'endcard')
O(306.2, 7.2, lambda L, t, d: gfx.tag(L, 'U.S. NAVY FILE FOOTAGE · ILLUSTRATIVE', 1, gfx.CREAM))
O(313.4, 6.8, lambda L, t, d: gfx.tag(L, REC_TAG, 1, gfx.CREAM))
O(308.4, 5.6, lambda L, t, d: gfx.quote(L, 'We don’t know what it was.', 'ALEX DIETRICH · F/A-18F PILOT · 2021', t, d, y=900))
O(314.4, 5.6, lambda L, t, d: gfx.headline(L, 'NOT PROOF. NOT EXPLAINED.', t, d, y=980, size=78))
O(320.2, 8.0, lambda L, t, d: gfx.tag(L, NAVY_TAG + ' · FLIR1', 1))

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

def versus_frame(t, d, bg):
    im = bg; L = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    a1 = clamp((t - 3.2) / .2); a2 = clamp((t - 5.8) / .2)
    f = gfx.font('black', 170)
    if a1 > 0:
        gfx.shadow_text(L, (W * .27, 500), '30+ SEC', f, gfx.CREAM + (int(255 * a1),))
        gfx.shadow_text(L, (W * .27, 640), 'AARO MEMO', gfx.font('monob', 36), (210, 200, 180, int(255 * a1)))
    if a2 > 0:
        gfx.shadow_text(L, (W * .73, 500), '~3 SEC', f, gfx.RED + (int(255 * a2),))
        gfx.shadow_text(L, (W * .73, 640), 'FBI WRITE-UP', gfx.font('monob', 36), (210, 200, 180, int(255 * a2)))
    if a1 > 0 and a2 > 0:
        ImageDraw.Draw(L).line([(W / 2, 360), (W / 2, 700)], fill=(120, 120, 130, 200), width=3)
    a3 = clamp((t - 12.0) / .3)
    if a3 > 0:
        gfx.headline(L, 'AND NO VIDEO AT ALL.', t - 12.0, d - 12.0, y=880, size=80)
    if t < 3.2:
        gfx.headline(L, 'HOW LONG DID IT LAST?', t, 3.2, y=540, size=96)
    return Image.alpha_composite(im.convert('RGBA'), L).convert('RGB')

def endcard_frame(t, d):
    im = Image.new('RGB', (W, H), (6, 8, 14)); L = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    a = clamp(t / .6)
    gfx.shadow_text(L, (W / 2, 470), 'SLOW LIGHT', gfx.font('black', 130), gfx.CREAM + (int(255 * a),))
    gfx.shadow_text(L, (W / 2, 570), 'stories worth slowing down for', gfx.font('serif', 52), (215, 205, 185, int(255 * a)))
    b = clamp((t - 1.2) / .5)
    gfx.shadow_text(L, (W / 2, 760), 'SUBSCRIBE FOR THE NEXT FILE', gfx.font('monob', 34), gfx.RED + (int(255 * b),))
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
                frame = versus_frame(lt, d, backdrop(reader.next(), u, fi))
            elif kind == 'endcard':
                frame = endcard_frame(lt, d)
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
