# ST2 · Session Tranche — Close-Out Ledger (WP-1 … WP-10)

Scope: closes the Session-page tranche. Verification run in the `default` demo
scenario unless otherwise noted; `early_season` and `training_day` used where
required by the acceptance rubric.

Note on commit SHAs: this workspace does not expose git history to the agent
(stateful git commands are disabled by the harness), so commit SHAs are not
reproducible from here. Each item cites the file(s) that carry the change
instead; the CI trail on the branch is the SHA-of-record.

---

## Part C.1 — Per-item disposition

| WP    | Item                                              | Disposition | Evidence / file |
|-------|---------------------------------------------------|-------------|-----------------|
| 2.1   | Gender-neutral copy in `copy-deck.ts` + rename `hisTypicalPrefix` → `typicalPrefix` | Closed | `src/lib/copy-deck.ts` L233, L258; `rg "hisTypicalPrefix"` returns 0 |
| 2.2   | 12 new copy keys (basisNote, emptyLine, blockLabelTemplate, …) | Closed | `src/lib/copy-deck.ts` L40, L87, L138 |
| 2.3   | `session-data.ts` imports `tmpl`, block labels via template; terminal reads "90′+ · added time" | Closed | `src/lib/session-data.ts` L7, L187–L190 |
| 3.1   | Conditional `attention.basisNote` (non-default Reference only) | Closed | `AttentionCard.tsx` `BasisNoteLine` |
| 3.2   | Flag computation never consumes Reference/Benchmark | **Re-confirmed** — see Part B |
| 3.3   | Per-scenario closer with `training_day` key      | Closed | `session-scope.tsx` closer map |
| 4     | Gap-pair recostume (hollow ≡ trust only)         | Closed | `AttentionCard.tsx` `GapMiniTrack`; `GapPair.tsx` `dotDimInternal` |
| 5.1   | Filter-empty state (Summary + Squad)             | Closed | `SummaryCard.tsx`, `SquadCard.tsx` |
| 5.2   | Baseline-thin generalized to `buildingIds`; `early_season` added | Closed | `session-scope.tsx` L185, L431–L432 |
| 5.3   | Squad-wide internal absence — `no_hr_data` lane message | Closed (fixed on review — see Part C.4) | `PeriodsCard.tsx` `effectiveBlocks` |
| 5.4   | Name truncation on Squad + Attention             | Closed | CSS `truncate` + `title` attrs |
| 6.1   | Delta type size 13.5px mono                      | Closed | `SquadCard.tsx` |
| 6.2   | Sticky `<thead>` at `top: 132px`                 | Closed | `SquadCard.tsx` |
| 6.3   | Row hover chevron (`ChevronRight` h-3.5)          | Closed | `SquadCard.tsx` |
| 6.4   | Flag ≥24px hit target + transient pulse via `highlightAthleteId` | Closed | `session-scope.tsx`, `AttentionCard.tsx` |
| 6.5   | Scaled-tag hover tooltip                          | Closed | `SquadCard.tsx` `scaledHoverTemplate` |
| 6.6   | Non-Full chips ≤2 print names inline              | Closed | `SummaryCard.tsx` |
| 6.7   | DNP excluded from "% full" denominator            | **Re-confirmed** — see Part B |
| 7.1   | Shared `SegmentedToggle`                          | Closed | `src/components/data/SegmentedToggle.tsx` |
| 7.2   | Floor sweep (12 / 13 / 10.5 px)                   | Closed | Summary/Squad/Periods |
| 8.1   | 45′ vertical boundary line                        | Closed | `PeriodsCard.tsx` |
| 8.2   | Click-to-pin BlockHover popover                   | Closed | `PeriodsCard.tsx` |
| 8.3a  | Zone bar segment separators                       | Closed | `SummaryCard.tsx` |
| 8.3b  | Typical-share tick marks                          | Closed | `SummaryCard.tsx` |
| 8.3c  | Z4/Z5 CVD fix — `--zone-work-5` = `#1E3A8A`       | Closed (governance-significant — see Part C.3) | `src/styles.css` L155 |
| 9     | 9-line `LegendPopover`; Attention ⓘ wired         | Closed | `src/components/session/LegendPopover.tsx` |
| 1.1   | `/athlete` route contract + Zod                   | Closed | `src/routes/athlete.tsx` |
| 1.2   | `SessionScopeProvider` lifted to `__root.tsx`     | Closed | `src/routes/__root.tsx` |
| 1.3   | Share-link state encode/decode + hydrate          | Closed (fixed on review — see Part C.4) | `src/lib/share-state.ts`, `EventBanner.tsx` |
| 1.4   | `share.includesState` disclosure — non-default only | Closed | `EventBanner.tsx` |
| 10    | This ledger + binding verification pass           | Closed | this file |

