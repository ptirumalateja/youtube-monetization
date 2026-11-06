#!/usr/bin/env python3
"""Hindi / Telugu dubs of Skeleton Lake V5, plus en/hi/te SRTs for every version.

Each script line is voiced separately (Viraj, eleven_v3) so its start and end are known. The dub VO keeps the
English pauses, and every English time (cut points, captions, SFX) is mapped onto the dub with a piecewise-linear
time map anchored at each line's start and end.

Usage: dub.py LANG EN_WORDS_JSON WORKDIR   (LANG = hi | te)
Writes WORKDIR/vo_LANG.wav, WORKDIR/cut_LANG.py (CUT / CAPS / MAPT for build4, captions4, mix4 via CUTMOD),
and WORKDIR/srt/*.srt."""
import json, os, subprocess, sys, urllib.request, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
VOICE, MODEL = 'tSVwqkJGEKjLklhiN0Nx', 'eleven_v3'      # Viraj - Deep, Resonant and Lyrical
TEMPO_EN = 1.08
# (English line, words in it, Hindi, Telugu). Tags only in the dub text; SRTs strip them.
SEG = [
 ("[whispers] Every summer, when the ice melts...", 6, "[whispers] हर गर्मी में, जब बर्फ़ पिघलती है...", "[whispers] ప్రతి వేసవిలో, మంచు కరిగినప్పుడు..."),
 ("this lake gives back its dead.", 6, "यह झील अपने मुर्दे लौटा देती है।", "ఈ సరస్సు తన మృతులను తిరిగి ఇచ్చేస్తుంది."),
 ("[slowly] Roopkund.", 1, "[slowly] रूपकुंड।", "[slowly] రూప్‌కుండ్."),
 ("Five thousand metres up in the Himalayas.", 7, "हिमालय में, पाँच हज़ार मीटर की ऊँचाई पर।", "హిమాలయాల్లో, ఐదు వేల మీటర్ల ఎత్తులో."),
 ("Hundreds of skeletons.", 3, "सैकड़ों कंकाल।", "వందల అస్థిపంజరాలు."),
 ("For decades, everyone believed they died together.", 7, "दशकों तक सब यही मानते रहे कि वे सब एक साथ मरे।", "దశాబ్దాల పాటు, వాళ్లంతా ఒకేసారి చనిపోయారని అందరూ నమ్మారు."),
 ("In one terrible night.", 4, "एक ही भयानक रात में।", "ఒకే ఒక భయంకరమైన రాత్రి."),
 ("[low] They didn't.", 2, "[low] ऐसा नहीं था।", "[low] కానీ అది నిజం కాదు."),
 ("Their DNA says one group died around 800 AD.", 9, "उनका DNA बताता है कि एक समूह की मौत करीब आठ सौ ईस्वी में हुई।", "వాళ్ల DNA ప్రకారం, ఒక గుంపు దాదాపు క్రీస్తు శకం ఎనిమిది వందలలో చనిపోయింది."),
 ("The other... around 1800.", 4, "और दूसरे की... करीब अठारह सौ में।", "మరొక గుంపు... దాదాపు పద్దెనిమిది వందలలో."),
 ("A thousand years apart.", 4, "हज़ार साल का फ़ासला।", "వెయ్యి సంవత్సరాల తేడా."),
 ("In the same frozen lake.", 5, "उसी जमी हुई झील में।", "అదే గడ్డకట్టిన సరస్సులో."),
 ("And the second group?", 4, "और दूसरा समूह?", "మరి ఆ రెండో గుంపు?"),
 ("Their closest match... is people from Greece and Crete.", 9, "उनका सबसे करीबी DNA मेल... ग्रीस और क्रीट के लोगों से है।", "వాళ్ల DNAకి అత్యంత దగ్గరి పోలిక... గ్రీస్, క్రీట్ ప్రజలతో."),
 ("[whispers] Some skulls are cracked.", 4, "[whispers] कुछ खोपड़ियाँ टूटी हुई हैं।", "[whispers] కొన్ని పుర్రెలు పగిలి ఉన్నాయి."),
 ("From above.", 2, "ऊपर से।", "పై నుంచి."),
 ("The villagers have a song for that.", 7, "गाँव वालों का इस पर एक लोकगीत है।", "దీని గురించి అక్కడి గ్రామస్తులకు ఒక పాట ఉంది."),
 ("A goddess.", 2, "एक देवी।", "ఒక దేవత."),
 ("Hail... as hard as iron.", 5, "ओले... लोहे जितने सख़्त।", "ఇనుమంత గట్టి... వడగళ్ళు."),
 ("[slowly] And every summer...", 3, "[slowly] और हर गर्मी में...", "[slowly] ప్రతి వేసవిలో..."),
 ("the ice gives back a little more.", 7, "बर्फ़ थोड़ा और लौटा देती है।", "మంచు ఇంకొంచెం బయటపెడుతుంది."),
 ("[whispers] Who were they?", 3, "[whispers] आख़िर वे कौन थे?", "[whispers] అసలు వాళ్లెవరు?"),
]
# on-screen captions: same slots as captions4.CAPS (English), localised
CAPS_L = {
 'hi': ["जब {Y}बर्फ़{W}\\Nपिघलती है...", "झील लौटा देती है\\Nअपने {Y}मुर्दे{W}", "{Y}रूपकुंड{W}", "{Y}5,000 मीटर{W} ऊपर", "{Y}हिमालय{W}",
        "{Y}सैकड़ों{W}\\Nकंकाल", "सबने\\Nमाना...", "सब {Y}एक साथ{W}\\Nमरे", "{Y}ऐसा नहीं था।{W}", "पहला समूह\\N{Y}~800 ईस्वी{W}",
        "दूसरा समूह\\N{Y}~1800{W}", "{Y}1,000 साल{W}\\Nका फ़ासला", "और दूसरा\\Nसमूह?", "सबसे करीबी\\NDNA मेल...", "{Y}ग्रीस{W} और {Y}क्रीट{W}",
        "खोपड़ियाँ\\N{Y}टूटी हुई{W}", "{Y}ऊपर{W} से", "गाँव का\\N{Y}लोकगीत{W}", "{Y}लोहे{W} जैसे\\Nओले", "हर गर्मी\\N{Y}कुछ और{W}",
        "आख़िर वे\\N{Y}कौन थे?{W}", "{\\pos(540,1470)\\fs60}आपकी थ्योरी? ↓"],
 'te': ["మంచు\\N{Y}కరిగినప్పుడు{W}...", "సరస్సు బయటపెడుతుంది\\N{Y}శవాలను{W}", "{Y}రూప్‌కుండ్{W}", "{Y}5,000 మీ.{W} ఎత్తు", "{Y}హిమాలయాలు{W}",
        "{Y}వందల{W}\\Nఅస్థిపంజరాలు", "అందరూ\\Nనమ్మారు...", "అంతా {Y}ఒకేసారి{W}\\Nచనిపోయారని", "{Y}కానీ కాదు.{W}", "మొదటి గుంపు\\N{Y}~క్రీ.శ. 800{W}",
        "రెండో గుంపు\\N{Y}~1800{W}", "{Y}1,000 ఏళ్ల{W}\\Nతేడా", "మరి రెండో\\Nగుంపు?", "అత్యంత దగ్గరి\\NDNA పోలిక...", "{Y}గ్రీస్{W}, {Y}క్రీట్{W}",
        "పుర్రెలు\\N{Y}పగిలి ఉన్నాయి{W}", "{Y}పై{W} నుంచి", "గ్రామస్తుల\\N{Y}పాట{W}", "{Y}ఇనుమంత{W} గట్టి\\Nవడగళ్ళు", "మంచు ఇంకొంచెం\\N{Y}బయటపెడుతుంది{W}",
        "అసలు వాళ్లు\\N{Y}ఎవరు?{W}", "{\\pos(540,1470)\\fs60}మీ థియరీ? ↓"],
}
strip = lambda s: ' '.join(w for w in s.split() if not (w.startswith('[') and w.endswith(']'))).strip()

