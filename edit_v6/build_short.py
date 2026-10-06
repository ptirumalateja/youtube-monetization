#!/usr/bin/env python3
"""Assemble the Slow Light Abhimanyu Short from Wan clips, narration, score and SFX.

Inputs (paths relative to this folder):
  cuts.json            shot order, start times (s) on the narration timeline, captions
  words.json           ElevenLabs Scribe word timings for narration.mp3
  narration.mp3        final narration
  clips/<shot>.mp4     Wan 2.2 clips, 704x1280 @ 16 fps
  audio/score.mp3, audio/amb.mp3, audio/sfx_*.mp3
  fonts/               Montserrat (captions), Cinzel (title cards)
Output: out/abhimanyu_short.mp4 (1080x1920, 24 fps, -14 LUFS)
"""
import json, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
os.makedirs("out/shots", exist_ok=True)

W, H, FPS = 1080, 1920, 24
cuts = json.load(open("cuts.json"))
shots = cuts["shots"]
narr_len = float(subprocess.check_output(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "narration.mp3"]).decode())
TOTAL = round(narr_len + cuts["tail_seconds"], 3)

GRADE = ("eq=contrast=1.06:saturation=0.9:gamma=0.98,"
         "vignette=angle=PI/5,unsharp=5:5:0.35,noise=alls=5:allf=t")


def run(cmd):
    subprocess.run(cmd, check=True)


# ---------- 1. per-shot clips: retime to the narration slot, 24 fps, 1080x1920, grade ----------
parts = []
for i, s in enumerate(shots):
    start = s["start"]
    end = shots[i + 1]["start"] if i + 1 < len(shots) else TOTAL
    slot = round(end - start, 3)
    src = f"clips/{s['shot']}.mp4"
    dur = float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src]).decode())
    # Skip the first few frames (still identical to the source image) when there is spare footage.
    offset = min(0.25, max(0.0, dur - slot))
    if s.get("anchor") == "end" and dur > slot:  # keep the clip's ending (e.g. the moment light snaps out)
        offset = dur - slot - 0.05
    usable = dur - offset
    if usable >= slot:
        speed = 1.0
        pad = 0.0
    else:
        speed = min(slot / usable, 1.5)          # slow motion up to 1.5x
        pad = max(0.0, slot - usable * speed)    # hold the last frame for the rest
    vf = (f"trim=start={offset},setpts=(PTS-STARTPTS)*{speed:.4f},"
          f"minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:vsbmc=1,"
          f"tpad=stop_mode=clone:stop_duration={pad:.3f},"
          f"trim=duration={slot},setpts=PTS-STARTPTS,"
          f"scale={W}:{H}:flags=lanczos,setsar=1,{GRADE},format=yuv420p")
    out = f"out/shots/{i:02d}_{s['shot']}.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", vf, "-an", "-r", str(FPS),
         "-c:v", "libx264", "-preset", "medium", "-crf", "16", out])
    parts.append(out)
    print(f"{s['shot']:5} slot {slot:5.2f}s  clip {dur:4.2f}s  speed {speed:.2f}  hold {pad:.2f}s")

with open("out/concat.txt", "w") as f:
    f.writelines(f"file '{os.path.abspath(p)}'\n" for p in parts)
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "out/concat.txt",
     "-c", "copy", "out/picture.mp4"])

# ---------- 2. captions (ASS): 1-4 word chunks, current word in amber ----------
DISPLAY = {"/əbʱɪˈmənjuː/": "Abhimanyu", "/ˈərdʒʊnə/": "Arjuna", "/ˈdroːɳəz/": "Drona's",
           "/tʃəkrəˈʋjuːɦə/": "Chakravyuha", "/ˈərdʒʊnəz/": "Arjuna's",
           "/dʒəjəˈdrətʰə/": "Jayadratha", "/ˈpaːɳɖəʋə/": "Pandava"}
