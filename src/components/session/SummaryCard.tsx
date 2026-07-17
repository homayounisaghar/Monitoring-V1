/**
 * ST2 — Session > Summary card.
 * Two-axis pair (S6), zones, vs-full-match (S3) and Participation (S4).
 * Header carries scope once (via ScopeTag). No axis-tinted panes.
 */
import { useMemo, useState } from "react";
import { Info } from "lucide-react";
import { useSessionScope, currentSession, COVERAGE_MIN } from "@/lib/session-scope";
import type { ParticipationTag } from "@/lib/session-data";
import { ValueOnTrack } from "@/components/data/ValueOnTrack";
import { copy, tmpl } from "@/lib/copy-deck";
import { METRICS as METRIC_LIB } from "@/lib/squad-metrics";
import { ScopeTag } from "@/components/session/ScopeTag";
import { SegmentedToggle } from "@/components/data/SegmentedToggle";

/* ---------- Static (curated) squad averages, keyed to Benchmark ---------- */

type BenchKey =
  | "typical_daytype"
  | "typical_match"
  | "last_match"
  | "last_5"
  | "same_opponent";

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
  typical_daytype: {
    refTotalDistanceM: 6800, refRelDistanceMpm: 95,
    refHsrM: 380, refAccDec: 88,
    refCardioLoadCL: 150, refSrpeMean: 5.4,
    z4z5TypicalDistance: 14, z4z5TypicalDuration: 9,
  },
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

const SESSION_VS_FULL = { volumePct: 101, intensityPct: 106 } as const;

const PARTICIPATION_TAGS: ParticipationTag[] = [
  "Full", "Part", "Modified", "Rehab", "Injury", "Other",
];
// Mid-tone fills — kept below the Summary loudness budget (≤60).
// Category carried by texture, not hue.
const TAG_TEXTURE: Record<ParticipationTag, string> = {
  Full:     "bg-[color:var(--color-slate-500)]",
  // Part — wider stripe pitch, high-contrast slate pair for arm's-length read.
  Part:     "bg-[color:var(--color-slate-500)] bg-[repeating-linear-gradient(45deg,var(--color-slate-500)_0_5px,var(--color-slate-100)_5px_10px)]",
  Modified: "bg-[color:var(--color-slate-400)] bg-[repeating-linear-gradient(-45deg,var(--color-slate-400)_0_4px,var(--color-slate-200)_4px_8px)]",
  Rehab:    "bg-[color:var(--color-slate-300)] bg-[repeating-linear-gradient(90deg,var(--color-slate-300)_0_5px,var(--color-slate-100)_5px_10px)]",
  // Injury — darker base + lighter stripes; horizontal, distinct from Part.
  Injury:   "bg-[color:var(--color-slate-700)] bg-[repeating-linear-gradient(0deg,var(--color-slate-700)_0_3px,var(--color-slate-200)_3px_7px)]",
  Other:    "bg-[color:var(--color-slate-300)]",
};

/* ---------- Small shared bits ---------- */

function AxisDot({ axis }: { axis: "work" | "cost" }) {
  return (
    <span
      className="h-2 w-2 rounded-full"
      style={{
        backgroundColor:
          axis === "work" ? "var(--color-axis-work)" : "var(--color-axis-cost)",
      }}
    />
  );
}

function RefParen({ children }: { children: React.ReactNode }) {
  return (
    <span
      className="type-num text-[12px]"
      style={{ color: "var(--color-text-tertiary)" }}
    >
      ({children})
    </span>
  );
}

/* ---------- Component ---------- */

