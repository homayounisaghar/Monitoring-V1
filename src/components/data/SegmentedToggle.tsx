/**
 * SegmentedToggle — the single house style for in-flow segmented controls.
 *
 * Modeled on the Summary-card implementation: sel-active / sel-idle class
 * pair (see src/styles.css) — no inline dark fills. Dark fills are barred
 * for in-flow controls; only overlay-chrome primaries (e.g. popover Done
 * buttons) use --color-slate-900.
 */
export function SegmentedToggle<T extends string>({
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
