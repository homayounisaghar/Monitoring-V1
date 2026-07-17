import { useEffect, useRef } from "react";
import { Flag, HelpCircle } from "lucide-react";
import { copy, type CopyKey } from "@/lib/copy-deck";
import { useSessionScope } from "@/lib/session-scope";

/* ---------- Swatches (reused idioms from GapPair / AttentionCard.GapMiniTrack
     and PeriodsCard.Legend — drawn identically, sized for the legend column) ---------- */

function BandSwatch() {
  return (
    <span className="relative inline-block h-3 w-6 shrink-0" aria-hidden>
      <span
        className="absolute left-0 right-0 top-1/2 h-[6px] -translate-y-1/2 rounded-full"
        style={{ backgroundColor: "var(--color-data-band)" }}
      />
    </span>
  );
}
function TickSwatch() {
  return (
    <span className="relative inline-block h-3 w-6 shrink-0" aria-hidden>
      <span
        className="absolute left-0 right-0 top-1/2 h-[6px] -translate-y-1/2 rounded-full"
        style={{ backgroundColor: "var(--color-data-band)" }}
      />
      <span
        className="absolute left-1/2 top-1/2 h-3 w-[2px] -translate-x-1/2 -translate-y-1/2 rounded-sm"
        style={{ backgroundColor: "var(--color-data-reference)" }}
      />
    </span>
  );
}
function DotSwatch() {
  return (
    <span className="relative inline-block h-3 w-6 shrink-0" aria-hidden>
      <span
        className="absolute left-0 right-0 top-1/2 h-[6px] -translate-y-1/2 rounded-full"
        style={{ backgroundColor: "var(--color-data-band)" }}
      />
      <span
        className="absolute left-1/2 top-1/2 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full ring-2 ring-white"
        style={{ backgroundColor: "var(--color-axis-work)" }}
      />
    </span>
  );
}
function GapPairSwatch() {
  // External (work-blue) + internal (cost-purple, smaller) with white halos,
  // matches the recostumed pair in GapPair / AttentionCard.GapMiniTrack.
  return (
    <span className="relative inline-block h-3 w-6 shrink-0" aria-hidden>
      <span
        className="absolute top-1/2 h-3 w-3 -translate-y-1/2 rounded-full ring-2 ring-white"
        style={{ left: "20%", backgroundColor: "var(--color-axis-work)", transform: "translate(-50%, -50%)" }}
      />
      <span
        className="absolute top-1/2 h-[10px] w-[10px] -translate-y-1/2 rounded-full ring-2 ring-white"
        style={{ left: "70%", backgroundColor: "var(--color-axis-cost)", transform: "translate(-50%, -50%)" }}
      />
    </span>
  );
}
function TrustDotSwatch() {
  return (
    <span className="relative inline-flex h-3 w-6 shrink-0 items-center justify-center" aria-hidden>
      <span
        className="inline-block h-2 w-2 rounded-full"
        style={{ backgroundColor: "transparent", border: "1.25px solid var(--color-trust-dot)" }}
      />
    </span>
  );
}
function UnconfirmedSwatch() {
  // Ring-on-hatch chip — identical to PeriodsCard.Legend's "hatch" swatch.
  return (
    <span
      className="relative inline-block h-3 w-6 shrink-0 rounded-sm"
      style={{
        backgroundColor: "var(--color-slate-400)",
        backgroundImage:
          "repeating-linear-gradient(-45deg, rgba(255,255,255,0.55) 0 2px, transparent 2px 5px)",
      }}
      aria-hidden
    >
      <span
        className="absolute left-1/2 top-1/2 h-1.5 w-1.5 -translate-x-1/2 -translate-y-1/2 rounded-full"
        style={{ backgroundColor: "#fff", border: "1px solid var(--color-slate-500)" }}
      />
    </span>
  );
}
function BreakSwatch() {
  // Break-slash chip — identical to PeriodsCard.Legend's "break" swatch.
  return (
    <span
      className="relative inline-block h-3 w-6 shrink-0 overflow-hidden rounded-sm"
      style={{ backgroundColor: "var(--color-slate-500)" }}
      aria-hidden
    >
      <span className="absolute left-0 right-0" style={{ top: 3, height: 1.5, backgroundColor: "#fff", transform: "skewY(-18deg)" }} />
      <span className="absolute left-0 right-0" style={{ top: 7, height: 1.5, backgroundColor: "#fff", transform: "skewY(-18deg)" }} />
    </span>
  );
}
function DashSwatch() {
  return (
    <span className="inline-flex h-3 w-6 shrink-0 items-center justify-center type-num text-[13px]" aria-hidden>
      —
    </span>
  );
}
function FlagSwatch() {
  return (
    <span className="inline-flex h-3 w-6 shrink-0 items-center justify-center" aria-hidden>
      <Flag className="h-3 w-3" style={{ color: "var(--color-text-secondary)" }} />
    </span>
  );
}

