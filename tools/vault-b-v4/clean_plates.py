"""Remove the baked-in v1 text from the Blender clips: rebuild each overlay mask with tools/vault-b/overlay.py and inpaint it.
Writes plates/clean/<shot>/f####.jpg. v1 frame map (24 fps): gold 0-59, door 60-119, gopuram 120-179, vaults 180-239,
lamp 240-275, heads 276-317, seam 318-359, hand 360-401, eyes 402-479."""
import os, sys, numpy as np, cv2
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "vault-b"))
import overlay as ov
R = os.path.dirname(os.path.abspath(__file__))
def mask_of(fn):
    blk = Image.new("RGB", (ov.W, ov.H), (128, 128, 128)); a = np.asarray(fn(blk.copy()), np.int16)
    core = ((a - 128).max(2) > 22).astype(np.uint8) * 255   # bright strokes + glow core
    near = cv2.dilate(core, np.ones((41, 41), np.uint8))       # the dark drop-shadow halo hugging the letters
    halo = ((np.abs(a - 128).max(2) > 14).astype(np.uint8) * 255) & near
    return cv2.dilate(core | halo, np.ones((7, 7), np.uint8))
SEGS = {  # shot: (first v1 frame, count, [(local frame from, overlay fn)])
    "gold":   (0, 60,  [(0, lambda im: ov.tag(im)), (9, lambda im: ov.big(ov.tag(im), ['THEY OPENED', 'FIVE DOORS.']))]),
    "door":   (60, 60, [(0, lambda im: ov.tag(im)), (9, lambda im: ov.big(ov.tag(im), ['THIS ONE,', 'THEY LEFT SHUT.'], cy=1520, size=84))]),
    "gopuram":(120, 60,[(0, lambda im: ov.small(im, ['Beneath Padmanabhaswamy.', "India's richest room."], cy=1560, size=56))]),
    "vaults": (180, 60, []),
    "lamp":   (240, 36, [(5, lambda im: ov.big(im, ['THEN THEY', 'REACHED B.'], cy=700))]),
    "heads":  (276, 42, [(4, lambda im: ov.small(im, ['No handle.', 'No lock.'], cy=1480, size=62))]),
    "seam":   (318, 42, [(4, lambda im: ov.small(im, ['They say only a chant', 'can open it.'], cy=1420, size=58))]),
    "hand":   (360, 42, []),
    "eyes":   (402, 78, [(10, lambda im: ov.big(im, ['STILL SHUT.'], cy=1460, size=104)),
                         (36, lambda im: ov.small(ov.big(im, ['STILL SHUT.'], cy=1460, size=104), ['Would you open it?'], cy=1610, size=58))]),
}
ONLY = sys.argv[1:]
for shot, (f0, n, ovs) in SEGS.items():
    if ONLY and shot not in ONLY: continue
    out = f"{R}/plates/clean/{shot}"; os.makedirs(out, exist_ok=True)
    masks = [(s, mask_of(fn)) for s, fn in ovs]
    for i in range(n):
        im = cv2.imread(f"{R}/plates/v1_{f0 + i + 1:04d}.jpg")
        m = None
        for s, mm in masks:
            if i >= s - 1: m = mm  # one frame early: fades
        # the fade-in frames before a line lands also carry faint text
        if m is not None: im = cv2.inpaint(im, m, 5, cv2.INPAINT_TELEA)
        cv2.imwrite(f"{out}/f{i:04d}.jpg", im, [cv2.IMWRITE_JPEG_QUALITY, 95])
    print(shot, n, flush=True)
