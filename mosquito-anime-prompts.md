# Mosquito Reel v2 (anime look): Flow prompts

Style references: the two owner stills (swarm over meadow at dusk; calm meadow at dusk with a lit hut and palm).
Same timeline, overlay and mix scripts as v1 (`tools/mosquito/edit/`). Wordless, ~32 s, loops.

## Style lock (paste at the start of every prompt)
"Cinematic hand-painted anime film look, Studio Ghibli-inspired backgrounds, soft cel shading, warm amber and rose dusk light, deep teal shadows, drifting golden light motes, subtle film grain, vertical 9:16, smooth natural motion. No text, no captions, no letters, no logos, no watermark, no UI, no blue plasma or electric glow, no music, no speech."

## Anatomy lock (any shot with a mosquito)
"Aedes mosquito: slim body, black with white stripes on the abdomen and white bands on the long thin legs, one long straight proboscis, two narrow clear wings, feathery antennae. Never a fly, never a bee."

## O1 - Meadow vanish (5 s). Start frame = swarm still (image 1)
"[Style lock] Locked camera, very slow push-in on a village meadow at sunset with a thatched hut and palm tree. Thousands of small black mosquitoes fill the sky and grass, with one large hero mosquito in front. Quietly, starting from the hero and rippling outward, every mosquito softens into a warm golden light mote and drifts up and away like embers. No explosion, no flash. By the end the sky and grass are completely empty and calm, only fireflies-like golden motes remain. [Anatomy lock]"
Last frame must be an EMPTY meadow (no insects in the grass); use the calm-meadow still with the grass mosquitoes painted out if the model leaves any behind.

## O2 - Clouds to Earth (4 s). Start frame = last frame of O1
"[Style lock] The camera lifts smoothly up from the empty sunset meadow, rises through a soft layer of warm clouds, keeps rising past the sky into space, and ends on the whole Earth floating in a black star field with a thin warm amber atmosphere rim and visible city lights on the night side. Continuous single move, calm and awe-filled. No glowing shield, no blue energy rings, no text."

## Shots after the globe (generate 2 variants each)

### T - Arctic tundra (5 s, then used again as T2)
"[Style lock] Cool pastel tundra at dusk, shallow pools, white cotton grass, about thirty caribou grazing peacefully, rose-lilac sky. Slow gentle camera drift forward. The air is clear and still, no insects."

### T2 - Tundra, ten years later (4 s). Start frame = last frame of T
"[Style lock] The same tundra plain ten years later at dusk, caribou still grazing, a thin drifting haze of tiny non-biting midges rising from the pools, golden in the low light. Slow forward drift. No mosquitoes."

### H - Heron (3.5 s)
"[Style lock] A grey heron standing in still wetland water at sunset, reeds in the foreground, reflections. It snaps its beak at empty air and tilts its head, finding nothing, then looks around calmly. Clear air, no insects. Shallow depth of field."

### F - Underwater (3 s)
"[Style lock] Calm pond seen from just below the surface, sunbeams through teal-green water, small fish feeding among tiny aquatic insects and drifting plants. Slow gentle drift."

### C - Bog orchid (3.6 s)
"[Style lock] Close-up of a slender wild bog orchid (blunt-leaf orchid) with a spike of tiny pale green-white flowers and one blunt basal leaf, in a damp northern bog at dusk, soft teal background. One mosquito hovers in front of the flowers, then softens into a golden light mote and drifts away, leaving the orchid alone. Locked camera, shallow depth of field. [Anatomy lock]"

### E - Earth sunrise (4 s)
"[Style lock] Earth from space, slow pull-back as the sun rises over the horizon with a warm amber rim, soft atmosphere glow, city lights on the night side, black star field. Calm, no overlays, no blue shield."

### L - Loop mosquito (2.5 s)
"[Style lock] Single mosquito hovering facing the camera against a dark warm-brown dusk background, wings blurring, slowly descending and landing on bare skin, legs touching down, about to bite. Shallow depth of field, slight push-in. [Anatomy lock]"

## Kept from v1 (no regeneration)
Designed data globe (WHO Africa region, `land.json`), black beat before the globe, all overlay text, chips and sound. Globe sits between O2 and T; add a dusk grade so it matches.

## Review checklist per clip
No baked text or sparkle; striped Aedes legs; no blue plasma; calm vanish (no flash); last frame of a clip equals the first frame of the next where the table says so.
