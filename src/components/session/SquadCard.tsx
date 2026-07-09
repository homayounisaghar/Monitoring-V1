/**
 * ST2 — Session > Squad card.
 *
 * Every athlete × the core metrics. The load-bearing rule: DERIVE, do
 * not tabulate. Every delta, every %-mode cell, every sort key, and
 * the squad-avg row are computed live from raw value + raw reference.
 *
 * Two modes:
 *   Table (default): 19 rows including P. Sturm (DNP); neutral cells,
 *     sortable by any column, pinned "Squad avg · N" row.
 *   Chart: single-column ranked list on one metric, ValueOnTrack in
 *     shared-scale mode; partial/building/DNP shown honestly.
 *
 * Cell honesty: Ebel scaled/not-compared, Köhler building baseline,
 * low-coverage Cardio Load with TrustMark veil, Sturm did-not-
 * participate row, non-submitters "—" on sRPE.
 */
import { useMemo, useState } from "react";
import { ChevronRight, Flag, ChevronUp, ChevronDown, X } from "lucide-react";
import { useNavigate } from "@tanstack/react-router";
import { useSessionScope, COVERAGE_MIN } from "@/lib/session-scope";
import { squad, POSITION_LABEL, type Athlete } from "@/lib/session-data";
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
    totalParticipants,
    filter,
    filterIsDefault,
    scopeLabel,
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

  // Table shows all 19 (including Sturm DNP) when no filter; a filter
  // subsets participants (DNP drops from filtered subsets by design).
  const scopedIds = useMemo(
    () => new Set(activeAthletes.map((a) => a.id)),
    [activeAthletes],
  );
  const tableRows: Athlete[] = useMemo(() => {
    if (filterIsDefault) return squad;
    return squad.filter((a) => scopedIds.has(a.id));
  }, [filterIsDefault, scopedIds]);

  /* --- flagged identity set — SAME source as the Attention card --- */

  const lowCovIds = effectiveParticipants
    .filter((a) => a.hrCoveragePct !== null && a.hrCoveragePct < COVERAGE_MIN)
    .map((a) => a.id);
  const flagged = useMemo(
    () => flaggedIds(tier1Rows, lowCovIds),
    [tier1Rows, lowCovIds],
  );

  /* --- sRPE column badge — coverage on the column head (not the toolbar) --- */

  const srpeSubmitted = activeAthletes.filter((a) => a.srpeSubmitted).length;
  const srpeTotal = activeAthletes.length;

  /* --- sort key derives from active display mode --- */

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

  /* --- squad-avg row over IN-SCOPE participants --- */

  const scopeParticipants = activeAthletes; // participants only
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

  /* --- header descriptor --- */

  const descriptorScope = !filterIsDefault && scopeLabel ? scopeLabel : null;

  return (
    <section id="squad" className="scroll-mt-28">
      <header className="mb-3 flex items-baseline justify-between gap-4">
        <div className="flex items-baseline gap-2 flex-wrap">
          <h2 className="type-section-h">Squad</h2>
          <span
            className="type-label"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            — Every athlete on this session · sort, scan, drill
            {descriptorScope ? ` · ${descriptorScope}` : ""}
          </span>
        </div>
        {!filterIsDefault && (
          <span
            className="type-num text-[11px]"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            {activeAthletes.length} of {totalParticipants}
          </span>
        )}
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
          onRowClick={(a) => navigate({ to: "/athlete" })}
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
          rows={activeAthletes}
          nonRankedIds={sturmAndNoDataIds(activeAthletes, METRICS[chartMetric])}
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
            <th className="px-3 py-2 text-left type-col-head" style={{ minWidth: 180 }}>
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
                    minWidth: id === "min" ? 68 : 100,
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
                        className="type-num text-[10px]"
                        style={{ color: "var(--color-text-tertiary)" }}
                        title={`${srpeCoverage.submitted} of ${srpeCoverage.total} submitted`}
                      >
                        · {srpeCoverage.submitted}/{srpeCoverage.total}
                      </span>
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

          {rows.map((a) => (
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
                    <Cell a={a} m={m} display={display} />
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/* ---------- individual cell renderers ---------- */

function Cell({ a, m, display }: { a: Athlete; m: Metric; display: DisplayMode }) {
  const state = cellState(a, m);
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
  if (state === "empty") {
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
    const v = valueFor(a, m);
    return (
      <div className="flex flex-col items-end">
        <span
          className="type-num text-[13px]"
          style={{ color: "var(--color-text-primary)" }}
        >
          {formatValue(v, m)}
        </span>
        <span
          className="type-label"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          · not compared
        </span>
      </div>
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

  const primary = cellIsPercent
    ? `${pct}%`
    : m.id === "min"
      ? `${v}'`
      : formatValue(v, m);

  const scaledTag = isScaled(a, m);
  const primaryInk = lowCov
    ? "var(--color-text-tertiary)"
    : "var(--color-text-primary)";

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
      {m.id !== "min" && deltaPct != null && !cellIsPercent && (
        <span
          className="type-num text-[10.5px]"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          {deltaPct >= 0 ? "+" : ""}
          {deltaPct}%{scaledTag ? " · scaled" : ""}
        </span>
      )}
      {cellIsPercent && scaledTag && (
        <span
          className="type-label"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          · scaled
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
  const suffix = m.unit === "%" ? "%" : m.unit === "/10" ? "" : "";
  const rawDelta =
    ref != null && ref !== 0 ? ((value - ref) / ref) * 100 : null;
  const deltaPct = rawDelta != null && Number.isFinite(rawDelta) ? Math.round(rawDelta) : null;

  return (
    <div className="flex flex-col items-end">
      <span
        className="type-num text-[12px] font-semibold"
        style={{ color: "var(--color-text-secondary)" }}
      >
        {printed}
        {suffix}
      </span>
      {deltaPct != null && (
        <span
          className="type-num text-[10px]"
          style={{ color: "var(--color-text-tertiary)" }}
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
  rows,
  nonRankedIds,
  allSquadForTray,
  flagged,
  onRowClick,
  onScrollToAttention,
}: {
  metric: Metric;
  rows: Athlete[];
  nonRankedIds: Set<string>;
  allSquadForTray: Athlete[];
  flagged: Set<string>;
  onRowClick: (a: Athlete) => void;
  onScrollToAttention: () => void;
}) {
  const ranked = rows
    .filter((a) => a.participation !== null && !nonRankedIds.has(a.id))
    .map((a) => {
      const state = cellState(a, metric);
      const v = valueFor(a, metric);
      const r = refFor(a, metric);
      return { a, v, r, state };
    })
    .sort((x, y) => (y.v ?? -Infinity) - (x.v ?? -Infinity));

  const trayIds = new Set(nonRankedIds);
  // add Sturm and anyone with no data on this metric that isn't already
  const tray = allSquadForTray.filter(
    (a) => trayIds.has(a.id) || (a.participation === null && rows.some((r) => r.id === a.id) === false),
  );
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
          Ranked by {metric.label}
        </span>
        <span
          className="type-label"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          delta vs own typical for this day-type · shared scale 0–{formatScale(metric, scaleMax)}
        </span>
      </div>
      <ul className="max-h-[560px] overflow-y-auto">
        {ranked.map((r, i) => (
          <ChartRow
            key={r.a.id}
            rank={i + 1}
            a={r.a}
            m={metric}
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
  value: number | null;
  ref: number | null;
  state: ReturnType<typeof cellState>;
  scaleMax: number;
  flagged: boolean;
  onClick: () => void;
  onFlagClick: () => void;
}) {
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
          {a.posDetail} · {a.minutes}'
        </div>
      </div>
      <div className="min-w-0 flex-1">
        {state === "building" ? (
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
            <span
              className="w-[140px] text-right type-label italic"
              style={{ color: "var(--color-text-tertiary)" }}
            >
              building baseline
            </span>
          </div>
        ) : state === "not_compared" ? (
          <div className="flex items-center gap-3">
            <div
              className="relative h-5 flex-1 rounded-full"
              style={{ backgroundColor: "var(--color-data-band)" }}
            />
            <span
              className="w-[140px] text-right type-label"
              style={{ color: "var(--color-text-tertiary)" }}
            >
              · not compared
            </span>
          </div>
        ) : value == null || ref == null ? (
          <div
            className="text-[12px]"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            —
          </div>
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
        {isScaled(a, m) && state === "ok" && (
          <div
            className="type-label mt-0.5"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            · scaled to {a.minutes}'
          </div>
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
  const toggle = (id: MetricId) => {
    if (id === "min") return; // identity — always on
    const next = new Set(selected);
    if (next.has(id)) next.delete(id);
    else {
      if (next.size >= MAX_COLUMNS) return;
      next.add(id);
    }
    // preserve library order + always-on identity first
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
              {selected.size} of max {MAX_COLUMNS} · remove one to add another
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
                return (
                  <button
                    key={id}
                    onClick={() => toggle(id)}
                    className={`flex items-center justify-between rounded border px-2 py-1.5 text-left text-[12.5px] transition-colors ${
                      on
                        ? "bg-[color:var(--color-slate-100)]"
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
            Need something that isn't here? The full data is in Export.
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

function sturmAndNoDataIds(rows: Athlete[], m: Metric): Set<string> {
  const set = new Set<string>();
  for (const a of rows) {
    if (a.participation === null) set.add(a.id);
    else if (valueFor(a, m) == null) set.add(a.id);
  }
  return set;
}

// squad exported from session-data (unused typed suppression not needed)
export { POSITION_LABEL };
