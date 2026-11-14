#!/bin/bash
# ElevenLabs foley for mix.py. Needs ELEVENLABS_API_KEY. One request at a time.
cd "$(dirname "$0")"
gen(){ n=$1; d=$2; p="$3"; [ -s $n.mp3 ] && [ -z "$FORCE" ] && return; for i in 1 2 3; do curl -sS -o $n.mp3 -X POST https://api.elevenlabs.io/v1/sound-generation -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" -d "{\"text\":\"$p\",\"duration_seconds\":$d,\"prompt_influence\":0.7}"; [ $(stat -c%s $n.mp3) -gt 2000 ] && break; sleep 4; done; echo $n $(stat -c%s $n.mp3); }
gen rain 11 "Steady soft rain falling on a quiet park at night, drops on a wooden bench and wet pavement, gentle and melancholic, no thunder, no music"
gen thunder 4 "One deep distant thunder rumble rolling slowly across the sky, cinematic low boom, no rain, no music"
gen wetstep 0.6 "A single footstep on wet pavement with a small splash, sneaker, close-up, no music"
gen creak 1.2 "A person sitting down on an old wooden park bench, soft wooden creak and a little rain splash, close-up, no music"
gen lean 1.5 "Soft rustle of a wet jacket as a friend puts an arm around someone's shoulders, gentle, intimate, close-up, no music"
gen exhale 1.5 "A quiet shaky exhale of relief from a sad person, soft breath, very close, no words, no music"
