/**
 * ST2 — absolutes for the Attention card rows.
 *
 * The Tier-1 rows author a deviation (deltaFrac) because the flag is the
 * record item; the absolute value, reference and unit are NOT authored —
 * they are read from the athlete's record for the session so the track
 * hover can print a real "typical 902 m" instead of a normalised 1.
 *
 * Deviation geometry is ratio-based, so the drawn positions are unchanged:
 * value is the authored deviation applied to the real reference.
 */
import { spineForAthleteSession, type SpineMetricId } from "./athlete-data";
import { hrvResponseForSession } from "./recovery-data";

export type Tier1Absolutes = {
  value: number;
  reference: number;
  unit: string;
};

export function tier1Absolutes(
  athleteId: string,
  sessionId: string,
  metric: string,
  deltaFrac: number,
): Tier1Absolutes | null {
  if (metric === "hrv") {
    const hrv = hrvResponseForSession(athleteId, sessionId);
    if (hrv.state !== "ok") return null;
    const reference = hrv.baselineMs;
    if (!reference) return null;
    return { value: reference * (1 + deltaFrac), reference, unit: "ms" };
  }

  const spine = spineForAthleteSession(athleteId, sessionId);
  const row = spine.rows.find((r) => r.metricId === (metric as SpineMetricId));
  if (!row || row.reference == null || row.reference === 0) return null;
  return {
    value: row.reference * (1 + deltaFrac),
    reference: row.reference,
    unit: row.unit,
  };
}
