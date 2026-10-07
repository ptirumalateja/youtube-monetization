#!/usr/bin/env python3
"""Assemble the Slow Light long-form: "What If We're Looking for Aliens in the Wrong Place?" (1920x1080, 30 fps).

Run from this folder:  python3 build_long.py [--clips DIR]
Inputs:  audio/narration_raw.mp3 + audio/words.json (single Higgsfield take, Scribe timings)
         stills/*.png (Qwen, 16:9), gfx/*.mp4 (scripts/gfx_aliens.py), clips/*.mp4 (LTX-2.3, SeedVR2-upscaled if present)
Output:  out/aliens_long.mp4, out/aliens_long.srt

All shot boundaries are written on the ORIGINAL narration clock; silences inserted into the narration
(pre-roll, after "Wow!", the title card, after "technosignatures") shift everything after them.
"""
import json, math, os, subprocess, sys
import numpy as np

W, H, FPS, SR = 1920, 1080, 30, 48000
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
CLIPS = sys.argv[sys.argv.index("--clips") + 1] if "--clips" in sys.argv else "clips"
FONTS = os.path.join(HERE, "..", "..", "edit_v7", "fonts")
os.makedirs("out/seg", exist_ok=True)

NARR_END = 232.3
PRE = 2.5                                     # black + static before the first word
INSERTS = [(24.6, 0.8, None),                 # breathe after "Wow!"
           (27.3, 4.0, "gfx/T_title.mp4"),    # title card after "It was never heard again."
           (122.4, 0.8, None)]                # breathe after "technosignatures"
TAIL_HOLD, TAIL_BLACK, END_CARD = 3.5, 1.5, 6.0


def shift(t):
    return t + PRE + sum(d for at, d, _ in INSERTS if t > at)


# (orig_start, orig_end, kind, source, options)   kinds: clip, still, gfx
SHOTS = [
    (0.0, 9.2, "clip", "A01_bigear", {}),
    (9.2, 12.8, "gfx", "G01_scope", {}),
    (12.8, 25.7, "gfx", "G02_printout", {}),
    (25.7, 27.3, "still", "A02_emptysky", {"zoom": "in"}),
    (27.3, 34.8, "clip", "A03_dish1960", {}),
    (34.8, 44.1, "still", "A04_drake", {"zoom": "in"}),
    (44.1, 57.5, "gfx", "G03_spectrum", {}),
    (57.5, 61.5, "still", "A05_chart", {"zoom": "in"}),
    (61.5, 71.5, "still", "A06_fermi", {"zoom": "in"}),
    (71.5, 74.0, "still", "A09_deepfield", {"zoom": "out", "focus": 0.28}),
    (74.0, 79.1, "clip", "A07_array", {}),
    (79.1, 83.6, "still", "A08_parkes", {"zoom": "in"}),
    (83.6, 93.0, "gfx", "G05_timeline", {}),
    (93.0, 98.6, "still", "A09_deepfield", {"zoom": "in", "focus": 0.25, "dim": 0.7}),
    (98.6, 106.0, "clip", "A10_earthnight", {}),
    (106.0, 121.1, "still", "A10_earthnight", {"zoom": "out"}),
    (121.1, 123.3, "gfx", "G06_techno", {}),
    (123.3, 138.6, "still", "A11_exoplanet", {"zoom": "in"}),
    (138.6, 147.2, "clip", "A12_listener", {}),
    (147.2, 157.3, "clip", "A13_cockpit", {}),
    (157.3, 171.8, "gfx", "G08a_grid", {}),
    (171.8, 178.0, "gfx", "G08b_grid", {}),
    (178.0, 184.9, "still", "A14_archive", {"zoom": "in"}),
    (184.9, 190.8, "still", "A15_lonelight", {"zoom": "in"}),
    (190.8, 193.8, "still", "A02_emptysky", {"zoom": "out", "dim": 0.75}),
    (193.8, 202.4, "still", "A07_array", {"zoom": "out"}),
    (202.4, 211.1, "gfx", "G10_scale", {}),
    (211.1, 216.3, "clip", "A16_hottub", {}),
    (216.3, 219.8, "still", "A17_abyss", {"zoom": "in"}),
    (219.8, 225.4, "still", "A01_bigear", {"zoom": "out"}),
    (225.4, NARR_END, "clip", "A18_end", {"tail": TAIL_HOLD}),
]

