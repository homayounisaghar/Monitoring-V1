/**
 * ST2 — Longitudinal derivation checks (Workstream 04 · prompt 1/6).
 *
 * Runnable script. Assertions + report. Exits non-zero on failure.
 */

import {
  demoSessions, demoDays, demoRecords, demoAthletes,
  DEMO_TODAY, SEASON_START_ISO,
} from "./demo-library";
import {
  windowFor, windowComposition, daySeries,
  squadLoadGauges, availability, athleteAvailabilityRanking,
  windowTotals, sessionDayIndex, sessionCategories,
  LONGI_WINDOW_DEFAULT, GAUGE_MIN_COVERAGE, HR_COVERAGE_THRESHOLD,
  LONGI_METRICS,
  type Horizon, type LongiMetric,
} from "./longitudinal-data";

type Check = { name: string; pass: boolean; detail: string };
const checks: Check[] = [];
const push = (name: string, pass: boolean, detail: string) => checks.push({ name, pass, detail });

function fmt(n: number | null, digits = 0): string {
  if (n == null) return "—";
  if (!Number.isFinite(n)) return "∞";
  return n.toFixed(digits);
}
function pad(s: string, n: number, right = false): string {
  if (s.length >= n) return s.slice(0, n);
  return right ? " ".repeat(n - s.length) + s : s + " ".repeat(n - s.length);
}
function addDays(iso: string, n: number): string {
  const t = Date.UTC(
    parseInt(iso.slice(0, 4), 10),
    parseInt(iso.slice(5, 7), 10) - 1,
    parseInt(iso.slice(8, 10), 10),
  ) + n * 86_400_000;
  const d = new Date(t);
  return `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, "0")}-${String(d.getUTCDate()).padStart(2, "0")}`;
}
function diffDays(a: string, b: string): number {
  const p = (iso: string) => Date.UTC(
    parseInt(iso.slice(0, 4), 10),
    parseInt(iso.slice(5, 7), 10) - 1,
    parseInt(iso.slice(8, 10), 10),
  );
  return Math.round((p(a) - p(b)) / 86_400_000);
}

/* ───────── assertions (§C1) ───────── */

const w28 = windowFor(28);
const comp28 = windowComposition(w28);
push("28-day window has 28 days", comp28.days === 28, `${comp28.days}`);
push("28-day sessions = 24", comp28.sessions === 24, `${comp28.sessions}`);
push("28-day matches = 5", comp28.matchSessions === 5, `${comp28.matchSessions}`);
push("28-day non-match = 19", comp28.nonMatchSessions === 19, `${comp28.nonMatchSessions}`);
push("28-day rest days = 4", comp28.restDays === 4, `${comp28.restDays}`);
push("28-day no-record days = 1", comp28.noRecordDays === 1, `${comp28.noRecordDays}`);

const series28 = daySeries(w28);
push("28-day series length equals horizon", series28.length === 28, `${series28.length}`);

const missingHasNulls = series28
  .filter((d) => d.kind === "missing")
  .every((d) => LONGI_METRICS.every((m) => d.perMetric[m] === null));
push("Every missing day has null values, never zero", missingHasNulls, "");

const restIsZero = series28
  .filter((d) => d.kind === "rest")
  .every((d) => LONGI_METRICS.every((m) => d.perMetric[m] === 0));
push("Every rest day carries zero, not null", restIsZero, "");

const everyDayHasKind = series28.every((d) => d.kind === "session" || d.kind === "rest" || d.kind === "missing");
push("Every day in series has a kind", everyDayHasKind, "");

// Gauges cover identical (session, athlete) pair sets — enforced by construction
// because both bases use the same expectedSumForSession contributor logic.
// Verify by re-running expectedSum under both bases for the 28-day window.
import { expectedSumForSession } from "./demo-typicals";
const w28Sessions = demoSessions.filter((s) => s.dateISO >= w28.startISO && s.dateISO <= w28.endISO);
let pairSetOk = true;
for (const s of w28Sessions) {
  const ev = expectedSumForSession(s.id, "typicalDuration");
  const ei = expectedSumForSession(s.id, "actualMinutes");
  if (ev.state === "computed" && ei.state === "computed") {
    const a = [...ev.contributed].sort().join(",");
    const b = [...ei.contributed].sort().join(",");
    if (a !== b) pairSetOk = false;
  } else if (ev.state !== ei.state) {
    pairSetOk = false;
  }
}
push("Both gauge ratios cover identical (session, athlete) pair sets", pairSetOk, "");

