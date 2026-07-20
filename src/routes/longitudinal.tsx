import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { SourceSidebar } from "@/components/shell/SourceSidebar";
import { DemoPill } from "@/components/shell/DemoPill";

import {
  windowFor,
  sessionDayIndex,
  type Horizon,
} from "@/lib/longitudinal-data";
import { WindowBanner, DEFAULT_HORIZON } from "@/components/longitudinal/WindowBanner";
import { AnchorStrip } from "@/components/longitudinal/AnchorStrip";
import {
  ScopeLine,
  DEFAULT_BENCH,
  DEFAULT_REF,
  type BenchKind,
  type RefKind,
} from "@/components/longitudinal/ScopeLine";
import { SummarySection } from "@/components/longitudinal/SummarySection";
import { DaysSection } from "@/components/longitudinal/DaysSection";
import { AthletesSection } from "@/components/longitudinal/AthletesSection";

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
  const [benchKind, setBenchKind] = useState<BenchKind>(DEFAULT_BENCH);
  const [refKind, setRefKind] = useState<RefKind>(DEFAULT_REF);

  const w = useMemo(() => windowFor(horizon), [horizon]);

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
          <div className="mx-auto max-w-[1320px] px-6 pt-4">
            <WindowBanner
              horizon={horizon}
              onHorizonChange={setHorizon}
              window={w}
            />
          </div>

          <div
            className="sticky top-12 z-30 border-b"
            style={{
              backgroundColor: "var(--color-canvas)",
              borderColor: "var(--color-border)",
            }}
          >
            <div className="mx-auto flex h-12 max-w-[1320px] items-center gap-4 px-6">
              <ScopeLine
                window={w}
                horizon={horizon}
                benchKind={benchKind}
                onBenchChange={setBenchKind}
                refKind={refKind}
                onRefChange={setRefKind}
              />
            </div>
          </div>

          <div className="sticky top-24 z-20">
            <AnchorStrip />
          </div>

          <main className="mx-auto max-w-[1320px] space-y-16 px-6 pt-10 pb-24">
            <SummarySection window={w} horizon={horizon} benchKind={benchKind} />
            <DaysSection window={w} horizon={horizon} benchKind={benchKind} />
            <AthletesSection window={w} horizon={horizon} refKind={refKind} />
          </main>
        </div>
      </div>
      <DemoPill />
    </>
  );
}
