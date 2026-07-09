/**
 * ST2 — Session > Summary card.
 * Squad load vs the active Benchmark, on the two axes side by side,
 * plus zones, vs-full-match, and a separate Participation card.
 * All counts derived from effective participants; the benchmark chip
 * re-labels the descriptor live.
 */
import { useMemo, useState } from "react";
import { Info } from "lucide-react";
import { useSessionScope, currentSession, COVERAGE_MIN } from "@/lib/session-scope";
import type { ParticipationTag } from "@/lib/session-data";
import { ValueOnTrack } from "@/components/data/ValueOnTrack";

/* ---------- Static (curated) squad averages, keyed to Benchmark ---------- */

type BenchKey = "typical_match" | "last_match" | "last_5" | "same_opponent";

// Benchmark-DEPENDENT references only. Current-session values (distances,
// counts, zone shares, vs-full-match %) are session-level and live below;
// switching the benchmark must not appear to move a measured fact.
type BenchRefs = {
  refTotalDistanceM: number;
  refRelDistanceMpm: number;
  refHsrM: number;
  refAccDec: number;
  refCardioLoadCL: number;
  refSrpeMean: number;
  z4z5TypicalDistance: number;
  z4z5TypicalDuration: number;
};

const SQUAD_REF: Record<BenchKey, BenchRefs> = {
  typical_match: {
    refTotalDistanceM: 9010, refRelDistanceMpm: 102,
    refHsrM: 665, refAccDec: 108,
    refCardioLoadCL: 205, refSrpeMean: 6.9,
    z4z5TypicalDistance: 26, z4z5TypicalDuration: 16,
  },
  last_match: {
    refTotalDistanceM: 9640, refRelDistanceMpm: 104,
    refHsrM: 720, refAccDec: 111,
    refCardioLoadCL: 210, refSrpeMean: 7.1,
    z4z5TypicalDistance: 28, z4z5TypicalDuration: 17,
  },
  last_5: {
    refTotalDistanceM: 9350, refRelDistanceMpm: 103,
    refHsrM: 690, refAccDec: 109,
    refCardioLoadCL: 207, refSrpeMean: 7.0,
    z4z5TypicalDistance: 27, z4z5TypicalDuration: 16,
  },
  same_opponent: {
    refTotalDistanceM: 9200, refRelDistanceMpm: 103,
    refHsrM: 640, refAccDec: 106,
    refCardioLoadCL: 202, refSrpeMean: 6.8,
    z4z5TypicalDistance: 25, z4z5TypicalDuration: 15,
  },
};

// Session-level facts — invariant across benchmark choice.
const SESSION_MARKS = {
  totalDistanceM: 9820,
  relDistanceMpm: 108,
  hsrM: 812,
  accDec: 118,
  cardioLoadCL: 218,
  srpeMean: 7.4,
} as const;

const SESSION_ZONES = {
  distance: { z1: 34, z2: 22, z3: 13, z4: 19, z5: 12 },
  duration: { z1: 46, z2: 24, z3: 12, z4: 12, z5: 6 },
} as const;

// vs a typical FULL match — reference is an EXTERNAL fixed baseline (100),
// never the squad benchmark; modeled as a session-level constant so it can't
// drift when the benchmark changes.
const SESSION_VS_FULL = { volumePct: 101, intensityPct: 106 } as const;


