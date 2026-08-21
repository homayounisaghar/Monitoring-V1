import { ChevronDown } from "lucide-react";
import { useState } from "react";
import { copy } from "@/lib/copy-deck";

/**
 * DegradedBanner — the ratified pattern for a section or screen that
 * cannot be read (see styleguide · "Degraded-state banner").
 *
 * Three parts, in this order:
 *   1. headline — one line, label slot (sentence case, sans). Never the
 *      display slot: a degraded state is not a hero read.
 *   2. summary  — one line stating the extent once. Numerals in the
 *      key-value slot; the sentence around them stays sans.
 *   3. detail   — collapsed by default, expandable. The full list never
 *      renders unopened, and never sets the banner's height.
 */
export function DegradedBanner({
  headline,
  summaryNumeral,
  summaryText,
  detailCount,
  children,
}: {
  headline: string;
  /** Numerals only — rendered in the key-value slot. */
  summaryNumeral?: string;
  /** The sentence around the numeral, sans, sentence case. */
  summaryText: string;
  /** Count shown on the disclosure control. Omit to hide the control. */
  detailCount?: number;
  /** The collapsed detail list. */
  children?: React.ReactNode;
}) {
  const [open, setOpen] = useState(false);
  const hasDetail = children != null && (detailCount ?? 0) > 0;

  return (
    <div>
      <div
        className="border-b px-5 py-4"
        style={{ borderColor: "var(--color-border)" }}
      >
        <p
          className="text-[15px] font-medium"
          style={{ color: "var(--color-text-primary)", letterSpacing: 0 }}
        >
          {headline}
        </p>

        <p className="mt-1.5 flex items-baseline gap-2">
          {summaryNumeral && (
            <span className="type-keyvalue">{summaryNumeral}</span>
          )}
          <span className="type-label">{summaryText}</span>
        </p>

        {hasDetail && (
          <button
            onClick={() => setOpen((o) => !o)}
            aria-expanded={open}
            className="mt-2.5 inline-flex items-center gap-1 rounded text-[12.5px] font-medium underline-offset-2 hover:underline"
            style={{ color: "var(--color-text-primary)" }}
          >
            <span>
              {open ? copy("degraded.detail.hide") : copy("degraded.detail.show")}
            </span>
            <span className="type-num" style={{ color: "var(--color-text-tertiary)" }}>
              {detailCount}
            </span>
            <ChevronDown
              className="h-3.5 w-3.5 transition-transform"
              style={{ transform: open ? "rotate(180deg)" : undefined }}
              aria-hidden
            />
          </button>
        )}
      </div>

      {hasDetail && open && (
        <div
          className="max-h-[240px] overflow-y-auto"
          style={{ backgroundColor: "var(--color-slate-50)" }}
        >
          {children}
        </div>
      )}
    </div>
  );
}
