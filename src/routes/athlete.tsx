import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { zodValidator, fallback } from "@tanstack/zod-adapter";
import { z } from "zod";

const timeframeSchema = fallback(z.string(), "session").default("session");
const athleteSearchSchema = z.object({
  athleteId: fallback(z.string(), "").default(""),
  sessionId: fallback(z.string(), "").default(""),
  timeframe: timeframeSchema,
});

export const Route = createFileRoute("/athlete")({
  validateSearch: zodValidator(athleteSearchSchema),
  head: () => ({
    meta: [
      { title: "Athlete · ST2" },
      { name: "description", content: "Per-athlete deep dive — built next." },
    ],
  }),
  component: AthleteRoute,
});

function AthleteRoute() {
  const { athleteId, sessionId, timeframe } = Route.useSearch();
  const navigate = useNavigate();
  const safeTimeframe: "session" | "window" =
    timeframe === "window" ? "window" : "session";

  return (
    <div className="mx-auto flex max-w-[1320px] items-center justify-center px-6 py-24">
      <div
        className="w-full max-w-md rounded-lg border p-8 text-center"
        style={{
          borderColor: "var(--color-border)",
          backgroundColor: "var(--color-surface-card)",
        }}
      >
        <div
          className="type-label"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          Athlete
        </div>
        <h1
          className="mt-2 text-[20px] font-semibold tracking-tight"
          style={{ color: "var(--color-text-primary)" }}
        >
          Athlete — built next
        </h1>
        <p
          className="mt-2 text-[13px]"
          style={{ color: "var(--color-text-secondary)" }}
        >
          This tab lands every athlete drill from Session and Longitudinal.
          Coming in a later prompt.
        </p>

        <dl
          className="mt-6 grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 text-left text-[12.5px]"
          style={{ color: "var(--color-text-secondary)" }}
        >
          <dt style={{ color: "var(--color-text-tertiary)" }}>athleteId</dt>
          <dd data-testid="athleteId" className="type-num">{athleteId || "—"}</dd>
          <dt style={{ color: "var(--color-text-tertiary)" }}>sessionId</dt>
          <dd data-testid="sessionId" className="type-num">{sessionId || "—"}</dd>
          <dt style={{ color: "var(--color-text-tertiary)" }}>timeframe</dt>
          <dd data-testid="timeframe" className="type-num">{safeTimeframe}</dd>
        </dl>

        <button
          onClick={() => navigate({ to: "/session" })}
          className="mt-6 inline-flex items-center rounded border px-3 py-1.5 text-[12.5px] transition-colors hover:bg-[color:var(--color-slate-100)]"
          style={{
            borderColor: "var(--color-border)",
            color: "var(--color-text-primary)",
          }}
        >
          Back to session
        </button>
      </div>
    </div>
  );
}
