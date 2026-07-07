/**
 * ST2 — Session > Periods card.
 * Within-session distribution: how load was distributed through the match.
 *
 * §Q — per-block PER-MINUTE RATE, expressed as % of the session's mean
 * per-minute rate on the SAME axis. Computed from raw block loads and the
 * block's minutes (never hand-authored percentages):
 *
 *   sessionMeanRate_axis   = Σ block.load_axis / Σ block.minutes
 *   block.renderedPct_axis = (block.load_axis / block.minutes) / sessionMeanRate_axis × 100
 *
 * So a short window like the ~5' stoppage reads honestly by its RATE — a
 * modest total load divided by few minutes lands high on the shared scale —
 * without being diluted by its share of the match.
 *
 * A period filter never restricts this section — Periods always shows its
 * full breakdown. Position / participation / athlete filters do NOT re-scope
 * these per-block rates in the current data model (per-position period
 * profiles aren't authored), so this section deliberately does not stamp a
 * scope in its descriptor — an honest omission rather than a scope stamp the
 * numbers didn't perform. Use the other sections for scoped views.
 *
 * Peak = the block with the highest computed INTERNAL rate.
 */
import { useMemo, useState } from "react";
import { GapPair } from "@/components/data/GapPair";
import { useSessionScope, currentSession } from "@/lib/session-scope";
import { timeline } from "@/lib/session-data";

/* ---------- Raw loads (units) ------------------------------------------
 * External unit: an external-load unit (think high-intensity-metres-equivalent).
 * Internal unit: an internal-load unit (TRIMP-equivalent).
 * Values chosen so the story lands under §Q — 75-90' the true internal-rate
 * max, 0-15' loud but not the max, ~5' stoppage HIGH by rate. Coverage on
 * b60 (78%) triggers the internal TrustMark idiom.
 */

type Load = { external: number; internal: number; coverage?: number };

const LOADS_15: Record<string, Load> = {
  b0:       { external: 1650, internal: 1590 }, // 15' — loud open
  b15:      { external: 1620, internal: 1380 },
  b30:      { external: 1440, internal: 1320 },
  b45:      { external: 1320, internal: 1410 },
  b60:      { external: 1560, internal: 1470, coverage: 78 },
  b75:      { external: 1440, internal: 1770 }, // 15' — internal peak
  stoppage: { external:  290, internal:  560 }, // 5'  — high by rate
};

const LOADS_HALVES: Record<string, Load> = {
  h1: { external: 4880, internal: 4515 }, // 47'
  h2: { external: 4650, internal: 5040 }, // 48'
};

/* ---------- Scale / gridlines ------------------------------------------ */

const SCALE_MIN = 40;
const SCALE_MAX = 160;
const GRIDLINES = [50, 75, 100, 125, 150];

/* ---------- Component -------------------------------------------------- */

