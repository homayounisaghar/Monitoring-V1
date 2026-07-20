/**
 * ST2 — Recovery data (HRV) and Balance (per-athlete L/R load share).
 *
 * Two ratified metrics that extend the demo library as a third and fourth
 * read alongside external work and internal cost.
 *
 *   - HRV is a daily, between-session, per-athlete state. Meaningful only
 *     as deviation from that athlete's own trailing 7-day baseline; raw
 *     ms must never be averaged across athletes because personal baselines
 *     differ hugely. The % of own baseline may be averaged because each
 *     value is already normalised.
 *   - Balance is a within-session, per-athlete L/R distribution of load.
 *     The neutral point is the athlete's own habitual split, never 50/50 —
 *     asserting symmetry is correct would be a verdict, and this app
 *     renders none.
 *
 * Both render in NEUTRAL SLATE. Neither is external work nor internal
 * cost, so neither joins those groups.
 *
 * Deterministic under the same seed discipline as demo-library.ts. This
 * module reads from demo-library (roster, dates, session index) and adds
 * its own read layer; it does NOT mutate the library.
 */

import {
  demoAthletes,
  demoSessions,
  DEMO_TODAY,
  SEASON_START_ISO,
} from "./demo-library";

/* ─────────────────────────── constants ─────────────────────────── */

export const HRV_TRAILING_WINDOW_DAYS = 7;
/** Minimum readings in the trailing window before % of baseline may print. */
export const HRV_BASELINE_MIN_READINGS = 5;

/** Fixed drawn range for the Longitudinal Days recovery lane. Never
 *  auto-fits, per the "80–120" spec. */
export const HRV_LANE_DOMAIN: readonly [number, number] = [80, 120] as const;

/** Slate ink for both HRV and Balance marks — a single existing token,
 *  never a new hue. */
export const RECOVERY_INK_VAR = "var(--color-text-secondary)";

/* ─────────────────────────── PRNG (own copy) ─────────────────────────── */

const DEMO_SEED = 0x51_2E_2E_07 >>> 0;

