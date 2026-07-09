/**
 * ST2 — Attention card.
 * The coach's 5-second answer to "who needs me?". This is the only place
 * severity ink and the severity glyphs are allowed to appear.
 *
 * All data is read from the effective (scenario-adjusted) scope. No
 * demo branches live here — isAllClear is a consequence of the data
 * (zero tier-1 flags + full coverage across participants).
 */
import { useState } from "react";
import { ChevronRight, ChevronDown } from "lucide-react";
import { useNavigate } from "@tanstack/react-router";
import { useSessionScope, COVERAGE_MIN } from "@/lib/session-scope";
import {
  BUILDING_ID,
  BUILDING_SESSIONS_TO_MIN,
  flaggedIds,
  type Tier1Row,
} from "@/lib/session-flags";
import { SeverityGlyph } from "@/components/data/SeverityGlyph";
import { copy } from "@/lib/copy-deck";
import { ValueOnTrack } from "@/components/data/ValueOnTrack";
import { GapPair } from "@/components/data/GapPair";

/* ---------- Component ---------- */

export function AttentionCard() {
  const {
    effectiveParticipants,
    tier1Rows,
    activeAthletes,
    filterIsDefault,
    scopeLabel,
    totalParticipants,
  } = useSessionScope();
  const [showCheck, setShowCheck] = useState(false);

  const total = totalParticipants; // "of 18" invariant, derived
  const inScope = new Set(activeAthletes.map((a) => a.id));

  const tier1 = tier1Rows.filter((r) => inScope.has(r.id));
  const lowCovAthletes = activeAthletes.filter(
    (a) => a.hrCoveragePct !== null && a.hrCoveragePct < COVERAGE_MIN,
  );
  const building = activeAthletes.filter((a) => a.id === BUILDING_ID);

  const escalateCount = tier1.filter((r) => r.tier === "escalate").length;
  const noticeCount = tier1.filter((r) => r.tier === "notice").length;
  const manageCount = tier1.length;
  const checkCount = lowCovAthletes.length;
  const buildCount = building.length;

  // Coverage of the SQUAD (not the filtered subset) drives the synthesis
  // scope rule and the all-clear substantiation.
  const squadLowCov = effectiveParticipants.filter(
    (a) => a.hrCoveragePct !== null && a.hrCoveragePct < COVERAGE_MIN,
  ).length;
  const squadFullCov = effectiveParticipants.length - squadLowCov;
  const squadTier1 = tier1Rows.length;

  // Consequence-of-data flags.
  const isAllClear =
    squadTier1 === 0 && squadLowCov === 0; // "cleared" when nobody flagged and every input trustworthy
  const cantSayCoverage =
    squadFullCov / effectiveParticipants.length < 0.6; // < ~60% trustworthy → can't-say state

  const flaggedSet = flaggedIds(tier1, lowCovAthletes.map((a) => a.id));
  const clearCount = isAllClear
    ? activeAthletes.length - buildCount
    : activeAthletes.filter((a) => !flaggedSet.has(a.id)).length;
  const totalInScope = activeAthletes.length;

  return (
    <section id="attention" className="scroll-mt-28">
      <header className="mb-3 flex items-baseline justify-between gap-4">
        <div className="flex items-baseline gap-3">
          <h2 className="type-section-h">Attention</h2>
          {!filterIsDefault && scopeLabel && (
            <span
              className="type-label"
              style={{ color: "var(--color-text-tertiary)" }}
            >
              — {scopeLabel}
            </span>
          )}
        </div>
        {!filterIsDefault && (
          <span
            className="type-num text-[11px]"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            {totalInScope} of {total}
          </span>
        )}
      </header>
      <p className="type-section-desc mb-3">
        Who needs attention this session — checked against each athlete's own typical
        for this day-type.
      </p>

      <div
        className="overflow-hidden rounded-lg border"
        style={{
          borderColor: "var(--color-border)",
          backgroundColor: "var(--color-surface-card)",
        }}
      >
        <div
          className="flex items-start justify-between gap-6 border-b px-5 pb-3 pt-4"
          style={{ borderColor: "var(--color-border)" }}
        >
          <div className="min-w-0">
            {isAllClear ? (
              <div className="flex items-baseline gap-2">
                <span
                  className="text-[18px] font-semibold tracking-tight"
                  style={{ color: "var(--color-text-primary)" }}
                >
                  Nothing needs attention
                </span>
                <span
                  className="text-[12.5px]"
                  style={{ color: "var(--color-text-secondary)" }}
                >
                  · {clearCount} of {totalInScope} clear
                </span>
              </div>
            ) : (
              <div className="flex flex-wrap items-baseline gap-x-2 gap-y-1">
                <span
                  className="text-[18px] font-semibold tracking-tight"
                  style={{ color: "var(--color-text-primary)" }}
                >
                  {manageCount} to manage
                </span>
                <span
                  className="text-[12.5px]"
                  style={{ color: "var(--color-text-secondary)" }}
                >
                  · {escalateCount} escalate · {noticeCount} notice
                </span>
                <span
                  className="text-[12.5px]"
                  style={{ color: "var(--color-text-tertiary)" }}
                >
                  &nbsp;—&nbsp;
                </span>
                <span
                  className="text-[12.5px]"
                  style={{ color: "var(--color-text-secondary)" }}
                >
                  {checkCount} to check · {buildCount} building baseline · {clearCount} of {totalInScope} clear
                </span>
              </div>
            )}
          </div>
          <div
            className="shrink-0 text-[11px]"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            tracks: window ±40% vs each athlete's own typical for this day-type
          </div>
        </div>

        {isAllClear ? (
          <AllClearBody totalInScope={totalInScope} />
        ) : (
          <ul>
            {tier1.map((r) => (
              <Tier1RowUI key={r.id} row={r} />
            ))}
            {tier1.length === 0 && (
              <li
                className="px-5 py-4 text-[13px]"
                style={{ color: "var(--color-text-secondary)" }}
              >
                No divergence flags in this scope.
              </li>
            )}
          </ul>
        )}

        {checkCount > 0 && !isAllClear && (
          <Tier2Row
            count={checkCount}
            expanded={showCheck}
            onToggle={() => setShowCheck((s) => !s)}
            athletes={lowCovAthletes.map((a) => ({
              name: a.name,
              cov: a.hrCoveragePct ?? 0,
            }))}
          />
        )}

        {buildCount > 0 && (
          <div
            className="flex items-center gap-3 border-t px-5 py-2.5"
            style={{
              borderColor: "var(--color-border)",
              backgroundColor: "var(--color-slate-50)",
            }}
          >
            <span
              className="type-label"
              style={{ color: "var(--color-text-tertiary)" }}
            >
              Building baseline
            </span>
            <span className="text-[12.5px]" style={{ color: "var(--color-text-secondary)" }}>
              B. Köhler · {BUILDING_SESSIONS_TO_MIN} sessions to minimum history
            </span>
          </div>
        )}

        <SynthesisLine
          isAllClear={isAllClear}
          cantSay={cantSayCoverage}
          filterIsDefault={filterIsDefault}
        />
      </div>

      {/* Seam — coach-to-analyst boundary */}
      <div className="mt-8">
        <div
          className="h-px w-full"
          style={{ backgroundColor: "var(--color-border)" }}
        />
        <div
          className="type-label pt-3"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          Depth — Summary · Periods · Squad
        </div>
      </div>
    </section>
  );
}

