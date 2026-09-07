# Making money with ClipVein

ClipVein finds clips worth reposting. The money comes from **real, original
views** on content you re-cut well — and from the programs built to pay clippers
for exactly that. This page is the honest playbook.

The two paths you're most likely to use:

1. **Clipping bounties** — streamers and brands pay per view / per approved clip.
2. **Affiliate & referral** — you earn a cut of sign-ups or sales your clips drive.

Everything below is above-board: you're being paid for attention you genuinely
created.

---

## 1. Clipping bounties (pay-per-view programs)

The biggest streamers run **clipping programs**: they *want* an army of people
cutting their best moments and spreading them, and they pay for it. Typical
shapes:

- **Pay-per-1K-views** — a fixed rate (often a few cents to a dollar per 1K
  views) on clips that meet their rules, capped at a monthly pool.
- **Per-approved-clip bounties** — a flat payout for clips that hit a view
  threshold or get picked.
- **Leaderboards** — top clippers by views in a period split a prize pool.

### How ClipVein fits

The whole reason these programs pay is that finding *the right moment fast* is
hard. That's the step ClipVein automates:

1. Join the streamer's official clipping program (usually a Whop / Discord /
   Google Form the streamer links in their bio).
2. Read their rules: minimum length, required tags, allowed platforms,
   watermark/credit requirements, banned content.
3. Use ClipVein to surface the streamer's hottest recent moments.
4. Re-cut to the program's spec, caption it, post it on the platforms they pay
   for, submit the link.

### Make the rules machine-visible

Add the program's constraints straight into your ClipVein setup so you never
clip something that won't pay:

- Set `CLIPVEIN_MIN_VIEWS` to match the "moment must already be proven" bar.
- Add the streamer with all their aliases in `streamers.py` so nothing slips
  past the text match.
- Keep a note in the repo of each program's rate + rules (a `programs.md` you
  keep private is a good habit).

> **Read the rules every time.** Programs ban re-uploading other clippers'
> edits, stolen captions, misleading titles, and reused content across
> accounts. ClipVein helps you find *the source moment* so your edit is
> genuinely yours — that's what keeps you eligible and paid.

---

## 2. Affiliate & referral

If you're building an audience around a lane, your clips can carry offers:

- **Streamer/creator referral programs** — some pay for sign-ups (to their
  platform, membership, or merch) driven by your link.
- **Platform affiliate** — clip-hosting and editing tools, betting-adjacent
  sponsors (know your platform's rules and your local law), and creator SaaS
  often have affiliate tiers.
- **Your own funnel** — a link-in-bio to a newsletter, a Discord, or a service
  you sell (see below).

Disclose sponsorships and affiliate links where the platform or law requires it
(e.g. `#ad`). It's not just compliance — audiences reward creators who are
straight with them.

---

## 3. Other legitimate income around the same skill

- **Sell the service.** Once you can reliably find and cut winners, brands and
  smaller streamers will pay you to run *their* clip funnel. ClipVein is your
  edge; the deliverable is views.
- **Sponsorship on your own accounts.** A clip account with real reach gets
  brand DMs. Reach is the asset.
- **Platform creator funds & rev-share.** X, TikTok, YouTube and others pay
  creators for views/engagement under their own programs. Original, compliant
  edits qualify; re-uploads and farms get demonetised.
- **Tips / memberships.** If people follow *you* for the curation, GitHub
  Sponsors, Boosty, memberships, and tips are direct support.

---

## What NOT to do

Some "monetization" ideas look fast and end careers (and can be illegal). Steer
clear:

- **Pump-and-dump / memecoin farming.** Driving an audience into a token so you
  can skim fees or sell into their buys is market manipulation in many
  jurisdictions and gets accounts and repos removed. Don't build your reputation
  on a scheme that pays you when your followers lose.
- **Fake engagement.** Bought views/followers/bots violate every platform's
  terms and get clips demonetised and accounts banned.
- **Stolen edits & captions.** Re-uploading another clipper's cut, or lifting
  their caption, gets you kicked from bounty programs and can be a copyright
  strike.
- **Misleading bait.** Clickbait that misrepresents the clip tanks retention and
  trust, and trips platform "misleading content" rules.

The durable money is boring and real: **find genuinely good moments faster than
everyone else, cut them well, post consistently, get paid for the attention you
actually create.** That's what ClipVein is for.

---

## A simple first-month plan

1. Pick one streamer with an official clipping program. Join it, read the rules.
2. Set up ClipVein for that streamer (roster + view floor to match the program).
3. Ship one clip a day for 30 days. Log link + caption + 72h views.
4. After two weeks, double down on the streamer/caption/time that's winning.
5. Once a lane is proven, add a second streamer or pitch a brand your service.

Reach compounds. The tool just makes the finding fast.
