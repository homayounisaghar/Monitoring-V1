/**
 * demo-spatial · crude positional coordinates for the Spatial section
 *
 * Demo precision only. Not a simulation.
 *
 * For each athlete × session where the athlete actually played (minutes > 0
 * under the participation contract in `demo-library.ts`), we emit:
 *   - a small set of position-biased points on a normalised pitch
 *     (x = attacking axis 0..100 attacking left→right, y = width 0..100)
 *   - a legible ordered polyline through those points
 *   - the resulting share-of-time-in-third breakdown (D / M / A)
 *   - a positional-coverage percentage
 *
 * The `thirds` figures fall out of `points`, not the other way round — the
 * comparable absolute that sits next to the picture must be derivable from
 * the same stream the picture draws from.
 *
 * A small number of athlete-sessions have no positional data at all so the
 * unavailable state can render; one athlete (M. Meier) carries that state
 * across the whole window. Voss / Lange / Köhler / Sturm are deliberately
 * left alone — they carry other states already.
 *
 * PRNG is `mulberry32` seeded off `DEMO_SEED`, identical to `demo-library.ts`.
 * Copied inline (helpers there are private); no new PRNG.
 */

import {
  DEMO_SEED,
  demoAthletes,
  demoRecords,
  type DemoRecord,
} from "./demo-library";

// ────────────────────────────────────────────────────────────────────────────
// seeded jitter (mirrors demo-library.ts)

