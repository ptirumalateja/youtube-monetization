# Render the Galwan reel picture track. Usage: python3 render.py timing.json out.mp4 [fps] [t0 t1]
import json, sys, os, subprocess, math
import numpy as np
from multiprocessing import Pool
from lino import Canvas, label, W, H
from shots import SHOTS

# line -> shots (name, weight)
# line -> shots (name, phrase index it starts on)
PLAN = [
    [("standoff", 0), ("front", 1), ("milestone", 2)],
    [("date", 0), ("valley", 1), ("cold", 2)],
    [("tent", 0), ("walk", 1), ("name", 2)],
    [("rifle", 0), ("rocks", 2), ("clubs", 3)],
    [("wounded", 0), ("moonclose", 2), ("moonhero", 3)],
    [("diyas", 0)],
    [("medal", 0), ("medal2", 1)],
    [("flag", 0)],
]
NOPUNCH = {"standoff", "diyas", "flag", "name", "date", "rifle"}
NOCAP = {"milestone", "name", "medal", "medal2", "flag", "moonclose", "date", "standoff", "front"}
WIPE = 0.12  # seconds of brayer wipe across a cut


def build(timing):
    shots = []
    for ph, plan in zip(timing["phrases"], PLAN):
        for n, k in plan:
            shots.append((n, max(0, ph[k] - 0.08), None))
    # first shot starts at 0, last ends at total
    shots[0] = (shots[0][0], 0.0, shots[0][2])
    for i in range(len(shots) - 1):
        shots[i] = (shots[i][0], shots[i][1], shots[i + 1][1])
    shots[-1] = (shots[-1][0], shots[-1][1], timing["total"])
    return shots


def frame(args):
    t, shots, caps = args
    idx = max(i for i, s in enumerate(shots) if s[1] <= t + 1e-6)
    n, a, b = shots[idx]
    import lino
    lino.PUNCH[0] = 1.14 if (b - a > 1.25 and t - a > (b - a) * 0.5 and n not in NOPUNCH) else 1.0
    C = Canvas(t)
    SHOTS[n](C, t - a, b - a)
    img = C.out()
    # wipe from previous shot
    if idx > 0 and t - a < WIPE and n not in ("standoff",):
        pn, pa, pb = shots[idx - 1]
        lino.PUNCH[0] = 1.14 if (pb - pa > 1.25 and pn not in NOPUNCH) else 1.0
        P = Canvas(t)
        SHOTS[pn](P, t - pa, pb - pa)
        prev = P.out()
        u = (t - a) / WIPE
        yy, xx = np.mgrid[0:H, 0:W]
        edge = -400 + u * (H + 1300)
        pos = yy + (xx - 540) * 0.35
        m = (pos < edge)[..., None]
        img = np.where(m, img, prev)
        band = ((pos >= edge - 26) & (pos < edge))[..., None]
        img = np.where(band, np.array([228, 126, 34], np.uint8), img)
    # captions
    if n not in NOCAP:
        for c in caps:
            if c["a"] <= t < c["b"]:
                C2 = Canvas(t)
                C2.img = img.astype(np.float32)
                label(C2, [(x[0], x[1]) for x in c["lines"]], 1300, size=70, t=t, tin=c["a"])
                img = C2.out()
                break
    return img.tobytes()


def main():
    timing = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    fps = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    t0 = float(sys.argv[4]) if len(sys.argv) > 4 else 0
    t1 = float(sys.argv[5]) if len(sys.argv) > 5 else timing["total"]
    shots = build(timing)
    json.dump(shots, open(out + ".shots.json", "w"), indent=0)
    caps = timing.get("caps", [])
    ts = [t0 + i / fps for i in range(int((t1 - t0) * fps))]
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    with Pool(4) as p:
        for i, buf in enumerate(p.imap(frame, [(t, shots, caps) for t in ts], chunksize=4)):
            ff.stdin.write(buf)
            if i % 60 == 0:
                print(f"{i}/{len(ts)}", flush=True)
    ff.stdin.close()
    ff.wait()


if __name__ == "__main__":
    main()
