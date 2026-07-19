/**
 * ST2 — Demo typicals layer (Workstream 01 · prompt 2/4).
 *
 * The second half of the dataset. Every "vs typical" read on the Athlete
 * and Longitudinal pages resolves against values produced here.
 *
 * Load-bearing rules (see prompt spec §1–§5):
 *   - A typical is conditioned on day type. Bucket key is
 *     (dayCode, sessionType) — the double day carries gym and pitch under
 *     the same MD code and they are NOT commensurable.
 *   - No pooled mean anywhere. No positional fallback. A missing baseline
 *     is withheld with its reason, never substituted.
 *   - A session contributes a sample for an athlete ONLY if he actually
 *     participated — the contract's minutes-bearing tags (Full/Part/
 *     Modified) with minutes > 0. Injury/Rehab/Other/unselected contribute
 *     nothing. An injured athlete's zero is not a sample.
 *   - Rest days contribute nothing (a rest day is not an instance of a
 *     day type).
 *   - The 19 Jul unconfirmed session contributes nothing (provisional
 *     data must not enter a baseline).
 *   - Cumulative metrics normalised per minute; rates taken as they stand.
 *   - Minutes-weighted mean and (biased) SD so a short appearance carries
 *     proportionally less weight.
 *   - Every typical carries a spread (±1 SD band). A zero-width band is
 *     a lie about certainty; if a metric comes out with SD = 0 that is
 *     a generator problem, not a display problem.
 *
 * Naming collision (flagged in the reply): `session-flags.ts` exports
 * `BUILDING_SESSIONS_TO_MIN = 3`, which is a *different* quantity (how
 * many Köhler currently has). Do not reuse or alias it here.
 *
 * Nothing in this module is imported yet.
 */

import {
  demoSessions, demoRecords, demoAthletes,
  recordsForSession,
  type DemoSession, type DemoRecord,
} from "./demo-library";

/* ─────────────────────────── constants ─────────────────────────── */

/** Below this many comparable sessions in a bucket, the typical is withheld. */
export const TYPICAL_MIN_SESSIONS = 5;

/**
 * Whole-of-sum coverage floor for the composition-matched expected sum.
 * If fewer than this fraction of participating athletes contribute (or fewer
 * than `EXPECTED_MIN_CONTRIBUTORS` in absolute terms), the sum withholds as
 * a whole. Alterable — defaults documented in ST2_Build_Findings.
 */
export const EXPECTED_MIN_COVERAGE = 0.5;
export const EXPECTED_MIN_CONTRIBUTORS = 3;

/* ─────────────────────────── types ─────────────────────────── */

export type TypicalMetric =
  | "totalDistance" | "hsr" | "sprintDist" | "accDec" | "cardioLoad" | "srpeAU"
  | "mMin" | "topSpeedKmh";

const CUMULATIVE_METRICS: readonly TypicalMetric[] =
  ["totalDistance", "hsr", "sprintDist", "accDec", "cardioLoad", "srpeAU"];
const RATE_METRICS: readonly TypicalMetric[] =
  ["mMin", "topSpeedKmh"];
export const TYPICAL_METRICS: readonly TypicalMetric[] =
  [...CUMULATIVE_METRICS, ...RATE_METRICS];

function isCumulative(m: TypicalMetric): boolean {
  return (CUMULATIVE_METRICS as readonly string[]).includes(m);
}

export type BucketKey = string; // `${dayCode}::${sessionType}`

export function bucketKeyFor(s: Pick<DemoSession, "dayCode" | "type">): BucketKey {
  return `${s.dayCode}::${s.type}`;
}
function parseBucketKey(k: BucketKey): { dayCode: string; sessionType: DemoSession["type"] } {
  const [dayCode, sessionType] = k.split("::") as [string, DemoSession["type"]];
  return { dayCode, sessionType };
}

export type PerMetricTypical = {
  /** Weighted mean per minute (cumulative metrics only). Null for rate metrics. */
  perMinute: number | null;
  /** Full-session value: cumulative → perMinute × nominalDurationMin; rate → weighted mean. */
  fullSession: number;
  /** Weighted, biased SD in the same unit as `fullSession`. */
  sd: number;
  /** Convenience band = fullSession ± sd. */
  bandLo: number;
  bandHi: number;
  /** Number of samples that carried a value for THIS metric (may be < sessionCount for CL/sRPE). */
  n: number;
};

