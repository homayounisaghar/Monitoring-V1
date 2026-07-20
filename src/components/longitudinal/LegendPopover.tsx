/**
 * Longitudinal — the legend.
 *
 * Light interactive popover (dark is reserved for transient data tooltips).
 * Term + gloss, six words or fewer per line; no sentences. State-aware:
 * a mark's line renders only when that mark is on screen in the current
 * window. The two hue lines and the participation key always render.
 *
 * Note (omission): no "light purple — sRPE, where collected" line — both
 * internal lanes render in the same cost purple, so the line would describe
 * a distinction the chart doesn't draw.
 */

import { useEffect, useMemo, useRef, useState } from "react";
import { copy } from "@/lib/copy-deck";
import {
  daySeries,
  athleteAvailabilityRanking,
  type LongiWindow,
  type LongiMetric,
  type DayEntry,
} from "@/lib/longitudinal-data";
import {
  PARTICIPATION_TAGS,
  TAG_FILL,
  TAG_STYLE,
  NOT_IN_SQUAD_STYLE,
} from "@/lib/participation-style";

/** Fixed drawn caps — mirrors DaysSection ABS_CAP; used only to compute
 *  whether the "break" mark is present in the window. */
const ABS_CAP: Record<LongiMetric, number> = {
  totalDistance: 9000,
  hsr: 700,
  sprintDist: 220,
  accDec: 110,
  cardioLoad: 220,
  srpeAU: 700,
};

type Presence = {
  hollow: boolean;
  cov: boolean;
  hatch: boolean;
  brk: boolean;
  gap: boolean;
  rest: boolean;
  matchMark: boolean;
  flag: boolean;
};

function computePresence(w: LongiWindow): Presence {
  const series: DayEntry[] = daySeries(w);
  let hollow = false, cov = false, hatch = false, brk = false;
  let gap = false, rest = false, matchMark = false;
  for (const d of series) {
    if (d.kind === "missing") gap = true;
    if (d.kind === "rest") rest = true;
    if (d.dayCode === "MD") matchMark = true;
    if (d.unconfirmed) hatch = true;
    if (d.hrCoverageShare != null && d.hrCoverageShare < 1) {
      hollow = true;
      cov = true;
    }
    // "break" — any lane value exceeds its drawn cap.
    for (const m of Object.keys(ABS_CAP) as LongiMetric[]) {
      const v = d.perMetric[m];
      if (v != null && v > ABS_CAP[m]) { brk = true; break; }
    }
  }
  // Flag glyph — any athlete in the window has attentionFlagged.
  const rows = athleteAvailabilityRanking(w);
  const flag = rows.some((r) => r.attentionFlagged);
  return { hollow, cov, hatch, brk, gap, rest, matchMark, flag };
}

