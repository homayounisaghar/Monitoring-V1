import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { SourceSidebar } from "@/components/shell/SourceSidebar";
import { DemoPill } from "@/components/shell/DemoPill";
import { copy } from "@/lib/copy-deck";
import {
  windowFor,
  sessionDayIndex,
  type Horizon,
} from "@/lib/longitudinal-data";
import { WindowBanner, DEFAULT_HORIZON } from "@/components/longitudinal/WindowBanner";
import { AnchorStrip } from "@/components/longitudinal/AnchorStrip";
import { ScopeLine } from "@/components/longitudinal/ScopeLine";
import { SummarySection } from "@/components/longitudinal/SummarySection";
import { DaysSection } from "@/components/longitudinal/DaysSection";

export const Route = createFileRoute("/longitudinal")({
  head: () => ({
    meta: [
      { title: "Longitudinal · ST2" },
      {
        name: "description",
        content: "Multi-session trends — how the squad's load has been distributed over recent windows.",
      },
    ],
  }),
  component: LongitudinalRoute,
});

function LongitudinalRoute() {
  const [horizon, setHorizon] = useState<Horizon>(DEFAULT_HORIZON);
  const [focusId, setFocusId] = useState<string | undefined>(undefined);

  const w = useMemo(() => windowFor(horizon), [horizon]);

  // Focus derivation is wired but nothing is rendered from it yet.
  const _focusDayIndex = useMemo(
    () => (focusId ? sessionDayIndex(focusId, w) : null),
    [focusId, w],
  );
  void _focusDayIndex;

  return (
    <>
      <div className="flex min-h-[calc(100vh-3rem)]">
        <SourceSidebar
          scope={{ startISO: w.startISO, endISO: w.endISO, horizonDays: w.days }}
          focusSessionId={focusId}
          onFocusSession={setFocusId}
          showOutOfWindow
        />
        <div className="min-w-0 flex-1">
          {/* Banner — content, grid-width, aligned to the same grid as below */}
          <div className="mx-auto max-w-[1320px] px-6 pt-4">
            <WindowBanner
              horizon={horizon}
              onHorizonChange={setHorizon}
              window={w}
            />
          </div>

          {/* Sticky shell row: scope line + filter */}
          <div
            className="sticky top-12 z-30 border-b"
            style={{
              backgroundColor: "var(--color-canvas)",
              borderColor: "var(--color-border)",
            }}
          >
            <div className="mx-auto flex h-12 max-w-[1320px] items-center gap-4 px-6">
              <ScopeLine window={w} />
            </div>
          </div>

          {/* Sticky section anchor-nav */}
          <div className="sticky top-24 z-20">
            <AnchorStrip />
          </div>

          <main className="mx-auto max-w-[1320px] space-y-16 px-6 pt-10 pb-24">
            <SummarySection window={w} horizon={horizon} />
            <DaysSection window={w} />
            <SectionHeading id="athletes" label={copy("longi.anchor.athletes")} />
          </main>
        </div>
      </div>
      <DemoPill />
    </>
  );
}

function SectionHeading({ id, label }: { id: string; label: string }) {
  return (
    <section id={id} className="scroll-mt-28">
      <h2
        className="type-section-h"
        style={{ color: "var(--color-text-primary)" }}
      >
        {label}
      </h2>
    </section>
  );
}
