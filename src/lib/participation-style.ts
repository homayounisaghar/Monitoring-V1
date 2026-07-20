/**
 * Participation styles — one map for every surface that draws a participation
 * segment or swatch. Colour carries the category; texture stays as a faint
 * translucent overlay so colour-blind readers keep the same angle/pitch as
 * before.
 *
 * Every hex value lives here and nowhere else. Consumers spread `TAG_STYLE[t]`
 * onto a div's `style` prop. This is a time-boxed demo palette; see
 * ST2_Build_Findings_2026-07-19.md.
 */

import type { CSSProperties } from "react";
import type { ParticipationTag } from "@/lib/session-data";

/** Fixed rendering order. */
export const PARTICIPATION_TAGS: ParticipationTag[] = [
  "Full", "Part", "Modified", "Rehab", "Injury", "Other",
];

/** Raw fills — hex kept only here. */
export const TAG_FILL: Record<ParticipationTag, string> = {
  Full:     "#64748B", // neutral slate
  Part:     "#14B8A6", // present-but-reduced, light (teal)
  Modified: "#0F766E", // present-but-reduced, dark  (teal)
  Rehab:    "#B08968", // unavailable, light          (brown)
  Injury:   "#8A5A44", // unavailable, dark           (brown)
  Other:    "#6B7280", // neutral residual
};

/**
 * Faint white overlay carrying the old stripe angle/pitch as a colour-blind
 * backstop. `Full` and `Other` are flat. Opacity per tag lands within
 * 0.10–0.18 — see findings for why each value.
 */
function stripe(
  angleDeg: number,
  onPx: number,
  offPx: number,
  alpha: number,
): string {
  const c = `rgba(255,255,255,${alpha})`;
  return `repeating-linear-gradient(${angleDeg}deg, ${c} 0 ${onPx}px, transparent ${onPx}px ${onPx + offPx}px)`;
}

const OVERLAY: Partial<Record<ParticipationTag, string>> = {
  Part:     stripe(45, 2, 3, 0.14),   // 45°, 5px pitch
  Modified: stripe(-45, 2, 2, 0.14),  // −45°, 4px pitch
  Rehab:    stripe(90, 2, 3, 0.14),   // 90°, 5px pitch
  Injury:   stripe(0, 3, 4, 0.14),    // 0°, 3px on / 4px off (7px pitch)
};

export const TAG_STYLE: Record<ParticipationTag, CSSProperties> = (() => {
  const out = {} as Record<ParticipationTag, CSSProperties>;
  for (const t of PARTICIPATION_TAGS) {
    out[t] = OVERLAY[t]
      ? { backgroundColor: TAG_FILL[t], backgroundImage: OVERLAY[t] }
      : { backgroundColor: TAG_FILL[t] };
  }
  return out;
})();

/**
 * Not-in-squad costume — no fill, hairline outline. Longitudinal-only.
 */
export const NOT_IN_SQUAD_CLASS = "bg-transparent";
export const NOT_IN_SQUAD_STYLE: CSSProperties = {
  border: "1px solid #CBD5E1",
};
