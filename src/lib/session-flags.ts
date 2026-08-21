/**
 * ST2 — Session flag model (Tier-1 flags, coverage minimum, building
 * baseline). Single source consumed by AttentionCard now and, later,
 * by the Squad section for its neutral flag glyphs.
 *
 * Tier-1 rows are sorted escalate-first; author order does not matter.
 */
import type { SeverityTier } from "@/components/data/SeverityGlyph";

export const COVERAGE_MIN = 80;
export const BUILDING_ID = "koehler";
export const BUILDING_SESSIONS_TO_MIN = 3;
// Comparable-athlete floor for the baseline-thin headline state — placeholder
// pending real data (same pattern as PERIODS_DISPLAY_FLOOR).
export const BASELINE_COMPARABLE_MIN = 10;


export type Tier1Read =
  | {
      kind: "vot";
      axis: "work" | "cost" | "neutral";
      deltaFrac: number; // 0.34 → +34% vs own typical
      bandFrac: number;
      /** Which metric the row reads, so the absolute value / reference /
       *  unit can be resolved from the record instead of normalised 1.0. */
      metric: "totalDistance" | "hsr" | "cardioLoad" | "srpeAU" | "accDec" | "mMin" | "hrv";
    }
  | {
      kind: "gap";
      externalPct: number; // signed % vs typical
      internalPct: number;
      gapPts: number;
    };


export type Tier1Row = {
  id: string;
  tier: SeverityTier;
  reason: string;
  read: Tier1Read;
};

/** Default (day-of-match) tier-1 flags. */
export const TIER1_ROWS_DEFAULT: Tier1Row[] = [
  {
    id: "fischer",
    tier: "escalate",
    reason: "Sprint distance · HSR",
    read: { kind: "vot", axis: "work", deltaFrac: 0.34, bandFrac: 0.1, metric: "hsr" },
  },
  {
    id: "werner",
    tier: "notice",
    reason: "High-speed running",
    read: { kind: "vot", axis: "work", deltaFrac: 0.22, bandFrac: 0.1, metric: "hsr" },
  },
  {
    id: "schaefer",
    tier: "notice",
    reason: "External · cardio",
    read: { kind: "gap", externalPct: 19, internalPct: -3, gapPts: 22 },
  },
  {
    id: "hofmann",
    tier: "notice",
    reason: "Total distance",
    read: { kind: "vot", axis: "work", deltaFrac: 0.14, bandFrac: 0.14, metric: "totalDistance" },
  },
  {
    // Chronic HRV suppression through his injury stretch (recovery-data.ts).
    // Slate axis — HRV belongs to neither work nor cost. Same row anatomy,
    // same severity language; the deviation is stated against his own
    // 7-day baseline.
    id: "lange",
    tier: "notice",
    reason: "HRV · own baseline",
    read: { kind: "vot", axis: "neutral", deltaFrac: -0.27, bandFrac: 0.1, metric: "hrv" },
  },
];

const TIER_ORDER: Record<SeverityTier, number> = { escalate: 0, notice: 1 };
export function sortTier1(rows: Tier1Row[]): Tier1Row[] {
  return [...rows].sort((a, b) => TIER_ORDER[a.tier] - TIER_ORDER[b.tier]);
}

/** The identity set the Squad section will use to place neutral flags. */
export function flaggedIds(
  tier1: Tier1Row[],
  lowCovIds: string[],
): Set<string> {
  return new Set<string>([...tier1.map((r) => r.id), ...lowCovIds, BUILDING_ID]);
}
