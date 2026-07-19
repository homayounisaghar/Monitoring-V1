/**
 * ST2 — Demo library (Workstream 01 · prompt 1/4, corrections 1b).
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
 *   - Nothing in this module is imported yet.
 *
 * Two time series over one truth (prompt 1b · §2):
 *   - `demoSessions` — real sessions only, no rest entries.
 *   - `demoDays`     — one entry per calendar date except the missing day
 *                      (kind: "session" | "rest"). The day-arranged reads
 *                      (rolling averages, chronic window) consume this;
 *                      session-arranged reads consume `demoSessions`.
 *   - Rest-day records keep `sessionId: null`.
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
  unconfirmed?: boolean;
  srpeCollected: boolean;
  opponent?: string;
  venue?: "home" | "away";
  result?: string;
  /** Free-text session annotation (e.g. "AET" for extra time). */
  note?: string;
};

export type DemoDay = {
  dateISO: string;
  dayCode: string;
  kind: "session" | "rest";
  sessionIds: string[];
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
  /** null on rest days (§2 · records are keyed to the date, not a session). */
  sessionId: string | null;
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

// B. Köhler is the building-baseline signing.
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

const ATHLETE_BY_ID = new Map(demoAthletes.map((a) => [a.id, a]));

/* ─────────────────────────── calendar ─────────────────────────── */

type MatchDef = { date: string; opp: string; venue: "home" | "away"; result?: string; note?: string; durationMin?: number };
const MATCHES: MatchDef[] = [
  { date: "2026-05-31", opp: "Hertha BSC",         venue: "away", result: "1–1 D" },
  { date: "2026-06-03", opp: "Werder Bremen",      venue: "home", result: "2–0 W" },
  { date: "2026-06-06", opp: "VfB Stuttgart",      venue: "away", result: "0–1 L" },
  { date: "2026-06-09", opp: "Mainz 05",           venue: "home", result: "1–1 D" },
  { date: "2026-06-12", opp: "SC Freiburg",        venue: "away", result: "2–2 D" },
  { date: "2026-06-14", opp: "FC Augsburg",        venue: "home", result: "3–1 W" },
  { date: "2026-06-16", opp: "Union Berlin",       venue: "away", result: "0–0 D" },
  { date: "2026-06-21", opp: "Bayer 04",           venue: "home", result: "3–2 W" },
  { date: "2026-06-28", opp: "FC Köln",            venue: "home", result: "1–1 D" },
  { date: "2026-07-04", opp: "VfL Wolfsburg",      venue: "away", result: "0–2 L" },
  // Cup tie taken to extra time — the reason 8 Jul sits above the domain cap.
  { date: "2026-07-08", opp: "Eintracht Frankfurt",venue: "home", result: "2–2 D", note: "AET", durationMin: 120 },
  { date: "2026-07-11", opp: "TSG Hoffenheim",     venue: "away", result: "1–0 W" },
  { date: "2026-07-18", opp: "Borussia Dortmund",  venue: "away", result: "2–1 W" }, // pinned
];

const MATCH_DATES = new Set(MATCHES.map((m) => m.date));
const MATCH_BY_DATE = new Map(MATCHES.map((m) => [m.date, m]));
const MATCH_INDEX = new Map(MATCHES.map((m, i) => [m.date, i]));

const REST_DAYS = new Set(["2026-06-22", "2026-06-29", "2026-07-05", "2026-07-06"]);
const MISSING_DAYS = new Set(["2026-07-14"]);
const DOUBLE_DAYS = new Set(["2026-07-13"]);

// The pinned Dortmund session — id preserved as opaque key.
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

/** dayCode: distance to nearest match; upcoming wins ties. */
function dayCodeFor(dateISO: string): string {
  if (MATCH_DATES.has(dateISO)) return "MD";
  let bestNext = Infinity, bestPrev = Infinity;
  for (const m of MATCHES) {
    const d = diffDays(m.date, dateISO);
    if (d > 0 && d < bestNext) bestNext = d;
    if (d < 0 && -d < bestPrev) bestPrev = -d;
  }
  if (bestNext <= bestPrev) return `MD-${Math.min(bestNext, 9)}`;
  return `MD+${Math.min(bestPrev, 9)}`;
}

/* ─────────────────────────── session build ─────────────────────────── */

const START_ISO = "2026-05-25";
const END_ISO = "2026-07-19";

/**
 * Non-match session identity derived purely from computed day code
 * (§1 · PRESERVED table deleted — names never contradict badges).
 */
function nonMatchName(dayCode: string): { name: string; type: SessionType; durationMin: number } {
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

export function buildSessions(): DemoSession[] {
  const out: DemoSession[] = [];
  const days = diffDays(END_ISO, START_ISO) + 1;
  for (let i = 0; i < days; i++) {
    const dateISO = addDays(START_ISO, i);
    if (MISSING_DAYS.has(dateISO)) continue;
    if (REST_DAYS.has(dateISO)) continue; // §2 — rest days are days, not sessions

    if (MATCH_DATES.has(dateISO)) {
      const m = MATCH_BY_DATE.get(dateISO)!;
      const isDortmund = dateISO === "2026-07-18";
      out.push({
        id: isDortmund ? DORTMUND_SESSION_ID : `s-${dateISO}-match`,
        dateISO,
        name: `vs ${m.opp}`,
        type: "match",
        durationMin: isDortmund ? 95 : (m.durationMin ?? 94),
        dayCode: "MD",
        srpeCollected: true,
        opponent: m.opp,
        venue: m.venue,
        result: m.result,
        note: m.note,
      });
      continue;
    }

    const dayCode = dayCodeFor(dateISO);

    if (DOUBLE_DAYS.has(dateISO)) {
      out.push({
        id: `s-${dateISO}-gym`,
        dateISO, name: "Gym · AM", type: "gym", durationMin: 45,
        dayCode, srpeCollected: true,
      });
      out.push({
        id: `s-${dateISO}-pitch`,
        dateISO, name: "Pitch · PM", type: "training", durationMin: 70,
        dayCode, srpeCollected: true,
      });
      continue;
    }

    const spec = nonMatchName(dayCode);
    const srpeCollected = !(dateISO === "2026-07-12" || dateISO === "2026-07-19");
    const unconfirmed = dateISO === "2026-07-19" ? true : undefined;
    out.push({
      id: `s-${dateISO}-${spec.type}`,
      dateISO,
      name: spec.name,
      type: spec.type,
      durationMin: spec.durationMin,
      dayCode,
      srpeCollected,
      unconfirmed,
    });
  }
  return out.sort((a, b) => (a.dateISO < b.dateISO ? -1 : a.dateISO > b.dateISO ? 1 : a.id.localeCompare(b.id)));
}

export const demoSessions: readonly DemoSession[] = Object.freeze(buildSessions());

/* ─────────────────────────── day build ─────────────────────────── */

export function buildDays(): DemoDay[] {
  const sessionsByDate = new Map<string, string[]>();
  for (const s of demoSessions) {
    const arr = sessionsByDate.get(s.dateISO) ?? [];
    arr.push(s.id);
    sessionsByDate.set(s.dateISO, arr);
  }
  const out: DemoDay[] = [];
  const days = diffDays(END_ISO, START_ISO) + 1;
  for (let i = 0; i < days; i++) {
    const dateISO = addDays(START_ISO, i);
    if (MISSING_DAYS.has(dateISO)) continue;
    const isRest = REST_DAYS.has(dateISO);
    out.push({
      dateISO,
      dayCode: dayCodeFor(dateISO),
      kind: isRest ? "rest" : "session",
      sessionIds: sessionsByDate.get(dateISO) ?? [],
    });
  }
  return out;
}

export const demoDays: readonly DemoDay[] = Object.freeze(buildDays());

/* ─────────────────────────── position typicals ─────────────────────────── */

const POS_MATCH_TD:  Record<PositionCode, number> = { GK: 4900, DEF: 9800, MID: 11200, ATT: 10400 };
const POS_MATCH_HSR: Record<PositionCode, number> = { GK:  120, DEF:  620, MID:   780, ATT:   900 };
const POS_MATCH_SPR: Record<PositionCode, number> = { GK:   30, DEF:  180, MID:   220, ATT:   340 };
const POS_MATCH_AD:  Record<PositionCode, number> = { GK:   45, DEF:  115, MID:   130, ATT:   125 };
const POS_MATCH_CL:  Record<PositionCode, number> = { GK:  130, DEF:  220, MID:   250, ATT:   235 };

function typeScale(type: SessionType, name: string): { td: number; hsr: number; spr: number; ad: number; cl: number } {
  if (type === "match")    return { td: 1.00, hsr: 1.00, spr: 1.00, ad: 1.00, cl: 1.00 };
  if (type === "recovery") return { td: 0.28, hsr: 0.05, spr: 0.02, ad: 0.20, cl: 0.30 };
  if (type === "gym")      return { td: 0.05, hsr: 0.00, spr: 0.00, ad: 0.05, cl: 0.55 };
  if (name.startsWith("MD-2")) return { td: 0.85, hsr: 0.75, spr: 0.60, ad: 0.85, cl: 0.90 };
  if (name.startsWith("MD-1")) return { td: 0.55, hsr: 0.35, spr: 0.20, ad: 0.55, cl: 0.55 };
  if (name.startsWith("MD-3")) return { td: 0.70, hsr: 0.50, spr: 0.35, ad: 0.70, cl: 0.75 };
  if (name.startsWith("MD-4")) return { td: 0.55, hsr: 0.30, spr: 0.15, ad: 0.55, cl: 0.60 };
  if (name.startsWith("MD-5")) return { td: 0.65, hsr: 0.40, spr: 0.25, ad: 0.60, cl: 0.65 };
  return { td: 0.60, hsr: 0.40, spr: 0.30, ad: 0.60, cl: 0.65 };
}

/* ─────────────────────────── participation ─────────────────────────── */

/**
 * Participation contract (§1, prompt 1d) — the single source of truth.
 *
 * Consulted by both minutes assignment (below) and record generation
 * (`generateRecord`). No branch anywhere in this module may decide these
 * facts independently; `demo-library.check.ts` walks every record and
 * asserts it satisfies its own tag's row.
 *
 * "None" = the field is `null` where the type allows null, `0` where it does
 * not. A zero must never stand in for "no such record"; the only legitimate
 * zero is a rest-day record (a real observation of zero accumulation).
 *
 * | tag        | minutes  | external+internal load | HR coverage | sRPE
 * |------------|----------|------------------------|-------------|------
 * | unselected | 0        | none                   | none        | none
 * | Injury     | 0        | none                   | none        | none
 * | Rehab      | 0        | none (not in session)  | none        | none
 * | Other      | 0        | none (off-team prog.)  | none        | none
 * | Modified   | reduced  | reduced                | present     | if collected+submits
 * | Part       | reduced  | reduced                | present     | if collected+submits
 * | Full       | normal   | normal                 | present     | if collected+submits
 *
 * Two-meanings note: `Injury` currently carries two facts —
 * "unavailable for this session" (history, always minutes=0) and
 * "injured during this session" (pinned 18 Jul Voss/Lange, minutes>0).
 * The pinned session is a declared exception; the invariant permits
 * `Injury` with minutes>0 only there, and the check names the exempted
 * rows. Held for the post-meeting register — see findings.
 */
type ContractRow = {
  hasMinutes: boolean;   // minutes > 0
  hasLoad: boolean;      // td/hsr/spr/ad/mMin/topSpeed non-zero, cardioLoad non-null
  hasCoverage: boolean;  // hrCoveragePct non-null
  srpeEligible: boolean; // may carry srpeRating/srpeAU if session collected + athlete submits
};
const CONTRACT: Record<"unselected" | ParticipationTag, ContractRow> = {
  unselected: { hasMinutes: false, hasLoad: false, hasCoverage: false, srpeEligible: false },
  Injury:     { hasMinutes: false, hasLoad: false, hasCoverage: false, srpeEligible: false },
  Rehab:      { hasMinutes: false, hasLoad: false, hasCoverage: false, srpeEligible: false },
  Other:      { hasMinutes: false, hasLoad: false, hasCoverage: false, srpeEligible: false },
  Modified:   { hasMinutes: true,  hasLoad: true,  hasCoverage: true,  srpeEligible: true  },
  Part:       { hasMinutes: true,  hasLoad: true,  hasCoverage: true,  srpeEligible: true  },
  Full:       { hasMinutes: true,  hasLoad: true,  hasCoverage: true,  srpeEligible: true  },
};

export function contractRowFor(tag: ParticipationTag | null): ContractRow {
  return tag === null ? CONTRACT.unselected : CONTRACT[tag];
}

const PINNED_DORTMUND: Record<string, { participation: ParticipationTag | null; minutes: number; hrCoveragePct: number | null; srpeSubmitted: boolean }> =
  Object.fromEntries(squad.map((a) => [a.id, {
    participation: a.participation,
    minutes: a.minutes,
    hrCoveragePct: a.hrCoveragePct,
    srpeSubmitted: a.srpeSubmitted,
  }]));

function langeParticipationOn(dateISO: string): ParticipationTag {
  if (dateISO <= "2026-06-28") return "Full";
  if (dateISO <= "2026-07-05") return "Part";
  if (dateISO <= "2026-07-12") return "Rehab";
  return "Injury";
}

function inSquadOn(athleteId: string, dateISO: string): boolean {
  const a = ATHLETE_BY_ID.get(athleteId)!;
  return dateISO >= a.joinedISO;
}

/** Compute the participation map for a match session (§4). */
function computeMatchParticipation(session: DemoSession): Map<string, ParticipationTag | null> {
  const result = new Map<string, ParticipationTag | null>();
  const eligible: string[] = [];
  const forcedPart: string[] = [];
  for (const a of demoAthletes) {
    if (!inSquadOn(a.id, session.dateISO)) { result.set(a.id, null); continue; }
    if (a.id === "sturm") { result.set(a.id, null); continue; }
    if (a.id === "voss")  { result.set(a.id, "Injury"); continue; }
    if (a.id === "lange") {
      const p = langeParticipationOn(session.dateISO);
      if (p === "Full") eligible.push(a.id);
      else if (p === "Part") forcedPart.push(a.id);
      else result.set(a.id, p);
      continue;
    }
    eligible.push(a.id);
  }
  const rand = mulberry32(hashSeed(session.id, "squad"));
  const matchIdx = MATCH_INDEX.get(session.dateISO) ?? 0;
  // Rotation-based pick: sort pool stably, then choose a contiguous slice
  // starting at (matchIdx * step) % poolSize. This guarantees rotation across
  // matches while remaining deterministic (§4 — no athlete starts every match).
  const rotate = (pool: string[], n: number, step: number, posKey: string): string[] => {
    if (pool.length === 0 || n <= 0) return [];
    const sorted = [...pool].sort();
    // Position-specific phase offset breaks alignment between positions so
    // one athlete cannot be "always index 0" across the whole window.
    const offset = hashSeed("rotation-phase", posKey) % sorted.length;
    const start = ((matchIdx * step + offset) % sorted.length + sorted.length) % sorted.length;
    const take = Math.min(n, sorted.length);
    const picks: string[] = [];
    for (let i = 0; i < take; i++) picks.push(sorted[(start + i) % sorted.length]);
    return picks;
  };
  const byPos: Record<PositionCode, string[]> = { GK: [], DEF: [], MID: [], ATT: [] };
  for (const id of eligible) byPos[ATHLETE_BY_ID.get(id)!.position].push(id);

  // Formation variation breaks the starter-lock that pure 4-4-2 would produce
  // given a tight roster (only ~5 defenders means all 4 always start).
  const formations: Array<[number, number, number]> = [
    [4, 4, 2], [3, 5, 2], [4, 3, 3], [3, 4, 3],
  ];
  const [nDef, nMid, nAtt] = formations[matchIdx % formations.length];
  const starters = new Set<string>();
  for (const id of rotate(byPos.GK,  1,    1, "GK"))  starters.add(id);
  for (const id of rotate(byPos.DEF, nDef, 1, "DEF")) starters.add(id);
  for (const id of rotate(byPos.MID, nMid, 1, "MID")) starters.add(id);
  for (const id of rotate(byPos.ATT, nAtt, 1, "ATT")) starters.add(id);
  // Fill any shortfall from remaining eligibles.
  const shortfallPool = rotate(eligible.filter((id) => !starters.has(id)), 11 - starters.size, 3, "FILL");
  for (const id of shortfallPool) { if (starters.size >= 11) break; starters.add(id); }

  // Extra-time cup tie: 4–5 subs instead of 3–5 (fresh legs after 90'+).
  const targetPart = session.dateISO === "2026-07-08"
    ? 4 + Math.floor(rand() * 2)
    : 3 + Math.floor(rand() * 3);
  const subsNeeded = Math.max(0, targetPart - forcedPart.length);
  const subs = new Set(
    rotate(eligible.filter((id) => !starters.has(id)), subsNeeded, 2, "SUB"),
  );

  for (const id of forcedPart) result.set(id, "Part");
  for (const id of eligible) {
    if (starters.has(id)) result.set(id, "Full");
    else if (subs.has(id)) result.set(id, "Part");
    else result.set(id, null);
  }
  return result;
}

/** Non-match scatter: aim for 8–12 % non-Full among eligible athletes. */
function trainingScatterTag(athleteId: string, session: DemoSession): ParticipationTag {
  const roll = hashSeed(session.id, athleteId, "nonfull") % 100;
  if (roll < 4) return "Modified"; // 4 %
  if (roll < 8) return "Part";     // 4 %
  if (roll < 10) return "Other";   // 2 %
  return "Full";
}

const MATCH_PARTICIPATION = new Map<string, Map<string, ParticipationTag | null>>();
for (const s of demoSessions) {
  if (s.type === "match" && s.id !== DORTMUND_SESSION_ID) {
    MATCH_PARTICIPATION.set(s.id, computeMatchParticipation(s));
  }
}

/**
 * Rotation-enforcement pass (§4). Given the tight roster and small number of
 * in-window matches, pure rotation cannot guarantee that every outfielder sits
 * out at least once. This pass detects any outfield athlete who would start
 * every match and swaps them into a Part slot in one match, promoting a
 * same-position sub to Full in their place.
 */
(function enforceStarterRotation() {
  const windowMatchIds = demoSessions
    .filter((s) => s.type === "match" && s.id !== DORTMUND_SESSION_ID && s.dateISO >= "2026-06-22" && s.dateISO <= "2026-07-19")
    .map((s) => s.id);
  const total = windowMatchIds.length;
  const counts = new Map<string, number>();
  const recount = () => {
    counts.clear();
    for (const mid of windowMatchIds) {
      for (const [id, tag] of MATCH_PARTICIPATION.get(mid)!) {
        if (tag === "Full") counts.set(id, (counts.get(id) ?? 0) + 1);
      }
    }
    return [...counts.entries()]
      .filter(([id, c]) => id !== "keller" && c === total)
      .map(([id]) => id);
  };
  let monopolists = recount();
  let guard = 0;
  while (monopolists.length > 0 && guard++ < 20) {
    const id = monopolists[0];
    const pos = ATHLETE_BY_ID.get(id)!.position;
    let swapped = false;
    for (const mid of windowMatchIds) {
      const p = MATCH_PARTICIPATION.get(mid)!;
      if (p.get(id) !== "Full") continue;
      // Prefer a same-position Part sub whose promotion won't create a new monopolist.
      let replacement: string | null = null;
      for (const [otherId, tag] of p) {
        if (otherId === id) continue;
        if (ATHLETE_BY_ID.get(otherId)?.position !== pos) continue;
        if (otherId === "lange" || otherId === "voss" || otherId === "sturm") continue;
        if (tag === "Part" && (counts.get(otherId) ?? 0) < total - 1) { replacement = otherId; break; }
      }
      if (!replacement) {
        for (const [otherId, tag] of p) {
          if (otherId === id) continue;
          if (ATHLETE_BY_ID.get(otherId)?.position !== pos) continue;
          if (tag === null && otherId !== "sturm" && otherId !== "voss" && otherId !== "lange"
              && inSquadOn(otherId, demoSessions.find((s) => s.id === mid)!.dateISO)
              && (counts.get(otherId) ?? 0) < total - 1) {
            replacement = otherId; break;
          }
        }
      }
      if (replacement) {
        p.set(id, "Part");
        p.set(replacement, "Full");
        swapped = true;
        break;
      }
    }
    if (!swapped) break;
    monopolists = recount();
  }
})();



function resolveParticipation(athleteId: string, session: DemoSession): { participation: ParticipationTag | null; minutes: number; hrCoveragePct: number | null; srpeSubmitted: boolean } {
  // Pinned session overrides everything.
  if (session.id === DORTMUND_SESSION_ID) {
    const p = PINNED_DORTMUND[athleteId];
    if (p) return p;
  }
  if (!inSquadOn(athleteId, session.dateISO)) {
    return { participation: null, minutes: 0, hrCoveragePct: null, srpeSubmitted: false };
  }

  let part: ParticipationTag | null;
  if (session.type === "match") {
    part = MATCH_PARTICIPATION.get(session.id)?.get(athleteId) ?? null;
  } else {
    // Non-match: forced overrides first, then scatter.
    if (athleteId === "sturm") part = null;
    else if (athleteId === "voss") part = "Injury";
    else if (athleteId === "lange") part = langeParticipationOn(session.dateISO);
    else part = trainingScatterTag(athleteId, session);
  }

  if (part === null) {
    return { participation: null, minutes: 0, hrCoveragePct: null, srpeSubmitted: false };
  }

  // Minutes — driven by the contract (§1, prompt 1d). No-minutes rows never
  // gain a minute here; only Full/Part/Modified accumulate.
  const row = contractRowFor(part);
  let minutes: number;
  if (!row.hasMinutes) {
    minutes = 0;
  } else if (session.type === "match") {
    const isExtraTime = session.dateISO === "2026-07-08";
    if (part === "Full") {
      minutes = isExtraTime
        ? 114 + Math.round(jit(3, athleteId, session.id, "min")) // 111–117
        : 90 + Math.round(jit(4, athleteId, session.id, "min"));  // 86–94
    } else { // Part (Modified never occurs on match sessions in this library)
      minutes = isExtraTime
        ? Math.max(20, Math.min(45, Math.round(33 + jit(12, athleteId, session.id, "pmin"))))
        : Math.max(8, Math.min(35, Math.round(22 + jit(12, athleteId, session.id, "pmin"))));
    }
  } else {
    if (part === "Modified")      minutes = Math.round(session.durationMin * 0.6);
    else if (part === "Part")     minutes = Math.round(session.durationMin * 0.5);
    else                          minutes = session.durationMin; // Full
  }

  // Coverage — present iff the contract says so. Low-coverage demo pair is
  // pinned to Thu 2 Jul (MD-2 · Intensive), the heaviest training session
  // in the window, where thin HR genuinely undermines the internal-load read.
  let hr: number | null = row.hasCoverage ? Math.round(90 + jit(8, athleteId, session.id, "hr")) : null;
  if (session.dateISO === "2026-07-02" && (athleteId === "brandt" || athleteId === "kuhn") && row.hasCoverage) {
    hr = Math.round(65 + jit(10, athleteId, "lowhr"));
  }
  if (row.hasCoverage && hashSeed(athleteId, session.id, "hrpick") % 40 === 0) {
    hr = Math.round(60 + jit(12, athleteId, session.id, "hrscat"));
  }
  const srpeSubmitted = row.srpeEligible && athleteId !== "frei" && minutes > 0;
  return { participation: part, minutes, hrCoveragePct: hr, srpeSubmitted };
}

/* ─────────────────────────── record generation ─────────────────────────── */

/**
 * Fixed drawn domain for the squad-day distance lane.
 * The upper bound is a demo-calibrated placeholder pending real per-day
 * exports and must never auto-fit to the current data — the whole point
 * of "beyond range" is that the domain doesn't move when an outlier appears.
 * Chosen to sit above every day in the eight-week history except one (8 Jul,
 * the extra-time cup tie) so exactly one day breaks the cap.
 */
export const DAY_TD_DOMAIN_MIN = 0;
export const DAY_TD_DOMAIN_MAX = 143_000;


function generateRecord(a: DemoAthlete, s: DemoSession): DemoRecord {
  const base = { athleteId: a.id, sessionId: s.id, dateISO: s.dateISO } as const;

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

  if (s.dateISO === "2026-07-08") {
    // Extra-time cup tie: intensity per minute sags slightly beyond 90'.
    // The distance/HSR uplift comes from the 120' duration (minFrac ≈ 1.30),
    // not from a multiplier — this dampener knocks the per-minute rate back.
    const damp = 0.93;
    td  = Math.round(td  * damp);
    hsr = Math.round(hsr * damp);
    spr = Math.round(spr * damp);
  }

  const mMin = resolved.minutes > 0 ? Math.round(td / resolved.minutes) : 0;

  const speedCap = a.maxVelKmh;
  let topSpeed = speedCap - Math.abs(jit(2.5, a.id, s.id, "tsp"));
  if (s.type !== "match") topSpeed = speedCap - 2.5 - Math.abs(jit(3.5, a.id, s.id, "tsp2"));
  if (s.type === "gym" || s.type === "recovery") topSpeed = 12 + Math.abs(jit(4, a.id, s.id, "tsp3"));
  topSpeed = Math.max(6, Math.min(speedCap, Number(topSpeed.toFixed(1))));

  if (resolved.hrCoveragePct == null) cl = null;

  let srpeRating: number | null = null;
  let srpeAU: number | null = null;
  if (s.srpeCollected && resolved.srpeSubmitted && resolved.minutes > 0) {
    const anchor = s.type === "match" ? 7.4
      : s.type === "recovery" ? 3.0
      : s.type === "gym"      ? 5.0
      : s.name.startsWith("MD-2") ? 7.0
      : s.name.startsWith("MD-1") ? 4.5
      : 5.5;
    srpeRating = Math.max(1, Math.min(10, Number((anchor + jit(0.9, a.id, s.id, "srpe")).toFixed(1))));
    srpeAU = Math.round(srpeRating * resolved.minutes);
  }

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

export function buildRecords(): DemoRecord[] {
  const out: DemoRecord[] = [];
  for (const s of demoSessions) {
    for (const a of demoAthletes) out.push(generateRecord(a, s));
  }
  // Rest-day records — one zero-accumulation row per in-squad athlete per rest date (§2).
  const restDates = Array.from(REST_DAYS).sort();
  for (const dateISO of restDates) {
    for (const a of demoAthletes) {
      const inS = inSquadOn(a.id, dateISO);
      out.push({
        athleteId: a.id,
        sessionId: null,
        dateISO,
        inSquad: inS,
        participation: null,
        minutes: 0,
        totalDistance: 0, hsr: 0, sprintDist: 0, topSpeedKmh: 0, mMin: 0, accDec: 0,
        cardioLoad: inS ? 0 : null,
        hrCoveragePct: null,
        srpeRating: null,
        srpeAU: null,
      });
    }
  }
  return out;
}

export const demoRecords: readonly DemoRecord[] = Object.freeze(buildRecords());

/* ─────────────────────────── lookups ─────────────────────────── */

const RECORDS_BY_SESSION = new Map<string, DemoRecord[]>();
const RECORDS_BY_ATHLETE = new Map<string, DemoRecord[]>();
for (const r of demoRecords) {
  if (r.sessionId != null) {
    const arr = RECORDS_BY_SESSION.get(r.sessionId) ?? [];
    arr.push(r); RECORDS_BY_SESSION.set(r.sessionId, arr);
  }
  const arr = RECORDS_BY_ATHLETE.get(r.athleteId) ?? [];
  arr.push(r); RECORDS_BY_ATHLETE.set(r.athleteId, arr);
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
export function daysInRange(fromISO: string, toISO: string): readonly DemoDay[] {
  return demoDays.filter((d) => d.dateISO >= fromISO && d.dateISO <= toISO);
}
