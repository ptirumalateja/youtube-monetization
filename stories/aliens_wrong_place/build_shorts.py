#!/usr/bin/env python3
"""Two 9:16 Shorts cut from the aliens long-form narration (1080x1920, 30 fps).

Run from this folder:  python3 build_shorts.py [short1|short2 ...]
Inputs: audio/narration_raw.mp3, audio/words.json, stills_v/*.png, gfx/*_v.mp4, clips_v/*.mp4
Output: out/short1.mp4, out/short2.mp4 (burned-in captions, current word in amber)
"""
import json, os, subprocess, sys, wave
import numpy as np

W, H, FPS, SR = 1080, 1920, 30, 48000
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
FONTS = os.path.join(HERE, "..", "..", "edit_v7", "fonts")
os.makedirs("out/sseg", exist_ok=True)

SHORTS = {
    "short1": {
        "pieces": [(0.0, 27.1), (211.1, 218.7), (225.4, 232.3)],
        "inserts": [(24.6, 0.8)],
        "shots": [(0.0, 9.2, "still", "A01_bigear"), (9.2, 12.8, "gfx", "G01_scope_v"), (12.8, 25.7, "gfx", "G02_printout_v"),
                  (25.7, 27.1, "still", "A02_emptysky"), (211.1, 216.3, "clip", "A16_hottub"), (216.3, 218.7, "still", "A17_abyss"),
                  (225.4, 232.3, "clip", "A18_end")],
        "kicker": "THE UNKNOWN",
    },
    "short2": {
        "pieces": [(90.0, 94.4), (190.8, 232.3)],
        "inserts": [],
        "shots": [(90.0, 94.4, "still", "A09_deepfield"), (190.8, 193.8, "still", "A02_emptysky"), (193.8, 202.4, "still", "A07_array"),
                  (202.4, 211.1, "gfx", "G10_scale_v"), (211.1, 216.3, "clip", "A16_hottub"), (216.3, 219.8, "still", "A17_abyss"),
                  (219.8, 225.4, "still", "A01_bigear"), (225.4, 232.3, "clip", "A18_end")],
        "kicker": "THE UNKNOWN",
    },
}
PRE, GAP, TAIL, END_CARD = 0.6, 0.9, 2.2, 2.5
GRADE = "eq=contrast=1.04:saturation=0.92:gamma=0.98,vignette=angle=PI/4.5,noise=alls=6:allf=t"


def run(cmd):
    subprocess.run(cmd, check=True)


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))


