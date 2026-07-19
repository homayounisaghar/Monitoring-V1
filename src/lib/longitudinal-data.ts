/**
 * ST2 — Longitudinal derivation layer (Workstream 04 · prompt 1/6).
 *
 * Data-only. Pure derivation over `demo-library.ts` and `demo-typicals.ts`.
 * No React, no components, no display strings. The Longitudinal page will
 * consume this in a later prompt.
 *
 * Load-bearing rules (spec §B1–§B8):
 *   - Window identity is the calendar. A day with no data still counts.
 *   - Rest day = a real zero. Missing day = null, never interpolated.
 *   - A day with more than one session sums the sessions and divides by the
 *     count of distinct athletes who trained that day.
 *   - Vs-typical uses the "typicalDuration" basis (volume). When the expected
 *     side withholds, the day's vs-typical value withholds too.
 *   - Availability is over training sessions only. Selection ≠ availability.
 *   - Athletes with zero participation are returned separately, not as zeros.
 */

import {
  demoSessions, demoDays, demoRecords, demoAthletes,
  DEMO_TODAY, SEASON_START_ISO,
  recordsForSession, recordsForAthlete,
  type DemoSession, type DemoRecord, type DemoAthlete,
} from "./demo-library";
import {
  typicalFor, bucketKeyFor,
  expectedSumForSession, comparableSessionCount,
  type ExpectedSumBasis,
} from "./demo-typicals";
import type { ParticipationTag } from "./session-data";
import { TIER1_ROWS_DEFAULT } from "./session-flags";

/** Pinned session identity — the flag source below is scoped to this date. */
const PINNED_SESSION_DATE_ISO = "2026-07-18";
const TIER1_FLAG_IDS: ReadonlySet<string> = new Set(TIER1_ROWS_DEFAULT.map((r) => r.id));

/* ─────────────────────────── constants ─────────────────────────── */

/** Default horizon for the Longitudinal page. */
export const LONGI_WINDOW_DEFAULT = 28;

/**
 * Squad-load gauges withhold when contributing sessions are fewer than this
 * share of the window's sessions. Exported so it can be changed in one place.
 */
export const GAUGE_MIN_COVERAGE = 2 / 3;

/**
 * HR coverage threshold — a record whose `hrCoveragePct` is at or above this
 * counts as adequately covered for Cardio Load. Below, the record still
 * enters totals but is marked sub-threshold.
 */
export const HR_COVERAGE_THRESHOLD = 80;

/* ─────────────────────────── metric surface ─────────────────────────── */

export type LongiMetric =
  | "totalDistance" | "hsr" | "sprintDist" | "accDec" | "cardioLoad" | "srpeAU";

export const LONGI_METRICS: readonly LongiMetric[] =
  ["totalDistance", "hsr", "sprintDist", "accDec", "cardioLoad", "srpeAU"];

/* ─────────────────────────── date helpers ─────────────────────────── */

function parseISO(iso: string): number {
  return Date.UTC(
    parseInt(iso.slice(0, 4), 10),
    parseInt(iso.slice(5, 7), 10) - 1,
    parseInt(iso.slice(8, 10), 10),
  );
}
function fmtISO(ms: number): string {
  const d = new Date(ms);
  const y = d.getUTCFullYear();
  const m = String(d.getUTCMonth() + 1).padStart(2, "0");
  const dd = String(d.getUTCDate()).padStart(2, "0");
  return `${y}-${m}-${dd}`;
}
function addDays(iso: string, n: number): string {
  return fmtISO(parseISO(iso) + n * 86_400_000);
}
function diffDays(a: string, b: string): number {
  return Math.round((parseISO(a) - parseISO(b)) / 86_400_000);
}

/* ─────────────────────────── windows (§B1) ─────────────────────────── */

export type Horizon = 7 | 14 | 28 | "season";

export type LongiWindow = {
  horizon: Horizon;
  startISO: string;
  endISO: string;
  days: number;
};

/**
 * Horizon of N days ends on DEMO_TODAY and covers the N calendar days ending
 * that day inclusive. Season-to-date runs SEASON_START_ISO → DEMO_TODAY.
 * A custom `endISO` is supported for the check's back-dated 14-day probe.
 */