export type AthleteBucketTypical =
  | {
      state: "computed";
      athleteId: string;
      bucketKey: BucketKey;
      dayCode: string;
      sessionType: DemoSession["type"];
      sessionCount: number;
      required: number;
      nominalDurationMin: number;
      metrics: Partial<Record<TypicalMetric, PerMetricTypical>>;
    }
  | {
      state: "withheld";
      athleteId: string;
      bucketKey: BucketKey;
      dayCode: string;
      sessionType: DemoSession["type"];
      sessionCount: number;
      required: number;
      reason: "insufficient_sessions";
    };

export type SquadBucketTypical = {
  bucketKey: BucketKey;
  dayCode: string;
  sessionType: DemoSession["type"];
  nominalDurationMin: number;
  contributingAthletes: number;
  totalAthletes: number;
  metrics: Partial<Record<TypicalMetric, { fullSession: number; sd: number; n: number }>>;
};

export type ExpectedSumForSession =
  | {
      state: "computed";
      sessionId: string;
      bucketKey: BucketKey;
      metrics: Partial<Record<TypicalMetric, number>>;
      contributed: string[];       // athlete ids that contributed a typical
      withheldAthletes: string[];  // participated but no typical for this bucket
      participatedCount: number;
      contributedCount: number;
      coverage: number;            // contributedCount / participatedCount
    }
  | {
      state: "withheld";
      sessionId: string;
      bucketKey: BucketKey;
      participatedCount: number;
      contributedCount: number;
      coverage: number;
      reason: "insufficient_coverage";
    };

/* ─────────────────────────── sample extraction ─────────────────────────── */

const MINUTES_BEARING = new Set<string>(["Full", "Part", "Modified"]);

/** Sessions that contribute samples (rest days already excluded by having sessionId != null). */
const CONTRIBUTING_SESSIONS: readonly DemoSession[] = demoSessions.filter(
  // The unconfirmed session must never enter a baseline. Provisional in, provisional out.
  (s) => !s.unconfirmed,
);

const CONTRIBUTING_SESSION_IDS = new Set(CONTRIBUTING_SESSIONS.map((s) => s.id));

/** All records that qualify as samples: sessionId present, session contributing, minutes-bearing tag, minutes>0. */
function sampleRecords(): DemoRecord[] {
  return demoRecords.filter(
    (r) =>
      r.sessionId != null &&
      CONTRIBUTING_SESSION_IDS.has(r.sessionId) &&
      r.participation != null &&
      MINUTES_BEARING.has(r.participation) &&
      r.minutes > 0,
  );
}

/* ─────────────────────────── weighted stats ─────────────────────────── */

function weightedMeanSd(
  samples: readonly { x: number; w: number }[],
): { mean: number; sd: number; n: number } {
  const n = samples.length;
  if (n === 0) return { mean: 0, sd: 0, n: 0 };
  let W = 0;
  for (const s of samples) W += s.w;
  if (W <= 0) return { mean: 0, sd: 0, n };
  let mean = 0;
  for (const s of samples) mean += (s.w / W) * s.x;
  let varAcc = 0;
  for (const s of samples) {
    const d = s.x - mean;
    varAcc += (s.w / W) * d * d;
  }
  return { mean, sd: Math.sqrt(varAcc), n };
}

/* ─────────────────────────── bucket assembly ─────────────────────────── */

/** Sessions per bucket + nominal duration (mean session.durationMin, rounded). */
const BUCKET_SESSIONS: Map<BucketKey, DemoSession[]> = (() => {
  const m = new Map<BucketKey, DemoSession[]>();
  for (const s of CONTRIBUTING_SESSIONS) {
    const k = bucketKeyFor(s);
    const arr = m.get(k) ?? [];
    arr.push(s);
    m.set(k, arr);
  }
  return m;
})();

function nominalDurationFor(bucketKey: BucketKey): number {
  const ss = BUCKET_SESSIONS.get(bucketKey);
  if (!ss || ss.length === 0) return 0;
  let sum = 0;
  for (const s of ss) sum += s.durationMin;
  return Math.round(sum / ss.length);
}

