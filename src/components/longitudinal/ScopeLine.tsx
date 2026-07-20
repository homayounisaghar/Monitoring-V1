/**
 * Longitudinal — scope line.
 *
 * The two clauses are load-bearing text (Summary tick and Days 100-line
 * echo them), so their wording is preserved verbatim; only the offering
 * affordance is removed. The Filter button and panel are gone as a demo
 * removal — they scoped nothing — and reinstate when scoping is wired.
 * `How to read this` stays and now opens the legend.
 */
import { copy } from "@/lib/copy-deck";
import { LegendPopover } from "./LegendPopover";
import type { LongiWindow } from "@/lib/longitudinal-data";

export function ScopeLine({ window: w }: { window: LongiWindow }) {
  return (
    <div className="flex min-w-0 flex-1 items-center gap-3">
      <span
        className="text-[12.5px]"
        style={{ color: "var(--color-text-secondary)" }}
      >
        {copy("longi.scope.benchmarkChip")}
        <span
          aria-hidden
          className="mx-2"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          ·
        </span>
        {copy("longi.scope.referenceChip")}
      </span>
      <div className="ml-auto flex items-center gap-3">
        <LegendPopover window={w} />
      </div>
    </div>
  );
}
