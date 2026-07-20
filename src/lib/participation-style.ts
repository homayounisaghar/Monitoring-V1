/**
 * Participation styles — one map for every surface that draws a participation
 * segment or swatch. Lifted out of `SummaryCard.tsx` so Session, Longitudinal
 * Summary, and any future surface render pixel-identically.
 *
 * Category is carried by texture, not hue. The palette lands here at
 * step 5 with the greyscale gate; not now.
 */

import type { ParticipationTag } from "@/lib/session-data";

/** Fixed rendering order. */
export const PARTICIPATION_TAGS: ParticipationTag[] = [
  "Full", "Part", "Modified", "Rehab", "Injury", "Other",
];

// Mid-tone fills — kept below the Summary loudness budget (≤60).
// Category carried by texture, not hue.
export const TAG_TEXTURE: Record<ParticipationTag, string> = {
  Full:     "bg-[color:var(--color-slate-500)]",
  // Part — wider stripe pitch, high-contrast slate pair for arm's-length read.
  Part:     "bg-[color:var(--color-slate-500)] bg-[repeating-linear-gradient(45deg,var(--color-slate-500)_0_5px,var(--color-slate-100)_5px_10px)]",
  Modified: "bg-[color:var(--color-slate-400)] bg-[repeating-linear-gradient(-45deg,var(--color-slate-400)_0_4px,var(--color-slate-200)_4px_8px)]",
  Rehab:    "bg-[color:var(--color-slate-300)] bg-[repeating-linear-gradient(90deg,var(--color-slate-300)_0_5px,var(--color-slate-100)_5px_10px)]",
  // Injury — darker base + lighter stripes; horizontal, distinct from Part.
  Injury:   "bg-[color:var(--color-slate-700)] bg-[repeating-linear-gradient(0deg,var(--color-slate-700)_0_3px,var(--color-slate-200)_3px_7px)]",
  Other:    "bg-[color:var(--color-slate-300)]",
};

/**
 * Not-in-squad costume — no fill, hairline outline. Segment/swatch consumers
 * apply the className *and* the inline style (className alone can't carry an
 * arbitrary CSS variable border reliably across Tailwind versions).
 */
export const NOT_IN_SQUAD_CLASS = "bg-transparent";
export const NOT_IN_SQUAD_STYLE: React.CSSProperties = {
  border: "1px solid var(--color-border)",
};