/** Records grouped as { athleteId → bucketKey → DemoRecord[] } over sample records. */
const ATHLETE_BUCKET_RECORDS: Map<string, Map<BucketKey, DemoRecord[]>> = (() => {
  const sessionById = new Map(demoSessions.map((s) => [s.id, s]));
  const out = new Map<string, Map<BucketKey, DemoRecord[]>>();
  for (const r of sampleRecords()) {
    const s = sessionById.get(r.sessionId!)!;
    const bk = bucketKeyFor(s);
    let a = out.get(r.athleteId);
    if (!a) { a = new Map(); out.set(r.athleteId, a); }
    const arr = a.get(bk) ?? [];
    arr.push(r);
    a.set(bk, arr);
  }
  return out;
})();

/* ─────────────────────────── per-athlete-bucket typical ─────────────────────────── */

function computeMetric(records: readonly DemoRecord[], metric: TypicalMetric, nominalMin: number): PerMetricTypical | null {
  // For cumulative metrics: sample = value / minutes (per-min rate), weight = minutes.
  // For rate metrics: sample = value as-is, weight = minutes.
  const samples: { x: number; w: number }[] = [];
  for (const r of records) {
    const raw = (r as Record<string, unknown>)[metric];
    if (raw == null) continue;
    const v = raw as number;
    if (!Number.isFinite(v)) continue;
    if (r.minutes <= 0) continue;
    const x = isCumulative(metric) ? v / r.minutes : v;
    samples.push({ x, w: r.minutes });
  }
  if (samples.length === 0) return null;
  const { mean, sd, n } = weightedMeanSd(samples);
  if (isCumulative(metric)) {
    const fs = mean * nominalMin;
    const sdFs = sd * nominalMin;
    return { perMinute: mean, fullSession: fs, sd: sdFs, bandLo: fs - sdFs, bandHi: fs + sdFs, n };
  }
  return { perMinute: null, fullSession: mean, sd, bandLo: mean - sd, bandHi: mean + sd, n };
}

const TYPICAL_CACHE = new Map<string, AthleteBucketTypical>();

export function typicalFor(athleteId: string, bucketKey: BucketKey): AthleteBucketTypical {
  const cacheKey = `${athleteId}::${bucketKey}`;
  const hit = TYPICAL_CACHE.get(cacheKey);
  if (hit) return hit;
  const { dayCode, sessionType } = parseBucketKey(bucketKey);
  const records = ATHLETE_BUCKET_RECORDS.get(athleteId)?.get(bucketKey) ?? [];
  const sessionCount = records.length;
  if (sessionCount < TYPICAL_MIN_SESSIONS) {
    const t: AthleteBucketTypical = {
      state: "withheld",
      athleteId, bucketKey, dayCode, sessionType,
      sessionCount, required: TYPICAL_MIN_SESSIONS,
      reason: "insufficient_sessions",
    };
    TYPICAL_CACHE.set(cacheKey, t);
    return t;
  }
  const nominalDurationMin = nominalDurationFor(bucketKey);
  const metrics: Partial<Record<TypicalMetric, PerMetricTypical>> = {};
  for (const m of TYPICAL_METRICS) {
    const pm = computeMetric(records, m, nominalDurationMin);
    if (pm) metrics[m] = pm;
  }
  const t: AthleteBucketTypical = {
    state: "computed",
    athleteId, bucketKey, dayCode, sessionType,
    sessionCount, required: TYPICAL_MIN_SESSIONS,
    nominalDurationMin, metrics,
  };
  TYPICAL_CACHE.set(cacheKey, t);
  return t;
}

export function typicalForSession(athleteId: string, sessionId: string): AthleteBucketTypical | null {
  const s = demoSessions.find((x) => x.id === sessionId);
  if (!s) return null;
  return typicalFor(athleteId, bucketKeyFor(s));
}

/** Number of comparable sessions this athlete has in the given bucket (regardless of state). */
export function comparableSessionCount(athleteId: string, bucketKey: BucketKey): number {
  return ATHLETE_BUCKET_RECORDS.get(athleteId)?.get(bucketKey)?.length ?? 0;
}

/* ─────────────────────────── squad day-type typicals ─────────────────────────── */

const SQUAD_TYPICAL_CACHE = new Map<BucketKey, SquadBucketTypical>();