def build(name, cfg):
    pieces, inserts = cfg["pieces"], cfg["inserts"]
    # map original narration time -> short time
    starts, t = [], PRE
    for a, b in pieces:
        starts.append(t)
        t += (b - a) + sum(d for at, d in inserts if a < at < b) + GAP
    speech_end = t - GAP

    def m(x):
        for (a, b), s in zip(pieces, starts):
            if a - 1e-6 <= x <= b + 1e-6:
                return s + (x - a) + sum(d for at, d in inserts if a < at < x)
        raise ValueError(x)

    total = speech_end + TAIL + END_CARD
    # ---------- picture ----------
    parts = []
    shots = cfg["shots"]
    bounds = []
    for k, (a, b, kind, src) in enumerate(shots):
        t0 = 0 if k == 0 else bounds[-1][1]
        last_of_piece = (k + 1 == len(shots)) or not any(p[0] <= shots[k + 1][0] <= p[1] and p[0] <= a <= p[1] for p in pieces)
        t1 = m(b) + (GAP if last_of_piece and k + 1 < len(shots) else 0) + (TAIL if k + 1 == len(shots) else 0)
        bounds.append((t0, t1))
    for k, ((a, b, kind, src), (t0, t1)) in enumerate(zip(shots, bounds)):
        n = round(t1 * FPS) - round(t0 * FPS)
        out = f"out/sseg/{name}_{k:02d}_{src}.mp4"
        if kind == "still":
            zin = k % 2 == 0
            z = f"1.0+0.08*on/{n}" if zin else f"1.08-0.08*on/{n}"
            vf = (f"scale=1620:-2:flags=lanczos,zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS},"
                  f"{GRADE},format=yuv420p")
            run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", f"stills_v/{src}.png", "-vf", vf, "-frames:v", str(n),
                 "-c:v", "libx264", "-crf", "17", "-preset", "medium", out])
        else:
            path = f"gfx/{src}.mp4" if kind == "gfx" else f"clips_v/{src}.mp4"
            d = dur(path)
            slot = n / FPS
            speed = 1.0 if kind == "gfx" else min(max(slot / d, 1.0), 1.5)
            g = "" if kind == "gfx" else GRADE + ","
            vf = (f"setpts={speed:.4f}*PTS,fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                  f"tpad=stop_mode=clone:stop_duration={slot + 2:.2f},{g}format=yuv420p")
            run(["ffmpeg", "-v", "error", "-y", "-i", path, "-vf", vf, "-an", "-frames:v", str(n),
                 "-c:v", "libx264", "-crf", "17", "-preset", "medium", out])
        parts.append(out)
    endc = f"out/sseg/{name}_zz_end.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-i", "gfx/T_end_v.mp4", "-vf", f"fps={FPS},format=yuv420p", "-frames:v", str(round(END_CARD * FPS)),
         "-c:v", "libx264", "-crf", "17", endc])
    parts.append(endc)
    with open(f"out/{name}_concat.txt", "w") as f:
        f.writelines(f"file '{os.path.abspath(p)}'\n" for p in parts)
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"out/{name}_concat.txt", "-c", "copy", f"out/{name}_pic.mp4"])
    total = dur(f"out/{name}_pic.mp4")

    # ---------- captions: 1-4 word chunks, current word amber ----------
    words = [w for w in json.load(open("audio/words.json"))["words"] if w["type"] == "word"]
    sel = [w for w in words if any(a - 0.05 <= w["start"] <= b for a, b in pieces)]
    chunks, cur = [], []
    for w in sel:
        cur.append(w)
        if len(cur) >= 4 or w["text"].rstrip('"').endswith((".", ",", "?", "!", ":")):
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)

    def ts(x):
        return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}"

    ass = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "", "[V4+ Styles]",
           "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
           "Style: Cap,Montserrat,66,&H00F2F4F2,&H000000FF,&H00101010,&H96000000,-1,0,0,0,100,100,0,0,1,4,2,5,80,80,0,1",
           "Style: Kick,Montserrat,30,&H00B9BE6E,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,8,0,1,0,0,8,0,0,150,1",
           "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    ass.append(f"Dialogue: 0,{ts(0)},{ts(3.2)},Kick,,0,0,0,,{{\\fad(400,600)}}SLOW LIGHT  ·  {cfg['kicker']}")
    for ch in chunks:
        for i, w in enumerate(ch):
            a = m(w["start"])
            b = m(ch[i + 1]["start"]) if i + 1 < len(ch) else m(w["end"]) + 0.25
            txt = " ".join((f"{{\\c&H54B0E8&}}{x['text']}{{\\c&HF2F4F2&}}" if j == i else x["text"]) for j, x in enumerate(ch))
            ass.append(f"Dialogue: 0,{ts(a)},{ts(b)},Cap,,0,0,0,,{{\\pos({W // 2},{int(H * 0.66)})}}{txt}")
    open(f"out/{name}.ass", "w").write("\n".join(ass) + "\n")

    # ---------- audio: narration pieces + eerie bed ----------
    fc, labs = [], []
    for k, (a, b) in enumerate(pieces):
        cuts = [(at, d) for at, d in inserts if a < at < b]
        prev = a
        for j, (at, d) in enumerate(cuts + [(None, 0)]):
            end = at if at is not None else b
            fc.append(f"[0:a]atrim={prev}:{end},asetpts=N/SR/TB[p{k}_{j}]")
            labs.append(f"[p{k}_{j}]")
            if at is not None:
                fc.append(f"anullsrc=r={SR}:cl=mono,atrim=0:{d}[q{k}_{j}]")
                labs.append(f"[q{k}_{j}]")
                prev = at
        fc.append(f"anullsrc=r={SR}:cl=mono,atrim=0:{GAP}[g{k}]")
        labs.append(f"[g{k}]")
    fc = ";".join(fc) + ";" + "".join(labs) + f"concat=n={len(labs)}:v=0:a=1,adelay={int(PRE * 1000)},apad=whole_dur={total}[o]"
    run(["ffmpeg", "-v", "error", "-y", "-i", "audio/narration_raw.mp3", "-filter_complex", fc, "-map", "[o]", "-ac", "1", "-ar", str(SR),
         f"out/{name}_narr.wav"])
    N = int(total * SR)
    tt = np.arange(N) / SR
    rng = np.random.default_rng(72)
    drone = (np.sin(2 * np.pi * 41.2 * tt) + 0.6 * np.sin(2 * np.pi * 61.9 * tt) + 0.32 * np.sin(2 * np.pi * 123.5 * tt) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.09 * tt))
             + 0.16 * np.sin(2 * np.pi * 185.0 * tt + 0.8 * np.sin(2 * np.pi * 0.05 * tt)))
    env = np.clip(0.5 + 0.5 * tt / speech_end, 0, 1) * np.clip(1 - (tt - speech_end) / 2.0, 0, 1)
    hiss = rng.normal(0, 1, N)
    c = np.cumsum(np.concatenate([[0.0], hiss]))
    hiss = hiss - np.concatenate([(c[8:] - c[:-8]) / 8, np.zeros(7)])
    stat = np.where(tt < PRE + 1.2, 1.0, 0.25 * np.exp(-np.clip(tt - PRE - 1.2, 0, None) / 6))
    bed = drone * 0.5 * env + hiss * 0.12 * stat
    bed = bed / (np.abs(bed).max() + 1e-9) * 0.35
    with wave.open(f"out/{name}_bed.wav", "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes((np.clip(bed, -1, 1) * 32767).astype(np.int16).tobytes())
    run(["ffmpeg", "-v", "error", "-y", "-i", f"out/{name}_narr.wav", "-i", f"out/{name}_bed.wav", "-filter_complex",
         "[0:a]highpass=f=70,acompressor=threshold=0.1:ratio=2.5:attack=15:release=250[n];[1:a]volume=2.4,lowpass=f=6000[b];"
         "[n][b]amix=inputs=2:normalize=0:duration=longest,volume=3.4,alimiter=limit=0.89:level=disabled[a]",
         "-map", "[a]", "-ac", "2", "-ar", str(SR), f"out/{name}_mix.wav"])
    run(["ffmpeg", "-v", "error", "-y", "-i", f"out/{name}_pic.mp4", "-i", f"out/{name}_mix.wav",
         "-vf", f"ass=out/{name}.ass:fontsdir={FONTS}", "-c:v", "libx264", "-b:v", "10M", "-maxrate", "14M", "-bufsize", "20M",
         "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", "-shortest", f"out/{name}.mp4"])
    print(name, "done", round(dur(f"out/{name}.mp4"), 1), "s")


for nm in (sys.argv[1:] or SHORTS):
    build(nm, SHORTS[nm])
