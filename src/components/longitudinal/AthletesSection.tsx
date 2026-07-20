/**
 * Longitudinal — Athletes section (Step 5).
 *
 * Three surfaces, in order:
 *   1. Ranked availability list — six rows + one computed remainder line.
 *   2. Window totals — position-grouped table across three views
 *      (ABSOLUTE · VS TYPICAL · A:C), with a foot row for the one
 *      zero-participation athlete.
 *   3. Matrix — NOT built. The expander control is intentionally omitted.
 *
 * No row is clickable and no row shows a hover affordance. This is the last
 * section; there is nothing to drill into.
 *
 * Registers consumed only:
 *   - participation-style   → TAG_STYLE, NOT_IN_SQUAD_STYLE, PARTICIPATION_TAGS
 *   - squad-metrics         → METRICS, MAX_COLUMNS (for the twelve-column cap)
 *   - longitudinal-data     → athleteAvailabilityRanking, windowTotals
 *   - format-date           → dayMonthLong (deterministic, no toLocaleString)
 */
import { useMemo, useState } from "react";
import { Flag, ChevronUp, ChevronDown } from "lucide-react";
import { useNavigate } from "@tanstack/react-router";

import { copy, tmpl } from "@/lib/copy-deck";
import { SegmentedToggle } from "@/components/data/SegmentedToggle";
import {
  PARTICIPATION_TAGS,
  TAG_STYLE,
  NOT_IN_SQUAD_STYLE,
} from "@/lib/participation-style";
import {
  athleteAvailabilityRanking,
  windowTotals,
  athleteDayMatrix,
  type LongiWindow,
  type LongiMetric,
  type AthleteAvailEntry,
  type AthleteTotals,
  type MatrixCellState,
  type MatrixColumn,
} from "@/lib/longitudinal-data";
import type { ParticipationTag, PositionCode } from "@/lib/session-data";
import { POSITION_LABEL } from "@/lib/session-data";
import { MAX_COLUMNS } from "@/lib/squad-metrics";
import { dayMonth, dayMonthLong } from "@/lib/format-date";
import { refLabel, DEFAULT_REF, type RefKind } from "./ScopeLine";

/* ─────────────────────────── shared bits ─────────────────────────── */

const VISIBLE_ROWS = 6;
const POS_ORDER: PositionCode[] = ["GK", "DEF", "MID", "ATT"];

type MetricCol = {
  id: LongiMetric;
  head: string;
  /** Format an absolute value for this metric. */
  fmtAbs: (v: number) => string;
};

/** Column definitions consumed by the table (see spec §2). */
const METRIC_COLS: MetricCol[] = [
  { id: "totalDistance", head: "DISTANCE (km)", fmtAbs: (v) => (v / 1000).toFixed(1) },
  { id: "hsr",           head: "HSR (m)",        fmtAbs: (v) => String(Math.round(v)) },
  { id: "sprintDist",    head: "SPRINT DIST (m)",fmtAbs: (v) => String(Math.round(v)) },
  { id: "accDec",        head: "ACC–DEC (ct)",   fmtAbs: (v) => String(Math.round(v)) },
  { id: "cardioLoad",    head: "CARDIO LOAD (AU)", fmtAbs: (v) => String(Math.round(v)) },
  { id: "srpeAU",        head: "SRPE (AU)",      fmtAbs: (v) => String(Math.round(v)) },
];

function fmt2(v: number): string {
  return v.toFixed(2);
}
function fmtInt(v: number): string {
  return String(Math.round(v));
}
function surname(name: string): string {
  const parts = name.trim().split(/\s+/);
  return parts[parts.length - 1];
}

/* ─────────────────────────── section ─────────────────────────── */

export function AthletesSection({
  window: w,
  refKind,
}: {
  window: LongiWindow;
  refKind: RefKind;
}) {
  const referenceLabel = refLabel(refKind);
  const referenceIsDefault = refKind === DEFAULT_REF;
  return (
    <section id="athletes" className="scroll-mt-28">
      <header className="mb-4 flex items-baseline gap-2 flex-wrap">
        <h2
          className="type-section-h"
          style={{ color: "var(--color-text-primary)" }}
        >
          {copy("longi.anchor.athletes")}
        </h2>
        <span
          className="type-label"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          {copy("longi.athletes.subtitle")}
        </span>
      </header>

      <div className="space-y-8">
        <AvailabilityList window={w} />
        <WindowTotalsTable
          window={w}
          referenceLabel={referenceLabel}
          referenceIsDefault={referenceIsDefault}
        />
        <SessionByMatrix window={w} />
      </div>
    </section>
  );
}

