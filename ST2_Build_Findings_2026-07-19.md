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

## Corrections applied in prompt 3 (spatial layer)

### Defaults taken

- **Coordinate model, point-count rule, and missing-data athlete.** Normalised pitch 0–100 on both axes with attacking left→right; per-`posDetail` anchor + spread table drives 2–3 cluster centres per athlete-session, points count = clamp(round(minutes × 1.5), 12, 160) so subs read visibly sparser than starters; polyline is a 24-waypoint 3-tap moving average through the points in generation order; thirds are computed from the points (`x < 33.3` D, `< 66.6` M, else A) with rounding drift absorbed into the attacking share so D+M+A = 100; coverage is 84 ± 10 % clamped to 65–99. **M. Meier** carries the "no positional data" state across the whole window (Voss / Lange / Köhler / Sturm already carry other states); a small scatter (~3 %) of other athlete-sessions also drop to `null`. PRNG is `mulberry32` keyed off `DEMO_SEED` — no new PRNG.

## Corrections applied in prompt 4 (session wiring)

### Defaults taken

- **Session re-dated and sidebar re-pointed.** `currentSession.dateISO` moved from 2026-07-04 to 2026-07-18 (id, name, day code, halves, weather, result unchanged); `sessionLibrary` deleted from `session-data.ts` and derived inside `SourceSidebar.tsx` from `demoSessions` (last 30 days, most-recent-first, `match` stays `match` and `training`/`recovery`/`gym` collapse to `training`; halves for non-match rows are a two-way split of duration). Derivation lives in the sidebar rather than `session-data.ts` to avoid a module-init cycle with `demo-library.ts`, which reads `squad` at init.

## Workstream 04 · prompt 1 (Longitudinal derivation layer)

New module: `src/lib/longitudinal-data.ts` and its check `src/lib/longitudinal-data.check.ts`. Two additive changes in `src/lib/demo-typicals.ts` (§A1 typical-duration field, §A2 required basis argument on `expectedSumForSession`); one call-site update in `demo-library.check.ts` to pass `"actualMinutes"`. Nothing under `src/components/` or `src/routes/` touched.

### Decisions consumed

- **Windows are calendar-anchored.** A horizon of N days ends on `DEMO_TODAY` and covers the N calendar days ending that day inclusive; a day with no data still counts. Season-to-date runs `SEASON_START_ISO → DEMO_TODAY`. The 28-day window contains 28 days, 24 sessions, 5 matches, 19 non-match, 4 rest days and 1 no-record day — asserted by the check.
- **Rest = real zero, missing = null.** Never interpolated. Enforced structurally in `daySeries` and asserted.
- **Vs-typical uses the typicalDuration (volume) basis.** When any session on the day withholds its expected sum, the day's vs-typical withholds for every metric with its reason — never silently absolute.
- **Availability is over training sessions only.** Selection ≠ availability. Numerator = Full training-sessions; denominator = per session, the number of athletes in the squad on that date. Athletes joining mid-window enter the denominator only from their join date.
- **A:C is a bare ratio.** 7-day average / 28-day average per metric per athlete, no band, no verdict. Rest = zero enters averages; missing = absent (neither sum nor count).
- **Composition-parity for gauges.** Both Volume % and Intensity % ratios cover exactly the same (session, athlete) pair set — the same `contributed` list from `expectedSumForSession`. A session that withholds drops out of the numerator too.

### Defaults taken

