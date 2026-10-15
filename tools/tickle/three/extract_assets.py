#!/usr/bin/env python3
"""Extract teal contour line art from the Meta hand/brain/macro images into alpha PNGs (white lines, transparent bg) for scene4.
usage: python3 extract_assets.py <images_dir> <out_dir>   (expects 20.webp palm, 21.webp two hands, 22.webp brain, 23.webp macro)"""
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
src, out = sys.argv[1], sys.argv[2]
def alpha_of(im):
    a = np.asarray(im.convert("RGB")).astype(float); R, G = a[..., 0], a[..., 1]
    return np.clip(np.clip((G - np.maximum(R * 1.3, 32)) / 160, 0, 1) * 1.7, 0, 1)
def save(al, name):
    o = np.zeros(al.shape + (4,), np.uint8); o[..., :3] = 255; o[..., 3] = (al * 255).astype(np.uint8)
    Image.fromarray(o, "RGBA").save(f"{out}/{name}.png"); print(name, o.shape)
for f, name in (("20.webp", "palm"), ("22.webp", "brain"), ("23.webp", "macro")):
    save(alpha_of(Image.open(f"{src}/{f}")), name)
al = alpha_of(Image.open(f"{src}/21.webp")); m = ndi.binary_dilation(al > 0.2, iterations=9)
lab, n = ndi.label(m); sizes = ndi.sum(m, lab, range(1, n + 1)); top2 = np.argsort(-sizes)[:2] + 1
cents = [ndi.center_of_mass(lab == k)[0] for k in top2]
top = top2[int(np.argmin(cents))]; palm = top2[int(np.argmax(cents))]
save(al * (lab == top), "other_hand"); save(al * (lab == palm), "own_palm")
