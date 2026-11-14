"""Kepler-cut sound mix: python3 kmix.py SFXDIR OUT.wav"""
import sys, subprocess
SFX, OUT = sys.argv[1], sys.argv[2]
DUR = 25.8
EV = [
    ('space', 0, -18, 0, 6.0),
    ('space', 6, -18, 0, 6.0),
    ('space', 12, -18, 0, 6.0),
    ('space', 18, -18, 0, 6.0),
    ('space', 24, -18, 0, 6.0),
    ('whoosh', 2.45, -16, 0.3, 0.8),
    ('whoosh', 4.05, -16, 0.3, 0.8),
    ('whoosh', 6.6499999999999995, -16, 0.3, 0.8),
    ('whoosh', 7.85, -16, 0.3, 0.8),
    ('whoosh', 10.549999999999999, -16, 0.3, 0.8),
    ('whoosh', 12.35, -16, 0.3, 0.8),
    ('whoosh', 13.85, -16, 0.3, 0.8),
    ('whoosh', 20.85, -16, 0.3, 0.8),
    ('rise', 13.6, -6, 0, 2.0),
    ('braam', 15.6, 0, 0, 4.0),
    ('whoosh', 18.5, -6, 0, 1.4),
    ('whoosh', 19.2, -3, 0.2, 1.0),
    ('impacts', 20.07, 0, 0, 1.6),
    ('impacts', 20.35, -6, 1.0, 1.0),
    ('braam', 22.8, -5, 0, 3.0),
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
