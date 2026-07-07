import { useState } from "react";
import { FlaskConical, ChevronDown } from "lucide-react";
import { useSessionScope, type DemoScenario } from "@/lib/session-scope";

const SCENARIOS: Array<{ id: DemoScenario; label: string }> = [
  { id: "default",        label: "Default" },
  { id: "all_clear",      label: "All-clear" },
  { id: "srpe_none",      label: "sRPE not collected" },
  { id: "srpe_full",      label: "sRPE full (18 of 18)" },
  { id: "coverage_thin",  label: "Coverage thin" },
];

export function DemoPill() {
  const { demo, setDemo } = useSessionScope();
  const [open, setOpen] = useState(false);
  const active = SCENARIOS.find((s) => s.id === demo) ?? SCENARIOS[0];

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {open && (
        <div
          className="mb-2 w-56 overflow-hidden rounded-md border shadow-lg"
          style={{
            backgroundColor: "var(--color-surface-card)",
            borderColor: "var(--color-border)",
          }}
        >
          <div
            className="type-card-eyebrow border-b px-3 py-2"
            style={{
              borderColor: "var(--color-border)",
              color: "var(--color-text-tertiary)",
            }}
          >
            Demo scenario
          </div>
          <ul className="p-1">
            {SCENARIOS.map((s) => {
              const isActive = s.id === demo;
              return (
                <li key={s.id}>
                  <button
                    onClick={() => {
                      setDemo(s.id);
                      setOpen(false);
                    }}
                    className="flex w-full items-center justify-between rounded px-2 py-1.5 text-left text-[12.5px] transition-colors hover:bg-[color:var(--color-slate-100)]"
                    style={{
                      color: isActive ? "var(--color-text-primary)" : "var(--color-text-secondary)",
                      fontWeight: isActive ? 500 : 400,
                    }}
                  >
                    <span>{s.label}</span>
                    {isActive && (
                      <span
                        className="h-1.5 w-1.5 rounded-full"
                        style={{ backgroundColor: "var(--color-brand)" }}
                        aria-hidden
                      />
                    )}
                  </button>
                </li>
              );
            })}
          </ul>
        </div>
      )}

      <button
        onClick={() => setOpen((o) => !o)}
        className="flex h-8 items-center gap-1.5 rounded-full border pl-2.5 pr-2 shadow-sm transition-colors"
        style={{
          backgroundColor: "var(--color-slate-900)",
          borderColor: "var(--color-slate-800)",
          color: "var(--color-text-on-brand)",
        }}
      >
        <FlaskConical className="h-3 w-3" />
        <span className="type-card-eyebrow" style={{ color: "var(--color-slate-300)" }}>
          Demo
        </span>
        <span className="text-[12px] font-medium">{active.label}</span>
        <ChevronDown className="h-3 w-3 opacity-70" />
      </button>
    </div>
  );
}
