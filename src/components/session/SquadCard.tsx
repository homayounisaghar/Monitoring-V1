/**
 * ST2 — Session > Squad card.
 *
 * Every athlete × the core metrics. The load-bearing rule: DERIVE, do
 * not tabulate. Every delta, every %-mode cell, every sort key, and
 * the squad-avg row are computed live from raw value + raw reference.
 *
 * Table (default): rows for every athlete in scope; sortable columns;
 *   pinned "Squad avg · N" row on top; DNP + no-data rows pin to foot.
 * Chart: single-column ranked list on one metric.
 *   Absolute → shared unit axis 0..scaleMax, ranked by value.
 *   Percent  → each row rebased to its own typical, ranked by delta.
 *
 * Cell honesty: partial players carry a single row-level "N′ · scaled"
 * beside the minutes; other cells stay clean. Non-comparable cells
 * render "—" with a hover reason. Trust follows the RW0 grammar — a
 * hollow leading dot on the value, coverage % on hover; no hatch
 * behind digits. Köhler prints his value at his rank; his delta is
 * suppressed with "building baseline".
 */
import { useMemo, useState } from "react";
import { ChevronRight, Flag, ChevronUp, ChevronDown, X } from "lucide-react";
import { useNavigate } from "@tanstack/react-router";
import { useSessionScope, COVERAGE_MIN } from "@/lib/session-scope";
import { squad, POSITION_LABEL, type Athlete } from "@/lib/session-data";
import { ScopeTag } from "@/components/session/ScopeTag";
import { copy, tmpl } from "@/lib/copy-deck";
import {
  METRICS,
  DEFAULT_COLUMNS,
  COLUMN_LIBRARY,
  MAX_COLUMNS,
  refFor,
  valueFor,
  cellState,
  isScaled,
  formatValue,
  type Metric,
  type MetricId,
} from "@/lib/squad-metrics";
import { flaggedIds } from "@/lib/session-flags";
import { ValueOnTrack } from "@/components/data/ValueOnTrack";

/* ============================================================ */

type ViewMode = "table" | "chart";
type DisplayMode = "absolute" | "percent";

