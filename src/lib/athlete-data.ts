/**
 * ST2 — Athlete page · derivation layer (Workstream 02 · prompt 2).
 *
 * Pure data. No JSX. Everything the Summary spine draws is resolved
 * here — the component picks marks and never math.
 *
 * Rules folded in from the prompt:
 *   - Six metrics on one shared fixed axis, 40–160 % of the athlete's
 *     own typical for this session's day type. `ATHLETE_SPINE_DOMAIN`
 *     is a demo-calibrated placeholder; never auto-fit.
 *   - Band is mean ± 1 SD from `demo-typicals.ts`, not a flat ±5 %.
 *     A flat percentage would assert that every athlete/metric has the
 *     same normal range, which is exactly what this page rejects.
 *   - Four honest states: OK, hollow (thin coverage 40–80 %, CL only),
 *     withheld (below the coverage floor), building baseline
 *     (< TYPICAL_MIN_SESSIONS comparable — band/dot/delta all suppress
 *     together, absolute stays), beyond drawn range (caret + exact %).
 *   - sRPE is a load in AU; there is no `/10` anywhere in this section.
 */

import {
  demoAthletes,
  recordsForSession,
  demoSessions,
  type DemoRecord,
} from "./demo-library";
import {
  typicalForSession,
  TYPICAL_MIN_SESSIONS,
  type TypicalMetric,
  type PerMetricTypical,
} from "./demo-typicals";
import { METRICS, HR_COVERAGE_GATE, hrGateWithholds } from "./squad-metrics";
import { copy, tmpl } from "./copy-deck";

/** Fixed drawn range — demo-calibrated placeholder. Never auto-fit. */
export const ATHLETE_SPINE_DOMAIN: readonly [number, number] = [40, 160] as const;

/** HR-coverage floor for internal metrics. Below this the value withholds
 *  outright with its reason — no number, no dot. This is the ratified 80 %
 *  gate, enforced through `hrGateWithholds` in the metrics layer. */
export const VALUE_COVERAGE_FLOOR = HR_COVERAGE_GATE;

/** Above this, coverage is treated as complete. Between the gate and here
 *  the mark is hollow and carries `· NN% cov` at the value edge. */
export const COVERAGE_FULL = 100;


export type SpineAxis = "work" | "cost";
export type SpineGroup = "external" | "internal";

export type SpineMetricId =
  | "totalDistance"
  | "mMin"
  | "hsr"
  | "accDec"
  | "cardioLoad"
  | "srpeAU";

/** Ordered as it renders on the spine: external group first, internal at
 *  the foot. Ratified order — see prompt §1. */
export const SPINE_METRICS: readonly SpineMetricId[] = [
  "totalDistance", "mMin", "hsr", "accDec", "cardioLoad", "srpeAU",
] as const;

export type SpineRowState =
  | { kind: "ok" }
  | { kind: "hollow"; coveragePct: number }          // internal + 40–80 % cov
  | { kind: "withheld"; reason: "coverage" | "notSubmitted" | "notParticipating" }
  | { kind: "building" }                             // no baseline (band/dot/delta suppress)
  | { kind: "beyondRange"; side: "high" | "low"; truePct: number };

export type SpineRow = {
  metricId: SpineMetricId;
  /** From `squad-metrics.ts` — see below. Never authored here. */
  label: string;
  short: string;
  axis: SpineAxis;
  group: SpineGroup;
  unit: string;
  /** Absolute this session, in metric unit. Null when the athlete did
   *  not participate. */
  value: number | null;
  /** Reference (full-session typical) in same unit as `value`. Null when
   *  baseline is building. */
  reference: number | null;
  /** ± 1 SD from the typical, converted to a pct of typical. Null when
   *  building or reference is 0. */
  bandLoPct: number | null;
  bandHiPct: number | null;
  /** Value as % of typical (100 = typical). Null when withheld/building. */
  valuePct: number | null;
  /** Signed delta % vs typical. Null when withheld/building. */
  deltaPct: number | null;
  state: SpineRowState;
  /** `salience` and `flagged` are stamped at spine assembly, not per-row math. */
  salience: boolean;
  flagged: boolean;
};

export type SpineHeaderState = {
  /** True when this athlete has an overall building baseline in this
   *  bucket. The card prints one strip; per-row band/dot/delta suppress. */
  buildingBaseline: boolean;
  /** Number of comparable sessions in this bucket (informational). */
  comparableCount: number;
  /** For copy: the human basis phrase — read against "MD (match)". */
  basisPhrase: string;
};

export type AthleteSpine = {
  athleteId: string;
  sessionId: string;
  rows: SpineRow[];
  header: SpineHeaderState;
};

