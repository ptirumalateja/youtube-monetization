"""Free narration with Kokoro (open-source TTS, runs locally) after the ElevenLabs quota ran out.
python3 kokoro_vo.py [beat ...] -> vo_kokoro/<beat>.wav
Every beat already recorded with ElevenLabs (vo_eleven/<beat>.wav) is time-stretched to that take's length, so the
new voice keeps the old pace and the picture timeline doesn't move. New beats use Kokoro's natural pace.
Model files: github.com/thewh1teagle/kokoro-onnx releases, tag model-files-v1.0, in $KOKORO_DIR (default ~/kokoro)."""
import os, re, sys, subprocess, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
sys.path.insert(0, 'subs')
from cues import CUES
from timeline import ORDER
KD = os.environ.get('KOKORO_DIR', os.path.expanduser('~/kokoro'))
VOICE, SPEED = 'am_michael', .92     # closest to the ElevenLabs voice in pitch (median f0 116 vs 114 Hz) and brightness

TEXT = {k: ' '.join(c[0] for c in CUES[k]) for k in CUES}
TEXT['b03s'] = ' '.join(c[0] for c in CUES['b03'][:-1])          # last sentence was cut in v2
for m in re.finditer(r'\*\*([hc]\d\d) \(new[^)]*\)\*\* (.+)', open('script_v2.md').read()):
    TEXT[m.group(1)] = m.group(2).strip()

# spell things the way they are said
SAY = [('F/A-18F', 'F A eighteen F'), ('USS ', 'U S S '), ('AARO', 'Arrow'), ('FLIR1', 'Fleer one'), ('Fravor', 'Frayvor'),
       ('Slaight', 'Slate'), ('2004', 'two thousand four'), ('2015', 'twenty fifteen'), ('2025', 'twenty twenty-five'),
       ('2026', 'twenty twenty-six'), ('757', 'seven hundred and fifty-seven'), ('UFO', 'U F O'), ('Tic Tac', 'Tick Tack'),
       ('...', ', ,')]
def say(s):
    for a, b in SAY: s = s.replace(a, b)
    return s

def dur(p):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p],
                                capture_output=True, text=True).stdout)

if __name__ == '__main__':
    k_ = Kokoro(f'{KD}/kokoro-v1.0.onnx', f'{KD}/voices-v1.0.bin')
    os.makedirs('vo_kokoro', exist_ok=True)
    beats = sys.argv[1:] or [k for k, _ in ORDER]
    for k in beats:
        a, sr = k_.create(say(TEXT[k]), voice=VOICE, speed=SPEED, lang='en-us')
        sf.write('/tmp/kk_raw.wav', a, sr)
        # trim edges, warm low end, gentle compression, 48 kHz like the rest of the mix
        chain = 'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,' \
                'equalizer=f=140:t=q:w=1:g=2.5,equalizer=f=5500:t=q:w=1.5:g=-1.5,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120'
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', '/tmp/kk_raw.wav', '-af', chain, '-ar', '48000', '/tmp/kk_t.wav'], check=True)
        d = dur('/tmp/kk_t.wav'); ref = f'vo_eleven/{k}.wav'
        tempo = 1.0
        if os.path.exists(ref):
            tempo = min(max(d / dur(ref), .8), 1.25)
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', '/tmp/kk_t.wav', '-af', f'atempo={tempo:.4f}', f'vo_kokoro/{k}.wav'], check=True)
        print(f'{k:5s} kokoro {d:5.2f}s  tempo {tempo:.3f}  -> {dur(f"vo_kokoro/{k}.wav"):5.2f}s' +
              (f'  (eleven {dur(ref):5.2f}s)' if os.path.exists(ref) else '  (new)'), flush=True)
