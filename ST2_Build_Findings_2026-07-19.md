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

## Corrections applied in prompt 1d

### Decisions consumed

- **Participation contract (§1).** Minutes, load, coverage and sRPE eligibility per participation tag are now decided in one place — the `CONTRACT` table near the top of the participation section — and consulted by both `resolveParticipation` and `generateRecord`. No branch decides these facts independently. `demo-library.check.ts` walks every record and asserts it against `contractRowFor(tag)`; violations report athlete, date, tag and the field that disagreed. Contract table (verbatim from source):

  | tag        | minutes  | external+internal load | HR coverage | sRPE
  |------------|----------|------------------------|-------------|------
  | unselected | 0        | none                   | none        | none
  | Injury     | 0        | none                   | none        | none
  | Rehab      | 0        | none (not in session)  | none        | none
  | Other      | 0        | none (off-team prog.)  | none        | none
  | Modified   | reduced  | reduced                | present     | if collected+submits
  | Part       | reduced  | reduced                | present     | if collected+submits
  | Full       | normal   | normal                 | present     | if collected+submits

  "None" means `null` where the type allows and `0` otherwise; a zero never stands in for "no such record". The one legitimate zero is a rest-day record.

- **Declared exception.** The pinned 18 Jul session may carry `Injury` with minutes > 0 — the coherent reading is that the injury happened during that session. The invariant permits this only on `s-2026-07-04-dortmund` and the check prints the exempted rows by name (currently: `voss Injury@12′`, `lange Injury@29′`) so the exception stays visible.

### Defaults taken

- **`Other` shape.** Ali's rule named Injury, Rehab, Modified, Part, Full and not-in-squad — `Other` was not enumerated. Mapped `Other` to the same shape as `Rehab` (minutes 0, no load, no coverage, no sRPE) on the reading that "Other" means an individual off-team programme, not a reduced team session. Alterable — flag for the post-meeting register.
- **Low-coverage pair moved.** Brandt and Kuhn are now below the HR-coverage threshold on **Thu 2 Jul (MD-2 · Intensive, 82′)** instead of Tue 30 Jun (MD+2 · Regen). 30 Jun is a 50′ recovery session where thin coverage withholds almost nothing; 2 Jul is the heaviest training session in the window and is where the internal-load read is actually undermined. Same band (55–75 %).

### New questions (held)

- **`Injury` carries two facts.** In the generated history it means "unavailable for this session" (minutes = 0); on the pinned session it means "injured during this session" (minutes > 0). The two are distinguished only by whether minutes are non-zero, which is a modelling smell. Held for the post-meeting register — do not resolve here.

## Corrections applied in prompt 2 (typicals layer)

New module: `src/lib/demo-typicals.ts` (nothing imports it yet).

### Decisions consumed

