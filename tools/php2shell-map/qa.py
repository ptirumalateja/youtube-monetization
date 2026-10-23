"""Checks before delivery: counters only go up, the date ticker only goes up (until the loop wraps)."""
from PIL import Image
import text as T
from timeline import *

T.LOG = {}
blank = Image.new("RGB", (W, H))
for i in range(int(DUR * FPS)):
    T.draw(blank, i / FPS)
for k, v in T.LOG.items():
    assert all(b >= a for a, b in zip(v, v[1:])), k
    print(k, "monotonic,", v[0], "->", v[-1])
