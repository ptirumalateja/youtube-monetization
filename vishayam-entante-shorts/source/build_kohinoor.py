#!/usr/bin/env python3
"""Build the Akasa Ganga devotional Short (Telugu / Hindi) from Flow clips + ElevenLabs VO/music."""
import subprocess, sys, os, json

UP = "/root/.claude/uploads/668b95d7-3360-5306-a35c-3faf3e74c46a"
W = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(os.path.dirname(W), "fonts")
OUT = "/home/user/youtube-monetization/vishayam-entante-shorts"
os.makedirs(OUT, exist_ok=True)

CLIP = {
    "miner": f"{W}/clean/db19f1f6.mp4",
    "mines": f"{W}/clean/b44afa61.mp4",
    "throne": f"{W}/clean/62d1d215.mp4",
    "nader": f"{W}/clean/64067cb7.mp4",
    "british": f"{W}/clean/e767b800.mp4",
    "reveal": f"{W}/clean/8dc961c8.mp4",
}
SRC_LEN = 9.96
VO_OFF = 0.25
TAIL = 1.6
FPS = 24
GRADE = ("eq=contrast=1.04:saturation=1.10:gamma=0.98,"
         "colorbalance=rs=0.03:gs=0.01:bs=-0.03:rm=0.02:bm=-0.02,"
         "vignette=angle=PI/5,unsharp=5:5:0.35")

# transitions between scenes (type, duration)
TRANS = [("fadewhite", 0.5), ("fade", 0.6), ("fade", 0.6), ("fadeblack", 0.7), ("fade", 0.8)]
# scene: clip, src_start, keep_audio, audio_vol
SCENES = [("miner", 3.4, False, 0), ("mines", 0.0, False, 0), ("throne", 0.0, False, 0),
          ("nader", 0.0, False, 0), ("british", 0.0, False, 0), ("reveal", 0.0, False, 0)]

LANG = {
    "te": dict(
        vo="vo_teja2.mp3", vo_len=52.56, music_tempo=1.0,
        font="Noto Sans Telugu", size=72,
        bounds=[7.22, 12.52, 19.57, 30.79, 39.71],
        hook="కోహినూర్ మనదే… మరి లండన్‌లో ఎందుకు?",
        caps=[
            (0.0, 2.71, 'ప్రపంచంలోనే అత్యంత ప్రసిద్ధ వజ్రం…'),
            (3.15, 4.64, 'మన తెలుగు నేలపై దొరికింది'),
            (5.16, 6.95, 'మరి ఇప్పుడు {\\c&H40B4FF&}లండన్\u200cలో{\\c&HE6F6FF&} ఎందుకు ఉంది?'),
            (7.5, 8.84, 'చరిత్రకారుల ప్రకారం…'),
            (9.02, 12.29, '{\\c&H40B4FF&}కోహినూర్{\\c&HE6F6FF&} కృష్ణా నది ఒడ్డున ఉన్న {\\c&H40B4FF&}కొల్లూరు{\\c&HE6F6FF&} గనుల్లో దొరికింది'),
            (12.76, 16.55, 'ఆ తర్వాత ఢిల్లీ సుల్తానులు, మొఘలుల చేతుల్లోకి వెళ్లింది…'),
            (16.95, 19.37, 'షాజహాన్ {\\c&H40B4FF&}నెమలి సింహాసనంలో{\\c&HE6F6FF&} మెరిసింది'),
            (19.78, 21.46, '1739లో…'),
            (21.63, 25.26, 'పర్షియా రాజు {\\c&H40B4FF&}నాదిర్ షా{\\c&HE6F6FF&} ఢిల్లీని దోచుకుని దాన్ని తీసుకెళ్లాడు'),
            (25.61, 30.59, 'కోహినూర్ అంటే {\\c&H40B4FF&}"వెలుగుల కొండ"{\\c&HE6F6FF&} — ఆ పేరు పెట్టింది అతనేనని చెబుతారు'),
            (30.99, 34.97, '1849లో, బ్రిటిష్ వాళ్లు పంజాబ్\u200cను ఆక్రమించి'),
            (35.16, 38.05, 'పదేళ్ల మహారాజా {\\c&H40B4FF&}దులీప్ సింగ్{\\c&HE6F6FF&} నుంచి దాన్ని తీసుకుని'),
            (38.2, 39.52, 'క్వీన్ విక్టోరియాకు పంపారు'),
            (39.9, 43.79, 'ఈ రోజుకీ అది {\\c&H40B4FF&}లండన్ టవర్\u200cలో,{\\c&HE6F6FF&} బ్రిటిష్ రాణి కిరీటంలోనే ఉంది'),
            (44.25, 46.14, 'భారత్ ఎన్నోసార్లు తిరిగి అడిగింది'),
            (46.6, 47.57, 'మీ అభిప్రాయం ఏంటి?'),
            (47.97, 49.65, '{\\c&H40B4FF&}కోహినూర్ మళ్లీ భారత్\u200cకి రావాలా?'),
            (50.09, 50.72, 'కామెంట్ చేయండి'),
            (51.17, 52.56 + TAIL, '{\\c&H40B4FF&}అదీ… విషయం!'),
        ]),
}


