import { useState, useRef, useEffect } from "react";
import { ChevronDown, X, HelpCircle } from "lucide-react";
import {
  useSessionScope,
  REFERENCE_OPTIONS,
  BENCHMARK_OPTIONS,
  type ReferenceKind,
  type BenchmarkKind,
} from "@/lib/session-scope";
import { copy } from "@/lib/copy-deck";

export function ReadingLine() {
  const {
    reference, setReference, benchmark, setBenchmark,
  } = useSessionScope();

  const referenceIsDefault = reference.kind === REFERENCE_OPTIONS[0].kind;
  const benchmarkIsDefault = benchmark.kind === BENCHMARK_OPTIONS[0].kind;

  return (
    <div className="flex min-w-0 items-center gap-1.5 text-[13px]" style={{ color: "var(--color-text-secondary)" }}>
      <span>each athlete vs</span>

      <EditableChip
        value={reference.label}
        changed={!referenceIsDefault}
        onReset={() => setReference(REFERENCE_OPTIONS[0])}
        renderPopover={(close) => (
          <ChipOptions
            title="Reference · per athlete"
            options={REFERENCE_OPTIONS}
            activeKind={reference.kind}
            glossKey={(kind) => `readingLine.gloss.${kind}`}
            onSelect={(opt) => {
              setReference(opt);
              close();
            }}
          />
        )}
      />

      <span>·</span>
      <span>squad vs</span>

      <EditableChip
        value={benchmark.label}
        changed={!benchmarkIsDefault}
        onReset={() => setBenchmark(BENCHMARK_OPTIONS[0])}
        renderPopover={(close) => (
          <ChipOptions
            title="Benchmark · squad"
            options={BENCHMARK_OPTIONS}
            activeKind={benchmark.kind}
            glossKey={(kind) => `readingLine.bgloss.${kind}`}
            onSelect={(opt) => {
              setBenchmark(opt);
              close();
            }}
          />
        )}
      />

      {/* Right end — the key */}
      <div className="ml-auto">
        <HowToReadPopover />
      </div>
    </div>
  );
}

/* ------------ EditableChip ------------ */
/* One anatomy in both states: always a chip.
   Changed = filled slate chip with an inline × (no detached reset link). */

