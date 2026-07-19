/**
 * ST2 — Demo library (Workstream 01 · prompt 1/4).
 *
 * Deterministic 8-week squad history for the Athlete and Longitudinal pages.
 * "Crude but structurally truthful": no physiology, but every honest-display
 * state (missing vs rest, thin coverage, unconfirmed, beyond-range, building
 * baseline) occurs in real generated data — not as component-level branches.
 *
 * Rules:
 *   - One seeded PRNG (mulberry32 + DEMO_SEED). No Math.random. No Date.now.
 *     No new Date() without an explicit ISO argument. Two runs must produce
 *     byte-identical output.
 *   - The Sat 18 Jul session (id "s-2026-07-04-dortmund") copies its
 *     per-athlete participation/minutes/hrCoveragePct/srpeSubmitted verbatim
 *     from `squad` in session-data.ts. Session and Athlete pages must never
 *     disagree about who played and for how long.
 *   - Nothing in this module is imported yet. Three later prompts extend it
 *     (per-day-type typicals; positional coordinates) — leave seams.
 */

import { squad, POSITION_LABEL, type Athlete as SessionAthlete, type PositionCode, type ParticipationTag } from "./session-data";

/* ─────────────────────────── constants ─────────────────────────── */

export const DEMO_TODAY = "2026-07-19";
export const DEMO_SEED = 0x51_2E_2E_07 >>> 0;

/* ─────────────────────────── PRNG ─────────────────────────── */

