#!/usr/bin/env python3
"""Skeleton Lake hi/te dubs v2: natural spoken scripts (roopkund-reel/dub-scripts-v2.md), fitted to 40-45 s.

Each new line covers a group of the English V5 lines (GRP = first..last English SEG index from dub.py), so the
English picture cut, SFX and caption slots are mapped onto the dub group by group (piecewise linear).
Inside a group, Scribe word times on the dub line give extra anchors where an English caption slot has a KEY word.

Usage: dub2.py LANG EN_WORDS_JSON WORKDIR   (writes vo_LANG.wav, cut_LANG.py, srt/, map_LANG.json)
Env: GAP (pause between lines, s, default .28)  TEMPO (playback tempo in mix4, default 1.12)"""
import json, os, sys, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dub import SEG as SEG_EN, tts, load, en_segments, srt, strip, HERE

# (first English SEG index, last, Telugu, Hindi). Tags are eleven_v3 delivery hints only.
LINES = [
 (0, 1,   "[whispers] ప్రతి వేసవిలో మంచు కరగగానే... ఈ సరస్సు శవాలను బయటపెడుతుంది.",
          "[whispers] हर साल जब बर्फ़ पिघलती है... ये झील अपनी लाशें बाहर ले आती है।"),
 (2, 4,   "ఇది రూప్‌కుండ్. హిమాలయాల్లో ఐదు వేల మీటర్ల ఎత్తు. ఇక్కడ వందల అస్థిపంజరాలు దొరికాయి.",
          "ये है रूपकुंड। हिमालय में पाँच हज़ार मीटर ऊपर। यहाँ मिले हैं सैकड़ों कंकाल।"),
 (5, 6,   "వీళ్లంతా ఒకే రాత్రి చనిపోయారని అందరూ అనుకున్నారు.",
          "माना गया कि ये सब एक ही रात में मरे थे।"),
 (7, 7,   "[low] కానీ అది నిజం కాదు.",
          "[low] लेकिन ऐसा नहीं था।"),
 (8, 11,  "DNA చెప్పిన నిజం... ఒక గుంపు పన్నెండు వందల ఏళ్ల క్రితం చనిపోయింది. ఇంకో గుంపు... కేవలం రెండు వందల ఏళ్ల క్రితం. ఒకే సరస్సు... వెయ్యేళ్ల తేడా.",
          "DNA ने चौंका दिया। एक ग्रुप की मौत बारह सौ साल पहले हुई... और दूसरे की सिर्फ़ दो सौ साल पहले। एक ही झील... हज़ार साल का फ़ासला।"),
 (12, 13, "ఇంకా విచిత్రం... ఆ రెండో గుంపు DNA, గ్రీస్, క్రీట్ ప్రజలకు దగ్గరగా ఉంది.",
          "और सबसे अजीब? दूसरे ग्रुप का DNA... ग्रीस और क्रीट के लोगों से मिलता है।"),
 (14, 15, "కొన్ని పుర్రెలు పగిలి ఉన్నాయి... పై నుంచి ఏదో బలంగా తగిలినట్టు.",
          "कुछ खोपड़ियाँ टूटी हुई हैं... जैसे ऊपर से कोई ज़ोरदार चोट लगी हो।"),
 (16, 18, "ఊరి వాళ్ల పాట ప్రకారం... నందాదేవి కోపంతో ఇనుప గుండ్ల లాంటి వడగళ్లు కురిపించింది.",
          "गाँव के लोकगीत में... नंदा देवी के गुस्से से लोहे जैसे ओले बरसे थे।"),
 (19, 20, "ప్రతి వేసవి... మంచు ఇంకొన్ని రహస్యాలు బయటపెడుతుంది.",
          "और हर गर्मी... बर्फ़ कुछ और राज़ खोल देती है।"),
 (21, 21, "[whispers] అసలు వీళ్లెవరు? కామెంట్‌లో చెప్పండి.",
          "[whispers] आख़िर ये कौन थे? कमेंट में बताइए।"),
]


if __name__ == '__main__':
    LANG, WORDS, WORK = sys.argv[1:4]
    li = 2 if LANG == 'te' else 3
    GAP = float(os.environ.get('GAP', '.28')); TEMPO = float(os.environ.get('TEMPO', '1.12'))
    d = f'{WORK}/{os.environ.get("SEGDIR", "seg3")}_{LANG}'; os.makedirs(d, exist_ok=True)
    en = en_segments(json.load(open(WORDS)))
    pieces, dub, t = [np.zeros(int(.15 * 48000), np.float32)], [], .15
    for k, L in enumerate(LINES):
        mp3 = f'{d}/{k:02d}.mp3'; tts(L[li], mp3); a = load(mp3)
        if k: pieces.append(np.zeros(int(GAP * 48000), np.float32)); t += GAP
        dub.append((t, t + len(a) / 48000)); pieces.append(a); t += len(a) / 48000
    end_pad = .6; pieces.append(np.zeros(int(end_pad * 48000), np.float32))
    y = np.concatenate(pieces)
    o = wave.open(f'{WORK}/vo2_{LANG}.wav', 'wb'); o.setnchannels(1); o.setsampwidth(2); o.setframerate(48000)
    o.writeframes(np.clip(y, -32768, 32767).astype(np.int16).tobytes()); o.close()
    for k, (a, b) in enumerate(dub): print(k, round(b - a, 2))
    print(LANG, 'raw', round(len(y) / 48000, 2), 's ->', round(len(y) / 48000 / TEMPO, 2), 's at tempo', TEMPO)
    json.dump({'dub': dub, 'en': en}, open(f'{WORK}/map2_{LANG}.json', 'w'), indent=0)
