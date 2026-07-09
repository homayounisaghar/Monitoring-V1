import { useState, useRef, useEffect } from "react";
import { ChevronDown, Info, X, HelpCircle } from "lucide-react";
import {
  useSessionScope,
  REFERENCE_OPTIONS,
  BENCHMARK_OPTIONS,
  type ReferenceKind,
  type BenchmarkKind,
} from "@/lib/session-scope";

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
            onSelect={(opt) => {
              setBenchmark(opt);
              close();
            }}
          />
        )}
      />

      {/* ⓘ on Benchmark only */}
      <InfoDot />

      {/* Right end — "How to read this" */}
      <div className="ml-auto">
        <HowToReadPopover />
      </div>
    </div>
  );
}

/* ------------ EditableChip ------------ */

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
    <span className="relative inline-flex items-center gap-1" ref={wrapRef}>
      <button
        onClick={() => setOpen((o) => !o)}
        className={
          "inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[13px] transition-colors " +
          (changed ? "chip-changed" : "")
        }
        style={
          changed
            ? undefined
            : {
                color: "var(--color-text-primary)",
                fontWeight: 500,
              }
        }
        onMouseEnter={(e) => {
          if (!changed) e.currentTarget.style.backgroundColor = "var(--color-slate-100)";
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
          className="inline-flex items-center gap-0.5 rounded px-1 py-0.5 text-[11.5px] transition-colors hover:bg-[color:var(--color-slate-200)]"
          style={{ color: "var(--color-text-tertiary)" }}
          title="Reset"
        >
          <span>reset</span>
          <X className="h-3 w-3" />
        </button>
      )}
      {open && (
        <div
          className="absolute left-0 top-full z-30 mt-1 w-64 overflow-hidden rounded-md border shadow-lg"
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
  onSelect,
}: {
  title: string;
  options: Array<{ kind: T; label: string }>;
  activeKind: T;
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
          return (
            <li key={opt.kind}>
              <button
                onClick={() => onSelect(opt)}
                className="flex w-full items-center justify-between rounded px-2 py-1.5 text-left text-[12.5px] transition-colors hover:bg-[color:var(--color-slate-100)]"
                style={{
                  color: active ? "var(--color-text-primary)" : "var(--color-text-secondary)",
                  fontWeight: active ? 500 : 400,
                }}
              >
                <span>{opt.label}</span>
                <span className="flex items-center gap-2">
                  {isDefault && (
                    <span className="type-label" style={{ color: "var(--color-text-tertiary)" }}>
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
              </button>
            </li>
          );
        })}
      </ul>
    </>
  );
}

/* ------------ ⓘ on Benchmark ------------ */

function InfoDot() {
  const [open, setOpen] = useState(false);
  const [pinned, setPinned] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const hoverTimer = useRef<number | null>(null);

  useEffect(() => {
    if (!open) return;
    const onDoc = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
        setPinned(false);
      }
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, [open]);

  const onEnter = () => {
    if (pinned) return;
    if (hoverTimer.current) window.clearTimeout(hoverTimer.current);
    hoverTimer.current = window.setTimeout(() => setOpen(true), 180);
  };
  const onLeave = () => {
    if (pinned) return;
    if (hoverTimer.current) window.clearTimeout(hoverTimer.current);
    setOpen(false);
  };

  return (
    <span ref={ref} className="relative inline-flex" onMouseEnter={onEnter} onMouseLeave={onLeave}>
      <button
        aria-label="About benchmark"
        onClick={() => {
          setOpen(true);
          setPinned(true);
        }}
        className="grid h-4 w-4 place-items-center rounded-full transition-colors hover:bg-[color:var(--color-slate-100)]"
        style={{ color: "var(--color-text-tertiary)" }}
      >
        <Info className="h-3 w-3" />
      </button>
      {open && (
        <div
          className="absolute left-0 top-full z-30 mt-1 w-80 rounded-md border p-3 text-[12px] leading-relaxed shadow-lg"
          style={{
            backgroundColor: "var(--color-surface-card)",
            borderColor: "var(--color-border)",
            color: "var(--color-text-secondary)",
          }}
        >
          The default compares the squad to a typical match of this type, drawn from your
          own match history. Change it to compare against a specific set of matches instead.
        </div>
      )}
    </span>
  );
}

/* ------------ How to read this ------------ */

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
          className="absolute right-0 top-full z-30 mt-1 w-[380px] rounded-md border p-4 text-[12px] leading-relaxed shadow-xl"
          style={{
            backgroundColor: "var(--color-surface-card)",
            borderColor: "var(--color-border)",
            color: "var(--color-text-secondary)",
          }}
        >
          <dl className="space-y-3">
            <Row term="the track">
              a <b style={{ color: "var(--color-text-primary)" }}>band</b> (the athlete's
              normal range for this day-type) with a <b style={{ color: "var(--color-text-primary)" }}>tick</b> (the reference)
              and a <b style={{ color: "var(--color-text-primary)" }}>dot</b> (this session).
              Past the tick is above typical, past the band is beyond his normal variation.
              The signed % is the delta vs the reference.
            </Row>
            <Row term="the two hues">
              <span style={{ color: "var(--color-axis-work)", fontWeight: 500 }}>blue</span> = external work,{" "}
              <span style={{ color: "var(--color-axis-cost)", fontWeight: 500 }}>purple</span> = internal cost.
              Hue marks <em>which axis</em>, never how high.
            </Row>
            <Row term="severity tiers">
              <span style={{ color: "var(--color-escalate-ink)" }}>▲ red</span> = escalate,{" "}
              <span style={{ color: "var(--color-notice-ink)" }}>◆ amber</span> = notice.
              These live only in the Attention card.
            </Row>
            <Row term="trust mark">
              a dot + hatch means thin data; coverage is printed on the number.
            </Row>
            <Row term="flag glyph">
              marks a flagged athlete's name in depth sections and links back to the Attention card.
            </Row>
          </dl>
        </div>
      )}
    </span>
  );
}

function Row({ term, children }: { term: string; children: React.ReactNode }) {
  return (
    <div className="grid grid-cols-[90px_1fr] gap-3">
      <dt className="type-label" style={{ color: "var(--color-text-tertiary)" }}>{term}</dt>
      <dd>{children}</dd>
    </div>
  );
}
