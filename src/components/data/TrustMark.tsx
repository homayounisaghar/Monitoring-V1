/**
 * TrustMark — one costume at every size.
 * Leading trust dot + hatched veil on the qualified mark + coverage
 * printed on the value.
 */
export type TrustMarkProps = {
  size?: "sm" | "md" | "lg";
  value: string;
  unit?: string;
  coverage: number; // 0-100
};

export function TrustMark({ size = "md", value, unit, coverage }: TrustMarkProps) {
  const dot = { sm: "h-1.5 w-1.5", md: "h-2 w-2", lg: "h-2.5 w-2.5" }[size];
  const veilH = { sm: "h-3", md: "h-4", lg: "h-5" }[size];
  const veilW = { sm: "w-10", md: "w-14", lg: "w-20" }[size];
  const num = { sm: "text-xs", md: "text-sm", lg: "text-base" }[size];

  return (
    <div className="inline-flex items-center gap-2">
      <span
        className={`${dot} shrink-0 rounded-full`}
        style={{ backgroundColor: "var(--color-trust-dot)" }}
        aria-hidden
      />
      <div className="relative inline-flex items-baseline gap-1">
        <span
          className={`veil-hatch absolute inset-x-0 top-1/2 -translate-y-1/2 ${veilH} ${veilW} rounded-sm opacity-70`}
          aria-hidden
        />
        <span
          className={`type-num ${num} relative font-semibold`}
          style={{ color: "var(--color-text-primary)" }}
        >
          {value}
          {unit ? <span className="type-data-label ml-0.5">{unit}</span> : null}
        </span>
      </div>
      <span className="type-data-label type-num">— {coverage}% cov</span>
    </div>
  );
}
