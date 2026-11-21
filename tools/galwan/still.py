import sys, time
from PIL import Image
from lino import Canvas
from shots import SHOTS
names = sys.argv[1].split(",") if len(sys.argv) > 1 else list(SHOTS)
out = "/tmp/claude-0/galwan/stills"; import os; os.makedirs(out, exist_ok=True)
ims = []
for n in names:
    t0 = time.time(); C = Canvas(0.6); SHOTS[n](C, 0.6, 1.4); a = C.out()
    print(n, round(time.time() - t0, 2)); im = Image.fromarray(a); im.save(f"{out}/{n}.jpg", quality=88); ims.append(im.resize((270, 480)))
cols = 7; rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (cols * 270, rows * 480), "white")
for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * 270, (i // cols) * 480))
sheet.save(f"{out}/sheet.jpg", quality=85)