# On-screen words (orig time, text): quiet labels, never more than one line.
LABELS = [
    (71.6, 74.0, "where is everybody?", "big"),
    (108.2, 121.0, "CITY LIGHTS", "l1"), (110.3, 121.0, "RADIO LEAKAGE", "l2"), (113.4, 121.0, "CHANGED AIR", "l3"),
    (129.7, 138.5, "ARTIFICIAL LIGHT", "l1"), (132.6, 138.5, "A GAS NATURE DOESN'T MAKE", "l2"), (136.1, 138.5, "WASTE HEAT", "l3"),
]


def run(cmd):
    subprocess.run(cmd, check=True)


def dur(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]))


GRADE = "eq=contrast=1.04:saturation=0.92:gamma=0.98,vignette=angle=PI/4.5,noise=alls=6:allf=t"


def render_segment(i, a, b, kind, src, opt):
    t0, t1 = shift(a), shift(b) + opt.get("tail", 0.0)
    n = round(t1 * FPS) - round(t0 * FPS)
    out = f"out/seg/{i:02d}_{src}.mp4"
    dim = opt.get("dim", 1.0)
    if kind == "still":
        zin = opt.get("zoom", "in") == "in"
        fy = opt.get("focus", 0.5)
        z = f"1.0+0.07*on/{n}" if zin else f"1.07-0.07*on/{n}"
        vf = (f"scale=2880:-2:flags=lanczos,zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*{fy}':d={n}:s={W}x{H}:fps={FPS},"
              f"eq=brightness={-(1 - dim) * 0.25:.3f},{GRADE},format=yuv420p")
        run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", f"stills/{src}.png", "-vf", vf, "-frames:v", str(n),
             "-c:v", "libx264", "-crf", "16", "-preset", "medium", out])
    else:
        path = f"gfx/{src}.mp4" if kind == "gfx" else f"{CLIPS}/{src}.mp4"
        d = dur(path)
        slot = n / FPS
        speed = 1.0 if kind == "gfx" else min(max(slot / d, 1.0), 1.5)   # slow clips down up to 1.5x, then hold
        g = "" if kind == "gfx" else GRADE + ","
        vf = (f"setpts={speed:.4f}*PTS,fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
              f"tpad=stop_mode=clone:stop_duration={slot + 2:.2f},{g}format=yuv420p")
        run(["ffmpeg", "-v", "error", "-y", "-i", path, "-vf", vf, "-an", "-frames:v", str(n),
             "-c:v", "libx264", "-crf", "16", "-preset", "medium", out])
    return out


# ---------- picture ----------
parts = []
segs = []
for i, (a, b, kind, src, opt) in enumerate(SHOTS):
    segs.append((a, b, kind, src, opt))
    for at, d, vis in INSERTS:
        if vis and abs(at - b) < 1e-6:
            segs.append(("INSERT", at, d, vis))
idx = 0
pre = "out/seg/00_pre.mp4"
run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=0x020305:s={W}x{H}:r={FPS}", "-frames:v", str(round(PRE * FPS)),
     "-vf", "noise=alls=5:allf=t,format=yuv420p", "-c:v", "libx264", "-crf", "16", pre])
parts.append(pre)
for s in segs:
    idx += 1
    if s[0] == "INSERT":
        _, at, d, vis = s
        out = f"out/seg/{idx:02d}_insert.mp4"
        run(["ffmpeg", "-v", "error", "-y", "-i", vis, "-vf", f"fps={FPS},tpad=stop_mode=clone:stop_duration=3,format=yuv420p",
             "-frames:v", str(round(d * FPS)), "-c:v", "libx264", "-crf", "16", out])
        parts.append(out)
    else:
        parts.append(render_segment(idx, *s))
    print("seg", idx, parts[-1])
