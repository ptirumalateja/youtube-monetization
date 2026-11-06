"""Shorts covers (1080x1920) per language: LANG_V=en|te|hi python3 thumb.py OUT.jpg"""
import sys, numpy as np, cv2, edit as E
T = dict(en=(["VAULT B"], ["₹1 LAKH CRORE FOUND.", "THIS DOOR STAYED SHUT."]),
         te=(["VAULT B"], ["లక్ష కోట్లు దొరికాయి.", "ఈ తలుపు మాత్రం తెరవలేదు."]),
         hi=(["VAULT B"], ["1 लाख करोड़ मिले।", "ये दरवाज़ा नहीं खुला।"]))[E.LANG]
f = E.fit(E.src_frame("flow", "strike_floor", 6.7), 1.04, 0.5, 0.46, wm=True)
f = E.grade(f, "warm") * 1.05
y = np.linspace(0, 1, E.H, dtype=np.float32)[:, None, None]
f = f * (1 - 0.55 * np.clip((0.30 - y) / 0.30, 0, 1)) * (1 - 0.7 * np.clip((y - 0.6) / 0.4, 0, 1)) * E.VIG
f = E.tag(f, 1.0) if False else f
for lines, size, style, cy in ((T[0], 170, "gold", 1330), (T[1][:1], 74, "gold", 1540), (T[1][1:], 62, "ice", 1650)):
    col, a = E.text_rgba(tuple(lines), size, 900, style, cy, 6 if style == "gold" and size > 200 else 2)
    f = f * (1 - a) + col
cv2.imwrite(sys.argv[1], (np.clip(f, 0, 1) * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 95])