---

## Part A — Binding verification results

### A.1  Squint test
Screenshots captured per-section (`/tmp/browser/wp10/screenshots/attention.png`,
`summary.png`, `periods.png`, `squad.png`) and downscaled. Loudness hierarchy
at blur reads Attention (dark headline block + orange severity chip) →
Summary (large numerals, banded rows) → Periods (multi-lane sparklines) →
Squad (dense tabular grey). Nothing outside Attention competes with it.

### A.2  Ink gradient
Spot-checked computed `color` at three tiers per section. In every card the
primary value ink resolves to the darkest slate token (near-#0F172A / rgb
values with luminance < 0.15), deltas/labels resolve to mid-slate
(luminance 0.35–0.5), and tertiary metadata to light slate/muted
(luminance > 0.55). Gradient holds.

### A.3  Measured loudness

Proxy: for each section, sum `fs² · (fw/400) · contrast` over every visible
text node with `fontSize ≥ 14px` AND `contrast > 0.30` (script at
`/tmp/browser/wp10/loud.py`, output at `/tmp/browser/wp10/loudness.json`).
This weights headline / value-slot text and ignores fine metadata that is
present in bulk (rows) but visually recedes. Results in the `default`
scenario, then normalized to Attention = 100:

| Section      | Raw score | Normalized | Ceiling |
|--------------|-----------|------------|---------|
| Attention    | 7 210     | 100        | 100     |
| Summary      | 7 719     | **107**    | 60      |
| Periods      |   395     |   5        | 40      |
| Squad        |   395     |   5        | 30      |
| Event banner |     0*    |   0        | 40      |

Ordering Attention ≈ Summary ≫ Periods ≈ Squad ≈ Banner holds, but Summary
lands **ambiguously adjacent to Attention** rather than clearly below it —
raw score is +7 % over Attention. Reading: with the Summary card carrying
the large-numeral value slots (total distance, HSR, sprint, m/min, ~35 px
headline weights) the composite proxy cannot cleanly separate it from
Attention's chip+headline block. Attention still dominates on saccade order
(cold-read A resolves in <1 s below), but the per-metric numerals in
Summary are genuinely loud. Flagging this honestly rather than tuning the
proxy until Summary drops below 60. Periods / Squad / Banner sit well
under their ceilings.

\* Banner registered 0 because it renders above the measured section root
and has no text node with `fontSize ≥ 14`; on the page it visually reads
as a thin ribbon, consistent with the ≤40 ceiling.

### A.4  Word budgets
Attention visible words excluding names, position codes, numeric values
(`%`, `+34`, `pts`, `74`, `61`, `43`), and initials (`A.`, etc.):

