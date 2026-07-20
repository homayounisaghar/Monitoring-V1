/**
 * Longitudinal — Days section.
 *
 * Three lanes over one shared day grid, plus a readout rail that replaces
 * the floating card. Fixed drawn domains; never auto-fit. Missing days
 * keep their slot, rest days show a baseline dot, unconfirmed hatches,
 * thin HR coverage hollows the Cardio Load bar, beyond-range breaks the
 * top and prints the exact value.
 */
import { useMemo, useState, useRef, useEffect } from "react";
import { copy, tmpl } from "@/lib/copy-deck";
import { SegmentedToggle } from "@/components/data/SegmentedToggle";
import { METRICS } from "@/lib/squad-metrics";
import {
  daySeries,
  type LongiWindow,
  type LongiMetric,
  type DayEntry,
  type Horizon,
} from "@/lib/longitudinal-data";
import { dayMonth2, weekdayDayMonth } from "@/lib/format-date";
import { benchLabel, DEFAULT_BENCH, type BenchKind } from "./ScopeLine";
import { hrvSquadOnDay, HRV_LANE_DOMAIN, RECOVERY_INK_VAR } from "@/lib/recovery-data";

/* ─────────────────── fixed drawn domains (§2) ─────────────────── */
/*
 * The two uncalibrated caps (sprintDist, accDec) were computed once from
 * the built data: 95th-percentile day / 0.85, rounded. Reported values
 * live beside the four spec-fixed caps. Never re-derive at render time.
 *
 *   sprintDist  p95 = 184 m  →  184 / 0.85 ≈ 216  →  round 220 m
 *   accDec      p95 =  94 ct →   94 / 0.85 ≈ 111  →  round 110 ct
 */
const ABS_CAP: Record<LongiMetric, number> = {
  totalDistance: 9000,
  hsr: 700,
  sprintDist: 220,
  accDec: 110,
  cardioLoad: 220,
  srpeAU: 700,
};

const EXTERNAL_METRICS: readonly LongiMetric[] = [
  "totalDistance", "hsr", "sprintDist", "accDec",
] as const;

type Mode = "absolute" | "typical";
type View = "chart" | "table";

/* ─────────────────── labels + units ─────────────────── */

function longiToMetricId(m: LongiMetric): keyof typeof METRICS {
  if (m === "srpeAU") return "srpe";
  return m as keyof typeof METRICS;
}
function laneLabel(m: LongiMetric): string {
  return METRICS[longiToMetricId(m)].label;
}
function laneUnit(m: LongiMetric): string {
  if (m === "srpeAU") return copy("longi.days.lane.srpeUnit");
  if (m === "cardioLoad") return copy("longi.days.lane.cardioUnit");
  return METRICS[longiToMetricId(m)].unit;
}

/* ─────────────────── section shell ─────────────────── */

export function DaysSection({
  window: w,
  horizon,
  benchKind,
}: {
  window: LongiWindow;
  horizon: Horizon;
  benchKind: BenchKind;
}) {
  const [metric, setMetric] = useState<LongiMetric>("totalDistance");
  const [mode, setMode] = useState<Mode>("absolute");
  const [view, setView] = useState<View>("chart");

  const series = useMemo(() => daySeries(w), [w]);
  const laneMetrics: LongiMetric[] = [metric, "cardioLoad", "srpeAU"];
  const tickText = tmpl("longi.basis.tick", { label: benchLabel(benchKind, horizon) });
  const benchmarkIsDefault = benchKind === DEFAULT_BENCH;

  return (
    <section id="days" className="scroll-mt-28">
      <div className="mb-3 flex items-baseline justify-between gap-4">
        <div className="flex items-baseline gap-2">
          <h2 className="type-section-h" style={{ color: "var(--color-text-primary)" }}>
            {copy("longi.anchor.days")}
          </h2>
          <span className="type-data-label" style={{ color: "var(--color-text-secondary)" }}>
            {copy("longi.days.subtitle")}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <MetricPicker value={metric} onChange={setMetric} />
          <SegmentedToggle<Mode>
            value={mode}
            onChange={setMode}
            options={[
              { id: "absolute", label: copy("longi.days.mode.absolute") },
              { id: "typical", label: copy("longi.days.mode.typical") },
            ]}
          />
          <SegmentedToggle<View>
            value={view}
            onChange={setView}
            options={[
              { id: "chart", label: copy("longi.days.view.chart") },
              { id: "table", label: copy("longi.days.view.table") },
            ]}
          />
        </div>
      </div>

      <div
        className="mb-3 text-[11.5px]"
        style={{ color: "var(--color-text-tertiary)" }}
      >
        {copy("longi.days.basisLine")}
      </div>

      {view === "chart" ? (
        <DaysChart
          series={series}
          laneMetrics={laneMetrics}
          mode={mode}
          tickText={tickText}
          benchmarkIsDefault={benchmarkIsDefault}
        />
      ) : (
        <DaysTable series={series} laneMetrics={laneMetrics} />
      )}
    </section>
  );
}

