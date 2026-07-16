/**
 * ST2 — Session > Periods card (rebuilt).
 *
 * Four metric lanes over one true time axis. Descriptive
 * "what happened when" — the work/cost gap becomes a secondary read.
 *
 * Rates are computed, never hard-coded:
 *   rate = (value / minutes) / sessionMeanPerMinute × 100
 * External means are computed over all 95 minutes. The internal
 * (Cardio Load) mean is computed over covered minutes only — blocks
 * whose hrCoverage is at or above PERIODS_DISPLAY_FLOOR.
 *
 * Contact grammar: above-average columns stand ON the 100 line,
 * below-average columns hang 2.5px clear below it. Column fill = axis hue,
 * full saturation — colour is never keyed to a value or side.
 */
import { useMemo, useState } from "react";
import { copy, tmpl } from "@/lib/copy-deck";
import {
  periodsBlocks,
  PERIODS_DISPLAY_FLOOR,
  PERIODS_DOMAIN_MIN,
  PERIODS_DOMAIN_MAX,
  PERIODS_SQUAD_SIZE,
  type PeriodBlock,
} from "@/lib/session-data";
import { ScopeTag } from "@/components/session/ScopeTag";
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "@/components/ui/hover-card";

/* ---------- Geometry ---------- */

const PLOT_H = 90;                                      // px
const PX_PER_PT = PLOT_H / (PERIODS_DOMAIN_MAX - PERIODS_DOMAIN_MIN); // 0.75
const LINE_Y = (PERIODS_DOMAIN_MAX - 100) * PX_PER_PT;  // 37.5 — the 100 line
const BELOW_GAP = 2.5;
const MIN_COL_H = 2;
const COL_MAX_W = 44;

const AXIS_TICKS = [PERIODS_DOMAIN_MAX, 100, PERIODS_DOMAIN_MIN] as const;

/* ---------- Metric config ---------- */

type MetricKey = "totalDistance" | "hsr" | "accelDecel" | "cardioLoad";
type Axis = "work" | "cost";

const METRICS: Array<{
  key: MetricKey;
  labelKey: string;
  unitKey: string;
  axis: Axis;
}> = [
  { key: "totalDistance", labelKey: "canonical.summary.metric.totalDistance", unitKey: "periods.unit.m",  axis: "work" },
  { key: "hsr",           labelKey: "canonical.summary.metric.hsr",           unitKey: "periods.unit.m",  axis: "work" },
  { key: "accelDecel",    labelKey: "canonical.summary.metric.accDec",        unitKey: "periods.unit.ct", axis: "work" },
  { key: "cardioLoad",    labelKey: "canonical.summary.metric.cardioLoad",    unitKey: "periods.unit.cl", axis: "cost" },
];


/* ---------- Aggregation ---------- */

type MetricCell = {
  value: number | null; // null = absent (below floor, internal only)
  rate: number | null;  // true unclamped rate
  unconfirmed?: boolean;
  covered?: number;     // athletes contributing (internal only)
  total?: number;       // squad size
};

type Aggregate = {
  id: string;
  label: string;
  minutes: number;
  weight: number;                       // for grid template
  internalCoveredMin: number;           // for hover foot
  internalMissingMin: number;
  cells: Record<MetricKey, MetricCell>;
};

