/**
 * ST2 — Athlete page · Summary spine (Workstream 02 · prompt 2).
 *
 * Six metrics, one row each, on a shared fixed axis of 40–160 % of the
 * athlete's own typical for this session's day type. Two groups —
 * External · work above, Internal · cost anchoring the foot. The read
 * is positional: the outlying dot answers "what's off" before any
 * number does. Co-equality across all six is carried by identical
 * costume — same mark size, same track, same axis. Hue carries axis
 * membership only. No severity colour on this page, anywhere.
 *
 * Divergence recorded in the findings file: band = mean ± 1 SD from
 * demo-typicals.ts, NOT the flat ±5 % that Session/Longitudinal draw.
 * On a page whose entire claim is that it reads this athlete against
 * himself, a flat percentage would assert an identical normal range
 * across every athlete and every metric — false, and the opposite of
 * what this surface is for.
 */

import { useMemo } from "react";
import { copy, tmpl } from "@/lib/copy-deck";
import { currentSession } from "@/lib/session-data";
import { demoSessions } from "@/lib/demo-library";
import {
  spineForAthleteSession,
  characterLineFor,
  flaggedMetricFor,
  ATHLETE_SPINE_DOMAIN,
  SPINE_METRICS,
  type SpineRow,
  type SpineMetricId,
  type AthleteSpine,
} from "@/lib/athlete-data";
import { demoAthletes } from "@/lib/demo-library";
import { TIER1_ROWS_DEFAULT } from "@/lib/session-flags";
import { Flag } from "lucide-react";

const PINNED_SESSION_ID = "s-2026-07-04-dortmund";

type Props = {
  athleteId: string;
  sessionId: string;
  flagActive: boolean;
  peerSpine?: AthleteSpine | null;
};

/** The one place the spine is ordered for render. External group first;
 *  within a group, the flagged metric hoists to row one. Salience does
 *  not reorder — only flag does. */
function orderRowsForRender(rows: SpineRow[]): SpineRow[] {
  const byId = new Map(rows.map((r) => [r.metricId, r] as const));
  const groups: SpineMetricId[][] = [
    ["totalDistance", "mMin", "hsr", "accDec"],
    ["cardioLoad", "srpeAU"],
  ];
  const out: SpineRow[] = [];
  for (const g of groups) {
    const list = g.map((id) => byId.get(id)!).filter(Boolean);
    // hoist flagged within its own group
    const flaggedIdx = list.findIndex((r) => r.flagged);
    if (flaggedIdx > 0) {
      const [f] = list.splice(flaggedIdx, 1);
      list.unshift(f);
    }
    out.push(...list);
  }
  return out;
}

