# Abhimanyu v7: the Epic Redesign

## Design statement
**Cinematic Indian epic realism**: larger-than-life characters and monumental environments, grounded by tactile materials, atmospheric dust, natural light and believable ancient-world detail. Heroic and mythic in scale, but never fantasy-game, superhero or CGI spectacle.

- The old design (v6) gives the **production discipline**: faceless hero, master sets, one story object, camera-only motion, frame-exact edit.
- The new design gives the **Mahabharata soul**: elephants, ornate chariots, dhvaja banners, gold, silk, a prince.

## What carries over from v6 (unchanged)
- Narration: take C (Teja Clone, `edit_v6/narration.mp3`), word timings, captions, score, sound effects, and the shot timing in `edit_v6/cuts.json`. Only the picture is replaced.
- **Faceless hero:** Abhimanyu is always seen from behind or as hands and details. His identifiers are the deep indigo silk angavastram with a gold border, gold armlets, dark curls and gold kundala earrings.
- **The story object is still "the opening":** a narrow gap of golden light in a living wall, open in Shot 1, breached in 11, closed in 12, sealed in 21.
- **Master sets first;** every shot is derived from a master.
- **No fighting on camera:** motion is camera, dust, cloth, banners, light and objects.

## What changes (the "not 300" rules)
| v6 (reads as "300") | v7 (reads as Mahabharata) |
|---|---|
| Wall of round bronze hoplite shields | A living wall of armoured war elephants in crimson-and-gold caparisons, ornate chariots and tall dhvaja banners |
| Crimson cloaks, crested helmets | Silk angavastrams, dhotis, engraved kavacha breastplates, crowns, no capes |
| Cold teal grade, grey sky | Natural golden-hour light that **fades to dusk** across the story |
| Lean, battered youth | A young prince, larger than life: tall, strong, adorned |
| Bare sand | Kurukshetra as a plain of thousands: banners, chariots, elephants to the horizon |

## Light arc (fixes "too orange")
Not every frame is orange. Light carries the story:
1. **Shots 1–11, golden afternoon.** Warm sunlight, a pale blue haze kept in the upper sky, rich colour, long shadows.
2. **Shots 12–13, the light breaks.** The sun goes behind the dust: amber but darker, with contrast.
3. **Shots 14–19, dusk.** Deep amber and smoke; the sun is low and partly hidden; silhouettes.
4. **Shots 20–21, after.** Blue-violet twilight, a last ember on the horizon, the indigo silk the only strong colour.

## Composition rules (fixes "too centred")
- Use rule-of-thirds or diagonal placement. The hero sits on a third line, never dead centre, except Shot 2 and Shot 14, where the centre is the point (the trap).
- No sun starbursts and no symmetrical god-ray fans. Light comes from the side or behind the formation, the sun disc is mostly hidden by dust or the formation, and its rays are soft.
- Every frame has real foreground depth: a spear shaft, a banner edge, an elephant's flank, dust.
- **Caption-safe:** keep key action out of the bottom 20% and the right-hand 12%.

## Palette
Saffron, gold and deep crimson for the world; **indigo for Abhimanyu only**; natural sky blue-haze at the top of golden frames; smoke grey-brown at dusk. Teal is neutralised in grading (`scripts/grade_epic.py`).

## Master sets
- **M1 The Opening:** extreme low angle into a living wall of two colossal war elephants and chariots, with a narrow gap of golden light between them. Off-centre gap.
- **M2 The Vyuha:** high aerial of the spiral formation of chariots, elephants, cavalry and banners coiling into an empty sand circle.
- **M3 The Sand:** a patch of dusty ground at golden light for the hand-drawn spiral; his hand wears a gold armlet and an indigo silk edge.
- **M4 The Prince:** waist-up from behind, off-centre: indigo angavastram with a gold border, kavacha, armlets, kundalas, curls, bow and peacock-feather quiver.
- **M5 The Wheel:** a massive ornate chariot wheel with a gold-plated rim and carved spokes.