export function SquadCard() {
  const {
    tier1Rows,
    activeAthletes,
    effectiveParticipants,
    filterIsDefault,
  } = useSessionScope();

  const [view, setView] = useState<ViewMode>("table");
  const [display, setDisplay] = useState<DisplayMode>("absolute");
  const [columns, setColumns] = useState<MetricId[]>(DEFAULT_COLUMNS);
  const [sort, setSort] = useState<{ key: MetricId; dir: "asc" | "desc" }>({
    key: "totalDistance",
    dir: "desc",
  });
  const [chartMetric, setChartMetric] = useState<MetricId>("totalDistance");
  const [pickerOpen, setPickerOpen] = useState(false);
  const navigate = useNavigate();

  /* --- rows in scope --- */

  const scopedIds = useMemo(
    () => new Set(activeAthletes.map((a) => a.id)),
    [activeAthletes],
  );
  const tableRows: Athlete[] = useMemo(() => {
    if (filterIsDefault) return squad;
    return squad.filter((a) => scopedIds.has(a.id));
  }, [filterIsDefault, scopedIds]);

  /* --- flagged identity set --- */

  const lowCovIds = effectiveParticipants
    .filter((a) => a.hrCoveragePct !== null && a.hrCoveragePct < COVERAGE_MIN)
    .map((a) => a.id);
  const flagged = useMemo(
    () => flaggedIds(tier1Rows, lowCovIds),
    [tier1Rows, lowCovIds],
  );

  /* --- sRPE column trust --- */

  const srpeSubmitted = activeAthletes.filter((a) => a.srpeSubmitted).length;
  const srpeTotal = activeAthletes.length;

  /* --- sort --- */

  const hasSortData = (a: Athlete, key: MetricId): boolean => {
    if (a.participation === null) return false;
    const m = METRICS[key];
    const v = valueFor(a, m);
    if (v == null) return false;
    if (display === "percent") {
      const r = refFor(a, m);
      if (r == null) return false;
    }
    return true;
  };

  const sortValue = (a: Athlete, key: MetricId): number => {
    const m = METRICS[key];
    const v = valueFor(a, m)!;
    if (display === "percent") {
      const r = refFor(a, m)!;
      return (v / r) * 100;
    }
    return v;
  };

  const sortedRows = useMemo(() => {
    const rows = [...tableRows];
    rows.sort((a, b) => {
      // DNP + no-data pin to foot explicitly, regardless of dir.
      const aHas = hasSortData(a, sort.key);
      const bHas = hasSortData(b, sort.key);
      if (!aHas && bHas) return 1;
      if (aHas && !bHas) return -1;
      if (!aHas && !bHas) return a.name.localeCompare(b.name);
      const av = sortValue(a, sort.key);
      const bv = sortValue(b, sort.key);
      if (av === bv) return a.name.localeCompare(b.name);
      return sort.dir === "asc" ? av - bv : bv - av;
    });
    return rows;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tableRows, sort, display]);

  /* --- squad-avg row (in-scope participants) --- */

  const scopeParticipants = activeAthletes;
  const avgCell = (m: Metric): { value: number | null; ref: number | null } => {
    if (m.scaling === "identity") {
      const vs = scopeParticipants
        .map((a) => valueFor(a, m))
        .filter((x): x is number => x != null);
      if (vs.length === 0) return { value: null, ref: null };
      return { value: mean(vs), ref: null };
    }
    if (display === "percent") {
      const pcts = scopeParticipants
        .map((a) => {
          const v = valueFor(a, m);
          const r = refFor(a, m);
          if (v == null || r == null || r === 0) return null;
          return (v / r) * 100;
        })
        .filter((x): x is number => x != null);
      if (pcts.length === 0) return { value: null, ref: 100 };
      return { value: mean(pcts), ref: 100 };
    }
    const pairs = scopeParticipants.map((a) => ({
      v: valueFor(a, m),
      r: refFor(a, m),
    }));
    const vs = pairs.map((p) => p.v).filter((x): x is number => x != null);
    const rs = pairs.map((p) => p.r).filter((x): x is number => x != null);
    return {
      value: vs.length ? mean(vs) : null,
      ref: rs.length ? mean(rs) : null,
    };
  };

  return (
    <section id="squad" className="scroll-mt-28">
      <header className="mb-3 flex items-baseline justify-between gap-4">
        <div className="flex items-baseline gap-2 flex-wrap">
          <h2 className="type-section-h">Squad</h2>
          <span
            className="type-label"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            — {copy("squad.section.desc")}
          </span>
        </div>
        <ScopeTag />
      </header>

      {/* Toolbar */}
      <div
        className="mb-3 flex items-center justify-between gap-3 rounded-t-lg border border-b-0 px-3 py-2"
        style={{
          borderColor: "var(--color-border)",
          backgroundColor: "var(--color-surface-card)",
        }}
      >
        <SegmentedToggle
          value={view}
          onChange={(v) => setView(v)}
          options={[
            { id: "table", label: "Table" },
            { id: "chart", label: "Chart" },
          ]}
        />
        <div className="flex items-center gap-2">
          {view === "chart" && (
            <select
              value={chartMetric}
              onChange={(e) => setChartMetric(e.target.value as MetricId)}
              className="rounded-md border px-2 py-1 text-[12px]"
              style={{
                borderColor: "var(--color-border)",
                backgroundColor: "var(--color-canvas)",
                color: "var(--color-text-primary)",
              }}
            >
              {[...DEFAULT_COLUMNS.filter((c) => c !== "min"),
                ...COLUMN_LIBRARY.flatMap((g) => g.ids).filter(
                  (id) => !DEFAULT_COLUMNS.includes(id),
                )].map((id) => (
                <option key={id} value={id}>
                  {METRICS[id].label}
                </option>
              ))}
            </select>
          )}
          <SegmentedToggle
            value={display}
            onChange={(v) => setDisplay(v)}
            options={[
              { id: "absolute", label: "Absolute" },
              { id: "percent", label: "%" },
            ]}
          />
          {view === "table" && (
            <button
              onClick={() => setPickerOpen(true)}
              className="rounded-md border px-2 py-1 text-[12px] transition-colors hover:bg-[color:var(--color-slate-100)]"
              style={{
                borderColor: "var(--color-border)",
                color: "var(--color-text-secondary)",
              }}
            >
              Columns
            </button>
          )}
        </div>
      </div>

      {/* Body */}
      {view === "table" ? (
        <TableBody
          rows={sortedRows}
          columns={columns}
          display={display}
          sort={sort}
          onSort={(key) =>
            setSort((prev) =>
              prev.key === key
                ? { key, dir: prev.dir === "asc" ? "desc" : "asc" }
                : { key, dir: "desc" },
            )
          }
          flagged={flagged}
          srpeCoverage={{ submitted: srpeSubmitted, total: srpeTotal }}
          onRowClick={(_a) => navigate({ to: "/athlete" })}
          avgCell={avgCell}
          scopeCount={activeAthletes.length}
          onScrollToAttention={() => {
            const el = document.getElementById("attention");
            el?.scrollIntoView({ behavior: "smooth", block: "start" });
          }}
        />
      ) : (
        <ChartBody
          metric={METRICS[chartMetric]}
          display={display}
          rows={activeAthletes}
          allSquadForTray={squad}
          flagged={flagged}
          onRowClick={() => navigate({ to: "/athlete" })}
          onScrollToAttention={() => {
            const el = document.getElementById("attention");
            el?.scrollIntoView({ behavior: "smooth", block: "start" });
          }}
        />
      )}

      {pickerOpen && (
        <ColumnsPicker
          columns={columns}
          onChange={setColumns}
          onClose={() => setPickerOpen(false)}
          onReset={() => setColumns(DEFAULT_COLUMNS)}
        />
      )}
    </section>
  );
}

