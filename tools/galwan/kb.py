# Galwan v2: realistic-image reel (Ken Burns + quick dissolves + yellow Telugu subtitles), friend-ref style.
# Usage: python3 kb.py IMGDIR timing.json vo.wav music.mp3 whoosh.mp3 out.mp4
import json, sys, os, subprocess, glob
import numpy as np
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "fonts/NotoSansTelugu-800.ttf")
YEL = (255, 222, 60)
XF = 0.2  # dissolve length (s)
# image k starts on (line, phrase)
ANCH = [(0, 0), (0, 1), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2), (3, 0), (3, 2), (3, 3), (4, 0), (4, 1), (4, 2), (4, 3), (5, 0), (5, 0, 0.5), (6, 0), (6, 1), (7, 0), (7, 1)]
# small top labels like the ref's "19 నవంబర్ 1977" tag (image index -> lines)
TAGS = {0: [("ఒక్క బుల్లెట్ కూడా", 92, (255, 255, 255)), ("పేలలేదు!", 120, YEL)],
        2: [("15 జూన్ 2020", 64, (255, 255, 255)), ("గల్వాన్ లోయ, లద్దాఖ్", 46, YEL)],
        6: [("కల్నల్ బి. సంతోష్ బాబు", 62, (255, 255, 255)), ("సూర్యాపేట, తెలంగాణ · 16 బిహార్ CO", 44, YEL)]}


