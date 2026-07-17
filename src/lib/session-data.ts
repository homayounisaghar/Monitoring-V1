/**
 * ST2 — Single source of session sample data.
 * Every section imports from here. The provider derives from `participants`,
 * never `squad`, so the "of 18" invariant holds by construction.
 */

import { tmpl } from "./copy-deck";

export type PositionCode = "GK" | "DEF" | "MID" | "ATT";
export type PositionLabel = "GK" | "Defenders" | "Midfielders" | "Attackers";
export type ParticipationTag =
  | "Full"
  | "Part"
  | "Modified"
  | "Rehab"
  | "Injury"
  | "Other";

export const POSITION_LABEL: Record<PositionCode, PositionLabel> = {
  GK: "GK",
  DEF: "Defenders",
  MID: "Midfielders",
  ATT: "Attackers",
};

export type Athlete = {
  id: string;
  name: string;
  posDetail: string; // e.g. "ST", "RW", "CB"
  position: PositionCode;
  participation: ParticipationTag | null; // null = did not participate
  minutes: number; // played
  hrCoveragePct: number | null; // null = did not participate
  srpeSubmitted: boolean;
  historySessions?: number; // for young-baseline athletes
  notes?: string;
};

export type Session = {
  id: string;
  kind: "match" | "training";
  label: string; // e.g. "vs Borussia Dortmund"
  dayCode: string; // "MD", "MD-1", "MD+1", …
  dateISO: string;
  durationMin: number;
  halves: [number, number]; // half durations, minutes
  venue?: string;
  weather?: { tempC: number; humidityPct: number };
  result?: string; // "2–1 W"
};

/* ---------- The session ---------- */

export const currentSession: Session = {
  id: "s-2026-07-04-dortmund",
  kind: "match",
  label: "vs Borussia Dortmund",
  dayCode: "MD",
  dateISO: "2026-07-04",
  durationMin: 95,
  halves: [47, 48],
  venue: "Signal Iduna Park",
  weather: { tempC: 14, humidityPct: 72 },
  result: "2–1 W",
};


/* ---------- Squad (19) — Sturm is squad but did not participate ---------- */

export const squad: Athlete[] = [
  { id: "fischer",  name: "A. Fischer",  posDetail: "ST", position: "ATT", participation: "Full",     minutes: 90, hrCoveragePct: 96, srpeSubmitted: true },
  { id: "werner",   name: "K. Werner",   posDetail: "RW", position: "ATT", participation: "Full",     minutes: 88, hrCoveragePct: 94, srpeSubmitted: true },
  { id: "schaefer", name: "D. Schäfer",  posDetail: "CM", position: "MID", participation: "Full",     minutes: 95, hrCoveragePct: 91, srpeSubmitted: true },
  { id: "hofmann",  name: "M. Hofmann",  posDetail: "RB", position: "DEF", participation: "Full",     minutes: 95, hrCoveragePct: 92, srpeSubmitted: true },
  { id: "koehler",  name: "B. Köhler",   posDetail: "CB", position: "DEF", participation: "Full",     minutes: 95, hrCoveragePct: 89, srpeSubmitted: false, historySessions: 3, notes: "new signing" },
  { id: "ebel",     name: "N. Ebel",     posDetail: "RW", position: "ATT", participation: "Part",     minutes: 26, hrCoveragePct: 88, srpeSubmitted: true },
  { id: "keller",   name: "J. Keller",   posDetail: "GK", position: "GK",  participation: "Full",     minutes: 95, hrCoveragePct: 84, srpeSubmitted: true },
  { id: "roth",     name: "M. Roth",     posDetail: "CB", position: "DEF", participation: "Full",     minutes: 95, hrCoveragePct: 90, srpeSubmitted: true },
  { id: "hoffmann", name: "D. Hoffmann", posDetail: "LB", position: "DEF", participation: "Full",     minutes: 95, hrCoveragePct: 93, srpeSubmitted: true },
  { id: "frei",     name: "M. Frei",     posDetail: "DM", position: "MID", participation: "Full",     minutes: 95, hrCoveragePct: 87, srpeSubmitted: false },
  { id: "wagner",   name: "L. Wagner",   posDetail: "CM", position: "MID", participation: "Full",     minutes: 69, hrCoveragePct: 91, srpeSubmitted: true },
  { id: "albrecht", name: "J. Albrecht", posDetail: "AM", position: "MID", participation: "Full",     minutes: 74, hrCoveragePct: 86, srpeSubmitted: true },
  { id: "brunner",  name: "E. Brunner",  posDetail: "LW", position: "ATT", participation: "Full",     minutes: 90, hrCoveragePct: 92, srpeSubmitted: false },
  { id: "brandt",   name: "T. Brandt",   posDetail: "CM", position: "MID", participation: "Part",     minutes: 21, hrCoveragePct: 74, srpeSubmitted: true },
  { id: "kuhn",     name: "S. Kuhn",     posDetail: "LB", position: "DEF", participation: "Part",     minutes: 26, hrCoveragePct: 61, srpeSubmitted: false },
  { id: "voss",     name: "F. Voss",     posDetail: "ST", position: "ATT", participation: "Injury",   minutes: 12, hrCoveragePct: 43, srpeSubmitted: false },
  { id: "lange",    name: "P. Lange",    posDetail: "CB", position: "DEF", participation: "Injury",   minutes: 29, hrCoveragePct: 82, srpeSubmitted: false },
  { id: "meier",    name: "H. Meier",    posDetail: "RM", position: "MID", participation: "Full",     minutes: 78, hrCoveragePct: 85, srpeSubmitted: true },
  // In squad, did NOT participate — must not appear in any "of 18" read.
  { id: "sturm",    name: "P. Sturm",    posDetail: "CB", position: "DEF", participation: null,       minutes: 0,  hrCoveragePct: null, srpeSubmitted: false },
];

