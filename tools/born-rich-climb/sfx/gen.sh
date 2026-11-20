#!/bin/bash
# ElevenLabs foley for the Born Rich climb reel. Needs ELEVENLABS_API_KEY. hammer*/step*/plank_grab come from tools/climb.
cd "$(dirname "$0")"
gen(){ n=$1; d=$2; p="$3"; [ -s $n.mp3 ] && return; for i in 1 2 3; do curl -sS -o $n.mp3 -X POST https://api.elevenlabs.io/v1/sound-generation -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" -d "{\"text\":\"$p\",\"duration_seconds\":$d,\"prompt_influence\":0.7}"; [ $(stat -c%s $n.mp3) -gt 2000 ] && break; rm -f $n.mp3; sleep 4; done; }
gen rung 0.6 "A wooden ladder rung slapped into place against two wooden rails, one quick dry wood knock, close-up foley, no music" &
gen rope 0.7 "A rope pulled tight around a wooden pole, a quick rope cinch and creak, close-up foley, no music" &
gen level_ding 0.8 "One tiny bright satisfying metal ding, small precise bell tap, no music" &
gen heli_far 4.5 "A helicopter approaching from far away, rotor thumping growing louder and closer, outdoors, no music" &
gen heli_land 5.0 "A helicopter landing very close overhead, loud rotor wash, strong gust of wind and blowing dust, no music" &
gen wood_snap 1.5 "A tall wooden ladder snapping apart, loud wood crack and splintering, planks breaking, no music" &
wait
gen tumble 1.0 "A person tumbling through the air, a fast rush of air whoosh, no music, no voice" &
gen thud 0.8 "A body falling flat onto sandy dirt ground, one heavy dull thud with a puff of sand, no music, no voice" &
gen planks_rain 2.2 "Many loose wooden planks clattering and bouncing onto dirt ground one after another, no music" &
gen dizzy 2.0 "Cartoon dizzy tweeting little birds circling after a knockout, playful, short" &
gen door_slam 1.2 "A heavy wooden door slams shut hard, deep thud and a metal latch click, no music" &
gen glint 0.6 "A short bright sparkle twinkle, one quick shimmering ding, no music" &
wait
