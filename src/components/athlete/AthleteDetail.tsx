/**
 * ST2 — Athlete page · Detail section (Workstream 02 · prompt 5).
 *
 * A curated metric table. One row per metric, THIS SESSION and
 * VS THEIR TYPICAL columns. The curated set is the six governed
 * spine metrics (totalDistance, m/min, HSR, Acc–Dec, Cardio Load,
 * sRPE-AU) — every one has a demo typical and travels with all four
 * honest states already computed by `spineForAthleteSession`. Reusing
 * the spine's derivation is the whole point: the table cannot drift
 * from the marks above it.
 *
 * Data gate dispositions (see findings 2026-07-20):
 *   - built:   metric rows · absolute + vs-typical delta
 *   - built:   `not submitted` in words wherever sRPE is absent
 *   - built:   `· NN% cov` beside the value on hollow-coverage rows.
 *              No ring glyph — the ring is reserved for the Spatial
 *              trace's final whistle; three places on this page could
 *              otherwise collide with the spine's hollow costume.
 *   - built:   inert columns picker (curated set, up to 12)
 *   - omitted: vs a typical full match — SUM-5's promoted/collapsed
 *              render condition is a second form, not a conditional;
 *              logged and not built (demo default is a match).
 *   - omitted: Z1–Z5 distribution — DemoRecord carries no per-athlete
 *              zone shares; deriving from a session total would assert
 *              a distribution the data does not carry.
 *   - omitted: Wellness (sleep/soreness/mood) — not present in the
 *              record. Its absence is honest; it is an optional read.
 *
 * The section renders only when at least one row is available; the
 * anchor strip is trimmed if it does not (see `athlete.tsx`).
 */

import { useState } from "react";
import { copy, tmpl } from "@/lib/copy-deck";
import { spineForAthleteSession, type SpineRow } from "@/lib/athlete-data";

type Props = {
  athleteId: string;
  sessionId: string;
  flaggedMetric?: import("@/lib/athlete-data").SpineMetricId | null;
};

export function AthleteDetail({ athleteId, sessionId, flaggedMetric = null }: Props) {
  const spine = spineForAthleteSession(athleteId, sessionId, { flaggedMetric });
  const rows = spine.rows;

  return (
    <section
      className="rounded-lg border"
      style={{
        backgroundColor: "var(--color-surface-card)",
        borderColor: "var(--color-border)",
      }}
      data-section="athlete-detail"
    >
      <div
        className="flex items-center justify-between border-b px-5 py-2.5"
        style={{ borderColor: "var(--color-border)" }}
      >
        <h2
          className="type-section-h"
          style={{ color: "var(--color-text-primary)" }}
        >
          {copy("athlete.detail.title")}
        </h2>
        <ColumnsButton />
      </div>

      <div className="px-5 pb-4 pt-3">
        <table className="w-full border-collapse text-[12.5px]">
          <thead>
            <tr
              className="type-microcaps text-[10.5px]"
              style={{ color: "var(--color-text-tertiary)" }}
            >
              <th className="py-1.5 pr-4 text-left font-normal">
                {copy("athlete.detail.colMetric")}
              </th>
              <th className="py-1.5 pr-4 text-right font-normal">
                {copy("athlete.detail.colThisSession")}
              </th>
              <th className="py-1.5 text-right font-normal">
                {copy("athlete.detail.colVsTypical")}
              </th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <DetailRow key={r.metricId} row={r} />
            ))}
          </tbody>
        </table>

        <p
          className="mt-3 border-t pt-2 text-[11.5px]"
          style={{
            borderColor: "var(--color-border)",
            color: "var(--color-text-tertiary)",
          }}
        >
          {copy("athlete.detail.footnote")}
        </p>
      </div>
    </section>
  );
}

/* ─────────────────── row ─────────────────── */

function DetailRow({ row }: { row: SpineRow }) {
  const flaggedTint = row.flagged
    ? "var(--color-slate-50)"
    : "transparent";
  return (
    <tr
      className="border-t"
      style={{
        borderColor: "var(--color-border)",
        backgroundColor: flaggedTint,
      }}
    >
      <td
        className="py-2 pr-4 text-left"
        style={{ color: "var(--color-text-primary)" }}
      >
        {row.label}
      </td>
      <td className="py-2 pr-4 text-right tabular-nums">
        <ThisSessionCell row={row} />
      </td>
      <td className="py-2 text-right tabular-nums">
        <VsTypicalCell row={row} />
      </td>
    </tr>
  );
}