export function windowFor(horizon: Horizon, endISO: string = DEMO_TODAY): LongiWindow {
  if (horizon === "season") {
    return {
      horizon,
      startISO: SEASON_START_ISO,
      endISO,
      days: diffDays(endISO, SEASON_START_ISO) + 1,
    };
  }
  return {
    horizon,
    startISO: addDays(endISO, -(horizon - 1)),
    endISO,
    days: horizon,
  };
}

/* ─────────────────────────── composition (§B2) ─────────────────────────── */

export type WindowComposition = {
  days: number;                // == window.days
  sessions: number;
  matchSessions: number;
  nonMatchSessions: number;
  restDays: number;
  noRecordDays: number;
  doubleSessionDays: number;
};

function sessionsIn(w: LongiWindow): DemoSession[] {
  return demoSessions.filter((s) => s.dateISO >= w.startISO && s.dateISO <= w.endISO);
}

export function windowComposition(w: LongiWindow): WindowComposition {
  const ss = sessionsIn(w);
  const matches = ss.filter((s) => s.type === "match").length;
  // Enumerate calendar dates in the window and classify each.
  const bySession = new Map<string, number>();
  for (const s of ss) bySession.set(s.dateISO, (bySession.get(s.dateISO) ?? 0) + 1);
  const dayByDate = new Map(demoDays.map((d) => [d.dateISO, d]));
  let rest = 0, noRec = 0, dbl = 0;
  for (let i = 0; i < w.days; i++) {
    const dateISO = addDays(w.startISO, i);
    const d = dayByDate.get(dateISO);
    if (!d) noRec++;
    else if (d.kind === "rest") rest++;
    const c = bySession.get(dateISO) ?? 0;
    if (c > 1) dbl++;
  }
  return {
    days: w.days,
    sessions: ss.length,
    matchSessions: matches,
    nonMatchSessions: ss.length - matches,
    restDays: rest,
    noRecordDays: noRec,
    doubleSessionDays: dbl,
  };
}

/* ─────────────────────────── day series (§B3) ─────────────────────────── */

export type DayKind = "session" | "rest" | "missing";

/** Vs-typical per-metric value: percentage of typical, or withheld with reason. */
export type VsTypicalCell =
  | { state: "computed"; pct: number }
  | { state: "withheld"; reason: string };

export type DayEntry = {
  dateISO: string;
  dayCode: string | null;
  kind: DayKind;
  sessionIds: string[];
  athletesTrained: number;
  unconfirmed: boolean;
  /** Per-metric value on the "average per athlete who trained" basis. Null on missing days. Zero on rest days. */
  perMetric: Partial<Record<LongiMetric, number | null>>;
  /** Per-metric vs-typical (%) on typicalDuration basis. Absent on rest/missing. */
  vsTypical: Partial<Record<LongiMetric, VsTypicalCell>>;
  /** Share of contributing HR records at or above threshold (0–1). Null if no HR records. */
  hrCoverageShare: number | null;
  /** Count of contributing records with hrCoveragePct below threshold. */
  hrBelowThresholdCount: number;
  /** Lowest hrCoveragePct across contributing records (null if none). */
  hrCoverageMin: number | null;
  /** sRPE facts (§B3). Both null on missing/rest, or on session days that did not collect. */
  srpeCollected: boolean;
  srpeSubmitted: number;
  srpeEligible: number;
};

/** Cache keyed by window identity so repeated reads don't rebuild. */
const DAY_SERIES_CACHE = new Map<string, DayEntry[]>();
function windowKey(w: LongiWindow): string { return `${w.horizon}|${w.startISO}|${w.endISO}`; }

/**
 * Sum the value of `field` over sessions on `dateISO` for all records with
 * minutes > 0. `field` may be a non-null numeric metric on DemoRecord.
 */
