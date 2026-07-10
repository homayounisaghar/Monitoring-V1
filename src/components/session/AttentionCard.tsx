/**
 * ST2 — Attention card (RW2).
 *
 * Contract (A9): the card computes SQUAD-WIDE. Filters never re-scope
 * the tier-1 read; when a filter hides an escalation, one neutral line
 * names the out-of-scope escalation.
 *
 * Anatomy:
 *   1. Headline slot — display "N" + suffix, right meta "K of T clear · (i)"
 *   2. Tier rows — escalate (large) then notice (bare diamond + slate delta)
 *   3. Row phrase = metric names only; delta prints once at the right
 *   4. Gap dialect for gap-read rows (paired value + "pts" unit)
 *   5. Accounting line — "To check — {names+cov} · Köhler — baseline, 3 of 5"
 *   6. Card close — the squad read as the card's only sentence
 *   7. Edge states — coverage-thin > all-clear > flags
 */
import { useNavigate } from "@tanstack/react-router";
import { Info, ChevronDown } from "lucide-react";
import { useSessionScope, COVERAGE_MIN } from "@/lib/session-scope";
import {
  BUILDING_ID,
  BUILDING_SESSIONS_TO_MIN,
  type Tier1Row,
} from "@/lib/session-flags";
import { copy, tmpl, BUILDING_BASELINE_MIN_SESSIONS } from "@/lib/copy-deck";
import { ValueOnTrack } from "@/components/data/ValueOnTrack";

/* ---------- Component ---------- */

export function AttentionCard() {
  const {
    effectiveParticipants,
    tier1Rows,
    activeAthletes,
    filterIsDefault,
    totalParticipants,
  } = useSessionScope();

  // A9 — always squad-wide.
  const tier1 = tier1Rows;
  const squadLowCov = effectiveParticipants.filter(
    (a) => a.hrCoveragePct !== null && a.hrCoveragePct < COVERAGE_MIN,
  );
  const building = effectiveParticipants.filter((a) => a.id === BUILDING_ID);

  const escalateCount = tier1.filter((r) => r.tier === "escalate").length;
  const flaggedSet = new Set<string>([
    ...tier1.map((r) => r.id),
    ...squadLowCov.map((a) => a.id),
    ...building.map((a) => a.id),
  ]);
  const clearCount = effectiveParticipants.length - flaggedSet.size;
  const manageCount = tier1.length;

  const isAllClear = tier1.length === 0 && squadLowCov.length === 0;
  const isCovThin =
    tier1.length === 0 &&
    squadLowCov.length / effectiveParticipants.length > 0.5;

  // Out-of-scope escalation notice (A9).
  const inScopeIds = new Set(activeAthletes.map((a) => a.id));
  const outsideEscalations = !filterIsDefault
    ? tier1.filter((r) => r.tier === "escalate" && !inScopeIds.has(r.id))
    : [];

  return (
    <section id="attention" className="scroll-mt-28">
      <header className="mb-3">
        <h2 className="type-section-h">{copy("canonical.section.attention")}</h2>
      </header>

      <div
        className="overflow-hidden rounded-lg border"
        style={{
          borderColor: "var(--color-border)",
          backgroundColor: "var(--color-surface-card)",
        }}
      >
        {/* Headline slot */}
        <Headline
          state={isCovThin ? "covThin" : isAllClear ? "allClear" : "flags"}
          manageCount={manageCount}
          clearCount={clearCount}
          totalSquad={totalParticipants}
          squadLowCov={squadLowCov.length}
        />

        {/* Body by state */}
        {isCovThin ? (
          <CovThinBody rows={squadLowCov.map((a) => ({ name: a.name, cov: a.hrCoveragePct ?? 0 }))} />
        ) : isAllClear ? (
          <AllClearBody buildCount={building.length} />
        ) : (
          <>
            <ul>
              {tier1.map((r) => (
                <Tier1RowUI key={r.id} row={r} />
              ))}
            </ul>

            {outsideEscalations.length > 0 && (
              <OutsideEscalationLine />
            )}

            <AccountingLine
              lowCov={squadLowCov.map((a) => ({ name: a.name, cov: a.hrCoveragePct ?? 0 }))}
              buildCount={building.length}
            />

            <CloserLine />
          </>
        )}
      </div>
    </section>
  );
}

/* ---------- Headline ---------- */

