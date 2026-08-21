import { copy, tmpl } from "@/lib/copy-deck";
import { TRACK_GEO } from "@/components/data/ValueOnTrack";

/**
 * GapPair — work (blue) and cost (purple) marks on ONE shared track,
 * drawn in the ValueOnTrack anatomy (hairline + end caps, bounded
 * reference band, reference tick, canonical dots).
 *
 * The distance between the two marks is stated by a measurement
 * bracket drawn ABOVE the track: a 1px slate-500 span with 4px
 * down-ticks at both ends and the label "N pts gap" centred above it.
 * Bracket and label are neutral slate — no severity, no third hue.
 *
 * The pair sits under the same <TrackAxis> as its sibling rows; it
 * never prints its own endpoints or scale sentence.
 *
 * Hover reveals only what is not printed: the two component deltas.
 */
export type GapPairProps = {
  mode?: "shared" | "signed";
  externalPct: number;
  internalPct: number;
  scaleMin?: number;
  scaleMax?: number;
  /** Signed mode deviation window, as a fraction. Default ±40 pts. */
  windowPct?: number;
  /** Half-width of the reference band, in scale points. */
  referenceBand?: number;
  size?: "default" | "compact";
  /** deltaLabel override — e.g. "+22 pts gap". Auto-computed when omitted. */
  deltaLabel?: string;
  /** When set, the cost mark wears the TrustMark veil; coverage on hover. */
  internalTrust?: { coverage: number };
};

export function GapPair({
  mode = "shared",
  externalPct,
  internalPct,
  scaleMin,
  scaleMax,
  windowPct = 40,
  referenceBand,
  size = "default",
  deltaLabel,
  internalTrust,
}: GapPairProps) {
  const compact = size === "compact";
  const g = compact ? TRACK_GEO.compact : TRACK_GEO.default;

  const signed = mode === "signed";
  const min = signed ? -windowPct : (scaleMin ?? 0);
  const max = signed ? windowPct : (scaleMax ?? 100);
  const refValue = signed ? 0 : (min + max) / 2;
  const band = referenceBand ?? (max - min) * 0.1;

  const toPos = (v: number) =>
    Math.max(0, Math.min(100, ((v - min) / (max - min)) * 100));

  const extPos = toPos(externalPct);
  const intPos = toPos(internalPct);
  const refPct = toPos(refValue);
  const bandLeft = toPos(refValue - band);
  const bandRight = toPos(refValue + band);

  const left = Math.min(extPos, intPos);
  const right = Math.max(extPos, intPos);

  const gapPts = externalPct - internalPct;
  const printedGap =
    deltaLabel ??
    `${gapPts >= 0 ? "+" : ""}${gapPts.toFixed(0)} ${copy("canonical.attention.ptsGap")}`;

  const sign = (v: number) => (signed ? `${v >= 0 ? "+" : "−"}${Math.abs(Math.round(v))}` : `${Math.round(v)}`);
  const hoverText = tmpl("canonical.gap.pairHover", { ext: sign(externalPct), int: sign(internalPct) });

  const bracketY = g.y - g.deltaUp; // bracket rail sits where the delta ink rides
  const labelSize = compact ? 10 : 10.5;

  return (
    <div className="group relative w-full" style={{ height: g.h }}>
      {/* hairline */}
      <div
        className="absolute left-0 right-0"
        style={{ top: g.y, height: 1, backgroundColor: "var(--color-slate-300)" }}
      />
      {/* end caps */}
      <div
        className="absolute left-0"
        style={{ top: g.y - g.cap / 2, height: g.cap, width: 1, backgroundColor: "var(--color-slate-300)" }}
      />
      <div
        className="absolute right-0"
        style={{ top: g.y - g.cap / 2, height: g.cap, width: 1, backgroundColor: "var(--color-slate-300)" }}
      />

      {/* reference band — a bounded interval */}
      <div
        className="absolute"
        style={{
          left: `${bandLeft}%`,
          width: `${bandRight - bandLeft}%`,
          top: g.y - g.band / 2,
          height: g.band,
          backgroundColor: "var(--color-reference-band)",
          borderLeft: "1px solid var(--color-slate-300)",
          borderRight: "1px solid var(--color-slate-300)",
          borderRadius: 2,
        }}
        aria-hidden
      />
      {/* reference tick */}
      <div
        className="absolute -translate-x-1/2"
        style={{
          left: `${refPct}%`,
          top: g.y - g.tick / 2,
          height: g.tick,
          width: 1,
          backgroundColor: "var(--color-data-reference)",
        }}
        aria-label={copy("canonical.vot.reference")}
      />

      {/* measurement bracket — the distance between the two marks */}
      <div
        className="absolute"
        style={{
          left: `${left}%`,
          width: `${right - left}%`,
          top: bracketY,
          height: 1,
          backgroundColor: "var(--color-slate-500)",
        }}
        aria-hidden
      />
      <div
        className="absolute"
        style={{ left: `${left}%`, top: bracketY, height: 4, width: 1, backgroundColor: "var(--color-slate-500)" }}
        aria-hidden
      />
      <div
        className="absolute"
        style={{ left: `${right}%`, top: bracketY, height: 4, width: 1, backgroundColor: "var(--color-slate-500)" }}
        aria-hidden
      />
      <span
        className="type-num absolute -translate-x-1/2 whitespace-nowrap font-medium"
        style={{
          left: `${(left + right) / 2}%`,
          top: bracketY - labelSize - 4,
          fontSize: labelSize,
          lineHeight: `${labelSize + 2}px`,
          color: "var(--color-slate-700)",
        }}
      >
        {printedGap}
      </span>

      {/* marks */}
      {internalTrust && (
        <span
          className="veil-hatch absolute -translate-x-1/2 rounded-sm opacity-70"
          style={{ left: `${intPos}%`, top: g.y - 6, height: 12, width: 20 }}
          aria-hidden
        />
      )}
      <div
        className="absolute -translate-x-1/2 rounded-full"
        style={{
          left: `${extPos}%`,
          top: g.y - g.dot / 2,
          height: g.dot,
          width: g.dot,
          backgroundColor: "var(--color-axis-work)",
        }}
        aria-label={copy("canonical.axisGroup.externalWorkLower")}
      />
      <div
        className="absolute -translate-x-1/2 rounded-full"
        style={{
          left: `${intPos}%`,
          top: g.y - g.dot / 2,
          height: g.dot,
          width: g.dot,
          backgroundColor: "var(--color-axis-cost)",
        }}
        aria-label={copy("canonical.axisGroup.internalCostLower")}
        title={internalTrust ? `${internalTrust.coverage}% cov` : undefined}
      />

      {/* transient hover — the two component deltas only */}
      <div
        className="type-num pointer-events-none absolute left-1/2 z-10 hidden -translate-x-1/2 whitespace-nowrap rounded px-2 py-1 text-[10.5px] group-hover:block"
        style={{ top: g.y + 8, backgroundColor: "var(--color-slate-800)", color: "#FFFFFF" }}
        role="tooltip"
      >
        {hoverText}
      </div>
    </div>
  );
}
