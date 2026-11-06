#!/usr/bin/env python3
"""Fit the V5 picture to the v2 (natural, ~45 s) hi/te dubs from dub2.py.
Anchors pair an English tight-VO word time with the matching dub word time (from Scribe on vo2_LANG.wav),
so every cut, SFX hit and duck lands on the dub word. Captions are written fresh, in dub time.
Usage: fit2.py LANG WORKDIR   (needs WORKDIR/stt2_LANG.json; writes cut2_LANG.py and srt/skeleton-lake-v5-LANG.LANG.srt)
Env TEMPO = playback tempo of the dub in mix4."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dub import srt, strip, HERE
from dub2 import LINES
LANG, WORK = sys.argv[1:3]
TEMPO = float(os.environ['TEMPO'])
W = [w for w in json.load(open(f'{WORK}/stt2_{LANG}.json'))['words'] if w['type'] == 'word']
s = lambda i: W[i]['start']; e = lambda i: W[i]['end']

# (English tight-VO time, dub word index) ; final pair is the end of the reel
if LANG == 'te':
    A = [(1.43, 2), (2.67, 4), (4.53, 8), (5.42, 10), (6.54, 12), (9.28, 18), (11.18, 21), (16.97, 27), (18.14, 31),
         (21.12, 36), (22.59, 41), (23.97, 44), (25.17, 48), (28.96, 52), (33.07, 58), (35.03, 63), (36.25, 65),
         (37.31, 67), (38.54, 71), (40.58, 75), (41.73, 77), (43.49, 78), (44.32, 83), (47.52, 89), (48.61, 90)]
    C = [(2, 4, "మంచు\\N{Y}కరగగానే{W}..."), (4, 9, "సరస్సు బయటపెడుతుంది\\N{Y}శవాలను{W}"), (9, 12, "{Y}రూప్‌కుండ్{W}"),
         (12, 13, "{Y}హిమాలయాలు{W}"), (13, 17, "{Y}5,000 మీ.{W} ఎత్తు"), (17, 21, "{Y}వందల{W}\\Nఅస్థిపంజరాలు"),
         (21, 25, "అంతా {Y}ఒకే రాత్రి{W}\\Nచనిపోయారని..."), (25, 27, "అందరూ\\Nఅనుకున్నారు"), (27, 31, "{Y}కానీ కాదు.{W}"),
         (31, 34, "DNA చెప్పిన\\N{Y}నిజం{W}"), (34, 41, "మొదటి గుంపు\\N{Y}1,200 ఏళ్ల క్రితం{W}"),
         (41, 48, "రెండో గుంపు\\N{Y}200 ఏళ్ల క్రితం{W}"), (48, 50, "{Y}ఒకే{W} సరస్సు"), (50, 52, "{Y}1,000 ఏళ్ల{W}\\Nతేడా"),
         (52, 54, "ఇంకా\\N{Y}విచిత్రం{W}..."), (54, 58, "రెండో గుంపు\\NDNA..."), (58, 63, "{Y}గ్రీస్{W}, {Y}క్రీట్{W}"),
         (63, 67, "పుర్రెలు\\N{Y}పగిలి ఉన్నాయి{W}"), (67, 71, "{Y}పై{W} నుంచి"), (71, 75, "ఊరి వాళ్ల\\N{Y}పాట{W}"),
         (75, 78, "{Y}నందాదేవి{W}\\Nకోపం"), (78, 83, "{Y}ఇనుప గుండ్ల{W}\\Nలాంటి వడగళ్లు"), (83, 85, "ప్రతి\\N{Y}వేసవి{W}..."),
         (85, 90, "ఇంకొన్ని\\N{Y}రహస్యాలు{W}"), (90, None, "అసలు వాళ్లు\\N{Y}ఎవరు?{W}"),
         (92, None, "{\\pos(540,1470)\\fs60}కామెంట్‌లో చెప్పండి ↓")]
else:
    A = [(1.43, 3), (2.67, 6), (4.53, 10), (5.42, 16), (6.54, 17), (9.28, 22), (11.18, 27), (16.97, 38), (17.17, 40),
         (18.14, 42), (21.12, 50), (22.59, 54), (23.97, 58), (25.17, 61), (28.96, 68), (33.07, 75), (35.03, 83),
         (36.25, 85), (37.31, 89), (38.54, 96), (40.58, 101), (41.73, 104), (43.49, 106), (44.32, 111), (47.52, 118),
         (48.61, 121)]
    C = [(3, 6, "जब {Y}बर्फ़{W}\\Nपिघलती है..."), (6, 14, "झील बाहर ले आती है\\N{Y}लाशें{W}"), (14, 17, "{Y}रूपकुंड{W}"),
         (17, 19, "{Y}हिमालय{W}"), (19, 22, "{Y}5,000 मीटर{W} ऊपर"), (22, 27, "{Y}सैकड़ों{W}\\Nकंकाल"),
         (27, 38, "सब {Y}एक ही रात{W}\\Nमें मरे?"), (38, 42, "{Y}ऐसा नहीं था।{W}"), (42, 46, "DNA ने\\N{Y}चौंका दिया{W}"),
         (46, 54, "पहला ग्रुप\\N{Y}1,200 साल पहले{W}"), (54, 61, "दूसरा ग्रुप\\N{Y}सिर्फ़ 200 साल{W}"), (61, 64, "{Y}एक ही{W} झील"),
         (64, 68, "{Y}1,000 साल{W}\\Nका फ़ासला"), (68, 71, "सबसे\\N{Y}अजीब?{W}"), (71, 75, "दूसरे ग्रुप का\\NDNA..."),
         (75, 83, "{Y}ग्रीस{W} और {Y}क्रीट{W}"), (83, 88, "खोपड़ियाँ\\N{Y}टूटी हुई{W}"), (88, 96, "{Y}ऊपर{W} से\\Nचोट?"),
         (96, 101, "गाँव का\\N{Y}लोकगीत{W}"), (101, 106, "{Y}नंदा देवी{W}\\Nका गुस्सा"), (106, 111, "{Y}लोहे{W} जैसे\\Nओले"),
         (111, 114, "हर\\N{Y}गर्मी{W}..."), (114, 121, "कुछ और\\N{Y}राज़{W}"), (121, None, "आख़िर ये\\N{Y}कौन थे?{W}"),
         (125, None, "{\\pos(540,1470)\\fs60}कमेंट में बताइए ↓")]

END = W[-1]['end'] + 0.55
anc = [(0.0, 0.0)] + [(t, round(s(i) - 0.04, 3)) for t, i in A] + [(50.30, round(END, 3))]
assert all(b[0] > a[0] and b[1] > a[1] for a, b in zip(anc, anc[1:])), anc
caps = [(round(s(a) - 0.06, 3), round((s(b) - 0.04) if b is not None else END, 3), t) for a, b, t in C]
with open(f'{WORK}/cut2_{LANG}.py', 'w') as f:
    f.write(f"""import numpy as np
ANC = {anc!r}
_x = [a for a, _ in ANC]; _y = [b for _, b in ANC]
MAPT = lambda t: float(np.interp(t, _x, _y))
CAPS = {caps!r}
""")
# SRT: one row per script line, from dub2's line start/end
dub = json.load(open(f'{WORK}/map2_{LANG}.json'))['dub']
rows = [(a / TEMPO, b / TEMPO + .2, strip(L[2 if LANG == 'te' else 3])) for (a, b), L in zip(dub, LINES)]
os.makedirs(f'{WORK}/srt', exist_ok=True)
srt(f'{WORK}/srt/skeleton-lake-v5-{LANG}.{LANG}.srt', rows)
print(LANG, 'final length', round(END / TEMPO, 2), 's')
