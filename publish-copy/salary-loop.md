# The Salary Loop (Slow Light Dark)

| | |
|---|---|
| Status | v2 (lived-in) rendered, pending the owner's OK |
| Upload file | `salary-loop.mp4` (silent cut for your own music: `salary-loop_music-ready.mp4`, hit at 6.40 s) |
| Length | 20.0 s, 1080x1920, 30 fps, a true loop: he ends on his bed with the phone in his hand, exactly where he starts, and the last second rushes into the notification that opens the video |
| Voice | None (wordless; plain on-screen text) |
| Build | `tools/salary-loop/` (three.js, PIL, numpy, ffmpeg) |

## Publish copy

**YouTube Shorts title:** ₹50,000 Credited. ₹0 by Day 6. The Month Isn't Over. #shorts

**YouTube description:**
> Salary credited: ₹50,000. He springs off the bed and does a tiny dance.
> Then the landlord knocks. Day 1 rent. Day 2 bike EMI. Day 3 groceries. Day 4 electricity, water and Wi-Fi. Day 5 food. Day 6 fuel. Balance: ₹0. He turns the wallet upside down. Nothing falls out.
> The alarm rings at 7:00. Backpack, bus, traffic, office, the walk home in the dark, and the other 24 days, until the 1st comes round and the phone buzzes again. Somebody is already knocking.
>
> SALARY LASTED 6 DAYS. WORK LASTS ALL 30.
>
> A Slow Light story about living payday to payday. The numbers are made up for the story and add up exactly: 18,000 + 12,000 + 7,000 + 4,000 + 4,000 + 5,000 = 50,000.
> Made entirely in code (three.js, rendered frame by frame). Sound is synthesised, plus two CC0 Freesound files (sleepCircle, qubodup).
>
> #salary #salaryday #emi #middleclass #india #stickman #shorts

**Instagram / Facebook caption:**
> Salary credited. ₹50,000. 📲
> The landlord knocks. The bike EMI. Groceries. The light bill. Food. Fuel.
> Day 6. Wallet upside down. Nothing falls out.
> And the alarm still rings at 7:00.
> SALARY LASTED 6 DAYS. WORK LASTS ALL 30.
> Which day does your salary actually run out? Tag the friend who is on day 6 right now. 👇
> #salaryday #emi #middleclass #stickman #reels

**Pinned comment:** Which day does your salary run out? Be honest. 👇

**Hashtags:** #shorts #salaryday #salary #emi #middleclass #india #stickman #slowlight

**Sound credit line (optional courtesy):** CC0 sounds by sleepCircle and qubodup via Freesound. All other sound is synthesised for this reel; no credit required.

**Upload settings:** 9:16, AI/synthetic media label on (synthetic scene), no music claimed.

## Facts and sources

| On screen | Value | Source / check |
|---|---|---|
| SALARY CREDITED +₹50,000 | A made-up monthly take-home salary | Story figure, not a statistic. The description says the numbers are invented for the story. |
| Six bills: RENT −₹18,000, EMI −₹12,000, GROCERIES −₹7,000, ELECTRICITY, WATER, WI-FI −₹4,000, FOOD −₹4,000, FUEL −₹5,000 | Sum = 50,000 | Arithmetic, asserted in code (`overlay.py check`). One gold coin = ₹1,000, so the wallet holds 50 coins and each bill takes 18, 12, 7, 4, 4, 5 of them. |
| Balance counter | 0 → 50,000 as the coins land, then 32,000 → 20,000 → 13,000 → 9,000 → 5,000 → 0, then ₹0 through the grind | Asserted monotonic within each direction, frame by frame. |
| DAY 1 → DAY 6 → DAY 30 | One bill per day for days 1-6; the day counter then runs 6 → 30 and only increases | Story pacing; asserted monotonic. Days 7-30 are a time-lapse (no number is claimed beyond "the rest of the month"). |
| TODAY: 6TH, 07:00 AM, 1ST OF NEXT MONTH | The calendar and the alarm | Story props. |
| Landlord knock, bike, bags, fan and meter, plates, fuel gauge | One visible thing per bill (door shakes, motorbike drops in, bags drop on the table, ceiling fan and electric meter spin, plate tower, gauge needle falls to E) | Visual devices for the six bills; the amounts are the same story figures. |
| "SALARY LASTED 6 DAYS. WORK LASTS ALL 30." | The money lasted 6 days; he works every day of the 30-day month, 24 of them with ₹0 | Arithmetic (30 − 6 = 24). |

No external statistic is claimed. If the copy is ever extended with household-debt or EMI figures, cite RBI data directly and keep this story's numbers separate from it.