- **`LONGI_WINDOW_DEFAULT = 28`.** Alterable.
- **`GAUGE_MIN_COVERAGE = 2/3`.** Below this share of the window's sessions contributing, the gauges withhold as a whole. Named constant, one-place change.
- **`HR_COVERAGE_THRESHOLD = 80` (percent).** Matches the value already used in `demo-library.check.ts` (Brandt/Kuhn <80 % on 2 Jul). Records below the threshold stay in day totals and are counted separately in `hrBelowThresholdCount`; never dropped.
- **Attention flag is a stand-in.** The per-athlete ranking's `attentionFlagged` currently derives from the presence of any `Injury`/`Rehab`/`Modified` record in-window. There is no Attention data source in the demo library; when the Attention section exposes its own signal, this helper should read from that instead. Documented so the substitution stays visible.
- **`ExpectedSumBasis` type is required, not defaulted.** `"actualMinutes"` (rate basis) vs `"typicalDuration"` (volume basis). Every existing call site (`demo-library.check.ts`) passes `"actualMinutes"`, preserving prior behaviour.
- **Per-athlete typical duration.** Plain unweighted mean of `minutes` across an athlete's sample records in a bucket, rounded. Added to the `"computed"` `AthleteBucketTypical`. Enables the volume basis without touching the existing weighted per-metric statistics.
- **Zero-participation athletes are returned separately.** `windowTotals.zeroParticipation`. Reasoned from the tag(s) they carried across the window ("unselected" for Sturm on the 28-day window). Prevents a row of zeros passing itself off as data.
- **`SessionCategory` filter surface** for §B8 = `["All", "Matches", "Training", ...dayCodesPresent]`.
- **Vs-typical uses composition parity across observed and expected** — observed sum for each metric restricted to the same contributed set that the expected sum uses, so a metric-level cell cannot silently over- or under-count relative to its denominator.

### Defects found

- **A:C withholds for every athlete in the 28-day window.** The window contains one missing day (14 Jul), so every athlete's record set spans at most 27 dates — one short of the 28 the ratio requires. The check reports `computed=0 withheld=18 (insufficient_days:18)`. This is the spec's literal rule ("if he has fewer than 28 days of history … withhold and carry how many days") applied honestly to a window with a missing day, not a bug — but it is the reason no A:C reads on 19 Jul under this window. Two paths for the design pass: (a) accept it — A:C is unreadable in a window with any missing day, which is what "we don't have the data" should look like; (b) relax the denominator to "days with a record" rather than "calendar days", in which case 27 becomes the threshold and Köhler still withholds (12 of 28). Held for the display prompt.
- **The 14-day probe at 2026-01-07 is unreachable.** Explicitly permitted by the spec ("otherwise for the most match-dense 14-day window in the library"). Used the most match-dense reachable window instead — 14 days ending 2026-06-16 with 6 matches. Named in the report.

### New questions (held)

- **Vs-typical percentage at day level vs at pair level.** The current day-level vs-typical is `sum(observed) / sum(expected)` — mathematically an athlete-weighted mean of per-pair ratios. An alternative is `mean over contributors of (observed_i / expected_i)`, which weights each contributor equally. The two differ when a high-minutes contributor sits far from typical. Both are defensible; the load-bearing rule is composition parity (same pair set on both sides), which either form satisfies. Held for the display pass to pick.
- **Attention wiring.** Replace the Injury/Rehab/Modified stand-in with a real Attention signal when the Attention derivation lands.

### Domain-calibration table (from the check, whole library, avg per athlete who trained)

```
metric             highest       2nd       p95date-of-max
totalDistance         9682      8734      7993   2026-07-08
hsr                    667       592       571   2026-07-08
cardioLoad             231       192       186   2026-07-08
srpeAU                 630       546       544   2026-07-08
```

### Check surface

Longitudinal check: **15 / 15 assertions pass.** Demo-library + typicals check unchanged at **42 / 44** (the two prior structural findings — MD-4 / MD-5 shortfall and `sprintDist` zero-SD in `MD+1::recovery` for `keller`/`lange` — are still reported, still not silenced).

## Workstream 04 · prompt 1 — corrections

### Defects found (mine)

