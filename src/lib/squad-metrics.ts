/**
 * ST2 — Squad section metric library + per-athlete raw values.
 *
 * The load-bearing build rule: this module exposes RAW value + RAW
 * reference per (athlete × metric). The Squad section derives every
 * delta, every "%"-mode cell, every sort key, and the squad-avg row
 * from these — nothing is pre-tabulated.
 *
 * Reference derivation:
 *   - Position typical (full match) × minutes/90 for cumulative metrics
 *   - Position typical as-is for rate metrics (m/min, sRPE, Z4+Z5)
 *   - No reference at all for the building-baseline athlete
 *   - No reference for identity columns (min)
 *   - "not compared" for vs-full-match metrics on <60' partials
 */
import { BUILDING_ID } from "./session-flags";
import type { Athlete, PositionCode } from "./session-data";

export type Axis = "work" | "cost" | "neutral";
export type ScalingPolicy = "identity" | "cumulative" | "rate" | "vsFull";

export type MetricId =
  | "min"
  | "totalDistance"
  | "mMin"
  | "hsr"
  | "accDec"
  | "cardioLoad"
  | "srpe"
  | "sprintDist"
  | "repeatSprints"
  | "z4z5Share"
  | "volumePct"
  | "intensityPct"
  | "maxVel";

export type Metric = {
  id: MetricId;
  label: string;
  short: string;
  axis: Axis;
  unit: string;
  group: "identity" | "external" | "internal";
  scaling: ScalingPolicy;
  decimals?: number;
  /** Chart-mode shared-scale ceiling (in unit's terms). */
  chartMax: number;
};

export const METRICS: Record<MetricId, Metric> = {
  min:           { id: "min",           label: "Min",             short: "Min",   axis: "neutral", unit: "'",     group: "identity", scaling: "identity",   chartMax: 100 },
  totalDistance: { id: "totalDistance", label: "Total distance",  short: "Dist",  axis: "work",    unit: "m",     group: "external", scaling: "cumulative", chartMax: 13000 },
  mMin:          { id: "mMin",          label: "m/min",           short: "m/min", axis: "work",    unit: "m/min", group: "external", scaling: "rate",       decimals: 0, chartMax: 140 },
  hsr:           { id: "hsr",           label: "HSR",             short: "HSR",   axis: "work",    unit: "m",     group: "external", scaling: "cumulative", chartMax: 1200 },
  accDec:        { id: "accDec",        label: "Acc–Dec",         short: "A/D",   axis: "work",    unit: "ct",    group: "external", scaling: "cumulative", chartMax: 160 },
  cardioLoad:    { id: "cardioLoad",    label: "Cardio Load",     short: "CL",    axis: "cost",    unit: "CL",    group: "internal", scaling: "cumulative", chartMax: 300 },
  srpe:          { id: "srpe",          label: "sRPE",            short: "sRPE",  axis: "cost",    unit: "/10",   group: "internal", scaling: "rate",       decimals: 1, chartMax: 10 },
  sprintDist:    { id: "sprintDist",    label: "Sprint distance", short: "Sprint",axis: "work",    unit: "m",     group: "external", scaling: "cumulative", chartMax: 500 },
  repeatSprints: { id: "repeatSprints", label: "Repeat sprints",  short: "R-spr", axis: "work",    unit: "ct",    group: "external", scaling: "cumulative", chartMax: 30 },
  z4z5Share:     { id: "z4z5Share",     label: "Z4+Z5 share",     short: "Z4+5",  axis: "cost",    unit: "%",     group: "internal", scaling: "rate",       decimals: 0, chartMax: 50 },
  volumePct:     { id: "volumePct",     label: "Volume %",        short: "Vol%",  axis: "work",    unit: "%",     group: "external", scaling: "vsFull",     decimals: 0, chartMax: 150 },
  intensityPct:  { id: "intensityPct",  label: "Intensity %",     short: "Int%",  axis: "work",    unit: "%",     group: "external", scaling: "vsFull",     decimals: 0, chartMax: 150 },
  maxVel:        { id: "maxVel",         label: "Max velocity",    short: "Max vel", axis: "work",  unit: "km/h",  group: "external", scaling: "identity",   decimals: 1, chartMax: 40 },
};

/** Athlete + 7 metric columns = 8 default columns. */
export const DEFAULT_COLUMNS: MetricId[] = [
  "min", "totalDistance", "mMin", "hsr", "accDec", "cardioLoad", "srpe",
];

export const COLUMN_LIBRARY: { group: "external" | "internal"; ids: MetricId[] }[] = [
  { group: "external", ids: ["totalDistance", "mMin", "hsr", "accDec", "sprintDist", "repeatSprints", "volumePct", "intensityPct"] },
  { group: "internal", ids: ["cardioLoad", "srpe", "z4z5Share"] },
];

export const MAX_COLUMNS = 12;

/* ---------- Position typicals (full-match for cumulative, direct for rate) ---------- */

