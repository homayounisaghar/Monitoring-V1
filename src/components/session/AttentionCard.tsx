/**
 * ST2 — Attention card.
 * The coach's 5-second answer to "who needs me?". This is the only place
 * severity ink and the severity glyphs are allowed to appear.
 */
import { useState } from "react";
import { ChevronRight, ChevronDown } from "lucide-react";
import { useSessionScope } from "@/lib/session-scope";
import { participants } from "@/lib/session-data";

type Tier = "escalate" | "notice";

/* ---------- Data (derived from participants, not hardcoded counts) ---------- */

type Tier1Row = {
  id: string;               // athlete id
  tier: Tier;
  reason: string;
  read:
    | {
        kind: "vot";
        axis: "work" | "cost" | "neutral";
        // deviation (relative to athlete's own typical), in fractions
        deltaFrac: number;    // e.g. 0.34 = +34%
        bandFrac: number;     // half-width of the typical band
      }
    | {
        kind: "gap";
        externalPct: number;   // signed deviation vs his typical (%)
        internalPct: number;
        gapPts: number;
      };
};

const TIER1_ROWS: Tier1Row[] = [
  {
    id: "fischer",
    tier: "escalate",
    reason: "Sprint distance +34% · +1 more",
    read: { kind: "vot", axis: "work", deltaFrac: 0.34, bandFrac: 0.10 },
  },
  {
    id: "werner",
    tier: "notice",
    reason: "High-speed running +22%",
    read: { kind: "vot", axis: "work", deltaFrac: 0.22, bandFrac: 0.10 },
  },
  {
    id: "schaefer",
    tier: "notice",
    reason: "External up · cardio flat",
    read: { kind: "gap", externalPct: 19, internalPct: -3, gapPts: 22 },
  },
  {
    id: "hofmann",
    tier: "notice",
    reason: "Total distance +14%",
    read: { kind: "vot", axis: "work", deltaFrac: 0.14, bandFrac: 0.14 },
  },
];

// Tier 2 — data-to-check, HR coverage below 80%. Comes from data, not literals.
const COVERAGE_MIN = 80;

// Building baseline
const BUILDING_ID = "koehler";
const BUILDING_SESSIONS_TO_MIN = 3;

/* ---------- Component ---------- */