def load(path, cover=1.16):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    r = w / h
    tw, th = int(W * cover), int(H * cover)
    if abs(r - W / H) < 0.12:
        s = max(tw / w, th / h)
        im = im.resize((int(w * s + 1), int(h * s + 1)), Image.LANCZOS)
        x, y = (im.width - tw) // 2, (im.height - th) // 2
        return im.crop((x, y, x + tw, y + th))
    # other aspect (e.g. a real portrait): blurred fill + framed photo
    s = max(tw / w, th / h)
    bg = im.resize((int(w * s + 1), int(h * s + 1)), Image.LANCZOS)
    bg = bg.crop(((bg.width - tw) // 2, (bg.height - th) // 2, (bg.width - tw) // 2 + tw, (bg.height - th) // 2 + th))
    bg = bg.filter(ImageFilter.GaussianBlur(40))
    bg = Image.eval(bg, lambda v: int(v * 0.55))
    fw = int(tw * 0.74)
    fh = int(fw / r)
    if fh > th * 0.42:
        fh = int(th * 0.42); fw = int(fh * r)
    fg = im.resize((fw, fh), Image.LANCZOS)
    d = ImageDraw.Draw(bg)
    x, y = (tw - fw) // 2, int(th * 0.52 - fh / 2)
    d.rectangle((x - 10, y - 10, x + fw + 10, y + fh + 10), fill=(235, 225, 200))
    bg.paste(fg, (x, y))
    return bg


_F = {}


def font(sz):
    if sz not in _F:
        _F[sz] = ImageFont.truetype(FONT, sz, layout_engine=ImageFont.Layout.RAQM)
    return _F[sz]


def text_img(lines, y0, align_mid=True):
    """lines: [(text, size, color)] stacked from y0; black outline + soft shadow like the ref."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d, ds = ImageDraw.Draw(im), ImageDraw.Draw(sh)
    y = y0
    for txt, sz, col in lines:
        f = font(sz)
        while True:
            bb = d.textbbox((0, 0), txt, font=f, stroke_width=max(3, sz // 14))
            if bb[2] - bb[0] <= 860 or sz < 40:
                break
            sz -= 4; f = font(sz)
        x = (W - (bb[2] - bb[0])) // 2 - bb[0]
        ds.text((x + 3, y + 5), txt, font=f, fill=(0, 0, 0, 200), stroke_width=max(3, sz // 14) + 4, stroke_fill=(0, 0, 0, 200))
        d.text((x, y), txt, font=f, fill=col, stroke_width=max(3, sz // 14), stroke_fill=(0, 0, 0))
        y += int(sz * 1.45)
    sh = sh.filter(ImageFilter.GaussianBlur(8))
    sh.alpha_composite(im)
    return sh


def kb_frame(src, u, k):
    """Ken Burns: alternate push-in / pull-out with a gentle drift."""
    tw, th = src.size
    if k % 2 == 0:
        z = 1.0 + 0.13 * u
    else:
        z = 1.13 - 0.13 * u
    cw, ch = tw / (1.16 * z) * 1.0, th / (1.16 * z)
    drift = (0.5 + 0.06 * (u - 0.5) * (1 if k % 3 else -1))
    cx = tw * drift
    cy = th * (0.5 - 0.03 * (u - 0.5))
    box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
    return src.transform((W, H), Image.EXTENT, box, Image.BICUBIC)


G = {}


def init(imgs, starts, total, caps):
    G["src"] = [load(p) for p in imgs]
    G["starts"], G["total"] = starts, total
    G["caps"] = caps
    G["capimg"] = {}
    G["tags"] = {k: text_img(v, 360) for k, v in TAGS.items()}


def cap_img(i):
    if i not in G["capimg"]:
        lines = G["caps"][i]["lines"]
        n = len(lines)
        y0 = 1380 - int(78 * 1.45) * n + 30
        G["capimg"][i] = text_img([(t, 78, YEL) for t, _ in lines], y0)
    return G["capimg"][i]


def frame(t):
    st, total = G["starts"], G["total"]
    k = max(i for i, s in enumerate(st) if s <= t + 1e-6)
    end = st[k + 1] if k + 1 < len(st) else total
    a = st[k] - (XF if k > 0 else 0)
    u = (t - a) / (end + XF - a)
    im = kb_frame(G["src"][k], min(1, max(0, u)), k)
    if k > 0 and t - st[k] < XF / 2:
        # dissolve from previous: previous plays on into the start of this one
        pk = k - 1
        pa = st[pk] - (XF if pk > 0 else 0)
        pu = (t - pa) / (st[k] + XF - pa)
        prev = kb_frame(G["src"][pk], min(1, pu), pk)
        al = 0.5 + (t - st[k]) / XF
        im = Image.blend(prev, im, max(0, min(1, al)))
    elif k + 1 < len(st) and st[k + 1] - t < XF / 2:
        nk = k + 1
        nxt = kb_frame(G["src"][nk], 0.0, nk)
        al = 0.5 - (st[nk] - t) / XF
        im = Image.blend(im, nxt, max(0, min(1, al)))
    im = im.convert("RGBA")
    if k in G["tags"]:
        im.alpha_composite(G["tags"][k])
    for i, c in enumerate(G["caps"]):
        if c["a"] <= t < c["b"]:
            im.alpha_composite(cap_img(i))
            break
    return np.asarray(im.convert("RGB")).tobytes()


def main():
    imgdir, timing, vo, music, whoosh, out = sys.argv[1:7]
    T = json.load(open(timing))
    imgs = sorted(glob.glob(os.path.join(imgdir, "[0-9][0-9].*")))
    assert len(imgs) == len(ANCH), imgs
    ph = T["phrases"]
    flat = [x for p in ph for x in p] + [T["total"]]

    def at(a):
        l, p = a[0], a[1]
        t = ph[l][p]
        if len(a) > 2:
            i = flat.index(t)
            t = t + (flat[i + 1] - t) * a[2]
        return t - 0.06
    starts = [0.0] + [at(a) for a in ANCH[1:]]
    total = T["total"]
    ts = [i / FPS for i in range(int(total * FPS))]
    pic = out + ".pic.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", pic], stdin=subprocess.PIPE)
    with Pool(4, initializer=init, initargs=(imgs, starts, total, T["caps"])) as p:
        for i, buf in enumerate(p.imap(frame, ts, chunksize=8)):
            ff.stdin.write(buf)
            if i % 150 == 0:
                print(f"{i}/{len(ts)}", flush=True)
    ff.stdin.close(); ff.wait()
    # audio: VO + ducked music + soft whooshes on cuts after the hook (none in hook / CTA)
    ins = ["-i", pic, "-i", vo, "-i", music]
    fl = []
    cuts = [s for s in starts[1:] if 3.0 < s < 27.5]
    for j, s in enumerate(cuts):
        ins += ["-i", whoosh]
        fl.append(f"[{j+3}:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.18,adelay={int((s-0.12)*1000)}|{int((s-0.12)*1000)}[w{j}]")
    fl.append("[1:a]aresample=48000,aformat=channel_layouts=stereo,apad,asplit=2[v1][v2]")
    fl.append(f"[2:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.34,afade=t=out:st={total-1.2:.2f}:d=1.2[mu]")
    fl.append("[mu][v2]sidechaincompress=threshold=0.05:ratio=4:attack=20:release=300[md]")
    fl.append("[v1][md]" + "".join(f"[w{j}]" for j in range(len(cuts))) + f"amix=inputs={len(cuts)+2}:normalize=0:duration=first,atrim=0:{total:.3f},loudnorm=I=-14:TP=-1.5:LRA=9[a]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + ins + ["-filter_complex", ";".join(fl), "-map", "0:v", "-map", "[a]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", out], check=True)
    print("done", out)


if __name__ == "__main__":
    main()