- **A:C withheld for every athlete.** `acForAthlete` decided "fewer than 28 days of history" by counting the athlete's record dates inside the window. The 14 Jul day is unrecorded for everyone, so every athlete came out at 27/28 and the whole A:C column withheld. The rule is history, not record count: an athlete has the full history when his `joinedISO` falls on or before the window's first day. `daysOfData` still carries his real record count (so a mid-window joiner reads as 12/28, not 13/28). After the fix exactly one athlete withholds — B. Köhler (joined 2026-07-07, after the window's start 2026-06-22). Asserted in the check.
- **`attentionFlagged` derived from participation tags.** It returned true for any Injury/Rehab/Modified in-window record, which put a flag on most of the squad and rendered the page as an alarm. Fixed to source the signal from `src/lib/session-flags.ts` (Tier-1 rows for the pinned session). If the pinned session (2026-07-18) falls in the window and the athlete's id is in `TIER1_ROWS_DEFAULT`, he is flagged; otherwise not. No participation-tag fallback.

### Flag source

`session-flags.ts` → `TIER1_ROWS_DEFAULT` (the pinned session's day-of-match Tier-1 set: `fischer`, `werner`, `schaefer`, `hofmann`). Scoped to windows that include 2026-07-18; false everywhere else. Attention wiring for non-pinned sessions is still held for the Attention section itself.

### A:C rule as implemented

Withhold when `athlete.joinedISO > window.startISO`. Otherwise compute `avg(7d) / avg(28d)` per metric, with rest days entering as real zeros and missing days absent from both numerator and denominator. `daysOfData` on the withheld state reports the athlete's real in-window record count.

### Re-printed numbers (verbatim from the check)

Domain calibration (whole library, avg per athlete who trained):
```
metric             highest       2nd       p95date-of-max   
totalDistance         9682      8734      79932026-07-08    
hsr                    667       592       5712026-07-08    
cardioLoad             231       192       1862026-07-08    
srpeAU                 630       546       5442026-07-08    
```

Gauges:
```
28-day: Volume 103.0%  Intensity 99.6%  (16 of 24 sessions; match-dominant=false)
  target 2026-01-07 unreachable; used most match-dense 14-day window ending 2026-06-16 (6 matches): Vol 98.0% Int 100.4% (14/14, match-dominant=false)
```

Availability (28-day):
```
28        278/352          79.0      19   19 Full=278 Part=15 Injury=25 Modified=6 Other=5 Rehab=4 notInSquad=9
```

Zero-participation athletes (28-day):
```
  P. Sturm            reason=unselected
```

## Workstream 04 · derived decisions (strategist, not in document 04)

### Lane domains — supersede document 04 §6's placeholders

Placeholders were set before the dataset existed and are wrong against it in both directions: distance would break on at least two days, Cardio Load on most heavy days, HSR would sit permanently in the bottom half of a track twice as tall as its data.

Rule used: cap each lane so the 95th-percentile day sits at roughly 85% of the track, rounded to a readable number, then let the data decide what breaks. Never auto-fit.

| lane | domain | 95th pct | highest | breaks |
|---|---|---|---|---|
| Total distance | 0–9,000 m | 7,993 | 9,682 (8 Jul) | 8 Jul only |
| HSR | 0–700 m | 571 | 667 (8 Jul) | none |
| Cardio Load | 0–220 AU | 186 | 231 (8 Jul) | 8 Jul only |
| sRPE | 0–700 AU | 544 | 630 (8 Jul) | none |

Sprint distance and Acc–Dec are not yet calibrated; the same rule applies when they are.

### Participation palette — Ali's ruling, 2026-07-19, supersedes document 04 §3's defaults

Two families by meaning, lightness step inside each. Full is neutral; hue appears only on departures.

```
Full          #64748B   neutral slate
Part          #14B8A6   present but reduced, light
Modified      #0F766E   present but reduced, dark
Rehab         #B08968   unavailable, light
Injury        #8A5A44   unavailable, dark
Other         #6B7280   neutral residual
not in squad  no fill, 1px #CBD5E1 outline — absence of ink, never a colour
```

Reserved and unavailable as fills: blue, purple, green, red, amber. Bar width scales to the sessions available to each athlete, so a mid-window joiner's bar is visibly shorter rather than his denominator hiding in the fraction. Expander label: `Session by session ⌄`.

Binding gate: a greyscale screenshot must keep all five departure categories separable. If it fails, widen the lightness steps within each pair — never add hues. Measured lightness of the ruled values is Part 67, Rehab 60, Other 48, Modified 45, Injury 43, so the three dark categories sit within five points of each other and the gate is expected to depend on the shipped stripe textures being retained under the hue rather than replaced by it.

This remains a time-boxed demo exception with an expiry at the post-meeting review, not a ratified palette.

### Squad-load gauge construction

Both gauges run on total distance and share one numerator: observed distance over every session-athlete pair where the athlete participated and had a computable typical for that session's bucket. Volume divides by the same pairs' expected distance at each athlete's own typical session length; Intensity divides by the same pairs' expected distance at the minutes he actually played. Both sides of both ratios cover an identical pair set.

### Strings derived here, needed as deck keys

- Gauge coverage basis line — `across {n} of {m} sessions` — renders only when contributing sessions are fewer than the window's sessions. Not in the copy-corrections file; derived from document 04 §2.
- Athlete-list expander line — `{n} more athletes · {max} or fewer training sessions missed`, and where max is zero, `{n} more athletes · no training sessions missed`. Document 04 §3's example wording does not generalise.
- Window-table foot row — `did not participate · not in squad`, not `· injury`. The data's only zero-participation athlete is P. Sturm, whose state is unselected; F. Voss carries twelve minutes on 18 July and is an ordinary row.

### Character line

Must be re-authored against the library, not transcribed. The copy file's example says Lange returned through rehab; the dataset reversed his arc, so he went out through rehab into injury. Köhler joining 7 July is correct.

### Three findings

1. **Lane ranges wrong against the data** — found and resolved; the resolution is the domain table above.
2. **The match-dominant regime never fires anywhere in the library.** The densest fortnight is six matches against eight training sessions — dense, not a majority. The receded-gauge state shown in the exploration return cannot be demonstrated from this data. Build the rule as written and leave it dormant; do not bend the rule or the data to make it appear.
3. **The gauges sit exactly on their own coverage floor.** Sixteen of twenty-four sessions have a computable baseline against a two-thirds threshold. They pass and print, with the coverage line beneath them. One session moving would tip the Summary's primary object into withholding entirely. Fragile, not wrong.

Also recorded: availability is 278 of 352 at Full across nineteen training sessions and nineteen athletes. Nineteen times nineteen is 361, not 352 — the nine-session gap is Köhler's pre-join period, and the sub-line will not multiply out on screen. Ratified behaviour, flagged because a stakeholder may do the arithmetic aloud.


**Availability sub-line — corrected (Ali, 2026-07-19).** Prints `{full} of {possible} · {trainings} training sessions`. The earlier `{trainings} trainings × {athletes} athletes` gloss invited a multiplication that fails — 19 × 19 is 361 against a true possible of 352, because a mid-window joiner is only in the denominator from his join date. The denominator is still stated; the trap is removed. Supersedes the copy-corrections template for this line.

**Coverage floor — one constant at one half (Ali, 2026-07-19).** Two thirds was an invented default, not a derived one, and the demo landed exactly on it, leaving the Summary's primary object one session and one comparison operator from vanishing. Two modules also disagreed. Padding a baseline with fabricated comparable sessions would be dishonest; moving an arbitrary threshold is not, and the printed coverage line carries the honesty either way.

**Greyscale remedy — changed (Ali, 2026-07-19).** The earlier remedy of widening lightness steps is withdrawn. Separating five categories by lightness alone would make lightness monotonic across them, which reads as a severity ranking on a taxonomy that has no order — trading one gate failure for a worse one, and against the ratified rule that hue carries category while position carries magnitude, so colour is never a verdict. The remedy is instead: **retain the shipped stripe textures under the hue rather than replacing them, and soften their contrast**, since colour now does the fast distinguishing and texture only has to carry the greyscale and colour-blindness floor. This also makes the demo exception additive — the post-meeting reversal becomes the removal of a fill. Test at the **start** of step 5, not the end.

**Match-dominant regime — not built (Ali, 2026-07-19).** The rule is skipped entirely rather than built dormant. A branch proven unable to fire is invisible work on the critical path. If asked, the answer is unchanged: the demo calendar contains no match-dominant window, its densest fortnight being six matches against eight training sessions.

**Deterministic dates — one formatter, no `Intl` (Ali, 2026-07-19).** Three date strings were routed through `toLocaleDateString`; two passed no `timeZone`. Parsing `2026-07-19` as UTC and formatting in `America/Los_Angeles` yielded `18 Jul` on the client while SSR produced `19 Jul` — a hydration mismatch, and simply a wrong date for any reader west of Greenwich. The sidebar row date, in particular, was reaching the shipped Session page: it sat next to the day-code badge and contradicted it. The third string (the banner range) was routed via `timeZone: "UTC"` and so zone-safe, but its output still depends on the ICU version, which differs between the SSR runtime and the browser.

Remedy: `src/lib/format-date.ts`, four exports (`dayMonth2`, `dayMonth`, `weekdayDayMonth`, `rangeLabel`) built from ISO string parts with fixed month and weekday arrays; `getUTCDay()` on a `Date.UTC(...)` value is the only date primitive used. `SourceSidebar.tsx` row date → `dayMonth2`; `WindowBanner.tsx` range → `rangeLabel` (handles cross-year properly, dropping the dead ternary); season gloss date → `dayMonth`. `formatShort` and `formatRange` deleted.

Fence exception: `SourceSidebar.tsx` was edited under the Session fence for the row-date correctness fix. No design change — same shape (`19 Jul · 46'`), same alignment, same day-code badge.

`DEMO_TODAY` as found: `export const DEMO_TODAY = "2026-07-19"` in `src/lib/demo-library.ts` (line 32) — a hard ISO literal. No clock reads; left as-is.

**Window menu clipped by a vestigial `truncate` (Ali, 2026-07-19).** The banner's left group carried `flex min-w-0 items-baseline gap-x-2.5 truncate`, copied from Session's banner where the ellipsis lives on an inner `<h1>`. Here there is no long title, and `truncate`'s `overflow: hidden` clipped the absolutely-positioned window menu — click the range, nothing appeared. Removed `truncate` from the wrapper; the range span already carries `whitespace-nowrap`, so no width guard is lost. The four menu rows now render on screen, `default` on the 28-day row, `since 13 Apr · 14 wk` on Season to date.

**Session banner date — same defect, same remedy (Ali, 2026-07-19).** `EventBanner.formatDate` was `new Date(iso).toLocaleDateString("en-GB", …)` with no `timeZone`. In LA the server wrote `Fri, 17 Jul 2026` and the browser wrote `Sat, 18 Jul 2026` — hydration mismatch on the page's top object, contradicting the sidebar row `18 Jul · 95'` beneath it. Added `weekdayDayMonthYear(iso)` to `format-date.ts`; `EventBanner` now reads `Sat 18 Jul 2026`. `formatDate` deleted.

**Fence exception logged: `EventBanner.tsx` edited under the Session fence — date formatting only, no other change.**

**Default taken — dropped the comma in the Session banner date (Ali, 2026-07-19).** `Sat, 18 Jul 2026` → `Sat 18 Jul 2026`. There was no stable current rendering to preserve — the two sides disagreed by a whole day — and the no-comma form is the idiom the Longitudinal banner already ships (`Mon 22 Jun – Sun 19 Jul 2026`). One date vocabulary across two banners a stakeholder may see side by side. Reversible in one line.

**Sweep — every `toLocale*`, `Intl.`, and unqualified `new Date(` in `src/` (Ali, 2026-07-19).**

Date-producing, reader-visible on Session or Longitudinal — fixed this turn:
- `src/components/session/EventBanner.tsx:239–240` — `new Date(iso).toLocaleDateString(...)`. Now `weekdayDayMonthYear`.

Number formatting, not date — left in place, safe across zones and locales because they format integers/decimals:
- `src/lib/squad-metrics.ts:166` — `v.toLocaleString()` on a number.
- `src/components/ui/chart.tsx:225` — `item.value.toLocaleString()`.
- `src/components/data/ValueOnTrack.tsx:193` — `value.toLocaleString()`.
- `src/components/session/SummaryCard.tsx:432, 483` — `value.toLocaleString()`.
- `src/components/session/SquadCard.tsx:878` — `Math.round(value).toLocaleString()`.
- `src/components/session/PeriodsCard.tsx:748` — `Math.round(v).toLocaleString()`.

  Note: `toLocaleString()` on a number can insert locale-specific thousands separators (comma in en-US, space in fr-FR, dot in de-DE) and produce different strings on SSR vs client. Not date-wrong, but is the same *class* of nondeterminism. Flagged for a later sweep; not fixed under this fence.

Third-party primitive, not on Session or Longitudinal — left:
- `src/components/ui/calendar.tsx:35, 157` — react-day-picker internals.

Unqualified `new Date(...)` — all safe:
- `src/lib/demo-library.ts:11` — comment.
- `src/lib/demo-library.ts:223`, `src/lib/longitudinal-data.ts:76`, `src/lib/longitudinal-data.check.ts:40`, `src/lib/format-date.ts:26` — `new Date(ms)` where `ms` comes from `Date.UTC(...)` arithmetic; only `getUTC*` accessors are called on the result. Zone-independent.
- `src/components/shell/SourceSidebar.tsx:120` — `new Date(ms).toISOString().slice(0, 10)` with `ms` from `Date.UTC` arithmetic. Zone-independent.


---

## Workstream 04 · Step 3 — Summary section (Ali, 2026-07-20)

**Built.** One card, two panes (SQUAD LOAD left, AVAILABILITY right), and a character-line foot. No Days/Athletes content — those stay as anchor placeholders.

**Participation-style lift.** Created `src/lib/participation-style.ts` with `PARTICIPATION_TAGS` (fixed order) and `TAG_TEXTURE` — byte-identical values lifted out of `SummaryCard.tsx`, plus `NOT_IN_SQUAD_CLASS` / `NOT_IN_SQUAD_STYLE` for the no-fill hairline costume. `SummaryCard.tsx` imports both and drops its local copies. **Fence exception:** `SummaryCard.tsx` edited under the Session fence — one import swap only, no visual change; Session's Participation card renders pixel-identically.

**Squad load pane — as rendered (28d, default).** Volume `103`, Intensity `100`, both as integers. Shared 40–160 track, tick label `100 — typical, like-for-like`, end labels `40` and `160`. Coverage line `across 16 of 24 sessions`. No trust mark, no HR mark, no delta suffix, no derivation clause — struck as directed. Blue axis dot before `SQUAD LOAD` is the only hue on the pane.

**Squad load pane — 7d re-timed.** Volume `103`, Intensity `101`. Coverage `across 4 of 7 sessions`.

**Withheld branch.** Cannot fire in this library (coverage 16/24 against a floor of one half). Implemented as a null-safety branch — em-dash in place of the value, band-only track, coverage line prints regardless. Never called in verification.

**Match-dominant regime.** Not built. Provably unreachable in this library.

**Availability pane — as rendered (28d).** `79%` at 52px + `at Full` at label size. Sub-line `278 of 352 · 19 training sessions` — the corrected wording (supersedes the copy-corrections file's `{trainings} trainings × {athletes} athletes` gloss, which would multiply to 361 against a true possible of 352).

**Tag counts and the invariant.** `Full 278 · Part 15 · Modified 6 · Rehab 4 · Injury 25 · Other 5 · not in squad 19`. Sum: 278+15+6+4+25+5 = 333; remainder 352−333 = **19**; 333+19 = **352 = possibleTrainingSessions**. ✓
Zero counts never print (none occurred in 28d; in 7d, `Rehab 0` was correctly absent).

**Availability pane — 7d re-timed.** `75%`, `86 of 114 · 6 training sessions`. Segments: `Full 86 · Part 5 · Modified 4 · Injury 12 · Other 1 · not in squad 6`. Sum: 86+5+4+12+1 = 108; remainder 114−108 = 6; 108+6 = 114. ✓

**Character line — as rendered.**
- 28d: `Five matches in four weeks; Lange went out through rehab, Köhler joined 7 July.` — matches the expected string byte-for-byte.
- 7d:  `One matches in one week; Tuesday is unrecorded, Sunday's session is not confirmed.`

**Grammar defect flagged, not silently fixed.** The 7d line reads `One matches in one week`. The composition template `{n} matches in {span}` is fixed, and the number-word substitution is prescribed — the rule produces that string. It is grammatically wrong ("One match", not "One matches"). I did not adjust the template or the rule; flagging for a follow-up prompt to decide whether the template branches on singular or the substitution flips.

**Defaults taken.**
- Foot strip: `border-t` on `--color-slate-50`, `text-[13px]`, primary text colour. One sentence, no adjectives, no day-indices — dates only.
- Not-in-squad segment/swatch: `bg-transparent` + inline `border: 1px solid var(--color-border)`, hairline outline, no fill. Lives in `participation-style.ts` as `NOT_IN_SQUAD_CLASS` + `NOT_IN_SQUAD_STYLE`.
- Deterministic date helpers (`dayMonthLong`, `weekdayLong`) inlined in `SummarySection.tsx` — parsed from ISO parts, `getUTCDay()` only, no `Intl`/`toLocale*`, no `new Date(iso)` without `Z`. `format-date.ts` not editable in this step's fence; kept the helpers scoped to the section.
- Number-word list `zero..twelve`; capitalized at sentence start. Numerals above twelve.
- Season span `{n} weeks` computed as `Math.round(w.days / 7)`.
- Gauge and availability values print via `String(Math.round(n))` — no `toLocaleString()` added; the seven pre-existing sites remain, logged in the previous sweep.
- Segment/swatch order fixed: `PARTICIPATION_TAGS` then not-in-squad remainder. Zero counts absent.

**Copy keys added.** Exactly the 17 keys listed in §6 of the prompt, verbatim strings. No hardcoded strings in the component.

**Gates.**
- Squint: the 52px `79%` is the loudest object; gauges sit well below it.
- Cold-read: end labels `40`/`160` and tick label `100 — typical, like-for-like` all print on the canvas.
- Words: one sentence on the page, and it is the character line.
- Colour: blue on squad-load, neutral slate everywhere else. No severity hue, no green.

**Anything else that looked wrong.**
- The 7d grammar quirk noted above.
- Nothing else — console clean, no hydration warning, no error overlay on either window.

---

## Workstream 04 · Step 3 corrections (Ali, 2026-07-20)

**Four items landed as a set. No new sections.**

**1 · Composition clause branches on match count.** Added `longi.character.compositionOne` (`"One match in {span}"`) and `longi.character.compositionNone` (`"No matches in {span}"`). The two-and-above template is unchanged. `characterLine` picks the form by `comp.matchSessions`. Zero case never fires in this library but is wired for data movement.

**As rendered (verified in `America/Los_Angeles`):**
- 28d: `Five matches in four weeks; Lange went out through rehab, Köhler joined 7 July.` — byte-identical to the prior render.
- 7d:  `One match in one week; Tuesday is unrecorded, Sunday's session is not confirmed.` — grammar defect closed.

**2 · Section headers unified.** `SummarySection`'s `<h2>` and the `SectionHeading` in `longitudinal.tsx` (used by Days and Athletes) both now use `type-section-h`. The inline `text-[20px] font-semibold tracking-tight` is gone from both. Longitudinal and Session share one section-header vocabulary at 17px.

**3 · Date helpers consolidated in `format-date.ts`.** `dayMonthLong(iso)` → `"7 July"` and `weekdayLong(iso)` → `"Tuesday"` now live there alongside `MONTHS_LONG` and `WEEKDAYS_LONG` arrays. Same module rules — no `Intl`, no `toLocale*`, no `new Date(iso)` without `Z`. `SummarySection.tsx` imports both and drops its local `MONTHS_LONG` / `WEEKDAYS_LONG` / `isoParts` / `dayMonthLong` / `weekdayLong`. One copy of the month and weekday arrays across the project.

**4 · Session Participation card — verified pixel-identical.** Screenshotted after the participation-style lift. `Full 13 · Part 3 · Injury 2 — Voss, Lange` — three segments in the bar and three swatches in the count row, textures unchanged (Full solid slate-500, Part 45° stripes, Injury 0° horizontal stripes), stripe angles unchanged, count chips unchanged. The 72% `full` read at the top-right of the card is unchanged. Nothing moved.

**Console clean on both routes.** No hydration warning, no error overlay.

**Nothing else flagged.**

## Workstream 05 · Participation renders in colour (time-boxed demo exception)

**Palette as landed** — hex lives only in `src/lib/participation-style.ts`:

| Tag          | Fill    | Family                          |
|--------------|---------|---------------------------------|
| Full         | #64748B | neutral slate                   |
| Part         | #14B8A6 | present-but-reduced, light (teal) |
| Modified     | #0F766E | present-but-reduced, dark  (teal) |
| Rehab        | #B08968 | unavailable, light          (brown) |
| Injury       | #8A5A44 | unavailable, dark           (brown) |
| Other        | #6B7280 | neutral residual                |
| not-in-squad | none    | 1px #CBD5E1 outline (Longi only) |

**Overlay opacity** — settled at `rgba(255,255,255,0.14)` for all four striped
tags (Part 45°/5px, Modified −45°/4px, Rehab 90°/5px, Injury 0°/3px on 7px
pitch). No per-tag opacity variance was needed: at 0.14 the stripes read as a
faint tooth on each fill without dragging the surface back toward the old
texture-first look. Full and Other stay flat by rule.

**Full/Other observation** — on the Longitudinal availability bar the two
neutrals sit adjacent as narrow segments (278 vs 5). At demo distance they
read as one continuous slate band split only by the 1px segment border; the
hue difference is present but sub-threshold. Not fixed — the ruling is that
Other stays flat and neither hue shifts. Left as an open question for the
post-meeting review.

**Data-hue collision check** — teals (#14B8A6 / #0F766E) sit well clear of
`--color-axis-work` (work blue), `--color-axis-cost` (cost purple), and the
brand green. Confirmed on the Session Summary page where the participation
bar sits below the Z1–Z5 blue ramp: teal reads distinctly against the blues.
No collision.

**Greyscale result** — bar screenshot in grayscale attached. Of the five
departure categories, Modified and Injury (the dark siblings) stay clearly
separable; Part and Rehab collapse toward the same mid-tone and rely on
stripe angle alone (45° vs 90°) to separate — legible up close, ambiguous at
arm's length; Other, which is untextured, becomes indistinguishable from
Full. **The greyscale gate fails as recorded**, per the ruling that hue
carries and neither textures nor lightness-only steps come back to rescue
it.

**Status** — this is a **time-boxed demo exception**, expiring at the
post-meeting review. It stands in for the open question of *six unordered
categories at roughly 10px without hue*, which the greyscale run confirms is
still unsolved. Not a ratified palette; do not extend, defend, or reuse.
