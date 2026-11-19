# Mix VO + SFX + music for the Galwan reel. Usage: python3 mix.py timing.json vo.wav sfxdir out.wav
import json, sys, subprocess
T = json.load(open(sys.argv[1])); vo, S, out = sys.argv[2], sys.argv[3], sys.argv[4]
import render
shots = render.build(T)
total = T["total"]
ev = []  # (file, start, vol)
for n, a, b in shots:
    if 3.0 < a < 27.5:
        ev.append(("whoosh", a - 0.05, 0.22))
cut = {n: a for n, a, b in shots}
ev += [("stamp", cut["date"], 0.5), ("stamp", cut["name"] + 0.15, 0.45), ("stamp", cut["rifle"] + 0.28, 0.5),
       ("stamp", cut["medal"] + 0.05, 0.4), ("rocks", cut["rocks"], 0.45), ("bell", cut["diyas"], 0.35),
       ("wind", cut["date"], 0.2), ("wind", cut["rocks"], 0.14)]
inputs = ["-i", vo, "-i", f"{S}/music.mp3"]
fl = []
for i, (f, st, v) in enumerate(ev):
    inputs += ["-i", f"{S}/{f}.mp3"]
    k = i + 2
    extra = ""
    if f == "wind":
        extra = f",atrim=0:{min(8, 27.5 - st):.2f},afade=t=in:d=0.6,afade=t=out:st={min(8, 27.5 - st) - 1:.2f}:d=1"
    fl.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo{extra},volume={v},adelay={int(st*1000)}|{int(st*1000)}[e{i}]")
fl.append("[0:a]aresample=48000,aformat=channel_layouts=stereo,adelay=0|0,apad[vo]")
fl.append("[vo]asplit=2[vo1][vo2]")
fl.append(f"[1:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.32,afade=t=out:st={total-1.2:.2f}:d=1.2[mu]")
fl.append("[mu][vo2]sidechaincompress=threshold=0.05:ratio=4:attack=20:release=300[mud]")
fl.append("[vo1][mud]" + "".join(f"[e{i}]" for i in range(len(ev))) + f"amix=inputs={len(ev)+2}:normalize=0:duration=first,atrim=0:{total:.3f},loudnorm=I=-14:TP=-1.5:LRA=9[out]")
cmd = ["ffmpeg", "-y", "-loglevel", "error"] + inputs + ["-filter_complex", ";".join(fl), "-map", "[out]", "-ar", "48000", out]
subprocess.run(cmd, check=True)
print("mixed", out)