blk = "out/seg/zz_black.mp4"
run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:r={FPS}", "-frames:v", str(round(TAIL_BLACK * FPS)),
     "-vf", "format=yuv420p", "-c:v", "libx264", "-crf", "16", blk])
endc = "out/seg/zz_end.mp4"
run(["ffmpeg", "-v", "error", "-y", "-i", "gfx/T_end.mp4", "-vf", f"fps={FPS},format=yuv420p", "-frames:v", str(round(END_CARD * FPS)),
     "-c:v", "libx264", "-crf", "16", endc])
parts += [blk, endc]
with open("out/concat.txt", "w") as f:
    f.writelines(f"file '{os.path.abspath(p)}'\n" for p in parts)
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "out/concat.txt", "-c", "copy", "out/picture.mp4"])
TOTAL = dur("out/picture.mp4")
LAST_WORD = shift(NARR_END)
print("picture", TOTAL)

# ---------- labels (ASS, quiet fades) ----------
POS = {"big": (W // 2, 560, 64, "Cinzel"), "l1": (W // 2, 820, 34, "Montserrat"), "l2": (W // 2, 880, 34, "Montserrat"), "l3": (W // 2, 940, 34, "Montserrat")}


def ts(t):
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


ass = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "",
       "[V4+ Styles]", "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
       "Style: Lab,Montserrat,34,&H00E4E6E2,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,6,0,1,0,2,5,0,0,0,1",
       "Style: Big,Cinzel,64,&H00E4E6E2,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,2,0,1,0,3,5,0,0,0,1",
       "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
for a, b, text, slot in LABELS:
    x, y, size, fnt = POS[slot]
    style = "Big" if slot == "big" else "Lab"
    ass.append(f"Dialogue: 0,{ts(shift(a))},{ts(shift(b))},{style},,0,0,0,,{{\\pos({x},{y})\\fad(700,600)}}{text}")
open("out/labels.ass", "w").write("\n".join(ass) + "\n")

# ---------- subtitles (SRT for YouTube upload, from Scribe word timings) ----------
words = [w for w in json.load(open("audio/words.json"))["words"] if w["type"] == "word"]
srt, cur, n = [], [], 1


def flush():
    global n, cur
    if not cur:
        return
    a, b = shift(cur[0]["start"]), shift(cur[-1]["end"])
    f = lambda t: f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(t * 1000 % 1000):03d}"
    srt.append(f"{n}\n{f(a)} --> {f(b)}\n{' '.join(w['text'] for w in cur)}\n")
    n += 1
    cur = []


for w in words:
    cur.append(w)
    if w["text"].rstrip('"').endswith((".", "?", "!", ":")) or len(cur) >= 9:
        flush()
flush()
open("out/aliens_long.srt", "w").write("\n".join(srt))

# ---------- audio ----------
# narration with inserted silences
narr = "out/narr_shifted.wav"
segs_a, prev = [], 0.0
cuts = sorted([(at, d) for at, d, _ in INSERTS])
filt, labels = [], []
for k, (at, d) in enumerate(cuts + [(None, 0)]):
    end = at if at is not None else 10_000
    filt.append(f"[0:a]atrim={prev}:{end},asetpts=N/SR/TB[n{k}]")
    labels.append(f"[n{k}]")
    if at is not None:
        filt.append(f"anullsrc=r={SR}:cl=mono,atrim=0:{d}[s{k}]")
        labels.append(f"[s{k}]")
        prev = at
fc = ";".join(filt) + ";" + "".join(labels) + f"concat=n={len(labels)}:v=0:a=1,adelay={int(PRE * 1000)},apad=whole_dur={TOTAL}[out]"
run(["ffmpeg", "-v", "error", "-y", "-i", "audio/narration_raw.mp3", "-filter_complex", fc, "-map", "[out]", "-ac", "1", "-ar", str(SR), narr])

# eerie bed, synthesised: a low drone that slowly rises, radio static where the story is about listening
N = int(TOTAL * SR)
t = np.arange(N) / SR
rng = np.random.default_rng(1977)
env = np.clip(0.35 + 0.65 * (t / LAST_WORD), 0, 1)                         # slowly rising over the film
lfo = 0.6 + 0.4 * np.sin(2 * np.pi * t / 23.0)
drone = (np.sin(2 * np.pi * 41.2 * t) + 0.6 * np.sin(2 * np.pi * 61.9 * t + 0.4 * np.sin(2 * np.pi * 0.07 * t))
         + 0.25 * np.sin(2 * np.pi * 82.4 * t * (1 + 0.002 * np.sin(2 * np.pi * 0.11 * t))))
air = np.convolve(rng.normal(0, 1, N), np.ones(400) / 400, mode="same") * 6       # dark wind
bed = (drone * 0.55 + air * 0.35) * env * lfo


def window(a, b, fade=1.2):
    w = np.zeros(N)
    i0, i1 = int(a * SR), min(N, int(b * SR))
    if i1 <= i0:
        return w
    seg = np.ones(i1 - i0)
    f = int(fade * SR)
    f = min(f, len(seg) // 2)
    seg[:f] = np.linspace(0, 1, f)
    seg[-f:] = np.linspace(1, 0, f)
    w[i0:i1] = seg
    return w


hiss = rng.normal(0, 1, N)
hiss = hiss - np.convolve(hiss, np.ones(8) / 8, mode="same")                          # thin, high radio static
crackle = (rng.random(N) < 0.0006) * rng.normal(0, 6, N)
static = (hiss * 0.5 + crackle) * (window(0, PRE + 1.5, 0.4) * 0.9 + window(shift(9.2), shift(25.0), 0.8) * 0.45
                                   + window(shift(57.5), shift(61.6), 0.6) * 0.8 + window(shift(44.1), shift(57.5), 1.5) * 0.2)
# hush: the bed drops away for the big silences
duck = np.ones(N)
for a, b in [(shift(24.5), shift(25.7)), (shift(121.2), shift(123.3))]:
    duck -= window(a, b, 0.3) * 0.85
fin = window(0, LAST_WORD + 1.5, 0.01)
tail = np.clip(1 - (t - LAST_WORD) / 2.5, 0, 1)
duck *= np.where(t > LAST_WORD, tail, 1) * 1.0
boom_t = shift(27.3)
boom = np.exp(-np.clip(t - boom_t, 0, None) * 1.6) * np.sin(2 * np.pi * 34 * t) * (t >= boom_t) * 1.6
bed_all = (bed * 0.5 + static * 0.18) * duck + boom * 0.5 * (t < boom_t + 5)
# the end card gets a faint, cold tone
endtone = window(TOTAL - END_CARD + 0.5, TOTAL, 1.5) * np.sin(2 * np.pi * 220 * t) * 0.03
mix_bed = bed_all + endtone
mix_bed = mix_bed / (np.abs(mix_bed).max() + 1e-9) * 0.35
import wave
with wave.open("out/bed.wav", "wb") as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes((np.clip(mix_bed, -1, 1) * 32767).astype(np.int16).tobytes())

run(["ffmpeg", "-v", "error", "-y", "-i", narr, "-i", "out/bed.wav", "-filter_complex",
     "[0:a]highpass=f=70,acompressor=threshold=0.1:ratio=2.5:attack=15:release=250,volume=1.0[n];"
     "[1:a]volume=0.55,lowpass=f=6000[b];[n][b]amix=inputs=2:normalize=0:duration=longest,"
     "volume=2.2,alimiter=limit=0.89:level=disabled[a]",
     "-map", "[a]", "-ar", str(SR), "-ac", "2", "out/mix.wav"])

# ---------- final ----------
run(["ffmpeg", "-v", "error", "-y", "-i", "out/picture.mp4", "-i", "out/mix.wav",
     "-vf", f"ass=out/labels.ass:fontsdir={FONTS}", "-c:v", "libx264", "-crf", "17", "-preset", "slow", "-pix_fmt", "yuv420p",
     "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", "-shortest", "out/aliens_long.mp4"])
print("done", dur("out/aliens_long.mp4"), "s")
