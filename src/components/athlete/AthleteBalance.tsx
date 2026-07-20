/**
 * ST2 — Athlete page · Balance block.
 *
 * A compact horizontal L/R bar in slate, sitting directly beneath the
 * Summary spine inside the same Summary section. The tick on the bar is
 * the athlete's OWN typical split — never the midpoint. Balance renders
 * quieter than the spine, which remains the page's primary object, and
 * carries no severity or on-canvas explanation; the legend states its
 * meaning and that it is not used for flags.
 */

import { copy, tmpl } from "@/lib/copy-deck";
import { balanceForSession, balanceTypicalFor, RECOVERY_INK_VAR } from "@/lib/recovery-data";

type Props = {
  athleteId: string;
  sessionId: string;
};

export function AthleteBalance({ athleteId, sessionId }: Props) {
  const bal = balanceForSession(athleteId, sessionId);
  const typ = balanceTypicalFor(athleteId);

  return (
    <section
      className="mt-3 rounded-lg border"
      style={{
        backgroundColor: "var(--color-surface-card)",
        borderColor: "var(--color-border)",
      }}
      data-section="athlete-balance"
    >
      <div
        className="flex items-baseline justify-between border-b px-5 py-2"
        style={{ borderColor: "var(--color-border)" }}
      >
        <h3
          className="type-section-h text-[13px]"
          style={{ color: "var(--color-text-primary)" }}
        >
          {copy("athlete.balance.title")}
        </h3>
        {bal ? (
          <span
            className="type-num text-[12px]"
            style={{ color: "var(--color-text-secondary)" }}
          >
            {tmpl("athlete.balance.splitTemplate", { l: bal.leftPct, r: bal.rightPct })}
          </span>
        ) : null}
      </div>

      <div className="px-5 py-3">
        {bal ? (
          <>
            <BalanceBar
              leftPct={bal.leftPct}
              typicalLeftPct={typ.leftPct}
            />
            <div
              className="mt-2 flex items-baseline justify-between text-[11.5px]"
              style={{ color: "var(--color-text-tertiary)" }}
            >
              <span aria-hidden>L</span>
              <span>
                {bal.deltaPts === 0
                  ? copy("athlete.balance.deltaZero")
                  : tmpl("athlete.balance.deltaTemplate", {
                      sign: bal.deltaPts > 0 ? "+" : "−",
                      d: Math.abs(bal.deltaPts),
                    })}
              </span>
              <span aria-hidden>R</span>
            </div>
          </>
        ) : (
          <span
            className="type-data-label italic text-[11.5px]"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            {copy("athlete.balance.unavailable")}
          </span>
        )}
      </div>
    </section>
  );
}

function BalanceBar({
  leftPct,
  typicalLeftPct,
}: {
  leftPct: number;
  typicalLeftPct: number;
}) {
  return (
    <div className="relative h-3 w-full rounded-full" style={{ backgroundColor: "var(--color-slate-100)" }}>
      {/* L fill in slate */}
      <div
        className="absolute inset-y-0 left-0 rounded-l-full"
        style={{
          width: `${leftPct}%`,
          backgroundColor: RECOVERY_INK_VAR,
          opacity: 0.55,
        }}
        aria-hidden
      />
      {/* R fill — same slate but lighter, so the split is visible without a
          second hue. */}
      <div
        className="absolute inset-y-0 right-0 rounded-r-full"
        style={{
          width: `${100 - leftPct}%`,
          backgroundColor: RECOVERY_INK_VAR,
          opacity: 0.28,
        }}
        aria-hidden
      />
      {/* Typical tick — the reference. Not at the midpoint. */}
      <div
        className="absolute top-1/2 h-4 w-[2px] -translate-x-1/2 -translate-y-1/2 rounded-sm"
        style={{
          left: `${typicalLeftPct}%`,
          backgroundColor: "var(--color-data-reference)",
        }}
        title={copy("athlete.balance.tickHover")}
        aria-label="typical split"
      />
    </div>
  );
}
