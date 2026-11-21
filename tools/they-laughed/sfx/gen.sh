#!/bin/bash
# ElevenLabs foley for the They Laughed reel. Needs ELEVENLABS_API_KEY. dizzy/thud/tumble/step*/glint reused from tools/born-rich-climb.
cd "$(dirname "$0")"
gen(){ n=$1; d=$2; p="$3"; [ -s $n.mp3 ] && return; for i in 1 2 3; do curl -sS -o $n.mp3 -X POST https://api.elevenlabs.io/v1/sound-generation -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" -d "{\"text\":\"$p\",\"duration_seconds\":$d,\"prompt_influence\":0.7}"; [ $(stat -c%s $n.mp3) -gt 2000 ] && break; rm -f $n.mp3; sleep 4; done; }
gen laugh 3.0 "A small group of people laughing mockingly and jeering at someone, outdoors, no music" &
gen laugh2 3.0 "A crowd of people bursting into loud mocking laughter, pointing and teasing, outdoors, no music" &
gen grip 0.5 "A hand gripping a rough rock ledge, short gritty scrape of fingers on stone, close-up foley, no music" &
gen pebbles 1.5 "A climber's foot slips on a cliff, small rocks and pebbles crumbling and falling away, no music" &
gen gasp 1.0 "A small crowd gasping in surprise together, short, no music" &
gen wind 6.0 "High mountain wind blowing steadily on a cliff top, cold airy gusts, no music" &
wait
gen applause 3.0 "A small crowd of people clapping and applauding politely, outdoors, no music" &
gen lift 1.2 "A heavy stone boulder scraping and lifting off rocky ground with a deep strained human grunt, no music" &
gen whoosh 1.0 "A huge heavy boulder flying fast through the air, deep rushing whoosh, no music" &
gen smash 2.0 "A giant boulder crashing down hard onto rocky ground, massive heavy impact with rock debris scattering and dust, no music" &
gen groan 1.6 "A crowd of people groaning in pain after being knocked over, cartoon style, short, no music" &
gen dust 1.0 "Someone dusting off their hands, two quick claps of dusty palms, close-up foley, no music" &
wait