function Headline({
  state,
  manageCount,
  clearCount,
  totalSquad,
  squadLowCov,
}: {
  state: "flags" | "allClear" | "covThin";
  manageCount: number;
  clearCount: number;
  totalSquad: number;
  squadLowCov: number;
}) {
  if (state === "covThin") {
    return (
      <div
        className="flex items-baseline justify-between gap-6 border-b px-5 py-4"
        style={{ borderColor: "var(--color-border)" }}
      >
        <span
          className="type-display"
          style={{ color: "var(--color-text-primary)" }}
        >
          {tmpl("attention.covThin.headlineTemplate", {
            below: squadLowCov,
            total: totalSquad,
          })}
        </span>
      </div>
    );
  }

  if (state === "allClear") {
    return (
      <div
        className="flex items-baseline justify-between gap-6 border-b px-5 py-4"
        style={{ borderColor: "var(--color-border)" }}
      >
        <div className="flex items-baseline gap-2">
          <span
            className="text-[18px] font-semibold tracking-tight"
            style={{ color: "var(--color-text-primary)" }}
          >
            {tmpl("attention.allClear", { n: clearCount, total: totalSquad })}
          </span>
        </div>
      </div>
    );
  }

  return (
    <div
      className="flex items-baseline justify-between gap-6 border-b px-5 pb-4 pt-5"
      style={{ borderColor: "var(--color-border)" }}
    >
      <div className="flex items-baseline gap-3">
        <span
          className="type-display"
          style={{ color: "var(--color-text-primary)" }}
        >
          {manageCount}
        </span>
        <span
          className="text-[15px] font-medium"
          style={{ color: "var(--color-text-primary)" }}
        >
          {copy("attention.headline.suffix")}
        </span>
      </div>
      <div className="flex items-center gap-2">
        <span
          className="text-[12.5px]"
          style={{ color: "var(--color-text-secondary)" }}
        >
          {tmpl("attention.headline.metaTemplate", { clear: clearCount, total: totalSquad })}
        </span>
        <button
          type="button"
          onClick={() => {
            document
              .getElementById("legend")
              ?.scrollIntoView({ behavior: "smooth", block: "start" });
          }}
          className="inline-flex h-5 w-5 items-center justify-center rounded-full transition-colors hover:bg-[color:var(--color-slate-100)]"
          style={{ color: "var(--color-text-tertiary)" }}
          aria-label={copy("control.legend")}
        >
          <Info className="h-3.5 w-3.5" />
        </button>
      </div>
    </div>
  );
}

/* ---------- Tier 1 row ---------- */