# Phonetic spellings used for the voice -> correct spellings for the captions.
SPELL = {"Paandavaas": "Pandavas", "Dhrona": "Drona", "Yud-hish-tee-ra": "Yudhishthira", "Jayathratha": "Jayadratha"}
words = []
in_tag = False
for w in json.load(open("words.json"))["words"]:
    t = w["text"]
    # Skip delivery tags such as [pause] or [calm, low ... engaged], which Scribe splits into several tokens.
    if t.startswith("[") or in_tag:
        in_tag = not t.endswith("]")
        continue
    m = re.match(r"^(/[^/]+/)(.*)$", t)
    if m:
        t = DISPLAY.get(m.group(1), m.group(1)) + m.group(2)
    for k, v in SPELL.items():
        t = t.replace(k, v)
    t = t.replace("...", "…")
    words.append({"t": t, "s": w["start"], "e": w["end"]})
if words and words[0]["t"] and words[0]["s"] < 0.2:
    words[0]["s"] = 0.0

# Split into phrases at punctuation or pauses, then into balanced groups of at most 4 words.
phrases, cur = [], []
for k, w in enumerate(words):
    cur.append(w)
    nxt = words[k + 1] if k + 1 < len(words) else None
    end_phrase = re.search(r"[.!?…:,\"”]$", w["t"])
    gap = nxt is not None and nxt["s"] - w["e"] > 0.35
    if end_phrase or gap or nxt is None:
        phrases.append(cur)
        cur = []
