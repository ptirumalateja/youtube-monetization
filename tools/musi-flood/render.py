# Musi flood (చింత చెట్టు) Telugu real-image reel: stills with Ken Burns + two Flow clips, yellow subs, big number tags.
# Usage: python3 render.py IMGDIR out.mp4   (needs tok_final.json, vo_final.wav, music.mp3, clipfr/A|B frames)
import json, sys, os, subprocess
import numpy as np
from multiprocessing import Pool
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../galwan"))
import kb  # load(), kb_frame(), text_img(), YEL, W, H
W, H, FPS, XF, YEL = kb.W, kb.H, 30, 0.2, kb.YEL
WH = (255, 255, 255)
T = json.load(open(os.path.join(HERE, os.environ.get("TOK", "tok_v5.json"))))
tok = [t for _, t in T["tokens"]]
TOTAL = T["total"] + 0.6

# (start token, media, tag lines). media: "NN" still or ("A"|"B", src start s)
SHOTS = [
    (0.0, "09", [("హైదరాబాద్ · 1908", 80, WH)]),
    (1.48, ("B", 1.8), [("15,000+", 150, YEL), ("ఒకే రాత్రి", 70, WH)]),
    (7, ("A", 0.3), [("150", 170, YEL), ("మంది బతికారు", 64, WH)]),
    (11, "11", None),
    (16, "03", [("28 సెప్టెంబర్ 1908", 72, WH), ("హైదరాబాద్", 50, YEL)]),
    (23, "04", None),
    (25, "05", [("36 గంటలు", 92, YEL), ("17 అంగుళాల వర్షం", 62, WH)]),
    (31, ("B", 5.0), [("60 అడుగులు", 110, YEL), ("పైకి లేచిన మూసీ", 60, WH)]),
    (37, "07", None),
    (38, "08", None),
    (39, "06", None),
    (42, "10", [("అఫ్జల్‌గంజ్", 80, YEL)]),
    (49, ("A", 3.6), [("150", 170, YEL)]),
    (52, "12", None),
    (55, "02", None),
    (59, "13", [("ఉస్మానియా ఆసుపత్రి", 76, WH), ("అఫ్జల్‌గంజ్ · ఇప్పటికీ ఉంది", 50, YEL)]),
    (64, "14", None),
    (70, "15", [("ఎం. విశ్వేశ్వరయ్య", 70, WH)]),
    (76, "16", None),
    (80, "17", [("ఉస్మాన్ సాగర్", 84, YEL), ("+ హిమాయత్ సాగర్", 70, YEL)]),
    (84, "18", None),
    (89, "19", None),
    (94, "20", None),
]
# caption chunks: (first token, display text)
CAPS = [(0.0, "హైదరాబాద్‌ను ముంచేసిన వరద…"), (1.48, "ఒకే రాత్రి…"), (2.16, "15,000 మందికి పైగా బలి తీసుకుంది."), (7, "కానీ 150 మందిని…"), (11, "ఒకే ఒక్క చెట్టు కాపాడింది."),
        (15, "తెలుసా?"), (16, "అది 1908, సెప్టెంబర్ 28."), (23, "హైదరాబాద్ నిద్రపోతోంది."), (25, "36 గంటల్లో"),
        (28, "17 అంగుళాల వర్షం."), (31, "మూసీ నది"), (33, "60 అడుగులు పైకి లేచింది."), (37, "ఇళ్లు, వంతెనలు, మనుషులు…"),
        (40, "అన్నీ కొట్టుకుపోయాయి."), (42, "అప్పుడు అఫ్జల్‌గంజ్‌లో"), (44, "ఒక పెద్ద చింత చెట్టు ఎక్కారు"), (49, "150 మంది."),
        (52, "నీళ్లు తగ్గే వరకూ…"), (55, "ఆ కొమ్మలే వాళ్ల ప్రాణం."), (59, "ఆ చెట్టు ఇప్పటికీ"), (62, "ఉస్మానియా ఆసుపత్రిలో బతికే ఉంది."),
        (66, "కానీ అసలు విషయం ఏంటంటే…"), (70, "ఈ వరద తర్వాతే"), (73, "నిజాం విశ్వేశ్వరయ్యను పిలిపించారు."),
        (76, "మళ్లీ ఇలా జరగకూడదని కట్టినవే…"), (80, "ఉస్మాన్ సాగర్, హిమాయత్ సాగర్."), (84, "అంటే ఈరోజు హైదరాబాద్ తాగే నీళ్లు…"),
        (89, "ఆ ఒక్క రాత్రి నేర్పిన పాఠం."), (94, "ఇలాంటి మరిన్ని విషయాల కోసం…"), (98, "'విషయం ఏంటంటే' ని సబ్‌స్క్రైబ్ చేయండి.")]