function sumFieldOnDate(
  sessionIdsOnDate: readonly string[],
  field: LongiMetric,
): { total: number; count: number; nHR: number; nHROk: number; nHRBelow: number; hrMin: number | null } {
  let total = 0;
  const athleteSet = new Set<string>();
  let nHR = 0, nHROk = 0, nHRBelow = 0;
  let hrMin: number | null = null;
  for (const sid of sessionIdsOnDate) {
    for (const r of recordsForSession(sid)) {
      if (r.minutes <= 0) continue;
      const v = (r as unknown as Record<string, number | null>)[field];
      if (v == null) continue;
      total += v;
      athleteSet.add(r.athleteId);
      if (r.hrCoveragePct != null) {
        nHR++;
        if (r.hrCoveragePct >= HR_COVERAGE_THRESHOLD) nHROk++;
        else nHRBelow++;
        if (hrMin == null || r.hrCoveragePct < hrMin) hrMin = r.hrCoveragePct;
      }
    }
  }
  return { total, count: athleteSet.size, nHR, nHROk, nHRBelow, hrMin };
}

function athletesTrainedOnDate(sessionIdsOnDate: readonly string[]): number {
  const set = new Set<string>();
  for (const sid of sessionIdsOnDate) {
    for (const r of recordsForSession(sid)) {
      if (r.minutes > 0) set.add(r.athleteId);
    }
  }
  return set.size;
}

export function daySeries(w: LongiWindow): DayEntry[] {
  const key = windowKey(w);
  const hit = DAY_SERIES_CACHE.get(key);
  if (hit) return hit;

  const dayByDate = new Map(demoDays.map((d) => [d.dateISO, d]));
  const sessionsByDate = new Map<string, DemoSession[]>();
  for (const s of demoSessions) {
    const arr = sessionsByDate.get(s.dateISO) ?? [];
    arr.push(s);
    sessionsByDate.set(s.dateISO, arr);
  }

  const out: DayEntry[] = [];
  for (let i = 0; i < w.days; i++) {
    const dateISO = addDays(w.startISO, i);
    const d = dayByDate.get(dateISO);
    const ss = sessionsByDate.get(dateISO) ?? [];

    if (!d) {
      // Missing day — null everywhere, no interpolation.
      const perMetric: Partial<Record<LongiMetric, number | null>> = {};
      for (const m of LONGI_METRICS) perMetric[m] = null;
      out.push({
        dateISO, dayCode: null, kind: "missing",
        sessionIds: [], athletesTrained: 0, unconfirmed: false,
        perMetric, vsTypical: {},
        hrCoverageShare: null, hrBelowThresholdCount: 0, hrCoverageMin: null,
        srpeCollected: false, srpeSubmitted: 0, srpeEligible: 0,
      });
      continue;
    }

    if (d.kind === "rest") {
      const perMetric: Partial<Record<LongiMetric, number | null>> = {};
      for (const m of LONGI_METRICS) perMetric[m] = 0; // Rest = real observation of zero.
      out.push({
        dateISO, dayCode: d.dayCode, kind: "rest",
        sessionIds: [], athletesTrained: 0, unconfirmed: false,
        perMetric, vsTypical: {},
        hrCoverageShare: null, hrBelowThresholdCount: 0, hrCoverageMin: null,
        srpeCollected: false, srpeSubmitted: 0, srpeEligible: 0,
      });
      continue;
    }

    // Session day (may be a double).
    const sessionIds = ss.map((s) => s.id);
    const athletesTrained = athletesTrainedOnDate(sessionIds);
    const unconfirmed = ss.some((s) => s.unconfirmed);

    const perMetric: Partial<Record<LongiMetric, number | null>> = {};
    let hrNHR = 0, hrNHROk = 0, hrNHRBelow = 0, hrMin: number | null = null;
    for (const m of LONGI_METRICS) {
      const { total, nHR, nHROk, nHRBelow, hrMin: mn } = sumFieldOnDate(sessionIds, m);
      perMetric[m] = athletesTrained > 0 ? total / athletesTrained : null;
      // HR facts are shared across metrics — accumulate once (any metric pass surfaces the same records).
      if (m === "cardioLoad") {
        hrNHR = nHR; hrNHROk = nHROk; hrNHRBelow = nHRBelow; hrMin = mn;
      }
    }

    // sRPE facts.
    const anyCollected = ss.some((s) => s.srpeCollected);
    let submitted = 0, eligible = 0;
    for (const sid of sessionIds) {
      const s = ss.find((x) => x.id === sid)!;
      if (!s.srpeCollected) continue;
      for (const r of recordsForSession(sid)) {
        if (r.minutes <= 0) continue;
        eligible++;
        if (r.srpeAU != null) submitted++;
      }
    }

    // Vs-typical per metric on typicalDuration basis. If any session withholds
    // its expected sum, the day-level vs-typical for every metric withholds.
    const vsTypical: Partial<Record<LongiMetric, VsTypicalCell>> = {};
    const expBySession = sessionIds.map((sid) => expectedSumForSession(sid, "typicalDuration"));
    const anyWithheld = expBySession.find((e) => e.state === "withheld");
    if (anyWithheld) {
      for (const m of LONGI_METRICS) vsTypical[m] = { state: "withheld", reason: anyWithheld.state === "withheld" ? anyWithheld.reason : "unknown" };
    } else {
      // Observed sum = sum over sessions of sum over contributed athletes of record's metric.
      for (const m of LONGI_METRICS) {
        let obs = 0;
        let exp = 0;
        let missing = false;
        for (let k = 0; k < sessionIds.length; k++) {
          const e = expBySession[k];
          if (e.state !== "computed") { missing = true; break; }
          const eV = e.metrics[m];
          if (eV == null) { missing = true; break; }
          exp += eV;
          // Observed side over the same contributed set (composition parity).
          const contribSet = new Set(e.contributed);
          for (const r of recordsForSession(sessionIds[k])) {
            if (!contribSet.has(r.athleteId)) continue;
            const v = (r as unknown as Record<string, number | null>)[m];
            if (v == null) continue;
            obs += v;
          }
        }
        if (missing || exp <= 0) {
          vsTypical[m] = { state: "withheld", reason: "metric_not_in_expected" };
        } else {
          vsTypical[m] = { state: "computed", pct: (obs / exp) * 100 };
        }
      }
    }

    out.push({
      dateISO, dayCode: d.dayCode, kind: "session",
      sessionIds, athletesTrained, unconfirmed,
      perMetric, vsTypical,
      hrCoverageShare: hrNHR > 0 ? hrNHROk / hrNHR : null,
      hrBelowThresholdCount: hrNHRBelow,
      hrCoverageMin: hrMin,
      srpeCollected: anyCollected,
      srpeSubmitted: submitted,
      srpeEligible: eligible,
    });
  }

  DAY_SERIES_CACHE.set(key, out);
  return out;
}