export function PeriodsCard() {
  const [granularity, setGranularity] = useState<"halves" | "15min">("15min");
  // filter is read but does not re-scope this section (see header docblock).
  useSessionScope();

  const opts = useMemo(
    () => timeline(currentSession, granularity),
    [granularity],
  );

  const rows = useMemo(() => {
    const table = granularity === "halves" ? LOADS_HALVES : LOADS_15;

    // Session means from raw loads across the rendered partition.
    let sumExt = 0;
    let sumInt = 0;
    let sumMin = 0;
    for (const o of opts) {
      const l = table[o.id];
      if (!l) continue;
      sumExt += l.external;
      sumInt += l.internal;
      sumMin += o.endMin - o.startMin;
    }
    const meanExt = sumMin > 0 ? sumExt / sumMin : 1;
    const meanInt = sumMin > 0 ? sumInt / sumMin : 1;

    return opts.map((o) => {
      const l = table[o.id] ?? { external: 0, internal: 0 };
      const durationMin = o.endMin - o.startMin;
      const extRate = (l.external / durationMin / meanExt) * 100;
      const intRate = (l.internal / durationMin / meanInt) * 100;
      return {
        id: o.id,
        label: o.label,
        durationMin,
        external: Math.round(extRate),
        internal: Math.round(intRate),
        coverage: l.coverage,
      };
    });
  }, [opts, granularity]);

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

  const [pinned, setPinned] = useState<string[]>([]);
  const togglePin = (id: string) => {
    setPinned((prev) => {
      if (prev.includes(id)) return prev.filter((p) => p !== id);
      const next = [...prev, id];
      if (next.length > 2) next.shift();
      return next;
    });
  };

  const pinnedRows = pinned
    .map((id) => rows.find((r) => r.id === id))
    .filter((r): r is (typeof rows)[number] => Boolean(r));
  const pinDelta =
    pinnedRows.length === 2
      ? {
          a: pinnedRows[0],
          b: pinnedRows[1],
          gapA: pinnedRows[0].external - pinnedRows[0].internal,
          gapB: pinnedRows[1].external - pinnedRows[1].internal,
          delta:
            pinnedRows[1].external -
            pinnedRows[1].internal -
            (pinnedRows[0].external - pinnedRows[0].internal),
        }
      : null;

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
          </span>
        </div>
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
            not vs a typical match · session-wide (not re-scoped by filter)
          </span>
          <GranularityToggle value={granularity} onChange={setGranularity} />
        </div>

        {/* Chart */}
        <div className="px-5 pt-5 pb-3">
          <div className="mb-1.5 grid grid-cols-[110px_1fr_72px] items-baseline gap-3">
            <span
              className="type-data-label"
              style={{ color: "var(--color-text-tertiary)" }}
            >
              Period
            </span>
            <div
              className="type-data-label"
              style={{ color: "var(--color-text-tertiary)" }}
            >
              per-minute rate — external ● / internal ○
            </div>
            <span
              className="type-data-label text-right"
              style={{ color: "var(--color-text-tertiary)" }}
            >
              GAP E−I · pts
            </span>
          </div>

          <div>
            {rows.map((r, i) => {
              const isPeak = i === peakIdx;
              const isPinned = pinned.includes(r.id);
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
                  title={`${r.label} · ${r.durationMin}' · E ${r.external}% / I ${r.internal}% · gap ${gap >= 0 ? "+" : ""}${gap} pts${r.coverage ? ` · ${r.coverage}% cov (internal)` : ""}`}
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

          {/* Scale legend */}
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
            100% = the session's average per-minute rate on the same axis.
            Each block's mark is its per-minute load rate — a short window
            reads honestly at its own rate, not diluted by its length.
          </p>

          {/* Pin-delta readout */}
          {pinDelta && (
            <div
              className="mt-3 rounded-md border px-3 py-2.5"
              style={{
                borderColor: "var(--color-border)",
                backgroundColor: "var(--color-slate-50)",
              }}
            >
              <div className="mb-1.5 flex items-baseline justify-between">
                <span
                  className="type-card-eyebrow"
                  style={{ color: "var(--color-text-tertiary)" }}
                >
                  gap delta · {pinDelta.a.label} → {pinDelta.b.label}
                </span>
                <span
                  className="type-num text-[13px] font-semibold"
                  style={{ color: "var(--color-text-primary)" }}
                >
                  Δ {pinDelta.delta >= 0 ? "+" : ""}
                  {pinDelta.delta} pts
                </span>
              </div>
              <div className="relative h-4">
                <Gridlines />
                <PinDeltaTrack
                  gapA={pinDelta.gapA}
                  gapB={pinDelta.gapB}
                />
              </div>
              <div
                className="mt-1 flex items-center justify-between type-data-label"
                style={{ color: "var(--color-text-secondary)" }}
              >
                <span>
                  {pinDelta.a.label} gap{" "}
                  <span className="type-num">
                    {pinDelta.gapA >= 0 ? "+" : ""}
                    {pinDelta.gapA}
                  </span>
                </span>
                <span>
                  {pinDelta.b.label} gap{" "}
                  <span className="type-num">
                    {pinDelta.gapB >= 0 ? "+" : ""}
                    {pinDelta.gapB}
                  </span>
                </span>
              </div>
            </div>
          )}
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
                pinned.length > 0
                  ? "var(--color-text-secondary)"
                  : "var(--color-text-tertiary)",
            }}
          >
            {pinned.length === 0
              ? "tap a row to pin — pick two to read the gap delta"
              : pinned.length === 1
                ? "1 pinned — pick one more"
                : "2 pinned · tap to unpin"}
          </span>
        </div>
      </div>
    </section>
  );
}

/* ---------- Sub-parts -------------------------------------------------- */

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
            }}
            aria-hidden
          />
        );
      })}
    </div>
  );
}

/**
 * PinDeltaTrack — places the two pinned gap values on the same shared
 * scale used for the row rates, with a slate connector between them
 * (the delta). Gap values are signed points around 0; map onto the
 * SCALE_MIN..SCALE_MAX window by treating 0 as the 100% (session-avg)
 * gridline anchor.
 */
function PinDeltaTrack({ gapA, gapB }: { gapA: number; gapB: number }) {
  // Map gap-pts (typically -30..+30) onto the 40-160 window centered on 100.
  const toPos = (g: number) => {
    const centered = 100 + g;
    const clamped = Math.max(SCALE_MIN, Math.min(SCALE_MAX, centered));
    return ((clamped - SCALE_MIN) / (SCALE_MAX - SCALE_MIN)) * 100;
  };
  const a = toPos(gapA);
  const b = toPos(gapB);
  const left = Math.min(a, b);
  const right = Math.max(a, b);
  return (
    <div className="relative h-full">
      <div
        className="absolute left-0 right-0 top-1/2 h-[6px] -translate-y-1/2 rounded-full"
        style={{ backgroundColor: "var(--color-data-band)" }}
      />
      <div
        className="absolute top-1/2 h-[2px] -translate-y-1/2"
        style={{
          left: `${left}%`,
          width: `${right - left}%`,
          backgroundColor: "var(--color-slate-500)",
        }}
      />
      <div
        className="absolute top-1/2 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full ring-2 ring-white"
        style={{
          left: `${a}%`,
          backgroundColor: "var(--color-slate-500)",
        }}
        aria-label="first pinned gap"
      />
      <div
        className="absolute top-1/2 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full ring-2 ring-white"
        style={{
          left: `${b}%`,
          backgroundColor: "var(--color-text-primary)",
        }}
        aria-label="second pinned gap"
      />
    </div>
  );
}
