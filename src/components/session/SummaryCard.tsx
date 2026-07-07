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

type Marks = {
  totalDistanceM: number; refTotalDistanceM: number;
  relDistanceMpm: number; refRelDistanceMpm: number;
  hsrM: number;           refHsrM: number;
  accDec: number;         refAccDec: number;
  cardioLoadCL: number;   refCardioLoadCL: number;
  srpeMean: number;       refSrpeMean: number;
  z1: number; z2: number; z3: number; z4: number; z5: number;
  z4z5Typical: number;
  volumePct: number; intensityPct: number;
};

const SQUAD: Record<BenchKey, Marks> = {
  typical_match: {
    totalDistanceM: 9820, refTotalDistanceM: 9010,
    relDistanceMpm: 108,  refRelDistanceMpm: 102,
    hsrM: 812,            refHsrM: 665,
    accDec: 118,          refAccDec: 108,
    cardioLoadCL: 218,    refCardioLoadCL: 205,
    srpeMean: 7.4,        refSrpeMean: 6.9,
    z1: 34, z2: 22, z3: 13, z4: 19, z5: 12, z4z5Typical: 26,
    volumePct: 101, intensityPct: 106,
  },
  last_match: {
    totalDistanceM: 9820, refTotalDistanceM: 9640,
    relDistanceMpm: 108,  refRelDistanceMpm: 104,
    hsrM: 812,            refHsrM: 720,
    accDec: 118,          refAccDec: 111,
    cardioLoadCL: 218,    refCardioLoadCL: 210,
    srpeMean: 7.4,        refSrpeMean: 7.1,
    z1: 34, z2: 22, z3: 13, z4: 19, z5: 12, z4z5Typical: 28,
    volumePct: 101, intensityPct: 106,
  },
  last_5: {
    totalDistanceM: 9820, refTotalDistanceM: 9350,
    relDistanceMpm: 108,  refRelDistanceMpm: 103,
    hsrM: 812,            refHsrM: 690,
    accDec: 118,          refAccDec: 109,
    cardioLoadCL: 218,    refCardioLoadCL: 207,
    srpeMean: 7.4,        refSrpeMean: 7.0,
    z1: 34, z2: 22, z3: 13, z4: 19, z5: 12, z4z5Typical: 27,
    volumePct: 101, intensityPct: 106,
  },
  same_opponent: {
    totalDistanceM: 9820, refTotalDistanceM: 9200,
    relDistanceMpm: 108,  refRelDistanceMpm: 103,
    hsrM: 812,            refHsrM: 640,
    accDec: 118,          refAccDec: 106,
    cardioLoadCL: 218,    refCardioLoadCL: 202,
    srpeMean: 7.4,        refSrpeMean: 6.8,
    z1: 34, z2: 22, z3: 13, z4: 19, z5: 12, z4z5Typical: 25,
    volumePct: 101, intensityPct: 106,
  },
};

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

  const marks = SQUAD[benchmark.kind];
  const nInScope = activeAthletes.length;

  // Coverage badge — squad aggregate on effective data.
  const lowCov = effectiveParticipants.filter(
    (a) => a.hrCoveragePct !== null && a.hrCoveragePct < COVERAGE_MIN,
  );
  const coveredCount = effectiveParticipants.length - lowCov.length;

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
    // The distance ramp is the primary; duration is a re-basis toy that
    // subtly shifts the low-intensity end (walking dominates duration).
    if (zoneBasis === "distance") {
      return { z1: marks.z1, z2: marks.z2, z3: marks.z3, z4: marks.z4, z5: marks.z5, hi: marks.z4 + marks.z5, typ: marks.z4z5Typical };
    }
    return { z1: 46, z2: 24, z3: 12, z4: 12, z5: 6, hi: 18, typ: 16 };
  }, [zoneBasis, marks]);

  const descriptorScope = !filterIsDefault && scopeLabel ? scopeLabel : null;

  return (
    <section id="summary" className="scroll-mt-28">
      <header className="mb-3 flex items-baseline justify-between gap-4">
        <div className="flex items-baseline gap-2 flex-wrap">
          <h2 className="type-section-h">Summary</h2>
          <span
            className="type-card-eyebrow"
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
                reference={marks.refTotalDistanceM}
                unit="m"
              />
              <WorkMark
                label="Relative distance"
                value={marks.relDistanceMpm}
                reference={marks.refRelDistanceMpm}
                unit="m/min"
              />
              <WorkMark
                label="HSR"
                value={marks.hsrM}
                reference={marks.refHsrM}
                unit="m"
              />
              <WorkMark
                label="Acc–Dec"
                value={marks.accDec}
                reference={marks.refAccDec}
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
                  reference={marks.refCardioLoadCL}
                  unit="CL"
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
                    reference={marks.refSrpeMean}
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
                    reference={marks.refSrpeMean}
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
            <div className="flex items-baseline gap-2">
              <span className="type-col-head">Z4+Z5 high-intensity share</span>
              <span
                className="type-num text-[15px] font-semibold"
                style={{ color: "var(--color-text-primary)" }}
              >
                {zoneShares.hi}%
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
              className="type-card-eyebrow"
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
            <FullMatchRead label="Volume" pct={marks.volumePct} />
            <FullMatchRead label="Intensity" pct={marks.intensityPct} />
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
          <div className="type-card-eyebrow mb-1">Below {COVERAGE_MIN}% coverage</div>
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
          <div className="type-card-eyebrow mb-1">Responders — never imputed</div>
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
              backgroundColor: `var(--color-zone-work-${s.ramp})`,
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
              className="type-card-eyebrow"
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
          <div className="type-card-eyebrow mb-1">{popover} — {counts[popover].length}</div>
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