/* ─────────────────────────── squad-load gauges (§B4) ─────────────────────────── */

export type SquadLoadGauges =
  | {
      state: "computed";
      volumePct: number;
      intensityPct: number;
      contributingSessions: number;
      windowSessions: number;
      matchDominant: boolean;
    }
  | {
      state: "withheld";
      reason: "insufficient_coverage";
      contributingSessions: number;
      windowSessions: number;
      matchDominant: boolean;
    };

export function squadLoadGauges(w: LongiWindow): SquadLoadGauges {
  const ss = sessionsIn(w);
  const windowSessions = ss.length;
  const matches = ss.filter((s) => s.type === "match").length;
  const matchDominant = matches > windowSessions - matches;

  let numer = 0;
  let denomVol = 0;
  let denomInt = 0;
  let contributingSessions = 0;

  for (const s of ss) {
    const ev = expectedSumForSession(s.id, "typicalDuration");
    const ei = expectedSumForSession(s.id, "actualMinutes");
    if (ev.state !== "computed" || ei.state !== "computed") continue;
    contributingSessions++;
    // Identical contributed set (same coverage logic under both bases).
    const contribSet = new Set(ev.contributed);
    for (const r of recordsForSession(s.id)) {
      if (!contribSet.has(r.athleteId)) continue;
      numer += r.totalDistance;
      const t = typicalFor(r.athleteId, bucketKeyFor(s));
      if (t.state !== "computed") continue;
      const pm = t.metrics.totalDistance;
      if (!pm || pm.perMinute == null) continue;
      denomVol += pm.perMinute * t.typicalDurationMin;
      denomInt += pm.perMinute * r.minutes;
    }
  }

  if (windowSessions === 0 || contributingSessions / windowSessions < GAUGE_MIN_COVERAGE) {
    return { state: "withheld", reason: "insufficient_coverage", contributingSessions, windowSessions, matchDominant };
  }
  return {
    state: "computed",
    volumePct: (numer / denomVol) * 100,
    intensityPct: (numer / denomInt) * 100,
    contributingSessions, windowSessions, matchDominant,
  };
}