const posTypical: Record<PositionCode, Partial<Record<MetricId, number>>> = {
  GK:  { totalDistance: 4900,  mMin: 55,  hsr: 120, accDec: 45,  cardioLoad: 130, srpe: 6.4, sprintDist: 30,  repeatSprints: 3,  z4z5Share: 8,  volumePct: 100, intensityPct: 100 },
  DEF: { totalDistance: 9800,  mMin: 105, hsr: 620, accDec: 115, cardioLoad: 220, srpe: 7.0, sprintDist: 180, repeatSprints: 12, z4z5Share: 22, volumePct: 100, intensityPct: 100 },
  MID: { totalDistance: 11200, mMin: 118, hsr: 780, accDec: 130, cardioLoad: 250, srpe: 7.2, sprintDist: 220, repeatSprints: 15, z4z5Share: 28, volumePct: 100, intensityPct: 100 },
  ATT: { totalDistance: 10400, mMin: 110, hsr: 900, accDec: 125, cardioLoad: 235, srpe: 7.1, sprintDist: 340, repeatSprints: 20, z4z5Share: 32, volumePct: 100, intensityPct: 100 },
};

/* ---------- Deltas: overrides for the flagged athletes, deterministic jitter otherwise ---------- */

const OVERRIDE_DELTA: Record<string, Partial<Record<MetricId, number>>> = {
  fischer:  { sprintDist: 0.34, hsr: 0.10, totalDistance: 0.07, repeatSprints: 0.25 },
  werner:   { hsr: 0.22, sprintDist: 0.14, totalDistance: 0.06 },
  hofmann:  { totalDistance: 0.14, hsr: 0.08, mMin: 0.05 },
  schaefer: { totalDistance: 0.19, hsr: 0.15, mMin: 0.09, cardioLoad: -0.03, srpe: -0.02, z4z5Share: -0.04 },
};

function jitter(id: string, m: MetricId): number {
  let h = 0;
  const s = id + ":" + m;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0;
  const n = ((h % 41) + 41) % 41; // 0..40
  return (n - 20) / 100; // -0.20..+0.20
}

/* ---------- Public API: refFor / valueFor / cell state ---------- */

export function refFor(a: Athlete, m: Metric, buildingIds?: Set<string>): number | null {
  const bset = buildingIds ?? new Set([BUILDING_ID]);
  if (a.participation === null) return null;
  if (m.scaling === "identity") return null;
  if (bset.has(a.id)) return null;
  const pt = posTypical[a.position]?.[m.id];
  if (pt == null) return null;
  if (m.scaling === "cumulative") return pt * (a.minutes / 90);
  return pt;
}

export function valueFor(a: Athlete, m: Metric): number | null {
  if (a.participation === null) return null;
  if (m.id === "min") return a.minutes;
  if (m.id === "srpe" && !a.srpeSubmitted) return null;
  const pt = posTypical[a.position]?.[m.id];
  if (pt == null) return null;
  const scaleFactor = m.scaling === "cumulative" ? a.minutes / 90 : 1;
  const base = pt * scaleFactor;
  const delta = OVERRIDE_DELTA[a.id]?.[m.id] ?? jitter(a.id, m.id);
  const raw = base * (1 + delta);
  if (m.decimals != null) return Number(raw.toFixed(m.decimals));
  return Math.round(raw);
}

export type CellState =
  | "ok"           // number + delta/%
  | "not_compared" // partial + vsFull metric
  | "building"     // no reference exists (Köhler)
  | "dnp"          // did not participate
  | "empty";       // "—" (no data or non-submitter)

export function cellState(a: Athlete, m: Metric, buildingIds?: Set<string>): CellState {
  const bset = buildingIds ?? new Set([BUILDING_ID]);
  if (a.participation === null) return "dnp";
  if (m.scaling === "identity") return "ok";
  if (bset.has(a.id)) return "building";
  if (m.scaling === "vsFull" && a.minutes < 60) return "not_compared";
  if (m.id === "srpe" && !a.srpeSubmitted) return "empty";
  if (valueFor(a, m) == null) return "empty";
  return "ok";
}

/** True where cumulative metric on a partial player — deltas are minutes-scaled and tagged "· scaled". */
export function isScaled(a: Athlete, m: Metric, buildingIds?: Set<string>): boolean {
  const bset = buildingIds ?? new Set([BUILDING_ID]);
  return (
    m.scaling === "cumulative" &&
    a.participation !== null &&
    !bset.has(a.id) &&
    a.minutes < 60
  );
}


export function formatValue(v: number | null, m: Metric): string {
  if (v == null) return "—";
  if (m.unit === "%") return `${v}%`;
  if (m.unit === "/10") return v.toFixed(m.decimals ?? 1);
  if (m.unit === "'") return `${v}'`;
  const num = m.decimals != null ? v.toFixed(m.decimals) : v.toLocaleString();
  return num;
}

