import { copy } from "@/lib/copy-deck";
/**
 * ValueOnTrack — canonical comparison object (foundation anatomy).
 * Band always rendered. Reference band + tick honor baseline state
 * (mature=narrow, young=wide, building=withheld). Value in owning
 * axis hue. Signed % delta in the canonical dialect. Overflow clamps
 * to the window edge and shows a caret past the printed number.
 *
 * `size="compact"` renders a row-height version (used inside Attention
 * rows). `showValue={false}` hides the absolute number and shows only
 * the track + delta, useful for row reads where the label lives at the
 * left of the row.
 */
export type Axis = "work" | "cost" | "neutral";
export type BaselineState = "mature" | "young" | "building";

function axisColor(axis: Axis) {
  if (axis === "work") return "var(--color-axis-work)";
  if (axis === "cost") return "var(--color-axis-cost)";
  return "var(--color-data-ink)";
}

export type ValueOnTrackProps = {
  mode: "deviation" | "shared";
  axis?: Axis;
  value: number;
  reference: number;
  /** deviation: half-width as fraction of reference. shared: half-width in scale units. */
  referenceBandPct?: number;
  windowPct?: number;
  scaleMin?: number;
  scaleMax?: number;
  scaleLabel?: string; // shared mode — labels the reference tick
  unit?: string;
  deltaAbs?: string;
  baselineState?: BaselineState;
  size?: "default" | "compact";
  showValue?: boolean;
  showDelta?: boolean;
  deltaTone?: "default" | "escalate" | "notice";
  /** When false, applies TrustMark treatment to the value (hatch veil + grey ink). */
  qualified?: boolean;
};