export function SummaryCard() {
  const {
    benchmark,
    filter,
    activeAthletes,
    effectiveParticipants,
    sessionIsTraining,
  } = useSessionScope();

  const refs = SQUAD_REF[benchmark.kind];
  const marks = SESSION_MARKS;

  // Coverage — squad aggregate on effective data.
  const lowCov = effectiveParticipants.filter(
    (a) => a.hrCoveragePct !== null && a.hrCoveragePct < COVERAGE_MIN,
  );
  const coveredCount = effectiveParticipants.length - lowCov.length;
  const clQualified =
    effectiveParticipants.length === 0
      ? true
      : coveredCount / effectiveParticipants.length >= 0.6;

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

  const isMatch = !sessionIsTraining;

  return (
    <section id="summary" className="scroll-mt-36">
      <header className="mb-3 flex items-baseline justify-between gap-4">
        <div className="flex items-baseline gap-2 flex-wrap">
          <h2 className="type-section-h">{copy("canonical.section.summary")}</h2>
          <span
            className="type-label"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            {copy("canonical.summary.subtitlePrefix")}{benchmark.label}
          </span>
        </div>
        <ScopeTag />
      </header>

      {/* ---- Squad-load card — two axes side by side (white, hairline) ---- */}
      <div
        className="overflow-hidden rounded-lg border"
        style={{
          borderColor: "var(--color-border)",
          backgroundColor: "var(--color-surface-card)",
        }}
      >
        {/* Shared header row */}
        <div
          className="grid grid-cols-[minmax(0,1.4fr)_minmax(0,1fr)] border-b"
          style={{ borderColor: "var(--color-border)" }}
        >
          <div
            className="border-r px-5 py-3 flex items-center gap-2"
            style={{ borderColor: "var(--color-border)" }}
          >
            <AxisDot axis="work" />
            <span className="type-col-head">{copy("canonical.axisGroup.externalWork")}</span>
          </div>
          <div className="px-5 py-3 flex items-center gap-2">
            <AxisDot axis="cost" />
            <span className="type-col-head">{copy("canonical.axisGroup.internalCost")}</span>
          </div>
        </div>

        <div className="grid grid-cols-[minmax(0,1.4fr)_minmax(0,1fr)]">
          {/* External — Work */}
          <div
            className="border-r p-5"
            style={{ borderColor: "var(--color-border)" }}
          >
            <div className="grid grid-cols-2 gap-x-5 gap-y-4">
              <WorkMark
                label={METRIC_LIB.totalDistance.label}
                value={marks.totalDistanceM}
                reference={refs.refTotalDistanceM}
                unit="m"
                basisLabel={`100 · ${benchmark.label.charAt(0).toLowerCase()}${benchmark.label.slice(1)}`}
              />

              <WorkMark
                label={METRIC_LIB.mMin.label}
                value={marks.relDistanceMpm}
                reference={refs.refRelDistanceMpm}
                unit="m/min"
              />
              <WorkMark
                label={METRIC_LIB.hsr.label}
                value={marks.hsrM}
                reference={refs.refHsrM}
                unit="m"
              />
              <WorkMark
                label={METRIC_LIB.accDec.label}
                value={marks.accDec}
                reference={refs.refAccDec}
                unit="ct"
              />
            </div>
          </div>

          {/* Internal — Cost */}
          <div className="p-5">
            <div className="grid grid-cols-1 gap-x-5 gap-y-4">
              {/* Cardio Load */}
              {!clQualified && coveredCount === 0 ? (
                <div className="space-y-1">
                  <div className="flex items-baseline justify-between">
                    <span className="type-data-label">{METRIC_LIB.cardioLoad.label}</span>
                    <span
                      className="type-num text-[13px]"
                      style={{ color: "var(--color-text-tertiary)" }}
                    >
                      {copy("summary.internalNotMeasured")}
                    </span>
                  </div>
                </div>
              ) : (
                <CostMark
                  label={METRIC_LIB.cardioLoad.label}
                  value={marks.cardioLoadCL}
                  reference={refs.refCardioLoadCL}
                  unit="CL"
                  qualified={clQualified}
                  badge={
                    <CoverageBadge
                      covered={coveredCount}
                      total={effectiveParticipants.length}
                      below={lowCov.map((a) => ({
                        name: a.name,
                        cov: a.hrCoveragePct ?? 0,
                      }))}
                    />
                  }
                />
              )}

              {/* sRPE */}
              {srpeState === "none" ? (
                <div className="space-y-1">
                  <div className="flex items-baseline justify-between">
                    <span className="type-data-label">{METRIC_LIB.srpe.label}</span>
                    <span
                      className="type-num text-[13px]"
                      style={{ color: "var(--color-text-tertiary)" }}
                    >
                      {copy("srpe.empty")}
                    </span>
                  </div>
                </div>
              ) : (
                <CostMark
                  label={METRIC_LIB.srpe.label}
                  value={
                    srpeState === "filled"
                      ? marks.srpeMean
                      : Number((marks.srpeMean * 0.97).toFixed(1))
                  }
                  reference={refs.refSrpeMean}
                  unit="/10"
                  badge={
                    srpeState === "partial" ? (
                      <SrpeBadge
                        submitted={submitters.length}
                        total={effectiveParticipants.length}
                        responders={submitters.map((a) => a.name)}
                      />
                    ) : null
                  }
                />
              )}
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
              <span className="type-col-head">{copy("canonical.summary.zones.head")}</span>
              <span
                className="type-num text-[15px] font-semibold"
                style={{ color: "var(--color-text-primary)" }}
              >
                — {zoneShares.hi}%
              </span>
              <RefParen>{copy("canonical.summary.zones.typicalPrefix")}{zoneShares.typ}%</RefParen>
            </div>
            <SegmentedToggle
              value={zoneBasis}
              onChange={setZoneBasis}
              options={[
                { id: "distance", label: copy("canonical.summary.zones.basis.distance") },
                { id: "duration", label: copy("canonical.summary.zones.basis.duration") },
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

        {/* vs Full match — promoted on training, collapsed on match */}
        {isMatch ? (
          <div
            className="border-t px-5 py-3 flex items-baseline justify-between gap-4"
            style={{
              borderColor: "var(--color-border)",
              backgroundColor: "var(--color-slate-50)",
            }}
          >
            <span
              className="type-label"
              style={{ color: "var(--color-text-tertiary)" }}
            >
              {copy("summary.vsFullMatch.label")}
            </span>
            <div className="flex items-baseline gap-4">
              <CollapsedFullRead label={copy("canonical.summary.vsFullMatch.volume")} pct={SESSION_VS_FULL.volumePct} />
              <CollapsedFullRead label={copy("canonical.summary.vsFullMatch.intensity")} pct={SESSION_VS_FULL.intensityPct} />
            </div>
          </div>
        ) : (
          <div
            className="border-t px-5 py-4"
            style={{
              borderColor: "var(--color-border)",
              backgroundColor: "var(--color-slate-50)",
            }}
          >
            <div className="mb-2">
              <span
                className="type-label"
                style={{ color: "var(--color-text-tertiary)" }}
              >
                {copy("summary.vsFullMatch.label")}
              </span>
            </div>
            <div className="grid grid-cols-2 gap-6">
              <FullMatchRead label={copy("canonical.summary.vsFullMatch.volume")} pct={SESSION_VS_FULL.volumePct} />
              <FullMatchRead label={copy("canonical.summary.vsFullMatch.intensity")} pct={SESSION_VS_FULL.intensityPct} />
            </div>
          </div>
        )}
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
  basisLabel,
}: {
  label: string;
  value: number;
  reference: number;
  unit: string;
  basisLabel?: string;
}) {
  return (
    <div className="space-y-1">
      <div className="flex items-baseline justify-between">
        <span className="type-data-label">{label}</span>
        <span
          className="type-num text-[25px] font-semibold leading-none"
          style={{ color: "var(--color-text-primary)" }}
        >
          {value.toLocaleString()}
          {label !== unit && <span className="type-data-label ml-0.5">{unit}</span>}
        </span>
      </div>
      <ValueOnTrack
        mode="deviation"
        axis="work"
        value={value}
        reference={reference}
        size="compact"
        showValue={false}
        showDelta={false}
      />
      {basisLabel && (
        <div
          className="type-num text-[12px] text-center"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          {basisLabel}
        </div>
      )}
    </div>
  );
}

function CostMark({
  label,
  value,
  reference,
  unit,
  qualified = true,
  badge,
}: {
  label: string;
  value: number;
  reference: number;
  unit: string;
  qualified?: boolean;
  badge?: React.ReactNode;
}) {
  return (
    <div className="space-y-1">
      <div className="flex items-baseline justify-between gap-2">
        <span className="type-data-label inline-flex items-baseline gap-2">
          {label}
          {badge}
        </span>
        <span
          className="type-num text-[25px] font-semibold leading-none"
          style={{ color: "var(--color-text-primary)" }}
        >
          {value.toLocaleString()}
          {label !== unit && <span className="type-data-label ml-0.5">{unit}</span>}
        </span>
      </div>
      <ValueOnTrack
        mode="deviation"
        axis="cost"
        value={value}
        reference={reference}
        size="compact"
        showValue={false}
        showDelta={false}
        qualified={qualified}
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
        className="type-num text-[12px]"
        style={{ color: "var(--color-text-tertiary)" }}
      >
        · {covered} of {total}
      </span>
    );
  }
  return (
    <span className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        className="inline-flex items-center gap-1 rounded px-1 py-0.5 type-num text-[12px] transition-colors hover:bg-[color:var(--color-slate-100)]"
        style={{ color: "var(--color-text-secondary)" }}
      >
        <span
          className="h-1.5 w-1.5 rounded-full"
          style={{ backgroundColor: "var(--color-trust-dot)" }}
          aria-hidden
        />
        · {covered} of {total}
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
          <div className="type-label mb-1">{tmpl("canonical.summary.coverageBelowTemplate", { pct: COVERAGE_MIN })}</div>
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
        className="inline-flex items-center gap-1 rounded px-1 py-0.5 type-num text-[12px] transition-colors hover:bg-[color:var(--color-slate-100)]"
        style={{ color: "var(--color-text-secondary)" }}
      >
        <span
          className="h-1.5 w-1.5 rounded-full"
          style={{ backgroundColor: "var(--color-trust-dot)" }}
          aria-hidden
        />
        · {submitted} of {total}
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
          <div className="type-label mb-1">{copy("srpe.respondersHover")}</div>
          <div className="text-[12px]" style={{ color: "var(--color-text-secondary)" }}>
            {responders.join(", ")}
          </div>
        </div>
      )}
    </span>
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
      <div className="flex text-[12px]">
        {shares.map((s) => {
          // Full label "Zn — nn%" is ~52px at 11px; drop it under ~12%
          // (the segment's title/hover still carries it). Never truncate.
          const showLabel = s.pct >= 12;
          return (
            <div
              key={s.id}
              className="type-num"
              style={{
                width: `${s.pct}%`,
                color: "var(--color-text-secondary)",
                paddingLeft: 4,
              }}
              title={`Z${s.ramp} — ${s.pct}%`}
            >
              {showLabel ? `Z${s.ramp} — ${s.pct}%` : "\u00a0"}
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ---------- vs Full match reads ---------- */

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
        scaleLabel={copy("canonical.summary.vsFullMatch.fullMatchScale")}
        size="compact"
        showValue={false}
      />
      {/* End labels — the axis itself draws them */}
      <div
        className="flex justify-between type-num text-[10.5px]"
        style={{ color: "var(--color-text-tertiary)" }}
      >
        <span>{copy("canonical.summary.vsFullMatch.tick0")}</span>
        <span>{copy("canonical.summary.vsFullMatch.tick100")}</span>
        <span>{copy("canonical.summary.vsFullMatch.tick150")}</span>
      </div>
    </div>
  );
}

function CollapsedFullRead({ label, pct }: { label: string; pct: number }) {
  return (
    <span className="inline-flex items-baseline gap-1.5">
      <span
        className="type-data-label"
        style={{ color: "var(--color-text-secondary)" }}
      >
        {label}
      </span>
      <span
        className="type-num text-[13px] font-semibold"
        style={{ color: "var(--color-text-primary)" }}
      >
        {pct}%
      </span>
    </span>
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
  const absent = withCounts.filter((x) => x.names.length === 0);

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
          <h3 className="type-section-h">{copy("canonical.section.participation")}</h3>
        </div>
        {total > 0 && (
          <div
            className="type-num text-[18px] font-semibold"
            style={{ color: "var(--color-text-primary)" }}
          >
            {fullPct}% <span className="type-data-label ml-0.5">{copy("canonical.summary.fullSuffix")}</span>
          </div>
        )}
      </div>

      {total === 0 ? (
        <div
          className="type-label py-6 text-center"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          {copy("scope.emptyLine")}
        </div>
      ) : (
        <>


      {/* Segmented bar — mid-tone, no in-bar labels */}
      <div
        className="relative flex h-8 overflow-hidden rounded-md"
        style={{ border: "1px solid var(--color-border)" }}
      >
        {present.map((seg, i) => {
          const pct = (seg.names.length / total) * 100;
          const isLast = i === present.length - 1;
          return (
            <button
              key={seg.tag}
              onClick={() => setPopover((p) => (p === seg.tag ? null : seg.tag))}
              className={`relative transition-opacity hover:opacity-90 ${TAG_TEXTURE[seg.tag]}`}
              style={{
                width: `${pct}%`,
                borderRight: isLast
                  ? undefined
                  : "1px solid var(--color-border)",
              }}
              title={`${seg.tag} — ${seg.names.length}`}
              aria-label={`${seg.tag}: ${seg.names.length}`}
            />
          );
        })}
      </div>

      {/* Count-chips keyed by swatch — "Full 13 · Part 3 · Injury 2" */}
      <div className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1.5">
        {present.map((seg, idx) => {
          const inlineNames = seg.tag !== "Full" && seg.names.length > 0 && seg.names.length <= 2;
          return (
            <span key={seg.tag} className="inline-flex items-center gap-x-3">
              {idx > 0 && (
                <span
                  className="type-num text-[12px]"
                  style={{ color: "var(--color-text-tertiary)" }}
                  aria-hidden
                >
                  ·
                </span>
              )}
              {inlineNames ? (
                <span
                  className="inline-flex items-center gap-1.5 text-[12px]"
                  style={{ color: "var(--color-text-secondary)" }}
                >
                  <span
                    className={`h-2.5 w-2.5 rounded-sm ${TAG_TEXTURE[seg.tag]}`}
                    aria-hidden
                  />
                  <span>{seg.tag}</span>
                  <span
                    className="type-num"
                    style={{ color: "var(--color-text-primary)" }}
                  >
                    {seg.names.length}
                  </span>
                  <span style={{ color: "var(--color-text-tertiary)" }}>
                    — {seg.names.map((n) => n.split(" ").slice(-1)[0]).join(", ")}
                  </span>
                </span>
              ) : (
                <button
                  onClick={() => setPopover((p) => (p === seg.tag ? null : seg.tag))}
                  className="inline-flex items-center gap-1.5 text-[12px] transition-colors hover:text-[color:var(--color-text-primary)]"
                  style={{ color: "var(--color-text-secondary)" }}
                >
                  <span
                    className={`h-2.5 w-2.5 rounded-sm ${TAG_TEXTURE[seg.tag]}`}
                    aria-hidden
                  />
                  <span>{seg.tag}</span>
                  <span
                    className="type-num"
                    style={{ color: "var(--color-text-primary)" }}
                  >
                    {seg.names.length}
                  </span>
                </button>
              )}
            </span>
          );
        })}
        {/* Zeros surface on hover only */}
        {absent.length > 0 && (
          <span
            className="group relative inline-flex items-center"
            tabIndex={0}
          >
            <span
              className="type-num text-[12px] cursor-default"
              style={{ color: "var(--color-text-tertiary)" }}
              aria-label={copy("participation.zerosHover")}
            >
              ·
            </span>
            <span
              className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 whitespace-nowrap rounded border px-2 py-1 opacity-0 shadow-sm transition-opacity group-hover:opacity-100 group-focus:opacity-100 type-data-label"
              style={{
                backgroundColor: "var(--color-surface-card)",
                borderColor: "var(--color-border)",
                color: "var(--color-text-tertiary)",
                zIndex: 40,
              }}
            >
              {copy("canonical.summary.zonesNonePrefix")}{absent.map((x) => x.tag).join(" · ")}
            </span>
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
        </>
      )}
    </div>
  );
}