function computeAggregates(
  blocks: PeriodBlock[],
  view: "halves" | "15min",
): { rows: Aggregate[]; peakId: string | null; totalMin: number; coveredMin: number } {
  const totalMin = blocks.reduce((s, b) => s + b.minutes, 0);
  const covered = blocks.filter((b) => b.hrCoverage >= PERIODS_DISPLAY_FLOOR);
  const coveredMin = covered.reduce((s, b) => s + b.minutes, 0);

  const meanTD = blocks.reduce((s, b) => s + b.totalDistance, 0) / totalMin;
  const meanHSR = blocks.reduce((s, b) => s + b.hsr, 0) / totalMin;
  const meanAD = blocks.reduce((s, b) => s + b.accelDecel, 0) / totalMin;
  const meanCL = coveredMin > 0
    ? covered.reduce((s, b) => s + b.cardioLoad, 0) / coveredMin
    : 1;

  const buckets: PeriodBlock[][] =
    view === "15min"
      ? blocks.map((b) => [b])
      : [
          blocks.filter((b) => b.endMin <= 45),
          blocks.filter((b) => b.startMin >= 45),
        ];
  const labels =
    view === "15min"
      ? blocks.map((b) => b.label)
      : [copy("periods.halfLabel.first"), copy("periods.halfLabel.second")];


  const rows: Aggregate[] = buckets.map((bucket, i) => {
    const minutes = bucket.reduce((s, b) => s + b.minutes, 0);
    const coveredBucket = bucket.filter((b) => b.hrCoverage >= PERIODS_DISPLAY_FLOOR);
    const coveredBucketMin = coveredBucket.reduce((s, b) => s + b.minutes, 0);
    const missingMin = minutes - coveredBucketMin;

    const sumTD = bucket.reduce((s, b) => s + b.totalDistance, 0);
    const sumHSR = bucket.reduce((s, b) => s + b.hsr, 0);
    const sumAD = bucket.reduce((s, b) => s + b.accelDecel, 0);
    const sumCL = coveredBucket.reduce((s, b) => s + b.cardioLoad, 0);
    const anyAdUnconfirmed = bucket.some((b) => b.unconfirmed?.accelDecel);

    // Coverage numbers (only meaningful for internal / cardio)
    let coveredAthletes: number | undefined;
    let totalAthletes: number | undefined;
    if (view === "15min") {
      coveredAthletes = bucket[0].hrCoverage;
      totalAthletes = PERIODS_SQUAD_SIZE;
    } else {
      // For halves, express coverage as the minimum of the constituent
      // covered blocks — a scalar honest enough for the hover badge.
      coveredAthletes = coveredBucket.length > 0
        ? Math.min(...coveredBucket.map((b) => b.hrCoverage))
        : 0;
      totalAthletes = PERIODS_SQUAD_SIZE;
    }

    const cardioAbsent = coveredBucketMin === 0;

    const cells: Record<MetricKey, MetricCell> = {
      totalDistance: {
        value: sumTD,
        rate: (sumTD / minutes) / meanTD * 100,
      },
      hsr: {
        value: sumHSR,
        rate: (sumHSR / minutes) / meanHSR * 100,
      },
      accelDecel: {
        value: sumAD,
        rate: (sumAD / minutes) / meanAD * 100,
        unconfirmed: anyAdUnconfirmed,
      },
      cardioLoad: cardioAbsent
        ? {
            value: null,
            rate: null,
            covered: view === "15min" ? bucket[0].hrCoverage : 0,
            total: totalAthletes,
          }
        : {
            value: sumCL,
            rate: (sumCL / coveredBucketMin) / meanCL * 100,
            covered: coveredAthletes,
            total: totalAthletes,
          },
    };

    return {
      id: view === "15min" ? bucket[0].id : `h${i + 1}`,
      label: labels[i],
      minutes,
      weight: minutes,
      internalCoveredMin: coveredBucketMin,
      internalMissingMin: missingMin,
      cells,
    };
  });

  // Peak = highest covered Cardio Load rate
  let peakId: string | null = null;
  let peakRate = -Infinity;
  for (const r of rows) {
    const cl = r.cells.cardioLoad.rate;
    if (cl !== null && cl > peakRate) {
      peakRate = cl;
      peakId = r.id;
    }
  }

  return { rows, peakId, totalMin, coveredMin };
}

/* ---------- Component ---------- */