/* ─────────────────── metric display registry ───────────────────
 * The prompt requires labels to come from squad-metrics.ts — that
 * module is the technical record of metric display names. We import
 * only its labels/units and keep this list restricted to the six
 * metrics the spine actually draws.
 */


type SpineMetricMeta = {
  label: string;
  short: string;
  axis: SpineAxis;
  group: SpineGroup;
  unit: string;
};

export const SPINE_METRIC_META: Record<SpineMetricId, SpineMetricMeta> = {
  totalDistance: {
    label: METRICS.totalDistance.label,
    short: METRICS.totalDistance.short,
    axis: "work", group: "external",
    unit: METRICS.totalDistance.unit,
  },
  mMin: {
    label: METRICS.mMin.label,
    short: METRICS.mMin.short,
    axis: "work", group: "external",
    unit: METRICS.mMin.unit,
  },
  hsr: {
    label: METRICS.hsr.label,
    short: METRICS.hsr.short,
    axis: "work", group: "external",
    unit: METRICS.hsr.unit,
  },
  accDec: {
    label: METRICS.accDec.label,
    short: METRICS.accDec.short,
    axis: "work", group: "external",
    unit: METRICS.accDec.unit,
  },
  cardioLoad: {
    label: METRICS.cardioLoad.label,
    short: METRICS.cardioLoad.short,
    axis: "cost", group: "internal",
    unit: METRICS.cardioLoad.unit,
  },
  // sRPE prints as a LOAD in AU here, not a rating out of ten.
  // The `/10` unit on METRICS.srpe belongs to Squad's rating column and
  // does not travel to this page. We read the display *label* from the
  // library (governed record) and override only the unit at this call site.
  //
  // Governance gap logged in ST2_Build_Findings: the metric library
  // needs a first-class `srpeAU` entry with unit `AU`. Adding one is a
  // Decision-Set-governed change, not a build call — hence the local
  // override here.
  srpeAU: {
    label: METRICS.srpe.label,
    short: METRICS.srpe.short,
    axis: "cost", group: "internal",
    unit: "AU",
  },
};

/* ─────────────────── flag → metric mapping ─────────────────── */

const FLAG_REASON_MAP: Array<{ needle: RegExp; id: SpineMetricId }> = [
  { needle: /total distance/i, id: "totalDistance" },
  { needle: /m\/min/i,          id: "mMin" },
  { needle: /high-speed|hsr/i,  id: "hsr" },
  { needle: /acc/i,             id: "accDec" },
  { needle: /cardio/i,          id: "cardioLoad" },
  { needle: /srpe/i,            id: "srpeAU" },
];

/** Best-effort mapping from a Tier-1 `reason` string to a spine metric.
 *  Compound reasons like "Sprint distance · HSR" fall through to `hsr`;
 *  a reason with no match returns null and the spine does not hoist. */
export function flaggedMetricFor(reason: string | null | undefined): SpineMetricId | null {
  if (!reason) return null;
  for (const { needle, id } of FLAG_REASON_MAP) {
    if (needle.test(reason)) return id;
  }
  return null;
}

/* ─────────────────── the assembly ─────────────────── */

function recordFor(sessionId: string, athleteId: string): DemoRecord | undefined {
  return recordsForSession(sessionId).find((r) => r.athleteId === athleteId);
}

function readMetricValue(rec: DemoRecord | undefined, m: SpineMetricId): number | null {
  if (!rec) return null;
  const v = (rec as unknown as Record<string, number | null>)[m];
  return v == null ? null : v;
}

/** Convert a per-min typical row to a full-session reference for one
 *  metric. Cumulative metrics multiply by the session's nominal duration;
 *  rate metrics take `fullSession` directly. */
function referenceFor(pm: PerMetricTypical): number {
  // PerMetricTypical.fullSession is already the full-session value
  // whether rate or cumulative — see demo-typicals.ts.
  return pm.fullSession;
}

