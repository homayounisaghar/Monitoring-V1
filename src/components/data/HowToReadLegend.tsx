/**
 * HowToReadLegend — the single shared vocabulary key.
 *
 * Rendered identically on Session, Athlete and Longitudinal. It teaches
 * FORMS only: no numbers from the data, no mechanism narration, no
 * sentences about how anything is computed, no scale/range lines (the
 * TrackAxis header on the canvas carries scale identity).
 *
 * Every swatch is drawn from the same tokens the live components use
 * (TRACK_GEO, --color-slate-300/400, --color-reference-band,
 * --color-axis-work / --color-axis-cost, --color-trust-dot), so the
 * legend cannot drift from the canvas.
 */

import { Flag } from "lucide-react";
import { copy, type CopyKey } from "@/lib/copy-deck";
import { TRACK_GEO } from "./ValueOnTrack";

const G = TRACK_GEO.compact;

/** Common swatch frame — a short piece of the real track. */
function Frame({ children, w = 44 }: { children?: React.ReactNode; w?: number }) {
  return (
    <span className="relative inline-block shrink-0" style={{ width: w, height: 22 }} aria-hidden>
      {children}
    </span>
  );
}

function Hairline() {
  return (
    <>
      <span
        className="absolute left-0 right-0"
        style={{ top: 11, height: 1, backgroundColor: "var(--color-slate-300)" }}
      />
      <span
        className="absolute left-0"
        style={{ top: 11 - G.cap / 2, height: G.cap, width: 1, backgroundColor: "var(--color-slate-300)" }}
      />
      <span
        className="absolute right-0"
        style={{ top: 11 - G.cap / 2, height: G.cap, width: 1, backgroundColor: "var(--color-slate-300)" }}
      />
    </>
  );
}

function Band() {
  return (
    <span
      className="absolute"
      style={{
        left: "22%",
        width: "56%",
        top: 11 - G.band / 2,
        height: G.band,
        backgroundColor: "var(--color-reference-band)",
        borderLeft: "1px solid var(--color-slate-300)",
        borderRight: "1px solid var(--color-slate-300)",
        borderRadius: 2,
      }}
    />
  );
}

function Tick() {
  return (
    <span
      className="absolute -translate-x-1/2"
      style={{
        left: "50%",
        top: 11 - G.tick / 2,
        height: G.tick,
        width: 1,
        backgroundColor: "var(--color-data-reference)",
      }}
    />
  );
}

function Dot({ left, axis }: { left: string; axis: "work" | "cost" }) {
  return (
    <span
      className="absolute -translate-x-1/2 rounded-full"
      style={{
        left,
        top: 11 - G.dot / 2,
        height: G.dot,
        width: G.dot,
        backgroundColor: axis === "work" ? "var(--color-axis-work)" : "var(--color-axis-cost)",
      }}
    />
  );
}

function SwBand() {
  return (
    <Frame>
      <Hairline />
      <Band />
    </Frame>
  );
}

function SwTick() {
  return (
    <Frame>
      <Hairline />
      <Tick />
    </Frame>
  );
}

function SwDot() {
  return (
    <Frame>
      <Hairline />
      <Dot left="58%" axis="work" />
      <span
        className="type-num absolute -translate-x-1/2 whitespace-nowrap font-medium"
        style={{
          left: "58%",
          top: 0,
          fontSize: 9.5,
          lineHeight: "10px",
          color: "var(--color-axis-work-ink, #1D4ED8)",
        }}
      >
        +14%
      </span>
    </Frame>
  );
}

function SwPair() {
  return (
    <Frame>
      <Hairline />
      {/* measurement bracket above the track */}
      <span
        className="absolute"
        style={{ left: "26%", width: "48%", top: 3, height: 1, backgroundColor: "var(--color-slate-500)" }}
      />
      <span
        className="absolute"
        style={{ left: "26%", top: 3, height: 3, width: 1, backgroundColor: "var(--color-slate-500)" }}
      />
      <span
        className="absolute"
        style={{ left: "74%", top: 3, height: 3, width: 1, backgroundColor: "var(--color-slate-500)" }}
      />
      <Dot left="26%" axis="work" />
      <Dot left="74%" axis="cost" />
    </Frame>
  );
}

