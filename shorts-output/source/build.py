#!/usr/bin/env python3
"""Build the Akasa Ganga devotional Short (Telugu / Hindi) from Flow clips + ElevenLabs VO/music."""
import subprocess, sys, os, json

UP = "/root/.claude/uploads/668b95d7-3360-5306-a35c-3faf3e74c46a"
W = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(os.path.dirname(W), "fonts")
OUT = "/home/user/youtube-monetization/shorts-output"
os.makedirs(OUT, exist_ok=True)

CLIP = {
    "climb": f"{UP}/ecd8df4c-Sage_carrying_water_pot_climbing_21a717f7_1080p.mp4",
    "ask": f"{UP}/2fbcab4e-Boy_asking_sage_for_water_f82ed5aa_1080p.mp4",
    "arrow": f"{UP}/b483f998-Boy_drinks_water_from_arrow_842b7cf0_1080p.mp4",
    "fall": f"{UP}/3423bd6a-Boy_shoots_arrow_creating_waterfall_812f5c27_1080p.mp4",
    "reveal": f"{UP}/b8e57853-Sage_kneels_before_deity_silhouette_6a01977b_1080p.mp4",
}
SRC_LEN = 9.96
VO_OFF = 0.25
TAIL = 1.6
FPS = 24
GRADE = ("eq=contrast=1.04:saturation=1.10:gamma=0.98,"
         "colorbalance=rs=0.03:gs=0.01:bs=-0.03:rm=0.02:bm=-0.02,"
         "vignette=angle=PI/5,unsharp=5:5:0.35")

# transitions between scenes (type, duration)
TRANS = [("fadewhite", 0.5), ("fade", 0.6), ("fade", 0.4), ("fade", 0.6), ("fade", 0.9)]
# scene: clip, src_start, keep_audio, audio_vol
SCENES = [("arrow", 2.3, True, 0.45), ("climb", 0.0, False, 0), ("ask", 0.0, False, 0),
          ("arrow", 2.6, True, 0.45), ("fall", 0.0, True, 0.40), ("reveal", 0.0, False, 0)]