/* ---------- Tier 1 row ---------- */

function Tier1RowUI({ row }: { row: Tier1Row }) {
  const { effectiveParticipants } = useSessionScope();
  const navigate = useNavigate();
  const athlete = effectiveParticipants.find((a) => a.id === row.id);
  if (!athlete) return null;

  return (
    <li
      className="group relative border-b last:border-b-0 transition-colors hover:bg-[color:var(--color-slate-50)]"
      style={{ borderColor: "var(--color-border)" }}
    >
      <button
        className="flex w-full items-center gap-4 px-5 py-3 text-left"
        onClick={() => navigate({ to: "/athlete" })}
      >
        <div className="w-[92px] shrink-0">
          <SeverityGlyph tier={row.tier} size="compact" />
        </div>

        <div className="w-[170px] shrink-0">
          <div
            className="text-[13.5px] font-medium leading-tight"
            style={{ color: "var(--color-text-primary)" }}
          >
            {athlete.name}
          </div>
          <div
            className="type-label"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            {athlete.posDetail}
          </div>
        </div>

        <div
          className="min-w-0 flex-1 text-[13px]"
          style={{ color: "var(--color-text-secondary)" }}
        >
          {row.reason}
        </div>

        <div className="w-[38%] shrink-0">
          {row.read.kind === "vot" ? (
            <ValueOnTrack
              mode="deviation"
              axis={row.read.axis}
              value={1 + row.read.deltaFrac}
              reference={1}
              referenceBandPct={row.read.bandFrac}
              size="compact"
              showValue={false}
              deltaTone={row.tier}
            />
          ) : (
            <GapPair
              mode="signed"
              externalPct={row.read.externalPct}
              internalPct={row.read.internalPct}
              deltaLabel={`${row.read.gapPts >= 0 ? "+" : ""}${row.read.gapPts} pts`}
              size="compact"
              tone={row.tier}
            />
          )}
        </div>

        <div className="ml-2 flex w-[92px] shrink-0 items-center justify-end gap-1.5">
          <span
            className="type-label opacity-0 transition-opacity group-hover:opacity-100"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            view athlete
          </span>
          <ChevronRight
            className="h-3.5 w-3.5"
            style={{ color: "var(--color-text-tertiary)" }}
          />
        </div>
      </button>
    </li>
  );
}

/* ---------- Tier 2 row — data to check ---------- */