export function AthleteSummarySpine({ athleteId, sessionId, flagActive, peerSpine = null }: Props) {
  const activeSession =
    demoSessions.find((s) => s.id === sessionId) ??
    demoSessions.find((s) => s.id === PINNED_SESSION_ID);

  const tier1 = TIER1_ROWS_DEFAULT.find((r) => r.id === athleteId);
  const flaggedMetric = flagActive && tier1 ? flaggedMetricFor(tier1.reason) : null;

  const spine = useMemo(
    () => spineForAthleteSession(athleteId, sessionId, { flaggedMetric }),
    [athleteId, sessionId, flaggedMetric],
  );

  // Peer row lookup — passed to each SpineRowView so the muted dot lands
  // on the same track as the subject's dot (same axis basis: peer's own
  // valuePct against their own typical for this day type).
  const peerByMetric = useMemo(() => {
    const m = new Map<SpineMetricId, SpineRow>();
    if (peerSpine) for (const r of peerSpine.rows) m.set(r.metricId, r);
    return m;
  }, [peerSpine]);
  const peer = peerSpine ? demoAthletes.find((a) => a.id === peerSpine.athleteId) ?? null : null;
  const subject = demoAthletes.find((a) => a.id === athleteId) ?? null;

  const rows = orderRowsForRender(spine.rows);
  const external = rows.filter((r) => r.group === "external");
  const internal = rows.filter((r) => r.group === "internal");

  // Echo the scope-line Reference chip: on a match this reads
  // "their typical match", on other days "their typical MD-N".
  const basisRef = activeSession
    ? activeSession.type === "match"
      ? copy("athlete.summary.basisRefMatch")
      : tmpl("athlete.summary.basisRefDayTemplate", { dayCode: activeSession.dayCode })
    : copy("athlete.summary.basisFallback");
  const basisLine = tmpl("athlete.summary.basisTemplate", { ref: basisRef });

  const characterLine = characterLineFor(spine);

  return (
    <section
      className="rounded-lg border"
      style={{
        backgroundColor: "var(--color-surface-card)",
        borderColor: "var(--color-border)",
      }}
      data-section="athlete-summary"
    >
      {/* Building-baseline strip — prints once, above all rows. */}
      {spine.header.buildingBaseline && (
        <div
          className="border-b px-5 py-2 text-[12px]"
          style={{
            borderColor: "var(--color-border)",
            color: "var(--color-text-secondary)",
            backgroundColor: "var(--color-slate-100)",
          }}
        >
          {copy("athlete.summary.buildingStrip")}
        </div>
      )}

      {/* Basis line — the scale sentence, printed once. */}
      <div
        className="flex items-baseline justify-between border-b px-5 py-2.5"
        style={{ borderColor: "var(--color-border)" }}
      >
        <h3 className="type-section-h" style={{ color: "var(--color-text-primary)" }}>
          {copy("athlete.summary.title")}
        </h3>
        <span
          className="type-data-label text-[11.5px]"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          {basisLine}
        </span>
      </div>

      {/* Peer identity block — session-scope compare. Prints once, above
          the groups, when a peer is selected. */}
      {peer && subject && (
        <div
          className="flex items-center gap-4 border-b px-5 py-2 text-[11.5px]"
          style={{
            borderColor: "var(--color-border)",
            backgroundColor: "var(--color-slate-50)",
          }}
        >
          <span className="flex items-center gap-1.5">
            <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ backgroundColor: "var(--color-text-primary)" }} aria-hidden />
            <span style={{ color: "var(--color-text-primary)" }}>
              {tmpl("athlete.peer.subjectHeadTemplate", { name: subject.name })}
            </span>
          </span>
          <span className="flex items-center gap-1.5">
            <span
              className="inline-block h-2.5 w-2.5 rounded-full"
              style={{ backgroundColor: "var(--color-text-tertiary)", opacity: 0.55 }}
              aria-hidden
            />
            <span style={{ color: "var(--color-text-secondary)" }}>
              {tmpl("athlete.peer.peerHeadTemplate", { name: peer.name })}
            </span>
          </span>
        </div>
      )}

      {/* Groups */}
      <div className="px-5 py-4">
        <GroupBlock label={copy("athlete.summary.groupExternal")} rows={external} firstRowShowsAxis peerByMetric={peerByMetric} />
        <div className="my-3 h-px" style={{ backgroundColor: "var(--color-border)" }} aria-hidden />
        <GroupBlock label={copy("athlete.summary.groupInternal")} rows={internal} peerByMetric={peerByMetric} />
      </div>

      {/* Character line — the only sentence on this page. */}
      <div
        className="border-t px-5 py-3 text-[13px]"
        style={{
          borderColor: "var(--color-border)",
          color: "var(--color-text-primary)",
        }}
      >
        {characterLine}
      </div>
    </section>
  );
}

/* ─────────────────── group ─────────────────── */

function GroupBlock({
  label,
  rows,
  firstRowShowsAxis = false,
  peerByMetric,
}: {
  label: string;
  rows: SpineRow[];
  firstRowShowsAxis?: boolean;
  peerByMetric?: Map<SpineMetricId, SpineRow>;
}) {
  return (
    <div>
      <div
        className="type-microcaps mb-2 text-[10.5px]"
        style={{ color: "var(--color-text-tertiary)" }}
      >
        {label}
      </div>
      <div className="flex flex-col">
        {rows.map((r, idx) => (
          <SpineRowView
            key={r.metricId}
            row={r}
            showAxisLabels={firstRowShowsAxis && idx === 0}
            peerRow={peerByMetric?.get(r.metricId) ?? null}
          />
        ))}
      </div>
    </div>
  );
}

/* ─────────────────── one row ─────────────────── */

const DOMAIN_LO = ATHLETE_SPINE_DOMAIN[0];
const DOMAIN_HI = ATHLETE_SPINE_DOMAIN[1];
const DOMAIN_SPAN = DOMAIN_HI - DOMAIN_LO;

function pctToLeft(pct: number) {
  return ((pct - DOMAIN_LO) / DOMAIN_SPAN) * 100;
}

function axisColor(axis: SpineRow["axis"]) {
  return axis === "work" ? "var(--color-axis-work)" : "var(--color-axis-cost)";
}

