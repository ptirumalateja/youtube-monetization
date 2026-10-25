# Payday to Payday (Slow Light Dark)

| | |
|---|---|
| Status | v2 rendered, pending the owner's OK |
| Upload file | `payday-to-payday.mp4` (silent cut for your own music: `payday-to-payday_music-ready.mp4`, hit at 9.15 s) |
| Length | 20.0 s, 1080x1920, 30 fps, loops (the last frames are salary day again) |
| Voice | None (wordless; plain on-screen text) |
| Build | `tools/payday-to-payday/` (three.js, PIL, numpy, ffmpeg) |

## Publish copy

**YouTube Shorts title:** ₹50,000 Salary. Gone by Day 5. Then Back to Work. #shorts

**YouTube description:**
> Salary day: ₹50,000 in, and he is happy.
> Day 1 rent. Day 2 EMI. Day 3 groceries. Day 4 food. Day 5 party. By day 5 the wallet is empty and he sits on the floor in the rain.
> Then he goes back to work. The sun sets, the sun rises, 25 days pass, and it is salary day again.
>
> A Slow Light story about living payday to payday. The numbers are made up for the story and add up exactly: 18,000 + 12,000 + 8,000 + 7,000 + 5,000 = 50,000.
>
> Made entirely in code (three.js, rendered frame by frame). Sound is synthesised, plus two CC0 Freesound files (sleepCircle, qubodup).
>
> #salary #salaryday #emi #middleclass #india #stickman #shorts

**Instagram / Facebook caption:**
> Salary day. ₹50,000 in. 😄
> Rent. EMI. Groceries. Food. One party.
> Day 5. Wallet empty.
> So he goes back to work. The sun goes down, the sun comes up, and the days roll on.
> 25 days later it is salary day again. Same smile.
> Which day does your salary run out? Tag the friend who is on day 5 right now. 👇
> #salaryday #emi #middleclass #stickman #reels

**Pinned comment:** Which day does your salary run out? Be honest. 👇

**Hashtags:** #shorts #salaryday #salary #emi #middleclass #india #stickman #slowlight

**Sound credit line (optional courtesy):** CC0 sounds by sleepCircle and qubodup via Freesound. All other sound is synthesised for this reel; no credit required.

**Upload settings:** 9:16, AI/synthetic media label on (synthetic scene), no music claimed.

## Facts and sources

| On screen | Value | Source / check |
|---|---|---|
| SALARY DAY: ₹50,000 IN. | A made-up monthly take-home salary | Story figure, not a statistic. The description says the numbers are invented for the story. |
| RENT −₹18,000, EMI −₹12,000, GROCERIES −₹8,000, FOOD −₹7,000, PARTY −₹5,000 | 18,000 + 12,000 + 8,000 + 7,000 + 5,000 = 50,000 | Arithmetic; checked in code (`overlay.py check`: the balance rises to exactly 50,000, then falls to exactly 0). |
| Balance counter | Rises only while the five bundles land (0 → 50,000), falls only while they are taken (50,000 → 0), then stays ₹0 | Asserted frame by frame in `overlay.py check`. |
| DAY 1 → DAY 5 → DAY 30 | One deduction per day for days 1-5; the day counter only increases and speeds up through the routine | Story pacing; asserted monotonic. The 25 days of routine are shown as a time-lapse, so the sun/moon cycles are not one per counter tick. |
| 25 DAYS TO GO | 30-day month − 5 days = 25 | Arithmetic; the 30-square calendar shows 5 crossed, 25 open. |
| Ghost hands, rain | Grey translucent hands take one bundle per expense; rain falls in the lamp beam on the day-5 low and on the routine's nights | Visual devices only. |
| Sun / moon icon | The lamp is the sun: bright = day, dim = night | Visual device only. |

No external statistic is claimed. If the copy is ever extended with household-debt or EMI figures, cite RBI data directly and keep this story's numbers separate from it.