export function AttentionCard() {
  const { demo, activeAthletes, filterIsDefault, scopeLabel } = useSessionScope();
  const [showCheck, setShowCheck] = useState(false);

  const total = participants.length; // "of 18" invariant, derived
  const inScope = new Set(activeAthletes.map((a) => a.id));

  const tier1 = TIER1_ROWS.filter((r) => inScope.has(r.id));
  const lowCovAthletes = activeAthletes.filter(
    (a) => a.hrCoveragePct !== null && a.hrCoveragePct < COVERAGE_MIN
  );
  const building = activeAthletes.filter((a) => a.id === BUILDING_ID);

  const escalateCount = tier1.filter((r) => r.tier === "escalate").length;
  const noticeCount = tier1.filter((r) => r.tier === "notice").length;
  const manageCount = tier1.length;
  const checkCount = lowCovAthletes.length;
  const buildCount = building.length;

  const isAllClear = demo === "all_clear";

  // "clear" = participants NOT in tier1, NOT in tier2, NOT building baseline
  const flaggedIds = new Set<string>([
    ...tier1.map((r) => r.id),
    ...lowCovAthletes.map((a) => a.id),
    ...building.map((a) => a.id),
  ]);
  const clearCount = isAllClear
    ? activeAthletes.length - buildCount // all clear except building baseline
    : activeAthletes.length - flaggedIds.size;
  const totalInScope = activeAthletes.length;

  return (
    <section id="attention" className="scroll-mt-28">
      {/* Section header — the h2 is the label; the card carries NO eyebrow */}
      <header className="mb-3 flex items-baseline justify-between gap-4">
        <div className="flex items-baseline gap-3">
          <h2 className="type-section-h">Attention</h2>
          {!filterIsDefault && scopeLabel && (
            <span
              className="type-card-eyebrow"
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

      {/* The card */}
      <div
        className="overflow-hidden rounded-lg border"
        style={{
          borderColor: "var(--color-border)",
          backgroundColor: "var(--color-surface-card)",
        }}
      >
        {/* Card header */}
        <div className="flex items-start justify-between gap-6 border-b px-5 pb-3 pt-4"
             style={{ borderColor: "var(--color-border)" }}>
          <div className="min-w-0">
            {isAllClear ? (
              <>
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
              </>
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

        {/* Tier 1 rows — or all-clear substantiation */}
        {isAllClear ? (
          <AllClearBody totalInScope={totalInScope} />
        ) : (
          <ul>
            {tier1.map((r) => (
              <Tier1RowUI key={r.id} row={r} />
            ))}
          </ul>
        )}

        {/* Tier 2 — data to check */}
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

        {/* Building baseline line — remains in all-clear too */}
        {buildCount > 0 && (
          <div
            className="flex items-center gap-3 border-t px-5 py-2.5"
            style={{
              borderColor: "var(--color-border)",
              backgroundColor: "var(--color-slate-50)",
            }}
          >
            <span
              className="type-card-eyebrow"
              style={{ color: "var(--color-text-tertiary)" }}
            >
              Building baseline
            </span>
            <span className="text-[12.5px]" style={{ color: "var(--color-text-secondary)" }}>
              B. Köhler · {BUILDING_SESSIONS_TO_MIN} sessions to minimum history
            </span>
          </div>
        )}

        {/* Synthesis line */}
        <SynthesisLine isAllClear={isAllClear} />
      </div>

      {/* Seam — coach-to-analyst boundary */}
      <div className="mt-8">
        <div
          className="h-px w-full"
          style={{ backgroundColor: "var(--color-border)" }}
        />
        <div
          className="type-card-eyebrow pt-3"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          Depth · Summary · Periods · Squad
        </div>
      </div>
    </section>
  );
}

/* ---------- Tier 1 row ---------- */

function Tier1RowUI({ row }: { row: Tier1Row }) {
  const athlete = participants.find((a) => a.id === row.id);
  if (!athlete) return null;

  return (
    <li
      className="group relative border-b last:border-b-0 transition-colors hover:bg-[color:var(--color-slate-50)]"
      style={{ borderColor: "var(--color-border)" }}
    >
      <button
        className="flex w-full items-center gap-4 px-5 py-3 text-left"
        onClick={() => {
          // Would route to /athlete/:id when built.
        }}
      >
        {/* Glyph + word */}
        <div className="w-[92px] shrink-0">
          <SeverityGlyph tier={row.tier} />
        </div>

        {/* Name + position */}
        <div className="w-[170px] shrink-0">
          <div
            className="text-[13.5px] font-medium leading-tight"
            style={{ color: "var(--color-text-primary)" }}
          >
            {athlete.name}
          </div>
          <div
            className="type-card-eyebrow"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            {athlete.posDetail}
          </div>
        </div>

        {/* Reason label */}
        <div
          className="min-w-0 flex-1 text-[13px]"
          style={{ color: "var(--color-text-secondary)" }}
        >
          {row.reason}
        </div>

        {/* Read — contained ~40% width */}
        <div className="w-[38%] shrink-0">
          {row.read.kind === "vot" ? (
            <MiniValueOnTrack
              axis={row.read.axis}
              deltaFrac={row.read.deltaFrac}
              bandFrac={row.read.bandFrac}
              tier={row.tier}
            />
          ) : (
            <MiniGapPair
              externalPct={row.read.externalPct}
              internalPct={row.read.internalPct}
              gapPts={row.read.gapPts}
              tier={row.tier}
            />
          )}
        </div>

        {/* Hover affordance + chevron */}
        <div className="ml-2 flex w-[92px] shrink-0 items-center justify-end gap-1.5">
          <span
            className="type-card-eyebrow opacity-0 transition-opacity group-hover:opacity-100"
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
          className="type-card-eyebrow"
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

function SynthesisLine({ isAllClear }: { isAllClear: boolean }) {
  if (isAllClear) {
    return (
      <div
        className="border-t px-5 py-3"
        style={{ borderColor: "var(--color-border)" }}
      >
        <div className="text-[13px]" style={{ color: "var(--color-text-secondary)" }}>
          A steady session — loads in each athlete's typical range.
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
          A hard, high-intensity match — external work ran ahead of cardio cost, led by the front line.
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
            document.getElementById("summary")?.scrollIntoView({ behavior: "smooth", block: "start" });
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

/* ---------- Data objects (compact, in-row) ---------- */

function SeverityGlyph({ tier }: { tier: Tier }) {
  if (tier === "escalate") {
    return (
      <span
        className="inline-flex items-center gap-1 rounded px-1.5 py-0.5 type-micro"
        style={{
          backgroundColor: "var(--color-escalate-surface)",
          color: "var(--color-escalate-ink)",
        }}
      >
        <svg width="9" height="9" viewBox="0 0 10 10" aria-hidden>
          <polygon points="5,1 9.5,9 0.5,9" fill="currentColor" />
        </svg>
        escalate
      </span>
    );
  }
  return (
    <span
      className="inline-flex items-center gap-1 rounded px-1.5 py-0.5 type-micro"
      style={{
        backgroundColor: "var(--color-notice-surface)",
        color: "var(--color-notice-ink)",
      }}
    >
      <svg width="9" height="9" viewBox="0 0 10 10" aria-hidden>
        <polygon points="5,1 9,5 5,9 1,5" fill="currentColor" />
      </svg>
      notice
    </span>
  );
}

function axisFill(axis: "work" | "cost" | "neutral") {
  if (axis === "work") return "var(--color-axis-work)";
  if (axis === "cost") return "var(--color-axis-cost)";
  return "var(--color-data-ink)";
}

/** Deviation mode, ±40% window. Band around the tick = his normal range. */
function MiniValueOnTrack({
  axis,
  deltaFrac,
  bandFrac,
  tier,
}: {
  axis: "work" | "cost" | "neutral";
  deltaFrac: number;
  bandFrac: number;
  tier: Tier;
}) {
  const WINDOW = 0.4;
  const posPct = Math.max(
    0,
    Math.min(100, ((Math.max(-WINDOW, Math.min(WINDOW, deltaFrac)) + WINDOW) / (WINDOW * 2)) * 100)
  );
  const refPct = 50;
  const bandLeftPct = ((-bandFrac + WINDOW) / (WINDOW * 2)) * 100;
  const bandRightPct = ((bandFrac + WINDOW) / (WINDOW * 2)) * 100;
  const deltaPct = deltaFrac * 100;
  const deltaLabel = `${deltaPct >= 0 ? "+" : ""}${deltaPct.toFixed(0)}%`;
  const deltaInk =
    tier === "escalate" ? "var(--color-escalate-ink)" : "var(--color-notice-ink)";

  return (
    <div className="flex items-center gap-2.5">
      <div className="relative h-5 flex-1">
        <div
          className="absolute left-0 right-0 top-1/2 h-[6px] -translate-y-1/2 rounded-full"
          style={{ backgroundColor: "var(--color-data-band)" }}
        />
        <div
          className="absolute top-1/2 h-[9px] -translate-y-1/2 rounded-sm"
          style={{
            left: `${bandLeftPct}%`,
            width: `${bandRightPct - bandLeftPct}%`,
            backgroundColor: "var(--color-reference-band)",
          }}
        />
        <div
          className="absolute top-1/2 h-3 w-[2px] -translate-x-1/2 -translate-y-1/2 rounded-sm"
          style={{ left: `${refPct}%`, backgroundColor: "var(--color-data-reference)" }}
        />
        <div
          className="absolute top-1/2 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full ring-2 ring-white"
          style={{ left: `${posPct}%`, backgroundColor: axisFill(axis) }}
        />
      </div>
      <span
        className="type-num w-[54px] shrink-0 text-right text-[12.5px] font-semibold"
        style={{ color: deltaInk }}
      >
        {deltaLabel}
      </span>
    </div>
  );
}

/** Signed deviation GapPair — 0-line = "his typical". */
function MiniGapPair({
  externalPct,
  internalPct,
  gapPts,
  tier,
}: {
  externalPct: number;
  internalPct: number;
  gapPts: number;
  tier: Tier;
}) {
  const WINDOW = 40; // % window each side
  const toPos = (v: number) =>
    ((Math.max(-WINDOW, Math.min(WINDOW, v)) + WINDOW) / (WINDOW * 2)) * 100;
  const extPos = toPos(externalPct);
  const intPos = toPos(internalPct);
  const left = Math.min(extPos, intPos);
  const right = Math.max(extPos, intPos);
  const deltaInk =
    tier === "escalate" ? "var(--color-escalate-ink)" : "var(--color-notice-ink)";

  return (
    <div className="flex items-center gap-2.5">
      <div className="relative h-5 flex-1">
        <div
          className="absolute left-0 right-0 top-1/2 h-[6px] -translate-y-1/2 rounded-full"
          style={{ backgroundColor: "var(--color-data-band)" }}
        />
        {/* 0-line = his typical */}
        <div
          className="absolute top-1/2 h-3 w-[2px] -translate-x-1/2 -translate-y-1/2 rounded-sm"
          style={{ left: "50%", backgroundColor: "var(--color-data-reference)" }}
          title="his typical"
        />
        {/* connector */}
        <div
          className="absolute top-1/2 h-[2px] -translate-y-1/2"
          style={{
            left: `${left}%`,
            width: `${right - left}%`,
            backgroundColor: "var(--color-slate-400)",
          }}
        />
        {/* external — filled blue */}
        <div
          className="absolute top-1/2 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full ring-2 ring-white"
          style={{ left: `${extPos}%`, backgroundColor: "var(--color-axis-work)" }}
        />
        {/* internal — open purple ring */}
        <div
          className="absolute top-1/2 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full bg-white"
          style={{
            left: `${intPos}%`,
            border: "2px solid var(--color-axis-cost)",
          }}
        />
      </div>
      <span
        className="type-num w-[54px] shrink-0 text-right text-[12.5px] font-semibold"
        style={{ color: deltaInk }}
      >
        {gapPts >= 0 ? "+" : ""}
        {gapPts} pts
      </span>
    </div>
  );
}
