# ST2 · Build findings — 2026-07-19

Workstream 01, prompt 1 of 4 (`src/lib/demo-library.ts` + `src/lib/demo-library.check.ts`).
Factual, short, and specific to this prompt.

## Decisions consumed

- `DEMO_TODAY = 2026-07-19` (Sunday); history spans Mon 25 May → Sun 19 Jul inclusive (56 days).
- 13-match fixed schedule ending with Dortmund on Sat **2026-07-18** (id `s-2026-07-04-dortmund` preserved as an opaque key).
- 28-day window arithmetic: 24 sessions = 28 days − 4 rest − 1 missing + 1 double; 5 matches + 19 non-match.
- Rest days are records with zero accumulation; the missing day is absent (no record). This distinction is what lets A:C treat rest as zero and missing as absent.
- One PRNG (`mulberry32`) seeded with `DEMO_SEED`; two runs produce byte-identical output.
- All 19 Dortmund per-athlete rows copied verbatim from `squad` in `session-data.ts` (participation, minutes, hrCoveragePct, srpeSubmitted).
- Portrait mapping reused from `src/lib/avatars.ts` (not duplicated).

## Defaults taken

- **Roster is 19, not 18.** The brief says 18; the built `squad` has 19 including P. Sturm, who is in-squad-never-participates. Kept all 19; Sturm receives no participation on any day (matches the existing single-session invariant).
- **Lange's arc reversed** — brief description implies Injury→…→Full; that cannot end anywhere but Injury without contradicting the pinned 18 Jul Injury row. Arc is Full (→28 Jun) → Part (→5 Jul) → Rehab (→12 Jul) → Injury (13 Jul→).
- **M. Frei substituted for H. Meier** as the never-submits-sRPE athlete. Meier's pinned 18 Jul row has `srpeSubmitted: true`; Frei's does not. Making Meier the never-submitter would contradict the pinned session.
- Rest-day placement: Mon 22 Jun, Mon 29 Jun, Sun 5 Jul, Mon 6 Jul (per brief).
- Missing day: Tue 14 Jul (per brief).
- Double-session day: Mon 13 Jul — "Gym · AM" (45') + "Pitch · PM" (70').
- Non-match session grammar reused from existing sidebar rows (`MD-1 · Activation`, `MD-2 · Intensive`, `MD-3 · Possession`, `MD-3 · Tactical`, `MD+1 · Recovery`, etc.).
- Two day-level "sRPE not collected" days: Sun 12 Jul and Sun 19 Jul (both recovery).
- Beyond-range day: Wed 8 Jul boosted ~16 % on team TD (measured: 192,578 m vs next-highest match 166,915 m — 15.4 % over).
- Match durations: pinned Dortmund 95'; other matches 94' regulation.
- Max velocity per athlete (fixed, position-plausible): GK 27–29, DEF 31–35, MID 31–34, ATT 33–36.
- Position typicals for TD/HSR/Sprint/AccDec/CL/mMin anchored on `posTypical` in `squad-metrics.ts`; day-type scaling table lives inline pending prompt 2 of this workstream.

## Defects found

- **`squad-metrics.ts` models sRPE as a 1–10 rate with unit `"/10"`, not a load in AU.** `demo-library.ts` carries both `srpeRating` (1–10) and `srpeAU` (rating × minutes) so downstream pages can display the correct load. Known defect; being fixed elsewhere; not touched here.
- No other new defects surfaced.

## New questions (held)

- The Session page's `currentSession.dateISO` in `session-data.ts` is still `"2026-07-04"`. A later prompt in this workstream re-dates it to `2026-07-18` to match the demo library — deliberately deferred, not a defect.
- The dataset brief calls the sidebar's rows "Day 7"-indexed; they are not — `SourceSidebar.tsx` already renders real dates and day-code badges. Requirement already satisfied; no action.

## Corrections applied in prompt 1b

### Defects found (all fixed in this pass)

- **Two session names contradicted their own day codes.** Wed 24 Jun rendered as "MD-1 · Activation" while `dayCodeFor` returns MD+3; Thu 25 Jun rendered as "MD+1 · Recovery" while the code returns MD-3. The `PRESERVED` table has been deleted; every non-match session now derives its name, type and duration purely from the computed day code via `nonMatchName`. Fixed.
- **Rest days were modelled as sessions.** A rest day used to appear in `demoSessions` as a `type: "recovery"` entry named "Rest day", conflating rest with an actual recovery session and putting rest days into `sessionsInRange`. Split into two series over one truth: `demoSessions` contains only real sessions (24 in the 28-day window), and a new `demoDays` list carries one entry per calendar date except the missing day, with `kind: "session" | "rest"` and a `sessionIds: string[]`. Rest-day records now have `sessionId: null` and `DemoRecord.sessionId` is widened to `string | null`. Fixed.
- **Injury and Rehab athletes accumulated match minutes.** `resolveParticipation` only zeroed minutes on non-match sessions, so F. Voss played about 12 minutes in every match. Injury and Rehab are now zero minutes on every session type; only the pinned 18 Jul rows survive as an override. Fixed.
- **Every athlete was "Full" on every session.** `participationFor` returned "Full" for everyone except Sturm/Voss/Lange, so matches ran with 18 outfielders at 90′ each and the participation categories never occurred. Match sessions now build a real squad shape (11 starters at 86–94′, 3–5 Part subs, remainder not in that match squad); training/gym sessions apply a deterministic scatter (≈ 10 % Modified/Part/Other). All six tags occur in the 28-day window; a rotation-enforcement post-pass guarantees no outfield athlete starts every non-pinned in-window match (Keller exempt as sole GK). Fixed.
- **The determinism check was self-certifying.** It hashed the same frozen array twice, which is guaranteed identical regardless of whether generation is deterministic. `buildSessions`, `buildDays` and `buildRecords` are now exported and the check calls them a second time, deep-comparing JSON-stringified output element-by-element and reporting the first divergent field. Fixed.