/* ─────────────────────────── availability (§B5) ─────────────────────────── */

export type Availability = {
  fullTrainingSessions: number;
  possibleTrainingSessions: number;
  fullOfPossiblePct: number;
  trainingSessions: number;
  athletesAtWindowEnd: number;
  /** Only tags that actually occurred; not-in-squad kept separate. */
  tagCounts: Partial<Record<ParticipationTag, number>>;
  notInSquadCount: number;
};

function joinedByDate(athleteId: string, dateISO: string): boolean {
  const a = demoAthletes.find((x) => x.id === athleteId)!;
  return dateISO >= a.joinedISO;
}

export function availability(w: LongiWindow): Availability {
  const trainings = sessionsIn(w).filter((s) => s.type !== "match");
  const tagCounts: Partial<Record<ParticipationTag, number>> = {};
  let notInSquad = 0;
  let possible = 0;
  let full = 0;
  for (const s of trainings) {
    for (const a of demoAthletes) {
      const joined = joinedByDate(a.id, s.dateISO);
      if (!joined) { notInSquad++; continue; }
      possible++;
      const rec = recordsForSession(s.id).find((r) => r.athleteId === a.id);
      const tag = rec?.participation ?? null;
      if (tag === "Full") full++;
      if (tag) tagCounts[tag] = (tagCounts[tag] ?? 0) + 1;
    }
  }
  const athletesAtEnd = demoAthletes.filter((a) => a.joinedISO <= w.endISO).length;
  return {
    fullTrainingSessions: full,
    possibleTrainingSessions: possible,
    fullOfPossiblePct: possible > 0 ? (full / possible) * 100 : 0,
    trainingSessions: trainings.length,
    athletesAtWindowEnd: athletesAtEnd,
    tagCounts,
    notInSquadCount: notInSquad,
  };
}

/* ─────────────────────────── availability ranking (§B6) ─────────────────────────── */

export type AthleteAvailEntry = {
  athlete: DemoAthlete;
  tagCounts: Partial<Record<ParticipationTag, number>>;
  notInSquadCount: number;
  availableSessions: number;   // training sessions in window on/after his join date
  fullFraction: number;        // Full / availableSessions (0..1); 0 when denominator is 0
  attentionFlagged: boolean;
};

export function athleteAvailabilityRanking(w: LongiWindow): AthleteAvailEntry[] {
  const trainings = sessionsIn(w).filter((s) => s.type !== "match");
  const out: AthleteAvailEntry[] = [];
  for (const a of demoAthletes) {
    const tagCounts: Partial<Record<ParticipationTag, number>> = {};
    let notInSquad = 0;
    let available = 0;
    let full = 0;
    for (const s of trainings) {
      if (!joinedByDate(a.id, s.dateISO)) { notInSquad++; continue; }
      available++;
      const rec = recordsForSession(s.id).find((r) => r.athleteId === a.id);
      const tag = rec?.participation ?? null;
      if (tag === "Full") full++;
      if (tag) tagCounts[tag] = (tagCounts[tag] ?? 0) + 1;
    }
    // Attention approximation: any Injury/Rehab/Modified record on any
    // in-window session (training or match). See findings — this is a
    // stand-in until the Attention section exposes its own signal.
    const flagged = demoRecords.some(
      (r) => r.athleteId === a.id
        && r.dateISO >= w.startISO && r.dateISO <= w.endISO
        && r.sessionId != null
        && (r.participation === "Injury" || r.participation === "Rehab" || r.participation === "Modified"),
    );
    out.push({
      athlete: a, tagCounts, notInSquadCount: notInSquad,
      availableSessions: available,
      fullFraction: available > 0 ? full / available : 0,
      attentionFlagged: flagged,
    });
  }
  out.sort((x, y) => x.fullFraction - y.fullFraction || x.athlete.name.localeCompare(y.athlete.name));
  return out;
}

/* ─────────────────────────── window totals per athlete (§B7) ─────────────────────────── */

