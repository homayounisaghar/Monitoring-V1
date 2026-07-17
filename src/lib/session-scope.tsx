/**
 * ST2 — Session-tab shared state.
 * Benchmark + Reference + Filter + Demo scenario live here so later
 * section prompts inherit working propagation, not a paint.
 *
 * Effective data: the provider derives ONE dataset per demo scenario
 * (participants overrides + tier-1 flag set) and every component
 * reads only that — no per-component demo branches.
 */
import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import {
  participants as rawParticipants,
  currentSession,
  POSITION_LABEL,
  timeline,
  type Athlete,
  type PositionCode,
  type ParticipationTag,
  type PeriodOption,
} from "./session-data";
import {
  COVERAGE_MIN,
  TIER1_ROWS_DEFAULT,
  sortTier1,
  type Tier1Row,
} from "./session-flags";

export type ReferenceKind =
  | "own_typical"
  | "positional"
  | "cohort"
  | "last_n"
  | "season"
  | "same_opponent";
export type BenchmarkKind =
  | "typical_daytype"
  | "typical_match"
  | "last_match"
  | "last_5"
  | "same_opponent";

export type BenchmarkOption = { kind: BenchmarkKind; label: string };

export type ReferenceOption = { kind: ReferenceKind; label: string };

export const REFERENCE_OPTIONS: ReferenceOption[] = [
  { kind: "own_typical",   label: "their typical match" },
  { kind: "last_n",        label: "last 5 matches" },
  { kind: "season",        label: "season average" },
  { kind: "positional",    label: "positional norm" },
  { kind: "cohort",        label: "squad average" },
  { kind: "same_opponent", label: "same opponent" },
];

// Match menu — the day-type typical of a match IS "typical match".
export const BENCHMARK_OPTIONS: BenchmarkOption[] = [
  { kind: "typical_match", label: "typical match" },
  { kind: "last_match",    label: "last match" },
  { kind: "last_5",        label: "last 5 matches" },
  { kind: "same_opponent", label: "same opponent" },
];

// Demo day code for the training-day scenario. Placeholder like the rest.
export const TRAINING_DAY_CODE = "MD-2";

export type Filter = {
  participation: Set<ParticipationTag>;
  positions: Set<PositionCode>;
  period: { granularity: "halves" | "15min"; selected: Set<string> };
  athletes: Set<string>;
};

export type DemoScenario =
  | "default"
  | "all_clear"
  | "srpe_none"
  | "srpe_full"
  | "coverage_thin"
  | "training_day"
  | "early_season"
  | "no_hr_data";

export type SessionScope = {
  reference: ReferenceOption;
  setReference: (r: ReferenceOption) => void;
  referenceOptions: ReferenceOption[];
  defaultReference: ReferenceOption;
  benchmark: BenchmarkOption;
  setBenchmark: (b: BenchmarkOption) => void;
  benchmarkOptions: BenchmarkOption[];
  defaultBenchmark: BenchmarkOption;
  benchmarkIsDefault: boolean;
  dayCode: string | null;

  filter: Filter;
  setFilter: (f: Filter) => void;

  demo: DemoScenario;
  setDemo: (d: DemoScenario) => void;

  // Effective (scenario-adjusted) participants — every read uses this.
  effectiveParticipants: Athlete[];
  tier1Rows: Tier1Row[];
  sessionIsTraining: boolean;
  buildingIds: Set<string>;
  comparableCount: number;

  // derived
  activeAthletes: Athlete[];
  showingCount: number;
  totalParticipants: number;
  scopeLabel: string | null;
  filterIsDefault: boolean;
};


const emptyFilter: Filter = {
  participation: new Set(),
  positions: new Set(),
  period: { granularity: "15min", selected: new Set() },
  athletes: new Set(),
};

const Ctx = createContext<SessionScope | null>(null);

/* --- Effective-data overlays --- */

const COVERAGE_LIFT_ALL_CLEAR: Record<string, number> = {
  brandt: 92,
  kuhn: 88,
  voss: 86,
};