/* ─────────────────────────── 1 · ranked availability list ─────────────────────────── */

function AvailabilityList({ window: w }: { window: LongiWindow }) {
  const rows = useMemo(() => athleteAvailabilityRanking(w), [w]);
  const [expanded, setExpanded] = useState(false);

  // Denominator for bar widths — the widest available-sessions across the
  // whole roster, so a mid-window joiner's bar is visibly shorter.
  const maxAvailable = useMemo(
    () => rows.reduce((m, r) => Math.max(m, r.availableSessions), 0),
    [rows],
  );

  const visible = expanded ? rows : rows.slice(0, VISIBLE_ROWS);
  const hidden = expanded ? [] : rows.slice(VISIBLE_ROWS);
  const hiddenCount = hidden.length;
  const maxMissedInHidden = hidden.reduce(
    (m, r) => Math.max(m, r.availableSessions - Math.round(r.fullFraction * r.availableSessions)),
    0,
  );
  // Recompute Full count exactly (fullFraction × available rounds cleanly here).
  const hiddenMaxMissed = hidden.reduce((m, r) => {
    const full = Math.round(r.fullFraction * r.availableSessions);
    return Math.max(m, r.availableSessions - full);
  }, 0);

  return (
    <div
      className="surface-card rounded-lg"
      style={{
        backgroundColor: "var(--color-surface-card)",
        border: "1px solid var(--color-border)",
      }}
    >
      <ul className="divide-y" style={{ borderColor: "var(--color-border)" }}>
        {visible.map((r) => (
          <li key={r.athlete.id}>
            <AvailabilityRow row={r} maxAvailable={maxAvailable} />
          </li>
        ))}
      </ul>

      {hiddenCount > 0 && (
        <button
          type="button"
          onClick={() => setExpanded(true)}
          className="w-full border-t px-4 py-2.5 text-left text-[12.5px]"
          style={{
            borderColor: "var(--color-border)",
            color: "var(--color-text-tertiary)",
            backgroundColor: "var(--color-slate-50)",
          }}
        >
          {hiddenMaxMissed === 0 && maxMissedInHidden === 0
            ? tmpl("longi.athletes.moreNone", { n: hiddenCount })
            : tmpl("longi.athletes.more", { n: hiddenCount, max: hiddenMaxMissed })}
        </button>
      )}
    </div>
  );
}

function AvailabilityRow({
  row,
  maxAvailable,
}: {
  row: AthleteAvailEntry;
  maxAvailable: number;
}) {
  const { athlete, tagCounts, availableSessions, fullFraction, attentionFlagged } = row;
  const fullCount = Math.round(fullFraction * availableSessions);
  const barWidth = maxAvailable > 0 ? (availableSessions / maxAvailable) * 100 : 0;

  // Segments in fixed order; then a hairline leftover (unselected within his
  // own available window) so the bar denominator = availableSessions.
  const segs: { key: ParticipationTag; count: number }[] = [];
  let tagged = 0;
  for (const t of PARTICIPATION_TAGS) {
    const c = tagCounts[t] ?? 0;
    if (c > 0) segs.push({ key: t, count: c });
    tagged += c;
  }
  const leftover = Math.max(0, availableSessions - tagged);

  return (
    <div className="group grid grid-cols-[220px_1fr_88px_88px] items-center gap-4 px-4 py-3">
      {/* Name + position + optional neutral flag glyph. */}
      <div className="flex items-center gap-2 min-w-0">
        {attentionFlagged && (
          <Flag
            className="h-3.5 w-3.5 shrink-0"
            style={{ color: "var(--color-text-tertiary)" }}
            aria-label="flagged"
          />
        )}
        <span
          className="truncate text-[13px]"
          style={{ color: "var(--color-text-primary)" }}
        >
          {athlete.name}
        </span>
        <span
          className="type-microcaps shrink-0"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          {athlete.posDetail}
        </span>
      </div>

      {/* Stacked participation bar, width scaled to available sessions. */}
      <div className="relative h-4">
        <div
          className="absolute left-0 top-0 flex h-full overflow-hidden rounded-sm"
          style={{
            width: `${barWidth}%`,
            border: "1px solid var(--color-border)",
          }}
        >
          {segs.map((seg, i) => {
            const wPct = availableSessions > 0 ? (seg.count / availableSessions) * 100 : 0;
            const isLast = i === segs.length - 1 && leftover === 0;
            return (
              <div
                key={seg.key}
                style={{
                  ...TAG_STYLE[seg.key],
                  width: `${wPct}%`,
                  borderRight: isLast ? undefined : "1px solid var(--color-border)",
                }}
                aria-label={`${seg.key}: ${seg.count}`}
              />
            );
          })}
          {leftover > 0 && (
            <div
              style={{
                ...NOT_IN_SQUAD_STYLE,
                border: "none",
                width: `${(leftover / availableSessions) * 100}%`,
              }}
              aria-label={`unselected: ${leftover}`}
            />
          )}
        </div>
      </div>

      {/* Fraction — the only count on the row. */}
      <div
        className="text-right type-num text-[13px]"
        style={{ color: "var(--color-text-primary)" }}
      >
        {tmpl("longi.athletes.fraction", { n: fullCount, m: availableSessions })}
      </div>

      {/* Drill affordance — hover-only. Click intentionally unwired: the
          destination athlete page is not built, and cross-page navigation
          into an unbuilt page is worse than none. */}
      <DrillAffordance />
    </div>
  );
}