/* Eight lines · swatch + existing deck term (no new copy). */
const ENTRIES: Array<{ key: CopyKey; swatch: React.ReactNode }> = [
  { key: "legend.band",        swatch: <BandSwatch /> },
  { key: "legend.tick",        swatch: <TickSwatch /> },
  { key: "legend.dot",         swatch: <DotSwatch /> },
  { key: "legend.gapPair",     swatch: <GapPairSwatch /> },
  { key: "legend.trustDot",    swatch: <TrustDotSwatch /> },
  { key: "periods.legend.states", swatch: <UnconfirmedSwatch />, /* replaced below */ } as never,
];
// The three additional lines (unconfirmed, beyond, not measured) don't have
// bespoke deck keys — they're carried in periods.legend.states, split on " · ".
// Assemble the eight-line list explicitly from the pre-existing pieces.

function LegendBody() {
  const stateTerms = copy("periods.legend.states").split(" · ");
  // Order in the deck string: [thin coverage, ring+hatch unconfirmed, break, — no data]
  const unconfirmedTerm = stateTerms[1] ?? "unconfirmed";
  const beyondTerm = stateTerms[2] ?? "beyond chart range";
  const notMeasuredTerm = (stateTerms[3] ?? "no data").replace(/^—\s*/, "");

  const rows: Array<{ swatch: React.ReactNode; text: string }> = [
    { swatch: <BandSwatch />,        text: copy("legend.band") },
    { swatch: <TickSwatch />,        text: copy("legend.tick") },
    { swatch: <DotSwatch />,         text: copy("legend.dot") },
    { swatch: <GapPairSwatch />,     text: copy("legend.gapPair") },
    { swatch: <TrustDotSwatch />,    text: copy("legend.trustDot") },
    { swatch: <UnconfirmedSwatch />, text: unconfirmedTerm },
    { swatch: <BreakSwatch />,       text: beyondTerm },
    { swatch: <DashSwatch />,        text: notMeasuredTerm },
    { swatch: <FlagSwatch />,        text: copy("legend.flagGlyph") },
  ];

  // Silence unused-const warning for ENTRIES scaffolding.
  void ENTRIES;

  return (
    <div className="space-y-1.5">
      {rows.map((r, i) => (
        <div
          key={i}
          className="flex items-center gap-2 text-[12px] leading-snug"
          style={{ color: "var(--color-text-secondary)" }}
        >
          {r.swatch}
          <span>{r.text}</span>
        </div>
      ))}
    </div>
  );
}

/* ---------- Popover shells ---------- */

function LegendPanel({ align }: { align: "left" | "right" }) {
  return (
    <div
      className={
        "absolute top-full z-30 mt-1 w-[360px] rounded-md border p-3 shadow-xl " +
        (align === "right" ? "right-0" : "left-0")
      }
      style={{
        backgroundColor: "var(--color-surface-card)",
        borderColor: "var(--color-border)",
        color: "var(--color-text-secondary)",
      }}
    >
      <LegendBody />
    </div>
  );
}

/** Chrome trigger — icon + "Legend" label, used by ReadingLine. */
export function HowToReadPopover() {
  const { legendOpen, setLegendOpen } = useSessionScope();
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!legendOpen) return;
    const onDoc = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setLegendOpen(false);
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, [legendOpen, setLegendOpen]);

  return (
    <span ref={ref} className="relative inline-flex">
      <button
        onClick={() => setLegendOpen(!legendOpen)}
        className="inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[12px] transition-colors hover:bg-[color:var(--color-slate-100)]"
        style={{ color: "var(--color-text-tertiary)" }}
      >
        <HelpCircle className="h-3 w-3" />
        <span>{copy("control.legend")}</span>
      </button>
      {legendOpen && <LegendPanel align="right" />}
    </span>
  );
}

/**
 * Anchor for the Attention card's ⓘ. Renders no trigger of its own —
 * it's an invisible positioning anchor next to the ⓘ button so the panel
 * opens in place. Attention card controls open via useSessionScope().
 */
export function LegendAnchor({ align = "right" }: { align?: "left" | "right" }) {
  const { legendOpen, setLegendOpen } = useSessionScope();
  const ref = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    if (!legendOpen) return;
    const onDoc = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setLegendOpen(false);
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, [legendOpen, setLegendOpen]);

  if (!legendOpen) return null;
  return (
    <span ref={ref} className="relative inline-flex">
      <LegendPanel align={align} />
    </span>
  );
}