export function squadTypicalFor(bucketKey: BucketKey): SquadBucketTypical {
  const hit = SQUAD_TYPICAL_CACHE.get(bucketKey);
  if (hit) return hit;
  const { dayCode, sessionType } = parseBucketKey(bucketKey);
  const nominalDurationMin = nominalDurationFor(bucketKey);
  const perMetricSamples = new Map<TypicalMetric, { x: number; w: number }[]>();
  let contributing = 0;
  for (const a of demoAthletes) {
    const t = typicalFor(a.id, bucketKey);
    if (t.state !== "computed") continue;
    contributing++;
    for (const m of TYPICAL_METRICS) {
      const pm = t.metrics[m];
      if (!pm) continue;
      const arr = perMetricSamples.get(m) ?? [];
      // Weight athletes equally at the squad level (each athlete has already
      // been minutes-weighted internally). Using n as weight would let one
      // athlete's high-frequency bucket dominate; a squad typical should be
      // per-athlete, not per-appearance.
      arr.push({ x: pm.fullSession, w: 1 });
      perMetricSamples.set(m, arr);
    }
  }
  const metrics: SquadBucketTypical["metrics"] = {};
  for (const [m, samples] of perMetricSamples) {
    const { mean, sd, n } = weightedMeanSd(samples);
    metrics[m] = { fullSession: mean, sd, n };
  }
  const t: SquadBucketTypical = {
    bucketKey, dayCode, sessionType,
    nominalDurationMin,
    contributingAthletes: contributing,
    totalAthletes: demoAthletes.length,
    metrics,
  };
  SQUAD_TYPICAL_CACHE.set(bucketKey, t);
  return t;
}

/* ─────────────────────────── composition-matched expected sum ─────────────────────────── */

/**
 * Expected sum for a session: Σ over athletes who actually participated of
 * (their own typical per-minute rate for this bucket × minutes played in
 * this session). Only cumulative metrics — a "sum" of a rate is not a
 * meaningful figure and rate metrics are excluded on purpose.
 *
 * Honesty conditions (§5, load-bearing):
 *   - Withholding athletes are EXCLUDED from the sum, never substituted.
 *   - The returned object states its own coverage (contributed / participated).
 *   - If coverage is thinner than the floor, the sum withholds as a whole.
 */
export function expectedSumForSession(sessionId: string): ExpectedSumForSession {
  const s = demoSessions.find((x) => x.id === sessionId);
  if (!s) {
    return { state: "withheld", sessionId, bucketKey: "", participatedCount: 0, contributedCount: 0, coverage: 0, reason: "insufficient_coverage" };
  }
  const bucketKey = bucketKeyFor(s);
  const records = recordsForSession(sessionId);
  const participants = records.filter(
    (r) => r.participation != null && MINUTES_BEARING.has(r.participation) && r.minutes > 0,
  );
  const participatedCount = participants.length;

  const contributed: string[] = [];
  const withheldAthletes: string[] = [];
  const metricAcc = new Map<TypicalMetric, number>();

  for (const r of participants) {
    const t = typicalFor(r.athleteId, bucketKey);
    if (t.state !== "computed") {
      withheldAthletes.push(r.athleteId);
      continue;
    }
    contributed.push(r.athleteId);
    for (const m of CUMULATIVE_METRICS) {
      const pm = t.metrics[m];
      if (!pm || pm.perMinute == null) continue;
      metricAcc.set(m, (metricAcc.get(m) ?? 0) + pm.perMinute * r.minutes);
    }
  }

  const contributedCount = contributed.length;
  const coverage = participatedCount > 0 ? contributedCount / participatedCount : 0;
  if (contributedCount < EXPECTED_MIN_CONTRIBUTORS || coverage < EXPECTED_MIN_COVERAGE) {
    return {
      state: "withheld",
      sessionId, bucketKey,
      participatedCount, contributedCount, coverage,
      reason: "insufficient_coverage",
    };
  }
  const metrics: Partial<Record<TypicalMetric, number>> = {};
  for (const [m, v] of metricAcc) metrics[m] = v;
  return {
    state: "computed",
    sessionId, bucketKey,
    metrics,
    contributed, withheldAthletes,
    participatedCount, contributedCount,
    coverage,
  };
}

/* ─────────────────────────── enumeration helpers ─────────────────────────── */

/** All bucket keys that have at least one contributing session. */
export function allBucketKeys(): BucketKey[] {
  return Array.from(BUCKET_SESSIONS.keys()).sort();
}

/** For tests: the raw sample records for one athlete-bucket. */
export function _samplesFor(athleteId: string, bucketKey: BucketKey): readonly DemoRecord[] {
  return ATHLETE_BUCKET_RECORDS.get(athleteId)?.get(bucketKey) ?? [];
}
