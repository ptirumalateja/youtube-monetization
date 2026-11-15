#!/bin/bash
# ElevenLabs foley for mix.py. Needs ELEVENLABS_API_KEY.
cd "$(dirname "$0")"
gen(){ n=$1; d=$2; p="$3"; [ -s $n.mp3 ] && [ -z "$FORCE" ] && return; for i in 1 2 3; do curl -sS -o $n.mp3 -X POST https://api.elevenlabs.io/v1/sound-generation -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" -d "{\"text\":\"$p\",\"duration_seconds\":$d,\"prompt_influence\":0.7}"; [ $(stat -c%s $n.mp3) -gt 2000 ] && break; sleep 4; done; echo $n $(stat -c%s $n.mp3); }
gen swipe 0.8 "A quick paper page whoosh swipe, soft, no music" &
gen paws 0.6 "Single soft dog paw step on a stone floor, light click of claws, no music" &
gen pop 1.0 "A sudden eerie shimmering glass reveal, many mirrors flashing at once, short, no music" &
gen growl 1.6 "One dog growling low and threatening, close-up, no music" &
gen growls 2.2 "Hundreds of dogs growling back at once, echoing in a stone hall, menacing, no music" &
gen snarls 1.8 "A huge echoing crowd of dogs snarling and baring teeth, layered, no music" &
wait
gen glass 0.9 "A dog slamming into a mirror, glass thump and crack, no music" &
gen bark 0.7 "One angry dog bark echoing in a stone hall, no music" &
gen clock 3 "A clock ticking fast in an empty stone hall at night, no music" &
gen thud 1.2 "A tired dog collapsing onto a stone floor, soft heavy thud, no music" &
gen whimper 1.4 "A dog's faint exhausted whimper fading out, no music" &
gen birds 3 "Gentle morning birdsong outside a quiet temple, soft, no music" &
wait
gen wag 1.5 "A happy dog panting softly and its tail thumping, playful, no music" &
gen chime 1.6 "Warm bright magical chime shimmer, many soft bells at once, no music" &
gen marker 1.0 "A thick marker pen writing quickly on paper, squeak, no music" &
gen ding 0.8 "A smartphone message notification ding, single, no music" &
gen frost 1.2 "Ice crackling and freezing quickly, cold crisp crackle, no music" &
gen boom 1.4 "A cartoon fight cloud burst, angry punchy boom and scuffle, no music" &
wait
gen room 8 "Quiet empty stone temple hall room tone, faint air, very soft, no music" &
wait