def run(cmd):
    print("+", " ".join(cmd)[:300], flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-3000:])
        sys.exit(1)


def ts(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def write_ass(lang, cfg, total, path):
    def st(name, size, colour, align, mv, outline):
        return (f"Style: {name},{cfg['font']},{size},{colour},&H000000FF,&H00102040,&H96000000,"
                f"-1,0,0,0,100,100,0,0,1,{outline},2,{align},90,90,{mv},1")
    lines = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920",
             "WrapStyle: 0", "ScaledBorderAndShadow: yes", "",
             "[V4+ Styles]",
             "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
             "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, "
             "Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
             st("Cap", cfg["size"], "&H00E6F6FF", 2, 470, 5),
             st("Hook", 78, "&H006BD3FF", 8, 250, 6),
             "", "[Events]",
             "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    lines.append(f"Dialogue: 0,{ts(0.15)},{ts(cfg['bounds'][0] + VO_OFF)},Hook,,0,0,0,,"
                 f"{{\\fad(250,300)}}{cfg['hook']}")
    caps = cfg["caps"]
    for i, (s, e, txt) in enumerate(caps):
        s += VO_OFF; e += VO_OFF
        if i + 1 < len(caps):
            nxt = caps[i + 1][0] + VO_OFF
            if nxt - e < 0.6:
                e = nxt - 0.04
            else:
                e += 0.25
        e = min(e, total - 0.3)
        txt = "".join(ch for ch in txt if ord(ch) < 0x10000).rstrip()  # emoji not in caption font
        lines.append(f"Dialogue: 0,{ts(s)},{ts(e)},Cap,,0,0,0,,{{\\fad(120,120)}}{txt}")
    open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")