export function PeriodsCard() {
  const [view, setView] = useState<"halves" | "15min">("15min");
  const [hoverCol, setHoverCol] = useState<string | null>(null);

  const { rows, peakId, totalMin, coveredMin } = useMemo(
    () => computeAggregates(periodsBlocks, view),
    [view],
  );

  const partialInternal = coveredMin < totalMin;

  const gridTemplate = useMemo(
    () =>
      `200px ${rows.map((r) => `${r.weight}fr`).join(" ")} 40px`,
    [rows],
  );

  return (
    <section id="periods" className="scroll-mt-36">
      <header className="mb-3 flex items-baseline justify-between gap-4">
        <div className="flex items-baseline gap-2 flex-wrap">
          <h2 className="type-section-h">{copy("canonical.section.periods")}</h2>
          <span className="type-label" style={{ color: "var(--color-text-tertiary)" }}>
            {copy("canonical.periods.subtitle")}
          </span>
        </div>
        <div className="flex items-center gap-3">
          <GranularityToggle value={view} onChange={setView} />
          <ScopeTag full />
        </div>
      </header>

      <div
        className="overflow-hidden rounded-lg border"
        style={{
          borderColor: "var(--color-border)",
          backgroundColor: "var(--color-surface-card)",
        }}
      >
        <div className="px-5 pt-5 pb-4">
          {/* External group head */}
          <GroupHead
            axis="work"
            label={copy("canonical.axisGroup.externalWork")}
            rightNote={copy("periods.axisNote")}
          />

          {/* Time header row */}
          <TimeHeader
            rows={rows}
            gridTemplate={gridTemplate}
            peakId={peakId}
            hoverCol={hoverCol}
            setHoverCol={setHoverCol}
          />

          {/* Three external lanes */}
          {METRICS.filter((m) => m.axis === "work").map((m, i) => (
            <Lane
              key={m.key}
              metric={m}
              rows={rows}
              gridTemplate={gridTemplate}
              peakId={peakId}
              hoverCol={hoverCol}
              setHoverCol={setHoverCol}
              showRightTicks={i === 0}
              rowsAll={rows}
              view={view}
              partialInternal={partialInternal}
              totalMin={totalMin}
              coveredMin={coveredMin}
            />
          ))}

          {/* Divider */}
          <div
            aria-hidden
            className="my-4 h-px w-full"
            style={{ backgroundColor: "var(--color-border)" }}
          />

          {/* Internal group head */}
          <GroupHead
            axis="cost"
            label={copy("canonical.axisGroup.internalCost")}
          />

          {METRICS.filter((m) => m.axis === "cost").map((m) => (
            <Lane
              key={m.key}
              metric={m}
              rows={rows}
              gridTemplate={gridTemplate}
              peakId={peakId}
              hoverCol={hoverCol}
              setHoverCol={setHoverCol}
              showRightTicks={false}
              rowsAll={rows}
              view={view}
              partialInternal={partialInternal}
              totalMin={totalMin}
              coveredMin={coveredMin}
            />
          ))}

          {/* Gap row */}
          <div
            aria-hidden
            className="mt-3 h-px w-full"
            style={{ backgroundColor: "var(--color-border)" }}
          />
          <GapRow
            rows={rows}
            gridTemplate={gridTemplate}
            hoverCol={hoverCol}
            setHoverCol={setHoverCol}
          />
        </div>

        {/* Legend */}
        <div
          className="border-t px-5 py-3"
          style={{
            borderColor: "var(--color-border)",
            backgroundColor: "var(--color-slate-50)",
          }}
        >
          <Legend />
        </div>
      </div>
    </section>
  );
}

/* ---------- Sub-parts ---------- */

function GroupHead({
  axis,
  label,
  rightNote,
}: {
  axis: Axis;
  label: string;
  rightNote?: string;
}) {
  return (
    <div className="mb-2 flex items-baseline justify-between gap-4">
      <div className="flex items-center gap-2">
        <span
          className="h-2 w-2 rounded-full"
          style={{
            backgroundColor:
              axis === "work" ? "var(--color-axis-work)" : "var(--color-axis-cost)",
          }}
          aria-hidden
        />
        <span className="type-col-head">{label}</span>
      </div>
      {rightNote && (
        <span
          className="type-num text-[11px]"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          {rightNote}
        </span>
      )}
    </div>
  );
}

