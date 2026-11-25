#!/bin/bash
# Regenerates the ElevenLabs sound effects used by mix.py (POST /v1/sound-generation). Needs an ElevenLabs key:
# ELEVENLABS_API_KEY, or a key injected by the session's network proxy (then any placeholder value works). One request at a time.
cd "$(dirname "$0")"
KEY="${ELEVENLABS_API_KEY:-proxy-injected}"
gen(){ n=$1; d=$2; p="$3"; [ -s $n.mp3 ] && [ -z "$FORCE" ] && return; for i in 1 2 3; do curl -sS -o $n.mp3 -X POST https://api.elevenlabs.io/v1/sound-generation -H "xi-api-key: $KEY" -H "Content-Type: application/json" -d "{\"text\":\"$p\",\"duration_seconds\":$d,\"prompt_influence\":0.7}"; [ $(stat -c%s $n.mp3) -gt 2000 ] && break; sleep 4; done; echo "$n $(stat -c%s $n.mp3)"; }
gen strain 3.5 "A man straining under a very heavy load, slow labored breathing and low grunts, no words, close, no music"
gen steps_heavy 3.5 "Slow heavy footsteps trudging up a steep gravel hill, feet sliding a little, close, no music"
gen slide 1.2 "Feet slipping and sliding backwards down loose gravel, a scrape and a stumble, no music"
gen sack_drop 1.0 "A heavy burlap sack full of rocks dropped onto gravel ground, one deep thud and rocks clunking inside, no music"
gen rummage 1.0 "A hand reaching into a burlap sack and pulling out a rock, rough cloth rustle and a stone clink, close, no music"
gen throw 0.7 "A heavy rock thrown hard through the air, one short whoosh, no music"
gen roll 3.5 "A large rock hitting a steep gravel slope and tumbling and rolling far down the hill, heavy thuds fading away, no music"
gen exhale 1.6 "A man letting out a long deep relieved breath, no words, close, no music"
gen steps_light 3.0 "Light quick confident footsteps walking briskly up a gravel slope, close, no music"
gen arrive 3.5 "A soft warm cinematic swell of light, gentle shimmering rise and glow, calm, no drums, no music melody"
gen boom 3.0 "A single deep cinematic low boom hit with a long dark tail, no music"
gen shimmer 4.0 "A radiant bright ethereal shimmer swelling up, soft airy choir-like glow and gentle high sparkles, calm and uplifting, no drums, no music melody"
gen flag 4.0 "A cloth flag flapping softly in a gentle wind on a hilltop, close, no music"
gen slide_long 1.4 "A man losing his footing and sliding all the way down a steep gravel slope, a long scrape and stones skittering, no music"