const avail28 = availability(w28);
push("Availability numerator ≤ denominator",
  avail28.fullTrainingSessions <= avail28.possibleTrainingSessions,
  `${avail28.fullTrainingSessions}/${avail28.possibleTrainingSessions}`);

const vsTypWithheldOnAnyWithheldExpected = series28
  .filter((d) => d.kind === "session")
  .every((d) => {
    const anyExpWithheld = d.sessionIds.some((sid) => expectedSumForSession(sid, "typicalDuration").state === "withheld");
    if (!anyExpWithheld) return true;
    return LONGI_METRICS.every((m) => d.vsTypical[m]?.state === "withheld");
  });
push("Vs-typical withheld whenever expected side withheld", vsTypWithheldOnAnyWithheldExpected, "");

// Every horizon: day series length == horizon.
let horizonLenOk = true;
for (const h of [7, 14, 28] as Horizon[]) {
  const w = windowFor(h);
  const s = daySeries(w);
  if (s.length !== w.days) horizonLenOk = false;
}
{
  const w = windowFor("season");
  const s = daySeries(w);
  if (s.length !== w.days) horizonLenOk = false;
}
push("Every horizon's day series length equals its horizon", horizonLenOk, "");

// No athlete's A:C is computed from a synthetic zero. A "synthetic zero" would
// be a fabricated zero for a missing day. Our A:C code never enters a missing
// day into the average (only real records; rest records are real zeros).
// Assertion: for every computed A:C, the daysOfData matches the count of
// dates the athlete actually has records on within the window.
const wt28 = windowTotals(w28);
let acSynthOk = true;
for (const at of wt28.perAthlete) {
  if (at.ac.state === "computed") {
    const dates = new Set(
      demoRecords.filter((r) => r.athleteId === at.athlete.id && r.dateISO >= w28.startISO && r.dateISO <= w28.endISO)
        .map((r) => r.dateISO),
    );
    if (dates.size !== at.ac.daysOfData) acSynthOk = false;
  }
}
push("A:C daysOfData matches real record dates (no synthetic zeros)", acSynthOk, "");

