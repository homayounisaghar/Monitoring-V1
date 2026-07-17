/**
 * ST2 — URL ⇄ session-scope state.
 *
 * Encodes the shareable analysis state (reference, benchmark, filter,
 * squad sort/view/display/chartMetric) into a compact query string.
 * The link carries only state, never snapshotted values — hydration
 * feeds the state variables and downstream re-derivation does the rest.
 *
 * Clean-default rule: when every field is at its default, only
 * `sessionId` is emitted (no empty params).
 */
import {
  BENCHMARK_OPTIONS,
  REFERENCE_OPTIONS,
  type BenchmarkKind,
  type BenchmarkOption,
  type Filter,
  type ReferenceKind,
  type ReferenceOption,
} from "./session-scope";
import type { ParticipationTag, PositionCode } from "./session-data";
import type { MetricId } from "./squad-metrics";
import { METRICS } from "./squad-metrics";

export type SquadView = "table" | "chart";
export type SquadDisplay = "absolute" | "percent";
export type SortDir = "asc" | "desc";
export type SquadSort = { key: MetricId | "name"; dir: SortDir };

export type ShareState = {
  reference: ReferenceKind;
  benchmark: BenchmarkKind;
  filter: Filter;
  squadView: SquadView;
  squadDisplay: SquadDisplay;
  squadSort: SquadSort;
  squadChartMetric: MetricId;
};

export type ShareDefaults = {
  reference: ReferenceKind;
  benchmark: BenchmarkKind;
  squadView: SquadView;
  squadDisplay: SquadDisplay;
  squadSort: SquadSort;
  squadChartMetric: MetricId;
};

const PARTICIPATION_VALUES: ParticipationTag[] = ["Full", "Part", "Injury", "Sick", "DNP"];
const POSITION_VALUES: PositionCode[] = ["GK", "DEF", "MID", "ATT"];

function isMetricId(x: string | null | undefined): x is MetricId {
  return !!x && Object.prototype.hasOwnProperty.call(METRICS, x);
}

/* ---------- parse ---------- */

export function parseShareUrl(
  raw: URLSearchParams | string | undefined,
): Partial<ShareState> {
  const sp =
    typeof raw === "string"
      ? new URLSearchParams(raw)
      : raw instanceof URLSearchParams
        ? raw
        : new URLSearchParams();

  const out: Partial<ShareState> = {};

  const ref = sp.get("ref");
  const refOpt = REFERENCE_OPTIONS.find((o) => o.kind === ref);
  if (refOpt) out.reference = refOpt.kind;

  const bench = sp.get("bench");
  const benchOpt = BENCHMARK_OPTIONS.find((o) => o.kind === bench);
  if (benchOpt) out.benchmark = benchOpt.kind;

  const parts = splitSet(sp.get("part")).filter((v): v is ParticipationTag =>
    (PARTICIPATION_VALUES as string[]).includes(v),
  );
  const pos = splitSet(sp.get("pos")).filter((v): v is PositionCode =>
    (POSITION_VALUES as string[]).includes(v),
  );
  const athletes = splitSet(sp.get("ath"));
  const gran = sp.get("gran") === "halves" ? "halves" : "15min";
  const perSel = splitSet(sp.get("per"));

  if (parts.length || pos.length || athletes.length || perSel.length || sp.get("gran")) {
    out.filter = {
      participation: new Set(parts),
      positions: new Set(pos),
      period: { granularity: gran, selected: new Set(perSel) },
      athletes: new Set(athletes),
    };
  }

  const view = sp.get("view");
  if (view === "table" || view === "chart") out.squadView = view;

  const disp = sp.get("disp");
  if (disp === "absolute" || disp === "percent") out.squadDisplay = disp;

  const sort = sp.get("sort");
  if (sort) {
    const [key, dir] = sort.split(":");
    if ((isMetricId(key) || key === "name") && (dir === "asc" || dir === "desc")) {
      out.squadSort = { key: key as MetricId | "name", dir };
    }
  }

  const cm = sp.get("cm");
  if (isMetricId(cm)) out.squadChartMetric = cm;

  return out;
}

/* ---------- build ---------- */

export function buildShareUrl(
  origin: string,
  sessionId: string,
  state: ShareState,
  defaults: ShareDefaults,
  filterIsDefault: boolean,
): string {
  const sp = new URLSearchParams();
  sp.set("sessionId", sessionId);

  if (state.reference !== defaults.reference) sp.set("ref", state.reference);
  if (state.benchmark !== defaults.benchmark) sp.set("bench", state.benchmark);

  if (!filterIsDefault) {
    const f = state.filter;
    if (f.participation.size) sp.set("part", [...f.participation].join(","));
    if (f.positions.size) sp.set("pos", [...f.positions].join(","));
    if (f.athletes.size) sp.set("ath", [...f.athletes].join(","));
    if (f.period.selected.size) {
      sp.set("per", [...f.period.selected].join(","));
      sp.set("gran", f.period.granularity);
    }
  }

  if (state.squadView !== defaults.squadView) sp.set("view", state.squadView);
  if (state.squadDisplay !== defaults.squadDisplay) sp.set("disp", state.squadDisplay);
  if (
    state.squadSort.key !== defaults.squadSort.key ||
    state.squadSort.dir !== defaults.squadSort.dir
  ) {
    sp.set("sort", `${state.squadSort.key}:${state.squadSort.dir}`);
  }
  if (state.squadView === "chart" && state.squadChartMetric !== defaults.squadChartMetric) {
    sp.set("cm", state.squadChartMetric);
  }

  return `${origin}/session?${sp.toString()}`;
}

export function isShareStateDefault(
  state: Omit<ShareState, "filter">,
  defaults: ShareDefaults,
  filterIsDefault: boolean,
): boolean {
  return (
    filterIsDefault &&
    state.reference === defaults.reference &&
    state.benchmark === defaults.benchmark &&
    state.squadView === defaults.squadView &&
    state.squadDisplay === defaults.squadDisplay &&
    state.squadSort.key === defaults.squadSort.key &&
    state.squadSort.dir === defaults.squadSort.dir &&
    (state.squadView !== "chart" || state.squadChartMetric === defaults.squadChartMetric)
  );
}

function splitSet(v: string | null): string[] {
  if (!v) return [];
  return v.split(",").filter(Boolean);
}