# per-image camera move: (zoom start, zoom end, focus start (x,y), focus end (x,y)); focus in 0-1 of the image
MOVES = {
    "11": (1.25, 1.12, (.50, .30), (.55, .58)),   # tilt down from the sky onto the crowd
    "02": (1.05, 1.35, (.40, .45), (.55, .38)),   # push into the gripping hands
    "03": (1.30, 1.15, (.50, .75), (.50, .38)),   # tilt up the street to Charminar
    "04": (1.35, 1.05, (.65, .65), (.50, .50)),   # pull out from the family
    "05": (1.30, 1.25, (.55, .28), (.50, .70)),   # pan down: lightning -> river
    "07": (1.05, 1.30, (.45, .50), (.68, .55)),   # diagonal push toward the fleeing people
    "08": (1.30, 1.30, (.30, .55), (.70, .55)),   # side pan across the broken bridge
    "06": (1.30, 1.20, (.50, .78), (.50, .40)),   # tilt up from the torches to the bridge
    "09": (1.00, 1.45, (.50, .60), (.72, .30)),   # hook: fast push into flooded Charminar
    "10": (1.30, 1.15, (.30, .70), (.55, .55)),   # rising diagonal toward the child
    "12": (1.30, 1.18, (.50, .78), (.50, .35)),   # tilt up the trunk
    "13": (1.40, 1.05, (.45, .62), (.50, .50)),   # pull out from the trunk to reveal the hospital
    "14": (1.05, 1.35, (.50, .50), (.48, .62)),   # push into the plaque
    "15": (1.10, 1.35, (.35, .40), (.60, .62)),   # push onto the map
    "16": (1.30, 1.22, (.45, .25), (.50, .72)),   # pan down along the dam works
    "17": (1.30, 1.15, (.70, .70), (.40, .35)),   # diagonal glide along the dam
    "18": (1.05, 1.30, (.50, .40), (.52, .72)),   # push down to the glass
    "19": (1.30, 1.30, (.70, .55), (.30, .55)),   # side pan across the skyline
    "20": (1.30, 1.00, (.40, .60), (.50, .50)),   # slow pull out at the end
}


def ease(u):
    return u * u * (3 - 2 * u)


def move_frame(src, u, mv):
    z0, z1, (x0, y0), (x1, y1) = mv
    e = ease(u)
    z = z0 + (z1 - z0) * e
    tw, th = src.size
    cw, ch = tw / (1.16 * z), th / (1.16 * z)
    mx, my = tw * 0.065, th * 0.065  # keep off the edges (Gemini sparkle sits bottom-right)
    cw, ch = min(cw, tw - 2 * mx), min(ch, th - 2 * my)
    cx = min(max(tw * (x0 + (x1 - x0) * e), mx + cw / 2), tw - mx - cw / 2)
    cy = min(max(th * (y0 + (y1 - y0) * e), my + ch / 2), th - my - ch / 2)
    return src.transform((W, H), Image.EXTENT, (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2), Image.BICUBIC)


LEAD = 0.06
at = lambda x: x if isinstance(x, float) else tok[x] - LEAD
starts = [0.0] + [at(s[0]) for s in SHOTS[1:]]
cst = [0.0] + [at(c[0]) for c in CAPS[1:]]
G = {}


