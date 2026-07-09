/**
 * TrustMark — trust grammar.
 *
 * Grammar: a small HOLLOW dot precedes a clean value. Coverage sits on
 * hover as a native tooltip (e.g. "74% HR coverage"). Texture NEVER sits
 * behind numerals — the hatched veil is retired from this component.
 *
 * The dot is the trust affordance; the number stays legible at every size.
 */
export type TrustMarkProps = {
  size?: "sm" | "md" | "lg";
  value: string;
  unit?: string;
  coverage: number; // 0-100
  /** What is being covered — surfaces in the hover string. Default: "coverage". */
  coverageOf?: string;
};

export function TrustMark({
  size = "md",
  value,
  unit,
  coverage,
  coverageOf = "coverage",
}: TrustMarkProps) {
  const dot = { sm: "h-1.5 w-1.5", md: "h-2 w-2", lg: "h-2.5 w-2.5" }[size];
  const num = { sm: "text-xs", md: "text-sm", lg: "text-base" }[size];
  const hover = `${coverage}% ${coverageOf}`;

  return (
    <span
      className="inline-flex items-baseline gap-1.5"
      title={hover}
      aria-label={`${value}${unit ? " " + unit : ""} — ${hover}`}
    >
      <span
        className={`${dot} inline-block shrink-0 translate-y-[-1px] rounded-full`}
        style={{
          backgroundColor: "transparent",
          border: "1.25px solid var(--color-trust-dot)",
        }}
        aria-hidden
      />
      <span
        className={`type-num ${num} font-semibold`}
        style={{ color: "var(--color-text-primary)" }}
      >
        {value}
        {unit ? (
          <span
            className="type-data-label ml-0.5"
            style={{ color: "var(--color-text-secondary)" }}
          >
            {unit}
          </span>
        ) : null}
      </span>
    </span>
  );
}