export function LegendPopover({ window: w }: { window: LongiWindow }) {
  const [open, setOpen] = useState(false);
  const wrapRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onDoc = (e: MouseEvent) => {
      if (wrapRef.current && !wrapRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, [open]);

  const presence = useMemo(() => computePresence(w), [w]);

  return (
    <div className="relative" ref={wrapRef}>
      <button
        onClick={() => setOpen((o) => !o)}
        aria-haspopup="dialog"
        aria-expanded={open}
        className="text-[12px] transition-colors hover:underline"
        style={{ color: "var(--color-text-secondary)" }}
      >
        {copy("control.legend")}
      </button>
      {open && (
        <div
          role="dialog"
          className="absolute right-0 top-full z-40 mt-2 w-[320px] overflow-hidden rounded-md border shadow-xl"
          style={{
            backgroundColor: "var(--color-surface-card)",
            borderColor: "var(--color-border)",
            color: "var(--color-text-primary)",
          }}
        >
          <div
            className="type-microcaps px-3 py-2"
            style={{
              color: "var(--color-text-secondary)",
              borderBottom: "1px solid var(--color-border)",
            }}
          >
            {copy("control.legend")}
          </div>

          <ul className="flex flex-col gap-1.5 px-3 py-2.5 text-[12px]">
            {/* The Benchmark chip's foot gloss is the single home for the
                basis definition. */}
            <LegendRow swatch={<SwHue kind="ext" />} text={copy("legend.ext")} />
            <LegendRow swatch={<SwHue kind="int" />} text={copy("legend.int")} />
            <LegendRow swatch={<SwSrpeLight />} text={copy("legend.srpeLight")} />
            {presence.hollow && (
              <LegendRow swatch={<SwHollow />} text={copy("legend.hollow")} />
            )}
            {presence.cov && (
              <LegendRow swatch={<SwCov />} text={copy("legend.cov")} />
            )}
            {presence.hatch && (
              <LegendRow swatch={<SwHatch />} text={copy("legend.hatch")} />
            )}
            {presence.brk && (
              <LegendRow swatch={<SwBreak />} text={copy("legend.break")} />
            )}
            {presence.gap && (
              <LegendRow swatch={<SwGap />} text={copy("legend.gap")} />
            )}
            {presence.rest && (
              <LegendRow swatch={<SwRest />} text={copy("legend.rest")} />
            )}
            {presence.matchMark && (
              <LegendRow swatch={<SwMatchMark />} text={copy("legend.matchMark")} />
            )}
            {presence.flag && (
              <LegendRow swatch={<SwFlag />} text={copy("legend.flag")} />
            )}
          </ul>

          <div
            className="border-t px-3 py-2.5"
            style={{ borderColor: "var(--color-border)" }}
          >
            <div className="flex flex-wrap items-center gap-x-3 gap-y-1.5">
              {PARTICIPATION_TAGS.map((t) => (
                <div key={t} className="flex items-center gap-1.5 text-[11.5px]">
                  <span
                    className="inline-block h-3 w-3 rounded-[2px]"
                    style={TAG_STYLE[t]}
                  />
                  <span style={{ color: "var(--color-text-primary)" }}>{t}</span>
                </div>
              ))}
              <div className="flex items-center gap-1.5 text-[11.5px]">
                <span
                  className="inline-block h-3 w-3 rounded-[2px]"
                  style={NOT_IN_SQUAD_STYLE}
                />
                <span style={{ color: "var(--color-text-secondary)" }}>
                  not in squad
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/* ─────────────────── row + swatches ─────────────────── */

function LegendRow({ swatch, text }: { swatch: React.ReactNode; text: string }) {
  return (
    <li className="flex items-center gap-2.5">
      <span className="grid h-4 w-6 place-items-center shrink-0">{swatch}</span>
      <span style={{ color: "var(--color-text-primary)" }}>{text}</span>
    </li>
  );
}

const EXT_BLUE = "#3B82F6";
const INT_PURPLE = "#8B5CF6";

// SwBasis — retired swatch for the retired legend.basis row. Retained
// (unexported, referenced by a void statement below) so the swatch stays
// available if the legend line ever comes back.
function SwBasis() {
  return (
    <span
      className="inline-block h-[1.5px] w-5"
      style={{ backgroundColor: "var(--color-text-secondary)" }}
    />
  );
}
void SwBasis;
function SwHue({ kind }: { kind: "ext" | "int" }) {
  return (
    <span
      className="inline-block h-3 w-3 rounded-[2px]"
      style={{ backgroundColor: kind === "ext" ? EXT_BLUE : INT_PURPLE }}
    />
  );
}
function SwSrpeLight() {
  return (
    <span
      className="inline-block h-3 w-3 rounded-[2px]"
      style={{ backgroundColor: "var(--color-axis-cost-light)" }}
    />
  );
}
function SwHollow() {
  return (
    <span
      className="inline-block h-3 w-3 rounded-[2px]"
      style={{ backgroundColor: "transparent", border: `1.5px solid ${INT_PURPLE}` }}
    />
  );
}
function SwCov() {
  return (
    <span
      className="type-num text-[10px]"
      style={{ color: "var(--color-text-tertiary)" }}
    >
      74%
    </span>
  );
}
function SwHatch() {
  return (
    <span
      className="inline-block h-3 w-3 rounded-[2px]"
      style={{
        backgroundColor: EXT_BLUE,
        backgroundImage:
          "repeating-linear-gradient(45deg, rgba(255,255,255,0.55) 0 1.5px, transparent 1.5px 3px)",
      }}
    />
  );
}
function SwBreak() {
  // Two short diagonals — the break-slash mark on the cap.
  return (
    <span className="relative inline-block h-3 w-4">
      <span
        className="absolute left-0 top-1/2 h-[1.5px] w-2 -rotate-[20deg]"
        style={{ backgroundColor: "var(--color-text-primary)" }}
      />
      <span
        className="absolute right-0 top-1/2 h-[1.5px] w-2 -rotate-[20deg]"
        style={{ backgroundColor: "var(--color-text-primary)" }}
      />
    </span>
  );
}
function SwGap() {
  return (
    <span
      className="inline-block h-[2px] w-4"
      style={{ backgroundColor: "var(--color-text-tertiary)" }}
    />
  );
}
function SwRest() {
  return (
    <span className="relative inline-block h-3 w-4">
      <span
        className="absolute bottom-[3px] left-1/2 h-[3px] w-[3px] -translate-x-1/2 rounded-full"
        style={{ backgroundColor: "var(--color-text-secondary)" }}
      />
      <span
        className="absolute bottom-[4px] left-0 h-[1px] w-full"
        style={{ backgroundColor: "var(--color-border)" }}
      />
    </span>
  );
}
function SwMatchMark() {
  return (
    <span
      className="type-microcaps text-[10px]"
      style={{ color: "var(--color-text-primary)" }}
    >
      MD
    </span>
  );
}
function SwFlag() {
  return (
    <svg viewBox="0 0 12 12" className="h-3.5 w-3.5" aria-hidden>
      <path
        d="M3 1v10M3 2h6l-1.5 2L9 6H3"
        fill={TAG_FILL.Rehab}
        stroke={TAG_FILL.Rehab}
        strokeWidth="1"
        strokeLinejoin="round"
      />
    </svg>
  );
}
