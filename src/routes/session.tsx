import { createFileRoute } from "@tanstack/react-router";
import { SessionScopeProvider } from "@/lib/session-scope";
import { SourceSidebar } from "@/components/shell/SourceSidebar";
import { DemoPill } from "@/components/shell/DemoPill";
import { EventBanner } from "@/components/session/EventBanner";
import { AnchorRow } from "@/components/session/AnchorRow";
import { ReadingLine } from "@/components/session/ReadingLine";
import { FilterCluster } from "@/components/session/FilterPanel";
import { AttentionCard } from "@/components/session/AttentionCard";
import { SummaryCard } from "@/components/session/SummaryCard";
import { PeriodsCard } from "@/components/session/PeriodsCard";
import { SquadCard } from "@/components/session/SquadCard";

export const Route = createFileRoute("/session")({
  head: () => ({
    meta: [
      { title: "Session · ST2" },
      {
        name: "description",
        content: "Post-session monitoring for the last squad session.",
      },
    ],
  }),
  component: SessionRoute,
});

function SessionRoute() {
  return (
    <SessionScopeProvider>
      <div className="flex min-h-[calc(100vh-3rem)]">
        <SourceSidebar />
        <div className="min-w-0 flex-1">
          {/* Banner — content, grid-width, aligned to the same grid as below */}
          <div className="mx-auto max-w-[1320px] px-6 pt-4">
            <EventBanner />
          </div>

          {/* Sticky shell row: reading-line + filter */}
          <div
            className="sticky top-12 z-30 border-b"
            style={{
              backgroundColor: "var(--color-canvas)",
              borderColor: "var(--color-border)",
            }}
          >
            <div className="mx-auto flex h-12 max-w-[1320px] items-center gap-4 px-6">
              <div className="min-w-0 flex-1">
                <ReadingLine />
              </div>
              <FilterCluster />
            </div>
          </div>

          {/* Content column */}
          <main className="mx-auto max-w-[1320px] px-6 pt-8">
            <AttentionCard />

            {/* Seam — form only: tone step down + hairline crossing the column */}
            <div
              className="mt-10"
              style={{ backgroundColor: "var(--color-canvas-sunken, var(--color-slate-100))" }}
            >
              <div
                aria-hidden
                className="h-px w-full"
                style={{ backgroundColor: "var(--color-border)" }}
              />
              <div className="space-y-10 py-10">
                <SummaryCard />
                <PeriodsCard />
                <SquadCard />
              </div>
            </div>
          </main>
        </div>
      </div>



      <DemoPill />
    </SessionScopeProvider>
  );
}