/* ─────────────────── metric picker ─────────────────── */

function MetricPicker({
  value,
  onChange,
}: {
  value: LongiMetric;
  onChange: (m: LongiMetric) => void;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!open) return;
    const h = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", h);
    return () => document.removeEventListener("mousedown", h);
  }, [open]);

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen((o) => !o)}
        className="type-micro rounded-md border px-2.5 py-1"
        style={{
          borderColor: "var(--color-border)",
          backgroundColor: "var(--color-surface-card)",
          color: "var(--color-text-primary)",
        }}
      >
        {laneLabel(value)} ⌄
      </button>
      {open && (
        <div
          className="absolute right-0 z-40 mt-1 w-56 rounded-md border shadow-md"
          style={{
            borderColor: "var(--color-border)",
            backgroundColor: "var(--color-surface-card)",
          }}
        >
          <div
            className="type-microcaps px-3 py-2"
            style={{
              color: "var(--color-text-secondary)",
              borderBottom: "1px solid var(--color-border)",
            }}
          >
            {copy("longi.days.metricMenuHead")}
          </div>
          {EXTERNAL_METRICS.map((m) => (
            <button
              key={m}
              onClick={() => { onChange(m); setOpen(false); }}
              className="type-body flex w-full items-center justify-between px-3 py-1.5 text-left"
              style={{
                color: "var(--color-text-primary)",
                backgroundColor:
                  m === value ? "var(--color-slate-100)" : "transparent",
              }}
            >
              <span>{laneLabel(m)}</span>
              <span
                className="type-num text-[11px]"
                style={{ color: "var(--color-text-tertiary)" }}
              >
                {METRICS[longiToMetricId(m)].unit}
              </span>
            </button>
          ))}
          {/* Fixed, non-selectable internal lanes. */}
          {(["cardioLoad", "srpeAU"] as LongiMetric[]).map((m) => (
            <div
              key={m}
              className="type-body flex items-center justify-between px-3 py-1.5"
              style={{
                color: "var(--color-text-tertiary)",
                backgroundColor: "var(--color-slate-50)",
                borderTop: "1px solid var(--color-border)",
                fontStyle: "italic",
                cursor: "not-allowed",
              }}
              aria-disabled
            >
              <span>{laneLabel(m)}</span>
              <span className="type-num text-[11px]">{laneUnit(m).split(" ")[0]}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ─────────────────── chart ─────────────────── */

const LANE_H = 52;
const LANE_GAP = 8;
const LABEL_W = 220;

function laneAverage(series: DayEntry[], m: LongiMetric, mode: Mode): number | null {
  let n = 0, sum = 0;
  for (const d of series) {
    if (d.kind !== "session") continue;
    if (mode === "absolute") {
      const v = d.perMetric[m];
      if (v == null) continue;
      sum += v; n++;
    } else {
      const c = d.vsTypical[m];
      if (!c || c.state !== "computed") continue;
      sum += c.pct; n++;
    }
  }
  return n > 0 ? sum / n : null;
}

function formatAbs(v: number, m: LongiMetric): string {
  return String(Math.round(v));
}

function DaysChart({
  series,
  laneMetrics,
  mode,
  tickText,
  benchmarkIsDefault,
}: {
  series: DayEntry[];
  laneMetrics: LongiMetric[];
  mode: Mode;
  tickText: string;
  benchmarkIsDefault: boolean;
}) {
  const [hover, setHover] = useState<number | null>(null);
  const nDays = series.length;

  const averages = laneMetrics.map((m) => laneAverage(series, m, mode));
  const activeDay = hover != null ? series[hover] : null;

  const identity = activeDay
    ? tmpl("longi.days.identity", {
        date: weekdayDayMonth(activeDay.dateISO),
        code:
          activeDay.kind === "missing"
            ? copy("longi.days.missingLabel")
            : activeDay.dayCode ?? copy("longi.days.missingLabel"),
        n: activeDay.athletesTrained,
      })
    : "";
  const identityExtra =
    activeDay?.kind === "missing"
      ? copy("longi.days.hover.noData")
      : activeDay && activeDay.sessionIds.length > 1
      ? copy("longi.days.hover.double")
      : "";

  return (
    <div
      className="rounded-lg border p-4"
      style={{
        backgroundColor: "var(--color-surface-card)",
        borderColor: "var(--color-border)",
      }}
    >
      {/* Header row — reserved-width identity slot */}
      <div className="mb-2 flex items-center justify-end" style={{ minHeight: 20 }}>
        <div
          className="type-num text-[12px] tabular-nums"
          style={{ color: "var(--color-text-secondary)", minWidth: 320, textAlign: "right" }}
        >
          {activeDay ? (
            <>
              {identity}
              {identityExtra && (
                <span style={{ color: "var(--color-text-tertiary)" }}>
                  {" · "}
                  {identityExtra}
                </span>
              )}
            </>
          ) : (
            <span style={{ color: "var(--color-text-tertiary)" }}>
              {/* reserved */}&nbsp;
            </span>
          )}
        </div>
      </div>

      <div className="relative flex">
        {/* Label column */}
        <div className="shrink-0" style={{ width: LABEL_W }}>
          {laneMetrics.map((m, i) => (
            <LaneLabel
              key={m}
              metric={m}
              activeDay={activeDay}
              windowAvg={averages[i]}
              mode={mode}
              heightPx={LANE_H}
              marginBottom={i < laneMetrics.length - 1 ? LANE_GAP : 0}
            />
          ))}
          {/* Recovery group label — sits above the recovery lane label,
              aligned with the recovery lane in the track column. */}
          <div
            className="type-microcaps text-[9.5px] pt-4 pb-1"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            {copy("longi.days.recoveryHead")}
          </div>
          <RecoveryLaneLabel
            activeDay={activeDay}
            heightPx={LANE_H}
          />
        </div>


        {/* Track — three lanes + axis rows */}
        <div
          className="relative min-w-0 flex-1"
          onMouseLeave={() => setHover(null)}
        >
          {/* Highlight column overlay */}
          {hover != null && (
            <div
              className="pointer-events-none absolute top-0"
              style={{
                left: `${(hover / nDays) * 100}%`,
                width: `${100 / nDays}%`,
                bottom: 0,
                backgroundColor: "var(--color-slate-100)",
                opacity: 0.55,
                zIndex: 0,
              }}
            />
          )}

          {laneMetrics.map((m, li) => (
            <div
              key={m}
              className="relative grid"
              style={{
                gridTemplateColumns: `repeat(${nDays},1fr)`,
                height: LANE_H,
                marginBottom: li < laneMetrics.length - 1 ? LANE_GAP : 0,
                borderBottom: "1px solid var(--color-slate-100)",
              }}
              onMouseMove={(e) => {
                const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
                const x = e.clientX - rect.left;
                const idx = Math.max(0, Math.min(nDays - 1, Math.floor((x / rect.width) * nDays)));
                setHover(idx);
              }}
            >
              {/* Endpoint value labels on the lane */}
              <div
                className="pointer-events-none absolute -left-0.5 -top-0.5 type-num text-[9.5px]"
                style={{ color: "var(--color-text-tertiary)" }}
              >
                {mode === "typical" ? 160 : ABS_CAP[m]}
              </div>
              <div
                className="pointer-events-none absolute -left-0.5 -bottom-0.5 type-num text-[9.5px]"
                style={{ color: "var(--color-text-tertiary)" }}
              >
                {mode === "typical" ? 40 : 0}
              </div>
              {mode === "typical" && li === 0 && (
                <div
                  className={
                    "pointer-events-none absolute right-0.5 type-num text-[9.5px] whitespace-nowrap " +
                    (benchmarkIsDefault ? "" : "chip-changed")
                  }
                  style={{
                    top: "50%",
                    transform: "translateY(-110%)",
                    ...(benchmarkIsDefault
                      ? { color: "var(--color-text-tertiary)" }
                      : {}),
                  }}
                >
                  {tickText}
                </div>
              )}

              {series.map((d, i) => (
                <DayBar
                  key={d.dateISO}
                  day={d}
                  metric={m}
                  mode={mode}
                  hovered={hover === i}
                />
              ))}
            </div>
          ))}

          {/* RECOVERY group — separated by a larger gap; HRV squad median
              as % of own baseline, fixed 80–120, slate. Continues across
              rest days and days with no session — the whole point of the
              lane. Thin-reading days render the honest empty slot. */}
          <div style={{ height: 16 }} aria-hidden />
          <div
            className="type-microcaps text-[9.5px] absolute"
            style={{ color: "var(--color-text-tertiary)", left: 0, transform: "translateX(-100%)" }}
            aria-hidden
          />
          <div
            className="relative grid"
            style={{
              gridTemplateColumns: `repeat(${nDays},1fr)`,
              height: LANE_H,
              borderBottom: "1px solid var(--color-slate-100)",
            }}
            onMouseMove={(e) => {
              const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
              const x = e.clientX - rect.left;
              const idx = Math.max(0, Math.min(nDays - 1, Math.floor((x / rect.width) * nDays)));
              setHover(idx);
            }}
          >
            <div
              className="pointer-events-none absolute -left-0.5 -top-0.5 type-num text-[9.5px]"
              style={{ color: "var(--color-text-tertiary)" }}
            >
              {HRV_LANE_DOMAIN[1]}
            </div>
            <div
              className="pointer-events-none absolute -left-0.5 -bottom-0.5 type-num text-[9.5px]"
              style={{ color: "var(--color-text-tertiary)" }}
            >
              {HRV_LANE_DOMAIN[0]}
            </div>
            {/* 100 baseline */}
            <div
              className="pointer-events-none absolute left-0 right-0"
              style={{
                top: `${((HRV_LANE_DOMAIN[1] - 100) / (HRV_LANE_DOMAIN[1] - HRV_LANE_DOMAIN[0])) * 100}%`,
                height: 1,
                backgroundColor: "var(--color-slate-200)",
              }}
              aria-hidden
            />
            {series.map((d) => (
              <RecoveryDot key={d.dateISO} dateISO={d.dateISO} />
            ))}
          </div>


          {/* Day-code axis */}
          <div
            className="mt-2 grid"
            style={{ gridTemplateColumns: `repeat(${nDays},1fr)` }}
          >
            {series.map((d) => (
              <div
                key={d.dateISO}
                className="type-microcaps text-center text-[9.5px]"
                style={{ color: "var(--color-text-tertiary)" }}
              >
                {codeLabel(d)}
              </div>
            ))}
          </div>

          {/* Monday-cadence date labels */}
          <div
            className="mt-1 grid"
            style={{ gridTemplateColumns: `repeat(${nDays},1fr)` }}
          >
            {series.map((d) => (
              <div
                key={d.dateISO}
                className="type-num text-center text-[10px]"
                style={{ color: "var(--color-text-tertiary)" }}
              >
                {isMonday(d.dateISO) ? weekdayDayMonth(d.dateISO) : ""}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function codeLabel(d: DayEntry): string {
  if (d.kind === "missing") return copy("longi.days.missingLabel");
  if (d.kind === "rest") return copy("longi.days.restLabel");
  if (d.dayCode === "MD") return copy("longi.days.matchMark");
  return d.dayCode ?? "";
}

function isMonday(iso: string): boolean {
  const y = Number(iso.slice(0, 4));
  const m = Number(iso.slice(5, 7));
  const dd = Number(iso.slice(8, 10));
  return new Date(Date.UTC(y, m - 1, dd)).getUTCDay() === 1;
}

/* ─────────────────── lane label + value slot ─────────────────── */

function LaneLabel({
  metric,
  activeDay,
  windowAvg,
  mode,
  heightPx,
  marginBottom,
}: {
  metric: LongiMetric;
  activeDay: DayEntry | null;
  windowAvg: number | null;
  mode: Mode;
  heightPx: number;
  marginBottom: number;
}) {
  const axis = metric === "cardioLoad" || metric === "srpeAU" ? "cost" : "work";
  const dot =
    metric === "srpeAU"
      ? "var(--color-axis-cost-light)"
      : axis === "cost"
      ? "var(--color-axis-cost)"
      : "var(--color-axis-work)";

  const slotText = valueSlotText(activeDay, metric, mode, windowAvg);

  return (
    <div
      className="flex items-center justify-between pr-3"
      style={{ height: heightPx, marginBottom }}
    >
      <div className="flex items-center gap-2 min-w-0">
        <span
          className="h-2 w-2 rounded-full shrink-0"
          style={{ backgroundColor: dot }}
          aria-hidden
        />
        <div className="min-w-0">
          <div
            className="type-data-label truncate"
            style={{ color: "var(--color-text-primary)" }}
          >
            {laneLabel(metric)}
          </div>
          <div
            className="type-num text-[10px]"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            {laneUnit(metric)}
          </div>
        </div>
      </div>
      <div
        className="type-num tabular-nums text-[12px] text-right"
        style={{ color: "var(--color-text-primary)", minWidth: 60 }}
      >
        {slotText || <span style={{ color: "var(--color-text-tertiary)" }}>—</span>}
      </div>
    </div>
  );
}

function valueSlotText(
  activeDay: DayEntry | null,
  metric: LongiMetric,
  mode: Mode,
  windowAvg: number | null,
): string {
  if (!activeDay) {
    if (windowAvg == null) return "";
    return mode === "absolute"
      ? formatAbs(windowAvg, metric)
      : `${Math.round(windowAvg)}%`;
  }
  if (activeDay.kind === "missing") return "—";
  if (activeDay.kind === "rest") return "0";
  if (mode === "absolute") {
    const v = activeDay.perMetric[metric];
    if (v == null) return "—";
    const base = formatAbs(v, metric);
    if (metric === "cardioLoad" && activeDay.hrCoverageShare != null && activeDay.hrCoverageShare < 1) {
      const pct = Math.round(activeDay.hrCoverageShare * 100);
      return `${base} ${tmpl("longi.days.cov", { pct })}`;
    }
    if (metric === "srpeAU") {
      if (!activeDay.srpeCollected) return copy("longi.days.srpeNotCollected");
      if (activeDay.srpeSubmitted < activeDay.srpeEligible) {
        return `${base} · ${tmpl("longi.days.srpePartial", { n: activeDay.srpeSubmitted, m: activeDay.srpeEligible })}`;
      }
    }
    return base;
  }
  if (metric === "srpeAU" && !activeDay.srpeCollected) return "—";
  const c = activeDay.vsTypical[metric];
  if (!c || c.state !== "computed") return "—";
  return `${Math.round(c.pct)}%`;
}

/* ─────────────────── bar renderer ─────────────────── */

function DayBar({
  day,
  metric,
  mode,
}: {
  day: DayEntry;
  metric: LongiMetric;
  mode: Mode;
  hovered: boolean;
}) {
  const axis = metric === "cardioLoad" || metric === "srpeAU" ? "cost" : "work";
  const color =
    metric === "srpeAU"
      ? "var(--color-axis-cost-light)"
      : axis === "cost"
      ? "var(--color-axis-cost)"
      : "var(--color-axis-work)";
  const unconfirmed = day.unconfirmed;
  const hatch =
    "repeating-linear-gradient(45deg, transparent 0 3px, rgba(255,255,255,0.35) 3px 6px)";

  if (day.kind === "missing") {
    return (
      <div
        className="relative h-full"
        title={copy("longi.days.hover.noData")}
        style={{ borderRight: "1px solid var(--color-slate-100)" }}
      />
    );
  }
  if (day.kind === "rest") {
    return (
      <div
        className="relative h-full"
        style={{ borderRight: "1px solid var(--color-slate-100)" }}
      >
        <div
          className="absolute left-1/2 bottom-0.5 h-1 w-1 -translate-x-1/2 rounded-full"
          style={{ backgroundColor: "var(--color-text-tertiary)" }}
        />
      </div>
    );
  }

  // session
  if (mode === "absolute") {
    const v = day.perMetric[metric];
    if (v == null) return <div className="h-full" />;

    if (metric === "srpeAU" && !day.srpeCollected) {
      return (
        <div
          className="relative h-full flex items-end justify-center"
          style={{ borderRight: "1px solid var(--color-slate-100)" }}
          title={copy("longi.days.srpeNotCollected")}
        >
          <div
            className="type-num text-[8px] whitespace-nowrap pb-0.5"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            {copy("longi.days.srpeNotCollected")}
          </div>
        </div>
      );
    }

    const cap = ABS_CAP[metric];
    const over = v > cap;
    const heightPct = over ? 100 : (v / cap) * 100;
    const hollow = metric === "cardioLoad" && day.hrCoverageShare != null && day.hrCoverageShare < 1;

    return (
      <div
        className="relative h-full"
        style={{ borderRight: "1px solid var(--color-slate-100)" }}
      >
        <div
          className="absolute bottom-0 left-1/2 -translate-x-1/2"
          style={{
            width: "70%",
            height: `${heightPct}%`,
            backgroundColor: hollow ? "transparent" : color,
            border: hollow ? `1.5px solid ${color}` : undefined,
            backgroundImage: unconfirmed ? hatch : undefined,
          }}
        />
        {over && (
          <>
            {/* break slashes at cap */}
            <div
              className="absolute left-1/2 -translate-x-1/2"
              style={{
                top: 2,
                width: "80%",
                height: 6,
                background:
                  "repeating-linear-gradient(-30deg, var(--color-surface-card) 0 2px, transparent 2px 4px)",
              }}
              aria-hidden
            />
            <div
              className="absolute left-1/2 -translate-x-1/2 top-0 type-num text-[8.5px] tabular-nums"
              style={{ color: "var(--color-text-primary)", transform: "translate(-50%, -110%)" }}
            >
              {Math.round(v)}
            </div>
          </>
        )}
        {metric === "srpeAU" && day.srpeCollected && day.srpeSubmitted < day.srpeEligible && (
          <div
            className="absolute left-1/2 -translate-x-1/2 top-0 type-num text-[8px] whitespace-nowrap"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            {tmpl("longi.days.srpePartial", { n: day.srpeSubmitted, m: day.srpeEligible })}
          </div>
        )}
      </div>
    );
  }

  // vs typical
  // Guard: an absent numerator is not a zero. sRPE without collection has no
  // ratio to draw — render withheld, matching other withheld days.
  if (metric === "srpeAU" && !day.srpeCollected) {
    return (
      <div
        className="relative h-full"
        style={{ borderRight: "1px solid var(--color-slate-100)" }}
      >
        <div
          className="absolute left-1/2 top-1/2 h-px w-2 -translate-x-1/2 -translate-y-1/2"
          style={{ backgroundColor: "var(--color-text-tertiary)" }}
        />
      </div>
    );
  }
  const c = day.vsTypical[metric];
  if (!c) return <div className="h-full" />;
  if (c.state === "withheld") {
    return (
      <div
        className="relative h-full"
        style={{ borderRight: "1px solid var(--color-slate-100)" }}
      >
        <div
          className="absolute left-1/2 top-1/2 h-px w-2 -translate-x-1/2 -translate-y-1/2"
          style={{ backgroundColor: "var(--color-text-tertiary)" }}
        />
      </div>
    );
  }
  const pct = c.pct;
  const clamped = Math.max(40, Math.min(160, pct));
  const midPct = 50; // 100 sits at 50% of 40–160
  const valPct = ((clamped - 40) / 120) * 100;
  const over = pct > 160 || pct < 40;
  const barTop = Math.max(midPct, valPct);
  const barBot = Math.min(midPct, valPct);

  return (
    <div
      className="relative h-full"
      style={{ borderRight: "1px solid var(--color-slate-100)" }}
    >
      {/* 100 baseline */}
      <div
        className="absolute left-0 right-0"
        style={{ bottom: "50%", height: 1, backgroundColor: "var(--color-slate-200)" }}
      />
      <div
        className="absolute left-1/2 -translate-x-1/2"
        style={{
          width: "70%",
          bottom: `${barBot}%`,
          height: `${barTop - barBot}%`,
          backgroundColor: color,
          backgroundImage: unconfirmed ? hatch : undefined,
        }}
      />
      {over && (
        <div
          className="absolute left-1/2 -translate-x-1/2 top-0 type-num text-[8.5px] tabular-nums"
          style={{ color: "var(--color-text-primary)" }}
        >
          {Math.round(pct)}%
        </div>
      )}
    </div>
  );
}

/* ─────────────────── table ─────────────────── */

function DaysTable({
  series,
  laneMetrics,
}: {
  series: DayEntry[];
  laneMetrics: LongiMetric[];
}) {
  const [extMetric, cardio, srpe] = laneMetrics;
  const sessionDays = series.filter((d) => d.kind === "session");

  const avg = (pick: (d: DayEntry) => number | null) => {
    let n = 0, sum = 0;
    for (const d of sessionDays) {
      const v = pick(d);
      if (v == null) continue;
      sum += v; n++;
    }
    return n > 0 ? sum / n : null;
  };
  const avgExt = avg((d) => d.perMetric[extMetric] ?? null);
  const avgExtPct = avg((d) => {
    const c = d.vsTypical[extMetric];
    return c && c.state === "computed" ? c.pct : null;
  });
  const avgCardio = avg((d) => d.perMetric[cardio] ?? null);
  const avgCardioPct = avg((d) => {
    const c = d.vsTypical[cardio];
    return c && c.state === "computed" ? c.pct : null;
  });
  const avgSrpe = avg((d) => d.perMetric[srpe] ?? null);

  const th = "type-microcaps px-2 py-1.5 text-left";
  const td = "px-2 py-1.5 type-num tabular-nums";

  const cell = (v: number | null | string): string => {
    if (v == null || v === "") return "";
    if (typeof v === "string") return v;
    return String(Math.round(v));
  };
  const pct = (c: DayEntry["vsTypical"][LongiMetric]): string => {
    if (!c) return "";
    if (c.state === "withheld") return "—";
    return `${Math.round(c.pct)}%`;
  };

  return (
    <div
      className="overflow-x-auto rounded-lg border"
      style={{
        backgroundColor: "var(--color-surface-card)",
        borderColor: "var(--color-border)",
      }}
    >
      <table className="w-full text-[12px]">
        <thead>
          <tr style={{ borderBottom: "1px solid var(--color-border)", color: "var(--color-text-secondary)" }}>
            <th className={th}>{copy("longi.days.table.head.date")}</th>
            <th className={th}>{copy("longi.days.table.head.day")}</th>
            <th className={th}>{copy("longi.days.table.head.sessions")}</th>
            <th className={th}>{copy("longi.days.table.head.athletes")}</th>
            <th className={th}>{laneLabel(extMetric)}</th>
            <th className={th}>{copy("longi.days.table.head.pctTypical")}</th>
            <th className={th}>{laneLabel(cardio)}</th>
            <th className={th}>{copy("longi.days.table.head.pctTypical")}</th>
            <th className={th}>{laneLabel(srpe)}</th>
          </tr>
        </thead>
        <tbody>
          {series.map((d) => {
            const isRest = d.kind === "rest";
            const isMissing = d.kind === "missing";
            const dayLabel = isMissing
              ? copy("longi.days.missingLabel")
              : isRest
              ? copy("longi.days.restLabel")
              : d.dayCode ?? "";
            const sessCount = d.sessionIds.length;
            return (
              <tr
                key={d.dateISO}
                style={{ borderBottom: "1px solid var(--color-slate-100)", color: "var(--color-text-primary)" }}
              >
                <td className={td}>{weekdayDayMonth(d.dateISO)}</td>
                <td className={td} style={{ color: isRest || isMissing ? "var(--color-text-tertiary)" : undefined }}>
                  {dayLabel}
                </td>
                <td className={td}>{sessCount > 0 ? String(sessCount) : ""}</td>
                <td className={td}>{d.athletesTrained > 0 ? String(d.athletesTrained) : ""}</td>
                <td className={td}>{d.kind === "session" ? cell(d.perMetric[extMetric] ?? null) : ""}</td>
                <td className={td}>{d.kind === "session" ? pct(d.vsTypical[extMetric]) : ""}</td>
                <td className={td}>{d.kind === "session" ? cell(d.perMetric[cardio] ?? null) : ""}</td>
                <td className={td}>{d.kind === "session" ? pct(d.vsTypical[cardio]) : ""}</td>
                <td className={td}>
                  {d.kind === "session"
                    ? d.srpeCollected
                      ? cell(d.perMetric[srpe] ?? null)
                      : copy("longi.days.srpeNotCollected")
                    : ""}
                </td>
              </tr>
            );
          })}
          <tr style={{ borderTop: "2px solid var(--color-border)", color: "var(--color-text-secondary)" }}>
            <td className={td} colSpan={4}>
              {tmpl("longi.days.table.average", { n: sessionDays.length })}
            </td>
            <td className={td}>{cell(avgExt)}</td>
            <td className={td}>{avgExtPct != null ? `${Math.round(avgExtPct)}%` : ""}</td>
            <td className={td}>{cell(avgCardio)}</td>
            <td className={td}>{avgCardioPct != null ? `${Math.round(avgCardioPct)}%` : ""}</td>
            <td className={td}>{cell(avgSrpe)}</td>
          </tr>
        </tbody>
      </table>
      <div
        className="px-3 py-2 text-[11px]"
        style={{ color: "var(--color-text-tertiary)", borderTop: "1px solid var(--color-border)" }}
      >
        {copy("longi.days.table.footnote")}
      </div>
    </div>
  );
}

/* ─────────────────── recovery lane (HRV, slate) ─────────────────── */

function RecoveryLaneLabel({
  activeDay,
  heightPx,
}: {
  activeDay: DayEntry | null;
  heightPx: number;
}) {
  // Value slot: the day's HRV squad median % when hovered; window mean
  // otherwise. Read only for the active day's date — the lane is
  // date-driven, so we don't need a session to draw.
  const dateISO = activeDay?.dateISO;
  const read = dateISO ? hrvSquadOnDay(dateISO) : null;
  const slotText = (() => {
    if (!read) return "";
    if (read.state === "withheld") return "—";
    return `${Math.round(read.medianPct)}%`;
  })();

  return (
    <div
      className="flex items-center justify-between pr-3"
      style={{ height: heightPx }}
    >
      <div className="flex items-center gap-2 min-w-0">
        <span
          className="h-2 w-2 rounded-full shrink-0"
          style={{ backgroundColor: RECOVERY_INK_VAR }}
          aria-hidden
        />
        <div className="min-w-0">
          <div
            className="type-data-label truncate"
            style={{ color: "var(--color-text-primary)" }}
          >
            {copy("longi.days.recoveryLane")}
          </div>
          <div
            className="type-num text-[10px]"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            {copy("longi.days.recoveryUnit")}
          </div>
        </div>
      </div>
      <div
        className="type-num tabular-nums text-[12px] text-right"
        style={{ color: "var(--color-text-primary)", minWidth: 60 }}
      >
        {slotText || <span style={{ color: "var(--color-text-tertiary)" }}>—</span>}
      </div>
    </div>
  );
}

function RecoveryDot({ dateISO }: { dateISO: string }) {
  const read = hrvSquadOnDay(dateISO);
  const LO = HRV_LANE_DOMAIN[0];
  const HI = HRV_LANE_DOMAIN[1];
  if (read.state === "withheld") {
    // Thin-reading day — honest empty slot, never a zero.
    return (
      <div
        className="relative h-full"
        style={{ borderRight: "1px solid var(--color-slate-100)" }}
        title={copy("longi.days.recoveryEmpty")}
      >
        <div
          className="absolute left-1/2 top-1/2 h-px w-2 -translate-x-1/2 -translate-y-1/2"
          style={{ backgroundColor: "var(--color-text-tertiary)" }}
        />
      </div>
    );
  }
  const clamped = Math.max(LO, Math.min(HI, read.medianPct));
  const topPct = ((HI - clamped) / (HI - LO)) * 100;
  return (
    <div
      className="relative h-full"
      style={{ borderRight: "1px solid var(--color-slate-100)" }}
      title={`${Math.round(read.medianPct)}% · ${read.read} of ${read.eligible}`}
    >
      <div
        className="absolute left-1/2 h-1.5 w-1.5 -translate-x-1/2 -translate-y-1/2 rounded-full"
        style={{
          top: `${topPct}%`,
          backgroundColor: RECOVERY_INK_VAR,
          opacity: 0.85,
        }}
      />
    </div>
  );
}