def tts(text, out):
    if os.path.exists(out): return
    body = json.dumps({"text": text, "model_id": MODEL, "voice_settings": {"stability": 0.5, "similarity_boost": 0.75, "style": 0.3}}).encode()
    r = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}?output_format=mp3_44100_192", data=body,
                               headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"], "Content-Type": "application/json"})
    open(out, 'wb').write(urllib.request.urlopen(r, timeout=300).read())

def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-af',
                          'silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.03,areverse,'
                          'silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse',
                          '-ac', '1', '-ar', '48000', '-f', 's16le', '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32)
    # squeeze long pauses inside a line (v3 stretches "..." and [pause]) to MAXP seconds
    fr = 960; n = len(x) // fr
    rms = np.sqrt((x[:n*fr].reshape(n, fr) ** 2).mean(1) + 1e-9); quiet = 20 * np.log10(rms / 32768) < -42
    keep = np.ones(len(x), bool); run = 0; MAXP = 0.30
    for k in range(n + 1):
        if k < n and quiet[k]: run += 1; continue
        if run * fr / 48000 > MAXP:
            cut0 = (k - run) * fr + int(MAXP / 2 * 48000); cut1 = k * fr - int(MAXP / 2 * 48000); keep[cut0:cut1] = False
        run = 0
    return x[keep]

