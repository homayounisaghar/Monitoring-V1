/**
 * Longitudinal — Summary section.
 *
 * One card, two panes, one sentence beneath.
 *   Left  · SQUAD LOAD    — Volume + Intensity on a shared 40–160 track.
 *   Right · AVAILABILITY  — 52px "Full %" + stacked participation bar.
 *   Foot  · character line — the page's only sentence, generated from data.
 *
 * Category carried by texture, not hue. Number formatting is deterministic
 * (no toLocaleString anywhere in this file).
 */
import { copy, tmpl } from "@/lib/copy-deck";
import { ValueOnTrack } from "@/components/data/ValueOnTrack";
import {
  PARTICIPATION_TAGS,
  TAG_TEXTURE,
  NOT_IN_SQUAD_CLASS,
  NOT_IN_SQUAD_STYLE,
} from "@/lib/participation-style";
import {
  availability,
  squadLoadGauges,
  windowComposition,
  daySeries,
  type LongiWindow,
  type Horizon,
} from "@/lib/longitudinal-data";
import {
  demoAthletes,
  demoSessions,
  recordsForAthlete,
} from "@/lib/demo-library";
import { dayMonthLong, weekdayLong } from "@/lib/format-date";
import type { ParticipationTag } from "@/lib/session-data";

const WORDS = [
  "zero", "one", "two", "three", "four", "five", "six",
  "seven", "eight", "nine", "ten", "eleven", "twelve",
];

function nWord(n: number): string {
  if (n >= 0 && n <= 12) return WORDS[n];
  return String(n);
}
function cap(s: string): string {
  return s.length === 0 ? s : s[0].toUpperCase() + s.slice(1);
}
function surname(name: string): string {
  // "M. Lange" → "Lange", "B. Köhler" → "Köhler".
  const parts = name.trim().split(/\s+/);
  return parts[parts.length - 1];
}

/* ─────────────────────────── section ─────────────────────────── */

export function SummarySection({
  window: w,
  horizon,
}: {
  window: LongiWindow;
  horizon: Horizon;
}) {
  return (
    <section id="summary" className="scroll-mt-28">
      <h2
        className="type-section-h mb-4"
        style={{ color: "var(--color-text-primary)" }}
      >
        {copy("longi.anchor.summary")}
      </h2>
      <div
        className="surface-card overflow-hidden rounded-lg"
        style={{
          backgroundColor: "var(--color-surface-card)",
          border: "1px solid var(--color-border)",
        }}
      >
        <div className="grid grid-cols-2 gap-x-10 gap-y-6 p-6">
          <SquadLoadPane window={w} />
          <AvailabilityPane window={w} />
        </div>
        <CharacterFoot window={w} horizon={horizon} />
      </div>
    </section>
  );
}

/* ─────────────────────────── left pane ─────────────────────────── */

function SquadLoadPane({ window: w }: { window: LongiWindow }) {
  const g = squadLoadGauges(w);

  const withheld = g.state === "withheld";
  const volumeInt = !withheld ? Math.round(g.volumePct) : null;
  const intensityInt = !withheld ? Math.round(g.intensityPct) : null;
  const showCoverage =
    g.state === "computed"
      ? g.contributingSessions < g.windowSessions
      : true; // withheld branch always prints coverage

  return (
    <div>
      <div className="mb-4 flex items-center gap-2">
        <span
          className="h-2 w-2 rounded-full"
          style={{ backgroundColor: "var(--color-axis-work)" }}
          aria-hidden
        />
        <span
          className="type-microcaps"
          style={{ color: "var(--color-text-secondary)" }}
        >
          {copy("longi.summary.squadLoadHead")}
        </span>
      </div>

      <div className="space-y-4">
        <GaugeRow
          label={copy("canonical.summary.vsFullMatch.volume")}
          value={volumeInt}
        />
        <GaugeRow
          label={copy("canonical.summary.vsFullMatch.intensity")}
          value={intensityInt}
        />
      </div>

      {/* Under the pair: end labels, tick label, coverage line. */}
      <div className="mt-3">
        <div
          className="flex justify-between type-num text-[10.5px]"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          <span>{copy("longi.gauge.tick40")}</span>
          <span className="type-data-label">{copy("longi.basis.tick")}</span>
          <span>{copy("longi.gauge.tick160")}</span>
        </div>
        {showCoverage && (
          <div
            className="mt-2 text-[11.5px]"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            {tmpl("longi.gauge.coverageTemplate", {
              n: g.contributingSessions,
              m: g.windowSessions,
            })}
          </div>
        )}
      </div>
    </div>
  );
}

