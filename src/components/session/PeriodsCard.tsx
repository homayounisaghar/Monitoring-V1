/**
 * ST2 — Session > Periods card.
 * Within-session distribution: how load was distributed through the match.
 * Per-block PER-MINUTE RATE (as % of the session's mean per-minute rate),
 * so a 5' window reads honestly by its rate, not its share of total.
 *
 * A period filter never restricts this section — Periods always shows its
 * full breakdown. Position / participation / athlete filters DO re-scope
 * the per-block rates and stamp the section descriptor inline.
 *
 * Peak = the block with the highest INTERNAL rate — computed from the
 * rendered data (no override, no editorial flag).
 */
import { useMemo, useState } from "react";
import { GapPair } from "@/components/data/GapPair";
import {
  useSessionScope,
  currentSession,
} from "@/lib/session-scope";
import {
  timeline,
  POSITION_LABEL,
  type PositionCode,
} from "@/lib/session-data";

/* ---------- Sample rates (% of session mean per-minute rate) ---------- */

type Rates = { external: number; internal: number; coverage?: number };

// 15' blocks — ids match timeline("15min"): b0, b15, b30, b45, b60, b75, stoppage.
// 75-90' is the TRUE internal maximum (118); the loud opening (0-15') is high but
// not the max (106). The 5' stoppage reads high by RATE (I 112) even though its
// share-of-total would be near 33%.
const RATES_15: Record<string, Rates> = {
  b0:       { external: 110, internal: 106 },
  b15:      { external: 108, internal: 92  },
  b30:      { external: 96,  internal: 88  },
  b45:      { external: 88,  internal: 94  },
  b60:      { external: 104, internal: 98, coverage: 78 },
  b75:      { external: 96,  internal: 118 },
  stoppage: { external: 58,  internal: 112 },
};

// Halves — 1st 0-47', 2nd 47-95'. Non-trivially unequal.
const RATES_HALVES: Record<string, Rates> = {
  h1: { external: 104, internal: 96  },
  h2: { external: 97,  internal: 105 },
};

// Position-scope multipliers — a filter re-computes the per-block rates
// against a plausible position-slice. Deterministic; small.
const POS_MULT: Record<PositionCode, { e: number; i: number }> = {
  GK:  { e: 0.42, i: 0.68 },
  DEF: { e: 0.94, i: 0.98 },
  MID: { e: 1.06, i: 1.03 },
  ATT: { e: 1.02, i: 1.00 },
};

function scopedRates(base: Rates, positions: Set<PositionCode>): Rates {
  if (positions.size === 0) return base;
  let e = 0, i = 0;
  positions.forEach((p) => {
    e += POS_MULT[p].e;
    i += POS_MULT[p].i;
  });
  e /= positions.size;
  i /= positions.size;
  return {
    ...base,
    external: Math.round(base.external * e),
    internal: Math.round(base.internal * i),
  };
}

/* ---------- Component ---------- */

const SCALE_MIN = 40;
const SCALE_MAX = 160;
const GRIDLINES = [50, 75, 100, 125, 150];