function ThisSessionCell({ row }: { row: SpineRow }) {
  const s = row.state;

  // Non-participating athletes: state precedence.
  if (s.kind === "withheld" && s.reason === "notParticipating") {
    return (
      <span style={{ color: "var(--color-text-tertiary)" }}>
        {copy("athlete.detail.dnp")}
      </span>
    );
  }

  // sRPE not submitted — words, never a dash, never a zero.
  if (s.kind === "withheld" && s.reason === "notSubmitted") {
    return (
      <span style={{ color: "var(--color-text-tertiary)" }}>
        {copy("athlete.detail.notSubmitted")}
      </span>
    );
  }

  // Cardio Load below coverage floor — value withholds outright.
  if (s.kind === "withheld" && s.reason === "coverage") {
    return (
      <span style={{ color: "var(--color-text-tertiary)" }}>
        {copy("athlete.summary.withheld.coverage")}
      </span>
    );
  }

  // Otherwise a real value; append `· NN% cov` on hollow (no ring glyph).
  const valueText = row.value != null ? formatAbsolute(row.value, row.unit) : "—";
  return (
    <span style={{ color: "var(--color-text-primary)" }}>
      {valueText}
      {s.kind === "hollow" && (
        <span
          className="ml-1 text-[11.5px]"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          {tmpl("athlete.detail.covSuffixTemplate", { n: Math.round(s.coveragePct) })}
        </span>
      )}
    </span>
  );
}

function VsTypicalCell({ row }: { row: SpineRow }) {
  const s = row.state;

  if (s.kind === "withheld") return <Dash />;
  if (s.kind === "building") {
    return (
      <span style={{ color: "var(--color-text-tertiary)" }}>
        {copy("athlete.detail.building")}
      </span>
    );
  }

  // beyondRange or ok/hollow — deltaPct is set on any finalised row.
  if (row.deltaPct == null) return <Dash />;
  const sign = row.deltaPct > 0 ? "+" : row.deltaPct < 0 ? "−" : "";
  const mag = Math.abs(row.deltaPct);
  return (
    <span style={{ color: "var(--color-text-primary)" }}>
      {sign}
      {mag.toFixed(0)}%
    </span>
  );
}

function Dash() {
  return (
    <span style={{ color: "var(--color-text-tertiary)" }}>—</span>
  );
}

/* ─────────────────── columns picker (inert) ─────────────────── */

function ColumnsButton() {
  const [open, setOpen] = useState(false);
  return (
    <div className="relative">
      <button
        onClick={() => setOpen((v) => !v)}
        className="type-microcaps rounded border px-2 py-1 text-[10.5px] transition-colors"
        style={{
          borderColor: "var(--color-border)",
          color: "var(--color-text-secondary)",
          backgroundColor: open ? "var(--color-slate-100)" : "transparent",
        }}
        aria-expanded={open}
      >
        {copy("athlete.detail.columnsButton")} ⌄
      </button>
      {open && (
        <div
          className="absolute right-0 top-full z-20 mt-1 w-[220px] rounded-md border p-2 text-[12px] shadow-sm"
          style={{
            borderColor: "var(--color-border)",
            backgroundColor: "var(--color-surface-card)",
            color: "var(--color-text-secondary)",
          }}
          onMouseLeave={() => setOpen(false)}
        >
          {copy("athlete.detail.columnsHint")}
        </div>
      )}
    </div>
  );
}

/* ─────────────────── value formatting ─────────────────── */

function formatAbsolute(v: number, unit: string): string {
  if (unit === "m" || unit === "CL" || unit === "AU" || unit === "ct") {
    return `${Math.round(v).toLocaleString()} ${unit}`;
  }
  if (unit === "m/min") {
    return `${Math.round(v)} ${unit}`;
  }
  if (unit === "km/h") {
    return `${v.toFixed(1)} ${unit}`;
  }
  return `${v} ${unit}`;
}