### Defaults taken

- **Match-squad shape.** 11 starters (Full, 86–94′), 3–5 substitutes (Part, 8–35′), remainder in-squad but `participation: null, minutes: 0`. Formation varies across matches ([4,4,2], [3,5,2], [4,3,3], [3,4,3]) so 4-of-4 tight defenders don't force the same 4 to start every week. Rotation is deterministic (matchIdx-driven, per-position hash phase), plus a post-pass swap that guarantees no outfield athlete starts every non-pinned in-window match. Alterable.
- **Non-match participation scatter.** Roughly 10 % of eligible athlete-sessions carry a non-Full tag on training/gym days (~4 % Modified, ~4 % Part, ~2 % Other). Alterable.
- **Beyond-range boost.** The 8 Jul match now multiplies squad TD/HSR/sprint by 1.55 (was 1.16). The higher factor is required because realistic squad selection introduces per-match variance of its own (~10 %), which was masking a 16 % boost. Team TD on 8 Jul now sits ~29 % above the next-highest match. Alterable.

### Notes

- `MATCH_PARTICIPATION` is precomputed at module init in match-date order, then a rotation-enforcement IIFE iteratively swaps monopolist starters into a Part slot while promoting a same-position sub. Arc-forced athletes (Lange, Voss) and never-participants (Sturm) are excluded from replacement selection so the post-pass cannot violate their storylines.
- `DemoSession.isRestDay` remains on the type but is always `false`; retained only so any hypothetical consumer written against the earlier shape doesn't hit a missing property. Prefer `demoDays[i].kind === "rest"`.

## Corrections applied in prompt 1c

### Defects found (all fixed in this pass)

- **The beyond-range multiplier reached 1.55 and produced implausible per-athlete distances.** `BEYOND_RANGE_TD_MULT` grew from 1.16 → 1.35 → 1.55 across prompts to clear the pinned 18 Jul squad-day total, which sits high because the pinned rows carry ~1,270 player-minutes vs ~1,050 for a real match. At 1.55 a midfielder was running ~16 km in a 94′ match. Retired. 8 Jul now has a real cause: an extra-time cup tie of 120′ (`durationMin: 120`, `note: "AET"`). Starters play 111–117′, subs are 4–5 in number at 20–45′. Session distance/HSR/sprint are dampened by 0.93 per minute relative to a straight extrapolation, reflecting that intensity sags in extra time. Maximum athlete-session TD is now 14,503 m (Albrecht, 8 Jul) — under the 15 km plausibility floor.
- **The "beyond range" test had nothing fixed to be beyond.** The retired check compared 8 Jul against the highest other match in the window, which is a moving peer target that can be satisfied by inflation. Replaced with `DAY_TD_DOMAIN_MIN = 0` and `DAY_TD_DOMAIN_MAX = 143_000` exported as a fixed drawn domain the UI must not auto-fit, plus two new checks: exactly one day in the whole library exceeds the cap (8 Jul at 145,492 m), and no athlete-session exceeds 15,000 m.
- **`DemoSession.isRestDay` was dead weight.** Field was always `false` since the day/session split, and no consumer read it. Field and all initializers removed; the check that asserted it was always false is gone too.
- **Rotation-phase seed literal read as a version number.** `"rotphase-v12"` suggested twelve prior tuning passes; renamed to `"rotation-phase"`. Behaviour unchanged — the string only feeds `hashSeed`.

### Defaults taken

- **`DAY_TD_DOMAIN_MAX = 143_000` m.** Chosen to sit above the second-highest squad day (pinned 18 Jul Dortmund at 140,762 m) and below 8 Jul (145,492 m) so exactly one day in the eight-week library breaks the cap. Comment in source flags it as a demo-calibrated placeholder pending real per-day exports. Alterable, but must never auto-fit.
- **8 Jul extra-time framing.** `MatchDef` now carries optional `note?: string` and `durationMin?: number`; 8 Jul is the only entry using them (`note: "AET"`, `durationMin: 120`). Full-tag minutes: `114 + jit(3)` clamped implicitly to 111–117. Part-tag minutes: `33 + jit(12)` clamped 20–45. Target Part count on 8 Jul is 4–5 (vs 3–5 elsewhere). Per-minute distance dampener: 0.93. Alterable within plausibility.
