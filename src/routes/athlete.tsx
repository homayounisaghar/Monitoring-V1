import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/athlete")({
  head: () => ({
    meta: [
      { title: "Athlete · ST2" },
      { name: "description", content: "Per-athlete deep dive — built next." },
    ],
  }),
  component: AthleteRoute,
});

function AthleteRoute() {
  return <Placeholder title="Athlete" />;
}

function Placeholder({ title }: { title: string }) {
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
          className="type-card-eyebrow"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          {title}
        </div>
        <h1
          className="mt-2 text-[20px] font-semibold tracking-tight"
          style={{ color: "var(--color-text-primary)" }}
        >
          {title} — built next
        </h1>
        <p
          className="mt-2 text-[13px]"
          style={{ color: "var(--color-text-secondary)" }}
        >
          This tab lands every athlete drill from Session and Longitudinal. Coming in a
          later prompt.
        </p>
      </div>
    </div>
  );
}
