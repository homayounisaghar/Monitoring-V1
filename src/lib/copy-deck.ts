/**
 * ST2 — single copy source.
 *
 * Transcribed from ST2_Copy_Deck.md (Decision Set §R). Components consume
 * strings from this module; they may NOT declare user-facing sentences
 * inline. Strings not present here do not ship. A string change is a deck
 * diff.
 *
 * Register (§R.B2): the instrument may only NAME, STATE, or OFFER on
 * canvas. Sentence case everywhere; caps-with-tracking is reserved for
 * column heads and axis labels only, never a sentence. A row-level
 * condition renders once per row, never per cell; zero counts never print.
 *
 * Status values are informational: FINAL ships verbatim; DRAFT ships
 * pending review; KEEP means already-shipping wording ratified as-is.
 */

export const BUILDING_BASELINE_MIN_SESSIONS = 5;

/**
 * Copy registry — dotted keys grouped by surface.
 * Values are the exact strings from ST2_Copy_Deck.md.
 */
export const COPY = {
  // ---------- Attention ----------
  "attention.headline.suffix": "to manage",
  "attention.headline.metaTemplate": "{clear} of {total} clear",
  "attention.filtered.escalationOutside": "1 escalation outside this filter — A. Fischer",
  // The single accounting line — one row-level condition per athlete.
  // Names are hover-expandable in the row that consumes this key.
  "attention.accountingLine.prefix": "To check",
  "attention.baseline.suffixTemplate": "baseline, {done} of {min} sessions",
  // The card's only prose — closes the card, replaces the NOTABLE box.
  "attention.closer": "Hard, high-intensity match — external work ran ahead of cardio cost, led by the front line.",
  // Pattern for combined-flag rows (replaces "+1 more"). The delta lives
  // once, at right, in the row's own render.
  "attention.combinedMetrics.example": "Sprint distance · HSR",

  // ---------- Attention · all-clear state ----------
  "attention.allClear.link": "Squad summary ↓",

  // ---------- Attention · coverage-thin state (headline) ----------
  // DRAFT — {below} = count of athletes under 80% HR coverage, {total} = squad size.
  "attention.covThin.headlineTemplate": "Can't read the squad today — {below} of {total} under 80% HR coverage",

  // ---------- Legend (the key) ----------
  "legend.band": "band — his normal range",
  "legend.tick": "tick — reference",
  "legend.dot": "dot — this session",
  "legend.trustDot": "trust dot — coverage under 80%",
  "legend.flagGlyph": "flag glyph — flagged in Attention",

  // ---------- Register-class hovers / labels (v2 + v3) ----------
  "flag.hover": "Flagged in Attention — view",
  "trust.hoverGeneric": "coverage under 80%",
  "columns.capReason": "At the 12-column cap — remove one to add another",
  "chart.captionAbsolute": "Ranked by {metric}",
  "chart.captionPercent": "Ranked by delta · {metric}",
  "chart.noData": "No data on this metric",
  "row.baseline": "building baseline",
  "menu.titleReference": "Reference · per athlete",
  "menu.titleBenchmark": "Benchmark · squad",
  "attention.allClear": "Nothing needs attention · {n} of {total} clear",
  "chart.axisPercentNote": "Each row re-based to its own typical · ticks align at 100%",
  "chart.axisAbsoluteNote": "Shared unit axis · 0 — {max}",
  "periods.peakHover": "highest internal-load rate",
  "periods.gapHover": "external minus internal, in per-minute-rate points",
  "vot.bandHover": "reference band — typical variation",
  "vot.baselineHover": "Baseline still building — no reference yet",
  "srpe.respondersHover": "Mean of responders only",
  "participation.zerosHover": "Categories with zero athletes",
  "control.reset": "Reset to default",
  "control.legend": "How to read this",
  "control.clearAll": "Clear all",
  "squad.dnpRow": "did not participate",
  "squad.dnpChart": "DNP",
  "squad.avgRow": "Squad avg",
  "gap.typicalHover": "his typical",

  // ---------- Reading-line menu glosses (per option kind) ----------
  "readingLine.cohortGloss": "cohort — same position group, this season",
  // Reference (per-athlete) glosses — DRAFT
  "readingLine.gloss.own_typical": "his usual output for this match type",
  "readingLine.gloss.positional": "typical for his position group",
  "readingLine.gloss.cohort": "same position group, this season",
  "readingLine.gloss.last_n": "average of his last five matches",
  "readingLine.gloss.season": "his rolling season average",
  "readingLine.gloss.same_opponent": "his output vs this opponent before",
  // Benchmark (squad) glosses — DRAFT
  "readingLine.bgloss.typical_match": "a typical match of this type",
  "readingLine.bgloss.last_match": "the squad's previous match",
  "readingLine.bgloss.last_5": "average of the squad's last five matches",
  "readingLine.bgloss.same_opponent": "squad output vs this opponent before",

  // ---------- Filter panel ----------
  "filter.group.timeWindow": "Time window",

  // ---------- Unscoped-section micro-tag ----------
  "scope.unscopedTag": "all 18 · full match",

  // ---------- Sidebar ----------
  "sidebar.header": "Sessions",

  // ---------- Summary ----------
  // DRAFT — the "vs typical full match" module label.
  "summary.vsFullMatch.label": "Vs typical full match",

  // ---------- Squad ----------
  // Section-header descriptor.
  "squad.section.desc": "Every athlete on this session",
  // Row-level scaled tag pattern; consumers substitute the minutes.
  "squad.row.scaledTagTemplate": "{min}′ · scaled",
  // Replaces per-cell "NOT COMPARED".
  "squad.cell.notCompared": "—",
  "squad.cell.notComparedHoverTemplate": "{min}′ — too short to compare",
  // Column-picker counter.
  "squad.columnPicker.counterTemplate": "{n} / {max}",
  // Full-data pointer.
  "squad.export.link": "Full data in export →",

  // ---------- sRPE empty state ----------
  "srpe.empty": "not collected this session",

  // ---------- Trust — coverage hover ----------
  // DRAFT — used by TrustMark (hover). Consumers pass the number in.
  "trust.coverageHoverTemplate": "{pct}% {of}",
} as const satisfies Record<string, string>;