function GaugeRow({ label, value }: { label: string; value: number | null }) {
  return (
    <div className="space-y-1">
      <div className="flex items-baseline justify-between">
        <span
          className="type-data-label"
          style={{ color: "var(--color-text-secondary)" }}
        >
          {label}
        </span>
        <span
          className="type-num text-[25px] font-semibold leading-none"
          style={{ color: "var(--color-text-primary)" }}
        >
          {value == null ? "—" : String(value)}
        </span>
      </div>
      {value == null ? (
        // Withheld: draw the track (band only) with no reference tick or dot.
        <div className="relative h-5 flex-1">
          <div
            className="absolute left-0 right-0 top-1/2 h-[6px] -translate-y-1/2 rounded-full"
            style={{ backgroundColor: "var(--color-data-band)" }}
          />
        </div>
      ) : (
        <ValueOnTrack
          mode="shared"
          axis="work"
          value={value}
          reference={100}
          scaleMin={40}
          scaleMax={160}
          referenceBandPct={6}
          scaleLabel={copy("longi.basis.tick")}
          size="compact"
          showValue={false}
          showDelta={false}
        />
      )}
    </div>
  );
}

/* ─────────────────────────── right pane ─────────────────────────── */

function AvailabilityPane({ window: w }: { window: LongiWindow }) {
  const av = availability(w);
  const pct = Math.round(av.fullOfPossiblePct);
  const possible = av.possibleTrainingSessions;

  // Segments in fixed order, then remainder as "not in squad".
  const tagSegments: { key: ParticipationTag; count: number }[] = [];
  let tagged = 0;
  for (const t of PARTICIPATION_TAGS) {
    const c = av.tagCounts[t] ?? 0;
    if (c > 0) tagSegments.push({ key: t, count: c });
    tagged += c;
  }
  const remainder = Math.max(0, possible - tagged);
  const totalForBar = tagged + remainder;

  return (
    <div>
      <div className="mb-4 flex items-center gap-2">
        <span
          className="type-microcaps"
          style={{ color: "var(--color-text-secondary)" }}
        >
          {copy("longi.summary.availHead")}
        </span>
      </div>

      <div className="flex items-baseline gap-2">
        <span
          className="type-num font-semibold leading-none"
          style={{ color: "var(--color-text-primary)", fontSize: "52px" }}
        >
          {String(pct)}%
        </span>
        <span
          className="type-data-label"
          style={{ color: "var(--color-text-secondary)" }}
        >
          {copy("longi.avail.headSuffix")}
        </span>
      </div>

      <div
        className="mt-2 text-[12px]"
        style={{ color: "var(--color-text-tertiary)" }}
      >
        {tmpl("longi.avail.subTemplate", {
          full: String(av.fullTrainingSessions),
          possible: String(possible),
          trainings: String(av.trainingSessions),
        })}
      </div>

      {/* Stacked participation bar. */}
      <div
        className="mt-4 relative flex h-8 overflow-hidden rounded-md"
        style={{ border: "1px solid var(--color-border)" }}
      >
        {tagSegments.map((seg, i) => {
          const width = (seg.count / totalForBar) * 100;
          const isLast = i === tagSegments.length - 1 && remainder === 0;
          return (
            <div
              key={seg.key}
              className={`relative ${TAG_TEXTURE[seg.key]}`}
              style={{
                width: `${width}%`,
                borderRight: isLast ? undefined : "1px solid var(--color-border)",
              }}
              title={`${seg.key} — ${seg.count}`}
              aria-label={`${seg.key}: ${seg.count}`}
            />
          );
        })}
        {remainder > 0 && (
          <div
            className={`relative ${NOT_IN_SQUAD_CLASS}`}
            style={{
              width: `${(remainder / totalForBar) * 100}%`,
              ...NOT_IN_SQUAD_STYLE,
              borderTop: "none",
              borderRight: "none",
              borderBottom: "none",
            }}
            title={`${copy("longi.avail.notInSquad")} — ${remainder}`}
            aria-label={`${copy("longi.avail.notInSquad")}: ${remainder}`}
          />
        )}
      </div>

      {/* Count row — swatch + tag + count, in the same fixed order. */}
      <div className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1.5">
        {tagSegments.map((seg, idx) => (
          <span key={seg.key} className="inline-flex items-center gap-x-3">
            {idx > 0 && (
              <span
                className="type-num text-[12px]"
                style={{ color: "var(--color-text-tertiary)" }}
                aria-hidden
              >
                ·
              </span>
            )}
            <span
              className="inline-flex items-center gap-1.5 text-[12px]"
              style={{ color: "var(--color-text-secondary)" }}
            >
              <span
                className={`h-2.5 w-2.5 rounded-sm ${TAG_TEXTURE[seg.key]}`}
                aria-hidden
              />
              <span>{seg.key}</span>
              <span
                className="type-num"
                style={{ color: "var(--color-text-primary)" }}
              >
                {String(seg.count)}
              </span>
            </span>
          </span>
        ))}
        {remainder > 0 && (
          <span className="inline-flex items-center gap-x-3">
            {tagSegments.length > 0 && (
              <span
                className="type-num text-[12px]"
                style={{ color: "var(--color-text-tertiary)" }}
                aria-hidden
              >
                ·
              </span>
            )}
            <span
              className="inline-flex items-center gap-1.5 text-[12px]"
              style={{ color: "var(--color-text-secondary)" }}
            >
              <span
                className={`h-2.5 w-2.5 rounded-sm ${NOT_IN_SQUAD_CLASS}`}
                style={NOT_IN_SQUAD_STYLE}
                aria-hidden
              />
              <span>{copy("longi.avail.notInSquad")}</span>
              <span
                className="type-num"
                style={{ color: "var(--color-text-primary)" }}
              >
                {String(remainder)}
              </span>
            </span>
          </span>
        )}
      </div>
    </div>
  );
}