function TimeHeader({
  rows,
  gridTemplate,
  peakId,
  hoverCol,
  setHoverCol,
}: {
  rows: Aggregate[];
  gridTemplate: string;
  peakId: string | null;
  hoverCol: string | null;
  setHoverCol: (id: string | null) => void;
}) {
  return (
    <div
      className="grid items-end pb-2"
      style={{ gridTemplateColumns: gridTemplate }}
    >
      <span />
      {rows.map((r) => {
        const isPeak = r.id === peakId;
        const isHovered = hoverCol === r.id;
        return (
          <div
            key={r.id}
            className="flex items-baseline justify-center gap-1 border-l px-1 py-1"
            style={{
              borderColor: "var(--color-border)",
              backgroundColor: isHovered ? "var(--color-slate-50)" : "transparent",
            }}
            onMouseEnter={() => setHoverCol(r.id)}
            onMouseLeave={() => setHoverCol(null)}
          >
            <span
              className="type-num text-[12px]"
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
                  backgroundColor: "var(--color-slate-100)",
                  color: "var(--color-text-secondary)",
                }}
              >
                {copy("periods.peakChip")}
              </span>
            )}
          </div>
        );
      })}
      <span
        className="border-l"
        style={{ borderColor: "var(--color-border)" }}
      />
    </div>
  );
}

function Lane({
  metric,
  rows,
  gridTemplate,
  peakId,
  hoverCol,
  setHoverCol,
  showRightTicks,
  view,
  partialInternal,
  totalMin,
  coveredMin,
}: {
  metric: (typeof METRICS)[number];
  rows: Aggregate[];
  gridTemplate: string;
  peakId: string | null;
  hoverCol: string | null;
  setHoverCol: (id: string | null) => void;
  showRightTicks: boolean;
  rowsAll: Aggregate[];
  view: "halves" | "15min";
  partialInternal: boolean;
  totalMin: number;
  coveredMin: number;
}) {
  const unit = copy(metric.unitKey);
  return (
    <div
      className="grid items-stretch"
      style={{ gridTemplateColumns: gridTemplate }}
    >
      {/* left rail — metric name + unit */}
      <div className="flex flex-col justify-center py-2 pr-3">
        <span
          className="type-num text-[12.5px] font-medium"
          style={{ color: "var(--color-text-primary)" }}
        >
          {copy(metric.labelKey)}
        </span>
        <span
          className="type-data-label text-[10.5px]"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          {unit}
        </span>
      </div>

      {rows.map((r) => {
        const cell = r.cells[metric.key];
        const isHovered = hoverCol === r.id;
        return (
          <HoverCard key={r.id} openDelay={80} closeDelay={40}>
            <HoverCardTrigger asChild>
              <div
                className="relative flex flex-col items-center border-l pt-1 pb-1"
                style={{
                  borderColor: "var(--color-border)",
                  backgroundColor: isHovered ? "var(--color-slate-50)" : "transparent",
                }}
                onMouseEnter={() => setHoverCol(r.id)}
                onMouseLeave={() => setHoverCol(null)}
              >
                <NumeralHead
                  cell={cell}
                  unit={unit}
                  isCardio={metric.key === "cardioLoad"}
                  partialCoverage={
                    metric.key === "cardioLoad" && r.internalMissingMin > 0
                  }
                />

                <Column
                  cell={cell}
                  axis={metric.axis}
                />
              </div>
            </HoverCardTrigger>
            <HoverCardContent
              className="w-72 p-3"
              side="top"
              align="center"
            >
              <BlockHover
                row={r}
                peakId={peakId}
                view={view}
                partialInternal={partialInternal}
                totalMin={totalMin}
                coveredMin={coveredMin}
              />
            </HoverCardContent>
          </HoverCard>
        );
      })}

      {/* right axis rail */}
      <div
        className="relative border-l"
        style={{
          borderColor: "var(--color-border)",
          height: PLOT_H + 24, // include head area
        }}
      >
        {showRightTicks ? (
          <>
            {AXIS_TICKS.map((t) => {
              const y = 24 + (PERIODS_DOMAIN_MAX - t) * PX_PER_PT;
              return (
                <span
                  key={t}
                  className="absolute left-1 type-num text-[10px]"
                  style={{
                    top: y - 6,
                    color: "var(--color-text-tertiary)",
                  }}
                >
                  {t}
                </span>
              );
            })}
          </>
        ) : (
          <span
            className="absolute left-1 type-num text-[10px]"
            style={{
              top: 24 + (PERIODS_DOMAIN_MAX - 100) * PX_PER_PT - 6,
              color: "var(--color-text-tertiary)",
            }}
          >
            100
          </span>
        )}
      </div>
    </div>
  );
}