function mulberry32(seed: number) {
  let s = seed >>> 0;
  return function () {
    s = (s + 0x6D2B79F5) >>> 0;
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

/** Deterministic jitter in [-amp, +amp] keyed by parts. */
function jit(amp: number, ...parts: (string | number)[]): number {
  const r = mulberry32(hashSeed(...parts))();
  return (r * 2 - 1) * amp;
}

/* ─────────────────────────── types ─────────────────────────── */

export type SessionType = "training" | "match" | "recovery" | "gym";

export type DemoSession = {
  id: string;
  dateISO: string;
  name: string;
  type: SessionType;
  durationMin: number;
  dayCode: string;
  isRestDay: boolean;
  unconfirmed?: boolean;
  srpeCollected: boolean;
  opponent?: string;
  venue?: "home" | "away";
  result?: string;
};

export type DemoAthlete = {
  id: string;
  name: string;
  posDetail: string;
  position: PositionCode;
  positionLabel: string;
  joinedISO: string;
  maxVelKmh: number;
};

export type DemoRecord = {
  athleteId: string;
  sessionId: string;
  dateISO: string;
  inSquad: boolean;
  participation: ParticipationTag | null;
  minutes: number;
  totalDistance: number;   // m
  hsr: number;             // m
  sprintDist: number;      // m
  topSpeedKmh: number;     // km/h
  mMin: number;            // m/min
  accDec: number;          // ct
  cardioLoad: number | null;
  hrCoveragePct: number | null;
  srpeRating: number | null;   // 1-10
  srpeAU: number | null;       // rating × minutes
};

/* ─────────────────────────── roster ─────────────────────────── */

// Position-plausible fixed top speeds (GK 27–29, DEF 31–35, MID 31–34, ATT 33–36).
const MAX_VEL_BY_ID: Record<string, number> = {
  keller: 27.4, hofmann: 33.1, koehler: 32.0, hoffmann: 32.6, roth: 31.8,
  frei: 31.6, schaefer: 32.9, wagner: 32.4, albrecht: 33.2, meier: 31.9,
  brandt: 32.1, fischer: 35.4, werner: 35.9, brunner: 34.2, ebel: 34.6,
  kuhn: 32.8, voss: 33.5, lange: 31.2, sturm: 31.5,
};

// B. Köhler is the building-baseline signing (see §4.2).
const JOINED_OVERRIDES: Record<string, string> = { koehler: "2026-07-07" };

export const demoAthletes: readonly DemoAthlete[] = Object.freeze(
  squad.map((a: SessionAthlete): DemoAthlete => ({
    id: a.id,
    name: a.name,
    posDetail: a.posDetail,
    position: a.position,
    positionLabel: POSITION_LABEL[a.position],
    joinedISO: JOINED_OVERRIDES[a.id] ?? "2026-05-25",
    maxVelKmh: MAX_VEL_BY_ID[a.id] ?? 33.0,
  })),
);

/* ─────────────────────────── calendar ─────────────────────────── */

// Matches: dateISO, opponent, home/away, result (undefined for pre-21 Jun demo fills).
type MatchDef = { date: string; opp: string; venue: "home" | "away"; result?: string };
const MATCHES: MatchDef[] = [
  { date: "2026-05-31", opp: "Hertha BSC",         venue: "away", result: "1–1 D" },
  // Congested block, six in fourteen days:
  { date: "2026-06-03", opp: "Werder Bremen",      venue: "home", result: "2–0 W" },
  { date: "2026-06-06", opp: "VfB Stuttgart",      venue: "away", result: "0–1 L" },
  { date: "2026-06-09", opp: "Mainz 05",           venue: "home", result: "1–1 D" },
  { date: "2026-06-12", opp: "SC Freiburg",        venue: "away", result: "2–2 D" },
  { date: "2026-06-14", opp: "FC Augsburg",        venue: "home", result: "3–1 W" },
  { date: "2026-06-16", opp: "Union Berlin",       venue: "away", result: "0–0 D" },
  { date: "2026-06-21", opp: "Bayer 04",           venue: "home", result: "3–2 W" },
  { date: "2026-06-28", opp: "FC Köln",            venue: "home", result: "1–1 D" },
  { date: "2026-07-04", opp: "VfL Wolfsburg",      venue: "away", result: "0–2 L" },
  { date: "2026-07-08", opp: "Eintracht Frankfurt",venue: "home", result: "2–2 D" }, // beyond-range day
  { date: "2026-07-11", opp: "TSG Hoffenheim",     venue: "away", result: "1–0 W" },
  { date: "2026-07-18", opp: "Borussia Dortmund",  venue: "away", result: "2–1 W" }, // pinned
];

const MATCH_DATES = new Set(MATCHES.map((m) => m.date));
const MATCH_BY_DATE = new Map(MATCHES.map((m) => [m.date, m]));

// 28-day window rest days and the missing day (see §2, §4.9).
const REST_DAYS = new Set(["2026-06-22", "2026-06-29", "2026-07-05", "2026-07-06"]);
const MISSING_DAYS = new Set(["2026-07-14"]);
const DOUBLE_DAYS = new Set(["2026-07-13"]);

// Preserved existing identities (see §2).
type Preserved = { name: string; type: SessionType; durationMin: number };
const PRESERVED: Record<string, Preserved> = {
  "2026-06-25": { name: "MD+1 · Recovery",   type: "recovery", durationMin: 45 },
  "2026-06-24": { name: "MD-1 · Activation", type: "training", durationMin: 52 },
  "2026-07-01": { name: "MD-3 · Tactical",   type: "training", durationMin: 68 },
  "2026-07-02": { name: "MD-2 · Intensive",  type: "training", durationMin: 82 },
};

// The pinned Dortmund session — id preserved as opaque key even though the
// date changed from 2026-07-04 to 2026-07-18 (see §4.1 and the findings file).
const DORTMUND_SESSION_ID = "s-2026-07-04-dortmund";

/* ── date helpers (UTC-anchored so no host TZ leaks into determinism) ── */

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

/** dayCode: distance to nearest match; upcoming wins ties (see §2). */
function dayCodeFor(dateISO: string): string {
  if (MATCH_DATES.has(dateISO)) return "MD";
  let bestNext = Infinity, bestPrev = Infinity;
  for (const m of MATCHES) {
    const d = diffDays(m.date, dateISO); // +ve → match is upcoming
    if (d > 0 && d < bestNext) bestNext = d;
    if (d < 0 && -d < bestPrev) bestPrev = -d;
  }
  // Upcoming wins ties (rule §2).
  if (bestNext <= bestPrev) return `MD-${Math.min(bestNext, 9)}`;
  return `MD+${Math.min(bestPrev, 9)}`;
}

/* ─────────────────────────── session build ─────────────────────────── */

const START_ISO = "2026-05-25";
const END_ISO = "2026-07-19";

function nonMatchName(dateISO: string, dayCode: string): { name: string; type: SessionType; durationMin: number } {
  if (PRESERVED[dateISO]) return PRESERVED[dateISO];
  if (dayCode.startsWith("MD+")) {
    const n = parseInt(dayCode.slice(3), 10);
    if (n === 1) return { name: "MD+1 · Recovery", type: "recovery", durationMin: 45 };
    if (n === 2) return { name: "MD+2 · Regen",    type: "recovery", durationMin: 50 };
    return { name: `${dayCode} · Aerobic`,          type: "training", durationMin: 60 };
  }
  const n = parseInt(dayCode.slice(3), 10);
  if (n === 1) return { name: "MD-1 · Activation", type: "training", durationMin: 52 };
  if (n === 2) return { name: "MD-2 · Intensive",  type: "training", durationMin: 82 };
  if (n === 3) return { name: "MD-3 · Possession", type: "training", durationMin: 68 };
  if (n === 4) return { name: "MD-4 · Strength",   type: "training", durationMin: 60 };
  if (n === 5) return { name: "MD-5 · Aerobic",    type: "training", durationMin: 70 };
  return { name: `${dayCode} · Base`,               type: "training", durationMin: 65 };
}

function buildSessions(): DemoSession[] {
  const out: DemoSession[] = [];
  const days = diffDays(END_ISO, START_ISO) + 1;
  for (let i = 0; i < days; i++) {
    const dateISO = addDays(START_ISO, i);
    if (MISSING_DAYS.has(dateISO)) continue; // no record at all — load-bearing

    if (REST_DAYS.has(dateISO)) {
      out.push({
        id: `s-${dateISO}-rest`,
        dateISO,
        name: "Rest day",
        type: "recovery",
        durationMin: 0,
        dayCode: dayCodeFor(dateISO),
        isRestDay: true,
        srpeCollected: false,
      });
      continue;
    }

    if (MATCH_DATES.has(dateISO)) {
      const m = MATCH_BY_DATE.get(dateISO)!;
      const isDortmund = dateISO === "2026-07-18";
      out.push({
        id: isDortmund ? DORTMUND_SESSION_ID : `s-${dateISO}-match`,
        dateISO,
        name: `vs ${m.opp}`,
        type: "match",
        durationMin: isDortmund ? 95 : 94,
        dayCode: "MD",
        isRestDay: false,
        srpeCollected: true,
        opponent: m.opp,
        venue: m.venue,
        result: m.result,
      });
      continue;
    }

    const dayCode = dayCodeFor(dateISO);

    if (DOUBLE_DAYS.has(dateISO)) {
      // Double-session day (§2): gym AM + pitch PM.
      out.push({
        id: `s-${dateISO}-gym`,
        dateISO,
        name: "Gym · AM",
        type: "gym",
        durationMin: 45,
        dayCode,
        isRestDay: false,
        srpeCollected: true,
      });
      out.push({
        id: `s-${dateISO}-pitch`,
        dateISO,
        name: "Pitch · PM",
        type: "training",
        durationMin: 70,
        dayCode,
        isRestDay: false,
        srpeCollected: true,
      });
      continue;
    }

    const spec = nonMatchName(dateISO, dayCode);
    // Day-level "sRPE not collected" for two recovery days (§4.8).
    const srpeCollected = !(dateISO === "2026-07-12" || dateISO === "2026-07-19");
    const unconfirmed = dateISO === "2026-07-19" ? true : undefined;
    out.push({
      id: `s-${dateISO}-${spec.type}`,
      dateISO,
      name: spec.name,
      type: spec.type,
      durationMin: spec.durationMin,
      dayCode,
      isRestDay: false,
      srpeCollected,
      unconfirmed,
    });
  }
  return out;
}

export const demoSessions: readonly DemoSession[] = Object.freeze(
  buildSessions().sort((a, b) => (a.dateISO < b.dateISO ? -1 : a.dateISO > b.dateISO ? 1 : a.id.localeCompare(b.id))),
);

/* ─────────────────────────── position typicals ─────────────────────────── */

// Anchored to posTypical in squad-metrics.ts (full-match), scaled by day-type.
// A later prompt lifts these into a per-day-type table — do not fold them in
// there yet.
const POS_MATCH_TD:  Record<PositionCode, number> = { GK: 4900, DEF: 9800, MID: 11200, ATT: 10400 };
const POS_MATCH_HSR: Record<PositionCode, number> = { GK:  120, DEF:  620, MID:   780, ATT:   900 };
const POS_MATCH_SPR: Record<PositionCode, number> = { GK:   30, DEF:  180, MID:   220, ATT:   340 };
const POS_MATCH_AD:  Record<PositionCode, number> = { GK:   45, DEF:  115, MID:   130, ATT:   125 };
const POS_MATCH_CL:  Record<PositionCode, number> = { GK:  130, DEF:  220, MID:   250, ATT:   235 };
const POS_MATCH_MMIN:Record<PositionCode, number> = { GK:   55, DEF:  105, MID:   118, ATT:   110 };

/** Session-type × (roughly) fraction-of-a-full-match load. */
function typeScale(type: SessionType, name: string): { td: number; hsr: number; spr: number; ad: number; cl: number } {
  if (type === "match")    return { td: 1.00, hsr: 1.00, spr: 1.00, ad: 1.00, cl: 1.00 };
  if (type === "recovery") return { td: 0.28, hsr: 0.05, spr: 0.02, ad: 0.20, cl: 0.30 };
  if (type === "gym")      return { td: 0.05, hsr: 0.00, spr: 0.00, ad: 0.05, cl: 0.55 };
  // training — heavier for MD-2 Intensive, lighter for MD-4/-5 base days.
  if (name.startsWith("MD-2")) return { td: 0.85, hsr: 0.75, spr: 0.60, ad: 0.85, cl: 0.90 };
  if (name.startsWith("MD-1")) return { td: 0.55, hsr: 0.35, spr: 0.20, ad: 0.55, cl: 0.55 };
  if (name.startsWith("MD-3")) return { td: 0.70, hsr: 0.50, spr: 0.35, ad: 0.70, cl: 0.75 };
  if (name.startsWith("MD-4")) return { td: 0.55, hsr: 0.30, spr: 0.15, ad: 0.55, cl: 0.60 };
  if (name.startsWith("MD-5")) return { td: 0.65, hsr: 0.40, spr: 0.25, ad: 0.60, cl: 0.65 };
  return { td: 0.60, hsr: 0.40, spr: 0.30, ad: 0.60, cl: 0.65 };
}

/* ─────────────────────────── participation logic ─────────────────────────── */

// Pinned per-athlete rows for the Dortmund session (copied verbatim from
// `squad` in session-data.ts). Session and Athlete pages must not disagree.
const PINNED_DORTMUND: Record<string, { participation: ParticipationTag | null; minutes: number; hrCoveragePct: number | null; srpeSubmitted: boolean }> =
  Object.fromEntries(squad.map((a) => [a.id, {
    participation: a.participation,
    minutes: a.minutes,
    hrCoveragePct: a.hrCoveragePct,
    srpeSubmitted: a.srpeSubmitted,
  }]));

/** Lange's arc across the 28-day window (§4.4, reversed from brief to land on the pinned Injury row). */
function langeParticipationOn(dateISO: string): ParticipationTag {
  if (dateISO <= "2026-06-28") return "Full";
  if (dateISO <= "2026-07-05") return "Part";
  if (dateISO <= "2026-07-12") return "Rehab";
  return "Injury";
}

/** Full-window Injury for F. Voss (§4.3). */
function voss(): ParticipationTag { return "Injury"; }

function inSquadOn(athleteId: string, dateISO: string): boolean {
  const a = demoAthletes.find((x) => x.id === athleteId)!;
  return dateISO >= a.joinedISO;
}

/** Base participation before pinning overrides. */
function participationFor(athleteId: string, session: DemoSession): ParticipationTag | null {
  if (!inSquadOn(athleteId, session.dateISO)) return null;
  if (session.isRestDay) return null; // rest days: record is a zero, no tag
  if (athleteId === "sturm") return null; // in squad, never plays
  if (athleteId === "voss") return voss();
  if (athleteId === "lange") return langeParticipationOn(session.dateISO);
  return "Full";
}

/** Pinned session overrides everything else for the 19 rows on 18 Jul. */
function resolveParticipation(athleteId: string, session: DemoSession): { participation: ParticipationTag | null; minutes: number; hrCoveragePct: number | null; srpeSubmitted: boolean } {
  if (session.id === DORTMUND_SESSION_ID) {
    const p = PINNED_DORTMUND[athleteId];
    if (p) return p;
  }
  const part = participationFor(athleteId, session);
  if (part === null) {
    return { participation: null, minutes: 0, hrCoveragePct: null, srpeSubmitted: false };
  }
  // Minutes: matches ≈ full; partials/injury are short; training uses duration.
  let minutes = session.durationMin;
  if (session.type === "match") {
    minutes = part === "Full" ? 90 + Math.round(jit(3, athleteId, session.id, "min")) : Math.max(8, Math.round(20 + jit(10, athleteId, session.id, "pmin")));
    if (part === "Injury") minutes = Math.max(6, Math.round(12 + jit(4, athleteId, session.id, "imin")));
    if (part === "Rehab") minutes = 0;
  } else if (part === "Rehab" || part === "Injury") {
    minutes = 0;
  }
  // HR coverage — normally 82–98 %; drop specific athletes on 30 Jun (§4.5).
  let hr: number | null = Math.round(90 + jit(8, athleteId, session.id, "hr"));
  if (session.dateISO === "2026-06-30" && (athleteId === "brandt" || athleteId === "kuhn")) {
    hr = Math.round(65 + jit(10, athleteId, "lowhr")); // 55–75 % band
  }
  // Scatter a few other low-coverage athlete-sessions.
  if (hashSeed(athleteId, session.id, "hrpick") % 40 === 0) hr = Math.round(60 + jit(12, athleteId, session.id, "hrscat"));
  if (minutes === 0) hr = null;
  const srpeSubmitted = athleteId !== "frei"; // Frei never submits (§4.8)
  return { participation: part, minutes, hrCoveragePct: hr, srpeSubmitted };
}

/* ─────────────────────────── record generation ─────────────────────────── */

// The beyond-range day (§4.7): boost squad TD ~15 % above the highest other match.
const BEYOND_RANGE_TD_MULT = 1.16;

function generateRecord(a: DemoAthlete, s: DemoSession): DemoRecord {
  const base = { athleteId: a.id, sessionId: s.id, dateISO: s.dateISO } as const;

  if (s.isRestDay) {
    // Rest days: true zero record (§4.9). Only in-squad athletes get one.
    if (!inSquadOn(a.id, s.dateISO)) {
      return { ...base, inSquad: false, participation: null, minutes: 0,
        totalDistance: 0, hsr: 0, sprintDist: 0, topSpeedKmh: 0, mMin: 0, accDec: 0,
        cardioLoad: null, hrCoveragePct: null, srpeRating: null, srpeAU: null };
    }
    return { ...base, inSquad: true, participation: null, minutes: 0,
      totalDistance: 0, hsr: 0, sprintDist: 0, topSpeedKmh: 0, mMin: 0, accDec: 0,
      cardioLoad: 0, hrCoveragePct: null, srpeRating: null, srpeAU: null };
  }

  const resolved = resolveParticipation(a.id, s);
  const inSquad = inSquadOn(a.id, s.dateISO);
  if (!inSquad) {
    return { ...base, inSquad: false, participation: null, minutes: 0,
      totalDistance: 0, hsr: 0, sprintDist: 0, topSpeedKmh: 0, mMin: 0, accDec: 0,
      cardioLoad: null, hrCoveragePct: null, srpeRating: null, srpeAU: null };
  }
  if (resolved.participation === null || resolved.minutes <= 0) {
    return { ...base, inSquad: true, participation: resolved.participation, minutes: 0,
      totalDistance: 0, hsr: 0, sprintDist: 0, topSpeedKmh: 0, mMin: 0, accDec: 0,
      cardioLoad: null, hrCoveragePct: resolved.hrCoveragePct, srpeRating: null, srpeAU: null };
  }

  const pos = a.position;
  const scale = typeScale(s.type, s.name);
  const minFrac = resolved.minutes / 90;

  const jitAmp = 0.14;
  const j = (k: string) => 1 + jit(jitAmp, a.id, s.id, k);

  let td   = Math.round(POS_MATCH_TD[pos]  * scale.td  * minFrac * j("td"));
  let hsr  = Math.round(POS_MATCH_HSR[pos] * scale.hsr * minFrac * j("hsr"));
  let spr  = Math.round(POS_MATCH_SPR[pos] * scale.spr * minFrac * j("spr"));
  const ad = Math.round(POS_MATCH_AD[pos]  * scale.ad  * minFrac * j("ad"));
  let cl: number | null = Math.round(POS_MATCH_CL[pos] * scale.cl * minFrac * j("cl"));

  // Beyond-range boost on 8 Jul (§4.7).
  if (s.dateISO === "2026-07-08") {
    td = Math.round(td * BEYOND_RANGE_TD_MULT);
    hsr = Math.round(hsr * BEYOND_RANGE_TD_MULT);
    spr = Math.round(spr * BEYOND_RANGE_TD_MULT);
  }

  const mMin = resolved.minutes > 0 ? Math.round(td / resolved.minutes) : 0;

  // Top speed: near per-athlete max on matches with sprint work; lower elsewhere.
  const speedCap = a.maxVelKmh;
  let topSpeed = speedCap - Math.abs(jit(2.5, a.id, s.id, "tsp"));
  if (s.type !== "match") topSpeed = speedCap - 2.5 - Math.abs(jit(3.5, a.id, s.id, "tsp2"));
  if (s.type === "gym" || s.type === "recovery") topSpeed = 12 + Math.abs(jit(4, a.id, s.id, "tsp3"));
  topSpeed = Math.max(6, Math.min(speedCap, Number(topSpeed.toFixed(1))));

  // HR coverage: null → cardioLoad null (honest absence).
  if (resolved.hrCoveragePct == null) cl = null;

  // sRPE: rating × minutes (AU). Day-level not-collected → all null.
  let srpeRating: number | null = null;
  let srpeAU: number | null = null;
  if (s.srpeCollected && resolved.srpeSubmitted && resolved.minutes > 0) {
    // Rating anchored on session load (matches ~7.5, MD-2 ~7, recovery ~3, gym ~5).
    const base = s.type === "match" ? 7.4
      : s.type === "recovery" ? 3.0
      : s.type === "gym"      ? 5.0
      : s.name.startsWith("MD-2") ? 7.0
      : s.name.startsWith("MD-1") ? 4.5
      : 5.5;
    srpeRating = Math.max(1, Math.min(10, Number((base + jit(0.9, a.id, s.id, "srpe")).toFixed(1))));
    srpeAU = Math.round(srpeRating * resolved.minutes);
  }

  // Partial-submission on some days (§4.8) — drop ~40 % of athletes on a couple
  // of dates so the "n of m" print exercises. Frei is always null; this just
  // adds honest additional partial-collection days.
  if ((s.dateISO === "2026-07-09" || s.dateISO === "2026-07-15") && hashSeed(a.id, "psub") % 5 < 2) {
    srpeRating = null;
    srpeAU = null;
  }

  return {
    ...base,
    inSquad: true,
    participation: resolved.participation,
    minutes: resolved.minutes,
    totalDistance: Math.max(0, td),
    hsr: Math.max(0, hsr),
    sprintDist: Math.max(0, spr),
    topSpeedKmh: topSpeed,
    mMin,
    accDec: Math.max(0, ad),
    cardioLoad: cl,
    hrCoveragePct: resolved.hrCoveragePct,
    srpeRating,
    srpeAU,
  };
}

function buildRecords(): DemoRecord[] {
  const out: DemoRecord[] = [];
  for (const s of demoSessions) {
    for (const a of demoAthletes) {
      out.push(generateRecord(a, s));
    }
  }
  return out;
}

export const demoRecords: readonly DemoRecord[] = Object.freeze(buildRecords());

/* ─────────────────────────── lookups ─────────────────────────── */

const RECORDS_BY_SESSION = new Map<string, DemoRecord[]>();
const RECORDS_BY_ATHLETE = new Map<string, DemoRecord[]>();
for (const r of demoRecords) {
  (RECORDS_BY_SESSION.get(r.sessionId) ?? RECORDS_BY_SESSION.set(r.sessionId, []).get(r.sessionId)!).push(r);
  (RECORDS_BY_ATHLETE.get(r.athleteId) ?? RECORDS_BY_ATHLETE.set(r.athleteId, []).get(r.athleteId)!).push(r);
}
for (const [k, v] of RECORDS_BY_SESSION) RECORDS_BY_SESSION.set(k, Object.freeze(v) as DemoRecord[]);
for (const [k, v] of RECORDS_BY_ATHLETE) RECORDS_BY_ATHLETE.set(k, Object.freeze(v) as DemoRecord[]);

export function recordsForSession(sessionId: string): readonly DemoRecord[] {
  return RECORDS_BY_SESSION.get(sessionId) ?? [];
}
export function recordsForAthlete(athleteId: string): readonly DemoRecord[] {
  return RECORDS_BY_ATHLETE.get(athleteId) ?? [];
}
export function sessionsInRange(fromISO: string, toISO: string): readonly DemoSession[] {
  return demoSessions.filter((s) => s.dateISO >= fromISO && s.dateISO <= toISO);
}