function mulberry32(seed: number) {
  let s = seed >>> 0;
  return function () {
    s = (s + 0x6d2b79f5) >>> 0;
    let t = s;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
function hashSeed(...parts: (string | number)[]): number {
  let h = DEMO_SEED >>> 0;
  const s = parts.join("|");
  for (let i = 0; i < s.length; i++) {
    h = Math.imul(h ^ s.charCodeAt(i), 0x01000193) >>> 0;
  }
  return h >>> 0;
}
function jit(amp: number, ...parts: (string | number)[]): number {
  const r = mulberry32(hashSeed(...parts))();
  return (r * 2 - 1) * amp;
}

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
function addDaysISO(iso: string, n: number): string {
  return fmtISO(parseISO(iso) + n * 86_400_000);
}

/* ─────────────────────────── baselines ─────────────────────────── */

/**
 * Personal HRV baseline (ms) per athlete — deterministic, spread across
 * ~40–110 to make the "raw ms never averaged" rule visible even in the
 * demo. Assigned by a hash of the athlete id, not by list order.
 */
const HRV_BASELINE_MS: Record<string, number> = (() => {
  const out: Record<string, number> = {};
  for (const a of demoAthletes) {
    // Uniform-ish spread inside [42, 108] with a deterministic per-id offset.
    const r = mulberry32(hashSeed(a.id, "hrv-base"))();
    out[a.id] = Math.round(42 + r * (108 - 42));
  }
  return out;
})();

export function hrvBaselineFor(athleteId: string): number | null {
  return HRV_BASELINE_MS[athleteId] ?? null;
}

/**
 * Personal balance typical (percent on LEFT foot/side, 44–56). The tick
 * on the Balance bar sits here, never at 50.
 */
const BALANCE_TYPICAL_L: Record<string, number> = (() => {
  const out: Record<string, number> = {};
  for (const a of demoAthletes) {
    // 44 to 56 inclusive; deterministic per athlete.
    out[a.id] = 44 + (hashSeed(a.id, "bal-typ") % 13);
  }
  return out;
})();

export function balanceTypicalFor(athleteId: string): { leftPct: number; rightPct: number } {
  const L = BALANCE_TYPICAL_L[athleteId] ?? 50;
  return { leftPct: L, rightPct: 100 - L };
}

/* ─────────────────────────── match dates & rest ─────────────────────────── */

const MATCH_DATES = new Set(
  demoSessions.filter((s) => s.type === "match").map((s) => s.dateISO),
);

/** Lange's chronic suppression window covers his injury stretch (see
 *  demo-library `langeParticipationOn`). Any morning inside this range
 *  reads consistently low against his own baseline. */
function langeSuppressed(dateISO: string): boolean {
  return dateISO >= "2026-07-06" && dateISO <= DEMO_TODAY;
}

/** Sparse absent-record pattern per athlete. Not zeros — the reading
 *  simply wasn't logged that morning. ~2% of days. */
function readingIsAbsent(athleteId: string, dateISO: string): boolean {
  return hashSeed(athleteId, dateISO, "hrv-absent") % 50 === 0;
}

/* ─────────────────────────── HRV reading ─────────────────────────── */

/**
 * Morning HRV reading (rMSSD-like, ms) for an athlete on a calendar day.
 * Returns null when the athlete has no record for that morning; a zero
 * would be a false "reading of zero". Includes match-after suppression
 * (8–20 % recovering over ~2 days) and Lange's chronic suppression.
 */
export function hrvReadingOnDay(athleteId: string, dateISO: string): number | null {
  if (dateISO < SEASON_START_ISO) return null;
  if (dateISO > DEMO_TODAY) return null;
  if (readingIsAbsent(athleteId, dateISO)) return null;
  const base = HRV_BASELINE_MS[athleteId];
  if (base == null) return null;

  // Baseline day-to-day variation ±5–12 %.
  const dayVarPct = jit(0.09, athleteId, dateISO, "hrv-var");
  let ms = base * (1 + dayVarPct);

  // Match-after suppression: yesterday = -8 to -20 %, day-two = -3 to -8 %.
  const yest = addDaysISO(dateISO, -1);
  const dayTwo = addDaysISO(dateISO, -2);
  if (MATCH_DATES.has(yest)) {
    const drop = 0.08 + Math.abs(jit(0.06, athleteId, yest, "hrv-supp1")) * 2;
    ms *= 1 - drop;
  } else if (MATCH_DATES.has(dayTwo)) {
    const drop = 0.03 + Math.abs(jit(0.025, athleteId, dayTwo, "hrv-supp2")) * 2;
    ms *= 1 - drop;
  }

  if (athleteId === "lange" && langeSuppressed(dateISO)) {
    ms *= 0.72 + jit(0.03, athleteId, dateISO, "hrv-lange");
  }

  return Math.max(10, Math.round(ms));
}

/**
 * Trailing 7-day mean of the athlete's own readings, ending the day
 * BEFORE `dateISO`. This is the baseline against which `dateISO`'s
 * reading is compared — the reading itself is never part of its own
 * baseline.
 */
export function hrvBaselineOnDay(
  athleteId: string,
  dateISO: string,
): { mean: number | null; count: number } {
  let sum = 0;
  let count = 0;
  for (let back = 1; back <= HRV_TRAILING_WINDOW_DAYS; back++) {
    const d = addDaysISO(dateISO, -back);
    if (d < SEASON_START_ISO) break;
    const r = hrvReadingOnDay(athleteId, d);
    if (r != null) {
      sum += r;
      count += 1;
    }
  }
  if (count === 0) return { mean: null, count: 0 };
  return { mean: sum / count, count };
}

export type HrvReadState =
  | {
      state: "ok";
      valueMs: number;
      baselineMs: number;
      pct: number;
      readingCount: number;
    }
  | { state: "withheld"; reason: "notEnoughReadings"; readingCount: number; min: number }
  | { state: "withheld"; reason: "noReading" }
  | { state: "withheld"; reason: "notYet" };

/** Reading as a % of the athlete's own baseline, withheld until the
 *  trailing window has at least `HRV_BASELINE_MIN_READINGS` readings. */
export function hrvPctOfBaseline(athleteId: string, dateISO: string): HrvReadState {
  if (dateISO > DEMO_TODAY) return { state: "withheld", reason: "notYet" };
  const v = hrvReadingOnDay(athleteId, dateISO);
  if (v == null) return { state: "withheld", reason: "noReading" };
  const b = hrvBaselineOnDay(athleteId, dateISO);
  if (b.mean == null || b.count < HRV_BASELINE_MIN_READINGS) {
    return {
      state: "withheld",
      reason: "notEnoughReadings",
      readingCount: b.count,
      min: HRV_BASELINE_MIN_READINGS,
    };
  }
  return {
    state: "ok",
    valueMs: v,
    baselineMs: b.mean,
    pct: (v / b.mean) * 100,
    readingCount: b.count,
  };
}

/**
 * The recovery RESPONSE to a session — read on the morning AFTER.
 * When that morning hasn't happened yet, withholds with reason "notYet".
 */
export function hrvResponseForSession(
  athleteId: string,
  sessionId: string,
): HrvReadState & { morningAfterISO: string } {
  const s = demoSessions.find((x) => x.id === sessionId);
  if (!s) return { state: "withheld", reason: "notYet", morningAfterISO: "" };
  const after = addDaysISO(s.dateISO, 1);
  if (after > DEMO_TODAY) {
    return { state: "withheld", reason: "notYet", morningAfterISO: after };
  }
  return { ...hrvPctOfBaseline(athleteId, after), morningAfterISO: after };
}

/**
 * Squad-level recovery response: median of each eligible athlete's HRV
 * as a % of his own baseline, the morning after `sessionId`. Median is
 * safe here because each contributing value is already normalised to
 * its own baseline.
 */
export function hrvSquadResponseForSession(sessionId: string):
  | { state: "ok"; medianPct: number; read: number; eligible: number; morningAfterISO: string }
  | { state: "withheld"; reason: "notYet"; morningAfterISO: string }
  | { state: "withheld"; reason: "none"; morningAfterISO: string } {
  const s = demoSessions.find((x) => x.id === sessionId);
  if (!s) return { state: "withheld", reason: "none", morningAfterISO: "" };
  const after = addDaysISO(s.dateISO, 1);
  if (after > DEMO_TODAY) {
    return { state: "withheld", reason: "notYet", morningAfterISO: after };
  }
  const eligible = demoAthletes.filter((a) => after >= a.joinedISO);
  const pcts: number[] = [];
  for (const a of eligible) {
    const r = hrvPctOfBaseline(a.id, after);
    if (r.state === "ok") pcts.push(r.pct);
  }
  if (pcts.length === 0) {
    return { state: "withheld", reason: "none", morningAfterISO: after };
  }
  pcts.sort((x, y) => x - y);
  const mid = Math.floor(pcts.length / 2);
  const median = pcts.length % 2 ? pcts[mid] : (pcts[mid - 1] + pcts[mid]) / 2;
  return {
    state: "ok",
    medianPct: median,
    read: pcts.length,
    eligible: eligible.length,
    morningAfterISO: after,
  };
}

/**
 * Longitudinal Days lane read — the same squad-median % of own baseline,
 * for an arbitrary calendar day (not tied to a session's morning-after).
 * Continues across rest days and days with no session, which is the
 * whole point of the lane. Days below the readings floor render empty.
 */
export function hrvSquadOnDay(
  dateISO: string,
):
  | { state: "ok"; medianPct: number; read: number; eligible: number }
  | { state: "withheld"; reason: "thin" } {
  const eligible = demoAthletes.filter((a) => dateISO >= a.joinedISO);
  const pcts: number[] = [];
  for (const a of eligible) {
    const r = hrvPctOfBaseline(a.id, dateISO);
    if (r.state === "ok") pcts.push(r.pct);
  }
  const MIN_CONTRIB = Math.max(6, Math.floor(eligible.length * 0.4));
  if (pcts.length < MIN_CONTRIB) return { state: "withheld", reason: "thin" };
  pcts.sort((x, y) => x - y);
  const mid = Math.floor(pcts.length / 2);
  const median = pcts.length % 2 ? pcts[mid] : (pcts[mid - 1] + pcts[mid]) / 2;
  return {
    state: "ok",
    medianPct: median,
    read: pcts.length,
    eligible: eligible.length,
  };
}

/* ─────────────────────────── Balance ─────────────────────────── */

export type BalanceRead = {
  leftPct: number;
  rightPct: number;
  typicalLeftPct: number;
  /** L% minus their typical L% — signed points. */
  deltaPts: number;
};

/**
 * Per-athlete, per-session L/R load split summing to 100. Absent on
 * recovery sessions (no L/R read to derive) and on sessions where the
 * athlete did not accumulate minutes. K. Werner carries a notable
 * deviation on the pinned 18 Jul session.
 */
export function balanceForSession(
  athleteId: string,
  sessionId: string,
): BalanceRead | null {
  const s = demoSessions.find((x) => x.id === sessionId);
  if (!s) return null;
  if (s.type === "recovery") return null;
  const typ = BALANCE_TYPICAL_L[athleteId];
  if (typ == null) return null;

  const isPinned = sessionId === "s-2026-07-04-dortmund";
  let L: number;
  if (isPinned && athleteId === "werner") {
    // Notable deviation: 8-point drop from his typical.
    L = typ - 8 + jit(0.7, athleteId, sessionId, "bal-werner");
  } else {
    L = typ + jit(3.5, athleteId, sessionId, "bal");
  }
  L = Math.max(30, Math.min(70, Math.round(L)));
  return {
    leftPct: L,
    rightPct: 100 - L,
    typicalLeftPct: typ,
    deltaPts: L - typ,
  };
}
