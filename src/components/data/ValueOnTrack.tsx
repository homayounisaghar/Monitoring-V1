import { copy } from "@/lib/copy-deck";
/**
 * ValueOnTrack — canonical comparison object (foundation anatomy).
 *
 * Anatomy (ratified 2026-08-21):
 *   • endpoints     — the scale's low/high numerals sit OUTSIDE the end caps
 *                     (4px gap), mono 10px (9px compact), tertiary ink,
 *                     centred on the hairline. Anatomy of EVERY track.
 *   • hairline      — 1px slate-300 rule, with 1px × 8px end caps at both extremes
 *   • reference band— slate-200 fill, 16px tall, 1px slate-300 left/right edges,
 *                     2px radius. A bounded interval, not a smudge.
 *   • reference tick— 1px slate-400, 22px tall, crossing the hairline
 *   • session mark  — 8px dot, filled in the metric's axis hue, on the hairline
 *   • delta         — rides the mark: mono 11px, centred on the dot, 21px above
 *                     the hairline. Never detached in the value column.
 *   • value column  — absolute value + unit only.
 *
 * One-utterance rule: endpoints are anatomy of every track; the tick label
 * ("100 · typical match") is uttered exactly once per scale group per card,
 * by <TrackAxis>. Never as a sentence, never per row.
 *
 * Hover on the track reveals only what is not on canvas: the band bounds in
 * scale units and the reference absolute with its unit.
 */

export type Axis = "work" | "cost" | "neutral";

/**
 * Canonical data-mark glyph. One dot style across every track in the
 * system: filled in its axis hue, one diameter per density. Hue says which
 * axis, position says how much. No open/filled or double-dot variants, and
 * no halo — the reserved white ring belongs to the two-mark pair only.
 */
export function dataDotSize(density: "default" | "compact" | "heavy" | "heavyCompact") {
  if (density === "heavy") return "h-[22px] w-[22px]";
  if (density === "heavyCompact") return "h-[18px] w-[18px]";
  return density === "compact" ? "h-[6px] w-[6px]" : "h-2 w-2";
}
export const DATA_DOT_KEYLINE = "rounded-full ring-2 ring-white";
export type BaselineState = "mature" | "young" | "building";

function axisColor(axis: Axis) {
  if (axis === "work") return "var(--color-axis-work)";
  if (axis === "cost") return "var(--color-axis-cost)";
  return "var(--color-data-ink)";
}

function axisDeltaInk(axis: Axis) {
  if (axis === "work") return "var(--color-axis-work-ink)";
  if (axis === "cost") return "var(--color-axis-cost-ink)";
  return "var(--color-text-secondary)";
}

/* ------------------------------------------------------------------ */
/* Geometry — one table, two densities. Nothing shrinks into illegibility. */
/* ------------------------------------------------------------------ */
export const TRACK_GEO = {
  default: { h: 42, y: 30, band: 16, tick: 22, cap: 8, dot: 8, delta: 11, deltaUp: 21 },
  compact: { h: 34, y: 25, band: 12, tick: 18, cap: 7, dot: 6, delta: 10, deltaUp: 17 },
} as const;
const GEO = TRACK_GEO;

function fmt(n: number) {
  return Math.abs(n) >= 1000 || Number.isInteger(n)
    ? n.toLocaleString()
    : n.toFixed(1);
}

/* ------------------------------------------------------------------ */
/* Endpoints — anatomy of every track                                   */
/* ------------------------------------------------------------------ */
export function endpointFontSize(size: "default" | "compact") {
  return size === "compact" ? 9 : 10;
}

/** Scale numeral riding just outside an end cap, centred on the hairline. */
export function TrackEndpoint({
  label,
  geo,
  size = "default",
  hidden = false,
}: {
  label: string;
  geo: { h: number; y: number };
  size?: "default" | "compact";
  hidden?: boolean;
}) {
  const fs = endpointFontSize(size);
  return (
    <span
      className="type-num shrink-0 whitespace-nowrap"
      aria-hidden={hidden || undefined}
      style={{
        fontSize: fs,
        lineHeight: `${fs + 2}px`,
        color: "var(--color-text-tertiary)",
        transform: `translateY(${geo.y - geo.h / 2}px)`,
        visibility: hidden ? "hidden" : undefined,
      }}
    >
      {label}
    </span>
  );
}