export type VsTypicalAthlete =
  | {
      state: "computed";
      perMetricPct: Partial<Record<LongiMetric, number>>;
      sessionsContributed: number;
      sessionsParticipated: number;
    }
  | {
      state: "withheld";
      reason: "no_comparable_typical";
      sessionsParticipated: number;
      largestBucketSampleCount: number;
    };

export type AcRatio =
  | { state: "computed"; perMetric: Partial<Record<LongiMetric, number | null>>; daysOfData: number }
  | { state: "withheld"; reason: "insufficient_days"; daysOfData: number; required: 28 };

export type AthleteTotals = {
  athlete: DemoAthlete;
  sessionsParticipated: number;
  minutes: number;
  absolute: Partial<Record<LongiMetric, number>>;
  hrCoverageShareByMetric: Partial<Record<LongiMetric, number | null>>;
  vsTypical: VsTypicalAthlete;
  ac: AcRatio;
};

export type WindowTotals = {
  perAthlete: AthleteTotals[];
  zeroParticipation: { athlete: DemoAthlete; reason: string }[];
};

function largestBucketSampleCount(athleteId: string, w: LongiWindow): number {
  const inWin = new Set(sessionsIn(w).map((s) => s.id));
  const buckets = new Set<string>();
  for (const r of recordsForAthlete(athleteId)) {
    if (r.sessionId == null) continue;
    if (!inWin.has(r.sessionId)) continue;
    const s = demoSessions.find((x) => x.id === r.sessionId);
    if (!s) continue;
    buckets.add(bucketKeyFor(s));
  }
  let max = 0;
  for (const bk of buckets) {
    max = Math.max(max, comparableSessionCount(athleteId, bk));
  }
  return max;
}

function acForAthlete(athleteId: string, endISO: string): AcRatio {
  // 28-day and 7-day day series for this athlete, using his own records.
  const win28 = windowFor(28, endISO);
  const win7 = windowFor(7, endISO);
  const recsByDate = new Map<string, DemoRecord>();
  for (const r of recordsForAthlete(athleteId)) {
    if (r.dateISO >= win28.startISO && r.dateISO <= win28.endISO) recsByDate.set(r.dateISO, r);
  }
  // Days of data across 28-day window: count of dates with a record.
  const daysOfData28 = recsByDate.size;
  if (daysOfData28 < 28) {
    return { state: "withheld", reason: "insufficient_days", daysOfData: daysOfData28, required: 28 };
  }
  const perMetric: Partial<Record<LongiMetric, number | null>> = {};
  for (const m of LONGI_METRICS) {
    let sum28 = 0, n28 = 0, sum7 = 0, n7 = 0;
    for (const [dateISO, r] of recsByDate) {
      const v = (r as unknown as Record<string, number | null>)[m] ?? 0;
      sum28 += v; n28++;
      if (dateISO >= win7.startISO) { sum7 += v; n7++; }
    }
    const avg28 = n28 > 0 ? sum28 / n28 : 0;
    const avg7 = n7 > 0 ? sum7 / n7 : 0;
    perMetric[m] = avg28 > 0 ? avg7 / avg28 : null;
  }
  return { state: "computed", perMetric, daysOfData: daysOfData28 };
}