function DrillAffordance() {
  return (
    <button
      type="button"
      tabIndex={-1}
      aria-hidden
      className="text-right text-[11.5px] opacity-0 transition-opacity group-hover:opacity-100"
      style={{ color: "var(--color-text-tertiary)" }}
    >
      {copy("longi.athletes.drill")}
    </button>
  );
}

/* ─────────────────────────── 2 · window totals table ─────────────────────────── */

type View = "absolute" | "typical" | "ac";
type SortDir = "asc" | "desc";
type SortKey = "sessions" | "minutes" | LongiMetric;
type SortState = { key: SortKey; dir: SortDir } | null;

function WindowTotalsTable({
  window: w,
  referenceLabel,
  referenceIsDefault,
}: {
  window: LongiWindow;
  referenceLabel: string;
  referenceIsDefault: boolean;
}) {
  const [view, setView] = useState<View>("absolute");
  const [sort, setSort] = useState<SortState>(null);

  const totals = useMemo(() => windowTotals(w), [w]);

  // Position-first grouping across position-order.
  const grouped = useMemo(() => {
    const buckets = new Map<PositionCode, AthleteTotals[]>();
    for (const p of POS_ORDER) buckets.set(p, []);
    for (const t of totals.perAthlete) {
      const arr = buckets.get(t.athlete.position);
      if (arr) arr.push(t);
    }
    // Within each group, apply sort. Rows lacking a comparable value pin
    // to the group foot in name order.
    for (const [pos, arr] of buckets) {
      arr.sort((a, b) => rowCompare(a, b, view, sort));
      buckets.set(pos, arr);
    }
    return buckets;
  }, [totals, view, sort]);

  // Column cap: SESSIONS + MINUTES + 6 metric columns = 8 ≤ 12. Assert.
  const columnCount = (view === "absolute" ? 2 : 0) + METRIC_COLS.length;
  if (columnCount > MAX_COLUMNS) {
    throw new Error(`Window totals exceeds ${MAX_COLUMNS}-column cap`);
  }

  return (
    <div>
      {/* Title + view toggle. */}
      <header className="mb-2 flex items-baseline justify-between gap-3">
        <h3
          className="type-section-h text-[15px]"
          style={{ color: "var(--color-text-primary)" }}
        >
          {copy("longi.wt.title")}
        </h3>
        <SegmentedToggle
          value={view}
          onChange={(v) => {
            setView(v);
            setSort(null);
          }}
          options={[
            { id: "absolute", label: copy("longi.wt.view.absolute") },
            { id: "typical",  label: copy("longi.wt.view.typical") },
            { id: "ac",       label: copy("longi.wt.view.ac") },
          ]}
        />
      </header>

      {/* Basis / method line — VS TYPICAL and A:C only. */}
      {view === "typical" && (
        <div
          className={"mb-2 text-[11.5px] " + (referenceIsDefault ? "" : "chip-changed inline-block px-2 py-0.5 rounded")}
          style={referenceIsDefault ? { color: "var(--color-text-tertiary)" } : undefined}
        >
          {tmpl("longi.basis.tickTable", { label: referenceLabel })}
        </div>
      )}
      {view === "ac" && (
        <div
          className="mb-2 text-[11.5px]"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          {copy("longi.ac.method")}
        </div>
      )}

      <div
        className="surface-card overflow-x-auto rounded-lg"
        style={{
          backgroundColor: "var(--color-surface-card)",
          border: "1px solid var(--color-border)",
        }}
      >
        <table className="w-full border-collapse text-[12.5px]">
          <thead>
            <tr
              style={{
                backgroundColor: "var(--color-slate-50)",
                borderBottom: "1px solid var(--color-border)",
              }}
            >
              <th
                className="px-3 py-2 text-left"
                style={{ minWidth: 200 }}
              >
                <span className="type-col-head" style={{ color: "var(--color-text-secondary)" }}>
                  ATHLETE
                </span>
              </th>
              {view === "absolute" && (
                <>
                  <SortableHead
                    label={copy("longi.wt.head.sessions")}
                    active={sort?.key === "sessions"}
                    dir={sort?.key === "sessions" ? sort.dir : null}
                    onClick={() => setSort(cycleSort(sort, "sessions"))}
                  />
                  <SortableHead
                    label={copy("longi.wt.head.minutes")}
                    active={sort?.key === "minutes"}
                    dir={sort?.key === "minutes" ? sort.dir : null}
                    onClick={() => setSort(cycleSort(sort, "minutes"))}
                  />
                </>
              )}
              {METRIC_COLS.map((c) => (
                <SortableHead
                  key={c.id}
                  label={c.head}
                  active={sort?.key === c.id}
                  dir={sort?.key === c.id ? sort.dir : null}
                  onClick={() => setSort(cycleSort(sort, c.id))}
                />
              ))}
            </tr>
          </thead>

          <tbody>
            {POS_ORDER.map((pos) => {
              const arr = grouped.get(pos) ?? [];
              if (arr.length === 0) return null;
              return (
                <PositionGroup
                  key={pos}
                  pos={pos}
                  rows={arr}
                  view={view}
                  colCount={columnCount + 1 /* athlete col */}
                />
              );
            })}

            {/* Squad average row — computed across participants under the active view. */}
            <SquadAverageRow
              rows={totals.perAthlete}
              view={view}
            />

            {/* Foot row — the window's zero-participation athlete(s). */}
            {totals.zeroParticipation.map((z) => (
              <tr
                key={z.athlete.id}
                style={{ borderTop: "1px solid var(--color-border)" }}
              >
                <td className="px-3 py-2">
                  <span
                    className="text-[13px]"
                    style={{ color: "var(--color-text-primary)" }}
                  >
                    {z.athlete.name}
                  </span>{" "}
                  <span
                    className="type-microcaps"
                    style={{ color: "var(--color-text-tertiary)" }}
                  >
                    {z.athlete.posDetail}
                  </span>
                </td>
                <td
                  className="px-3 py-2 text-[12px]"
                  style={{ color: "var(--color-text-tertiary)" }}
                  colSpan={columnCount}
                >
                  {copy("longi.wt.footRow")}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Footnote — em-dash meaning. */}
      <div
        className="mt-2 text-[11.5px]"
        style={{ color: "var(--color-text-tertiary)" }}
      >
        {copy("longi.wt.footnote")}
      </div>
    </div>
  );
}

/* ─────────────────────────── position group + rows ─────────────────────────── */

function PositionGroup({
  pos,
  rows,
  view,
  colCount,
}: {
  pos: PositionCode;
  rows: AthleteTotals[];
  view: View;
  colCount: number;
}) {
  return (
    <>
      <tr
        style={{
          backgroundColor: "var(--color-slate-50)",
          borderTop: "1px solid var(--color-border)",
        }}
      >
        <td
          className="px-3 py-1.5 type-microcaps"
          style={{ color: "var(--color-text-tertiary)" }}
          colSpan={colCount}
        >
          {POSITION_LABEL[pos]}
        </td>
      </tr>
      {rows.map((r) => (
        <TotalsRow key={r.athlete.id} row={r} view={view} />
      ))}
    </>
  );
}

function TotalsRow({ row, view }: { row: AthleteTotals; view: View }) {
  return (
    <tr className="group" style={{ borderTop: "1px solid var(--color-border)" }}>
      <td className="px-3 py-2 whitespace-nowrap">
        <div className="flex items-center justify-between gap-3">
          <span>
            <span
              className="text-[13px]"
              style={{ color: "var(--color-text-primary)" }}
            >
              {row.athlete.name}
            </span>{" "}
            <span
              className="type-microcaps"
              style={{ color: "var(--color-text-tertiary)" }}
            >
              {row.athlete.posDetail}
            </span>
          </span>
          {/* Drill affordance — hover-only, click intentionally unwired. */}
          <span
            aria-hidden
            className="text-[11.5px] opacity-0 transition-opacity group-hover:opacity-100"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            {copy("longi.athletes.drill")}
          </span>
        </div>
      </td>


      {view === "absolute" && (
        <>
          <NumericCell text={fmtInt(row.sessionsParticipated)} />
          <NumericCell text={fmtInt(row.minutes)} />
          {METRIC_COLS.map((c) => {
            const v = row.absolute[c.id];
            const hrShare = row.hrCoverageShareByMetric[c.id];
            const coveragePartial =
              c.id === "cardioLoad" && hrShare != null && hrShare < 0.8;
            return (
              <NumericCell
                key={c.id}
                text={v == null || v === 0 ? "—" : c.fmtAbs(v)}
                sub={
                  coveragePartial
                    ? tmpl("longi.days.cov", { pct: Math.round((hrShare as number) * 100) })
                    : undefined
                }
              />
            );
          })}
        </>
      )}

      {view === "typical" && (
        <TypicalRowCells row={row} />
      )}

      {view === "ac" && (
        <AcRowCells row={row} />
      )}
    </tr>
  );
}

function TypicalRowCells({ row }: { row: AthleteTotals }) {
  if (row.vsTypical.state === "withheld") {
    const n = row.vsTypical.largestBucketSampleCount;
    const hover = tmpl("longi.wt.hover.baseline", {
      date: dayMonthLong(row.athlete.joinedISO),
      n,
    });
    return (
      <td
        className="px-3 py-2 text-[12px]"
        style={{ color: "var(--color-text-tertiary)" }}
        colSpan={METRIC_COLS.length}
        title={hover}
      >
        {tmpl("longi.wt.withheld.sessions", { n })}
      </td>
    );
  }
  const pct = row.vsTypical.perMetricPct;
  return (
    <>
      {METRIC_COLS.map((c) => {
        const v = pct[c.id];
        return (
          <NumericCell
            key={c.id}
            text={v == null ? "—" : fmtInt(v)}
          />
        );
      })}
    </>
  );
}

function AcRowCells({ row }: { row: AthleteTotals }) {
  if (row.ac.state === "withheld") {
    const n = row.ac.daysOfData;
    const hover = tmpl("longi.wt.hover.ac", {
      date: dayMonthLong(row.athlete.joinedISO),
      n,
    });
    return (
      <td
        className="px-3 py-2 text-[12px]"
        style={{ color: "var(--color-text-tertiary)" }}
        colSpan={METRIC_COLS.length}
        title={hover}
      >
        {tmpl("longi.wt.withheld.ac", { n })}
      </td>
    );
  }
  const per = row.ac.perMetric;
  return (
    <>
      {METRIC_COLS.map((c) => {
        const v = per[c.id];
        return (
          <NumericCell
            key={c.id}
            // A:C carries bare numbers and nothing else.
            text={v == null ? "—" : fmt2(v)}
          />
        );
      })}
    </>
  );
}

function NumericCell({ text, sub }: { text: string; sub?: string }) {
  return (
    <td
      className="px-3 py-2 text-right type-num whitespace-nowrap"
      style={{ color: "var(--color-text-primary)" }}
    >
      {text}
      {sub && (
        <span
          className="ml-1 text-[10.5px]"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          {sub}
        </span>
      )}
    </td>
  );
}

/* ─────────────────────────── squad average row ─────────────────────────── */

function SquadAverageRow({
  rows,
  view,
}: {
  rows: AthleteTotals[];
  view: View;
}) {
  // Participants = those with sessions > 0.
  const participants = rows;
  const n = participants.length;

  const avg = (nums: number[]): number | null =>
    nums.length === 0 ? null : nums.reduce((a, b) => a + b, 0) / nums.length;

  return (
    <tr
      style={{
        backgroundColor: "var(--color-slate-50)",
        borderTop: "1px solid var(--color-border)",
      }}
    >
      <td className="px-3 py-2">
        <span
          className="text-[12.5px]"
          style={{ color: "var(--color-text-secondary)" }}
        >
          {tmpl("longi.wt.squadAvg", { n })}
        </span>
      </td>

      {view === "absolute" && (
        <>
          <NumericCell text={fmtInt(avg(participants.map((r) => r.sessionsParticipated)) ?? 0)} />
          <NumericCell text={fmtInt(avg(participants.map((r) => r.minutes)) ?? 0)} />
          {METRIC_COLS.map((c) => {
            const nums = participants
              .map((r) => r.absolute[c.id])
              .filter((x): x is number => x != null && x > 0);
            const v = avg(nums);
            return (
              <NumericCell key={c.id} text={v == null ? "—" : c.fmtAbs(v)} />
            );
          })}
        </>
      )}

      {view === "typical" && (
        <>
          {METRIC_COLS.map((c) => {
            const nums: number[] = [];
            for (const r of participants) {
              if (r.vsTypical.state !== "computed") continue;
              const v = r.vsTypical.perMetricPct[c.id];
              if (v != null) nums.push(v);
            }
            const v = avg(nums);
            return (
              <NumericCell key={c.id} text={v == null ? "—" : fmtInt(v)} />
            );
          })}
        </>
      )}

      {view === "ac" && (
        <>
          {METRIC_COLS.map((c) => {
            const nums: number[] = [];
            for (const r of participants) {
              if (r.ac.state !== "computed") continue;
              const v = r.ac.perMetric[c.id];
              if (v != null) nums.push(v);
            }
            const v = avg(nums);
            return (
              <NumericCell key={c.id} text={v == null ? "—" : fmt2(v)} />
            );
          })}
        </>
      )}
    </tr>
  );
}

/* ─────────────────────────── sort helpers ─────────────────────────── */

function cycleSort(prev: SortState, key: SortKey): SortState {
  if (!prev || prev.key !== key) return { key, dir: "desc" };
  return { key, dir: prev.dir === "desc" ? "asc" : "desc" };
}

function rowSortValue(r: AthleteTotals, view: View, key: SortKey): number | null {
  if (key === "sessions") return r.sessionsParticipated;
  if (key === "minutes") return r.minutes;
  const metric = key as LongiMetric;
  if (view === "absolute") return r.absolute[metric] ?? null;
  if (view === "typical") {
    if (r.vsTypical.state !== "computed") return null;
    return r.vsTypical.perMetricPct[metric] ?? null;
  }
  if (r.ac.state !== "computed") return null;
  return r.ac.perMetric[metric] ?? null;
}

function rowCompare(
  a: AthleteTotals,
  b: AthleteTotals,
  view: View,
  sort: SortState,
): number {
  if (!sort) return a.athlete.name.localeCompare(b.athlete.name);
  const av = rowSortValue(a, view, sort.key);
  const bv = rowSortValue(b, view, sort.key);
  const aHas = av != null;
  const bHas = bv != null;
  if (aHas !== bHas) return aHas ? -1 : 1;
  if (!aHas) return surname(a.athlete.name).localeCompare(surname(b.athlete.name));
  const cmp = (av as number) - (bv as number);
  if (cmp === 0) return surname(a.athlete.name).localeCompare(surname(b.athlete.name));
  return sort.dir === "desc" ? -cmp : cmp;
}

function SortableHead({
  label,
  active,
  dir,
  onClick,
}: {
  label: string;
  active: boolean;
  dir: SortDir | null;
  onClick: () => void;
}) {
  return (
    <th
      className="px-3 py-2 text-right"
      style={{
        backgroundColor: active ? "var(--color-slate-100)" : undefined,
      }}
    >
      <button
        type="button"
        onClick={onClick}
        className="ml-auto inline-flex items-center gap-1.5"
      >
        <span
          className="type-col-head"
          style={{
            color: active
              ? "var(--color-text-primary)"
              : "var(--color-text-secondary)",
          }}
        >
          {label}
        </span>
        {active ? (
          dir === "asc" ? (
            <ChevronUp className="h-3 w-3" />
          ) : (
            <ChevronDown className="h-3 w-3" />
          )
        ) : (
          <span className="w-3" />
        )}
      </button>
    </th>
  );
}

/* ─────────────────────────── 3 · session-by-session matrix ─────────────────────────── */

const MATRIX_CELL_W = 22;
const MATRIX_CELL_H = 20;
const MATRIX_NAME_W = 168;

type HoverCell = { row: string; col: number; slot: number };

function SessionByMatrix({ window: w }: { window: LongiWindow }) {
  const [open, setOpen] = useState(false);
  const [hover, setHover] = useState<HoverCell | null>(null);
  const matrix = useMemo(() => athleteDayMatrix(w), [w]);

  // Group rows position-first for the muted subheaders.
  const grouped = useMemo(() => {
    const byPos = new Map<PositionCode, typeof matrix.rows>();
    for (const p of POS_ORDER) byPos.set(p, []);
    for (const r of matrix.rows) byPos.get(r.athlete.position)?.push(r);
    return byPos;
  }, [matrix]);

  const gridW = MATRIX_NAME_W + matrix.columns.length * MATRIX_CELL_W;

  const identityText = useMemo(() => {
    if (!hover) return "";
    const row = matrix.rows.find((r) => r.athlete.id === hover.row);
    const col = matrix.columns[hover.col];
    if (!row || !col) return "";
    const cell = row.cells[hover.col]?.[hover.slot];
    if (!cell) return "";
    const stateLabel = cellStateLabel(cell);
    return tmpl("longi.matrix.identityTemplate", {
      athlete: row.athlete.name,
      date: dayMonthLong(col.dateISO),
      state: stateLabel,
    });
  }, [hover, matrix]);

  return (
    <div>
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        className="inline-flex items-center gap-1 rounded px-2 py-1 text-[12.5px] transition-colors hover:bg-[color:var(--color-slate-100)]"
        style={{ color: "var(--color-text-secondary)" }}
      >
        {open ? "Session by session ⌃" : copy("longi.athletes.expander")}
      </button>

      {open && (
        <div
          className="mt-3 surface-card overflow-x-auto rounded-lg"
          style={{
            backgroundColor: "var(--color-surface-card)",
            border: "1px solid var(--color-border)",
          }}
          onMouseLeave={() => setHover(null)}
        >
          {/* Reserved identity slot — always present so the grid doesn't shift. */}
          <div
            className="flex items-center px-3"
            style={{
              height: 28,
              borderBottom: "1px solid var(--color-border)",
              backgroundColor: "var(--color-slate-50)",
              color: "var(--color-text-secondary)",
              fontSize: 12,
            }}
          >
            <span className="type-num" style={{ minHeight: 14 }}>
              {identityText || "\u00A0"}
            </span>
          </div>

          <div style={{ minWidth: gridW }}>
            {/* Column axis — Monday dates row, then day codes row. */}
            <MatrixDateAxis
              columns={matrix.columns}
              hoverCol={hover?.col ?? null}
            />
            <MatrixCodeAxis
              columns={matrix.columns}
              hoverCol={hover?.col ?? null}
            />

            {/* Rows — position groups. */}
            {POS_ORDER.map((pos) => {
              const rows = grouped.get(pos) ?? [];
              if (rows.length === 0) return null;
              return (
                <div key={pos}>
                  <div
                    className="type-microcaps px-3 py-1"
                    style={{
                      color: "var(--color-text-tertiary)",
                      backgroundColor: "var(--color-slate-50)",
                      borderTop: "1px solid var(--color-border)",
                      borderBottom: "1px solid var(--color-border)",
                    }}
                  >
                    {POSITION_LABEL[pos]}
                  </div>
                  {rows.map((r) => (
                    <MatrixRowView
                      key={r.athlete.id}
                      athleteId={r.athlete.id}
                      name={r.athlete.name}
                      posDetail={r.athlete.posDetail}
                      cells={r.cells}
                      columns={matrix.columns}
                      hover={hover}
                      setHover={setHover}
                    />
                  ))}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

function MatrixDateAxis({
  columns,
  hoverCol,
}: {
  columns: MatrixColumn[];
  hoverCol: number | null;
}) {
  return (
    <div
      className="flex"
      style={{ height: 18, borderBottom: "1px solid var(--color-border)" }}
    >
      <div style={{ width: MATRIX_NAME_W }} />
      {columns.map((c, i) => (
        <div
          key={c.dateISO}
          className="type-num relative"
          style={{
            width: MATRIX_CELL_W,
            fontSize: 10,
            color: "var(--color-text-tertiary)",
            backgroundColor: hoverCol === i ? "var(--color-slate-100)" : "transparent",
          }}
        >
          {c.isMondayLabel && (
            <span
              style={{
                position: "absolute",
                left: 2,
                top: 2,
                whiteSpace: "nowrap",
              }}
            >
              {dayMonth(c.dateISO)}
            </span>
          )}
        </div>
      ))}
    </div>
  );
}

function MatrixCodeAxis({
  columns,
  hoverCol,
}: {
  columns: MatrixColumn[];
  hoverCol: number | null;
}) {
  return (
    <div
      className="flex"
      style={{ height: 16, borderBottom: "1px solid var(--color-border)" }}
    >
      <div style={{ width: MATRIX_NAME_W }} />
      {columns.map((c, i) => (
        <div
          key={c.dateISO}
          className="type-microcaps grid place-items-center"
          style={{
            width: MATRIX_CELL_W,
            fontSize: 9,
            color: c.isMatchDay
              ? "var(--color-text-primary)"
              : "var(--color-text-tertiary)",
            backgroundColor: hoverCol === i ? "var(--color-slate-100)" : "transparent",
          }}
        >
          {c.isMatchDay ? "MD" : ""}
        </div>
      ))}
    </div>
  );
}

function MatrixRowView({
  athleteId,
  name,
  posDetail,
  cells,
  columns,
  hover,
  setHover,
}: {
  athleteId: string;
  name: string;
  posDetail: string;
  cells: MatrixCellState[][];
  columns: MatrixColumn[];
  hover: HoverCell | null;
  setHover: (h: HoverCell | null) => void;
}) {
  const rowHovered = hover?.row === athleteId;
  return (
    <div
      className="flex"
      style={{
        height: MATRIX_CELL_H,
        borderTop: "1px solid var(--color-border)",
        backgroundColor: rowHovered ? "var(--color-slate-50)" : "transparent",
      }}
    >
      <div
        className="flex items-center gap-1.5 px-3"
        style={{ width: MATRIX_NAME_W }}
      >
        <span
          className="truncate text-[11.5px]"
          style={{ color: "var(--color-text-primary)" }}
        >
          {name}
        </span>
        <span
          className="type-microcaps shrink-0"
          style={{ color: "var(--color-text-tertiary)", fontSize: 9 }}
        >
          {posDetail}
        </span>
      </div>
      {columns.map((col, i) => {
        const slots = cells[i];
        const colHovered = hover?.col === i;
        return (
          <div
            key={col.dateISO}
            style={{
              width: MATRIX_CELL_W,
              height: MATRIX_CELL_H,
              backgroundColor: colHovered ? "var(--color-slate-100)" : "transparent",
              padding: 2,
            }}
          >
            <MatrixCell
              slots={slots}
              onHoverSlot={(slot) =>
                setHover({ row: athleteId, col: i, slot })
              }
              onLeave={() => {
                // Row-mouseleave clears; individual slot leave is a no-op so
                // hover persists across a row scan.
              }}
            />
          </div>
        );
      })}
    </div>
  );
}

function MatrixCell({
  slots,
  onHoverSlot,
  onLeave,
}: {
  slots: MatrixCellState[];
  onHoverSlot: (slot: number) => void;
  onLeave: () => void;
}) {
  // slots is length 1 for outside/rest/missing/single-session, or 2 for double.
  return (
    <div
      className="flex h-full w-full flex-col overflow-hidden rounded-[2px]"
      onMouseLeave={onLeave}
    >
      {slots.map((s, idx) => (
        <div
          key={idx}
          onMouseEnter={() => onHoverSlot(idx)}
          style={{
            flex: 1,
            minHeight: 0,
            ...cellStyle(s),
          }}
        />
      ))}
    </div>
  );
}

function cellStyle(s: MatrixCellState): React.CSSProperties {
  switch (s.kind) {
    case "tag":
      return TAG_STYLE[s.tag];
    case "unselected":
      // Hairline no-fill costume — in-squad, not picked.
      return {
        backgroundColor: "transparent",
        border: "1px solid var(--color-border)",
      };
    case "outside":
      // Our absence of a claim — faint neutral wash, no border.
      // Visibly distinct from unselected (hairline box) and rest (blank).
      return { backgroundColor: "var(--color-slate-100)" };
    case "rest":
      // Real zero — empty ground across the row.
      return { backgroundColor: "transparent" };
    case "missing":
      // Dashed void — unknown, visibly distinct from rest.
      return {
        backgroundColor: "transparent",
        backgroundImage:
          "repeating-linear-gradient(45deg, var(--color-border) 0 2px, transparent 2px 5px)",
      };
  }
}

function cellStateLabel(s: MatrixCellState): string {
  switch (s.kind) {
    case "tag":
      return s.tag;
    case "unselected":
      return copy("longi.matrix.state.unselected");
    case "outside":
      return copy("longi.matrix.state.outside");
    case "rest":
      return copy("longi.matrix.state.rest");
    case "missing":
      return copy("longi.matrix.state.missing");
  }
}
