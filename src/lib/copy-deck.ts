/**
 * ST2 — single copy source.
 *
 * Every user-facing sentence, section header, descriptor, empty-state,
 * tooltip, and legend string ships from this module. Components MUST NOT
 * declare inline user-facing sentences. Strings not present here do not ship.
 *
 * Populate from ST2_Copy_Deck.md (the canonical deck). Until an entry is
 * transcribed, `copy(...)` returns a visible `⟨missing:key⟩` marker in dev
 * so any un-transcribed surface is caught by eye during review.
 *
 * Formatter rules (§ Prompt 0):
 *  - `count(n, one, many)` returns `""` when n === 0 (zero never prints).
 *  - `rowCondition(...)` is a helper for row-level flags: emit ONCE per row,
 *    never per cell. (Consumed by table components; here as a marker.)
 *
 * Baseline: building-baseline minimum = 5 sessions (Köhler currently 3 of 5).
 */

export const BUILDING_BASELINE_MIN_SESSIONS = 5;

/**
 * Copy registry. Keys use `section.subkey` dotted paths.
 * Add entries by transcribing directly from ST2_Copy_Deck.md.
 */
export const COPY: Record<string, string> = {
  // deck entries land here — one line per string, exact wording from the deck
};

/**
 * Resolve a copy key. Missing keys return a visible marker so the gap is
 * obvious in preview and impossible to miss in review.
 */
export function copy(key: string): string {
  const v = COPY[key];
  if (v === undefined) {
    if (import.meta.env.DEV) return `⟨missing:${key}⟩`;
    return "";
  }
  return v;
}

/**
 * Zero-count formatter. Returns "" when n is 0 so callers can render nothing.
 * Use when a badge/label would otherwise say "0 …".
 */
export function count(n: number, one: string, many: string): string {
  if (!n || n <= 0) return "";
  return `${n} ${n === 1 ? one : many}`;
}

/**
 * Marker helper — a row-level condition should be produced ONCE per row and
 * threaded through to the row's flag column, never re-computed per cell.
 * (No behaviour; documents the contract for row renderers.)
 */
export function rowCondition<T>(perRow: T): T {
  return perRow;
}