function Tier2Row({
  count,
  expanded,
  onToggle,
  athletes,
}: {
  count: number;
  expanded: boolean;
  onToggle: () => void;
  athletes: Array<{ name: string; cov: number }>;
}) {
  return (
    <div
      className="border-t"
      style={{
        borderColor: "var(--color-border)",
        backgroundColor: "var(--color-slate-50)",
      }}
    >
      <div className="flex items-center gap-3 px-5 py-2.5">
        <span
          className="type-label"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          To check
        </span>
        <span className="text-[12.5px]" style={{ color: "var(--color-text-secondary)" }}>
          {count} to check · HR coverage below {COVERAGE_MIN}%
        </span>
        <button
          onClick={onToggle}
          className="ml-auto inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[12px] transition-colors hover:bg-[color:var(--color-slate-100)]"
          style={{ color: "var(--color-text-secondary)" }}
        >
          <span>{expanded ? "Hide athletes" : "Show athletes"}</span>
          {expanded ? (
            <ChevronDown className="h-3 w-3" />
          ) : (
            <ChevronRight className="h-3 w-3" />
          )}
        </button>
      </div>
      {expanded && (
        <ul className="px-5 pb-3 pt-1">
          {athletes.map((a) => (
            <li
              key={a.name}
              className="flex items-center gap-3 py-1.5 text-[12.5px]"
              style={{ color: "var(--color-text-secondary)" }}
            >
              <span
                className="h-1.5 w-1.5 rounded-full"
                style={{ backgroundColor: "var(--color-trust-dot)" }}
                aria-hidden
              />
              <span style={{ color: "var(--color-text-primary)" }}>{a.name}</span>
              <span className="type-num" style={{ color: "var(--color-text-tertiary)" }}>
                — {a.cov}% cov
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

/* ---------- Synthesis line ---------- */

function SynthesisLine({
  isAllClear,
  cantSay,
  filterIsDefault,
}: {
  isAllClear: boolean;
  cantSay: boolean;
  filterIsDefault: boolean;
}) {
  // Squad answer only — never re-scopes to the filter subset.
  const scopePrefix = !filterIsDefault ? (
    <span
      className="type-label mr-2"
      style={{ color: "var(--color-text-tertiary)" }}
    >
      Squad ·
    </span>
  ) : null;

  if (cantSay) {
    return (
      <div
        className="border-t px-5 py-3"
        style={{ borderColor: "var(--color-border)" }}
      >
        <div
          className="flex items-baseline text-[13px]"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          {scopePrefix}
          <span>Not enough coverage to read the squad's load today.</span>
        </div>
      </div>
    );
  }

  if (isAllClear) {
    return (
      <div
        className="border-t px-5 py-3"
        style={{ borderColor: "var(--color-border)" }}
      >
        <div
          className="flex items-baseline text-[13px]"
          style={{ color: "var(--color-text-secondary)" }}
        >
          {scopePrefix}
          <span>A steady session — loads in each athlete's typical range.</span>
        </div>
      </div>
    );
  }
  return (
    <div
      className="border-t px-5 py-3"
      style={{ borderColor: "var(--color-border)" }}
    >
      <div className="flex items-center gap-2">
        {scopePrefix}
        <span
          className="type-micro rounded px-1.5 py-0.5"
          style={{
            border: "1px solid var(--color-text-primary)",
            color: "var(--color-text-primary)",
          }}
        >
          notable
        </span>
        <span
          className="text-[13px] font-medium"
          style={{ color: "var(--color-text-primary)" }}
        >
          {copy("attention.closer")}
        </span>
      </div>
    </div>
  );
}

/* ---------- All-clear body ---------- */

function AllClearBody({ totalInScope }: { totalInScope: number }) {
  const lines = [
    "Loads within each athlete's typical range",
    "No internal-external divergence",
    `HR coverage checked on all ${totalInScope}`,
  ];
  return (
    <div className="px-5 pb-4 pt-4">
      <ul className="space-y-2">
        {lines.map((l) => (
          <li
            key={l}
            className="flex items-center gap-2.5 text-[13px]"
            style={{ color: "var(--color-text-secondary)" }}
          >
            <span
              className="h-1.5 w-1.5 rounded-full"
              style={{ backgroundColor: "var(--color-clear-ink)" }}
              aria-hidden
            />
            {l}
          </li>
        ))}
      </ul>
      <div className="mt-4 flex items-center gap-1.5">
        <button
          onClick={() => {
            document
              .getElementById("summary")
              ?.scrollIntoView({ behavior: "smooth", block: "start" });
          }}
          className="inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[12.5px] transition-colors hover:bg-[color:var(--color-slate-100)]"
          style={{ color: "var(--color-text-primary)", fontWeight: 500 }}
        >
          <span>Read the squad summary</span>
          <ChevronDown className="h-3.5 w-3.5" />
        </button>
      </div>
    </div>
  );
}