function NumeralHead({
  cell,
  unit,
  isCardio,
  partialCoverage = false,
}: {
  cell: MetricCell;
  unit: string;
  isCardio: boolean;
  partialCoverage?: boolean;
}) {
  if (cell.value === null || cell.rate === null) {
    return (
      <span
        className="type-num text-[11px]"
        style={{ color: "var(--color-text-tertiary)" }}
      >
        —
      </span>
    );
  }
  const clamped = cell.rate > PERIODS_DOMAIN_MAX || cell.rate < PERIODS_DOMAIN_MIN;
  const thinAthletes =
    isCardio && cell.covered !== undefined && cell.total !== undefined && cell.covered < cell.total;
  const thinCoverage = isCardio && (thinAthletes || partialCoverage);
  return (
    <span
      className="type-num inline-flex items-baseline gap-1 text-[11px]"
      style={{ color: "var(--color-text-secondary)" }}
    >
      {thinCoverage && (
        <span
          className="inline-block h-1.5 w-1.5 shrink-0 translate-y-[-1px] rounded-full"
          style={{ backgroundColor: "var(--color-trust-dot)" }}
          aria-hidden
        />
      )}
      <span>
        {formatValue(cell.value)}
      </span>
      {clamped && (
        <span
          className="type-num text-[10.5px]"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          · {Math.round(cell.rate)}%
        </span>
      )}
      <span className="sr-only">{unit}</span>
    </span>
  );
}

function formatValue(v: number): string {
  return Math.round(v).toLocaleString();
}

function Column({
  cell,
  axis,
}: {
  cell: MetricCell;
  axis: Axis;
}) {
  if (cell.value === null || cell.rate === null) {
    return <div style={{ height: PLOT_H, width: "100%" }} />;
  }
  const color = axis === "work" ? "var(--color-axis-work)" : "var(--color-axis-cost)";
  const rawRate = cell.rate;
  const clampedHigh = rawRate > PERIODS_DOMAIN_MAX;
  const clampedLow = rawRate < PERIODS_DOMAIN_MIN;
  const drawn = Math.max(
    PERIODS_DOMAIN_MIN,
    Math.min(PERIODS_DOMAIN_MAX, rawRate),
  );

  let top: number;
  let height: number;
  const above = drawn >= 100;
  if (above) {
    const rise = (drawn - 100) * PX_PER_PT;
    height = Math.max(MIN_COL_H, rise);
    top = LINE_Y - height;
  } else {
    top = LINE_Y + BELOW_GAP;
    const fall = (100 - drawn) * PX_PER_PT;
    height = Math.max(MIN_COL_H, fall);
  }

  const unconfirmed = !!cell.unconfirmed;

  return (
    <div
      className="relative w-full"
      style={{ height: PLOT_H }}
    >
      {/* 100 line */}
      <div
        aria-hidden
        className="absolute left-0 right-0"
        style={{
          top: LINE_Y,
          height: 1,
          backgroundColor: "var(--color-slate-300)",
        }}
      />

      {/* column */}
      <div
        className="absolute left-1/2"
        style={{
          top,
          height,
          width: `min(${COL_MAX_W}px, 80%)`,
          transform: "translateX(-50%)",
          backgroundColor: color,
          backgroundImage: unconfirmed
            ? `repeating-linear-gradient(-45deg, rgba(255,255,255,0.55) 0 2px, transparent 2px 5px)`
            : undefined,
          boxShadow: unconfirmed ? `inset 0 0 0 1px ${color}` : undefined,
        }}
      >
        {/* clamp break slashes */}
        {(clampedHigh || clampedLow) && (
          <>
            <span
              aria-hidden
              className="absolute left-0 right-0"
              style={{
                [clampedHigh ? "top" : "bottom"]: 3,
                height: 2,
                transform: "skewY(-18deg)",
                backgroundColor: "#fff",
              }}
            />
            <span
              aria-hidden
              className="absolute left-0 right-0"
              style={{
                [clampedHigh ? "top" : "bottom"]: 8,
                height: 2,
                transform: "skewY(-18deg)",
                backgroundColor: "#fff",
              }}
            />
          </>
        )}
      </div>

      {/* unconfirmed ring cap at the far end */}
      {unconfirmed && (
        <div
          className="absolute left-1/2 rounded-full"
          style={{
            top: above ? top - 3 : top + height - 4,
            transform: "translateX(-50%)",
            width: 7,
            height: 7,
            backgroundColor: "#fff",
            border: `1px solid ${color}`,
          }}
          aria-hidden
        />
      )}
    </div>
  );
}

