import { copy } from "@/lib/copy-deck";
/**
 * GapPair — external (blue filled) vs internal (purple open ring) on
 * one shared track. Slate connector = the gap.
 *
 * Two modes:
 *   - "shared": absolute % scale 0-100 (or scaleMin..scaleMax).
 *   - "signed": deviations vs each athlete's typical, window ±40%,
 *     0-line drawn at 50% ("his typical"). Used inside Attention rows.
 *
 * The basis is part of the object — pass `basisLabel` (e.g.
 * "% of session-average rate") and it renders as an eyebrow above
 * the track. In compact/signed use the eyebrow is suppressed; the
 * card holding the row states the basis once.
 */
export type GapPairProps = {
  mode?: "shared" | "signed";
  externalPct: number;
  internalPct: number;
  scaleMin?: number;
  scaleMax?: number;
  basisLabel?: string;
  size?: "default" | "compact";
  showLegend?: boolean;
  tone?: "default" | "escalate" | "notice";
  /** deltaLabel override — e.g. "+22 pts". Auto-computed when omitted. */
  deltaLabel?: string;
  /** When set, the internal (cost) ring wears the TrustMark idiom
   *  (hatch veil + leading dot). Coverage is surfaced on hover title. */
  internalTrust?: { coverage: number };
  /** When true, dots grow half a step and the slate connector thickens one step. Slate only, no hue. */
  heavy?: boolean;
};

export function GapPair({
  mode = "shared",
  externalPct,
  internalPct,
  scaleMin,
  scaleMax,
  basisLabel,
  size = "default",
  showLegend,
  tone = "default",
  deltaLabel,
  internalTrust,
  heavy = false,
}: GapPairProps) {
  const compact = size === "compact";
  const withLegend = showLegend ?? (!compact && mode === "shared");

  let extPos: number;
  let intPos: number;
  if (mode === "signed") {
    const W = 40;
    const toPos = (v: number) =>
      ((Math.max(-W, Math.min(W, v)) + W) / (W * 2)) * 100;
    extPos = toPos(externalPct);
    intPos = toPos(internalPct);
  } else {
    const min = scaleMin ?? 0;
    const max = scaleMax ?? 100;
    const toPos = (v: number) =>
      Math.max(0, Math.min(100, ((v - min) / (max - min)) * 100));
    extPos = toPos(externalPct);
    intPos = toPos(internalPct);
  }
  const left = Math.min(extPos, intPos);
  const right = Math.max(extPos, intPos);

  const gapPts = externalPct - internalPct;
  const printedDelta =
    deltaLabel ??
    `${gapPts >= 0 ? "+" : ""}${gapPts.toFixed(0)} pts`;

  const trackH = compact ? "h-5" : "h-8";
  const trackBandH = compact ? "h-[6px]" : "h-[7px]";
  const dotDim = heavy
    ? compact ? "h-[18px] w-[18px]" : "h-[22px] w-[22px]"
    : compact ? "h-3 w-3" : "h-3.5 w-3.5";
  const connectorH = heavy ? "h-[4px]" : "h-[2px]";
  const connectorInk = heavy ? "var(--color-slate-500)" : "var(--color-slate-400)";
  const deltaInk =
    tone === "escalate"
      ? "var(--color-escalate-ink)"
      : tone === "notice"
        ? "var(--color-notice-ink)"
        : "var(--color-text-primary)";

  return (
    <div className={compact ? "flex items-center gap-2.5" : "space-y-2"}>
      {!compact && basisLabel && (
        <div className="type-label">{copy("canonical.gap.basisPrefix")}{basisLabel}</div>
      )}
      <div className={compact ? `relative ${trackH} flex-1` : `relative ${trackH}`}>
        <div
          className={`absolute left-0 right-0 top-1/2 ${trackBandH} -translate-y-1/2 rounded-full`}
          style={{ backgroundColor: "var(--color-data-band)" }}
        />
        {mode === "signed" && (
          <div
            className="absolute top-1/2 h-3 w-[2px] -translate-x-1/2 -translate-y-1/2 rounded-sm"
            style={{ left: "50%", backgroundColor: "var(--color-data-reference)" }}
            title={copy("gap.typicalHover")}
          />
        )}
        <div
          className={`absolute top-1/2 ${connectorH} -translate-y-1/2`}
          style={{
            left: `${left}%`,
            width: `${right - left}%`,
            backgroundColor: connectorInk,
          }}
        />
        <div
          className={`absolute top-1/2 ${dotDim} -translate-x-1/2 -translate-y-1/2 rounded-full ring-2 ring-white`}
          style={{ left: `${extPos}%`, backgroundColor: "var(--color-axis-work)" }}
          aria-label={copy("canonical.axisGroup.externalWorkLower")}
        />
        {internalTrust && (
          <span
            className="veil-hatch absolute top-1/2 h-3 w-5 -translate-x-1/2 -translate-y-1/2 rounded-sm opacity-70"
            style={{ left: `${intPos}%` }}
            aria-hidden
            title={`${internalTrust.coverage}% cov`}
          />
        )}
        <div
          className={`absolute top-1/2 ${dotDim} -translate-x-1/2 -translate-y-1/2 rounded-full bg-white`}
          style={{
            left: `${intPos}%`,
            border: "2px solid var(--color-axis-cost)",
          }}
          aria-label={copy("canonical.axisGroup.internalCostLower")}
          title={internalTrust ? `internal · ${internalTrust.coverage}% cov` : undefined}
        />
      </div>

      {compact ? (
        <span
          className="type-num w-[54px] shrink-0 text-right text-[12.5px] font-semibold"
          style={{ color: deltaInk }}
        >
          {printedDelta}
        </span>
      ) : (
        withLegend && (
          <div className="flex items-center justify-between type-data-label">
            <div className="flex items-center gap-4">
              <span className="inline-flex items-center gap-1.5">
                <span
                  className="h-2.5 w-2.5 rounded-full"
                  style={{ backgroundColor: "var(--color-axis-work)" }}
                />
                {copy("canonical.axisGroup.externalWork")}
              </span>
              <span className="inline-flex items-center gap-1.5">
                <span
                  className="h-2.5 w-2.5 rounded-full bg-white"
                  style={{ border: "2px solid var(--color-axis-cost)" }}
                />
                {copy("canonical.axisGroup.internalCost")}
              </span>
            </div>
            <span
              className="type-num font-semibold"
              style={{ color: deltaInk }}
            >
              {printedDelta}
            </span>
          </div>
        )
      )}
    </div>
  );
}
