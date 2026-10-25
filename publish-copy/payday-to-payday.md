# Payday to Payday (Slow Light Dark)

| | |
|---|---|
| Status | Rendered, pending the owner's OK |
| Upload file | `payday-to-payday.mp4` (silent cut for your own music: `payday-to-payday_music-ready.mp4`, hit at 8.45 s) |
| Length | 18.0 s, 1080x1920, 30 fps, loops |
| Voice | None (wordless; plain on-screen text) |
| Build | `tools/payday-to-payday/` (three.js, PIL, numpy, ffmpeg) |

## Publish copy

**YouTube Shorts title:** ₹50,000 Came In. By Day 3 It Was Gone. #shorts

**YouTube description:**
> Payday: ₹50,000 in. Rent, EMI, food, mom, friends, and by day 3 the wallet is empty with 27 days still to go.
> A Slow Light story about living payday to payday. The numbers are made up for the story and add up exactly: 18,000 + 12,000 + 9,000 + 6,000 + 5,000 = 50,000.
>
> Made entirely in code (three.js, rendered frame by frame). Sound is synthesised, plus two CC0 Freesound files (sleepCircle, qubodup).
>
> #payday #salary #emi #middleclass #india #stickman #shorts

**Instagram / Facebook caption:**
> Payday: ₹50,000 in. 💸
> Rent took ₹18,000. EMI took ₹12,000. Food, mom, friends took the rest.
> Day 3. Wallet empty. 27 days to go.
> He still has the same smile for the next payday.
> Who in your circle is already counting the days? Tag them. 👇
> #payday #salary #emi #middleclass #stickman #reels

**Pinned comment:** How many days does your salary last? Be honest. 👇

**Hashtags:** #shorts #payday #salary #emi #middleclass #india #stickman #slowlight

**Sound credit line (optional courtesy):** CC0 sounds by sleepCircle and qubodup via Freesound. All other sound is synthesised for this reel; no credit required.

**Upload settings:** 9:16, AI/synthetic media label on (synthetic scene), no music claimed.

## Facts and sources

| On screen | Value | Source / check |
|---|---|---|
| PAYDAY: ₹50,000 IN. | A made-up monthly take-home salary | Story figure, not a statistic. The description says the numbers are invented for the story. |
| RENT −₹18,000, EMI −₹12,000, FOOD −₹9,000, MOM −₹6,000, FRIENDS −₹5,000 | 18,000 + 12,000 + 9,000 + 6,000 + 5,000 = 50,000 | Arithmetic; checked in code (`overlay.py check`: the balance rises to exactly 50,000, then falls to exactly 0). |
| Balance counter | Rises only while the five bundles land (0 → 50,000), falls only while they are taken (50,000 → 0) | Asserted frame by frame in `overlay.py check`. |
| DAY 1 → DAY 3 | Day counter only increases (1, 2, 3) | Story pacing: RENT and EMI on day 1, FOOD and MOM on day 2, FRIENDS on day 3. |
| 27 DAYS TO PAYDAY | 30-day month − 3 days = 27 | Arithmetic; the 30-square calendar shows 3 crossed, 27 open. |

No external statistic is claimed. If the copy is ever extended with household-debt or EMI figures, cite RBI data directly and keep this story's numbers separate from it.