function Tier1RowUI({ row }: { row: Tier1Row }) {
  const { effectiveParticipants } = useSessionScope();
  const navigate = useNavigate();
  const athlete = effectiveParticipants.find((a) => a.id === row.id);
  if (!athlete) return null;

  const isEscalate = row.tier === "escalate";

  // Delta printed once, at the right, sized per tier.
  const deltaText =
    row.read.kind === "vot"
      ? `${row.read.deltaFrac >= 0 ? "+" : ""}${Math.round(row.read.deltaFrac * 100)}%`
      : null;

  const nameCls = isEscalate
    ? "text-[16px] font-semibold leading-tight"
    : "text-[14px] font-medium leading-tight";
  const rowPad = isEscalate ? "py-4" : "py-3";

  return (
    <li
      className={`group relative border-b last:border-b-0 transition-colors hover:bg-[color:var(--color-slate-50)]`}
      style={{ borderColor: "var(--color-border)" }}
    >
      <button
        className={`flex w-full items-center gap-4 px-5 text-left ${rowPad}`}
        onClick={() => navigate({ to: "/athlete" })}
      >
        {/* Tier mark — pigment lives here, not on numerals (unless escalate delta) */}
        <div className="w-[92px] shrink-0">
          {isEscalate ? (
            <span
              className="inline-flex items-center gap-1.5 rounded px-1.5 py-0.5 type-micro"
              style={{
                backgroundColor: "var(--color-escalate-surface)",
                color: "var(--color-escalate-ink)",
              }}
            >
              <svg width={10} height={10} viewBox="0 0 10 10" aria-hidden>
                <polygon points="5,1 9.5,9 0.5,9" fill="currentColor" />
              </svg>
              {copy("canonical.severity.escalate")}
            </span>
          ) : (
            <span
              className="inline-flex items-center gap-1.5 type-micro"
              style={{ color: "var(--color-text-secondary)" }}
            >
              <svg width={9} height={9} viewBox="0 0 10 10" aria-hidden>
                <polygon
                  points="5,1 9,5 5,9 1,5"
                  fill="var(--color-notice-ink)"
                />
              </svg>
              {copy("canonical.severity.notice")}
            </span>
          )}
        </div>

        <div className="w-[170px] shrink-0">
          <div className={nameCls} style={{ color: "var(--color-text-primary)" }}>
            {athlete.name}
          </div>
          <div
            className="type-label"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            {athlete.posDetail}
          </div>
        </div>

        {/* Phrase = metric names only. No delta here. */}
        <div
          className="min-w-0 flex-1 text-[13px]"
          style={{ color: "var(--color-text-secondary)" }}
        >
          {row.reason}
        </div>

        {/* Track = position; no delta echo on the track */}
        <div className="w-[34%] shrink-0">
          {row.read.kind === "vot" ? (
            <ValueOnTrack
              mode="deviation"
              axis={row.read.axis}
              value={1 + row.read.deltaFrac}
              reference={1}
              referenceBandPct={row.read.bandFrac}
              size="compact"
              showValue={false}
              showDelta={false}
              deltaTone="default"
            />
          ) : (
            <GapMiniTrack
              externalPct={row.read.externalPct}
              internalPct={row.read.internalPct}
            />
          )}
        </div>

        {/* Delta — one place, sized per tier */}
        <div className="ml-2 flex w-[92px] shrink-0 items-baseline justify-end">
          {row.read.kind === "vot" ? (
            <span
              className={
                isEscalate
                  ? "type-num text-[21px] font-semibold"
                  : "type-num text-[14px] font-semibold"
              }
              style={{
                color: isEscalate
                  ? "var(--color-escalate-ink)"
                  : "var(--color-text-primary)",
              }}
            >
              {deltaText}
            </span>
          ) : (
            <span className="inline-flex items-baseline gap-0.5">
              <span
                className={
                  isEscalate
                    ? "type-num text-[21px] font-semibold"
                    : "type-num text-[14px] font-semibold"
                }
                style={{
                  color: isEscalate
                    ? "var(--color-escalate-ink)"
                    : "var(--color-text-primary)",
                }}
              >
                {`${row.read.gapPts >= 0 ? "+" : ""}${row.read.gapPts}`}
              </span>
              <span
                className="type-data-label"
                style={{ color: "var(--color-text-tertiary)" }}
              >
                {copy("canonical.attention.pts")}
              </span>
            </span>
          )}
        </div>
      </button>
    </li>
  );
}

/* Track-only signed gap for the row read (no delta — that lives at right) */
function GapMiniTrack({
  externalPct,
  internalPct,
}: {
  externalPct: number;
  internalPct: number;
}) {
  const W = 40;
  const toPos = (v: number) =>
    ((Math.max(-W, Math.min(W, v)) + W) / (W * 2)) * 100;
  const extPos = toPos(externalPct);
  const intPos = toPos(internalPct);
  const left = Math.min(extPos, intPos);
  const right = Math.max(extPos, intPos);

  return (
    <div className="relative h-5">
      <div
        className="absolute left-0 right-0 top-1/2 h-[6px] -translate-y-1/2 rounded-full"
        style={{ backgroundColor: "var(--color-data-band)" }}
      />
      <div
        className="absolute top-1/2 h-3 w-[2px] -translate-x-1/2 -translate-y-1/2 rounded-sm"
        style={{ left: "50%", backgroundColor: "var(--color-data-reference)" }}
      />
      <div
        className="absolute top-1/2 h-[2px] -translate-y-1/2"
        style={{
          left: `${left}%`,
          width: `${right - left}%`,
          backgroundColor: "var(--color-slate-400)",
        }}
      />
      <div
        className="absolute top-1/2 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full ring-2 ring-white"
        style={{ left: `${extPos}%`, backgroundColor: "var(--color-axis-work)" }}
      />
      <div
        className="absolute top-1/2 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full bg-white"
        style={{
          left: `${intPos}%`,
          border: "2px solid var(--color-axis-cost)",
        }}
      />
    </div>
  );
}

/* ---------- Outside-scope escalation neutral line ---------- */

function OutsideEscalationLine() {
  return (
    <div
      className="border-t px-5 py-2.5 text-[12.5px]"
      style={{
        borderColor: "var(--color-border)",
        color: "var(--color-text-secondary)",
      }}
    >
      {copy("attention.filtered.escalationOutside")}
    </div>
  );
}

/* ---------- Accounting line (A5) ---------- */