// coverage_thin: keep these 5 above the floor.
const COVERAGE_THIN_KEEP = new Set(["keller", "schaefer", "hofmann", "roth", "hoffmann"]);
// Deterministic below-floor values for the other 13.
const COVERAGE_THIN_LOW: Record<string, number> = {
  fischer: 74,
  werner: 71,
  koehler: 68,
  ebel: 66,
  frei: 63,
  wagner: 72,
  albrecht: 70,
  brunner: 67,
  brandt: 58,
  kuhn: 54,
  voss: 43,
  lange: 61,
  meier: 76,
};

export const CLOSER_KEY_BY_SCENARIO: Partial<Record<DemoScenario, string>> = {
  training_day: "attention.closer.trainingDay",
};

export const BUILDING_IDS_BY_SCENARIO: Partial<Record<DemoScenario, string[]>> = {
  early_season: [
    "werner", "schaefer", "koehler", "ebel", "frei", "wagner", "albrecht",
    "brunner", "brandt", "kuhn", "voss", "lange", "hofmann",
  ],
};

// Deterministic 1..4 history counts for early-season building athletes.
const EARLY_SEASON_HISTORY: Record<string, number> = {
  werner: 4, schaefer: 2, koehler: 3, ebel: 1, frei: 2, wagner: 3,
  albrecht: 4, brunner: 2, brandt: 1, kuhn: 3, voss: 2, lange: 1, hofmann: 4,
};

function applyOverlay(
  demo: DemoScenario,
  participants: Athlete[],
): { participants: Athlete[]; tier1: Tier1Row[] } {
  const sorted = sortTier1(TIER1_ROWS_DEFAULT);
  switch (demo) {
    case "default":
      return { participants, tier1: sorted };
    case "all_clear":
      return {
        participants: participants.map((a) =>
          a.id in COVERAGE_LIFT_ALL_CLEAR
            ? { ...a, hrCoveragePct: COVERAGE_LIFT_ALL_CLEAR[a.id] }
            : a,
        ),
        tier1: [],
      };
    case "srpe_none":
      return {
        participants: participants.map((a) => ({ ...a, srpeSubmitted: false })),
        tier1: sorted,
      };
    case "srpe_full":
      return {
        participants: participants.map((a) => ({ ...a, srpeSubmitted: true })),
        tier1: sorted,
      };
    case "coverage_thin":
      return {
        participants: participants.map((a) => {
          if (a.hrCoveragePct === null) return a;
          if (COVERAGE_THIN_KEEP.has(a.id)) return a;
          const lowered = COVERAGE_THIN_LOW[a.id];
          return lowered !== undefined ? { ...a, hrCoveragePct: lowered } : a;
        }),
        // Divergence flags suppressed into "to check" per the gating rule.
        tier1: [],
      };
    case "training_day":
      return { participants, tier1: sorted };
    case "early_season":
      return {
        participants: participants.map((a) =>
          a.id in EARLY_SEASON_HISTORY
            ? { ...a, historySessions: EARLY_SEASON_HISTORY[a.id] }
            : a,
        ),
        tier1: sorted.filter((r) => r.id === "fischer"),
      };
    case "no_hr_data":
      return {
        participants: participants.map((a) =>
          a.hrCoveragePct === null ? a : { ...a, hrCoveragePct: 0 },
        ),
        tier1: [],
      };
  }
}