function EditableChip({
  value,
  changed,
  onReset,
  renderPopover,
}: {
  value: string;
  changed: boolean;
  onReset: () => void;
  renderPopover: (close: () => void) => React.ReactNode;
}) {
  const [open, setOpen] = useState(false);
  const wrapRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onDoc = (e: MouseEvent) => {
      if (wrapRef.current && !wrapRef.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, [open]);

  return (
    <span className="relative inline-flex items-center" ref={wrapRef}>
      <span
        className={
          "inline-flex items-center rounded transition-colors " +
          (changed ? "chip-changed" : "")
        }
        style={
          changed
            ? undefined
            : { color: "var(--color-text-primary)", fontWeight: 500 }
        }
      >
        <button
          onClick={() => setOpen((o) => !o)}
          className="inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[13px] transition-colors"
          onMouseEnter={(e) => {
            if (!changed)
              e.currentTarget.style.backgroundColor = "var(--color-slate-100)";
          }}
          onMouseLeave={(e) => {
            if (!changed) e.currentTarget.style.backgroundColor = "transparent";
          }}
        >
          <span>{value}</span>
          <ChevronDown className="h-3 w-3 opacity-60" />
        </button>
        {changed && (
          <button
            onClick={onReset}
            aria-label="Reset to default"
            title="Reset"
            className="ml-0.5 mr-1 grid h-4 w-4 place-items-center rounded transition-colors hover:bg-[color:var(--color-slate-200)]"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            <X className="h-3 w-3" />
          </button>
        )}
      </span>
      {open && (
        <div
          className="absolute left-0 top-full z-30 mt-1 w-72 overflow-hidden rounded-md border shadow-lg"
          style={{
            backgroundColor: "var(--color-surface-card)",
            borderColor: "var(--color-border)",
          }}
        >
          {renderPopover(() => setOpen(false))}
        </div>
      )}
    </span>
  );
}

function ChipOptions<T extends ReferenceKind | BenchmarkKind>({
  title,
  options,
  activeKind,
  glossKey,
  onSelect,
}: {
  title: string;
  options: Array<{ kind: T; label: string }>;
  activeKind: T;
  glossKey: (kind: T) => string;
  onSelect: (opt: { kind: T; label: string }) => void;
}) {
  return (
    <>
      <div
        className="type-label border-b px-3 py-2"
        style={{
          borderColor: "var(--color-border)",
          color: "var(--color-text-tertiary)",
        }}
      >
        {title}
      </div>
      <ul className="p-1">
        {options.map((opt) => {
          const active = opt.kind === activeKind;
          const isDefault = opt.kind === options[0].kind;
          const gloss = copy(glossKey(opt.kind));
          return (
            <li key={opt.kind}>
              <button
                onClick={() => onSelect(opt)}
                className="block w-full rounded px-2 py-1.5 text-left transition-colors hover:bg-[color:var(--color-slate-100)]"
              >
                <span className="flex items-center justify-between">
                  <span
                    className="text-[12.5px]"
                    style={{
                      color: active
                        ? "var(--color-text-primary)"
                        : "var(--color-text-secondary)",
                      fontWeight: active ? 500 : 400,
                    }}
                  >
                    {opt.label}
                  </span>
                  <span className="flex items-center gap-2">
                    {isDefault && (
                      <span
                        className="type-label"
                        style={{ color: "var(--color-text-tertiary)" }}
                      >
                        default
                      </span>
                    )}
                    {active && (
                      <span
                        className="h-1.5 w-1.5 rounded-full"
                        style={{ backgroundColor: "var(--color-slate-700)" }}
                        aria-hidden
                      />
                    )}
                  </span>
                </span>
                {gloss && (
                  <span
                    className="mt-0.5 block text-[11.5px]"
                    style={{ color: "var(--color-text-tertiary)" }}
                  >
                    {gloss}
                  </span>
                )}
              </button>
            </li>
          );
        })}
      </ul>
    </>
  );
}

/* ------------ The key (five lines from copy-deck) ------------ */

function HowToReadPopover() {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onDoc = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, [open]);

  const KEY: Array<{ term: string; gloss: string }> = [
    { term: "band",       gloss: copy("legend.band") },
    { term: "tick",       gloss: copy("legend.tick") },
    { term: "dot",        gloss: copy("legend.dot") },
    { term: "trust dot",  gloss: copy("legend.trustDot") },
    { term: "flag glyph", gloss: copy("legend.flagGlyph") },
  ];

  return (
    <span ref={ref} className="relative inline-flex">
      <button
        onClick={() => setOpen((o) => !o)}
        className="inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[12px] transition-colors hover:bg-[color:var(--color-slate-100)]"
        style={{ color: "var(--color-text-tertiary)" }}
      >
        <HelpCircle className="h-3 w-3" />
        <span>How to read this</span>
      </button>
      {open && (
        <div
          className="absolute right-0 top-full z-30 mt-1 w-[320px] rounded-md border p-3 shadow-xl"
          style={{
            backgroundColor: "var(--color-surface-card)",
            borderColor: "var(--color-border)",
            color: "var(--color-text-secondary)",
          }}
        >
          <dl className="space-y-1.5">
            {KEY.map(({ term, gloss }) => (
              <div key={term} className="grid grid-cols-[74px_1fr] gap-3 text-[12px] leading-snug">
                <dt
                  className="type-label"
                  style={{ color: "var(--color-text-tertiary)" }}
                >
                  {term}
                </dt>
                <dd style={{ color: "var(--color-text-secondary)" }}>{gloss}</dd>
              </div>
            ))}
          </dl>
        </div>
      )}
    </span>
  );
}
