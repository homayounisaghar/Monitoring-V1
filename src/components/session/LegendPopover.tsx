/**
 * Session — "How to read this" trigger + anchors.
 *
 * The legend itself is the shared vocabulary key
 * (`@/components/data/HowToReadLegend`), rendered identically here, on the
 * Athlete page and on Longitudinal. This file owns only the triggers and
 * the open/close wiring.
 */

import { useEffect, useRef } from "react";
import { HelpCircle } from "lucide-react";
import { copy } from "@/lib/copy-deck";
import { useSessionScope } from "@/lib/session-scope";
import { HowToReadLegendPanel } from "@/components/data/HowToReadLegend";

/** Chrome trigger — icon + "How to read this" label, used by ReadingLine. */
export function HowToReadPopover() {
  const { legendOpen, setLegendOpen, legendSource, setLegendSource } = useSessionScope();
  const ref = useRef<HTMLSpanElement>(null);
  const isMine = legendOpen && legendSource === "chrome";

  useEffect(() => {
    if (!isMine) return;
    const onDoc = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setLegendOpen(false);
        setLegendSource(null);
      }
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, [isMine, setLegendOpen, setLegendSource]);

  return (
    <span ref={ref} className="relative inline-flex">
      <button
        onClick={() => {
          const next = !isMine;
          setLegendOpen(next);
          setLegendSource(next ? "chrome" : null);
        }}
        aria-haspopup="dialog"
        aria-expanded={isMine}
        className="inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[12px] transition-colors hover:bg-[color:var(--color-slate-100)]"
        style={{ color: "var(--color-text-tertiary)" }}
      >
        <HelpCircle className="h-3 w-3" />
        <span>{copy("control.legend")}</span>
      </button>
      {isMine && <HowToReadLegendPanel align="right" />}
    </span>
  );
}

/**
 * Anchor for the Attention card's ⓘ. Renders no trigger of its own —
 * it's an invisible positioning anchor next to the ⓘ button so the panel
 * opens in place.
 */
export function LegendAnchor({ align = "right" }: { align?: "left" | "right" }) {
  const { legendOpen, setLegendOpen, legendSource, setLegendSource } = useSessionScope();
  const ref = useRef<HTMLSpanElement>(null);
  const isMine = legendOpen && legendSource === "attention";

  useEffect(() => {
    if (!isMine) return;
    const onDoc = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setLegendOpen(false);
        setLegendSource(null);
      }
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, [isMine, setLegendOpen, setLegendSource]);

  if (!isMine) return null;
  return (
    <span ref={ref} className="relative inline-flex">
      <HowToReadLegendPanel align={align} />
    </span>
  );
}

/** Hook helper so a card's toggle sets the source. */
export function useLegendToggle(source: "chrome" | "attention") {
  const { legendOpen, legendSource, setLegendOpen, setLegendSource } = useSessionScope();
  const isMine = legendOpen && legendSource === source;
  return () => {
    const next = !isMine;
    setLegendOpen(next);
    setLegendSource(next ? source : null);
  };
}