// Exactly one athlete's A:C withholds — Köhler (joined 2026-07-07, after the
// 28-day window's first day 2026-06-22). Everyone else has full history.
const acWithheldCount = wt28.perAthlete.filter((at) => at.ac.state === "withheld").length;
const acWithheldNames = wt28.perAthlete.filter((at) => at.ac.state === "withheld").map((at) => at.athlete.id).join(",");
push("Exactly one athlete's A:C withholds (mid-window joiner)", acWithheldCount === 1 && acWithheldNames === "koehler", `${acWithheldCount}: ${acWithheldNames}`);
{
push("A:C daysOfData matches real record dates (no synthetic zeros)", acSynthOk, "");

/* ───────── report (§C2) ───────── */

const lines: string[] = [];
lines.push("");
lines.push("═══ 1. Composition per horizon ═══");
lines.push(pad("horizon", 12) + pad("days", 6, true) + pad("sess", 6, true) + pad("train", 6, true) + pad("match", 6, true) + pad("rest", 6, true) + pad("norec", 7, true) + pad("dbl", 5, true));
for (const h of [7, 14, 28] as Horizon[]) {
  const w = windowFor(h);
  const c = windowComposition(w);
  lines.push(pad(`${h}d`, 12) + pad(String(c.days), 6, true) + pad(String(c.sessions), 6, true) + pad(String(c.nonMatchSessions), 6, true) + pad(String(c.matchSessions), 6, true) + pad(String(c.restDays), 6, true) + pad(String(c.noRecordDays), 7, true) + pad(String(c.doubleSessionDays), 5, true));
}
{
  const w = windowFor("season");
  const c = windowComposition(w);
  const weeks = Math.floor(diffDays(DEMO_TODAY, SEASON_START_ISO) / 7);
  lines.push(pad("season", 12) + pad(String(c.days), 6, true) + pad(String(c.sessions), 6, true) + pad(String(c.nonMatchSessions), 6, true) + pad(String(c.matchSessions), 6, true) + pad(String(c.restDays), 6, true) + pad(String(c.noRecordDays), 7, true) + pad(String(c.doubleSessionDays), 5, true));
  lines.push(`  season start = ${SEASON_START_ISO}, whole weeks to ${DEMO_TODAY} = ${weeks}`);
}

lines.push("");
lines.push("═══ 2. Full 28-day series ═══");
lines.push(pad("date", 12) + pad("code", 6) + pad("kind", 9) + pad("ss", 3, true) + pad("ath", 4, true) + pad("avgTD", 8, true) + pad("avgCL", 7, true) + pad("avgSRPE", 8, true) + pad("sRPE", 8, true) + pad("hrMin", 7, true));
for (const d of series28) {
  const avgTD = d.perMetric.totalDistance;
  const avgCL = d.perMetric.cardioLoad;
  const avgSR = d.perMetric.srpeAU;
  const sr = d.kind === "session" && d.srpeCollected ? `${d.srpeSubmitted}/${d.srpeEligible}` : (d.kind === "session" ? "n/c" : "—");
  lines.push(
    pad(d.dateISO, 12) +
    pad(d.dayCode ?? "—", 6) +
    pad(d.kind, 9) +
    pad(String(d.sessionIds.length), 3, true) +
    pad(String(d.athletesTrained), 4, true) +
    pad(fmt(avgTD ?? null, 0), 8, true) +
    pad(fmt(avgCL ?? null, 0), 7, true) +
    pad(fmt(avgSR ?? null, 0), 8, true) +
    pad(sr, 8, true) +
    pad(fmt(d.hrCoverageMin, 0), 7, true),
  );
}

lines.push("");
lines.push("═══ 3. Domain calibration (whole library, avg per athlete who trained) ═══");
lines.push(pad("metric", 16) + pad("highest", 10, true) + pad("2nd", 10, true) + pad("p95", 10, true) + pad("date-of-max", 14));
// Build day series across the whole library (season) to get avg-per-athlete-who-trained per day.
const wSeason = windowFor("season");
const seasonSeries = daySeries(wSeason);
const domainMetrics: LongiMetric[] = ["totalDistance", "hsr", "cardioLoad", "srpeAU"];
for (const m of domainMetrics) {
  const rows: { date: string; v: number }[] = [];
  for (const d of seasonSeries) {
    if (d.kind !== "session") continue;
    const v = d.perMetric[m];
    if (v == null) continue;
    rows.push({ date: d.dateISO, v });
  }
  rows.sort((a, b) => b.v - a.v);
  const highest = rows[0];
  const second = rows[1];
  const sortedAsc = [...rows].sort((a, b) => a.v - b.v);
  const p95Idx = Math.min(sortedAsc.length - 1, Math.floor(0.95 * (sortedAsc.length - 1)));
  const p95 = sortedAsc[p95Idx];
  lines.push(
    pad(m, 16) +
    pad(fmt(highest?.v ?? null, 0), 10, true) +
    pad(fmt(second?.v ?? null, 0), 10, true) +
    pad(fmt(p95?.v ?? null, 0), 10, true) +
    pad(highest?.date ?? "—", 14),
  );
}

lines.push("");
lines.push("═══ 4. Gauges ═══");
const g28 = squadLoadGauges(w28);
if (g28.state === "computed") {
  lines.push(`28-day: Volume ${g28.volumePct.toFixed(1)}%  Intensity ${g28.intensityPct.toFixed(1)}%  (${g28.contributingSessions} of ${g28.windowSessions} sessions; match-dominant=${g28.matchDominant})`);
} else {
  lines.push(`28-day: withheld (${g28.reason}) contrib=${g28.contributingSessions}/${g28.windowSessions}`);
}
// The 14-day probe: 14 days ending 2026-01-07 is before SEASON_START — unreachable.
// Find the most match-dense 14-day window in the library instead.
const targetEnd = "2026-01-07";
const targetReachable = targetEnd >= SEASON_START_ISO && targetEnd <= DEMO_TODAY;
if (targetReachable) {
  const w14 = windowFor(14, targetEnd);
  const g = squadLoadGauges(w14);
  lines.push(`  used range ending ${targetEnd}: ${g.state === "computed" ? `Vol ${g.volumePct.toFixed(1)}% Int ${g.intensityPct.toFixed(1)}% (${g.contributingSessions}/${g.windowSessions}, match-dominant=${g.matchDominant})` : `withheld ${g.reason}`}`);
} else {
  // Most match-dense 14-day window: slide across every possible end date and count matches.
  let best: { end: string; matches: number } | null = null;
  for (let i = 0; i < demoDays.length; i++) {
    const end = demoDays[i].dateISO;
    if (diffDays(end, SEASON_START_ISO) < 13) continue;
    const w = windowFor(14, end);
    const c = windowComposition(w);
    if (!best || c.matchSessions > best.matches) best = { end, matches: c.matchSessions };
  }
  if (best) {
    const w14 = windowFor(14, best.end);
    const g = squadLoadGauges(w14);
    if (g.state === "computed") {
      lines.push(`  target ${targetEnd} unreachable; used most match-dense 14-day window ending ${best.end} (${best.matches} matches): Vol ${g.volumePct.toFixed(1)}% Int ${g.intensityPct.toFixed(1)}% (${g.contributingSessions}/${g.windowSessions}, match-dominant=${g.matchDominant})`);
    } else {
      lines.push(`  target ${targetEnd} unreachable; most match-dense 14-day window ending ${best.end}: withheld ${g.reason}`);
    }
  }
}

lines.push("");
lines.push("═══ 5. Availability per horizon ═══");
lines.push(pad("horizon", 10) + pad("full/poss", 14) + pad("%", 7, true) + pad("trains", 8, true) + pad("ath", 5, true) + " tags");
for (const h of [7, 14, 28, "season"] as Horizon[]) {
  const w = windowFor(h);
  const a = availability(w);
  const tagStr = Object.entries(a.tagCounts).map(([t, n]) => `${t}=${n}`).join(" ") + (a.notInSquadCount ? ` notInSquad=${a.notInSquadCount}` : "");
  lines.push(
    pad(String(h), 10) +
    pad(`${a.fullTrainingSessions}/${a.possibleTrainingSessions}`, 14) +
    pad(a.fullOfPossiblePct.toFixed(1), 7, true) +
    pad(String(a.trainingSessions), 8, true) +
    pad(String(a.athletesAtWindowEnd), 5, true) +
    " " + tagStr,
  );
}

lines.push("");
lines.push("═══ 6. Availability ranking (28-day) ═══");
lines.push(pad("athlete", 18) + pad("full/avail", 12) + pad("%", 6, true) + pad("flag", 6) + " tags");
const rank = athleteAvailabilityRanking(w28);
for (const r of rank) {
  const full = r.tagCounts.Full ?? 0;
  const tagStr = Object.entries(r.tagCounts).map(([t, n]) => `${t}=${n}`).join(" ") + (r.notInSquadCount ? ` NIS=${r.notInSquadCount}` : "");
  lines.push(
    pad(r.athlete.name, 18) +
    pad(`${full}/${r.availableSessions}`, 12) +
    pad((r.fullFraction * 100).toFixed(0), 6, true) +
    pad(r.attentionFlagged ? "att" : "", 6) +
    " " + tagStr,
  );
}

lines.push("");
lines.push("═══ 7. Zero-participation athletes (28-day) ═══");
for (const z of wt28.zeroParticipation) {
  lines.push(`  ${z.athlete.name.padEnd(18)}  reason=${z.reason}`);
}
if (wt28.zeroParticipation.length === 0) lines.push("  (none)");

lines.push("");
lines.push("═══ 8. A:C on total distance (28-day) ═══");
let acComputed = 0;
let acWithheld = 0;
const withheldBy: Record<string, number> = {};
let lowest: { name: string; v: number } | null = null;
let highest: { name: string; v: number } | null = null;
for (const at of wt28.perAthlete) {
  if (at.ac.state === "withheld") {
    acWithheld++;
    withheldBy[at.ac.reason] = (withheldBy[at.ac.reason] ?? 0) + 1;
  } else {
    const v = at.ac.perMetric.totalDistance;
    if (v == null) continue;
    acComputed++;
    if (!lowest || v < lowest.v) lowest = { name: at.athlete.name, v };
    if (!highest || v > highest.v) highest = { name: at.athlete.name, v };
  }
}
lines.push(`  computed=${acComputed} withheld=${acWithheld} (${Object.entries(withheldBy).map(([k, v]) => `${k}:${v}`).join(", ") || "—"})`);
lines.push(`  lowest = ${lowest?.name} ${lowest ? lowest.v.toFixed(3) : "—"}`);
lines.push(`  highest = ${highest?.name} ${highest ? highest.v.toFixed(3) : "—"}`);

lines.push("");
lines.push("═══ 9. Named facts ═══");
const koehler = demoAthletes.find((a) => a.id === "koehler")!;
lines.push(`  Köhler joined: ${koehler.joinedISO}`);
const langeFirst = series28[0].dateISO;
const langeLast = series28[series28.length - 1].dateISO;
const langeRecFor = (date: string) => demoRecords.find((r) => r.athleteId === "lange" && r.dateISO === date && r.sessionId != null);
lines.push(`  Lange on ${langeFirst}: ${langeRecFor(langeFirst)?.participation ?? "no-session"}`);
lines.push(`  Lange on ${langeLast}: ${langeRecFor(langeLast)?.participation ?? "no-session"}`);
const langeTagChanges: string[] = [];
let prev: string | null = null;
for (const d of series28) {
  if (d.kind !== "session") continue;
  const r = langeRecFor(d.dateISO);
  const tag = r?.participation ?? null;
  if (tag && tag !== prev) { langeTagChanges.push(`${d.dateISO}=${tag}`); prev = tag; }
}
lines.push(`  Lange tag changes: ${langeTagChanges.join(" ")}`);
lines.push(`  Never submits sRPE: M. Frei (id=frei)`);
const jul02 = demoRecords.filter((r) => r.dateISO === "2026-07-02" && (r.hrCoveragePct ?? 100) < HR_COVERAGE_THRESHOLD);
lines.push(`  Below HR threshold on 2026-07-02: ${jul02.map((r) => `${r.athleteId}=${r.hrCoveragePct}`).join(", ")}`);

lines.push("");
lines.push("═══ 10. Spearman ρ (avg TD vs avg CL, day series) ═══");
type Pair = { td: number; cl: number };
const pairs: Pair[] = [];
for (const d of series28) {
  const td = d.perMetric.totalDistance;
  const cl = d.perMetric.cardioLoad;
  if (td == null || cl == null) continue;
  pairs.push({ td, cl });
}
function ranks(vals: number[]): number[] {
  const idx = vals.map((v, i) => ({ v, i })).sort((a, b) => a.v - b.v);
  const r = new Array<number>(vals.length);
  let i = 0;
  while (i < idx.length) {
    let j = i;
    while (j + 1 < idx.length && idx[j + 1].v === idx[i].v) j++;
    const avg = (i + j) / 2 + 1;
    for (let k = i; k <= j; k++) r[idx[k].i] = avg;
    i = j + 1;
  }
  return r;
}
const rTD = ranks(pairs.map((p) => p.td));
const rCL = ranks(pairs.map((p) => p.cl));
const n = pairs.length;
let dsq = 0;
for (let i = 0; i < n; i++) { const d = rTD[i] - rCL[i]; dsq += d * d; }
const rho = n > 1 ? 1 - (6 * dsq) / (n * (n * n - 1)) : NaN;
lines.push(`  n=${n}  ρ=${rho.toFixed(3)}`);

lines.push("");
lines.push("═══ Session category filter (28-day) ═══");
lines.push(`  ${sessionCategories(w28).join(", ")}`);

lines.push("");
lines.push(`═══ Constants ═══  LONGI_WINDOW_DEFAULT=${LONGI_WINDOW_DEFAULT}  GAUGE_MIN_COVERAGE=${GAUGE_MIN_COVERAGE.toFixed(4)}  HR_COVERAGE_THRESHOLD=${HR_COVERAGE_THRESHOLD}`);

// Focus helper sanity
const dortmundIdx = sessionDayIndex("s-2026-07-04-dortmund", w28);
lines.push(`  sessionDayIndex(dortmund, 28d) = ${dortmundIdx}   (0-indexed; 18 Jul is day index 26 of the 28-day window)`);

/* ───────── output ───────── */

declare const process: { argv: string[]; exit(n: number): never; stdout: { write(s: string): boolean } } | undefined;
if (typeof process !== "undefined" && process.argv[1] && process.argv[1].endsWith("longitudinal-data.check.ts")) {
  const padL = (s: string, n: number) => (s + " ".repeat(n)).slice(0, n);
  for (const r of checks) {
    console.log(`${r.pass ? "PASS" : "FAIL"}  ${padL(r.name, 62)}  ${r.detail}`);
  }
  const fails = checks.filter((r) => !r.pass).length;
  console.log(`\n${checks.length - fails}/${checks.length} passed`);
  for (const l of lines) console.log(l);
  process.exit(fails === 0 ? 0 : 1);
}

export { checks, lines };