export function spineForAthleteSession(
  athleteId: string,
  sessionId: string,
  opts?: { flaggedMetric?: SpineMetricId | null },
): AthleteSpine {
  const rec = recordFor(sessionId, athleteId);
  const t = typicalForSession(athleteId, sessionId);
  const participated =
    rec != null &&
    rec.participation != null &&
    rec.minutes > 0 &&
    (rec.participation === "Full" || rec.participation === "Part" || rec.participation === "Modified");

  const buildingBaseline = t?.state !== "computed";
  const comparableCount = t?.state === "computed"
    ? t.sessionCount
    : (t?.state === "withheld" ? t.sessionCount : 0);

  const hrCovPct = rec?.hrCoveragePct ?? null;

  const rows: SpineRow[] = SPINE_METRICS.map((m) => {
    const meta = SPINE_METRIC_META[m];
    const rawValue = participated ? readMetricValue(rec, m as unknown as SpineMetricId) : null;

    // Reference (full-session typical for this metric)
    const pm = t?.state === "computed" ? t.metrics[m as TypicalMetric] : undefined;
    const reference = pm ? referenceFor(pm) : null;
    const sd = pm ? pm.sd : null;

    // Band withholds when the spread withholds — per metric. sd = 0 is
    // not a narrow spread, it is an absent one; drawing a zero-width
    // hairline would assert perfect certainty (the "sprintDist" defect
    // logged in the findings file). Dot and value are unaffected.
    const bandLoPct = reference != null && sd != null && sd > 0 && reference > 0
      ? ((reference - sd) / reference) * 100
      : null;
    const bandHiPct = reference != null && sd != null && sd > 0 && reference > 0
      ? ((reference + sd) / reference) * 100
      : null;

    // participation gate
    if (!participated) {
      return baseRow(m, meta, null, reference, bandLoPct, bandHiPct, { kind: "withheld", reason: "notParticipating" });
    }

    // sRPE — value can be missing when not submitted
    if (m === "srpeAU" && rawValue == null) {
      return baseRow(m, meta, null, reference, bandLoPct, bandHiPct, { kind: "withheld", reason: "notSubmitted" });
    }

    // Internal (Cardio Load) — the shared 80 % HR-coverage gate.
    if (m === "cardioLoad") {
      if (rawValue == null || hrGateWithholds(hrCovPct, "cardioLoad")) {
        return baseRow(m, meta, null, reference, bandLoPct, bandHiPct, { kind: "withheld", reason: "coverage" });
      }
    }


    // Building baseline — value stays; band/dot/delta suppress.
    if (buildingBaseline || reference == null || reference <= 0) {
      return baseRow(m, meta, rawValue, reference, null, null, { kind: "building" });
    }

    const valuePct = (rawValue! / reference) * 100;
    const deltaPct = valuePct - 100;

    // Beyond drawn range?
    if (valuePct > ATHLETE_SPINE_DOMAIN[1]) {
      return finalizeRow(m, meta, rawValue!, reference, bandLoPct, bandHiPct, valuePct, deltaPct,
        { kind: "beyondRange", side: "high", truePct: valuePct });
    }
    if (valuePct < ATHLETE_SPINE_DOMAIN[0]) {
      return finalizeRow(m, meta, rawValue!, reference, bandLoPct, bandHiPct, valuePct, deltaPct,
        { kind: "beyondRange", side: "low", truePct: valuePct });
    }

    // Hollow (internal, thin coverage between floor and full)
    if (m === "cardioLoad" && hrCovPct != null && hrCovPct < COVERAGE_FULL) {
      return finalizeRow(m, meta, rawValue!, reference, bandLoPct, bandHiPct, valuePct, deltaPct,
        { kind: "hollow", coveragePct: hrCovPct });
    }

    return finalizeRow(m, meta, rawValue!, reference, bandLoPct, bandHiPct, valuePct, deltaPct, { kind: "ok" });
  });

  // Salience — furthest from 100 % among rows that have a delta.
  let salientIdx = -1;
  let maxAbs = -1;
  rows.forEach((r, i) => {
    if (r.deltaPct == null) return;
    const a = Math.abs(r.deltaPct);
    if (a > maxAbs) { maxAbs = a; salientIdx = i; }
  });
  if (salientIdx >= 0) rows[salientIdx].salience = true;

  // Flag → set flagged flag on that row. (The hoist itself happens in
  // the component: internal rows never hoist above the group boundary.)
  const flaggedId = opts?.flaggedMetric ?? null;
  if (flaggedId) {
    const r = rows.find((x) => x.metricId === flaggedId);
    if (r) r.flagged = true;
  }

  const header: SpineHeaderState = {
    buildingBaseline,
    comparableCount,
    basisPhrase: t
      ? tmpl("athlete.summary.basisPhraseTemplate", {
          dayCode: t.dayCode,
          sessionType: t.sessionType,
        })
      : copy("athlete.summary.basisFallback"),
  };

  return { athleteId, sessionId, rows, header };
}

function baseRow(
  m: SpineMetricId,
  meta: SpineMetricMeta,
  value: number | null,
  reference: number | null,
  bandLoPct: number | null,
  bandHiPct: number | null,
  state: SpineRowState,
): SpineRow {
  return {
    metricId: m,
    label: meta.label, short: meta.short,
    axis: meta.axis, group: meta.group,
    unit: meta.unit,
    value, reference,
    bandLoPct, bandHiPct,
    valuePct: null, deltaPct: null,
    state,
    salience: false, flagged: false,
  };
}