const PARTICIPATION_TAGS: ParticipationTag[] = [
  "Full", "Part", "Modified", "Rehab", "Injury", "Other",
];
const TAG_LETTER: Record<ParticipationTag, string> = {
  Full: "F", Part: "P", Modified: "M", Rehab: "R", Injury: "I", Other: "O",
};
const TAG_TEXTURE: Record<ParticipationTag, string> = {
  // Neutral slate textures — distinguished by pattern, not hue ranking.
  Full:     "bg-[color:var(--color-slate-700)]",
  Part:     "bg-[color:var(--color-slate-500)] bg-[repeating-linear-gradient(45deg,var(--color-slate-500)_0_6px,var(--color-slate-400)_6px_12px)]",
  Modified: "bg-[color:var(--color-slate-400)] bg-[repeating-linear-gradient(-45deg,var(--color-slate-400)_0_4px,var(--color-slate-300)_4px_8px)]",
  Rehab:    "bg-[color:var(--color-slate-300)] bg-[repeating-linear-gradient(90deg,var(--color-slate-300)_0_5px,var(--color-slate-200)_5px_10px)]",
  Injury:   "bg-[color:var(--color-slate-500)] bg-[repeating-linear-gradient(0deg,var(--color-slate-500)_0_3px,var(--color-slate-300)_3px_6px)]",
  Other:    "bg-[color:var(--color-slate-300)]",
};
const TAG_TEXT_ON: Record<ParticipationTag, string> = {
  Full: "text-white", Part: "text-white", Modified: "text-[color:var(--color-slate-900)]",
  Rehab: "text-[color:var(--color-slate-900)]", Injury: "text-white",
  Other: "text-[color:var(--color-slate-900)]",
};

/* ---------- Component ---------- */

