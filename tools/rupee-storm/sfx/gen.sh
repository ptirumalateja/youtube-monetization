#!/bin/bash
# ElevenLabs foley for mix.py. Needs ELEVENLABS_API_KEY.
cd "$(dirname "$0")"
gen(){ n=$1; d=$2; p="$3"; [ -s $n.mp3 ] && [ -z "$FORCE" ] && return; for i in 1 2 3; do curl -sS -o $n.mp3 -X POST https://api.elevenlabs.io/v1/sound-generation -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" -d "{\"text\":\"$p\",\"duration_seconds\":$d,\"prompt_influence\":0.7}"; [ $(stat -c%s $n.mp3) -gt 2000 ] && break; sleep 4; done; echo $n $(stat -c%s $n.mp3); }
gen coin 0.5 "A single metal coin dropping onto a stack of coins, one bright clink, close, no music"
gen bundle 0.6 "A thick bundle of paper banknotes slapped down onto a stack of cash, crisp thud and paper flutter, close, no music"
gen riffle 1.0 "Banknotes being riffled quickly by thumb, crisp paper flutter, close, no music"
gen cash 1.2 "A huge pile of cash and coins crashing down onto a table, loud impactful money slam, no music"
gen heart 3 "Slow heavy heartbeat, deep thumps, tense, silent background, no music"
gen boom 1.5 "A massive deep cinematic boom impact with a sub bass hit, no music"
gen rise 1.2 "A fast rising whoosh building up into an impact, cinematic, no music"
gen room 6 "Very quiet empty large room tone with faint distant hum, no music"
# v2 notification-storm sounds
gen ping 0.5 "A short bright smartphone payment received notification chime, two quick rising tones, clean digital, no music"
gen buzz 0.5 "A smartphone vibrating once on a wooden table, short buzz, close, no music"
gen stamp 0.5 "A heavy rubber stamp slammed onto paper on a desk, one punchy thunk, close, no music"
gen crack 1.0 "A smartphone glass screen cracking sharply, crisp glass crack, no music"
gen shatter 1.5 "A glass screen shattering into pieces that fly apart, bright glass explosion, no music"
gen whoosh 0.6 "A fast short air whoosh swipe transition, clean, no music"
gen scratch 0.6 "A short vinyl record scratch, comedic stop, no music"
gen ooh 1.5 "A small crowd of people going ooooh in surprise, amazed, no music"
gen chime 2.0 "A big bright cash register ka-ching followed by shimmering coins, celebratory, no music"
gen beat 8 "Energetic upbeat Indian dhol and tabla percussion groove loop, punchy, steady 120 bpm, driving rhythm, no melody, no vocals"
gen beat2 8 "Tense fast ticking percussion with deep pulsing bass, building suspense rhythm loop, steady 120 bpm, no melody, no vocals"
