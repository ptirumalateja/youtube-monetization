"""Kepler-cut sound mix: python3 kmix.py SFXDIR OUT.wav"""
import sys, subprocess
SFX, OUT = sys.argv[1], sys.argv[2]
DUR = 31.2
EV = [
    ('space', 0, -18, 0, 6.0),
    ('space', 6, -18, 0, 6.0),
    ('space', 12, -18, 0, 6.0),
    ('space', 18, -18, 0, 6.0),
    ('space', 24, -18, 0, 6.0),
    ('rise', 15.2, -4, 0, 1.9),
    ('braam', 17.0, 0, 0, 4.0),
    ('braam', 18.2, -7, 0.5, 2.8),
    ('whoosh', 20.9, -6, 0, 1.2),
    ('whoosh', 21.1, -3, 0.2, 1.0),
    ('impacts', 22.12, 0, 0, 1.6),
    ('impacts', 22.4, -6, 1.0, 1.0),
    ('whoosh', 22.7, -12, 0.2, 1.0),
    ('rise', 23.4, -12, 0, 2.0),
    ('braam', 24.0, -9, 0.6, 2.4),
    ('rise', 25.4, -14, 0, 2.5),
    ('space', 30.0, -18, 0, 1.2),
    ('braam', 28.4, -8, 0, 2.8),
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
