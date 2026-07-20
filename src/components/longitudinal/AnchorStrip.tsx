import { useEffect, useState } from "react";
import { copy } from "@/lib/copy-deck";

const ANCHORS = [
  { id: "summary", label: copy("longi.anchor.summary") },
  { id: "days", label: copy("longi.anchor.days") },
  { id: "athletes", label: copy("longi.anchor.athletes") },
] as const;

export function AnchorStrip() {
  const [active, setActive] = useState<string>("summary");

  useEffect(() => {
    const ids: string[] = ANCHORS.map((a) => a.id);
    let raf = 0;
    const compute = () => {
      raf = 0;
      const anchorLine = 140;
      const els = ids
        .map((id) => ({ id, el: document.getElementById(id) }))
        .filter((x): x is { id: string; el: HTMLElement } => Boolean(x.el));
      if (els.length === 0) return;
      const nearBottom =
        window.innerHeight + window.scrollY >=
        document.documentElement.scrollHeight - 2;
      if (nearBottom) {
        setActive(els[els.length - 1].id);
        return;
      }
      let current = els[0].id;
      for (const { id, el } of els) {
        if (el.getBoundingClientRect().top <= anchorLine) current = id;
        else break;
      }
      setActive(current);
    };
    const onScroll = () => {
      if (raf) return;
      raf = requestAnimationFrame(compute);
    };
    compute();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
      if (raf) cancelAnimationFrame(raf);
    };
  }, []);

  return (
    <div
      className="border-b"
      style={{
        borderColor: "var(--color-border)",
        backgroundColor: "var(--color-canvas)",
      }}
    >
      <nav
        aria-label="Longitudinal sections"
        className="mx-auto flex h-9 max-w-[1320px] items-center gap-5 px-6"
      >
        {ANCHORS.map((a) => {
          const isActive = active === a.id;
          return (
            <a
              key={a.id}
              href={`#${a.id}`}
              aria-current={isActive ? "true" : undefined}
              onClick={(e) => {
                e.preventDefault();
                const el = document.getElementById(a.id);
                if (!el) return;
                const prefersReduced = window.matchMedia(
                  "(prefers-reduced-motion: reduce)",
                ).matches;
                el.scrollIntoView({
                  behavior: prefersReduced ? "auto" : "smooth",
                  block: "start",
                });
              }}
              className="relative flex h-9 items-center text-[12px] transition-colors focus-visible:outline-none"
              style={{
                color: isActive
                  ? "var(--color-text-primary)"
                  : "var(--color-text-tertiary)",
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
      </nav>
    </div>
  );
}