chunks = []
for ph in phrases:
    n = -(-len(ph) // 4)
    size = -(-len(ph) // n)
    chunks += [ph[i:i + size] for i in range(0, len(ph), size)]


def ts(x):
    x = max(0.0, x)
    return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}"


def esc(t):
    return t.replace("{", "(").replace("}", ")")


ass = [
    "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 0", "",
    "[V4+ Styles]",
    "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
    "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
    "MarginR, MarginV, Encoding",
    # Captions sit at ~70% height: clear of the bottom 20% and the right-hand UI column.
    "Style: Cap,Montserrat,74,&H00F2F2F2,&H00F2F2F2,&H00101010,&H64000000,1,0,0,0,100,100,0,0,1,4,2,2,110,150,560,1",
    "Style: Title,Cinzel,76,&H00E6EEF2,&H00E6EEF2,&H00101010,&H00000000,1,0,0,0,100,100,6,0,1,3,0,8,90,90,250,1",
    "Style: Brand,Cinzel,96,&H00E6EEF2,&H00E6EEF2,&H00101010,&H00000000,1,0,0,0,100,100,14,0,1,3,0,5,90,90,0,1",
    "Style: Tag,Montserrat,44,&H00C8D4DA,&H00C8D4DA,&H00101010,&H00000000,0,1,0,0,100,100,2,0,1,2,0,5,90,90,0,1",
    "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
]
AMBER = r"{\c&H4AB0E8&}"
WHITE = r"{\c&HF2F2F2&}"
for ci, ch in enumerate(chunks):
    chunk_end = chunks[ci + 1][0]["s"] if ci + 1 < len(chunks) else ch[-1]["e"] + 0.6
    chunk_end = min(chunk_end, ch[-1]["e"] + 0.8)
    for wi, w in enumerate(ch):
        a = w["s"]
        b = ch[wi + 1]["s"] if wi + 1 < len(ch) else chunk_end
        text = " ".join((AMBER if j == wi else WHITE) + esc(x["t"]) for j, x in enumerate(ch))
        ass.append(f"Dialogue: 0,{ts(a)},{ts(b)},Cap,,0,0,0,,{{\\fad(0,0)}}{text}")
# Opening title for muted viewers, and the end card.
TITLE = cuts.get("title", "THE REAL TRAGEDY\\NOF ABHIMANYU")
ass.append(f"Dialogue: 1,{ts(0.0)},{ts(3.6)},Title,,0,0,0,,{{\\fad(150,400)}}{TITLE}")
tail0 = narr_len + 0.35
ass.append(f"Dialogue: 2,{ts(tail0)},{ts(TOTAL)},Brand,,0,0,0,,{{\\fad(500,0)\\pos(540,900)}}SLOW LIGHT")
ass.append(f"Dialogue: 2,{ts(tail0 + 0.3)},{ts(TOTAL)},Tag,,0,0,0,,{{\\fad(500,0)\\pos(540,1010)}}Stories worth slowing down for.")
open("out/captions.ass", "w").write("\n".join(ass) + "\n")

# ---------- 3. audio mix ----------
SCORE_OFFSET = cuts.get("score_offset", 1.8)  # where in the score to start, so its drop lands on the key line
sfx = {s["shot"]: s["start"] for s in shots}
QS = cuts.get("quiet_shot", "s14")  # the line where score and ambience dip
qi = next(i for i, s in enumerate(shots) if s["shot"] == QS)
quiet_a = shots[qi]["start"] - 0.2
quiet_b = shots[qi + 1]["start"]
SFX = cuts.get("sfx", {"bow": "s16a", "chariot": "s16b", "sword": "s16c"})
fc = (
    f"[0:a]aresample=48000,volume=1.0,apad=whole_dur={TOTAL}[nar];"
    f"[nar]asplit=2[nar1][nar_sc];"
    f"[1:a]aresample=48000,atrim=start={SCORE_OFFSET},asetpts=PTS-STARTPTS,atrim=0:{TOTAL},afade=t=in:d=0.6,afade=t=out:st={TOTAL-2.4}:d=2.4,"
    f"volume='if(between(t,{quiet_a},{quiet_b}),0.12,1)':eval=frame,volume=0.55[mus];"
    f"[mus][nar_sc]sidechaincompress=threshold=0.04:ratio=5:attack=25:release=450[musd];"
    f"[2:a]aresample=48000,aloop=loop=-1:size=2147483647,atrim=0:{TOTAL},"
    f"volume='if(between(t,{quiet_a},{quiet_b}),0.25,1)':eval=frame,volume=0.22,afade=t=out:st={TOTAL-2}:d=2[amb];"
    f"anoisesrc=color=brown:amplitude=0.5:duration={TOTAL}:sample_rate=48000,lowpass=f=380,highpass=f=40,"
    f"volume=0.05,afade=t=in:d=1,afade=t=out:st={TOTAL-1.5}:d=1.5[wind];"
    f"[3:a]aresample=48000,adelay={int(sfx[SFX['bow']]*1000)}|{int(sfx[SFX['bow']]*1000)},volume=0.8[b1];"
    f"[4:a]aresample=48000,adelay={int(sfx[SFX['chariot']]*1000)}|{int(sfx[SFX['chariot']]*1000)},volume=0.8[b2];"
    f"[5:a]aresample=48000,adelay={int(sfx[SFX['sword']]*1000)}|{int(sfx[SFX['sword']]*1000)},volume=0.8[b3];"
    f"[nar1][musd][amb][wind][b1][b2][b3]amix=inputs=7:normalize=0:duration=first,"
    f"atrim=0:{TOTAL},loudnorm=I=-13:TP=-1.5:LRA=11[aout]"
)
run(["ffmpeg", "-v", "error", "-y", "-i", "narration.mp3", "-i", "audio/score.mp3", "-i", "audio/amb.mp3",
     "-i", "audio/sfx_bow.mp3", "-i", "audio/sfx_chariot.mp3", "-i", "audio/sfx_sword.mp3",
     "-filter_complex", fc, "-map", "[aout]", "-ar", "48000", "-c:a", "pcm_s16le", "out/mix.wav"])

# ---------- 4. final: picture + captions + end fade + mix ----------
# Fade the picture to black after the last line, then draw captions and the end card on top.
vf =(f"fade=t=out:st={narr_len+0.2}:d=0.9:color=black,ass=out/captions.ass:fontsdir=fonts")
run(["ffmpeg", "-v", "error", "-y", "-i", "out/picture.mp4", "-i", "out/mix.wav", "-vf", vf,
     "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-maxrate", "16M", "-bufsize", "32M", "-profile:v", "high",
     "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart",
     "-t", str(TOTAL), "out/abhimanyu_short.mp4"])
print("done:", TOTAL, "s")