/* ------------------------------------------------------------------ */
/* TrackAxis — the tick label only, uttered once per scale group        */
/* ------------------------------------------------------------------ */
export type TrackAxisProps = {
  mode: "deviation" | "shared";
  windowPct?: number;
  scaleMin?: number;
  scaleMax?: number;
  unit?: string;
  /** Label sitting over the reference tick, e.g. "100 · typical match". */
  tickLabel?: string;
  /** Shared mode: the reference value the tick label sits over. */
  reference?: number;
  size?: "default" | "compact";
  /** Reserve the same right-hand value column the rows use. */
  withValueColumn?: boolean;
  /** Optional left gutter matching the row's label column width, in px. */
  leadingGutter?: number;
};

export function TrackAxis({
  mode,
  windowPct = 0.4,
  scaleMin = 0,
  scaleMax = 1,
  unit,
  tickLabel,
  reference = 100,
  size = "default",
  withValueColumn = true,
  leadingGutter,
}: TrackAxisProps) {
  // Endpoints now live on every track; an axis with no tick label has
  // nothing left to say.
  if (!tickLabel) return null;

  const deviation = mode === "deviation";
  const fs = endpointFontSize(size);
  const lo = deviation ? `${Math.round((1 - windowPct) * 100)}` : `${fmt(scaleMin)}`;
  const hi = deviation
    ? `${Math.round((1 + windowPct) * 100)}`
    : `${fmt(scaleMax)}${unit ? ` ${unit}` : ""}`;
  const refPct = deviation
    ? 50
    : Math.max(0, Math.min(100, ((reference - scaleMin) / (scaleMax - scaleMin)) * 100));

  return (
    <div className="flex items-end gap-3">
      {leadingGutter ? <div style={{ width: leadingGutter }} className="shrink-0" /> : null}
      {/* mirror the row's endpoint gutters so the tick label stays over the tick */}
      <div className="flex flex-1 items-end gap-1">
        <span
          className="type-num shrink-0 whitespace-nowrap"
          style={{ fontSize: fs, visibility: "hidden" }}
          aria-hidden
        >
          {lo}
        </span>
        <div className="relative flex-1" style={{ height: fs + 4 }}>
          <span
            className="type-num absolute bottom-0 whitespace-nowrap"
            style={{
              fontSize: fs,
              left: `${refPct}%`,
              transform: "translateX(-50%)",
              color: "var(--color-text-secondary)",
            }}
          >
            {tickLabel}
          </span>
        </div>
        <span
          className="type-num shrink-0 whitespace-nowrap"
          style={{ fontSize: fs, visibility: "hidden" }}
          aria-hidden
        >
          {hi}
        </span>
      </div>
      {withValueColumn ? <div className="min-w-[130px] shrink-0" /> : null}
    </div>
  );
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
  /** Sessions banked so far, printed in the building-baseline state. */
  baselineSessions?: number;
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
  baselineSessions = 3,
  size = "default",
  showValue,
  showDelta = true,
  deltaTone = "default",
  qualified = true,
}: ValueOnTrackProps) {
  const compact = size === "compact";
  const g = compact ? GEO.compact : GEO.default;
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
  let bandLoLabel: string;
  let bandHiLabel: string;

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
    bandLoLabel = `${Math.round((1 - halfBandFrac) * 100)}`;
    bandHiLabel = `${Math.round((1 + halfBandFrac) * 100)}`;
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
    bandLoLabel = fmt(reference - halfBandAbs);
    bandHiLabel = fmt(reference + halfBandAbs);
  }

  const deltaInk =
    deltaTone === "escalate"
      ? "var(--color-escalate-ink)"
      : deltaTone === "notice"
        ? "var(--color-notice-ink)"
        : axisDeltaInk(axis);

  const hoverText = `normal range ${bandLoLabel}–${bandHiLabel} · typical ${fmt(reference)}${unit ? ` ${unit}` : ""}`;

  // Endpoint numerals — anatomy of every track.
  const loLabel =
    mode === "deviation"
      ? `${Math.round((1 - windowPct) * 100)}`
      : fmt(scaleMin ?? 0);
  const hiLabel =
    mode === "deviation"
      ? `${Math.round((1 + windowPct) * 100)}`
      : `${fmt(scaleMax ?? 1)}${unit ? ` ${unit}` : ""}`;

  return (
    <div className="flex items-center gap-3">
      <div className="flex flex-1 items-center gap-1">
      <TrackEndpoint label={loLabel} geo={g} size={size} />
      <div className="group relative flex-1" style={{ height: g.h }}>

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

        {withheld ? (
          <span
            className="absolute left-1/2 -translate-x-1/2 -translate-y-1/2 whitespace-nowrap px-2 text-[11px]"
            style={{
              top: g.y,
              color: "var(--color-text-tertiary)",
              backgroundColor: "var(--color-surface-card)",
            }}
          >
            {copy("canonical.vot.baselineBuilding")} · {baselineSessions} of 5 sessions
          </span>
        ) : (
          <>
            {/* reference band — a bounded interval */}
            <div
              className="absolute"
              style={{
                left: `${bandLeftPct}%`,
                width: `${bandRightPct - bandLeftPct}%`,
                top: g.y - g.band / 2,
                height: g.band,
                backgroundColor: "var(--color-reference-band)",
                borderLeft: "1px solid var(--color-slate-300)",
                borderRight: "1px solid var(--color-slate-300)",
                borderRadius: 2,
              }}
              aria-label={copy("vot.bandHover")}
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
              title={scaleLabel}
            />
            {/* clamp break glyph — two slanted strokes just inside the end */}
            {clamped && (
              <div
                className="absolute"
                style={{
                  left: clampDir === "high" ? undefined : 10,
                  right: clampDir === "high" ? 10 : undefined,
                  top: g.y - 5,
                  height: 10,
                  width: 9,
                }}
                aria-hidden
              >
                <div
                  className="absolute left-0 top-0"
                  style={{
                    height: 10,
                    width: 1,
                    backgroundColor: "var(--color-trust-dot)",
                    transform: "rotate(24deg)",
                  }}
                />
                <div
                  className="absolute right-0 top-0"
                  style={{
                    height: 10,
                    width: 1,
                    backgroundColor: "var(--color-trust-dot)",
                    transform: "rotate(24deg)",
                  }}
                />
              </div>
            )}
            {/* session mark */}
            <div
              className="absolute -translate-x-1/2 rounded-full"
              style={{
                left: `${posPct}%`,
                top: g.y - g.dot / 2,
                height: g.dot,
                width: g.dot,
                backgroundColor: color,
              }}
              aria-label={copy("canonical.vot.value")}
            />
            {/* delta rides the mark */}
            {showDelta && (
              <span
                className="type-num absolute -translate-x-1/2 whitespace-nowrap font-medium"
                style={{
                  left: `${posPct}%`,
                  top: g.y - g.deltaUp - g.delta,
                  fontSize: g.delta,
                  lineHeight: `${g.delta + 2}px`,
                  color: deltaInk,
                }}
                title={deltaAbs ? `Δ ${deltaAbs}` : undefined}
              >
                {deltaLabel}
              </span>
            )}
            {/* transient hover — only the numbers not on canvas */}
            <div
              className="type-num pointer-events-none absolute left-1/2 z-10 hidden -translate-x-1/2 whitespace-nowrap rounded px-2 py-1 text-[10.5px] group-hover:block"
              style={{
                top: g.y + 8,
                backgroundColor: "var(--color-slate-800)",
                color: "#FFFFFF",
              }}
              role="tooltip"
            >
              {hoverText}
            </div>
          </>
        )}
      </div>

      {withValue && (
        <div className="flex min-w-[130px] items-baseline justify-end gap-2">
          {withheld ? (
            <span className="type-num text-[13px]" style={{ color: "var(--color-text-tertiary)" }}>
              —
            </span>
          ) : (
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
                className="type-num text-[13px] font-semibold"
                style={{ color: qualified ? "var(--color-text-primary)" : "var(--color-text-tertiary)" }}
              >
                {value.toLocaleString()}
              </span>
              {unit ? (
                <span
                  className="type-num text-[10.5px]"
                  style={{ color: "var(--color-text-tertiary)" }}
                >
                  {unit}
                </span>
              ) : null}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
