import { ChevronDown, SlidersHorizontal } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { copy } from "@/lib/copy-deck";
import { sessionCategories, type LongiWindow } from "@/lib/longitudinal-data";

export function ScopeLine({ window: w }: { window: LongiWindow }) {
  return (
    <div className="flex min-w-0 flex-1 items-center gap-3">
      <Chip label={copy("longi.scope.benchmarkChip")} />
      <span aria-hidden style={{ color: "var(--color-text-tertiary)" }}>
        ·
      </span>
      <Chip label={copy("longi.scope.referenceChip")} />
      <div className="ml-auto flex items-center gap-3">
        <button
          className="text-[12px] transition-colors hover:underline"
          style={{ color: "var(--color-text-secondary)" }}
        >
          {copy("control.legend")}
        </button>
        <WindowFilter window={w} />
      </div>
    </div>
  );
}

function Chip({ label }: { label: string }) {
  return (
    <button
      className="inline-flex h-8 items-center gap-1 rounded-md border px-2.5 text-[12.5px] transition-colors hover:bg-[color:var(--color-slate-100)]"
      style={{
        borderColor: "var(--color-border)",
        backgroundColor: "var(--color-surface-card)",
        color: "var(--color-text-secondary)",
      }}
    >
      <span>{label}</span>
      <ChevronDown className="h-3.5 w-3.5 opacity-70" aria-hidden />
    </button>
  );
}

function WindowFilter({ window: w }: { window: LongiWindow }) {
  const [open, setOpen] = useState(false);
  const wrapRef = useRef<HTMLDivElement>(null);
  const [sessionType, setSessionType] = useState<string>("All");

  useEffect(() => {
    if (!open) return;
    const onDoc = (e: MouseEvent) => {
      if (wrapRef.current && !wrapRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, [open]);

  const categories = sessionCategories(w);

  return (
    <div className="relative" ref={wrapRef}>
      <button
        onClick={() => setOpen((o) => !o)}
        className="inline-flex h-8 items-center gap-1.5 rounded-md border px-2.5 text-[12.5px] transition-colors"
        style={{
          borderColor: "var(--color-border)",
          backgroundColor: "var(--color-surface-card)",
          color: "var(--color-text-secondary)",
        }}
      >
        <SlidersHorizontal className="h-3.5 w-3.5" />
        <span>{copy("canonical.filter.button")}</span>
      </button>
      {open && (
        <div
          className="absolute right-0 top-full z-40 mt-2 w-[320px] overflow-hidden rounded-md border shadow-xl"
          style={{
            backgroundColor: "var(--color-surface-card)",
            borderColor: "var(--color-border)",
          }}
        >
          <div className="p-4">
            {/* Only the Session-type category is built in this step; it is
                placed last in the fixed category order. */}
            <div
              className="type-label mb-1.5"
              style={{ color: "var(--color-text-tertiary)" }}
            >
              {copy("longi.filter.group.sessionType")}
            </div>
            <div className="flex flex-wrap gap-1">
              {categories.map((c) => {
                const label =
                  c === "All"
                    ? copy("canonical.filter.all")
                    : c === "Matches"
                    ? copy("longi.filter.opt.matches")
                    : c === "Training"
                    ? copy("longi.filter.opt.training")
                    : c;
                const active = sessionType === c;
                return (
                  <button
                    key={c}
                    onClick={() => setSessionType(c)}
                    className={
                      "h-6 rounded-md border px-2 text-[11.5px] transition-colors " +
                      (active ? "sel-active" : "sel-idle")
                    }
                    style={{
                      borderColor: active ? "transparent" : "var(--color-border)",
                    }}
                  >
                    {label}
                  </button>
                );
              })}
            </div>
          </div>
          <div
            className="flex items-center justify-end border-t px-4 py-2.5"
            style={{
              borderColor: "var(--color-border)",
              backgroundColor: "var(--color-slate-50)",
            }}
          >
            <button
              onClick={() => setOpen(false)}
              className="rounded px-3 py-1 text-[12px] font-medium sel-active"
            >
              {copy("canonical.filter.done")}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