export type CopyKey = keyof typeof COPY;

/**
 * Resolve a copy key. Missing keys return a visible marker in dev so gaps
 * are impossible to miss in review; in production they render as empty
 * (per doctrine: strings not in the deck do not ship).
 */
export function copy(key: CopyKey): string;
export function copy(key: string): string;
export function copy(key: string): string {
  const v = (COPY as Record<string, string>)[key];
  if (v === undefined) {
    if (import.meta.env.DEV) return `⟨missing:${key}⟩`;
    return "";
  }
  return v;
}

/**
 * Fill `{token}` slots in a template string with values. Missing values
 * are left as `{token}` in dev so the gap is visible; stripped in prod.
 */
export function tmpl(key: CopyKey | string, vars: Record<string, string | number>): string {
  const src = copy(key);
  return src.replace(/\{(\w+)\}/g, (_, k) => {
    const v = vars[k];
    if (v == null) return import.meta.env.DEV ? `{${k}}` : "";
    return String(v);
  });
}

/**
 * Zero-count formatter. Returns "" when n is 0 so callers can render
 * nothing — a count of zero never prints (§Prompt 0.5).
 */
export function count(n: number, one: string, many: string): string {
  if (!n || n <= 0) return "";
  return `${n} ${n === 1 ? one : many}`;
}

/**
 * Marker helper — a row-level condition is produced ONCE per row and
 * threaded through, never re-computed per cell (§Prompt 0.5).
 */
export function rowCondition<T>(perRow: T): T {
  return perRow;
}
