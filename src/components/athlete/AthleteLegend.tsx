/**
 * Athlete page · legend trigger.
 *
 * The legend itself is the shared vocabulary key
 * (`@/components/data/HowToReadLegend`), rendered identically on Session,
 * Athlete and Longitudinal. This file owns only the trigger + panel shell.
 */

import { useEffect, useRef, useState } from "react";
import { copy } from "@/lib/copy-deck";
import { HowToReadLegendPanel } from "@/components/data/HowToReadLegend";

export function AthleteLegend(_props: { spine?: unknown; peerActive?: boolean }) {
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
    <div className="relative" ref={wrapRef}>
      <button
        onClick={() => setOpen((o) => !o)}
        aria-haspopup="dialog"
        aria-expanded={open}
        className="text-[12px] transition-colors hover:underline"
        style={{ color: "var(--color-text-secondary)" }}
      >
        {copy("control.legend")}
      </button>
      {open && <HowToReadLegendPanel align="right" />}
    </div>
  );
}