function GapRow({
  rows,
  gridTemplate,
  hoverCol,
  setHoverCol,
}: {
  rows: Aggregate[];
  gridTemplate: string;
  hoverCol: string | null;
  setHoverCol: (id: string | null) => void;
}) {
  return (
    <div
      className="grid items-center py-2"
      style={{ gridTemplateColumns: gridTemplate }}
    >
      <div className="flex items-center pr-3">
        <span
          className="type-num text-[12.5px] font-medium"
          style={{ color: "var(--color-text-secondary)" }}
        >
          {copy("periods.gap.label")}
        </span>
      </div>
      {rows.map((r) => {
        const isHovered = hoverCol === r.id;
        const gap = computeGap(r);
        return (
          <div
            key={r.id}
            className="flex justify-center border-l py-1"
            style={{
              borderColor: "var(--color-border)",
              backgroundColor: isHovered ? "var(--color-slate-50)" : "transparent",
            }}
            onMouseEnter={() => setHoverCol(r.id)}
            onMouseLeave={() => setHoverCol(null)}
          >
            <span
              className="type-num text-[12.5px]"
              style={{ color: "var(--color-text-primary)" }}
            >
              {gap === null ? "—" : `${gap >= 0 ? "+" : ""}${gap}`}
            </span>
          </div>
        );
      })}
      <span
        className="border-l"
        style={{ borderColor: "var(--color-border)" }}
      />
    </div>
  );
}

function computeGap(r: Aggregate): number | null {
  const ext = r.cells.totalDistance.rate;
  const int = r.cells.cardioLoad.rate;
  if (ext === null || int === null) return null;
  return Math.round(ext) - Math.round(int);
}