- **Day-type conditioning.** A typical is conditioned on day type. Bucket key is **(dayCode, sessionType)** — the double day carries gym and pitch under the same MD code and they are not commensurable, so keying on dayCode alone would produce a like-for-not-quite-like baseline. Matches key as (`MD`, `match`).
- **No pooled/positional fallback.** There is no code path anywhere in the module that returns a squad or positional mean when a bucket is thin or empty. A missing baseline is withheld with its reason; the returned object carries `sessionCount` and `required` so a consumer can print "3 of 5 sessions" without recomputing.
- **Participation-only samples.** A session contributes a sample for an athlete only if that athlete actually participated — contract-minutes-bearing tags (`Full`, `Part`, `Modified`) with minutes > 0. `Injury`, `Rehab`, `Other`, unselected and not-in-squad contribute nothing. An injured athlete's zero is not a low sample, it is not a sample.
- **Two exclusions.** Rest days contribute nothing (a rest day is a real zero for accumulation but is not an instance of a day type). The 19 Jul unconfirmed session contributes nothing (provisional data must not enter a baseline). Both filtered at sample construction.
- **`TYPICAL_MIN_SESSIONS = 5`.** Below five comparable sessions in a bucket, the typical is withheld. Naming collision with `session-flags.ts`'s `BUILDING_SESSIONS_TO_MIN = 3` (a different quantity — how many Köhler currently has) is flagged and deliberately not aliased.
- **Composition-matched expected sum.** For each session, sum over the athletes who actually participated of (that athlete's own per-minute typical for this bucket × minutes played in this session). Withholding athletes are **excluded** from the sum and reported by name — never substituted with a squad or positional mean. The sum states its own coverage (contributed / participated). If coverage is thinner than the floor, the sum withholds as a whole rather than returning a misleading number.

### Defaults taken

- **Bucket key format.** `${dayCode}::${sessionType}` — literal join, not a struct. Alterable but the whole module funnels through `bucketKeyFor` / `parseBucketKey` so a format change is one call site.
- **Minutes-weighted mean and biased SD.** Weight = minutes. Biased SD (population form) rather than sample-corrected — the samples in a bucket ARE the population of comparable observations for this athlete-bucket, not a random draw from a larger one.
- **Nominal duration per bucket.** Mean of `session.durationMin` across contributing sessions in the bucket, rounded. Used to convert the per-minute rate into a full-session value. For match buckets this pulls in the 120′ AET tie, nudging the nominal above 90′ — realistic given the mix, and alterable if we later want a strict 90′ reference.
- **Squad-level aggregation weight = 1 per athlete.** In `squadTypicalFor`, each contributing athlete's per-bucket typical is weighted equally rather than by his sample count. Using n as weight would let a high-frequency athlete dominate a squad typical that is meant to be per-athlete, not per-appearance. Alterable.
- **Expected sum whole-of-sum floor.** `EXPECTED_MIN_COVERAGE = 0.5` and `EXPECTED_MIN_CONTRIBUTORS = 3`. Below either the sum withholds as a whole.
- **Rate metrics excluded from expected sum.** A sum of a rate is not a meaningful figure — only cumulative metrics (`totalDistance`, `hsr`, `sprintDist`, `accDec`, `cardioLoad`, `srpeAU`) enter the sum. Rate metrics (`mMin`, `topSpeedKmh`) are still exposed per-athlete-bucket for the drill.

### Defects found

- **Zero-spread sprint distance in `MD+1::recovery` for two athletes.** The check surfaces two typicals with `sd = 0` on `sprintDist`: `keller` and `lange` in the `MD+1 · Recovery` bucket. Cause is in the generator, not the typicals layer: recovery-session scaling multiplies position sprint by 0.02, and for GK (sprint typical 30) and lower-typical outfielders the per-minute value rounds to 0 across every sample, producing an identical zero across all five recovery appearances. This is exactly the "zero spread is a lie about certainty" case the check exists to surface; it is fenced out of this prompt (no `demo-library.ts` edits) and held for the next demo-library correction pass. Two options for that fix, neither taken here: raise the sprint recovery multiplier just enough that GK/DEF-lite still round to a non-zero value with the usual jitter, or model sprint as a Bernoulli-per-appearance rather than a scale-of-typical, since real recovery sessions contain no sprints at all and the honest read for those buckets may be "no sprint distance for this day type, withheld" rather than "typical sprint = 0".

### New questions (held)

- Should `sprintDist` and other metrics with a near-zero typical for a day type be **withheld per-metric** rather than reported as a zero-plus-zero-SD figure? A "0 ± 0" band is technically what the samples say, and it is also useless. Held for the post-meeting register.

### Check surface

Full suite (library + typicals) run at end of prompt 2: **38 / 39 pass**. The single failure is the zero-spread finding above, retained as evidence rather than silenced.

## Corrections applied in prompt 1e (history extension)

Fences: only `src/lib/demo-library.ts` and `src/lib/demo-library.check.ts`.

### Decisions consumed

- **History extended backwards to a weekly rhythm.** `START_ISO` moved from 2026-05-25 to **2026-04-13** (a Monday), and six weekly Saturday fixtures added before the congested block: Schalke 04 (18 Apr), VfL Bochum (25 Apr), FC Heidenheim (2 May), Darmstadt 98 (9 May), Holstein Kiel (16 May), SV Elversberg (23 May). Everything from 31 May onwards is unchanged: same matches, same rest days, same missing day, same double day, same extra-time tie, same pinned session. The 28-day window still contains 24 sessions / 5 matches / 19 non-match with the same four rest dates. The reason for the extension is not history length per se: the buckets are thin because match density is high, and the fix is a stretch of weekly rhythm where a full microcycle can occur.

### Defaults taken

- **`SEASON_START_ISO = "2026-04-13"`.** New exported constant; commented as demo-calibrated pending Ali's ruling on when the season is declared to begin. `START_ISO` now aliases it — nothing hardcodes a season-start date. Any season-to-date read derives from this constant.
- **Six extended-stretch fixtures** listed above; all ordinary weekly matches, one home / one away alternating. Results are decoration and irrelevant to load.
- **Monday-after-match rest rule** for dates < 2026-05-31 only. All six extended-stretch matches fall on Saturdays, so the rule adds six new rest days: 20 Apr, 27 Apr, 4 May, 11 May, 18 May, 25 May. The rule does not apply from 31 May onwards, so the four fixed rest dates inside the 28-day window are untouched.
- **Extra-time dampener retightened from 0.93 → 0.91.** The new `matchIdx` values (existing matches shifted by +6) reshuffled starter rotation, and one athlete (Frei) ended up starting the 8 Jul AET tie for the first time; at 0.93 his total distance came in at 15,134 m, just over the 15,000 m plausibility floor. 0.91 brings the maximum to 14,808 m and leaves the 8 Jul day total at 145,237 m — still the only day above `DAY_TD_DOMAIN_MAX`. `DAY_TD_DOMAIN_MAX` unchanged: the second-highest day is still pinned 18 Jul at 140,762 m, well below the cap.

### Defects found

- **`dayCodeFor` tie rule cannot produce MD-4 or MD-5 from a weekly rhythm.** The rule ("upcoming wins ties" — closer match wins) resolves the six days between two weekly Saturday matches as `MD+1, MD+2 (rest), MD+3, MD-3, MD-2, MD-1`. There is no MD-4 or MD-5 in this pattern; the only MD-4/-5 sessions in the whole eight-week library are the two days at the very start of history (13 Apr = MD-5, 14 Apr = MD-4) before any prior match exists to pull those days into MD+ territory. Final census: `MD-1 · training = 19, MD::match = 19, MD+1 · recovery = 14, MD-2 · training = 11, MD-3 · training = 10, MD+3 · training = 7, MD+2 · recovery = 3, MD-4 · training = 2, MD-5 · training = 1, MD+2 · gym = 1, MD+2 · training = 1`. MD-2 and MD-3 are now well over the five-session floor; MD-4 and MD-5 are short and cannot be filled by adding more history under the current tie rule. Not resolved here per the prompt's explicit instruction ("report the counts and stop rather than adding more matches on your own initiative"). The check reports `SHORT: MD-4=2 MD-5=1`. Held for the next design pass: either change `dayCodeFor` to a count-backwards rule (each day is labelled by its distance to the *next* match, up to a cap; days beyond that cap fall back to MD+ from the last match), or accept that MD-4 and MD-5 are structurally rare in this fixture pattern and let the typicals layer withhold them.

### New questions (held)

- **When does the season start?** The extended stretch is in-season by construction. If Ali declares the season to begin after 13 April, this pre-season regime should not feed baselines — which would undo the extension. `SEASON_START_ISO` names the value and flags the ruling.
- **`dayCodeFor` semantics.** "Nearest match" is the current rule; MD-4/MD-5 need a "count backwards from next match" rule to fill under any realistic in-season schedule. Not resolved here.

### Check surface

Full suite (library + typicals) after prompt 1e: **42 / 44 pass**. The two failures are the reportable outcomes above: (1) the MD-4/MD-5 shortfall (structural, per the tie rule — instructed to stop, not to compensate); (2) the pre-existing zero-SD finding in `MD+1::recovery::sprintDist` for `keller` and `lange`, which is fenced out of this prompt (a `demo-library.ts` generator issue held from prompt 2's findings). Every previously passing check still passes.
