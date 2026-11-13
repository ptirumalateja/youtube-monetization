"""Sound mix: python3 mix.py SFXDIR OUT.wav"""
import sys, subprocess
SFX, OUT = sys.argv[1], sys.argv[2]
DUR = 14.0
# (file, start_s, gain_db, trim_start, trim_len)
EV = [
    ("space", 0.0, -20, 0, 6.0), ("space", 6.0, -20, 0, 6.0), ("space", 12.0, -20, 0, 2.0),
    ("whoosh", 0.0, -5, 0.2, 1.0),             # fireballs roaring at Earth on frame 0
    ("impacts", 0.28, -1, 0.0, 1.0),            # yanked into Jupiter
    ("impacts", 0.82, -4, 1.0, 0.6),
    ("msg_in", 1.33, -3, 0, 0.6),
    ("msg_out", 2.33, -3, 0, 0.6),
    ("msg_in", 3.45, -3, 0, 0.6),
    ("msg_in", 4.50, -3, 0, 0.6),
    ("typing", 5.65, -14, 0, 1.7),
    ("rise", 5.55, -2, 0, 1.9),
    ("braam", 7.30, 0, 0, 4.0),
    ("msg_out", 7.35, -6, 0, 0.6),
    ("whoosh", 7.9, -6, 0, 1.5),
    ("impacts", 8.6, -2, 0, 1.5),
    ("whoosh", 9.3, -8, 0, 1.5),
    ("impacts", 9.8, -3, 0.3, 1.5),
    ("impacts", 11.0, -4, 0.0, 1.3),
    ("msg_in", 10.20, -3, 0, 0.6),
    ("leave", 10.90, -5, 0, 1.0),
    ("braam", 12.05, -10, 1.0, 1.95),
]
args = ["ffmpeg", "-y"]
filt = []
for i, (f, st, g, ts, tl) in enumerate(EV):
    args += ["-i", f"{SFX}/{f}.mp3"]
    fade = min(0.25, tl / 3)
    filt.append(f"[{i}:a]aresample=48000,atrim={ts}:{ts+tl},asetpts=PTS-STARTPTS,afade=t=out:st={tl-fade}:d={fade},"
                f"volume={g}dB,adelay={int(st*1000)}|{int(st*1000)}[a{i}]")
filt.append("".join(f"[a{i}]" for i in range(len(EV))) +
            f"amix=inputs={len(EV)}:normalize=0,atrim=0:{DUR},loudnorm=I=-14:TP=-1.5:LRA=11[out]")
args += ["-filter_complex", ";".join(filt), "-map", "[out]", "-ac", "2", "-ar", "48000", OUT]
subprocess.run(args, check=True, capture_output=True)
print("ok", OUT)
