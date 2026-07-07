import { createFileRoute, Link } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
  component: Index,
});

function Index() {
  return (
    <div
      className="flex min-h-screen items-center justify-center px-6"
      style={{ backgroundColor: "var(--color-canvas)" }}
    >
      <div className="max-w-xl space-y-6 text-center">
        <div className="type-micro" style={{ color: "var(--color-text-tertiary)" }}>
          ST2 · Foundation
        </div>
        <h1
          className="text-4xl font-semibold tracking-tight"
          style={{ color: "var(--color-text-primary)" }}
        >
          Post-session monitoring for professional squads.
        </h1>
        <p style={{ color: "var(--color-text-secondary)" }}>
          Design system and core data objects only. Product screens ship in later prompts.
        </p>
        <div>
          <Link
            to="/styleguide"
            className="type-micro inline-flex items-center rounded-md px-4 py-2 text-white transition-colors"
            style={{ backgroundColor: "var(--color-brand)" }}
          >
            Open styleguide →
          </Link>
        </div>
      </div>
    </div>
  );
}