function formatValue(v: number, unit: string) {
  if (unit === "m" || unit === "AU" || unit === "CL" || unit === "ct") {
    return Math.round(v).toLocaleString();
  }
  if (unit === "m/min") return Math.round(v).toLocaleString();
  return v.toLocaleString();
}

function SpineRowView({
  row,
  showAxisLabels = false,
  peerRow = null,
}: {
  row: SpineRow;
  showAxisLabels?: boolean;
  peerRow?: SpineRow | null;
}) {
  const color = axisColor(row.axis);

  // Track pieces
  const bandVisible =
    row.state.kind !== "building" &&
    row.state.kind !== "withheld" &&
    row.bandLoPct != null &&
    row.bandHiPct != null;
  const bandLeft = bandVisible ? Math.max(0, pctToLeft(row.bandLoPct!)) : 0;
  const bandRight = bandVisible ? Math.min(100, pctToLeft(row.bandHiPct!)) : 0;

  // Dot
  const dotVisible =
    row.state.kind === "ok" ||
    row.state.kind === "hollow" ||
    row.state.kind === "beyondRange";
  const clampedLeft = (() => {
    if (!dotVisible || row.valuePct == null) return 0;
    if (row.state.kind === "beyondRange") {
      return row.state.side === "high" ? 100 : 0;
    }
    return pctToLeft(row.valuePct);
  })();

  const hollow = row.state.kind === "hollow";

  // Delta ink stays neutral — no severity colour here, ever.
  const deltaInk = "var(--color-text-secondary)";

  // Right-edge value
  const rightSide = (() => {
    if (row.state.kind === "withheld") {
      const reason =
        row.state.reason === "coverage"
          ? copy("athlete.summary.withheld.coverage")
          : row.state.reason === "notSubmitted"
            ? copy("athlete.summary.withheld.notSubmitted")
            : copy("athlete.summary.withheld.notParticipating");
      return (
        <span
          className="type-data-label italic text-[11.5px]"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          {reason}
        </span>
      );
    }
    // Absolute value + delta line
    const abs = row.value == null ? "—" : formatValue(row.value, row.unit);
    return (
      <div className="flex flex-col items-end leading-tight">
        <span className="type-num text-[13px] font-semibold" style={{ color: "var(--color-text-primary)" }}>
          {abs}
          {row.unit && row.value != null ? (
            <span className="type-data-label ml-0.5" style={{ color: "var(--color-text-tertiary)" }}>
              {row.unit}
            </span>
          ) : null}
          {row.state.kind === "hollow" && (
            <span
              className="type-num ml-1.5 text-[11.5px]"
              style={{ color: "var(--color-text-tertiary)" }}
            >
              {tmpl("athlete.summary.covSuffixTemplate", { n: Math.round(row.state.coveragePct) })}
            </span>
          )}
          {row.state.kind === "beyondRange" && (
            /* Beyond-range prints the TRUE percent alongside the absolute,
               in the same primary ink and weight as an ordinary value —
               a mark at 161 % of typical reads `161%`, not `+61%`. */
            <span
              className="type-num ml-1.5 text-[13px] font-semibold"
              style={{ color: "var(--color-text-primary)" }}
              title="beyond drawn range"
            >
              {`${Math.round(row.state.truePct)}%`}
            </span>
          )}
        </span>
        {row.state.kind === "building" ? (
          <span
            className="type-data-label italic text-[11px]"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            {copy("athlete.summary.baselineBuilding")}
          </span>
        ) : row.deltaPct != null && row.state.kind !== "beyondRange" ? (
          <span
            className="type-num text-[11.5px]"
            style={{ color: deltaInk }}
          >
            {`${row.deltaPct >= 0 ? "+" : ""}${row.deltaPct.toFixed(0)}%`}
          </span>
        ) : (
          <span className="text-[11.5px]" style={{ color: "transparent" }}>·</span>
        )}
      </div>
    );
  })();

  return (
    <div className="grid grid-cols-[170px_1fr_128px] items-center gap-4 py-2">
      {/* Metric name + optional flag glyph + optional salience chip */}
      <div className="flex items-center gap-1.5 min-w-0">
        {row.flagged && (
          <Flag
            className="h-3 w-3 shrink-0"
            aria-hidden
            style={{ color: "var(--color-text-secondary)" }}
          />
        )}
        <span
          className="truncate text-[13px]"
          style={{
            color: "var(--color-text-primary)",
            fontWeight: row.flagged ? 500 : 400,
          }}
        >
          {row.label}
        </span>
        {row.salience && (
          <span
            className="type-microcaps ml-1 rounded px-1 py-0.5 text-[9.5px] whitespace-nowrap"
            style={{
              backgroundColor: "var(--color-slate-100)",
              color: "var(--color-text-secondary)",
            }}
          >
            {copy("athlete.summary.salience")}
          </span>
        )}
      </div>

      {/* The track */}
      <div className={showAxisLabels ? "relative h-9 pt-3" : "relative h-6"}>
        {/* base rail */}
        <div
          className="absolute left-0 right-0 top-1/2 h-[6px] -translate-y-1/2 rounded-full"
          style={{ backgroundColor: "var(--color-data-band)" }}
        />
        {/* 40 / 160 tick labels — printed ONCE per section, on the first row. */}
        {showAxisLabels && (
          <>
            <span
              className="type-num absolute -left-0.5 top-0 text-[9.5px]"
              style={{ color: "var(--color-text-tertiary)" }}
              aria-hidden
            >
              {DOMAIN_LO}
            </span>
            <span
              className="type-num absolute -right-0.5 top-0 text-[9.5px]"
              style={{ color: "var(--color-text-tertiary)" }}
              aria-hidden
            >
              {DOMAIN_HI}
            </span>
            {/* `100 — typical` label — printed once for the section, on
                the first row's track. Required by the scale cold-read
                gate: a screen-reader aria-label is not a mark on the
                canvas. */}
            <span
              className="type-num absolute top-0 -translate-x-1/2 whitespace-nowrap text-[9.5px]"
              style={{
                left: `${pctToLeft(100)}%`,
                color: "var(--color-text-tertiary)",
              }}
              aria-hidden
            >
              {copy("athlete.summary.hundred")}
            </span>
          </>
        )}
        {/* band ±1 SD */}
        {bandVisible && (
          <div
            className="absolute top-1/2 h-[10px] -translate-y-1/2 rounded-sm"
            style={{
              left: `${bandLeft}%`,
              width: `${Math.max(0, bandRight - bandLeft)}%`,
              backgroundColor: "var(--color-reference-band)",
            }}
            aria-label="normal range · ±1 SD"
          />
        )}
        {/* 100 line — always present so the gate holds */}
        <div
          className="absolute top-1/2 h-4 w-[2px] -translate-x-1/2 -translate-y-1/2 rounded-sm"
          style={{
            left: `${pctToLeft(100)}%`,
            backgroundColor: "var(--color-data-reference)",
          }}
          aria-label="typical"
        />
        {/* Peer dot — muted, on the same track, drawn beneath the
            subject's mark so the subject stays legible on overlap.
            Same axis basis: peer's own valuePct against their own
            typical for this day type. Withheld/building states skip. */}
        {peerRow && (peerRow.state.kind === "ok" || peerRow.state.kind === "hollow" || peerRow.state.kind === "beyondRange") && (
          <div
            className="absolute top-1/2 h-2.5 w-2.5 -translate-x-1/2 -translate-y-1/2 rounded-full"
            style={{
              left: `${
                peerRow.state.kind === "beyondRange"
                  ? peerRow.state.side === "high" ? 100 : 0
                  : peerRow.valuePct != null ? pctToLeft(peerRow.valuePct) : 0
              }%`,
              backgroundColor: color,
              opacity: 0.42,
            }}
            aria-label="peer, same axis"
          />
        )}
        {/* dot — no halo. The white ring is the two-mark pair's internal
            marker in the product grammar; this page has no such pair. */}
        {dotVisible && (
          <div
            className="absolute top-1/2 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full"
            style={{
              left: `${clampedLeft}%`,
              backgroundColor: hollow ? "transparent" : color,
              border: hollow ? `1.75px solid ${color}` : undefined,
              boxSizing: "border-box",
            }}
            aria-label="this session"
          />
        )}
        {/* caret at edge for beyond-range */}
        {row.state.kind === "beyondRange" && (
          <span
            className="absolute top-1/2 -translate-y-1/2 type-num text-[10px]"
            style={{
              [row.state.side === "high" ? "right" : "left"]: "-8px",
              color: "var(--color-text-secondary)",
            }}
            aria-hidden
          >
            {row.state.side === "high" ? "▸" : "◂"}
          </span>
        )}
      </div>

      {/* Value edge */}
      <div className="flex justify-end">{rightSide}</div>
    </div>
  );
}