function AccountingLine({
  lowCov,
  buildCount,
}: {
  lowCov: Array<{ name: string; cov: number }>;
  buildCount: number;
}) {
  if (lowCov.length === 0 && buildCount === 0) return null;

  const parts: Array<React.ReactNode> = [];

  if (lowCov.length > 0) {
    parts.push(
      <span key="prefix" style={{ color: "var(--color-text-tertiary)" }}>
        {copy("attention.accountingLine.prefix")} —{" "}
      </span>,
    );
    lowCov.forEach((a, i) => {
      parts.push(
        <span
          key={`n-${a.name}`}
          title={`${a.cov}${copy("canonical.attention.hrCoverageSuffix")}`}
          className="cursor-help"
          style={{ color: "var(--color-text-secondary)" }}
        >
          {a.name}{" "}
          <span className="type-num" style={{ color: "var(--color-text-tertiary)" }}>
            {a.cov}
            {i === lowCov.length - 1 ? copy("canonical.attention.hrCovSuffix") : ""}
          </span>
        </span>,
      );
      if (i < lowCov.length - 1) {
        parts.push(
          <span key={`sep-${i}`} style={{ color: "var(--color-text-tertiary)" }}>
            {" · "}
          </span>,
        );
      }
    });
  }

  if (buildCount > 0) {
    if (parts.length > 0) {
      parts.push(
        <span key="build-sep" style={{ color: "var(--color-text-tertiary)" }}>
          {"  ·  "}
        </span>,
      );
    }
    parts.push(
      <span key="build" style={{ color: "var(--color-text-secondary)" }}>
        B. Köhler —{" "}
        {tmpl("attention.baseline.suffixTemplate", {
          done: BUILDING_SESSIONS_TO_MIN,
          min: BUILDING_BASELINE_MIN_SESSIONS,
        })}
      </span>,
    );
  }

  return (
    <div
      className="border-t px-5 py-2.5 text-[12.5px]"
      style={{
        borderColor: "var(--color-border)",
        backgroundColor: "var(--color-slate-50)",
      }}
    >
      {parts}
    </div>
  );
}

/* ---------- Card close (A6) ---------- */

function CloserLine() {
  return (
    <div
      className="border-t px-5 py-3 text-[13px] font-medium"
      style={{
        borderColor: "var(--color-border)",
        color: "var(--color-text-primary)",
      }}
    >
      {copy("attention.closer")}
    </div>
  );
}

/* ---------- All-clear body ---------- */

function AllClearBody({ buildCount }: { buildCount: number }) {
  return (
    <div className="px-5 pb-4 pt-3">
      {buildCount > 0 && (
        <div
          className="text-[12.5px]"
          style={{ color: "var(--color-text-secondary)" }}
        >
          B. Köhler —{" "}
          {tmpl("attention.baseline.suffixTemplate", {
            done: BUILDING_SESSIONS_TO_MIN,
            min: BUILDING_BASELINE_MIN_SESSIONS,
          })}
        </div>
      )}
      <div className="mt-3">
        <button
          onClick={() => {
            document
              .getElementById("summary")
              ?.scrollIntoView({ behavior: "smooth", block: "start" });
          }}
          className="inline-flex items-center gap-1 rounded text-[12.5px] underline-offset-2 hover:underline"
          style={{ color: "var(--color-text-primary)", fontWeight: 500 }}
        >
          <span>{copy("attention.allClear.link")}</span>
          <ChevronDown className="h-3.5 w-3.5" />
        </button>
      </div>
    </div>
  );
}

/* ---------- Coverage-thin body ---------- */

function CovThinBody({
  rows,
}: {
  rows: Array<{ name: string; cov: number }>;
}) {
  return (
    <ul className="px-5 pb-4 pt-3">
      {rows.map((a) => (
        <li
          key={a.name}
          className="flex items-baseline gap-3 py-1 text-[13px]"
          style={{ color: "var(--color-text-secondary)" }}
        >
          <span
            className="h-1.5 w-1.5 rounded-full"
            style={{
              backgroundColor: "transparent",
              border: "1.25px solid var(--color-trust-dot)",
            }}
            aria-hidden
          />
          <span style={{ color: "var(--color-text-primary)" }}>{a.name}</span>
          <span className="type-num" style={{ color: "var(--color-text-tertiary)" }}>
            {a.cov}{copy("canonical.attention.hrCovSuffix")}
          </span>
        </li>
      ))}
    </ul>
  );
}