## Storyboard
| # | Line | Master | Frame | Light | Motion |
|---|---|---|---|---|---|
| 1 | He knew how to get in. | M1 | Ground-level into the elephant wall; one narrow gap of golden light, dust in the beam | golden | Slow push toward the gap |
| 2 | He didn't know how to get out. | M2 | High aerial of the spiral; one tiny indigo figure in the empty centre | golden | Slow rise |
| 3 | So why did the Pandavas send Abhimanyu into the Chakravyuha? | M4 | The prince from behind, off-centre, facing the formation on the horizon | golden | Push over his shoulder; silk moves |
| 4 | Because on that day... Arjuna was away. | none | Arjuna's empty ornate chariot with the monkey-emblem kapidhvaja banner furled; a far dust trail leaving | golden | Lateral drift; banner stirs |
| 5 | And Drona had formed a battle array the Pandavas couldn't break. | M2 | Lower aerial across the rings: elephants, chariots, a white banner with a golden altar emblem at the centre | golden | Forward drift across the rings |
| 6 | Abhimanyu knew how to breach it. | M3 | Macro: his fingertip (gold armlet, indigo silk) draws a spiral in the sand and cuts a line into it | golden | Static macro |
| 7 | But he admitted... he didn't know how to escape. | M3 | Same spiral: the line stops at the centre; the hand lifts and hesitates | golden | Slow push |
| 8 | Still, Yudhishthira told him to break the formation... | M4 | Over his shoulder: an older royal hand with gold rings and white silk points to the formation | golden | Slow push |
| 9 | and promised the others would follow. | M4 | Behind him, rows of Pandava chariots, elephants and banners raised (the army at his back) | golden | Slow pull back |
| 10 | Abhimanyu charged. | none | Ground level: an ornate gold chariot wheel and horse hooves blasting dust at the lens | golden | Fast |
| 11 | He broke through. | M1 | Same gap: the wall splits, golden light floods out, a chariot silhouette drives into it | golden | Fast push into the light |
| 12 | Then the opening closed. | M1 | From inside: elephants and chariots close the gap; the gold line narrows to nothing | light breaks | Gap closes; light snaps out |
| 13 | Jayadratha stopped the Pandavas from following. | M1 | Outside the sealed wall: a crowned commander from behind in silver and crimson silk (no cape), a silver boar banner; Pandava chariots halted | light breaks | Slow push; banner ripples |
| 14 | Abhimanyu was alone. | M2 | Top-down: the indigo figure in the empty sand circle, ringed by elephants and chariots | dusk | Very slow rise; silence |
| 15 | His bow was destroyed. | none | Macro: an ornate gold-inlaid bow snapping in his hands (indigo silk, armlet) | dusk | Snap, then slow motion |
| 16 | His chariot was wrecked. | M5 | Ground level: an overturned ornate chariot, its gold wheel spinning to a stop | dusk | Wheel slows |
| 17 | His sword was gone. | none | A broken engraved sword in the dust beside his open palm (gold armlet) | dusk | Static; dust settles |
| 18a | So he picked up... | M5 + M4 | From behind and low: both hands grip the gold rim of the wheel in the dust | dusk | Slow push |
| 18b | ...a chariot wheel... | M5 + M4 | The wheel rises upright into frame, huge against the dusk | dusk | Wheel lifts |
| 19 | and kept fighting. | M4 + M5 | From behind, off-centre: the colossal wheel raised overhead against the low hidden sun, spears and banners closing in | dusk | Slow push; spears close |
| 20 | But that was the tragedy. | M5 | The wheel lying in dust in twilight, the indigo silk caught on a spoke, fluttering | twilight | Static; only the silk moves |
| 21 | He was never supposed to be alone. | M1 | Same composition as Shot 1: the elephant wall fully sealed, no light; far behind, the Pandava banners stand waiting | twilight | Slow pull back; hold |

## Production plan
1. Masters M1–M5 in the new look (Qwen 2511, fast drafts, then full quality on the picks). **Review checkpoint with Teja.**
2. Derive all 22 frames from the masters, grade with `grade_epic.py`, contact sheet. **Review checkpoint.**
3. Wan 2.2 motion for each frame (the same camera-only prompts as v6).
4. Rebuild with `edit_v6/build_short.py` using the same narration and cuts, then release v7.