export const participants: Athlete[] = squad.filter((a) => a.participation !== null);
// Invariant: participants.length === 18.

/* ---------- Source sidebar sessions ---------- */

export const sessionLibrary: Array<Session & { selected?: boolean }> = [
  { ...currentSession, selected: true },
  { id: "s-2026-07-02", kind: "training", label: "MD-2 · Intensive", dayCode: "MD-2", dateISO: "2026-07-02", durationMin: 82, halves: [41, 41] },
  { id: "s-2026-07-01", kind: "training", label: "MD-3 · Tactical",  dayCode: "MD-3", dateISO: "2026-07-01", durationMin: 68, halves: [34, 34] },
  { id: "s-2026-06-28", kind: "match",    label: "vs FC Köln",       dayCode: "MD",   dateISO: "2026-06-28", durationMin: 94, halves: [46, 48], result: "1–1 D" },
  { id: "s-2026-06-25", kind: "training", label: "MD+1 · Recovery",  dayCode: "MD+1", dateISO: "2026-06-25", durationMin: 45, halves: [45, 0] },
  { id: "s-2026-06-24", kind: "training", label: "MD-1 · Activation",dayCode: "MD-1", dateISO: "2026-06-24", durationMin: 52, halves: [26, 26] },
  { id: "s-2026-06-21", kind: "match",    label: "vs Bayer 04",      dayCode: "MD",   dateISO: "2026-06-21", durationMin: 96, halves: [47, 49], result: "3–2 W" },

];


/* ---------- Timeline helper — derived, never hardcoded (rule 9) ---------- */

export type PeriodOption = { id: string; label: string; startMin: number; endMin: number };

/**
 * Derives period options from a session's declared duration and half lengths.
 * Windows sum to the declared duration by construction.
 */
