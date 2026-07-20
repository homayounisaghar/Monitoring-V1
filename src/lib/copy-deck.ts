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
  // DRAFT — WP-3.3: per-scenario closer for training_day.
  "attention.closer.trainingDay": "Intensive training session — external work ran ahead of cardio cost, led by the front line.",
  // Pattern for combined-flag rows (replaces "+1 more"). The delta lives
  // once, at right, in the row's own render.
  "attention.combinedMetrics.example": "Sprint distance · HSR",
  "attention.basisNote": "Flags — each athlete vs their own typical for this day type; the reference above doesn't move them.",
  "attention.baselineThin.headlineTemplate": "Building baselines — {n} of {total} comparable",
  "attention.baselineThin.leadTemplate": "Building baselines — {n} of {total}",

  // ---------- Attention · all-clear state ----------
  "attention.allClear.link": "Squad summary ↓",

  // ---------- Attention · coverage-thin state (headline) ----------
  // DRAFT — {below} = count of athletes under 80% HR coverage, {total} = squad size.
  "attention.covThin.headlineTemplate": "Can't read the squad today — {below} of {total} under 80% HR coverage",

  // ---------- Legend (the key) ----------
  "legend.band": "band — their normal range",
  "legend.tick": "tick — reference",
  "legend.dot": "dot — this session",
  "legend.trustDot": "trust dot — coverage under 80%",
  "legend.flagGlyph": "flag glyph — flagged in Attention",
  "legend.gapPair": "pair — external + internal, gap in pts",

  // ---------- Legend — Longitudinal (product-wide corrected wording;
  // still needs propagating back to Session's legend at a later pass). ----------
  "legend.basis": "typical, like-for-like — each day vs its own typical",
  "legend.ext": "blue — external · work",
  "legend.int": "purple — internal · cost",
  "legend.hollow": "hollow — coverage below 80%",
  "legend.cov": "· NN% cov — coverage, beside the value",
  "legend.hatch": "hatch — unconfirmed",
  "legend.break": "break — beyond chart range, value printed",
  "legend.gap": "dash — no data recorded",
  "legend.rest": "dot on the baseline — rest day",
  "legend.matchMark": "MD — match day",
  "legend.flag": "flag — flagged in the session's Attention",

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

  // ---------- Periods (rebuilt lane view) ----------
  "periods.axisNote": "per-min rate · 100 = session avg · chart range 30–150",
  "periods.gap.label": "gap E−I · pts",
  "periods.peakChip": "peak",
  "periods.unit.m": "m",
  "periods.unit.ct": "ct",
  "periods.unit.cl": "CL",
  "periods.legend.states": "thin coverage · ring + hatch unconfirmed · break = beyond chart range, exact % shown · — no data",
  "periods.legend.gap": "gap E−I = distance rate − Cardio Load rate · hover a block for detail",
  "periods.halfLabel.first": "1st half · 0–45′",
  "periods.halfLabel.second": "2nd half · 45–95′",
  "periods.blockLabelTemplate": "{start}–{end}′",
  "periods.blockLabelTerminalTemplate": "{start}′+ · added time",
  "periods.internalNotMeasured": "Cardio Load not measured this session",
  "periods.hover.pastScale": "beyond chart range (30–150)",
  "periods.hover.unconfirmed": "unconfirmed",
  "periods.hover.belowFloorTemplate": "coverage {cov} of {total} · below floor {floor}",
  "periods.hover.coverageTemplate": "coverage {cov} of {total}",
  "periods.hover.covOfTemplate": "{cov} of {total}",
  "periods.hover.peakLine": "peak — highest Cardio Load per-min rate",
  "periods.hover.gapVsDist": "vs distance rate",
  "periods.hover.internalAbsent": "internal absent",
  "periods.hover.covFootTemplate": "internal session avg over covered {covered}′ of {total}′",
  "periods.hover.includesUnconfirmed": "includes unconfirmed 60–75′",
  "periods.hover.halvesCovTemplate": "covers {covered}′ of {total}′ · none in 90–95′+",
  "periods.hover.rowLabel.gap": "Gap E−I",

  "vot.bandHover": "reference band — typical variation",
  "vot.baselineHover": "Baseline still building — no reference yet",
  "srpe.respondersHover": "Mean of responders only",
  "participation.zerosHover": "Categories with zero athletes",
  "control.reset": "Reset to default",
  "control.legend": "How to read this",
  "control.clearAll": "Clear all",
  "control.filter": "Filter",
  "control.apply": "Apply",
  "control.cancel": "Cancel",
  "squad.dnpRow": "did not participate",
  "squad.dnpChart": "DNP",
  "squad.avgRow": "Squad avg",
  "gap.typicalHover": "their typical",

  // ---------- Reading-line menu glosses (per option kind) ----------
  "readingLine.cohortGloss": "cohort — same position group, this season",
  // Reference (per-athlete) glosses — DRAFT
  "readingLine.gloss.own_typical": "their own typical for sessions of this type",
  "readingLine.gloss.positional": "typical for their position group",
  "readingLine.gloss.cohort": "the squad's average for sessions of this type",
  "readingLine.gloss.last_n": "average of their last five matches",
  "readingLine.gloss.season": "their season average for sessions of this type",
  "readingLine.gloss.same_opponent": "their output vs this opponent before",
  // Benchmark (squad) glosses — DRAFT
 "readingLine.bgloss.typical_daytype": "a typical session of this day type",
 "readingLine.bgloss.typical_match": "a typical match of this type",
  "readingLine.bgloss.last_match": "the squad's previous match",
  "readingLine.bgloss.last_5": "average of the squad's last five matches",
  "readingLine.bgloss.same_opponent": "squad output vs this opponent before",

  // ---------- Filter panel ----------
  "filter.group.timeWindow": "Time window",

  // ---------- Unscoped-section micro-tag ----------
  "scope.unscopedTag": "all 18 · full match",

  // ---------- Scope — empty ----------
  "scope.emptyLine": "No athletes in this filter",

  // ---------- Share ----------
  "share.includesState": "Link opens this exact view — filters, comparison, sort included",

  // ---------- Sidebar ----------
  "sidebar.header": "Sessions",
  "sidebar.searchPlaceholder": "Search sessions",
  "sidebar.searchClear": "Clear search",
  "sidebar.searchEmpty": "No sessions match",

  // ---------- Summary ----------
  // DRAFT — the "vs typical full match" module label.
  "summary.vsFullMatch.label": "Vs typical full match",
  "summary.internalNotMeasured": "not measured this session",
  "summary.zones.typicalTickHover": "typical Z4+Z5 · {pct}%",

  // ---------- Squad ----------
  // Section-header descriptor.
  "squad.section.desc": "Every athlete on this session",
  // Row-level scaled tag pattern; consumers substitute the minutes.
  "squad.row.scaledTagTemplate": "{min}′ · scaled",
  "squad.row.scaledHoverTemplate": "played {min}′ — reference adjusted to minutes",
  // Replaces per-cell "NOT COMPARED".
  "squad.cell.notCompared": "—",
  "squad.cell.notComparedHoverTemplate": "{min}′ — too short to compare",
  // DRAFT — hover for the empty %-mode cell on the building-baseline row.
  "squad.cell.buildingHoverTemplate": "Building baseline · {done} of {min} sessions to minimum history",
  // Column-picker counter.
  "squad.columnPicker.counterTemplate": "{n} / {max}",
  // Full-data pointer.
  "squad.export.link": "Full data in export →",

  // ---------- sRPE empty state ----------
  "srpe.empty": "not collected this session",

  // ---------- Trust — coverage hover ----------
  // DRAFT — used by TrustMark (hover). Consumers pass the number in.
  "trust.coverageHoverTemplate": "{pct}% {of}",

  // ---------- Canonical vocabulary — changes only via Decision Set amendment. ----------
  "canonical.section.attention": "Attention",
  "canonical.section.summary": "Summary",
  "canonical.section.periods": "Periods",
  "canonical.section.squad": "Squad",
  "canonical.section.participation": "Participation",

  "canonical.anchor.attention": "Attention",
  "canonical.anchor.summary": "Summary",
  "canonical.anchor.periods": "Periods",
  "canonical.anchor.squad": "Squad",

  "canonical.axisGroup.externalWork": "External — work",
  "canonical.axisGroup.internalCost": "Internal — cost",
  "canonical.axisGroup.externalWorkLower": "external — work",
  "canonical.axisGroup.internalCostLower": "internal — cost",

  "canonical.filter.button": "Filter",
  "canonical.filter.group.participation": "Participation",
  "canonical.filter.group.position": "Position",
  "canonical.filter.group.timeWindow": "Time window",
  "canonical.filter.group.athletes": "Athletes",
  "canonical.filter.granularity.halves": "Halves",
  "canonical.filter.granularity.blocks15": "15' blocks",
  "canonical.filter.done": "Done",
  "canonical.filter.all": "All",
  "canonical.filter.findAthletes": "Find athletes…",
  "canonical.filter.showingPrefix": "Showing",
  "canonical.filter.showingConnector": "of",
  "canonical.filter.athletesChip.one": "athlete",
  "canonical.filter.athletesChip.many": "athletes",

  "canonical.eventBanner.match": "Match",
  "canonical.eventBanner.training": "Training",
  "canonical.eventBanner.editSession": "Edit session",
  "canonical.eventBanner.shareExport": "Share / export",
  "canonical.eventBanner.exportCsv": "Export CSV",
  "canonical.eventBanner.exportPdf": "Export PDF",
  "canonical.eventBanner.copyLink": "Copy link",
  "canonical.eventBanner.totalSuffix": "' total",

  "canonical.readingLine.athletePrefix": "each athlete vs",
  "canonical.readingLine.squadPrefix": "squad vs",
  "canonical.readingLine.separator": "·",
  "canonical.readingLine.default": "default",

  "canonical.periods.subtitle": "— How load was distributed through the match",
  "canonical.periods.tableHead.period": "Period",
  "canonical.periods.tableHead.rate": "per-minute rate — external ● / internal ○",
  "canonical.periods.tableHead.gap": "GAP E−I · pts",
  "canonical.periods.peak": "peak",
  "canonical.periods.sessionAvgSuffix": " · session avg",

  "canonical.summary.subtitlePrefix": "— Squad load vs ",
  "canonical.summary.zones.head": "Z4+Z5 high-intensity share",
  "canonical.summary.zones.typicalPrefix": "typical ",
  "canonical.summary.zones.basis.distance": "Distance",
  "canonical.summary.zones.basis.duration": "Duration",
  "canonical.summary.fullSuffix": "full",
  "canonical.summary.zonesNonePrefix": "none: ",
  "canonical.summary.coverageBelowTemplate": "Below {pct}% coverage",
  "canonical.summary.vsFullMatch.volume": "Volume",
  "canonical.summary.vsFullMatch.intensity": "Intensity",
  "canonical.summary.vsFullMatch.fullMatchScale": "full match",
  "canonical.summary.vsFullMatch.tick0": "0",
  "canonical.summary.vsFullMatch.tick100": "100",
  "canonical.summary.vsFullMatch.tick150": "150",

  "canonical.squad.toolbar.table": "Table",
  "canonical.squad.toolbar.chart": "Chart",
  "canonical.squad.toolbar.absolute": "Absolute",
  "canonical.squad.toolbar.percent": "%",
  "canonical.squad.toolbar.columns": "Columns",
  "canonical.squad.tableHead.athlete": "Athlete",
  "canonical.squad.sortByPrefix": "Sort by ",
  
  "canonical.squad.picker.title": "Columns",
  "canonical.squad.picker.on": "on",
  "canonical.squad.picker.off": "off",
  "canonical.squad.picker.done": "Done",
  "canonical.squad.chart.typicalPrefix": "their typical: ",
  
  
  "canonical.squad.chart.scaledSuffix": " · scaled",

  "canonical.gap.basisPrefix": "basis · ",

  "canonical.vot.value": "value",
  "canonical.vot.reference": "reference",
  "canonical.vot.baselineBuilding": "baseline building",
  "canonical.vot.building": "building",

  "canonical.severity.escalate": "escalate",
  "canonical.severity.notice": "notice",

  "canonical.trust.coverage": "coverage",

  "canonical.attention.pts": "pts",
  "canonical.attention.hrCoverageSuffix": "% HR coverage",
  "canonical.attention.hrCovSuffix": "% HR cov",
  "canonical.attention.flaggedInAttentionSuffix": "flagged in Attention",

  // ---------- Sidebar — scoped sub-lines (owned here, chosen by presence of scope) ----------
  "sidebar.subline.allInWindowTemplate": "all {n} sessions in the window",
  "sidebar.subline.partialTemplate": "{n} of {m} sessions in the {d}-day window",
  "sidebar.overflowTemplate": "…{n} more in the window",
  "sidebar.rowUnconfirmedSuffix": "· unconfirmed",

  // ---------- Longitudinal ----------
  "longi.anchor.summary": "Summary",
  "longi.anchor.days": "Days",
  "longi.anchor.athletes": "Athletes",

  "longi.banner.compositionTemplate": "{days} days · {trainings} trainings · {matches} matches",

  "longi.window.buttonTemplate": "Last {n} days",
  "longi.window.seasonButton": "Season to date",
  "longi.window.opt.7": "Last 7 days",
  "longi.window.opt.14": "Last 14 days",
  "longi.window.opt.28": "Last 28 days",
  "longi.window.opt.season": "Season to date",
  "longi.window.seasonGlossTemplate": "since {date} · {n} wk",

  "longi.scope.benchmarkChip": "squad vs typical, like-for-like",
  "longi.scope.referenceChip": "each athlete vs their typical, day-aware",
  "longi.scope.benchmarkGloss": "each day vs its own typical",
  "longi.benchmark.gap": "further options not yet in copy deck",
  "longi.reference.gap": "six options not yet in copy deck",

  "longi.filter.title": "Filter",
  "longi.filter.group.sessionType": "Session type",
  "longi.filter.opt.matches": "Matches",
  "longi.filter.opt.training": "Training",
  "longi.filter.gap": "further categories not yet in copy deck",
  "longi.filter.chipDismissAria": "dismiss filter",

  // ---------- Longitudinal · Summary section ----------
  "longi.summary.squadLoadHead": "SQUAD LOAD",
  "longi.summary.availHead": "AVAILABILITY",
  "longi.basis.tick": "100 — typical, like-for-like",
  "longi.gauge.tick40": "40",
  "longi.gauge.tick160": "160",
  "longi.gauge.coverageTemplate": "across {n} of {m} sessions",
  "longi.avail.headSuffix": "at Full",
  "longi.avail.subTemplate": "{full} of {possible} · {trainings} training sessions",
  "longi.avail.notInSquad": "not in squad",
  "longi.character.compositionTemplate": "{n} matches in {span}",
  "longi.character.compositionOne": "One match in {span}",
  "longi.character.compositionNone": "No matches in {span}",
  "longi.character.span.7": "one week",
  "longi.character.span.14": "two weeks",
  "longi.character.span.28": "four weeks",
  "longi.character.span.seasonTemplate": "{n} weeks",
  "longi.character.fact.rehabOut": "{name} went out through rehab",
  "longi.character.fact.joined": "{name} joined {date}",
  "longi.character.fact.unrecorded": "{weekday} is unrecorded",
  "longi.character.fact.unconfirmed": "{weekday}'s session is not confirmed",

  // ---------- Longitudinal · Days section ----------
  "longi.days.subtitle": "— day by day",
  "longi.days.basisLine": "average per athlete who trained",
  "longi.days.metricMenuHead": "External metric",
  "longi.days.mode.absolute": "ABSOLUTE",
  "longi.days.mode.typical": "VS TYPICAL",
  "longi.days.view.chart": "CHART",
  "longi.days.view.table": "TABLE",
  "longi.days.restLabel": "rest",
  "longi.days.missingLabel": "—",
  "longi.days.matchMark": "MD",
  "longi.days.srpeNotCollected": "not collected",
  "longi.days.srpePartial": "{n} of {m}",
  "longi.days.cov": "· {pct}% cov",
  "longi.days.identity": "{date} · {code} · {n} trained",
  "longi.days.hover.noData": "no data recorded for this day",
  "longi.days.hover.double": "double-session day",
  "longi.days.table.head.date": "DATE",
  "longi.days.table.head.day": "DAY",
  "longi.days.table.head.sessions": "SESSIONS",
  "longi.days.table.head.athletes": "ATHLETES",
  "longi.days.table.head.pctTypical": "% TYPICAL",
  "longi.days.table.average": "Average · {n} days with sessions",
  "longi.days.table.footnote": "average per athlete who trained · a double-session day is one day",
  "longi.days.lane.srpeUnit": "AU · where collected",
  "longi.days.lane.cardioUnit": "AU",

  // ---------- Longitudinal · Athletes section ----------
  "longi.athletes.subtitle":     "— who was there · window totals",
  "longi.athletes.more":         "{n} more athletes · {max} or fewer training sessions missed",
  "longi.athletes.moreNone":     "{n} more athletes · no training sessions missed",
  "longi.athletes.fraction":     "{n} of {m}",
  "longi.athletes.expander":     "Session by session ⌄",
  "longi.wt.title":              "Window totals",
  "longi.basis.tickTable":       "100 — their typical, like-for-like",
  "longi.wt.view.absolute":      "ABSOLUTE",
  "longi.wt.view.typical":       "VS TYPICAL",
  "longi.wt.view.ac":            "A:C",
  "longi.ac.method":             "A:C — 7-day ÷ 28-day average, per metric",
  "longi.wt.withheld.sessions":  "— · {n} of 5 sessions",
  "longi.wt.withheld.ac":        "— · {n} of 28 days",
  "longi.wt.hover.baseline":     "Joined {date} — {n} of 5 sessions; five needed to compare.",
  "longi.wt.hover.ac":           "Joined {date} — {n} of 28 days; A:C needs 28.",
  "longi.wt.squadAvg":           "Squad average · {n} participated",
  "longi.wt.footnote":           "— not submitted / did not participate",
  "longi.wt.footRow":            "did not participate · not in squad",
  "longi.wt.head.sessions":      "SESSIONS",
  "longi.wt.head.minutes":       "MINUTES",
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
