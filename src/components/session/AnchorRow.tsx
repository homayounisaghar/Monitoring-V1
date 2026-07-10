import { useEffect, useState } from "react";
import { copy } from "@/lib/copy-deck";

const ANCHORS = [
  { id: "attention", label: "Attention" },
  { id: "summary",   label: "Summary" },
  { id: "periods",   label: "Periods" },
  { id: "squad",     label: "Squad" },
] as const;

export function AnchorRow() {
  const [active, setActive] = useState<string>("attention");

  useEffect(() => {
    const els = ANCHORS
      .map((a) => document.getElementById(a.id))
      .filter((el): el is HTMLElement => Boolean(el));
    if (els.length === 0) return;

    const io = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (visible[0]?.target.id) setActive(visible[0].target.id);
      },
      { rootMargin: "-120px 0px -60% 0px", threshold: 0 }
    );

    els.forEach((el) => io.observe(el));
    return () => io.disconnect();
  }, []);

  return (
    <div
      className="border-b"
      style={{
        borderColor: "var(--color-border)",
        backgroundColor: "var(--color-canvas)",
      }}
    >
      <div className="mx-auto flex h-9 max-w-[1320px] items-center gap-5 px-6">
        {ANCHORS.map((a) => {
          const isActive = active === a.id;
          return (
            <a
              key={a.id}
              href={`#${a.id}`}
              onClick={(e) => {
                e.preventDefault();
                document.getElementById(a.id)?.scrollIntoView({ behavior: "smooth", block: "start" });
              }}
              className="relative flex h-9 items-center text-[12px] transition-colors"
              style={{
                color: isActive ? "var(--color-text-primary)" : "var(--color-text-tertiary)",
                fontWeight: isActive ? 500 : 400,
              }}
            >
              {a.label}
              {isActive && (
                <span
                  className="absolute inset-x-0 bottom-0 h-px"
                  style={{ backgroundColor: "var(--color-slate-700)" }}
                  aria-hidden
                />
              )}
            </a>
          );
        })}
      </div>
    </div>
  );
}
