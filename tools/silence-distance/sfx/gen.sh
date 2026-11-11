#!/bin/bash
# Regenerates the ElevenLabs foley used by mix.py. Needs ELEVENLABS_API_KEY. One request at a time.
cd "$(dirname "$0")"
gen(){ n=$1; d=$2; p="$3"; [ -s $n.mp3 ] && [ -z "$FORCE" ] && return; for i in 1 2 3; do curl -sS -o $n.mp3 -X POST https://api.elevenlabs.io/v1/sound-generation -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" -d "{\"text\":\"$p\",\"duration_seconds\":$d,\"prompt_influence\":0.7}"; [ $(stat -c%s $n.mp3) -gt 2000 ] && break; sleep 4; done; echo $n $(stat -c%s $n.mp3); }
gen type 1.2 "Soft quick thumb taps typing on a smartphone glass screen, gentle tiny clicks, close-up, quiet room, no music"
gen erase 0.8 "A few soft rapid smartphone backspace key taps deleting a message, tiny dry clicks, close-up, no music"
gen send 0.7 "A soft airy message sent swoosh from a phone, short gentle whoosh upward, clean, no music"
gen ping 0.8 "A soft warm gentle phone message received chime, one short bell-like ding, clean, no music"
gen brick1 0.5 "One small glass tile clicking into place, soft satisfying crisp click with a tiny shimmer, close-up, dry, no music"
gen brick2 0.5 "A small ceramic block snapping into place, one short bright click, close-up, dry, no music"
gen step 0.5 "A single soft footstep on a smooth hard tile floor, light sneaker step, close-up, dry, no music"
gen rise 0.8 "A person standing up from sitting on the floor, soft clothing rustle, quiet, close-up, no music"
gen swell 3.5 "A warm soft shimmering swell of light, gentle airy rising chime pad that blooms and fades, cinematic, no voice"
gen wind 8 "Lonely cold night wind blowing softly over an empty cliff, hollow distant air, very quiet and sparse, no music"
gen whoosh 1.0 "A slow soft cinematic camera push in whoosh, airy low swell, no music"
gen pullback 1.2 "A soft cinematic pull back whoosh receding into distance, airy, low, no music"