export function timeline(
  session: Session,
  granularity: "halves" | "15min"
): PeriodOption[] {
  const [h1, h2] = session.halves;
  const total = session.durationMin;

  if (granularity === "halves") {
    const first: PeriodOption = { id: "h1", label: `1st 0–${h1}'`, startMin: 0, endMin: h1 };
    if (h2 <= 0) return [first];
    const second: PeriodOption = { id: "h2", label: `2nd ${h1}–${total}'`, startMin: h1, endMin: total };
    return [first, second];
  }

  // 15' blocks — 0–15, 15–30, … up to the last full 90; stoppage remainder as "90–total +"
  const blocks: PeriodOption[] = [];
  const regulation = Math.min(90, total);
  const lastFullEnd = Math.floor(regulation / 15) * 15;
  for (let start = 0; start < lastFullEnd; start += 15) {
    const end = start + 15;
    blocks.push({ id: `b${start}`, label: `${start}–${end}'`, startMin: start, endMin: end });
  }
  // remainder up to 90 (if regulation isn't a multiple of 15)
  if (lastFullEnd < regulation) {
    blocks.push({
      id: `b${lastFullEnd}`,
      label: `${lastFullEnd}–${regulation}'`,
      startMin: lastFullEnd,
      endMin: regulation,
    });
  }
  // stoppage
  if (total > 90) {
    blocks.push({
      id: "stoppage",
      label: `90–${total}' +`,
      startMin: 90,
      endMin: total,
    });
  }
  return blocks;
}

/* ---------- Periods — per-block staged data (Session > Periods) ----------
 * Values are placeholders that exercise the section's honest states:
 * thin coverage (30–45'), unconfirmed (60–75' accel+decel), an over-scale
 * clamp (75–90' HSR), a below-floor absence (90–95'+), and the peak block
 * (75–90'). Rates are computed in the component from these raw loads.
 */
export type PeriodBlock = {
  id: string;
  label: string;
  startMin: number;
  endMin: number;
  minutes: number;
  totalDistance: number; // m
  hsr: number;           // m
  accelDecel: number;    // ct
  cardioLoad: number;    // CL (team aggregate)
  hrCoverage: number;    // athletes with HR data, of 18
  unconfirmed?: { accelDecel?: boolean };
};

export const PERIODS_DISPLAY_FLOOR = 8;   // athletes — below this, internal is absent
export const PERIODS_DOMAIN_MIN = 30;      // rate points — drawn scale floor
export const PERIODS_DOMAIN_MAX = 150;     // rate points — drawn scale ceiling
export const PERIODS_SQUAD_SIZE = 18;      // "of 18" invariant

export const periodsBlocks: PeriodBlock[] = [
  { id: "b0",       label: tmpl("periods.blockLabelTemplate", { start:  0, end: 15 }), startMin:  0, endMin: 15, minutes: 15, totalDistance: 1613, hsr: 101, accelDecel: 19, cardioLoad: 35, hrCoverage: 18 },
  { id: "b15",      label: tmpl("periods.blockLabelTemplate", { start: 15, end: 30 }), startMin: 15, endMin: 30, minutes: 15, totalDistance: 1675, hsr: 149, accelDecel: 20, cardioLoad: 31, hrCoverage: 18 },
  { id: "b30",      label: tmpl("periods.blockLabelTemplate", { start: 30, end: 45 }), startMin: 30, endMin: 45, minutes: 15, totalDistance: 1504, hsr: 112, accelDecel: 18, cardioLoad: 30, hrCoverage: 13 },
  { id: "b45",      label: tmpl("periods.blockLabelTemplate", { start: 45, end: 60 }), startMin: 45, endMin: 60, minutes: 15, totalDistance: 1411, hsr:  94, accelDecel: 16, cardioLoad: 33, hrCoverage: 18 },
  { id: "b60",      label: tmpl("periods.blockLabelTemplate", { start: 60, end: 75 }), startMin: 60, endMin: 75, minutes: 15, totalDistance: 1489, hsr: 128, accelDecel: 19, cardioLoad: 31, hrCoverage: 18, unconfirmed: { accelDecel: true } },
  { id: "b75",      label: tmpl("periods.blockLabelTemplate", { start: 75, end: 90 }), startMin: 75, endMin: 90, minutes: 15, totalDistance: 1768, hsr: 214, accelDecel: 23, cardioLoad: 47, hrCoverage: 18 },
  { id: "stoppage", label: tmpl("periods.blockLabelTerminalTemplate", { start: 90 }), startMin: 90, endMin: 95, minutes:  5, totalDistance:  360, hsr:  14, accelDecel:  3, cardioLoad:  9, hrCoverage:  3 },
];