export function windowTotals(w: LongiWindow): WindowTotals {
  const winSessionIds = new Set(sessionsIn(w).map((s) => s.id));
  const perAthlete: AthleteTotals[] = [];
  const zero: { athlete: DemoAthlete; reason: string }[] = [];

  for (const a of demoAthletes) {
    let minutes = 0;
    let sessions = 0;
    const absolute: Partial<Record<LongiMetric, number>> = {};
    const hrTotals: Partial<Record<LongiMetric, { n: number; ok: number }>> = {};
    for (const m of LONGI_METRICS) { absolute[m] = 0; hrTotals[m] = { n: 0, ok: 0 }; }

    // Vs-typical aggregation on typicalDuration basis.
    const vtObs: Partial<Record<LongiMetric, number>> = {};
    const vtExp: Partial<Record<LongiMetric, number>> = {};
    for (const m of LONGI_METRICS) { vtObs[m] = 0; vtExp[m] = 0; }
    let sessionsWithTypical = 0;

    // Iterate this athlete's in-window session records.
    const seenSessions = new Set<string>();
    for (const r of recordsForAthlete(a.id)) {
      if (r.sessionId == null) continue;
      if (!winSessionIds.has(r.sessionId)) continue;
      if (r.minutes <= 0) continue;
      seenSessions.add(r.sessionId);
      minutes += r.minutes;
      sessions++;
      for (const m of LONGI_METRICS) {
        const v = (r as unknown as Record<string, number | null>)[m];
        if (v == null) continue;
        absolute[m] = (absolute[m] ?? 0) + v;
        const hr = hrTotals[m]!;
        if (r.hrCoveragePct != null) {
          hr.n++;
          if (r.hrCoveragePct >= HR_COVERAGE_THRESHOLD) hr.ok++;
        }
      }
      // Vs-typical: does this athlete have a computable typical for this session's bucket?
      const s = demoSessions.find((x) => x.id === r.sessionId)!;
      const t = typicalFor(a.id, bucketKeyFor(s));
      if (t.state === "computed") {
        sessionsWithTypical++;
        for (const m of LONGI_METRICS) {
          const pm = t.metrics[m];
          if (!pm || pm.perMinute == null) continue;
          const obs = (r as unknown as Record<string, number | null>)[m];
          if (obs == null) continue;
          vtObs[m] = (vtObs[m] ?? 0) + obs;
          vtExp[m] = (vtExp[m] ?? 0) + pm.perMinute * t.typicalDurationMin;
        }
      }
    }

    if (sessions === 0) {
      // Find the tag he carried across the window.
      const inWinTags = new Set<string>();
      for (const r of recordsForAthlete(a.id)) {
        if (r.dateISO < w.startISO || r.dateISO > w.endISO) continue;
        if (r.sessionId == null) continue;
        if (r.participation) inWinTags.add(r.participation);
        else if (!r.inSquad) inWinTags.add("not-in-squad");
        else inWinTags.add("unselected");
      }
      zero.push({ athlete: a, reason: [...inWinTags].sort().join("/") || "no-records" });
      continue;
    }

    const hrShare: Partial<Record<LongiMetric, number | null>> = {};
    for (const m of LONGI_METRICS) {
      const hr = hrTotals[m]!;
      hrShare[m] = hr.n > 0 ? hr.ok / hr.n : null;
    }

    let vsTypical: VsTypicalAthlete;
    if (sessionsWithTypical === 0) {
      vsTypical = {
        state: "withheld",
        reason: "no_comparable_typical",
        sessionsParticipated: sessions,
        largestBucketSampleCount: largestBucketSampleCount(a.id, w),
      };
    } else {
      const perMetricPct: Partial<Record<LongiMetric, number>> = {};
      for (const m of LONGI_METRICS) {
        const exp = vtExp[m] ?? 0;
        if (exp > 0) perMetricPct[m] = ((vtObs[m] ?? 0) / exp) * 100;
      }
      vsTypical = {
        state: "computed",
        perMetricPct,
        sessionsContributed: sessionsWithTypical,
        sessionsParticipated: sessions,
      };
    }

    perAthlete.push({
      athlete: a,
      sessionsParticipated: sessions,
      minutes,
      absolute,
      hrCoverageShareByMetric: hrShare,
      vsTypical,
      ac: acForAthlete(a.id, w.endISO),
    });
  }

  return { perAthlete, zeroParticipation: zero };
}

/* ─────────────────────────── focus + filter helpers (§B8) ─────────────────────────── */

export function sessionDayIndex(sessionId: string, w: LongiWindow): number | null {
  const s = demoSessions.find((x) => x.id === sessionId);
  if (!s) return null;
  if (s.dateISO < w.startISO || s.dateISO > w.endISO) return null;
  return diffDays(s.dateISO, w.startISO);
}

export type SessionCategory = "All" | "Matches" | "Training" | string;

export function sessionCategories(w: LongiWindow): SessionCategory[] {
  const ss = sessionsIn(w);
  const codes = new Set<string>();
  for (const s of ss) codes.add(s.dayCode);
  return ["All", "Matches", "Training", ...[...codes].sort()];
}
