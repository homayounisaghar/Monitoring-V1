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