export function ValueOnTrack({
  mode,
  axis = "neutral",
  value,
  reference,
  referenceBandPct,
  windowPct = 0.4,
  scaleMin,
  scaleMax,
  scaleLabel,
  unit,
  deltaAbs,
  baselineState = "mature",
  size = "default",
  showValue,
  showDelta = true,
  deltaTone = "default",
  qualified = true,
}: ValueOnTrackProps) {
  const compact = size === "compact";
  const withValue = showValue ?? !compact;
  const color = axisColor(axis);
  const withheld = baselineState === "building";
  const deltaPct = ((value - reference) / reference) * 100;
  const deltaLabel = `${deltaPct >= 0 ? "+" : ""}${deltaPct.toFixed(0)}%`;

  let posPct: number;
  let refPct: number;
  let bandLeftPct = 0;
  let bandRightPct = 0;
  let clamped = false;
  let clampDir: "high" | "low" | null = null;

  if (mode === "deviation") {
    const raw = (value - reference) / reference;
    if (raw > windowPct) {
      posPct = 100;
      clamped = true;
      clampDir = "high";
    } else if (raw < -windowPct) {
      posPct = 0;
      clamped = true;
      clampDir = "low";
    } else {
      posPct = ((raw + windowPct) / (windowPct * 2)) * 100;
    }
    refPct = 50;
    const halfBandFrac = referenceBandPct ?? 0.08;
    bandLeftPct = Math.max(0, ((-halfBandFrac + windowPct) / (windowPct * 2)) * 100);
    bandRightPct = Math.min(100, ((halfBandFrac + windowPct) / (windowPct * 2)) * 100);
  } else {
    const min = scaleMin ?? 0;
    const max = scaleMax ?? 1;
    if (value > max) {
      posPct = 100;
      clamped = true;
      clampDir = "high";
    } else if (value < min) {
      posPct = 0;
      clamped = true;
      clampDir = "low";
    } else {
      posPct = ((value - min) / (max - min)) * 100;
    }
    refPct = Math.max(0, Math.min(100, ((reference - min) / (max - min)) * 100));
    const halfBandAbs = referenceBandPct ?? (max - min) * 0.05;
    bandLeftPct = Math.max(0, ((reference - halfBandAbs - min) / (max - min)) * 100);
    bandRightPct = Math.min(100, ((reference + halfBandAbs - min) / (max - min)) * 100);
  }


  const trackH = compact ? "h-5" : "h-7";
  const trackBandH = compact ? "h-[6px]" : "h-[7px]";
  const refBandH = compact ? "h-[9px]" : "h-[11px]";
  const tickH = compact ? "h-3" : "h-4";
  const dotDim = compact ? "h-3 w-3" : "h-3.5 w-3.5";
  const deltaInk =
    deltaTone === "escalate"
      ? "var(--color-escalate-ink)"
      : deltaTone === "notice"
        ? "var(--color-notice-ink)"
        : "var(--color-text-secondary)";

  return (
    <div className="flex items-center gap-3">
      <div className={`relative ${trackH} flex-1`}>
        <div
          className={`absolute left-0 right-0 top-1/2 ${trackBandH} -translate-y-1/2 rounded-full`}
          style={{ backgroundColor: "var(--color-data-band)" }}
        />
        {!withheld && (
          <div
            className={`absolute top-1/2 ${refBandH} -translate-y-1/2 rounded-sm`}
            style={{
              left: `${bandLeftPct}%`,
              width: `${bandRightPct - bandLeftPct}%`,
              backgroundColor: "var(--color-reference-band)",
            }}
            aria-label={copy("vot.bandHover")}
          />
        )}
        {!withheld && (
          <div
            className={`absolute top-1/2 ${tickH} w-[2px] -translate-x-1/2 -translate-y-1/2 rounded-sm`}
            style={{ left: `${refPct}%`, backgroundColor: "var(--color-data-reference)" }}
            aria-label={copy("canonical.vot.reference")}
            title={scaleLabel}
          />
        )}
        <div
          className={`absolute top-1/2 ${dotDim} -translate-x-1/2 -translate-y-1/2 rounded-full ring-2 ring-white`}
          style={{ left: `${posPct}%`, backgroundColor: color }}
          aria-label={copy("canonical.vot.value")}
        />
        {clamped && !withheld && (
          <div
            className="absolute top-1/2 -translate-y-1/2 type-num text-[10px] font-semibold"
            style={{
              [clampDir === "high" ? "right" : "left"]: "-4px",
              color: "var(--color-text-secondary)",
            }}
          >
            {clampDir === "high" ? "▸" : "◂"}
          </div>
        )}
      </div>

      {(withValue || showDelta) &&
        (withValue ? (
          <div className="flex min-w-[130px] items-baseline justify-end gap-2">
            <span
              className="inline-flex items-baseline gap-1.5"
              title={!qualified ? copy("trust.hoverGeneric") : undefined}
            >
              {!qualified && (
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
                className="type-num text-sm font-semibold"
                style={{ color: qualified ? "var(--color-text-primary)" : "var(--color-text-tertiary)" }}
              >
                {value.toLocaleString()}
                {unit ? <span className="type-data-label ml-0.5">{unit}</span> : null}
              </span>
            </span>
            {withheld ? (
              <span
                className="type-data-label italic"
                title={copy("vot.baselineHover")}
              >
                {copy("canonical.vot.baselineBuilding")}
              </span>
            ) : (
              <span
                className="type-num text-xs font-medium"
                style={{ color: deltaInk }}
                title={deltaAbs ? `Δ ${deltaAbs}` : undefined}
              >
                {deltaLabel}
              </span>
            )}
          </div>
        ) : withheld ? (
          <span
            className="type-data-label w-[54px] shrink-0 text-right italic"
            title={copy("vot.baselineHover")}
          >
            {copy("canonical.vot.building")}
          </span>
        ) : (
          <span
            className="type-num w-[54px] shrink-0 text-right text-[12.5px] font-semibold"
            style={{ color: deltaInk }}
            title={deltaAbs ? `Δ ${deltaAbs}` : undefined}
          >
            {deltaLabel}
          </span>
        ))}
    </div>
  );
}