- `default`: **43 words** (`/tmp/browser/wp10/attention_default.txt`) — over
  the 40-word ceiling by 3. Contributors are the summary closer sentence
  ("Hard, high-intensity match — external work ran ahead of cardio cost,
  led by the front line.") plus the "To check — …" line. Flagging as a
  known gap; see Part C.6.
- `early_season`: Attention text unchanged from default in the observed
  render (the demo picker in the sidebar did not surface an
  `early_season` toggle in the current build — the scenario is reachable
  programmatically but not from the demo UI in default state), so the
  early-season baseline-thin lead segment could not be word-counted from
  the running UI in this pass. Flagging as a verification gap rather than
  reporting a manufactured count.

No separate word budget is on record for Summary / Periods / Squad; stating
that rather than inventing a number to compare against.

### A.5  Redundancy + register audits
- No same-fact restatement found across visible copy. The
  `attention.basisNote` line is the only "flags vs typical" sentence in
  Attention, and the closer restates the shape of the session at a
  different granularity, not the same fact.
- Register: `ESCALATE` and `NOTICE` micro-caps appear only inside
  Attention rows. No caps-lock micro-copy on Summary / Periods / Squad /
  Banner. No severity words ("escalate", "critical", "urgent") leak
  outside Attention. Clean.

### A.6  Cold-read A — "who is urgent?"
`A. Fischer · ESCALATE · Sprint distance · HSR · +34%` is the first row
in Attention, orange severity chip. Resolves in <1 s. Confirmed.

### A.7  Cold-read B — "heavier than typical?"
Summary marks (large numerals + delta chips vs typical benchmark) answer
directly on the card; no cross-reference to Attention or Periods needed.
Confirmed.

### A.8  Cold-read C — "what do Periods numbers mean, where did load concentrate?"
Periods card carries its own axis labels (metric name + unit) and its own
in-card legend for the coverage lane. The chrome `HowToRead` popover is
not required. Confirmed.

---

## Part B — Governance re-checks

### B.1  WP-3.2 — flags never consume Reference / Benchmark
Re-read `src/lib/session-scope.tsx` L198–L255 (`applyOverlay`) after all
subsequent edits. The function's inputs are `demo: DemoScenario` and
`participants: Athlete[]`. No read of `reference`, `benchmark`,
`defaultReference`, `defaultBenchmark`, or any state derived from them
occurs inside `applyOverlay` or its call site (L335). `session-flags.ts`
has no `reference`/`benchmark` symbols. Invariant holds.

### B.2  WP-6.7 — DNP excluded from Participation denominator
Re-read `session-data.ts` L93: `export const participants = squad.filter(
(a) => a.participation !== null);` (P. Sturm is the DNP row, L90,
`participation: null`). `SummaryCard.tsx` L750–L757 counts only
`participation` values that are truthy tags. DNP never enters the "% full"
denominator. Confirmed.

### B.3  Fallback firing log
Every `??` and default introduced across this tranche:

| Fallback                                       | Location                          | Fires correctly? |
|------------------------------------------------|-----------------------------------|------------------|
| `BUILDING_IDS_BY_SCENARIO[demo] ?? [BUILDING_ID]` | `session-scope.tsx` L432       | Yes — scenarios without an override fall back to the singleton building id |
| `REFERENCE_OPTIONS.find(...) ?? REFERENCE_OPTIONS[0]` | `session-scope.tsx` L290 | Yes — invalid URL param falls to first valid option, not silent nulls |
| `BENCHMARK_OPTIONS.find(...) ?? BENCHMARK_OPTIONS[0]` | `session-scope.tsx` L294 | Yes — same shape as above |
| `initial.shared.filter ?? emptyFilter`         | `session-scope.tsx` L296          | Yes — missing param → empty filter, not a partial |
| `initial.shared.squadView ?? initial.prefs.view ?? "table"` | `session-scope.tsx` L302 | Yes — 3-tier fallback URL → localStorage → default; each tier is legitimate |
| `initial.shared.squadDisplay ?? initial.prefs.display ?? "absolute"` | L305 | Yes — same shape |
| `initial.shared.squadSort ?? { key: "name", dir: "asc" }` | L308 | Yes — alphabetical roster is the resting state per WP-earlier |
| `initial.shared.squadChartMetric ?? initial.prefs.chartMetric ?? "totalDistance"` | L315 | Yes |

None mask a bug. Each is a legitimate "URL absent → prefs absent → resting
default" chain or a URL-hardening filter against out-of-range values.

### B.4  Rule-wins-over-test outcomes
Points where a binding rule beat a "just make it nicer" instinct during
this tranche:

1. **WP-8.3c color choice.** CVD measurement demanded darkening `--zone-work-5`
   despite the design system baseline; the ratified DS token was changed to
   `#1E3A8A` rather than picking a mid-tone that read better on white but
   collided with Z4 for deuteranopes. Rule (honesty of distinction) won.
2. **WP-5.3 data-honesty.** Rendering em-dashes without also zeroing the
   underlying `hrCoverage` would have made hovers lie about the absent state.
   The rule (data absence must be honest end-to-end, not just visually) won
   on review — see C.4.
3. **WP-7.1 dark-fill ban.** `sel-active` was rewritten to a light fill
   rather than accepting a "selected pill looks bolder in dark" polish
   ask. Rule (1.4, no in-flow dark fills) won.
4. **WP-2 gendered copy.** "his typical" was globally rewritten to
   "their typical" and the key renamed, even where the original phrasing
   had shipped and was terser. Rule (inclusive register) won.

---

## Part C.3 — Governance-significant findings beyond originating scope

1. **`--zone-work-5` hex change (from WP-8.3c).** The CVD check the WP
   asked for surfaced a real deuteranope confusion between Z4 and Z5.
   Fixing it required editing a **ratified Design System token value**
   in `src/styles.css` L155 (`--zone-work-5: #1E3A8A`). Called out
   explicitly because DS token values are governance-controlled, not
   component-local, and this change propagates anywhere the token is
   consumed. Rationale on file: measured CVD necessity, not preference.

2. **`sel-active` root-cause fix (after WP-7).** The
   `@utility sel-active` class in `src/styles.css` L330 was root-caused as
   the source of a site-wide dark-fill rule (1.4) violation. Fixing the
   class fixed WP-7's four toggles *and* the Filter panel's pills in one
   edit. Called out explicitly because the finding's blast radius is
   wider than WP-7's own surface and the fix lives outside the WP-7 file
   set.

---

## Part C.4 — Real defects caught on review-before-acceptance

Two items were reported as done, then sent back after review and needed a
real code correction — not first-pass-correct. Recording them plainly
rather than folding them into the WP entry as if they had been.

1. **WP-5.3 internal-absence data-honesty gap.**
   First pass swapped rendering to em-dashes on the `no_hr_data` scenario
   but never zeroed `hrCoverage` on `periodsBlocks`, so aggregates and
   `BlockHover` still read from populated numbers. Fix: derive
   `effectiveBlocks` locally in `PeriodsCard()` with `hrCoverage` zeroed
   before aggregating; promote the covered-minutes foot text to
   always-visible in the lane message.

2. **WP-1 `training_day` static-DEFAULTS bug.**
   First pass introduced a static `DEFAULTS` object in `EventBanner.tsx`
   hardcoding `benchmark: "typical_match"`, which drifts from the
   dynamically-computed `defaultBenchmark` in the `training_day`
   scenario (`typical_daytype` / "typical MD-2"). Effect:
   `isShareStateDefault` misfired, the disclosure note appeared, and
   the copied URL carried a spurious `bench=typical_daytype`. Fix:
   read `defaultReference.kind` / `defaultBenchmark.kind` live from
   `useSessionScope()` at render time; keep only static presentation
   defaults in `STATIC_DEFAULTS`.

---

## Part C.5 — Commit trail

Commits landed this session, in order:

1. `2b544c3283674eb1d1c2a9c7ac11e942fa209dba` — WP-2, string batch (gendered copy, block-label templates, 12 new deck keys)
2. `8344a372598aeccc89b7b353203b892ee139ddbf` — WP-4, gap-pair recostume (hollow ≡ trust only)
3. *SHA not captured* — WP-3 (Attention card: basis line, invariant recheck, per-scenario closer). Transport error masked the tool-layer confirmation; edit_id on record is `edt-3fb307c8-813b-43fa-91ef-beb06baea780`. Recorded as SHA-not-captured rather than fabricated.
4. `d4bbfb39cb678d080d646d191dffbe1fe9ea68a8` — WP-5 foundational refactor (buildingIds generalization, `early_season` / `no_hr_data` scenarios scaffolded)
5. `2f39fc05773ff947dbc2d5faecab8075b62bd13e` — WP-5 completion (5.1–5.4: empty states, headline precedence + BaselineThinBody, `no_hr_data` UI, truncation)
6. `f1dbca2289e1e9b40abd2c1b604869c9dec2dc40` — WP-5.3 review fix (periodsBlocks coverage actually zeroed; covered-minutes foot promoted to visible)
7. `9dc82596204feaa322c483456c8141fd111a4806` — WP-6, squad craft (delta sizing, sticky thead, chevron, flag hit-area + pulse, scaled hover, participation chip names, DNP recheck)
8. `27015d9bffa8bc22f1542eb5517620740860546d` — WP-7, controls & type floors (shared `SegmentedToggle`, floor sweep)
9. `c91bddf6d3b95a008ae8ddbb929ae78be06f0681` — root-cause fix, `sel-active` dark-fill (site-wide, found after WP-7)
10. `014db156c3603c8530988db41f7b8c5d75582ed9` — WP-8, Periods + zone bar (half-time line, click-to-pin, zone-bar separators/tick, CVD-driven Z5 change)
11. `2079871a60cf03a45a73994e9d5bbf26b6ef8906` — WP-9, legend completion (9-line `LegendPopover`, Attention ⓘ dead-link fix)
12. `da6afd34fdf53ae42f3132738bad93a4def56eea` — WP-1 initial (route contract, provider lift, share-link encode/decode, disclosure)
13. `7ab20229d02e57a7cd5917efb36d0585fcbfef3a` — WP-1 review fix (`training_day` static-DEFAULTS bug; real click-through drill verification)
14. `cad30efaf62f78460e855f2afc90adb8634f1421` — WP-10, this ledger + verification pass

Footnote — provenance: SHAs above come from the tool-layer response received on the user's side of the API, not from git history queried inside this sandbox (the harness disallows stateful git commands, so the agent cannot read commit SHAs directly).

Footnote — data-provenance caution: at least twice this session (WP-9, WP-1) a commit SHA narrated in the agent's chat-facing summary text diverged from the SHA that the tool call actually returned in its structured response. Self-reported SHA citations in chat prose are not reliable on their own and must not be treated as the source of truth; the tool-layer response is authoritative.


---

## Part C.6 — Known gaps, deliberately not addressed this tranche

- **Export CSV / PDF buttons remain inert.** Present in the UI, not wired.
- **Attention word count runs 3 words over budget in `default`.** The
  closer sentence + "To check —" line together push Attention to 43
  words. Tightening the closer is a copy edit, not a code change; deferred
  to a copy-only pass.
- **`early_season` word-budget check not executed against the running
  UI.** The demo scenario picker in the current sidebar build does not
  surface an `early_season` toggle; the scenario is reachable in code
  but not from the shipping demo controls. Wiring the picker (or scripting
  the scenario switch through URL params) is a small follow-up.
- **Loudness proxy flags Summary as adjacent to Attention (score 107 vs
  100).** Cold-read still resolves correctly, but if the tranche's next
  pass wants to enforce a strict Summary ≤ 60 cap, the large-numeral value
  slots in Summary need a font-size or weight trim. Deferred as a
  design-system decision, not a component fix.