/* ─────────────────────────── character line ─────────────────────────── */

type Fact = string;

function computeFacts(w: LongiWindow): Fact[] {
  const facts: Fact[] = [];

  // (1) Rehab-out: someone whose in-window session tag history has an earlier
  //     Rehab and whose last in-window tag is Injury.
  for (const a of demoAthletes) {
    const tags: { dateISO: string; tag: ParticipationTag }[] = [];
    for (const r of recordsForAthlete(a.id)) {
      if (r.sessionId == null) continue;
      if (r.dateISO < w.startISO || r.dateISO > w.endISO) continue;
      if (r.participation == null) continue;
      tags.push({ dateISO: r.dateISO, tag: r.participation });
    }
    tags.sort((x, y) => x.dateISO.localeCompare(y.dateISO));
    if (tags.length === 0) continue;
    const last = tags[tags.length - 1];
    if (last.tag !== "Injury") continue;
    const earlierHadRehab = tags.slice(0, -1).some((t) => t.tag === "Rehab");
    if (earlierHadRehab) {
      facts.push(
        tmpl("longi.character.fact.rehabOut", { name: surname(a.name) }),
      );
      break;
    }
  }

  // (2) Joined-in-window.
  for (const a of demoAthletes) {
    if (a.joinedISO >= w.startISO && a.joinedISO <= w.endISO) {
      facts.push(
        tmpl("longi.character.fact.joined", {
          name: surname(a.name),
          date: dayMonthLong(a.joinedISO),
        }),
      );
      break;
    }
  }

  // (3) Unrecorded weekday — only if exactly one missing day.
  const missing = daySeries(w).filter((d) => d.kind === "missing");
  if (missing.length === 1) {
    facts.push(
      tmpl("longi.character.fact.unrecorded", {
        weekday: weekdayLong(missing[0].dateISO),
      }),
    );
  }

  // (4) Unconfirmed session — only if exactly one.
  const unconfirmed = demoSessions.filter(
    (s) => s.dateISO >= w.startISO && s.dateISO <= w.endISO && s.unconfirmed,
  );
  if (unconfirmed.length === 1) {
    facts.push(
      tmpl("longi.character.fact.unconfirmed", {
        weekday: weekdayLong(unconfirmed[0].dateISO),
      }),
    );
  }

  return facts.slice(0, 2);
}

function spanLabel(w: LongiWindow, horizon: Horizon): string {
  if (horizon === 7) return copy("longi.character.span.7");
  if (horizon === 14) return copy("longi.character.span.14");
  if (horizon === 28) return copy("longi.character.span.28");
  const weeks = Math.max(1, Math.round(w.days / 7));
  return tmpl("longi.character.span.seasonTemplate", { n: String(weeks) });
}

export function characterLine(w: LongiWindow, horizon: Horizon): string {
  const comp = windowComposition(w);
  const composition = tmpl("longi.character.compositionTemplate", {
    n: cap(nWord(comp.matchSessions)),
    span: spanLabel(w, horizon),
  });
  const facts = computeFacts(w);
  if (facts.length === 0) return `${composition}.`;
  return `${composition}; ${facts.join(", ")}.`;
}

function CharacterFoot({
  window: w,
  horizon,
}: {
  window: LongiWindow;
  horizon: Horizon;
}) {
  const line = characterLine(w, horizon);
  return (
    <div
      className="border-t px-6 py-3 text-[13px]"
      style={{
        borderColor: "var(--color-border)",
        backgroundColor: "var(--color-slate-50)",
        color: "var(--color-text-primary)",
      }}
    >
      {line}
    </div>
  );
}