function BlockHover({
  row,
  peakId,
  view,
  partialInternal,
  totalMin,
  coveredMin,
}: {
  row: Aggregate;
  peakId: string | null;
  view: "halves" | "15min";
  partialInternal: boolean;
  totalMin: number;
  coveredMin: number;
}) {
  const gap = computeGap(row);
  const extRate = row.cells.totalDistance.rate;
  const rows: Array<{ label: string; body: string }> = [];

  const push = (labelKey: string, cell: MetricCell, unitKey: string) => {
    const label = copy(labelKey);
    const unit = copy(unitKey);
    if (cell.value === null || cell.rate === null) {
      const covTxt =
        cell.covered !== undefined && cell.total !== undefined
          ? ` · ${tmpl("periods.hover.belowFloorTemplate", {
              cov: cell.covered,
              total: cell.total,
              floor: PERIODS_DISPLAY_FLOOR,
            })}`
          : "";
      rows.push({ label, body: `—${covTxt}` });
      return;
    }
    let body = `${formatValue(cell.value)} ${unit} · ${Math.round(cell.rate)}%`;
    if (cell.rate > PERIODS_DOMAIN_MAX || cell.rate < PERIODS_DOMAIN_MIN) {
      body += ` — ${copy("periods.hover.pastScale")}`;
    }
    if (cell.unconfirmed) {
      body += ` · ${copy("periods.hover.unconfirmed")}`;
    }
    if (cell.covered !== undefined && cell.total !== undefined) {
      body += ` · ${tmpl("periods.hover.covOfTemplate", {
        cov: cell.covered,
        total: cell.total,
      })}`;
    }
    rows.push({ label, body });
  };

  push("periods.hover.rowLabel.total", row.cells.totalDistance, "periods.unit.m");
  push("periods.hover.rowLabel.hsr", row.cells.hsr, "periods.unit.m");
  push("periods.hover.rowLabel.accDec", row.cells.accelDecel, "periods.unit.ct");
  push("periods.hover.rowLabel.cardio", row.cells.cardioLoad, "periods.unit.cl");

  const gapBody =
    gap === null
      ? `— · ${copy("periods.hover.internalAbsent")}`
      : extRate !== null
        ? `${gap >= 0 ? "+" : ""}${gap} pts · ${copy("periods.hover.gapVsDist")} ${Math.round(extRate)}`
        : `${gap >= 0 ? "+" : ""}${gap} pts`;
  rows.push({ label: copy("periods.hover.rowLabel.gap"), body: gapBody });

  const includesUnconfirmed =
    view === "halves" && row.cells.accelDecel.unconfirmed;

  return (
    <div className="space-y-2">
      <div
        className="type-num text-[12.5px] font-semibold"
        style={{ color: "var(--color-text-primary)" }}
      >
        {row.label} · {row.minutes} min
      </div>
      <div className="space-y-1">
        {rows.map((r, i) => (
          <div key={i} className="flex items-baseline justify-between gap-3">
            <span
              className="type-data-label text-[11px]"
              style={{ color: "var(--color-text-tertiary)" }}
            >
              {r.label}
            </span>
            <span
              className="type-num text-[11.5px] text-right"
              style={{ color: "var(--color-text-primary)" }}
            >
              {r.body}
            </span>
          </div>
        ))}
      </div>

      {row.id === peakId && (
        <div
          className="type-num text-[11px] pt-1"
          style={{ color: "var(--color-text-secondary)" }}
        >
          {copy("periods.hover.peakLine")}
        </div>
      )}
      {includesUnconfirmed && (
        <div
          className="type-num text-[11px]"
          style={{ color: "var(--color-text-secondary)" }}
        >
          {copy("periods.hover.includesUnconfirmed")}
        </div>
      )}
      {view === "halves" && row.internalMissingMin > 0 && (
        <div
          className="type-num text-[11px]"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          {tmpl("periods.hover.halvesCovTemplate", {
            covered: row.internalCoveredMin,
            total: row.minutes,
          })}
        </div>
      )}
      {partialInternal && (
        <div
          className="type-num text-[11px] border-t pt-1 mt-1"
          style={{
            color: "var(--color-text-tertiary)",
            borderColor: "var(--color-border)",
          }}
        >
          {tmpl("periods.hover.covFootTemplate", {
            covered: coveredMin,
            total: totalMin,
          })}
        </div>
      )}
    </div>
  );
}

function Legend() {
  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center gap-4 flex-wrap">
        <span className="inline-flex items-center gap-1.5">
          <span
            className="h-2 w-2 rounded-full"
            style={{ backgroundColor: "var(--color-axis-work)" }}
            aria-hidden
          />
          <span
            className="h-2 w-2 rounded-full"
            style={{ backgroundColor: "var(--color-axis-cost)" }}
            aria-hidden
          />
          <span
            className="type-num text-[11px]"
            style={{ color: "var(--color-text-secondary)" }}
          >
            {copy("periods.legend.axes")}
          </span>
        </span>
        <span
          className="type-num text-[11px]"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          {copy("periods.legend.columns")}
        </span>
      </div>
      <div className="flex items-center gap-4 flex-wrap">
        <span
          className="type-num text-[11px]"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          {copy("periods.legend.states")}
        </span>
        <span
          className="type-num text-[11px]"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          {copy("periods.legend.gap")}
        </span>
      </div>
    </div>
  );
}

/* ---------- Granularity toggle (unchanged shape) ---------- */

function GranularityToggle({
  value,
  onChange,
}: {
  value: "halves" | "15min";
  onChange: (v: "halves" | "15min") => void;
}) {
  const options: Array<{ id: "halves" | "15min"; label: string }> = [
    { id: "halves", label: copy("canonical.filter.granularity.halves") },
    { id: "15min", label: copy("canonical.filter.granularity.blocks15") },
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