def build(lang):
    cfg = LANG[lang]
    total = cfg["vo_len"] + VO_OFF + TAIL
    b = [x + VO_OFF for x in cfg["bounds"]]
    edges = [0.0] + b + [total]
    tmp = os.path.join(W, f"tmp_{lang}"); os.makedirs(tmp, exist_ok=True)
    parts = []
    for i, (clip, s0, keep_a, avol) in enumerate(SCENES):
        dur = edges[i + 1] - edges[i]
        t_in = TRANS[i - 1][1] if i > 0 else 0
        t_out = TRANS[i][1] if i < len(TRANS) else 0
        L = dur + t_in / 2 + t_out / 2
        src = CLIP[clip]
        part = os.path.join(tmp, f"s{i}.mp4")
        if os.environ.get("REUSE") and os.path.exists(part.replace(".mp4", ".mkv")):
            parts.append(part.replace(".mp4", ".mkv")); continue
        a_chain = f"volume={avol}" if keep_a else None
        if clip == "reveal":
            # play the clip at 1x, then hold the final frame with a slow push-in toward the deity
            play = min(SRC_LEN - 0.05, L)
            hold = max(L - play, 0)
            last = os.path.join(tmp, "last.png")
            run(["ffmpeg", "-y", "-v", "error", "-sseof", "-0.08", "-i", src, "-frames:v", "1", "-update", "1", last])
            nfr = int(round(hold * FPS))
            vf = (f"[0:v]trim=0:{play},setpts=PTS-STARTPTS,fps={FPS},{GRADE}[a];"
                  f"[1:v]scale=2160:3840,zoompan=z='1+0.07*on/{max(nfr,1)}':x='iw/2-(iw/zoom/2)':"
                  f"y='ih*0.5-(ih/zoom*0.5)':d={max(nfr,1)}:s=1080x1920:fps={FPS},{GRADE}[b];"
                  f"[a][b]concat=n=2:v=1:a=0,trim=0:{L},format=yuv420p[v]")
            run(["ffmpeg", "-y", "-v", "error", "-i", src, "-loop", "1", "-t", f"{hold+0.5}", "-i", last,
                 "-f", "lavfi", "-t", f"{L}", "-i", "anullsrc=r=48000:cl=stereo",
                 "-filter_complex", vf, "-map", "[v]", "-map", "2:a",
                 "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-c:a", "pcm_s16le", "-t", f"{L}",
                 part.replace(".mp4", ".mkv")])
            parts.append(part.replace(".mp4", ".mkv"))
            continue
        avail = SRC_LEN - s0 - 0.02
        speed = min(avail / L, 1.06)
        speed = max(speed, 0.70)
        need_src = L * speed
        interp = f"minterpolate=fps={FPS}:mi_mode=blend" if speed < 0.9 else f"fps={FPS}"
        vf = (f"[0:v]trim={s0}:{s0+need_src},setpts=(PTS-STARTPTS)/{speed:.4f},{interp},{GRADE},"
              f"trim=0:{L},setpts=PTS-STARTPTS,format=yuv420p[v]")
        if keep_a:
            af = (f"[0:a]atrim={s0}:{s0+need_src},asetpts=PTS-STARTPTS,atempo={speed:.4f},"
                  f"aresample=48000,{a_chain},apad,atrim=0:{L}[a]")
        else:
            af = f"anullsrc=r=48000:cl=stereo,atrim=0:{L}[a]"
        run(["ffmpeg", "-y", "-v", "error", "-i", src, "-filter_complex", vf + ";" + af,
             "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "14", "-preset", "fast",
             "-c:a", "pcm_s16le", "-t", f"{L}", part.replace(".mp4", ".mkv")])
        parts.append(part.replace(".mp4", ".mkv"))
        print(f"  scene {i} {clip}: L={L:.2f}s speed={speed:.3f}")

    # xfade chain
    inputs = []
    for p in parts:
        inputs += ["-i", p]
    fc = []
    vprev, aprev = "[0:v]", "[0:a]"
    acc = 0.0
    lens = [float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                           "-of", "csv=p=0", p]).decode()) for p in parts]
    acc = lens[0]
    for k, (tt, td) in enumerate(TRANS):
        off = acc - td
        fc.append(f"{vprev}[{k+1}:v]xfade=transition={tt}:duration={td}:offset={off:.3f}[v{k}]")
        fc.append(f"{aprev}[{k+1}:a]acrossfade=d={td}[a{k}]")
        vprev, aprev = f"[v{k}]", f"[a{k}]"
        acc = off + lens[k + 1]
    ass = os.path.join(tmp, "caps.ass")
    write_ass(lang, cfg, total, ass)
    fc.append(f"{vprev}ass={ass}:fontsdir={FONTS}:shaping=complex,format=yuv420p,"
              f"fade=t=in:st=0:d=0.3,fade=t=out:st={total-0.8:.2f}:d=0.8[vout]")
    # audio: veo sfx + VO + ducked music
    vo_i = len(parts); mu_i = vo_i + 1
    fc.append(f"[{vo_i}:a]aresample=48000,adelay={int(VO_OFF*1000)}|{int(VO_OFF*1000)},"
              f"apad,atrim=0:{total},asplit=2[vo][vosc]")
    mt = cfg["music_tempo"]
    mtempo = f"atempo={mt}," if mt != 1.0 else ""
    fc.append(f"[{mu_i}:a]aresample=48000,{mtempo}volume=0.42,apad,atrim=0:{total},"
              f"afade=t=in:st=0:d=0.6,afade=t=out:st={total-2.2:.2f}:d=2.2[mus]")
    fc.append("[mus][vosc]sidechaincompress=threshold=0.04:ratio=5:attack=25:release=450:makeup=1[musd]")
    fc.append(f"{aprev}atrim=0:{total}[sfx]")
    fc.append("[vo][musd][sfx]amix=inputs=3:duration=first:normalize=0,"
              "loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
    out = os.path.join(OUT, f"kohinoor_{lang}.mp4")
    run(["ffmpeg", "-y", "-v", "error"] + inputs +
        ["-i", os.path.join(W, cfg["vo"]), "-i", os.path.join(W, "music1.mp3"),
         "-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]",
         "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-profile:v", "high", "-pix_fmt", "yuv420p",
         "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart",
         "-t", f"{total:.3f}", out])
    print("DONE", out, total)


if __name__ == "__main__":
    for l in sys.argv[1:] or ["te", "hi"]:
        build(l)