/* ============================================================ */
/* Table body                                                    */
/* ============================================================ */

function TableBody({
  rows,
  columns,
  display,
  sort,
  onSort,
  flagged,
  srpeCoverage,
  onRowClick,
  avgCell,
  scopeCount,
  onScrollToAttention,
}: {
  rows: Athlete[];
  columns: MetricId[];
  display: DisplayMode;
  sort: { key: MetricId; dir: "asc" | "desc" };
  onSort: (key: MetricId) => void;
  flagged: Set<string>;
  srpeCoverage: { submitted: number; total: number };
  onRowClick: (a: Athlete) => void;
  avgCell: (m: Metric) => { value: number | null; ref: number | null };
  scopeCount: number;
  onScrollToAttention: () => void;
}) {
  return (
    <div
      className="overflow-x-auto rounded-b-lg border"
      style={{
        borderColor: "var(--color-border)",
        backgroundColor: "var(--color-surface-card)",
      }}
    >
      <table className="w-full min-w-[900px] border-collapse text-[13px]">
        <thead>
          <tr
            className="border-b"
            style={{
              borderColor: "var(--color-border)",
              backgroundColor: "var(--color-slate-50)",
            }}
          >
            <th className="px-3 py-2 text-left type-col-head" style={{ minWidth: 200 }}>
              Athlete
            </th>
            {columns.map((id) => {
              const m = METRICS[id];
              const active = sort.key === id;
              return (
                <th
                  key={id}
                  className="px-3 py-2 text-right"
                  style={{
                    minWidth: id === "min" ? 96 : 100,
                    backgroundColor: active
                      ? "var(--color-slate-100)"
                      : undefined,
                  }}
                >
                  <button
                    className="ml-auto inline-flex items-center gap-1.5"
                    onClick={() => onSort(id)}
                    title={`Sort by ${m.label}`}
                  >
                    <span
                      className="h-1.5 w-1.5 rounded-full"
                      style={{
                        backgroundColor:
                          m.axis === "work"
                            ? "var(--color-axis-work)"
                            : m.axis === "cost"
                              ? "var(--color-axis-cost)"
                              : "var(--color-slate-400)",
                        visibility: m.axis === "neutral" ? "hidden" : "visible",
                      }}
                      aria-hidden
                    />
                    <span
                      className="type-col-head"
                      style={{
                        color: active
                          ? "var(--color-text-primary)"
                          : "var(--color-text-secondary)",
                      }}
                    >
                      {m.short}
                    </span>
                    {id === "srpe" && (
                      <span
                        className="inline-block h-2 w-2 shrink-0 rounded-full"
                        style={{
                          backgroundColor: "transparent",
                          border: "1.25px solid var(--color-trust-dot)",
                        }}
                        aria-hidden
                        title={`${srpeCoverage.submitted} of ${srpeCoverage.total}`}
                      />
                    )}
                    {active ? (
                      sort.dir === "desc" ? (
                        <ChevronDown className="h-3 w-3" />
                      ) : (
                        <ChevronUp className="h-3 w-3" />
                      )
                    ) : (
                      <span className="w-3" />
                    )}
                  </button>
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {/* Squad avg row — pinned */}
          <tr
            className="border-b"
            style={{
              borderColor: "var(--color-border)",
              backgroundColor: "var(--color-slate-50)",
            }}
          >
            <td className="px-3 py-2">
              <span
                className="type-label"
                style={{ color: "var(--color-text-tertiary)" }}
              >
                Squad avg · {scopeCount}
              </span>
            </td>
            {columns.map((id) => {
              const m = METRICS[id];
              const { value, ref } = avgCell(m);
              return (
                <td key={id} className="px-3 py-2 text-right">
                  <AvgCell m={m} value={value} ref={ref} display={display} />
                </td>
              );
            })}
          </tr>

          {rows.map((a) => {
            const rowScaled =
              a.participation !== null &&
              a.minutes < 60 &&
              a.id !== "koehler"; // building baseline speaks for itself
            return (
              <tr
                key={a.id}
                onClick={() => onRowClick(a)}
                className="cursor-pointer border-b transition-colors hover:bg-[color:var(--color-slate-50)] last:border-b-0"
                style={{ borderColor: "var(--color-border)" }}
              >
                <td className="px-3 py-2">
                  <div className="flex items-center gap-2">
                    <span
                      className="text-[13px] font-medium"
                      style={{
                        color:
                          a.participation === null
                            ? "var(--color-text-tertiary)"
                            : "var(--color-text-primary)",
                      }}
                    >
                      {a.name}
                    </span>
                    {flagged.has(a.id) && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onScrollToAttention();
                        }}
                        title="Flagged in Attention — view"
                        className="inline-flex h-4 w-4 items-center justify-center rounded transition-colors hover:bg-[color:var(--color-slate-200)]"
                        aria-label={`${a.name} flagged in Attention`}
                      >
                        <Flag
                          className="h-3 w-3"
                          style={{ color: "var(--color-slate-500)" }}
                        />
                      </button>
                    )}
                    <span
                      className="type-label ml-1"
                      style={{ color: "var(--color-text-tertiary)" }}
                    >
                      {a.posDetail}
                    </span>
                    {a.participation === null && (
                      <span
                        className="type-label ml-2"
                        style={{ color: "var(--color-text-tertiary)" }}
                      >
                        · did not participate
                      </span>
                    )}
                  </div>
                </td>
                {columns.map((id) => {
                  const m = METRICS[id];
                  return (
                    <td key={id} className="px-3 py-2 text-right align-middle">
                      <Cell
                        a={a}
                        m={m}
                        display={display}
                        rowScaled={rowScaled}
                      />
                    </td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

/* ---------- individual cell renderers ---------- */

function Cell({
  a,
  m,
  display,
  rowScaled,
}: {
  a: Athlete;
  m: Metric;
  display: DisplayMode;
  rowScaled: boolean;
}) {
  const state = cellState(a, m);

  // Min column — the single home for row-level "· scaled" (Q2).
  if (m.id === "min") {
    if (state === "dnp") {
      return (
        <span
          className="type-num text-[13px]"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          —
        </span>
      );
    }
    const v = valueFor(a, m);
    // Q2: full "N′ · scaled" prints once, beside the minutes.
    if (rowScaled && v != null) {
      return (
        <span
          className="type-num text-[13px]"
          style={{ color: "var(--color-text-primary)" }}
        >
          {tmpl("squad.row.scaledTagTemplate", { min: v })}
        </span>
      );
    }
    return (
      <span
        className="type-num text-[13px]"
        style={{ color: "var(--color-text-primary)" }}
      >
        {v}'
      </span>
    );
  }


  if (state === "dnp" || state === "empty") {
    return (
      <span
        className="type-num text-[13px]"
        style={{ color: "var(--color-text-tertiary)" }}
      >
        —
      </span>
    );
  }
  if (state === "building") {
    const v = valueFor(a, m);
    return (
      <div className="flex flex-col items-end">
        <span
          className="type-num text-[13px]"
          style={{ color: "var(--color-text-primary)" }}
        >
          {display === "percent" ? "—" : formatValue(v, m)}
        </span>
        <span
          className="type-label italic"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          building baseline
        </span>
      </div>
    );
  }
  if (state === "not_compared") {
    // Non-comparable cells render "—" with hover (Q2).
    return (
      <span
        className="type-num text-[13px]"
        style={{ color: "var(--color-text-tertiary)" }}
        title={tmpl("squad.cell.notComparedHoverTemplate", { min: a.minutes })}
      >
        {copy("squad.cell.notCompared")}
      </span>
    );
  }

  // ok
  const v = valueFor(a, m);
  const r = refFor(a, m);
  const isCardio = m.id === "cardioLoad";
  const cov = a.hrCoveragePct ?? 100;
  const lowCov = isCardio && cov < COVERAGE_MIN;

  const cellIsPercent = display === "percent" && r != null;
  const pct = cellIsPercent && r ? Math.round(((v as number) / r) * 100) : null;
  const deltaPct =
    r != null && v != null ? Math.round(((v - r) / r) * 100) : null;

  const primary = cellIsPercent ? `${pct}%` : formatValue(v, m);
  const primaryInk = "var(--color-text-primary)";

  return (
    <div className="flex flex-col items-end">
      <span
        className="inline-flex items-baseline gap-1.5"
        title={lowCov ? `${cov}% HR coverage` : undefined}
      >
        {lowCov && (
          <span
            className="inline-block h-2 w-2 shrink-0 translate-y-[-1px] rounded-full"
            style={{
              backgroundColor: "transparent",
              border: "1.25px solid var(--color-trust-dot)",
            }}
            aria-hidden
          />
        )}
        <span
          className="type-num text-[13px]"
          style={{ color: primaryInk }}
        >
          {primary}
        </span>
      </span>
      {/* Delta once, muted, in absolute mode only. No per-cell "· scaled". */}
      {!cellIsPercent && deltaPct != null && (
        <span
          className="type-num text-[10.5px]"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          {deltaPct >= 0 ? "+" : ""}
          {deltaPct}%
        </span>
      )}
    </div>
  );
}

function AvgCell({
  m,
  value,
  ref,
  display,
}: {
  m: Metric;
  value: number | null;
  ref: number | null;
  display: DisplayMode;
}) {
  if (value == null) {
    return (
      <span
        className="type-num text-[12px]"
        style={{ color: "var(--color-text-tertiary)" }}
      >
        —
      </span>
    );
  }
  if (m.scaling === "identity") {
    return (
      <span
        className="type-num text-[12px] font-semibold"
        style={{ color: "var(--color-text-secondary)" }}
      >
        {Math.round(value)}'
      </span>
    );
  }
  if (display === "percent") {
    return (
      <span
        className="type-num text-[12px] font-semibold"
        style={{ color: "var(--color-text-secondary)" }}
      >
        {Math.round(value)}%
      </span>
    );
  }
  const printed =
    m.decimals != null ? value.toFixed(m.decimals) : Math.round(value).toLocaleString();
  const rawDelta =
    ref != null && ref !== 0 ? ((value - ref) / ref) * 100 : null;
  const deltaPct = rawDelta != null && Number.isFinite(rawDelta) ? Math.round(rawDelta) : null;

  return (
    <div className="flex flex-col items-end" suppressHydrationWarning>
      <span
        className="type-num text-[12px] font-semibold"
        style={{ color: "var(--color-text-secondary)" }}
        suppressHydrationWarning
      >
        {printed}
      </span>
      {deltaPct != null && (
        <span
          className="type-num text-[10px]"
          style={{ color: "var(--color-text-tertiary)" }}
          suppressHydrationWarning
        >
          {deltaPct >= 0 ? "+" : ""}
          {deltaPct}%
        </span>
      )}
    </div>
  );
}

/* ============================================================ */
/* Chart body                                                    */
/* ============================================================ */

function ChartBody({
  metric,
  display,
  rows,
  allSquadForTray,
  flagged,
  onRowClick,
  onScrollToAttention,
}: {
  metric: Metric;
  display: DisplayMode;
  rows: Athlete[];
  allSquadForTray: Athlete[];
  flagged: Set<string>;
  onRowClick: (a: Athlete) => void;
  onScrollToAttention: () => void;
}) {
  // ranked: everyone with a value AND (in % mode) a reference.
  // building baseline (Köhler) has value in absolute but no ref → he
  // ranks in absolute; in % he sinks to the foot of the ranked list.
  const withData = rows
    .filter((a) => a.participation !== null && valueFor(a, metric) != null)
    .map((a) => {
      const state = cellState(a, metric);
      const v = valueFor(a, metric);
      const r = refFor(a, metric);
      return { a, v, r, state };
    });

  const ranked = [...withData].sort((x, y) => {
    if (display === "percent") {
      const xd = x.r ? (x.v! / x.r) * 100 : null;
      const yd = y.r ? (y.v! / y.r) * 100 : null;
      if (xd == null && yd == null) return 0;
      if (xd == null) return 1;
      if (yd == null) return -1;
      return yd - xd;
    }
    return (y.v ?? -Infinity) - (x.v ?? -Infinity);
  });

  // Non-participants + no-data pin to foot explicitly.
  const trayIds = new Set<string>();
  for (const a of allSquadForTray) {
    if (a.participation === null) trayIds.add(a.id);
    else if (rows.some((r) => r.id === a.id) && valueFor(a, metric) == null)
      trayIds.add(a.id);
  }
  const tray = allSquadForTray.filter((a) => trayIds.has(a.id));

  const scaleMax = metric.chartMax;

  return (
    <div
      className="rounded-b-lg border"
      style={{
        borderColor: "var(--color-border)",
        backgroundColor: "var(--color-surface-card)",
      }}
    >
      <div
        className="flex items-baseline justify-between border-b px-4 py-2"
        style={{ borderColor: "var(--color-border)" }}
      >
        <span
          className="type-col-head"
          style={{ color: "var(--color-text-secondary)" }}
        >
          {display === "percent"
            ? `Ranked by delta · ${metric.label}`
            : `Ranked by ${metric.label}`}
        </span>
        <span
          className="type-label"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          {display === "percent"
            ? "Each row re-based to its own typical · ticks align at 100%"
            : `Shared unit axis · 0 — ${formatScale(metric, scaleMax)}`}
        </span>
      </div>
      <ul>
        {ranked.map((r, i) => (
          <ChartRow
            key={r.a.id}
            rank={i + 1}
            a={r.a}
            m={metric}
            display={display}
            value={r.v}
            ref={r.r}
            state={r.state}
            scaleMax={scaleMax}
            flagged={flagged.has(r.a.id)}
            onClick={() => onRowClick(r.a)}
            onFlagClick={onScrollToAttention}
          />
        ))}
      </ul>
      {tray.length > 0 && (
        <div
          className="border-t px-4 py-2"
          style={{
            borderColor: "var(--color-border)",
            backgroundColor: "var(--color-slate-50)",
          }}
        >
          <div
            className="type-label mb-1"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            No data on this metric
          </div>
          <ul className="flex flex-wrap gap-x-4 gap-y-1">
            {tray.map((a) => (
              <li
                key={a.id}
                className="text-[12px]"
                style={{ color: "var(--color-text-secondary)" }}
              >
                {a.name}
                {a.participation === null ? " · DNP" : ""}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function ChartRow({
  rank,
  a,
  m,
  display,
  value,
  ref,
  state,
  scaleMax,
  flagged,
  onClick,
  onFlagClick,
}: {
  rank: number;
  a: Athlete;
  m: Metric;
  display: DisplayMode;
  value: number | null;
  ref: number | null;
  state: ReturnType<typeof cellState>;
  scaleMax: number;
  flagged: boolean;
  onClick: () => void;
  onFlagClick: () => void;
}) {
  const rowScaled =
    a.participation !== null && a.minutes < 60 && a.id !== "koehler";
  return (
    <li
      onClick={onClick}
      className="group flex cursor-pointer items-center gap-3 border-b px-4 py-2.5 last:border-b-0 hover:bg-[color:var(--color-slate-50)]"
      style={{ borderColor: "var(--color-border)" }}
    >
      <span
        className="type-num w-7 text-right text-[12px]"
        style={{ color: "var(--color-text-tertiary)" }}
      >
        {rank}
      </span>
      <div className="w-[190px] shrink-0">
        <div className="flex items-center gap-1.5">
          <span
            className="text-[13px] font-medium"
            style={{ color: "var(--color-text-primary)" }}
          >
            {a.name}
          </span>
          {flagged && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onFlagClick();
              }}
              title="Flagged in Attention — view"
              className="inline-flex h-4 w-4 items-center justify-center rounded hover:bg-[color:var(--color-slate-200)]"
            >
              <Flag
                className="h-3 w-3"
                style={{ color: "var(--color-slate-500)" }}
              />
            </button>
          )}
        </div>
        <div
          className="type-label"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          {a.posDetail} · {a.minutes}'{rowScaled ? " · scaled" : ""}
        </div>
      </div>
      <div className="min-w-0 flex-1">
        {state === "building" ? (
          // Value at rank; delta suppressed; qualifier reads "building baseline".
          display === "percent" ? (
            <div className="flex items-center gap-3">
              <div
                className="relative h-5 flex-1 rounded-full"
                style={{ backgroundColor: "var(--color-data-band)" }}
              />
              <span
                className="w-[140px] text-right type-label italic"
                style={{ color: "var(--color-text-tertiary)" }}
              >
                building baseline
              </span>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <div
                className="relative h-5 flex-1 rounded-full"
                style={{ backgroundColor: "var(--color-data-band)" }}
              >
                {value != null && (
                  <span
                    className="absolute top-1/2 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full ring-2 ring-white"
                    style={{
                      left: `${Math.min(100, (value / scaleMax) * 100)}%`,
                      backgroundColor:
                        m.axis === "work"
                          ? "var(--color-axis-work)"
                          : m.axis === "cost"
                            ? "var(--color-axis-cost)"
                            : "var(--color-slate-500)",
                    }}
                  />
                )}
              </div>
              <div className="w-[140px] flex items-baseline justify-end gap-2">
                <span
                  className="type-num text-sm font-semibold"
                  style={{ color: "var(--color-text-primary)" }}
                >
                  {formatValue(value, m)}
                </span>
                <span
                  className="type-data-label italic"
                  style={{ color: "var(--color-text-tertiary)" }}
                >
                  building
                </span>
              </div>
            </div>
          )
        ) : value == null || ref == null ? (
          <div
            className="text-[12px]"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            —
          </div>
        ) : display === "percent" ? (
          <ValueOnTrack
            mode="deviation"
            axis={m.axis}
            value={value}
            reference={ref}
            windowPct={0.4}
            unit=""
            size="compact"
            showValue={false}
          />
        ) : (
          <ValueOnTrack
            mode="shared"
            axis={m.axis}
            value={value}
            reference={ref}
            scaleMin={0}
            scaleMax={scaleMax}
            referenceBandPct={scaleMax * 0.05}
            scaleLabel={`his typical: ${formatValue(ref, m)}`}
            unit={m.unit === "%" ? "%" : m.unit}
            showValue={true}
            size="compact"
          />
        )}
      </div>
      <ChevronRight
        className="h-3.5 w-3.5 opacity-0 transition-opacity group-hover:opacity-100"
        style={{ color: "var(--color-text-tertiary)" }}
      />
    </li>
  );
}

/* ============================================================ */
/* Columns picker                                                */
/* ============================================================ */

function ColumnsPicker({
  columns,
  onChange,
  onClose,
  onReset,
}: {
  columns: MetricId[];
  onChange: (c: MetricId[]) => void;
  onClose: () => void;
  onReset: () => void;
}) {
  const selected = new Set(columns);
  const atCap = selected.size >= MAX_COLUMNS;
  const toggle = (id: MetricId) => {
    if (id === "min") return;
    const next = new Set(selected);
    if (next.has(id)) next.delete(id);
    else {
      if (next.size >= MAX_COLUMNS) return;
      next.add(id);
    }
    const order: MetricId[] = ["min"];
    for (const g of COLUMN_LIBRARY) {
      for (const cid of g.ids) if (next.has(cid) && !order.includes(cid)) order.push(cid);
    }
    onChange(order);
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/30"
      onClick={onClose}
    >
      <div
        className="w-full max-w-lg rounded-lg border p-5 shadow-xl"
        style={{
          backgroundColor: "var(--color-surface-card)",
          borderColor: "var(--color-border)",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-3 flex items-baseline justify-between">
          <div>
            <div className="text-[15px] font-semibold" style={{ color: "var(--color-text-primary)" }}>
              Columns
            </div>
            <div
              className="type-label"
              style={{ color: "var(--color-text-tertiary)" }}
            >
              {tmpl("squad.columnPicker.counterTemplate", {
                n: selected.size,
                max: MAX_COLUMNS,
              })}
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded p-1 hover:bg-[color:var(--color-slate-100)]"
          >
            <X className="h-4 w-4" style={{ color: "var(--color-text-tertiary)" }} />
          </button>
        </div>

        {COLUMN_LIBRARY.map((g) => (
          <div key={g.group} className="mb-3">
            <div
              className="type-col-head mb-2 flex items-center gap-2"
              style={{ color: "var(--color-text-secondary)" }}
            >
              <span
                className="h-1.5 w-1.5 rounded-full"
                style={{
                  backgroundColor:
                    g.group === "external"
                      ? "var(--color-axis-work)"
                      : "var(--color-axis-cost)",
                }}
              />
              {g.group === "external" ? "External — work" : "Internal — cost"}
            </div>
            <div className="grid grid-cols-2 gap-2">
              {g.ids.map((id) => {
                const on = selected.has(id);
                const disabled = !on && atCap;
                return (
                  <button
                    key={id}
                    onClick={() => toggle(id)}
                    disabled={disabled}
                    title={
                      disabled
                        ? `At the ${MAX_COLUMNS}-column cap — remove one to add another`
                        : undefined
                    }
                    className={`flex items-center justify-between rounded border px-2 py-1.5 text-left text-[12.5px] transition-colors ${
                      on
                        ? "bg-[color:var(--color-slate-100)]"
                        : disabled
                          ? "cursor-not-allowed opacity-50"
                          : "hover:bg-[color:var(--color-slate-50)]"
                    }`}
                    style={{
                      borderColor: on
                        ? "var(--color-text-secondary)"
                        : "var(--color-border)",
                      color: "var(--color-text-primary)",
                    }}
                  >
                    <span>{METRICS[id].label}</span>
                    <span
                      className="type-num text-[10px]"
                      style={{ color: "var(--color-text-tertiary)" }}
                    >
                      {on ? "on" : "off"}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        ))}

        <div
          className="mt-3 flex items-center justify-between border-t pt-3"
          style={{ borderColor: "var(--color-border)" }}
        >
          <span
            className="type-label"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            {copy("squad.export.link")}
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={onReset}
              className="rounded px-2 py-1 text-[12px] transition-colors hover:bg-[color:var(--color-slate-100)]"
              style={{ color: "var(--color-text-secondary)" }}
            >
              Reset to default
            </button>
            <button
              onClick={onClose}
              className="rounded bg-[color:var(--color-slate-900)] px-3 py-1 text-[12px] font-medium text-white transition-colors hover:bg-[color:var(--color-slate-800)]"
            >
              Done
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ============================================================ */
/* Small pieces                                                  */
/* ============================================================ */

function SegmentedToggle<T extends string>({
  value,
  onChange,
  options,
}: {
  value: T;
  onChange: (v: T) => void;
  options: { id: T; label: string }[];
}) {
  return (
    <div
      className="inline-flex rounded-md border p-0.5"
      style={{
        borderColor: "var(--color-border)",
        backgroundColor: "var(--color-canvas)",
      }}
    >
      {options.map((o) => {
        const active = value === o.id;
        return (
          <button
            key={o.id}
            onClick={() => onChange(o.id)}
            className="rounded px-2.5 py-1 text-[12px] transition-colors"
            style={{
              backgroundColor: active
                ? "var(--color-slate-900)"
                : "transparent",
              color: active ? "white" : "var(--color-text-secondary)",
            }}
          >
            {o.label}
          </button>
        );
      })}
    </div>
  );
}

/* ---------- helpers ---------- */

function mean(xs: number[]): number {
  return xs.reduce((s, x) => s + x, 0) / xs.length;
}

function formatScale(m: Metric, max: number): string {
  if (m.unit === "m" && max >= 1000) return `${(max / 1000).toFixed(0)} km`;
  if (m.unit === "%") return `${max}%`;
  return `${max} ${m.unit}`;
}

// Suppressed lint: helper retained if callers need it in future.
export { POSITION_LABEL };
// unused import guard
void isScaled;
