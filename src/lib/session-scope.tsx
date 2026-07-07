/**
 * ST2 — Session-tab shared state.
 * Benchmark + Reference + Filter + Demo scenario live here so later section
 * prompts inherit working propagation, not a paint.
 *
 * Scoped to <SessionRoute>, not global: the Filter is Session-tab state by
 * rule, and whether Benchmark persists across tabs is an open decision the
 * Longitudinal prompt will make.
 */
import { createContext, useContext, useMemo, useState, type ReactNode } from "react";
import {
  participants,
  currentSession,
  POSITION_LABEL,
  type Athlete,
  type PositionCode,
  type ParticipationTag,
  type PeriodOption,
} from "./session-data";

export type ReferenceKind =
  | "own_typical"
  | "positional"
  | "cohort"
  | "last_n"
  | "season"
  | "same_opponent";
export type BenchmarkKind =
  | "typical_match"
  | "last_match"
  | "last_5"
  | "same_opponent";

export const REFERENCE_OPTIONS: Array<{ kind: ReferenceKind; label: string }> = [
  { kind: "own_typical",   label: "their typical match" },
  { kind: "positional",    label: "positional norm" },
  { kind: "cohort",        label: "cohort" },
  { kind: "last_n",        label: "last 5 matches" },
  { kind: "season",        label: "season average" },
  { kind: "same_opponent", label: "same opponent" },
];

export const BENCHMARK_OPTIONS: Array<{ kind: BenchmarkKind; label: string }> = [
  { kind: "typical_match", label: "typical match" },
  { kind: "last_match",    label: "last match" },
  { kind: "last_5",        label: "last 5 matches" },
  { kind: "same_opponent", label: "same opponent" },
];

export type Filter = {
  participation: Set<ParticipationTag>;
  positions: Set<PositionCode>;
  period: { granularity: "halves" | "15min"; selected: Set<string> };
  athletes: Set<string>;
};

export type DemoScenario = "default" | "all_clear" | "srpe_none" | "srpe_full";

export type SessionScope = {
  reference: { kind: ReferenceKind; label: string };
  setReference: (r: { kind: ReferenceKind; label: string }) => void;
  benchmark: { kind: BenchmarkKind; label: string };
  setBenchmark: (b: { kind: BenchmarkKind; label: string }) => void;

  filter: Filter;
  setFilter: (f: Filter) => void;

  demo: DemoScenario;
  setDemo: (d: DemoScenario) => void;

  // derived
  activeAthletes: Athlete[];         // participants ∩ filter — never includes Sturm
  showingCount: number;              // always "of 18"
  scopeLabel: string | null;         // "Defenders · 0–15'" when a non-default scope is active
  filterIsDefault: boolean;
};

const emptyFilter: Filter = {
  participation: new Set(),
  positions: new Set(),
  period: { granularity: "15min", selected: new Set() },
  athletes: new Set(),
};

const Ctx = createContext<SessionScope | null>(null);

export function SessionScopeProvider({ children }: { children: ReactNode }) {
  const [reference, setReference] = useState(REFERENCE_OPTIONS[0]);
  const [benchmark, setBenchmark] = useState(BENCHMARK_OPTIONS[0]);
  const [filter, setFilter] = useState<Filter>(emptyFilter);
  const [demo, setDemo] = useState<DemoScenario>("default");

  const derived = useMemo(() => {
    const filterIsDefault =
      filter.participation.size === 0 &&
      filter.positions.size === 0 &&
      filter.period.selected.size === 0 &&
      filter.athletes.size === 0;

    let active = participants;
    if (filter.participation.size > 0)
      active = active.filter((a) => a.participation && filter.participation.has(a.participation));
    if (filter.positions.size > 0)
      active = active.filter((a) => filter.positions.has(a.position));
    if (filter.athletes.size > 0)
      active = active.filter((a) => filter.athletes.has(a.id));

    // Scope label (built from same source as chips, not hardcoded)
    const parts: string[] = [];
    if (filter.positions.size > 0) {
      parts.push(
        [...filter.positions].map((p) => POSITION_LABEL[p]).join(" + ")
      );
    }
    if (filter.participation.size > 0) {
      parts.push([...filter.participation].join(" + "));
    }
    if (filter.athletes.size > 0 && filter.positions.size === 0) {
      parts.push(`${filter.athletes.size} selected`);
    }
    if (filter.period.selected.size > 0) {
      parts.push(`${filter.period.selected.size} period${filter.period.selected.size > 1 ? "s" : ""}`);
    }
    const scopeLabel = parts.length > 0 ? parts.join(" · ") : null;

    return {
      activeAthletes: active,
      showingCount: active.length,
      scopeLabel,
      filterIsDefault,
    };
  }, [filter]);

  const value: SessionScope = {
    reference,
    setReference,
    benchmark,
    setBenchmark,
    filter,
    setFilter,
    demo,
    setDemo,
    ...derived,
  };

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useSessionScope(): SessionScope {
  const v = useContext(Ctx);
  if (!v) throw new Error("useSessionScope must be used inside <SessionScopeProvider>");
  return v;
}

export { currentSession };
export type { PeriodOption };
