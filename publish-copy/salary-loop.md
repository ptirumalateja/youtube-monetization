# The Salary Loop (Slow Light Dark)

| | |
|---|---|
| Status | V2 (re-edit on the 30 Friends formula), waiting for Teja's OK. Planned for Facebook on Monday evening, 26 Oct 2026 |
| Upload file | `final-reels/salary-loop-v2.mp4` (silent cut for your own music: `final-reels/salary-loop-v2_music-ready.mp4`) |
| Length | 18.3 s, 1080x1920, 30 fps. It loops: the last 0.5 s shows the same hook line and SALARY CREDITED box as frame 0 |
| Voice | None (wordless; plain on-screen text) |
| Build | `tools/salary-loop-warm/` renders the 3D with `XF=0` (hard cuts); `tools/salary-loop-v2/` re-cuts and re-texts it |

## What changed from V1

| V1 | V2 | Why |
|---|---|---|
| Frame 0: him asleep, no text. The notification arrives at 1.0 s | Frame 0: **YOUR SALARY / LASTS 6 DAYS.** with the ₹50,000 box already on screen | Same move as "AT 20, YOU HAVE 30 FRIENDS." on frame 0. The thesis is the hook |
| Payoff "SALARY LASTED 6 DAYS. WORK LASTS ALL 30." at 13.5 s, small, half over a building | **YOUR WORK / LASTS ALL 30.** huge, from 11.5 s, held about 5 s over the street and office | This is the reel's "AT 60, YOU NEED ONE." It needs size and hold time |
| Balance pill + 6-box strike strip + DAY + bill card + NEXT SALARY chip | **DAY n** big and the balance under it, plus the bill card. Nothing else | The friends reel has one counter. Too much HUD is noise at phone size |
| 0.2 s dissolves at every cut, several washing to near white | Hard cuts on every bill | Washed frames read as a glitch on a phone; cuts give the bills a punch |
| 5 s office time-lapse | 4 s (the eye-rub beat cut) | The lowest-energy stretch, where people swipe |
| LIFE GOES ON end card darkens the frame | Ends on the next-month SALARY CREDITED box and the hook line | A seamless loop counts as rewatches |
| ₹0 moment: small "DAY 6: ₹0 LEFT." | **DAY 6. / ₹0 LEFT.** huge with the sub boom (rehook at 9.5 s) | The rehook needs to be a hit |

## Publish copy

**Facebook / Instagram caption (posting on the 26th):**
> Your salary lasts 6 days.
> Your work lasts all 30.
>
> 1st: ₹50,000 credited. 📲
> Day 1, rent. Day 2, bike EMI. Day 3, groceries.
> Day 4, fuel. Day 5, the bills. Day 6, one dinner out.
> ₹0.
>
> The alarm still rings at 7.
> And on the 1st, it starts again.
>
> It's the 26th. Be honest: which day did your salary run out this month? 👇

**Pinned comment:** Mine ran out on Day ___. Yours? 👇

**YouTube Shorts title:** Your Salary Lasts 6 Days. Your Work Lasts 30. #shorts

**YouTube description:**
> Salary credited: ₹50,000. Rent on Day 1, bike EMI on Day 2, groceries on Day 3, fuel on Day 4, electricity, water and Wi-Fi on Day 5, one dinner out on Day 6. Balance: ₹0.
> The alarm still rings at 7:00, and the other 24 days are still work, until the 1st comes round and the phone buzzes again.
>
> A Slow Light story about living payday to payday. The numbers are made up for the story and add up exactly: 18,000 + 12,000 + 7,000 + 5,000 + 4,000 + 4,000 = 50,000.
> Made entirely in code (three.js, rendered frame by frame). Sound is synthesised, plus two CC0 Freesound files (sleepCircle, qubodup).
>
> #salary #salaryday #emi #middleclass #stickman #shorts

**Hashtags:** #salaryday #salary #emi #middleclass #monthend #stickman #relatable #slowlight

**Sound credit line (optional courtesy):** CC0 sounds by sleepCircle and qubodup via Freesound. All other sound is synthesised for this reel; no credit required.

**Upload settings:** 9:16, AI/synthetic media label on (synthetic scene), no music claimed. Use the frame-0 hook as the cover (it already reads YOUR SALARY LASTS 6 DAYS).

## Platform notes (why 30 Friends did 2.5M on FB and ~3k on IG + YouTube)

These are likely reasons. None of them can be confirmed from outside the platforms' analytics.

1. **Who each app shows it to first.** Facebook pushes Reels hard to people who don't follow you, and it skews older (30+). For that audience, "friends fading away" is lived experience, and they share it in Messenger and WhatsApp. On Instagram and YouTube the account's history is science and space reels, so the first test viewers are science fans. They swipe a life-topic reel, and the test stops early.
2. **The first second on YouTube.** Shorts ranks on "viewed vs swiped away". A wordless first frame, or one with small text, loses that test. V2's frame 0 is a big line for that reason.
3. **Comment velocity.** Replying to every FB comment in the first hours most likely did help, because it doubles the comment count and keeps the post active. Keep doing it in the first 2 hours tonight.

**Per platform, for this reel:**
- **Facebook:** post Monday 7 to 9 pm IST, when people are home from work. End of month is when this topic hits hardest, and the caption's "It's the 26th" uses that. Pin the Day ___ comment and reply fast.
- **Instagram:** post it as a **Trial Reel**. That shows it to non-followers first, so the science-follower base doesn't judge it. Set the cover to the hook frame. Add a quiet trending track from the in-app library on the music-ready file if you like (only in-app music is licensed).
- **YouTube Shorts:** the title should be the hook line, word for word. Upload directly, never a downloaded FB or IG file with a watermark. Expect a slower start: Shorts often picks a reel up days later.

## Facts and sources

| On screen | Value | Source / check |
|---|---|---|
| SALARY CREDITED +₹50,000 | A made-up monthly take-home salary | Story figure, not a statistic |
| Six bills: RENT −₹18,000, BIKE EMI −₹12,000, GROCERIES −₹7,000, FUEL −₹5,000, ELECTRICITY, WATER, WI-FI −₹4,000, FOOD & PARTY −₹4,000 | Sum = 50,000 | Arithmetic, asserted in `tools/salary-loop-warm/overlay.py check` |
| DAY 1 → DAY 6, balance 32,000 → 20,000 → 13,000 → 8,000 → 4,000 → 0 | One bill per day | Same check |
| DAY 7 → 30 · BALANCE ₹0 over the office | The remaining 24 days | 30 − 6 = 24 |
| YOUR SALARY LASTS 6 DAYS. / YOUR WORK LASTS ALL 30. | The story's own numbers | As above |

No external statistic is claimed.
