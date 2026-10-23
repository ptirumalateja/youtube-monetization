# Someone Knew 4 Days Early (PHP2Shell attacks)

| | |
|---|---|
| Status | Final (v1), delivered 23 Oct 2026, awaiting Teja's review. **Time-sensitive: post while PHP2Shell is in the news.** |
| Upload file | `final-reels/php2shell-who-knew_master.mp4` for YouTube (share: `php2shell-who-knew.mp4`, with sound design) or `final-reels/php2shell-who-knew_music-ready.mp4` (silent, add platform music; drop on 9.0 s) |
| Length | 15 s, loops |
| Voice | None (wordless, on-screen text only) |
| Copy taken from | `final-reels/php2shell-who-knew.md` (project files); source in `tools/php2shell-map/` |

## Publish copy

**YouTube title:** Someone knew 4 days early 🔴 The PHP flaw hitting the internet #PHP2Shell
**Alt title (A/B):** 7 in 10 websites run on PHP. Attacks started before the bug was public.

**YouTube description:**
> The first attack was seen on 17 October. The bug wasn't made public until 21 October.
> PHP2Shell is a pair of critical flaws in PHP (CVE-2026-109618 and CVE-2026-109619, CVSS 9.2) that let an attacker run code on a web server with no login. PHP runs 69.3% of websites whose server language is known, and a scan found 1,886,612 PHP servers facing the internet. The weak code path goes back to PHP 5.4 (2012).
> If you run PHP: update to 8.2.35, 8.3.36, 8.4.27 or 8.5.12 now. 8.1 and older need vendor backports or replacement.
> So who knew?
>
> The map is an illustration: dots are not real attack locations. Facts as of 22 Oct 2026. Sources: PHP security advisory (via Tenable and watchTowr FAQs), Amazon Threat Intelligence (via Tenable / Help Net Security), W3Techs, Modat scan data (via Recorded Future).
> Sound design: original, made for this video.
>
> #PHP2Shell #PHP #CyberSecurity #Shorts #Hacking #WebSecurity #InfoSec #SlowLight

**Tags:** PHP2Shell, PHP vulnerability, CVE-2026-109618, CVE-2026-109619, PHP RCE, cyber attack, zero day, web security, WordPress security, server hack, cybersecurity news, infosec

**Instagram / Facebook caption:**
> Someone was attacking this bug 4 days before the world knew it existed. 🔴
> PHP runs about 7 in 10 websites. PHP2Shell lets an attacker take over a server with no password and one request. If you run a site: update PHP today.
> Follow @slowlight for stories worth slowing down for.
> #php2shell #cybersecurity #hacking #infosec #webdev #tech #reels

**Facebook tags (Tags field, no #):** PHP2Shell, PHP, PHP vulnerability, cyber attack, cybersecurity, hacking, zero day, website security, web server, WordPress security, data breach, cybersecurity news, tech news, internet security, ethical hacking, web development, programming, infosec, Slow Light

**Pinned comment:** Who do you think knew first? 👀 (And if you run a site: which PHP version are you on?)

**Upload checklist:** use `php2shell-who-knew.mp4` (or the music-ready file with a dark, tense track whose drop hits 9.0 s). Turn the AI/synthetic label on (computer-generated visuals). Cover frame: "NO PASSWORD." with the shockwave (about 9.3 s) or "ATTACKS ARE SPREADING." over the lit map (about 6.5 s). Post soon: the story is from 17 to 22 Oct 2026.

## Facts and sources

| On screen | Status | Source |
|---|---|---|
| "SOMEONE KNEW 4 DAYS EARLY." / "FIRST ATTACK SEEN 17 OCT · BUG MADE PUBLIC 21 OCT" | Verified | Amazon Threat Intelligence saw an exploitation attempt on its MadPot honeypots on 17 Oct 2026, four days before public disclosure; PHP released fixes on 21 Oct (Tenable FAQ https://www.tenable.com/blog/php2shell-cve-2026-109618-cve-2026-109619-frequently-asked-questions-about-critical-php-remote ; Help Net Security, 21 Oct https://www.helpnetsecurity.com/2026/10/21/php2shell-php-vulnerabilities-patched-cve-2026-109618-cve-2026-109619/). How the attacker had the details early is unknown; "someone" is the honest framing. |
| "ATTACK #1 · 17 OCT 2026" target on the map | Illustrative position | The date is real; the dot's place on the map is symbolic (the attempt hit a honeypot; its location isn't public). |
| "THE HOLE IS IN PHP." / "69.3% OF WEBSITES RUN ON IT" | Verified | W3Techs: "PHP is used by 69.3% of all the websites whose server-side programming language we know" (https://w3techs.com/technologies/details/pl-php, read 23 Oct 2026). Caption says "sites with a known server language". |
| "ATTACKS ARE SPREADING." | Verified | Amazon: "now being broadly exploited in the wild" (Tenable FAQ); watchTowr sees exploitation in the wild since 21 Oct (https://watchtowr.com/intelligence/php-cve-2026-109618-faq/); Cloudflare CTO: "We are seeing early attacks emerging". |
| "1,886,612 PHP SERVERS FACING THE INTERNET" | Verified (exposure, not compromises) | Modat: 4,384,302 PHP services on 1,886,612 unique hosts (Recorded Future, https://www.recordedfuture.com/blog/php2shell-vulnerability-exploitation). Consistent with a Shodan count of over 1.9 million (Tenable FAQ). We do not claim these were all hacked or all vulnerable. |
| "NO PASSWORD. ONE REQUEST." / "CRITICAL · CVSS 9.2 · REMOTE CODE EXECUTION" | Verified | Both CVEs are unauthenticated RCE, CVSS v4.0 9.2 (PHP via Tenable, Patchstack https://patchstack.com/articles/php-major-vulnerability-alert-10-2026/). Help Net Security: the exploit shows "a single unauthenticated request" can trigger it before application code runs. (The early 10.0 score that circulated was wrong, per the PHP Foundation.) |
| "HIDDEN IN PHP SINCE 2012." | Verified | Calif's write-up found the earliest affected code path in PHP 5.4.0 (Tenable FAQ); Wiz says every version back to 5.4 is affected by at least one flaw (Patchstack). PHP 5.4.0 shipped in March 2012. |
| "FIXED: 8.2.35 8.3.36 8.4.27 8.5.12" / "UPDATE PHP NOW" | Verified | PHP releases of 21 Oct 2026 (Tenable, watchTowr, Help Net Security). 7.4 to 8.1: source backports only; 7.3 and older: no fix. |
| Date ticker 17 to 22 Oct; red dots, rings and arcs spreading | Illustration | The dots are placed around real cities to look like the web, and the spread is animated. They are not attack data. The frame carries "ILLUSTRATIVE MAP". |

Not used on screen (single-source or unclear): Dutch and Japanese sites taken offline as a precaution (Patchstack citing NOS and ITmedia); who discovered the bugs (sources disagree between Calif and Wiz); attack counts (no source gives one).
