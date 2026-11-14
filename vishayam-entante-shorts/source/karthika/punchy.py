#!/usr/bin/env python3
"""Punchy ~30s Shorts editor: fast scenes, push-in on every shot, flash cuts, pop captions, ducked music."""
import json, os, subprocess, sys

W = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(os.path.dirname(W), "fonts")
FPS = 24
GRADE = ("eq=contrast=1.07:saturation=1.14:gamma=0.97,"
         "colorbalance=rs=0.03:gs=0.01:bs=-0.03:rm=0.02:bm=-0.02,"
         "vignette=angle=PI/5,unsparp".replace("unsparp", "unsharp=5:5:0.7"))


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(" ".join(cmd)[:400]); print(r.stderr[-2500:]); sys.exit(1)


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", p]).decode())


def ts(t):
    return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"


def build(cfg_path):
    cfg = json.load(open(cfg_path))
    tmp = os.path.join(W, "tmp_" + cfg["name"]); os.makedirs(tmp, exist_ok=True)
    vo = os.path.join(tmp, "vo.wav")
    run(["ffmpeg", "-y", "-v", "error", "-i", os.path.join(W, cfg["vo"]),
         "-af", f"atempo={cfg['vo_tempo']},aresample=48000", vo])
    T = cfg["vo_tempo"]; off = cfg["vo_offset"]
    vo_len = dur(vo)
    total = off + vo_len + cfg["tail"]
    edges = [0.0] + [b / T + off for b in cfg["bounds"]] + [total]
    parts = []
    for i, sc in enumerate(cfg["scenes"]):
        t_in = cfg["trans"][i-1][1] if i > 0 else 0
        t_out = cfg["trans"][i][1] if i < len(cfg["trans"]) else 0
        L = edges[i+1] - edges[i] + t_in/2 + t_out/2
        src = os.path.join(W, sc["clip"]); s0, s1 = sc["src"]
        hold = 0.0
        speed = (s1 - s0) / L
        if speed > sc.get("max_speed", 1.3):             # too much footage for the slot: use less of it instead of fast-forwarding
            s1 = s0 + L * 1.15; speed = 1.15
        if speed < sc.get("min_speed", 0.9):            # not enough footage: play at min speed, then hold last frame
            speed = sc.get("min_speed", 0.9); hold = L - (s1 - s0) / speed
        zin, zout = sc.get("zoom", [1.0, 1.08])
        ease = f"(1-pow(1-t/{L:.3f},2))"   # ease-out: fast start, gentle settle
        z = f"({zin}+({zout}-{zin})*{ease})"
        zx0, zx1 = sc.get("pan_x", [sc.get("zx", 0.5)] * 2)
        zy0, zy1 = sc.get("pan_y", [sc.get("zy", 0.5)] * 2)
        vf = (f"[0:v]trim={s0}:{s1},setpts=(PTS-STARTPTS)/{speed:.4f},fps={FPS},"
              f"tpad=stop_mode=clone:stop_duration={hold+0.2:.3f},"
              f"scale=w='trunc(1080*{z}/2)*2':h='trunc(1920*{z}/2)*2':eval=frame:flags=lanczos,"
              f"crop=1080:1920:x='(in_w-1080)*({zx0}+({zx1}-{zx0})*{ease})':y='(in_h-1920)*({zy0}+({zy1}-{zy0})*{ease})',"
              f"setsar=1,{GRADE},trim=0:{L:.3f},setpts=PTS-STARTPTS,format=yuv420p[v]")
        if sc.get("sfx"):
            af = (f"[1:a]atrim={s0}:{s1},asetpts=PTS-STARTPTS,atempo={max(min(speed,2),0.5):.4f},aresample=48000,"
                  f"volume={sc['sfx']},apad,atrim=0:{L:.3f}[a]")
        else:
            af = f"anullsrc=r=48000:cl=stereo,atrim=0:{L:.3f}[a]"
        out = os.path.join(tmp, f"s{i}.mkv")
        ain = ["-i", sc["orig"]] if sc.get("sfx") else []
        run(["ffmpeg", "-y", "-v", "error", "-i", src] + ain + ["-filter_complex", vf + ";" + af, "-map", "[v]", "-map", "[a]",
             "-c:v", "libx264", "-crf", "12", "-preset", "fast", "-c:a", "pcm_s16le", "-t", f"{L:.3f}", out])
        parts.append(out)
        print(f"scene {i}: {sc['clip']} L={L:.2f} speed={speed:.2f} hold={hold:.2f}")
    # captions
    ass = os.path.join(tmp, "caps.ass")
    if cfg.get("box"):
        def st(n, size, col, al, mv, ol):
            if n == "Hook":
                return f"Style: {n},{cfg['font']},{size},&H006BD3FF,&H000000FF,&H18000000,&H18000000,-1,0,0,0,100,100,0,0,3,18,0,{al},80,80,{mv},1"
            return f"Style: {n},{cfg['font']},{size},&H00FFFFFF,&H000000FF,&H22000000,&H22000000,-1,0,0,0,100,100,0,0,3,16,0,{al},80,80,{mv},1"
    else:
        st = lambda n, size, col, al, mv, ol: (f"Style: {n},{cfg['font']},{size},{col},&H000000FF,&H00102040,&H96000000,-1,0,0,0,100,100,0,0,1,{ol},2,{al},80,80,{mv},1")
    L_ = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "WrapStyle: 0", "ScaledBorderAndShadow: yes", "",
          "[V4+ Styles]", "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
          st("Cap", cfg["cap_size"], "&H00E6F6FF", 2, 500, 6), st("Hook", cfg["hook_size"], "&H006BD3FF", 8, 230, 7), "",
          "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    L_.append(f"Dialogue: 0,{ts(0.0)},{ts(cfg['hook_end'])},Hook,,0,0,0,,{{\\fad(0,200)\\fscx80\\fscy80\\t(0,160,\\fscx100\\fscy100)}}{cfg['hook']}")
    for s_, e_, txt in cfg.get("extra", []):
        e_ = total - 0.1 if e_ == "END" else e_ / T + off
        L_.append(f"Dialogue: 1,{ts(s_ / T + off)},{ts(e_)},Hook,,0,0,0,,{{\\fad(80,120)\\fscx70\\fscy70\\t(0,140,\\fscx100\\fscy100)}}{txt}")
    caps = cfg["caps"]
    for i, (s, e, txt) in enumerate(caps):
        s = s / T + off; e = (total if e == "END" else e / T + off)
        if i + 1 < len(caps):
            nxt = caps[i+1][0] / T + off
            e = nxt - 0.03 if nxt - e < 0.5 else e + 0.15
        e = min(e, total - 0.1)
        txt = "".join(ch for ch in txt if ord(ch) < 0x10000)
        L_.append(f"Dialogue: 0,{ts(s)},{ts(e)},Cap,,0,0,0,,{{\\fad(60,80)\\fscx88\\fscy88\\t(0,110,\\fscx100\\fscy100)}}{txt}")
    open(ass, "w", encoding="utf-8").write("\n".join(L_) + "\n")
    # assemble
    inputs = sum([["-i", p] for p in parts], [])
    lens = [dur(p) for p in parts]
    fc, vprev, aprev, acc = [], "[0:v]", "[0:a]", lens[0]
    for k, (tt, td) in enumerate(cfg["trans"]):
        o = acc - td
        fc.append(f"{vprev}[{k+1}:v]xfade=transition={tt}:duration={td}:offset={o:.3f}[v{k}]")
        fc.append(f"{aprev}[{k+1}:a]acrossfade=d={td}[a{k}]")
        vprev, aprev = f"[v{k}]", f"[a{k}]"; acc = o + lens[k+1]
    fc.append(f"{vprev}ass={ass}:fontsdir={FONTS}:shaping=complex,format=yuv420p,fade=t=out:st={total-0.5:.2f}:d=0.5[vout]")
    vi, mi = len(parts), len(parts) + 1
    od = int(off * 1000)
    fc.append(f"[{vi}:a]adelay={od}|{od},apad,atrim=0:{total:.3f},asplit=2[vo][vosc]")
    fc.append(f"[{mi}:a]atrim={cfg['music_start']},asetpts=PTS-STARTPTS,aresample=48000,volume={cfg['music_vol']},apad,atrim=0:{total:.3f},"
              f"afade=t=in:st=0:d=0.3,afade=t=out:st={total-1.5:.2f}:d=1.5[mus]")
    fc.append("[mus][vosc]sidechaincompress=threshold=0.05:ratio=4:attack=20:release=300[musd]")
    fc.append(f"{aprev}atrim=0:{total:.3f}[sfx]")
    fc.append("[vo][musd][sfx]amix=inputs=3:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9[aout]")
    out = cfg["out"]; os.makedirs(os.path.dirname(out), exist_ok=True)
    run(["ffmpeg", "-y", "-v", "error"] + inputs + ["-i", vo, "-i", os.path.join(W, cfg["music"]),
         "-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]", "-c:v", "libx264", "-crf", "17",
         "-preset", "medium", "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", "-t", f"{total:.3f}", out])
    print("DONE", out, round(total, 2))


if __name__ == "__main__":
    build(sys.argv[1])