function finalizeRow(
  m: SpineMetricId,
  meta: SpineMetricMeta,
  value: number,
  reference: number,
  bandLoPct: number | null,
  bandHiPct: number | null,
  valuePct: number,
  deltaPct: number,
  state: SpineRowState,
): SpineRow {
  return {
    metricId: m,
    label: meta.label, short: meta.short,
    axis: meta.axis, group: meta.group,
    unit: meta.unit,
    value, reference,
    bandLoPct, bandHiPct,
    valuePct, deltaPct,
    state,
    salience: false, flagged: false,
  };
}

/* ─────────────────── character-line derivation ─────────────────── */

/**
 * One plain sentence about the shape of the session — what the marks
 * cannot say. Data-derived; no fixed transcript.
 */
export function characterLineFor(spine: AthleteSpine): string {
  const a = demoAthletes.find((x) => x.id === spine.athleteId);
  const rows = spine.rows.filter((r) => r.deltaPct != null);
  if (rows.length === 0) {
    return copy("athlete.summary.character.fallback");
  }

  // Aggregate external/internal shape.
  const ext = rows.filter((r) => r.group === "external");
  const intl = rows.filter((r) => r.group === "internal");
  const meanDelta = (xs: SpineRow[]) =>
    xs.length ? xs.reduce((s, r) => s + (r.deltaPct ?? 0), 0) / xs.length : 0;

  const extMean = meanDelta(ext);
  const intMean = meanDelta(intl);
  const salient = rows.find((r) => r.salience);

  const dir = (d: number): "up" | "down" | "flat" =>
    d > 6 ? "up" : d < -6 ? "down" : "flat";

  const first = a ? `${a.name.split(" ").pop()}` : copy("athlete.summary.character.anon");

  const shapeKey = ((): string => {
    const e = dir(extMean), i = dir(intMean);
    if (e === "up"   && i === "up")   return "athlete.summary.character.shape.upUp";
    if (e === "up"   && i === "flat") return "athlete.summary.character.shape.upFlat";
    if (e === "up"   && i === "down") return "athlete.summary.character.shape.upDown";
    if (e === "flat" && i === "up")   return "athlete.summary.character.shape.flatUp";
    if (e === "down" && i === "up")   return "athlete.summary.character.shape.downUp";
    if (e === "down" && i === "flat") return "athlete.summary.character.shape.downFlat";
    if (e === "down" && i === "down") return "athlete.summary.character.shape.downDown";
    if (e === "flat" && i === "down") return "athlete.summary.character.shape.flatDown";
    return "athlete.summary.character.shape.flatFlat";
  })();

  const shape = copy(shapeKey);
  const tail = salient
    ? tmpl("athlete.summary.character.tailTemplate", { metric: salient.label.toLowerCase() })
    : "";

  return tmpl("athlete.summary.character.template", { first, shape, tail });
}

/* ─────────────────── periods derivation (fix 7.1) ─────────────────── */

export type PeriodOption =
  | { id: string; kind: "all"; label: string; count: number }
  | { id: string; kind: "block"; label: string; index: number }
  | { id: string; kind: "added"; label: string };

/**
 * 15-minute block set for the session's duration. Six 15-min blocks
 * plus an added-time block when the session runs past 90 min. Matches
 * the Session Periods granularity. Non-match sessions collapse to a
 * single "period 1" so the chip still opens with a real slot.
 */
export function periodOptionsFor(sessionId: string): PeriodOption[] {
  const session = demoSessions.find((s) => s.id === sessionId);
  if (!session) return [];
  const isMatch = session.type === "match";
  if (!isMatch) {
    return [
      { id: "all", kind: "all", label: tmpl("athlete.periods.allTemplate", { n: 1 }), count: 1 },
      { id: "p1", kind: "block", label: tmpl("athlete.periods.blockTemplate", { n: 1 }), index: 1 },
    ];
  }
  const blocks = Math.min(6, Math.floor(session.durationMin / 15));
  const hasAdded = session.durationMin > blocks * 15;
  const count = blocks + (hasAdded ? 1 : 0);
  const opts: PeriodOption[] = [
    { id: "all", kind: "all", label: tmpl("athlete.periods.allTemplate", { n: count }), count },
  ];
  for (let i = 1; i <= blocks; i++) {
    opts.push({
      id: `p${i}`,
      kind: "block",
      label: tmpl("athlete.periods.blockTemplate", { n: i }),
      index: i,
    });
  }
  if (hasAdded) {
    opts.push({ id: "added", kind: "added", label: copy("athlete.periods.addedTime") });
  }
  return opts;
}

export { TYPICAL_MIN_SESSIONS };