def en_segments(words):
    out, i = [], 0
    for s in SEG:
        ws = words[i:i + s[1]]; i += s[1]
        out.append((ws[0]['start'], ws[-1]['end']))
    assert i == len(words), (i, len(words))
    return out

def srt(path, rows):
    def t(x): h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60; return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s % 1) * 1000)) % 1000:03d}"
    with open(path, 'w') as f:
        for k, (a, b, txt) in enumerate(rows, 1): f.write(f"{k}\n{t(a)} --> {t(b)}\n{txt}\n\n")

def write_srts(work, tag, times):
    os.makedirs(f'{work}/srt', exist_ok=True)
    for li, lang in ((0, 'en'), (2, 'hi'), (3, 'te')):
        srt(f'{work}/srt/skeleton-lake-v5{tag}.{lang}.srt', [(a, b + 0.25, strip(s[li])) for (a, b), s in zip(times, SEG)])

if __name__ == '__main__':
    LANG, WORDS, WORK = sys.argv[1:4]
    os.makedirs(f'{WORK}/seg_{LANG}', exist_ok=True)
    en = en_segments(json.load(open(WORDS)))
    write_srts(WORK, '', [(a / TEMPO_EN, b / TEMPO_EN) for a, b in en])          # English version SRTs (en/hi/te)
    li = 2 if LANG == 'hi' else 3
    pieces, dub, t = [], [], 0.2
    pieces.append(np.zeros(int(.2 * 48000), np.float32))
    for k, s in enumerate(SEG):
        mp3 = f'{WORK}/seg_{LANG}/{k:02d}.mp3'; tts(s[li], mp3)
        a = load(mp3)
        if k:
            gap = min(max(en[k][0] - en[k - 1][1], 0.22), 0.85)
            pieces.append(np.zeros(int(gap * 48000), np.float32)); t += gap
        dub.append((t, t + len(a) / 48000)); pieces.append(a); t += len(a) / 48000
    end_pad = 0.7
    pieces.append(np.zeros(int(end_pad * 48000), np.float32))
    y = np.concatenate(pieces)
    o = wave.open(f'{WORK}/vo_{LANG}.wav', 'wb'); o.setnchannels(1); o.setsampwidth(2); o.setframerate(48000)
    o.writeframes(np.clip(y, -32768, 32767).astype(np.int16).tobytes()); o.close()
    # anchors English tight-VO time -> dub time
    anc = [(0.0, 0.0)]
    for (ea, eb), (da, db) in zip(en, dub): anc += [(ea, da), (eb, db)]
    anc.append((50.30, dub[-1][1] + end_pad + 0.1))
    TEMPO_DUB = float(os.environ.get('TEMPO', '1.08'))         # the dub is played at this tempo in mix4
    write_srts(WORK, f'-{LANG}', [(a / TEMPO_DUB, b / TEMPO_DUB) for a, b in dub])
    json.dump({'en': en, 'dub': dub, 'anchors': anc}, open(f'{WORK}/map_{LANG}.json', 'w'), indent=0)
    with open(f'{WORK}/cut_{LANG}.py', 'w') as f:
        f.write(f"""import sys, numpy as np
sys.path.insert(0, {HERE!r})
import caps_en as _c
ANC = {anc!r}
_x = [a for a, _ in ANC]; _y = [b for _, b in ANC]
MAPT = lambda t: float(np.interp(t, _x, _y))
CAPS_TXT = {CAPS_L[LANG]!r}
CAPS = [(MAPT(a), MAPT(b), txt) for (a, b, _), txt in zip(_c.CAPS, CAPS_TXT)]
""")
    print(LANG, 'dub length', round(len(y) / 48000, 2), 's; English', 50.3)