def clip_frame(name, t):
    n = int(round(t * FPS)) + 1
    d = os.path.join(HERE, "clipfr", name)
    n = max(1, min(n, len(os.listdir(d))))
    im = Image.open(os.path.join(d, f"{n:04d}.jpg")).convert("RGB")
    # crop 1.2x from the top to hide the Veo sparkle (bottom right) + slow push
    return im


def init(imgdir):
    G["src"] = {}
    for _, m, _ in SHOTS:
        if isinstance(m, str) and m not in G["src"]:
            G["src"][m] = kb.load(os.path.join(imgdir, m + ".jpg"))
    G["tags"] = {i: kb.text_img(tg, 330) for i, (_, _, tg) in enumerate(SHOTS) if tg}
    G["caps"] = {}


def cap_img(i):
    if i not in G["caps"]:
        G["caps"][i] = kb.text_img([(CAPS[i][1], 76, YEL)], 1290)
    return G["caps"][i]


def shot_img(k, t):
    s, m, _ = SHOTS[k]
    a = starts[k] - (XF if k else 0)
    end = starts[k + 1] if k + 1 < len(SHOTS) else TOTAL
    u = min(1, max(0, (t - a) / (end + XF - a)))
    if isinstance(m, str):
        return move_frame(G["src"][m], u, MOVES.get(m, (1.0, 1.13, (.5, .5), (.5, .5))))
    name, s0 = m
    im = clip_frame(name, s0 + max(0, t - starts[k]))
    z = 1.2 + 0.06 * u
    cw, ch = W / z, H / z
    x0, y0 = (W - cw) / 2, H * 0.02
    return im.transform((W, H), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BICUBIC)


def frame(t):
    k = max(i for i, s in enumerate(starts) if s <= t + 1e-6)
    im = shot_img(k, t)
    if k > 0 and t - starts[k] < XF / 2:
        im = Image.blend(shot_img(k - 1, t), im, max(0, min(1, 0.5 + (t - starts[k]) / XF)))
    elif k + 1 < len(starts) and starts[k + 1] - t < XF / 2:
        im = Image.blend(im, shot_img(k + 1, starts[k + 1]), max(0, min(1, 0.5 - (starts[k + 1] - t) / XF)))
    im = im.convert("RGBA")
    if k in G["tags"]:
        im.alpha_composite(G["tags"][k])
    c = max(i for i, s in enumerate(cst) if s <= t + 1e-6)
    if t < T["total"] + 0.3:
        im.alpha_composite(cap_img(c))
    return np.asarray(im.convert("RGB")).tobytes()


def main():
    imgdir, out = sys.argv[1], sys.argv[2]
    ts = [i / FPS for i in range(int(TOTAL * FPS))]
    pic = out + ".pic.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", pic], stdin=subprocess.PIPE)
    with Pool(4, initializer=init, initargs=(imgdir,)) as p:
        for i, buf in enumerate(p.imap(frame, ts, chunksize=8)):
            ff.stdin.write(buf)
    ff.stdin.close(); ff.wait()
    vo, mu = os.path.join(HERE, os.environ.get("VO", "vo_v5.wav")), os.path.join(HERE, "music.mp3")
    ps = T.get("pause", [0, 0])[0]
    fl = ["[1:a]aresample=48000,aformat=channel_layouts=stereo,apad,asplit=2[v1][v2]",
          f"[3:a]aresample=48000,aformat=channel_layouts=stereo,volume={os.environ.get('BRAAM', '0')},adelay={int(ps*1000)}|{int(ps*1000)}[br]",
          f"[2:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.32,afade=t=out:st={TOTAL-1.2:.2f}:d=1.2[mu]",
          "[mu][v2]sidechaincompress=threshold=0.05:ratio=4:attack=20:release=300[md]",
          f"[v1][md][br]amix=inputs=3:normalize=0:duration=first,atrim=0:{TOTAL:.3f},loudnorm=I=-14:TP=-1.5:LRA=9[a]"]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", pic, "-i", vo, "-i", mu, "-i", os.path.join(HERE, "braam.mp3"), "-filter_complex", ";".join(fl),
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", out], check=True)
    os.remove(pic)
    print("done", out, TOTAL)


if __name__ == "__main__":
    main()