export function PeriodsCard() {
  const {
    filter,
    filterIsDefault,
    scopeLabel,
    activeAthletes,
    totalParticipants,
  } = useSessionScope();

  const [granularity, setGranularity] = useState<"halves" | "15min">("15min");

  const opts = useMemo(
    () => timeline(currentSession, granularity),
    [granularity],
  );

  const rows = useMemo(() => {
    const table = granularity === "halves" ? RATES_HALVES : RATES_15;
    return opts.map((o) => {
      const base = table[o.id] ?? { external: 100, internal: 100 };
      const r = scopedRates(base, filter.positions);
      const durationMin = o.endMin - o.startMin;
      return {
        id: o.id,
        label: o.label,
        durationMin,
        external: r.external,
        internal: r.internal,
        coverage: r.coverage,
      };
    });
  }, [opts, granularity, filter.positions]);

  // Peak = argmax internal (computed, no override).
  const peakIdx = useMemo(() => {
    let idx = 0;
    let max = -Infinity;
    rows.forEach((r, i) => {
      if (r.internal > max) {
        max = r.internal;
        idx = i;
      }
    });
    return idx;
  }, [rows]);

  const [pinned, setPinned] = useState<Set<string>>(new Set());
  const togglePin = (id: string) => {
    setPinned((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else {
        if (next.size >= 2) {
          const first = next.values().next().value as string;
          next.delete(first);
        }
        next.add(id);
      }
      return next;
    });
  };

  // Descriptor: scope stamp uses the same pattern as other sections,
  // but any PERIOD scope in the filter is IGNORED here.
  const nonPeriodScope = useMemo(() => {
    if (filterIsDefault || !scopeLabel) return null;
    const parts: string[] = [];
    if (filter.positions.size > 0) {
      parts.push(
        [...filter.positions].map((p) => POSITION_LABEL[p]).join(" + "),
      );
    }
    if (filter.participation.size > 0) {
      parts.push([...filter.participation].join(" + "));
    }
    if (filter.athletes.size > 0 && filter.positions.size === 0) {
      parts.push(`${filter.athletes.size} selected`);
    }
    return parts.length > 0 ? parts.join(" · ") : null;
  }, [filter, filterIsDefault, scopeLabel]);

  const showAthleteCount = nonPeriodScope !== null;

  return (
    <section id="periods" className="scroll-mt-28">
      <header className="mb-3 flex items-baseline justify-between gap-4">
        <div className="flex items-baseline gap-2 flex-wrap">
          <h2 className="type-section-h">Periods</h2>
          <span
            className="type-card-eyebrow"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            — How load was distributed through the match · within-session
            distribution
            {nonPeriodScope ? ` · ${nonPeriodScope}` : ""}
          </span>
        </div>
        {showAthleteCount && (
          <span
            className="type-num text-[11px]"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            {activeAthletes.length} of {totalParticipants}
          </span>
        )}
      </header>

      <div
        className="overflow-hidden rounded-lg border"
        style={{
          borderColor: "var(--color-border)",
          backgroundColor: "var(--color-surface-card)",
        }}
      >
        {/* Toolbar */}
        <div
          className="flex items-center justify-between border-b px-5 py-3"
          style={{ borderColor: "var(--color-border)" }}
        >
          <span
            className="type-card-eyebrow"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            different question from Summary · this is within THIS session,
            not vs a typical match
          </span>
          <GranularityToggle
            value={granularity}
            onChange={setGranularity}
          />
        </div>

        {/* Chart */}
        <div className="px-5 pt-5 pb-3">
          {/* Column headers over the shared scale */}
          <div className="mb-1.5 grid grid-cols-[110px_1fr_72px] items-baseline gap-3">
            <span className="type-data-label" style={{ color: "var(--color-text-tertiary)" }}>
              Period
            </span>
            <div className="type-data-label" style={{ color: "var(--color-text-tertiary)" }}>
              per-minute rate — external ● / internal ○
            </div>
            <span
              className="type-data-label text-right"
              style={{ color: "var(--color-text-tertiary)" }}
            >
              GAP E−I · pts
            </span>
          </div>

          {/* Rows */}
          <div>
            {rows.map((r, i) => {
              const isPeak = i === peakIdx;
              const isPinned = pinned.has(r.id);
              const banded = i % 2 === 1;
              const gap = r.external - r.internal;
              return (
                <button
                  key={r.id}
                  type="button"
                  onClick={() => togglePin(r.id)}
                  className="grid w-full grid-cols-[110px_1fr_72px] items-center gap-3 rounded px-2 py-2 text-left transition-colors"
                  style={{
                    backgroundColor: isPeak
                      ? "var(--color-slate-100)"
                      : banded
                        ? "var(--color-slate-50)"
                        : "transparent",
                    outline: isPinned
                      ? "1px dashed var(--color-slate-400)"
                      : "none",
                    outlineOffset: "-2px",
                  }}
                  title={`${r.label} · E ${r.external}% / I ${r.internal}% · gap ${gap >= 0 ? "+" : ""}${gap} pts${r.coverage ? ` · ${r.coverage}% cov (internal)` : ""}`}
                >
                  <div className="flex items-center gap-1.5">
                    <span
                      className="type-num text-[12.5px]"
                      style={{
                        color: "var(--color-text-primary)",
                        fontWeight: isPeak ? 600 : 500,
                      }}
                    >
                      {r.label}
                    </span>
                    {isPeak && (
                      <span
                        className="rounded px-1 py-[1px] type-data-label text-[10px]"
                        style={{
                          backgroundColor: "var(--color-slate-200)",
                          color: "var(--color-text-secondary)",
                        }}
                      >
                        peak
                      </span>
                    )}
                  </div>

                  <div className="relative">
                    <Gridlines />
                    <div className="relative">
                      <GapPair
                        mode="shared"
                        size="compact"
                        externalPct={r.external}
                        internalPct={r.internal}
                        scaleMin={SCALE_MIN}
                        scaleMax={SCALE_MAX}
                        showLegend={false}
                        deltaLabel=" "
                        internalTrust={
                          r.coverage !== undefined
                            ? { coverage: r.coverage }
                            : undefined
                        }
                      />
                    </div>
                  </div>

                  <span
                    className="type-num text-right text-[12.5px]"
                    style={{
                      color: "var(--color-text-primary)",
                      fontWeight: isPeak ? 600 : 500,
                    }}
                  >
                    {gap >= 0 ? "+" : ""}
                    {gap}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Scale legend under the chart */}
          <div className="mt-2 grid grid-cols-[110px_1fr_72px] gap-3">
            <span />
            <div className="relative h-5">
              {GRIDLINES.map((g) => {
                const left = ((g - SCALE_MIN) / (SCALE_MAX - SCALE_MIN)) * 100;
                const prominent = g === 100;
                return (
                  <span
                    key={g}
                    className="absolute top-0 -translate-x-1/2 type-num text-[10px]"
                    style={{
                      left: `${left}%`,
                      color: prominent
                        ? "var(--color-text-secondary)"
                        : "var(--color-text-tertiary)",
                      fontWeight: prominent ? 600 : 400,
                    }}
                  >
                    {g}%{prominent ? " · session avg" : ""}
                  </span>
                );
              })}
            </div>
            <span />
          </div>

          <p
            className="mt-3 type-data-label"
            style={{ color: "var(--color-text-secondary)" }}
          >
            100% = the session's average rate. Each block's mark is its per-minute
            load rate — so a short window reads honestly at its own rate, not diluted
            by its length.
          </p>
        </div>

        {/* Foot */}
        <div
          className="flex items-center justify-between border-t px-5 py-2.5"
          style={{
            borderColor: "var(--color-border)",
            backgroundColor: "var(--color-slate-50)",
          }}
        >
          <span
            className="type-card-eyebrow"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            peak = the block with the highest internal-load rate
          </span>
          <span
            className="type-data-label"
            style={{
              color:
                pinned.size > 0
                  ? "var(--color-text-secondary)"
                  : "var(--color-text-tertiary)",
            }}
          >
            {pinned.size === 0
              ? "tap a row to pin — pick two to read the gap delta"
              : pinned.size === 1
                ? "1 pinned — pick one more"
                : "2 pinned"}
          </span>
        </div>
      </div>
    </section>
  );
}

/* ---------- Sub-parts ---------- */

function GranularityToggle({
  value,
  onChange,
}: {
  value: "halves" | "15min";
  onChange: (v: "halves" | "15min") => void;
}) {
  const options: Array<{ id: "halves" | "15min"; label: string }> = [
    { id: "halves", label: "Halves" },
    { id: "15min", label: "15' blocks" },
  ];
  return (
    <div
      className="inline-flex rounded-md border p-0.5"
      style={{
        borderColor: "var(--color-border)",
        backgroundColor: "var(--color-canvas)",
      }}
    >
      {options.map((o) => {
        const active = o.id === value;
        return (
          <button
            key={o.id}
            onClick={() => onChange(o.id)}
            className="rounded px-2.5 py-1 text-[12px] transition-colors"
            style={{
              backgroundColor: active
                ? "var(--color-slate-200)"
                : "transparent",
              color: active
                ? "var(--color-text-primary)"
                : "var(--color-text-secondary)",
              fontWeight: active ? 600 : 500,
            }}
          >
            {o.label}
          </button>
        );
      })}
    </div>
  );
}

function Gridlines() {
  return (
    <div className="pointer-events-none absolute inset-0">
      {GRIDLINES.map((g) => {
        const left = ((g - SCALE_MIN) / (SCALE_MAX - SCALE_MIN)) * 100;
        const prominent = g === 100;
        return (
          <span
            key={g}
            className="absolute top-0 h-full w-px"
            style={{
              left: `${left}%`,
              backgroundColor: prominent
                ? "var(--color-slate-400)"
                : "var(--color-slate-200)",
              opacity: prominent ? 0.9 : 0.6,
              borderLeft: prominent ? "none" : "1px dotted var(--color-slate-300)",
              width: prominent ? "1px" : "0",
            }}
            aria-hidden
          />
        );
      })}
    </div>
  );
}
