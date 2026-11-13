#!/bin/bash
# Extra ElevenLabs foley for Sorry Is 5 Letters (the rest is copied from tools/silence-distance/sfx). Needs ELEVENLABS_API_KEY.
cd "$(dirname "$0")"
gen(){ n=$1; d=$2; p="$3"; [ -s $n.mp3 ] && [ -z "$FORCE" ] && return; for i in 1 2 3; do curl -sS -o $n.mp3 -X POST https://api.elevenlabs.io/v1/sound-generation -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" -d "{\"text\":\"$p\",\"duration_seconds\":$d,\"prompt_influence\":0.7}"; [ $(stat -c%s $n.mp3) -gt 2000 ] && break; sleep 4; done; echo $n $(stat -c%s $n.mp3); }
gen slam 1.6 "A huge heavy stone block slamming down onto a stone floor, deep cinematic boom impact with a low rumble tail, no music"
gen thud 1.0 "A heavy stone block dropping a short distance onto stone, one deep dull thud, close, dry, no music"
gen crack 1.0 "Stone floor cracking under heavy weight, sharp brittle crack with small crumbling debris, close-up, no music"
gen creak 1.0 "Low strained creak of a heavy stone weight pressing down, tense groan, very short, no music"
gen rewind 0.6 "Fast tape rewind zip, short reverse whoosh, no music"
gen release 1.5 "Heavy weight lifting away, a soft airy release whoosh rising upward with a light shimmer, no music"
gen sub 1.5 "A massive deep sub bass impact boom, cinematic trailer hit, very low and heavy, short tail, no music"