LANG = {
    "te": dict(
        vo="vo_te.mp3", vo_len=55.36, music_tempo=1.0,
        font="Noto Sans Telugu", size=72,
        # scene boundaries in VO time (pause midpoints)
        bounds=[4.25, 15.80, 25.80, 32.19, 41.33],
        hook="ఆకాశగంగ ఎలా పుట్టింది?",
        # (start, end, text) in VO time
        caps=[
            (0.00, 4.00, "భగవంతుడే తన భక్తుడి కుండకు బాణం వేశాడు…\\N{\\c&H40B4FF&}ఎందుకో తెలుసా?"),
            (4.49, 5.25, "{\\c&H40B4FF&}తిరుమల నంబి{\\c&HE6F6FF&}…"),
            (5.66, 7.41, "రామానుజాచార్యుల మేనమామ"),
            (7.85, 12.52, "ప్రతి రోజూ స్వామి అభిషేకం కోసం, పాపవినాశనం నుంచి నీళ్లు మోసుకొచ్చేవారు"),
            (12.96, 15.54, "వయసు మీద పడినా… ఒక్క రోజూ మానలేదు"),
            (16.07, 18.82, "ఒక రోజు దారిలో ఒక వేటగాడి బాలుడు ఎదురై…"),
            (19.26, 22.54, "\"తాతా, దాహంగా ఉంది… కొంచెం నీళ్లు ఇవ్వు\""),
            (23.09, 25.55, "\"ఇవి స్వామి అభిషేకానికి నాయనా… ఇవ్వలేను\""),
            (26.06, 28.20, "బాలుడు చిరునవ్వుతో బాణం వేశాడు"),
            (28.64, 29.87, "కుండకు రంధ్రం పడింది…"),
            (30.32, 31.91, "కారుతున్న నీళ్లు తాగేశాడు"),
            (32.46, 35.33, "\"ఇంత దూరం ఎందుకు తాతా? దగ్గరలోనే నీళ్లు చూపిస్తా\""),
            (35.74, 37.38, "మరో బాణం కొండకు తగిలింది…"),
            (37.77, 38.99, "జలధార పొంగింది"),
            (39.49, 41.09, "అదే… {\\c&H40B4FF&}ఆకాశగంగ"),
            (41.57, 42.93, "ఆ బాలుడు ఎవరో కాదు…"),
            (43.38, 45.88, "సాక్షాత్తు {\\c&H40B4FF&}శ్రీ వెంకటేశ్వర స్వామి"),
            (46.44, 49.75, "ఈ రోజుకీ స్వామి అభిషేకానికి {\\c&H40B4FF&}ఆకాశగంగ{\\c&HE6F6FF&} జలమే"),
            (50.28, 53.10, "ఇలాంటి మరిన్ని దివ్య కథల కోసం {\\c&H40B4FF&}సబ్‌స్క్రైబ్{\\c&HE6F6FF&} చేయండి"),
            (53.53, 55.36 + TAIL, "{\\c&H40B4FF&}గోవింద… గోవింద 🙏\\N{\\fs44\\c&HE6F6FF&}కామెంట్‌లో 'గోవింద' అని రాయండి"),
        ]),
    "hi": dict(
        vo="vo_hi.mp3", vo_len=61.28, music_tempo=0.89,
        font="Noto Sans Devanagari", size=72,
        bounds=[4.53, 17.49, 28.70, 35.69, 46.07],
        hook="आकाशगंगा कैसे प्रकट हुई?",
        caps=[
            (0.00, 4.19, "भगवान ने खुद अपने भक्त के घड़े पर तीर चला दिया…\\N{\\c&H40B4FF&}क्यों?"),
            (4.88, 5.81, "{\\c&H40B4FF&}तिरुमला नंबी{\\c&HE6F6FF&}…"),
            (6.32, 8.06, "रामानुजाचार्य के मामा"),
            (8.65, 13.91, "रोज़ भगवान वेंकटेश्वर के अभिषेक के लिए, पापविनाशनम् से जल ढोकर लाते थे"),
            (14.41, 17.21, "बूढ़े हो गए… पर एक दिन भी नहीं छोड़ा"),
            (17.77, 20.15, "एक दिन रास्ते में एक शिकारी बालक मिला"),
            (20.66, 24.06, "\"बाबा, बहुत प्यास लगी है… थोड़ा पानी दे दो\""),
            (24.48, 28.45, "\"बेटा, ये भगवान के अभिषेक का जल है… नहीं दे सकता\""),
            (28.94, 31.60, "बालक मुस्कुराया और तीर चला दिया"),
            (32.13, 33.43, "घड़े में छेद हो गया…"),
            (33.79, 35.42, "और वो बहता जल पी गया"),
            (35.96, 39.20, "\"इतनी दूर क्यों जाते हो बाबा? पास में ही जल दिखाता हूँ\""),
            (39.61, 41.36, "दूसरा तीर पहाड़ पर लगा…"),
            (41.76, 43.30, "और जलधारा फूट पड़ी"),
            (43.78, 45.82, "यही है… {\\c&H40B4FF&}आकाशगंगा"),
            (46.32, 48.09, "वो बालक कोई और नहीं…"),
            (48.48, 50.53, "स्वयं {\\c&H40B4FF&}तिरुपति बालाजी{\\c&HE6F6FF&} थे"),
            (51.00, 54.73, "आज भी उनका अभिषेक {\\c&H40B4FF&}आकाशगंगा{\\c&HE6F6FF&} के जल से होता है"),
            (55.25, 58.75, "ऐसी ही और दिव्य कथाओं के लिए चैनल को {\\c&H40B4FF&}सब्सक्राइब{\\c&HE6F6FF&} करें"),
            (59.18, 61.28 + TAIL, "{\\c&H40B4FF&}गोविंदा… गोविंदा 🙏\\N{\\fs44\\c&HE6F6FF&}कमेंट में 'गोविंदा' लिखें"),
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
        txt = txt.replace(" 🙏", "")  # emoji not in caption font
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
                  f"y='ih*0.36-(ih/zoom*0.36)':d={max(nfr,1)}:s=1080x1920:fps={FPS},{GRADE}[b];"
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
    out = os.path.join(OUT, f"akasa_ganga_{lang}.mp4")
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