function mulberry32(seed: number) {
  let a = seed >>> 0;
  return function () {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
function hashSeed(...parts: (string | number)[]): number {
  let h = DEMO_SEED >>> 0;
  for (const p of parts) {
    const s = String(p);
    for (let i = 0; i < s.length; i++) {
      h = Math.imul(h ^ s.charCodeAt(i), 0x01000193) >>> 0;
    }
  }
  return h >>> 0;
}

// ────────────────────────────────────────────────────────────────────────────
// types

export type SpatialPoint = { x: number; y: number };

export type SpatialThirds = {
  defensivePct: number;
  middlePct: number;
  attackingPct: number;
};

export type SpatialField = {
  points: SpatialPoint[];
  path: SpatialPoint[];
  thirds: SpatialThirds;
  coveragePct: number;
};

// ────────────────────────────────────────────────────────────────────────────
// positional anchors (x attacking axis, y width)

const ANCHORS: Record<string, { x: number; y: number; spreadX: number; spreadY: number }> = {
  GK: { x: 8,  y: 50, spreadX: 4,  spreadY: 8  },
  CB: { x: 22, y: 50, spreadX: 8,  spreadY: 14 },
  LB: { x: 32, y: 18, spreadX: 12, spreadY: 10 },
  RB: { x: 32, y: 82, spreadX: 12, spreadY: 10 },
  DM: { x: 40, y: 50, spreadX: 10, spreadY: 18 },
  CM: { x: 50, y: 50, spreadX: 14, spreadY: 20 },
  AM: { x: 62, y: 50, spreadX: 12, spreadY: 20 },
  LM: { x: 55, y: 22, spreadX: 14, spreadY: 12 },
  RM: { x: 55, y: 78, spreadX: 14, spreadY: 12 },
  LW: { x: 72, y: 18, spreadX: 12, spreadY: 12 },
  RW: { x: 72, y: 82, spreadX: 12, spreadY: 12 },
  ST: { x: 78, y: 50, spreadX: 10, spreadY: 14 },
};
const FALLBACK = { x: 50, y: 50, spreadX: 20, spreadY: 20 };

// One athlete carries the "no positional data at all" state across the window.
// Not Voss / Lange / Köhler / Sturm (each carries another state already).
const NO_SPATIAL_ATHLETE = "meier";

// A tiny fraction of other athlete-sessions also drop out, so the unavailable
// state is not solely tied to one identity.
function isMissingScatter(athleteId: string, sessionId: string): boolean {
  return hashSeed(athleteId, sessionId, "spatial-miss") % 33 === 0;
}

function clamp(v: number, lo: number, hi: number) {
  return Math.max(lo, Math.min(hi, v));
}

function pointCountFor(minutes: number): number {
  // A substitute's field should read visibly sparser than a starter's.
  // ~1.5 points per minute, floored at 12 (so 8' subs still draw), capped at 160.
  return clamp(Math.round(minutes * 1.5), 12, 160);
}

// Build a couple of cluster centres around the anchor, so the field reads as
// two or three lobes rather than a Gaussian blob.
function clusterCentres(
  anchor: { x: number; y: number; spreadX: number; spreadY: number },
  rand: () => number,
): SpatialPoint[] {
  const n = 2 + Math.floor(rand() * 2); // 2 or 3
  const out: SpatialPoint[] = [];
  for (let i = 0; i < n; i++) {
    out.push({
      x: clamp(anchor.x + (rand() * 2 - 1) * anchor.spreadX * 0.6, 2, 98),
      y: clamp(anchor.y + (rand() * 2 - 1) * anchor.spreadY * 0.6, 2, 98),
    });
  }
  return out;
}

function buildField(
  athleteId: string,
  sessionId: string,
  posDetail: string,
  minutes: number,
): SpatialField {
  const anchor = ANCHORS[posDetail] ?? FALLBACK;
  const rand = mulberry32(hashSeed(athleteId, sessionId, "spatial"));
  const centres = clusterCentres(anchor, rand);
  const N = pointCountFor(minutes);

  const points: SpatialPoint[] = [];
  for (let i = 0; i < N; i++) {
    const c = centres[i % centres.length];
    const rx = (rand() * 2 - 1) * anchor.spreadX * 0.9;
    const ry = (rand() * 2 - 1) * anchor.spreadY * 0.9;
    points.push({
      x: clamp(c.x + rx, 1, 99),
      y: clamp(c.y + ry, 1, 99),
    });
  }

  // Legible polyline: take ~24 waypoints in generation order and smooth with
  // a 3-tap moving average. Not a simulation — enough to draw a trace.
  const stride = Math.max(1, Math.floor(points.length / 24));
  const raw: SpatialPoint[] = [];
  for (let i = 0; i < points.length; i += stride) raw.push(points[i]);
  const path: SpatialPoint[] = raw.map((p, i, arr) => {
    const a = arr[Math.max(0, i - 1)];
    const b = arr[Math.min(arr.length - 1, i + 1)];
    return {
      x: Number(((a.x + p.x + b.x) / 3).toFixed(2)),
      y: Number(((a.y + p.y + b.y) / 3).toFixed(2)),
    };
  });

  // Thirds fall out of `points`, not an independent draw.
  let d = 0, m = 0, a = 0;
  for (const p of points) {
    if (p.x < 100 / 3) d++;
    else if (p.x < 200 / 3) m++;
    else a++;
  }
  const total = points.length || 1;
  let dPct = Math.round((d / total) * 100);
  let mPct = Math.round((m / total) * 100);
  let aPct = 100 - dPct - mPct; // absorb rounding drift so shares sum to 100

  // Coverage: participating athlete-session, plausible band, jittered.
  const covRand = mulberry32(hashSeed(athleteId, sessionId, "spatial-cov"));
  const coveragePct = clamp(Math.round(84 + (covRand() * 2 - 1) * 10), 65, 99);

  return {
    points,
    path,
    thirds: { defensivePct: dPct, middlePct: mPct, attackingPct: aPct },
    coveragePct,
  };
}

// ────────────────────────────────────────────────────────────────────────────
// cache — built once per module load

const posDetailById: Record<string, string> = (() => {
  const m: Record<string, string> = {};
  for (const a of demoAthletes) m[a.id] = a.posDetail;
  return m;
})();

const cache: Map<string, SpatialField | null> = (() => {
  const out = new Map<string, SpatialField | null>();
  for (const r of demoRecords as readonly DemoRecord[]) {
    if (!r.sessionId) continue;                // rest-day record
    if (r.minutes <= 0) continue;              // contract: no participation
    const key = `${r.athleteId}::${r.sessionId}`;
    if (r.athleteId === NO_SPATIAL_ATHLETE || isMissingScatter(r.athleteId, r.sessionId)) {
      out.set(key, null);
      continue;
    }
    const pos = posDetailById[r.athleteId] ?? "CM";
    out.set(key, buildField(r.athleteId, r.sessionId, pos, r.minutes));
  }
  return out;
})();

// ────────────────────────────────────────────────────────────────────────────
// public API

export function spatialFor(athleteId: string, sessionId: string): SpatialField | null {
  const key = `${athleteId}::${sessionId}`;
  return cache.has(key) ? cache.get(key)! : null;
}

export function spatialPairForSession(
  athleteAId: string,
  athleteBId: string,
  sessionId: string,
): { a: SpatialField | null; b: SpatialField | null } {
  return {
    a: spatialFor(athleteAId, sessionId),
    b: spatialFor(athleteBId, sessionId),
  };
}

export const SPATIAL_MISSING_ATHLETE = NO_SPATIAL_ATHLETE;