function SwTrustDot() {
  return (
    <Frame>
      <span
        className="absolute left-1/2 -translate-x-1/2 rounded-full"
        style={{
          top: 11 - 4,
          height: 8,
          width: 8,
          backgroundColor: "transparent",
          border: "1.25px solid var(--color-trust-dot)",
        }}
      />
    </Frame>
  );
}

function SwUnconfirmed() {
  return (
    <Frame>
      <span
        className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 rounded-sm"
        style={{
          height: 12,
          width: 24,
          backgroundColor: "var(--color-slate-400)",
          backgroundImage:
            "repeating-linear-gradient(-45deg, rgba(255,255,255,0.55) 0 2px, transparent 2px 5px)",
        }}
      >
        <span
          className="absolute left-1/2 top-1/2 h-1.5 w-1.5 -translate-x-1/2 -translate-y-1/2 rounded-full"
          style={{ backgroundColor: "#fff", border: "1px solid var(--color-slate-500)" }}
        />
      </span>
    </Frame>
  );
}

function SwBreak() {
  return (
    <Frame>
      <Hairline />
      {/* the clamp break glyph — two slanted strokes just inside the end */}
      <span className="absolute" style={{ right: 8, top: 11 - 5, height: 10, width: 9 }}>
        <span
          className="absolute left-0 top-0"
          style={{ height: 10, width: 1, backgroundColor: "var(--color-trust-dot)", transform: "rotate(24deg)" }}
        />
        <span
          className="absolute right-0 top-0"
          style={{ height: 10, width: 1, backgroundColor: "var(--color-trust-dot)", transform: "rotate(24deg)" }}
        />
      </span>
      <Dot left="97%" axis="work" />
    </Frame>
  );
}

function SwNoData() {
  return (
    <Frame>
      <span
        className="type-num absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-[13px]"
        style={{ color: "var(--color-text-tertiary)" }}
      >
        —
      </span>
    </Frame>
  );
}

function SwFlag() {
  return (
    <Frame>
      <Flag
        className="absolute left-1/2 top-1/2 h-3.5 w-3.5 -translate-x-1/2 -translate-y-1/2"
        style={{ color: "var(--color-text-secondary)" }}
      />
    </Frame>
  );
}

/** The nine entries, in ratified order. */
const ENTRIES: Array<{ key: CopyKey; swatch: React.ReactNode }> = [
  { key: "legend.band", swatch: <SwBand /> },
  { key: "legend.tick", swatch: <SwTick /> },
  { key: "legend.dot", swatch: <SwDot /> },
  { key: "legend.gapPair", swatch: <SwPair /> },
  { key: "legend.trustDot", swatch: <SwTrustDot /> },
  { key: "legend.unconfirmed", swatch: <SwUnconfirmed /> },
  { key: "legend.breakGlyph", swatch: <SwBreak /> },
  { key: "legend.noData", swatch: <SwNoData /> },
  { key: "legend.flagGlyph", swatch: <SwFlag /> },
];

export function HowToReadLegendBody() {
  return (
    <ul className="flex flex-col gap-1.5">
      {ENTRIES.map((e) => (
        <li key={e.key} className="flex items-center gap-2.5 text-[12px] leading-snug">
          {e.swatch}
          <span style={{ color: "var(--color-text-primary)" }}>{copy(e.key)}</span>
        </li>
      ))}
    </ul>
  );
}

/** The shared panel shell — same width, same header, on every page. */
export function HowToReadLegendPanel({ align = "right" }: { align?: "left" | "right" }) {
  return (
    <div
      role="dialog"
      className={
        "absolute top-full z-40 mt-2 w-[330px] overflow-hidden rounded-md border shadow-xl " +
        (align === "right" ? "right-0" : "left-0")
      }
      style={{
        backgroundColor: "var(--color-surface-card)",
        borderColor: "var(--color-border)",
        color: "var(--color-text-primary)",
      }}
    >
      <div
        className="type-microcaps px-3 py-2"
        style={{ color: "var(--color-text-secondary)", borderBottom: "1px solid var(--color-border)" }}
      >
        {copy("control.legend")}
      </div>
      <div className="px-3 py-2.5">
        <HowToReadLegendBody />
      </div>
    </div>
  );
}
