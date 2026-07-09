import { useSessionScope, BENCHMARK_OPTIONS } from "@/lib/session-scope";
import { ScopeTag } from "@/components/session/ScopeTag";

type Kind = "attention" | "summary" | "periods" | "squad";

const META: Record<Kind, { title: string; desc: string }> = {
  attention: {
    title: "Attention",
    desc: "Who needs you now — escalations and notices, ranked by severity.",
  },
  summary: {
    title: "Summary",
    desc: "How the squad went today, on the shared work and cost axes.",
  },
  periods: {
    title: "Periods",
    desc: "How the session distributed load across halves or 15-minute blocks.",
  },
  squad: {
    title: "Squad",
    desc: "Every athlete on this session — sort, scan, drill.",
  },
};

export function SectionStub({ kind }: { kind: Kind }) {
  const { benchmark, scopeLabel, filterIsDefault } = useSessionScope();
  const meta = META[kind];
  const benchmarkChanged = benchmark.kind !== BENCHMARK_OPTIONS[0].kind;

  // The Summary stub echoes live Benchmark to prove wiring.
  const inlineScope =
    kind === "summary" && benchmarkChanged
      ? `vs ${benchmark.label}`
      : !filterIsDefault && scopeLabel
      ? scopeLabel
      : null;

  return (
    <section id={kind} className="scroll-mt-28">
      <header className="mb-3 flex items-baseline justify-between gap-4">
        <div className="flex items-baseline gap-3">
          <h2 className="type-section-h">{meta.title}</h2>
          {inlineScope && (
            <span
              className="type-label"
              style={{ color: "var(--color-text-tertiary)" }}
            >
              — {inlineScope}
            </span>
          )}
        </div>
        <ScopeTag />

      </header>
      <p className="type-section-desc mb-3">{meta.desc}</p>
      <div
        className="rounded-lg border p-8"
        style={{
          borderColor: "var(--color-border)",
          backgroundColor: "var(--color-surface-card)",
        }}
      >
        <div
          className="type-label"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          {meta.title} — built next
        </div>
      </div>
    </section>
  );
}