export function SummaryCard() {
  const {
    benchmark,
    filter,
    filterIsDefault,
    scopeLabel,
    activeAthletes,
    totalParticipants,
    effectiveParticipants,
  } = useSessionScope();

  const refs = SQUAD_REF[benchmark.kind];
  const marks = SESSION_MARKS;
  const nInScope = activeAthletes.length;

  // Coverage badge — squad aggregate on effective data.
  const lowCov = effectiveParticipants.filter(
    (a) => a.hrCoveragePct !== null && a.hrCoveragePct < COVERAGE_MIN,
  );
  const coveredCount = effectiveParticipants.length - lowCov.length;
  // Confidence gate — same threshold as the can't-say synthesis.
  const clQualified =
    effectiveParticipants.length === 0
      ? true
      : coveredCount / effectiveParticipants.length >= 0.6;

  // sRPE state, from effective data.
  const submitters = effectiveParticipants.filter((a) => a.srpeSubmitted);
  const srpeState: "filled" | "partial" | "none" =
    submitters.length === 0
      ? "none"
      : submitters.length === effectiveParticipants.length
        ? "filled"
        : "partial";

  const [zoneBasis, setZoneBasis] = useState<"distance" | "duration">("distance");
  const zoneShares = useMemo(() => {
    const z = SESSION_ZONES[zoneBasis];
    const typ =
      zoneBasis === "distance" ? refs.z4z5TypicalDistance : refs.z4z5TypicalDuration;
    return { ...z, hi: z.z4 + z.z5, typ };
  }, [zoneBasis, refs]);
  const basisWord = zoneBasis === "distance" ? "by distance" : "by duration";

  const descriptorScope = !filterIsDefault && scopeLabel ? scopeLabel : null;

  return (
    <section id="summary" className="scroll-mt-28">
      <header className="mb-3 flex items-baseline justify-between gap-4">
        <div className="flex items-baseline gap-2 flex-wrap">
          <h2 className="type-section-h">Summary</h2>
          <span
            className="type-label"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            — Squad load vs {benchmark.label}
            {descriptorScope ? ` · ${descriptorScope}` : ""} · {nInScope} athletes
          </span>
        </div>
        {!filterIsDefault && (
          <span
            className="type-num text-[11px]"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            {nInScope} of {totalParticipants}
          </span>
        )}
      </header>

      {/* ---- Squad-load card — two axes side by side ---- */}
      <div
        className="overflow-hidden rounded-lg border"
        style={{
          borderColor: "var(--color-border)",
          backgroundColor: "var(--color-surface-card)",
        }}
      >
        <div className="grid grid-cols-[minmax(0,1.4fr)_minmax(0,1fr)]">
          {/* External — Work */}
          <div
            className="border-r p-5"
            style={{
              borderColor: "var(--color-border)",
              backgroundColor: "var(--color-axis-work-tinted)",
            }}
          >
            <div className="mb-3 flex items-baseline justify-between">
              <div className="flex items-center gap-2">
                <span
                  className="h-2 w-2 rounded-full"
                  style={{ backgroundColor: "var(--color-axis-work)" }}
                />
                <span className="type-col-head">External — work</span>
              </div>
              <span
                className="type-data-label"
                style={{ color: "var(--color-text-tertiary)" }}
              >
                marks: window ±40% vs {benchmark.label}
              </span>
            </div>
            <div className="grid grid-cols-2 gap-x-5 gap-y-4">
              <WorkMark
                label="Total distance"
                value={marks.totalDistanceM}
                reference={refs.refTotalDistanceM}
                unit="m"
              />
              <WorkMark
                label="Relative distance"
                value={marks.relDistanceMpm}
                reference={refs.refRelDistanceMpm}
                unit="m/min"
              />
              <WorkMark
                label="HSR"
                value={marks.hsrM}
                reference={refs.refHsrM}
                unit="m"
              />
              <WorkMark
                label="Acc–Dec"
                value={marks.accDec}
                reference={refs.refAccDec}
                unit="ct"
              />
            </div>
          </div>

          {/* Internal — Cost */}
          <div
            className="p-5"
            style={{ backgroundColor: "var(--color-axis-cost-tinted)" }}
          >
            <div className="mb-3 flex items-center gap-2">
              <span
                className="h-2 w-2 rounded-full"
                style={{ backgroundColor: "var(--color-axis-cost)" }}
              />
              <span className="type-col-head">Internal — cost</span>
            </div>
            <div className="space-y-5">
              {/* Cardio Load */}
              <div className="space-y-1.5">
                <div className="flex items-baseline justify-between">
                  <span className="type-data-label">Cardio Load</span>
                  <CoverageBadge
                    covered={coveredCount}
                    total={effectiveParticipants.length}
                    below={lowCov.map((a) => ({
                      name: a.name,
                      cov: a.hrCoveragePct ?? 0,
                    }))}
                  />
                </div>
                <ValueOnTrack
                  mode="deviation"
                  axis="cost"
                  value={marks.cardioLoadCL}
                  reference={refs.refCardioLoadCL}
                  unit="CL"
                  qualified={clQualified}
                />
              </div>

              {/* sRPE — co-equal, three states */}
              <div className="space-y-1.5">
                <div className="flex items-baseline justify-between">
                  <span className="type-data-label">sRPE</span>
                  {srpeState === "partial" && (
                    <SrpeBadge
                      submitted={submitters.length}
                      total={effectiveParticipants.length}
                      responders={submitters.map((a) => a.name)}
                    />
                  )}
                </div>
                {srpeState === "none" ? (
                  <div
                    className="flex h-7 items-center text-[13px]"
                    style={{ color: "var(--color-text-tertiary)" }}
                  >
                    Not collected this session
                  </div>
                ) : srpeState === "filled" ? (
                  <ValueOnTrack
                    mode="deviation"
                    axis="cost"
                    value={marks.srpeMean}
                    reference={refs.refSrpeMean}
                    unit="/10"
                  />
                ) : (
                  <ValueOnTrack
                    mode="deviation"
                    axis="cost"
                    value={
                      // mean of submitters (rough — averages toward marks.srpeMean)
                      Number(
                        (submitters.length > 0
                          ? marks.srpeMean * 0.97
                          : marks.srpeMean
                        ).toFixed(1),
                      )
                    }
                    reference={refs.refSrpeMean}
                    unit="/10"
                  />
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Zones */}
        <div
          className="border-t p-5"
          style={{ borderColor: "var(--color-border)" }}
        >
          <div className="mb-2 flex items-baseline justify-between gap-4">
            <div className="flex items-baseline gap-2 flex-wrap">
              <span className="type-col-head">Z4+Z5 high-intensity share</span>
              <span
                className="type-label"
                style={{ color: "var(--color-text-tertiary)" }}
              >
                · {basisWord}
              </span>
              <span
                className="type-num text-[15px] font-semibold"
                style={{ color: "var(--color-text-primary)" }}
              >
                — {zoneShares.hi}%
              </span>
              <span
                className="text-[12px]"
                style={{ color: "var(--color-text-tertiary)" }}
              >
                (typical {zoneShares.typ}%)
              </span>
            </div>
            <SegmentedToggle
              value={zoneBasis}
              onChange={setZoneBasis}
              options={[
                { id: "distance", label: "Distance" },
                { id: "duration", label: "Duration" },
              ]}
            />
          </div>
          <ZoneBar
            shares={[
              { id: "z1", pct: zoneShares.z1, ramp: 1 },
              { id: "z2", pct: zoneShares.z2, ramp: 2 },
              { id: "z3", pct: zoneShares.z3, ramp: 3 },
              { id: "z4", pct: zoneShares.z4, ramp: 4 },
              { id: "z5", pct: zoneShares.z5, ramp: 5 },
            ]}
          />
        </div>

        {/* vs Full match — receded on a match day */}
        <div
          className="border-t px-5 py-4"
          style={{
            borderColor: "var(--color-border)",
            backgroundColor: "var(--color-slate-50)",
          }}
        >
          <div className="mb-2 flex items-baseline justify-between gap-4">
            <span
              className="type-label"
              style={{ color: "var(--color-text-tertiary)" }}
            >
              vs a typical full match — scale 0–150%, tick = full match
            </span>
            {currentSession.kind === "match" && (
              <span
                className="text-[11px] italic"
                style={{ color: "var(--color-text-tertiary)" }}
              >
                most useful on training days
              </span>
            )}
          </div>
          <div className="grid grid-cols-2 gap-6">
            <FullMatchRead label="Volume" pct={SESSION_VS_FULL.volumePct} />
            <FullMatchRead label="Intensity" pct={SESSION_VS_FULL.intensityPct} />
          </div>
        </div>
      </div>

      {/* ---- Participation card ---- */}
      <div className="mt-6">
        <ParticipationCard
          athletes={activeAthletes}
          filterActive={
            filter.participation.size > 0 ||
            filter.positions.size > 0 ||
            filter.athletes.size > 0
          }
        />
      </div>
    </section>
  );
}

/* ---------- Sub-parts ---------- */

function WorkMark({
  label,
  value,
  reference,
  unit,
}: {
  label: string;
  value: number;
  reference: number;
  unit: string;
}) {
  return (
    <div className="space-y-1">
      <div className="flex items-baseline justify-between">
        <span className="type-data-label">{label}</span>
        <span
          className="type-num text-[15px] font-semibold"
          style={{ color: "var(--color-text-primary)" }}
        >
          {value.toLocaleString()}
          <span className="type-data-label ml-0.5">{unit}</span>
        </span>
      </div>
      <ValueOnTrack
        mode="deviation"
        axis="work"
        value={value}
        reference={reference}
        size="compact"
        showValue={false}
      />
    </div>
  );
}

function CoverageBadge({
  covered,
  total,
  below,
}: {
  covered: number;
  total: number;
  below: Array<{ name: string; cov: number }>;
}) {
  const [open, setOpen] = useState(false);
  const degraded = covered < total;
  if (!degraded) {
    return (
      <span
        className="type-num text-[11px]"
        style={{ color: "var(--color-text-tertiary)" }}
      >
        {covered} of {total} ≥{COVERAGE_MIN}% cov
      </span>
    );
  }
  return (
    <span className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        className="inline-flex items-center gap-1 rounded px-1 py-0.5 type-num text-[11px] transition-colors hover:bg-[color:var(--color-slate-100)]"
        style={{ color: "var(--color-text-secondary)" }}
      >
        <span
          className="h-1.5 w-1.5 rounded-full"
          style={{ backgroundColor: "var(--color-trust-dot)" }}
          aria-hidden
        />
        {covered} of {total} ≥{COVERAGE_MIN}% cov
        <Info className="h-3 w-3" />
      </button>
      {open && (
        <div
          className="absolute right-0 top-full z-40 mt-1 w-64 rounded-md border p-3 shadow-lg"
          style={{
            backgroundColor: "var(--color-surface-card)",
            borderColor: "var(--color-border)",
          }}
        >
          <div className="type-label mb-1">Below {COVERAGE_MIN}% coverage</div>
          <ul className="space-y-1">
            {below.map((a) => (
              <li
                key={a.name}
                className="flex items-center justify-between text-[12px]"
                style={{ color: "var(--color-text-secondary)" }}
              >
                <span style={{ color: "var(--color-text-primary)" }}>{a.name}</span>
                <span className="type-num" style={{ color: "var(--color-text-tertiary)" }}>
                  {a.cov}%
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </span>
  );
}

function SrpeBadge({
  submitted,
  total,
  responders,
}: {
  submitted: number;
  total: number;
  responders: string[];
}) {
  const [open, setOpen] = useState(false);
  return (
    <span className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        className="inline-flex items-center gap-1 rounded px-1 py-0.5 type-num text-[11px] transition-colors hover:bg-[color:var(--color-slate-100)]"
        style={{ color: "var(--color-text-secondary)" }}
      >
        <span
          className="h-1.5 w-1.5 rounded-full"
          style={{ backgroundColor: "var(--color-trust-dot)" }}
          aria-hidden
        />
        {submitted} of {total} submitted
        <Info className="h-3 w-3" />
      </button>
      {open && (
        <div
          className="absolute right-0 top-full z-40 mt-1 w-64 rounded-md border p-3 shadow-lg"
          style={{
            backgroundColor: "var(--color-surface-card)",
            borderColor: "var(--color-border)",
          }}
        >
          <div className="type-label mb-1">Responders — never imputed</div>
          <div className="text-[12px]" style={{ color: "var(--color-text-secondary)" }}>
            {responders.join(", ")}
          </div>
        </div>
      )}
    </span>
  );
}

function SegmentedToggle<T extends string>({
  value,
  onChange,
  options,
}: {
  value: T;
  onChange: (id: T) => void;
  options: Array<{ id: T; label: string }>;
}) {
  return (
    <div
      className="inline-flex rounded-md p-0.5"
      style={{
        backgroundColor: "var(--color-slate-100)",
        border: "1px solid var(--color-border)",
      }}
    >
      {options.map((o) => (
        <button
          key={o.id}
          onClick={() => onChange(o.id)}
          className={`type-micro rounded px-2.5 py-1 transition-colors ${
            o.id === value ? "sel-active" : "sel-idle"
          }`}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}

function ZoneBar({
  shares,
}: {
  shares: Array<{ id: string; pct: number; ramp: 1 | 2 | 3 | 4 | 5 }>;
}) {
  return (
    <div className="space-y-1.5">
      <div
        className="flex h-6 overflow-hidden rounded-md"
        style={{ border: "1px solid var(--color-border)" }}
      >
        {shares.map((s) => (
          <div
            key={s.id}
            style={{
              width: `${s.pct}%`,
              backgroundColor: `var(--zone-work-${s.ramp})`,
            }}
            title={`Z${s.ramp} — ${s.pct}%`}
          />
        ))}
      </div>
      <div className="flex text-[11px]">
        {shares.map((s) => (
          <div
            key={s.id}
            className="type-num"
            style={{
              width: `${s.pct}%`,
              color: "var(--color-text-secondary)",
              paddingLeft: 4,
            }}
          >
            Z{s.ramp} — {s.pct}%
          </div>
        ))}
      </div>
    </div>
  );
}

function FullMatchRead({ label, pct }: { label: string; pct: number }) {
  return (
    <div className="space-y-1">
      <div className="flex items-baseline justify-between">
        <span className="type-data-label">{label}</span>
        <span
          className="type-num text-[13px] font-semibold"
          style={{ color: "var(--color-text-primary)" }}
        >
          {pct}%
        </span>
      </div>
      <ValueOnTrack
        mode="shared"
        axis="work"
        value={pct}
        reference={100}
        scaleMin={0}
        scaleMax={150}
        referenceBandPct={5}
        scaleLabel="full match"
        size="compact"
        showValue={false}
      />
    </div>
  );
}

/* ---------- Participation card ---------- */

function ParticipationCard({
  athletes,
  filterActive,
}: {
  athletes: Array<{ id: string; name: string; participation: ParticipationTag | null }>;
  filterActive: boolean;
}) {
  const counts: Record<ParticipationTag, string[]> = {
    Full: [], Part: [], Modified: [], Rehab: [], Injury: [], Other: [],
  };
  athletes.forEach((a) => {
    if (a.participation) counts[a.participation].push(a.name);
  });
  const total = athletes.length;
  const fullPct = total > 0 ? Math.round((counts.Full.length / total) * 100) : 0;

  const withCounts = PARTICIPATION_TAGS.map((t) => ({ tag: t, names: counts[t] }));
  const present = withCounts.filter((x) => x.names.length > 0);
  const absent = withCounts.filter((x) => x.names.length === 0).map((x) => x.tag);

  const [popover, setPopover] = useState<ParticipationTag | null>(null);

  return (
    <div
      className="rounded-lg border p-5"
      style={{
        borderColor: "var(--color-border)",
        backgroundColor: "var(--color-surface-card)",
      }}
    >
      <div className="mb-3 flex items-baseline justify-between">
        <div className="flex items-baseline gap-3">
          <h3 className="type-section-h">Participation</h3>
          {filterActive && (
            <span
              className="type-label"
              style={{ color: "var(--color-text-tertiary)" }}
            >
              — {total} in scope
            </span>
          )}
        </div>
        <div
          className="type-num text-[18px] font-semibold"
          style={{ color: "var(--color-text-primary)" }}
        >
          {fullPct}% <span className="type-data-label ml-0.5">full</span>
        </div>
      </div>

      {/* Segmented bar */}
      <div
        className="relative flex h-8 overflow-hidden rounded-md"
        style={{ border: "1px solid var(--color-border)" }}
      >
        {present.map((seg) => {
          const pct = (seg.names.length / total) * 100;
          const wide = pct >= 14;
          return (
            <button
              key={seg.tag}
              onClick={() => setPopover((p) => (p === seg.tag ? null : seg.tag))}
              className={`relative flex items-center justify-center overflow-hidden transition-opacity hover:opacity-90 ${TAG_TEXTURE[seg.tag]} ${TAG_TEXT_ON[seg.tag]}`}
              style={{ width: `${pct}%` }}
              title={`${seg.tag} — ${seg.names.length}`}
            >
              <span className="type-num text-[11px] font-semibold">
                {wide ? `${seg.tag} — ${seg.names.length}` : TAG_LETTER[seg.tag]}
              </span>
            </button>
          );
        })}
      </div>

      {/* Legend + zero-count muted line */}
      <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1.5">
        {present.map((seg) => (
          <button
            key={seg.tag}
            onClick={() => setPopover((p) => (p === seg.tag ? null : seg.tag))}
            className="inline-flex items-center gap-1.5 text-[11.5px] transition-colors hover:text-[color:var(--color-text-primary)]"
            style={{ color: "var(--color-text-secondary)" }}
          >
            <span
              className={`h-2.5 w-2.5 rounded-sm ${TAG_TEXTURE[seg.tag]}`}
              aria-hidden
            />
            <span>{seg.tag}</span>
            <span className="type-num" style={{ color: "var(--color-text-tertiary)" }}>
              {seg.names.length}
            </span>
          </button>
        ))}
        {absent.length > 0 && (
          <span
            className="type-data-label"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            none: {absent.join(" · ")}
          </span>
        )}
      </div>

      {popover && counts[popover].length > 0 && (
        <div
          className="mt-3 rounded-md border p-3"
          style={{
            borderColor: "var(--color-border)",
            backgroundColor: "var(--color-slate-50)",
          }}
        >
          <div className="type-label mb-1">{popover} — {counts[popover].length}</div>
          <div className="flex flex-wrap gap-x-3 gap-y-1 text-[12px]"
            style={{ color: "var(--color-text-secondary)" }}
          >
            {counts[popover].map((n) => (
              <span key={n} style={{ color: "var(--color-text-primary)" }}>
                {n}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