export function SessionScopeProvider({ children }: { children: ReactNode }) {
  const [reference, setReference] = useState(REFERENCE_OPTIONS[0]);
  const [benchmark, setBenchmark] = useState(BENCHMARK_OPTIONS[0]);
  const [filter, setFilter] = useState<Filter>(emptyFilter);
  const [demo, setDemo] = useState<DemoScenario>("default");

  const { effectiveParticipants, tier1Rows } = useMemo(() => {
    const overlay = applyOverlay(demo, rawParticipants);
    return { effectiveParticipants: overlay.participants, tier1Rows: overlay.tier1 };
  }, [demo]);

  const derived = useMemo(() => {
    const filterIsDefault =
      filter.participation.size === 0 &&
      filter.positions.size === 0 &&
      filter.period.selected.size === 0 &&
      filter.athletes.size === 0;

    let active = effectiveParticipants;
    if (filter.participation.size > 0)
      active = active.filter((a) => a.participation && filter.participation.has(a.participation));
    if (filter.positions.size > 0)
      active = active.filter((a) => filter.positions.has(a.position));
    if (filter.athletes.size > 0)
      active = active.filter((a) => filter.athletes.has(a.id));

    const parts: string[] = [];
    if (filter.positions.size > 0) {
      parts.push([...filter.positions].map((p) => POSITION_LABEL[p]).join(" + "));
    }
    if (filter.participation.size > 0) {
      parts.push([...filter.participation].join(" + "));
    }
    if (filter.athletes.size > 0 && filter.positions.size === 0) {
      parts.push(`${filter.athletes.size} selected`);
    }
    if (filter.period.selected.size > 0) {
      const opts = timeline(currentSession, filter.period.granularity);
      const selected = opts.filter((o) => filter.period.selected.has(o.id));
      if (selected.length <= 2) {
        parts.push(selected.map((o) => o.label).join(" · "));
      } else {
        parts.push(`${selected.length} periods`);
      }
    }
    const scopeLabel = parts.length > 0 ? parts.join(" · ") : null;

    return {
      activeAthletes: active,
      showingCount: active.length,
      totalParticipants: effectiveParticipants.length,
      scopeLabel,
      filterIsDefault,
    };
  }, [filter, effectiveParticipants]);

  const sessionIsTraining = demo === "training_day";
  const dayCode = sessionIsTraining ? TRAINING_DAY_CODE : null;

  const { benchmarkOptions, defaultBenchmark, referenceOptions, defaultReference } = useMemo(() => {
    const filteredRef = sessionIsTraining
      ? REFERENCE_OPTIONS.filter((o) => o.kind !== "same_opponent")
      : REFERENCE_OPTIONS;
    const refOpts: ReferenceOption[] = filteredRef.map((o) =>
      o.kind === "own_typical" && dayCode
        ? { kind: "own_typical", label: `their typical ${dayCode}` }
        : o,
    );
    const defRef = refOpts[0];

    if (dayCode) {
      const dayTypeOpt: BenchmarkOption = {
        kind: "typical_daytype",
        label: `typical ${dayCode}`,
      };
      const benchOpts = [
        dayTypeOpt,
        ...BENCHMARK_OPTIONS.filter((o) => o.kind !== "same_opponent"),
      ];
      return {
        benchmarkOptions: benchOpts,
        defaultBenchmark: dayTypeOpt,
        referenceOptions: refOpts,
        defaultReference: defRef,
      };
    }
    return {
      benchmarkOptions: BENCHMARK_OPTIONS,
      defaultBenchmark: BENCHMARK_OPTIONS[0],
      referenceOptions: refOpts,
      defaultReference: defRef,
    };
  }, [dayCode, sessionIsTraining]);

  // Reset benchmark + reference to the per-session defaults when the session type flips.
  useEffect(() => {
    setBenchmark(defaultBenchmark);
    setReference(defaultReference);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionIsTraining]);

  const benchmarkIsDefault = benchmark.kind === defaultBenchmark.kind;

  const buildingIds = useMemo(
    () => new Set(BUILDING_IDS_BY_SCENARIO[demo] ?? [BUILDING_ID]),
    [demo],
  );
  const comparableCount =
    effectiveParticipants.length -
    effectiveParticipants.filter((a) => buildingIds.has(a.id)).length;

  const value: SessionScope = {

    reference,
    setReference,
    referenceOptions,
    defaultReference,
    benchmark,
    setBenchmark,
    benchmarkOptions,
    defaultBenchmark,
    benchmarkIsDefault,
    dayCode,
    filter,
    setFilter,
    demo,
    setDemo,
    effectiveParticipants,
    tier1Rows,
    sessionIsTraining,
    ...derived,
  };

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useSessionScope(): SessionScope {
  const v = useContext(Ctx);
  if (!v) throw new Error("useSessionScope must be used inside <SessionScopeProvider>");
  return v;
}

export { currentSession, COVERAGE_MIN };
export type { PeriodOption };
