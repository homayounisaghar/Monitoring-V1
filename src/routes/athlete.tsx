import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { zodValidator, fallback } from "@tanstack/zod-adapter";
import { z } from "zod";
import { useEffect, useState } from "react";
import { SourceSidebar } from "@/components/shell/SourceSidebar";
import { DemoPill } from "@/components/shell/DemoPill";
import { SegmentedToggle } from "@/components/data/SegmentedToggle";
import { AthleteBanner } from "@/components/athlete/AthleteBanner";
import { AthleteScopeLine } from "@/components/athlete/AthleteScopeLine";
import { copy } from "@/lib/copy-deck";

const timeframeSchema = fallback(z.string(), "session").default("session");
const athleteSearchSchema = z.object({
  athleteId: fallback(z.string(), "").default(""),
  sessionId: fallback(z.string(), "").default(""),
  timeframe: timeframeSchema,
});

const DEFAULT_ATHLETE = "werner";
const DEFAULT_SESSION = "s-2026-07-04-dortmund";

export const Route = createFileRoute("/athlete")({
  validateSearch: zodValidator(athleteSearchSchema),
  head: () => ({
    meta: [
      { title: "Athlete · ST2" },
      { name: "description", content: "Per-athlete session read." },
    ],
  }),
  component: AthleteRoute,
});

type TF = "session" | "window";

function AthleteRoute() {
  const search = Route.useSearch();
  const navigate = useNavigate();

  const athleteId = search.athleteId || DEFAULT_ATHLETE;
  const sessionId = search.sessionId || DEFAULT_SESSION;
  const timeframe: TF = search.timeframe === "window" ? "window" : "session";

  const setSearch = (patch: Partial<{ athleteId: string; sessionId: string; timeframe: string }>) => {
    navigate({
      to: "/athlete",
      search: (prev) => ({ ...prev, ...patch }),
    });
  };

  return (
    <>
      <div className="flex min-h-[calc(100vh-3rem)]">
        <SourceSidebar />
        <div className="min-w-0 flex-1">
          {/* Banner — content-column width */}
          <div className="mx-auto max-w-[1320px] px-6 pt-4">
            <AthleteBanner
              athleteId={athleteId}
              onAthleteChange={(id) => setSearch({ athleteId: id })}
            />
          </div>

          {/* Sticky shell row: toggle + scope line */}
          <div
            className="sticky top-12 z-30 border-b"
            style={{
              backgroundColor: "var(--color-canvas)",
              borderColor: "var(--color-border)",
            }}
          >
            <div className="mx-auto flex h-12 max-w-[1320px] items-center gap-4 px-6">
              <SegmentedToggle<TF>
                value={timeframe}
                onChange={(t) => setSearch({ timeframe: t })}
                options={[
                  { id: "session", label: copy("athlete.tf.session") },
                  { id: "window", label: copy("athlete.tf.over") },
                ]}
              />
              {timeframe === "session" && (
                <AthleteScopeLine
                  athleteId={athleteId}
                  sessionId={sessionId}
                  onSessionChange={(id) => setSearch({ sessionId: id })}
                />
              )}
            </div>
          </div>

          {timeframe === "session" ? (
            <>
              <div className="sticky top-24 z-20">
                <AthleteAnchorStrip />
              </div>
              <main className="mx-auto max-w-[1320px] px-6 pt-8">
                <SectionAnchor id="summary" label={copy("athlete.anchor.summary")} />
                <SectionAnchor id="periods" label={copy("athlete.anchor.periods")} />
                <SectionAnchor id="spatial" label={copy("athlete.anchor.spatial")} />
                <SectionAnchor id="detail" label={copy("athlete.anchor.detail")} />
              </main>
            </>
          ) : (
            <main className="mx-auto max-w-[1320px] px-6 pt-8">
              <p
                className="text-[13px]"
                style={{ color: "var(--color-text-secondary)" }}
              >
                {copy("athlete.overtime.empty")}
              </p>
            </main>
          )}
        </div>
      </div>
      <DemoPill />
    </>
  );
}

/* ─────────────────── section anchor placeholder ─────────────────── */

function SectionAnchor({ id, label }: { id: string; label: string }) {
  return (
    <section id={id} className="scroll-mt-28 py-10">
      <h2
        className="type-section-h"
        style={{ color: "var(--color-text-primary)" }}
      >
        {label}
      </h2>
    </section>
  );
}

/* ─────────────────── local anchor strip (slate underline) ─────────────────── */

const ANCHORS = [
  { id: "summary", key: "athlete.anchor.summary" as const },
  { id: "periods", key: "athlete.anchor.periods" as const },
  { id: "spatial", key: "athlete.anchor.spatial" as const },
  { id: "detail",  key: "athlete.anchor.detail"  as const },
];

function AthleteAnchorStrip() {
  const [active, setActive] = useState<string>("summary");

  useEffect(() => {
    const ids = ANCHORS.map((a) => a.id);
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
        aria-label="Athlete sections"
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
              {copy(a.key)}
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
