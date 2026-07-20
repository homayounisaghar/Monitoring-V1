/**
 * ST2 — Athlete page · legend (Workstream 02 · prompt 2).
 *
 * Light interactive popover. State-aware: a line renders only when its
 * mark is actually on screen. Term + gloss, six words or fewer. Uses
 * existing legend.* keys verbatim — this component authors none.
 *
 * Explicit omissions (see prompt §7.2):
 *   - No closing sentence, no footnote, no diamond line.
 *   - No `legend.srpeLight` — on the Athlete spine, hue is axis only;
 *     sRPE renders in the same cost purple as Cardio Load.
 *   - No `legend.gapPair` — the spine has no two-mark pair.
 */

import { useEffect, useRef, useState } from "react";
import { copy } from "@/lib/copy-deck";
import type { AthleteSpine } from "@/lib/athlete-data";

type Presence = {
  band: boolean;
  tick: boolean;
  hollow: boolean;
  cov: boolean;
  brk: boolean;
  gap: boolean;
  flag: boolean;
};

function computePresence(spine: AthleteSpine): Presence {
  const p: Presence = {
    band: false, tick: false, hollow: false, cov: false,
    brk: false, gap: false, flag: false,
  };
  for (const r of spine.rows) {
    if (r.bandLoPct != null && r.bandHiPct != null) p.band = true;
    if (r.reference != null) p.tick = true;
    if (r.state.kind === "hollow") { p.hollow = true; p.cov = true; }
    if (r.state.kind === "beyondRange") p.brk = true;
    if (r.state.kind === "withheld") p.gap = true;
    if (r.flagged) p.flag = true;
  }
  return p;
}

const EXT_BLUE = "#3B82F6";
const INT_PURPLE = "#8B5CF6";

export function AthleteLegend({ spine, peerActive = false }: { spine: AthleteSpine; peerActive?: boolean }) {
  const [open, setOpen] = useState(false);
  const wrapRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onDoc = (e: MouseEvent) => {
      if (wrapRef.current && !wrapRef.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, [open]);

  const p = computePresence(spine);

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
            <LegendRow swatch={<SwHue kind="ext" />} text={copy("legend.ext")} />
            <LegendRow swatch={<SwHue kind="int" />} text={copy("legend.int")} />
            {p.band && <LegendRow swatch={<SwBand />} text={copy("legend.band")} />}
            {p.tick && <LegendRow swatch={<SwTick />} text={copy("legend.tick")} />}
            {p.hollow && <LegendRow swatch={<SwHollow />} text={copy("legend.hollow")} />}
            {p.cov && <LegendRow swatch={<SwCov />} text={copy("legend.cov")} />}
            {p.brk && <LegendRow swatch={<SwBreak />} text={copy("legend.break")} />}
            {p.gap && <LegendRow swatch={<SwGap />} text={copy("legend.gap")} />}
            {p.flag && <LegendRow swatch={<SwFlag />} text={copy("legend.flag")} />}
          </ul>
        </div>
      )}
    </div>
  );
}

function LegendRow({ swatch, text }: { swatch: React.ReactNode; text: string }) {
  return (
    <li className="flex items-center gap-2.5">
      <span className="grid h-4 w-6 place-items-center shrink-0">{swatch}</span>
      <span style={{ color: "var(--color-text-primary)" }}>{text}</span>
    </li>
  );
}

function SwHue({ kind }: { kind: "ext" | "int" }) {
  return (
    <span
      className="inline-block h-3 w-3 rounded-full"
      style={{ backgroundColor: kind === "ext" ? EXT_BLUE : INT_PURPLE }}
    />
  );
}
function SwBand() {
  return (
    <span
      className="inline-block h-2 w-5 rounded-sm"
      style={{ backgroundColor: "var(--color-reference-band)" }}
    />
  );
}
function SwTick() {
  return (
    <span
      className="inline-block h-3 w-[2px] rounded-sm"
      style={{ backgroundColor: "var(--color-data-reference)" }}
    />
  );
}
function SwHollow() {
  return (
    <span
      className="inline-block h-3 w-3 rounded-full"
      style={{ backgroundColor: "transparent", border: `1.75px solid ${INT_PURPLE}` }}
    />
  );
}
function SwCov() {
  return (
    <span className="type-num text-[10px]" style={{ color: "var(--color-text-tertiary)" }}>
      74%
    </span>
  );
}
function SwBreak() {
  return (
    <span className="type-num text-[13px]" style={{ color: "var(--color-text-secondary)" }}>
      ▸
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
function SwFlag() {
  return (
    <svg viewBox="0 0 12 12" className="h-3 w-3" aria-hidden>
      <path d="M3 1v10M3 2h6l-1.5 2L9 6H3" fill="currentColor" stroke="currentColor" strokeWidth="1" />
    </svg>
  );
}
